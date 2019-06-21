# Javarandom slime Python-version test harness.

from . import javarandom

rnd = javarandom.Random

def isSlimeSpawn(worldSeed, xPos, zPos):
	rnd = javarandom.Random(worldSeed + jlong(xPos * xPos * 0x4c1906) + jlong(xPos * 0x5ac0db) + jlong(zPos * zPos) * 0x4307a7 + jlong(zPos * 0x5f24f) ^ 0x3ad8025f)
	return rnd.nextInt(10) == 0

#Totally crucial!
def jlong(i):
	# Python and Java don't agree on how ints work.
	# Python 3 in particular treats everything as long.
	#The seed A term in the RNG was wrong, before...
	#This converts the unsigned generated int into a signed int if necessary.
	i = (i & 0xffffffff)	#vital!

	if i & (1 << 31):
		i -= (1 << 32)

	return i


if __name__ == '__main__':
	worldseed = 4784223057510287643	#Afarundria's seed.

#	for z in range(64):
#		for x in range(64):
#			isSlime = isSlimeSpawn(worldseed,x,z)
#			print("[%d,%d: %d]" % (x,z,isSlime), end="\r\n")


#	#write out all the seeds the above line of code would generate!!
#	for z in range(64):
#		for x in range(64):
#			seeda = jlong(x * x * 0x4c1906)	# BASTARD OF A 2's COMPLEMENT!
#			seedb = jlong(x * 0x5ac0db)
#			seedc = jlong(z * z) * 0x4307a7
#			seedd = jlong(z * 0x5f24f) ^ 0x3ad8025f
#			
#			seeder = (worldseed + seeda + seedb + seedc + seedd)
#			#The seed line is INCORRECT!!
#			# Here's the exact line of Java I'm trying to replicate:
#			# Random rnd = new Random(seed + (long) (xPosition * xPosition * 0x4c1906) + (long) (xPosition * 0x5ac0db) + (long) (zPosition * zPosition) * 0x4307a7L + (long) (zPosition * 0x5f24f) ^ 0x3ad8025f);

#			print("[%d,%d: %d] {%d,%d,%d,%d}" % (x,z,seeder,seeda,seedb,seedc,seedd), end="\r\n")