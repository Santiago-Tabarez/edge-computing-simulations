class Game:

    def __init__(self, years, max_cores_hosted, price_cpu, amount_of_players, daily_timeslots):

        self.years = years
        self.max_cores_hosted = max_cores_hosted
        self.price_cpu = price_cpu
        self.amount_of_players = amount_of_players
        self.daily_timeslots = daily_timeslots
        self.players = []
        self.coalitions = []
        self.gran_coalition = None

    def add_player(self, sp):
        self.players.append(sp)

    def __str__(self):
        players_str = '\n'.join(str(player) for player in self.players)
        return (f"Game:\n"
                f"Years: {self.years}\n"
                f"Max Cores Hosted: {self.max_cores_hosted}\n"
                f"Price per CPU: {self.price_cpu}\n"
                f"Amount of Players: {self.amount_of_players}\n"
                f"Daily Timeslots: {self.daily_timeslots}\n"
                f"Players:\n{players_str}"
                f"\n{self.gran_coalition}")
