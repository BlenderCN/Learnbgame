import os

import bpy

from .pbr_utils import PbrSettings
from . import pman
from . import operators

class PandaButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'PANDA'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine in cls.COMPAT_ENGINES


class PandaRender_PT_project(PandaButtonsPanel, bpy.types.Panel):
    bl_label = "Project Settings"
    bl_context = "render"

    def draw_with_config(self, context, _config):
        layout = self.layout
        project_settings = context.scene.panda_project

        layout.prop(project_settings, 'project_name')
        layout.prop(project_settings, 'renderer')
        layout.prop(project_settings, 'pbr_materials')
        layout.prop(project_settings, 'python_binary')
        layout.operator(operators.UpdateProject.bl_idname)


    def draw_no_config(self, _context):
        layout = self.layout
        layout.label(text="No config file detected")

    def draw(self, context):
        confdir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None
        if pman.config_exists(confdir):
            self.draw_with_config(context, pman.get_config(confdir))
        else:
            self.draw_no_config(context)

        layout = self.layout
        layout.operator(operators.CreateProject.bl_idname)
        layout.operator(operators.SwitchProject.bl_idname)


class PandaRender_PT_build(PandaButtonsPanel, bpy.types.Panel):
    bl_label = "Build Settings"
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        confdir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None
        return PandaButtonsPanel.poll(context) and pman.config_exists(confdir)

    def draw(self, context):
        layout = self.layout
        project_settings = context.scene.panda_project

        layout.prop(project_settings, 'asset_dir')
        layout.prop(project_settings, 'export_dir')
        layout.operator(operators.BuildProject.bl_idname)


class PandaRender_PT_run(PandaButtonsPanel, bpy.types.Panel):
    bl_label = "Run Settings"
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        confdir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else None
        return PandaButtonsPanel.poll(context) and pman.config_exists(confdir)

    def draw(self, context):
        layout = self.layout
        project_settings = context.scene.panda_project

        layout.prop(project_settings, 'auto_save')
        layout.prop(project_settings, 'auto_build')
        layout.operator(operators.RunProject.bl_idname)


class Panda_PT_context_material(PandaButtonsPanel, bpy.types.Panel):
    bl_label = ""
    bl_context = "material"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return (context.material or context.object) and PandaButtonsPanel.poll(context)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data
        is_sortable = len(ob.material_slots) > 1

        if ob:
            rows = 1
            if is_sortable:
                rows = 4

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.65)

        if ob:
            split.template_ID(ob, "active_material", new="material.new")
            row = split.row()

            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()

class PandaMaterial_PT_basic(PandaButtonsPanel, bpy.types.Panel):
    bl_label = "Basic Material"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material and PandaButtonsPanel.poll(context)

    def draw(self, context):
        layout = self.layout
        mat = context.material

        layout.label(text="Diffuse:")
        split = layout.split()
        col = split.column()
        col.prop(mat, "diffuse_color", text="")
        col = split.column()
        col.prop(mat, "diffuse_intensity", text="Intensity")

        layout.label(text="Specular:")
        split = layout.split()
        col = split.column()
        col.prop(mat, "specular_color", text="")
        col = split.column()
        col.prop(mat, "specular_intensity", text="Intensity")
        layout.prop(mat, "specular_hardness")

        layout.prop(mat, "emit", text="Emit")
        layout.prop(mat, "ambient", text="Ambient")


class PandaCamera_PT_lens(PandaButtonsPanel, bpy.types.Panel):
    bl_label = "Lens"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.camera and PandaButtonsPanel.poll(context)

    def draw(self, context):
        layout = self.layout

        camera = context.camera

        layout.prop(camera, "type", text="")

        if camera.type == "PERSP":
            split = layout.split()
            col = split.column()
            col.prop(camera, "lens")
            col = split.column()
            col.prop(camera, "lens_unit", text="")
        elif camera.type == "ORTHO":
            layout.prop(camera, "ortho_scale")
        else:
            layout.label("Not supported")


class PandaPhysics_PT_add(PandaButtonsPanel, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return PandaButtonsPanel.poll(context) and context.object

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj.rigid_body:
            layout.operator('rigidbody.object_remove', text="Remove Rigid Body Physics")
        else:
            layout.operator('rigidbody.object_add', text="Add Rigid Body Physics")

def get_panels():
    panels = [
        "DATA_PT_camera_display",
        "DATA_PT_camera_safe_areas",
        "DATA_PT_context_lamp",
        "DATA_PT_lamp",
        "DATA_PT_context_mesh",
        "DATA_PT_normals",
        "DATA_PT_texture_space",
        "DATA_PT_vertex_groups",
        "DATA_PT_shape_keys",
        "DATA_PT_uv_texture",
        "DATA_PT_vertex_colors",
        "DATA_PT_customdata",
        "WORLD_PT_preview",
        "WORLD_PT_world",
        "TEXTURE_PT_context_texture",
        "TEXTURE_PT_preview",
        "TEXTURE_PT_colors",
        "TEXTURE_PT_image",
        "TEXTURE_PT_image_sampling",
        "TEXTURE_PT_image_mapping",
        "TEXTURE_PT_mapping",
        "TEXTURE_PT_influence",
        "PHYSICS_PT_rigid_body",
        "PHYSICS_PT_rigid_body_collisions",
    ]

    return [getattr(bpy.types, p) for p in panels if hasattr(bpy.types, p)]


def register():
    for panel in get_panels():
        panel.COMPAT_ENGINES.add('PANDA')

    if not hasattr(bpy.types.Material, 'pbr_export_settings'):
        bpy.types.Material.pbr_export_settings = bpy.props.PointerProperty(type=PbrSettings)


def unregister():
    for panel in get_panels():
        if 'PANDA' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('PANDA')

    if hasattr(bpy.types.Material, 'pbr_export_settings'):
        del bpy.types.Material.pbr_export_settings
