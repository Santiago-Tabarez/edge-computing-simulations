import math

import numpy as np


def u_net(h, load, xi, beta, d_prime, p, q, r, s):
    """
    Calcula U_net según la siguiente fórmula:

        U_net = beta * load * (1 - exp(-xi * h / A)) - d_prime * h
    donde
        A = load^p * xi^q * beta^r * d_prime^s.

    Parámetros:
      h       : Variable de asignación (float)
      load    : Carga (float)
      xi      : Parámetro xi (float)
      beta    : Parámetro beta (float)
      d_prime : Parámetro d' (float)
      p, q, r, s : Exponentes (floats)

    Retorna:
      U_net (float)
    """
    A = (load ** p) * (xi ** q) * (beta ** r) * (d_prime ** s)
    return beta * load * (math.exp(-xi * h / A)) - d_prime * h


def exp_argument(h, load, xi, beta, d_prime, p, q, r, s):
    """
    Calcula el argumento del exponencial:

        E(h) = - (xi * h) / A,
    donde
        A = load^p * xi^q * beta^r * d_prime^s.

    Parámetros:
      h       : Variable de asignación (float)
      load    : Carga (float)
      xi      : Parámetro xi (float)
      beta    : Parámetro beta (float)
      d_prime : Parámetro d' (float)
      p, q, r, s : Exponentes (floats)

    Retorna:
      E (float) : El argumento del exponencial.
    """
    A = (load ** p) * (xi ** q) * (beta ** r) * (d_prime ** s)
    return -xi * h / A


def equilibrium_h(load, xi, beta, d_prime, p, q, r, s):
    """
    Calcula el valor de h en equilibrio (h_eq), es decir, el valor
    que anula la derivada de U_net respecto a h, usando la siguiente
    fórmula:

         h = - (A/xi) * ln((d_prime * A) / (beta * load * xi))

    donde
         A = load^p * xi^q * beta^r * d_prime^s.

    Parámetros:
      load, xi, beta, d_prime, p, q, r, s:
          los parámetros y exponentes según la función.

    Retorna:
      h_eq (float)
    """
    A = (load ** p) * (xi ** q) * (beta ** r) * (d_prime ** s)
    ratio = (beta * load * xi) / (-d_prime * A)
    if ratio <= 0:
        raise ValueError("El argumento del logaritmo es no positivo. Verifique los parámetros de entrada.")
    h_eq = (A / xi) * math.log(ratio)
    return h_eq


# Ejemplo de uso:
if __name__ == '__main__':
    # Valores de los parámetros:
    load = 500000
    beta = 1.5e-6
    d_prime = -4.76e-6  # Ejemplo de valor para d_prime

    #xi = (1 / (900 * beta * load))
    # xi = d_prime * np.exp(1)/(beta*load)
    xi = -((d_prime * np.exp(1)) / (beta * load))
    #xi = 0.00008


   # h_val = 1000  # Valor de h para evaluar U_net y exp_argument

    # Valores de los exponentes
    p = 0  # Ejemplo: p = 0 default
    q = 0  # Ejemplo: q = 0 default con 1 su peso en el allocation es cero
    r = 0  # Ejemplo: r = 0 default
    s = 0  # Ejemplo: s = 0 default


    h_eq = equilibrium_h(load, xi, beta, d_prime, p, q, r, s)
    # Calcular el argumento del exponencial
    exp_val = exp_argument(h_eq, load, xi, beta, d_prime, p, q, r, s)
    # Calcular U_net para h_val
    unet_value = u_net(h_eq, load, xi, beta, d_prime, p, q, r, s)
    # Calcular el valor de equilibrio h_eq
    print("El argumento del exponencial es:", exp_val)
    print("U_net(h) =", unet_value)
    print("Equilibrium h =", h_eq)



