import bpy
import os
import re

import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf



bl_info = {
    "name": "FJW Zaptools",
    "author": "GhostBrain3dex",
    "version": (1.0),
    "blender": (2, 77, 0),
    'location': 'Properties > Camera > Lens > CameraTools',
    "description": "CameraTools",
    "category": "Object",
}





#AssetSketcherのヘルパ
#メインパネル
class Asset_Sketcher_Helper(bpy.types.Panel):#メインパネル
    bl_label = "Asset Sketcher Helper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Asset Sketcher"

    @classmethod
    def poll(cls, context):
        pref = conf.get_pref()
        return pref.assetsketcherhelper

    def draw(self, context):
        layout = self.layout
        r = layout.row(align=True)

        r.operator("assetsketcherhelper.addphis")
        r.operator("assetsketcherhelper.delphis")
        r.operator("assetsketcherhelper.applyphis")


'''
class cls(bpy.types.Operator):
    """説明"""
    bl_idname="assetsketcherhelper.cls"
    bl_label = "ラベル"
    def execute(self,context):
        #self.report({"INFO"},"")
        pass
        return {"FINISHED"}
'''



#AssetSketcherでいろいろ撒いたあとに、選択オブジェクトに物理つける。
class AS_addphis(bpy.types.Operator):
    """選択スケッチオブジェクトに物理追加"""
    bl_idname = "assetsketcherhelper.addphis"
    bl_label = "物理追加"
    def execute(self,context):
        fjw.reject_notmesh()

        canvases = []
        targets = []
        #カスタムプロパティをチェック
        for obj in fjw.get_selected_list():
            if "canvas" in obj:
                canvases.append(obj)
                continue
            if "asset" in obj:
                targets.append(obj)
                continue

        #カンバス群にパッシブ追加
        fjw.deselect()
        fjw.activate(canvases[0])
        fjw.select(canvases)
        bpy.ops.rigidbody.objects_add(type='PASSIVE')

        #ターゲット群にアクティブ追加
        fjw.deselect()
        fjw.activate(targets[0])
        fjw.select(targets)
        bpy.ops.rigidbody.objects_add(type='ACTIVE')

        #アニメーション再生
        bpy.ops.screen.frame_jump()
        bpy.ops.screen.animation_play()

        #self.report({"INFO"},"")
        pass
        return {"FINISHED"}

class AS_delphis(bpy.types.Operator):
    """物理削除"""
    bl_idname = "assetsketcherhelper.delphis"
    bl_label = "削除"
    def execute(self,context):
        fjw.reject_notmesh()

        canvases = []
        targets = []
        #カスタムプロパティをチェック
        for obj in fjw.get_selected_list():
            if "canvas" in obj:
                canvases.append(obj)
                continue
            if "asset" in obj:
                targets.append(obj)
                continue

        fjw.select(canvases)
        fjw.select(targets)

        bpy.ops.rigidbody.objects_remove()


        #self.report({"INFO"},"")
        pass
        return {"FINISHED"}

class AS_applyphis(bpy.types.Operator):
    """物理確定"""
    bl_idname = "assetsketcherhelper.applyphis"
    bl_label = "確定"
    def execute(self,context):
        fjw.reject_notmesh()

        canvases = []
        targets = []
        #カスタムプロパティをチェック
        for obj in fjw.get_selected_list():
            if "canvas" in obj:
                canvases.append(obj)
                continue
            if "asset" in obj:
                targets.append(obj)
                continue

        fjw.select(canvases)
        fjw.select(targets)

        bpy.ops.object.visual_transform_apply()
        bpy.ops.screen.frame_jump()
        bpy.ops.rigidbody.objects_remove()

        #self.report({"INFO"},"")
        pass
        return {"FINISHED"}










def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()

