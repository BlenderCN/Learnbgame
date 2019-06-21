# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   operatorprops.py
# Date:   2014-07-03
# Author: Varvara Efremova
#
# Description:
# AtomBlend operator and operator property definitions.
# =============================================================================

import bpy

import os

# bpy types used
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator

# Own pkgs
from . import operatorexec as opexec

# TODO move this to a default settings module
HALO_IMG_PATH = os.path.dirname(__file__)+"/atomtex.png"
#HALO_IMG_PATH = "/Users/varvara/Library/Application Support/Blender/2.70/scripts/addons/AtomBlend/atomtex.png"

# === Operator classes ===
class VIEW3D_OT_pospath_button(Operator, ImportHelper):
    """Select POS file from dialogue"""
    bl_idname = "atomblend.import_pospath"
    bl_label = "Select .pos file"

    # ImportHelper mixin class uses this
    filename_ext = ".pos"

    filter_glob = StringProperty(
            default="*.pos",
            options={'HIDDEN'},
            )

    def execute(self, context):
        props = context.scene.pos_panel_props
        # set pos filename
        props.pos_filename = self.filepath
        return {'FINISHED'}

class VIEW3D_OT_rngpath_button(Operator, ImportHelper):
    """Select RNG file from dialogue"""
    bl_idname = "atomblend.import_rngpath"
    bl_label = "Select .rng file"

    # ImportHelper mixin class uses this
    filename_ext = ".rng"

    filter_glob = StringProperty(
            default="*.rng",
            options={'HIDDEN'},
            )

    def execute(self, context):
        props = context.scene.pos_panel_props
        # set rng filename
        props.rng_filename = self.filepath
        return {'FINISHED'}

class VIEW3D_OT_load_posrng_button(Operator):
    """Read and load POS/RNG files into memory"""
    bl_idname = "atomblend.load_posrng"
    bl_label = "Load POS/RNG files"

    def execute(self, context):
        return opexec.load_posrng(self, context)

class VIEW3D_OT_bake_button(Operator):
    """Bake POS data to object"""
    bl_idname = "atomblend.bake_button"
    bl_label = "Bake to object"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        return (area == 'VIEW_3D') and (mode == 'OBJECT')

    def execute(self, context):
        return opexec.bake(self, context)

class VIEW3D_OT_clear_button(Operator):
    """Clears all meshes in the scene"""
    bl_idname = "atomblend.clear_button"
    bl_label = "Clear all objects"

    def execute(self, context):
        return opexec.clear(self, context)

class VIEW3D_OT_remove_duplivert(Operator):
    """Remove vertex duplication object on active object"""
    bl_idname = "atomblend.remove_duplivert"
    bl_label = "Remove vertex object"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        obj = context.object
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (obj is not None) and (obj.vistype == 'DUPLI')

    def execute(self, context):
        return opexec.remove_duplivert(self, context)

class VIEW3D_OT_dupli_vert(Operator):
    """Duplicate icosphere on vertices of currently active object"""
    bl_idname = "atomblend.add_duplivert"
    bl_label = "Add vertex object"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        obj = context.object
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (obj is not None)

    def execute(self, context):
        return opexec.dupli_vert(self, context)

class VIEW3D_OT_add_halomat(Operator):
    """Apply halo material to currently selected object"""
    bl_idname = "atomblend.add_halomat"
    bl_label = "Add halo material"

    # path to billboard texture
    halo_img_path = StringProperty(
            description = "Image to use for halo texture",
            default = HALO_IMG_PATH
            )

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        obj = context.object
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (obj is not None)

    def execute(self, context):
        return opexec.add_halo_material(self, context)

class VIEW3D_OT_add_halo_material(Operator):
    """Remove halo material on currently selected object"""
    bl_idname = "atomblend.remove_halomat"
    bl_label = "Remove halo material"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        obj = context.object
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (obj is not None) and (obj.vistype == 'HALO')

    def execute(self, context):
        return opexec.remove_halo_material(self, context)

class VIEW3D_OT_add_camera_view(Operator):
    """View3D: Add camera placed at current view"""
    bl_idname = "atomblend.add_camera"
    bl_label = "Place camera here"

    @classmethod
    def poll(cls, context):
        # Needs View3D, object mode (for selection), and view_perspective to be PERSP
        area = context.area.type
        mode = context.mode
        persp = context.region_data.view_perspective
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (persp == 'PERSP')

    def execute(self, context):
        return opexec.add_camera_view(self, context)

class VIEW3D_OT_add_lamp_view(Operator):
    """Add lamp placed at current view location"""
    bl_idname = "atomblend.add_lamp"
    bl_label = "Place lamp here"

    @classmethod
    def poll(cls, context):
        # Needs View3D, object mode (for selection), and view_perspective to be PERSP
        area = context.area.type
        mode = context.mode
        persp = context.region_data.view_perspective
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (persp == 'PERSP')

    def execute(self, context):
        return opexec.add_lamp_view(self, context)

class VIEW3D_OT_add_bounding_box(Operator):
    """Add a bounding box to current data"""
    bl_idname = "atomblend.add_bound_box"
    bl_label = "Add bounding box"

    def execute(self, context):
        return opexec.add_bounding_box(self, context)

class VIEW3D_OT_make_camera_active(Operator):
    """Make currently selected camera active"""
    bl_idname = "atomblend.make_camera_active"
    bl_label = "Make camera active"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        obj = context.object
        if obj is None:
            return False
        return (area == 'VIEW_3D') and (obj.type == 'CAMERA')

    def execute(self, context):
        return opexec.make_camera_active(self, context)

class VIEW3D_OT_position_active_camera(Operator):
    """Position currently active camera"""
    bl_idname = "atomblend.position_cam"
    bl_label = "Position active camera"

    positioning = bpy.props.BoolProperty(name="Positioning", default=False)

    @classmethod
    def poll(cls, context):
        area = context.area.type
        cam = context.scene.camera
        if cam is None:
            return False
        return (area == 'VIEW_3D')

    def execute(self, context):
        if self.positioning == False:
            self.positioning = True
            return opexec.position_active_camera_on(self, context)
        else:
            self.positioning = False
            return opexec.position_active_camera_off(self, context)

class VIEW3D_OT_pointcloud_add(Operator):
    """Create pointcloud visualisation for the active object"""
    bl_idname = "atomblend.pointcloud_add"
    bl_label = "Create pointcloud"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        objtype = None
        if context.object is not None:
            objtype = context.object.type
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (objtype == 'MESH')

    def execute(self, context):
        return opexec.pointcloud_add(self, context)

class VIEW3D_OT_scale_child(Operator):
    """Scale child of currently selected object"""
    bl_idname = "atomblend.scale_child"
    bl_label = "Scale vertex object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj is not None) and obj.children

    def execute(self, context):
        return opexec.scale_child(self, context)

class VIEW3D_OT_animation_add(Operator):
    """Add animation around the currently selected object"""
    bl_idname = "atomblend.animation_add"
    bl_label = "Animate!"

    def execute(self, context):
        return opexec.animation_add(self, context)

class VIEW3D_OT_analysis_isosurface(Operator):
    """Calculate the isosurface of the imported dataset"""
    bl_idname = "atomblend.analysis_isosurf"
    bl_label = "Generate isosurface"

    def execute(self, context):
        return opexec.analysis_isosurface_gen(self, context)
