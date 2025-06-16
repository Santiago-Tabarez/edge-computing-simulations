import numpy as np
import matplotlib.pyplot as plt

# rho: potencial de monetización; a mayor rho, la curva de beneficio se satura más arriba
rho = 1.0

# p: exponente para acelerar la saturación de la utilidad en x bajos;
# al aumentar p, k(x) crece más rápido con x
p = 1

# x0: valor de referencia de x en el que queremos que h* = 0
x0 = 1

# k(x): tasa de decrecimiento efectiva en el término exponencial de la utilidad
# a mayor x, k(x) crece y provoca saturación más rápida en h
def k(x):
    return (1 + x) ** p

# calcular k(x0) para fijar a de modo que h*(x0) = 0
k0 = k(x0)

# a: escala del costo; definido como a = k0 * exp(k0) para que
# cuando x = x0 se cumpla f(x0) = k(x0) y por tanto h*(x0) = 0
a = k0 * np.exp(k0)

# f(x): función de costo lineal por unidad de h
# f(x) = a * exp(-k(x)); a medida que x crece, k(x) crece y f(x) disminuye
def f(x):
    return a * np.exp(-k(x))

# U_B(h, x): utilidad original desarrollada completamente
# U(h,x) = rho * (1 - exp(-k(x) * h / rho)) - h * f(x)
# - el primer término es el beneficio con retornos decrecientes en h
# - el segundo término es el costo lineal en h, que depende de x
# Aunque no usemos esta implementación directa, queda aquí definida
# def U_original(h, x):
#     return rho * (1 - np.exp(-k(x) * h / rho)) - h * f(x)

# h_B_star(x): condición de primer orden despejada
# h* = (rho / k(x)) * ln( k(x) / f(x) )
# mayor diferencia entre k(x) y f(x) implica un h* más alto
def h_B_star(x):
    return (rho / k(x)) * np.log(k(x) / f(x))

# U_B_star(x): utilidad evaluada en h*(x)
def U_B_star(x):
    h_opt = h_B_star(x)
    return rho * (1 - np.exp(-k(x) * h_opt / rho)) - h_opt * f(x)

# rango de valores de x para graficar
x = np.linspace(x0, 20, 500)

# filtrar solo donde h* es positivo
mask = h_B_star(x) > 0
x_pos = x[mask]

# calcular h* y U(h*) en puntos seleccionados
h_opt = h_B_star(x_pos)
U_opt = U_B_star(x_pos)

# graficar h* y U(h*) versus x
plt.figure()
plt.plot(x_pos, h_opt,    label='h* (óptimo)',      linewidth=2)
plt.plot(x_pos, U_opt,    label='U(h*) (utilidad)', linewidth=2)
plt.xlabel('x')
plt.ylabel('valor')
plt.title('Variante con k(x) = (1 + x)^p, p = {}'.format(p))
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
