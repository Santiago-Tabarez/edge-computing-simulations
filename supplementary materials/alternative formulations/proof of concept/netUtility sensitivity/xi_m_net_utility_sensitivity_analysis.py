import numpy as np
import matplotlib.pyplot as plt


class SensitivityAnalyzer:
    def __init__(self, d_prime=0.5 / (365 * 3 * 96)):
        self.d_prime = d_prime

    def optimal_h(self, m, xi):
        # Computes the optimal allocation h
        return (1 / xi) * np.log((m * xi) / self.d_prime)
       # return (1 - np.log((m * xi) / self.d_prime)) / (xi ** 2)
    def net_utility(self, m, xi):

        # Computes the net utility subject to the constraints  m > 0 and xi > (d_prime * e)/m.

        if xi <= (self.d_prime * np.e / m):
        #if self.d_prime > m * xi:
            return np.nan  # Constraint violation
        h = self.optimal_h(m, xi)
        #return h
        return m * (1 - np.exp(-xi * h)) - self.d_prime * h

    def global_sensitivity(self, m_range, xi_range, num_points=100):

        # Computes a grid of net utility values over the specified ranges for m and xi.

        m_values = np.linspace(*m_range, num_points)
        xi_values = np.linspace(*xi_range, num_points)
        M, XI = np.meshgrid(m_values, xi_values)
        utilities = np.zeros_like(M)

        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                utilities[i, j] = self.net_utility(M[i, j], XI[i, j])

        utilities_masked = np.ma.masked_invalid(utilities)
        return M, XI, utilities_masked

    def plot_sensitivity(self, M, XI, utilities, title):

        # Plots the net utility contour.
        fig, ax = plt.subplots(figsize=(10, 8))
        c = ax.contourf(M, XI, utilities, levels=100, cmap='viridis')
        ax.set_xlabel('m values')
        ax.set_ylabel(r'$\xi$ values')
        ax.set_title(title)
        fig.colorbar(c, ax=ax, label='Utility')
        plt.show()

    def run_analysis(self, mode='small'):
        # Runs the sensitivity analysis

        if mode == 'small':
            m_range = (1e-10, 0.5)
            #m_range = (0.01, 10)
            xi_range = (0.0001, 0.00025)
            #xi_range = (0.1, 10)
            title = 'Global Sensitivity of Net Utility (Small Range)'
        elif mode == 'large':
            m_range = (1e-8, 1)
            #m_range = (1, 10)
            xi_range = (1e-2, 1)
            #xi_range = (10, 20)
            title = 'Global Sensitivity of Net Utility (Large Range)'
        else:
            raise ValueError("Invalid mode. Choose 'small' or 'large'.")

        M, XI, utilities = self.global_sensitivity(m_range, xi_range)
        self.plot_sensitivity(M, XI, utilities, title)


analyzer = SensitivityAnalyzer()

analyzer.run_analysis(mode='small')

analyzer.run_analysis(mode='large')
