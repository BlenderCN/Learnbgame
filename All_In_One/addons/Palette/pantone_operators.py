import bpy
import os

from .pantone_functions import generate_similar_pantone, generate_monochromatic_pantone, generate_shading_pantone, generate_triad_pantone, generate_complementary_pantone
from .files_functions import GetPrefPath
from .node_functions import CreateNodeGroupFromPalette

class PaletteCreatePantone(bpy.types.Operator):
    bl_idname = "palette.create_pantone"
    bl_label = "Create Pantone"
    bl_description = "Create New Pantone from selected Base Color"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def check(self, context):
        return True

    def draw(self, context):
        palette_prop=bpy.data.window_managers['WinMan'].palette[0]
        layout = self.layout
        split=layout.split()
        col=split.column(align=False)
        col.label('Name')
        col.label('Base')
        col.label('Type')
        col.label('Offset')
        col.label('Precision')
        col=split.column(align=False)
        col.prop(palette_prop, 'pantone_name',text='')
        col.prop(palette_prop, 'pantone_base_color', text='')
        col.prop(palette_prop, 'pantone_type',text='')
        col.prop(palette_prop, 'pantone_offset',text='', slider=True)
        col.prop(palette_prop, 'pantone_precision',text='', slider=True)
        
    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        palettes=prop.palettes
        base_color=prop.pantone_base_color
        category=prop.pantone_type
        name=prop.pantone_name
        decalage=prop.pantone_offset
        precision=prop.pantone_precision
        
        #check for non existing name
        old_name=[]
        for p in palettes:
            if name in p.name:
                old_name.append(p.name)
        if len(old_name)!=0:
            old_name.sort()
            try:
                namenb=int((old_name[len(old_name)-1]).split(name+"_")[1])+1
            except IndexError:
                namenb=1
            name=name+"_"+str(namenb)
        else:
            name=name
        
        new_palette=palettes.add()
        new_palette.name=name
        new_palette.filepath=os.path.join(GetPrefPath(), new_palette.name+".gpl")
        if category=='SIMILAR':
            new_colors=generate_similar_pantone(decalage, precision, base_color)
        elif category=='MONOCHROMATIC':
            new_colors=generate_monochromatic_pantone(decalage, precision, base_color)
        elif category=='SHADING':
            new_colors=generate_shading_pantone(decalage, precision, base_color)
        elif category=='TRIAD':
            new_colors=generate_triad_pantone(decalage, precision, base_color)
        elif category=='COMPLEMENTARY':
            new_colors=generate_complementary_pantone(decalage, precision, base_color)
        ct=0
        for c in new_colors:
            ct+=1
            col=new_palette.colors.add()
            col.color_value=c
            col.name=name+"_"+str(ct)
            
        CreateNodeGroupFromPalette(new_palette)
        
        return {"FINISHED"}
        