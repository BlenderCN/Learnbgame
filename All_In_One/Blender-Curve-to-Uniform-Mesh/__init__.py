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

if "bpy" in locals():
    import imp;
    imp.reload(bezierCurve)
    imp.reload(bezierSegmentIterator)
else:
    import bpy
    import curve_to_even_mesh
    import curve_to_even_mesh.bezierCurve
    import curve_to_even_mesh.bezierSegmentIterator
    from curve_to_even_mesh.bezierCurve import *
    from curve_to_even_mesh.bezierSegmentIterator import *

bl_info = {
    "name": "Curve to even mesh",
    "author": "Denis Declara",
    "version": (0, 2),
    "blender": (2, 5, 3),   # I am not so sure about the compatibility :(
    "api": 32411,
    "location": "Toolshelf > search > Curve to Uniform Mesh",
    "description": "This script converts bezier curves or text objects to a mesh",
    "warning": "Beta",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

"""
This script converts curves and text objects to an even mesh.
"""


import bpy
from bpy.props import *
import mathutils
from mathutils import Vector

# The destination array is defined as follows
# - Array of loops
#   - [verts, faces]
# The loop_coll parameter is a list of a set of points
# describing a polygon and the validity of each edge
def insertMeshLoop(loop_coll, destination):
    # Prepare the data to be added to blender

    # Extract the lists contained in loop_coll
    loop = loop_coll[0]
    valid_edges = loop_coll[1]

    # Find the first free vertex slot, it coincides with the
    # count of vertices
    firstVertexId = 0
    for l in destination:
        firstVertexId += len(l[0])
    curVertex = firstVertexId
    verts = []
    faces = []
    for i, point in enumerate(loop):
        verts.append([point.x, point.y, point.z])
        # Small trick to create edges, just make a face, containing
        # two times the same vertex
        if valid_edges[i]:
            faces.append([curVertex, curVertex + 1, curVertex])
        curVertex+=1
    # Fix the mesh, closing the last edge, but only if it is a valid one
    if len(loop) != 0 and valid_edges[-1]: faces[-1][1] = firstVertexId

    # Append to the destination array
    destination.append([verts, faces])

# This uses an array of loops, as described in the above method,
# and generates actual blender mesh
def createMesh(mesh, loops):
    verts = []
    faces = []
    # First of all let's flatten the array of loops
    for l in loops:
        verts.extend(l[0])
        faces.extend(l[1])

    # Add geometry to mesh object
    mesh.from_pydata(verts, [], faces)
    mesh.update()



###########################
#####   Main Method   #####
###########################

def main(context, obj, options):
    #options = [
    #    self.fillMesh,      #0
    #    self.lengthApp,     #1
    #    self.density,       #2
    #    self.offset,        #3
    #    self.beautifyIters, #4
    #    self.execscript]    #5

    # main vars
    fillMesh = options[0]
    lengthApp = options[1]
    density = options[2]
    offset = options[3]
    beautifyIters = options[4]
    if(options[5] == False): # If the execute checkbox is not checked leave the method
     return;

    loops = []

    originalName = obj.name
    #try:
    #    if ("uniform_" + originalName) in bpy.data.objects.keys():
    #        context.scene.unlink(bpy.data.objects["uniform_" + originalName])
    #        bpy.data.objects.remove(bpy.data.objects["uniform_" + originalName])
    #    if ("uniform_"+originalName) in bpy.data.meshes.keys():
    #        bpy.data.meshes.remove(bpy.data.meshes["uniform_" + originalName])
    #finally:
    #    print("Couldn't delete old object")

    #isFontObject = (obj.type == 'FONT')
    #if isFontObject:
    #    # Convert font objects into curves
    #    bpy.ops.object.select_all(action='DESELECT')
    #    obj.select = True
    #    context.scene.objects.active = obj
    #    bpy.ops.object.convert(target='CURVE', keep_original=True)
    #    obj = bpy.context.active_object

    # Deselect all of the objects in the scene
    bpy.ops.object.select_all(action='DESELECT')
    scene = context.scene
    splines = obj.data.splines.values()

    # create a mesh datablock
    mesh = bpy.data.meshes.new("uniform_"+originalName)

    # go through splines
    for spline in splines:
        # test if spline is a bezier curve, otherwise skip it
        # also test if the curve has one or no points skip it
        if spline.type == 'BEZIER' and len(spline.bezier_points) > 1:
        # Convert blender's bpy bezier class in to my own bezier class
            bezier = fromBlenderSpline(spline)
            # Sample the curve uniformly and store the points in ip
            ip = None
            if offset == 0.0:
                ip = bezier.toPointCloud(lengthApp, density)
            else:
                ip = bezier.toOfsettedPointCloud(offset, lengthApp, density)

            # Store the data locally, in the loops array, so that we
            # can add it when we are done
            insertMeshLoop(ip, loops)
    # Add geometry to mesh object
    createMesh(mesh, loops)

    # Create object and link it to the scene
    newMesh = bpy.data.objects.new("uniform_"+originalName, mesh)
    scene.objects.link(newMesh)
    newMesh.select = True
    scene.objects.active = newMesh
    newMesh.matrix_world = obj.matrix_world
    newMesh.data.show_all_edges = True

    # Remove double vertices
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.remove_doubles()

    # If the user decides to fill the mesh, fill it with the
    # internal operators
    if fillMesh == True:
     bpy.ops.mesh.fill()
     # Repeat the beautify fill a couple of times as it may not
     # yield a perfect result the first time
     for i in range(0, beautifyIters):
         bpy.ops.mesh.beautify_fill()
     # Quadrangulate the mesh using blender ops
     bpy.ops.mesh.tris_convert_to_quads()

    # Switch back to object mode
    bpy.ops.object.mode_set(mode = 'OBJECT')

    # create ne object and put into scene

    #if isFontObject == True:
    #    scene.objects.unlink(obj)

    return

###########################
##### Curves OPERATOR #####
###########################
class CURVE_OT_to_even_mesh(bpy.types.Operator):
    ''''''
    bl_label = "Convert Curve To Even Mesh"
    bl_idname = "curve.to_even_mesh"
    bl_description = "converts curve to an uniform mesh"
    bl_options = {'REGISTER', 'UNDO'}

    # Whetever or not to execute the modifier
    execscript = BoolProperty(name="Execute",
                              description="execute the modifier",
                              default=True)


    # Whetever or not to fill the mesh
    fillMesh = BoolProperty(name="Fill mesh",
                            description="fill the mesh",
                            default=False)

    # Precision (number of segments) of the length approximation
    lengthApp = IntProperty(name="Length approximation",
                            min=1, soft_min=1,
                            default=8,
                            description="precision of the length approximation")

    # Number of times to execute blender's beautify_fill
    beautifyIters = IntProperty(name="Beautify fill iterations",
                                min=1, soft_min=1,
                                default=5,
                                description="number of time to execute beautify fill on the mesh")

    # Amount of vertices per blender unit to compute
    density = FloatProperty(name="Density",
                            description="amount of vertices per 1 blender unit to compute",
                            min=0, soft_min=0,
                            default=32.0, precision=3)

    # Amount of vertices per blender unit to compute
    offset = FloatProperty(name="Curve offset",
                           description="Curve offset in blender units",
                           min=-100,
                           default=0.0, precision=3, max=100)

    # Cure object, where to get the data from
    #curveObj = PointerProperty(name="Curve", type=bpy.types.Curve)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'execscript', icon="SCRIPTWIN")
        col.prop(self, 'fillMesh')
        col.prop(self, 'density')
        col.prop(self, 'beautifyIters')
        col.prop(self, 'offset')
        col.prop(self, 'lengthApp')
        #col.prop(self, 'curveObj')

    ## Check for curve or text object
    @classmethod
    def poll(cls, context):
        print("poll")
        obj = context.object
        #if (obj and (obj.type == 'CURVE' or obj.type == 'FONT')):
        #    return True
        if obj and obj.type == 'MESH' and obj.name.startswith("uniform_"):
            if obj.name[8:] in bpy.context.scene.objects:
                if bpy.context.scene.objects[obj.name[8:]].type == 'CURVE' or bpy.context.scene.objects[obj.name[8:]].type == 'FONT':
                     return True
        return bpy.context.object.type == 'CURVE';

    ## execute
    def execute(self, context):

        options = [
            self.fillMesh,      #0
            self.lengthApp,     #1
            self.density,       #2
            self.offset,        #3
            self.beautifyIters, #4
            self.execscript]    #5

        bpy.context.user_preferences.edit.use_global_undo = False

        # Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        # Grab the current object
        obj = context.active_object
        if obj.type == 'MESH':
            tempobj = obj
            obj = bpy.context.scene.objects[obj.name[8:]]
            bpy.context.scene.objects.active = obj;
            bpy.context.scene.objects.unlink(tempobj)

        main(context, obj, options)

        bpy.context.user_preferences.edit.use_global_undo = True

        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

# ******************************************** #
#               REGISTRATION                   #
# ******************************************** #
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
