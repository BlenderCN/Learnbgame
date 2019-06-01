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

# ------------------------------------------------------------------------------
# Create main object for the wall.
# ------------------------------------------------------------------------------
def create_wall(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False

    # we create main object and mesh for wall
    wallmesh = bpy.data.meshes.new("Wall")
    wallobject = bpy.data.objects.new("Wall", wallmesh)
    wallobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(wallobject)
    wallobject.ArchLabWallGenerator.add()

    wallobject.ArchLabWallGenerator[0].wall_height = self.wall_height
    wallobject.ArchLabWallGenerator[0].wall_width = self.wall_width
    wallobject.ArchLabWallGenerator[0].wall_depth = self.wall_depth

    # we shape the mesh.
    shape_wall_mesh(wallobject, wallmesh)

    # we select, and activate, main object for the wall.
    wallobject.select = True
    bpy.context.scene.objects.active = wallobject

# ------------------------------------------------------------------------------
# Shapes mesh and creates modifier solidify (the modifier, only the first time).
# ------------------------------------------------------------------------------
def shape_wall_mesh(mywall, tmp_mesh, update=False):
    pp = mywall.ArchLabWallGenerator[0]  # "pp" means "wall properties".
    # Create wall mesh data
    update_wall_mesh_data(tmp_mesh, pp.wall_width, pp.wall_height)
    mywall.data = tmp_mesh

    remove_doubles(mywall)
    set_normals(mywall)

    if pp.wall_depth > 0.0:
        if update is False or is_solidify(mywall) is False:
            set_modifier_solidify(mywall, pp.wall_depth)
        else:
            for mod in mywall.modifiers:
                if mod.type == 'SOLIDIFY':
                    mod.thickness = pp.wall_depth
        # Move to Top SOLIDIFY
        movetotopsolidify(mywall)

    else:  # clear not used SOLIDIFY
        for mod in mywall.modifiers:
            if mod.type == 'SOLIDIFY':
                mywall.modifiers.remove(mod)

    # deactivate others
    for o in bpy.data.objects:
        if o.select is True and o.name != mywall.name:
            o.select = False

# ------------------------------------------------------------------------------
# Creates wall mesh data.
# ------------------------------------------------------------------------------
def update_wall_mesh_data(mymesh, width, height):
    sizew = width
    sizez = height
    posw = width
    posz = height

    myvertices = [(0.0, 0.0, 0.0), (0.0, 0.0, posz),]
    myvertices.extend([(posw, 0.0, 0.0), (posw, 0.0, posz)])
    myfaces = [(0, 1, 3, 2)]

    mymesh.from_pydata(myvertices, [], myfaces)
    mymesh.update(calc_edges=True)

# ------------------------------------------------------------------------------
# Update wall mesh.
# ------------------------------------------------------------------------------
def update_wall(self, context):
    # When we update, the active object is the main object of the wall.
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that wall object to not delete it.
    o.select = False
    # and we create a new mesh for the wall:
    tmp_mesh = bpy.data.meshes.new("temp")
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally we shape the main mesh again,
    shape_wall_mesh(o, tmp_mesh, True)
    o.data = tmp_mesh
    # Remove data (mesh of active object),
    bpy.data.meshes.remove(oldmesh)
    tmp_mesh.name = oldname
    # and select, and activate, the main object of the wall.
    o.select = True
    bpy.context.scene.objects.active = o

# -----------------------------------------------------
# Verify if solidify exist
# -----------------------------------------------------
def is_solidify(myobject):
    flag = False
    try:
        if myobject.modifiers is None:
            return False

        for mod in myobject.modifiers:
            if mod.type == 'SOLIDIFY':
                flag = True
                break
        return flag
    except AttributeError:
        return False

# -----------------------------------------------------
# Move Solidify to Top
# -----------------------------------------------------
def movetotopsolidify(myobject):
    mymod = None
    try:
        if myobject.modifiers is not None:
            for mod in myobject.modifiers:
                if mod.type == 'SOLIDIFY':
                    mymod = mod

            if mymod is not None:
                while myobject.modifiers[0] != mymod:
                    bpy.ops.object.modifier_move_up(modifier=mymod.name)
    except AttributeError:
        return

# -----------------------------------------------------
# Property definition creator
# -----------------------------------------------------
def wall_height_property(callback=None):
    return FloatProperty(
            name='Height',
            soft_min=0.001,
            default=2.5, precision=3, unit = 'LENGTH',
            description='Wall height', update=callback,
            )

def wall_width_property(callback=None):
    return FloatProperty(
            name='Width',
            soft_min=0.001,
            default=1.0, precision=3, unit = 'LENGTH',
            description='Wall width', update=callback,
            )

def wall_depth_property(callback=None):
    return FloatProperty(
            name='Thickness',
            soft_min=0.001,
            default=0.025, precision=4, unit = 'LENGTH',
            description='Thickness of the wall', update=callback,
            )

# ------------------------------------------------------------------
# Define property group class to create or modify a walls.
# ------------------------------------------------------------------
class ArchLabWallProperties(PropertyGroup):
    wall_height = wall_height_property(callback=update_wall)
    wall_width = wall_width_property(callback=update_wall)
    wall_depth = wall_depth_property(callback=update_wall)

bpy.utils.register_class(ArchLabWallProperties)
Object.ArchLabWallGenerator = CollectionProperty(type=ArchLabWallProperties)

# ------------------------------------------------------------------
# Define panel class to modify walls.
# ------------------------------------------------------------------
class ArchLabWallGeneratorPanel(Panel):
    bl_idname = "OBJECT_PT_wall_generator"
    bl_label = "Wall"
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
        if 'ArchLabWallGenerator' not in o:
            return False
        if act_op is not None and act_op.bl_idname.endswith('archlab_wall'):
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'ArchLabWallGenerator', this panel is not created.
        try:
            if 'ArchLabWallGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            wall = o.ArchLabWallGenerator[0]
            row = layout.row()
            row.prop(wall, 'wall_width')
            row = layout.row()
            row.prop(wall, 'wall_height')
            row = layout.row()
            row.prop(wall, 'wall_depth')

# ------------------------------------------------------------------
# Define operator class to create walls
# ------------------------------------------------------------------
class ArchLabWall(Operator):
    bl_idname = "mesh.archlab_wall"
    bl_label = "Add Wall"
    bl_description = "Generate wall mesh"
    bl_category = 'ArchLab'
    bl_options = {'REGISTER', 'UNDO'}

    # preset
    wall_height = wall_height_property()
    wall_width = wall_width_property()
    wall_depth = wall_depth_property()

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            row = layout.row()
            row.prop(self, 'wall_width')
            row = layout.row()
            row.prop(self, 'wall_height')
            row = layout.row()
            row.prop(self, 'wall_depth')
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
                create_wall(self, context)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "ArchLab: Option only valid in global view mode")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "ArchLab: Option only valid in Object mode")
            return {'CANCELLED'}
