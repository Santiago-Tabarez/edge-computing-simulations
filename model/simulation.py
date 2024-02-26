from model.network_owner import NetworkOwner


class Simulation:

    def __init__(self, simulation_name, max_cores_hosted_min, max_cores_hosted_max, cpu_price_min, cpu_price_max,
                 years_min, years_max, daily_timeslots_min, daily_timeslots_max, amount_of_players):
        self.simulation_id = 0
        self.simulation_name = simulation_name
        self.max_cores_hosted_min = max_cores_hosted_min
        self.max_cores_hosted_max = max_cores_hosted_max
        self.cpu_price_min = cpu_price_min
        self.cpu_price_max = cpu_price_max
        self.years_min = years_min
        self.years_max = years_max
        self.daily_timeslots_min = daily_timeslots_min
        self.daily_timeslots_max = daily_timeslots_max
        self.amount_of_players = amount_of_players
        self.games = []
        self.players = []
        self.network_owner = NetworkOwner(simulation_name)
        self.is_update = False

