import numpy as np
from pysr import PySRRegressor
import matplotlib.pyplot as plt

# Simulemos datos: función real (que no vamos a decirle)
def f_true(x):
    return np.log(x) + np.sqrt(x)

# Derivadas de la función verdadera
def f_prime(x):
    return 1/x + 0.5/np.sqrt(x)

def f_double_prime(x):
    return -1/(x**2) - 0.25 / (x**(3/2))

# Dominio de entrada
x = np.linspace(0.1, 5, 100).reshape(-1, 1)

# Valores conocidos (como si fueran tus datos)
y = f_true(x).ravel()
dy = f_prime(x).ravel()
ddy = f_double_prime(x).ravel()

# Concatenamos todos los objetivos
y_combined = np.concatenate([y, dy, ddy])
x_combined = np.concatenate([x, x, x])

# Creamos un vector de pesos: podés ponderar más la función, o sus derivadas
weights = np.concatenate([
    np.ones_like(y),          # peso para f(x)
    0.5 * np.ones_like(dy),   # menos peso a la derivada si querés
    0.25 * np.ones_like(ddy)  # aún menos peso a la segunda derivada
])

# Ajuste con PySR
model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["sqrt", "log", "exp"],
    model_selection="best",  # Elige la mejor fórmula
    loss="loss(x, y) = (x - y)^2",  # Error cuadrático
    verbosity=1,
    weights=weights,
)

model.fit(x_combined, y_combined)

# Mostrar la mejor fórmula encontrada
print(model)

# Evaluamos y graficamos
x_test = np.linspace(0.1, 5, 200).reshape(-1, 1)
y_pred = model.predict(x_test)

plt.plot(x_test, f_true(x_test), label="Función real", linestyle="--")
plt.plot(x_test, y_pred, label="Función encontrada por PySR")
plt.legend()
plt.grid()
plt.title("Ajuste simbólico con PySR")
plt.show()
