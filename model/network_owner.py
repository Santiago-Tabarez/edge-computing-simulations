class NetworkOwner:

    def __init__(self, player_name):
        self.player_id = 0
        self.player_name = player_name
        self.sigma = 0  # TODO delete all this variables
        self.sigma_load = 0
        self.hyperparameters = []
        self.avg_load = 0  # average load that will be modeled by load function
        self.benefit_factor = 0  # beta factor for utility function
        self.xi = 0  # term to shape of the diminishing return, how fast it saturates to upper bound
        self.load_function_id = 0

    def __str__(self):
        return (f"Network owner:\n"
                f"Player id: {self.player_id}\n")
