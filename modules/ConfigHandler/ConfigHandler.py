#!/usr/bin/pyton3.5
"""Configuration handler management"""

from pathlib import Path
import configparser

class ConfigHandler:
    """Class designed for handle all configuration file management"""

    def __init__(self,app_path):
        self.EXEC_PATH = app_path
        self.CONFIG_FILE = "%s/conf/file_copier.conf" % self.EXEC_PATH
        if not self.exists():
            self.create()

    def exists(self):
        """Checks if the configuration file is exists"""
        return Path(self.CONFIG_FILE).is_file()

    def create(self):
        """Create the config file"""
        config = configparser.ConfigParser(allow_no_value=True)
        config.add_section("SOURCE")
        config.set("SOURCE", ";Type of the server (local or ftp)", None)
        config.set("SOURCE", 'Type', '')
        config.set("SOURCE", ";Address from where we should copy the files: localhost or IP address", None)
        config.set("SOURCE", 'address', '')
        config.set("SOURCE", ';Path of the root folder of the copy process. All files that is inside that folder will be copied', None)
        config.set("SOURCE", 'Path', '')
        config.set("SOURCE", ';Username of the source server. Will be used if the source server is a remote server', None)
        config.set("SOURCE", 'User', '')
        config.set("SOURCE", ';Password of the source server. Will be used if the source server is a remote server', None)
        config.set("SOURCE", 'Password', '')
        config.add_section("TARGET")
        config.set("TARGET", ";Type of the server (local or ftp)", None)
        config.set("TARGET", 'type', '')
        config.set("TARGET", ";Address from where we should copy the files: localhost or IP address", None)
        config.set("TARGET", 'address', '')
        config.set("TARGET", ';Path of the root folder of the copy process. All files that is inside that folder will be copied', None)
        config.set("TARGET", 'path', '')
        config.set("TARGET", ';Username of the target server. Will be used if the target server is a remote server', None)
        config.set("TARGET", 'user', '')
        config.set("TARGET", ';Password of the target server. Will be used if the target server is a remote server', None)
        config.set("TARGET", 'password', '')

        with open(self.CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        print("Configuration stored at %s. Please enter all needed details in this file before continue"%self.CONFIG_FILE)
        exit(0)

    def read(self, section=None, option=None):
        """Reads and validates the configuration file"""
        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE)
        ret = None
        if section is not None and option is not None:
            ret = config.get(section, option)
        elif section is not None and option is None:
            ret = config.items(section)
        else:
            ret = config
        return ret
