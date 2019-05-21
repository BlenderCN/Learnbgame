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
from bpy.props import IntProperty, FloatProperty, CollectionProperty
from .archlab_utils import *

# ------------------------------------------------------------------------------
# Create main object for the stairs.
# ------------------------------------------------------------------------------
def create_stairs(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False

    # we create main object and mesh for stairs
    stairsmesh = bpy.data.meshes.new("Stairs")
    stairsobject = bpy.data.objects.new("Stairs", stairsmesh)
    stairsobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(stairsobject)
    stairsobject.ArchLabStairsGenerator.add()

    stairsobject.ArchLabStairsGenerator[0].stairs_width = self.stairs_width
    stairsobject.ArchLabStairsGenerator[0].stairs_unit_count = self.stairs_unit_count
    stairsobject.ArchLabStairsGenerator[0].stairs_unit_run = self.stairs_unit_run
    stairsobject.ArchLabStairsGenerator[0].stairs_unit_raise = self.stairs_unit_raise
    stairsobject.ArchLabStairsGenerator[0].stairs_noising = self.stairs_noising
    stairsobject.ArchLabStairsGenerator[0].stairs_noising_thickness = self.stairs_noising_thickness
    stairsobject.ArchLabStairsGenerator[0].stairs_tread = self.stairs_tread

    # we shape the mesh.
    shape_stairs_mesh(stairsobject, stairsmesh)

    # we select, and activate, main object for the stairs.
    stairsobject.select = True
    bpy.context.scene.objects.active = stairsobject

# ------------------------------------------------------------------------------
# Shapes mesh and creates modifier solidify (the modifier, only the first time).
# ------------------------------------------------------------------------------
def shape_stairs_mesh(mystairs, tmp_mesh, update=False):
    sp = mystairs.ArchLabStairsGenerator[0]  # "sp" means "stairs properties".
    # Create stairs mesh data
    update_stairs_mesh_data(tmp_mesh, sp.stairs_width, sp.stairs_unit_count, sp.stairs_unit_run, sp.stairs_unit_raise)
    mystairs.data = tmp_mesh

    remove_doubles(mystairs)
    set_normals(mystairs)

    # deactivate others
    for o in bpy.data.objects:
        if o.select is True and o.name != mystairs.name:
            o.select = False

# ------------------------------------------------------------------------------
# Creates stairs mesh data.
# ------------------------------------------------------------------------------
def update_stairs_mesh_data(mymesh, width, unit_count, unit_run, unit_raise):
    myvertices = []
    myfaces = []
    lastp = (-width / 2.0, 0.0, 0.0)
    myvertices.extend([
        (-width / 2.00, lastp[1], lastp[2]),
        (width / 2.0, lastp[1], lastp[2]),
    ])
    for ut in range(unit_count):
        p1 = (-width / 2.0, lastp[1] + unit_run, lastp[2] + unit_raise)
        myvertices.extend([
            (-width / 2.0, lastp[1], p1[2]),
            (width / 2.0, lastp[1], p1[2]),
            (-width / 2.0, p1[1], p1[2]),
            (width / 2.0, p1[1], p1[2]),
        ])
        myfaces.extend([
            (ut*4 + 0, ut*4 + 1, ut*4 + 3, ut*4 + 2),
            (ut*4 + 2, ut*4 + 3, ut*4 + 5, ut*4 + 4)
        ])
        lastp = p1

    mymesh.from_pydata(myvertices, [], myfaces)
    mymesh.update(calc_edges=True)

# ------------------------------------------------------------------------------
# Update stairs mesh.
# ------------------------------------------------------------------------------
def update_stairs(self, context):
    # When we update, the active object is the main object of the stairs.
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that stairs object to not delete it.
    o.select = False
    # and we create a new mesh for the stairs:
    tmp_mesh = bpy.data.meshes.new("temp")
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally we shape the main mesh again,
    shape_stairs_mesh(o, tmp_mesh, True)
    o.data = tmp_mesh
    # Remove data (mesh of active object),
    bpy.data.meshes.remove(oldmesh)
    tmp_mesh.name = oldname
    # and select, and activate, the main object of the stairs.
    o.select = True
    bpy.context.scene.objects.active = o

# -----------------------------------------------------
# Property definition creator
# -----------------------------------------------------
def stairs_width_property(callback=None):
    return FloatProperty(
            name='Width',
            soft_min=0.35,
            default=1, precision=3, unit = 'LENGTH',
            description='Stairs width', update=callback,
            )

def stairs_unit_count_property(callback=None):
    return IntProperty(
            name='Unit count',
            soft_min=3, soft_max=18,
            default=5,
            description='Stairs width', update=callback,
            )

def stairs_unit_run_property(callback=None):
    return FloatProperty(
            name='Unit run',
            soft_min=0.0,
            default=0.29, precision=3, unit = 'LENGTH',
            description='Stairs width', update=callback,
            )

def stairs_unit_raise_property(callback=None):
    return FloatProperty(
            name='Unit raise',
            soft_min=0.0,
            default=0.17, precision=3, unit = 'LENGTH',
            description='Stairs width', update=callback,
            )

def stairs_noising_property(callback=None):
    return FloatProperty(
            name='Noising',
            soft_min=0.0,
            default=0.1, precision=3, unit = 'LENGTH',
            description='Stairs width', update=callback,
            )

def stairs_noising_thickness_property(callback=None):
    return FloatProperty(
            name='Noising thickness',
            soft_min=0.0,
            default=0.1, precision=3, unit = 'LENGTH',
            description='Stairs width', update=callback,
            )

def stairs_tread_property(callback=None):
    return FloatProperty(
            name='Tread',
            soft_min=0.0,
            default=0.1, precision=3, unit = 'LENGTH',
            description='Stairs width', update=callback,
            )

def draw_props(layout, propg):
    row = layout.row()
    row.prop(propg, 'stairs_width')
    row = layout.row()
    row.prop(propg, 'stairs_unit_count')
    row = layout.row()
    row.prop(propg, 'stairs_unit_run')
    row = layout.row()
    row.prop(propg, 'stairs_unit_raise')

# ------------------------------------------------------------------
# Define property group class to create or modify a stairss.
# ------------------------------------------------------------------
class ArchLabStairsProperties(PropertyGroup):
    stairs_width = stairs_width_property(callback=update_stairs)
    stairs_unit_count = stairs_unit_count_property(callback=update_stairs)
    stairs_unit_run = stairs_unit_run_property(callback=update_stairs)
    stairs_unit_raise = stairs_unit_raise_property(callback=update_stairs)
    stairs_noising = stairs_noising_property(callback=update_stairs)
    stairs_noising_thickness = stairs_noising_thickness_property(callback=update_stairs)
    stairs_tread = stairs_tread_property(callback=update_stairs)

bpy.utils.register_class(ArchLabStairsProperties)
Object.ArchLabStairsGenerator = CollectionProperty(type=ArchLabStairsProperties)

# ------------------------------------------------------------------
# Define panel class to modify stairss.
# ------------------------------------------------------------------
class ArchLabStairsGeneratorPanel(Panel):
    bl_idname = "OBJECT_PT_stairs_generator"
    bl_label = "Stairs"
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
        if 'ArchLabStairsGenerator' not in o:
            return False
        if act_op is not None and act_op.bl_idname.endswith('archlab_stairs'):
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'ArchLabStairsGenerator', this panel is not created.
        try:
            if 'ArchLabStairsGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            stairs = o.ArchLabStairsGenerator[0]
            draw_props(layout, stairs)

# ------------------------------------------------------------------
# Define operator class to create stairss
# ------------------------------------------------------------------
class ArchLabStairs(Operator):
    bl_idname = "mesh.archlab_stairs"
    bl_label = "Add Stairs"
    bl_description = "Generate stairs mesh"
    bl_category = 'ArchLab'
    bl_options = {'REGISTER', 'UNDO'}

    # preset
    stairs_width = stairs_width_property()
    stairs_unit_count = stairs_unit_count_property()
    stairs_unit_run = stairs_unit_run_property()
    stairs_unit_raise = stairs_unit_raise_property()
    stairs_noising = stairs_noising_property()
    stairs_noising_thickness = stairs_noising_thickness_property()
    stairs_tread = stairs_tread_property()

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            draw_props(layout, self)
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
                create_stairs(self, context)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "ArchLab: Option only valid in global view mode")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "ArchLab: Option only valid in Object mode")
            return {'CANCELLED'}
