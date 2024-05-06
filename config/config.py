
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
    'database': 'edge-computing',
}

# Set of scripts to keep database structure within the code
# If one is True, corresponding script is executed and no games are processed
# Only one can be True, all of them should be False to process games
DATABASE_MANAGEMENT_CONFIG = {
    'drop': False,
    'truncate': False,
    'create': False,
}
# Save the utility and load for each service provider in the database
# Any combination is possible
SAVE_FUNCTION = {
    'utility': True,
    'load': True
}

# TODO MOVE all the following TO yaml file ?
# This defines how the model is going to be computed
# Only one can be True
VALUE_FUNCTION_MODE = {
    'additive': False,
    'non_additive_deterministic': True,
    'non_additive_estimation': False
}

# It shouldn't be used with 'additive': True, but it is possible
EXTRA_CONSIDERATIONS = {
    'variable_cpu_price': False,
    'per_time_slot_allocation': False
}

# It shouldn't be used with 'additive': True, but it is possible
EXTRA_FUNCTIONALITIES = {
    # "'calibrate_params': False,
    "check_for_cheat": False
}

# This is the amount of samples for each service provider to calculate the shapley value
MONTE_CARLO_VARIABLES = {
    'num_samples': 10
}
