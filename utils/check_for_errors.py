import logging.config

from utils.cpu_cost import CPUCost

logger = logging.getLogger(__name__)


class CheckForErrors:

    @staticmethod
    def check_for_errors(game, sim):

        logger.debug("Checking the correctness of the revenues and payments vectors...\n")
        cpu_cost = CPUCost()
        cost = cpu_cost.get_total_cpu_cost(game)
        # check for payments and costs
        if sim.simulation_type == 'additive' or (not sim.variable_cpu_price and not sim.per_time_slot_allocation):
            if abs(cost - sum(game.grand_coalition.payments)) > 0.001:
                logger.error("ERROR: the sum of single payments (for each player) don't match the total payment")
                logger.error("sum of payments is: %s", sum(game.grand_coalition.payments))
                logger.error("cost is: %s", cost)
                logger.error("difference is: %s", cost - sum(game.grand_coalition.payments))
                return False

        else:
            if abs(cost - sum(game.grand_coalition.payments)) > 0.001:
                logger.error("ERROR: the sum of single payments (for each player) don't match the total payment")
                logger.error("sum of payments is: %s", sum(game.grand_coalition.payments))
                logger.error("cost is: %s", cost)
                logger.error("difference is: %s", cost - sum(game.grand_coalition.payments))
                return False
            else:
                logger.debug(
                    "Since value function is not additive and allocation is not fixed, total cost - total payments should be a positive number")
                logger.debug("sum of payments is: %s", sum(game.grand_coalition.payments))
                logger.debug("cost is: %s", cost)
                logger.debug("difference is: %s", cost - sum(game.grand_coalition.payments))

        # Check for utilities and revenues
        if sim.simulation_type == 'additive' or (not sim.variable_cpu_price and not sim.per_time_slot_allocation):
            if abs(sum(game.grand_coalition.revenues) - sum(game.grand_coalition.utilities)) > 0.001:
                logger.error(
                    "ERROR: game is additive or allocation and cpu price are fixed and the sum of single utilities (for each player) don't match the total revenues")
                logger.error("sum of utilities is: %s", sum(game.grand_coalition.utilities))
                logger.error("sum of revenues is: %s", game.grand_coalition.revenues)
                logger.error("difference is: %s",
                             sum(game.grand_coalition.revenues) - sum(game.grand_coalition.utilities))
                return False

        else:
            if sum(game.grand_coalition.utilities) > sum(game.grand_coalition.revenues) + 0.001:
                logger.error(
                    "ERROR: game is not additive and allocation or cpu price are are not fixed and the sum of single revenues (for each player) don't match the total revenues")
                logger.error("sum of net utilities is: %s", sum(game.grand_coalition.utilities))
                logger.error("sum of revenues is: %s", sum(game.grand_coalition.revenues))
                logger.error("difference is: %s",
                             sum(game.grand_coalition.revenues) - sum(game.grand_coalition.utilities))
                return False
            else:

                logger.debug(
                    "Since value function is not additive and allocation or cpu price are are not fixed, total utilities - total revenues should be a positive number")
                logger.debug("sum of revenues is: %s", sum(game.grand_coalition.revenues))
                logger.debug("sum of utilities is: %s", sum(game.grand_coalition.utilities))
                logger.debug("difference is: %s",
                             sum(game.grand_coalition.revenues) - sum(game.grand_coalition.utilities))

        logger.debug("Total payment and sum of single payments and revenues are correct!")
        return True
