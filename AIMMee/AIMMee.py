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
from sys import stderr, argv, stdout
from time import time
from itertools import count as itertools_count
from itertools import combinations
from random import seed
from pprint import pprint
from typing import Callable
from math import cos, sin, pi

import numpy as np

from AIMM_simulator import UMa_pathloss_model
from AIMM_simulator import UMi_pathloss_model
from AIMM_simulator import NR_5G_standard_functions
from AIMM_simulator import Sim as AIMM_Sim
from AIMM_simulator import UE as AIMM_UE
from AIMM_simulator import Cell as AIMM_Cell
from AIMM_simulator import Logger as AIMM_Logger
from AIMM_simulator import Scenario as AIMM_Scenario
from AIMM_simulator import MME as AIMM_MME
from AIMM_simulator import RIC as AIMM_RIC
from AIMM_simulator import np_array_to_str, to_dB



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


class Experiment():
    """
    This class produces a pool of Sim() objects based on the configuration file and runs them in parallel. Using the multiprocessing module, the number of Sim() objects that can be run in parallel is limited by the number of CPU cores available on the machine.

    Parameters are read in from a JSON file and include details such as (but not limited to):  Experiment name, number of seeds, how many Sim() objects to run at the same time, Scenario to apply, where to put output files, plotting options, statistical analysis options etc.
    """
    def __init__(self, config):
        print('INIT of Experiment')
        self.guid=id(self)
        self.class_name = self.__class__.__name__
        self.config = config
        self.pool = []
    
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
    
    def add_to_pool(self, sim):
        """
        Adds a Sim() object to the simulation pool.
        """
        self.pool.append(sim)

    def run(self):
        t0 = time()
        # Run the Sim() objects in parallel
        t1 = time()
        print(f'Experiment took {t1-t0} seconds to run.')

    def confirm_sim_params_prompt(self, sim):
        """
        Prompts the user to confirm the simulation parameters.
        # FIXME: Update this so it works in the context of an experiment
        """
        pprint(sim.topology)
        # If user responds Y or y or Yes or yes, then add to the simulation pool.
        if input('Run simulation? [Y/N] ').lower() in ['y','yes']:
            self.add_to_pool(sim)
            print('Simulation added to pool.')
        else:
            print('Simulation discarded.')



