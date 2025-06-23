import logging.config
from math import factorial
from itertools import combinations
from controller.game_controller.generic_game_controller import GenericGameController
from controller.i_game_controller import IGameController
from model.coalition import Coalition
from model.network_owner import NetworkOwner
from utils.combinations_and_permutations import CombinationsAndPermutations

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

                # sol, utilities, cpu_price, opt = ggc.calculate_coal_payoff(game, coal)
                utility_ts, net_utility_ts, allocation_ts, effective_price = ggc.calculate_coal_payoff(game, coal)
                # If this is the grand coalition
                if len(game.players) == len(col):
                    ggc.create_grand_coalition(game, utility_ts, net_utility_ts, allocation_ts, effective_price)


            else:
                coal.allocation = [0] * len(col)
                coal.utilities = [0] * len(col)
                coal.coalition_payoff = 0

            game.coalitions.append(coal)


    @staticmethod
    def players_contribution(game):

        # number of players
        n = game.amount_of_players
        # list of players and map to indices
        players = list(game.players)
        idx_map = {p: idx for idx, p in enumerate(players)}

        # construct payoff map for all subsets (default 0)
        payoff_map = {}
        for r in range(n + 1):
            for combo in combinations(range(n), r):
                payoff_map[frozenset(combo)] = 0.0

        # fill actual payoffs from game.coalitions
        for coalition in game.coalitions:
            key = frozenset(idx_map[p] for p in coalition.players)
            payoff_map[key] = coalition.coalition_payoff

        # debug: log payoff_map to verify input
        # logger.info("Shapley debug - payoff_map: %s", payoff_map)

        # precompute factorials
        factorials = {i: factorial(i) for i in range(n + 1)}
        total_fact = factorials[n]

        # compute Shapley values
        shapley = [0.0] * n
        for i in range(n):
            for S, v_S in payoff_map.items():
                if i not in S:
                    T = S | {i}
                    v_T = payoff_map[T]
                    s = len(S)
                    weight = (factorials[s] * factorials[n - s - 1]) / total_fact
                    shapley[i] += weight * (v_T - v_S)

        game.grand_coalition.shapley_value =  [x for arr in shapley for x in arr.tolist()]
        logger.info("Players payoff (Shapley value) vector is %s", game.grand_coalition.shapley_value )


    # Now that we have the needed allocation for the grand coalition and each player contribution to that coalition (Shapley value)
    # We need to calculate how much each player needs to pay (or receive) from the coalition to make the initial investment
    @staticmethod
    def how_much_revenue_payment(game):

        gcc = GenericGameController()
        gcc.players_revenue_and_payment(game, game.grand_coalition.total_cpu_price)
