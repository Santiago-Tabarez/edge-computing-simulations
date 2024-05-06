class ServiceProvider:

    def __init__(self, player_id, player_name, avg_load, benefit_factor, xi, sigma, hyperparameters, load_function, load_function_id):
        self.player_id = player_id
        self.player_name = player_name
        self.allocation = 0  # allocated resources in milli-cores
        self.avg_load = avg_load  # Average load used to model load function
        self.benefit_factor = benefit_factor  # Beta factor for utility function
        self.xi = xi  # term to shape of the diminishing return, how fast it saturates to upper bound
        self.sigma_load = sigma
        self.hyperparameters = hyperparameters
        self.load_function_id = load_function_id  # Database id
        self.load_function = load_function  # list of values for each time slot
        self.payoff = 0
        self.utility = 0

        # This is only used to analyze what happens if players are not honest
        self.true_avg_load = 0
        self.true_benefit_factor = 0
        self.true_xi = 0
        self.true_sigma_load = 0
        self.true_hyperparameters = []
        self.true_load_function = []
        self.true_load_function_id = 0

        # TODO only used in additive value calculation controller
        self.payment = 0
        self.revenue = 0



