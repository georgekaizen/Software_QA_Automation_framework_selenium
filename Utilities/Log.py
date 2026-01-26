"""
Logging utility. Writes log output to the Logs/ directory.
"""

import logging
import os
import time


class Log:
    _log_dir = os.path.join(os.path.dirname(__file__), '..', 'Logs')

    @staticmethod
    def _get_logger():
        logger = logging.getLogger("AutomationFramework")
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)

            fmt = logging.Formatter(
                '%(asctime)s - %(filename)s:[%(lineno)s] - [%(levelname)s] - %(message)s'
            )

            os.makedirs(Log._log_dir, exist_ok=True)
            curr_time = time.strftime("%Y-%m-%d")
            log_file = os.path.join(Log._log_dir, f'log{curr_time}.txt')

            fh = logging.FileHandler(log_file, mode="a")
            fh.setFormatter(fmt)
            fh.setLevel(logging.INFO)
            logger.addHandler(fh)

        return logger


Log.logger = Log._get_logger()
