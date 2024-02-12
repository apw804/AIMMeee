import sys
from pathlib import Path
# Resolve the parent folder and add to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from AIMMee import Sim, AIMMeeLogger

def test_AIMMee_01():
    sim=Sim()
    cell=sim.make_cell()
    ues=[sim.make_UE().attach(cell) for i in range(4)]
    sim.add_logger(AIMMeeLogger(sim,logging_interval=10))
    sim.run(until=100)

if __name__ == '__main__':
    test_AIMMee_01()