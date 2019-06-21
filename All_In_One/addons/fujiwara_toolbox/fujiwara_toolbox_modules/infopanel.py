import bpy
import bmesh

import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf

bl_info = {
    "name": "FJW Subsurf Modeling Tools",
    "description": "Subsurfモデリングのための便利ツール",
    "author": "佑介",
    "version": (1, 0),
    "blender": (2, 68, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}



############################################################################################################################
############################################################################################################################
#ユーティリティ
############################################################################################################################
############################################################################################################################
def dummy():
    return

SelectedFile = ""
FileBrouserExecute = dummy


############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################
#ボタン登録リスト
ButtonList = []

#ラベルリスト
LabelList = []

#メインパネル
class SSMTView3DPanel(bpy.types.Panel):#メインパネル
    bl_label = "Subsurfモデリングツール"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #bl_category = "マイアドオン"

    @classmethod
    def poll(cls, context):
        pref = fujiwara_toolbox.conf.get_pref()
        return pref.subsurfmodelingtools
        
        l = self.layout
        r = l.row()
        b = r.box()

        #ボタン同士をくっつける
        b = b.column(align=True)

        #ボタンリストのボタンを登録
        lln = 0
        for btn in ButtonList:
            #テキストラベルの登録
            if LabelList[lln] != "":
                b.label(text=LabelList[lln])
            lln+=1
            #ボタンの登録
            b.operator(btn)

############################################################################################################################
############################################################################################################################
#カスタムボタン群
############################################################################################################################
############################################################################################################################


########################################
#ミラーCUBE作成
########################################
class create_msscube(bpy.types.Operator):#ミラーCUBE作成
    """ミラーCUBE作成"""
    bl_idname = "object.create_msscube"
    bl_label = "ミラーCUBE作成"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("Subsurfモデリング")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 4
        bpy.context.object.modifiers["Subsurf"].render_levels = 4
        
        obj = bpy.context.scene.objects.active
        bpy.ops.object.mode_set(mode = 'EDIT') 
        data = obj.data
        bm = bmesh.from_edit_mesh(data)
        bm.faces.active = None
        X = 0
        Y = 1
        Z = 2
        selectflag = False
        #選択リフレッシュ
        for v  in bm.verts:
        	v.select = False
        for e in bm.edges:
        	e.select = False
        for f in bm.faces:
        	f.select = False
        
        #マイナス位置の頂点を0位置に
        for v  in bm.verts:
            if(v.co[X] < 0):
                v.co[X] = 0
                v.select = True
        
        bmesh.update_edit_mesh(data)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        bpy.ops.object.mode_set(mode = 'EDIT') 
        #選択面削除
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        return {'FINISHED'}
########################################

########################################
#Mirror・SS追加（選択物）
########################################
class addmss(bpy.types.Operator):#Mirror・SS追加（選択物）
    """Sample Operator"""
    bl_idname = "object.addmss"
    bl_label = "Mirror・SS追加（選択物）"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_add(type='MIRROR')
                bpy.ops.object.modifier_add(type='SUBSURF')
                for mod in obj.modifiers:
                    if mod.type == "SUBSURF":
                        mod.levels = 4
        
        return {'FINISHED'}
########################################

########################################
#平面削減
########################################
class FUJIWARATOOLBOX_860996(bpy.types.Operator):#平面削減
    """平面削減"""
    bl_idname = "fujiwara_toolbox.command_860996"
    bl_label = "平面削減"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        
        return {'FINISHED'}
########################################







########################################
#SSのみ追加（選択物）
########################################
class FUJIWARATOOLBOX_130218(bpy.types.Operator):#SSのみ追加（選択物）
    """SSのみ追加（選択物）"""
    bl_idname = "fujiwara_toolbox.command_130218"
    bl_label = "SSのみ追加（選択物）"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_add(type='SUBSURF')
                bpy.context.object.modifiers["Subsurf"].levels = 2
                bpy.ops.object.shade_flat()
        
        return {'FINISHED'}
########################################








########################################
#SSのみ追加→隠す（選択物）
########################################
class FUJIWARATOOLBOX_655300(bpy.types.Operator):#SSのみ追加→隠す（選択物）
    """SSのみ追加→隠す（選択物）"""
    bl_idname = "fujiwara_toolbox.command_655300"
    bl_label = "SSのみ追加→隠す（選択物）"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_add(type='SUBSURF')
                bpy.context.object.modifiers["Subsurf"].levels = 2
                bpy.ops.object.shade_flat()
        
        
        bpy.ops.object.hide_view_set(unselected=False)
        #後処理
        for obj in bpy.data.objects:
            obj.select = False
        
        return {'FINISHED'}
########################################





########################################
#ノーマルを整える（選択物）
########################################
class FUJIWARATOOLBOX_590395(bpy.types.Operator):#ノーマルを整える（選択物）
    """ノーマルを整える（選択物）"""
    bl_idname = "fujiwara_toolbox.command_590395"
    bl_label = "ノーマルを整える（選択物）"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}
########################################







########################################
#クリーストグル
########################################
class toggle_crease(bpy.types.Operator):#クリーストグル
    """クリーストグル"""
    bl_idname = "mesh.toggle_crease"
    bl_label = "クリーストグル"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = bpy.context.scene.objects.active
        data = obj.data
        bm = bmesh.from_edit_mesh(data)
        crease_layer = bm.edges.layers.crease.active
        
        #クリースが1度もかかってなかったのでレイヤーがない場合
        if crease_layer == None:
            crease_layer = bm.edges.layers.crease.new()
        
        creased = False
        
        for edge in bm.edges:
            if edge.select:
                if edge[crease_layer] == 1:
                    creased = True
        
        for edge in bm.edges:
            if edge.select:
                if creased:
                    edge[crease_layer] = 0
                else:
                    edge[crease_layer] = 1
                    
