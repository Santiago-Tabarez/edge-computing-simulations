CREATE TABLE `simulations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `simulation_name` VARCHAR(45) NOT NULL,
  `max_cores_hosted_min` INT NOT NULL,
  `max_cores_hosted_max` INT NOT NULL,
  `cpu_price_min` FLOAT NOT NULL,
  `cpu_price_max` FLOAT NOT NULL,
  `years_min` FLOAT NOT NULL,
  `years_max` FLOAT NOT NULL,
  `daily_timeslots_min` INT NOT NULL,
  `daily_timeslots_max` INT NOT NULL,
  `amount_of_players` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `simulation_name_UNIQUE` (`simulation_name`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `games` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `simulation_id` INT NOT NULL,
  `max_cores_hosted` INT NOT NULL,
  `cpu_price` FLOAT NOT NULL,
  `years` FLOAT NOT NULL,
  `daily_timeslots` INT NOT NULL,
  `utility_funct_case` INT DEFAULT NULL,
  `simulation_type` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_sim_id_idx` (`simulation_id`),
  CONSTRAINT `fk_games_simulations` FOREIGN KEY (`simulation_id`) REFERENCES `simulations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `network_owners` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `network_owner_name` VARCHAR(45) NOT NULL,
  `simulation_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_network_owners_simulations` (`simulation_id`),
  CONSTRAINT `fk_network_owners_simulations` FOREIGN KEY (`simulation_id`) REFERENCES `simulations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `network_owners_games` (
  `network_owner_id` INT NOT NULL,
  `game_id` INT NOT NULL,
  `shapley_value` FLOAT NOT NULL,
  `revenues` FLOAT NOT NULL,
  `fairness_payment` FLOAT DEFAULT NULL,
  PRIMARY KEY (`network_owner_id`,`game_id`),
  KEY `fk_network_owners_games_games` (`game_id`),
  CONSTRAINT `fk_network_owner_games_games` FOREIGN KEY (`game_id`) REFERENCES `games` (`id`),
  CONSTRAINT `fk_network_owners_games_network_owners` FOREIGN KEY (`network_owner_id`) REFERENCES `network_owners` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `service_providers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `service_provider_name` VARCHAR(45) NOT NULL,
  `simulation_id` INT NOT NULL,
  `benefit_factor_min` FLOAT NOT NULL,
  `benefit_factor_max` FLOAT NOT NULL,
  `xi_min` FLOAT DEFAULT NULL,
  `xi_max` FLOAT DEFAULT NULL,
  `avg_load_min` FLOAT NOT NULL,
  `avg_load_max` FLOAT NOT NULL,
  `frac_sev_at_edge_min` FLOAT DEFAULT NULL,
  `frac_sev_at_edge_max` FLOAT DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_service_providers_simulations` (`simulation_id`),
  CONSTRAINT `fk_service_providers_simulations` FOREIGN KEY (`simulation_id`) REFERENCES `simulations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `load_functions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `service_provider_id` INT NOT NULL,
  `sigma` FLOAT NOT NULL,
  `avg_load` FLOAT NOT NULL,
  `hyper_params_a_k` VARCHAR(250) NOT NULL,
  `hyper_params_t_k` VARCHAR(250) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_load_functions_service_providers_idx` (`service_provider_id`),
  CONSTRAINT `fk_load_functions_service_providers_idx` FOREIGN KEY (`service_provider_id`) REFERENCES `service_providers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `load_function_values` (
  `function_id` INT NOT NULL,
  `time` FLOAT NOT NULL,
  `load_value` FLOAT NOT NULL,
  KEY `fk_service_provider_load_function_load_function_idx` (`function_id`),
  CONSTRAINT `fk_load_function_values_load_functions` FOREIGN KEY (`function_id`) REFERENCES `load_functions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `service_providers_games` (
  `service_provider_id` INT NOT NULL,
  `game_id` INT NOT NULL,
  `load_function_id` INT NOT NULL,
  `benefit_factor` DOUBLE NOT NULL,
  `xi` DOUBLE NOT NULL,
  `allocation` FLOAT NOT NULL,
  `utilities` FLOAT NOT NULL,
  `shapley_value` FLOAT NOT NULL,
  `revenues` FLOAT NOT NULL,
  `alloc_payment` FLOAT DEFAULT NULL,
  `frac_of_req` FLOAT DEFAULT NULL,
  `fairness_payment` FLOAT DEFAULT NULL,
  PRIMARY KEY (`service_provider_id`,`game_id`),
  KEY `fk_service_providers_games_games` (`game_id`),
  KEY `fk_service_providers_games_load_function_idx` (`load_function_id`),
  CONSTRAINT `fk_service_providers_games_game_id` FOREIGN KEY (`game_id`) REFERENCES `games` (`id`),
  CONSTRAINT `fk_service_providers_games_service_provider_id` FOREIGN KEY (`service_provider_id`) REFERENCES `service_providers` (`id`),
  CONSTRAINT `fk_service_providers_games_load_function_id` FOREIGN KEY (`load_function_id`) REFERENCES `load_functions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `utility_function_values` (
  `player_id` INT NOT NULL,
  `game_id` INT NOT NULL,
  `time` FLOAT NOT NULL,
  `value` FLOAT NOT NULL,
  KEY `fk_utility_function_values_service_provider_id_idx` (`player_id`),
  KEY `fk_utility_funct_values_serv_prov_games_idx` (`game_id`),
  CONSTRAINT `fk_utility_funct_values_serv_prov` FOREIGN KEY (`player_id`) REFERENCES `service_providers_games` (`service_provider_id`),
  CONSTRAINT `fk_utility_funct_values_serv_prov_games` FOREIGN KEY (`game_id`) REFERENCES `service_providers_games` (`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
