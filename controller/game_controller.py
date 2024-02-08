import itertools
import shap
from math import factorial

from scipy.optimize import minimize

from model.grand_coalition import GrandCoalition
from controller.optimization_controller import maximize_coalition_payoff, maximize_player_payoff, _utility_i
from model.network_owner import NetworkOwner


# Total coalition revenue is the result of the maximization of the objective function v(S)
# This v(S) is calculated: given each player a utility function, (with argument load per timeslot)
# we want to calculate the sum of each player utility function, and then sum it for each player.
# That way we get players allocation vector ~h and total capacity (C) to maximize the coalition value v(S):
# This is done for each coalition and then will be used as input to calculate players Shapley value
def calculate_coal_payoff(game, coalition):
    sol, utilities = maximize_coalition_payoff(game, coalition.players)
    coalition.utilities = utilities
    coalition.coalition_payoff = -sol['fun']
    if len(coalition.players) == game.amount_of_players:
        gc = GrandCoalition(utilities)
        gc.allocation = sol['x'][:-1]
        gc.coalition_payoff = 365 * game.years * sum(utilities)
        game.grand_coalition = gc

    # print("players", current_coalition.players)
    # print("utilities", current_coalition.utilities)
    return sol, utilities


def calculate_grand_coal_payoff(game):
    coal = game.coalitions[-1]
    sol, utilities = maximize_coalition_payoff(game, coal.players)
    coal.utilities = utilities
    coal.coalition_payoff = -sol['fun']

    gc = GrandCoalition(utilities)
    gc.allocation = sol['x'][:-1]
    gc.coalition_payoff = 365 * game.years * sum(utilities)
    game.grand_coalition = gc

    i = 0
    for player in coal.players:
        if i > 0:
            player.allocation = gc.allocation[i]
            player.payoff = utilities[i] * 365 * game.years
            player.utility = utilities[i]

        i += 1
        # print("players", current_coalition.players)
    # print("utilities", current_coalition.utilities)
    return sol, utilities



def calculate_all_coal_payoff(game):
    i = 0
    for current_coalition in game.coalitions:
        if not len(current_coalition.players) == game.amount_of_players:
            if any(isinstance(player, NetworkOwner) for player in current_coalition.players):

                for player in current_coalition.players:

                    if player.player_id != 0:
                        p = next(p for p in game.players if p.player_id == player.player_id)
                        current_coalition.utilities.append(p.utility)
                        current_coalition.coalition_payoff += player.payoff
                    else:
                        current_coalition.utilities.append(0)
            else:
                current_coalition.payoff = 0
                #current_coalition.coalition_payoff = payoff
                current_coalition.utilities = [0] * len(current_coalition.players)

            i += 1


def calculate_player_payoff(game, player):
    sol, utilities = maximize_player_payoff(game, player)

    # coalition.utilities = utilities
    # coalition.coalition_payoff = -sol['fun']
    # if len(coalition.players) == game.amount_of_players:
    #    gc = GrandCoalition(utilities)
    #    gc.allocation = sol['x'][:-1]
    #    gc.coalition_payoff = 365 * game.years * sum(utilities)
    #    game.grand_coalition = gc

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

    # print("Shapley value is (fair payoff vector):", game.grand_coalition.shapley_value, "\n")
    # print("Capacity:", sum(game.grand_coalition.allocation), "\n")
    # print("Resources split", game.grand_coalition.allocation, "\n")
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

    game.grand_coalition.revenues = res['x'][0:players_numb]
    game.grand_coalition.payments = res['x'][players_numb:]

    # print("Revenues array:", game.grand_coalition.revenues, "\n")
    # print("Payments array:", game.grand_coalition.payments, "\n")
    return
