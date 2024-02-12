import sys
from pathlib import Path
# Resolve the parent folder and add to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from numpy.random import standard_normal
from AIMMee import Sim 





if __name__ == '__main__':
    test_AIMMee_