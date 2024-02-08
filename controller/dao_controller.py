import sys

import mysql
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="edge-computing"
)


# Save general characteristics of the simulation, as max and min for each global value and the players of the game
# Save database generated id's in Simulation objects
def save_simulation(sim):
    cursor = mydb.cursor()
    query = "SELECT * FROM simulations WHERE simulation_name = %s;"
    try:

        cursor.execute(query, (sim.simulation_name,))
        results = cursor.fetchall()

        # TODO this case is not completed yet
        # check players are the same and update max and min values
        # update in case of overlap
        if results:

            sys.exit("This simulation name is already present in the database, and simulation update is not completed yet.")

            #values = (sim.max_cores_hosted_min, sim.max_cores_hosted_max, sim.cpu_price_min,
            #          sim.cpu_price_max, sim.years_min, sim.years_max, sim.daily_timeslots_min,
            #          sim.daily_timeslots_max, sim.amount_of_players, sim.simulation_name)

            # update_simulation = """
            #        UPDATE simulations
            #        SET max_cores_hosted_min = %s,
            #            max_cores_hosted_max = %s,
            #            cpu_price_min = %s,
            #            cpu_price_max = %s,
            #            years_min = %s,
            #            years_max = %s,
            #            daily_timeslots_min = %s,
            #            daily_timeslots_max = %s,
            #            amount_of_players = %s
            #        WHERE simulation_name = %s;
            #    """

            #cursor.execute(update_simulation, values)
            #mydb.commit()

        # Simulation game was not present in database
        else:
            # Save data about the game, the max and min for each global value and the amount of players
            insert_simulation = """
                      INSERT INTO simulations ( simulation_name, max_cores_hosted_min, max_cores_hosted_max, cpu_price_min, cpu_price_max,years_min, years_max, daily_timeslots_min, daily_timeslots_max, amount_of_players) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
            values = (sim.simulation_name, sim.max_cores_hosted_min, sim.max_cores_hosted_max, sim.cpu_price_min,
                      sim.cpu_price_max, sim.years_min, sim.years_max, sim.daily_timeslots_min, sim.daily_timeslots_max,
                      sim.amount_of_players)

            cursor.execute(insert_simulation, values)
            mydb.commit()
            # Get the database generated id
            sim.simulation_id = cursor.lastrowid

            # Save the network owner, the name is taken from the simulation name
            insert_network_owner = """
                                        INSERT INTO network_owners (network_owner_name, simulation_id) 
                                        VALUES ( %s, %s);
                                                      """
            values = (sim.simulation_name, sim.simulation_id)
            cursor.execute(insert_network_owner, values)
            mydb.commit()
            sim.network_owner.player_id = cursor.lastrowid

            # save the service providers
            insert_service_provider = """
            INSERT INTO service_providers ( service_provider_name, simulation_id, benefit_factor_min,
                benefit_factor_max, chi_min, chi_max, avg_load_min, avg_load_max) 
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s);
                                     """
            for player in sim.players:
                values = (
                    player.service_provider_name, sim.simulation_id, min(player.benefit_factor),
                    max(player.benefit_factor),
                    min(player.xi),
                    max(player.xi), min(player.avg_load), max(player.avg_load))

                cursor.execute(insert_service_provider, values)
                mydb.commit()
                player.player_id = cursor.lastrowid

    except mysql.connector.Error as err:
        print("Error occurred: ", err)
    finally:
        cursor.close()


# Save the result of each game
def save_game(game, sim):
    cursor = mydb.cursor()

    try:
        # Save input values for this game
        insert_game = """
        INSERT INTO games (simulation_id, max_cores_hosted, cpu_price, years, daily_timeslots) 
        VALUES (%s, %s, %s, %s, %s);
            """

        values = (sim.simulation_id, game.max_cores_hosted, game.price_cpu, game.years, game.daily_timeslots)
        # Executing the query

        cursor.execute(insert_game, values)
        mydb.commit()
        game_id = cursor.lastrowid
        # network_operator_id, game_id, benefit_factor, avg_load, xi, allocation, utilities, shapley_value, revenues
        insert_service_provider_game = """
               INSERT INTO service_providers_games (service_provider_id, game_id, benefit_factor, avg_load, chi, allocation, utilities, shapley_value, revenues, load_function_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
               """
        insert_network_owner_game = """
                       INSERT INTO network_owners_games (network_owner_id, game_id, shapley_value, revenues) 
                       VALUES (%s, %s, %s, %s);
                       """
        # Save the result for each player
        for i in range(game.amount_of_players):

            avg_load = game.players[i].avg_load
            benefit_factor = game.players[i].benefit_factor
            xi = game.players[i].xi
            allocation = game.grand_coalition.allocation[i]
            utilities = game.grand_coalition.utilities[i]
            shapley_value = game.grand_coalition.shapley_value[i]
            revenues = game.grand_coalition.revenues[i]
            payment = game.grand_coalition.payments[i]
            load_function_id = game.players[i].load_function_id

            # Is NO
            if i == 0:
                values = (
                    sim.network_owner.player_id, game_id, shapley_value, revenues)
                cursor.execute(insert_network_owner_game, values)
            else:
                values = (
                    sim.players[i - 1].player_id, game_id, benefit_factor, avg_load, xi, allocation, utilities,
                    shapley_value,
                    revenues, load_function_id)
                cursor.execute(insert_service_provider_game, values)

            mydb.commit()
    except mysql.connector.Error as err:
        print("Error occurred: ", err)

    finally:
        cursor.close()


def save_load_function(chart, sp, avg_l, sigma, hyper_params):
    cursor = mydb.cursor()
    try:
        # id, service_provider_id, sigma, avg_load, hyper_params_a_k, hyper_params_t_k
        insert_load_functions = """
              INSERT INTO load_functions (service_provider_id, sigma , avg_load,  hyper_params_a_k ,hyper_params_t_k) 
              VALUES (%s, %s, %s, %s, %s);
                  """

        values = (sp.player_id, sigma, avg_l, str(hyper_params[0]), str(hyper_params[1]))
        cursor.execute(insert_load_functions, values)
        function_id = cursor.lastrowid
        # Save input values for this game
        insert_service_provider_function = """
          INSERT INTO service_providers_load_functions (service_provider_id, function_id, time, load_value) 
          VALUES (%s, %s, %s, %s);
              """

        for i in chart:
            values = (sp.player_id, function_id, i[0], i[1])
            cursor.execute(insert_service_provider_function, values)

        mydb.commit()
        return function_id

    except mysql.connector.Error as err:
        print("Error occurred: ", err)

    finally:
        cursor.close()
