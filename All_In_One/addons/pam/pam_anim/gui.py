"""PAM-anim GUI module"""

import bpy

from .. import model
from . import anim_functions


class PamAnimDataPane(bpy.types.Panel):
    """A panel for loading model data"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Model data"
    bl_category = "PAM Animate"

    def draw(self, context):
        layout = self.layout
        row = layout.column()
        row.prop(context.scene.pam_anim_data, "simulationData")

class PamAnimAnimPane(bpy.types.Panel):
    """A panel for selecting the frames and speed"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Animation"
    bl_category = "PAM Animate"

    def draw(self, context):
        layout = self.layout

        options = bpy.context.scene.pam_anim_animation

        row = layout.row()
        col = row.column()
        sub = col.column(align=True)
        sub.label(text="Frames:")
        sub.prop(options, "startFrame")
        sub.prop(options, "endFrame")

        row = layout.row()
        col = row.column()
        sub = col.column(align=True)
        sub.label(text="Time:")
        sub.prop(options, "startTime")
        sub.prop(options, "endTime")

        row = layout.row()
        row.prop(options, "connNumber")

        row = layout.row()
        row.prop(options, "showPercent")

class PamAnimMaterialPane(bpy.types.Panel):
    """A panel for choosing materials"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Material"
    bl_category = "PAM Animate"

    def draw(self, context):
        layout = self.layout

        options = bpy.context.scene.pam_anim_material

        row = layout.row()
        row.prop(bpy.context.scene.pam_anim_material, 'materialOption', expand=True)

        if(options.materialOption == "CUSTOM"):
            row = layout.row()
            row.prop_search(context.scene.pam_anim_material, "material", bpy.data, "materials")

        row = layout.row()
        row.prop_search(options, 'pathMaterial', bpy.data, 'materials')

class PamAnimPathsPane(bpy.types.Panel):
    """A panel for choosing how to display paths"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Paths"
    bl_category = "PAM Animate"

    def draw_header(self, context):
        options = bpy.context.scene.pam_anim_mesh

        self.layout.prop(options, "animPaths", text="")

    def draw(self, context):
        layout = self.layout

        options = bpy.context.scene.pam_anim_mesh

        layout.active = options.animPaths

        row = layout.row()
        row.prop_search(options, 'mesh', bpy.data, 'objects')

        row = layout.row()
        row.prop(options, 'path_bevel_resolution')

        row = layout.row()
        row.label("Orientation:")

        row = layout.row()
        row.prop(options, 'orientationType', expand=True)

        if(options.orientationType == 'OBJECT'):
            row = layout.row()
            row.prop_search(options, 'orientationObject', bpy.data, "objects")

class PamAnimSpikesPane(bpy.types.Panel):
    """A panel for choosing how to display spikes"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Spikes"
    bl_category = "PAM Animate"

    def draw_header(self, context):
        options = bpy.context.scene.pam_anim_mesh

        self.layout.prop(options, "animSpikes", text="")

    def draw(self, context):
        layout = self.layout

        options = bpy.context.scene.pam_anim_mesh

        row = layout.row()
        row.prop_search(options, 'neuron_object', bpy.data, 'objects')

        row = layout.row()
        col = row.column()
        sub = col.column(align=True)
        sub.prop(options, 'spikeScale')
        sub.prop(options, 'spikeFadeout')

        row = layout.row()
        row.prop(options, 'spikeUseLayerColor')

        row = layout.row()
        row.active = not options.spikeUseLayerColor
        row.prop(options, 'spikeColor')

        row = layout.row()
        row.operator("pam_anim.generate_spiking_texture")

class PamAnimLayerPane(bpy.types.Panel):
    """A panel for choosing layer colors"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Color Simulation"
    bl_category = "PAM Animate"

    def draw_header(self, context):
        self.layout.prop(context.scene.pam_anim_material, "simulate_colors", text = "")
    def draw(self, context):
        layout = self.layout

        options = bpy.context.scene.pam_anim_material

        row = layout.row()

        row.prop(context.scene, "pam_anim_simulation")

        anim_functions.labelControllerDict[context.scene.pam_anim_simulation].draw(layout, context)

        row = layout.row()
        row.operator("pam_anim.recolor_spikes")

class PamAnimGeneratePanel(bpy.types.Panel):
    """A panel for all operators for pam_anim"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Generate"
    bl_category = "PAM Animate"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("pam_anim.generate")
        row = layout.row()
        row.operator("pam_anim.clear_pamanim")

class LayerSelectionList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.layerName)
        layout.prop(item, "layerGenerate", text = "")

