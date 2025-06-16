import numpy as np
import matplotlib.pyplot as plt

# Updated default parameters as provided by the user
default_params = {
    'l': 100000,  # load (requests)
    'beta': 1.0e-05,  # monetization factor
    'd_prime': 1.0e-05,  # new marginal cost
}

# Map case to its diminishing-return key
diminishing_map = {
    0: 'mu',
    1: 'xi1',
    2: 'lambda2',
    3: 'xi3'
}

# Map case to Greek label
greek_label = {
    0: r'$\mu$',
    1: r'$\xi$',
    2: r'$\lambda$',
    3: r'$\xi$'
}


def thresholds_and_peaks(params):
    """Compute threshold and peak for each case’s diminishing-return parameter."""
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

    h_opt = h_star(case, params)
    if h_opt <= 0 or np.isnan(h_opt):
        return np.nan

    if case == 0:
        mu = params['mu']
        return rho * (1 - np.exp(-mu * h_opt)) - d * h_opt
    elif case == 1:
        xi1 = params['xi1']
        return rho * (1 - np.exp(- (xi1 / l) * h_opt)) - d * h_opt
    elif case == 2:
        lam2 = params['lambda2']
        return rho * (1 - np.exp(- (d / (rho * lam2)) * h_opt)) - d * h_opt
    elif case == 3:
        xi3 = params['xi3']
        return rho * (1 - np.exp(- (xi3 / rho) * h_opt)) - d * h_opt


def constraint_satisfied(case, params):
    beta = params['beta']
    l = params['l']
    rho = l * beta
    d = params['d_prime']

    if case == 0:
        mu = params['mu']
        return (rho * mu / d) > 1
    elif case == 1:
        xi1 = params['xi1']
        return (beta * xi1 / d) > 1
    elif case == 2:
        lam2 = params['lambda2']
        return (lam2 > 0) and (lam2 < 1)
    elif case == 3:
        xi3 = params['xi3']
        return xi3 > d
    else:
        return False


# Prepare 2x2 plots for h* and U(h*)
fig_h, axes_h = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
fig_U, axes_U = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)

titles_h = {
    0: "Case 0: $h^*$ vs " + greek_label[0],
    1: "Case 1: $h^*$ vs " + greek_label[1],
    2: "Case 2: $h^*$ vs " + greek_label[2],
    3: "Case 3: $h^*$ vs " + greek_label[3]
}
titles_U = {
    0: "Case 0: $U(h^*)$ vs " + greek_label[0],
    1: "Case 1: $U(h^*)$ vs " + greek_label[1],
    2: "Case 2: $U(h^*)$ vs " + greek_label[2],
    3: "Case 3: $U(h^*)$ vs " + greek_label[3]
}

thresholds_peaks = thresholds_and_peaks(default_params)

for case in range(4):
    ax_h = axes_h[case // 2, case % 2]
    ax_U = axes_U[case // 2, case % 2]
    key = diminishing_map[case]
    threshold, peak = thresholds_peaks[case]

    # For cases 0,1,3: X up to 4*peak (300% beyond peak).
    # For case 2: unchanged (threshold → threshold + 3*(peak - threshold)).
    if case in [0, 1, 3]:
        start = threshold
        end = 4 * peak
    else:
        start = threshold
        end = threshold + 3 * (peak - threshold)

    var_vals = np.linspace(start, end, 300)

    h_vals = []
    U_vals = []
    valid_vars = []

    for v in var_vals:
        p = default_params.copy()
        p[key] = v
        if constraint_satisfied(case, p):
            h_val = h_star(case, p)
            U_val = U_star(case, p)
            if not np.isnan(h_val) and h_val > 0:
                h_vals.append(h_val)
                U_vals.append(U_val)
                valid_vars.append(v)

    # Plot h*
    ax_h.plot(valid_vars, h_vals, color='tab:orange', linewidth=3)
    ax_h.set_title(titles_h[case], fontsize=14)
    ax_h.set_xlabel(greek_label[case], fontsize=12)
    ax_h.set_ylabel('$h^*$ (millicores)', fontsize=12)
    ax_h.grid(False)
    if case == 0:
        ax_h.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    else:
        ax_h.locator_params(axis='x', nbins=5)

    # Plot U(h*)
    ax_U.plot(valid_vars, U_vals, color='tab:blue', linewidth=3)
    ax_U.set_title(titles_U[case], fontsize=14)
    ax_U.set_xlabel(greek_label[case], fontsize=12)
    ax_U.set_ylabel('$U(h^*)$', fontsize=12)
    ax_U.grid(False)
    if case == 0:
        ax_U.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    else:
        ax_U.locator_params(axis='x', nbins=5)

plt.show()
