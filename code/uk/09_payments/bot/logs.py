import logging
from json import dumps

import structlog
from structlog import WriteLoggerFactory

from bot.config_reader import LogConfig, LogRenderer


def get_structlog_config(
    log_config: LogConfig
) -> dict:
    """
    Отримання конфігурації для structlog
    :param log_config: об'єкт LogConfig з параметрами логування
    :return: словник з конфігурацією structlog
    """

    # Показувати чи ні логи рівня debug
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
    Повертає список процесорів для structlog
    :param log_config: об'єкт LogConfig з параметрами логування
    :return: список процесорів для structlog
    """
    def custom_json_serializer(data, *args, **kwargs):
        """
        Кастомний сериалізатор для JSON-логів
        """
        result = dict()


        if log_config.show_datetime is True:
            result["timestamp"] = data.pop("timestamp")

        # Усі решта наступних два ключі йдуть саме в такому порядку
        for key in ("level", "event"):
            if key in data:
                result[key] = data.pop(key)

        # Усі решта ключів виводяться "як є"
        # (зазвичай в алфавітному порядку)
        result.update(**data)
        return dumps(result, default=str)

    processors = list()

    # У деяких випадках не потрібно виводити позначку часу,
    # оскільки вона вже додається вищестоящим сервісом, наприклад, systemd
    if log_config.show_datetime is True:
        processors.append(structlog.processors.TimeStamper(
            fmt=log_config.datetime_format,
            utc=log_config.time_in_utc
            )
        )

    # Завжди додаємо рівень логу
    processors.append(structlog.processors.add_log_level)

    # Вибір рендера: JSON або для виведення в термінал
    if log_config.renderer == LogRenderer.JSON:
        processors.append(structlog.processors.JSONRenderer(serializer=custom_json_serializer))
    else:
        processors.append(structlog.dev.ConsoleRenderer(
            # Можна вимкнути кольори в логах
            colors=log_config.use_colors_in_console,
            # Можна прибрати паддінг в рівнях, тобто замість
            # [info   ] Some info log
            # [warning] Some warning log
            # буде
            # [info] Some info log
            # [warning] Some warning log
            pad_level=True
        ))
    return processors
