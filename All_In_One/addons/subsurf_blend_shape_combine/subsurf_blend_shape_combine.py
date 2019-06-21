import bpy

class SubsurfBlendShapeCombine(bpy.types.Operator):
    
    bl_idname = "blendshape.subsurf_blend_shape_combine"
    bl_label = "Subsurf Blend Shape Combine"
    bl_description = "Subsurf Blend Shape Combine"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        activeObject = bpy.context.active_object
        if activeObject.data.shape_keys is None:
            print("Shape keys is None")
            return {'FINISHED'}

        duplicatedObjects = []
        key_blocks = activeObject.data.shape_keys.key_blocks.values()
        for key_block in key_blocks:
            print(key_block.name)

            bpy.ops.object.duplicate(linked=False)
            duplicatedObject = bpy.context.scene.objects.active
            duplicatedObject.name = key_block.name
            duplicatedObject.data.shape_keys.key_blocks[key_block.name].value = 1

            # 現在のシェイプキーを最後に消す
            index = 0
            for remove_key_block in key_blocks:
                if remove_key_block is key_block:
                    index+=1
                    continue

                duplicatedObject.active_shape_key_index = index
                bpy.ops.object.shape_key_remove()

            duplicatedObject.active_shape_key_index = 0
            bpy.ops.object.shape_key_remove()

            bpy.ops.object.modifier_apply(modifier="Subsurf")
            bpy.ops.object.select_all(action='DESELECT')
            activeObject.select = True
            bpy.context.scene.objects.active = activeObject

            duplicatedObjects.append(duplicatedObject)
        

        bpy.ops.object.select_all(action='DESELECT')
        basicObject = duplicatedObjects[0]
        basicObject.select = True
        bpy.context.scene.objects.active = basicObject

        for joinObject in duplicatedObjects:
            if joinObject is basicObject:
                continue
            joinObject.select = True

        bpy.ops.object.join_shapes()

        basicObject.select = False
        bpy.ops.object.delete(use_global=False)

        return {'FINISHED'}