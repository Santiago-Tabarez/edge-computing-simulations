import numpy as np
import matplotlib.pyplot as plt

# Used for Figure 6
# Chart to study how varying ξ affects the optimal allocation

cpu_price = 0.5
horizon = 365 * 3
daily_time_slots = 96
time_slots_in_horizon = horizon * daily_time_slots
amortized_price = cpu_price / time_slots_in_horizon
y = 0.0001189  #fig 6
# y = 0.0727   #fig 7

xi_s = np.linspace(0.04, 1, 1000)  # Fig 6
# xi_s = np.linspace(0.0000645, 0.01, 1000) # Fig 7



optimal_allocation = np.log(cpu_price / (time_slots_in_horizon * y * xi_s)) / -xi_s

plt.figure(figsize=(10, 8))
plt.plot(xi_s, optimal_allocation, label='Optimal Allocation', linewidth=2)


plt.xlabel('ξ', fontsize=14, fontweight='bold')
plt.ylabel('Allocation in millicores', fontsize=14, fontweight='bold')
plt.title('Optimal Allocation for y = 0.0727', fontsize=16, fontweight='bold')
plt.legend(fontsize=12)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()