class Sim(AIMM_Sim):
    """
    AIMMee Sim: Defines the simulation environment and runs the simulation.
    """
    id_iter = itertools_count()
    def __init__(self, *args, **kwargs):
        print('INIT of Sim(AIMMee)')
        self.guid = id(self)
        self.class_name = self.__class__.__name__
        self.idx = next(Sim.id_iter)
        self.label = f'{self.class_name}[{self.idx}]'
        self.origin = np.array([0.,0.,0.])
        print(f'Sim[{self.idx}]: Initialised.')
        self.set_sim_topology()
        self.set_guid_map()
        self.raps=[]
        self.rus=[]
        self.rrhs=[]
        if 'until' in kwargs:
            self.until:int or float = kwargs.pop('until')
        else:
            logging.warning(f'Sim[{self.idx}]: No "until" parameter specified. Defaulting to 100.0.')
            self.until = 100.0
        super().__init__(*args, **kwargs) # This one calls the INIT of AIMM_Sim

    def set_sim_topology(self):
        """
        Makes the simulation topology.
        """
        if not hasattr(self, 'topology'):
            self.topology = {}
            print(f'Sim[{self.idx}]: Topology set.')

    def set_guid_map(self):
        """
        Makes the guid map.
        """
        if not hasattr(self, 'guid_map'):
            self.guid_map = {}
            print(f'Sim[{self.idx}]: GUID map set.')

    def get_sim_topology(self):
        """
        Returns the simulation topology.
        """
        return self.topology
    
    def get_object_from_guid(self, guid):
        """
        Returns the object from the given GUID.
        """
        if not isinstance(guid, int):
            raise ValueError(f'GUID {guid} must be an integer.')
        if guid not in self.sim.guid_map:
            raise ValueError(f'GUID {guid} not found in simulation.')
        return self.sim.guid_map[guid]

    def get_link_lists(self, sim_objs:list):
        """
        Returns a list of lists, containing the GUIDs of linked objects for the given sim_objs.
        """
        assert isinstance(sim_objs, list)
        for sim_obj in sim_objs:
            assert isinstance(sim_obj, SimObject)
        return [sim_obj.sim.topology[sim_obj.class_name][sim_obj.guid] for sim_obj in sim_objs]
    
    def set_object_id_map(self, other):
        """
        Maps the object id's to the object class names and instance index.
        """
        assert isinstance(other, SimObject)

    def get_origin(self):
        """
        Returns the origin location of the simulation.
        """
        return self.origin

    def make_cell(self,**cell_kwargs):
        """
        AIMMee Convenience function: make a new Cell instance and add it to the simulation; parameters as for the Cell class. Return the new Cell instance.
        """
        self.cells.append(AIMMeeCell(self,**cell_kwargs))
        xyz=self.cells[-1].get_xyz()
        self.cell_locations=np.vstack([self.cell_locations,xyz])
        return self.cells[-1]
    
    def make_UE(s,**kwargs):
        """
        AIMMee convenience function: make a new UE instance and add it to the simulation; parameters as for the UE class. Return the new UE instance.
        """
        s.UEs.append(AIMMeeUE(s,**kwargs))
        return s.UEs[-1]
    
    def make_RadioAccessPoint(self, **kwargs):
        """
        AIMMee convenience function: make a new RadioAccessPoint instance and add it to the simulation; parameters as for the RadioAccessPoint class. Return the new RadioAccessPoint instance.
        """
        self.raps.append(RadioAccessPoint(self, **kwargs))
        return self.raps[-1]
    
    def make_RadioUnit(self, **kwargs):
        """
        AIMMee convenience function: make a new RadioUnit instance and add it to the simulation; parameters as for the RadioUnit class. Return the new RadioUnit instance.
        """
        self.rus.append(RadioUnit(self, **kwargs))
        return self.rus[-1]
    
    def make_RemoteRadioHead(self, **kwargs):
        """
        AIMMee convenience function: make a new RemoteRadioHead instance and add it to the simulation; parameters as for the RemoteRadioHead class. Return the new RemoteRadioHead instance.
        """
        self.rrhs.append(RemoteRadioHead(self, **kwargs))
        return self.rrhs[-1]
    


    ##################################################
    # FIXME: Add the rest of the make_ functions here ^^^
    ##################################################


    def confirm_exe(self):
        """
        Prompts the user to confirm the simulation parameters.
        """
        pprint(self.topology)
        # If user responds Y or y or Yes or yes, then add to the simulation pool.
        if input('Run simulation? [Y/N] ').lower() in ['y','yes']:
            self.run(until=self.until)
        else:
            print('Simulation aborted.')
    
# END class Sim


class SimObject():
    """
    Defines the common attributes of all objects in the simulation.
    """
    id_iter = itertools_count()
    def __init__(self, sim:Sim):
        self.guid = id(self)
        self.class_name = self.__class__.__name__
        self.idx = next(self.id_iter)
        self.label = f'{self.class_name}[{self.idx}]'
        self.sim = sim
        self.add_to_sim(sim)
        if hasattr(self, 'interval'):
            # If the object already has a defined interval (from inheritance), 
            # then use that. Otherwise, use the default interval of None.
            return
        else:
            self.interval = 0.0

    def get_cls_name(self):
        return self.__class__.__name__

    def get_plural(self, other):
        return str(f'{other}s')

    def add_to_sim(self,sim:Sim):
        """
        Adds this object to the simulation (topology + guid map).
        """
        if not isinstance(sim, Sim):
            raise ValueError("`sim` argument MUST be a Sim() object")
        sim.topology.setdefault(self.class_name, {}).setdefault(self.guid, [])
        sim.guid_map.setdefault(self.guid, self)
        print(f'Sim[{sim.idx}]: Added {self.label} to {sim.label}.')


    def register_link(self, other):
        """
        Establishes a 'has a' relationship between this object (self) and other. This gets captured in the sim.topology dictionary.
        """
        if not isinstance(other, SimObject):
            raise ValueError("`other` argument MUST be a SimObject() object")
        if not isinstance(self.sim, Sim):
            raise ValueError("`self.sim` MUST be a Sim() object")
        # Get the topology dictionary for objects
        self_links_list = self.sim.topology[self.class_name][self.guid]
        other_links_list = other.sim.topology[other.class_name][other.guid]
        # Add `other` object to own list of attached objects
        if other.guid not in self_links_list:
            self_links_list.append(other.guid)
        else:
            print(f'{self.label}: {other.label} already exists in {self.label} topology list.')
        # Add `self` object to other's list of attached objects
        if self.guid not in other_links_list:
            other_links_list.append(self.guid)
        else:
            print(f'{self.label}: {self.label} already exists in {other.label} topology list.')


    def deregister_link(self, other):
        """
        Removes an adjacent object from this object, and vice versa (i.e. removes the two-way link between the objects) and updates the topology dictionary.
        """
        assert isinstance(other, SimObject)

        # Remove the other object from this object's list in the topology dictionary and vice versa
        self_links = self._sim.topology[self.class_name][self.guid]
        other_links = other._sim.topology[other.class_name][other.guid]
        if other.guid in self_links:
            self_links.remove(other.guid)
        else:
            print(f'{self.label}: {other.label} does not exist in {self.label} topology list.')
        if self._guid in other_links:
            other_links.remove(self.guid)
        else:
            print(f'{self.label}: {self.label} does not exist in {other.label} topology list.')

    @property
    def power_model(self):
        """
        Returns the energy model of the object.
        """
        if self._power_model is None:
            print(f'{self.__class__.__name__}[{self.idx}]: No energy model found.')
            return None
        else:
            return self._power_model
    
    @power_model.setter
    def power_model(self, new_power_model):
        """
        Sets the power model of the object.
        """
        if not isinstance(new_power_model, (int, float, Callable)):
            raise ValueError("power_model must be a constant or a function")
        self._power_model = new_power_model
        print(f'{self.__class__.__name__}[{self.idx}]: Power model set to {self.power_model.__repr__()}')

    def __repr__(self):
        return f'{self.class_name}(idx={self.idx}, guid={self.guid})'

