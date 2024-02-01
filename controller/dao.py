import mysql
import mysql.connector


mydb = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="edge-computing"
)


def save_simulation(sim):
    my_cursor = mydb.cursor()
    query = "SELECT * FROM simulations WHERE simulation_name = %s;"
    my_cursor.execute(query, (sim.simulation_name,))
    results = my_cursor.fetchall()

    # id, simulation_name, max_cores_hosted_min, max_cores_hosted_max, cpu_price_min, cpu_price_max,
    # years_min, years_max, daily_timeslots_min, daily_timeslots_max, amount of players

    if results:

        # TODO add same players checking
        # id = print(results[0].id)
        # print(results[0].max_cores_hosted_min)
        # print(results[0].max_cores_hosted_min)
        # print(results[0].max_cores_hosted_min)

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

        try:
            my_cursor.execute(update_simulation, values)
            mydb.commit()
        except mysql.connector.Error as err:
            print("Error occurred: ", err)
        finally:
            my_cursor.close()

        # my_cursor.execute(query, (max_cores_hosted_min, max_cores_hosted_max, cpu_price_min, cpu_price_max, years_min, years_max,
        # daily_timeslots_min, daily_timeslots_max, amount_of_players, simulation_name))



    else:

        insert_simulation = """
                  INSERT INTO simulations ( simulation_name, max_cores_hosted_min, max_cores_hosted_max, cpu_price_min, cpu_price_max,years_min, years_max, daily_timeslots_min, daily_timeslots_max, amount_of_players) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                  """
        values = (sim.simulation_name, sim.max_cores_hosted_min, sim.max_cores_hosted_max, sim.cpu_price_min,
                  sim.cpu_price_max, sim.years_min, sim.years_max, sim.daily_timeslots_min, sim.daily_timeslots_max,
                  sim.amount_of_players)

        try:
            my_cursor.execute(insert_simulation, values)
            mydb.commit()
            sim.simulation_id = my_cursor.lastrowid
        except mysql.connector.Error as err:
            print("Error occurred: ", err)
        # finally:
        #    my_cursor.close()

        insert_network_owner = """
                                    INSERT INTO network_owners (network_owner_name, simulation_id) 
                                    VALUES ( %s, %s);
                                                  """
        values = (sim.simulation_name, sim.simulation_id)
        try:
            my_cursor.execute(insert_network_owner, values)
            mydb.commit()
            sim.network_owner.player_id = my_cursor.lastrowid

        except mysql.connector.Error as err:
            print("Error occurred: ", err)
        # id, service_provider_name, simulation_id, benefit_factor_min, benefit_factor_max, chi_min, chi_max, avg_load_min, avg_load_max
        insert_service_provider = """
        INSERT INTO service_providers ( service_provider_name, simulation_id, benefit_factor_min, benefit_factor_max, chi_min, chi_max, avg_load_min, avg_load_max) 
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s);
                                     """
        for player in sim.players:
            values = (
                player.service_provider_name, sim.simulation_id, player.benefit_factor_min,
                player.benefit_factor_max,
                player.chi_min,
                player.chi_max, player.avg_load_min, player.avg_load_max)
            try:
                my_cursor.execute(insert_service_provider, values)
                mydb.commit()
                player.player_id = my_cursor.lastrowid

            except mysql.connector.Error as err:
                print("Error occurred: ", err)


#    query = "SELECT id FROM simulations WHERE simulation_name = %s;"
#    my_cursor.execute(query, (sim.simulation_name,))
#    sim.simulation_id = my_cursor.fetchone()[0]


