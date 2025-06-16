import numpy as np
import matplotlib.pyplot as plt

# Define functions
def h_star(xi, rho, d):
    h = (1/xi) * np.log(rho * xi / d)
    return np.where(h > 0, h, np.nan)

def U_star(xi, rho, d):
    h = h_star(xi, rho, d)
    return rho * (1 - np.exp(-xi * h)) - d * h

# Ratios for ρ/d
ratios = [1, 2, 3, 5, 10]

# 1. h* vs ξ for different ρ/d ratios
plt.figure()
for r in ratios:
    xi_min = 1/r + 1e-6
    xis = np.linspace(xi_min, 5, 200)
    plt.plot(xis, h_star(xis, r, 1), label=f"ρ/d={r}")
plt.xlabel('ξ')
plt.ylabel('h*')
plt.title('Optimal allocation h* vs ξ for varying ρ/d')
plt.legend(title='ρ/d')
plt.show()

# 2. U(h*) vs ξ for the same ratios
plt.figure()
for r in ratios:
    xi_min = 1/r + 1e-6
    xis = np.linspace(xi_min, 5, 200)
    plt.plot(xis, U_star(xis, r, 1), label=f"ρ/d={r}")
plt.xlabel('ξ')
plt.ylabel('U(h*)')
plt.title('Optimal net utility U(h*) vs ξ for varying ρ/d')
plt.legend(title='ρ/d')
plt.show()

# 3. Heatmap of h*(ξ,ρ)
xis_grid = np.linspace(0.1, 5, 200)
rhos = np.linspace(0.1, 10, 200)
XI, RHO = np.meshgrid(xis_grid, rhos)
H = h_star(XI, RHO, 1)
plt.figure()
cs = plt.contourf(XI, RHO, H, levels=50)
plt.xlabel('ξ')
plt.ylabel('ρ')
plt.title('Heatmap of h*(ξ,ρ)')
plt.colorbar(cs, label='h*')
plt.show()

# 4. Heatmap of U(h*)(ξ,ρ)
U = U_star(XI, RHO, 1)
plt.figure()
cs = plt.contourf(XI, RHO, U, levels=50)
plt.xlabel('ξ')
plt.ylabel('ρ')
plt.title('Heatmap of U(h*)(ξ,ρ)')
plt.colorbar(cs, label='U(h*)')
plt.show()
