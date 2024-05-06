
import numpy as np
import matplotlib.pyplot as plt

# Constants
beta_i = 1.5e-07  # Benefit factor
avg_load = 48530  # Average load
xi = 0.08
cpu_price = 0.5
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots

optimal_allocation = np.log(cpu_price / (time_slots_in_horizon * beta_i * avg_load * xi)) / -xi
xis = np.linspace(0.001, 0.5, 1000)  # Adjust the range as necessary

# Gross utility function
gross_utility = beta_i * avg_load * (1 - np.exp(-xis * optimal_allocation)) * time_slots_in_horizon
# Allocation cost
allocation_cost = cpu_price * optimal_allocation

# Range of h^i (allocated resources)
allocated_resources = np.linspace(0, 3000, 1000)  # Adjust the range as necessary

# Gross utility function
gross_utility = beta_i * avg_load * (1 - np.exp(-xi * allocated_resources)) * time_slots_in_horizon
# Allocation cost
allocation_cost = cpu_price * allocated_resources
# Net utility function
net_utility = gross_utility - allocation_cost

plt.figure(figsize=(40, 40))
plt.plot(allocated_resources, gross_utility, label='Gross Utility')
plt.plot(allocated_resources, allocation_cost, label='Allocation Cost')
plt.plot(allocated_resources, net_utility, label='Net Utility')
plt.xlabel('Dollars')
plt.ylabel('Allocation')
plt.title('Utilities and Cost')
plt.legend()
plt.grid(True)
plt.show()
