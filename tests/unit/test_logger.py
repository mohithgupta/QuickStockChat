"""
Unit tests for logger.py

Tests cover logger creation, configuration, file/console handlers,
log levels, and output verification.
"""

import pytest
import logging
import re
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from MarketInsight.utils.logger import get_logger, LOG_DIR, LOG_FILE


class TestLoggerCreation:
    """Test suite for logger creation and initialization"""

    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a valid Logger instance"""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_default_name(self):
        """Test get_logger with default name parameter"""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "__main__"

    def test_get_logger_with_custom_name(self):
        """Test get_logger with custom name"""
        logger = get_logger("custom_logger")
        assert logger.name == "custom_logger"

    def test_get_logger_same_name_returns_same_instance(self):
        """Test that calling get_logger with same name returns same logger instance"""
        logger1 = get_logger("duplicate_test")
        logger2 = get_logger("duplicate_test")
        assert logger1 is logger2

    def test_get_logger_different_names_returns_different_instances(self):
        """Test that calling get_logger with different names returns different instances"""
        logger1 = get_logger("logger_one")
        logger2 = get_logger("logger_two")
        assert logger1 is not logger2
        assert logger1.name == "logger_one"
        assert logger2.name == "logger_two"

    def test_logger_level_is_debug(self):
        """Test that logger is set to DEBUG level"""
        logger = get_logger("level_test")
        assert logger.level == logging.DEBUG


class TestLoggerConfiguration:
    """Test suite for logger configuration and handlers"""

    def test_root_logger_has_handlers(self):
        """Test that root logger gets configured with handlers"""
        # Reset logging configuration
        logging.getLogger().handlers.clear()
        import importlib
        import MarketInsight.utils.logger
        importlib.reload(MarketInsight.utils.logger)

        logger = get_logger("config_test")
        root_logger = logging.getLogger()

        assert len(root_logger.handlers) > 0

    def test_logger_has_file_handler(self):
        """Test that logger includes a file handler"""
        logger = get_logger("file_handler_test")
        root_logger = logging.getLogger()

        # Check if any handler is a FileHandler
        has_file_handler = any(
            isinstance(h, logging.FileHandler) for h in root_logger.handlers
        )
        assert has_file_handler

    def test_logger_has_stream_handler(self):
        """Test that logger includes a stream (console) handler"""
        logger = get_logger("stream_handler_test")
        root_logger = logging.getLogger()

        # Check if any handler is a StreamHandler
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler) for h in root_logger.handlers
        )
        assert has_stream_handler

    def test_file_handler_log_level(self):
        """Test that file handler is set to DEBUG level"""
        logger = get_logger("file_level_test")
        root_logger = logging.getLogger()

        file_handler = next(
            (h for h in root_logger.handlers if isinstance(h, logging.FileHandler)),
            None
        )
        assert file_handler is not None
        assert file_handler.level == logging.DEBUG

    def test_console_handler_log_level(self):
        """Test that console handler is set to WARNING level"""
        logger = get_logger("console_level_test")
        root_logger = logging.getLogger()

        console_handler = next(
            (h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)),
            None
        )
        assert console_handler is not None
        assert console_handler.level == logging.WARNING


class TestLogFormatter:
    """Test suite for log message formatting"""

    def test_formatter_exists(self):
        """Test that handlers have formatters attached"""
        logger = get_logger("formatter_test")
        root_logger = logging.getLogger()

        for handler in root_logger.handlers:
            assert handler.formatter is not None

    def test_formatter_format_string(self):
        """Test that formatter has correct format string"""
        logger = get_logger("format_test")
        root_logger = logging.getLogger()

        # Get the formatter from any handler
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        # Check that format contains expected elements
        format_str = formatter._fmt
        assert "%(asctime)s" in format_str
        assert "%(name)s" in format_str
        assert "%(levelname)s" in format_str
        assert "%(lineno)d" in format_str
        assert "%(message)s" in format_str

    def test_formatter_date_format(self):
        """Test that formatter has correct date format"""
        logger = get_logger("date_format_test")
        root_logger = logging.getLogger()

        handler = root_logger.handlers[0]
        formatter = handler.formatter

        # Check date format
        date_format = formatter.datefmt
        assert date_format == "%Y-%m-%d %H:%M:%S"


class TestLogFileCreation:
    """Test suite for log file and directory creation"""

    def test_log_dir_exists(self):
        """Test that log directory exists"""
        assert LOG_DIR.exists()
        assert LOG_DIR.is_dir()

    def test_log_dir_has_current_date(self):
        """Test that log directory includes current date"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        assert current_date in str(LOG_DIR)

    def test_log_file_path_exists(self):
        """Test that LOG_FILE path is defined"""
        assert LOG_FILE is not None
        assert isinstance(LOG_FILE, Path)

    def test_log_file_has_timestamp(self):
        """Test that log file includes timestamp in filename"""
        # The log file should match pattern: YYYY-MM-DD_HH-MM-SS.log
        filename = LOG_FILE.name
        pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.log"
        assert re.match(pattern, filename)

    def test_log_file_extension(self):
        """Test that log file has .log extension"""
        assert LOG_FILE.suffix == ".log"


