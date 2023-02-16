import os


logger_config = {
    'version': 1,
    'formatters': {
        'logger_formatter': {
            'format': '{asctime} - {levelname} - {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{'
        }
    },
    'handlers': {
        'logger_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'logger_formatter',
            'filename': os.path.join(os.getcwd(), 'log_varta.log'),
        }
    },
    'loggers': {
        'logger': {
            'level': 'DEBUG',
            'handlers': ['logger_handler']
        }
    }
}

