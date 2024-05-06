import random
import logging.config

from config import config
from controller.GameController.additive_value_game_controller import AdditiveValueGameController
from controller.GameController.generic_game_controller import GenericGameController
from controller.i_game_controller import IGameController
from model.coalition import Coalition
from model.network_owner import NetworkOwner

logger = logging.getLogger(__name__)


class EstimationSolverGameController(IGameController):

    @staticmethod
    def calculate_coal_payoff(game):

        # Only calculate the grand coalition
        additive_values_game_controller = AdditiveValueGameController()
        additive_values_game_controller.calculate_coal_payoff(game)

    # Approximating the Shapley value of players by using Monte Carlo methods
    @staticmethod
    def players_contribution(game):

        num_samples = config.MONTE_CARLO_VARIABLES['num_samples']
        # Used to calculate coalitions value
        ggc = GenericGameController()

        # Initialize cache for coalition values, to avoid recalculating same coalition value
        coalition_cache = {}
        shapley_values = [0] * game.amount_of_players

        # Function to generate a random coalition that includes a specific player and the N.O.
        def generate_coalition_with_player_and_no(all_players, specific_player):

            created_coalition_players = [specific_player]
            other_players = [p for p in all_players if p is not specific_player]
            for p in other_players:
                # We allways add the network owner to the coalition to avoid having a percentage of groups with-without it, not close to 50%
                # Since we only consider the coalitions with the N.O. the Shapley values of service providers will be the double
                if isinstance(p, NetworkOwner):
                    created_coalition_players = [p] + created_coalition_players
                elif random.random() < 0.5:  # With a 50% chance to add the player to the coalition
                    created_coalition_players.append(p)
            return created_coalition_players

        # Get the value of a coalition, no need for N.O. checking
        def coalition_value(g, coalition):
            # TODO check for ids order
            # Each player has a unique 'id' attribute
            coalition_key = tuple([p.player_id for p in coalition])
            if coalition_key in coalition_cache:
                return coalition_cache[coalition_key]
            else:
                if len(coalition) < 2:
                    return 0
                else:
                    sol, _, price, _ = ggc.calculate_coal_payoff(g, Coalition(coalition))
                    ret = -sol['fun']
                    coalition_cache[coalition_key] = ret
                    return ret

        for player_idx, player in enumerate(game.players):
            # Skip the N.O. and calculate it as the sum of other players, this gives consistency and precision
            if not isinstance(player, NetworkOwner):
                for _ in range(num_samples):
                    # Create a new random coalition for current player
                    coal_with_player = generate_coalition_with_player_and_no(game.players, player)
                    # Same coalition without current player
                    coal_without_player = [p for p in coal_with_player if p is not player]
                    # Value of the previous coalitions
                    payoff_with_player = coalition_value(game, coal_with_player)
                    payoff_without_player = coalition_value(game, coal_without_player)
                    # Calculate the marginal contribution of the player to the coalition
                    # No need for weighting since we are taking random coalitions
                    marginal_contribution = payoff_with_player - payoff_without_player
                    shapley_values[player_idx] += marginal_contribution

        # After accumulating contributions for all samples and service providers
        # Now we divide by num_samples to average the contributions
        for i in range(len(shapley_values)):
            if i > 0:
                shapley_values[i] /= num_samples * 2
        # Last we calculate the N.O. Shapley value by adding all other players Shapley values
        shapley_values[0] = sum(shapley_values[:])

        game.grand_coalition.shapley_value = shapley_values
        logger.info("Shapley value is (fair payoff vector): %s:", game.grand_coalition.shapley_value)

    # Now that we have the needed allocation for the grand coalition and each player contribution to that coalition (Shapley value)
    # We need to calculate how much each player needs to pay (or receive) from the coalition to make the initial investment
    @staticmethod
    def how_much_revenue_payment(game):

        gcc = GenericGameController()
        gcc.players_revenue_and_payment(game, game.grand_coalition.total_cpu_price)
