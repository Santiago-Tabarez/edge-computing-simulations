import os
import sys
import mysql.connector
import logging.config

import numpy as np

from config import config

logger = logging.getLogger(__name__)


class DAOController:
    mydb = mysql.connector.connect(
        host=config.DATABASE_CONNECTION_CONFIG['host'],
        user=config.DATABASE_CONNECTION_CONFIG['user'],
        password=config.DATABASE_CONNECTION_CONFIG['password'],
        database=config.DATABASE_CONNECTION_CONFIG['database']
    )

    # This function is used to modify database tables
    # If database structure is modified those scripts under sql scripts folder  should be updated
    def database_config(self):
        drop = config.DATABASE_MANAGEMENT_CONFIG['drop']
        truncate = config.DATABASE_MANAGEMENT_CONFIG['truncate']
        create = config.DATABASE_MANAGEMENT_CONFIG['create']

        # Determine script directory relative to this file
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        scripts_dir = os.path.join(base_dir, 'sql_scripts')

        # No database modification flags set: check for 'simulations' table
        if sum([drop, truncate, create]) == 0:
            cursor = self.mydb.cursor()
            cursor.execute("SHOW TABLES LIKE 'simulations'")
            if not cursor.fetchone():
                input("Database tables does not exist, we assume this is the first execution, "
                      "it will create tables and execution will be halted, run again "
                      "to execute simulations press enter to continue...")
                sql_file_path = os.path.join(scripts_dir, 'create.sql')
                if not os.path.isfile(sql_file_path):
                    logger.error("SQL script not found: %s", sql_file_path)
                    sys.exit(1)
                with open(sql_file_path, 'r') as file:
                    sql_commands = file.read().strip()
                cursor = self.mydb.cursor()
                for command in sql_commands.split(';'):
                    if command.strip() == '':
                        continue
                    try:
                        cursor.execute(command)
                    except mysql.connector.Error as err:
                        logger.error("Failed executing query %s", command)
                        logger.error("Error is: %s", err)
                        sys.exit(1)
                self.mydb.commit()
                cursor.close()
                self.mydb.close()
                print("SQL script:", sql_file_path, "executed successfully")
                print(
                    "Remember to set all DATABASE_MANAGEMENT_CONFIG variables to False in file config.py to process the simulations")
                sys.exit(0)
            return


        # No database modification, continue to run simulations
        if sum([drop, truncate, create]) == 0:
            return

        if sum([drop, truncate, create]) >= 2:
            logger.error("Two or more variables are True in DATABASE_MANAGEMENT_CONFIG.")
            logger.error("Only one should be true to modify database and none to run simulations.")
            sys.exit(0)


        if truncate:
            input("database tables are going to be truncated, press enter to continue...")
            sql_file_path = os.path.join(scripts_dir, 'truncate.sql')
        elif drop:
            input("Database tables are going to be dropped, press enter to continue...")
            sql_file_path = os.path.join(scripts_dir, 'drop.sql')
        else:  # create
            input("database tables are going to be created, press enter to continue...")
            sql_file_path = os.path.join(scripts_dir, 'create.sql')

        if not os.path.isfile(sql_file_path):
            logger.error("SQL script not found: %s", sql_file_path)
            sys.exit(1)

        with open(sql_file_path, 'r') as file:
            sql_commands = file.read().strip()

        cursor = self.mydb.cursor()

        sql_commands_list = sql_commands.split(';')

        for command in sql_commands_list:
            if command.strip() == '':
                continue
            try:
                cursor.execute(command)
            except mysql.connector.Error as err:
                logger.error("Failed executing query %s", command)
                logger.error("Error is: %s", err)
                sys.exit(1)

        # Committing only after all queries are executed
        self.mydb.commit()
        cursor.close()
        self.mydb.close()
        print("SQL script: ", sql_file_path, "executed successfully")
        print(
            "Remember to set all DATABASE_MANAGEMENT_CONFIG variables to False in file config.py to precess the simulations")
        sys.exit(0)

    # Save general characteristics of a set of games, as max and min for each global value and the players of the games
    # Use database generated id's in simulation objects
    def save_simulation(self, sim):
        cursor = self.mydb.cursor()
        query = "SELECT * FROM simulations WHERE simulation_name = %s;"
        try:

            cursor.execute(query, (sim.simulation_name,))
            results = cursor.fetchall()

            if results:
                sim.is_update = True
                old_sim = results[0]
                query = "SELECT * FROM service_providers where simulation_id = %s;"
                cursor.execute(query, (old_sim[0],))
                db_serv_providers = cursor.fetchall()
                sim_service_provider_names = [sp.service_provider_name for sp in sim.players]
                db_service_provider_names = [sp[1] for sp in db_serv_providers]

                if not set(sim_service_provider_names) == set(db_service_provider_names):
                    sys.exit(
                        "This simulation name is already present in the database with different players, change simulation name or delete old simulation from database.")
                else:
                    logger.warning(
                        "Simulation name already present in the database, games with the same parameters are going to be updated, press Enter to continue")
                    input()

                if sim.max_cores_hosted_min > old_sim[2]:
                    sim.max_cores_hosted_min = old_sim[2]
                if sim.max_cores_hosted_max < old_sim[3]:
                    sim.max_cores_hosted_max = old_sim[3]
                if sim.cpu_price_min > old_sim[4]:
                    sim.cpu_price_min = old_sim[4]
                if sim.cpu_price_max < old_sim[5]:
                    sim.cpu_price_max = old_sim[5]
                if sim.years_min > old_sim[6]:
                    sim.years_min = old_sim[6]
                if sim.years_max < old_sim[7]:
                    sim.years_max = old_sim[7]
                if sim.daily_timeslots_min > old_sim[8]:
                    sim.daily_timeslots_min = old_sim[8]
                if sim.daily_timeslots_max < old_sim[9]:
                    sim.daily_timeslots_max = old_sim[9]

                values = (sim.max_cores_hosted_min, sim.max_cores_hosted_max, sim.cpu_price_min,
                          sim.cpu_price_max, sim.years_min, sim.years_max, sim.daily_timeslots_min,
                          sim.daily_timeslots_max, sim.amount_of_players, sim.simulation_name)

                update_simulation = """
                       UPDATE simulations
                       SET max_cores_hosted_min = %s,
                           max_cores_hosted_max = %s,
                           cpu_price_min = %s,
                           cpu_price_max = %s,
                           years_min = %s,
                           years_max = %s,
                           daily_timeslots_min = %s,
                           daily_timeslots_max = %s,
                           amount_of_players = %s
                       WHERE simulation_name = %s;
                   """

                cursor.execute(update_simulation, values)
                self.mydb.commit()
                sim.simulation_id = old_sim[0]

                select_service_provider = """
                                        SELECT * from service_providers
                                        WHERE service_provider_name = %s AND simulation_id = %s;
                                        """

                update_service_provider = """
                           UPDATE service_providers SET 
                                benefit_factor_min = %s,
                                benefit_factor_max = %s,
                                xi_min = %s,
                                xi_max = %s,
                                frac_sev_at_edge_min = %s, 
                                frac_sev_at_edge_max = %s,
                                avg_load_min = %s,
                                avg_load_max = %s
                           WHERE service_provider_name = %s AND simulation_id = %s; 
                           """

                for player in sim.players:
                    values = (player.service_provider_name, sim.simulation_id)
                    cursor.execute(select_service_provider, values)
                    db_serv_provider = cursor.fetchone()
                    player.player_id = db_serv_provider[0]
                    min_benefit_factor = db_serv_provider[3] if db_serv_provider[3] < min(
                        player.benefit_factor) else min(
                        player.benefit_factor)
                    max_benefit_factor = db_serv_provider[4] if db_serv_provider[4] < max(
                        player.benefit_factor) else max(
                        player.benefit_factor)
                    min_xi = db_serv_provider[5] if db_serv_provider[5] < min(player.xi) else min(player.xi)
                    max_xi = db_serv_provider[6] if db_serv_provider[6] < max(player.xi) else max(player.xi)
                    min_avg_load = db_serv_provider[7] if db_serv_provider[7] < min(player.avg_load) else min(
                        player.avg_load)
                    max_avg_load = db_serv_provider[8] if db_serv_provider[8] < max(player.avg_load) else max(
                        player.avg_load)
                    min_frac = db_serv_provider[9] if db_serv_provider[9] < min(player.frac_of_req) else min(
                        player.frac_of_req)
                    max_frac = db_serv_provider[10] if db_serv_provider[10] < max(player.frac_of_req) else max(
                        player.frac_of_req)

                    values = (min_benefit_factor, max_benefit_factor,
                              min_xi, max_xi,
                              min_avg_load, max_avg_load,
                              min_frac, max_frac,
                              player.service_provider_name, sim.simulation_id)

                    cursor.execute(update_service_provider, values)

                self.mydb.commit()

                select_network_owner_id = """
                                    SELECT id from network_owners
                                    WHERE network_owner_name = %s AND simulation_id = %s;
                                """
                values = (sim.simulation_name, sim.simulation_id)
                cursor.execute(select_network_owner_id, values)
                sim.network_owner.player_id = cursor.fetchone()[0]

            # Simulation game is not present in database
            else:
                # Save data about the game, the max and min for each global value and the amount of players
                insert_simulation = """
                          INSERT INTO simulations ( simulation_name, max_cores_hosted_min, max_cores_hosted_max, cpu_price_min, cpu_price_max,years_min, years_max, daily_timeslots_min, daily_timeslots_max, amount_of_players) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """
                values = (sim.simulation_name, sim.max_cores_hosted_min, sim.max_cores_hosted_max, sim.cpu_price_min,
                          sim.cpu_price_max, sim.years_min, sim.years_max, sim.daily_timeslots_min,
                          sim.daily_timeslots_max,
                          sim.amount_of_players)

                cursor.execute(insert_simulation, values)
                self.mydb.commit()
                # Get the database generated id
                sim.simulation_id = cursor.lastrowid

                # Save the network owner, the name is taken from the simulation name
                insert_network_owner = """
                                            INSERT INTO network_owners (network_owner_name, simulation_id) 
                                            VALUES ( %s, %s);
                                                          """
                values = (sim.simulation_name, sim.simulation_id)
                cursor.execute(insert_network_owner, values)
                self.mydb.commit()
                sim.network_owner.player_id = cursor.lastrowid

                # save the service providers with min and max values of their load and utility functions
                insert_service_provider = """
                INSERT INTO service_providers ( service_provider_name, simulation_id, benefit_factor_min,
                    benefit_factor_max, xi_min, xi_max, frac_sev_at_edge_min, frac_sev_at_edge_max, avg_load_min, avg_load_max) 
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                                         """
                for player in sim.players:
                    values = (
                        player.service_provider_name, sim.simulation_id, min(player.benefit_factor),
                        max(player.benefit_factor),
                        min(player.xi),
                        max(player.xi),
                        min(player.frac_of_req),
                        max(player.frac_of_req),
                        min(player.avg_load), max(player.avg_load))

                    cursor.execute(insert_service_provider, values)
                    self.mydb.commit()
                    player.player_id = cursor.lastrowid

        except mysql.connector.Error as err:
            logger.error("Error occurred: %s", err)

        finally:
            cursor.close()

    # Save the result of each game
    def save_game(self, game, sim):
        cursor = self.mydb.cursor()

        try:
            load_function_ids = [player.load_function_id for player in game.players[1:]]
            joined_load_ids = ', '.join(['%s'] * len(load_function_ids))
            xis = [float(player.xi) for player in game.players[1:]]
            joined_xi = ', '.join(['%s'] * len(xis))
            benefit = [float(player.benefit_factor) for player in game.players[1:]]
            joined_benefit = ', '.join(['%s'] * len(benefit))

            select_game_id = f"""
                                SELECT g.id FROM games AS g
                                JOIN service_providers_games AS spg ON g.id = spg.game_id
                                WHERE g.simulation_id = %s
                                AND g.max_cores_hosted = %s 
                                AND g.cpu_price = %s
                                AND g.years = %s 
                                AND g.daily_timeslots = %s
                                AND g.utility_funct_case = %s
                                AND spg.game_id IN (
                                    SELECT spg_inner.game_id
                                    FROM service_providers_games AS spg_inner
                                    WHERE spg_inner.load_function_id IN ({joined_load_ids})
                                    AND spg_inner.xi IN ({joined_xi})
                                    AND spg_inner.benefit_factor IN ({joined_benefit})
                                    GROUP BY spg_inner.game_id
                                    HAVING COUNT(DISTINCT spg_inner.load_function_id) = %s
                                ) 
                                GROUP BY g.id
                             """

            cpu_price = game.fixed_price if game.fixed_price is not None else game.weighted_per_unit_price
            values = (sim.simulation_id, game.max_cores_hosted, float(cpu_price), game.years, game.daily_timeslots,
                      game.chosen_case,
                      *load_function_ids, *xis, *benefit, len(load_function_ids))

            cursor.execute(select_game_id, values)
            db_game_ids = cursor.fetchone()

            if db_game_ids is not None:
                game_id = db_game_ids[0]

                update_service_provider_game = """
                                UPDATE service_providers_games
                                SET benefit_factor = %s, 
                                    xi = %s, 
                                    allocation = %s, 
                                    utilities = %s, 
                                    shapley_value = %s, 
                                    revenues = %s, 
                                    load_function_id = %s, 
                                    alloc_payment = %s,
                                    frac_of_req = %s,
                                    fairness_payment = %s
                                WHERE service_provider_id = %s AND game_id = %s;
                                """

                update_network_owner_game = """
                                        UPDATE network_owners_games
                                        SET shapley_value = %s, 
                                            revenues = %s, 
                                            fairness_payment = %s
                                        WHERE network_owner_id = %s AND game_id = %s;
                                         """

                for i in range(game.amount_of_players):

                    shapley_value = game.grand_coalition.shapley_value[i]
                    revenues = game.grand_coalition.utilities[i]
                    allocation_payment = game.grand_coalition.allocation_payment[i]
                    fairness_payment = game.grand_coalition.fairness_payment[i]

                    # Is NO
                    if i == 0:
                        values = (
                            float(shapley_value), float(revenues), float(fairness_payment), sim.network_owner.player_id,
                            game_id)
                        cursor.execute(update_network_owner_game, values)
                    # Is SP
                    else:
                        benefit_factor = game.players[i].benefit_factor
                        xi = game.players[i].xi
                        frac = game.players[i].frac_of_load_at_edge
                        allocation = game.grand_coalition.allocation[i]
                        utilities = game.grand_coalition.utilities[i]
                        load_function_id = game.players[i].load_function_id
                        values = (
                            float(benefit_factor), float(xi), float(allocation), float(utilities),
                            float(shapley_value),
                            float(revenues), load_function_id, float(allocation_payment), float(frac),
                            float(fairness_payment), sim.players[i - 1].player_id, game_id)
                        cursor.execute(update_service_provider_game, values)

                    self.mydb.commit()

            else:
                # Save global values of this game
                insert_game = """
                INSERT INTO games (simulation_id, max_cores_hosted, cpu_price, years, daily_timeslots, utility_funct_case) 
                VALUES (%s, %s, %s, %s, %s, %s);
                    """

                values = (sim.simulation_id, game.max_cores_hosted, cpu_price, game.years, game.daily_timeslots, game.chosen_case)

                cursor.execute(insert_game, values)
                self.mydb.commit()
                game_id = cursor.lastrowid

                insert_service_provider_game = """
                       INSERT INTO service_providers_games (service_provider_id, game_id, benefit_factor, xi, allocation, utilities, shapley_value, revenues, load_function_id, alloc_payment, frac_of_req, fairness_payment) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                       """
                insert_network_owner_game = """
                               INSERT INTO network_owners_games (network_owner_id, game_id, shapley_value, revenues, fairness_payment) 
                               VALUES (%s, %s, %s, %s, %s);
                               """
                # Save the value of load function and utility function for the current game
                # And the result of the game for each player
                for i in range(game.amount_of_players):

                    shapley_value = game.grand_coalition.shapley_value[i]
                    revenues = game.grand_coalition.utilities[i]
                    alloc_payments = game.grand_coalition.allocation_payment[i]
                    fairness_payments = game.grand_coalition.fairness_payment[i]

                    # Is NO
                    if i == 0:
                        values = (
                            sim.network_owner.player_id,
                            game_id,
                            float(shapley_value),
                            float(revenues),
                            float(fairness_payments)
                        )
                        cursor.execute(insert_network_owner_game, values)
                    # Is SP
                    else:
                        benefit_factor = game.players[i].benefit_factor
                        xi = game.players[i].xi
                        frac_of_req = game.players[i].frac_of_load_at_edge
                        allocation = game.grand_coalition.allocation[i]
                        utilities = game.grand_coalition.utilities[i]
                        load_function_id = game.players[i].load_function_id
                        values = (
                            sim.players[i - 1].player_id, game_id, float(benefit_factor), float(xi), float(allocation),
                            float(utilities),
                            float(shapley_value),
                            float(revenues), load_function_id, float(alloc_payments), float(frac_of_req),
                            float(fairness_payments))
                        cursor.execute(insert_service_provider_game, values)

                    self.mydb.commit()

            if config.SAVE_FUNCTION['utility']:

                select_utility_functions = """
                                        SELECT 1 FROM utility_function_values 
                                        WHERE player_id = %s 
                                        AND game_id = %s 
                                    ;
                                    """

                insert_service_utility_function = """
                                     INSERT INTO utility_function_values (player_id, game_id, time, value) 
                                     VALUES (%s, %s, %s, %s);
                                         """


                for i, player in enumerate(game.players[1:]):

                    values = (player.player_id, game_id)
                    cursor.execute(select_utility_functions, values)

                    # This load function is not new
                    # In case sigma != 0 we need to update generated values
                    db_load_funct = cursor.fetchall()
                    if db_load_funct is not None:
                        select_utility_functions = """ 
                                                DELETE FROM utility_function_values 
                                                WHERE player_id = %s 
                                                AND game_id = %s 
                                                ;
                                                """
                        cursor.execute(select_utility_functions, values)
                        self.mydb.commit()

                    utility = player.benefit_factor * np.array(player.load_function) * player.frac_of_load_at_edge * game.years * 365
                    chart = [(i * 24 / game.daily_timeslots, utility[i]) for i in range(game.daily_timeslots - 1)]

                    for c in chart:
                        values = (player.player_id, game_id, c[0], float(c[1]))
                        cursor.execute(insert_service_utility_function, values)

                    self.mydb.commit()

        except mysql.connector.Error as err:
            logger.error("Error occurred: %s", err)

        finally:
            cursor.close()

    def save_load_function(self, chart, player_id, avg_l, sigma, hyper_params):
        cursor = self.mydb.cursor()
        try:

            select_load_functions = """
                SELECT id FROM load_functions 
                WHERE service_provider_id = %s 
                AND sigma = %s 
                AND avg_load = %s 
                AND hyper_params_a_k = %s 
                AND hyper_params_t_k = %s
            ;
            """
            values = (player_id, sigma, avg_l, str(hyper_params[0]), str(hyper_params[1]))
            cursor.execute(select_load_functions, values)

            # This load function is not new
            # In case sigma != 0 we need to update generated values
            db_load_funct = cursor.fetchone()
            if db_load_funct is not None:
                function_id = db_load_funct[0]
                if sigma != 0:
                    if config.SAVE_FUNCTION['load']:

                        update_service_provider_function = """
                                        UPDATE load_function_values
                                        SET load_value = %s
                                        WHERE function_id = %s AND time = %s;
                                                  """

                        for i in chart:
                            values = (i[1], player_id, function_id, i[0])
                            cursor.execute(update_service_provider_function, values)
                        self.mydb.commit()
            else:
                # id, service_provider_id, sigma, avg_load, hyper_params_a_k, hyper_params_t_k
                insert_load_functions = """
                              INSERT INTO load_functions (service_provider_id, sigma , avg_load,  hyper_params_a_k ,hyper_params_t_k) 
                              VALUES (%s, %s, %s, %s, %s);
                                  """

                values = (player_id, sigma, avg_l, str(hyper_params[0]), str(hyper_params[1]))
                cursor.execute(insert_load_functions, values)
                function_id = cursor.lastrowid
                # Save load function values for this game
                if config.SAVE_FUNCTION['load']:
                    insert_service_provider_function = """
                              INSERT INTO load_function_values (function_id, time, load_value) 
                              VALUES (%s, %s, %s);
                                  """

                    for i in chart:
                        values = (function_id, i[0], float(i[1]))
                        cursor.execute(insert_service_provider_function, values)

                    self.mydb.commit()

            return function_id

        except mysql.connector.Error as err:
            logger.error("Error occurred: %s", err)

        finally:
            cursor.close()
