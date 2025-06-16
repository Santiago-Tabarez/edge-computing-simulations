import numpy as np
import matplotlib.pyplot as plt

# Define functions
def h_star(xi, rho, d):
    h = (1/xi) * np.log(rho * xi / d)
    return np.where(h > 0, h, np.nan)

def U_star(xi, rho, d):
    h = h_star(xi, rho, d)
    return rho * (1 - np.exp(-xi * h)) - d * h

# 1. Peak-locus curve: xi_peak vs rho/d
ratios = np.linspace(0.1, 10, 200)
xi_peak = np.e / ratios  # xi_peak = e / (rho/d) for d=1
plt.figure()
plt.plot(ratios, xi_peak)
plt.xlabel('ρ/d')
plt.ylabel('ξ_peak')
plt.title('Peak-sensitivity ξ_peak vs ρ/d')
plt.show()

# 2. Marginal-return profiles: dh*/dξ and dU(h*)/dξ vs ξ
rho_d_values = [2, 5]
xis = np.linspace(0.2, 10, 500)
plt.figure()
for r in rho_d_values:
    # analytic derivative of h*
    dh_dxi = (1 - np.log(r * xis)) / xis**2
    plt.plot(xis, dh_dxi, label=f'dh*/dξ (ρ/d={r})')
plt.xlabel('ξ')
plt.ylabel('dh*/dξ')
plt.title('Marginal return of h* vs ξ')
plt.legend()
plt.show()

plt.figure()
for r in rho_d_values:
    U_vals = U_star(xis, r, 1)
    dU_dxi = np.gradient(U_vals, xis)
    plt.plot(xis, dU_dxi, label=f'dU/dξ (ρ/d={r})')
plt.xlabel('ξ')
plt.ylabel('dU(h*)/dξ')
plt.title('Marginal return of U(h*) vs ξ')
plt.legend()
plt.show()

# 3. Price-sensitivity sweep: h*(d') and U*(d') vs d'
d_prices = np.linspace(0.1, 10, 300)
xi_fixed = 1
rho_fixed = 5
plt.figure()
plt.plot(d_prices, h_star(xi_fixed, rho_fixed, d_prices))
plt.xlabel("d'")
plt.ylabel('h*')
plt.title("Allocation h* vs price d'")
plt.show()

plt.figure()
plt.plot(d_prices, U_star(xi_fixed, rho_fixed, d_prices))
plt.xlabel("d'")
plt.ylabel('U(h*)')
plt.title("Net utility U(h*) vs price d'")
plt.show()

# 4. Contour lines on heatmaps
xis_grid = np.linspace(0.1, 10, 200)
rhos = np.linspace(0.1, 10, 200)
XI, RHO = np.meshgrid(xis_grid, rhos)
H = h_star(XI, RHO, 1)
plt.figure()
cs = plt.contourf(XI, RHO, H, levels=50)
plt.contour(XI, RHO, H, levels=[1], linestyles='--')
plt.xlabel('ξ')
plt.ylabel('ρ')
plt.title('Heatmap of h*(ξ,ρ) with h*=1 contour')
plt.colorbar(cs, label='h*')
plt.show()

U = U_star(XI, RHO, 1)
plt.figure()
cs = plt.contourf(XI, RHO, U, levels=50)
plt.contour(XI, RHO, U - RHO/2, levels=[0], linestyles='--')
plt.xlabel('ξ')
plt.ylabel('ρ')
plt.title('Heatmap of U(h*)(ξ,ρ) with U=ρ/2 contour')
plt.colorbar(cs, label='U(h*)')
plt.show()

# 5. Elasticity surfaces: Eh_rho and Eh_xi
Eh_rho = 1 / (XI * H)
Eh_xi = (1 - np.log(RHO * XI)) / (XI * H)
plt.figure()
cs = plt.contourf(XI, RHO, Eh_rho, levels=50)
plt.xlabel('ξ')
plt.ylabel('ρ')
plt.title('Elasticity of h* w.r.t ρ')
plt.colorbar(cs, label='E_{h,ρ}')
plt.show()

plt.figure()
cs = plt.contourf(XI, RHO, Eh_xi, levels=50)
plt.xlabel('ξ')
plt.ylabel('ρ')
plt.title('Elasticity of h* w.r.t ξ')
plt.colorbar(cs, label='E_{h,ξ}')
plt.show()

# 6. Two-SP phase diagram: share_h1 > 0.5 boundary
omegas = np.linspace(0, 1, 200)
xis = np.linspace(0.1, 10, 200)
OMEGA, XI2 = np.meshgrid(omegas, xis)
l2, l1, beta_tot = 1, 4, 1
rho1 = l1 * (1 - OMEGA) * beta_tot
rho2 = l2 * OMEGA * beta_tot
h1 = h_star(XI2, rho1, 1)
h2 = h_star(XI2, rho2, 1)
share_h1 = h1 / (h1 + h2)
plt.figure()
cs = plt.contourf(OMEGA, XI2, share_h1, levels=[0, 0.5, 1])
plt.contour(OMEGA, XI2, share_h1, levels=[0.5], linestyles='--')
plt.xlabel('ω')
plt.ylabel('ξ')
plt.title('Phase diagram: Regions where SP1 allocation share >50%')
plt.colorbar(cs, label='share_{h1}')
plt.show()

