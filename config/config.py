
# Three levels defined in this code:
# DEBUG: algorithms, games and simulation times. Resources usage. Results checking. time-slot allocation and un used allocation
# INFO: Intermediate and final results
# ERROR: Only errors that invalidate the simulation results
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
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
    'create': False,
    'truncate': False,
    'drop': False

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

    # Independent contribution
    'additive_deterministic': False,
    # Non-independent contribution
    'non_additive_estimation': False,
    'non_additive_deterministic': True,

}

# It shouldn't be used with independent contribution ("estimation" or "additive")  : True, but it is possible
EXTRA_CONSIDERATIONS = {
    'variable_cpu_price': False,
    'per_time_slot_allocation': True
}

# This is the amount of samples for each service provider to calculate the shapley value
# Will only be considered non_additive_estimation is True
MONTE_CARLO_VARIABLES = {
    'num_samples': 10
}

# We use trust-constr as an optimization method for dynamic allocation
# These parameter are the one being used in the optimization_controller
TRUST_CONSTR_PARAMETERS = {
    'gtol': 1e-9,
    'xtol': 1e-6,
    'barrier_tol': 1e-6,
    'maxiter': 1000
}
