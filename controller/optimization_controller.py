from typing import List

import numpy as np
from scipy.optimize import minimize
import logging.config

from config import config
from model.service_provider import ServiceProvider
from utils.cpu_cost import CPUCost

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

    def __init__(self, min_cpu_price: float, max_cpu_price: float, min_cores_hosted: int, max_cores_hosted: int,
                 daily_timeslots: int,
                 horizon: int, service_providers: List[ServiceProvider]):

        self.utilities: List[float] = []

        self.min_cpu_price = min_cpu_price
        self.max_cpu_price = max_cpu_price
        self.min_cores_hosted = min_cores_hosted
        self.max_cores_hosted = max_cores_hosted

        if min_cpu_price == max_cpu_price:
            self.fixed_cpu_price = min_cpu_price
            self.weighted_by_alloc_cpu_price = None
        else:
            self.fixed_cpu_price = None
            self.weighted_by_alloc_cpu_price = 0

        self.daily_timeslots = daily_timeslots
        self.amount_of_service_providers = len(service_providers)

        self.horizon = horizon
        self.service_providers = service_providers

        # Vectorized Pre-calculate and store as class variables for better performance
        # loads_matrix is a 2D array where each row corresponds to a service provider's loads across timeslots
        self.loads_matrix = np.array([sp.load_function for sp in self.service_providers])
        self.beta_factors = np.array([sp.benefit_factor for sp in self.service_providers])
        self.xi_factors = np.array([sp.xi for sp in self.service_providers])

        # Boolean
        self.per_time_slot_allocation = config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']
        # Used to save allocation by time slot
        self.allocations = [0] * self.amount_of_service_providers * self.daily_timeslots
        self.total_allocation = 0
        self.max_alloc = [0] * self.amount_of_service_providers

    # Calculates the gross utility produced by each service provider for all the timeslots
    def _revenues(self, allocations):

        if self.per_time_slot_allocation:

            # Reshape allocations to match loads_matrix's structure
            self.allocations = np.asarray(allocations).reshape(self.amount_of_service_providers, self.daily_timeslots)

            # Compute utilities for all service providers and timeslots
            utility_matrix = self.beta_factors[:, np.newaxis] * self.loads_matrix * (
                    1 - np.exp(-self.xi_factors[:, np.newaxis] * allocations))

            # Sum utilities across timeslots for each service provider
            utilities_sum_per_sp = utility_matrix.sum(axis=1)

            # Multiply by horizon for total gross utilities for each service provider
            self.utilities = utilities_sum_per_sp * self.horizon

            # Sum across service providers for total utility which we aim to maximize
            total_revenues = np.sum(self.utilities)
            return total_revenues

        else:

            utility_matrix = self.beta_factors[:, None] * self.loads_matrix * (
                    1 - np.exp(-self.xi_factors[:, None] * allocations[:, None]))
            # Total utility for each service provider multiplied by the investment duration
            # Flatten the matrix into an array of the sums of utility function throw the timeslots
            total_utilities = np.sum(utility_matrix,
                                     axis=1) * self.horizon

            # Update 'utilities' with the total utilities for each service provider
            self.utilities = total_utilities.tolist()
            total_revenues = np.sum(total_utilities)

            return total_revenues

    def load_funct(self, t, i):
        load = self.loads_matrix[i, t]
        return load

    def utility_function(self, h, t, i):
        util = self.beta_factors[i] * self.load_funct(t, i) * (1 - np.exp(-self.xi_factors[i] * h))
        # print("timeslot", t, "player", i, "utility", util, "allocation", h)
        return util

    @staticmethod
    def global_allocation_constraint(x: List[float], global_alloc: float) -> float:
        return global_alloc - sum(x)

    def time_slot_utility(self, ts_alloc, ts):

        utility_ts_sum = 0
        # This function now directly returns the negative utility for simplicity
        for i in range(self.amount_of_service_providers):
            utility_ts_sum += self.utility_function(ts_alloc[i], ts, i)

        if self.min_cpu_price == self.max_cpu_price:

            # If the CPU price by unit is fixed
            cost = self.fixed_cpu_price * sum(self.max_alloc)
        else:
            # If the CPU by unit decrease as total amount of allocated CPU increases
            # Linear interpolation for price reduction
            cost = self.weighted_by_alloc_cpu_price = CPUCost.linear_interpolation_weighted_price(self.min_cpu_price,
                                                                                                  self.max_cpu_price,
                                                                                                  self.min_cores_hosted,
                                                                                                  self.max_cores_hosted,
                                                                                                  sum(self.max_alloc))
        # TODO review if it is correct tp divide price equally
        cost = cost / self.daily_timeslots
        # cost = (sum(self.max_alloc) * self.fixed_cpu_price) / 96
        return - 1 * (utility_ts_sum * self.horizon - cost)

    # Used to maximize the payoff of a coalition
    # Called by minimize from python lib, it will be executed an undetermined amount of times defined by the convergence criterion
    # x is the allocation vector for service providers and the total capacity
    def _objective(self, allocation: List[float]) -> float:

        # Revenues from the allocation vector

        # sum(sum(utility_function(h, t, i) for i in range(n)) for t in range(T))

        # if config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']:
        if self.per_time_slot_allocation:
            utility_sum = 0
            # max_alloc = [0, 0]  # Just for logging

            for t in range(self.daily_timeslots):
                # Optimization for a time slot
                bounds_ts = [(0, None)]
                ts_alloc = np.asarray(allocation)
                # TODO with ineq we should get slightly bigger allocation but we can somehow positively account not using 100% of CPU
                constraint = ({'type': 'eq', 'fun': lambda x: self.global_allocation_constraint(x, sum(allocation))})
                result_ts = minimize(self.time_slot_utility, ts_alloc, args=(t,), bounds=bounds_ts,
                                     constraints=constraint,
                                     method='SLSQP')

                if not result_ts.success:
                    print(
                        f"Optimization failed for time slot {t}. Reason: {result_ts.message}")
                    continue
                else:
                    for i in range(self.amount_of_service_providers):
                        al = t * self.amount_of_service_providers
                        self.allocations[al + i] = result_ts.x[i]

                # Summing up the negative of the result since we minimized the negative utility
                utility_sum -= result_ts.fun

                if sum(result_ts.x) > sum(self.max_alloc):
                    self.max_alloc = result_ts.x
                    # self.max_alloc = result_ts.x

            return -utility_sum  # Return negative for maximization

        else:
            rev = self._revenues(np.array(allocation[:-1]))
            # print("revenue:", rev)
            total_alloc = sum(allocation[:-1])
        # Calculate net utilities from gross utilities, this is what we want to maximize
        if self.min_cpu_price == self.max_cpu_price:

            # If the CPU price by unit is fixed
            payoff = rev - self.fixed_cpu_price * total_alloc
        else:
            # If the CPU by unit decrease as total amount of allocated CPU increases
            # Linear interpolation for price reduction
            self.weighted_by_alloc_cpu_price = CPUCost.linear_interpolation_weighted_price(self.min_cpu_price,
                                                                                           self.max_cpu_price,
                                                                                           self.min_cores_hosted,
                                                                                           self.max_cores_hosted,
                                                                                           total_alloc)
            payoff = rev - self.weighted_by_alloc_cpu_price
        # We are using minimize function, so we have to change the sign
        return -1 * payoff

    # Ensure the sum of allocations does not exceed the total Edge capacity
    @staticmethod
    def _max_allocation_constraint(x: List[float]) -> float:
        return sum(x[:-1]) - x[-1]

    @staticmethod
    def max_per_time_slot_allocation_constraint(alloc: List[float], amount_of_sps, max_alloc) -> float:
        by_time_slot_slices = [sum(alloc[i:i + amount_of_sps]) for i in
                               range(0, len(alloc), amount_of_sps)]
        # Find the greatest sum among all slices
        greatest_sum = max(by_time_slot_slices)

        return max_alloc - greatest_sum

    def allocation_constraints(self, allocations):

        biggest_tuple_sum = (lambda x: np.max(np.sum(x.reshape(-1, self.amount_of_service_providers), axis=1)))(
            allocations)
        constraints = []

        for t in range(self.daily_timeslots):
            slot_allocation = sum(
                allocations[t * self.amount_of_service_providers:(t + 1) * self.amount_of_service_providers])
            constraints.append(biggest_tuple_sum - slot_allocation + 0.1)
        return constraints

    def maximize_coalition_payoff(self):

        if config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']:

            self.per_time_slot_allocation = False
            max_alloc_const = {'type': 'eq', 'fun': self._max_allocation_constraint}
            b = (0, None)
            initial_allocations = np.concatenate(
                [np.ones(self.amount_of_service_providers), [self.amount_of_service_providers]])

            # Bounds for each service provider
            bounds = (b,) * self.amount_of_service_providers + ((0, self.max_cores_hosted),)
            sol = minimize(self._objective, initial_allocations, method='slsqp', bounds=bounds,
                           constraints=max_alloc_const,
                           options={'ftol': 1e-6, 'eps': 1.5e-6, 'maxiter': 1000, 'disp': False})
            initial_allocations = sol.x[:-1]

            self.per_time_slot_allocation = True

            bounds = [(0, None) for _ in range(self.amount_of_service_providers)]
            # Best result so far is 'ftol'~ 1e-12,'eps'~ 1e-9, and not calling gradient_of_total_utility
            # Faster results can be achieved by calling gradient_of_total_utility
            sol = minimize(self._objective, np.asarray(sol.x[:-1]), method='slsqp',
                           bounds=bounds,
                           options={'ftol': 1e-6,
                                    # Stop criteria, process is stopped when |f_n - f_{n-1}| < ftol, default ~ 1e-6
                                    'eps': 1.5e-5,
                                    # Step size used for numerical approximation of the Jacobian, default ~ 1.5e-5
                                    'maxiter': 1000,  # Max amount of iteration
                                    'disp': False})

            max_alloc_for_player = [max(sol.x[player::self.amount_of_service_providers]) for player in
                                    range(self.amount_of_service_providers)]

            sol.x = max_alloc_for_player
            self.total_allocation = sum(max_alloc_for_player)
        else:
            # Total allocation can't be greater than max_cores_hosted
            max_alloc_const = {'type': 'eq', 'fun': self._max_allocation_constraint}

            b = (0, None)

            initial_allocations = np.concatenate(
                [np.ones(self.amount_of_service_providers), [self.amount_of_service_providers]])
            # Bounds for each service provider
            bounds = (b,) * self.amount_of_service_providers + ((0, self.max_cores_hosted),)
            sol = minimize(self._objective, initial_allocations, method='slsqp', bounds=bounds,
                           constraints=max_alloc_const,
                           options={'ftol': 1e-9, 'eps': 1e-6, 'maxiter': 1000, 'disp': False})

        return sol, self.utilities, self.weighted_by_alloc_cpu_price
