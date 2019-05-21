######################################################################################################
# A simple add-on to allows the user to precisly place the border render region (Ctrl+B in cam view) #
# using numerical input, witch can be animated                                                       #
# Actualy uncommented (see further version)                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                   #
######################################################################################################


############# Add-on description (used by Blender)

bl_info = {
    "name": "Precise Render Border Adjust",
    "description": 'Allows to modify and animate the "Border Render" region with numerical input.',
    "author": "Lapineige",
    "version": (1, 3),
    "blender": (2, 71, 0),
    "location": "Properties > Render > Precise Render Border Adjust (panel)",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://le-terrier-de-lapineige.over-blog.com/2014/07/precise-render-border-adjust-mon-add-on-pour-positionner-precisement-le-border-render.html",
    "tracker_url": "http://blenderclan.tuxfamily.org/html/modules/newbb/viewtopic.php?topic_id=42159",
    "category": "Learnbgame"
}

##############

import bpy

bpy.types.Scene.x_min_pixels = bpy.props.IntProperty(min=0, description="Minimum X value (in pixel) for the render border")
bpy.types.Scene.x_max_pixels = bpy.props.IntProperty(min=0, description="Maximum X value (in pixel) for the render border")
bpy.types.Scene.y_min_pixels = bpy.props.IntProperty(min=0, description="Minimum Y value (in pixel) for the render border")
bpy.types.Scene.y_max_pixels = bpy.props.IntProperty(min=0, description="Maximum Y value (in pixel) for the render border")


class PreciseRenderBorderAdjust(bpy.types.Panel):
    """Creates the tools in a Panel, in the scene context of the properties editor"""
    bl_label = "Precise Render Border Adjust"
    bl_idname = "Precise_Render_Border_Adjust"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        if not scene.render.use_border:
            sub = layout.split(percentage=0.7)
            sub.label(icon="ERROR", text="Border Render not activated:")
            sub.prop(scene.render, "use_border")
        
        sub = layout.column()
        row = sub.row()
        row.label(text="")
        row.prop(scene.render, "border_max_y", text="Max", slider=True)
        row.label(text="")
        row = sub.row(align=True)
        row.prop(scene.render, "border_min_x", text="Min", slider=True)
        row.prop(scene.render, "border_max_x", text="Max", slider=True)
        row = sub.row()
        row.label(text="")
        row.prop(scene.render, "border_min_y", text="Min", slider=True)
        row.label(text="")
        
        row = layout.row()
        row.label(text="Convert values to pixels:")
        row.operator("render.bordertopixels", text="Border -> Pixels")
        
        layout.label(text="Pixels position X:")
        row = layout.row(align=True)
        row.prop(scene, "x_min_pixels", text="Min")
        row.prop(scene, "x_max_pixels", text="Max")
        layout.label(text="Pixels position Y:")
        row = layout.row(align=True)
        row.prop(scene, "y_min_pixels", text="Min")
        row.prop(scene, "y_max_pixels", text="Max")
        
        layout.label(icon="INFO", text="Don't forget to apply pixels values")
        row = layout.row()
        row.operator("render.pixelstoborder", text="Pixels -> Border")

class PixelsToBorder(bpy.types.Operator):
    """ Convert the pixel value into the proportion needed by the Blender native property """
    bl_idname = "render.pixelstoborder"
    bl_label = "Convert Pixels to Border proportion"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        C = bpy.context
    
        X = C.scene.render.resolution_x
        Y = C.scene.render.resolution_y
        
        C.scene.render.border_min_x = C.scene.x_min_pixels / X
        C.scene.render.border_max_x = C.scene.x_max_pixels / X
        C.scene.render.border_min_y = C.scene.y_min_pixels / Y
        C.scene.render.border_max_y = C.scene.y_max_pixels / Y
        
        if C.scene.x_min_pixels > X:
            C.scene.x_min_pixels = X
        if C.scene.x_max_pixels > X:
            C.scene.x_max_pixels = X
        if C.scene.y_min_pixels > Y:
            C.scene.y_min_pixels = Y
        if C.scene.y_max_pixels > Y:
            C.scene.y_max_pixels = Y
        
        return {'FINISHED'}
    
class BorderToPixels(bpy.types.Operator):
    """ Convert the Blender native property value to pixels"""
    bl_idname = "render.bordertopixels"
    bl_label = "Convert border values to pixels"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        C = bpy.context
    
        X = C.scene.render.resolution_x
        Y = C.scene.render.resolution_y
        
        C.scene.x_min_pixels = int(C.scene.render.border_min_x * X)
        C.scene.x_max_pixels = int(C.scene.render.border_max_x * X)
        C.scene.y_min_pixels = int(C.scene.render.border_min_y * Y)
        C.scene.y_max_pixels = int(C.scene.render.border_max_y * Y)
                
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PreciseRenderBorderAdjust)
    bpy.utils.register_class(PixelsToBorder)
    bpy.utils.register_class(BorderToPixels)


def unregister():
    bpy.utils.unregister_class(PreciseRenderBorderAdjust)
    bpy.utils.unregister_class(PixelsToBorder)
    bpy.utils.unregister_class(BorderToPixels)


if __name__ == "__main__":
    C = bpy.context
    
    X = C.scene.render.resolution_x
    Y = C.scene.render.resolution_y
    
    C.scene.x_min_pixels = 0
    C.scene.x_max_pixels = X
    C.scene.y_min_pixels = 0
    C.scene.y_max_pixels = Y
    
    register()
