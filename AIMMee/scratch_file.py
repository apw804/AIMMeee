"""
AIMM Energy Efficiency (AIMMee) is a fork of the AIMM Simulator (Credit: Keith Briggs). It is a simulator for 5G mobile networks that allows running experiments and analysing the energy efficiency of 5G and Open RAN networks.

Note:
    Transmit power is given in dBm.
    Pathloss is given in dB.
    Distance is given in metres.
    Frequency is given in Hz.
    Bandwidth is given in Hz.

    Energy is given in Joules.
    Power is given in Watts.
    Time is given in seconds.

    1 W.s = 1 J
    1 W.h = 3600 W.s = 3600 J
    1 kW.h = 3600 kWs = 1000 Wh = 3.6e6 J

Usage:
    Run this script to perform energy efficiency experiments on a mobile network. Modify the experiment configuration file to change the experiment parameters.

Example:
    $ python AIMMee.py -c config.json   # Run the simulator with the configuration file config.json
    $ python AIMMee.py -t               # Run the unit tests

For more information, refer to the project documentation and README.md file.
"""

__author__ = "Kishan Sthankiya"
__version__ = "0.1"
__date__ = "2023-07-10"

import logging
import argparse
import multiprocessing as mp
import json
from pathlib import Path
from time import time
from itertools import count as itertools_count
import numpy as np

from AIMM_simulator import UMa_pathloss_model, UMi_pathloss_model, NR_5G_standard_functions
from AIMM_simulator import Sim as AIMM_Sim, Scenario as AIMM_Scenario, UE as AIMM_UE, Cell as RadioFunctions



class ConfigLoader: 
    """
    Loads the configuration from a JSON file for different elements of the simulator.
    """
    def __init__(self):
        pass

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

    def load(self, config_file):
        # FIXME: Add a test to check the size, incase the config file is too large and need to be chunked.
        with open(config_file, 'r') as file:
            return json.load(file)


class Experiment:
    """
    This class produces a pool of Sim() objects based on the configuration file and runs them in parallel. Using the multiprocessing module, the number of Sim() objects that can be run in parallel is limited by the number of CPU cores available on the machine.

    Parameters are read in from a JSON file and include details such as (but not limited to):  Experiment name, number of seeds, how many Sim() objects to run at the same time, Scenario to apply, where to put output files, plotting options, statistical analysis options etc.
    """
    def __init__(self, config):
        self.config = config
        self.sim_pool = []
    
    def get_CPU_count(self):
        """
        Returns the number of CPU cores available on the machine.
        """
        return mp.cpu_count()

    def get_sim_pool(self):
        """
        Returns a list of Sim() objects to run in parallel.
        """
        return self.sim_pool
    
    def add_to_sim_pool(self, sim):
        """
        Adds a Sim() object to the simulation pool.
        """
        self.sim_pool.append(sim)
    

    def run(self):
        t0 = time()
        # Run the Sim() objects in parallel
        t1 = time()
        print(f'Experiment took {t1-t0} seconds to run.')


class Sim(AIMM_Sim):
    """
    Defines the simulation environment and runs the simulation.
    """
    # FIXME - is there a way to import the AIMM_Sim class and then override the __init__ method?
    id_iter = itertools_count(1, 1)
    def __init__(self, 
                 params={'fc_GHz':3.5,'h_UT':2.0,'h_BS':20.0}, 
                 show_params=False, 
                 rng_seed=None):
        self.id = next(self.id_iter)
        print(f'Sim[{self.id}] created.')
        # Turn off printing to console from the superclass

        super().__init__(params, show_params, rng_seed)

    def add_object(self, object):
        """
        Adds an object to the simulation.
        """
        assert isinstance(object, SimObject)
        # Get the object class name (plural)
        object_class = object.__class__.__name__ + 's'
        # If the class name is not in self, then add it
        if object_class not in self.__dict__:
            self.__dict__[object_class] = []
        # Add the object to the list
        self.__dict__[object_class].append(object)
        # Set the simulation object
        object.sim = self
        # Print message to console
        print(f'Sim[{self.id}]: Added {object_class}[{object.id}] to the simulation.')

    def add_RadioAccessSite(self,ras):
        '''
        Add a radio access site to the simulation.
        '''
        assert isinstance(ras,RadioAccessSite)
        self.add_object(ras)


    def add_RadioUnit(self,ru):
        '''
        Add a radio unit to the simulation.
        '''
        assert isinstance(ru,RadioUnit)
        self.add_object(ru)

    
    def add_PhysicalServer(self,ps):
        '''
        Add a physical server to the simulation.
        '''
        assert isinstance(ps,PhysicalServer)
        self.add_object(ps)

    def add_DistributedUnit(self,du):
        '''
        Add a distributed unit to the simulation.
        '''
        assert isinstance(du,DistributedUnit)
        self.add_object(du)

    def add_CentralisedUnit(self,cu):
        '''
        Add a centralised unit to the simulation.
        '''
        assert isinstance(cu,CentralisedUnit)
        self.add_object(cu)

