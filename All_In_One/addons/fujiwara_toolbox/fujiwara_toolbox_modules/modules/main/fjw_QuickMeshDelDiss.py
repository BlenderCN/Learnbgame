import bpy
import bmesh


import fujiwara_toolbox_modules as fujiwara_toolbox
from fujiwara_toolbox_modules import fjw, conf



bl_info = {
    "name": "FJW Quick Mesh Delete/Dissolve",
    "description": "メッシュ編集時、選択物が頂点・辺なら溶解、面なら削除します。",
    "author": "藤原佑介 https://twitter.com/GhostBrain3dex",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "3D View > Tool Shelf > Tools tab",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"
}


class quickmdd(bpy.types.Operator):
    """メッシュ編集時、選択物が頂点・辺なら溶解、面なら削除します。"""
    bl_idname = "mesh.quickmdd"
    bl_label = "クイック溶解・削除"

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
        
        
        
        return {"FINISHED"}


def quickmdd_ui(self, context):
    layout = self.layout
    layout.operator("mesh.quickmdd")


def sub_registration():
    bpy.types.VIEW3D_PT_tools_meshedit.append(quickmdd_ui)
    pass

def sub_unregistration():
    bpy.types.VIEW3D_PT_tools_meshedit.remove(quickmdd_ui)
    pass



def register():
    bpy.utils.register_class(quickmdd)
    sub_registration()


def unregister():
    bpy.utils.unregister_class(quickmdd)
    sub_unregistration()


if __name__ == "__main__":
    register()


