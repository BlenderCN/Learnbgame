# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Import Pointcache Format (.pc2)",
    "author": "Jasper van Nieuwenhuizen, Ivo Grigull, Matt Ebb,"\
              " Bill L. Nieuwendorp",
    "version": (0, 5),
    "blender": (2, 5, 8),
    "location": "File > Import > Pointcache (.pc2)",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/PC2_Pointcache_import",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=28056&group_id=153&atid=467",
    "category": "Learnbgame",
}


import bpy
from bpy.props import (StringProperty,
                       IntProperty,
                       )
from bpy_extras.io_utils import ImportHelper
from struct import unpack


def pc2_import(filepath, ob, scene, PREF_OFFSET=0, PREF_JUMP=1):

    print('\n\nimporting pointcache "%s"' % filepath)

    bpy.ops.object.mode_set(mode='OBJECT')

    file = open(filepath, 'rb')

    # Read info from the file header
    headerFormat = '<12ciiffi'
    header = unpack(headerFormat, file.read(32))

    #fileVersion = header[12]
    numPoints = header[13]
    startFrame = int(header[14])
    sampleRate = header[15]
    numSamples = header[16]

    print('\tnumPoints:%d startFrame:%d sampleRate:%d numSamples:%d'
        % (numPoints, startFrame, sampleRate, numSamples))

    # If target object doesn't have Basis shape key, create it.
    try:
        len(ob.data.shape_keys.key_blocks)
    except:
        ob.shape_key_add('Basis')
        ob.data.update()

    scene.frame_current = startFrame + PREF_OFFSET

    def updateMesh(ob, fr):

        # Insert new shape key.
        #new_shapekey =
        ob.shape_key_add('frame_%.4d' % fr)
        #new_shapekey_name = new_shapekey.name

        index = len(ob.data.shape_keys.key_blocks) - 1
        ob.active_shape_key_index = index

        shapeKeys = ob.data.shape_keys
        verts = shapeKeys.key_blocks[index].data

        for v in verts:
            # 12 is the size of 3 floats
            x, y, z = unpack('<3f', file.read(12))
            v.co[:] = x, y, z

        # Insert keyframes
        scene.frame_current -= 1
        shapeKeys.key_blocks[index].value = 0.0
        shapeKeys.key_blocks[index].keyframe_insert('value')

        scene.frame_current += 1
        shapeKeys.key_blocks[index].value = 1.0
        shapeKeys.key_blocks[index].keyframe_insert('value')

        scene.frame_current += 1
        shapeKeys.key_blocks[index].value = 0.0
        shapeKeys.key_blocks[index].keyframe_insert('value')

        ob.data.update()

    for i in range(numSamples):
        updateMesh(ob, i)

    scene.frame_current = startFrame + PREF_OFFSET

    print('done')


# Import operator
class Import_pc2(bpy.types.Operator, ImportHelper):
    '''Import .pc2 pointcache to shape keys.'''
    bl_idname = 'import_shape.pc2'
    bl_label = 'Import pointcache (.pc2)'

    # Get first scene to get min and max properties for frames.
    minframe = 0
    maxframe = 300000

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    filepath = StringProperty(
            name="File Path",
            description="File path used for importing the PC2 file",
            maxlen=1024,
            )
    frameOffset = IntProperty(
            name="Frame offset",
            description="Amount of frames to offset the cache animation",
            min=minframe, max=maxframe, default=0,
            )
    filename_ext = ".pc2"
    filter_glob = StringProperty(default="*.pc2", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH')

    def execute(self, context):
        if not self.properties.filepath:
            raise Exception("filename not set")

        pc2_import(self.properties.filepath, context.active_object,
                context.scene, self.properties.frameOffset)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Register script

def menu_func(self, context):
    self.layout.operator(Import_pc2.bl_idname, text='Pointcache (.pc2)')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
