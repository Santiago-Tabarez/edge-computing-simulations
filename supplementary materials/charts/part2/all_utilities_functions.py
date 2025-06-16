import numpy as np
import matplotlib.pyplot as plt

# Updated default parameters
default_params = {
    'l': 50000,  # load (millicores)
    'beta': 1.5e-06,  # monetization factor
    'd_prime': 5.0e-06,  # marginal cost
}

# Map case to its diminishing‐return key
diminishing_map = {
    0: 'mu',
    1: 'xi1',
    2: 'lambda2',
    3: 'xi3'
}


def thresholds_and_peaks(params):
    """Compute threshold and peak for each case’s diminishing‐return parameter."""
    l = params['l']
    beta = params['beta']
    d = params['d_prime']
    rho = l * beta

    # Case 0: threshold μ > d/ρ, peak μ = e·(d/ρ)
    threshold_mu = d / rho
    peak_mu = np.e * (d / rho)

    # Case 1: threshold ξ1 > d/β, peak ξ1 = e·(d/β)
    threshold_xi1 = d / beta
    peak_xi1 = np.e * (d / beta)

    # Case 2: threshold λ2 > 0 (choose small positive), peak λ2 = 1/e
    threshold_lambda2 = 0.01  # small ε above 0
    peak_lambda2 = np.exp(-1)

    # Case 3: threshold ξ3 > d, peak ξ3 = e·d
    threshold_xi3 = d
    peak_xi3 = np.e * d

    return {
        0: (threshold_mu, peak_mu),
        1: (threshold_xi1, peak_xi1),
        2: (threshold_lambda2, peak_lambda2),
        3: (threshold_xi3, peak_xi3)
    }


def h_star(case, params):
    l = params['l']
    beta = params['beta']
    d = params['d_prime']
    rho = l * beta

    if case == 0:
        mu = params['mu']
        return (1.0 / mu) * np.log((rho * mu) / d)
    elif case == 1:
        xi1 = params['xi1']
        return (l / xi1) * np.log((beta * xi1) / d)
    elif case == 2:
        lam2 = params['lambda2']
        return (rho * lam2 / d) * (-np.log(lam2))
    elif case == 3:
        xi3 = params['xi3']
        return (rho / xi3) * np.log(xi3 / d)
    else:
        raise ValueError("Unknown case")


def U_star(case, params):
    l = params['l']
    beta = params['beta']
    d = params['d_prime']
    rho = l * beta

    # Extract whichever diminishing‐return parameter is present
    mu = params.get('mu', None)
    xi1 = params.get('xi1', None)
    lam2 = params.get('lambda2', None)
    xi3 = params.get('xi3', None)

    h_opt = h_star(case, params)
    if h_opt <= 0 or np.isnan(h_opt):
        return np.nan

    if case == 0:
        return rho * (1 - np.exp(-mu * h_opt)) - d * h_opt
    elif case == 1:
        return rho * (1 - np.exp(- (xi1 / l) * h_opt)) - d * h_opt
    elif case == 2:
        return rho * (1 - np.exp(- (d / (rho * lam2)) * h_opt)) - d * h_opt
    elif case == 3:
        return rho * (1 - np.exp(- (xi3 / rho) * h_opt)) - d * h_opt


def constraint_satisfied(case, params):
    beta = params['beta']
    l = params['l']
    rho = l * beta
    d = params['d_prime']

    mu = params.get('mu', None)
    xi1 = params.get('xi1', None)
    lam2 = params.get('lambda2', None)
    xi3 = params.get('xi3', None)

    if case == 0:
        return (rho * mu / d) > 1
    elif case == 1:
        return (beta * xi1 / d) > 1
    elif case == 2:
        return (lam2 > 0) and (lam2 < 1)
    elif case == 3:
        return xi3 > d
    else:
        return False


def plot_peak_centered(cases, params=None, num=300):
    """
    Plot h* and U(h*) vs diminishing‐return parameter for each case,
    with X‐range from threshold up to threshold + 3*(peak - threshold),
    so that one‐third is before the peak and two‐thirds after.
    """
    if params is None:
        params = default_params.copy()
    else:
        params = params.copy()

    thresholds_peaks = thresholds_and_peaks(params)

    if cases == 'all':
        case_list = [0, 1, 2, 3]
    else:
        case_list = cases if isinstance(cases, list) else [cases]

    for case in case_list:
        key = diminishing_map[case]
        threshold, peak = thresholds_peaks[case]
        # X‐axis up to threshold + 3*(peak - threshold)
        end = threshold + 3 * (peak - threshold)
        var_vals = np.linspace(threshold, end, num)

        h_vals = []
        U_vals = []
        valid_vars = []

        for v in var_vals:
            p = params.copy()
            p[key] = v
            if constraint_satisfied(case, p):
                h_val = h_star(case, p)
                U_val = U_star(case, p)
                if not np.isnan(h_val) and h_val > 0:
                    h_vals.append(h_val)
                    U_vals.append(U_val)
                    valid_vars.append(v)

        # Plot h* vs diminishing‐return parameter
        plt.figure(figsize=(8, 4))
        plt.plot(valid_vars, h_vals, linestyle='-')
        plt.xlabel(key)
        plt.ylabel('h*')
        plt.title(f'Case {case}: h* vs {key}')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot U(h*) vs diminishing‐return parameter
        plt.figure(figsize=(8, 4))
        plt.plot(valid_vars, U_vals, linestyle='-')
        plt.xlabel(key)
        plt.ylabel('U(h*)')
        plt.title(f'Case {case}: U(h*) vs {key}')
        plt.grid(True)
        plt.tight_layout()
        plt.show()


# Execute: plot all four cases with peak‐centered ranges
plot_peak_centered(cases='all')
