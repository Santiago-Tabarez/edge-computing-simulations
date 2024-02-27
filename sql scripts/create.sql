CREATE TABLE `simulations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `simulation_name` varchar(45) NOT NULL,
  `max_cores_hosted_min` int NOT NULL,
  `max_cores_hosted_max` int NOT NULL,
  `cpu_price_min` float NOT NULL,
  `cpu_price_max` float NOT NULL,
  `years_min` float NOT NULL,
  `years_max` float NOT NULL,
  `daily_timeslots_min` int NOT NULL,
  `daily_timeslots_max` int NOT NULL,
  `amount_of_players` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `simulation_name_UNIQUE` (`simulation_name`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `games` (
  `id` int NOT NULL AUTO_INCREMENT,
  `simulation_id` int NOT NULL,
  `max_cores_hosted` int NOT NULL,
  `cpu_price` float NOT NULL,
  `years` float NOT NULL,
  `daily_timeslots` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_sim_id_idx` (`simulation_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='	';

CREATE TABLE `load_functions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `service_provider_id` int NOT NULL,
  `sigma` float NOT NULL,
  `avg_load` float NOT NULL,
  `hyper_params_a_k` varchar(250) NOT NULL,
  `hyper_params_t_k` varchar(250) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_load_functions_service_providers_idx` (`service_provider_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `network_owners` (
  `id` int NOT NULL AUTO_INCREMENT,
  `network_owner_name` varchar(45) NOT NULL,
  `simulation_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_network_owners_simulations` (`simulation_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `network_owners_games` (
  `network_owner_id` int NOT NULL,
  `game_id` int NOT NULL,
  `shapley_value` float NOT NULL,
  `revenues` float NOT NULL,
  `payments` float DEFAULT NULL,
  PRIMARY KEY (`network_owner_id`,`game_id`),
  KEY `fk_network_owners_games_games` (`game_id`),
  CONSTRAINT `fk_network_owner_games_games` FOREIGN KEY (`game_id`) REFERENCES `games` (`id`),
  CONSTRAINT `fk_network_owners_games_network_owners` FOREIGN KEY (`network_owner_id`) REFERENCES `network_owners` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `service_providers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `service_provider_name` varchar(45) NOT NULL,
  `simulation_id` int NOT NULL,
  `benefit_factor_min` float NOT NULL,
  `benefit_factor_max` float NOT NULL,
  `xi_min` float NOT NULL,
  `xi_max` float NOT NULL,
  `avg_load_min` float NOT NULL,
  `avg_load_max` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_service_providers_simulations` (`simulation_id`),
  CONSTRAINT `fk_service_providers_simulations` FOREIGN KEY (`simulation_id`) REFERENCES `simulations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `service_providers_games` (
  `service_provider_id` int NOT NULL,
  `game_id` int NOT NULL,
  `load_function_id` int NOT NULL,
  `benefit_factor` float NOT NULL,
  `xi` float NOT NULL,
  `allocation` float NOT NULL,
  `utilities` float NOT NULL,
  `shapley_value` float NOT NULL,
  `revenues` float NOT NULL,
  `payments` float DEFAULT NULL,
  PRIMARY KEY (`service_provider_id`,`game_id`),
  KEY `fk_service_providers_games_games` (`game_id`),
  KEY `fk_service_providers_games_load_function_idx` (`load_function_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `load_function_values` (
  `function_id` int NOT NULL,
  `time` float NOT NULL,
  `load_value` float NOT NULL,
  KEY `fk_service_provider_load_function_load_function_idx` (`function_id`),
  CONSTRAINT `fk_load_function_values_load_functions` FOREIGN KEY (`function_id`) REFERENCES `load_functions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
