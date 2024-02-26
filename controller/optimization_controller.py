import math
from typing import List

import numpy as np
from scipy.optimize import minimize
import logging.config

from model.service_provider import ServiceProvider

logger = logging.getLogger(__name__)

"""
   This class used to calculate the maximum value of a coalition by optimizing the allocation of resources among service providers to maximize their combined payoff.

   Attributes:
       cpu_price (float): Price per CPU unit.
       daily_timeslots (int): Number of timeslots in a daily.
       amount_of_service_providers (int): Number of service providers involved.
       max_cores_hosted (int): Maximum number of cores that can be deployed at the Edge.
       horizon (int): Time in days of the co-investment duration
       service_providers (List[ServiceProvider]): List of service providers participating in the coalition.
       
"""

class Optimization:
    def __init__(self, cpu_price: float, daily_timeslots: int, amount_of_service_providers: int, max_cores_hosted: int,
                 horizon: int, service_providers: List[ServiceProvider]):
        self.utilities: List[float] = []
        self.cpu_price = cpu_price
        self.daily_timeslots = daily_timeslots
        self.amount_of_service_providers = amount_of_service_providers
        self.max_cores_hosted = max_cores_hosted
        self.horizon = horizon
        self.service_providers = service_providers

        # Vectorized Pre-calculate and store as class variables for better performance
        # loads_matrix is a 2D array where each row corresponds to a service provider's loads across timeslots
        self.loads_matrix = np.array([sp.load_function for sp in self.service_providers])
        self.beta_factors = np.array([sp.benefit_factor for sp in self.service_providers])
        self.xi_factors = np.array([sp.xi for sp in self.service_providers])

    # Increasing and concave function, characterized by Amdahl's law (a diminishing return effect)
    # beta_i :  benefit factor of player i which represents the benefit that one SP gets from serving one unit of load at the Edge
    # xi : models the shape of the diminishing return, i.e. how fast it saturates to its upper bound (beta_i * load_t)
    # load_t : load in timeslot t for current SP
    # h_i : allocated resources for current SP
    @staticmethod
    def _utility_i(beta_i: float, h_i: float, load_t: float, xi: float) -> float:
        return beta_i * load_t * (1 - math.exp(-xi * h_i))

    # allocation_vec = array with allocated resources for each of the SPs
    """
    def _revenues(self, allocation_vec: List[float]) -> float:
        # gross utility produced by each service provider for all the timeslots
        self.utilities = []

        for i, sp in enumerate(self.service_providers):
            sp_utility = 0
            loads_i = sp.load_function
            for t in range(self.daily_timeslots):
                sp_utility += self._utility_i(sp.benefit_factor, allocation_vec[i], loads_i[t], sp.xi) * self.horizon
            self.utilities.append(sp_utility)

        total_revenues = sum(self.utilities)
        return total_revenues

    """

    # Calculates the gross utility produced by each service provider for all the timeslots
    def _revenues(self, allocation_vec: np.ndarray) -> float:

        # Calculate utilities for each service provider across all timeslots
        utility_matrix = self.beta_factors[:, None] * self.loads_matrix * (
                    1 - np.exp(-self.xi_factors[:, None] * allocation_vec[:, None]))
        # Total utility for each service provider multiplied by the investment duration
        total_utilities = np.sum(utility_matrix,
                                 axis=1) * self.horizon

        # Update 'utilities' with the total utilities for each service provider
        self.utilities = total_utilities.tolist()
        total_revenues = np.sum(total_utilities)

        return total_revenues

    # Used to maximize the payoff of a coalition
    # Called by minimize from python lib, it will be executed an undetermined amount of times defined by the convergence criterion
    # x is the allocation vector for service providers and the total capacity
    def _objective(self, x: List[float]) -> float:

        # Revenues from the allocation vector
        rev = self._revenues(np.array(x[:-1]))
        # Calculate net utilities from gross utilities, this is what we want to maximize
        payoff = rev - self.cpu_price * sum(x[:-1])
        # We are using minimize function, so we have to change the sign
        return -1 * payoff

    # Ensure the sum of allocations does not exceed the total Edge capacity
    @staticmethod
    def _max_allocation_constraint(x: List[float]) -> float:
        return sum(x[:-1]) - x[-1]

    def maximize_coalition_payoff(self):

        # This is the initial guest for each SP allocation plus the total allocation
        x0 = np.concatenate([np.ones(self.amount_of_service_providers), [self.amount_of_service_providers]])
        # Bounds for each service provider
        b = (0, None)
        # Total allocation can't be greater than max_cores_hosted
        bounds = (b,) * self.amount_of_service_providers + ((0, self.max_cores_hosted),)
        con = {'type': 'eq', 'fun': self._max_allocation_constraint}

        sol = minimize(self._objective, x0, method='slsqp', bounds=bounds, constraints=con)
        if not sol['success']:
            logger.error("Error in maximize_coalition_payoff %s", sol)

        return sol, self.utilities
