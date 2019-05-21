#各コンフィグを一括で記述する
import os


def dummy():
    return

#Addon Preferences
#https://docs.blender.org/api/blender_python_api_2_67_1/bpy.types.AddonPreferences.html

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

dirpath = os.path.dirname(__file__)
dir_name = os.path.basename(dirpath)
if "_modules" in dir_name:
    dirpath = os.path.dirname(dirpath)
    dir_name = os.path.basename(dirpath)
package_name = dir_name

print("package:"+package_name)#fuijwara_toolbox
print("name:"+__name__)#fuijwara_toolbox.conf

class FujiwaraToolBoxPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = package_name

    #Property https://docs.blender.org/api/blender_python_api_2_78c_release/bpy.types.Property.html#bpy.types.Property.subtype
    """
    filepath = StringProperty(
            name="Example File Path",
            subtype='FILE_PATH',
            )
    number = IntProperty(
            name="Example Number",
            default=4,
            )
    boolean = BoolProperty(
            name="Example Boolean",
            default=False,
            )
    """

    #ヘッダー
    #スナップボタン、ピボットボタン、ビューボタン、MarvelousDesigner用フレームボタン、GLレンダユーティリティーボタン、ローカルビューボタン
    """
    _buttons = BoolProperty(
            name="ボタン",
            default=False,
            )
    """
    maintools_button = BoolProperty(
            name="メインツールズボタン",
            default=True,
            )
    snap_buttons = BoolProperty(
            name="スナップボタン",
            default=True,
            )
    pivot_buttons = BoolProperty(
            name="ピボットボタン",
            default=True,
            )
    view_buttons = BoolProperty(
            name="ビューボタン",
            default=True,
            )
    mdframe_buttons = BoolProperty(
            name="MarvelousDesigner用フレームボタン",
            default=False,
            )
    glrenderutils_buttons = BoolProperty(
            name="OpenGLレンダユーティリティーボタン",
            default=False,
            )
    localview_button = BoolProperty(
            name="ローカルビューボタン",
            default=True,
            )

    #モジュール
    #MainTools、RoomTools、ページユーティリティ、Subsurfmodelingtools、Cameratools、Greasepenciltools、QuickMeshDelDiss
    """
     = BoolProperty(
            name="",
            default=False,
            )
    """
    maintools = BoolProperty(
            name="メインツールズ",
            default=True,
            )
    roomtools = BoolProperty(
            name="RoomTools",
            default=False,
            )
    pageutils = BoolProperty(
            name="ページユーティリティ",
            default=True,
            )
    pageutils_show_load_ui = BoolProperty(
            name="ページユーティリティに「UIをロード」設定を表示する",
            default=False,
    )
    pageutils_cpurender = BoolProperty(
            name="ページユーティリティでCPUプレビューを生成する",
            default=True,
            )
    pageutils_set_res_to_bgimg_onload = BoolProperty(
            name="ファイルロード時に背景にレンダサイズをあわせる",
            default=True,
            )
    subsurfmodelingtools = BoolProperty(
            name="Subsurf Modeling Tools",
            default=False,
            )
    cameratools = BoolProperty(
            name="Camera Tools",
            default=True,
            )
    greasepenciltools = BoolProperty(
            name="Greasepencil Tools",
            default=False,
            )
    quickmeshdeldiss = BoolProperty(
           name="Quick Mesh Delete / Dissolve",
            default=False,
            )
    assetsketcherhelper = BoolProperty(
           name="Asset Sketcher Helper",
            default=False,
            )
    fjwselector = BoolProperty(
           name="FJW Selector",
            default=False,
            )
    draw_tools = BoolProperty(
           name="FJW Draw Tools",
            default=False,
            )
    group_extract = BoolProperty(
           name="Group Extract",
            default=False,
            )
    #特殊設定
    asset_manager = BoolProperty(
           name="Asset Manager",
            default=False,
            )
    assetdir = StringProperty(
            name="アセットマネージャ用ファイルパス",
            subtype='FILE_PATH',
            )
