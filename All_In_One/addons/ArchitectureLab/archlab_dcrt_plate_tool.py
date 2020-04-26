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
from .archlab_utils_material_data import *
from .archlab_utils_mesh_generator import *

# ------------------------------------------------------------------------------
# Create main object for the plate.
# ------------------------------------------------------------------------------
def create_plate(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False

    # we create main object and mesh
    platemesh = bpy.data.meshes.new("Plate")
    plateobject = bpy.data.objects.new("Plate", platemesh)
    plateobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(plateobject)
    plateobject.ArchLabPlateGenerator.add()

    plateobject.ArchLabPlateGenerator[0].plate_diameter = self.plate_diameter
    plateobject.ArchLabPlateGenerator[0].plate_height = self.plate_height
    plateobject.ArchLabPlateGenerator[0].plate_segments = self.plate_segments
    plateobject.ArchLabPlateGenerator[0].plate_type = self.plate_type

    # we shape the mesh.
    shape_plate_mesh(plateobject, platemesh)
    set_smooth(plateobject)
    set_modifier_subsurf(plateobject)

    # assign a material
    mat = meshlib_ceramic_material()
    set_material(plateobject, mat.name)

    # we select, and activate, main object for the plate.
    plateobject.select = True
    bpy.context.scene.objects.active = plateobject

# ------------------------------------------------------------------------------
# Shapes mesh the plate mesh
# ------------------------------------------------------------------------------
def shape_plate_mesh(myplate, tmp_mesh, update=False):
    pp = myplate.ArchLabPlateGenerator[0]  # "pp" means "plate properties".
    # Create plate mesh data
    update_plate_mesh_data(tmp_mesh, pp.plate_diameter, pp.plate_height, pp.plate_segments, pp.plate_type)
    myplate.data = tmp_mesh

    remove_doubles(myplate)
    set_normals(myplate)

    # deactivate others
    for o in bpy.data.objects:
        if o.select is True and o.name != myplate.name:
            o.select = False

# ------------------------------------------------------------------------------
# Creates plate mesh data.
# ------------------------------------------------------------------------------
def update_plate_mesh_data(mymesh, diameter, height, segments, type):
    if type is None:
        mytype = 'Plate01'
    else:
        mytype = type

    (myvertices, myedges, myfaces) = generate_mesh_from_library(
        type,
        size=(diameter, diameter, height),
        segments=segments
    )

    mymesh.from_pydata(myvertices, myedges, myfaces)
    mymesh.update(calc_edges=True)

# ------------------------------------------------------------------------------
# Update plate mesh.
# ------------------------------------------------------------------------------
def update_plate(self, context):
    # When we update, the active object is the main object of the plate.
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that plate object to not delete it.
    o.select = False
    # and we create a new mesh for the plate:
    tmp_mesh = bpy.data.meshes.new("temp")
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally we shape the main mesh again,
    shape_plate_mesh(o, tmp_mesh, True)
    o.data = tmp_mesh
    # Remove data (mesh of active object),
    bpy.data.meshes.remove(oldmesh)
    tmp_mesh.name = oldname
    # and select, and activate, the main object of the plate.
    o.select = True
    bpy.context.scene.objects.active = o

# ------------------------------------------------------------------------------
# Update plate mesh and sizes based on new kind.
# ------------------------------------------------------------------------------
def update_plate_kind(self, context):
    update_plate_size(self, context)
    update_plate(self, context)

# ------------------------------------------------------------------------------
# Update plate sizes based on new kind.
# ------------------------------------------------------------------------------
def update_plate_size(self, context):
    cob = context.object
    cao = context.active_operator
    if cob is not None and 'ArchLabPlateGenerator' in cob:
        props = cob.ArchLabPlateGenerator[0]
    elif cao is not None:
        props = cao
    if props is not None:
        if props.plate_type == 'Plate01':
            props.plate_diameter = 0.21
            props.plate_height = 0.03
        elif props.plate_type == 'DinnerPlate01':
            props.plate_diameter = 0.25
            props.plate_height = 0.02
        elif props.plate_type == 'DeepPlate01':
            props.plate_diameter = 0.21
            props.plate_height = 0.03
        elif props.plate_type == 'SidePlate01':
            props.plate_diameter = 0.185
            props.plate_height = 0.017


# -----------------------------------------------------
# Property definition creator
# -----------------------------------------------------
def plate_diameter_property(callback=None):
    return FloatProperty(
            name='Diameter',
            soft_min=0.001,
            default=0.21, precision=3, unit = 'LENGTH',
            description='Plate diameter', update=callback,
            )

def plate_height_property(callback=None):
    return FloatProperty(
            name='Height',
            soft_min=0.001,
            default=0.03, precision=3, unit = 'LENGTH',
            description='Plate height', update=callback,
            )

def plate_segments_property(callback=None):
    return IntProperty(
            name='Segments',
            min=3, max=1000,
            default=16,
            description='Plate segments amount', update=callback,
            )

def plate_type_property(defaultitem='Plate01', callback=None):
    return EnumProperty(
            items=(
                ('Plate01', 'Plate', ''),
                ('DinnerPlate01', 'Dinner Plate', ''),
                ('DeepPlate01', 'Deep Plate', ''),
                ('SidePlate01', 'Side Plate', ''),
                ),
            name='Kind',
            default=defaultitem,
            description='Plate kind', update=callback,
            )

# ------------------------------------------------------------------
# Define property group class to create or modify a plates.
# ------------------------------------------------------------------
class ArchLabPlateProperties(PropertyGroup):
    plate_type = plate_type_property(callback=update_plate_kind)
    plate_diameter = plate_diameter_property(callback=update_plate)
    plate_height = plate_height_property(callback=update_plate)
    plate_segments = plate_segments_property(callback=update_plate)

bpy.utils.register_class(ArchLabPlateProperties)
Object.ArchLabPlateGenerator = CollectionProperty(type=ArchLabPlateProperties)

# ------------------------------------------------------------------
# Define panel class to modify plates.
# ------------------------------------------------------------------
class ArchLabPlateGeneratorPanel(Panel):
    bl_idname = "OBJECT_PT_plate_generator"
    bl_label = "Plate"
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
        if 'ArchLabPlateGenerator' not in o:
            return False
        if act_op is not None and act_op.bl_idname.endswith('archlab_plate'):
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'ArchLabPlateGenerator', this panel is not created.
        try:
            if 'ArchLabPlateGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            plate = o.ArchLabPlateGenerator[0]
            row = layout.row()
            row.prop(plate, 'plate_type')
            row = layout.row()
            row.prop(plate, 'plate_diameter')
            row = layout.row()
            row.prop(plate, 'plate_height')
            row = layout.row()
            row.prop(plate, 'plate_segments')

# ------------------------------------------------------------------
# Define operator class to create plates
# ------------------------------------------------------------------
class ArchLabPlate(Operator):
    bl_idname = "mesh.archlab_plate"
    bl_label = "Add Plate"
    bl_description = "Generate plate decoration"
    bl_category = 'ArchLab'
    bl_options = {'REGISTER', 'UNDO'}

    # preset
    plate_type = plate_type_property(callback=update_plate_size)
    plate_diameter = plate_diameter_property()
    plate_height = plate_height_property()
    plate_segments = plate_segments_property()

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            row = layout.row()
            row.prop(self, 'plate_type')
            row = layout.row()
            row.prop(self, 'plate_diameter')
            row = layout.row()
            row.prop(self, 'plate_height')
            row = layout.row()
            row.prop(self, 'plate_segments')
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
                create_plate(self, context)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "ArchLab: Option only valid in global view mode")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "ArchLab: Option only valid in Object mode")
            return {'CANCELLED'}
