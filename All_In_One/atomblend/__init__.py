# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   __init__.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# AtomBlend addon initialisation and UI definition
# =============================================================================

import sys
#sys.path.append("/home/user/Blender/2.72/scripts/addons/atomblend/docs")

#__all__ = ['properties', 'operators', 'drawing']

# === Addon info ===
bl_info = {
        "name": "AtomBlend",
        "description": "Atom Probe data visualisation plugin",
        "author": "Varvara Efremova",
        "version": (0, 9),
        "blender": (2, 7, 0),
        "location": "View3D tools panel",
        "warning": "", # used for warning icon and text in addons panel
        "wiki_url": "https://bitbucket.org/varvara/atomblend/wiki/Home",
        "category": "3D View"}

# === Addon reload support ===
# Try accessing package var, if it's there reload everything
if 'bpy' in locals():
    import imp
    if 'properties' in locals():
        imp.reload(properties)
        print("Reloaded properties")
    if 'operators' in locals():
        imp.reload(operators)
        print("Reloaded operators")
    print("Reloaded classes")



import bpy
from bpy.types import Panel
from . import operators
from .properties import VIEW3D_PT_pos_panel_props

# === Panel UI ===

# === Mixin classes ===
class AtomBlendPanel():
    """Mixin parent class for AtomBlend common properties"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    # Only display in object mode
    @classmethod
    def poll(cls, context):
        mode = context.mode
        return mode == 'OBJECT'

class ImportPanel(AtomBlendPanel):
    """Mixin for import/data load panel"""
    bl_category = "AP Import"

class VisualisationPanel(AtomBlendPanel):
    """Mixin parent class for common properties"""
    bl_category = "AP Visualisation"

class AnalysisPanel(AtomBlendPanel):
    """Mixin parent class for common properties"""
    bl_category = "AP Analysis"



# === View definitions ===

# === Import panel ===
class VIEW3D_PT_data_bake(ImportPanel, Panel):
    """Bake to object panel"""
    bl_label = "Import data"

    def draw(self, context):
        layout = self.layout
        props = context.scene.pos_panel_props

        col = layout.column(align=True)
        subrow = col.row(align=True)
        subrow.prop(props, "pos_filename")
        subrow.operator("atomblend.import_pospath")
        subrow = col.row(align=True)
        subrow.prop(props, "rng_filename")
        subrow.operator("atomblend.import_rngpath")
        col.operator("atomblend.load_posrng")

        col = layout.column(align=True)
        col.label(text="Select file and plot type:")
        col.prop(props, "apdata_list", text="")
        col.prop(props, "plot_type", text="")
        col.operator("atomblend.bake_button")

        row = layout.row()
        row.operator("atomblend.clear_button")



# === Visualisation panel ===
class VIEW3D_PT_data_visualisation(VisualisationPanel, Panel):
    """Visualisation panel viewed in object mode with an AtomBlend-generated dataset selected"""
    bl_label = "Visualisation"

    def draw(self, context):
        layout = self.layout
        props = context.scene.pos_panel_props

        col = layout.column(align=True)

        obj = context.object

        if obj is None or obj.datatype != 'DATA':
            col.label(text="[no dataset selected]")
        elif obj.vistype == 'HALO' and has_halo(obj):
            #--- halo material ---
            # active object already has applied halo material, show edit props
            col.label(text="Edit halo material:")
            mat = context.object.active_material
            halo = mat.halo

            subrow = col.row(align=True)
            subrow.prop(mat, "diffuse_color", text="")
            subrow.prop(halo, "size")
            col.operator("atomblend.remove_halomat")
        elif obj.vistype == 'DUPLI' and has_duplivert(obj):
            #--- duplivert ---
            # active object has duplivert applied, show edit props
            dupli = obj.children[0]
            mat = dupli.active_material

            col.label(text="Edit vertex object:")
            subrow = col.row(align=True)
            subrow.prop(mat, "diffuse_color", text="")
            subrow.operator("atomblend.scale_child")
            col.operator("atomblend.remove_duplivert")
        elif obj.datatype == 'DATA':
            # no visualisation applied yet
            col.operator("atomblend.add_halomat")
            col.operator("atomblend.add_duplivert")

        # === Boundbox ===
        row = layout.row()
        col = layout.column(align=True)

        if (obj is not None) and obj.datatype == 'BOUND' and is_bound(obj):
            # boundbox selected
            mod = obj.modifiers[0]
            mat = obj.active_material
            # TODO add remove boundbox button
            col.label(text="Edit bounding box:")
            col.prop(mod, "thickness", text="Thickness")
            col.prop(mat, "diffuse_color", text="")
        else:
            col.operator("atomblend.add_bound_box")
            col.prop(props, "boundbox_padding")
            #boundbox_props = col.operator("atomblend.add_bound_box")
            #col.prop(boundbox_props, "padding")
            #bpy.ops.atomblend.add_bound_box.padding

class VIEW3D_PT_data_render(VisualisationPanel, Panel):
    """Final touches"""
    bl_label = "Final touches"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        obj = context.object

        split = layout.split()

        #--- camera ---
        col = split.column(align=True)
        col.operator("atomblend.add_camera")
        col.operator("atomblend.make_camera_active")
        col.operator("atomblend.position_cam")

        #--- lamp ---
        col = split.column(align=True)
        col.operator("atomblend.add_lamp")
        if obj is not None and obj.type == 'LAMP':
            lamp = obj.data
            col.prop(lamp, "color", text="")

        #--- background/render settings ---
        world = context.scene.world
        render = context.scene.render

        row = layout.row()
        col = layout.column(align=True)
        col.label(text="Background:")
        col.prop(world, "horizon_color", text="")
        col.prop(render, "alpha_mode", text="")

        row = layout.row()
        row.operator("render.render", text="Render", icon='RENDER_STILL')

class VIEW3D_PT_data_animation(VisualisationPanel, Panel):
    """Animation operators and settings"""
    bl_label = "Animation"

    def draw(self, context):
        layout = self.layout
        props = context.scene.pos_panel_props

        col = layout.column(align=True)
        col.operator("atomblend.animation_add")
        subrow = col.row(align=True)
        subrow.prop(props, "animation_offsetx", text="X offset")
        subrow.prop(props, "animation_offsetz", text="Z offset")
        subrow = col.row(align=True)
        subrow.prop(props, "animation_time", text="Time")
        subrow.prop(props, "animation_scale", text="Scale")
        subrow = col.row(align=True)
        subrow.prop(props, "animation_fps", text="FPS")
        subrow.prop(props, "animation_clip_dist", text="Clip")

        #row = layout.row()
        #row.operator("render.render", text="Render animation", icon='RENDER_ANIMATION')



# === Analysis Panel ===
class VIEW3D_PT_data_analysis(AnalysisPanel, Panel):
    """Analysis operators and settings"""
    bl_label = "Analysis"

    def draw(self, context):
        layout = self.layout
        props = context.scene.pos_panel_props

        col = layout.column(align=True)
        col.operator("atomblend.analysis_isosurf")
        subrow = col.row(align=True)
        subrow.prop(props, "analysis_isosurf_rangefrom", text="Isorange")
        #subrow.prop(props, "analysis_isosurf_rangeto", text="")

# === Helper functions ===
def has_halo(obj):
    mat = obj.active_material
    return (mat is not None) and (mat.type == 'HALO')

def has_duplivert(obj):
    if obj is None:
        return False
    return obj.children and (obj.dupli_type == 'VERTS')

def is_bound(obj):
    if obj is None:
        return False
    mat = obj.active_material
    mods = obj.modifiers
    return mods and (mat is not None)



# === Registration ===
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.pos_panel_props = bpy.props.PointerProperty(type=VIEW3D_PT_pos_panel_props)

    print("AtomBlend registered successfully!")

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.pos_panel_props

if __name__ == "__main__":
    register()
