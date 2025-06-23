import sys
import time
import os
import psutil
import logging
import logging.config

from config.config import LOGGING_CONFIG
from config import config
from controller.game_controller.non_additive.deterministic_non_additive_game_controller import \
    DeterministicSolverGameController
from controller.game_controller.non_additive.estimation_non_additive_game_controller import \
    EstimationSolverGameController
from controller.dao_controller import DAOController
from controller.game_builder_controller import GameBuilderController
from controller.game_controller.additive.deterministic_additive_value_game_controller import DeterministicAdditiveValueGameController
from controller.simulation_controller import SimulationController
from utils.check_for_errors import CheckForErrors
from utils.yaml_data_reader import YAMLDataReader


def main():

    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)

    daoC = DAOController()
    daoC.database_config()

    # build absolute path to the data folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    folder_path = os.path.join(project_root, 'simulations_to_process')

    yaml_games_data = YAMLDataReader.read_yaml_files(folder_path)

    additive_deterministic = config.VALUE_FUNCTION_MODE['additive_deterministic']
    non_additive_estimation = config.VALUE_FUNCTION_MODE['non_additive_estimation']
    non_additive_deterministic = config.VALUE_FUNCTION_MODE['non_additive_deterministic']

    if sum([additive_deterministic,  non_additive_deterministic, non_additive_estimation]) != 1:
        logger.error("Exactly one variable should be true in VALUE_FUNCTION_MODE")
        sys.exit(0)

    if additive_deterministic:
        logger.info("Following simulations will be executed assuming additive value function for coalitional value,"
                    "only grand coalition value will be calculated")
        gc = DeterministicAdditiveValueGameController()

    elif non_additive_estimation:
        logger.info(
            "Following simulations will be executed assuming non additive value function for coalitional values, "
            "it will return a estimation result, only some coalitions values will be calculated")
        gc = EstimationSolverGameController()

    elif non_additive_deterministic:
        logger.info("Following simulations will be executed assuming non additive value function for coalition "
                    "values, it will return a deterministic result, all coalitions values will be calculated")
        gc = DeterministicSolverGameController()

    else:
        return

    gmc = GameBuilderController()
    sc = SimulationController()
    # cfe = CheckForErrors()

    for game_data in yaml_games_data:

        start_sim = time.time()
        sim = gmc.create_games(game_data)

        logger.info("Total amount games to be processed: %s", len(sim.games))

        for game_num, game in enumerate(sim.games, ):
            start_game = time.time()
            game = sc.simulate_game(gc, game)
            game_num += 1
            daoC.save_game(game, sim)

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
