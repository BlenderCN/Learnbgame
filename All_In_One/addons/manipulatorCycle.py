bl_info = {
    "name": "Manipulator Cycle",
    "author": "stan",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "",
    "description": "Cycle manipulator",
    "warning": "",
    "wiki_url": "stan.stz@gmail.com",
    "category": "Learnbgame"
}
    
import bpy

class StanManipulator(bpy.types.Operator):
    """Cycle manipulator"""
    bl_idname = "scene.stan_manipulator"
    bl_label = "Cycle manipulator"
    
    def execute(self, contect):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.show_manipulator = True
                        if space.transform_manipulators == {'TRANSLATE'}:
                            space.transform_manipulators = {'ROTATE'}
                        elif space.transform_manipulators == {'ROTATE'}:
                            space.transform_manipulators = {'SCALE'}
                        elif space.transform_manipulators == {'SCALE'}:
                            space.transform_manipulators = {'TRANSLATE'}
                        else:
                            space.transform_manipulators = {'TRANSLATE'}
        return {'FINISHED'}

def addon_button(self, context):
     self.layout.operator(
          "scene.stan_manipulator",
          text="Cycle manipulator",)


def register():
    bpy.utils.register_class(StanManipulator)
    bpy.types.INFO_HT_header.append(addon_button)

def unregister():
    bpy.utils.unregister_class(StanManipulator)
    bpy.types.INFO_HT_header.remove(addon_button)

if __name__ == "__main__":
    register()