# END class Sim

class SimObject:
    """
    Defines the common attributes of all objects in the simulation.
    """
    id_iter = itertools_count(1, 1)
    
    def __init__(self):
        self.id = next(self.id_iter)
        
    def get_sim(self):
        """
        Returns the simulation object that this object belongs to.
        """
        print(f'{self.__class__.__name__}[{self.id}] belongs to Sim[{self.sim.id}]')
        return self.sim
    
    def set_sim(self, sim:Sim):
        """
        Sets the simulation object that this object belongs to.
        """
        sim.add_object(self)
        print(f'{self.__class__.__name__}[{self.id}] now belongs to Sim[{sim.id}]')
        



class Scenario:
    """
    Defines the scenario for the simulation.
    - Mobility model
    - Traffic model
    - Network model
    - Environment dimensions
    """
    pass

class Interface:
    """
    An object that captures the graph (vertices and edges) of the RAN and the core network.
    Defines parameters for the network such as:
    - Topology
    - Link type (e.g. fibre, copper, wireless)
    - Link classification (e.g. fronthaul, midhaul, backhaul)
    - Link length
    - Link capacity
    - Link utilisation 
    - Link latency
    - End-to-end functional split of a subgraph (e.g. Opt1,...,Opt7.2, Opt8)
    """
    pass

class SMO:
    """
    An object that models the SMO interface.
    Function: Connects the non-RT RIC to the SMO.
    """
    def __init__(self):
        self.members = []

    pass

class O1:
    """
    An object that models the O1 interface.
    Functions: 
    - Connects O-RAN managed elements (near-RT RIC, O-CU, O-DU, O-RU) to the SMO and the non-RT RIC.
    - Supports SMO FCAPS (Fault, Configuration, Accounting, Performance, Security) management.
    """
    def __init__(self):
        self.SMO_parent = None
        self.nearRT_RIC_children = []
        self.O_CU_children = []
        self.O_DU_children = []
        self.O_RU_children = []
    pass

class O2:
    """
    An object that models the O2 interface.
    Function: Connects the SMO to the ORAN O-Cloud
    """
    def __init__(self):
        self.SMO_parent = None
        self.O_Cloud_children = []
    pass

class A1:
    """
    An object that models the A1 interface.
    Function: Connects the non-RT RIC (or SMO) and near-RT RIC. 
    """
    def __init__(self):
        self.nonRT_RIC_parent = None
        self.nearRT_RIC_children = []
    pass

class E2:
    """
    An object that models the E2 interface.
    Function: Connects the near-RT RIC to the O-CU, O-DU & O-RAN compliant eNBs.
    """
    def __init__(self):
        self.nearRT_RIC_parent = None
        self.O_CU_children = []
        self.O_DU_children = []
        self.eNB_children = []
    pass


class Cell:
    """
    A Cell defines a geographical area and the objects within it. 
    """

class UE(AIMM_UE):
    """
    A UE is a user equipment object that is connected to the network.
    """
    id=0
    def __init__(self, 
                 sim_id, 
                 xyz=None,
                 reporting_interval=1.0,
                 pathloss_model=None,
                 h_UT=2.0,
                 f_callback=None,
                 f_callback_kwargs={},
                 verbosity=0):
        self.id = UE.id
        UE.id += 1
        super().__init__(sim=sim_id,
                         xyz=xyz,
                         reporting_interval=reporting_interval,
                         pathloss_model=pathloss_model,
                         h_UT=h_UT,
                         f_callback=f_callback,
                         f_callback_kwargs=f_callback_kwargs,
                         verbosity=verbosity)

