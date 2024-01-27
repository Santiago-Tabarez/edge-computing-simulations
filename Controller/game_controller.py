import itertools
from math import factorial

from scipy.optimize import minimize

from model.coalition import MyCoalition
from model.grand_coalition import GrandCoalition
from model.game import Game
from Controller.optimization import maximize_payoff
from model.network_owner import NetworkOwner
from model.service_provider import ServiceProvider
from utils.yaml_data_reader import YAMLDataReader


def create_game(game_data):
    games = []

    for max_cor_h in game_data['max_cores_hosted']:
        for daily_tl in game_data['daily_timeslots']:
            for year in game_data['years']:
                for price in game_data['price_cpu']:
                    # Create combinations of avg_load and benefit_factor for each service provider
                    for sp_combinations in itertools.product(
                            *[itertools.product(sp['avg_load'], sp['benefit_factor'], sp['chi'])
                              for sp in game_data['service_providers']]):

                        game = Game(years=year, max_cores_hosted=max_cor_h,
                                    price_cpu=price,
                                    amount_of_players=1,
                                    daily_timeslots=daily_tl)

                        network_owner = NetworkOwner(0)
                        game.add_player(network_owner)

                        for sp, (avg_load, benefit_factor, chi) in zip(game_data['service_providers'], sp_combinations):
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

"""
    for max_cor_h in game_data['max_cores_hosted']:
        for daily_tl in game_data['daily_timeslots']:
            for year in game_data['years']:
                for price in game_data['price_cpu']:
                    for avg_loads in itertools.product(*[sp['avg_load'] for sp in game_data['service_providers']]):
                        game = Game(years=year, max_cores_hosted=max_cor_h,
                                    price_cpu=price,
                                    amount_of_players=len(game_data['service_providers']) + 1,
                                    daily_timeslots=daily_tl)

                        player_id = 0
                        network_owner = NetworkOwner(player_id)
                        game.add_player(network_owner)

                        for sp, avg_load in zip(game_data['service_providers'], avg_loads):
                            player_id += 1
                            service_provider = ServiceProvider(player_id=player_id, avg_load=avg_load,
                                                               benefit_factor=sp['benefit_factor'], chi=sp['chi'])
                            game.add_player(service_provider)

                        for col in YAMLDataReader.all_permutations(game.players)[1:]:
                            coal = MyCoalition(col, 0)
                            game.coalitions.append(coal)

                        games.append(game)

    return games

"""

"""
    for max_cor_h in game_data['max_cores_hosted']:
        for daily_tl in game_data['daily_timeslots']:
            for year in game_data['years']:
                for price in game_data['price_cpu']:

                    game = Game(years=year, max_cores_hosted=max_cor_h,
                                price_cpu=price,
                                amount_of_players=len(game_data['service_providers']) + 1,
                                daily_timeslots=daily_tl)

                    player_id = 0
                    network_owner = NetworkOwner(player_id)
                    game.add_player(network_owner)
                    for sp in game_data['service_providers']:
                        player_id += 1
                        service_provider = ServiceProvider(player_id=player_id, avg_load=sp['avg_load'],
                                                           benefit_factor=sp['benefit_factor'], chi=sp['chi'])
                        game.add_player(service_provider)

                    for col in YAMLDataReader.all_permutations(game.players)[1:]:
                        coal = MyCoalition(col, 0)
                        game.coalitions.append(coal)

                    games.append(game)

    return games
"""
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
