import logging.config

from controller.GameController.additive_value_calculation_controller import AdditiveValueCalculationController
from controller.GameController.generic_game_controller import GenericGameController
from controller.i_game_controller import IGameController
from model.game import Game
from controller.optimization_controller import Optimization

logger = logging.getLogger(__name__)


class AdditiveValueGameController(IGameController):

    # Calculate only the grand coalition payoff
    @staticmethod
    def calculate_coal_payoff(game: Game):
        avc = AdditiveValueCalculationController()
        avc.calculate_optimal_allocations(game)

        # FIXME DEPRECATED
        ggc = GenericGameController()

        # We remove the NO from the optimization since it doesn't use any edge resources
        opt = Optimization(game.min_cpu_price, game.max_cpu_price, game.min_cores_hosted, game.max_cores_hosted,
                           game.daily_timeslots, game.years * 365, game.players[1:])
        # Calculate the maximum value for grand coalition
        sol, utilities, price = opt.maximize_coalition_payoff()

        # In this case we create only the grand coalition
        ggc.create_grand_coalition(game, sol, utilities, opt.weighted_by_alloc_cpu_price, opt)

    # Since the value function is additive (Theorem 1)
    # And the Shapley value of N.O is equal to the sum of all S.P. Shapley values (Theorem 2)
    # This is the same as calculating the Shapley value and much faster
    @staticmethod
    def players_contribution(game: Game):
        # Network owner contribution is half of total payoff (Theorem 2)
        players_contribution = [sum(player.payoff for player in game.players[1:]) / 2]
        # Service providers contribution
        for player in game.players[1:]:
            players_contribution.append(player.payoff / 2)

        game.grand_coalition.shapley_value = players_contribution

        logger.info("Players contribution (Shapley value) vector is: %s:", players_contribution)

    # Now that we have the needed allocation for the grand coalition and each player contribution to that coalition (Shapley value)
    # We need to calculate how much each player needs to pay (or receive) from the coalition to make the initial investment
    @staticmethod
    def how_much_revenue_payment(game: Game):
        gcc = GenericGameController()
        gcc.players_revenue_and_payment(game, game.grand_coalition.total_cpu_price)
