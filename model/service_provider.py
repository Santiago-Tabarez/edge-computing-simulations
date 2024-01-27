
class ServiceProvider:

    def __init__(self, player_id, avg_load, benefit_factor, chi):
        self.player_id = player_id
        self.avg_load = avg_load                # average load that will be modeled by load function
        self.benefit_factor = benefit_factor    # beta factor for utility function
        self.chi = chi                          # term to shape of the diminishing return, how fast it saturates to upper bound
        self.allocation = 0                     # allocated resources in milli-cores

    def __str__(self):
        return (f"ServiceProvider:\n"
                f"Player Id: {self.player_id}\n"
                f"Avg Load: {self.avg_load}\n"
                f"Benefit Factor: {self.benefit_factor}\n"
                f"Chi: {self.chi}\n")
