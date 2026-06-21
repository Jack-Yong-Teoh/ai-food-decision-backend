import logging
from functools import wraps


def suppress_logs(name_startswith: str | None = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            target_loggers = []

            # pylint: disable-next=no-member
            for name, logger in logging.root.manager.loggerDict.items():
                if not isinstance(logger, logging.Logger):
                    continue  # Skip PlaceHolder objects

                if name_startswith is None or name.startswith(name_startswith):
                    target_loggers.append(logger)

            if name_startswith is None:
                target_loggers.append(logging.getLogger())

            # Remove duplicates
            target_loggers = list(set(target_loggers))

            original_states = {
                logger: (logger.level, logger.handlers[:], logger.propagate)
                for logger in target_loggers
            }

            for logger in target_loggers:
                logger.setLevel(logging.ERROR)
                logger.handlers = []
                logger.propagate = False

            try:
                return func(*args, **kwargs)
            finally:
                for logger, (level, handlers, propagate) in original_states.items():
                    logger.setLevel(level)
                    logger.handlers = handlers
                    logger.propagate = propagate

        return wrapper

    return decorator
