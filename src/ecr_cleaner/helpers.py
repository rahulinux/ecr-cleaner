import logging
import structlog


def config_logger(log_level: str):
    LOG_LEVEL = getattr(logging, log_level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL),
    )


def get_logger():
    return structlog.get_logger(__name__)
