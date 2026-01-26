"""
Utility for reading configuration values (locators, browser settings, etc.)
from the config.ini file using Python's ConfigParser.
"""

from configparser import ConfigParser
import os


class ConfigReader:
    _file_path = os.path.join(
        os.path.dirname(__file__), '..', 'Configurations', 'config.ini'
    )

    @staticmethod
    def readconfig(section, key):
        config = ConfigParser()
        config.read(ConfigReader._file_path)
        return config.get(section, key)
