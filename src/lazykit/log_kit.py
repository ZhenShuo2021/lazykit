from __future__ import annotations

import logging
import os
from typing import ClassVar

from .tool_kit import _check_module_installed

try:
    # from: fabiocaccamo/python-fsutil
    from colorama import Fore, Style, init

    requests_installed = True
except ImportError:
    requests_installed = False


class LogFormatter(logging.Formatter):
    COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: Fore.LIGHTBLACK_EX,
        logging.INFO: Fore.WHITE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }
    GREEN = Fore.GREEN
    RESET = Style.RESET_ALL

    def __init__(
        self, datefmt: str = '%H:%M:%S', use_color: bool = True, lower: bool = False
    ) -> None:
        super().__init__()
        if use_color:
            _check_module_installed('colorama')
            init()
        self.use_color = use_color
        self.datefmt = datefmt
        self.setup_levelname(lower)
        self._format_record = self._format_color if use_color else self._format_plain

    def setup_levelname(self, lower: bool) -> None:
        key = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
        self.level_map = {k: k.lower() if lower else k for k in key}

    def format(self, record: logging.LogRecord) -> str:
        return self._format_record(record)

    def _format_color(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        levelname = self.level_map[record.levelname]
        return f'[{self.GREEN}{self.formatTime(record, self.datefmt)}{self.RESET}][{color}{levelname}{self.RESET}] {record.getMessage()}'

    def _format_plain(self, record: logging.LogRecord) -> str:
        levelname = self.level_map[record.levelname]
        return f'[{self.formatTime(record, self.datefmt)}][{levelname}] {record.getMessage()}'


class LoggingUtility:
    """用來設置日誌的工具類，支援自定義處理器和過濾設置"""

    @staticmethod
    def setup_logging(
        level: int,
        log_path: str | None = None,
        logger_name: str | None = None,
        *,
        enable_file_logging: bool = True,
        use_color: bool = True,
        suppress_libs: dict[str, int] | None = None,
        handlers: list[logging.Handler] | None = None,
        formatter: logging.Formatter | None = None,
        clear_handlers: bool = True,
    ) -> logging.Logger:
        """簡單的建立記錄器的方法

        如果提供了 formatter，則 console_formatter 和 file_formatter 會同時套用該格式器。

        Args:
            level (int): 日誌等級。
            log_path (str | None): 日誌檔案路徑。
            logger_name (str | None): 記錄器名稱。
            enable_file_logging (bool): 是否啟用檔案日誌。
            use_color (bool): 是否使用彩色輸出。
            suppress_libs (dict[str, int] | None): 要抑制日誌的庫。
            handlers (list[logging.Handler] | None): 自定義處理器。
            formatter (logging.Formatter | None): 自定義格式器。
            clear_handlers (bool): 是否清除現有處理器。

        Returns:
            logging.Logger: Configured logger.

        Usage Examples:

            1. 基礎使用:
            lazykit.setup_logging()

            2. 客製化 formatter 和 handler:

            my_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            my_handler = logging.StreamHandler()
            my_handler.setFormatter(my_formatter)
            setup_logging(handlers=[my_handler], formatter=my_formatter)

            3. 支援抑制指定模組的 logger，例如 httpx 很吵:
            be_quiet={'httpx': logging.WARNING, 'httpcore': logging.WARNING}
            setup_logging(suppress_libs=be_quiet)
        """
        logger = logging.getLogger(logger_name)

        if clear_handlers:
            LoggingUtility.clear_handlers(logger)

        # Default formatter setup
        if not formatter:
            console_formatter = LoggingUtility.default_formatter(use_color)
            file_formatter = LoggingUtility.default_formatter(False)
        else:
            console_formatter = file_formatter = formatter

        # Add user-defined handlers if provided
        if handlers:
            for handler in handlers:
                handler.setFormatter(console_formatter)
                logger.addHandler(handler)
        else:
            # Add default handlers
            logger.addHandler(LoggingUtility.create_console_handler(level, console_formatter))
            if enable_file_logging and log_path:
                logger.addHandler(
                    LoggingUtility.create_file_handler(level, file_formatter, log_path)
                )

        # Set logger level
        logger.setLevel(level)

        # Suppress logs from specified libraries
        if suppress_libs:
            LoggingUtility.suppress_library_logs(suppress_libs)

        return logger

    @staticmethod
    def default_formatter(use_color: bool) -> logging.Formatter:
        """返回預設格式化程式，並可選擇性地支持顏色"""
        if use_color:
            return LogFormatter()
        else:
            return LogFormatter(use_color=False)

    @staticmethod
    def clear_handlers(logger: logging.Logger) -> None:
        """從 logger 移除所有 handlers"""
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    @staticmethod
    def create_console_handler(level: int, formatter: logging.Formatter) -> logging.Handler:
        """建立並且基本設定終端機 handler"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        return console_handler

    @staticmethod
    def create_file_handler(
        level: int, formatter: logging.Formatter | None, log_path: str
    ) -> logging.Handler:
        """建立並且基本設定檔案 handler，使用無顏色的 formatter"""
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_formatter = formatter or LoggingUtility.default_formatter(False)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        return file_handler

    @staticmethod
    def suppress_library_logs(suppressed_libraries: dict[str, int]) -> None:
        """設定指定函式庫的日誌等級"""
        for lib, level in suppressed_libraries.items():
            logging.getLogger(lib).setLevel(level)
