import sys
from pathlib import Path
# Resolve the parent folder and add to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from AIMMee import Sim

def test_AIMMee_00():
    sim=Sim()
    sim.make_cell()
    sim.make_UE().attach_to_strongest_cell_simple_pathloss_model()
    sim.run(until=100.0)

if __name__ == '__main__':
    test_AIMMee_00()
