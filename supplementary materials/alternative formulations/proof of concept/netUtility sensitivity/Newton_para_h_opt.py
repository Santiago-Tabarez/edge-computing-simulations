import numpy as np

def find_h_star(m_values, A, d, h0=1.0, tol=1e-8, max_iter=100):
    """
    Encuentra h* que satisface:
        sum_{t=1}^T exp(-d*A/m(t) * h) = T/A
    usando Newton–Raphson.

    Parámetros:
      m_values : array_like
        Lista o array de valores m(t) para t = 1..T.
      A        : float
        Señal estratégica A > 0.
      d        : float
        Coste lineal d > 0.
      h0       : float, opcional
        Valor inicial para h.
      tol      : float, opcional
        Tolerancia para la convergencia |h_{n+1} - h_n|.
      max_iter : int, opcional
        Número máximo de iteraciones.

    Retorna:
      h_star : float
        La raíz aproximada h*.
    """
    m = np.array(m_values, dtype=float)
    T = len(m)

    def f(h):
        # f(h) = sum_t exp(-d*A/m(t) * h) - T/A
        return np.sum(np.exp(-d * A / m * h)) - T / A

    def df(h):
        # f'(h) = sum_t [(-d*A/m(t)) * exp(-d*A/m(t) * h)]
        return np.sum((-d * A / m) * np.exp(-d * A / m * h))

    h = h0
    for i in range(max_iter):
        fh = f(h)
        dfh = df(h)
        if abs(dfh) < 1e-12:
            raise RuntimeError("Derivada cercana a cero en iteración {}".format(i))
        h_new = h - fh / dfh
        if abs(h_new - h) < tol:
            return h_new
        h = h_new

    raise RuntimeError("No convergió tras {} iteraciones".format(max_iter))

# Ejemplo de uso:
m_values = [1.0, 2.0, 1.5, 2.5]  # ejemplo de m(t) para T=4
A = 3.0
d = 1.0

h_star = find_h_star(m_values, A, d, h0=1.0)
print("h* =", h_star)
