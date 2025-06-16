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
        return self.m * (x * h) / (1 + x * h)**2 - self.d * h

def plot_functions(model, funcs, v_ranges):
    for label, func in funcs.items():
        v_min, v_max = v_ranges[label]
        v_vals = np.linspace(v_min, v_max, 500)
        x_vals = (model.d / model.m) * v_vals
        y_vals = [func(x) for x in x_vals]

        plt.figure()
        plt.plot(v_vals, y_vals, label=label)
        if label == 'f2':
            plt.plot(v_vals, v_vals, '--', label='reference y=x')
        plt.xlabel('v')
        plt.ylabel(f"{label}(x)")
        plt.title(f"{label}(x) vs v")
        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    m = 1
    d = 4.76e-6
    model = UtilityModel(m, d)

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

    v_ranges = {
        'f1': (1, 200),
        'f2': (1, 6),
        'f3': (1, 4),
        'f4': (1, 1000),
        'f5': (1, 11),
        'f6': (1, 23),
        'f7': (0, 6),
        'f8': (2, 50),
    }

    plot_functions(model, funcs, v_ranges)
