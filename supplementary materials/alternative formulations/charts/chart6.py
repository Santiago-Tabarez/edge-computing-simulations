import numpy as np
import matplotlib.pyplot as plt

rho = 2
x = np.linspace(0, 10, 500)

# Ejemplo 1: A1(x) = 2*x/(1+x)
A1 = 2 * x / (1 + x)
h1 = rho * A1 / 2
U1 = rho * A1**2 / 4

plt.figure()
plt.plot(x, h1, label='h* (racional)')
plt.plot(x, U1, label='U(h*) (racional)')
plt.xlabel('x')
plt.ylabel('Valor')
plt.title('Ejemplo 1: A(x)=2·x/(1+x)')
plt.legend()
plt.grid(True)

# Ejemplo 2: A2(x) = 2*(1 - exp(-x))
A2 = 2 * (1 - np.exp(-x))
h2 = rho * A2 / 2
U2 = rho * A2**2 / 4

plt.figure()
plt.plot(x, h2, label='h* (exponencial)')
plt.plot(x, U2, label='U(h*) (exponencial)')
plt.xlabel('x')
plt.ylabel('Valor')
plt.title('Ejemplo 2: A(x)=2·(1−e^(−x))')
plt.legend()
plt.grid(True)

plt.show()
