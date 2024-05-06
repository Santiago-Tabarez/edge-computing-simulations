class Coalition:

    # Class not used in additive value function
    def __init__(self, players):
        self.players = players
        self.utilities = 0
        self.revenues = []
        self.payments = []
        self.allocation = []
        self.coalition_payoff = None
