from .project import *  # noqa

# Set debug to True for development
DEBUG = True
TEMPLATE_DEBUG = DEBUG
LOGGING_OUTPUT_ENABLED = DEBUG
LOGGING_LOG_SQL = DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# LocMemCache resets on every process restart so there is no stale-state risk
# in development. It also lets sorl-thumbnail cache thumbnail lookups in memory
# (sorl always uses the 'default' cache alias; DummyCache broke this).
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default',
    },
}

# Make sure static files storage is set to default
STATIC_FILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # define output formats
        'verbose': {
            'format': (
                '%(levelname)s %(name)s %(asctime)s %(module)s %(process)d '
                '%(thread)d %(message)s')
        },
        'simple': {
            'format': (
                '%(name)s %(levelname)s %(filename)s L%(lineno)s: '
                '%(message)s')
        },
    },
    'handlers': {
        # console output
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # switch to DEBUG to log every SQL query with duration
        },
        'changes.profiling': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    # root logger
    # non handled logs will propagate to the root logger
    'root': {
        'handlers': ['console'],
        'level': 'WARNING'
    }
}

# set up devserver if installed
try:
    # noinspection PyUnresolvedReferences
    import devserver  # noqa
    INSTALLED_APPS += [
        'devserver',
    ]
    # more details at https://github.com/dcramer/django-devserver#configuration
    DEVSERVER_DEFAULT_ADDR = '0.0.0.0'
    DEVSERVER_DEFAULT_PORT = '8000'
    DEVSERVER_AUTO_PROFILE = False  # use decorated functions
    DEVSERVER_TRUNCATE_SQL = True  # squash verbose output, show from/where
    DEVSERVER_MODULES = (
        # uncomment if you want to show every SQL executed
        # 'devserver.modules.sql.SQLRealTimeModule',
        # show sql query summary
        'devserver.modules.sql.SQLSummaryModule',
        # Total time to render a request
        'devserver.modules.profile.ProfileSummaryModule',

        # Modules not enabled by default
        # 'devserver.modules.ajax.AjaxDumpModule',
        # 'devserver.modules.profile.MemoryUseModule',
        # 'devserver.modules.cache.CacheSummaryModule',
        # see documentation for line profile decorator examples
        # 'devserver.modules.profile.LineProfilerModule',
        # show django session information
        # 'devserver.modules.request.SessionInfoModule',
    )
except ImportError:
    pass

# Prepend timing middleware so it wraps everything (including other middleware)
MIDDLEWARE = ['core.profiling_middleware.RequestTimingMiddleware'] + MIDDLEWARE
