import math
import numpy as np
import matplotlib.pyplot as plt

class UtilityModel:
    def __init__(self, m, d):
        self.m = m
        self.d = d

    def f1(self, x):
        h = (1 / x) * math.log(self.m * x / self.d)
        return self.m * (1 - math.exp(-x * h)) - self.d * h

    def f2(self, x):
        h = self.m / self.d - 1 / x
        return self.m * math.log(1 + x * h) - self.d * h

    def f3(self, x):
        h = (self.m ** 2 * x) / (4 * self.d ** 2)
        return self.m * math.sqrt(x * h) - self.d * h

    def f4(self, x):
        h = (1 / x) * (math.sqrt(self.m * x / self.d) - 1)
        return self.m * (x * h) / (1 + x * h) - self.d * h

    def f5(self, x):
        h = (1 / x) * math.sqrt(self.m * x / self.d - 1)
        return self.m * math.atan(x * h) - self.d * h

    def f6(self, x):
        z = (-1 + math.sqrt(1 + 2 * self.m * x / self.d)) / 2
        h = z ** 2 / x
        return self.m * math.log(1 + math.sqrt(x * h)) - self.d * h

    def f7(self, x):
        h = (self.m * x / (3 * self.d)) ** 3
        return self.m * x * h ** (1/3) - self.d * h

    def f8(self, x):
        h = (1 / x) * (math.sqrt(self.m * x / (2 * self.d)) - 1)
        return self.m * (x * h) / (1 + x * h)**2  - self.d * h

# Instantiate model
m = 1
d = 4.76e-6
model = UtilityModel(m, d)

# Utility and allocation functions mapping
funcs = {
    'f1': model.f1,
    'f2': model.f2,
    'f3': model.f3,
    'f4': model.f4,
    'f5': model.f5,
    'f6': model.f6,
    'f7': model.f7,
    'f8': model.f8,
}

h_funcs = {
    'f1': lambda x: (1 / x) * np.log(model.m * x / model.d),
    'f2': lambda x: model.m / model.d - 1 / x,
    'f3': lambda x: (model.m**2 * x) / (4 * model.d**2),
    'f4': lambda x: (1 / x) * (np.sqrt(model.m * x / model.d) - 1),
    'f5': lambda x: (1 / x) * np.sqrt(model.m * x / model.d - 1),
    'f6': lambda x: ((-1 + np.sqrt(1 + 2 * model.m * x / model.d)) / 2)**2 / x,
    'f7': lambda x: (model.m * x / (3 * model.d))**3,
    'f8': lambda x: (1 / x) * (np.sqrt(model.m * x / (2 * model.d)) - 1),
}

# Updated v ranges
v_ranges = {
    'f1': (1, 200),
    'f2': (1, 10),   # extended to 10
    'f3': (1, 6),    # extended to 6
    'f4': (1, 1000),
    'f5': (1, 15),   # extended to 15
    'f6': (1, 50),   # extended to 50
    'f7': (0, 10),   # extended to 10
    'f8': (2, 50),
}

# Plot allocation (h) with log scale and utility (U) together, using distinct colors
for label, U_func in funcs.items():
    v_min, v_max = v_ranges[label]
    v_vals = np.linspace(v_min, v_max, 500)
    x_vals = (model.d / model.m) * v_vals

    h_vals = h_funcs[label](x_vals)
    U_vals = [U_func(x) for x in x_vals]

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    u_line, = ax1.plot(v_vals, U_vals, color='tab:blue', label='utility U')
    h_line, = ax2.plot(v_vals, h_vals, color='tab:orange', label='allocation h')
    ax2.set_yscale('log')

    ax1.set_xlabel('v')
    ax1.set_ylabel('utility U')
    ax2.set_ylabel('allocation h (log scale)')

    lines = [u_line, h_line]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left')

    ax1.set_title(f'{label}: utility and allocation vs v')
    plt.tight_layout()

plt.show()
