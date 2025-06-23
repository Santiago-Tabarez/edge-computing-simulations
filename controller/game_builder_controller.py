import itertools
import logging
import sys

from config import config
from controller.dao_controller import DAOController
from controller.load_function_controller import generate_loads

from model.game import Game
from model.network_owner import NetworkOwner
from model.service_provider import ServiceProvider
from model.service_provider_sim import ServiceProviderSimulation
from model.simulation import Simulation

logger = logging.getLogger(__name__)


class GameBuilderController:

    @staticmethod
    def compute_xi_from_frac(case, fraction, d_prime, rho=None, beta=None):

        if case not in {0, 1, 2, 3}:
            raise ValueError("Case must be 0, 1, 2, or 3.")
        if not (0 < fraction < 1):
            raise ValueError("Fraction must be strictly between 0 and 1.")
        if d_prime <= 0:
            raise ValueError("d_prime must be positive.")

        if case == 0:
            if rho is None:
                raise ValueError("Parameter 'rho' is required for case 0.")
            result = d_prime / (rho * (1 - fraction))

        elif case == 1:
            if beta is None:
                raise ValueError("Parameter 'beta' is required for case 1.")
            result = d_prime / (beta * (1 - fraction))

        elif case == 2:
            result = 1 - fraction
            if result <= 0:
                raise ValueError("Computed xi is non‐positive. Check the fraction for case 2.")

        else:  # case == 3
            result = d_prime / (1 - fraction)

        # This is needed to update the database results, if more precession is needed use Double in the database
        return float(f"{result:.6g}")

    @staticmethod
    def compute_frac_from_xi(case, xi, d_prime, rho=None, beta=None):
        """
        Inverse of compute_xi_from_frac.
        Given case ∈ {0,1,2,3}, xi, and d_prime (>0),
        returns fraction ∈ (0,1) rounded to 6 significant figures
        to match MySQL FLOAT precision.
        Requires rho for case 0, beta for case 1.
        """
        # validate inputs
        if case not in {0, 1, 2, 3}:
            raise ValueError("Case must be 0, 1, 2, or 3.")
        if xi <= 0:
            raise ValueError("xi must be positive.")
        if d_prime <= 0:
            raise ValueError("d_prime must be positive.")

        # compute raw fraction by case
        if case == 0:
            if rho is None:
                raise ValueError("Parameter 'rho' is required for case 0.")
            fraction = 1 - (d_prime / (rho * xi))
        elif case == 1:
            if beta is None:
                raise ValueError("Parameter 'beta' is required for case 1.")
            fraction = 1 - (d_prime / (beta * xi))
        elif case == 2:
            fraction = 1 - xi
        else:  # case == 3
            fraction = 1 - (d_prime / xi)

        # ensure the result is in (0,1)
        if not (0 < fraction < 1):
            raise ValueError(f"Computed fraction {fraction} is out of bounds (0,1).")

        # round to 6 significant figures for MySQL FLOAT compatibility
        return float(f"{fraction:.6g}")


    # Auxiliary functions to read the values from .yaml files

    # Transform an immediate value or a range
    # into a list of values
    @staticmethod
    def parse_value_list(value):
        if isinstance(value, list):
            if isinstance(value[0], str) and ':' in value[0]:
                return GameBuilderController.create_value_list(value[0])
            return value
        return [value]

    # Create a list of values from a string 'min:max:amount'
    @staticmethod
    def create_value_list(value_range):
        start, end, total_amount = map(float, value_range.split(':'))
        if total_amount <= 1:
            return [start]
        step = (end - start) / (total_amount - 1)
        return [start + i * step for i in range(int(total_amount))]

    # Used to a set of games from each of the .yaml files under the "simulations to process" folder
    # Will create a different game for each possible combination of the following values:
    # game: max_cores_hosted, daily_timeslots, years, price_cpu
    # for each service_provider: avg_load, benefit_factor, sigma, each pair of hyperparameters and xi
    # The amount of games will be the product of the amount of different values of those properties
    def create_games(self, game_data):

        daoC = DAOController()
        # transform the input values into a list
        max_cores_hoisted_list = self.parse_value_list(game_data['max_cores_hosted'])
        daily_timeslots_list = self.parse_value_list(game_data['daily_timeslots'])
        years_list = self.parse_value_list(game_data['years'])

        chosen_case = game_data['selected_case']
        aux_funct_exponents = game_data['cases'][chosen_case]

        simulation_type = ''
        # if config.VALUE_FUNCTION_MODE['additive_estimation']:
        #    simulation_type = 'additive_estimation'
        if config.VALUE_FUNCTION_MODE['additive_deterministic']:
            simulation_type = 'additive_deterministic'
        elif config.VALUE_FUNCTION_MODE['non_additive_deterministic']:
            simulation_type = 'non_additive_deterministic'
        elif config.VALUE_FUNCTION_MODE['non_additive_estimation']:
            simulation_type = 'non_additive_estimation'

        variable_cpu_price = config.EXTRA_CONSIDERATIONS['variable_cpu_price']
        per_time_slot_allocation = config.EXTRA_CONSIDERATIONS['per_time_slot_allocation']

        # If per unit cpu price is variable or allocation is variable through time the slots then contributions are not independent
        # We allow it but give the proper warning
        if variable_cpu_price and config.VALUE_FUNCTION_MODE['additive_deterministic']:
            logger.error(
                "Error: simulation type is additive (players contribution is independent) and CPU price is variable"
                "This combination is incompatible")
            sys.exit("Modify the configuration file and execute again")
        if per_time_slot_allocation and config.VALUE_FUNCTION_MODE['additive_deterministic']:
            logger.error(
                "Error: simulation type is additive (players contribution is independent) and allocation is variable in time slots"
                "This combination is incompatible")
            sys.exit("Modify the configuration file and execute again")

        amount_of_players = 1
        sim_players = []
        # First we create the simulation that will wrap all the games and add the players to it
        for sp in game_data['service_providers']:

            a_k = self.parse_value_list(sp['a_k'])
            t_k = self.parse_value_list(sp['t_k'])
            hyperparameters = list(zip(a_k, t_k))
            avg_load = self.parse_value_list(sp['avg_load'])
            benefit_factor = self.parse_value_list(sp['benefit_factor'])

            if 'frac_of_requests' in sp:
                fac_of_req = self.parse_value_list(sp['frac_of_requests'])
                xi = [0] * len(fac_of_req)
            else:
                xi = self.parse_value_list(sp['xi'])
                fac_of_req = [0] * len(xi)

            sigma = self.parse_value_list(sp['sigma'])

            for sp_id in sp['service_provider_name']:
                amount_of_players += 1

                sps = ServiceProviderSimulation(sp_id, sigma, avg_load, benefit_factor, xi, fac_of_req, hyperparameters)
                sim_players.append(sps)

        prices = game_data['prices']

        if not variable_cpu_price:
            cpu_price_list = prices['when_fixed']['cpu_price']
            cpu_price_list = self.parse_value_list(cpu_price_list)
            # Network owner is created here taking the name of the simulation
            sim = Simulation(game_data['simulation_name'], min(max_cores_hoisted_list), max(max_cores_hoisted_list),
                             min(cpu_price_list), max(cpu_price_list),
                             min(years_list), max(years_list), min(daily_timeslots_list), max(daily_timeslots_list),
                             amount_of_players, simulation_type, variable_cpu_price, per_time_slot_allocation)
            prices = cpu_price_list
        else:
            price_variables = prices['when_variable']
            min_cores_hosted_list = self.parse_value_list(price_variables['min_cores_hosted'])
            min_cpu_price_list = self.parse_value_list(price_variables['min_cpu_price'])
            max_cpu_price_list = self.parse_value_list(price_variables['max_cpu_price'])
            variable_prices_list = list(zip(min_cores_hosted_list, min_cpu_price_list, max_cpu_price_list))
            # Network owner is created here taking the name of the simulation
            sim = Simulation(game_data['simulation_name'], min(min_cores_hosted_list), max(max_cores_hoisted_list),
                             min(min_cpu_price_list), max(max_cpu_price_list),
                             min(years_list), max(years_list), min(daily_timeslots_list), max(daily_timeslots_list),
                             amount_of_players, simulation_type, variable_cpu_price, per_time_slot_allocation)

            prices = variable_prices_list

        sim.players = sim_players

        # Save simulation and players in the database, retrieve the database assigned ids for players and simulation
        daoC.save_simulation(sim)

        # We iterate over the daily time slots, to create the load functions and also to create the games
        for daily_tl in self.parse_value_list(game_data['daily_timeslots']):

            service_providers_load_functions = []
            # First we calculate all the load functions and assign them to the players
            # We need the value of the load function for each timeslot

            # This is a workaround to match the players with the corresponding load function
            # Since a different service provider will be created for each different name
            cloned_sp = []
            for sp in game_data['service_providers']:
                name_length = len(sp['service_provider_name'])
                if name_length == 1:
                    cloned_sp.append(False)
                else:
                    cloned_sp.append(False)
                    cloned_sp.extend([True] * (name_length - 1))

                # For each SP we generate all the possible load functions and save it
                # For that, we generate all the possible combinations of the SPs load function properties except 'service_provider_name'
                sigmas = self.parse_value_list(sp['sigma'])
                for sigma, avg_load, hyper_params in itertools.product(sigmas, sp['avg_load'],
                                                                       list(zip(sp['a_k'], sp['t_k']))):

                    # Now for each service provider name we will calculate the load function
                    # If sigma != 0 same load function will be different for "same" SP
                    for service_provider_name in sp['service_provider_name']:
                        loads = generate_loads(daily_tl, sigma, avg_load, hyper_params)

                        # Just to visualize it better we create the corresponding chart with hours on x and load value on y
                        chart = [(i * 24 / daily_tl, loads[i]) for i in range(daily_tl - 1)]

                        # Get the player saved in the database when simulation was saved, so we can assign it the load function
                        saved_service_provider = next(
                            (player for player in sim.players if player.service_provider_name == service_provider_name),
                            None)

                        # Database id of the saved load function
                        load_function_id = daoC.save_load_function(chart, saved_service_provider.player_id,
                                                                   avg_load,
                                                                   sigma, hyper_params)

                        # benefit_factor and xi will be assigned later since they determine the amount of games but not de amount of load functions
                        sp_aux = ServiceProvider(player_id=saved_service_provider.player_id,
                                                 player_name=service_provider_name, avg_load=avg_load,
                                                 benefit_factor=None, xi=None, frac_of_load_at_edge=None, sigma=sigma,
                                                 hyperparameters=hyper_params, load_function=loads,
                                                 load_function_id=load_function_id)


                        service_providers_load_functions.append(sp_aux)
                        saved_service_provider.load_functions.append([load_function_id, sigma, avg_load, loads])

            # If a players have two or more load functions, then we need to create a different game for each combination of them
            # This code is to create a list of lists, where the inner one is the load function for each player and the external one
            # has an element for each different game to be created due to different load functions
            grouped_by_player_id = {}
            for sp in service_providers_load_functions:
                if sp.player_id not in grouped_by_player_id:
                    grouped_by_player_id[sp.player_id] = []
                grouped_by_player_id[sp.player_id].append(sp)

            # Extract lists of service providers for each player_id
            grouped_lists = list(grouped_by_player_id.values())
            # Use product to generate all combinations across groups, each combination will be a list of lists
            # This is very memory consuming, so we may run out of memory in case of many players and many load functions
            all_combinations = list(itertools.product(*grouped_lists))
            # Flatten each combination into a single list
            result_service_providers_list = [list(combination) for combination in all_combinations]

            # Now that we created and assigned load functions we will create the games and assign them the corresponding function
            for max_cor_h in self.parse_value_list(game_data['max_cores_hosted']):
                for year in years_list:

                    # self.parse_value_list(game_data['cpu_price']):
                    for price in prices:
                        if variable_cpu_price:
                            amortized_price = price[2] / (365 * daily_tl * year)
                        else:
                            amortized_price = price / (365 * daily_tl * year)
                        for sp_list in result_service_providers_list:
                            sp_utility_functions = []
                            using_fractions = None
                            for sp in game_data['service_providers']:
                                benefit_factors = self.parse_value_list(sp['benefit_factor'])
                                if 'frac_of_requests' in sp:
                                    if using_fractions == 0:
                                        logger.error(
                                            "Set all SPs' diminishing return parameter as the fraction of the total load served "
                                            "at the edge or by directly defining the value of xi, but not a combination of both")
                                        sys.exit("Fix this and re-run the simulation")

                                    else:
                                        using_fractions = 1
                                    fractions = self.parse_value_list(sp['frac_of_requests'])
                                    combinations = list(itertools.product(benefit_factors, fractions))
                                    sp_utility_functions.append(combinations)
                                else:
                                    if using_fractions == 1:
                                        logger.error(
                                            "Set all SPs' diminishing return parameter as the fraction of the total load served "
                                            "at the edge or by directly defining the value of xi, but not a combination of both")
                                        sys.exit("Fix this and re-run the simulation")
                                    else:
                                        using_fractions = 0
                                    xis = self.parse_value_list(sp['xi'])
                                    combinations = list(itertools.product(benefit_factors, xis))
                                    sp_utility_functions.append(combinations)
                                # Generate all combinations of benefit_factor and xi for this service provider



                            # Create the cartesian product of combinations across all service providers
                            all_sp_utility_functions_combinations = list(itertools.product(*sp_utility_functions))
                            for combination in all_sp_utility_functions_combinations:
                                # Price is variable
                                if isinstance(price, tuple):
                                    game = Game(game_data['simulation_name'], years=year,
                                                max_cores_hosted=max_cor_h,
                                                min_cores_hosted=price[0],
                                                min_cpu_price=price[1],
                                                max_cpu_price=price[2],
                                                amount_of_players=1,
                                                daily_timeslots=daily_tl,
                                                aux_funct_exponents=aux_funct_exponents,
                                                chosen_case=chosen_case,
                                                simulation_type = simulation_type)
                                # Price is fixed
                                else:
                                    game = Game(game_data['simulation_name'], years=year,
                                                max_cores_hosted=max_cor_h,
                                                min_cores_hosted=0,
                                                min_cpu_price=price,
                                                max_cpu_price=price,
                                                amount_of_players=1,
                                                daily_timeslots=daily_tl,
                                                aux_funct_exponents=aux_funct_exponents,
                                                chosen_case=chosen_case,
                                                simulation_type= simulation_type)

                                # Network owner takes name from the simulation name
                                network_owner = NetworkOwner(game_data['simulation_name'])
                                game.add_player(network_owner)
                                i = 0
                                for j, serv_prov in enumerate(sp_list):
                                    if cloned_sp[j]:
                                        i -= 1
                                    util_funct = combination[i]
                                    i += 1
                                    # It will create len('service_provider_name') players with the same values but different names
                                    # This is just to easily add many players with the same values
                                    # for sp_load_funct in osp:
                                    benefit_fac = util_funct[0]
                                    rho = serv_prov.avg_load * benefit_fac
                                    if using_fractions:
                                        frac_val = util_funct[1]
                                        xi_val = self.compute_xi_from_frac(chosen_case, frac_val, amortized_price, rho=rho, beta=benefit_fac)
                                    else:
                                        xi_val = util_funct[1]
                                        frac_val = self.compute_frac_from_xi(chosen_case, xi_val, amortized_price, rho=rho, beta=benefit_fac)


                                    service_provider = ServiceProvider(
                                        player_id=serv_prov.player_id,
                                        player_name=serv_prov.player_name, avg_load=serv_prov.avg_load,
                                        benefit_factor=benefit_fac, xi=xi_val, frac_of_load_at_edge=frac_val,
                                        sigma=serv_prov.sigma_load, hyperparameters=serv_prov.hyperparameters,
                                        load_function=serv_prov.load_function,
                                        load_function_id=serv_prov.load_function_id)

                                    game.amount_of_players += 1
                                    game.add_player(service_provider)

                                sim.games.append(game)

        return sim
