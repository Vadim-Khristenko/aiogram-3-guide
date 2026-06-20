import logging
from json import dumps

import structlog
from structlog import WriteLoggerFactory

from bot.config_reader import LogConfig, LogRenderer


def get_structlog_config(
    log_config: LogConfig
) -> dict:
    """
    Getting structlog configuration
    :param log_config: LogConfig object with logging parameters
    :return: dictionary with structlog configuration
    """

    # Show or not debug level logs
    if log_config.show_debug_logs is True:
        min_level = logging.DEBUG
    else:
        min_level = logging.INFO

    return {
        "processors": get_processors(log_config),
        "cache_logger_on_first_use": True,
        "wrapper_class": structlog.make_filtering_bound_logger(min_level),
        "logger_factory": WriteLoggerFactory()
    }


def get_processors(log_config: LogConfig) -> list:
    """
    Returns a list of processors for structlog
    :param log_config: LogConfig object with logging parameters
    :return: list of processors for structlog
    """
    def custom_json_serializer(data, *args, **kwargs):
        """
        Custom serializer for JSON logs
        """
        result = dict()


        if log_config.show_datetime is True:
            result["timestamp"] = data.pop("timestamp")

        # All the following two keys go in exactly this order
        for key in ("level", "event"):
            if key in data:
                result[key] = data.pop(key)

        # All other keys are printed "as is"
        # (usually in alphabetical order)
        result.update(**data)
        return dumps(result, default=str)

    processors = list()

    # In some cases, you don't need to output a timestamp,
    # since it is already added by a higher-level service, for example, systemd
    if log_config.show_datetime is True:
        processors.append(structlog.processors.TimeStamper(
            fmt=log_config.datetime_format,
            utc=log_config.time_in_utc
            )
        )

    # Always add the log level
    processors.append(structlog.processors.add_log_level)

    # Choose render: JSON or for output to terminal
    if log_config.renderer == LogRenderer.JSON:
        processors.append(structlog.processors.JSONRenderer(serializer=custom_json_serializer))
    else:
        processors.append(structlog.dev.ConsoleRenderer(
            # Can disable colors in logs
            colors=log_config.use_colors_in_console,
            # Can remove padding in levels, i.e. instead of
            # [info   ] Some info log
            # [warning] Some warning log
            # will be
            # [info] Some info log
            # [warning] Some warning log
            pad_level=True
        ))
    return processors
