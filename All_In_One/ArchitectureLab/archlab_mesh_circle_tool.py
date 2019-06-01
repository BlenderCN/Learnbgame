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
from bpy.props import EnumProperty, IntProperty, FloatProperty, CollectionProperty
from .archlab_utils import *
from .archlab_utils_mesh_generator import *

# ------------------------------------------------------------------------------
# Create main object for the circle.
# ------------------------------------------------------------------------------
def create_circle(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False

    # we create main object and mesh for circle
    circlemesh = bpy.data.meshes.new("Circle")
    circleobject = bpy.data.objects.new("Circle", circlemesh)
    circleobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(circleobject)
    circleobject.ArchLabCircleGenerator.add()

    circleobject.ArchLabCircleGenerator[0].circle_radius = self.circle_radius
    circleobject.ArchLabCircleGenerator[0].circle_quality = self.circle_quality
    circleobject.ArchLabCircleGenerator[0].circle_fill_type = self.circle_fill_type
    circleobject.ArchLabCircleGenerator[0].circle_depth = self.circle_depth
    circleobject.ArchLabCircleGenerator[0].circle_truncation = self.circle_truncation

    # we shape the mesh.
    shape_circle_mesh(circleobject, circlemesh)

    # we select, and activate, main object for the circle.
    circleobject.select = True
    bpy.context.scene.objects.active = circleobject

# ------------------------------------------------------------------------------
# Shapes mesh and creates modifier solidify (the modifier, only the first time).
# ------------------------------------------------------------------------------
def shape_circle_mesh(mycircle, tmp_mesh, update=False):
    pp = mycircle.ArchLabCircleGenerator[0]  # "pp" means "circle properties".
    # Create circle mesh data
    update_circle_mesh_data(tmp_mesh, pp.circle_radius, pp.circle_quality, pp.circle_fill_type, pp.circle_truncation)
    mycircle.data = tmp_mesh

    remove_doubles(mycircle)
    set_normals(mycircle)

    if pp.circle_depth > 0.0:
        if update is False or is_solidify(mycircle) is False:
            set_modifier_solidify(mycircle, pp.circle_depth)
        else:
            for mod in mycircle.modifiers:
                if mod.type == 'SOLIDIFY':
                    mod.thickness = pp.circle_depth
        # Move to Top SOLIDIFY
        movetotopsolidify(mycircle)

    else:  # clear not used SOLIDIFY
        for mod in mycircle.modifiers:
            if mod.type == 'SOLIDIFY':
                mycircle.modifiers.remove(mod)

    # deactivate others
    for o in bpy.data.objects:
        if o.select is True and o.name != mycircle.name:
            o.select = False

# ------------------------------------------------------------------------------
# Creates circle mesh data.
# ------------------------------------------------------------------------------
def update_circle_mesh_data(mymesh, radius, vertices, fill_type, trunc_val):
    if fill_type == 'NONE':
        (myvertices, myedges, myfaces) = generate_circle_nofill_mesh_data(radius, vertices)
    if fill_type == 'NGON':
        (myvertices, myedges, myfaces) = generate_circle_ngonfill_mesh_data(radius, vertices, trunc_val)
    if fill_type == 'TRIF':
        (myvertices, myedges, myfaces) = generate_circle_tfanfill_mesh_data(radius, vertices)

    mymesh.from_pydata(myvertices, myedges, myfaces)
    mymesh.update(calc_edges=True)

# ------------------------------------------------------------------------------
# Update circle mesh.
# ------------------------------------------------------------------------------
def update_circle(self, context):
    # When we update, the active object is the main object of the circle.
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that circle object to not delete it.
    o.select = False
    # and we create a new mesh for the circle:
    tmp_mesh = bpy.data.meshes.new("temp")
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally we shape the main mesh again,
    shape_circle_mesh(o, tmp_mesh, True)
    o.data = tmp_mesh
    # Remove data (mesh of active object),
    bpy.data.meshes.remove(oldmesh)
    tmp_mesh.name = oldname
    # and select, and activate, the main object of the circle.
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
def circle_radius_property(callback=None):
    return FloatProperty(
            name='Radius',
            soft_min=0.001,
            default=1.0, precision=3, unit='LENGTH',
            description='Circle radius', update=callback,
            )

def circle_quality_property(callback=None):
    return IntProperty(
            name='Vertices',
            min=3, max=1000,
            default=32,
            description='Circle vertices', update=callback,
            )

def circle_depth_property(callback=None):
    return FloatProperty(
            name='Thickness',
            soft_min=0.0,
            default=0.0, precision=4, unit='LENGTH',
            description='Thickness of the circle', update=callback,
            )

def circle_fill_type_property(callback=None):
    return EnumProperty(
            items=(
                ('TRIF', 'Triangle Fan', ''),
                ('NGON', 'Ngon', ''),
                ('NONE', 'Nothing', ''),
                ),
            name='Fill type',
            description='Topology of circle face', update=callback,
            )

def circle_truncation_property(callback=None):
    return FloatProperty(
            name='Truncation',
            min=0.0, max=1.0,
            default=0.0, precision=4,
            description='Truncation of the circle', update=callback,
            )

# ------------------------------------------------------------------
# Define property group class to create or modify a circles.
# ------------------------------------------------------------------
class ArchLabCircleProperties(PropertyGroup):
    circle_radius = circle_radius_property(callback=update_circle)
    circle_quality = circle_quality_property(callback=update_circle)
    circle_fill_type = circle_fill_type_property(callback=update_circle)
    circle_depth = circle_depth_property(callback=update_circle)
    circle_truncation = circle_truncation_property(callback=update_circle)

bpy.utils.register_class(ArchLabCircleProperties)
Object.ArchLabCircleGenerator = CollectionProperty(type=ArchLabCircleProperties)

# ------------------------------------------------------------------
# Define panel class to modify circles.
# ------------------------------------------------------------------
class ArchLabCircleGeneratorPanel(Panel):
    bl_idname = "OBJECT_PT_circle_generator"
    bl_label = "Circle"
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
        if 'ArchLabCircleGenerator' not in o:
            return False
        if act_op is not None and act_op.bl_idname.endswith('archlab_circle'):
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'ArchLabCircleGenerator', this panel is not created.
        try:
            if 'ArchLabCircleGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            circle = o.ArchLabCircleGenerator[0]
            row = layout.row()
            row.prop(circle, 'circle_quality')
            row = layout.row()
            row.prop(circle, 'circle_radius')
            row = layout.row()
            row.prop(circle, 'circle_fill_type')
            row = layout.row()
            row.prop(circle, 'circle_depth')
            if circle.circle_fill_type == 'NGON':
                row = layout.row()
                row.prop(circle, 'circle_truncation')

# ------------------------------------------------------------------
# Define operator class to create circles
# ------------------------------------------------------------------
class ArchLabCircle(Operator):
    bl_idname = "mesh.archlab_circle"
    bl_label = "Add Circle"
    bl_description = "Generate circle primitive mesh"
    bl_category = 'ArchLab'
    bl_options = {'REGISTER', 'UNDO'}

    # preset
    circle_radius = circle_radius_property()
    circle_quality = circle_quality_property()
    circle_fill_type = circle_fill_type_property()
    circle_depth = circle_depth_property()
    circle_truncation = circle_truncation_property()

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            row = layout.row()
            row.prop(self, 'circle_quality')
            row = layout.row()
            row.prop(self, 'circle_radius')
            row = layout.row()
            row.prop(self, 'circle_fill_type')
            row = layout.row()
            row.prop(self, 'circle_depth')
            if self.circle_fill_type == 'NGON':
                row = layout.row()
                row.prop(self, 'circle_truncation')
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
                create_circle(self, context)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "ArchLab: Option only valid in global view mode")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "ArchLab: Option only valid in Object mode")
            return {'CANCELLED'}
