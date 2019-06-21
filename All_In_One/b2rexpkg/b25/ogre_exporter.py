"""
Classes managing the ogre tools from blender 2.5
"""

import os
import bpy

# hooks to be able to export uuids on the fly
import b2rexpkg.b25.uuidhooks

# export meshes
class OgreExporter(object):
    def export(self, path, pack_name, offset):
        """
        Export whole scene, including scene info and mesh info.
        """
        bpy.ops.ogre.export(filepath=os.path.join(path, pack_name),
                           EX_SWAP_MODE='-x z y')


