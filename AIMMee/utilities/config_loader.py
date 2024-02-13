from itertools import count as itertools_count
import argparse
import json

class ConfigLoader():
    """
    Loads the configuration from a JSON file for different elements of the simulator.
    """
    id_iter=itertools_count()
    def __init__(self):
        print('INIT of ConfigLoader')
        self.guid = id(self)
        self.class_name = self.__class__.__name__
        self.idx = next(ConfigLoader.id_iter)
        self.label = f'{self.class_name}[{self.idx}]'

    @staticmethod
    def get_argument_parser():
        parser = argparse.ArgumentParser(description='AIMMee simulator configuration parser.')
        parser.add_argument('-c', '--config-file', type=str, help='Path to configuration file.')
        parser.add_argument('-unittest', '--unittest', action='store_true', help='Run unit tests.')

        args = parser.parse_args()

        # Custom validation check
        if args.config_file and args.unittest:
            parser.error("Options -c/--config-file and -unittest cannot be specified together.")

        return parser

    def load(self, config_file, max_file_size_bytes=1e8):
        # Get the size of the file in bytes
        file_size = config_file.stat().st_size

        # Check if the file size is too large
        if file_size > max_file_size_bytes:
            # Handle the file accordingly (e.g. raise an exception, split the file into chunks, etc.)
            raise ValueError(f"File size ({file_size} bytes) exceeds maximum size ({max_file_size_bytes} bytes).")

        # Open the JSON file in read mode
        with open(config_file, 'r') as file:
            # Load the JSON data from the file
            return json.load(file)