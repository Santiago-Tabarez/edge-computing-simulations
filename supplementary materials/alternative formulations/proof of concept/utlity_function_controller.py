"""
# This class have different utility functions, not just the exponential saturation equation with different
# auxiliar function but completely different saturation and cost functions, we are not implementing this for now


import numpy as np


def evaluate(case, beta, load, d, x, gross_utility, h=None):

    # If h is None, returns (h*, U(h*)) for the given parameters.
    # If h is provided, returns U(h) only.

    # Default decay_scale for cases that don't override it
    decay_scale = 1.0
    m = None

    # 0) Original case, should give the same results as the original utility equation
    # 0 < xi < 1
    if case == 0:
        beta_flag = 0
        d_exp_lineal = 1
        h_exp_lineal = 1
        d_exp_exp = 0
        load_exp = 0
        beta_exp = 0
        xi_exp_exp = 0  # no extra x factor
        h_exp_exp = 1

        # Base case: c(x,d) = x
        def shape_exponent(x_val):
            return x_val

        def decay_weight(x_val):
            return 1.0

    # 1)
    # 1 < x < 10
    elif case == 1:
        beta_flag = 0
        d_exp_lineal = 1
        h_exp_lineal = 1
        d_exp_exp = 1
        load_exp = 1
        beta_exp = 1
        xi_exp_exp = 0  # no extra x factor
        h_exp_exp = 1

        # Base case: c(x,d) = x
        def shape_exponent(x_val):
            return x_val

        def decay_weight(x_val):
            return 1.0


    elif case == 2:
        beta_flag = 1
        d_exp_lineal = 1
        h_exp_lineal = 1
        d_exp_exp = 0
        load_exp = 1
        beta_exp = 1
        xi_exp_exp = 1
        h_exp_exp = 1

        m = 1.0

        def shape_exponent(x_val):
            return 1.0

        def decay_weight(x_val):
            return 1.0

    elif case == 3:
        x = x/2
        beta_flag = 0
        P = 1
        x0 = 0.5
        decay_scale = (1 + x0) ** P * np.exp((1 + x0) ** P)
        d_exp_lineal = 1
        h_exp_lineal = 1
        d_exp_exp = 1
        load_exp = 1
        beta_exp = 1
        xi_exp_exp = 0
        h_exp_exp = 1


        def shape_exponent(x_val):
            return (1 + x_val) ** P

        def decay_weight(x_val):
            return decay_scale * np.exp(-shape_exponent(x_val))

    elif case == 4:
        beta_flag = 0
        P = 2
        x0 = 0.5
        decay_scale = (1 + x0) ** P * np.exp((1 + x0) ** P)
        d_exp_lineal = 1
        h_exp_lineal = 1
        d_exp_exp = 0
        load_exp = 0
        beta_exp = 0
        xi_exp_exp = 1
        h_exp_exp = 1

        def shape_exponent(x_val):
            return (1 + x_val) ** P

        def decay_weight(x_val):
            return decay_scale * np.exp(-shape_exponent(x_val))


    else:
        raise ValueError("case must be 0, 1, 2 or 3")

    # 2) Shared helpers
    def benefit_saturation(x_val):
        return x_val / (x_val + m) if beta_flag == 1 else 1.0

    def decay_rate_coefficient(x_val, d_val):
        # for case 0, base = x_val, load_exp etc. zero => c=x
        base = shape_exponent(x_val) if beta_flag == 0 else decay_scale
        c_val = base ** (1 - beta_flag)
        c_val *= decay_scale ** beta_flag
        c_val *= d_val ** d_exp_exp
        c_val *= load ** (-load_exp)
        c_val *= beta ** (-beta_exp)
        return c_val

    def Utility(h_val, x_val, d_val, gross):
        prefactor = load * beta
        exp_arg = -decay_rate_coefficient(x_val, d_val) * (h_val ** h_exp_exp) * (x_val ** xi_exp_exp)
        benefit = prefactor * (benefit_saturation(x_val) ** beta_flag) * (1 - np.exp(exp_arg))
        if gross:
            return benefit
        else:
            cost = (d_val ** d_exp_lineal) * (h_val ** h_exp_lineal) * (decay_weight(x_val) ** (1 - beta_flag))
            return benefit - cost

    def h_star(x_val, d_val):
        C = decay_rate_coefficient(x_val, d_val)
        numerator = load * beta * (benefit_saturation(x_val) ** beta_flag) * C * (x_val ** xi_exp_exp)
        denominator = (d_val ** d_exp_lineal) * (decay_weight(x_val) ** (1 - beta_flag))
        if case == 2:
            return (1 / C) * np.log(numerator / denominator) * 1000
        return (1 / C) * np.log(numerator / denominator)

    def U_star(x_val, d_val, gross):
        h_opt_val = h_star(x_val, d_val)
        return Utility(h_opt_val, x_val, d_val, gross)

    # 3) Return results
    if h is None:
        return h_star(x, d), U_star(x, d, gross_utility)

    return Utility(h, x, d, gross_utility)
"""