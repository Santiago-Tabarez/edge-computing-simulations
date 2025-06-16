import numpy as np
import matplotlib.pyplot as plt

# Default parameters
default_params = {
    'l': 100000,  # load (millicores)
    # 100...100
    'beta': 1e-06,  # monetization factor
    'd_prime': 5e-06,  # per-millicore amortized price
    'mu': 10,  # requests per second per millicore
    # 0.01..10
    'slot_length': 900  # length of time-slot in seconds (e.g., 15 minutes)
}


def calibrations(params):
    """
    Compute calibrated parameters for each case:
    xi0  - saturation rate for Case 0
    xi1  - scaled saturation for Case 1
    lam2 - multiply-λ for Case 2
    lam3 - inverse-λ for Case 3
    """
    l = params['l']
    beta = params['beta']
    d = params['d_prime']
    mu = params['mu']
    slot = params['slot_length']
    rho = l * beta

    xi0 = mu
    xi1 = mu * slot / l
    lam2 = xi1 * rho / d
    lam3 = (l / (mu * slot)) * (d / rho)

    return xi0, xi1, lam2, lam3


def h_star(case, params):
    l = params['l']
    beta = params['beta']
    d = params['d_prime']
    rho = l * beta
    xi0, xi1, lam2, lam3 = calibrations(params)

    if case == 0:
        return (1 / xi0) * np.log(rho * xi0 / d)
    elif case == 1:
        return (1 / xi1) * np.log(rho * xi1 / d)
    elif case == 2:
        return (rho / (d * lam2)) * np.log(lam2)
    elif case == 3:
        return (rho * lam3 / d) * (-np.log(lam3))
    else:
        raise ValueError("Unknown case")


def U_star(case, params):
    l = params['l']
    beta = params['beta']
    d = params['d_prime']
    rho = l * beta
    xi0, xi1, lam2, lam3 = calibrations(params)
    h = h_star(case, params)

    if h <= 0:
        return np.nan
    if case == 0:
        return rho * (1 - np.exp(-xi0 * h)) - d * h
    elif case == 1:
        return rho * (1 - np.exp(-xi1 * h)) - d * h
    elif case == 2:
        return rho * (1 - np.exp(- (d / rho) * lam2 * h)) - d * h
    elif case == 3:
        return rho * (1 - np.exp(- (d / rho) * (1 / lam3) * h)) - d * h


def plot_sensitivity(case, var_name, var_range, params=None, num=200):
    """
    Plot sensitivity of h* and U(h*) with respect to var_name over var_range for the given case.
    case: 0, 1, 2, or 3
    var_name: one of 'l','beta','d_prime','mu','slot_length'
    var_range: tuple (min, max)
    """
    if params is None:
        params = default_params
    var_vals = np.linspace(var_range[0], var_range[1], num)
    h_vals, U_vals, valid_vars = [], [], []

    for v in var_vals:
        p = params.copy()
        p[var_name] = v
        h = h_star(case, p)
        if h > 0:
            h_vals.append(h)
            U_vals.append(U_star(case, p))
            valid_vars.append(v)

    # Plot optimal allocation
    plt.figure()
    plt.plot(valid_vars, h_vals)
    plt.xlabel(var_name)
    plt.ylabel('Optimal allocation $h^*$')
    plt.title(f'Case {case}: $h^*$ vs {var_name}')
    plt.grid(True)
    plt.show()

    # Plot utility at optimum
    plt.figure()
    plt.plot(valid_vars, U_vals)
    plt.xlabel(var_name)
    plt.ylabel('Utility at optimal allocation $U(h^*)$')
    plt.title(f'Case {case}: $U(h^*)$ vs {var_name}')
    plt.grid(True)
    plt.show()






# Or define a helper function and call it
def plot_all_sensitivity(var_name, var_range):
    for case in [0, 1, 2, 3]:
        plot_sensitivity(case=case, var_name=var_name, var_range=var_range)



var_names = ['l', 'beta', 'mu', 'd_prime']
plot_all_sensitivity(var_names[2], (0.01, 5e-05))