# END class UE


class TrafficGenerator:
    """
    An object that generates traffic that the UE has requested.
    Options include:
    - Traffic type (e.g. voice, video, data)
    - Traffic model (e.g. Poisson, Markov, ON/OFF)
    - Conditions (Low, Medium, High load)
    - File sizes (0.1kB, 1kB, 250kB)
    """
    pass

class Cabinet:
    """
    A location that holds the physical RAS equipment.
    """
    id=0
    def __init__(self, sim_id, radio_access_site_id):
        self.sim_id:int = sim_id
        self.id:int = Cabinet.id
        Cabinet.id += 1
        self.radio_access_site_id:int= radio_access_site_id

class RadioAccessSite:
    """
    A Radio Access Site is a collection of objects that are used to provide the radio access to UEs within a geographical area.
    This includes:
        RRH + fronthaul termination equipment (Open RAN)
    More generally, the RAS also includes a cabinet that holds:
        - Mains supply
        - Battery backup
        - Power Amplifier
        - Air conditioning (optional - if required)
    """
    id=0
    def __init__(self, sim_id):
        self.sim_id:int= sim_id
        self.id:int = RadioAccessSite.id
        RadioAccessSite.id += 1
        self.cell_ids:list = []
        self.cabinet_id:int = None
        self.radio_unit_id:int = None
        self.physical_BBU_id:int = None
        self.physical_links:list = []

    def __str__(self):
        return f'RadioAccessSite(id={self.id}, sim_id={self.sim_id}, cell_ids={self.cell_ids}, cabinet_id={self.cabinet_id}, open_RU_id={self.radio_unit_id}, physical_BBU_id={self.physical_BBU_id}, physical_links={self.physical_links})'
    
# End of RadioAccessSite class

class AntennaPanel:
    """
    An object that models the antenna panel of a radio access site.
    Options include:
    - Number of antenna elements
    - Beamforming
    - Antenna gain
    - Antenna type (e.g. omni, 2-port, 8-port, AAU, mMIMO)
    - Power consumption model
    """
    id=0
    def __init__(self, num_elements, beamforming, gain, antenna_type):
        self.num_elements = num_elements
        self.beamforming = beamforming
        self.gain = gain
        self.antenna_type = antenna_type
        self.id = AntennaPanel.id
        AntennaPanel.id += 1
        self.validate()

    def validate(self):
        if not isinstance(self.num_elements, int) or self.num_elements <= 0:
            raise ValueError('Number of antenna elements must be a positive integer.')

        if not isinstance(self.beamforming, bool):
            raise ValueError('Beamforming must be a boolean.')

        if not isinstance(self.gain, (int, float)) or self.gain <= 0:
            raise ValueError('Antenna gain must be a positive number.')

        valid_types = ['omni', '2-port', '8-port', 'AAU', 'mMIMO']
        if self.antenna_type not in valid_types:
            raise ValueError(f'Antenna type must be one of {valid_types}.')

    def power_model(self):
        power = self.num_elements * 10
        if self.beamforming:
            power += 50
        return power

    def __str__(self):
        return f'AntennaPanel(num_elements={self.num_elements}, beamforming={self.beamforming}, gain={self.gain}, type={self.antenna_type})'