#                if edge[crease_layer] == 0:
#                    edge[crease_layer] = 1
#                else:
#                    edge[crease_layer] = 0
        #選択リフレッシュ
#        for v in bm.verts:
#        	v.select = False
#        for e in bm.edges:
#        	e.select = False
#        for f in bm.faces:
#        	f.select = False
        
        bmesh.update_edit_mesh(data)
        
        
        
        return {'FINISHED'}
########################################


########################################
#頂点連結
########################################
class connectv(bpy.types.Operator):#頂点連結
    """頂点連結"""
    bl_idname = "mesh.connectv"
    bl_label = "頂点連結"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        import bmesh
        
        obj = bpy.context.scene.objects.active
        data = obj.data
        bm = bmesh.from_edit_mesh(data)
        
        #http://blender.stackexchange.com/questions/39540/cut-bmesh-with-python
        
        cverts = []
        for v  in bm.verts:
            if v.select:
                cverts.append(v)
        
        bmesh.ops.connect_verts(bm, verts=cverts, faces_exclude=[], check_degenerate=False)
        
        #選択リフレッシュ
        for v  in bm.verts:
            v.select = False
        for e in bm.edges:
            e.select = False
        for f in bm.faces:
            f.select = False
        
        bmesh.update_edit_mesh(data)
        
        return {'FINISHED'}
########################################







########################################
#自動溶解
########################################
class auto_dissolve(bpy.types.Operator):#溶解
    """自動溶解"""
    bl_idname = "mesh.auto_dissolve"
    bl_label = "自動溶解"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = bpy.context.scene.objects.active
        data = obj.data
        bm = bmesh.from_edit_mesh(data)
        
        skip = False
        for face in bm.faces:
            if face.select:
                skip = True
                bpy.ops.mesh.dissolve_faces(use_verts=False)
                break
        if not skip:
            for edge in bm.edges:
                if edge.select:
                    skip = True
                    bpy.ops.mesh.dissolve_edges(use_verts=True, use_face_split=False)
                    break
        if not skip:
            for vertex in bm.verts:
                if vertex.select:
                    bpy.ops.mesh.dissolve_verts(use_face_split=False, use_boundary_tear=False)
                    break
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.mode_set(mode = 'EDIT') 
        
        return {'FINISHED'}
########################################


########################################
#自動削除
########################################
class auto_delete(bpy.types.Operator):#自動削除
    """自動削除"""
    bl_idname = "mesh.auto_delete"
    bl_label = "自動削除"
    bl_options = {'REGISTER'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = bpy.context.scene.objects.active
        data = obj.data
        bm = bmesh.from_edit_mesh(data)
        
        skip = False
        for face in bm.faces:
            if face.select:
                skip = True
                bpy.ops.mesh.delete(type='FACE')
                break
        if not skip:
            for edge in bm.edges:
                if edge.select:
                    skip = True
                    bpy.ops.mesh.delete(type='EDGE')
                    break
        if not skip:
            for vertex in bm.verts:
                if vertex.select:
                    bpy.ops.mesh.delete(type='VERT')
                    break
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.mode_set(mode = 'EDIT') 
        
        return {'FINISHED'}
########################################


########################################
#クイック削除・溶解
########################################
class quick_deldis(bpy.types.Operator):#クイック削除・溶解
    """クイック削除・溶解"""
    bl_idname = "mesh.quick_deldis"
    bl_label = "クイック削除・溶解"
    bl_options = {'REGISTER', 'UNDO'}

    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        obj = bpy.context.scene.objects.active
        data = obj.data
        bm = bmesh.from_edit_mesh(data)
        
        skip = False
        for face in bm.faces:
            if face.select:
                skip = True
                bpy.ops.mesh.delete(type='FACE')
                break
        if not skip:
            for edge in bm.edges:
                if edge.select:
                    skip = True
                    bpy.ops.mesh.dissolve_edges(use_verts=True, use_face_split=False)
                    break
        if not skip:
            for vertex in bm.verts:
                if vertex.select:
                    bpy.ops.mesh.dissolve_verts(use_face_split=False, use_boundary_tear=False)
                    break
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        
        return {'FINISHED'}
########################################


########################################
#選択トグル
########################################
class FUJIWARATOOLBOX_927033(bpy.types.Operator):#選択トグル
    """選択トグル"""
    bl_idname = "fujiwara_toolbox.command_927033"
    bl_label = "選択トグル"
    bl_options = {'REGISTER', 'UNDO'}


    #メインパネルのボタンリストに登録
    ButtonList.append(bl_idname)
    #テキストラベルの追加
    LabelList.append("")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #モード判定
        msmode = bpy.context.scene.tool_settings.mesh_select_mode
        mode = 0
        if(msmode[0]):
            mode = 0
        
        if(msmode[1]):
            mode = 1
        
        if(msmode[2]):
            mode = 2
        
        #モードトグル 面はスキップでいいや
        mode+=1
        if(mode > 2):
            mode = 0
        
        if(mode == 0):
            msmode = [True,False,False]
        
        if(mode == 1):
            msmode = [False,True,False]
        
        if(mode == 2):
            msmode = [False,False,True]
        
        bpy.context.scene.tool_settings.mesh_select_mode = msmode
        
        
        
        return {'FINISHED'}
########################################











############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    pass
def sub_unregistration():
    pass

def register():    #登録
    bpy.utils.register_module(__name__)


def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()