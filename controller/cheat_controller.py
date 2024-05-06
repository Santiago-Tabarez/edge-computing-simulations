import numpy as np

from controller.GameController.additive_value_game_controller import AdditiveValueGameController

import logging.config

from controller.i_game_controller import IGameController
from controller.simulation_controller import SimulationController

logger = logging.getLogger(__name__)


class CheatController:

    # For now this is only working with additive value functions
    @staticmethod
    def calculate_true_payoff_for_all_cheaters(gc: IGameController, game):

        for player in game.players[1:]:
            if player.true_load_function:

                if player.true_benefit_factor:
                    benefit_factor = player.true_benefit_factor
                    xi = player.true_xi
                else:
                    benefit_factor = player.benefit_factor
                    xi = player.xi
                utilities_sum = 0
                for load in player.true_load_function:
                    utilities_sum += benefit_factor * load * (1 - np.exp(-xi * player.allocation)) * game.years * 365
                utilities_sum -= game.fixed_price * player.allocation
                difference = utilities_sum - player.payoff
                liar_payoff = player.payoff
                logger.info("Player %s has a different load and/or utility function:", player.player_name)
                logger.info("The real player payoff (net utility) is %s: and the difference in payoff is %s:",
                            utilities_sum, difference)
                if difference > 0:
                    sc = SimulationController()
                    id_current_player = player.player_id
                    logger.info(
                        "Since difference is > 0 then is worth to explore what would happen if player was honest")
                    logger.info(
                        "This is the result of the game using the real load and utility functions:\n")
                    # Now we set the true values as if they were the declared one and run the simulation again
                    player.benefit_factor = benefit_factor
                    player.xi = xi
                    player.load_function = player.true_load_function
                    # TODO load function id ? save result in database
                    sc.simulate_game(gc, game)
                    current_player = next((p for p in game.players if p.player_id == id_current_player), None)

                    dif = utilities_sum - current_player.payoff
                    if dif >= 0:
                        logger.info("Giving fake information resulted in player profit of: %s:", dif)
                    if dif < 0:
                        logger.info("Giving fake information resulted in player lose of: %s:", dif)

        return
