import numpy as np
import matplotlib.pyplot as plt

# Used for Figure 4 and 5
# Chart to study how varying y affects the optimal allocation

xi = 0.08
cpu_price = 0.5
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots
amortized_price = cpu_price / time_slots_in_horizon


#y_value = np.linspace(0.001, 1, 1000)  # Fig 4
y_value = np.linspace(0.001, 10, 1000)  # Fig 5

optimal_allocation = np.log(cpu_price / (time_slots_in_horizon * y_value * xi)) / -xi

plt.figure(figsize=(10, 8))
plt.plot(y_value, optimal_allocation, label='Optimal Allocation', linewidth=2)


plt.xlabel('y =  β * avg_load', fontsize=14, fontweight='bold')
plt.ylabel('Allocation in millicores', fontsize=14, fontweight='bold')
plt.title('Optimal Allocation for ξ=0.08', fontsize=16, fontweight='bold')
plt.legend(fontsize=12)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()
