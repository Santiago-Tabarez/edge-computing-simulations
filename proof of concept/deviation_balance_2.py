import numpy as np
from scipy.optimize import minimize


class DeviationBalance:

    def __init__(self, cpu_price: float, time_slots_in_horizon: int, xi: float):
        self.cpu_price = cpu_price
        self.time_slots_in_horizon = time_slots_in_horizon
        self.xi = xi

    def net_utility_impact(self, x, y, unit_price, expected_deviation, deviation_type):
        # Adjusted y value based on deviation_type
        adjusted_y = y * x + (expected_deviation * y * x) * (1 if deviation_type else -1)

        # Calculate allocation based on adjusted y
        allocation = np.log(self.cpu_price / (time_slots_in_horizon * adjusted_y * self.xi)) / -self.xi

        # Net utility for adjusted y
        net_utility_adjusted = time_slots_in_horizon * adjusted_y * (
                    1 - np.exp(-self.xi * allocation)) - unit_price * allocation

        # Net utility for original y (scaled by x)
        net_utility_original = time_slots_in_horizon * (y * x) * (
                    1 - np.exp(-self.xi * allocation)) - unit_price * allocation

        # Calculate the absolute difference in utilities
        # This is the opportunity cost when "y" is underestimated (deviation_type = True)
        # This is lost for no not used resources when "" overestimation cost when "y" is underestimated (deviation_type = True)
        utility_difference = abs(net_utility_adjusted - net_utility_original)

        return utility_difference

    def find_balance_point(self, y):
        # Function to solve: net_utility_impact == 0
        xi = self.xi
        dp = self.cpu_price
        result = minimize(lambda x: np.abs(self.net_utility_impact(x, y, dp, 0.2, True)), x0=np.asarray(1),
                          bounds=[(1.0e-12, None)])
        over = result.x
        print()
        result = minimize(lambda x: np.abs(self.net_utility_impact(x, y, dp, 0.2, False)), x0=np.asarray(1),
                          bounds=[(1.0e-12, None)])
        under = result.x
        result = over - under
        print("average", (over + under) / 2)
        print("y", y)
        return result



beta_i = 1.5e-6
avg_load = 48530.0
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots
initial_y = np.asarray(beta_i * avg_load)

bd = DeviationBalance(0.5, time_slots_in_horizon, 0.08)

aux = minimize(bd.find_balance_point, initial_y, bounds=[(1.0e-10, None)])

print(aux.x)
