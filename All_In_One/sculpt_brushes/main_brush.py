import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from bpy.types import Menu, Panel, UIList
from bpy.props import *
import os

root = bpy.utils.script_path_user()
sep = os.sep

from bl_ui.properties_paint_common import (
        UnifiedPaintPanel,
        )

def initViewOptions(scn):
    bpy.types.Scene.MirorB = BoolProperty(
        name = "Mirror ", 
        description = "True or False?")
    scn['MirorB'] = False
    
    bpy.types.Scene.CurveB = BoolProperty(
        name = "Curve", 
        description = "True or False?")
    scn['CurveB'] = False
    
    bpy.types.Scene.AlphaB = BoolProperty(
        name = "Alpha", 
        description = "True or False?")
    scn['AlphaB'] = False
    
    bpy.types.Scene.Presetb = BoolProperty(
        name = "Preset", 
        description = "True or False?")
    scn['Presetb'] = False
    
    bpy.types.Scene.Ikb = BoolProperty(
        name = "IK", 
        description = "True or False?")
    scn['Ikb'] = False
    return

#initier les boutons bool dans la scène
initViewOptions(bpy.context.scene)


class View3DPaintPanelBrush(UnifiedPaintPanel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

class VIEW3D_PT_brush(Panel, View3DPaintPanelBrush):
    bl_category = "Brushes"
    bl_label = "Active Brush"

    @classmethod
    def poll(cls, context):
        return (context.sculpt_object and context.tool_settings.sculpt)

    @classmethod
    def poll(cls, context):
        return cls.paint_settings(context)

    def draw(self, context):
        #if sculpt mode
        layout = self.layout
        toolsettings = context.tool_settings
        settings = self.paint_settings(context)
        brush = settings.brush

        if not context.particle_edit_object:
            col = layout.split().column()
            col.template_ID_preview(settings, "brush", new="brush.add", rows=3, cols=8)
            

        
        
        # Particle Mode #
        if context.particle_edit_object:
            tool = settings.tool

            layout.column().prop(settings, "tool", expand=True)

            if tool != 'NONE':
                col = layout.column()
                col.prop(brush, "size", slider=True)
                if tool != 'ADD':
                    col.prop(brush, "strength", slider=True)

            if tool == 'ADD':
                col.prop(brush, "count")
                col = layout.column()
                col.prop(settings, "use_default_interpolate")
                sub = col.column(align=True)
                sub.active = settings.use_default_interpolate
                sub.prop(brush, "steps", slider=True)
                sub.prop(settings, "default_key_count", slider=True)
            elif tool == 'LENGTH':
                layout.prop(brush, "length_mode", expand=True)
            elif tool == 'PUFF':
                layout.prop(brush, "puff_mode", expand=True)
                layout.prop(brush, "use_puff_volume")

        # Sculpt Mode #
        elif context.sculpt_object and brush:
            capabilities = brush.sculpt_capabilities

            col = layout.column()

            col.separator()

            row = col.row(align=True)

            ups = toolsettings.unified_paint_settings
            if ((ups.use_unified_size and ups.use_locked_size) or
                    ((not ups.use_unified_size) and brush.use_locked_size)):
                self.prop_unified_size(row, context, brush, "use_locked_size", icon='LOCKED')
                self.prop_unified_size(row, context, brush, "unprojected_radius", slider=True, text="Radius")
            else:
                self.prop_unified_size(row, context, brush, "use_locked_size", icon='UNLOCKED')
                self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")

            self.prop_unified_size(row, context, brush, "use_pressure_size")

            # strength, use_strength_pressure, and use_strength_attenuation
            row = col.row(align=True)

            if capabilities.has_space_attenuation:
                row.prop(brush, "use_space_attenuation", toggle=True, icon_only=True)

            self.prop_unified_strength(row, context, brush, "strength", text="Strength")

            if capabilities.has_strength_pressure:
                self.prop_unified_strength(row, context, brush, "use_pressure_strength")
                
        
        #Dyntopo
        layout = self.layout
        toolsettings = context.tool_settings
        sculpt = toolsettings.sculpt
        settings = self.paint_settings(context)
        brush = settings.brush


        if context.sculpt_object.use_dynamic_topology_sculpting:
            layout.operator("sculpt.dynamic_topology_toggle", icon='X', text="Disable Dyntopo")
            
            col = layout.column()
            col.active = context.sculpt_object.use_dynamic_topology_sculpting
            sub = col.column(align=True)
            sub.active = (brush and brush.sculpt_tool != 'MASK')
            if (sculpt.detail_type_method == 'CONSTANT'):
                row = sub.row(align=True)
                row.prop(sculpt, "constant_detail")
                row.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
            else:
                sub.prop(sculpt, "detail_size")
            sub.prop(sculpt, "detail_refine_method", text="")
            sub.prop(sculpt, "detail_type_method", text="")
            row = layout.row()
            row.prop(sculpt, "use_smooth_shading")
            row.operator("sculpt.optimize")
            if (sculpt.detail_type_method == 'CONSTANT'):
                col.operator("sculpt.detail_flood_fill")
        else:
            layout.operator("sculpt.dynamic_topology_toggle", icon='SCULPT_DYNTOPO', text="Enable Dyntopo")


#Alpha textures
class View3DPaintPanel(UnifiedPaintPanel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

# Used in both the View3D toolbar and texture properties
def brushoption_texture_settings(layout, brush, sculpt):
    tex_slot = brush.texture_slot

    # map_mode
    if sculpt:
        layout.row().prop(tex_slot, "map_mode", text="")
        layout.separator()
    else:
        layout.row().prop(tex_slot, "tex_paint_map_mode", text="")
        layout.separator()
   
class VIEW3D_Alpha_brush_texture(Panel, View3DPaintPanel):
    bl_category = "Brushes"
    bl_label = "Show Options"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        settings = cls.paint_settings(context)
        return (settings and settings.brush and settings.brush.curve)
    
    @classmethod
    def poll(cls, context):
        settings = cls.paint_settings(context)
        return (settings and settings.brush and
                (context.sculpt_object or context.image_paint_object or context.vertex_paint_object))

    def draw(self, context):
        #Bool show options
        layout = self.layout
        
        sculpt = context.tool_settings.sculpt
        scn = context.scene
        row = layout.row(align=True)
        row.prop(scn, 'AlphaB')
        row.prop(scn, 'MirorB')
        row.prop(scn, 'CurveB')
        row.prop(scn, 'Presetb')
        
        #Preset
        if bpy.context.scene.Presetb:
            layout = self.layout
            
            col = layout.column(align=True)
            col.label(text="Preset:")
            
            row = layout.row()
            box = row.box()
            box.operator("com.button", text="Comming soon: More Preset & IK Brushes", emboss=False, icon = 'PLUGIN').loc="4 11"
                
        #Curve options
        if bpy.context.scene.CurveB:
            layout = self.layout
            
            col = layout.column(align=True)
            col.label(text="Curve:")
            col = layout.column(align=True)
            row = col.row(align=True)

            settings = self.paint_settings(context)

            brush = settings.brush

            layout.template_curve_mapping(brush, "curve", brush=True)
            
           
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("brush.curve_preset", icon='SMOOTHCURVE', text=" ").shape = 'SMOOTH'
            row.operator("brush.curve_preset", icon='SPHERECURVE', text=" ").shape = 'ROUND'
            row.operator("brush.curve_preset", icon='ROOTCURVE', text=" ").shape = 'ROOT'
            row.operator("brush.curve_preset", icon='SHARPCURVE', text=" ").shape = 'SHARP'
            row.operator("brush.curve_preset", icon='LINCURVE', text=" ").shape = 'LINE'
            row.operator("brush.curve_preset", icon='NOCURVE', text=" ").shape = 'MAX'
        
        
        #mirror option
        if bpy.context.scene.MirorB:
            col = layout.column(align=True)
            col.label(text="Mirror:")
            row = col.row(align=True)
            row.prop(sculpt, "use_symmetry_x", text="X", toggle=True)
            row.prop(sculpt, "use_symmetry_y", text="Y", toggle=True)
            row.prop(sculpt, "use_symmetry_z", text="Z", toggle=True)
        
        #Alpha option    
        if bpy.context.scene.AlphaB:
            col = layout.column(align=True)
            col.label(text="Alpha texture:" )
            settings = self.paint_settings(context)
            brush = settings.brush

            col = layout.column()

            col.template_ID_preview(brush, "texture", new="texture.new", rows=3, cols=8)

            brushoption_texture_settings(col, brush, context.sculpt_object)
            
        
        
 

#fonction changer de brosse
def setB(Bname):
    bpy.context.tool_settings.sculpt.brush = bpy.data.brushes[Bname]

#operateur changer de brosse
class OperatorRemplacer(bpy.types.Operator):
    bl_idname = "object.operator_remplacer"
    bl_label = "Change broshes"
    chemin = bpy.props.StringProperty()
    
    def execute(self, context):
        if self.chemin == '':
            print("Hello world!")
        else:
            print("Hello world from %s!" % self.chemin)
            Bname = self.chemin
        
        #executer fonction changer de brosse
        setB(Bname)
  
        return {'FINISHED'}



#ajouter ds liste bouton et icone
def buldB(listebrush = []): 
    #build the sculpt brush list
    for items in bpy.data.brushes:
        # append the brush if hase sculpt capabiliti
        if items.use_paint_sculpt:
            listebrush.append(items.name)
    return listebrush

def buldI(nameI = []): 
    #build the sculpt brush list
    for items in bpy.data.brushes:
        # append the brush if hase sculpt capabiliti
        if items.use_paint_sculpt:
            nameI.append(items.sculpt_tool)
    return nameI

    
#charger le script main_brush.py
def execscript(listebrush = []):
    lien = root + sep + "addons" + sep + "sculpt_brushes" + sep + "main_brush.py"
    bpy.ops.script.python_file_run( filepath = lien )

#operateur charger main_brush.py
class ReloadOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.reload_operator"
    bl_label = "Reload"
 
    def execute(self, context):
        execscript()
        return {'FINISHED'}


#charger le script loadik.py
def execscriptik():
    lien = root + sep + "addons" + sep + "sculpt_brushes" + sep + "loadik.py"
    bpy.ops.script.python_file_run( filepath = lien )

#operateur charger loadik.py
class LoadikOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.loadik_operator"
    bl_label = "Load IK Brushes"
 
    def execute(self, context):
        execscriptik()
        return {'FINISHED'}


#liste bouton
liste = buldB()
nameIcon = buldI()

globalID = int(len(nameIcon))-1
countBrush = str(len(liste)) + ' : Brushes '

def ikexist():
    #verifier l'existance de brosse IK ds les data
    ikbrushexist = False  
    for item in bpy.data.brushes:
        if item.name.endswith("IK"):
            ikbrushexist = True
    return ikbrushexist  


#layout afichage de brosse
class BrushPanel(bpy.types.Panel):
    bl_label = "Brushes"
    bl_idname = "Brushes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Brushes"
    
    
    def draw(self, context):
        if bpy.context.mode == 'SCULPT':
            layout = self.layout
            row = layout.row()
            
            #option IK Brushes  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            customIc = 'MOD_CAST'
            sub = row.row()
            sub.scale_x = 1.8
            
            if ikexist() == False:
                sub.operator("object.loadik_operator", icon = 'MOD_CAST')
                
            if ikexist():
                sub.operator("object.loadik_operator", text = 'Remove IK Brushes', icon = 'MOD_CAST')
                
            row.operator("object.reload_operator", icon = 'FILE_REFRESH')
            
            split = layout.split(align=True)
            index = 0
          
     
            #bouton
            for items in liste:
                col = split.column(align=True)
                col.label(text=countBrush, icon = 'SCULPTMODE_HLT')
                
                dataIcon = bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items.keys()
                
                while index <= int(len(nameIcon)/2):
                    
                    nom = nameIcon[index]
                    Bname = liste[index]
                    nomIco = 'BRUSH_' + nom 
                    
                    if nomIco in dataIcon:
                        if bpy.data.brushes[Bname].use_custom_icon:
                            col.operator("object.operator_remplacer", text = Bname[0:8], icon = customIc, emboss=False ).chemin = Bname
                        else:
                            col.operator("object.operator_remplacer", text = Bname[0:8], icon = nomIco, emboss=False ).chemin = Bname
                    
                    else:
                        if nomIco == 'BRUSH_DRAW':
                            if bpy.data.brushes[Bname].use_custom_icon:
                                col.operator("object.operator_remplacer", text = Bname[0:8], icon = customIc, emboss=False ).chemin = Bname
                            else:
                                col.operator("object.operator_remplacer", text = Bname[0:8], icon = 'BRUSH_SCULPT_DRAW', emboss=False ).chemin = Bname
                        
                    
                    if index <= globalID:
                        index += 1
                        
                #Midel list    
                col = split.column(align=True)
                col.label(text="")
                
                for items in nameIcon:
                    
                    print ("INDEX____NAMEICON/2   :" + str(index)+ "---------" + str(len(nameIcon)))
                    
                    nom = nameIcon[index]
                    Bname = liste[index]
                    nomIco = 'BRUSH_' + nom

                    
                    
                    if nomIco in dataIcon:
                        if bpy.data.brushes[Bname].use_custom_icon:
                            col.operator("object.operator_remplacer", text = Bname[0:8], icon = customIc, emboss=False ).chemin = Bname
                        else:
                            col.operator("object.operator_remplacer", text = Bname[0:8], icon = nomIco, emboss=False ).chemin = Bname
                    
                    else:
                        if nomIco == 'BRUSH_DRAW':
                            if bpy.data.brushes[Bname].use_custom_icon:
                                col.operator("object.operator_remplacer", text = Bname[0:8], icon = customIc, emboss=False ).chemin = Bname
                            else:
                                col.operator("object.operator_remplacer", text = Bname[0:8], icon = 'BRUSH_SCULPT_DRAW', emboss=False ).chemin = Bname
                        
                    
                    if index <= globalID:
                        index += 1
        
        #if active mode # to Sculpt    
        else:
            layout = self.layout
            row = layout.row()
            row.scale_y = 1.2
            row.operator("sculpt.sculptmode_toggle", text="Sculpt", icon='SCULPTMODE_HLT')



class OBJECT_OT_initViewOptions(bpy.types.Operator):
    bl_idname = "idname_must.be_all_lowercase_and_contain_one_dot"
    bl_label = "Print props"
 
    def execute(self, context):
        scn = context.scene
        printProp("Bool:   ", 'AlphaB', scn)
        printProp("Bool:   ", 'MirorB', scn)
        printProp("Bool:   ", 'CurveB', scn)
        printProp("Bool:   ", 'Presetb', scn)
        printProp("Bool:   ", 'Ikb', scn)
        return{'FINISHED'}    
            
#For Comming Button
class OBJECT_OT_Button(bpy.types.Operator):
    bl_idname = "com.button"
    bl_label = "Button"
    row = bpy.props.IntProperty()
    loc = bpy.props.StringProperty()
 
    def execute(self, context):
        if self.loc:
            words = self.loc.split()
            self.row = int(words[0])
            self.number = int(words[1])
        print("Row %d button %d" % (self.row, self.number))
        return{'FINISHED'}             


if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)  
    