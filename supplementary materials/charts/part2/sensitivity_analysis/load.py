import numpy as np
import matplotlib.pyplot as plt

# Fixed default per-case diminishing parameters (found earlier)
fixed_params = {
    0: {'mu': 7.555783172758269e-05},       # Case 0
    1: {'xi1': 7.555783113310479},          # Case 1
    2: {'lambda2': 0.13234895510032824},    # Case 2
    3: {'xi3': 7.555783172758269e-05}       # Case 3
}

# Other constants
beta = 1.0e-05
d = 1.0e-05

# Range of load l (requests per time-slot)
l_vals = np.linspace(20000, 200000, 300)

# Prepare subplots: h*
fig_h, axes_h = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
# U(h*)
fig_U, axes_U = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)

titles_h = {
    0: "Case 0: $h^*$ vs $l$",
    1: "Case 1: $h^*$ vs $l$",
    2: "Case 2: $h^*$ vs $l$",
    3: "Case 3: $h^*$ vs $l$"
}
titles_U = {
    0: "Case 0: $U(h^*)$ vs $l$",
    1: "Case 1: $U(h^*)$ vs $l$",
    2: "Case 2: $U(h^*)$ vs $l$",
    3: "Case 3: $U(h^*)$ vs $l$"
}

for case in range(4):
    ax_h = axes_h[case // 2, case % 2]
    ax_U = axes_U[case // 2, case % 2]
    # Get fixed diminishing parameter
    if case == 0:
        mu = fixed_params[0]['mu']
    elif case == 1:
        xi = fixed_params[1]['xi1']
    elif case == 2:
        lam = fixed_params[2]['lambda2']
    elif case == 3:
        xi = fixed_params[3]['xi3']

    h_vals = []
    U_vals = []

    for l in l_vals:
        rho = l * beta
        # Compute h* for each case
        if case == 0:
            h_opt = (1.0 / mu) * np.log((rho * mu) / d)
        elif case == 1:
            h_opt = (l / xi) * np.log((beta * xi) / d)
        elif case == 2:
            h_opt = (rho * lam / d) * (-np.log(lam))
        elif case == 3:
            h_opt = (rho / xi) * np.log(xi / d)

        # Compute U(h*) for each case
        if case == 0:
            U_opt = rho * (1 - np.exp(-mu * h_opt)) - d * h_opt
        elif case == 1:
            U_opt = rho * (1 - np.exp(- (xi / l) * h_opt)) - d * h_opt
        elif case == 2:
            U_opt = rho * (1 - np.exp(- (d / (rho * lam)) * h_opt)) - d * h_opt
        elif case == 3:
            U_opt = rho * (1 - np.exp(- (xi / rho) * h_opt)) - d * h_opt

        h_vals.append(h_opt)
        U_vals.append(U_opt)

    # Plot h*
    ax_h.plot(l_vals, h_vals, color='tab:orange', linewidth=3)
    ax_h.set_title(titles_h[case], fontsize=14)
    ax_h.set_xlabel('$l$ (Requests per time-slot)', fontsize=12)
    ax_h.set_ylabel('$h^*$ (millicores)', fontsize=12)
    ax_h.grid(False)
    ax_h.locator_params(axis='x', nbins=5)

    # Plot U
    ax_U.plot(l_vals, U_vals, color='tab:blue', linewidth=3)
    ax_U.set_title(titles_U[case], fontsize=14)
    ax_U.set_xlabel('$l$ (Requests per time-slot)', fontsize=12)
    ax_U.set_ylabel('$U(h^*)$', fontsize=12)
    ax_U.grid(False)
    ax_U.locator_params(axis='x', nbins=5)

plt.show()
