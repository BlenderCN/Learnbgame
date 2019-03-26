#############################################################################
#                                                                           #
# CSC 472 Project                                                           #
#                                                                           #
# Import Image as Point Cloud                                               #
#                                                                           #
# Author: Haoyang Li & Stefan Fisher                                        #
#                                                                           #
# Description: Import any image type into Blender as a point cloud object.  #
#                                                                           #
# Options: 1. User defined scale factors in blender unit                    #
#          2. User controlled point reduce function                         #
#                                                                           #
# Reference: Blender script template -- addon_add_object.py                 #
#            Adjusting image pixels internally in Blender with bpy          #
#               http://goo.gl/FFxCRw                                        #
#                                                                           #
#############################################################################

bl_info = {
    "name": "Image to Point Cloud",
    "author": "Hao & Stef",
    "version": (0, 1),
    "blender": (2, 65, 0),
    "location": "View3D > Add > Mesh > Image to Point Cloud",
    "description": "Adds a new Point Cloud Mesh",
    "warning": "Not efficient to process image with more than 62500 pixels",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

import bpy
from bpy.types import Operator
from bpy_extras.object_utils import object_data_add
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector
import os
import collections
from bpy.props import (FloatVectorProperty,
                       StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       CollectionProperty,
                       )

# Load an input image and create a Point Cloud object
def load_pc(self, context, filepath):
    import time #Debug timer
    
    # Debug timmer
    t = time.time()
    
    # Get object name from the file name
    pc_name = bpy.path.display_name_from_filepath(filepath)
    
    # Load image file into blender
    D = bpy.data
    im = D.images.load(filepath)
    
    # Assign scale factors
    scale_x = self.scale.x
    scale_y = self.scale.y
    scale_z = self.scale.z
    
    # Enable/Disable point reduce step
    rp = self.reduce_point
    
    # Scale down the image size in pixels
    resX_len = len(str(im.size[0]))
    resY_len = len(str(im.size[1]))
    #scale_factor = int((resX_len + resY_len)/2 - 3)
    #if (resX_len > 2 or resY_len > 2):
    #    scale_down = 10**scale_factor
    #    scale_z *= 10*scale_down
    #else:
    #    scale_down = 1
    #    scale_z *= 10

    # Calculate Point Cloud size
    width = int(im.size[0])
    height = int(im.size[1])
    
    # Scale the height value according to the size of the Point Cloud
    scale_z *= 2**((resX_len + resY_len)/2 + 1)
    
    # Calculate height value (z coordinate) for each vertex vector
    num_p = len(im.pixels)
    mask = im.pixels
    gray = []
    for px in range(0, num_p-1, 4):
        gray.extend([(mask[px] + mask[px+1] + mask[px+2]) / 3])
    
    # Construct a vertex array
    verts = []
    for y in range(height):
        for x in range(width):
            # Check if Reduce Point needed
            if rp == False:
                create_verts(scale_x, scale_y, scale_z, x, y, gray, width, verts)
            else:
                # If the point is on the edge of point cloud, add to verts[] array
                if ((x == 0 or x == width -1) or ((y == 0) or(y == height -1))):
                    create_verts(scale_x, scale_y, scale_z, x, y, gray, width, verts)
                # If the point's height value is not equal to any of its surround neigbours,
                # add it to verts[] array
                elif (  check(gray[x + (y)*width], gray[x-1 + (y-1)*width])
                    or check(gray[x + (y)*width], gray[x + (y-1)*width])
                    or check(gray[x + (y)*width], gray[x+1 + (y-1)*width])
                    or check(gray[x + (y)*width], gray[x+1 + (y)*width])
                    or check(gray[x + (y)*width], gray[x+1 + (y+1)*width])
                    or check(gray[x + (y)*width], gray[x + (y+1)*width])
                    or check(gray[x + (y)*width], gray[x-1 + (y+1)*width])
                    or check(gray[x + (y)*width], gray[x-1 + (y)*width])
                    ):
                        create_verts(scale_x, scale_y, scale_z, x, y, gray, width, verts)

    # Construct the mesh object
    mesh = bpy.data.meshes.new(name=pc_name)
    mesh.from_pydata(verts, [], [])
    
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=None)
    
    # Debug info
    message = '\nSuccessfully imported %r in %.3f sec' % (filepath, time.time() - t)
    self.report({'INFO'}, message)
    print(message)

# Add vector to verts[] array
def create_verts(scale_x, scale_y, scale_z, x, y, gray_array, width, verts):
    verts.extend([Vector((x * scale_x, y * scale_y, gray_array[x + y*width] * scale_z))])

# Check if two floating point are almost the same
def check(a, b):
    if abs(a-b) > 0.01:
        return True
    else:
        return False

# Main
class OBJECT_OT_add_object(Operator, ImportHelper):
    """Create a new Point Cloud Object"""
    bl_idname = "mesh.point_cloud"
    bl_label = "Add Point Cloud Object"
    bl_options = {'REGISTER', 'UNDO'}
    
    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the Image file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty()

    # Show only images/videos, and directories!
    filter_image = BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    filter_folder = BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    filter_glob = StringProperty(default="", options={'HIDDEN', 'SKIP_SAVE'})
    
    # User defined scale factors
    scale = FloatVectorProperty(
    			name="scale",
    			default=(1.0, 1.0, 1.0),
    			subtype='TRANSLATION',
    			description="scaling",
    			)
    
    # Enable/Disable point reduce step
    reduce_point = BoolProperty(
                        name="Reduce Points", 
                        description="Enable to reduce imported points", 
                        default=False, 
                        options={'ANIMATABLE'}, 
                        subtype='NONE', 
                        update=None, 
                        get=None, 
                        set=None)
    
    def execute(self, context):
        # Get images' paths
        paths = [os.path.join(self.directory, name.name)
                 for name in self.files]
        if not paths:
            paths.append(self.filepath)
        for path in paths:
            # load each image
            load_pc(self, context, path)
            print(path)
        return {'FINISHED'}

# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Add Point Cloud",
        icon='MESH_DATA')


# This allows you to right click on a button and link to the manual
def add_object_manual_map():
    url_manual_prefix = "http://wiki.blender.org/index.php/Doc:2.6/Manual/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "Modeling/Objects"),
        )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()
