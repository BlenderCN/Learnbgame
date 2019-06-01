bl_info = {
    "name": "Transfer Shape Keys",
    "author": "Olli Hihnala",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Object > Mesh > Transfer Shape Keys by Surface",
    "description": "Transfer shape keys between non-identical meshes",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}


import bpy


def main(self, context):
    target = None
    source = None
    if len(context.selected_objects) == 2:
        target = bpy.context.object
        for object in context.selected_objects:
            if object != target:
                source = object
                if not source.data.shape_keys or len(source.data.shape_keys.key_blocks) < 2:
                    self.report({'INFO'}, "No shape keys found to transfer")
                    return {'CANCELLED'}
    else:
        self.report({'INFO'}, "Selected two objects")
        return {'CANCELLED'}

    key_values = {}
    for key in source.data.shape_keys.key_blocks:
        key_values[key.name] = key.value

    if source.data.shape_keys:
        keys = source.data.shape_keys.key_blocks[1:]
        for key in keys:
            key.value = 0
            bpy.context.scene.update()
            modifier = target.modifiers.new(
                name=key.name, type='SURFACE_DEFORM')
            modifier.target = source
            bpy.ops.object.surfacedeform_bind(modifier=modifier.name)
            key.value = 1
            bpy.context.scene.update()
            bpy.ops.object.modifier_apply(
                apply_as='SHAPE', modifier=modifier.name)
            key.value = 0

        for key in keys:
            print(key)
            key.value = key_values[key.name]
    return {'FINISHED'}


class TransferShapeKeysBySurface(bpy.types.Operator):
    """Transfer shape keys between non-identical meshes"""
    bl_idname = "object.transfer_shape_keys_by_surface"
    bl_label = "Transfer Shape Keys by Surface"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        result = main(self, context)
        if 'CANCELLED' in result:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}


def add_to_object_menu(self, context):
    self.layout.operator(TransferShapeKeysBySurface.bl_idname)


def register():
    bpy.utils.register_class(TransferShapeKeysBySurface)
    bpy.types.VIEW3D_MT_object.append(add_to_object_menu)


def unregister():
    bpy.utils.unregister_class(TransferShapeKeysBySurface)
    bpy.types.VIEW3D_MT_object.remove(add_to_object_menu)


if __name__ == "__main__":
    register()
