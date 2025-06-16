import numpy as np
import matplotlib.pyplot as plt

# Parámetros del modelo
m = 5.0
d = 1.0
h_bar = 1.5

# Coeficiente 'a' de la función f(h)
a = (m + d * h_bar**2) / h_bar

# Definición de las funciones h_int(A), h^*(A) y U^*(A)
def h_int(A):
    # Óptimo interior según la ecuación (3)
    return (a - A) / (2 * d)

def h_star(A):
    # Óptimo con plateau: min(h_int(A), h_bar)
    return np.minimum(h_int(A), h_bar)

def U_of_h(h):
    # Utilidad U(h) por tramos
    return np.where(h <= h_bar, a * h - d * h**2, m)

def U_star(A):
    # Utilidad en el óptimo
    return U_of_h(h_star(A))

# Rango de valores de A para evaluar (por ejemplo, de 0 a 5)
A_vals = np.linspace(0, 5, 200)
h_int_vals = h_int(A_vals)
h_star_vals = h_star(A_vals)
U_star_vals = U_star(A_vals)

# Determinar límites del plateau
A_min = 0.0
A_max = (m - d * h_bar**2) / h_bar  # valor ~1.83 en este caso

# Graficar h_int(A) y h^*(A)
plt.figure()
plt.plot(A_vals, h_int_vals, 'y--', label="h_int(A)")
plt.plot(A_vals, h_star_vals, 'r-', label="h^*(A)")
plt.axvspan(A_min, A_max, color='gray', alpha=0.3, label="plateau")
plt.xlabel("A")
plt.ylabel("Asignación óptima h")
plt.legend()
plt.title("h_int(A) y h^*(A)")

# Graficar U^*(A)
plt.figure()
plt.plot(A_vals, U_star_vals, 'g-', label="U^*(A)")
plt.axvspan(A_min, A_max, color='gray', alpha=0.3, label="plateau")
plt.xlabel("A")
plt.ylabel("Utilidad óptima U^*")
plt.legend()
plt.title("U^*(A) en función de A")

plt.show()