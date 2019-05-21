bl_info = {
    "name": "Copy Size",
	"description": "Copies the scale and dimension of the active object to the selected objects",
    "category": "Object",
	"blender": (2, 77, 0),
    "author": "Akshay More",
}

import bpy

class ObjectCopySize(bpy.types.Operator):
    """Object Copy Size"""
    bl_idname = "object.copy_size"
    bl_label = "Copy Size"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        obj = scene.objects.active
        
        for i in bpy.context.selected_objects:
            if i!=obj:
                i.scale=obj.scale
                i.dimensions=obj.dimensions
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ObjectCopySize)


def unregister():
    bpy.utils.unregister_class(ObjectCopySize)


if __name__ == "__main__":
    register()
