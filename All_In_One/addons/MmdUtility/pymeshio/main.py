# coding: utf-8
"""
"""


import sys
import os
import io
from .pmd import reader
from .pmx import writer
from . import converter


def pmd_to_pmx():
    if len(sys.argv)<3:
        print("usage: %s {input pmd_file} {out pmx_file}" % os.path.basename(sys.argv[0]))
        sys.exit()
    pmd=reader.read_from_file(sys.argv[1])
    pmx=converter.pmd_to_pmx(pmd)
    writer.write(io.open(sys.argv[2], "wb"), pmx)

def pmd_diff():
    if len(sys.argv)<3:
        print("sage: %s {pmd_file} {pmd_file}" % os.path.basename(sys.argv[0]))
        sys.exit()
    lhs=reader.read_from_file(sys.argv[1])
    rhs=reader.read_from_file(sys.argv[2])
    lhs.diff(rhs)

def pmd_validator():
    if len(sys.argv)==1:
        print("sage: %s {input pmd_file}" % os.path.basename(sys.argv[0]))
        sys.exit()
    pmd=reader.read_from_file(sys.argv[1])
    print("%s(%s)" % (pmd.name.decode('cp932'), pmd.english_name.decode('cp932')))
    print("vertices: %d" % len(pmd.vertices))
    print("indices: %d" % len(pmd.indices))
    print("materials: %d" % len(pmd.materials))
    print("bones: %d" % len(pmd.bones))
    print("ik_list: %d" % len(pmd.ik_list))
    print("morphs: %d" % len(pmd.morphs))
    print("morph_indices: %d" % len(pmd.morph_indices))
    print("bone_group_list: %d" % len(pmd.bone_group_list))
    print("bone_display_list: %d" % len(pmd.bone_group_list))
    print("toon_textures: %d" % len(pmd.toon_textures))
    print("rigidbodies: %d" % len(pmd.rigidbodies))
    print("joints: %d" % len(pmd.joints))

