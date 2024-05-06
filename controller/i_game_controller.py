from abc import ABC, abstractmethod

from model.game import Game


class IGameController(ABC):

    @staticmethod
    @abstractmethod
    def calculate_coal_payoff(game):
        """Calculate the grand coalition's payoff."""
        pass

    @staticmethod
    @abstractmethod
    def players_contribution(game):
        """Calculate each player's contribution to the grand coalition."""
        pass

    @staticmethod
    @abstractmethod
    def how_much_revenue_payment(game):
        """Calculate how much each player needs to pay or receive from the coalition."""
        pass
