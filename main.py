#!/usr/bin/pyton3.5
"""Main script of application"""

import os
from modules.ConfigHandler.ConfigHandler import ConfigHandler
from modules.Files.Parser import FilesParser
from modules.Files.Copier import FilesCopier

def main():
    """Main"""
    print("Initializing...")
    print("Parsing configuration file...")
    configuration_manager = ConfigHandler(os.path.abspath(os.path.dirname(__file__)))
    parsed_conf = configuration_manager.read()
    print("Beginning source scan...")
    files_parser = FilesParser(parsed_conf['SOURCE'])
    if files_parser.parse_files():
        print("Scan complete...")
        print("Beginning files copy. This process can take a while...")
        files_copier = FilesCopier()
        files_copier.start(parsed_conf['TARGET'], parsed_conf['SOURCE'])
        print("All done!")
if __name__ == '__main__':
    main()
