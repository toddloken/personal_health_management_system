import logging
import sys
from datetime import datetime
import os


class LoggingConfig:
    """
    Centralized logging configuration for the machine learning pipeline.
    Supports logging to file, console, or both.
    """

    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level
        self.logger = None
        self.log_filename = None

    def setup_logging(self, mode='both', log_dir='logs', log_filename=None):
        """
        Setup logging configuration.

        :param mode: 'file', 'console', or 'both'
        :param log_dir: Directory to store log files
        :param log_filename: Custom log filename (optional)
        """
        # Create logs directory if it doesn't exist
        if mode in ['file', 'both'] and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Generate log filename if not provided
        if log_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"ml_pipeline_{timestamp}.log"

        self.log_filename = os.path.join(log_dir, log_filename)

        # Create logger
        self.logger = logging.getLogger('MLPipeline')
        self.logger.setLevel(self.log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Setup handlers based on mode
        if mode in ['console', 'both']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if mode in ['file', 'both']:
            file_handler = logging.FileHandler(self.log_filename)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Log initial setup message
        self.logger.info(f"Logging initialized - Mode: {mode}, Level: {logging.getLevelName(self.log_level)}")
        if mode in ['file', 'both']:
            self.logger.info(f"Log file: {self.log_filename}")

        return self.logger

    def get_logger(self):
        """Return the configured logger instance."""
        if self.logger is None:
            raise RuntimeError("Logger not initialized. Call setup_logging() first.")
        return self.logger

    @staticmethod
    def get_class_logger(class_name):
        """
        Get a logger for a specific class.

        :param class_name: Name of the class requesting the logger
        :return: Logger instance
        """
        return logging.getLogger(f'MLPipeline.{class_name}')