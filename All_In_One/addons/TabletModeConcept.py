bl_info = {
    "name": "Tablet Mode",
    "author": "Matthias Ellerbeck",
    "version": (0, 0, 1),
    "blender": (2, 76, 0),
    "location": "No Location",
    "description": "Enables a Tablet Mode for Blender",
    "warning": "Proof of Concept only!",
    "wiki_url": "",
    "category": "Learnbgame",
    }


import bpy

class MouseClickModalOperator(bpy.types.Operator):
    bl_idname = "tabletmode.mouseclick"
    bl_label = "Tablet Mode: Mouseclick"

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            if event.is_tablet != 1.0:
                return{'PASS_THROUGH'}
            elif event.is_tablet == 1.0:
                print("Tablet!")
                return{'RUNNING_MODAL'}
        return{'PASS_THROUGH'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(MouseClickModalOperator)
    #bpy.utils.register_manual_map(add_object_manual_map)
    #bpy.types.INFO_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(MouseClickModalOperator)
    #bpy.utils.unregister_manual_map(add_object_manual_map)
    #bpy.types.INFO_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()
    bpy.ops.tabletmode.mouseclick()