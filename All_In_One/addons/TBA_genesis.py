import bpy
import random
import subprocess as sp
import webbrowser as wb
from bpy.props import IntProperty, FloatProperty
from bpy.props import EnumProperty, FloatVectorProperty


bl_info = {
    "name": "街を自動生成",
    "author": "大将丸(TaisyoFranoria)",
    "version": (2, 0),
    "blender": (2, 75, 0),
    "location": "3Dビュー > ツールシェルフ",
    "description": "街生成",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "User Interface"
}
#########################
class makehouse(object):
    def __init__(self):
        self.path_m = 'Q:\\TBA\\main\\'
        #self.path_m = 'D:\\TBA\\main\\'
        # path_m = '/home/taisyo/TBA/main/'
        self.path_r = 'Q:\\TBA\\roof\\'
        #self.path_r = 'D:\\TBA\\roof\\'
        # path_r = '/home/taisyo/TBA/roof/'
        self.path_p1 = 'Q:\\TBA\\parts_1\\'
        #self.path_p1 = 'D:\\TBA\\parts_1\\'
        # path_p1 = '/home/taisyo/TBA/parts_1/'
        self.path_p2 = 'Q:\\TBA\\parts_2\\'
        #self.path_p2 = 'D:\\TBA\\parts_2\\'
        # path_p2 = '/home/taisyo/TBA/parts_2/'
        self.path_base = 'Q:\\TBA\\base\\'
        #self.path_base = 'D:\\TBA\\base\\'
        self.path_ex = 'Q:\\TBA\\main\\ex\\1.fbx'
        #self.path_ex = 'D:\\TBA\\main\\ex\\1.fbx'
        self.tail = '.fbx'

        self.f2_mode = False

    #オブジェクトを結合する
    def join_object(self):
        for ob in bpy.context.scene.objects:
            #メッシュかどうか調べる
            if ob.type == 'MESH':
                ob.select = True
                bpy.context.scene.objects.active = ob
            else:
                ob.select = False

        bpy.ops.object.join()
        return

    #fbxファイルをBlenderにインポートする
    def import_fbx(self,path_i):
        bpy.ops.import_scene.fbx(filepath=path_i, axis_forward='-Z', axis_up='Y', directory="", filter_glob="*.fbx",
                                 ui_tab='MAIN', use_manual_orientation=False, global_scale=1.0,
                                 bake_space_transform=False, use_custom_normals=True, use_image_search=True,
                                 use_alpha_decals=False, decal_offset=0.0, use_anim=True, anim_offset=1.0,
                                 use_custom_props=True, use_custom_props_enum_as_string=True, ignore_leaf_bones=False,
                                 force_connect_children=False, automatic_bone_orientation=False, primary_bone_axis='Y',
                                 secondary_bone_axis='X', use_prepost_rot=True)
        return

    #fbxファイルをBlenderにエクスポートする
    def export_fbx(self,path_e):
        bpy.ops.export_scene.fbx(filepath=path_e, check_existing=True, axis_forward='-Z', axis_up='Y',
                                 filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', use_selection=False,
                                 global_scale=1.0, apply_unit_scale=True, bake_space_transform=False,
                                 object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'},
                                 use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False,
                                 use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y',
                                 secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL',
                                 bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True,
                                 bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True,
                                 bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True,
                                 use_anim_action_all=True, use_default_take=True, use_anim_optimize=True,
                                 anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF',
                                 use_batch_own_dir=True, use_metadata=True)
        return

    #オブジェクト、マテリアル、テクスチャ、メッシュのすべてをリフレッシュ（消す）
    def refresh(self):
        def refresh_obj():
            for x in bpy.data.objects:
                bpy.data.objects.remove(x)

        def refresh_mat():
            for x in bpy.data.materials:
                bpy.data.materials.remove(x)

        def refresh_tex():
            for x in bpy.data.textures:
                bpy.data.textures.remove(x)

        def refresh_mesh():
            for x in bpy.data.meshes:
                bpy.data.meshes.remove(x)
        refresh_obj()
        refresh_mat()
        refresh_tex()
        refresh_mesh()


    #オブジェクトの名前を変更
    def rename(self):
        for x in bpy.data.objects:
            x.name = 'obj'

    def name_mat(self):
        count = 0;
        for x in bpy.data.materials:
            if (len(x.texture_slots) != 0):
                x.name = bpy.data.textures[x.texture_slots[0].texture.name].image.filepath[-9:-4]

    #main関数
    def main(self):
        path = 'Q:\\TBA\\main\\test.fbx'
        #path = 'D:\\TBA\\main\\test.fbx'

        self.refresh()

        for x in range(100):
            if (random.randint(1, 3) == 2):
                f2_mode = True
            else:
                f2_mode = False

            path_mr = self.path_m + str(random.randint(0, 3)) + self.tail
            path_rr = self.path_r + str(random.randint(0, 5)) + self.tail
            path_p1r = self.path_p1 + str(random.randint(0, 1)) + self.tail
            path_p2r = self.path_p2 + str(random.randint(0, 5)) + self.tail
            path_br = self.path_base + str(0) + self.tail
            if (f2_mode):
                path_mr = self.path_m + '2f\\' + str(random.randint(0, 3)) + self.tail
                path_rr = self.path_r + '2f\\' + str(random.randint(0, 5)) + self.tail

            if (random.randint(0, 30) == 10):
                self.import_fbx(self.path_ex)
            else:
                self.import_fbx(path_br)
                self.import_fbx(path_mr)
                self.import_fbx(path_rr)
                self.import_fbx(path_p1r)
                self.import_fbx(path_p2r)

            path_e = 'Q:\\TBA\\result\\' + str(x) + '.fbx'
            #path_e = 'D:\\TBA\\result\\' + str(x) + '.fbx'
            # path_e = '/home/taisyo/TBA/result/' + str(x) + '.fbx'
            self.join_object()
            self.rename()
            self. name_mat()
            self.export_fbx(path_e)
            self.refresh()





