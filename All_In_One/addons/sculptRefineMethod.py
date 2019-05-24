bl_info = {
    "name": "Sculpt popup",
    "author": "stan",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "",
    "description": "Popup sculpt setting",
    "warning": "",
    "wiki_url": "stan.stz@gmail.com",
    "category": "Learnbgame",
}

import bpy

class SculptMethod(bpy.types.Operator):
    """sculpt refine method"""
    bl_idname = "screen.dialog_operator"
    bl_label = "sculpt refine method"
    bl_options = {'REGISTER', 'UNDO'}

    my_EnumProperty = bpy.props.EnumProperty(
        items = [('SUBDIVIDE', 'SUBDIVIDE', '', '', 1),
                ('COLLAPSE', 'COLLAPSE', '', '', 2),
                ('SUBDIVIDE_COLLAPSE', 'SUBDIVIDE_COLLAPSE', '', '', 3)],
        name = "detail refine method",
       )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = self.my_EnumProperty
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "my_EnumProperty", expand = True)

def addon_button(self, context):
     self.layout.operator(
          "screen.dialog_operator",
          text="sculpt refine method",)

def register():
    bpy.utils.register_class(SculptMethod)
    bpy.types.INFO_HT_header.append(addon_button)

def unregister():
    bpy.utils.unregister_class(SculptMethod)
    bpy.types.INFO_HT_header.remove(addon_button)

if __name__ == "__main__":
    register()
