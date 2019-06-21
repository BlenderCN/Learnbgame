from rngload import ORNLRNG
from posload import POS

rngpath = "../data/R04.rng"
pospath = "../data/R04.pos"

rngfile = ORNLRNG(rngpath)
print("Ranges:", rngfile.rangelist)
print("Atoms: ", rngfile.atomlist)
print("Ions:  ", rngfile.ionlist)
print("N ranges:", rngfile.nranges)
print("N atoms: ",  rngfile.natoms)
print()
print("DICTS")
print("Ranges:", rngfile._ranges)
print("Atoms: ", rngfile._atoms)
print("Ions:  ", rngfile._ions)

print()
posfile = POS(pospath)
print("Loading posfile")
rngfile.loadpos(posfile)
print("POS:    ", rngfile._pos)
print("POS map:", rngfile._posmap)

print()
ION = 2
ionname = rngfile.ionlist[ION]
print("Getting points for ion", ionname)
ionpoints = rngfile.getion(ionname)
print("Length", len(ionpoints))
print(ionpoints[0:5])

print()
ATOM = 1
atomname = rngfile.atomlist[ATOM]
print("Getting points for atom", atomname)
atompoints = rngfile.getatom(atomname)
print("Length", len(atompoints))
print(atompoints[0:5])
