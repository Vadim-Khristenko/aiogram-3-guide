import logging
from json import dumps

import structlog
from structlog import WriteLoggerFactory

from bot.config_reader import LogConfig, LogRenderer


def get_structlog_config(
    log_config: LogConfig
) -> dict:
    """
    获取 structlog 配置
    :param log_config: LogConfig 对象，包含日志参数
    :return: 包含 structlog 配置的字典
    """

    # 显示或隐藏调试级别的日志
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
    返回 structlog 的处理器列表
    :param log_config: LogConfig 对象，包含日志参数
    :return: structlog 的处理器列表
    """
    def custom_json_serializer(data, *args, **kwargs):
        """
        JSON 日志的自定义序列化程序
        """
        result = dict()


        if log_config.show_datetime is True:
            result["timestamp"] = data.pop("timestamp")

        # 以下两个键必须按照这个顺序排列
        for key in ("level", "event"):
            if key in data:
                result[key] = data.pop(key)

        # 所有其他键按原样打印
        # （通常按字母顺序）
        result.update(**data)
        return dumps(result, default=str)

    processors = list()

    # 在某些情况下，您不需要输出时间戳，
    # 因为它已经由更高级别的服务添加了，例如 systemd
    if log_config.show_datetime is True:
        processors.append(structlog.processors.TimeStamper(
            fmt=log_config.datetime_format,
            utc=log_config.time_in_utc
            )
        )

    # 始终添加日志级别
    processors.append(structlog.processors.add_log_level)

    # 选择渲染方式：JSON 或终端输出
    if log_config.renderer == LogRenderer.JSON:
        processors.append(structlog.processors.JSONRenderer(serializer=custom_json_serializer))
    else:
        processors.append(structlog.dev.ConsoleRenderer(
            # 可以禁用日志中的颜色
            colors=log_config.use_colors_in_console,
            # 可以移除级别的填充，即代替
            # [info   ] Some info log
            # [warning] Some warning log
            # 将是
            # [info] Some info log
            # [warning] Some warning log
            pad_level=True
        ))
    return processors
