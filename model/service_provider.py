class ServiceProvider:

    def __init__(self, player_id, player_name, avg_load, benefit_factor, xi, frac_of_load_at_edge, sigma, hyperparameters, load_function, load_function_id):

        # Input values
        self.player_id = player_id
        self.player_name = player_name
        self.avg_load = avg_load  # Average load used to model load function
        self.benefit_factor = benefit_factor  # Beta factor for utility function
        self.xi = xi  # term to shape of the diminishing return, how fast it saturates to upper bound
        self.frac_of_load_at_edge = frac_of_load_at_edge
        self.sigma_load = sigma
        self.hyperparameters = hyperparameters
        self.load_function_id = load_function_id  # Database id
        self.load_function = load_function  # list of values for each time slot

        # Calculated values
        self.allocation = 0  # allocated resources in milli-cores
        self.gross_utility = 0  # Also called revenues
        self.net_utility = 0    # This is revenues minus allocation cost
        self.payoff = 0         # Also called Shapley Value
        self.payment = 0




