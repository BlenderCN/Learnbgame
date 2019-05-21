
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy
import bmesh
bl_info = {
    "name": "Isolate",
    "description": "contextual Isolate function that work in object and edit mode",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}


class TILA_isolate(bpy.types.Operator):
    bl_idname = "view3d.tila_isolate"
    bl_label = "Isolate"
    bl_options = {'REGISTER', 'UNDO'}

    force_object_isolate = bpy.props.BoolProperty(name='force_object_isolate', default=False)

    is_isolated = False
    isolated_items = []

    def modal(self, context, event):
        pass

    def isolate(self, context,  isolate=None, reveal=None, sel_count=0):
        if sel_count == 0 or self.is_isolated:
            reveal()
            self.is_isolated = False
            self.isolated_items = []
            return 'REVEAL'
        else:
            isolate(unselected=True)
            self.is_isolated = True
            self.isolated_items.append(self.selected_objects)
            return 'ISOLATE'

    def invoke(self, context, event):
        self.selected_objects = bpy.context.selected_objects
        if context.space_data.type == 'VIEW_3D':

            if bpy.context.mode == 'OBJECT':
                if self.isolate(context, isolate=bpy.ops.object.hide_view_set, reveal=bpy.ops.object.hide_view_clear, sel_count=len(self.selected_objects)) == 'REVEAL':
                    bpy.ops.object.select_all(action='INVERT')
            elif bpy.context.mode == 'EDIT_MESH':
                selected_face = []
                for obj in self.selected_objects:
                    faces = obj.data
                    bm = bmesh.from_edit_mesh(faces)
                    for f in bm.faces:
                        if f.select:
                            selected_face.append(f)
                if self.isolate(context, isolate=bpy.ops.mesh.hide, reveal=bpy.ops.mesh.reveal, sel_count=len(selected_face)) == 'REVEAL':
                    bpy.ops.mesh.select_all(action='INVERT')
            elif bpy.context.mode in ['EDIT_CURVE', 'EDIT_SURFACE']:
                pass
            elif bpy.context.mode in ['PAINT_GPENCIL', 'EDIT_GPENCIL', 'SCULPT_GPENCIL']:
                pass

        if context.space_data.type == 'OUTLINER':
            pass

        return {'FINISHED'}


classes = (
    TILA_isolate
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
