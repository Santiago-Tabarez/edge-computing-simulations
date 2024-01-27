import math

from scipy.optimize import minimize
import numpy as np


class Optimization:

    def __init__(self):
        self.utilities = None
        self.p_cpu = None
        self.daily_timeslots = None
        self.amount_of_players = None
        self.max_cores_hosted = None
        self.horizon = None
        self.coalition = None


opt = Optimization()

# TODO remove from here and add to each player ?
#  ak and tk are hyperparameters determining the amplitude and the offset
#  of each of the K sinusoidal components. This is used to calculate load functions
a_k = (48530, 25313, -8832, 1757, -2873)
t_k = (0, 47340, 49080, 44520, 44880)


# Used to simulate the load changes through the day
# for each timeslot  it will associate a value
def _load_series_expansion_player_i(current_timeslot, daily_timeslots):
    tmp = 0
    for i in range(len(a_k) - 1):
        tmp += a_k[i + 1] * math.sin(2 * math.pi * (i + 1) * ((current_timeslot - t_k[i + 1]) / daily_timeslots))

    return a_k[0] + tmp


# daily_timeslots = amount of timeslots in a day typically we are working with 96
# avg_load = average load of the player, that will be used to calculate the load for each timeslot
# we are using the same average load and load profile for everyday
def _genera_loads(daily_timeslots, avg_load):
    if avg_load == 0:
        return [0] * daily_timeslots

    # random_normal_dist is allways going to be 0, it is necessary to make sigma != so we have some deviation
    # this would change the model into a stochastic one
    sigma = 0
    # it may make sense to add a significance level to avoid, low probable to big absolute value numbers
    # alpha = 0.05  # significance level
    # z_low, z_high = stats.norm.ppf(alpha / 2), stats.norm.ppf(1 - alpha / 2)
    # TODO avg_load is not being used, mu should be avg_load
    random_normal_dist = np.random.normal(avg_load, sigma, daily_timeslots)
    generated_loads = []
    for timeslot in range(daily_timeslots):
        load_for_timeslot = _load_series_expansion_player_i(timeslot, daily_timeslots) + random_normal_dist[timeslot]
        generated_loads.append(load_for_timeslot)
    return generated_loads


# csi=0.08 in the file csi optimization that I am deleting

# increasing and concave function, characterized by a diminishing return effect

# beta_i =  benefit factor of player i which represents the benefit that one SP gets from serving one unit of load at the Edge. null for the NO
# csi = models the shape of the diminishing return, i.e. how fast it saturates to its upper bound beta_i * load_t
# load_t = load in timeslot t for current player
# h_i = allocated resources for player i, if h_i=0 then utility=0
def _utility_i(beta_i, h_i, load_t, csi):
    return beta_i * load_t * (1 - math.exp(-csi * h_i))


# daily_timeslots = amount of timeslots in a day
# SPs = service providers of the game for which we are calculating revenue
# betas = array with beta value for each SP, used and explained in _utility_i function
# h_vec = array with allocated resources for each of the SPs
# etas = array with average load for each player
def _revenues(allocation_vec):
    # Handle the empty case, e.g., return early or set default values

    # utility produced by each player for all the timeslots
    opt.utilities = []
    i = 0

    for player in opt.coalition:
        utility = 0
        loads_i = _genera_loads(opt.daily_timeslots, player.avg_load)
        for t in range(opt.daily_timeslots):
            utility += _utility_i(player.benefit_factor, allocation_vec[i], loads_i[t], player.chi)

        opt.utilities.append(utility)
        i += 1

    total_revenues = sum(opt.utilities)
    return total_revenues


# used to maximize the payoff of a coalition
# called by minimize from python lib, it will be executed an undetermined amount of times
# x has num_of_players + 1 elements, the allocation vector for each player and the total capacity
def _objective(x):
    allocation_vec = x[:-1]
    capacity = x[-1]
    player_id_zero_exists = any(hasattr(obj, 'player_id') and obj.player_id == 0 for obj in opt.coalition)
    # add the condition to not be the only one ? remember to set utility to zero
    if player_id_zero_exists:
        tmp = (-opt.horizon * _revenues(allocation_vec) + opt.p_cpu
               * capacity)
    else:
        tmp = 0
    return tmp


# calculates the difference between the sum of all elements except the last one and the last element itself
def _constraint1(x):
    return sum(x[:-1]) - x[-1]


def maximize_payoff(game, coalition_players):
    opt.p_cpu = game.price_cpu
    opt.amount_of_players = game.amount_of_players
    opt.max_cores_hosted = game.max_cores_hosted
    opt.horizon = game.years * 365
    opt.daily_timeslots = game.daily_timeslots
    opt.coalition = coalition_players

    x0 = [1] * (opt.amount_of_players + 1)
    b = (0, None)
    bounds = (b,) * opt.amount_of_players + ((0, opt.max_cores_hosted),)
    con1 = {'type': 'eq', 'fun': _constraint1}
    cons = [con1]

    sol = minimize(_objective, x0, method='slsqp', bounds=bounds, constraints=cons)
    if not sol['success']:
        print(sol)
    return sol, opt.utilities
