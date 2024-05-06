import logging
import matplotlib.pyplot as plt

import numpy as np

from model.game import Game

logger = logging.getLogger(__name__)


class AdditiveValueCalculationController:
    """
    @staticmethod
    def calculate_optimal_allocations(game: Game):
        cpu_price = game.fixed_price
        time_slots_in_horizon = game.years * 365 * game.daily_timeslots
        player_total_net_utility = 0
        total_allocation = 0
        for player in game.players[1:]:
            xi = player.xi
            xi = 0.001
            # First derivative
            optimal_allocation = np.log(cpu_price / (time_slots_in_horizon * player.benefit_factor * player.avg_load * xi)) / -xi
            #optimal_allocation = np.log(cpu_price / (time_slots_in_horizon * player.benefit_factor * player.avg_load * 2 * xi)) / -xi

            gross_utility = player.benefit_factor * player.avg_load * (
                        1 - np.exp(-xi * optimal_allocation)) * time_slots_in_horizon
            net_utility = gross_utility - cpu_price * optimal_allocation
            player.allocation = optimal_allocation
            player.utility = gross_utility
            player.payoff = net_utility
            player.payment = cpu_price * optimal_allocation / 2
            player.revenue = net_utility / 2 + player.payment
            player_total_net_utility += player.payoff
            total_allocation += player.allocation
            print("For player: ", player.player_name, "allocation is: ", player.allocation, "net utility is: ", player.payoff,
                  "Contribution is: ", player.payoff / 2, "payment is: ", player.payment, "and revenues is: ", player.revenue)


            cpu_prices = np.linspace(0.001, 2, 200)
            optimal_allocation_per_price = np.log(
                cpu_prices / (time_slots_in_horizon * player.benefit_factor * player.avg_load * xi)) / -xi

            #gross_utility_chart = player.benefit_factor * player.avg_load * (
            #        1 - np.exp(-xi * optimal_allocation)) * time_slots_in_horizon

            net_utility_chart = gross_utility - cpu_price * optimal_allocation

            plt.figure(figsize=(20, 16))
            plt.plot(cpu_prices, optimal_allocation_per_price, label='Logarithm of cpu_price')
            plt.xlabel('CPU Price')
            plt.ylabel('Logarithm of CPU Price')
            plt.title('Logarithmic Function Demonstration')
            plt.legend()
            plt.grid(True)
            plt.show()

        print("Network Owner contribution:  ", player_total_net_utility/2, "payment:", total_allocation*cpu_price/2, "revenue", player_total_net_utility/2 - total_allocation*cpu_price/2)
"""
    @staticmethod
    def calculate_optimal_allocations(game: Game):
        cpu_price = game.fixed_price
        time_slots_in_horizon = game.years * 365 * game.daily_timeslots
        players_total_net_utility = 0
        total_allocation = 0
        for p in game.players[1:]:
            # First derivative
            optimal_allocation = np.log(
                cpu_price / (time_slots_in_horizon * p.benefit_factor * p.avg_load * p.xi)) / -p.xi

            net_utility = p.benefit_factor * p.avg_load * (
                    1 - np.exp(-p.xi * optimal_allocation)) * time_slots_in_horizon - cpu_price * optimal_allocation

            p.allocation = optimal_allocation
            p.payoff = net_utility
            p.payment = cpu_price * optimal_allocation / 2
            p.revenue = net_utility / 2 + p.payment
            players_total_net_utility += p.payoff
            total_allocation += p.allocation
            print("For player: ", p.player_name, "allocation is: ", p.allocation, "net utility is: ",
                  p.payoff,
                  "Contribution is: ", p.payoff / 2, "payment is: ", p.payment, "and revenues is: ",
                  p.revenue)

        print("Network Owner contribution is:  ", players_total_net_utility / 2, "payment:",
              total_allocation * cpu_price / 2, "revenue",
              players_total_net_utility / 2 - total_allocation * cpu_price / 2)