# END class SimObject


class AIMMeeCell(AIMM_Cell, SimObject):
    """
    Defines the cell object in the simulation.
    """
    idx=itertools_count()
    def __init__(self, sim, *args, **kwargs):
        print('INIT of Cell(AIMMee)')
        self.idx = next(AIMMeeCell.id_iter)
        self.sim = sim
        self.label = f'{self.__class__.__name__}[{self.idx}]'
        self.radius = 0.0
        super(AIMM_Cell, self).__init__(self.sim) # This one calls the INIT of SimObject
        super().__init__(self.sim, **kwargs) # This one calls the INIT of AIMM_Cell

    def __repr__(self):
        return f'Cell(idx={self.idx}, xyz={self.xyz}, radius={self.radius})'
# END class Cell


class RadioAccessPoint(SimObject):
    idx=itertools_count()
    def __init__(self, sim:Sim, cell:AIMMeeCell, at_cell_centre:bool=True, interval:float=1.0, verbosity:int=0, **kwargs):
        print('INIT of RadioAccessPoint')
        self.idx = next(RadioAccessPoint.id_iter)
        self.sim = sim
        self.cell = cell
        self.interval = interval
        self.at_cell_centre = at_cell_centre
        super().__init__(self.sim, **kwargs)
        if self.cell is not None:
            self.register_link(cell)
        # Put the RadioAccessPoint in the cell, within the cell's radius
        if self.at_cell_centre:
            self.xyz = self.cell.get_xyz()
        self.xyz = self.cell.get_xyz()+self.cell.radius*np.random.uniform(-1,1,3)
        self.xyz[2] = 0.0 # RadioAccessPoint is always on the ground
        self.verbosity = verbosity
        if self.verbosity > 0:
            print(f'Cell[{self.cell.idx}]: position={self.cell.get_xyz()}')
            print(f'Cell[{self.cell.idx}]: radius={self.cell.radius}')
            print(f'RadioAccessPoint[{self.idx}]: xyz={self.xyz}')

    def make_RadioUnit(self, **kwargs):
        """
        Convenience function: make a new RadioUnit instance and add it to the simulation; parameters as for the RadioUnit class. Return the new RadioUnit instance.
        """

        new_object=RadioUnit(sim=self.sim, cell=self.cell, **kwargs)
        self.register_link(other=new_object)
        return new_object
    
    def loop(self):
        '''
        Main loop of SimObject class.  Default: do nothing.
        '''
        while True:
            yield self.sim.env.timeout(self.interval)
# END class RadioAccessPoint


