bl_info = {
    "name": "Split Shape Key",
    "author": "Eduardo Teixeira, SAmbler",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "Object > Animation > Split Shape Key",
    "description": "Takes a shape key and splits its vertices translation into three new shape keys, one per axis, preserving the original",
    "warning": "",
    "wiki_url":"http://blender.stackexchange.com/q/23245/935",
    #"tracker_url": "",
    "category": "Learnbgame",
}

import bpy

class SplitShapeKey(bpy.types.Operator):
    """Takes a shape key and splits its vertices translation
    into three new shape keys, one per axis, preserving the original """
    bl_idname = "anim.split_shape_key"
    bl_label = "Split Shape Key"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context = bpy.context
        scene = context.scene
        obj = context.object
        shape_name = obj.active_shape_key.name

        ## enable shapekey before copying
        skey_value = obj.active_shape_key.value
        obj.active_shape_key.value = obj.active_shape_key.slider_max

        obj.shape_key_add(name=str(shape_name) + "_X", from_mix=True)
        xshape_idx = len(obj.data.shape_keys.key_blocks)-1
        obj.shape_key_add(name=str(shape_name) + "_Y", from_mix=True)
        yshape_idx = len(obj.data.shape_keys.key_blocks)-1
        obj.shape_key_add(name=str(shape_name) + "_Z", from_mix=True)
        zshape_idx = len(obj.data.shape_keys.key_blocks)-1

        ## reset shapekey
        obj.active_shape_key.value = skey_value

        kblocks = obj.data.shape_keys.key_blocks

        for vert in obj.data.vertices: #Isolate the translation on the X axis
            kblocks[xshape_idx].data[vert.index].co.y = kblocks['Basis'].data[vert.index].co.y
            kblocks[xshape_idx].data[vert.index].co.z = kblocks['Basis'].data[vert.index].co.z

        for vert in obj.data.vertices: #Isolate the translation on the Y axis
            kblocks[yshape_idx].data[vert.index].co.x = kblocks['Basis'].data[vert.index].co.x
            kblocks[yshape_idx].data[vert.index].co.z = kblocks['Basis'].data[vert.index].co.z

        for vert in obj.data.vertices: #Isolate the translation on the Z axis
            kblocks[zshape_idx].data[vert.index].co.x = kblocks['Basis'].data[vert.index].co.x
            kblocks[zshape_idx].data[vert.index].co.y = kblocks['Basis'].data[vert.index].co.y

        return{'FINISHED'}

class SplitShapePanel(bpy.types.Panel):
    """Creates a Panel in the Tools Window > Animation Tab"""

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Split Shape Key"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("anim.split_shape_key")

def menu_func(self, context):
    self.layout.operator(SplitShapeKey.bl_idname)

def register():
    bpy.utils.register_class(SplitShapeKey)
    bpy.types.VIEW3D_MT_object_animation.append(menu_func)
    bpy.utils.register_class(SplitShapePanel)

def unregister():
    bpy.utils.unregister_class(SplitShapeKey)
    bpy.types.VIEW3D_MT_object_animation.append(menu_func)
    bpy.utils.unregister_class(SplitShapePanel)

if __name__ == "__main__":
    register()

