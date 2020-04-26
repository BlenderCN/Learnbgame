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
from bpy.props import BoolProperty, FloatProperty, CollectionProperty
from .archlab_utils import *

# ------------------------------------------------------------------------------
# Create main object for the shelve.
# ------------------------------------------------------------------------------
def create_shelve(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False

    # we create shelve object and mesh
    shelvemesh = bpy.data.meshes.new("Shelve")
    shelveobject = bpy.data.objects.new("Shelve", shelvemesh)
    shelveobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(shelveobject)
    shelveobject.ArchLabShelveGenerator.add()

    shelveobject.ArchLabShelveGenerator[0].shelve_height = self.shelve_height
    shelveobject.ArchLabShelveGenerator[0].shelve_width = self.shelve_width
    shelveobject.ArchLabShelveGenerator[0].shelve_depth = self.shelve_depth
    shelveobject.ArchLabShelveGenerator[0].shelve_thickness = self.shelve_thickness
    shelveobject.ArchLabShelveGenerator[0].shelve_armature = self.shelve_armature
    
    # we shape the mesh.
    shape_shelve_mesh(shelveobject, shelvemesh)

    if self.shelve_armature:
        # we create main object and mesh for shelve
        shelvearmature = bpy.data.armatures.new("Shelve Armature")
        shelvearmatureobject = bpy.data.objects.new("Shelve Armature", shelvearmature)
        shelvearmatureobject.location = bpy.context.scene.cursor_location
        shelvearmatureobject.parent = shelveobject
        bpy.context.scene.objects.link(shelvearmatureobject)

        # we shape the armature.
        shape_shelve_armature(shelveobject, shelvearmatureobject, shelvearmature)

    # we select, and activate, main object for the shelve.
    shelveobject.select = True
    bpy.context.scene.objects.active = shelveobject

# ------------------------------------------------------------------------------
# Shapes mesh and creates modifier solidify (the modifier, only the first time).
# ------------------------------------------------------------------------------
def shape_shelve_mesh(myshelve, tmp_mesh, update=False):
    sp = myshelve.ArchLabShelveGenerator[0]  # "sp" means "shelve properties".
    # Create shelve mesh data
    update_shelve_mesh_data(tmp_mesh, sp.shelve_width, sp.shelve_height, sp.shelve_depth, sp.shelve_thickness)
    myshelve.data = tmp_mesh

    remove_doubles(myshelve)
    set_normals(myshelve)

    # Create Door vertex group
    if not is_vertex_group(myshelve, 'Shelve Door'):
        doorvg = myshelve.vertex_groups.new()
        doorvg.name = 'Shelve Door'
        doorvg.add(index=[8, 9, 11, 10], weight=1, type='ADD')

    if sp.shelve_thickness > 0.0:
        if update is False or is_solidify(myshelve) is False:
            set_modifier_solidify(myshelve, sp.shelve_thickness)
        else:
            for mod in myshelve.modifiers:
                if mod.type == 'SOLIDIFY':
                    mod.thickness = sp.shelve_thickness
        # Move to Top SOLIDIFY
        movetotopsolidify(myshelve)

    else:  # clear not used SOLIDIFY
        for mod in myshelve.modifiers:
            if mod.type == 'SOLIDIFY':
                myshelve.modifiers.remove(mod)

    # deactivate others
    for o in bpy.data.objects:
        if o.select is True and o.name != myshelve.name:
            o.select = False

# ------------------------------------------------------------------------------
# Shapes armature and creates modifier armature (the modifier, only the first time).
# ------------------------------------------------------------------------------
def shape_shelve_armature(myshelve, myarmatureobj, myarmature, update=False):
    sp = myshelve.ArchLabShelveGenerator[0]  # "sp" means "shelve properties".
    # Create shelve armature data
    update_shelve_armature_data(myarmatureobj, myarmature, sp.shelve_width, sp.shelve_height, sp.shelve_depth, sp.shelve_thickness)

    if sp.shelve_armature:
        if update is False or is_armature(myshelve) is False:
            set_modifier_armature(myshelve, myarmatureobj)
        else:
            for mod in myshelve.modifiers:
                if mod.type == 'ARMATURE':
                    mod.thickness = sp.shelve_thickness
        # Move to Top ARMATURE
        movetotoparmature(myshelve)

    else:  # clear not used ARMATURE
        for mod in myshelve.modifiers:
            if mod.type == 'ARMATURE':
                myshelve.modifiers.remove(mod)

# ------------------------------------------------------------------------------
# Creates shelve mesh data.
# ------------------------------------------------------------------------------
def update_shelve_mesh_data(mymesh, width, height, depth, thickness):
    basethick = thickness /2
    posx = width /2
    posy = depth /2
    posz = height +basethick

    myvertices = [
        (-posx, -posy, basethick), (posx, -posy, basethick),
        (-posx, posy, basethick), (posx, posy, basethick),
        (-posx, -posy, posz), (posx, -posy, posz),
        (-posx, posy, posz), (posx, posy, posz)]

    thickdiff = thickness /2 + 0.001
    myvertices.extend([
        (-posx + thickdiff, -posy + thickdiff, basethick + thickdiff),
        (posx - thickdiff, -posy + thickdiff, basethick + thickdiff),
        (-posx + thickdiff, -posy + thickdiff, posz - thickdiff),
        (posx - thickdiff, -posy + thickdiff, posz - thickdiff)
    ])

    myfaces = [
        (0, 1, 3, 2),
        (0, 4, 6, 2),
        (1, 5, 7, 3),
        (2, 3, 7, 6),
        (4, 5, 7, 6),

        (8, 9, 11, 10)
    ]

    mymesh.from_pydata(myvertices, [], myfaces)
    mymesh.update(calc_edges=True)

# ------------------------------------------------------------------------------
# Creates shelve armature data.
# ------------------------------------------------------------------------------
def update_shelve_armature_data(myarmatureobj, myarmature, width, height, depth, thickness):
    basethick = thickness /2
    posx = width /2
    posy = depth /2
    posz = height /2 +basethick
    thickdiff = thickness /2 + 0.001

    prev_o = bpy.context.scene.objects.active
    bpy.context.scene.objects.active = myarmatureobj
    myarmatureobj.select = True
    bpy.ops.object.editmode_toggle()

    doorbone = myarmature.edit_bones.new('Shelve Door')
    doorbone.head = (posx - thickdiff, -posy + thickdiff, posz )
    doorbone.tail = (-posx + thickdiff, -posy + thickdiff, posz)

    bpy.ops.object.editmode_toggle()
    bpy.context.scene.objects.active = prev_o

    doorbone = myarmatureobj.pose.bones[0]
    doorbone.rotation_mode = 'XYZ'
    doorbone.lock_location[0] = True
    doorbone.lock_location[1] = True
    doorbone.lock_location[2] = True
    doorbone.lock_rotation[0] = True
    doorbone.lock_rotation[1] = True
    doorbone.lock_scale[0] = True
    doorbone.lock_scale[1] = True
    doorbone.lock_scale[2] = True

# ------------------------------------------------------------------------------
# Update shelve mesh.
# ------------------------------------------------------------------------------
def update_shelve(self, context):
    # When we update, the active object is the main object of the shelve.
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that shelve object to not delete it.
    o.select = False
    # and we create a new mesh for the shelve:
    tmp_mesh = bpy.data.meshes.new("temp")
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally we shape the main mesh again,
    shape_shelve_mesh(o, tmp_mesh, True)
    o.data = tmp_mesh
    # Remove data (mesh of active object),
    bpy.data.meshes.remove(oldmesh)
    tmp_mesh.name = oldname
    # and select, and activate, the main object of the shelve.
    o.select = True
    bpy.context.scene.objects.active = o

# -----------------------------------------------------
# Verify if vertex group exist
# -----------------------------------------------------
def is_vertex_group(myobject, vgname):
    flag = False
    try:
        if myobject.vertex_groups is None:
            return False

        for vg in myobject.vertex_groups:
            if vg.name == vgname:
                flag = True
                break
        return flag
    except AttributeError:
        return False

# -----------------------------------------------------
# Verify if armature exist
# -----------------------------------------------------
def is_armature(myobject):
    flag = False
    try:
        if myobject.modifiers is None:
            return False

        for mod in myobject.modifiers:
            if mod.type == 'ARMATURE':
                flag = True
                break
        return flag
    except AttributeError:
        return False

# -----------------------------------------------------
# Move Armature to Top
# -----------------------------------------------------
def movetotoparmature(myobject):
    mymod = None
    try:
        if myobject.modifiers is not None:
            for mod in myobject.modifiers:
                if mod.type == 'ARMATURE':
                    mymod = mod

            if mymod is not None:
                while myobject.modifiers[0] != mymod:
                    bpy.ops.object.modifier_move_up(modifier=mymod.name)
    except AttributeError:
        return

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
def shelve_height_property(callback=None):
    return FloatProperty(
            name='Height',
            soft_min=0.001,
            default=0.65, precision=3, unit = 'LENGTH',
            description='Shelve height', update=callback,
            )

def shelve_width_property(callback=None):
    return FloatProperty(
            name='Width',
            soft_min=0.001,
            default=0.60, precision=3, unit = 'LENGTH',
            description='Shelve width', update=callback,
            )

def shelve_depth_property(callback=None):
    return FloatProperty(
            name='Depth',
            soft_min=0.001,
            default=0.40, precision=3, unit = 'LENGTH',
            description='Shelve depth', update=callback,
            )

def shelve_thickness_property(callback=None):
    return FloatProperty(
            name='Thickness',
            soft_min=0.001,
            default=0.015, precision=4, unit = 'LENGTH',
            description='Thickness of the shelve', update=callback,
            )

def shelve_armature_property(callback=None):
    return BoolProperty(
            name='Armature',
            default=False,
            description='Create armature for the shelve door', update=callback,
            )

# ------------------------------------------------------------------
# Define property group class to create or modify a shelves.
# ------------------------------------------------------------------
class ArchLabShelveProperties(PropertyGroup):
    shelve_height = shelve_height_property(callback=update_shelve)
    shelve_width = shelve_width_property(callback=update_shelve)
    shelve_depth = shelve_depth_property(callback=update_shelve)
    shelve_thickness = shelve_thickness_property(callback=update_shelve)
    shelve_armature = shelve_armature_property(callback=update_shelve)

bpy.utils.register_class(ArchLabShelveProperties)
Object.ArchLabShelveGenerator = CollectionProperty(type=ArchLabShelveProperties)

# ------------------------------------------------------------------
# Define panel class to modify shelves.
# ------------------------------------------------------------------
class ArchLabShelveGeneratorPanel(Panel):
    bl_idname = "OBJECT_PT_shelve_generator"
    bl_label = "Shelve"
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
        if 'ArchLabShelveGenerator' not in o:
            return False
        if act_op is not None and act_op.bl_idname.endswith('archlab_shelve'):
            return False
        if o.ArchLabShelveGenerator[0].shelve_armature:
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'ArchLabShelveGenerator', this panel is not created.
        try:
            if 'ArchLabShelveGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            shelve = o.ArchLabShelveGenerator[0]
            row = layout.row()
            row.prop(shelve, 'shelve_width')
            row = layout.row()
            row.prop(shelve, 'shelve_height')
            row = layout.row()
            row.prop(shelve, 'shelve_depth')
            row = layout.row()
            row.prop(shelve, 'shelve_thickness')

# ------------------------------------------------------------------
# Define operator class to create shelves
# ------------------------------------------------------------------
class ArchLabShelve(Operator):
    bl_idname = "mesh.archlab_shelve"
    bl_label = "Add Shelve"
    bl_description = "Generate shelve mesh"
    bl_category = 'ArchLab'
    bl_options = {'REGISTER', 'UNDO'}

    # preset
    shelve_height = shelve_height_property()
    shelve_width = shelve_width_property()
    shelve_depth = shelve_depth_property()
    shelve_thickness = shelve_thickness_property()
    shelve_armature = shelve_armature_property()

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            row = layout.row()
            row.prop(self, 'shelve_width')
            row = layout.row()
            row.prop(self, 'shelve_height')
            row = layout.row()
            row.prop(self, 'shelve_depth')
            row = layout.row()
            row.prop(self, 'shelve_thickness')
            row = layout.row()
            row.prop(self, 'shelve_armature')
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
                create_shelve(self, context)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "ArchLab: Option only valid in global view mode")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "ArchLab: Option only valid in Object mode")
            return {'CANCELLED'}
