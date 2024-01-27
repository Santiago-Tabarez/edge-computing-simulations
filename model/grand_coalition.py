from model.coalition import MyCoalition


class GrandCoalition:
    def __init__(self,  utilities):

        self.utilities = utilities
        self.revenues = []
        self.payments = []
        self.allocation = []
        self.shapley_value = []

    def __str__(self):
        return (f"Gran Coalition:\n"
                f"Utilities: {self.utilities}\n"
                f"Allocation: {self.allocation}\n"
                f"Shapley value: {self.shapley_value}\n"
                f"Revenues: {self.revenues}\n"
                f"Payments: {self.payments}\n"
                )
