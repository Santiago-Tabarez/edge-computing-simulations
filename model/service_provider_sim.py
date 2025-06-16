class ServiceProviderSimulation:

    def __init__(self, service_provider_name, sigma, avg_load, benefit_factor, xi, fac_of_req, hyperparameters):

        self.service_provider_name = service_provider_name
        self.sigma = sigma
        self.avg_load = avg_load
        self.benefit_factor = benefit_factor
        self.frac_of_req = fac_of_req
        self.xi = xi
        self.hyperparameters = hyperparameters
        self.id = 0
        self.load_functions = []

