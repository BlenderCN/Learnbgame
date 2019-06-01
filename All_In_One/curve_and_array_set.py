
bl_info = {
    "name": "Curve & Array Set",
    "author": "bookyakuno",
    "version": (1.0),
    "blender": (2, 76, 0),
    'location': 'View3D > Tool Shelf > Create > Curve & Array Set',
    "description": "Curve & Array Modifier Setting. 1.Curves → 2.object  select ",
    "category": "Learnbgame",
}






import bpy


def main(context):
    for ob in context.scene.objects:
        print(ob)


class curve_and_array_set(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.curve_and_array_set"
    bl_label = "Curve & Array Set"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None



    def execute(self, context):
        main(context)
        
        #  アクティブオブジェクトの定義
        active = bpy.context.active_object
        
        #  アクティブオブジェクトの名前を定義
        name = active.name
        
        #  "cv_" + アクティブオブジェクト名に定義 
        objname = "cv_" + name


        #  一度、アクティブの選択を解除し、リネームする
        active.select = False
        for obj in bpy.context.selected_objects:
            obj.name = objname

        #  再度、アクティブを選択
        active.select = True
        
        
        # ーーーーーーーーーーーーーーーーーーーーーーーーー
        # ーーーーーーーーーーーーーーーーーーーーーーーーー
        #  モディファイアを設定ーーーーーーーーーーーーーーーーーーーーーーーーー
                
        # 配列複製モディファイアを追加
        bpy.ops.object.modifier_add(type='ARRAY')

        # 適合する種類 …… カーブ
        bpy.context.object.modifiers["Array"].fit_type = 'FIT_CURVE'

        # カーブオブジェクトを設定 …… カーブ
        bpy.context.object.modifiers["Array"].curve = bpy.data.objects[objname]

        # カーブモディファイアを追加
        bpy.ops.object.modifier_add(type='CURVE')

        # オブジェクトを設定
        bpy.context.object.modifiers["Curve"].object = bpy.data.objects[objname]

        return {'FINISHED'}



        
        #  終了 ーーーーーーーーーーーーーーーーーーーーーーーーー
        # ーーーーーーーーーーーーーーーーーーーーーーーーー
        # ーーーーーーーーーーーーーーーーーーーーーーーーー
                





class curve_and_array_set_Panel(bpy.types.Panel):
    """ """
    bl_label = "Curve & Array Set"
    bl_idname = "curve_and_array_set_"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Create"
    bl_context = "objectmode"



    def draw(self, context):

        layout = self.layout

        row = layout.row()
        layout.operator("object.curve_and_array_set" , icon="PARTICLE_POINT")





def register():
    bpy.utils.register_class(curve_and_array_set)
    bpy.utils.register_class(curve_and_array_set_Panel)


def unregister():
    bpy.utils.unregister_class(curve_and_array_set)
    bpy.utils.unregister_class(curve_and_array_set_Panel)


if __name__ == "__main__":
    register()
