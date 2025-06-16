import logging
import numpy as np
from controller.game_controller.generic_game_controller import GenericGameController
from model.game import Game


logger = logging.getLogger(__name__)


class Sol(dict):
    def __init__(self, x, fun):
        super().__init__({'x': x, 'fun': fun})
        self.x = x
        self.fun = fun

    def __getitem__(self, key):
        return super().__getitem__(key)


class DeterministicAdditiveValueGameController:

    @staticmethod
    def calculate_coal_payoff(game: Game):
        # amortized cost per slot
        d_slot = game.fixed_price / (game.years * 365 * game.daily_timeslots)
        # total number of slots
        T = game.years * 365 * game.daily_timeslots

        allocations = []
        gross_utils = []
        total_gross = 0.0
        total_alloc = 0.0

        for p in game.players[1:]:
            # average load per slot
            load = np.sum(p.load_function) / game.daily_timeslots

            # exponents for [l, b, x, p]
            l_e = game.load_exponent[0]
            b_e = game.beta_exponent[0]
            x_e = game.xi_exponent[0]
            p_e = game.price_exponent[0]

            xi = p.xi
            beta = p.benefit_factor

            # saturation coefficient C = xi^x_e · load^l_e · beta^b_e · (d_slot)^p_e
            C = (xi ** x_e) * (load ** l_e) * (beta ** b_e) * (d_slot ** p_e)

            # first-order condition argument
            arg = (load * beta * C) / d_slot

            if arg <= 1.0:
                h_star = 0.0
                slot_u = 0.0
            else:
                # optimal allocation h*
                h_star = np.log(arg) / C
                # utility per slot at h*
                slot_u = load * beta * (1 - np.exp(-C * h_star)) #- d_slot * h_star

            total_u = slot_u * T

            allocations.append(h_star)
            gross_utils.append(total_u)
            total_gross += total_u
            total_alloc += h_star

        # append sum of all h*
        allocations.append(total_alloc)

        sol = Sol(x=allocations, fun=-total_gross)
        GenericGameController().create_grand_coalition(
            game, sol, gross_utils, None, None
        )

    @staticmethod
    def players_contribution(game: Game):
        # Network owner contribution is half of total payoff
        contributions = [sum(p.net_utility for p in game.players[1:]) / 2]
        # Service providers contribution
        contributions += [p.net_utility / 2 for p in game.players[1:]]

        game.grand_coalition.shapley_value = contributions
        logger.info("Players contribution (Shapley value) vector is: %s", contributions)

    @staticmethod
    def how_much_revenue_payment(game: Game):
        gcc = GenericGameController()
        gcc.players_revenue_and_payment(game, game.grand_coalition.total_cpu_price)
