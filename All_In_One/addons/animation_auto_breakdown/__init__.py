
bl_info = {
    "name": "Auto Breakdown",
    "author": "N(Natukikazemizo)",
    "version": (0, 0),
    "blender": (2, 79, 0),
    "location": "Dope Sheet > Key / NLA Editor > Edit",
    "description": "Automatic Breakdown & related functions",
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
        ("*", "Auto Twist"):
            "Auto Twist",
        ("*", "Overwrite Data"):
            "Overwrite Data",
        ("*", "Export Pose"):
            "Export Pose",
        ("*", "Emotion"):
            "Emotion",
        ("*", "Character Name"):
            "Character Name",
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
        ("*", "Select Strip."):
            "Select Strip.",
        ("*", "Overwrite Strip&Action"):
            "Overwrite Strip&Action",
        ("*", "Source Strip"):
            "Source Strip",
        ("*", "Source Action"):
            "Source Action",
        ("*", "Destination Track"):
            "Destination Track",
        ("*", "Destination Strip"):
            "Destination Strip",
        ("*", "Destination Action"):
            "Destination Action",
        ("*", "Duplicate Object."):
            "Duplicate Object.",
        ("*", "direction"):
            "direction",
        ("*", "Finished."):
            "Finished.",
        ("*", "Start."):
            "Start.",
        ("*", "X-Miller Bone Transformations"):
            "X-Miller Bone Transformations",
    },
    "ja_JP": {
        ("*", "Auto Breakdown: Enabled add-on 'Auto Breakdown'"):
            "自動中割り: アドオン「自動中割り」が有効化されました。",
        ("*", "Auto Breakdown: Disabled add-on 'testee'"):
            "自動中割り: アドオン「自動中割り」が無効化されました。",
        ("*", "Auto Breakdown"):
            "自動中割り",
        ("*", "Auto Twist"):
            "自動ひねり",
        ("*", "Overwrite Data"):
            "データ上書き",
        ("*", "Export Pose"):
            "ポーズ抽出",
        ("*", "Emotion"):
            "感情",
        ("*", "Character Name"):
            "キャラクター名",
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
            "Armatureを選択してください。",
        ("*", "Select Strip."):
            "ストリップを選択してください。",
        ("*", "Overwrite Strip&Action"):
            "ストリップとアクションを上書き",
        ("*", "Source Strip"):
            "元ストリップ",
        ("*", "Source Action"):
            "Source Action",
        ("*", "Destination Track"):
            "変換後トラック",
        ("*", "Destination Strip"):
            "変換後ストリップ",
        ("*", "Destination Action"):
            "変換後アクション",
        ("*", "Duplicate Object."):
            "オブジェクトが重複しています。",
        ("*", "direction"):
            "方向",
        ("*", "Finished."):
            "処理完了。",
        ("*", "Start."):
            "処理開始。",
        ("*", "X-Miller Bone Transformations"):
            "ボーントランスフォーメーションのX軸反転",
    }
}

if "bpy" in locals():
    import imp

    imp.reload(common)
    imp.reload(auto_twist)
    imp.reload(auto_breakdown)
    imp.reload(sync_bone_constraints)
else:
    from . import common
    from . import auto_twist
    from . import auto_breakdown
    from . import sync_bone_constraints


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

    bpy.types.WindowManager.sync_bone_constraints_props = bpy.props.PointerProperty(\
        type=sync_bone_constraints.MySettings)
    bpy.types.WindowManager.auto_twist_props = bpy.props.PointerProperty(\
        type=auto_twist.MySettings)

#    # 項目をメニューの先頭に追加
#    bpy.types.VIEW3D_MT_pose.append(export_pose.menu_fn_1)
#    # 項目をメニューの末尾に追加
#    bpy.types.VIEW3D_MT_pose.prepend(export_pose.menu_fn_2)

    print(
        bpy.app.translations.pgettext(
            "Auto Breakdown: Enabled add-on 'Auto Breakdown'"
        )
    )

def unregister():
    # UnRegister Translation dictionary
    bpy.utils.unregister_class(sync_bone_constraints.StringValGroup)
    bpy.app.translations.unregister(__name__)
    bpy.utils.unregister_module(__name__)

    del bpy.types.WindowManager.auto_twist_props
    del bpy.types.WindowManager.sync_bone_constraints_props

    print(
        bpy.app.translations.pgettext(
            "Auto Breakdown: Disabled add-on 'Auto Breakdown'"
        )
    )



if __name__ == "__main__":
    register()
