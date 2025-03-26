import os
import sys
import logging
import logging.config
import colorlog
from pathlib import Path

class LoggingConfig:
    """Manages logging configuration for the application."""

    @staticmethod
    def setup(config_path=None, default_level=logging.INFO):
        """
        Set up logging configuration.

        Args:
            config_path (str): Path to the logging configuration file
            default_level (int): Default logging level if config file is not found

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))), 'logs')
            os.makedirs(log_dir, exist_ok=True)

            # Remove all existing handlers
            root = logging.getLogger()
            if root.handlers:
                for handler in root.handlers:
                    root.removeHandler(handler)

            # Common format parts
            base_format = ('%(asctime)s %(process)d-%(thread)d '
                         '%(levelname)-8s %(name)s: %(message)s')
            date_format = '%Y-%m-%d %H:%M:%S'

            # Set up console handler with colors
            console_handler = colorlog.StreamHandler()
            console_handler.setFormatter(colorlog.ColoredFormatter(
                fmt=('%(log_color)s' + base_format + '%(reset)s'),
                datefmt=date_format,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
                secondary_log_colors={},
                style='%'
            ))
            console_handler.setLevel(logging.INFO)

            # Set up file handler
            file_handler = logging.FileHandler(os.path.join(log_dir, 'webauthn.log'))
            file_handler.setFormatter(logging.Formatter(
                fmt=base_format,
                datefmt=date_format
            ))
            file_handler.setLevel(logging.DEBUG)

            # Configure root logger
            root.setLevel(logging.DEBUG)
            root.addHandler(console_handler)
            root.addHandler(file_handler)

            # Test logging configuration
            root.info("Logging system initialized")
            return True

        except Exception as e:
            # Basic configuration in case of any error
            logging.basicConfig(
                level=default_level,
                format=base_format,
                datefmt=date_format
            )
            logging.error("Error setting up logging configuration: %s", str(e))
            return False

    @staticmethod
    def get_logger(name):
        """
        Get a logger instance with the specified name.

        Args:
            name (str): Name for the logger

        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(name)

    @staticmethod
    def add_file_handler(logger, filename, level=logging.DEBUG):
        """
        Add a file handler to the specified logger.

        Args:
            logger (logging.Logger): Logger instance to add handler to
            filename (str): Name of the log file
            level (int): Logging level for the file handler
        """
        log_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(os.path.join(log_dir, filename))
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(process)d-%(thread)d %(levelname)-8s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(file_handler)
