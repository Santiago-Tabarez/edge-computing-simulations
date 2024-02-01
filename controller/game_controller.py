import itertools
from math import factorial

from scipy.optimize import minimize

from model.coalition import MyCoalition
from model.grand_coalition import GrandCoalition
from model.game import Game
from controller.optimization import maximize_payoff
from model.network_owner import NetworkOwner
from model.service_provider import ServiceProvider
from model.service_provider_sim import ServiceProviderSimulation
from model.simulation import Simulation
from utils.yaml_data_reader import YAMLDataReader



# Get a list of games from each of the .yaml files under the games to process folder
# Will create a different game for each possible combination of the following values:
# game: max_cores_hosted, daily_timeslots, years, price_cpu
# for each service_provider: avg_load, benefit_factor, chi
# amount of games will be the product of the length of those properties
# For the player_id, it will create len(player:id) players with the same values but different player_id


# Aux function to
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
    # transform the global parameters into a list of values
    max_cores_hoisted_lis = parse_value_list(game_data['max_cores_hosted'])
    daily_timeslots_list = parse_value_list(game_data['daily_timeslots'])
    years_list = parse_value_list(game_data['years'])
    cpu_price_list = parse_value_list(game_data['cpu_price'])

    amount_of_players = 1
    sim_players = []
    #no = NetworkOwner(game_data['simulation_name'])
    #sim_players.append(no)
    for sp in game_data['service_providers']:

        load_l = parse_value_list(sp['avg_load'])
        ben_f_l = parse_value_list(sp['benefit_factor'])
        chi_l = parse_value_list(sp['chi'])

        # id, service_provider_name, simulation_id, benefit_factor_min, benefit_factor_max, chi_min, chi_max, avg_load_min, avg_load_max

        for sp_id in sp['service_provider_name']:
            amount_of_players += 1
            spm = ServiceProviderSimulation(sp_id, min(ben_f_l), max(ben_f_l), min(chi_l), max(chi_l), min(load_l),
                                            max(load_l))
            sim_players.append(spm)

    sim = Simulation(game_data['simulation_name'], min(max_cores_hoisted_lis), max(max_cores_hoisted_lis),
                     min(cpu_price_list), max(cpu_price_list),
                     min(years_list), max(years_list), min(daily_timeslots_list), max(daily_timeslots_list),
                     amount_of_players)
    sim.players = sim_players

    for max_cor_h in parse_value_list(game_data['max_cores_hosted']):
        for daily_tl in parse_value_list(game_data['daily_timeslots']):
            for year in parse_value_list(game_data['years']):
                for price in parse_value_list(game_data['cpu_price']):

                    for sp_combinations in itertools.product(
                            *[itertools.product(sp['avg_load'], sp['benefit_factor'], sp['chi'])
                              for sp in game_data['service_providers']]):

                        game = Game(game_data['simulation_name'], years=year, max_cores_hosted=max_cor_h,
                                    price_cpu=price,
                                    amount_of_players=1,
                                    daily_timeslots=daily_tl)

                        # Take name from the simulation name
                        network_owner = NetworkOwner(game_data['simulation_name'])
                        game.add_player(network_owner)

                        for sp, (avg_load, benefit_factor, chi) in zip(game_data['service_providers'],
                                                                       sp_combinations):
                            for service_provider_name in sp['service_provider_name']:
                                service_provider = ServiceProvider(player_name=service_provider_name, avg_load=avg_load,
                                                                   benefit_factor=benefit_factor, chi=chi)
                                game.amount_of_players += 1
                                game.add_player(service_provider)

                        for col in YAMLDataReader.all_permutations(game.players)[1:]:
                            coal = MyCoalition(col, 0)
                            game.coalitions.append(coal)

                        sim.games.append(game)

    return sim


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

    # print("players", current_coalition.players)
    # print("utilities", current_coalition.utilities)
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
                    player_s_ids = [obj.player_name for obj in S.players]
                    player_q_ids = [obj.player_name for obj in q.players]
                    # print("Contribution:", contribution, "Coalition S:", player_s_ids, "Coalition Q:",
                    #      player_q_ids)
                    # Weight the contribution by the number of permutations leading to this coalition formation
                    tmp = factorial(len(S.players)) * factorial(
                        game.amount_of_players - len(S.players) - 1) * contribution
                    summation = summation + tmp
        x_payoffs.append((1 / n_factorial) * summation)

    # print("Shapley value is (fair payoff vector):", game.gran_coalition.shapley_value, "\n")
    # print("Capacity:", sum(game.gran_coalition.allocation), "\n")
    # print("Resources split", game.gran_coalition.allocation, "\n")
    return x_payoffs


def how_much_revenue_payment(game, payoff_vector, w):
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

    # print("Revenues array:", game.gran_coalition.revenues, "\n")
    # print("Payments array:", game.gran_coalition.payments, "\n")
    return

