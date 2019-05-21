bl_info = {
    "name": "Viewer Target",
    "author": "Sebastian Koenig",
    "version": (0, 1),
    "blender": (2, 7, 2),
    "description": "Doubleclick to set the viewer node focus to the mouse position",
    "category": "Learnbgame"
}



import bpy

class NODE_OT_Viewer_Focus(bpy.types.Operator):
    """ Set the viewer tile center to the mouse position
    """
    bl_idname = "node.viewer_focus"
    bl_label = "Viewer Focus"

    x = bpy.props.IntProperty()
    y = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'NODE_EDITOR')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        render = context.scene.render
        space = context.space_data
        percent = render.resolution_percentage*0.01
        
        for n in bpy.context.scene.node_tree.nodes:
            if n.type == "VIEWER":
                self.x = event.mouse_region_x
                self.y = event.mouse_region_y

                region_x=context.region.width
                region_y=context.region.height

                region_center_x=region_x/2
                region_center_y=region_y/2

                rel_region_mouse_x=region_x-self.x
                rel_region_mouse_y=region_y-self.y
                
                bd_x = render.resolution_x*percent*space.backdrop_zoom
                bd_y = render.resolution_y* percent*space.backdrop_zoom

                backdrop_center_x=(bd_x/2)-space.backdrop_x
                backdrop_center_y=(bd_y/2)-space.backdrop_y

                margin_x = region_center_x-backdrop_center_x
                margin_y = region_center_y-backdrop_center_y
                
                absolute_x_max = margin_x+bd_x
                absolute_y_max = margin_y+bd_y

                abs_mouse_x = (self.x-margin_x)/bd_x
                abs_mouse_y = (self.y-margin_y)/bd_y

                rel_bd_x = (bd_x-rel_region_mouse_x)
                rel_bd_y = (bd_y-rel_region_mouse_y)

                n.center_x = abs_mouse_x
                n.center_y = abs_mouse_y

        return self.execute(context)



def register():
    bpy.utils.register_class(NODE_OT_Viewer_Focus)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
    kmi = km.keymap_items.new('node.viewer_focus', 'ACTIONMOUSE', 'DOUBLE_CLICK')

def unregister():
    bpy.utils.register_class(NODE_OT_Viewer_Focus)


if __name__ == "__main__":
    register()