class RemoteRadioHead:
    """
    An object that models the remote radio head (RRH).
    One or more antenna panel objects are connected to a RemoteRadioHead object.
    The RemoteRadioHead provides the RF processing.

    Options include:
    - Type (e.g. 2T2R, 4T4R, 8T8R, mMIMO)
    - Transmit antenna ports: (e.g. 2T, 4T, 8T, 64T) 

    # FIXME - add more options from the following:
    # [(https://cosconor.fr/GSM/Divers/Equipment/Nokia/SRAN%20configurations.pdf)]


    """
    id=0
    def __init__(self, sim_id, radio_access_site_id, tx_antenna_ports, rx_antenna_ports, antenna_panel_ids, network_interfaces, power_in, power_out, cabinet_id):
        self.id = RemoteRadioHead.id
        RemoteRadioHead.id += 1
        self.sim_id:int = sim_id # Simulation object ID that the RRH is connected to
        self.radio_access_site_id:int = radio_access_site_id # RadioAccessSite object ID that the RRH is connected to
        self.tx_antenna_ports:int = None # e.g. 2T, 4T, 8T, 64T
        self.rx_antenna_ports:int = None # e.g. 2R, 4R, 8R, 64R
        self.antenna_panel_ids:list = [] # AntennaPanel object IDs that are connected to the RRH
        self.network_interfaces:list = [] # [(type, capacity (Gbps), number)] e.g. [('CPRI', 9.8, 4), ('eCPRI', 24.3, 2)]
        self.power_in: int = 0 # e.g. 740 watts
        self.power_out: int = 0 # e.g. 640 watts
        self.cabinet_id:int = None # Cabinet object ID that the RRH is connected to
        self.BBU_id:int = None # BBU object ID that the RRH is connected to
        pass

    def __str__(self):
        return f'RemoteRadioHead(id={self.id}, sim_id={self.sim_id}, radio_access_site_id={self.radio_access_site_id}, tx_antenna_ports={self.tx_antenna_ports}, rx_antenna_ports={self.rx_antenna_ports}, antenna_panel_ids={self.antenna_panel_ids}, network_interfaces={self.network_interfaces}, power_in={self.power_in}, power_out={self.power_out}, cabinet_id={self.cabinet_id}, BBU_id={self.BBU_id})'
    
    def get_load(self):
        """
        Returns the load on the RRH in terms of the power in and power out.
        """
        return self.power_out / self.power_in
    
# End of RemoteRadioHead class

class RadioUnit:
    """
    A logical object that models the radio unit.
    It is the subset of components at a RadioAccessSite that provide the RF processing and optionally the low-PHY layer processing.
    
    Must include:
    - RF processing (e.g. 2T2R, 4T4R, 8T8R, mMIMO)
    - Antennas
    - Fronthaul interface
    - Power consumption model
    May include:
    - Low-PHY layer processing (e.g. FFT/iFFT, PRACH extraction), if functional split < Option 8
    """
    id=0

    def __init__(self, sim_id, radio_access_site_id):
        self.id = RadioUnit.id
        RadioUnit.id += 1
        self.sim_id = sim_id
        self.radio_access_site_id = radio_access_site_id

    def get_load(self):
        """
        Returns the load on the RadioUnit based on the load of the components within it.
        """
        pass

    def __str__(self):
        return f'RadioUnit(sim_id={self.sim_id}, radio_access_id={self.radio_access_site_id})'

# End of RadioUnit class

class PhysicalServer:
    def __init__(self, sim_id, cpu_cores, ram_gb, storage_tb, gpu_cores, location):
        self.sim_id = sim_id
        self.cpu_cores = cpu_cores
        self.cpu_cores_used = 0
        self.ram_gb = ram_gb
        self.ram_gb_used = 0
        self.storage_tb = storage_tb
        self.storage_tb_used = 0
        self.gpu_cores = gpu_cores
        self.gpu_cores_used = 0
        self.fgpa:bool = False
        self.location = location
        self.vDU_ids:list = [] # virtual DU object IDs
        self.vCU_ids:list = [] # virtual CU object IDs

    def boot_up(self):
        print(f"Booting up physical server located at {self.location}...")

    def shut_down(self):
        print(f"Shutting down physical server located at {self.location}...")



   
class DistributedUnit():
    """
    A logical object that models the distributed unit that is connected to the remote radio unit and provides the baseband processing.
    In this model, the DU is virtualised on a COTS server.
    Southbound interface: Fronthaul interface
    Northbound interface: Midhaul interface

    """
    id=0
    def __init__(self, sim_id, host_server:PhysicalServer, cpu_cores, ram_gb, storage_tb,
                 fronthaul_capacity_Gbps, midhaul_capacity_Gbps, radio_unit_ids=None, centralised_unit_id=None):
        self.id:int = DistributedUnit.id
        DistributedUnit.id += 1
        self.sim_id:int = sim_id
        self.host_server:PhysicalServer = host_server
        self.cpu_cores:int = cpu_cores
        self.cpu_cores_used:int = 0
        self.ram_gb:int = ram_gb
        self.ram_gb_used:int = 0
        self.storage_tb:int = storage_tb
        self.storage_tb_used:int = 0
        self.fronthaul_capacity:float = fronthaul_capacity_Gbps # Gbps
        self.radio_unit_ids:list = radio_unit_ids
        self.midhaul_capacity:float = midhaul_capacity_Gbps # Gbps
        self.centralised_unit_id:int = centralised_unit_id

    def get_load(self):
        """
        Returns the load on the DU in terms of the power in and power out.
        """
        self.load = self.host_server.get_vDU_load(self.id)
        return self.load
    
    def __str__(self):
        return f'DistributedUnit(id={self.id}, sim_id={self.sim_id}, radio_unit_ids={self.radio_unit_ids}, centralised_unit_id={self.centralised_unit_id}.)'
    
