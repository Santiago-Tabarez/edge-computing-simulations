class NetworkOwner:

    def __init__(self, player_id):
        self.player_id = player_id
        self.avg_load = 0  # average load that will be modeled by load function
        self.benefit_factor = 0  # beta factor for utility function
        self.chi = 0  # term to shape of the diminishing return, how fast it saturates to upper bound

    def __str__(self):
        return (f"Network owner:\n"
                f"Player id: {self.player_id}\n")
