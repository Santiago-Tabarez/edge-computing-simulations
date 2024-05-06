class Game:

    def __init__(self, simulation_id, years, max_cores_hosted, min_cores_hosted, min_cpu_price, max_cpu_price, amount_of_players, daily_timeslots):
        self.simulation_id = simulation_id
        self.years = years
        self.max_cores_hosted = max_cores_hosted
        self.min_cores_hosted = min_cores_hosted
        self.min_cpu_price = min_cpu_price
        self.max_cpu_price = max_cpu_price
        if self.min_cpu_price == self.max_cpu_price:
            self.fixed_price = min_cpu_price
            self.weighted_per_unit_price = None
        else:
            self.fixed_price = None
            self.weighted_per_unit_price = 0

        self.amount_of_players = amount_of_players
        self.daily_timeslots = daily_timeslots
        self.players = []
        self.grand_coalition = None
        # Not used when calculating values as additive function
        self.coalitions = []

    def add_player(self, sp):
        self.players.append(sp)
