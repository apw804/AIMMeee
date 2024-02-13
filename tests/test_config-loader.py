import unittest
from pathlib import Path
from unittest.mock import patch
from AIMMee.utilities import config_loader as ConfigLoader
import json

class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.config_loader = ConfigLoader()

    def test_load_valid_file(self):
        # Create a temporary JSON file
        config_file = Path("test_config.json")
        config_data = {"key": "value"}
        with open(config_file, "w") as file:
            json.dump(config_data, file)

        # Load the configuration from the file
        loaded_config = self.config_loader.load(config_file)

        # Assert that the loaded configuration matches the original data
        self.assertEqual(loaded_config, config_data)

        # Clean up the temporary file
        config_file.unlink()

    def test_load_large_file(self):
        # Create a temporary large JSON file
        config_file = Path("test_large_config.json")
        large_data = {"key": "value" * int(1e6)}  # Create a large data object
        with open(config_file, "w") as file:
            json.dump(large_data, file)

        # Mock the file size to be larger than the maximum allowed size
        with patch("config_loader.Path.stat") as mock_stat:
            mock_stat.return_value.st_size = int(1e9)  # Set the file size to be larger than 100MB

            # Assert that loading the large file raises a ValueError
            with self.assertRaises(ValueError):
                self.config_loader.load(config_file)

        # Clean up the temporary file
        config_file.unlink()

if __name__ == '__main__':
    unittest.main()