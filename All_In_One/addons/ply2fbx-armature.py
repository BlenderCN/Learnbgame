import bpy
import os

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.

# Copyright (C) 2018 YuTanaka
# v1.0.4
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import Operator

bl_info = {
    "name": "PLY2FBXエクスポーター",
    "author": "YuTanaka",
    "version": (1, 0, 4),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "description": "PLYファイルとアーマチュアの自動ウェイトやテクスチャ作成をしてFBXエクスポートするアドオン",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "https://am1tanaka.github.io/ply2fbx/",
    "tracker_url": "https://github.com/am1tanaka/ply2fbx/issues",
    "category": "Import-Export",
}


class ImportPLY(bpy.types.Operator):
    """
    PLYをインポートして、 重複頂点を結合して、左下の倍率でスケーリングします。
    """
    bl_idname = "import.ply"
    bl_label = "Import PLY"

    # ImportHelper mixin class uses this
    filename_ext = ".ply"

    filter_glob = StringProperty(
        default="*.ply",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = FloatProperty(
        name="Scale",
        description="Import Scaling",
        default=0.25,
    )

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.import_mesh.ply(filepath=self.filepath)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        bpy.ops.mesh.remove_doubles()

        # 3D Cursor to zero
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.context.space_data.pivot_point = 'CURSOR'

        # scaling
        bpy.ops.transform.resize(value=(self.use_setting, self.use_setting, self.use_setting), constraint_axis=(
            False, False, False), constraint_orientation='GLOBAL', proportional_edit_falloff='SMOOTH', proportional_size=1)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class View3DPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

####


class AutoWeight(bpy.types.Operator):
    """
    アーマチュア(BaseArmature.blend)と メッシュを自動的にウェイト設定します。
     事前にアーマチュアとメッシュを読み込んで重ねてから実行してください。
    """
    bl_idname = "armature.autoweight"
    bl_label = "Auto Weight"

    @classmethod
    def poll(cls, context):
        # armature and mesh neet to proc
        arm = [True for x in bpy.data.objects if x.type == 'ARMATURE']
        mesh = [True for x in bpy.data.objects if x.type == 'MESH']
        return (len(arm) > 0) and (len(mesh) > 0)

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.select_by_type(type='ARMATURE', extend=True)

        SetActiveObject('ARMATURE')

        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        return {'FINISHED'}

####


def SetActiveObject(type):
    for obj in bpy.data.objects:
        if (obj.type == type):
            bpy.context.scene.objects.active = obj


def GetFileName(fpath):
    return os.path.splitext(bpy.path.basename(fpath))[0]


def GetFilePath(fpath, fext):
    fdir = os.path.dirname(fpath)
    return os.path.join(fdir, bpy.path.ensure_ext(filepath=GetFileName(fpath), ext=fext))


class ExportFBX(bpy.types.Operator):
    """
    PLYメッシュへのマテリアル設定と、 頂点カラーのテクスチャーを生成して、
    指定の場所とファイル名でFBXとPNGを出力します。
    """
    bl_idname = "export.fbxtexture"
    bl_label = "Export FBX and Texture"

    filename_ext = ".fbx"

    filter_glob = StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    width = IntProperty(
        name="Texture Width",
        description="Texture Width",
        min=1, max=4096,
        default=512,
    )
    height = IntProperty(
        name="Texture Height",
        description="Texture Height",
        min=1, max=4096,
        default=512,
    )
    # ここから追加部分
    apply_unit_scale = BoolProperty(
        name="Apply Unit Scale",
        description="Apply Unit Scale"
    )

    back_space_transform = BoolProperty(
        name="Back Space Transform",
        description="Back Space Transform"
    )
    # ここまで追加部分
    object_types = EnumProperty(
        name="Object Types",
        options={'ENUM_FLAG'},
        items=(('EMPTY', "Empty", ""),
               ('CAMERA', "Camera", ""),
               ('LAMP', "Lamp", ""),
               ('ARMATURE', "Armature",
                "WARNING: not supported in dupli/group instances"),
               ('MESH', "Mesh", ""),
               ('OTHER', "Other", "Other geometry types, like curve, metaball, etc. (converted to meshes)"),
               ),
        description="Which kind of object to export",
        default={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
    )

    @classmethod
    def poll(cls, context):
        # armature and mesh neet to proc
        mesh = [True for x in bpy.data.objects if x.type == 'MESH']
        return (len(mesh) > 0)

    def execute(self, context):
        # テクスチャ生成
        self.makeTexture(context)

        # マテリアルの作成と設定
        self.makeMaterial(context)

        # FBXエクスポート　引数追加
        print(GetFilePath(self.filepath, ".fbx"))
        bpy.ops.export_scene.fbx(
            filepath=GetFilePath(self.filepath, ".fbx"),
            object_types=self.object_types,
            apply_unit_scale=self.apply_unit_scale,
            bake_space_transform=self.back_space_transform
        )

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def makeTexture(self, context):
        # make image for texture
        fname = GetFileName(self.filepath)
        image = bpy.data.images.new(
            name=fname, width=self.width, height=self.height)

        # unwrap
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_by_type(type='MESH')
        SetActiveObject('MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.uv.smart_project(island_margin=0.06)

        # bake bake_type='VERTEX_COLORS', bake_margin = 4
        bpy.context.scene.render.bake_type = 'VERTEX_COLORS'
        bpy.context.scene.render.bake_margin = 4
        bpy.data.screens['UV Editing'].areas[1].spaces[0].image = image
        bpy.ops.object.bake_image()

        # save PNG
        pngpath = os.path.dirname(self.filepath)
        pngpath = os.path.join(pngpath, bpy.path.ensure_ext(
            filepath=GetFileName(self.filepath), ext='.png'))
        image.filepath_raw = pngpath
        image.file_format = "PNG"
        image.save()

    def makeMaterial(self, context):
        objname = GetFileName(self.filepath)

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_by_type(type='MESH')

        mat = bpy.data.materials.new(objname)
        mat.diffuse_color = (1, 1, 1)
        bpy.context.object.active_material = mat
        tex = bpy.data.textures.new(objname, type='IMAGE')
        bpy.context.object.active_material.active_texture = tex

        tex.image = bpy.data.screens['UV Editing'].areas[1].spaces[0].image


class PanelPlyTool(View3DPanel, bpy.types.Panel):
    """Ply Convert Tool"""
    bl_idname = "VIEW3D_PT_ply_tool"
    bl_label = "Ply Tool"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator(ImportPLY.bl_idname, text="Import PLY")

        layout.operator(AutoWeight.bl_idname, text="Auto Weight")

        layout.operator(ExportFBX.bl_idname, text="Export FBX and Texture")

####


def register():
    bpy.utils.register_class(PanelPlyTool)
    bpy.utils.register_class(ImportPLY)
    bpy.utils.register_class(AutoWeight)
    bpy.utils.register_class(ExportFBX)


def unregister():
    bpy.utils.unregister_class(PanelPlyTool)
    bpy.utils.unregister_class(ImportPLY)
    bpy.utils.unregister_class(AutoWeight)
    bpy.utils.unregister_class(ExportFBX)


if __name__ == "__main__":
    register()
