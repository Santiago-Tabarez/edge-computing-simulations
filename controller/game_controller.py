import hashlib
import itertools
import random
import string

import mysql.connector

from math import factorial

from scipy.optimize import minimize

from model.coalition import MyCoalition
from model.grand_coalition import GrandCoalition
from model.game import Game
from controller.optimization import maximize_payoff
from model.network_owner import NetworkOwner
from model.service_provider import ServiceProvider
from utils.yaml_data_reader import YAMLDataReader

mydb = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="edge-computing-simulations"
)


# Get a list of games from each of the .yaml files under the games to process folder
# Will create a different game for each possible combination of the following values:
# game: max_cores_hosted, daily_timeslots, years, price_cpu
# for each service_provider: avg_load, benefit_factor, chi
# amount of games will be the product of the length of those properties
# For the player_id, it will create len(player:id) players with the same values but different player_id

def create_value_list(values):
    start, end, total_amount = map(float, values.split(':'))
    total_amount = int(total_amount)
    if total_amount <= 1:
        return [start]
    step = (end - start) / (total_amount - 1)
    return [start + i * step for i in range(total_amount)]


def parse_value_list(value):
    if isinstance(value, list):
        if isinstance(value[0], str):
            return create_value_list(value[0])
        else:
            return value
    else:
        _list = [value]
        return _list


def create_game(game_data):
    games = []
    for max_cor_h in parse_value_list(game_data['max_cores_hosted']):
        for daily_tl in parse_value_list(game_data['daily_timeslots']):
            for year in parse_value_list(game_data['years']):
                for price in parse_value_list(game_data['cpu_price']):
                    # Create combinations of avg_load, benefit_factor and chi for each service provider
                    # for serv_prov in game_data['service_providers']:

                    # avg_load = parse_value_list(serv_prov['avg_load'])
                    # benefit_factor = parse_value_list(serv_prov['benefit_factor'])
                    # chi = parse_value_list(serv_prov['chi'])

                    for sp_combinations in itertools.product(
                            *[itertools.product(sp['avg_load'], sp['benefit_factor'], sp['chi'])
                              for sp in game_data['service_providers']]):

                        game = Game(game_data['simulation_id'], years=year, max_cores_hosted=max_cor_h,
                                    price_cpu=price,
                                    amount_of_players=1,
                                    daily_timeslots=daily_tl)

                        network_owner = NetworkOwner(0)
                        game.add_player(network_owner)

                        for sp, (avg_load, benefit_factor, chi) in zip(game_data['service_providers'],
                                                                       sp_combinations):
                            for player_id in sp['player_id']:
                                service_provider = ServiceProvider(player_id=player_id, avg_load=avg_load,
                                                                   benefit_factor=benefit_factor, chi=chi)
                                game.amount_of_players += 1
                                game.add_player(service_provider)

                        for col in YAMLDataReader.all_permutations(game.players)[1:]:
                            coal = MyCoalition(col, 0)
                            game.coalitions.append(coal)

                        games.append(game)

    return games


# Total coalition revenue is the result of the maximization of the objective function v(S)
# This is, given each player a utility function, (with argument load per timeslot)
# we want to calculate the sum of each player utility function, and then sum it for each player.
# That way we get players allocation vector ~h and total capacity (C) to maximize the coalition value v(S):
# This is done for each coalition and then will be used as input to calculate players Shapley value
def calculate_coal_payoff(game, coalition):
    sol, utilities = maximize_payoff(game, coalition.players)
    coalition.utilities = utilities
    coalition.coalition_payoff = -sol['fun']
    if len(coalition.players) == game.amount_of_players:
        gc = GrandCoalition(utilities)
        gc.allocation = sol['x'][:-1]
        gc.coalition_payoff = 365 * game.years * sum(utilities)
        game.gran_coalition = gc

    return sol, utilities


# coalitions = list with all possible coalitions, for n player 2^n coalitions
# 0 player, 1 player, 2 player,,, n players so the last one in the gran coalition
# players_number = number of players
# infos_all_coal_one_config = list (2^n)-1 elements, (no empty coalition)
# where each element is a tuple with beta value, coalition, coalition payoff
def shapley_value_payoffs(game):
    # list of all player shapley value
    x_payoffs = []
    # Calculate the factorial of the number of players, used in Shapley value computation
    n_factorial = factorial(game.amount_of_players)
    # takes the last item (the grand coalition) and iterates in their players, so we get all players one by one
    for player in game.players:
        coalitions_dict_without_i = []
        coalitions_dict_with_i = []

        # Classify each coalition based on whether it includes the current player
        for coalition_dict in game.coalitions:
            if player not in coalition_dict.players:
                coalitions_dict_without_i.append(coalition_dict)
            else:
                coalitions_dict_with_i.append(coalition_dict)

        # Initialize summation for calculating the Shapley value for the current player
        summation = 0
        # Calculate the player's contribution to each coalition they are part of
        for S in coalitions_dict_without_i:
            for q in coalitions_dict_with_i:
                # Check if the only difference between the coalitions is the current player
                if tuple(set(S.players).symmetric_difference(q.players)) == (player,):
                    # Calculate the marginal contribution of the player
                    contribution = q.coalition_payoff - S.coalition_payoff
                    player_s_ids = [obj.player_id for obj in S.players]
                    player_q_ids = [obj.player_id for obj in q.players]
                    # print("Contribution:", contribution, "Coalition S:", player_s_ids, "Coalition Q:",
                    #      player_q_ids)
                    # Weight the contribution by the number of permutations leading to this coalition formation
                    tmp = factorial(len(S.players)) * factorial(
                        game.amount_of_players - len(S.players) - 1) * contribution
                    summation = summation + tmp
        x_payoffs.append((1 / n_factorial) * summation)

    return x_payoffs


