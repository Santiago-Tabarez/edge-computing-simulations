import numpy as np
import logging.config
from typing import List
import warnings

# We eliminate this warning from the console, this is due to
# the method being to close to linear in some cases
warnings.filterwarnings(
    "ignore",
    message="delta_grad == 0.0. Check if the approximated function is linear"
)
from scipy.optimize import minimize
from config import config
from model.service_provider import ServiceProvider
from utils.cpu_cost import CPUCost

logger = logging.getLogger(__name__)


class Optimization:
    def __init__(self,
                 min_cpu_price: float,
                 max_cpu_price: float,
                 min_cores_hosted: int,
                 max_cores_hosted: int,
                 daily_timeslots: int,
                 horizon: int,
                 load_exponent: int,
                 beta_exponent: int,
                 xi_exponent: int,
                 price_exponent: int,
                 service_providers: List[ServiceProvider]):

        self.utilities: List[float] = []
        self.min_cpu_price = min_cpu_price
        self.max_cpu_price = max_cpu_price
        self.min_cores_hosted = min_cores_hosted
        self.max_cores_hosted = max_cores_hosted
        self.load_exponent = load_exponent
        self.beta_exponent = beta_exponent
        self.xi_exponent = xi_exponent
        self.price_exponent = price_exponent

        if min_cpu_price == max_cpu_price:
            self.fixed_cpu_price = min_cpu_price
            self.weighted_by_alloc_cpu_price = None
        else:
            self.fixed_cpu_price = None
            self.weighted_by_alloc_cpu_price = 0

        self.amortized_cpu_price = max_cpu_price / (daily_timeslots * horizon)
        self.daily_timeslots = daily_timeslots
        self.amount_of_service_providers = len(service_providers)
        self.horizon = horizon
        self.service_providers = service_providers

        self.loads_matrix = np.array([sp.load_function for sp in self.service_providers])
        self.beta_factors = np.array([sp.benefit_factor for sp in self.service_providers])
        self.xi_factors = np.array([sp.xi for sp in self.service_providers])

        self.per_time_slot_allocation = config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']

        # TRUST_CONSTR_PARAMETERS parameters
        self.ftol = config.SLSQP_PARAMETERS['ftol']
        self.eps = config.SLSQP_PARAMETERS['eps']
        self.maxiter = config.SLSQP_PARAMETERS['maxiter']

        self.allocations = [0] * self.amount_of_service_providers * self.daily_timeslots
        self.total_allocation = 0
        self.max_alloc = [0] * self.amount_of_service_providers

    def load_funct(self, t: int, i: int) -> float:
        return self.loads_matrix[i, t]

    def utility_function(self, h: float, t: int, i: int) -> float:
        xi_i = self.xi_factors[i]
        l_i_t = self.load_funct(t, i)
        beta_i = self.beta_factors[i]
        price = self.amortized_cpu_price

        # Calculate exponent: h * xi^load_exponent * l^load_exponent * beta^beta_exponent * price^price_exponent
        exp_arg = (
                h
                * (xi_i ** self.xi_exponent)
                * (l_i_t ** self.load_exponent)
                * (beta_i ** self.beta_exponent)
                * (price ** self.price_exponent)
        )

        return beta_i * l_i_t * (1 - np.exp(-exp_arg))

    @staticmethod
    def global_allocation_constraint(x: List[float], global_alloc: float) -> float:
        return global_alloc - sum(x)

    def time_slot_net_utility(self, ts_alloc: np.ndarray, ts: int) -> float:
        utility_ts_sum = 0
        for i in range(self.amount_of_service_providers):
            utility_ts_sum += self.utility_function(ts_alloc[i], ts, i)
        cost = self._per_slot_cost()
        return -1 * (utility_ts_sum * self.horizon - cost)

    def time_slot_utility_hess(self, ts_alloc: np.ndarray, ts: int) -> np.ndarray:
        loads = self.loads_matrix[:, ts]
        xi = self.xi_factors
        beta = self.beta_factors
        price = self.amortized_cpu_price
        M = (xi ** self.xi_exponent) * (loads ** self.load_exponent) * (beta ** self.beta_exponent) * (
                price ** self.price_exponent)
        exp_term = np.exp(-M * ts_alloc)
        diag = - beta * loads * (M ** 2) * exp_term
        return np.diag(self.horizon * (-diag))

    def time_slot_utility_jac(self, ts_alloc: np.ndarray, ts: int) -> np.ndarray:

        loads = self.loads_matrix[:, ts]  # forma (n_providers,)
        xi = self.xi_factors  # forma (n_providers,)
        beta = self.beta_factors  # forma (n_providers,)
        price = self.amortized_cpu_price  # float

        # Build M_i = xi_i^load_exponent * l_{i,t}^load_exponent *
        #                 beta_i^beta_exponent * price^price_exponent
        M = (
                (xi ** self.xi_exponent)
                * (loads ** self.load_exponent)
                * (beta ** self.beta_exponent)
                * (price ** self.price_exponent)
        )

        # Calculate exp(-M_i * h_i) para cada i
        exp_term = np.exp(- M * ts_alloc)  # forma (n_providers,)
        dU = beta * loads * exp_term * M  # forma (n_providers,)
        return - self.horizon * dU  # forma (n_providers,)

    def _per_slot_cost(self) -> float:
        return (sum(self.max_alloc) * self.fixed_cpu_price) / self.daily_timeslots

    def _revenues(self, allocations: np.ndarray) -> float:
        if self.per_time_slot_allocation:
            self.allocations = allocations.reshape(self.amount_of_service_providers, self.daily_timeslots)
            # Utilities matrix for each SP and each time-slot
            utility_matrix = self.beta_factors[:, np.newaxis] * self.loads_matrix * (
                    1 - np.exp(
                - allocations[:, None]
                * (self.xi_factors[:, None] ** self.xi_exponent)
                * (self.loads_matrix ** self.load_exponent)
                * (self.beta_factors[:, None] ** self.beta_exponent)
                * (self.amortized_cpu_price ** self.price_exponent)
            )
            )
            utilities_sum_per_sp = utility_matrix.sum(axis=1)
            self.utilities = utilities_sum_per_sp * self.horizon
            return self.utilities.sum()
        else:
            utility_matrix = self.beta_factors[:, None] * self.loads_matrix * (
                    1 - np.exp(
                - allocations[:, None]
                * (self.xi_factors[:, None] ** self.xi_exponent)
                * (self.loads_matrix ** self.load_exponent)
                * (self.beta_factors[:, None] ** self.beta_exponent)
                * (self.amortized_cpu_price ** self.price_exponent)
            )
            )
            total_utilities = utility_matrix.sum(axis=1) * self.horizon
            self.utilities = total_utilities.tolist()
            return total_utilities.sum()

    def _objective(self, allocation: List[float]) -> float:
        if self.per_time_slot_allocation:
            utility_sum = 0
            for t in range(self.daily_timeslots):
                bounds_ts = [(0, None)] * self.amount_of_service_providers
                # bounds_ts = [(0, None)] * self.amount_of_service_providers + [(0, self.max_cores_hosted)]
                ts_alloc = np.asarray(allocation)
                constraint = {'type': 'eq', 'fun': lambda x: self.global_allocation_constraint(x, sum(allocation))}

                result_ts = minimize(
                    fun=self.time_slot_net_utility,
                    x0=ts_alloc,
                    args=(t,),
                    jac=self.time_slot_utility_jac,
                    # hess=self.time_slot_utility_hess,
                    bounds=bounds_ts,
                    constraints=constraint,
                    method='SLSQP',
                    options={'ftol': self.ftol, 'eps': self.eps, 'maxiter': self.maxiter, 'disp': False}
                )

                if not result_ts.success:
                    continue
                for i in range(self.amount_of_service_providers):
                    idx = t * self.amount_of_service_providers + i
                    self.allocations[idx] = result_ts.x[i]
                utility_sum -= result_ts.fun
                if sum(result_ts.x) > sum(self.max_alloc):
                    self.max_alloc = result_ts.x.tolist()
            return -utility_sum
        else:
            rev = self._revenues(np.array(allocation[:-1]))
            total_alloc = sum(allocation[:-1])
            if self.min_cpu_price == self.max_cpu_price:
                payoff = rev - self.fixed_cpu_price * total_alloc
            else:
                self.weighted_by_alloc_cpu_price = CPUCost.linear_interpolation_weighted_price(
                    self.min_cpu_price, self.max_cpu_price,
                    self.min_cores_hosted, self.max_cores_hosted,
                    total_alloc
                )
                payoff = rev - self.weighted_by_alloc_cpu_price
            return -1 * payoff

    @staticmethod
    def _max_allocation_constraint(x: List[float]) -> float:
        return sum(x[:-1]) - x[-1]

    @staticmethod
    def max_per_time_slot_allocation_constraint(alloc: List[float], amount_of_sps: int, max_alloc: float) -> float:
        slices = [sum(alloc[i:i + amount_of_sps]) for i in range(0, len(alloc), amount_of_sps)]
        return max_alloc - max(slices)

    def allocation_constraints(self, allocations: np.ndarray) -> List[float]:
        allocations = allocations.reshape(-1, self.amount_of_service_providers)
        max_slice = np.max(allocations.sum(axis=1))
        return [max_slice - allocations[t, :].sum() + 0.1 for t in range(self.daily_timeslots)]

    def maximize_coalition_payoff(self):
        if config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']:

            self.per_time_slot_allocation = False
            max_alloc_const = {'type': 'eq', 'fun': self._max_allocation_constraint}
            initial_allocations = np.concatenate([np.ones(self.amount_of_service_providers),
                                                  [self.amount_of_service_providers]])
            bounds = [(0, None)] * self.amount_of_service_providers + [(0, self.max_cores_hosted)]

            # if self.amount_of_service_providers == 1:

            sol = minimize(self._objective, initial_allocations,
                           bounds=bounds,
                           constraints=max_alloc_const,
                           method='SLSQP',
                           options={'ftol': self.ftol, 'eps': self.eps, 'maxiter': self.maxiter, 'disp': False})

            # else:
            """
            sol = minimize(self._objective, initial_allocations,
                           bounds=bounds,
                           constraints=max_alloc_const,
                           method='trust-constr',
                           options={
                               'gtol': self.gtol,
                               'xtol': self.xtol,
                               'barrier_tol': self.barrier_tol,
                               'maxiter': self.maxiter,
                               'verbose': 0
                           })
            """
            initial_allocations = sol.x[:-1]

            self.per_time_slot_allocation = True
            bounds_ts = [(0, None)] * self.amount_of_service_providers

            # This is not the maximization of the utility
            # but the maximization of all the time-slots utility combined
            sol = minimize(self._objective, initial_allocations,
                           method='SLSQP', bounds=bounds_ts,
                           options={'ftol': self.ftol, 'eps': self.eps, 'maxiter': self.maxiter, 'disp': False})

            max_alloc_for_player = [max(sol.x[player::self.amount_of_service_providers])
                                    for player in range(self.amount_of_service_providers)]
            sol.x = np.array(max_alloc_for_player)
            # print("max alloc: ", max_alloc_for_player)
            self.total_allocation = sum(max_alloc_for_player)
        else:
            max_alloc_const = {'type': 'eq', 'fun': self._max_allocation_constraint}
            initial_allocations = np.concatenate([np.ones(self.amount_of_service_providers),
                                                  [self.amount_of_service_providers]])
            bounds = [(0, None)] * self.amount_of_service_providers + [(0, self.max_cores_hosted)]
            sol = minimize(self._objective, initial_allocations,
                           bounds=bounds,
                           constraints=max_alloc_const,
                           method='SLSQP',
                           options={'ftol': self.ftol, 'eps': self.eps, 'maxiter': self.maxiter, 'disp': False})

        return sol, self.utilities, self.weighted_by_alloc_cpu_price
