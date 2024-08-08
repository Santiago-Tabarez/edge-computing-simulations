import numpy as np

# Initial values taken from the article simulations
beta_i = 1.5e-06
avg_load = 48530.0
xi = 0.08
cpu_price = 0.5
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots
y = beta_i * avg_load
estimation_error = 0.2  # 20% estimation error on y

optimal_alloc = np.log(cpu_price / (time_slots_in_horizon * y * xi)) / -xi
net_ut = y * (1 - np.exp(-xi * optimal_alloc)) * time_slots_in_horizon - cpu_price * optimal_alloc
print("Allocation for correct estimation of \"y\" is:", optimal_alloc, "Net utility for correct estimation is:", net_ut)
print()

y_over = y * (1 + estimation_error)
over_alloc = np.log(cpu_price / (time_slots_in_horizon * y_over * xi)) / -xi
print("SP allocation for a:", estimation_error * 100, "percent more of \"y\" is:", over_alloc)
net_ut_up_expect = y * (1 - np.exp(-xi * over_alloc)) * time_slots_in_horizon - cpu_price * over_alloc
print("If prediction is incorrect and \"y\" value is the originally expected, net utility is:", net_ut_up_expect)
net_ut_up_up = y_over * (1 - np.exp(-xi * over_alloc)) * time_slots_in_horizon - cpu_price * over_alloc
print("If prediction is correct and \"y\" value is:", estimation_error * 100, "above the originally expected, net utility is:", net_ut_up_up)
print("Opportunity cost is:", net_ut_up_up - net_ut)
print("Loss due to overestimation is:", net_ut - net_ut_up_expect)
print()

y_under = y * (1 - estimation_error)
under_alloc = np.log(cpu_price / (time_slots_in_horizon * y_under * xi)) / -xi
print("SP allocation for a:", estimation_error * 100, "percent less of \"y\" is:", under_alloc)
net_ut_down_expect = y * (1 - np.exp(-xi * under_alloc)) * time_slots_in_horizon - cpu_price * under_alloc
print("If prediction is incorrect and \"y\" value is the originally expected, net utility is:", net_ut_up_expect)
net_ut_down_down = y_under * (1 - np.exp(-xi * under_alloc)) * time_slots_in_horizon - cpu_price * under_alloc
print("If prediction is correct and \"y\" value is:", estimation_error * 100, "below the originally expected, net utility is:", net_ut_down_expect)
print("Potential opportunity cost is:", net_ut - net_ut_down_down)
print("Loss due to overestimation is:", net_ut - net_ut_down_expect)