class RadioUnit(SimObject):
    idx=itertools_count()
    def __init__(self, sim:Sim, cell:AIMMeeCell, rap:RadioAccessPoint, du=None, interval:float=1.0, verbosity:int=0, **kwargs):
        print('INIT of RadioUnit')
        self.idx = next(RadioUnit.id_iter)
        self.sim = sim
        self.cell = cell
        self.verbosity = verbosity
        self.rap= rap
        self.du = None
        self.interval = interval
        super().__init__(self.sim, **kwargs)
        if self.cell is not None:
            self.register_link(cell)
        if self.rap is not None:
            self.register_link(rap)
        if self.du is not None:
            self.register_link(du)

    
    
    def loop(self):
        '''
        Main loop of SimObject class.  Default: do nothing.
        '''
        while True:
            yield self.sim.env.timeout(self.interval)
# END class RadioUnit

class DistributedUnit(SimObject):
    idx=itertools_count()
    def __init__(self, sim:Sim):
        print('INIT of DistributedUnit')
        self.idx = next(DistributedUnit.id_iter)
        self.sim = sim
        super().__init__(sim=self.sim)
        self.power_model = self.example_DU_power_model()

    def attach_to_rrh(self, rrh):
        """
        Attaches the AntennaPanel to the RemoteRadioHead.
        """
        assert isinstance(rrh, RemoteRadioHead)
        self.rrh = rrh
        self.register_link(other=self.rrh)
        print(f'{self.label}: Attached to {self.rrh.label}.')

    def example_DU_power_model(self, P_supply_max=2100,
                                n_cpu=2, P_cpu=90.0,     
                                ram_GB=384, P_ram_GB=0.375,
                                n_gpu=0, P_gpu=0.0,
                                n_accel=1, P_accel=52.0,
                                n_asic=1, P_asic=23.0,
                                n_nic:int=3, P_nic:float=75.0):
        """
        Toy example power model for a Distributed Unit (DU) in a 5G base station. For more information on the parameters, see `example_DU_power_model.md`.
        """
        self.power_consumption = n_cpu*P_cpu + ram_GB*P_ram_GB + n_gpu*P_gpu + n_accel*P_accel + n_asic*P_asic + n_nic*P_nic
        self.p_load = self.power_consumption/P_supply_max
        return self.power_consumption
    
    def loop(self):
        '''
        Main loop of SimObject class.  Default: do nothing.
        '''
        while True:
            yield self.sim.env.timeout(self.interval)
# END class DistributedUnit


class CentralisedUnit(SimObject):
    idx=itertools_count()
    def __init__(self,
                 sim:Sim):
        print('INIT of CentralisedUnit')
        self.idx = next(CentralisedUnit.id_iter)
        self.sim = sim
        self.du = None
        super().__init__(sim=self.sim)
        self.power_model = self.example_CU_power_model(du_load=0.0)

    def attach_to_du(self, du:DistributedUnit):
        """
        Attaches the AntennaPanel to the DistributedUnit.
        """
        assert isinstance(du, DistributedUnit)
        self.du = du
        self.register_link(other=self.cu)
        print(f'{self.label}: Attached to {self.cu.label}.')

    def example_CU_power_model(self, du_load):
        """
        Toy function to estimate CU power consumption based on DU load. For more information on the parameters, see `example_CU_power_model.md`.
        NOTE: This assumes that the CU load is proportional to the DU load i.e. The more processing the DU does, the less processing the CU does.
        """
        return (1-du_load)*656.25            

    def loop(self):
        '''
        Main loop of SimObject class.  Default: do nothing.
        '''
        while True:
            yield self.sim.env.timeout(self.interval)
# END class CentralisedUnit


