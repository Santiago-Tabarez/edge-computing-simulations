import numpy as np
import matplotlib.pyplot as plt

# Parámetros
rho = 2.0
d = 1.0

# Rango de valores para x
x = np.linspace(0.1, 10, 300)

# Ejemplos: (f(x), g(x), descripción)
examples = [
    (lambda x: np.exp(-x / (1 + x)), lambda x: 0 * x,
     r'Ex1: $f(x)=e^{-x/(1+x)},\; g(x)=0$'),
    (lambda x: 1 / (1 + x), lambda x: 0 * x,
     r'Ex2: $f(x)=1/(1+x),\; g(x)=0$'),
    (lambda x: 1 / (1 + x), lambda x: 0.5 * x,
     r'Ex3: $f(x)=1/(1+x),\; g(x)=0.5x$')
]

# Almacenar resultados
h_stars = []
U_norms = []
labels = []

# Cálculo para cada ejemplo
for f, g, label in examples:
    denom = d * f(x) + g(x)
    h_star = rho * np.log(1 / denom)
    U = rho * (1 - np.exp(-h_star / rho)) - d * h_star * f(x) - h_star * g(x)
    U_norm = U / np.max(U)

    h_stars.append(h_star / rho)  # Normalizar por rho
    U_norms.append(U_norm)
    labels.append(label)

# Graficar
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 8))

# Gráfico de h*(x)/rho
for h_rho, label in zip(h_stars, labels):
    ax1.plot(x, h_rho, label=label, linewidth=2)
ax1.set_title(r"$h^*(x)/\rho$", fontsize=14)
ax1.set_xlabel("x")
ax1.set_ylabel(r"$h^*/\rho$")
ax1.grid(True)
ax1.legend()

# Gráfico de utilidad normalizada
for U_norm, label in zip(U_norms, labels):
    ax2.plot(x, U_norm, label=label, linewidth=2)
ax2.set_title("Utilidad Normalizada $U(x)$", fontsize=14)
ax2.set_xlabel("x")
ax2.set_ylabel("Utilidad Normalizada")
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.show()
