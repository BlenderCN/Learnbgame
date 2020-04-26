from posload import POS

path = "../data/R04.pos"

posfile = POS(path)
print(len(posfile))
print(posfile.xyz[10:15])
print(posfile.mc[10:15])
