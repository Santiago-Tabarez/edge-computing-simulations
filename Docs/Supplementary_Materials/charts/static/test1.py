import numpy as np
import matplotlib.pyplot as plt

# Define the new U_net function
def U_net_vary_y(y, d_prime, xi):
    return y * (1 - d_prime / (y * xi)) + d_prime * (1 / xi) * np.log(d_prime / (y * xi))

# Set the values for d' and xi
d_prime = 1  # Given value
xi = 0.08  # Given value
y = 0.072  # Given value

# Generate a range of values for y (varying y while keeping xi fixed)
y_values = np.linspace(0.01, 0.5, 500)
U_net_values_vary_y = U_net_vary_y(y_values, d_prime, xi)

# Generate a range of values for xi (varying xi while keeping y fixed)
xi_values = np.linspace(0.01, 0.5, 500)
U_net_values_vary_xi = U_net_vary_y(y, d_prime, xi_values)

# Plotting U_net with varying y
plt.figure(figsize=(8, 6))
plt.plot(y_values, U_net_values_vary_y, label="Varying y, fixed xi = 0.08", color='b')
plt.title("Plot of U_net as y varies with fixed xi")
plt.xlabel("y")
plt.ylabel("U_net")
plt.grid(True)
plt.legend()
plt.show()

# Plotting U_net with varying xi
plt.figure(figsize=(8, 6))
plt.plot(xi_values, U_net_values_vary_xi, label="Varying xi, fixed y = 0.072", color='r')
plt.title("Plot of U_net as xi varies with fixed y")
plt.xlabel("xi")
plt.ylabel("U_net")
plt.grid(True)
plt.legend()
plt.show()
