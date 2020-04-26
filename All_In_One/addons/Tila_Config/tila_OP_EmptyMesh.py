import bpy
from mathutils import *


class EmptyMeshOperator(bpy.types.Operator):
    bl_idname = "object.tila_emptymesh"
    bl_label = "TILA: Empty Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        currentActiveObject = bpy.context.active_object
        if currentActiveObject:
            currentMode = currentActiveObject.mode
        else:
            currentMode = "OBJECT"

        currentSelection = bpy.context.selected_objects

        if currentMode == "EDIT":
            bpy.ops.object.mode_set(mode='OBJECT')

        plane = bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, location=(0.0, 0.0, 0.0))
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.selected_objects[0].name = "EmptyMesh"

        if currentMode == "EDIT":
            bpy.ops.object.mode_set(mode='EDIT')

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
        kmi = [km[0].keymap_items.new(EmptyMeshOperator.bl_idname, 'N', 'PRESS', shift=True, ctrl=True, alt=True),
               km[1].keymap_items.new(EmptyMeshOperator.bl_idname, 'N', 'PRESS', shift=True, ctrl=True, alt=True),
               km[2].keymap_items.new(EmptyMeshOperator.bl_idname, 'N', 'PRESS', shift=True, ctrl=True, alt=True)]
        for i in range(len(km)):
            addon_keymaps.append((km[i], kmi[i]))


def unregister():
    pass
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
