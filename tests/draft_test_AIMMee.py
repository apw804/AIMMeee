import unittest
from pathlib import Path

from AIMMee import ConfigLoader, argparse, AntennaPanel, RadioAccessSite, RemoteRadioHead, RadioUnit

class TestAIMMee(unittest.TestCase):
    """
    A class that contains unit tests for the AIMMee package.
    """

    def test_init_conf_loader(self):
        """
        Test that the ConfigLoader() object can be initialised.
        """
        conf_loader = ConfigLoader()
        self.assertIsInstance(conf_loader, ConfigLoader)

    def test_conf_loader_arg_parser(self):
        """
        Test that the argument parser can be initialised.
        """
        conf_loader = ConfigLoader()
        arg_parser = conf_loader.get_argument_parser()
        self.assertIsInstance(arg_parser, argparse.ArgumentParser)

    def test_conf_loader_load(self):
        """
        Test that a YAML config file can be loaded and converted to a dictionary.
        """
        conf_loader = ConfigLoader()
        cwd = Path.cwd()
        test_conf = conf_loader.load(Path(cwd.parent / 'tests' / 'test_AIMMee.yaml'))
        self.assertEqual(test_conf['conf_loads'], True)

    def test_AnntennaPanel(self):
        """
        Test that the AntennaPanel() object can be initialised.
        """
        ap = AntennaPanel(num_elements=64, beamforming=True, gain=10, antenna_type='omni')
        print(ap)
        self.assertIsInstance(ap, AntennaPanel)
    
    def test_RadioAccessSite(self):
        """
        Test the radio access site class.
        """
        ras = RadioAccessSite(sim_id=1)
        print(ras)
        self.assertIsInstance(ras, RadioAccessSite)

    def test_RemoteRadioHead(self):
        """Test that the RemoteRadioHead() object can be initialised."""
        rrh = RemoteRadioHead(sim_id=1,
                              radio_access_site_id=1, 
                              tx_antenna_ports=4, 
                              rx_antenna_ports=4, 
                              antenna_panel_ids=[], 
                              network_interfaces=[('eCPRI', 24.3, 2)], 
                              power_in=740, 
                              power_out=640, 
                              cabinet_id=1)
        print(rrh)
        self.assertIsInstance(rrh, RemoteRadioHead)

    def test_RadioUnit(self):
        """Test that the RadioUnit() object can be initialised."""
        ru=RadioUnit(sim_id=1,
                     radio_access_site_id=1)
        print(ru)
        self.assertIsInstance(ru, RadioUnit)


if __name__ == '__main__':
    unittest.main()
