bl_info = {
"name": "Image Selector",
"author": "Sebastian Koenig",
"version": (1, 0),
"blender": (2, 7, 0),
"location": "Node Editor > Image Selector",
"description": "Use hotkey to select image data blocks",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Learnbgame"
}



import bpy



############### FUNCTIONS ##########################


def select_image():
    context = bpy.context
    scene = context.scene
    active_node = scene.node_tree.nodes.active 

    # check whether the active node is an image
    if context.active_node.type == 'TEX_IMAGE':
        my_image = context.active_node.image

        for area in context.screen.areas: 
            active_space = area.spaces.active

            # set image editor to the image   
            if area.type == 'IMAGE_EDITOR': 
                area.spaces.active.image = my_image
          


################ CLASSES #################


class SelectMask(bpy.types.Operator):
    bl_idname = "node.select_image"
    bl_label = "Select Image"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.tree_type == 'ShaderNodeTree'
    def execute(self, context):
        select_image()        
        return {'FINISHED'}




########## register ############



def register():
    bpy.utils.register_class(SelectMask)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')

    kmi = km.keymap_items.new('node.select_image', 'ACTIONMOUSE', 'DOUBLE_CLICK')



def unregister():
    bpy.utils.unregister_class(SelectMask)


if __name__ == "__main__":
    register()



