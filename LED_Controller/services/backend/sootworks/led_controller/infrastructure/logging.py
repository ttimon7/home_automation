import logging
import logging.handlers

from sootworks.led_controller.app_config import configuration

logging_configured = False


def set_up_logging() -> None:
    global logging_configured  # noqa: PLW0603

    if not logging_configured:
        level = configuration.log.log_level.name
        logging.basicConfig(level=level, format=configuration.log.format)
        root_logger = logging.getLogger()

        # Log to file
        formatter = logging.Formatter(configuration.log.format)
        if configuration.log.file_path is not None:
            file_handler = logging.handlers.RotatingFileHandler(
                configuration.log.file_path,
                maxBytes=configuration.log.size_limit_in_bytes,
                backupCount=configuration.log.backup_count,
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        logging_configured = True
