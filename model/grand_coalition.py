
class GrandCoalition:

    def __init__(self):

        # Gross utilities
        self.utilities = []
        # Net utilities
        self.net_utilities = []

        self.allocation_payment = []
        self.fairness_payment = []
        self.allocation = []
        self.shapley_value = []
        self.total_cpu_price = None
        # Only for time slot allocation
        self.per_time_slot_allocation = []
        self.total_time_slot_allocation = 0

