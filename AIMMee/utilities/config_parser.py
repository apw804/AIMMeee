import argparse

class ConfigParser:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = None
        self.parse_config_file()
        
    def get_config_parser():
        config_parser = argparse.ArgumentParser(
            description='Generic AIMMee simulator configuration parser.')
        config_parser.add_argument('-c',
                                '--config-file', 
                                type=str, 
                                help='Path to configuration file.')
        return config_parser
    