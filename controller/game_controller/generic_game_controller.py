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
                           game.daily_timeslots, game.years * 365, game.load_exponent, game.beta_exponent,
                           game.xi_exponent, game.price_exponent, coal.players[1:], game.chosen_case)

        utility_ts, net_utility_ts, allocation_ts, effective_price = opt.maximize_coalition_payoff()

        coal.allocation = [0] + allocation_ts.mean(axis=1).tolist()
        coal.utilities = [0] + utility_ts.sum(axis=1).tolist()
        coal.coalition_payoff = [0] + net_utility_ts.sum(axis=1).sum()
        return utility_ts, net_utility_ts, allocation_ts, effective_price

    @staticmethod
    def create_grand_coalition(game, utility_sp, net_utility_sp, allocation_ts, effective_price):

        if config.EXTRA_CONSIDERATIONS['variable_cpu_price']:
            game.weighted_per_unit_price = effective_price

        gc = GrandCoalition()
        # Add 0 for NO utilities and allocation
        if config.VALUE_FUNCTION_MODE['additive_deterministic']:
            gc.utilities = [0] + utility_sp
            gc.allocation = [0] + allocation_ts
            gc.net_utilities = [0] + net_utility_sp
            gc.total_cpu_price = effective_price

        else:

            gc.utilities = [0] + utility_sp.sum(axis=1).tolist()
            gc.allocation = [0] + allocation_ts.mean(axis=1).tolist()
            gc.net_utilities = [0] + net_utility_sp.sum(axis=1).tolist()
            gc.total_cpu_price = effective_price

            if not config.VALUE_FUNCTION_MODE['additive_deterministic']:
                gc.per_time_slot_allocation = allocation_ts
                gc.total_time_slot_allocation = allocation_ts.mean(axis=1).sum()

        game.grand_coalition = gc

        for i, player in enumerate(game.players):
            player.allocation = gc.allocation[i]
            player.gross_utility = gc.utilities[i]
            player.net_utility = gc.net_utilities[i]

        logger.info("Players allocation vector is: %s:", gc.allocation)
        if config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']:
            if not config.VALUE_FUNCTION_MODE['additive_deterministic']:
                # slice_by_t_s = [(opt.allocations[i:i + opt.amount_of_service_providers]) for i in
                #                range(0, len(opt.allocations), opt.amount_of_service_providers)]
                # unused_alloc = [(gc.total_time_slot_allocation - sum(t)) for t in slice_by_t_s]
                #     logger.debug("Players allocation for each time-slot is: %s:", slice_by_t_s)
                logger.info("Max allocation across all time slots is: %s:", gc.total_time_slot_allocation)
            # logger.debug("Unused allocation for each time-slot is: %s:", unused_alloc)
            #    logger.debug("Average unused allocation is: %s:", sum(unused_alloc)/game.daily_timeslots)

        logger.info("Players revenues (gross utilities) vector is: %s", gc.utilities)
        logger.info("Players contribution (net utilities) vector is: %s", gc.net_utilities)
        logger.info("Grand coalition total value (net utilities) is %s:", sum(gc.net_utilities))

    @staticmethod
    # p_cpu is the total CPU price
    def players_revenue_and_payment(game, effective_cost):

        game.grand_coalition.allocation_payment = [0] * game.amount_of_players
        game.grand_coalition.fairness_payment = [0] * game.amount_of_players
        no_payment = 0

        for i in range(game.amount_of_players):
            if i != 0:
                game.grand_coalition.allocation_payment[i] = game.grand_coalition.allocation[i] * effective_cost
                game.grand_coalition.fairness_payment[i] = game.grand_coalition.net_utilities[i] - \
                                                           game.grand_coalition.shapley_value[i]
                no_payment -= game.grand_coalition.net_utilities[i] - game.grand_coalition.shapley_value[i]

        game.grand_coalition.allocation_payment[0] = 0
        game.grand_coalition.fairness_payment[0] = no_payment

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
