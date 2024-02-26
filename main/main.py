import time
import os
import psutil
import logging
import logging.config

from config.config import LOGGING_CONFIG
from controller.dao_controller import save_game, database_config
from controller.game_controller import how_much_revenue_payment, calculate_grand_coal_payoff, players_contribution
from controller.game_builder_controller import create_games
from utils.yaml_data_reader import YAMLDataReader


def main():
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)

    database_config()

    folder_path = '../games to process/'
    yaml_games_data = YAMLDataReader.read_yaml_files(folder_path)

    for game_data in yaml_games_data:

        start_sim = time.time()
        sim = create_games(game_data)

        logger.info("Total amount games to be processed: %s", len(sim.games))

        for game_num, game in enumerate(sim.games):

            start_game = time.time()
            calculate_grand_coal_payoff(game)
            logger.debug("Time required for calculating maximizing grand coalition value: %s seconds",
                         round(time.time() - start_sim))

            start_shap = time.time()
            players_contribution(game)
            logger.debug("Time required for calculating players contribution: %s seconds",
                         round(time.time() - start_shap))

            start_rev_pay = time.time()
            how_much_revenue_payment(game)
            logger.debug("Time required for calculating players payments and revenues: %s seconds",
                         round(time.time() - start_rev_pay))

            # checking if the calculation of payments and revenues is correct
            logger.debug("Checking the correctness of the revenues and payments vectors...\n")
            if abs(sum(game.grand_coalition.allocation) * game.price_cpu - sum(
                    game.grand_coalition.payments)) > 0.001 or abs(
                sum(game.grand_coalition.revenues) - sum(game.grand_coalition.revenues)) > 0.001:

                logger.debug("ERROR: the sum of single payments (for each players) or revenues don't match the total "
                             "payment/revenues!")

            else:
                logger.debug("Total payment and sum of single payments and revenues are correct!\n")
                save_game(game, sim)

            logger.debug("Total memory used by the process: %s MB",
                         psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
            logger.debug("Time required for the game: %s seconds", round(time.time() - start_game))
            logger.debug("Estimated time for current file to complete simulation: %s seconds",
                         (time.time() - start_game) * (len(sim.games) - (game_num + 1)))

            game_num += 1

        logger.debug("Total memory used by the process: %s MB",
                     psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        logger.debug("Time required for the simulation: %s seconds", round(time.time() - start_sim))


if __name__ == '__main__':
    main()