def how_much_rev_paym(game, payoff_vector, w):
    p_cpu = game.price_cpu
    players_numb = game.amount_of_players

    def make_constraint_func(index1, index2):
        def _constraint(x):
            return x[index1] - x[index2] - payoff_vector[index1]

        return _constraint

    def _constraint_total_cap(x):
        return sum(x[players_numb:]) - p_cpu * w

    constraints = [{'type': 'eq', 'fun': _constraint_total_cap}]

    for i in range(players_numb):
        constraint_func = make_constraint_func(i, i + players_numb)
        constraints.append({'type': 'eq', 'fun': constraint_func})

    x0 = [1] * 2 * players_numb
    b = (None, None)
    bounds = (b,) * players_numb * 2

    def obj(x):
        return 0

    res = minimize(obj, x0, method='slsqp', bounds=bounds, constraints=constraints)
    # res = minimize(obj, x0, method='slsqp', bounds=bnds, constraints=cons)
    # This return two arrays, we extract from res, the list 'x' a list and split it in two, one from the
    # first element to the players_numb element, and the other from the players_numb element to the end
    # This is, a list of revenues and a list of payments

    game.gran_coalition.revenues = res['x'][0:players_numb]
    game.gran_coalition.payments = res['x'][players_numb:]
    return


def save_game(game):
    my_cursor = mydb.cursor()

    # SQL insert game
    insert_game = """
    INSERT INTO games (sim_id, cpu_price, years, daily_timeslots, max_cores_hosted, game_id) 
    VALUES (%s, %s, %s, %s, %s, %s);
    """

    simulation_id = game.simulation_id


    max_cores_hosted = game.max_cores_hosted
    price_cpu = game.price_cpu
    years = game.years
    daily_timeslots = game.daily_timeslots

    # Concatenate the variables into a single string and convert non-string variables to strings
    # concatenated_vars = f"{simulation_id}{max_cores_hosted}{price_cpu}{years}{daily_timeslots}"

    # Generate a hash value using SHA-256
    # hash_object = hashlib.sha256(concatenated_vars.encode())
    # game_id = hash_object.hexdigest()[:45]


    game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=45))
    # Values to insert
    values = (simulation_id, game.price_cpu, game.years, game.daily_timeslots,
              game.max_cores_hosted, game_id)

    # Executing the query
    try:
        my_cursor.execute(insert_game, values)
        mydb.commit()
    except mysql.connector.Error as err:
        print("Error occurred: ", err)
    # finally:
    # mycursor.close()

    insert_player = """
       INSERT INTO players (game_id, player_id, avg_load, benefit_factor, chi, allocation, utilities, shapley_value, revenues, payment) 
       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
       """

    for i in range(game.amount_of_players):
        player_id = game.players[i].player_id
        avg_load = game.players[i].avg_load
        benefit_factor = game.players[i].benefit_factor
        chi = game.players[i].chi
        allocation = game.gran_coalition.allocation[i]
        utilities = game.gran_coalition.utilities[i]
        shapley_value = game.gran_coalition.shapley_value[i]
        revenues = game.gran_coalition.revenues[i]
        payment = game.gran_coalition.payments[i]

        # Values to insert
        values = (game_id, player_id, avg_load, benefit_factor, chi,
                  allocation, utilities, shapley_value, revenues, payment)
        try:
            my_cursor.execute(insert_player, values)
            mydb.commit()
            print("Query executed successfully")
        except mysql.connector.Error as err:
            print("Error occurred: ", err)

        print(player_id, avg_load, benefit_factor, chi)

    """
    # CREATE TABLE `games` (
       `sim_id` varchar(45) DEFAULT NULL,
       `cpu_price` float DEFAULT NULL,
       `years` float DEFAULT NULL,
       `daily_timeslots` int DEFAULT NULL,
       `max_cores_hosted` int DEFAULT NULL,
       `game_id` varchar(45) DEFAULT NULL
     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    
    CREATE TABLE `players` (
        `game_id` varchar(45) DEFAULT NULL,
        `player_id` varchar(45) DEFAULT NULL,
        `avg_load` float DEFAULT NULL,
        `benefit_factor` float DEFAULT NULL,
        `chi` float DEFAULT NULL,
        `allocation` float DEFAULT NULL,
        `utilities` float DEFAULT NULL,
        `shapley_value` float DEFAULT NULL,
        `revenues` float DEFAULT NULL,
        `payment` float DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

    """

    return None
