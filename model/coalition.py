
class Coalition:

    def __init__(self, players, payoff):
        self.players = players
        self.coalition_payoff = payoff
        self.utilities = []

    def __str__(self):
        return (f"Coalition:\n"
                f"Players: {self.players}\n"
                f"Coal payoff: {self.coalition_payoff}\n"
                f"Utilities: {self.utilities}\n")

