import datetime
import logging
import os

from pygelf import GelfTcpHandler, GelfUdpHandler
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            # This doesn't use record.created, so it is slightly off
            now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


class ContextFilter(logging.Filter):
    def __init__(self, context_vars):
        """
        :param context_vars: the extra properties to add to the LogRecord
        :type context_vars: list[tuple[str, str]]
        """
        super().__init__()
        self.context_vars = context_vars

    def filter(self, record):
        for key, value in self.context_vars:
            setattr(record, key, value)
        return True


def logger(
    level,
    json_logging=True,
    graylog_host=None,
    graylog_port=None,
    graylog_adapter=None,
    log_shipping_level=None,
    log_shipping_env_var_prefix=None,
):
    # Exceptions
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.ERROR)
    # Exceptions
    if json_logging:
        log_handler = logging.StreamHandler()
        log_handler.setLevel(level)
        formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
        log_handler.setFormatter(formatter)
        logging.basicConfig(handlers=[log_handler], level=level, force=True)
    else:
        logging.basicConfig(level=level)

    if graylog_host is not None:
        if graylog_adapter == "tcp":
            shipping_handler = GelfTcpHandler(
                host=graylog_host, port=graylog_port, include_extra_fields=True
            )
        else:
            shipping_handler = GelfUdpHandler(
                host=graylog_host, port=graylog_port, include_extra_fields=True
            )
        shipping_handler.setLevel(log_shipping_level)

        if log_shipping_env_var_prefix is not None:
            filtered_env = [
                (k.removeprefix(log_shipping_env_var_prefix), v)
                for k, v in os.environ.items()
                if k.startswith(log_shipping_env_var_prefix)
            ]
            shipping_filter = ContextFilter(filtered_env)
            shipping_handler.addFilter(shipping_filter)

        logging.getLogger().addHandler(shipping_handler)

    class AppLogger:
        def __init__(self, name):
            self.local_logger = logging.getLogger(name)

        @staticmethod
        def prepare_meta(meta=None):
            return None if meta is None else {"attributes": meta}

        @staticmethod
        def setup_logger_level(lib, log_level):
            logging.getLogger(lib).setLevel(log_level)

        def debug(self, message, meta=None):
            self.local_logger.debug(message, extra=AppLogger.prepare_meta(meta))

        def info(self, message, meta=None):
            self.local_logger.info(message, extra=AppLogger.prepare_meta(meta))

        def warning(self, message, meta=None):
            self.local_logger.warning(message, extra=AppLogger.prepare_meta(meta))

        def error(self, message, meta=None):
            # noinspection PyTypeChecker
            self.local_logger.error(
                message, exc_info=1, extra=AppLogger.prepare_meta(meta)
            )

    return AppLogger
