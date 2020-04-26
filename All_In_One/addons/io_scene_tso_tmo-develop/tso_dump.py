#!/usr/bin/env python

import os
from io_scene_tso_tmo.io.tso import TSOFile

def dump_tso(tso):
	for mesh in tso.meshes:
		print("mesh name:{}".format(len(mesh.name)))
		for sub in mesh.sub_meshes:
			print("  sub spec:{} #bone_indices:{} #vertices:{}".format(sub.spec, len(sub.bone_indices), len(sub.vertices)))

def dump_tsofile(source_file):
	tso = TSOFile()
	print("tso load file:{}".format(source_file))
	tso.load(source_file)
	dump_tso(tso)

if __name__ == "__main__":
	source_file = os.path.join(os.path.expanduser('~'), "resources/mod1.tso")
	dump_tsofile(source_file)

	source_file = "/Applications/blender.app/blend1.tso"
	dump_tsofile(source_file)
