import numpy as np
import matplotlib.pyplot as plt

# Chart to study how varying y affects the net utility
# We consider always the optimal allocation

# Initial values taken from the article simulations
#beta_i = 1.5e-06
#avg_load = 48530.0
xi = 0.08
cpu_price = 0.5
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots
amortized_price = cpu_price / time_slots_in_horizon

y_values = np.linspace(0, 0.0005, 1000)


optimal_allocation = np.log(cpu_price / (time_slots_in_horizon * y_values * xi)) / -xi
optimal_gross_ut = y_values * (1 - np.exp(-xi * optimal_allocation)) * time_slots_in_horizon
# Allocation cost
optimal_alloc_cost = cpu_price * optimal_allocation
# Net utility
optimal_net_ut = optimal_gross_ut - optimal_alloc_cost

print('Optimal allocation and Net utility pairs:')
for alloc, net_ut in zip(optimal_allocation, optimal_net_ut):
    print(f'Optimal allocation: {alloc}, Net utility: {net_ut}')

# Now that we have the optimal allocation and optimal net utility
# We want to study how net utility varies for different allocation

plt.figure(figsize=(10, 8))
#plt.plot(y_values, gross_utility, label='Gross Utility', linewidth=2)
#plt.plot(y_values, allocation_cost, label='Allocation Cost', linewidth=2)
plt.plot(y_values, optimal_net_ut, label='Net Utility', linewidth=2)


plt.xlabel('Allocation in millicores', fontsize=14, fontweight='bold')
plt.ylabel('Dollars', fontsize=14, fontweight='bold')
plt.title('Utilities per Allocation', fontsize=16, fontweight='bold')
plt.legend(fontsize=12)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()
