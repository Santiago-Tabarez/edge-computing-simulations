
# Three levels defined in this code:
# DEBUG: algorithms, games and simulation times. Resources usage. Results checking. time-slot allocation and un used allocation
# INFO: Intermediate and final results
# ERROR: Only errors that invalidate the simulation results
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

DATABASE_CONNECTION_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'admin',
    'password': 'admin',
    'database': 'edge_computing',
}

# Set of scripts to keep database structure within the code
# If one is True, corresponding script is executed and no games are processed
# Only one at a time can be True, all of them should be False to process games
DATABASE_MANAGEMENT_CONFIG = {
    'drop': False,
    'truncate': False,
    'create': True,
}

# Save the utility and load for each service provider in the database
# Any combination is possible
SAVE_FUNCTION = {
    'utility': True,
    'load': True
}

# This defines how the model is going to be computed
# Only one can be True
VALUE_FUNCTION_MODE = {
    'additive': True,
    'non_additive_deterministic': False,
    'non_additive_estimation': False
}

# It shouldn't be used with 'additive': True, but it is possible
EXTRA_CONSIDERATIONS = {
    'variable_cpu_price': False,
    'per_time_slot_allocation': False
}

# This is the amount of samples for each service provider to calculate the shapley value
# Will only be considered non_additive_estimation is True
MONTE_CARLO_VARIABLES = {
    'num_samples': 10
}


# It shouldn't be used with 'additive': True, but it is possible
EXTRA_FUNCTIONALITIES = {
    # "'calibrate_params': False,
    "check_for_cheat": True
}
