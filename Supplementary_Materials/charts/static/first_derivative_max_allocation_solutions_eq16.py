import numpy as np
import matplotlib.pyplot as plt

# This chart corresponds to equation 16

h = 89  # example fixed value for h

# Define xi and y ranges
xi = np.linspace(0.01, 2, 1000)  # avoid very small values near zero
y = np.linspace(0.001, 2, 1000)  # range for y values
Xi, Y = np.meshgrid(xi, y)

# Calculate the function values
Z = Y * (Xi * np.exp(-h * Xi))

# Create the plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
surface = ax.plot_surface(Xi, Y, Z, cmap='viridis')

fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)
ax.set_title(r'3D Surface Plot of f($\xi$, y) = y * ($\xi * e^{(-h * \xi )}$) where y= $\beta \cdot \l_{avg}$')
ax.set_xlabel(r'$\xi$')
ax.set_ylabel(r'$\beta \cdot l_{avg}$')
ax.set_zlabel('f(xi, y)')

plt.show()
