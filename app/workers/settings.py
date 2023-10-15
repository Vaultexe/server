from app.core.config import settings

REDIS_URL = str(settings.REDIS_URI)

# You can also specify the Redis DB to use
# REDIS_HOST = 'redis.example.com'
# REDIS_PORT = 6380
# REDIS_DB = 3
# REDIS_PASSWORD = 'very secret'

# Queues to listen on
QUEUES = ["high", "default", "low"]

# TODO: connect to sentry
# If you're using Sentry to collect your runtime exceptions, you can use this
# to configure RQ for it in a single step
# The 'sync+' prefix is required for raven: https://github.com/nvie/rq/issues/350#issuecomment-43592410
# SENTRY_DSN = 'sync+http://public:secret@example.com/1'

# If you want custom worker name
# NAME = 'worker-1024'

# If you want to use a dictConfig <https://docs.python.org/3/library/logging.config.html#logging-config-dictschema>
# for more complex/consistent logging requirements.
DICT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",  # Default is stderr
        },
    },
    "loggers": {
        "root": {"handlers": ["default"], "level": "INFO", "propagate": False},  # root logger
    },
}
