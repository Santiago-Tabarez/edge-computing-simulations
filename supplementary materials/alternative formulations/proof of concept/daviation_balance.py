import numpy as np
import matplotlib.pyplot as plt

# Definimos el dominio: x > 0 (evitamos x=0 para evitar división por cero)
x = np.linspace(0.001, 1, 400)

# Calculamos y = (1/x) * log(1/x)
y = (1/x) * np.log(1/x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, label=r'$y = \frac{1}{x}\log\left(\frac{1}{x}\right)$')
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.xlabel('x')
plt.ylabel('y')
plt.title('Gráfica de la función y = (1/x) * log(1/x)')
plt.legend()
plt.grid(True)
plt.show()