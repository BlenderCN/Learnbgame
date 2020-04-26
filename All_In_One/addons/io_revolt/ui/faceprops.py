import bpy
from ..common import *
from .widgets import *

class RevoltFacePropertiesPanel(bpy.types.Panel):
    bl_label = "Face Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Re-Volt"

    selection = None
    selected_face_count = None

    def draw_header(self, context):
        self.layout.label("", icon="FACESEL_HLT")

    def draw(self, context):
        props = context.scene.revolt

        if props.face_edit_mode == "prm":
            prm_edit_panel(self, context)
        elif props.face_edit_mode == "ncp":
            ncp_edit_panel(self, context)


def prm_edit_panel(self, context):
    """  """
    obj = context.object
    layout = self.layout

    props = context.scene.revolt

    mesh = obj.data
    meshprops = obj.data.revolt
    bm = get_edit_bmesh(obj)
    flags = (bm.faces.layers.int.get("Type") or
             bm.faces.layers.int.new("Type"))
    if (self.selected_face_count is None or
            self.selected_face_count != mesh.total_face_sel):
        self.selected_face_count = mesh.total_face_sel
        self.selection = [face for face in bm.faces if face.select]

    # Counts the number of faces the flags are set for
    count = [0] * len(FACE_PROPS)
    for face in self.selection:
        for x in range(len(FACE_PROPS)):
            if face[flags] & FACE_PROPS[x]:
                count[x] += 1

    row = layout.row()
    row.label("Properties:")

    row  = layout.row()
    col = row.column(align=True)
    col.prop(meshprops, "face_double_sided",
        text="{}: Double sided".format(count[1]))
    col.prop(meshprops, "face_translucent",
        text="{}: Translucent".format(count[2]))
    col.prop(meshprops, "face_mirror",
        text="{}: Mirror".format(count[3]))
    col.prop(meshprops, "face_additive",
        text="{}: Additive blending".format(count[4]))
    col.prop(meshprops, "face_texture_animation",
        text="{}: Texture animation".format(count[5]))
    col.prop(meshprops, "face_no_envmapping",
        text="{}: No EnvMap".format(count[6]))
    if meshprops.face_envmapping:
        split = col.split(percentage=.7)
        scol = split.column(align=True)
        scol.prop(meshprops, "face_envmapping",
        text="{}: EnvMap".format(count[7]))
        scol = split.column(align=True)
        scol.prop(meshprops, "face_env", text="")
    else:
        col.prop(meshprops, "face_envmapping",
        text="{}: EnvMap".format(count[7]))

    col.prop(meshprops, "face_cloth",
        text="{}: Cloth effect".format(count[8]))
    col.prop(meshprops, "face_skip",
        text="{}: Do not export".format(count[9]))
    col = row.column(align=True)
    col.scale_x = 0.15
    col.operator("faceprops.select", text="sel").prop = FACE_DOUBLE
    col.operator("faceprops.select", text="sel").prop = FACE_TRANSLUCENT
    col.operator("faceprops.select", text="sel").prop = FACE_MIRROR
    col.operator("faceprops.select", text="sel").prop = FACE_TRANSL_TYPE
    col.operator("faceprops.select", text="sel").prop = FACE_TEXANIM
    col.operator("faceprops.select", text="sel").prop = FACE_NOENV
    col.operator("faceprops.select", text="sel").prop = FACE_ENV
    col.operator("faceprops.select", text="sel").prop = FACE_CLOTH
    col.operator("faceprops.select", text="sel").prop = FACE_SKIP

    if props.use_tex_num:
        row = layout.row()
        row.label("Texture:")
        row = layout.row()
        if len(self.selection) > 1:
            if context.object.data.revolt.face_texture == -2:
                row.prop(context.object.data.revolt, "face_texture",
                    text="Texture (different numbers)")
            else:
                row.prop(context.object.data.revolt, "face_texture",
                    text="Texture (set for all)")
        elif len(self.selection) == 0:
            row.prop(context.object.data.revolt, "face_texture",
                text="Texture (no selection)")
        else:
            row.prop(context.object.data.revolt, "face_texture",
                text="Texture".format(""))
        row.active = context.object.data.revolt.face_texture != -3


def ncp_edit_panel(self, context):
    props = context.scene.revolt
    obj = context.object
    meshprops = context.object.data.revolt
    layout = self.layout

    mesh = obj.data
    bm = get_edit_bmesh(obj)
    flags = (bm.faces.layers.int.get("NCPType") or
             bm.faces.layers.int.new("NCPType"))
    if (self.selected_face_count is None or
            self.selected_face_count != mesh.total_face_sel):
        self.selected_face_count = mesh.total_face_sel
        self.selection = [face for face in bm.faces if face.select]

    # Counts the number of faces the flags are set for
    count = [0] * len(NCP_PROPS)
    for face in self.selection:
        for x in range(len(NCP_PROPS)):
            if face[flags] & NCP_PROPS[x]:
                count[x] += 1

    row = layout.row()
    row.label("Properties:")
    row  = self.layout.row()
    col = row.column(align=True)
    col.prop(meshprops, "face_ncp_double",
        text="{}: Double sided".format(count[1]))
    col.prop(meshprops, "face_ncp_no_skid",
        text="{}: No Skid Marks".format(count[5]))
    col.prop(meshprops, "face_ncp_oil",
        text="{}: Oil".format(count[6]))
    col.prop(meshprops, "face_ncp_object_only",
        text="{}: Object Only".format(count[2]))
    col.prop(meshprops, "face_ncp_camera_only",
        text="{}: Camera Only".format(count[3]))
    col.prop(meshprops, "face_ncp_nocoll",
        text="{}: No Collision".format(count[7]))


    col = row.column(align=True)
    col.scale_x = 0.15
    col.operator("ncpfaceprops.select", text="sel").prop = NCP_DOUBLE
    col.operator("ncpfaceprops.select", text="sel").prop = NCP_NO_SKID
    col.operator("ncpfaceprops.select", text="sel").prop = NCP_OIL
    col.operator("ncpfaceprops.select", text="sel").prop = NCP_OBJECT_ONLY
    col.operator("ncpfaceprops.select", text="sel").prop = NCP_CAMERA_ONLY
    col.operator("ncpfaceprops.select", text="sel").prop = NCP_NOCOLL

    row = layout.row()
    row.label("Material:")

    # Warns if texture mode is not enabled
    widget_texture_mode(self)

    row = layout.row(align=True)
    col = row.column(align=True)
    # Dropdown list of the current material
    col.prop(meshprops, "face_material", text="Set")
    col = row.column(align=True)
    col.scale_x = 0.15
    col.operator("ncpmaterial.select")

    # Dropdown list for selecting materials
    row = layout.row()
    row.prop(props, "select_material", text="Select all")