class RemoteRadioHead(SimObject):
    idx=itertools_count()
    # RF ports are where the antennas are connected
    # Fronthaul ports are where the DU is connected
    def __init__(self,
                 sim:Sim, 
                 rap:RadioAccessPoint,
                 ru:RadioUnit=None,
                 du:DistributedUnit=None,
                 n_rf_ports:int=2,
                 fronthaul_ports:dict={'n_ports':2, 'protocol':'CPRI', 'data_rate_Gbps_max':10.0},
                 verbosity:int=0,
                 **kwargs):
        print('INIT of RemoteRadioHead')
        self.idx = next(RemoteRadioHead.id_iter)
        self.sim = sim
        self.cell = None
        self.rap = rap
        self.ru = ru
        self.du = None
        super().__init__(sim=self.sim, **kwargs)
        self.n_rf_ports = n_rf_ports
        if n_rf_ports > 0:
            self.rf_ports = self.make_rf_ports(n_rf_ports)
        else:
            self.rf_ports = self.make_rf_ports(2)
        self.make_fronthaul_ports(**fronthaul_ports)
        self.verbosity = verbosity
        if self.rap is not None:
            self.cell = self.rap.cell
            self.register_link(self.cell)
        if self.ru is not None:
            self.register_link(self.ru)
        if self.du is not None:
            self.register_link(self.du)

    def make_rf_ports(self, n_rf_ports):
        """
        Makes the antenna ports of the RemoteRadioHead.
        """
        rf_port_dict = {f'port[{i}]': {'antenna_panel': None,
                                      'rf_output_max_watts': 20.0, 
                                      'rf_output_watts': 0.0
                                      } for i in range(n_rf_ports)}
        print(f'{self.label}]: Antenna RF ports initialised')
        return rf_port_dict

    def get_rf_port(self, i:int):
        """
        Returns the antenna port of the RemoteRadioHead.
        """
        assert isinstance(i, int)
        assert 0 < i <= self.n_rf_ports
        return self.antenna_ports[f'port[{i}]']

    def make_fronthaul_ports(self, n_ports, protocol:str, data_rate_Gbps_max:float):
        """
        Makes the fronthaul interface of the RemoteRadioHead.
        """
        self._default_port_params = {
                                    'protocol': protocol,
                                    'data_rate_Gbps': 0.0,
                                    'data_rate_Gbps_max': 10.0
                                    }
        self._fronthaul_ports = {f'fh_port[{i}]': self._default_port_params for i in range(n_ports)}

        print(f'{self.label}]: Fronthaul interface initialised')

    def get_fronthaul_port(self, protocol:str='', i:int=0):
        """
        Returns the fronthaul interface of the RemoteRadioHead.
        """
        return self._fronthaul_ports[f'fh_port[{i}]']
    
    def make_AntennaPanel(self, **kwargs):
        """
        Adds an AntennaPanel to the RemoteRadioHead.
        """
        ap=AntennaPanel(sim=self.sim, rrh=self, **kwargs)
        self.add_to_sim(sim=self.sim)
        self.register_link(other=ap)
        if isinstance(ap, AntennaPanel):
            # Assign to the first free antenna port
            for i in self.rf_ports:
                if self.rf_ports[i]['antenna_panel'] is None:
                    self.rf_ports[i]['antenna_panel'] = ap
                    print(f'{self.label}: {ap.label} connected to {self.label}.')
                    break
                # If none are free, then raise an exception
                raise Exception(f'{self.label}: No free antenna ports available.')
            return ap

    def loop(self):
        '''
        Main loop of SimObject class.  Default: do nothing.
        '''
        while True:
            yield self.sim.env.timeout(self.interval)
# END class RemoteRadioHead


class AntennaPanel(SimObject):
    # FIXME - when initialised, the Antenna Panel MUST be at a RadioAccessPoint
    # FIXME - inherit the radiation pattern from Cell
    # FIXME - should have a down-tilt angle

    idx=itertools_count()
    def __init__(self, 
                 sim:Sim,
                 rrh:RemoteRadioHead,
                 xyz:np.ndarray=np.zeros(3), 
                 azimuth:float=0.0, 
                 elevation:float=0.0, 
                 pattern=None,):
                
                print('INIT of AntennaPanel')
                self.sim=sim
                self.xyz=xyz
                self.azimuth=azimuth
                self.elevation=elevation
                self.pattern=pattern
                super().__init__(sim=self.sim)

    def loop(self):
        '''
        Main loop of SimObject class.  Default: do nothing.
        '''
        while True:
            yield self.sim.env.timeout(self.interval)
# END class AntennaPanel



