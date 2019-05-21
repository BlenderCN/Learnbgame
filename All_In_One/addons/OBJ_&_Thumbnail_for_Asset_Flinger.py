

bl_info = {
    'name': 'OBJ & Thumbnail for Asset Flinger',
    'description': '"create OBJ & Thumbnail for Asset Flinger addon"',
    'author': 'bookyakuno',
    'version': (1,1),
    'blender': (2, 76, 0),
    'warning': "",
    'location': 'View3D > Tool Shelf > Create > Asset Flinger OBJ & Thumbnail',
    'category': 'Export'
}



# # # # # # # # インポート
################################################################

import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.app.handlers import persistent
from os.path import dirname, exists, join
from bpy.path import basename
from os import mkdir, listdir
from re import findall


import subprocess, os, bpy
from bpy.types import Operator, AddonPreferences, Panel
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from sys import platform as _platform
import bpy.utils.previews

################################################################
# # # # # # # #

################################################################
# # # # # # # #


# # # # # # # # アドオン設定でのパス
################################################################

class assetflinger_objPreferences(AddonPreferences):
    bl_idname = __name__



    temp_folder = StringProperty(
            name="Your Library",
            subtype='FILE_PATH',
            )


    def draw(self, context):
        layout = self.layout

        layout.prop(self, "temp_folder")







# ===============================================================

# ===============================================================

def main(context):
    for ob in context.scene.objects:
        print(ob)


