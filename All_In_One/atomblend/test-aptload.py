import numpy as np
from aptread.aptload import APData

pospath = "./data/R04.pos"
rngpath = "./data/R04.rng"

data = APData(pospath, rngpath)
print("POS:", data.rng._pos)
print("POS map:", data.rng._posmap)
