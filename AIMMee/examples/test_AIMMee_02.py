import sys
from pathlib import Path
# Resolve the parent folder and add to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from AIMMee import Sim, AIMM_Logger, AIMM_MME, AIMM_Scenario
from numpy.random import standard_normal

class Test02Scenario(AIMM_Scenario):
  def loop(self,interval=0.1):
    while True:
      for ue in self.sim.UEs: ue.xyz[:2]+=standard_normal(2)
      yield self.sim.wait(interval)

def test_AIMMee_02():
  sim=Sim()
  cell=sim.make_cell()
  for i in range(4): sim.make_UE().attach(cell)
  sim.add_logger(AIMM_Logger(sim,logging_interval=10))
  sim.add_scenario(Test02Scenario(sim))
  sim.add_MME(AIMM_MME(sim,interval=10.0))
  sim.run(until=500)

if __name__ == '__main__':
    test_AIMMee_02()