def save_game(game, sim):
    my_cursor = mydb.cursor()

    # id, simulation_id, max_cores_hosted, cpu_price, years, daily_timeslots
    insert_game = """
    INSERT INTO games (simulation_id, max_cores_hosted, cpu_price, years, daily_timeslots) 
    VALUES (%s, %s, %s, %s, %s);
    """

    values = (sim.simulation_id, game.max_cores_hosted, game.price_cpu, game.years, game.daily_timeslots)
    # Executing the query
    try:
        my_cursor.execute(insert_game, values)
        mydb.commit()
        game_id = my_cursor.lastrowid
        # network_operator_id, game_id, benefit_factor, avg_load, chi, allocation, utilities, shapley_value, revenues
        insert_service_provider_game = """
               INSERT INTO service_providers_games (service_provider_id, game_id, benefit_factor, avg_load, chi, allocation, utilities, shapley_value, revenues) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
               """
        insert_network_owner_game = """
                       INSERT INTO network_owners_games (network_owner_id, game_id, shapley_value, revenues) 
                       VALUES (%s, %s, %s, %s);
                       """

        for i in range(game.amount_of_players):
            #player_id = game.players[i].player_id
            avg_load = game.players[i].avg_load
            benefit_factor = game.players[i].benefit_factor
            chi = game.players[i].chi
            allocation = game.gran_coalition.allocation[i]
            utilities = game.gran_coalition.utilities[i]
            shapley_value = game.gran_coalition.shapley_value[i]
            revenues = game.gran_coalition.revenues[i]
            payment = game.gran_coalition.payments[i]

            # Values to insert

            try:
                if i == 0:
                    values = (
                        sim.network_owner.player_id, game_id, shapley_value, revenues)
                    my_cursor.execute(insert_network_owner_game, values)
                else:
                    values = (
                        sim.players[i-1].player_id, game_id, benefit_factor, avg_load, chi, allocation, utilities, shapley_value,
                        revenues)
                    my_cursor.execute(insert_service_provider_game, values)
                mydb.commit()

            except mysql.connector.Error as err:
                print("Error occurred: ", err)

            #print(player_id, avg_load, benefit_factor, chi)

    except mysql.connector.Error as err:
        print("Error occurred: ", err)

    finally:
        my_cursor.close()

    return None


"""

CREATE TABLE `games` (
  `id` int NOT NULL AUTO_INCREMENT,
  `simulation_id` int DEFAULT NULL,
  `max_cores_hosted` int DEFAULT NULL,
  `cpu_price` float DEFAULT NULL,
  `years` float DEFAULT NULL,
  `daily_timeslots` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_sim_id_idx` (`simulation_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='	';

CREATE TABLE `network_owners` (
  `id` int NOT NULL AUTO_INCREMENT,
  `network_owner_name` varchar(45) DEFAULT NULL,
  `simulation_id` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `network_owners_games` (
  `network_owner_id` int NOT NULL,
  `game_id` int NOT NULL,
  `shapley_value` float DEFAULT NULL,
  `revenues` float DEFAULT NULL,
  PRIMARY KEY (`network_owner_id`,`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `service_providers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `service_provider_name` varchar(45) DEFAULT NULL,
  `simulation_id` varchar(45) DEFAULT NULL,
  `benefit_factor_min` float DEFAULT NULL,
  `benefit_factor_max` float DEFAULT NULL,
  `chi_min` float DEFAULT NULL,
  `chi_max` float DEFAULT NULL,
  `avg_load_min` float DEFAULT NULL,
  `avg_load_max` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `service_providers_games` (
  `service_provider_id` int NOT NULL,
  `game_id` int NOT NULL,
  `benefit_factor` float DEFAULT NULL,
  `avg_load` float DEFAULT NULL,
  `chi` float DEFAULT NULL,
  `allocation` float DEFAULT NULL,
  `utilities` float DEFAULT NULL,
  `shapley_value` float DEFAULT NULL,
  `revenues` float DEFAULT NULL,
  PRIMARY KEY (`service_provider_id`,`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `simulations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `simulation_name` varchar(45) NOT NULL,
  `max_cores_hosted_min` int DEFAULT NULL,
  `max_cores_hosted_max` int DEFAULT NULL,
  `cpu_price_min` float DEFAULT NULL,
  `cpu_price_max` float DEFAULT NULL,
  `years_min` float DEFAULT NULL,
  `years_max` float DEFAULT NULL,
  `daily_timeslots_min` int DEFAULT NULL,
  `daily_timeslots_max` int DEFAULT NULL,
  `amount_of_players` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `simulation_name_UNIQUE` (`simulation_name`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

"""
