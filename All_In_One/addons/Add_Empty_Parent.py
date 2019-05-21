bl_info = {
"name": "Add a parent",
"author": "Chebhou",
"version": (1, 0),
"blender": (2, 65, 0),
"description": "Adds a parent for the selected objects",
"category": "Learnbgame"
}


import bpy
import sys
from bpy.props import BoolProperty, EnumProperty, StringProperty

def add_parent(self, context):
    selected_obj = bpy.context.selected_objects.copy()
    if self.position != 'None' :
        exec("bpy.ops.view3d.snap_cursor_to_%s()"%self.position)
    bpy.ops.object.empty_add(type = self.type)
    bpy.context.object.name = self.name
    inv_mat = bpy.context.object.matrix_world.inverted()
    for obj in selected_obj :
        obj.parent = bpy.context.object
        if self.inverse :
            obj.matrix_parent_inverse = inv_mat

class AddParent(bpy.types.Operator):
    """Create a new parent"""
    bl_idname = "object.add_parent"
    bl_label = "Add a parent"
    bl_options = {'REGISTER', 'UNDO'}

    type  = EnumProperty(
        name="empty type",
        description="choose the empty type",
        items=(('PLAIN_AXES', "Axis", "Axis"),
                ('ARROWS', "Arrows", "Arrows"),
                ('SINGLE_ARROW', "Single arrow", "Single arrow"),
                ('CIRCLE', "Circle", "Circle"),
                ('CUBE', "Cube", "Cube"),
               ('SPHERE', "Sphere", "Sphere"),
               ('CONE', "Cone", "Cone")),
        default='PLAIN_AXES'
        )

    inverse = BoolProperty(                        
                name = "parent inverse",                          
                default = 0,                
                description = "check to set the inverse"
                )


    position  = EnumProperty(
                name="parent position",
                description="where to create the parent",
                items=(('center', "World center", "World center"),
                       ('None', "Cursor position", "Cursor position"),
                       ('selected', "Median point", "Median position"),
                       ('active', "Active object position", "Active position"),),
                default='center'
                )

    name      = StringProperty(
                name ="name",
                default ="Parent")

    def execute(self, context):
        add_parent(self, context)
        return {'FINISHED'}


addon_keymaps = []

def register():
    bpy.utils.register_class(AddParent)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(AddParent.bl_idname, 'P', 'PRESS')# you can chnge the shortcut later
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(AddParent)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
