from scipy.optimize import minimize

from config import config
from controller.optimization_controller import Optimization
from model.grand_coalition import GrandCoalition
import logging.config

from utils.cpu_cost import CPUCost

logger = logging.getLogger(__name__)


class GenericGameController:

    # Total coalition net revenue is the result of the maximization of the value function v(S)
    # V(S) is calculated: given each player's utility function, (with argument load per timeslot)
    # we want to calculate the sum of each player utility function, and then sum it for all players.
    # That way we get players allocation vector ~h and total capacity (C) as to maximize the coalition value v(S)
    # This should be called only when N.O. is in the coalition
    @staticmethod
    def calculate_coal_payoff(game, coal):
        # Skip first players since it is the N.O.
        opt = Optimization(game.min_cpu_price, game.max_cpu_price, game.min_cores_hosted, game.max_cores_hosted,
                           game.daily_timeslots, game.years * 365, coal.players[1:])

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
        gc.coalition_payoff = -sol['fun']
        # Save the total cpu price
        # If variable
        if cpu_price:
            gc.total_cpu_price = cpu_price
        # If fixed
        else:
            gc.total_cpu_price = game.min_cpu_price * sum(gc.allocation)

        game.grand_coalition = gc

        for i, player in enumerate(game.players):
            player.allocation = gc.allocation[i]
            player.utility = gc.utilities[i]
            # TODO use simulation property
            # If cpu price is variable
            if cpu_price:
                player.payoff = gc.utilities[i] - player.allocation * cpu_price / sum(gc.allocation)

            else:
                player.payoff = gc.utilities[i] - player.allocation * game.min_cpu_price

            gc.net_utilities[i] = player.payoff

        payoffs = [player.payoff for player in game.players]
        logger.info("Players allocation vector is: %s:", gc.allocation)
        if config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']:
            slice_by_t_s = [(opt.allocations[i:i + opt.amount_of_service_providers]) for i in
                            range(0, len(opt.allocations), opt.amount_of_service_providers)]
            unused_alloc = [(gc.total_time_slot_allocation - sum(t)) for t in slice_by_t_s]
            logger.debug("Players allocation for each time-slot is: %s:", slice_by_t_s)
            logger.info("Max allocation across all time slots is: %s:", gc.total_time_slot_allocation)
            logger.debug("Unused allocation for each time-slot is: %s:", unused_alloc)
            logger.debug("Average unused allocation is: %s:", sum(unused_alloc)/96)

        logger.info("Players gross revenue (gross utilities) vector is: %s", gc.utilities)
        logger.info("Players payoff (net utilities) vector is: %s", payoffs)
        logger.info("Grand coalition total payoff (net utilities) is %s:", gc.coalition_payoff)

    @staticmethod
    def players_revenue_and_payment(game, p_cpu):

        players_numb = game.amount_of_players
        payoff_vector = game.grand_coalition.shapley_value
        w = sum(game.grand_coalition.allocation)

        constraints = [{
            'type': 'eq',
            'fun': lambda x: sum(x[players_numb:]) - p_cpu
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
