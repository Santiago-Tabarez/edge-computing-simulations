class ServiceProvider:

    def __init__(self, player_id, player_name, avg_load, benefit_factor, xi, sigma, hyperparameters, load_function, load_function_id):
        self.player_id = player_id
        self.player_name = player_name
        self.avg_load = avg_load  # average load that will be modeled by load function
        self.benefit_factor = benefit_factor  # beta factor for utility function
        self.xi = xi  # term to shape of the diminishing return, how fast it saturates to upper bound
        self.allocation = 0  # allocated resources in milli-cores
        self.sigma_load = sigma
        self.hyperparameters = hyperparameters
        self.load_function_id = load_function_id
        self.load_function = load_function
        self.payoff = 0
        self.utility = 0


