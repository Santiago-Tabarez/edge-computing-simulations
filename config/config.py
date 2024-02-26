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
    'database': 'edge-computing',
}

DATABASE_MANAGEMENT_CONFIG = {
    'drop': False,
    'truncate': False,
    'create': False,
}
