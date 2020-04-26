#!/usr/bin/python3
# -*- coding: utf-8 -*-

import m3
import sys


structureName = sys.argv[1]
structureVersion = int(sys.argv[2])

structureDescription = m3.structures[structureName].getVersion(structureVersion)
if structureDescription == None:
    raise Exception("The structure %s hasn't been defined in version %d" % (structureName, structureVersion))
offset = 0
for field in structureDescription.fields:
    print("%s: %s" % (offset, field.name))
    offset += field.size

