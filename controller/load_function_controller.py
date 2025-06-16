import math
import numpy as np


# Used to simulate the load changes through the day
# for each timeslot in the day it will associate a value representing the expected load for a service provider
# for that it will use the average load, sigma and the hyperparameters that define the sinusoidal function
def _load_series_expansion_player_i(current_timeslot, daily_timeslots,
                                    avg_load, hyper_params):

    # Factor to scale total daily load, this is to reproduce results from the provided code
    # This could be eliminated, it would only multiply allocation utilities Shapley value, etc. by 900
    # but analogs results would be obtained
    scale = 96 / daily_timeslots

    # In the hyperparameters t_k is in seconds, so we need to calculate amount of seconds per time slot
    secs_tl = 24 * 60 * 60 / daily_timeslots

    # Sum of the sinusoidal terms
    ret = 0.0
    k = 1
    for a_k, t_k in zip(hyper_params[0], hyper_params[1]):
        phase = ((current_timeslot * secs_tl) - t_k) / (daily_timeslots * secs_tl)
        ret += a_k * math.sin(2 * math.pi * k * phase)
        k += 1

    return (avg_load + ret) * scale


# daily_timeslots = amount of timeslots in a day typically we are working with 96 but can be changed
# avg_load = average load of a service provider, that will be used within the hyperparameters to calculate the load for each timeslot
# sigma = standard deviation from the calculated load, if sigma = 0 then the simulation is deterministic
def generate_loads(daily_timeslots, sigma, avg_load, hyper_params):
    if avg_load == 0:
        return [0] * daily_timeslots

    random_normal_dist = np.random.normal(0, sigma, daily_timeslots)
    generated_loads = []
    for timeslot in range(daily_timeslots):
        # Use of max just in case sigma is too big and may produce negative load
        load_for_timeslot = max(_load_series_expansion_player_i(timeslot, daily_timeslots, avg_load, hyper_params) +
                                random_normal_dist[timeslot], 0)
        generated_loads.append(load_for_timeslot)
    # print(generated_loads)
    return generated_loads
