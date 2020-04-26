# ##### BEGIN MIT LICENSE BLOCK #####
# MIT License
# 
# Copyright (c) 2018 Insma Software
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ##### END MIT LICENSE BLOCK #####

# ----------------------------------------------------------
# Author: Maciej Klemarczyk (mklemarczyk)
# ----------------------------------------------------------
import bpy
from bpy.types import Operator, PropertyGroup, Object, Panel
from bpy.props import FloatProperty, CollectionProperty
from .archlab_utils import *
from .archlab_utils_mesh_generator import *

# ------------------------------------------------------------------------------
# Create main object for the cube.
# ------------------------------------------------------------------------------
def create_cube(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False

    # we create main object and mesh for cube
    cubemesh = bpy.data.meshes.new("Cube")
    cubeobject = bpy.data.objects.new("Cube", cubemesh)
    cubeobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(cubeobject)
    cubeobject.ArchLabCubeGenerator.add()

    cubeobject.ArchLabCubeGenerator[0].cube_height = self.cube_height
    cubeobject.ArchLabCubeGenerator[0].cube_width = self.cube_width
    cubeobject.ArchLabCubeGenerator[0].cube_depth = self.cube_depth

    # we shape the mesh.
    shape_cube_mesh(cubeobject, cubemesh)

    # we select, and activate, main object for the cube.
    cubeobject.select = True
    bpy.context.scene.objects.active = cubeobject

# ------------------------------------------------------------------------------
# Shapes mesh the cube mesh
# ------------------------------------------------------------------------------
def shape_cube_mesh(mycube, tmp_mesh, update=False):
    cp = mycube.ArchLabCubeGenerator[0]  # "cp" means "cube properties".
    # Create cube mesh data
    update_cube_mesh_data(tmp_mesh, cp.cube_width, cp.cube_height, cp.cube_depth)
    mycube.data = tmp_mesh

    remove_doubles(mycube)
    set_normals(mycube)

    # deactivate others
    for o in bpy.data.objects:
        if o.select is True and o.name != mycube.name:
            o.select = False

# ------------------------------------------------------------------------------
# Creates cube mesh data.
# ------------------------------------------------------------------------------
def update_cube_mesh_data(mymesh, width, height, depth):
    (myvertices, myedges, myfaces) = generate_cube_mesh_data(width, height, depth)

    mymesh.from_pydata(myvertices, myedges, myfaces)
    mymesh.update(calc_edges=True)

# ------------------------------------------------------------------------------
# Update cube mesh.
# ------------------------------------------------------------------------------
def update_cube(self, context):
    # When we update, the active object is the main object of the cube.
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that cube object to not delete it.
    o.select = False
    # and we create a new mesh for the cube:
    tmp_mesh = bpy.data.meshes.new("temp")
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally we shape the main mesh again,
    shape_cube_mesh(o, tmp_mesh, True)
    o.data = tmp_mesh
    # Remove data (mesh of active object),
    bpy.data.meshes.remove(oldmesh)
    tmp_mesh.name = oldname
    # and select, and activate, the main object of the cube.
    o.select = True
    bpy.context.scene.objects.active = o

# -----------------------------------------------------
# Property definition creator
# -----------------------------------------------------
def cube_height_property(callback=None):
    return FloatProperty(
            name='Height',
            soft_min=0.001,
            default=1.0, precision=3, unit = 'LENGTH',
            description='Cube height', update=callback,
            )

def cube_width_property(callback=None):
    return FloatProperty(
            name='Width',
            soft_min=0.001,
            default=1.0, precision=3, unit = 'LENGTH',
            description='Cube width', update=callback,
            )

def cube_depth_property(callback=None):
    return FloatProperty(
            name='Depth',
            soft_min=0.001,
            default=1.0, precision=3, unit = 'LENGTH',
            description='Cube depth', update=callback,
            )

# ------------------------------------------------------------------
# Define property group class to create or modify a cubes.
# ------------------------------------------------------------------
class ArchLabCubeProperties(PropertyGroup):
    cube_height = cube_height_property(callback=update_cube)
    cube_width = cube_width_property(callback=update_cube)
    cube_depth = cube_depth_property(callback=update_cube)

bpy.utils.register_class(ArchLabCubeProperties)
Object.ArchLabCubeGenerator = CollectionProperty(type=ArchLabCubeProperties)

# ------------------------------------------------------------------
# Define panel class to modify cubes.
# ------------------------------------------------------------------
class ArchLabCubeGeneratorPanel(Panel):
    bl_idname = "OBJECT_PT_cube_generator"
    bl_label = "Cube"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'ArchLab'

    # -----------------------------------------------------
    # Verify if visible
    # -----------------------------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        act_op = context.active_operator
        if o is None:
            return False
        if 'ArchLabCubeGenerator' not in o:
            return False
        if act_op is not None and act_op.bl_idname.endswith('archlab_cube'):
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'ArchLabCubeGenerator', this panel is not created.
        try:
            if 'ArchLabCubeGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            cube = o.ArchLabCubeGenerator[0]
            row = layout.row()
            row.prop(cube, 'cube_width')
            row = layout.row()
            row.prop(cube, 'cube_height')
            row = layout.row()
            row.prop(cube, 'cube_depth')

# ------------------------------------------------------------------
# Define operator class to create cubes
# ------------------------------------------------------------------
class ArchLabCube(Operator):
    bl_idname = "mesh.archlab_cube"
    bl_label = "Add Cube"
    bl_description = "Generate cube primitive mesh"
    bl_category = 'ArchLab'
    bl_options = {'REGISTER', 'UNDO'}

    # preset
    cube_height = cube_height_property()
    cube_width = cube_width_property()
    cube_depth = cube_depth_property()

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            row = layout.row()
            row.prop(self, 'cube_width')
            row = layout.row()
            row.prop(self, 'cube_height')
            row = layout.row()
            row.prop(self, 'cube_depth')
        else:
            row = layout.row()
            row.label("Warning: Operator does not work in local view mode", icon='ERROR')

    # -----------------------------------------------------
    # Execute
    # -----------------------------------------------------
    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            space = bpy.context.space_data
            if not space.local_view:
                create_cube(self, context)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "ArchLab: Option only valid in global view mode")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "ArchLab: Option only valid in Object mode")
            return {'CANCELLED'}
