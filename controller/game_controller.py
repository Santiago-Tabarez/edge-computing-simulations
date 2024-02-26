from scipy.optimize import minimize
import logging.config

from model.grand_coalition import GrandCoalition
from controller.optimization_controller import Optimization

logger = logging.getLogger(__name__)


# Total coalition net revenue is the result of the maximization of the value function v(S)
# V(S) is calculated: given each player's utility function, (with argument load per timeslot)
# we want to calculate the sum of each player utility function, and then sum it for all players.
# That way we get players allocation vector ~h and total capacity (C) as to maximize the coalition value v(S)
def calculate_grand_coal_payoff(game):

    # We remove the NO from the optimization since it doesn't use any edge resources
    opt = Optimization(game.price_cpu, game.daily_timeslots, game.amount_of_players-1, game.max_cores_hosted, game.years * 365, game.players[1:])
    # Calculate the maximum value for grand coalition
    sol, utilities = opt.maximize_coalition_payoff()

    # Create grand coalition and assign results to players
    # Add 0 for NO utilities and allocation
    gc = GrandCoalition([0] + utilities)
    gc.allocation = [0] + list(sol['x'][:-1])
    gc.coalition_payoff = -sol['fun']
    game.grand_coalition = gc

    for i, player in enumerate(game.players):
        player.allocation = gc.allocation[i]
        player.utility = gc.utilities[i]
        player.payoff = gc.utilities[i] - player.allocation * game.price_cpu

    payoffs = [player.payoff for player in game.players]
    logger.info("Players allocation vector is: %s:", gc.allocation)
    logger.info("Players gross revenue (gross utilities) vector is: %s", gc.utilities)
    logger.info("Players payoff (net utilities) vector is: %s", payoffs)
    logger.info("Grand coalition total payoff (net utilities) is %s:", gc.coalition_payoff)


# Since the value function is additive (Theorem 1) this is the same as calculating the Shapley value and much faster
def players_contribution(game):

    # Network owner contribution is half of total payoff (Theorem 2)
    players_contribution_result = [sum(player.payoff for player in game.players[1:]) / 2]
    # Service providers contribution
    for player in game.players[1:]:
        players_contribution_result.append(player.payoff / 2)

    game.grand_coalition.shapley_value = players_contribution_result

    logger.info("Players contribution (Shapley value) vector is: %s:", players_contribution_result)


# Now that we have the value for the grand coalition and each player contribution to that coalition (Shapley value)
# We need to calculate how much each player needs to pay (or receive) from the coalition to make the initial investment
"""
def how_much_revenue_payment(game):
    p_cpu = game.price_cpu
    players_numb = game.amount_of_players
    payoff_vector = game.grand_coalition.shapley_value
    w = sum(game.grand_coalition.allocation)

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
    # This return two arrays, we extract from res, the list 'x' a list and split it in two, one from the
    # first element to the players_numb element, and the other from the players_numb element to the end
    # This is, a list of revenues and a list of payments

    game.grand_coalition.revenues = res['x'][0:players_numb]
    game.grand_coalition.payments = res['x'][players_numb:]

    logger.info("Revenues array: %s", game.grand_coalition.revenues)
    logger.info("Payments array: %s", game.grand_coalition.payments)
"""


# Now that we have the value for the grand coalition and each player contribution to that coalition (Shapley value)
# We need to calculate how much each player needs to pay (or receive) from the coalition to make the initial investment
def how_much_revenue_payment(game):
    p_cpu = game.price_cpu
    players_numb = game.amount_of_players
    payoff_vector = game.grand_coalition.shapley_value
    w = sum(game.grand_coalition.allocation)

    constraints = [{
        'type': 'eq',
        'fun': lambda x: sum(x[players_numb:]) - p_cpu * w
    }]

    constraints += [{
        'type': 'eq',
        'fun': lambda x, i=i: x[i] - x[i + players_numb] - payoff_vector[i]
    } for i in range(players_numb)]

    x0 = [1] * 2 * players_numb
    bounds = [(None, None)] * 2 * players_numb

    res = minimize(lambda x: 0, x0, method='slsqp', bounds=bounds, constraints=constraints)

    game.grand_coalition.revenues, game.grand_coalition.payments = res.x[:players_numb], res.x[players_numb:]

    logger.info("Revenues array: %s", game.grand_coalition.revenues)
    logger.info("Payments array: %s", game.grand_coalition.payments)
