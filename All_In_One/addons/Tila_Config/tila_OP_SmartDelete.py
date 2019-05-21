import bpy
bl_info = {
    "name": "Smart Delete",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Learnbgame",
}


class SmartDeleteOperator(bpy.types.Operator):
    bl_idname = "object.tila_smartdelete"
    bl_label = "TILA: Smart Delete"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'EDIT_MESH':
                current_mesh_mode = context.tool_settings.mesh_select_mode[:]
                # if vertex mode on
                if current_mesh_mode[0]:
                    bpy.ops.mesh.dissolve_verts()

                # if vertex mode on
                if current_mesh_mode[1]:
                    bpy.ops.mesh.dissolve_edges(use_verts=False)

                # if vertex mode on
                if current_mesh_mode[2]:
                    bpy.ops.mesh.delete(type='FACE')
            elif context.mode == 'EDIT_CURVE':
                bpy.ops.curve.delete(type='VERT')

            elif context.mode == 'EDIT_GPENCIL':
                try:
                    bpy.ops.gpencil.delete(type='POINTS')
                except Exception as e:
                    print("Warning: %r" % e)
        
            elif context.mode == 'OBJECT':
                bpy.ops.object.delete(use_global=False, confirm=False)

        elif context.space_data.type == 'OUTLINER':
            bpy.ops.outliner.collection_delete(hierarchy=False)
            bpy.ops.outliner.object_operation(type='DELETE')

        # elif context.space_data.type == 'IMAGE_EDITOR':
        #     layout.label("No Context! image editor")
        return {'FINISHED'}


addon_keymaps = []


def register():
    pass
    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = [kc.keymaps.new(name='3D View', space_type='VIEW_3D'),
              kc.keymaps.new(name='Outliner', space_type='OUTLINER'),
              kc.keymaps.new(name='File Browser', space_type='FILE_BROWSER')]

        kmi = [km[0].keymap_items.new(SmartDeleteOperator.bl_idname, 'DEL', 'PRESS'),
               km[1].keymap_items.new(SmartDeleteOperator.bl_idname, 'DEL', 'PRESS'),
               km[2].keymap_items.new(SmartDeleteOperator.bl_idname, 'DEL', 'PRESS')]

        for i in range(len(km)):
            addon_keymaps.append(km[i])


def unregister():
    pass
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
