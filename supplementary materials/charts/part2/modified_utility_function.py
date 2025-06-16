import numpy as np
import matplotlib.pyplot as plt
from math import e

# Parameters
d = 1e-4
b = 1e-4
beta = 0.01  # rate of phi(x) saturation
l0 = 60000

# Define phi(x) that increases from 1 to e
def phi(x):
    return 1 + (e - 1) * (1 - np.exp(-beta * x))

# Closed‐form optimum
def h_star_mod(d, b, l, x):
    ph = phi(x)
    return (l / ph) * np.log(b * ph / d)

def U_mod(d, b, l, x):
    h = h_star_mod(d, b, l, x)
    ph = phi(x)
    return l * b * (1 - np.exp(-ph * h / l)) - d * h

# Base values
x0 = 60
h_base = h_star_mod(d, b, l0, x0)
U_base = U_mod(d, b, l0, x0)

print(f"Optimal h*: {h_base:.4f}")
print(f"Optimal U(h*): {U_base:.4f}")

# Sensitivity vs load
l_vals = np.linspace(1e3, 1.2e5, 100)
h_vals_l = [h_star_mod(d, b, lv, x0) for lv in l_vals]
U_vals_l = [U_mod(d, b, lv, x0) for lv in l_vals]

plt.figure()
plt.plot(l_vals, h_vals_l)
plt.xlabel("Load l")
plt.ylabel("h*")
plt.title("h* vs Load")

plt.figure()
plt.plot(l_vals, U_vals_l)
plt.xlabel("Load l")
plt.ylabel("U(h*)")
plt.title("U(h*) vs Load")

# Sensitivity vs x
x_vals = np.linspace(1, 120, 100)
h_vals_x = [h_star_mod(d, b, l0, xv) for xv in x_vals]
U_vals_x = [U_mod(d, b, l0, xv) for xv in x_vals]

plt.figure()
plt.plot(x_vals, h_vals_x)
plt.xlabel("x")
plt.ylabel("h*")
plt.title("h* vs x")

plt.figure()
plt.plot(x_vals, U_vals_x)
plt.xlabel("x")
plt.ylabel("U(h*)")
plt.title("U(h*) vs x")

plt.tight_layout()
plt.show()