class save_thumbnail(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.save_thumbnail"
    bl_label = "save thumbnail"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        
        
        


        # # # # # # # # レンダー設定を保存
        ################################################################

        old_path = bpy.context.scene.render.filepath
        old_fileformat = bpy.context.scene.render.image_settings.file_format
        old_extension = bpy.context.scene.render.use_file_extension
        old_x = bpy.context.scene.render.resolution_x
        old_y = bpy.context.scene.render.resolution_y
        old_percentage = bpy.context.scene.render.resolution_percentage
        old_aspect_x = bpy.context.scene.render.pixel_aspect_x
        old_aspect_y = bpy.context.scene.render.pixel_aspect_y

        ################################################################
        # # # # # # # # レンダー設定を保存

        
#         # # # # # # # #  Blendファイルの保存を必要とする
# 
#         # path to the folder
#         file_path = bpy.data.filepath
#         file_name = bpy.path.display_name_from_filepath(file_path)
#         file_ext = '.blend'
#         file_dir = file_path.replace(file_name+file_ext, '')

        mainScreen = bpy.context.screen

        #current scene
        scene = mainScreen.scene 
        #set render settings
        scene.render.resolution_x = 128
        scene.render.resolution_y = 128
        scene.render.resolution_percentage = 100



        #render from view (set view_context = False for the camera render)
        bpy.ops.render.opengl(view_context = True)





        # # # # # # # #
        ################################################################

        ################################################################
        
        rndr = scene.render
#         original_format = rndr.image_settings.file_format
# 
#         format = rndr.image_settings.file_format = scene.auto_save_format
#         if format == 'OPEN_EXR_MULTILAYER': extension = '.exr'
#         if format == 'JPEG': extension = '.jpg'
#         if format == 'PNG': extension = '.png'  
#         blendname = basename(bpy.data.filepath).rpartition('.')[0]


        addon_preferences = bpy.context.user_preferences.addons[__name__].preferences
        filepath = dirname(bpy.data.filepath) + addon_preferences.temp_folder

        if not exists(filepath):
            mkdir(filepath)

        if scene.auto_save_subfolders:
            filepath = join(filepath, blendname)
        if not exists(filepath):
            mkdir(filepath)
            
        ################################################################

        ################################################################

        # # # # # # # #
# 
#         #imagefiles starting with the blendname
#         files = [f for f in listdir(filepath) \
#                 if f.startswith(blendname) \
#                 and f.lower().endswith(('.png', '.jpg', '.jpeg', '.exr'))]
#         
#         highest = 0
#         if files:
#             for f in files:
#                 #find last numbers in the filename after the blendname
#                 suffix = findall('\d+', f.split(blendname)[-1])
#                 if suffix:
#                     if int(suffix[-1]) > highest:
#                         highest = int(suffix[-1])
#         

            ###############################################################

        ################################################################
        # # # # # # # #


        # # # # # # # #
        ################################################################


        active_object = bpy.context.active_object
        name = active_object.name

        save_name = join(filepath) + name + ".png"


        image = bpy.data.images['Render Result']
        if not image:
            print('Auto Save: Render Result not found. Image not saved')
            return
        
        print('Auto_Save:', save_name)
        image.save_render(save_name, scene=None)

#        rndr.image_settings.file_format = original_format

        ################################################################
        # # # # # # # #


        # # # # # # # #
        ################################################################



        # レンダー設定を元に戻す  restore old settings
        bpy.context.scene.render.filepath = old_path
        bpy.context.scene.render.image_settings.file_format = old_fileformat
        bpy.context.scene.render.use_file_extension = old_extension
        bpy.context.scene.render.resolution_x = old_x
        bpy.context.scene.render.resolution_y = old_y
        bpy.context.scene.render.resolution_percentage = old_percentage
        bpy.context.scene.render.pixel_aspect_x = old_aspect_x
        bpy.context.scene.render.pixel_aspect_y = old_aspect_y


        ################################################################
        # # # # # # # #
       
        
        
        return {'FINISHED'}




        #  書き出す前に表示をいろいろ変える
        # # # # # # # #
        ################################################################

class asset_flinger_thumbnail(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.asset_flinger_thumbnail"
    bl_label = "asset_flinger_thumbnail"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)


        # # # # # # # #
        ################################################################

        # シェーディング設定を保存
        old_shade = bpy.context.space_data.viewport_shade
        
        # Matcapのオンオフ設定を保存
        old_matcap = bpy.context.space_data.use_matcap
        old_matcap_number = bpy.context.space_data.matcap_icon
        
        # レンダリングするもののみのオンオフ設定を保存
        old_show_only_render = bpy.context.space_data.show_only_render

        ################################################################
        # # # # # # # #



        # ↓ ↓ ここをいじると表示設定が変わるぞい

        #  ソリッド表示にする
        bpy.ops.object.shadingvariable(variable="SOLID")
        

        # Matcapのオン
        bpy.context.space_data.use_matcap = True

        #  matcapを設定       …… 好きな番号に変えて下さい
        bpy.context.space_data.matcap_icon = '12'
        
        
#        # ローカルビューにし、選択中のみの表示にする   …… ズームができなくなりますが、実行前に他のオブジェクトを隠す必要がなくなります。348行目の『#』を削除してコメントアウトを外して下さい
#        bpy.ops.view3d.localview()
        
        
        #レンダリングするもののみ表示      …… これを消すとアウトライン付きになります
        bpy.context.space_data.show_only_render = True

        #平行投影/透視投影      平行投影にする
        bpy.ops.view3d.view_persportho()
        
        
        # ↑ ↑ ここまでいじれるぞい


        ################################################################
        # # # # # # # #
        
        #サムネイル作成を実行する
        bpy.ops.object.save_thumbnail()


        # # # # # # # #
        ################################################################



        ################################################################
        
        #平行投影/透視投影      透視投影に戻す
        bpy.ops.view3d.view_persportho()



        #matcapの設定を戻す
        bpy.context.space_data.matcap_icon = '06'
  
        # ローカルビューからグローバルビューに戻す
#        bpy.ops.view3d.localview()
        


        # シェーディング設定を復元
        bpy.context.space_data.viewport_shade = old_shade



        # Matcapのオンオフを復元
        bpy.context.space_data.use_matcap = old_matcap
        bpy.context.space_data.matcap_icon = old_matcap_number
        
        # レンダリングするもののみのオンオフを復元
        bpy.context.space_data.show_only_render = old_show_only_render
        
        
        ################################################################
        # # # # # # # #


        return {'FINISHED'}





        










#===============================================================

#===============================================================

class assetflinger_obj(bpy.types.Operator):
    bl_idname = "ops.assetflinger_obj"
    bl_label = "instant meshes export"
    bl_options = {'REGISTER', 'UNDO'}
    bl_region_type = "WINDOW"

    operation = bpy.props.StringProperty()

    targetDir = "" # If nothing is specified, the 'home' directory is used

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if len(bpy.context.selected_objects) < 1:
            return {'CANCELLED'}





#===============================================================

#===============================================================

        #  OBJ 保存  =======================================================
        
        self.setUpPaths(context)

        active_object = bpy.context.active_object
        name = active_object.name
        objname = name + ".obj" # The temp object is called the same as the active object you have selected in Blender.
#        bpy.ops.view3d.snap_cursor_to_selected() # Set 3D Cursor to the origin of the selected object

        try:
            bpy.ops.export_scene.obj(filepath=objname, use_selection=True, use_materials=False) # Exports the *.obj to your home directory (on Linux, at least) or the directory you specified above under the 'targetDir' variable
        except Exception as e:
            printErrorMessage("Could not create OBJ", e)
            return {'CANCELLED'}

        return {'FINISHED'}


#===============================================================

#===============================================================

        #  セットアップ パス  =======================================================


    def setUpPaths(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences


        self.targetDir = str(addon_prefs.temp_folder) # Set path for temp dir to store objs in


        if self.targetDir != "" and os.path.isdir(self.targetDir):
            os.chdir(self.targetDir)
        else:
            os.chdir(os.path.expanduser("~"))
            



class assetflinger_objPanel(bpy.types.Panel):
    """ """
    bl_label = "'Asset Flinger OBJ & Thumbnail"
    bl_idname = "OBJECT_PT_assetflinger_obj"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Create"
    bl_context = "objectmode"



    def draw(self, context):

        layout = self.layout
        obj = context.object
        wm = context.window_manager
        row = layout.row()
        layout.operator("ops.assetflinger_obj", text="OBJ export", icon="OBJECT_DATAMODE").operation = "cmd"
        layout.operator("object.asset_flinger_thumbnail", text="Thumbnail export", icon="IMAGE_DATA")





#===============================================================

#===============================================================


# Utility functions
def printErrorMessage(msg, e):
    print("-- Error ---- !")
    print(msg, "\n", str(e))
    print("------\n\n")


def register():

    bpy.utils.register_class(assetflinger_objPreferences)
    bpy.utils.register_class(assetflinger_obj)
    bpy.utils.register_class(assetflinger_objPanel)
    bpy.utils.register_class(save_thumbnail)
    bpy.utils.register_class(asset_flinger_thumbnail)



def unregister():

    bpy.utils.unregister_class(assetflinger_objPreferences)

    bpy.utils.unregister_class(assetflinger_obj)
    bpy.utils.unregister_class(assetflinger_objPanel)
    bpy.utils.unregister_class(save_thumbnail)
    bpy.utils.unregister_class(asset_flinger_thumbnail)




if __name__ == "__main__":
    register()