class TestLoggingOutput:
    """Test suite for logging output to file"""

    def setup_method(self):
        """Setup method to create a temporary log directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_log_file = LOG_FILE

    def teardown_method(self):
        """Cleanup method to remove temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_logger_can_log_debug_message(self):
        """Test that logger can log DEBUG level messages"""
        logger = get_logger("debug_test")

        # This should not raise an exception
        logger.debug("This is a debug message")

    def test_logger_can_log_info_message(self):
        """Test that logger can log INFO level messages"""
        logger = get_logger("info_test")

        # This should not raise an exception
        logger.info("This is an info message")

    def test_logger_can_log_warning_message(self):
        """Test that logger can log WARNING level messages"""
        logger = get_logger("warning_test")

        # This should not raise an exception
        logger.warning("This is a warning message")

    def test_logger_can_log_error_message(self):
        """Test that logger can log ERROR level messages"""
        logger = get_logger("error_test")

        # This should not raise an exception
        logger.error("This is an error message")

    def test_logger_can_log_critical_message(self):
        """Test that logger can log CRITICAL level messages"""
        logger = get_logger("critical_test")

        # This should not raise an exception
        logger.critical("This is a critical message")

    def test_logger_handles_special_characters(self):
        """Test that logger handles special characters in messages"""
        logger = get_logger("special_chars_test")

        # Should not raise exceptions
        logger.info("Message with special chars: @#$%^&*()[]{}")
        logger.info("Message with quotes: 'single' and \"double\"")
        logger.info("Message with unicode: ñ, é, 中文")

    def test_logger_handles_long_messages(self):
        """Test that logger handles long messages"""
        logger = get_logger("long_message_test")

        long_message = "x" * 10000  # 10k character message
        logger.info(long_message)

    def test_logger_handles_empty_message(self):
        """Test that logger handles empty messages"""
        logger = get_logger("empty_message_test")

        logger.info("")

    def test_logger_handles_multiline_message(self):
        """Test that logger handles multiline messages"""
        logger = get_logger("multiline_test")

        multiline_msg = """Line 1
Line 2
Line 3"""
        logger.info(multiline_msg)


class TestLoggerBehavior:
    """Test suite for logger behavior and edge cases"""

    def test_multiple_loggers_share_configuration(self):
        """Test that multiple loggers share the same root configuration"""
        logger1 = get_logger("behavior_test1")
        logger2 = get_logger("behavior_test2")

        root_logger = logging.getLogger()

        # Both loggers should propagate to root
        assert logger1.propagate is True
        assert logger2.propagate is True

    def test_logger_configuration_happens_once(self):
        """Test that logging configuration only happens once"""
        # Import the module-level flag
        from MarketInsight.utils import logger

        # Get configuration status before
        initial_configured = logger._LOGGING_CONFIGURED

        # Call get_logger multiple times
        get_logger("once_test1")
        get_logger("once_test2")
        get_logger("once_test3")

        # Configuration should still be True (or set to True after first call)
        assert logger._LOGGING_CONFIGURED is True

    def test_logger_with_different_names(self):
        """Test creating loggers with various name formats"""
        # Test with simple name
        logger1 = get_logger("simple")
        assert logger1.name == "simple"

        # Test with dotted name (module-style)
        logger2 = get_logger("package.module.submodule")
        assert logger2.name == "package.module.submodule"

        # Test with underscores
        logger3 = get_logger("my_test_logger")
        assert logger3.name == "my_test_logger"

    def test_logger_handles_exception_logging(self):
        """Test that logger can log exceptions"""
        logger = get_logger("exception_test")

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            # Should not raise an exception
            logger.exception("An exception occurred")


class TestLoggerThreadSafety:
    """Test suite for logger thread safety considerations"""

    def test_concurrent_logger_access(self):
        """Test that multiple loggers can be created concurrently"""
        import threading

        loggers = []
        errors = []

        def create_logger(name):
            try:
                logger = get_logger(f"thread_test_{name}")
                loggers.append(logger)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=create_logger, args=(i,))
            for i in range(10)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors
        assert len(errors) == 0
        assert len(loggers) == 10


class TestLoggerEdgeCases:
    """Test suite for logger edge cases"""

    def test_logger_name_with_special_characters(self):
        """Test logger names with special characters"""
        # These should still work
        logger1 = get_logger("test.logger-123")
        assert logger1.name == "test.logger-123"

    def test_logger_name_with_unicode(self):
        """Test logger names with unicode characters"""
        logger = get_logger("test_ログ")
        assert logger.name == "test_ログ"

    def test_get_logger_callable_without_arguments(self):
        """Test that get_logger can be called without arguments"""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)

    def test_logger_exception_with_extra_info(self):
        """Test logging exception with extra parameter"""
        logger = get_logger("extra_test")

        try:
            raise ValueError("Test")
        except ValueError:
            # Should not raise an exception even with extra dict
            logger.exception("Error occurred", extra={"key": "value"})