#########################
class summaryhouse(object):

    def __init__(self):
        self.path = 'Q:\\TBA\\result\\'
        #self.path = 'D:\\TBA\\result\\'
        # path = '/home/taisyo/TBA/result/'
        self.tail = '.fbx'

    #fbxファイルをインポート
    def import_fbx(self,path_i):
        bpy.ops.import_scene.fbx(filepath=path_i, axis_forward='-Z', axis_up='Y', directory="", filter_glob="*.fbx",
                                 ui_tab='MAIN', use_manual_orientation=False, global_scale=1.0,
                                 bake_space_transform=False, use_custom_normals=True, use_image_search=True,
                                 use_alpha_decals=False, decal_offset=0.0, use_anim=True, anim_offset=1.0,
                                 use_custom_props=True, use_custom_props_enum_as_string=True, ignore_leaf_bones=False,
                                 force_connect_children=False, automatic_bone_orientation=False, primary_bone_axis='Y',
                                 secondary_bone_axis='X', use_prepost_rot=True)
        return

    #fbxファイルをエクスポート
    def export_fbx(self,path_e):
        bpy.ops.export_scene.fbx(filepath=path_e, check_existing=True, axis_forward='-Z', axis_up='Y',
                                 filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', use_selection=False,
                                 global_scale=1.0, apply_unit_scale=True, bake_space_transform=False,
                                 object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'},
                                 use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False,
                                 use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y',
                                 secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL',
                                 bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True,
                                 bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True,
                                 bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True,
                                 use_anim_action_all=True, use_default_take=True, use_anim_optimize=True,
                                 anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF',
                                 use_batch_own_dir=True, use_metadata=True)
        return

    #main関数
    def main(self):
        for x in range(100):
            path_i = self.path + str(x) + self.tail
            self.import_fbx(path_i)

        data_ = []
        mat_ = []
        count = 0

        for x in bpy.data.objects:
            data_.append(x)

        #"makehouse"で生成されたモデルを並べる
        for y in range(10):
            for x in range(10):
                #テクスチャ名が同じ（同じテクスチャを参照してる）マテリアルをそれぞれ統合する
                for m in data_[count].material_slots:
                    insert_flag = 1
                    for m2 in mat_:
                        if (m.name[0:5] == m2.name):
                            bpy.data.materials.remove(m.material)
                            m.material = m2
                            insert_flag = 0
                            break
                    if (insert_flag == 1):
                        mat_.append(m.material)

                data_[count].location.x += x * 6
                data_[count].location.y += y * 6
                count += 1

        #結果を"res.fbx"として出力
        path_e = self.path + 'res' + self.tail
        self.export_fbx(path_e)

mh = makehouse()
sh = summaryhouse()



class makehouse_button(bpy.types.Operator):

    bl_idname = "object.makehouse"
    bl_label = "makehouse"
    bl_description = "家を100個生成。たまに空き地"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        mh.main()
        return {'FINISHED'}


class summaryhouse_button(bpy.types.Operator):
    bl_idname = "object.summaryhouse"
    bl_label = "summaryhouse"
    bl_description = "作った家を設置"
    bl_options = {'REGISTER', 'UNDO'}



    def execute(self, context):
        sh.main()
        return {'FINISHED'}


class ShowAllIcons(bpy.types.Operator):

    bl_idname = "object.show_all_icons"
    bl_label = "利用可能なアイコンをすべて表示"
    bl_description = "利用可能なアイコンをすべて表示"
    bl_options = {'REGISTER', 'UNDO'}

    num_column = IntProperty(
        name="一行に表示するアイコン数",
        description="一行に表示するアイコン数",
        default=2,
        min=1,
        max=5
    )

    # オプションのUI
    def draw(self, context):
        layout = self.layout

        layout.prop(self, "num_column")

        layout.separator()

        # 利用可能なアイコンをすべて表示
        layout.label(text="利用可能なアイコン一覧:")
        icon = bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon']
        for i, key in enumerate(icon.enum_items.keys()):
            if i % self.num_column == 0:
                row = layout.row()
            row.label(text=key, icon=key)

    def execute(self, context):
        return {'FINISHED'}


# 「カスタムメニュー」タブを追加
class VIEW3D_PT_CustomMenu(bpy.types.Panel):

    bl_label = "TBA"          # タブに表示される文字列
    bl_space_type = 'VIEW_3D'           # メニューを表示するエリア
    bl_region_type = 'TOOLS'            # メニューを表示するリージョン
    bl_category = "TBA"       # タブを開いたメニューのヘッダーに表示される文字列
    bl_context = "objectmode"           # パネルを表示するコンテキスト

    # 本クラスの処理が実行可能かを判定する
    @classmethod
    def poll(cls, context):

        return True

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PLUGIN')

    # メニューの描画処理
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # ボタンを追加
        layout.label(text="街生成")
        layout.operator(makehouse_button.bl_idname, text="モデルデータ生成")
        layout.operator(summaryhouse_button.bl_idname, text="並べる")

       


def register():
    bpy.utils.register_module(__name__)
    print("大将街自動生成が有効化されました。")


def unregister():
    bpy.utils.unregister_module(__name__)
    print("大将街自動生成が無効化されました。")


if __name__ == "__main__":
    register()
