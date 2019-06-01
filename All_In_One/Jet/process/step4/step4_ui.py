import bpy
from ... common_utils import apply_to_selected, any_mesh_obj_selected, get_hotkey
from .step4_utils import SharpToSeam, Unwrap, ManageSeam, triangulate, is_texture_atlas_enabled, enable_texture_atlas, \
    select_objs_no_uvs


def arrange_uvs(layout):
    layout.operator("uv.average_islands_scale", text="Average Islands Scale")
    layout.operator("uv.pack_islands", text="Pack Islands")
    layout.operator("scene.ms_remove_other_uv", text="Remove Other UVs")
    layout.label("-Advanced Packing (Shot Packer Addon)")


def texture_atlas(layout):
    if not is_texture_atlas_enabled():
        layout.label("Texture Atlas is not enabled", icon="ERROR")
        layout.operator("jet_texture_atlas_on.btn", text="Enable Texture Atlas")
    else:
        layout.operator("scene.ms_add_lightmap_group", text="Start Texture Atlas").name = "TextureAtlas_Jet"
        layout.operator("object.ms_run", text="Start Manual Unwrap")
        arrange_uvs(layout)
        layout.operator("object.ms_run_remove", text="Finish Manual Unwrap")


def uv_panel(layout, context):
    col = layout.column(align=True)
    col.operator("jet_sharp_to_seam.btn", text="Mark Sharp as Seam")

    text = "Disable" if context.scene.Jet.tag.seam else "Enable"
    col.prop(context.scene.Jet.tag, "seam",
             text=text + " Seam Tagging  - " + get_hotkey(context, "mesh.shortest_path_pick"),
             icon="BLANK1")

    row = col.row(align=True)
    row.operator("jet_seam.btn", text="Mark Seam").mark = True
    row.operator("jet_seam.btn", text="Clear Seam").mark = False

    row = layout.row()
    col = row.column(align=True)
    col.operator("jet_unwrap.btn", text="Unwrap")
    col.operator("jet_no_uvs.btn", text="Select objects without UVs")

    row = layout.row()
    col = row.column(align=True)
    texture_atlas(col)

    row = layout.row()
    row.operator("jet_triangulate.btn", text="Triangulate")


#Panel
class VIEW3D_PT_jet_step4(bpy.types.Panel):
    bl_label = "4. UVs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Jet"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.Jet.info, "uvs", text="", icon="INFO")

    def draw(self, context):
        uv_panel(self.layout, context)


#Panel UV Editor
class VIEW3D_PT_jet_step4_UVEditor(bpy.types.Panel):
    bl_label = "4. UVs"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Jet"

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.Jet.info, "uvs", text="", icon="INFO")

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        uv_panel(self.layout, context)


# Operators
class VIEW3D_OT_jet_sharp_to_seam(bpy.types.Operator):
    bl_idname = "jet_sharp_to_seam.btn"
    bl_label = "Sharp to Seam"
    bl_description = "Mark Sharp edges as Seam"

    def execute(self, context):
        apply_to_selected(context, SharpToSeam)
        return {'FINISHED'}


class VIEW3D_OT_jet_unwrap(bpy.types.Operator):
    bl_idname = "jet_unwrap.btn"
    bl_label = "Unwrap"
    bl_description = "Unwrap"

    def execute(self, context):
        obj = context.active_object
        if obj is not None and obj.type == "MESH" and obj.mode == 'EDIT':
            bpy.ops.wm.call_menu(name="VIEW3D_MT_uv_map")
        else:
            apply_to_selected(context, Unwrap)
        return {'FINISHED'}


class VIEW3D_OT_jet_seam(bpy.types.Operator):
    bl_idname = "jet_seam.btn"
    bl_label = "Seam"
    bl_description = "Manage Seam"

    mark = bpy.props.BoolProperty(default=True)

    def execute(self, context):
        ManageSeam(context, self.mark)
        return {'FINISHED'}


class VIEW3D_OT_jet_triangulate(bpy.types.Operator):
    bl_idname = "jet_triangulate.btn"
    bl_label = "Triangulate"
    bl_description = "Triangulate"

    def execute(self, context):
        apply_to_selected(context, triangulate)
        return {'FINISHED'}


class VIEW3D_OT_jet_texture_atlas_on(bpy.types.Operator):
    bl_idname = "jet_texture_atlas_on.btn"
    bl_label = "EnableTextureAtlas"
    bl_description = "Enable Texture Atlas Addon"

    def execute(self, context):
        enable_texture_atlas()
        return {'FINISHED'}


class VIEW3D_OT_jet_no_uvs(bpy.types.Operator):
    bl_idname = "jet_no_uvs.btn"
    bl_label = "Select objects without UVs"
    bl_description = "Select objects without UVs"

    def execute(self, context):
        select_objs_no_uvs(context)
        return {'FINISHED'}


