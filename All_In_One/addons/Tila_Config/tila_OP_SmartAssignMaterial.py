import bpy
import bmesh
from pprint import pprint
bl_info = {
    "name": "Smart Assign Material",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Learnbgame",
}


class SmartMaterialAssignOperator(bpy.types.Operator):
    bl_idname = "object.tila_smart_assign_material"
    bl_label = "TILA: Assign material to selected faces or objects"
    bl_options = {'REGISTER', 'UNDO'}

    def get_selected_face(self):
        selected = ()
        for o in bpy.context.selected_objects:
            bm = bmesh.new()
            bm.from_mesh(o.data)
            for f in bm.faces:
                if f.select:
                    selected = selected + (o,)
                    break

        return selected

    def execute(self, context):
        if context.space_data.type == 'VIEW_3D':

            if context.mode == 'OBJECT':
                for o in bpy.context.selected_objects:
                    if o.type == 'MESH':
                        print(o.name)
                        bpy.context.scene.objects.active = o
                        bpy.ops.object.material_slot_assign()
            if context.mode == 'EDIT_MESH':
                selected_face = self.get_selected_face()

                for f in selected_face:
                    bpy.ops.object.editmode_toggle()
                    bpy.data.objects[f.name].select_set(True)
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.object.material_slot_add()
                    bpy.ops.object.material_slot_assign()

        return {'FINISHED'}


addon_keymaps = []


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
