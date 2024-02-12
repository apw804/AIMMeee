import sys
from pathlib import Path
# Resolve the parent folder and add to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from AIMMee import Sim, AIMM_MME, AIMM_Scenario, AIMM_Logger, np_array_to_str 
from numpy.random import standard_normal

class Test03Scenario(AIMM_Scenario):
  def loop(self,interval=0.1):
    while True:
      for ue in self.sim.UEs: ue.xyz[:2]+=standard_normal(2)
      yield self.sim.wait(interval)

class Test03Logger(AIMM_Logger):
  def loop(self):
    self.f.write('#time\tcell\tUE\tx\ty\tthroughput\n')
    while True:
      for cell in self.sim.cells:
        for ue_i in cell.reports['cqi']:
          xy=self.sim.get_UE_position(ue_i)[:2]
          tp=np_array_to_str(cell.get_UE_throughput(ue_i))
          self.f.write(f't={self.sim.env.now:.1f}\tcell={cell.i}\tUE={ue_i}\tx={xy[0]:.0f}\ty={xy[1]:.0f}\ttp={tp}Mb/s\n')
      yield self.sim.wait(self.logging_interval)

def test_AIMMee_03():
  sim=Sim()
  for i in range(4): sim.make_cell()
  for i in range(8): sim.make_UE().attach_to_nearest_cell()
  sim.add_logger(Test03Logger(sim,logging_interval=1))
  sim.add_scenario(Test03Scenario(sim))
  sim.add_MME(AIMM_MME(sim,interval=10.0))
  sim.run(until=10)

if __name__ == '__main__':
    test_AIMMee_03()