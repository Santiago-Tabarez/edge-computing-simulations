from config import config
from controller.optimization_controller import Optimization
from model.grand_coalition import GrandCoalition
import logging.config

logger = logging.getLogger(__name__)


class GenericGameController:

    # Total coalition net revenue is the result of the maximization of the value function v(S)
    # V(S) is calculated: given each player's utility function, (with argument load per timeslot)
    # we want to calculate the sum of each player utility function, and then sum it for all players.
    # That way we get players allocation vector ~h and total capacity (C) as to maximize the coalition value v(S)
    # This should be called only when N.O. is in the coalition
    @staticmethod
    def calculate_coal_payoff(game, coal):
        # We skip first player since it is the N.O.
        opt = Optimization(game.min_cpu_price, game.max_cpu_price, game.min_cores_hosted, game.max_cores_hosted,
                           game.daily_timeslots, game.years * 365, game.load_exponent, game.beta_exponent, game.xi_exponent, game.price_exponent, coal.players[1:])

        sol, utilities, price = opt.maximize_coalition_payoff()
        coal.allocation = [0] + list(sol['x'][:-1])
        coal.utilities = [0] + utilities
        coal.coalition_payoff = -sol['fun']
        return sol, utilities, price, opt

    @staticmethod
    def create_grand_coalition(game, sol, utilities, cpu_price, opt):

        gc = GrandCoalition()
        # Add 0 for NO utilities and allocation

        if config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']:
            gc.utilities = [0] + utilities
            gc.allocation = [0] + list(sol['x'])
            gc.per_time_slot_allocation = opt.allocations
            gc.total_time_slot_allocation = opt.total_allocation
        else:
            gc.utilities = [0] + utilities
            gc.allocation = [0] + list(sol['x'][:-1])

        gc.net_utilities = [0] * game.amount_of_players
        #gc.coalition_payoff = -sol['fun']
        # Save the total cpu price
        # If cpu_price is variable
        if cpu_price:
            gc.total_cpu_price = cpu_price
        # If cpu_price is fixed
        else:
            gc.total_cpu_price = game.min_cpu_price * sum(gc.allocation)

        game.grand_coalition = gc

        for i, player in enumerate(game.players):
            player.allocation = gc.allocation[i]
            player.gross_utility = gc.utilities[i]
            # If cpu price is variable
            if cpu_price:
                player.net_utility = gc.utilities[i] - player.allocation * cpu_price / sum(gc.allocation)

            else:
                player.net_utility = gc.utilities[i] - player.allocation * game.min_cpu_price

            gc.net_utilities[i] = player.net_utility

        net_utilities = [player.net_utility for player in game.players]
        logger.info("Players allocation vector is: %s:", gc.allocation)
        if config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']:
            slice_by_t_s = [(opt.allocations[i:i + opt.amount_of_service_providers]) for i in
                            range(0, len(opt.allocations), opt.amount_of_service_providers)]
            unused_alloc = [(gc.total_time_slot_allocation - sum(t)) for t in slice_by_t_s]
            logger.debug("Players allocation for each time-slot is: %s:", slice_by_t_s)
            logger.info("Max allocation across all time slots is: %s:", gc.total_time_slot_allocation)
            # logger.debug("Unused allocation for each time-slot is: %s:", unused_alloc)
            logger.debug("Average unused allocation is: %s:", sum(unused_alloc)/game.daily_timeslots)

        logger.info("Players revenues (gross utilities) vector is: %s", gc.utilities)
        logger.info("Players contribution (net utilities) vector is: %s", net_utilities)
        logger.info("Grand coalition total value (net utilities) is %s:", sum(net_utilities))

    @staticmethod
    # p_cpu is the total CPU price
    def players_revenue_and_payment(game, deployment_cost):

        cpu_cost = deployment_cost / sum(game.grand_coalition.allocation)
        players_numb = game.amount_of_players
        shapley_vector = game.grand_coalition.shapley_value
        revenues_vector = game.grand_coalition.utilities
        contribution_vector = game.grand_coalition.net_utilities

        game.grand_coalition.allocation_payment = [0] * players_numb
        game.grand_coalition.fairness_payment = [0] * players_numb
        no_payment = 0

        # if config.VALUE_FUNCTION_MODE['additive_deterministic']:
        for i in range(players_numb):
            if i != 0:
                game.grand_coalition.allocation_payment[i] = cpu_cost * game.grand_coalition.allocation[i]
                game.grand_coalition.fairness_payment[i] = game.grand_coalition.net_utilities[i]/2
                no_payment += game.grand_coalition.net_utilities[i]/2

        game.grand_coalition.allocation_payment[0] = 0
        game.grand_coalition.fairness_payment[0] = -1 * no_payment

        logger.info("Allocation Payments array: %s", game.grand_coalition.allocation_payment)
        logger.info("Fairness payments array: %s", game.grand_coalition.fairness_payment)




        # This give the same result as the code I was provided
"""
        constraints = [{
            'type': 'eq',
            'fun': lambda x: sum(x[players_numb:]) - deployment_cost
        }]

        constraints += [{
            'type': 'eq',
            'fun': lambda x, i=i: x[i] - x[i + players_numb] - payoff_vector[i]
        } for i in range(players_numb)]

        x0 = [1] * 2 * players_numb
        bounds = [(None, None)] * 2 * players_numb

        res = minimize(lambda x: 0, x0, method='slsqp', bounds=bounds, constraints=constraints)

        game.grand_coalition.deployment_cost, game.grand_coalition.payments = res.x[:players_numb], res.x[players_numb:]

        logger.info("Revenues array: %s", game.grand_coalition.deployment_cost)
        logger.info("Payments array: %s", game.grand_coalition.payments)

"""