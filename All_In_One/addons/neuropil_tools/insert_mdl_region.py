#!/usr/bin/env python

import sys

if (len(sys.argv)<3):
  sys.stderr.write('\nUsage: %s mdl_geom_filename mdl_region_filename \n' % (sys.argv[0]))
  sys.stderr.write('           Insert mdl region into mdl geometry\n')
  sys.stderr.write('           Output is written to stdout\n\n')
  exit(1)

mdl_geom_filename = sys.argv[1]
mdl_region_filename = sys.argv[2]


mdl_geom = open(mdl_geom_filename)

# Jump to end of file
mdl_geom.seek(0, 2)
pos = mdl_geom.tell()

# Look for last brace starting at end of file
while mdl_geom.read(1) != '}':
  pos -= 1
  mdl_geom.seek(pos)

# Jump to beginning of file
mdl_geom.seek(0)

# Write mdl geom file up to last brace
sys.stdout.write(mdl_geom.read(pos))
mdl_geom.close()

# Insert mdl region file in output 
mdl_region = open(mdl_region_filename)
sys.stdout.write(mdl_region.read())
mdl_region.close()

# Write terminating brace after region
sys.stdout.write('}\n')


