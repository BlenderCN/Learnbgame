bl_info = {
"name": "Maskerade",
"author": "Sebastian Koenig",
"version": (1, 0),
"blender": (2, 7, 0),
"location": "Node Editor > maskerade",
"description": "Use hotkeys to add and select masks",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Learnbgame",
}



import bpy



############### FUNCTIONS ##########################


def select_mask():
    # Select the mask in the Image Editor and set Viewer Node

    context = bpy.context
    scene = context.scene
    active_node = scene.node_tree.nodes.active 

    # check whether the active node is a mask
    if active_node.type == 'MASK':
        the_mask = active_node.mask

        # set the correct mode in image and clip editor to the mask (handed over from argument)
        set_mask_mode(the_mask)



def set_mask_mode(mask):
    # Set the Mask mode in image and clip editor

    context = bpy.context
    scene = context.scene
    active_node = scene.node_tree.nodes.active 

    # find image or movie editor
    for area in context.screen.areas: 
        active_space = area.spaces.active

        # set mode to mask and select the mask    
        if area.type == 'IMAGE_EDITOR' or area.type == 'CLIP_EDITOR': 
            active_space.mode = 'MASK' 
            active_space.mask = mask

        # if it's the image editor, assign the viewer node if possible    
        elif area.type == 'IMAGE_EDITOR':
            if bpy.data.images["Viewer Node"]:
                area.spaces.active.image = bpy.data.images["Viewer Node"]


def add_mask_node(the_mask):
    # Add a mask node, connect it to active node 

    context = bpy.context
    scene = bpy.context.scene
    tree = scene.node_tree
    links = tree.links
    
    # link the viewer to the active node 
    active_node = scene.node_tree.nodes.active
    bpy.ops.node.link_viewer()
    scene.node_tree.nodes.active = active_node

    # create a new mask node and link mask to factor input (if that exists)
    my_mask = tree.nodes.new(type="CompositorNodeMask")
    my_mask.location = active_node.location[0]-200, active_node.location[1]+100
    if 'Fac' in active_node.inputs:
        links.new(my_mask.outputs[0], active_node.inputs['Fac'])
    my_mask.use_antialiasing = True
    
    # assing the mask from image editor (handed over from function argument)
    my_mask.mask = the_mask



def add_mask():
    # Add the mask in Clip or Image Editor, and set the Viewer Node if possible

    context = bpy.context
    scene = context.scene
    active_node = scene.node_tree.nodes.active

    # see if the active node has an input and output at all
    if 'Image' in active_node.inputs and 'Image' in active_node.outputs:

        #create a new mask 
        new_mask = bpy.data.masks.new()

        #call the function to set mask mode in image and clip editor
        set_mask_mode(new_mask)
              
        # finally create a new mask node with the current mask as input
        add_mask_node(new_mask)

   


################ CLASSES #################


class SelectMask(bpy.types.Operator):
    bl_idname = "node.select_mask"
    bl_label = "Select Mask"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.tree_type == 'CompositorNodeTree'

    def execute(self, context):
        select_mask()        
        return {'FINISHED'}




class AddMask(bpy.types.Operator):
    bl_idname = "node.add_mask"
    bl_label = "Add Mask"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.tree_type == 'CompositorNodeTree'

    def execute(self, context):
        add_mask()        
        return {'FINISHED'}



########## register ############



def register():
    bpy.utils.register_class(SelectMask)
    bpy.utils.register_class(AddMask)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')

    kmi = km.keymap_items.new('node.select_mask', 'ACTIONMOUSE', 'DOUBLE_CLICK')
    kmi = km.keymap_items.new('node.add_mask', 'M', 'PRESS', ctrl=True )



def unregister():
    bpy.utils.unregister_class(SelectMask)
    bpy.utils.unregister_class(AddMask)


if __name__ == "__main__":
    register()



