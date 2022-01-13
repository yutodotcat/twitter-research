import logging
from logging import Logger
from typing import Any, Dict


class _LoggerForMe:
    __DEFAULT_LOG_FILE: str = "logger.log"
    __DEFAULT_FORMAT: str = (
        '%(asctime)s - %(name)s'
        '- %(levelname)s - %(message)s'
    )
    __LOGGER_LEVEL_DICT: Dict[str, Any] = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    def __init__(
        self,
        log_file: str = __DEFAULT_LOG_FILE,
        format: str = __DEFAULT_FORMAT
    ) -> None:
        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.DEBUG)

        self.__console_handler = logging.StreamHandler()
        self.__console_handler.setFormatter(
            logging.Formatter(
                ('%(asctime)s:%(levelname)s'
                 '- %(message)s')
            )
        )

        self.__file_handler = logging.FileHandler(log_file)

    def __set_console_handler_and_file_handler(self) -> None:
        self.__logger.addHandler(self.__console_handler)
        self.__logger.addHandler(self.__file_handler)

    def create_logger_show_debug_and_save_info_or_more(
        self,
        console_handl_level: str = __LOGGER_LEVEL_DICT["debug"],
        file_handle_level: str = __LOGGER_LEVEL_DICT["info"],
    ) -> Logger:
        self.__console_handler.setLevel(console_handl_level)
        self.__file_handler.setLevel(file_handle_level)

        self.__set_console_handler_and_file_handler()

        return self.__logger


class LoggerFactory:
    @ classmethod
    def create_save_info_or_more(cls) -> Logger:
        """
        Comments:
            * create_default_logger_to_display_debug_and_save_log_info_or_more
            * and save data by logger.info or more
            * return instance of _LoggerForme
            * that displays debug by logger.debug
        """
        return _LoggerForMe().create_logger_show_debug_and_save_info_or_more()
