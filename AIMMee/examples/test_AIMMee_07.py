import sys
from pathlib import Path
# Resolve the parent folder and add to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from numpy.random import standard_normal
from AIMMee import Sim, AIMM_Scenario, AIMMeeLogger, AIMM_MME, np_array_to_str


class Test07Scenario(AIMM_Scenario):
  def loop(self,interval=10):
    while True:
      for ue in self.sim.UEs: ue.xyz[:2]+=20*standard_normal(2)
      yield self.sim.wait(interval)

class Test07Logger(AIMMeeLogger):
  # throughput of UE[0], UE[0] position, serving cell index
  def loop(self):
    while True:
      sc=self.sim.UEs[0].serving_cell.i
      tp=self.sim.cells[sc].get_UE_throughput(0)
      xy0=np_array_to_str(self.sim.UEs[0].xyz[:2])
      self.f.write(f'{self.sim.env.now:.2f}\t{tp:.4f}\t{xy0}\t{sc}\n')
      yield self.sim.wait(self.logging_interval)

def test_AIMMee_07(n_subbands=1):
  sim=Sim()
  for i in range(9): # macros
    sim.make_cell(xyz=(500.0*(i//3),500.0*(i%3),20.0),power_dBm=30.0,n_subbands=n_subbands)
  for i in range(10): # small cells
    sim.make_cell(power_dBm=10.0,n_subbands=n_subbands)
  for i in range(20):
    sim.make_UE().attach_to_strongest_cell_simple_pathloss_model()
  sim.UEs[0].set_xyz([500.0,500.0,2.0])
  for UE in sim.UEs: UE.attach_to_strongest_cell_simple_pathloss_model()
  sim.add_logger(Test07Logger(sim,logging_interval=1.0))
  sim.add_scenario(Test07Scenario(sim))
  sim.add_MME(AIMM_MME(sim,verbosity=0,interval=50.0))
  sim.run(until=2000)

if __name__ == '__main__':
    test_AIMMee_07()