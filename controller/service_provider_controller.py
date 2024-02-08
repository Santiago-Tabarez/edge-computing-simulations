import csv

from controller.dao_controller import save_load_function
from controller.optimization_controller import _genera_loads, _revenues


# This is not necessary for the simulations
# We save the load function and utility function of the service providers to analyze them latter
def save_players_load_functions(sim):
    for sp in sim.players:

        for avg_l in sp.avg_load:
            for sigma in sp.sigma:
                for hyper_params in sp.hyperparameters:
                    print("+1")
                    loads = _genera_loads(96, avg_l, sigma, hyper_params)
                    chart = []
                    for i in range(0, 95):
                        time = i * 24 / 96
                        chart.append((time, loads[i]))

                    save_load_function(chart, sp, avg_l, sigma, hyper_params)
            # _revenues(loads)


class ServiceProviderController:
    pass
