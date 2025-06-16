import numpy as np
import matplotlib.pyplot as plt

# Parámetros globales
rho = 1  # escala lineal de todas las curvas
d = 0.5    # coste marginal constante
p = 1    # exponente en x^p

# Dominio de x
x = np.linspace(0.1, 10, 500)

# ---- Definición de las nuevas funciones ----
# Óptimo lineal en rho: h_tilde(x) = (rho / x^p) * ln(x^p / d)
h_tilde = (rho / x**p) * np.log(x**p / d)

# Utilidad máxima lineal en rho:
# U_tilde(x) = rho * [1 - (d / x^p)] - d * h_tilde
U_tilde = rho * (1 - d / x**p) - d * h_tilde

# Curva de referencia lineal en rho: h_mod_tilde(x) = rho * [U_tilde(x)]^2
h_mod_tilde = rho * U_tilde**2

# Coste dependiente de x para imponer h = h_mod_tilde
d_x = rho * x**p * np.exp(- (x**p / rho) * h_mod_tilde)

# Utilidad evaluada en la referencia, lineal en rho:
# U_mod_tilde(x) = rho * (1 - exp(- (x^p/rho) * h_mod_tilde)) - d_x * h_mod_tilde
U_mod_tilde = rho * (1 - np.exp(- (x**p / rho) * h_mod_tilde)) - d_x * h_mod_tilde

# Filtrar donde
mask = (h_tilde > 0) & (U_tilde > 0)
x_masked = x[mask]

# ---- Gráfica de h_tilde y U_tilde ----
plt.figure(figsize=(6, 4))
plt.plot(x_masked, h_tilde[mask], label=r'$\tilde h^*(x)$', linewidth=2)
plt.plot(x_masked, U_tilde[mask], label=r'$\tilde U^*(x)$', linewidth=2)
plt.xlabel('x')
plt.ylabel('Valor')
plt.title('Óptimo y utilidad con escala lineal en $\\rho$')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ---- Gráfica de h_mod_tilde y U_mod_tilde ----
#plt.figure(figsize=(6, 4))
#plt.plot(x, h_mod_tilde, label=r'$\tilde h_{\mathrm{mod}}(x)$', linewidth=2)
#plt.plot(x, U_mod_tilde, label=r'$\tilde U_{\mathrm{mod}}(x)$', linewidth=2)
#plt.xlabel('x')
#plt.ylabel('Valor')
#plt.title('Curva de referencia y utilidad modificada con escala lineal en $\\rho$')
#plt.legend()
#plt.grid(True)
#plt.tight_layout()
#plt.show()
