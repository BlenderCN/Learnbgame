
bl_info = {
    "name": "Dorothy's Development Environment",
    "author": "N(Natukikazemizo)",
    "version": (0, 0),
    "blender": (2, 79, 0),
    "location": "Everywhere",
    "description": "Development Environment of Dorthy by Dorohy for Dorothy.",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"
}

# Translation dictionary
translation_dict = {
    "en_US": {
        ("*", "Auto Breakdown: Enabled add-on 'Auto Breakdown'"):
            "Auto Breakdown: Enabled add-on 'Auto Breakdown'",
        ("*", "Auto Breakdown: Disabled add-on 'Auto Breakdown'"):
            "Auto Breakdown: Disabled add-on 'Auto Breakdown'",
        ("*", "Auto Breakdown"):
            "Auto Breakdown",
        ("*", "Overwrite Data"):
            "Overwrite Data",
        ("*", "Export Pose"):
            "Export Pose",
        ("*", "Emotion"):
            "Emotion",
        ("*", "Character Name:"):
            "Character Name:",
        ("*", "Sync Bone Constraints"):
            "Sync Bone Constraints",
        ("*", "Sync"):
            "Sync",
        ("*", "Write CSV"):
            "Write CSV",
        ("*", "Read CSV"):
            "Read CSV",
        ("*", "Select CSV File"):
            "Select CSV File",
        ("*", "Armature Menu"):
            "Armature Menu",
        ("*", "Select Objects which has Armature."):
            "Select Objects which has Armature.",
        ("*", "Sync IK"):
            "Sync IK",
        ("*", "Select CSV file."):
            "Select CSV file.",
        ("*", "Select target Armature."):
            "Select target Armature.",
    },
    "ja_JP": {
        ("*", "Auto Breakdown: Enabled add-on 'Auto Breakdown'"):
            "自動中割り: アドオン「自動中割り」が有効化されました。",
        ("*", "Auto Breakdown: Disabled add-on 'testee'"):
            "自動中割り: アドオン「自動中割り」が無効化されました。",
        ("*", "Auto Breakdown"):
            "自動中割り",
        ("*", "Overwrite Data"):
            "データ上書き",
        ("*", "Export Pose"):
            "ポーズ抽出",
        ("*", "Emotion"):
            "感情",
        ("*", "Character Name:"):
            "キャラクター名：",
        ("*", "Sync Bone Constraints"):
            "ボーン 拘束の同期",
        ("*", "Sync"):
            "同期",
        ("*", "Write CSV"):
            "CSV出力",
        ("*", "Read CSV"):
            "CSV入力",
        ("*", "Select CSV File"):
            "CSVファイルの選択",
        ("*", "Armature Menu"):
            "Armature メニュー",
        ("*", "Select Objects which has Armature."):
            "Armatureを選択するメニュー",
        ("*", "Sync IK"):
            "IKの同期",
        ("*", "Select CSV file."):
            "CSVファイルを選択してください。",
        ("*", "Select target Armature."):
            "対象Armatureを選択してください。",
    }
}

if "bpy" in locals():
    import imp

#    imp.reload(common)
#else:
#    from . import common


import bpy

class TestOps1(bpy.types.Operator):

    bl_idname = "object.test_ops_1d"
    bl_label = "Test1"
    bl_description = "Test target Operation1"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}


class TestOps2(bpy.types.Operator):

    bl_idname = "object.test_ops_2d"
    bl_label = "Test2"
    bl_description = "Test target Operation2"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # オブジェクト名が「Cube」であるオブジェクトが存在しない場合
        if bpy.data.objects.find('Cube') == -1:
            return {'CANCELLED'}
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

    # Register Translation dictionary
    bpy.app.translations.register(__name__, translation_dict)

#    bpy.types.WindowManager.sync_bone_constraints_props = bpy.props.PointerProperty(\
#        type=sync_bone_constraints.MySettings)

#    # 項目をメニューの先頭に追加
#    bpy.types.VIEW3D_MT_pose.append(export_pose.menu_fn_1)
#    # 項目をメニューの末尾に追加
#    bpy.types.VIEW3D_MT_pose.prepend(export_pose.menu_fn_2)

    print(
        bpy.app.translations.pgettext(
            "DDE: Enabled add-on `Dorothy's Development Environment'"
        )
    )

def unregister():
    # UnRegister Translation dictionary
#    bpy.utils.unregister_class(sync_bone_constraints.StringValGroup)
    bpy.app.translations.unregister(__name__)
    bpy.utils.unregister_module(__name__)
#    del bpy.types.WindowManager.sync_bone_constraints_props
    print(
        bpy.app.translations.pgettext(
            "DDE: Disabled add-on `Dorothy's Development Environment`"
        )
    )



if __name__ == "__main__":
    register()
