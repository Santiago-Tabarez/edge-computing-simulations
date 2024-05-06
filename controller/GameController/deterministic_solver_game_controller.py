from math import factorial

from scipy.optimize import minimize
import logging.config

from controller.GameController.generic_game_controller import GenericGameController
from controller.i_game_controller import IGameController
from model.coalition import Coalition
from model.network_owner import NetworkOwner
from utils.combinations_and_permutations import CombinationsAndPermutations
from utils.cpu_cost import CPUCost

logger = logging.getLogger(__name__)


class DeterministicSolverGameController(IGameController):

    @staticmethod
    def calculate_coal_payoff(game):

        ggc = GenericGameController()
        # Iterate over the combination of players that will create all possible coalitions, skip the first one since it is the empty one
        for col in CombinationsAndPermutations.all_combinations(game.players)[1:]:

            coal = Coalition(col)
            no = next((obj for obj in col if isinstance(obj, NetworkOwner)), None)
            # If N.O. is in the coalition and is not the only one
            if no and len(col) > 1:

                sol, utilities, cpu_price, opt = ggc.calculate_coal_payoff(game, coal)
                # If this is the grand coalition
                if len(game.players) == len(col):
                    ggc.create_grand_coalition(game, sol, utilities, cpu_price, opt)

            else:
                coal.allocation = [0] * len(col)
                coal.utilities = [0] * len(col)
                coal.coalition_payoff = 0

            game.coalitions.append(coal)

    @staticmethod
    def players_contribution(game):

        # Pre-compute factorials
        factorials = {i: factorial(i) for i in range(game.amount_of_players + 1)}
        # Create a mapping from each subset to its immediate supersets that include exactly one additional player
        subset_to_superset = {}
        for coalition in game.coalitions:
            coalition_set = frozenset(coalition.players)
            if coalition_set not in subset_to_superset:
                subset_to_superset[coalition_set] = []
            for other_coalition in game.coalitions:
                other_set = frozenset(other_coalition.players)
                if coalition_set < other_set and len(other_set) - len(coalition_set) == 1:
                    subset_to_superset[coalition_set].append((other_set, other_coalition.coalition_payoff))

        # Calculate Shapley values
        shapley_values = [0] * game.amount_of_players

        for player_idx, player in enumerate(game.players):
            for coalition in game.coalitions:
                if player not in coalition.players:
                    coalition_set = frozenset(coalition.players)
                    s_size = len(coalition_set)
                    if coalition_set in subset_to_superset:
                        for superset, superset_payoff in subset_to_superset[coalition_set]:
                            if player in superset:
                                contribution = superset_payoff - coalition.coalition_payoff
                                weight = factorials[s_size] * factorials[game.amount_of_players - s_size - 1]
                                shapley_values[player_idx] += weight * contribution

        # Normalize the Shapley values
        total_factorial = factorials[game.amount_of_players]
        shapley_values = [val / total_factorial for val in shapley_values]

        game.grand_coalition.shapley_value = shapley_values

        logger.info("Players contribution (Shapley value) vector is %s:", game.grand_coalition.shapley_value)

    # Now that we have the needed allocation for the grand coalition and each player contribution to that coalition (Shapley value)
    # We need to calculate how much each player needs to pay (or receive) from the coalition to make the initial investment
    @staticmethod
    def how_much_revenue_payment(game):

        gcc = GenericGameController()
        gcc.players_revenue_and_payment(game, game.grand_coalition.total_cpu_price)
