import itertools

from controller.dao_controller import save_simulation, save_load_function
from controller.optimization_controller import _genera_loads
from model.coalition import Coalition
from model.game import Game
from model.network_owner import NetworkOwner
from model.service_provider import ServiceProvider
from model.service_provider_sim import ServiceProviderSimulation
from model.simulation import Simulation
from utils.yaml_data_reader import YAMLDataReader


# Aux functions to transform an immediate value, or a set of values defined as [min:max:amount_of_values] into a list
def parse_value_list(value):
    if isinstance(value, list):
        if isinstance(value[0], str):
            return create_value_list(value[0])
        else:
            return value
    else:
        _list = [value]
        return _list


def create_value_list(values):
    start, end, total_amount = map(float, values.split(':'))
    total_amount = int(total_amount)
    if total_amount <= 1:
        return [start]
    step = (end - start) / (total_amount - 1)
    return [start + i * step for i in range(total_amount)]


# Get a list of games from each of the .yaml files under the "games to process" folder
# Will create a different game for each possible combination of the following values:
# game: max_cores_hosted, daily_timeslots, years, price_cpu
# for each service_provider: avg_load, benefit_factor, xi
# The amount of games will be the product of the length of those properties
def create_games(game_data):
    # transform the input values into a list
    max_cores_hoisted_lis = parse_value_list(game_data['max_cores_hosted'])
    daily_timeslots_list = parse_value_list(game_data['daily_timeslots'])
    years_list = parse_value_list(game_data['years'])
    cpu_price_list = parse_value_list(game_data['cpu_price'])

    amount_of_players = 1
    sim_players = []
    # Create the simulation and add the players to it
    for sp in game_data['service_providers']:

        a_k = parse_value_list(sp['a_k'])
        t_k = parse_value_list(sp['t_k'])

        hyperparameters = list(zip(a_k, t_k))
        avg_load = parse_value_list(sp['avg_load'])
        benefit_factor = parse_value_list(sp['benefit_factor'])
        xi = parse_value_list(sp['xi'])
        sigma = parse_value_list(sp['sigma'])

        for sp_id in sp['service_provider_name']:
            amount_of_players += 1
            sps = ServiceProviderSimulation(sp_id, sigma, avg_load, benefit_factor, xi, hyperparameters)
            sim_players.append(sps)

    sim = Simulation(game_data['simulation_name'], min(max_cores_hoisted_lis), max(max_cores_hoisted_lis),
                     min(cpu_price_list), max(cpu_price_list),
                     min(years_list), max(years_list), min(daily_timeslots_list), max(daily_timeslots_list),
                     amount_of_players)
    sim.players = sim_players

    save_simulation(sim)

    # All the combinations of the game variables
    # for each daily timeslot we calculate all the load function values
    for daily_tl in parse_value_list(game_data['daily_timeslots']):

        for sp in game_data['service_providers']:
            # Generate combinations of all properties except 'service_provider_name'
            non_name_combinations = itertools.product(sp['sigma'], sp['avg_load'], list(zip(sp['a_k'], sp['t_k'])))
            new_game = 1

            # Now, handle 'service_provider_name' separately in an inner loop if necessary
            print(non_name_combinations)
            for sp_combinations in non_name_combinations:
                print(sp_combinations[0])
                print(sp_combinations[1])
                print(sp_combinations[2])
                service_providers_load_functions = []
                load_functions_id = []
                charts = []
                avg_loads = sp_combinations[1]
                sigmas = sp_combinations[0]
                for service_provider_name in sp['service_provider_name']:  # This is a bit artificial since it's always a single element
                    print(service_provider_name)
                    # if last_sigma == sp_combinations[1] and last_average == sp_combinations[2] and last_hyperparams == sp_combinations[3]:

                    # daily_timeslots, avg_load, sigma, hyper_params)
                    #avg_loads.append(sp_combinations[1])
                    #sigmas.append(sp_combinations[0])
                    loads = _genera_loads(daily_tl, sp_combinations[1], sp_combinations[0], sp_combinations[2])
                    chart = []
                    for i in range(0, daily_tl - 1):
                        time = i * 24 / 96
                        chart.append((time, loads[i]))

                    current_service_provider_load_function = next(
                        (player for player in sim.players if player.service_provider_name == service_provider_name),
                        None)
                    service_providers_load_functions.append(current_service_provider_load_function)

                    load_function_id = save_load_function(chart, current_service_provider_load_function,
                                                          sp_combinations[1],
                                                          sp_combinations[0], sp_combinations[2])
                    charts.append(loads)
                    load_functions_id.append(load_function_id)

                for max_cor_h in parse_value_list(game_data['max_cores_hosted']):
                    for year in parse_value_list(game_data['years']):
                        for price in parse_value_list(game_data['cpu_price']):

                            for sp_ut in itertools.product(
                                    *[itertools.product(sp['xi'], sp['benefit_factor'])
                                      for sp in game_data['service_providers']]):

                                # sp_ut is a tuple of tuples, where each inner tuple is a combination of (xi, benefit_factor)
                                for xi, benefit_factor in sp_ut:
                                    # Now you can work with individual xi and benefit_factor values
                                    print("xi:", xi, "Benefit Factor:", benefit_factor)

                                    game = Game(game_data['simulation_name'], years=year, max_cores_hosted=max_cor_h,
                                                price_cpu=price,
                                                amount_of_players=1,
                                                daily_timeslots=daily_tl)

                                    # Network operator takes name from the simulation name
                                    network_owner = NetworkOwner(game_data['simulation_name'])
                                    game.add_player(network_owner)

                                    # It will create len('service_provider_name') players with the same values but different names
                                    i = 0

                                    for service_provider_name in sp['service_provider_name']:
                                        service_provider = ServiceProvider(
                                            service_providers_load_functions[i].player_id,
                                            player_name=service_provider_name, avg_load=avg_loads,
                                            benefit_factor=benefit_factor, xi=xi,
                                            sigma=sigmas, hyperparameters=sp_combinations[2],
                                            load_function=charts[i], load_function_id=load_functions_id[i])
                                        i += 1
                                        game.amount_of_players += 1
                                        game.add_player(service_provider)

                                    # Create all permutations from players, this is all possible coalitions
                                    for col in YAMLDataReader.all_permutations(game.players)[1:]:
                                        coal = Coalition(col, 0)
                                        game.coalitions.append(coal)

                                    sim.games.append(game)

    return sim
