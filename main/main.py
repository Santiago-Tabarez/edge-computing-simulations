import sys
import time
import os
import psutil
import logging
import logging.config

from config.config import LOGGING_CONFIG
from config import config
from controller.GameController.deterministic_solver_game_controller import DeterministicSolverGameController
from controller.GameController.estimation_solver_game_controller import EstimationSolverGameController
from controller.cheat_controller import CheatController
from controller.dao_controller import DAOController
from controller.game_builder_controller import GameBuilderController
from controller.GameController.additive_value_game_controller import AdditiveValueGameController
from controller.simulation_controller import SimulationController
from utils.check_for_errors import CheckForErrors
from utils.yaml_data_reader import YAMLDataReader


def main():

    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)

    daoC = DAOController()
    daoC.database_config()

    folder_path = '../simulations to process/'
    yaml_games_data = YAMLDataReader.read_yaml_files(folder_path)

    # Determine the type of game based on value function
    additive = config.VALUE_FUNCTION_MODE['additive']
    deterministic = config.VALUE_FUNCTION_MODE['non_additive_deterministic']
    estimation = config.VALUE_FUNCTION_MODE['non_additive_estimation']
    if sum([additive, deterministic, estimation]) != 1:
        logger.error("Only one variable should be true in VALUE_FUNCTION_MODE")
        sys.exit(0)

    if additive:
        logger.info("Following simulations will be executed assuming additive value function for coalition value,"
                    "only grand coalition value will be calculated")
        gc = AdditiveValueGameController()
    elif deterministic:
        logger.info("Following simulations will be executed assuming non additive value function for coalition "
                    "values, it will return a deterministic result, all coalitions values will be calculated")
        gc = DeterministicSolverGameController()
    else:
        logger.info(
            "Following simulations will be executed assuming non additive value function for coalition values, "
            "it will return a estimation result, only some coalitions values will be calculated")
        gc = EstimationSolverGameController()

    gmc = GameBuilderController()
    cc = CheatController()
    sc = SimulationController()
    cfe = CheckForErrors()

    for game_data in yaml_games_data:

        start_sim = time.time()
        sim = gmc.create_games(game_data)

        logger.info("Total amount games to be processed: %s", len(sim.games))

        for game_num, game in enumerate(sim.games,):
            start_game = time.time()
            game = sc.simulate_game(gc, game)
            game_num += 1
            daoC.save_game(game, sim)

            if config.EXTRA_FUNCTIONALITIES['check_for_cheat']:
                cc.calculate_true_payoff_for_all_cheaters(gc, game)

            logger.debug("Total memory used by the process: %s MB",
                         psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
            logger.debug("Time required for the game: %s seconds", round(time.time() - start_game))
            logger.debug("Estimated time for current file to complete simulation: %s seconds",
                         (time.time() - start_game) * (len(sim.games) - game_num))

        logger.debug("Total memory used by the process: %s MB",
                     psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        logger.debug("Time required for the simulation: %s seconds", round(time.time() - start_sim))


if __name__ == '__main__':
    main()
