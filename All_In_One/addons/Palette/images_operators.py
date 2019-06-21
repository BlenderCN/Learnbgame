import bpy

from .files_functions import GenerateImageFromPalette
from .node_functions import PaletteListCallback

# create image
class PaletteCreateImagePalette(bpy.types.Operator):
    bl_idname = "palette.create_image_palette"
    bl_label = "Create Image"
    bl_description = "Create Image from Palette"
    bl_options = {"REGISTER", "UNDO"}
    
    image_name=bpy.props.StringProperty(name='Name', default='image_palette')
    image_size_x=bpy.props.IntProperty(name='Resolution X', default=128, min=8)
    image_size_y=bpy.props.IntProperty(name='Resolution Y', default=128, min=8)
    palette_list=bpy.props.EnumProperty(name='Palette List', items=PaletteListCallback)

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def check(self, context):
        return True

    def draw(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        layout = self.layout
        col=layout.column()
        col.prop(self, 'palette_list', text="")
        col.prop(self, 'image_name')
        row=col.row()
        row.prop(self, 'image_size_x')
        row.prop(self, 'image_size_y')
        if len(prop.palettes[self.palette_list].colors)>self.image_size_x:
            col.label('More Colors than Pixels', icon='INFO')
            col.label('Increase the X resolution to display all the palette')
    
    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        palette=prop.palettes[self.palette_list]
        GenerateImageFromPalette(self.image_name, palette, self.image_size_x, self.image_size_y)
        return {'FINISHED'}
