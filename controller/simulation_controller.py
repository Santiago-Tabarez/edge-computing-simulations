import logging
import os
import time

import psutil

from controller.i_game_controller import IGameController
from model.game import Game
from model.simulation import Simulation
from utils.cpu_cost import CPUCost

logger = logging.getLogger(__name__)


class SimulationController:

    @staticmethod
    def simulate_game(gc: IGameController, game: Game):
        start_game = time.time()
        gc.calculate_coal_payoff(game)
        logger.debug("Time required for calculating maximizing grand coalition value: %s seconds",
                     round(time.time() - start_game))

        start_shap = time.time()
        gc.players_contribution(game)
        logger.debug("Time required for calculating players contribution: %s seconds",
                     round(time.time() - start_shap))

        start_rev_pay = time.time()
        gc.how_much_revenue_payment(game)
        logger.debug("Time required for calculating players payments and revenues: %s seconds",
                     round(time.time() - start_rev_pay))

        return game
