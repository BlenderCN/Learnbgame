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
from .archlab_utils_material_data import *
from .archlab_utils_mesh_generator import *

# ------------------------------------------------------------------------------
# Create main object for the glass.
# ------------------------------------------------------------------------------
def create_glass(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select = False

    # we create main object and mesh
    glassmesh = bpy.data.meshes.new("Glass")
    glassobject = bpy.data.objects.new("Glass", glassmesh)
    glassobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(glassobject)
    glassobject.ArchLabGlassGenerator.add()

    glassobject.ArchLabGlassGenerator[0].glass_diameter = self.glass_diameter
    glassobject.ArchLabGlassGenerator[0].glass_height = self.glass_height
    glassobject.ArchLabGlassGenerator[0].glass_segments = self.glass_segments

    # we shape the mesh.
    shape_glass_mesh(glassobject, glassmesh)
    set_smooth(glassobject)
    set_modifier_subsurf(glassobject)

    # assign a material
    mat = meshlib_glass_material()
    set_material(glassobject, mat.name)

    # we select, and activate, main object for the glass.
    glassobject.select = True
    bpy.context.scene.objects.active = glassobject

# ------------------------------------------------------------------------------
# Shapes mesh the glass mesh
# ------------------------------------------------------------------------------
def shape_glass_mesh(myglass, tmp_mesh, update=False):
    gp = myglass.ArchLabGlassGenerator[0]  # "gp" means "glass properties".
    # Create glass mesh data
    update_glass_mesh_data(tmp_mesh, gp.glass_diameter, gp.glass_height, gp.glass_segments)
    myglass.data = tmp_mesh

    remove_doubles(myglass)
    set_normals(myglass)

    # deactivate others
    for o in bpy.data.objects:
        if o.select is True and o.name != myglass.name:
            o.select = False

# ------------------------------------------------------------------------------
# Creates glass mesh data.
# ------------------------------------------------------------------------------
def update_glass_mesh_data(mymesh, diameter, height, segments):
    (myvertices, myedges, myfaces) = generate_mesh_from_library(
        'Glass01',
        size=(diameter, diameter, height),
        segments=segments
    )

    mymesh.from_pydata(myvertices, myedges, myfaces)
    mymesh.update(calc_edges=True)

# ------------------------------------------------------------------------------
# Update glass mesh.
# ------------------------------------------------------------------------------
def update_glass(self, context):
    # When we update, the active object is the main object of the glass.
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that glass object to not delete it.
    o.select = False
    # and we create a new mesh for the glass:
    tmp_mesh = bpy.data.meshes.new("temp")
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select = False
    # Finally we shape the main mesh again,
    shape_glass_mesh(o, tmp_mesh, True)
    o.data = tmp_mesh
    # Remove data (mesh of active object),
    bpy.data.meshes.remove(oldmesh)
    tmp_mesh.name = oldname
    # and select, and activate, the main object of the glass.
    o.select = True
    bpy.context.scene.objects.active = o


# -----------------------------------------------------
# Property definition creator
# -----------------------------------------------------
def glass_diameter_property(callback=None):
    return FloatProperty(
            name='Diameter',
            soft_min=0.001,
            default=0.05, precision=3, unit = 'LENGTH',
            description='Glass diameter', update=callback,
            )

def glass_quality_property(callback=None):
    return FloatProperty(
            name='Height',
            soft_min=0.001,
            default=0.08, precision=3, unit = 'LENGTH',
            description='Glass height', update=callback,
            )

def glass_segments_property(callback=None):
    return IntProperty(
            name='Segments',
            min=3, max=1000,
            default=16,
            description='Glass segments amount', update=callback,
            )

# ------------------------------------------------------------------
# Define property group class to create or modify a glasss.
# ------------------------------------------------------------------
class ArchLabGlassProperties(PropertyGroup):
    glass_diameter = glass_diameter_property(callback=update_glass)
    glass_height = glass_quality_property(callback=update_glass)
    glass_segments = glass_segments_property(callback=update_glass)

bpy.utils.register_class(ArchLabGlassProperties)
Object.ArchLabGlassGenerator = CollectionProperty(type=ArchLabGlassProperties)

# ------------------------------------------------------------------
# Define panel class to modify glasss.
# ------------------------------------------------------------------
class ArchLabGlassGeneratorPanel(Panel):
    bl_idname = "OBJECT_PT_glass_generator"
    bl_label = "Glass"
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
        if 'ArchLabGlassGenerator' not in o:
            return False
        if act_op is not None and act_op.bl_idname.endswith('archlab_glass'):
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # If the selected object didn't be created with the group 'ArchLabGlassGenerator', this panel is not created.
        try:
            if 'ArchLabGlassGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label('Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            glass = o.ArchLabGlassGenerator[0]
            row = layout.row()
            row.prop(glass, 'glass_diameter')
            row = layout.row()
            row.prop(glass, 'glass_height')
            row = layout.row()
            row.prop(glass, 'glass_segments')

# ------------------------------------------------------------------
# Define operator class to create glasss
# ------------------------------------------------------------------
class ArchLabGlass(Operator):
    bl_idname = "mesh.archlab_glass"
    bl_label = "Add Glass"
    bl_description = "Generate glass decoration"
    bl_category = 'ArchLab'
    bl_options = {'REGISTER', 'UNDO'}

    # preset
    glass_diameter = glass_diameter_property()
    glass_height = glass_quality_property()
    glass_segments = glass_segments_property()

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            row = layout.row()
            row.prop(self, 'glass_diameter')
            row = layout.row()
            row.prop(self, 'glass_height')
            row = layout.row()
            row.prop(self, 'glass_segments')
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
                create_glass(self, context)
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "ArchLab: Option only valid in global view mode")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "ArchLab: Option only valid in Object mode")
            return {'CANCELLED'}