class AIMMeeUE(AIMM_UE, SimObject):
    """
    User Equipment (UE): 
    --------------------
    """
    idx=itertools_count()
    def __init__(self, sim:Sim, *args,**kwargs):
        print('INIT of AIMMeeUE')
        self.guid = id(self)
        self.idx = next(AIMMeeUE.id_iter)
        self.sim = sim
        self.last_cell_guid = None
        self.current_cell_guid = None
        super(AIMM_UE, self).__init__(self.sim) # This one calls the INIT of SimObject
        super().__init__(self.sim, *args, **kwargs) # This one calls the INIT of AIMM_UE

    def update_cell_guid(self):
        """
        Updates the cell GUID.
        """
        if self.serving_cell.guid == self.current_cell_guid:
            return
        self.last_cell_guid = self.current_cell_guid
        self.current_cell_guid = self.serving_cell.guid

    def update_ue_topology(self):
        """
        Updates the UE topology.
        """
        if self.guid == None:
            return
        if self.last_cell_guid != self.current_cell_guid:
            # Remove the UE from the last cell
            if self.last_cell_guid is not None:
                while self.guid in self.sim.topology['AIMMeeCell'][self.last_cell_guid]:
                    self.sim.topology['AIMMeeCell'][self.last_cell_guid].remove(self.guid)
                while self.last_cell_guid in self.sim.topology['AIMMeeUE'][self.guid]:
                    self.sim.topology['AIMMeeUE'][self.guid].remove(self.last_cell_guid)
            # Add the UE to the current cell
            if self.guid not in self.sim.topology['AIMMeeCell'][self.current_cell_guid]:
                self.sim.topology['AIMMeeCell'][self.current_cell_guid].append(self.guid)
            # Update the UE's serving cell in the topology
            if self.current_cell_guid not in self.sim.topology['AIMMeeUE'][self.guid]:
                self.sim.topology['AIMMeeUE'][self.guid].append(self.current_cell_guid)
    
    def loop(s):
        ' Main loop of UE class '
        if s.verbosity>1:
            print(f'Main loop of UE[{s.i}] started')
            stdout.flush()
        while True:
            if s.f_callback is not None: s.f_callback(s,**s.f_callback_kwargs)
            s.update_cell_guid()
            s.update_ue_topology()
            s.send_rsrp_reports()
            s.send_subband_cqi_report()
            yield s.sim.env.timeout(s.reporting_interval)

# END class AIMMeeUE

class AIMMeeLogger(AIMM_Logger):
    """
    AIMMee Logger: Accesses the AIMM default logger via super().
    """
    id_iter = itertools_count()
    def __init__(self, *args, **kwargs):
        print('INIT of AIMMeeLogger')
        self.guid = id(self)
        self.idx = next(AIMMeeLogger.id_iter)
        self.label = f'{self.__class__.__name__}[{self.idx}]'
        super().__init__(*args, **kwargs)
# END class AIMMeeLogger


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


class MyLogger(AIMMeeLogger):
    def loop(s):
      while True:
        for cell in s.sim.cells:
          #if cell.i!=0: continue # cell[0] only
          for ue_i in cell.reports['cqi']:
            #if ue_i!=0: continue # UE[0] only
            rep=cell.reports['cqi'][ue_i]
            if not rep: continue
            xy= s.np_array_to_str(s.sim.UEs[ue_i].xyz[:2])
            cqi=s.np_array_to_str(cell.reports['cqi'][ue_i][1])
            tp= s.np_array_to_str(cell.reports['throughput_Mbps'][ue_i][1])
            s.f.write(f'{s.sim.env.now:.1f}\t{xy}\t{cqi}\t{tp}\n')
        yield s.sim.env.timeout(s.logging_interval)

def test_01(ncells=4,nues=9,n_subbands=2,until=10.0):
    sim=Sim(until=until)
    for i in range(ncells):
      sim.make_cell(n_subbands=n_subbands,MIMO_gain_dB=3.0,verbosity=0)
      cell=sim.cells[-1]
      sim.make_RadioAccessPoint(cell=cell)
      rap=sim.raps[-1]
      sim.make_RadioUnit(cell=cell, rap=rap, verbosity=0)
      ru=sim.rus[-1]
      sim.make_RemoteRadioHead(rap=rap, n_rf_ports=2, verbosity=0)
    sim.cells[0].set_xyz((500.0,500.0,20.0)) # fix cell[0]
    for i in range(nues):
      ue=sim.make_UE(verbosity=1)
      if 0==i: # force ue[0] to attach to cell[0]
        ue.set_xyz([501.0,502.0,2.0],verbose=True)
      ue.attach_to_nearest_cell()
    scenario=AIMM_Scenario(sim,verbosity=0)
    logger=MyLogger(sim,logging_interval=1.0)
    ric=AIMM_RIC(sim)
    sim.add_logger(logger)
    sim.add_scenario(scenario)
    sim.add_ric(ric)
    sim.confirm_exe()
    print('Exiting...')


if __name__=='__main__': 

    np.set_printoptions(precision=4,linewidth=200)

    test_01()