import numpy as np
from scipy.optimize import minimize

# This is the amortized price
d_prime = 0.5 / (365 * 3 * 96)
xi = 0.08
k = 0.02  # 20% error

def u_net(y, h):
    if y <= 0 or (y * xi) < d_prime or h < 0:
        return np.inf  # Return a high value if y is negative or the condition for h positive is violated
    return y * (1 - np.exp(-xi * h)) - d_prime * h


def opt_alloc(y):
    return -(1 / xi) * np.log(d_prime / (y * xi))


# Given the amortized price, the xi value and the percentage of expected miss estimation
# We want to know the value of y, that makes underestimating on k percent and overestimating in k percent
# Produce the same amount of loss in monetary units
def objective(y):
    h_under = opt_alloc(y * (1 - k))
    h_over = opt_alloc(y * (1 + k))
    U_net_over_over = u_net(y * (1 + k), h_over) * (365 * 3 * 96)
    U_net_under_under = u_net(y * (1 - k), h_under) * (365 * 3 * 96)

    return abs(U_net_over_over - U_net_under_under)


initial_guesses = np.asarray(10)
result = minimize(
    objective,
    initial_guesses,
    bounds=[((d_prime / xi) * 2, None)],  # y must be positive
    options={'ftol': 1e-16, 'eps': 2e-8, 'disp': False}
)

print("Result y is:", result.x)
