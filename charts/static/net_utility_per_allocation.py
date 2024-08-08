import numpy as np
import matplotlib.pyplot as plt

# Used for Figure 1, 2, 3
# Chart to study how varying allocation affects the net utility

# Initial values taken from the article simulations
beta_i = 1.5e-06
avg_load = 48530.0
xi = 0.08
cpu_price = 0.5
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots
amortized_price = cpu_price / time_slots_in_horizon
y = beta_i * avg_load  # figure 1
# y = 0.00011891  # figure 2
# y = y / 100  # figure 3
y = 0.00011891

optimal_allocation = np.log(cpu_price / (time_slots_in_horizon * y * xi)) / -xi

optimal_gross_ut = y * (1 - np.exp(-xi * optimal_allocation)) * time_slots_in_horizon
# Allocation cost
optimal_alloc_cost = cpu_price * optimal_allocation
# Net utility
optimal_net_ut = optimal_gross_ut - optimal_alloc_cost
print('Optimal allocation', optimal_allocation)
print('Net utility', optimal_net_ut)


# Now that we have the optimal allocation and optimal net utility
# We want to study how net utility varies for different allocation


# Range of h^i (allocated resources)
allocated_resources = np.linspace(0, 200, 1000)  # Adjust the range as necessary
# Gross utility function
gross_utility = y * (1 - np.exp(-xi * allocated_resources)) * time_slots_in_horizon
# Allocation cost
allocation_cost = cpu_price * allocated_resources
# Net utility function
net_utility = gross_utility - allocation_cost

plt.figure(figsize=(10, 8))
plt.plot(allocated_resources, gross_utility, label='Gross Utility', linewidth=2)
plt.plot(allocated_resources, allocation_cost, label='Allocation Cost', linewidth=2)
plt.plot(allocated_resources, net_utility, label='Net Utility', linewidth=2)


plt.xlabel('Allocation in millicores', fontsize=14, fontweight='bold')
plt.ylabel('Dollars', fontsize=14, fontweight='bold')
plt.title('Utilities per Allocation', fontsize=16, fontweight='bold')
plt.legend(fontsize=12)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()
