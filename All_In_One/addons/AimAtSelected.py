bl_info = {
        'name': 'AimAtSelected',
        'author': 'bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'View',
        'location': 'View > Aim at selected',
        'wiki_url': ''}

import bpy


def main(context):
    selected = bpy.context.selected_objects
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.view3d.view_center_cursor()

                
class BR_OT_aim_at_selected(bpy.types.Operator):
    """Aim at Selected"""
    bl_idname = "view3d.aim_at_selected"
    bl_label = "Aim Selected"

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def menu_draw(self, context):
    self.layout.operator(BR_OT_aim_at_selected.bl_idname)



def register():
    bpy.utils.register_class(BR_OT_aim_at_selected)
    bpy.types.VIEW3D_MT_view.prepend(menu_draw)  

def unregister():
    bpy.utils.unregister_class(BR_OT_aim_at_selected)
    bpy.types.VIEW3D_MT_view.remove(menu_draw)  

    if __name__ != "__main__":
        bpy.types.VIEW3D_MT_view.remove(menu_draw)

if __name__ == "__main__":
    register()
