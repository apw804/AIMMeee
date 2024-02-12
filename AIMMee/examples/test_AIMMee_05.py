import sys
from pathlib import Path
# Resolve the parent folder and add to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from numpy.random import standard_normal
from math import cos,sin,pi
from AIMMee import Sim, AIMM_Scenario, AIMMeeLogger, to_dB


class Test05Scenario(AIMM_Scenario):
  # move the UE around a circle of specified radius, period T seconds
  def loop(self,interval=1.0,radius=100.0,T=100.0):
        while True:
            t=self.sim.env.now
            for ue in self.sim.UEs:
                ue.xyz[:2]=radius*cos(2*pi*t/T),radius*sin(2*pi*t/T)
            yield self.sim.wait(interval)

class Test05Logger(AIMMeeLogger):
  def loop(self,ue_i=0):
    ' log for UE[ue_i] only, from reports sent to Cell[0]. '
    cell=self.sim.cells[0]
    UE=self.sim.UEs[ue_i]
    while True:
      tm=self.sim.env.now              # current time
      xy=UE.get_xyz()[:2]              # current UE position
      tp=cell.get_UE_throughput(ue_i)  # current UE throughput
      self.f.write(f'{tm:.1f}\t{xy[0]:.0f}\t{xy[1]:.0f}\t{tp}\n')
      yield self.sim.wait(self.logging_interval)

def test_AIMMee_05():
  sim=Sim()
  pattern=lambda angle: 10.0+to_dB(abs(cos(0.5*angle*pi/180.0)))
  cell0=sim.make_cell(xyz=[  0.0,0.0,20.0],pattern=pattern)
  cell1=sim.make_cell(xyz=[200.0,0.0,20.0])
  ue=sim.make_UE(xyz=[100.0,0.0,2.0])
  ue.attach(cell0)
  sim.add_logger(Test05Logger(sim,logging_interval=5))
  sim.add_scenario(Test05Scenario(sim))
  sim.run(until=500)


if __name__ == '__main__':
    test_AIMMee_05()