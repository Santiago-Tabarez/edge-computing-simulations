class ServiceProviderSimulation:

   # def __init__(self):
   #     self.service_provider = ""

    def __init__(self, service_provider_name, benefit_factor_min, benefit_factor_max, chi_min, chi_max, avg_load_min,
                 avg_load_max):
        self.service_provider_name = service_provider_name
        self.benefit_factor_min = benefit_factor_min
        self.benefit_factor_max = benefit_factor_max
        self.chi_min = chi_min
        self.chi_max = chi_max
        self.avg_load_min = avg_load_min
        self.avg_load_max = avg_load_max

    def __str__(self):
        return (f"ServiceProvider:\n"
                f"Player Id: {self.player_id}\n"
                f"Avg Load: {self.avg_load}\n"
                f"Benefit Factor: {self.benefit_factor}\n"
                f"Chi: {self.chi}\n")
