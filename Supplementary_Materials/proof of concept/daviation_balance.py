import numpy as np
from scipy.optimize import  minimize


class DeviationBalance:

    def __init__(self, cpu_price: float, time_slots_in_horizon: int, xi: float):
        self.cpu_price = cpu_price
        self.time_slots_in_horizon = time_slots_in_horizon
        self.xi = xi

    def net_utility_impact(self, x, y, unit_price, expected_deviation, deviation_type):

        y = y * x
        expected_dev = expected_deviation * y

        # Real "y" is expected_deviation above
        if deviation_type:
            y_over = y + expected_dev
            over_alloc = np.log(self.cpu_price / (time_slots_in_horizon * y_over * self.xi)) / -self.xi
            U_net_over_over = time_slots_in_horizon * y_over * (1 - np.exp(- self.xi * over_alloc)) - unit_price * over_alloc
            U_net_over_avg = time_slots_in_horizon * y * (1 - np.exp(-self.xi * over_alloc)) - unit_price * over_alloc
            ret = abs(U_net_over_over - U_net_over_avg)
            # print("y", y_over)
        # Real "y" is expected_deviation below
        else:
            y_under = y - expected_dev
            under_alloc = np.log(self.cpu_price / (time_slots_in_horizon * y_under * self.xi)) / -self.xi
            U_net_under_under = time_slots_in_horizon * y_under * (
                        1 - np.exp(-self.xi * under_alloc)) - unit_price * under_alloc
            U_net_under_avg = time_slots_in_horizon * y * (1 - np.exp(-self.xi * under_alloc)) - unit_price * under_alloc
            ret = abs(U_net_under_under - U_net_under_avg)
            # print("y", y_under)

        # print("ret", ret)
        # print("x", x)

        return ret

    def find_balance_point(self, y):
        # Function to solve: net_utility_impact == 0
        xi = self.xi
        dp = self.cpu_price
        result = minimize(lambda x: np.abs(self.net_utility_impact(x, y, dp, 0.2, True)), x0=np.asarray(1),
                          bounds=[(1.0e-12, None)])
        over = result.x
        result = minimize(lambda x: np.abs(self.net_utility_impact(x, y, dp, 0.2, False)), x0=np.asarray(1),
                          bounds=[(1.0e-12, None)])
        under = result.x
        result = over - under
        print("over", over, "under", under)
        print("y", y)
        return result


# Example function call (to be uncommented in production)

beta_i = 1.5e-6
avg_load = 48530.0
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots
initial_y = np.asarray(beta_i * avg_load)

bd = DeviationBalance(0.5, time_slots_in_horizon, 0.08)

aux = minimize(bd.find_balance_point, initial_y, bounds=[(1.0e-10, None)])

print(aux.x)
