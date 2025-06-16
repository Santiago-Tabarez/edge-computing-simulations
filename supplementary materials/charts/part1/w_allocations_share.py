import numpy as np
import matplotlib.pyplot as plt

# Parameters
l1, l2 = 4.0, 1.0
d = 1.0
beta_tot = 2.0  # 2 * d
xi = 900

omegas = np.linspace(0.5, 1.0, 200)

# Prepare arrays
share_alloc1 = np.zeros_like(omegas)
share_alloc2 = np.zeros_like(omegas)
share_pay1 = np.zeros_like(omegas)
share_pay2 = np.zeros_like(omegas)

for i, w in enumerate(omegas):

    beta1 = (1 - w) * beta_tot
    beta2 = w * beta_tot
    print(beta1, beta2)
    rho1 = l1 * beta1
    rho2 = l2 * beta2

    # optimal allocations

    h1 = (1 / xi) * np.log(rho1 * xi / d) if rho1 * xi > d else 0
    h2 = (1 / xi) * np.log(rho2 * xi / d) if rho2 * xi > d else 0



    # share allocation
    total_h = h1 + h2
    share_alloc1[i] = 100 * (h1 / total_h) if total_h > 0 else 50
    share_alloc2[i] = 100 - share_alloc1[i]

    if i == 1:
        print(share_alloc1[i],  share_alloc2[i])

    # net utilities
    U1 = rho1 * (1 - np.exp(-xi * h1)) - d * h1
    U2 = rho2 * (1 - np.exp(-xi * h2)) - d * h2
    total_U = U1 + U2

    # share payoffs of coalition value
    share_pay1[i] = 100 * (U1 / total_U) if total_U > 0 else 50
    share_pay2[i] = 100 - share_pay1[i]

# Plot Allocation Share
plt.figure(figsize=(6, 4))
plt.plot(omegas, share_alloc1, label='SP1 Allocation Share')
plt.plot(omegas, share_alloc2, label='SP2 Allocation Share')
plt.xlabel('ω')
plt.ylabel('Allocation Share (%)')
plt.title('CPU Allocation Share vs ω')
plt.legend()
plt.show()

# Plot Payoff Share
plt.figure(figsize=(6, 4))
plt.plot(omegas, share_pay1, label='SP1 Payoff Share')
plt.plot(omegas, share_pay2, label='SP2 Payoff Share')
plt.xlabel('ω')
plt.ylabel('Payoff Share (%)')
plt.title('Coalition Payoff Share vs ω')
plt.legend()
plt.show()