#     MarvelousDesigner_dir = StringProperty(
#             name="MarvelousDesigner作業用ディレクトリ",
#             subtype='FILE_PATH',
#             )
    script_loader = BoolProperty(
            name="FJW Script Loader",
            default=False,
            )
    SubstanceAutomationToolkit_dir = StringProperty(
            name="Substance Automation Toolkitのディレクトリ",
            subtype='FILE_PATH',
            )

    #MarvelousDesigner
    use_md7script = BoolProperty(
            name="Marvelous Designer 7のスクリプト機能を使用してシミュレーションする",
            default=False,
            )
    MarvelousDesigner_path = StringProperty(
            name="Marvelous Designer 7のexeファイル",
            subtype='FILE_PATH',
            )
    Python27lib_dir = StringProperty(
            name="Python 2.7のlibディレクトリ",
            subtype='FILE_PATH',
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="ヘッダー設定")
        layout.prop(self, "maintools_button")
        layout.prop(self, "snap_buttons")
        layout.prop(self, "pivot_buttons")
        layout.prop(self, "view_buttons")
        layout.prop(self, "mdframe_buttons")
        layout.prop(self, "glrenderutils_buttons")
        layout.prop(self, "localview_button")

        layout.label(text="モジュール表示設定")
        layout.prop(self, "maintools")
        layout.prop(self, "roomtools")
        layout.prop(self, "pageutils")
        layout.prop(self, "pageutils_show_load_ui")
        layout.prop(self, "pageutils_cpurender")
        layout.prop(self, "pageutils_set_res_to_bgimg_onload")
        layout.prop(self, "subsurfmodelingtools")
        layout.prop(self, "cameratools")
        layout.prop(self, "greasepenciltools")
        layout.prop(self, "quickmeshdeldiss")
        layout.prop(self, "assetsketcherhelper")
        layout.prop(self, "draw_tools")
        layout.prop(self, "group_extract")

        layout.label(text="特殊設定")
        layout.prop(self, "asset_manager")
        layout.prop(self, "assetdir")
        # layout.prop(self, "MarvelousDesigner_dir")
        layout.prop(self, "SubstanceAutomationToolkit_dir")
        layout.prop(self, "script_loader")
        layout.prop(self, "fjwselector")

        layout.label(text="Marvelous Desinger 7")
        layout.prop(self, "use_md7script")
        layout.prop(self, "MarvelousDesigner_path")
        layout.prop(self, "Python27lib_dir")


def get_pref():
    addon_prefs = bpy.context.user_preferences.addons[package_name].preferences
    return addon_prefs
    

# class OBJECT_OT_addon_prefs_example(Operator):
#     """Display example preferences"""
#     bl_idname = "object.addon_prefs_example"
#     bl_label = "Addon Preferences Example"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         user_preferences = context.user_preferences
#         addon_prefs = user_preferences.addons[prefname].preferences

#         info = ("Path: %s, Number: %d, Boolean %r" %
#                 (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

#         self.report({'INFO'}, info)
#         print(info)

#         return {'FINISHED'}




#maintools
maintools_vrexportdir = r"Z:\Unity\VRTest\New Unity Project\Assets"
maintools_vrexportpath = r"Z:\Unity\VRTest\New Unity Project\Assets\VRRoom.blend"

#MarvelousDesigner
MarvelousDesigner_dir = "G:" + os.sep + "MarvelousDesigner" + os.sep
os.sep + "MarvelousDesigner" + os.sep

from bpy.app.handlers import persistent
@persistent
def scene_update_post_handler(dummy):
    bpy.app.handlers.scene_update_post.remove(scene_update_post_handler)
    global MarvelousDesigner_dir
    MarvelousDesigner_dir = get_pref().MarvelousDesigner_dir




# Registration
def sub_registration():
    bpy.app.handlers.scene_update_post.append(scene_update_post_handler)
    pass

def sub_unregistration():
    pass
    

def register():
    bpy.utils.register_module(__name__)
    sub_registration()
    


def unregister():
    bpy.utils.unregister_module(__name__)
    sub_unregistration()


if __name__ == "__main__":
    register()