# End of DistributedUnit class


class CentralisedUnit:
    """
    A logical object that models the centralised unit that is connected to the distributed unit.
    This could be a physical object or a virtualised object.
    The CU hosts the RRC, SDAP and PDCP protocols
    """
    id=0
    def __init__(self, sim_id, distributed_unit_ids, host_server=None):
        self.id:int = CentralisedUnit.id
        CentralisedUnit.id += 1
        self.sim_id:int = sim_id
        self.distributed_unit_ids:list = distributed_unit_ids
        self.host_server_id:int = host_server.id

    
    def get_load(self):
        """
        Returns the load on the CU in terms of the power in and power out.
        """
        self.load = self.host_server.get_vCU_load(self.id)
        return self.load
    
    def __str__(self):
        return f'CentralisedUnit(id={self.id}, sim_id={self.sim_id}, distributed_unit_ids={self.distributed_unit_ids}, host_server_id={self.host_server_id}.)'

# FIXME - Consider adding a class for the physical BBU

class RIC:
    """
    An object that models the RAN Intelligent Controller that is connected to the baseband unit and provides the RAN control plane.
    Options include:
    - Virtual or physical
    - Near-RT RIC or non-RT RIC
    - Power consumption model
    """
    pass


class Logger:
    """
    An object that logs the simulation results.
    """
    pass


def initialise_AIMMee():
    """
    Initialise the AIMMee Simulator.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('Initializing AIMMee Simulation...')
    loader = ConfigLoader()
    arg_parser = loader.get_argument_parser()
    args = arg_parser.parse_args()
    conf_file = args.config_file
    if conf_file:
        logging.info('Loading configuration...')
        conf = loader.load(Path(conf_file).resolve())
        logging.info(f'Configuration loaded: {conf_file}')
    elif args.unittest:
        logging.info('Running unit tests...')
        import unittest
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover(start_dir='.', pattern='test_*.py')
        unittest.TextTestRunner().run(test_suite)
        logging.info('Unit tests complete.')
    

def test_AnntennaPanel():
    """
    Test that the AntennaPanel() object can be initialised.
    """
    logging.info('Testing antenna panel class...')
    ap = AntennaPanel(num_elements=64, beamforming=True, gain=10, antenna_type='omni')
    logging.info(ap)
    logging.info('Antenna panel class test complete.')

def test_RadioAccessSite():
    """
    Test the radio access site class.
    """
    logging.info('Testing radio access site class...')
    ras = RadioAccessSite(sim_id=1)
    logging.info(ras)
    logging.info('Radio access site class test complete.')

def test_RemoteRadioHead():
    """
    Test the remote radio head class.
    """
    logging.info('Testing remote radio head class...')
    rrh = RemoteRadioHead(sim_id=1,
                          radio_access_site_id=1, 
                          tx_antenna_ports=4, 
                          rx_antenna_ports=4, 
                          antenna_panel_ids=[], 
                          network_interfaces=[('eCPRI', 24.3, 2)], 
                          power_in=740, 
                          power_out=640, 
                          cabinet_id=1)
    logging.info(rrh)
    logging.info('Remote radio head class test complete.')

def test_RadioUnit():
    """
    Test the radio unit class.
    """
    logging.info('Testing radio unit class...')
    ru_1 = RadioUnit(sim_id=1, radio_access_site_id=1)
    ru_2 = RadioUnit(sim_id=2, radio_access_site_id=2)
    logging.info(ru_1)
    logging.info(ru_2)
    logging.info('Radio unit class test complete.')



if __name__ == '__main__':
    initialise_AIMMee()
    test_AnntennaPanel()
    test_RadioAccessSite()
    test_RemoteRadioHead()
    test_RadioUnit()
    logging.info('All tests complete.')