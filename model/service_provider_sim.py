class ServiceProviderSimulation:

    def __init__(self, service_provider_name, sigma, avg_load, benefit_factor, xi, hyperparameters):
        self.service_provider_name = service_provider_name
        self.sigma = sigma
        self.avg_load = avg_load
        self.benefit_factor = benefit_factor
        self.xi = xi
        self.hyperparameters = hyperparameters
        self.id = 0

    def __str__(self):
        return (f"ServiceProvider:\n"
                f"Player Id: {self.player_id}\n"
                f"Avg Load: {self.avg_load}\n"
                f"Benefit Factor: {self.benefit_factor}\n"
                f"Xi: {self.xi}\n")
