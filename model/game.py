class Game:

    def __init__(self, simulation_id, years, max_cores_hosted, price_cpu, amount_of_players, daily_timeslots):
        self.simulation_id = simulation_id
        self.years = years
        self.max_cores_hosted = max_cores_hosted
        self.price_cpu = price_cpu
        self.amount_of_players = amount_of_players
        self.daily_timeslots = daily_timeslots
        self.players = []
        # self.coalitions = []
        self.grand_coalition = None

    def add_player(self, sp):
        self.players.append(sp)
