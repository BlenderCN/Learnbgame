#==================================================================
#  Copyright (C) 6/27/2014  Blender Sensei (Seth Fentress)
#  ####BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#  ####END GPL LICENSE BLOCK #####
#  To report a bug or suggest a feature visit:
#  Blendersensei.com/forums/zerobrush
#  VISIT Blendersensei.com for more information.
#  SUBSCRIBE at Youtube.com/Blendersensei
#====================================================================

bl_info = {  
 "name": "Zero Brush",  
 "author": "Blender Sensei (Seth Fentress) Blendersensei.com",
 "version": (1, 0, 0),
 "blender": (7, 1, 0),  
 "location": "Found in the properties shelf/ Brush options in tool shelf/ Press SPACE when available for menu",  
 "description": "Zero button texture painting by Blender Sensei. Full Functionality in Blender Render. Support for Cycles coming soon.",  
 "wiki_url": "http://blendersensei.com/zero-brush",  
 "category": "Learnbgame"
}  

import bpy
from bpy.props import*
import os
from bpy_extras.io_utils import ImportHelper
#Extra imports for custom brush panel
from bpy.types import Menu, Panel
from bl_ui.properties_paint_common import (
        UnifiedPaintPanel,
        brush_texture_settings,
        )


#Brush Loading==============================================
#Clean brush names
def cleanBrushName(fn):
    #Strip selected from name
    newName = ''.join(x for x in fn if x not in 
    ',<>:""[]{}()/\|!@#$%^&*,.?')
    #List of stuff to remove from file name
    toReplace = ['seamless','texture','tex','by:','free', '.com',
    '.net','.org','the','image','photos', 'original','photo', 'tileable']
    #Now remove it.
    newName = newName.lower()
    for bad in toReplace:
        newName = newName.replace(bad, "")
    
    #Recoginze as intentional spaces        
    newName = newName.replace("-", " ")
    newName = newName.replace("_", " ")
    
    #Author kill. Remove all after " by " found.
    sep = " by "
    newName = newName.split(sep, 1)[0]
    newName = newName.title()
    
    #Parenth kill. Remove all after "(" found.
    sep = "("
    newName = newName.split(sep, 1)[0]
    newName = newName.title()
    
    #If name to long get rid of spaces
    if len(newName) > 20:
        newName = newName.replace(" ", "")    
    
    #18 max characters
    newName = newName[:18]
    
    x = 0
    # if first letters blank
    while x < 18:
        if newName[:1] == " ":
            newName = newName[1:]
        else:
            break
        x += 1

    #Add generic if name to short
    if len(newName) < 1:
        newName = "myBrush"
    
    #Seperate new from standard brushes
    newName = "°" + newName    
    return newName
        
               
#Load single brush
def load_a_brush(context, filepath):
    if os.path.isdir(filepath):
        return
    else:
        try:
            fn = bpy.path.display_name_from_filepath(filepath)
            #create image and load...
            img = bpy.data.images.load(filepath)
            img.use_fake_user =True
            
            #create a texture
            tex = bpy.data.textures.new(name =fn, type='IMAGE')
            #link the img to the texture
            tex.image = img
            
            settings = bpy.context.tool_settings
            #Create New brush
            if bpy.context.mode.startswith('PAINT') is True:
                #switch brush to assure inherited properties
                try:
                    settings.image_paint.brush = bpy.data.brushes["Draw"]
                except:
                    pass
                bpy.ops.brush.add()
                brush = bpy.context.tool_settings.image_paint.brush
                #Set up new brush settings
                bpy.ops.brush.curve_preset(shape='SHARP')
                brush.color = (1, 1, 1)
                brush.strength = 1
                
            elif bpy.context.mode.startswith('SCULPT') is True:
                #switch brush to assure inherited properties
                try:
                    settings.sculpt.brush = bpy.data.brushes["SculptDraw"]
                except:
                    pass
                #Create New brush and assign texture
                bpy.ops.brush.add()
                brush = bpy.context.tool_settings.sculpt.brush
                bpy.ops.brush.curve_preset(shape='SHARP')
                brush.strength = 0.125
                brush.auto_smooth_factor = 0.15
            
            #Clean up brush name from file name
            #Run function, return results to newName
            newName = cleanBrushName(fn)
            
            #Give brush name cleaned filename
            brush.name = newName
            #Assign texture to brush
            brush.texture = tex

            #Give brush texture icon
            brush.use_custom_icon = True
            brush.icon_filepath = filepath
            
            #Change method of brush
            brush.stroke_method = 'DOTS'
            brush.texture_slot.tex_paint_map_mode = 'TILED'
            #Update brush texture scale option
            bpy.data.window_managers["WinMan"].texBrushScale = 85
        except:
            pass
    return {'FINISHED'}


class load_single_brush(bpy.types.Operator, ImportHelper):
    bl_idname = "texture.load_single_brush"  
    bl_label = "Brush"
    bl_description = "Load an image (png, jpeg, tiff, etc..) as a brush"
    
    @classmethod
    def poll(cls, context):
        return context.active_object != None
    def execute(self, context):
        return load_a_brush(context, self.filepath)


#Load a folder of brushes
def loadbrushes(context, filepath):
    if os.path.isdir(filepath):
        directory = filepath 
    else:
        #is a file, find parent directory    
        li = filepath.split(os.sep)
        directory = filepath.rstrip(li[-1])
        
    files = os.listdir(directory)
    for f in files:
        try:
            fn = f[3:]
            #create image and load...
            img = bpy.data.images.load(filepath = directory +os.sep + f)
            img.use_fake_user =True
            #create a texture
            tex = bpy.data.textures.new(name =fn, type='IMAGE')
            tex.use_fake_user =True
            #link the img to the texture
            tex.image = img
        except:
            pass
        
        settings = bpy.context.tool_settings
        #Create New brush
        if bpy.context.mode.startswith('PAINT') is True:
            #switch brush to assure inherited properties
            try:
                settings.image_paint.brush = bpy.data.brushes["Draw"]
            except:
                pass
            bpy.ops.brush.add()
            brush = bpy.context.tool_settings.image_paint.brush
            bpy.ops.brush.curve_preset(shape='SHARP')
            #Set up new brush settings
            brush.color = (1, 1, 1)
            
        elif bpy.context.mode.startswith('SCULPT') is True:
            #switch brush to assure inherited properties
            try:
                settings.sculpt.brush = bpy.data.brushes["SculptDraw"]
            except:
                pass
            #Create New brush and assign texture
            bpy.ops.brush.add()
            brush = bpy.context.tool_settings.sculpt.brush
            bpy.ops.brush.curve_preset(shape='SHARP')
            brush.strength = 0.125
            brush.auto_smooth_factor = 0.15
                   
        #Clean up brush name from file name
        fn = bpy.path.display_name_from_filepath(directory +os.sep + f)
        newName = cleanBrushName(fn)
        
        #Give brush name of file name
        brush.name = newName
        brush.texture = tex
            
        #Give brush texture icon
        brush.use_custom_icon = True
        brush.icon_filepath = directory +os.sep + f
        
        #Change method of brush
        brush.stroke_method = 'DOTS'
        brush.texture_slot.tex_paint_map_mode = 'TILED'
        
    #Update brush texture scale option
    bpy.data.window_managers["WinMan"].texBrushScale = 85
    return {'FINISHED'}


class ImportBrushes(bpy.types.Operator, ImportHelper):
    bl_idname = "texture.load_brushes"  
    bl_label = "Brushes"
    bl_description = "Load a folder of images (png, jpeg, tiff, etc..) as brushes"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        return loadbrushes(context, self.filepath)
#End of brush loading=============================



#Brush Menu=======================================        
#Required to invoke menu
def justForKix(context):
    pass

class SCULPT_MT_brush_menu(bpy.types.Menu):
    bl_idname = "SCULPT_MT_brush_menu"
    bl_label = "Sculpt Brush"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        flow = layout.column_flow(columns=4)
        for brush in bpy.data.brushes:
            if brush.use_paint_sculpt:
                col = flow.column()
                props = col.operator("wm.context_set_id", text=brush.name)
                props.data_path = "tool_settings.sculpt.brush"
                props.value = brush.name
                
                
class IMAGE_MT_brush_menu(bpy.types.Menu):
    bl_idname = "IMAGE_MT_brush_menu"
    bl_label = "Paint Brush"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        flow = layout.column_flow(columns=4)
        for brush in bpy.data.brushes:
            if brush.use_paint_image:
                col = flow.column()
                props = col.operator("wm.context_set_id", text=brush.name)
                props.data_path = "tool_settings.image_paint.brush"
                props.value = brush.name


class selectBrush(bpy.types.Operator):
    bl_idname = "object.select_brush"
    bl_label = "Select Brush"
    bl_options = {'DEFAULT_CLOSED'}
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def invoke(self, context, event):
        context.window_manager.invoke_props_popup(self, event)
        return {'FINISHED'}
    
    #Required to invoke menu
    def execute(self, context):
        justForKix(context)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        toolsettings = context.tool_settings
        settings = UnifiedPaintPanel.paint_settings(context)
        brush = settings.brush

        if not context.particle_edit_object:
            flow = layout.column_flow(columns=2)
            for brush in bpy.data.brushes:
                #Sculpt Brush Menu
                if context.sculpt_object:
                    if brush.use_paint_sculpt:
                        row = flow.row(align=True)
                        row.label(icon_value=layout.icon(brush))
                        props = row.operator("wm.context_set_id", text=brush.name)
                        props.data_path = "tool_settings.sculpt.brush"
                        props.value = brush.name
                #Texture Paint Brush Menu
                if context.image_paint_object:
                    if brush.use_paint_image:    
                        row = flow.row(align = True)
                        
                        row.label(icon_value=layout.icon(brush))
                        props = row.operator("wm.context_set_id", text=brush.name)
                        props.data_path = "tool_settings.image_paint.brush"
                        props.value = brush.name
        else:
            #Particle Brush Menu
            col = layout.column()            
            tool = settings.tool
            
            if tool == 'ADD':
                row = layout.row(align=True)
                row.prop(brush, "count")
            elif tool == 'LENGTH':
                row = layout.row(align=True)
                row.prop(brush, "length_mode", expand=True)
            elif tool == 'PUFF':
                row = layout.row(align=True)
                row.prop(brush, "puff_mode", expand=True)
            row = layout.row(align=True)
            row.prop(settings, "tool", expand=True)
            

#Convert skin object to workable object
def skinExtractor():
    bpy.ops.object.mode_set(mode='OBJECT')
    #make armature from the skin
    realOb = bpy.context.active_object #store original object
    armature = len([mod for mod in realOb.modifiers if mod.type == 'ARMATURE'])
    if armature < 1:
        bpy.ops.object.skin_armature_create(modifier="Skin") #create bones
        ob = bpy.context.active_object #store the bones
        #Turn on auto IK
        bones = bpy.context.object.data
        bones.use_auto_ik = True
        ob.name = realOb.name + "sBones" #Name the bones
        bpy.context.active_object.select = False #deselect bones
        bpy.context.object.hide = True #Turn off bones visibility
        bpy.context.scene.objects.active = realOb #set flesh as active
        
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Skin")
    realOb.select = True #select flesh
    bpy.context.space_data.use_occlude_geometry = True #Turn off seethrough
    #Clean up mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.vert_connect_nonplanar()
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.object.mode_set(mode='OBJECT')
    for x in range(20):
        bpy.ops.object.modifier_move_up(modifier="Armature") #send mod to top
    return{'FINISHED'}            


#Mode Change Buttons========================================
class modeButtons(bpy.types.Operator):
    bl_idname = "object.mode_buttons"
    bl_label = "Button"
    bl_description = "Select Mode: Object | Sculpt | Paint | Particle Strands"
    modeButton = bpy.props.IntProperty(name = 'modeValue', default = 0)
            
    def execute(self, context):
        ob = bpy.context.active_object
        
        if ob and ob.type == 'MESH':
            mat = ob.active_material
            #Save texture layers if leaving texture paint       
            if self.modeButton != 3 and self.modeButton < 5:
                if bpy.context.mode.startswith('PAINT'):  
                    if mat:
                        for ts in mat.texture_slots:
                            if ts and ts.texture.type == 'IMAGE':
                                if ts.texture_coords  == 'UV':
                                    image = ts.texture.image
                                    bpy.ops.image.pack({'edit_image': image}, as_png = True)
                        self.report({'INFO'}, "Paint layers saved.")
    
            #Object Mode
            if self.modeButton == 1:
                #Turn multires back on
                try:
                    bpy.context.object.modifiers["Multires"].show_viewport = True
                except:
                    pass
                bpy.context.space_data.viewport_shade = 'TEXTURED'
                bpy.ops.object.mode_set(mode='OBJECT')
            
            #Sculpt Mode    
            elif self.modeButton == 2:
                #Turn multires back on
                try:
                    bpy.context.object.modifiers["Multires"].show_viewport = True
                except:
                    pass
                bpy.ops.object.mode_set(mode='SCULPT')
                
                if bpy.data.window_managers["WinMan"].fast_mode == True:
                    bpy.context.space_data.viewport_shade = 'SOLID'
                
                #Update brush texture scale option
                try:
                    ts = context.tool_settings.sculpt.brush.texture_slot
                    bpy.data.window_managers["WinMan"].texBrushScale = round((3 - ts.scale[0]) * 33.33333)
                    if bpy.data.window_managers["WinMan"].texBrushScale == 97:
                        bpy.data.window_managers["WinMan"].texBrushScale = 100
                    texBrushScaleUpdater(self, context)
                except:
                    pass
                
            #Texture Paint Mode     
            elif self.modeButton == 3:
                #Turn multires back on
                try:
                    bpy.context.object.modifiers["Multires"].show_viewport = True
                except:
                    pass
                
                #Apply skin if exists
                ob = bpy.context.active_object
                skin = len([mod for mod in ob.modifiers if mod.type == 'SKIN'])
                if skin:
                    skinExtractor()
                    self.report({'INFO'}, 
                    ("Applied Skin modifier to object. Click the 'Eye' icon next" 
                    " to your character's bones in the outliner to view them."))
                #Message if didn't make armature
                report = 0
                for type in ob.modifiers:
                    try:
                        if "Bones" not in type.object.name:
                            report = 1
                            break
                    except:
                        pass
                if report == 1:    
                    self.report({'INFO'}, "Object already has armature. None created for it.")          
                a = 0
                #Add default color layer if none found
                if ob is not None and ob.active_material is not None:
                    for ts in ob.active_material.texture_slots:
                        if ts and ts.texture.type == 'IMAGE':
                            if ts.texture_coords  == 'UV':
                                a += 1

                if a == 0:
                    bpy.ops.object.zb_paint_color()
                else:
                    #Change viewport shading to Textured
                    bpy.context.space_data.viewport_shade = 'TEXTURED'
                    #Change to GLSL mode
                    try:
                        bpy.context.scene.game_settings.material_mode = 'GLSL'
                    except:
                        pass
                    
                #Enter texture paint mode    
                bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
                
                #Update brush texture scale option
                try:
                    ts = context.tool_settings.image_paint.brush.texture_slot
                    bpy.data.window_managers["WinMan"].texBrushScale = round((3 - ts.scale[0]) * 33.33333)
                    if bpy.data.window_managers["WinMan"].texBrushScale == 97:
                        bpy.data.window_managers["WinMan"].texBrushScale = 100
                    texBrushScaleUpdater(self, context)
                except:
                    pass
                
            #Particle Strands Mode    
            elif self.modeButton == 4:
                
                #Turn off multires if in fast mode
                if bpy.data.window_managers["WinMan"].fast_mode == True:
                     try:
                         bpy.context.object.modifiers["Multires"].show_viewport = False
                     except:
                         pass
                bpy.context.space_data.viewport_shade = 'TEXTURED' #Force tex view
                
                #Apply skin if exists
                ob = bpy.context.active_object
                skin = len([mod for mod in ob.modifiers if mod.type == 'SKIN'])
                if skin:
                    skinExtractor()
                    self.report({'INFO'}, 
                    ("Applied Skin modifier to object. Click the 'Eye' icon next" 
                    "to your character's bones in the outliner to view them."))
                #Message if didn't make armature
                report = 0
                for type in ob.modifiers:
                    try:
                        if "Bones" not in type.object.name:
                            report = 1
                            break
                    except:
                        pass
                if report == 1:    
                    self.report({'INFO'}, "Object already has armature. None created for it.") 
                    
                #If no strands make some    
                if context.active_object.particle_systems.active is None:
                    #Add generic strands
                    bpy.ops.object.add_strands()
                    if not skin:
                        self.report({'INFO'}, "Warning. Particle strands do not render while in sculpt mode.")
                bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
                    
        else:
            #If nothing selected or an object that can't use modes
            if self.modeButton != 1:
                if self.modeButton != 6:
                    self.report({'INFO'}, "This mode is only for mesh objects.")
        
        #Full screen Mode        
        if self.modeButton == 6:
            bpy.ops.screen.screen_full_area()
            
        return{'FINISHED'}   
			
#Fast Mode
def fastModeUpdater(self, context):
    settings = bpy.context.scene
    simplify = settings.render

    #For toggling fast mode on and off
    if self.fast_mode == True:
        #turn on fast nav for sculpting
        settings.tool_settings.sculpt.show_low_resolution = True
        
        if context.sculpt_object:
            bpy.context.space_data.viewport_shade = 'SOLID'
        
        #disable multires if in particle
        if context.particle_edit_object:
            try:
                bpy.context.object.modifiers["Multires"].show_viewport = False
            except:
                pass
        else:
            try:
                bpy.context.object.modifiers["Multires"].show_viewport = True
            except:
                pass
            
        simplify.use_simplify = True
        simplify.simplify_child_particles = 0.0
        #Restrict user settings to 2-4 sub levels    
        if simplify.simplify_subdivision < 2:
            simplify.simplify_subdivision = 2
        #Change Blender default to 2 levels
        elif simplify.simplify_subdivision > 4:
            simplify.simplify_subdivision = 2
        
        try:
            if bpy.data.window_managers["WinMan"].useSimplify == False:
                bpy.data.window_managers["WinMan"].useSimplify = True
        except:
            pass
        
    if self.fast_mode == False:
        bpy.context.scene.render.use_simplify = False
        settings.tool_settings.sculpt.show_low_resolution = False
        bpy.context.space_data.viewport_shade = 'TEXTURED'
        
        try:
            if bpy.data.window_managers["WinMan"].useSimplify == True:
                bpy.data.window_managers["WinMan"].useSimplify = False
        except:
            pass
        
        #Turn multires back on
        try:
            bpy.context.object.modifiers["Multires"].show_viewport = True
        except:
            pass
		
#TEXTURE PAINT==============================================
#main layer manager function================================
def layerManager(context,tn):
    ob = context.active_object
    me = ob.data
    mat = ob.active_material
    #tn is the active texture
    mat.active_texture_index = tn    
    ts = mat.texture_slots[tn]
    try:
        #make sure it's visible
        try:
            ts.use = True
        except:
            pass
            
        #Mesh use UVs?
        if not me.uv_textures:
            bpy.ops.mesh.uv_texture_add()
            
        # texture Slot uses UVs?
        if ts.texture_coords  == 'UV':
            if ts.uv_layer:
                uvtex = me.uv_textures[ts.uv_layer]       
            else:
                uvtex = me.uv_textures.active
                me.uv_textures.active= uvtex
        else:
            uvtex = me.uv_textures.active
            
        uvtex = uvtex.data.values()
        #get image from texture slot
        img = ts.texture.image  
        #get material index
        m_id = ob.active_material_index 

        if img:
            for f in me.polygons:  
                if f.material_index == m_id:
                    uvtex[f.index].image = img
        else:
            for f in me.polygons:  
                if f.material_index == m_id:
                    uvtex[f.index].image = None
        me.update()
    except:
        pass
		
#Select layers
class set_active_paint_layer(bpy.types.Operator):
    bl_idname = "object.set_active_paint_layer"
    bl_label = "Set Active Texture Layer"
    bl_description = "Active texture layer"
    tex_index = IntProperty(name = 'tex_index', default = 0)

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        tn = self.tex_index
        layerManager(context, tn)
        return {'FINISHED'}

#Eraser
class shiftEraser(bpy.types.Operator):
    bl_idname = "paint.shift_eraser"
    bl_label = "Shift Eraser"

    def execute(self, context):
        brushBlend = bpy.context.tool_settings.image_paint.brush.blend 
        bpy.context.window_manager.lastBrushBlend = brushBlend
        bpy.context.tool_settings.image_paint.brush.blend = 'ERASE_ALPHA'
        return {'FINISHED'}

class shiftEraserUp(bpy.types.Operator):
    bl_idname = "paint.shift_eraser_up"
    bl_label = "Shift Eraser Up"

    def execute(self, context):
        brushBlend = bpy.context.window_manager.lastBrushBlend
        if brushBlend == "ERASE_ALPHA":
            brushBlend = "MIX" 
        bpy.context.tool_settings.image_paint.brush.blend = brushBlend
        return {'FINISHED'}	


#Move textures up and down
class moveTex(bpy.types.Operator):
    bl_idname = "object.move_texture"
    bl_label = "Move Texture"
    bl_description = "Move texture layer up or down"
    tex_move_up = IntProperty(name="tex_move_up", default = 0)
    tex_move_down = IntProperty(name="tex_move_down", default = 0)

    def execute(self, context):
        ob = bpy.context.object
        try:
            mat = ob.active_material
            slots = mat.texture_slots
            ts = slots[mat.active_texture_index]
        except (TypeError, IndexError):
            pass
        else:
			#Bypass Blender's poll restrictions
            ctx = bpy.context.copy()
            ctx['texture_slot'] = ts
                
        if self.tex_move_up == 1:
            moveType = "UP"
            moveValue = -2
        if self.tex_move_down == 1:
            moveType = "DOWN"
            moveValue = 1
            
        #Gap solver
        x = 0
        while x == 0:
            tex = slots[mat.active_texture_index + moveValue]
            if tex is None or tex.texture_coords != 'UV':
                bpy.ops.texture.slot_move(ctx, type= moveType)
            else:
                bpy.ops.texture.slot_move(ctx, type= moveType)
                self.tex_move_down = 0
                x = 1
                
        return {'FINISHED'}


#Delete texture layer
class delTex(bpy.types.Operator):
    bl_idname = "object.delete_texture"
    bl_label = "Delete Texture"
    bl_description = "Delete texture layer"
    tex_kill = IntProperty(name="tex_kill", default = 0)

    def execute(self, context):
        ob = bpy.context.active_object
        mat = ob.active_material
        ts = mat.texture_slots[self.tex_kill]
        texName = mat.texture_slots[self.tex_kill].name
        
        #Special case if texture was transparent
        if ts.use_map_alpha == True:
            mat.use_transparency = False
            
        #Special case if texture was specular
        if ts.use_map_color_spec == True:
            mat.specular_color = (1, 1, 1)
            mat.specular_intensity = 0.5
        
        #Delete the texture and image
        if self.tex_kill > -1:
            if ts:
                if mat.texture_slots[self.tex_kill]:
                    #Delete image and texture
                    mat.texture_slots[self.tex_kill].texture.image.user_clear()
                    ts.texture = None
                    mat.texture_slots.clear(self.tex_kill)
                    

            #Set new active texture if deleted texture was active
            if self.tex_kill == mat.active_texture_index:
                x = 17
                while x > -1:
                    if mat.texture_slots[x]:
                        bpy.ops.object.set_active_paint_layer(tex_index=x)
                        break
                    x -= 1
                    
        return {'FINISHED'}


#Save all texture layer images
class zbSaveLayers(bpy.types.Operator):  
    bl_idname = "object.zb_save_layers"  
    bl_label = "Save My Layers"
    bl_description = "Click this before saving your file or your layers will be lost"
    
    def execute(self, context):
        # Run loop to go through all images and pack them as pngs
        ob = bpy.context.active_object
        mat = ob.active_material
        for ob in bpy.data.objects:
            if ob and ob.active_material:
                for ts in ob.active_material.texture_slots:
                    if ts and ts.texture.type == 'IMAGE':
                        if ts.texture_coords  == 'UV':
                            image = ts.texture.image
                            bpy.ops.image.pack({'edit_image': image}, as_png = True)
        self.report({'INFO'}, "All paint layers saved.")
             
        return {'FINISHED'}


#Texture layer options
def layerOptions(self, context):
    brushSettings = bpy.context.scene.tool_settings.image_paint
    mat = bpy.context.object.active_material
    
    #For Paint Through Button
    if self.paint_through == True:
        brushSettings.use_occlude = False
        brushSettings.use_normal_falloff = False
        brushSettings.use_backface_culling = False
    else:
        brushSettings.use_occlude = True
        brushSettings.use_normal_falloff = True
        brushSettings.use_backface_culling = True
    
    #For Disable Shading Button
    if self.disable_shading == True:
        mat.use_shadeless = True
    else:
        mat.use_shadeless = False
    
    #For disabling material's shadows
    if self.disable_shadows == True:
        bpy.context.object.active_material.use_shadows = False
    else:
        bpy.context.object.active_material.use_shadows = True
    
    #For toggling display only render
    if self.display_render == True:
        bpy.context.space_data.show_only_render = True
    else:
        bpy.context.space_data.show_only_render = False
		

#Reset UVs button
class resetUVs(bpy.types.Operator):
    bl_idname = "object.reset_uvs"
    bl_label = "Reset UV Map"
    bl_description = "Reset object's UV Map: Warning, if your object's mesh has changed your paint layers will be distorted"
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        #Use Smart UV project to create a UV Map
        bpy.ops.uv.smart_project(island_margin=0.03, angle_limit=40)
        #Average the scale of UVs.
        bpy.ops.uv.average_islands_scale()
        bpy.ops.object.mode_set(mode = 'TEXTURE_PAINT')
        
        return{'FINISHED'}


#Main texture layer adding function
def texLayerAdder(layerType, texCol, texOpas, alphaChoice,
    normalChoice):
    #Tidy Up Variables
    ob = bpy.context.active_object 
    mat = ob.active_material
    try:
        #Delete alpha mask or transparent layer if exists
        #There can be only one
        if layerType == "Transparent" or layerType == "Alpha_Mask":
            if mat:
                n = 0
                for tex in mat.texture_slots:
                    if tex:
                        if tex.use_map_alpha == True:
                            tex.texture.image = None
                            tex.texture = None
                            mat.texture_slots.clear(n)
                    n += 1
     
        #Test if object has material, create one if not
        if ob.active_material is None:
            
            #Create a new material and give it the name of the object
            mat = bpy.data.materials.new(ob.name)
            #Assign it some properties
            mat.diffuse_shader = 'LAMBERT'
            mat.darkness = 0.8
            
            #Set up strand material properties
            mat.strand.use_tangent_shading = False
            mat.strand.root_size = 2.5
            mat.strand.tip_size = 0.25
            mat.strand.width_fade = 0.5
            
            #Assign Material to the active object
            ob.active_material = mat
        
        #Get the user input values for creating custom image size.
        xAndY = round(bpy.context.window_manager.imgSize)

        #Create transparent image to be used as texture with RNA method
        img = bpy.data.images.new(ob.name + layerType, xAndY, xAndY, alpha= alphaChoice)
        #Set alpha and color to none
        img.pixels[:] = (texCol, texCol, texCol, texOpas) * xAndY * xAndY
        #Create A New texture and store it in cTex
        cTex = bpy.data.textures.new( name = ob.name + layerType, type = 'IMAGE')
        
        #Get active texture layer for the layer manager
        activeTex = -1
        for ts in mat.texture_slots:
            activeTex += 1
            if ts is None:
                break
            
        #Add a texture slot and assign it the texture just created
        mTex = mat.texture_slots.add()
        mTex.texture = cTex
        
        #Change mapping to UV now that we have a texture in place
        mTex.texture_coords = 'UV'
        
        if normalChoice == True:
            #Setup Normal mapping
            mTex.use_map_normal = True 
            mTex.bump_method = 'BUMP_MEDIUM_QUALITY'
            mTex.normal_factor = 0.0
                    
        #Assign the image we created to the texture we created
        cTex.image = img
        
        #Enter edit mode to select all faces
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        #Check for UV Map, if not one make one
        if not bpy.context.active_object.data.uv_textures:
            #Use Smart UV project to create a UV Map
            bpy.ops.uv.smart_project(island_margin=0.03, angle_limit=40)
            #Average the scale of UVs.
            bpy.ops.uv.average_islands_scale()
        
        #Use loop to link texture to UV Map of all faces
        for uv_face in ob.data.uv_textures.active.data:
            uv_face.image = img
        
        #Switch viewport shading to textured
        bpy.context.space_data.viewport_shade = 'TEXTURED'
        #Change shading to GLSL (if possible)
        try:
            bpy.context.scene.game_settings.material_mode = 'GLSL'
        except:
            pass
        
        #Exit edit mode and back to texture paint
        bpy.ops.object.mode_set(mode = 'TEXTURE_PAINT')
        
        #Bleed fixer: Setup bleed size to increase with new layer size
        bleed = 3
        if xAndY > 1040:
            dimension = xAndY / 1040
            bleed = round(dimension * 3)
        bpy.context.scene.tool_settings.image_paint.seam_bleed = bleed

        #Set active texture layer
        bpy.ops.object.set_active_paint_layer(tex_index=activeTex)
        #Move it to bottom of list
        slots = mat.texture_slots
        ts = slots[mat.active_texture_index]
        ctx = bpy.context.copy()
        ctx['texture_slot'] = ts
        x = 0
        while x < 17:
            bpy.ops.texture.slot_move(ctx, type='DOWN')
            x += 1
    except:
        pass
    return mTex  
    		
#Add Color
class zbPaintColor(bpy.types.Operator):  
    bl_idname = "object.zb_paint_color"  
    bl_label = "Add Color"
    bl_description = "This adds a regular texture layer you can paint on"

    def execute(self, context):
        layerType = "Color"
        texCol = 0.0
        texOpas = 1.0
        alphaChoice = False
        normalChoice = True
        texLayerAdder(layerType, texOpas, texCol, alphaChoice,
        normalChoice)
    
        return {'FINISHED'}
   
#Add Bump
class zbPaintBump(bpy.types.Operator):  
    bl_idname = "object.zb_paint_bump"  
    bl_label = "Add Bump"
    bl_description = 'This adds a texture layer with "Normal Mapping" for a pseudo 3D or "Bump" effect'

    
    def execute(self, context):
        
        layerType = "Bump"
        texCol = 1.0
        texOpas = 0.0
        alphaChoice = True
        normalChoice = True
        mTex = texLayerAdder(layerType, texOpas, texCol, alphaChoice,
        normalChoice)
        
        #Setup bump settings
        mTex.use_map_color_diffuse = False
        mTex.normal_factor = 0.6
        
        #Switch to draw brush
        try:
            brush = bpy.context.tool_settings.image_paint.brush
            brush.use_pressure_strength = False
            brush.blend = 'MIX' 
            bpy.data.brushes["Draw"].color = (1, 1, 1)
        except:
            pass
        
        return {'FINISHED'}

#Add Specular
class zbPaintSpecular(bpy.types.Operator):  
    bl_idname = "object.zb_paint_specular"  
    bl_label = "Add Specular"
    bl_description = 'This adds a specular or "Shininess" map which lets you paint where you want the shine'
    
    def execute(self, context):
        
        layerType = "Specular"
        texCol = 0.0
        texOpas = 0.0
        alphaChoice = True
        normalChoice = False
        mTex = texLayerAdder(layerType, texOpas, texCol, alphaChoice,
        normalChoice)

        ob = bpy.context.active_object
        mat = ob.active_material
        #Change material properties for specular
        mat.specular_color = (0, 0, 0)
        mat.specular_intensity = 1
        #Assign the texture properties for specular
        mTex.use_map_color_diffuse = False
        mTex.use_map_color_spec = True
        
        #Set up brush to work better with layer type  
        try:
            brush = bpy.context.tool_settings.image_paint.brush 
            brush.use_pressure_strength = True
        except:
            pass
       
        return {'FINISHED'}

#Add Transparent
class zbPaintTransparent(bpy.types.Operator):  
    bl_idname = "object.zb_paint_transparent"  
    bl_label = "Add Transparent"
    bl_description = 'This will turn your object invisible and let you paint on it'
    
    def execute(self, context):
        
        layerType = "Transparent"
        texCol = 0.0
        texOpas = 0.0
        alphaChoice = True
        normalChoice = False
        mTex = texLayerAdder(layerType, texOpas, texCol, alphaChoice,
        normalChoice)

        #Change material settings to work with transparency
        ob = bpy.context.active_object
        mat = ob.active_material
        mat.use_transparency = True
        mat.transparency_method = 'Z_TRANSPARENCY'
        mat.alpha = 0
        #Configure rest of transparent texture settings
        mTex.use_map_alpha = True
        #Turn off culling
        bpy.context.space_data.show_backface_culling = False
        
        #Switch to draw brush
        try:
            bpy.context.tool_settings.image_paint.brush = bpy.data.brushes['Draw']
            brush = bpy.context.tool_settings.image_paint.brush
            brush.blend = 'MIX' 
        except:
            pass

        return {'FINISHED'}

#Add Alpha Mask
class zbPaintAlphaMask(bpy.types.Operator):  
    bl_idname = "object.zb_alpha_mask"  
    bl_label = "Add Alpha Mask"
    bl_description = 'This lets you paint transparency onto your object wherever you choose'
    
    def execute(self, context):
        
        layerType = "Alpha_Mask"
        texCol = 0.0
        texOpas = 0.0
        alphaChoice = True
        normalChoice = False
        mTex = texLayerAdder(layerType, texOpas, texCol, alphaChoice,
        normalChoice)
        
        #Change material settings to work with transparency
        ob = bpy.context.active_object 
        mat = ob.active_material
        mat.use_transparency = True
        mat.transparency_method = 'Z_TRANSPARENCY'
        mat.alpha = 0

        #Set up the masking bit with the texture
        mTex.use_map_alpha = True
        mTex.diffuse_color_factor = 0
        mTex.alpha_factor = -1
        
        #Turn off culling
        bpy.context.space_data.show_backface_culling = False
        
        #Switch to draw brush
        try:
            bpy.context.tool_settings.image_paint.brush = bpy.data.brushes['Draw']
            brush = bpy.context.tool_settings.image_paint.brush
            brush.blend = 'MIX' 
        except:
            pass
        return {'FINISHED'}            
 

#SCULPT MODE================================================
#Make Sculptable
class addMultires(bpy.types.Operator):  
    bl_idname = "object.multires_add"  
    bl_label = "Make Sculptable"
    bl_description = "Adds multires modifier or converts modifiers into a multires"
    
    def execute(self, context):
        
        ob = bpy.context.active_object
        
        #Apply mirror if exists
        mirror = len([mod for mod in ob.modifiers if mod.type == 'MIRROR'])
        if mirror:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Mirror")
            #turn on x mirror symmetry if mirror
            bpy.context.scene.tool_settings.sculpt.use_symmetry_x = True
            
        #Apply skin if exists
        ob = bpy.context.active_object
        skin = len([mod for mod in ob.modifiers if mod.type == 'SKIN'])
        if skin:
            skinExtractor()
            self.report({'INFO'}, 
            ("Applied Skin modifier to object. Click the 'Eye' icon next" 
            "to your character's bones in the outliner to view them."))
        #Message if didn't make armature
        report = 0
        for type in ob.modifiers:
            try:
                if "Bones" not in type.object.name:
                    report = 1
                    break
            except:
                pass
        if report == 1:    
            self.report({'INFO'}, "Object already has armature. None created for it.") 
            
        #Apply solidify if exists
        solidify = len([mod for mod in ob.modifiers if mod.type == 'SOLIDIFY'])
        if solidify:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
            bpy.context.object.show_x_ray = False

                               
        #If has subsurf in Sculpt mode then delete subsurf
        subsurf = len([mod for mod in ob.modifiers if mod.type == 'SUBSURF'])
        if subsurf:
            newLevels = ob.modifiers["Subsurf"].levels
            bpy.ops.object.modifier_remove(modifier="Subsurf")
            bpy.ops.object.modifier_add(type='MULTIRES')
            #substitute multires levels with old subsurf levels
            while newLevels > 0:
                bpy.ops.object.multires_subdivide(modifier="Multires")
                bpy.context.object.modifiers["Multires"].levels += 1 
                newLevels -= 1
        else:
            #Add multires and subdivide
            bpy.ops.object.modifier_add(type='MULTIRES')
            newLevels = 3
            while newLevels > 0:
                bpy.ops.object.multires_subdivide(modifier="Multires")
                bpy.context.object.modifiers["Multires"].levels += 1 
                newLevels -= 1
                
        #Make sure multires modifier is at top of stack
        for x in range(20):
            bpy.ops.object.modifier_move_up(modifier="Multires")
        #unless there's an armature then make it number one
        try:
            for x in range(20):
                bpy.ops.object.modifier_move_up(modifier="Armature")
        except:
            pass 
            
        #Add smoothing
        bpy.ops.object.shade_smooth()
        #Send to object mode then back to sculpt to update
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='SCULPT')
        return {'FINISHED'}
    

#Button to subdivide multires modifier
class subMultires(bpy.types.Operator):  
    bl_idname = "object.multires_me_subdivide"  
    bl_label = "More Detail"
    bl_description = "Subdivide your object for more detailed sculpting (Hotkey is W)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        ob = bpy.context.active_object
        multires = len([mod for mod in ob.modifiers if mod.type == 'MULTIRES'])
        if multires:
            bpy.ops.object.multires_subdivide(modifier="Multires")
            bpy.context.object.modifiers["Multires"].levels += 1
            #Update the change by switching modes
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='SCULPT')
        #For use with hotkey
        if not multires:
            bpy.ops.object.multires_add()
        return {'FINISHED'}
    
    
#Button to generate base mesh
class generateBaseMesh(bpy.types.Operator):  
    bl_idname = "object.generate_base_mesh"  
    bl_label = "Make Base"
    bl_description = "Create low poly shape from sculpture (helps with Particle Mode but will erase current particle strands)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #Jump to object mode to apply multires
        bpy.ops.object.mode_set(mode='OBJECT')
        resLevels = bpy.context.object.modifiers["Multires"].levels
        if resLevels < 2:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Multires")
        else:
            bpy.context.object.modifiers["Multires"].levels = 2
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Multires")
            
        #Remove particles/Add multires/Return to sculpt
        bpy.ops.object.particle_system_remove()
        bpy.ops.object.modifier_add(type='MULTIRES')
        bpy.ops.object.mode_set(mode='SCULPT')
        return {'FINISHED'}
    
#PARTICLE EDIT MODE==========================================
#Add generic particle strands
class addStrands(bpy.types.Operator):  
    bl_idname = "object.add_strands"  
    bl_label = "Add Strands"
    bl_description = "Add particle strands to your object (I.E. Hair/Grass/Fur)"
    bl_options = {'REGISTER', 'UNDO'}
    
    #Create generic particle strands
    def execute(self, context):
        ob = bpy.context.active_object
        #Add to name for bug fix
        par = len(bpy.data.particles)
        parSys = ob.name + "Strands" + "%s" % par

        bpy.ops.object.particle_system_add()
        activeSys = context.active_object.particle_systems.active
        activeSys.settings.name = parSys
        
        #Set to particle strands
        bpy.data.particles[parSys].type = 'HAIR'
        bpy.data.particles[parSys].hair_length = 0.15
        bpy.data.particles[parSys].count = 0
        
        #Render settings
        bpy.data.particles[parSys].adaptive_angle = 3
        bpy.data.particles[parSys].use_strand_primitive = True
        bpy.data.particles[parSys].use_hair_bspline = True
        bpy.data.particles[parSys].render_step = 8
        bpy.data.particles[parSys].draw_step = 4

        #Handle particle children
        bpy.data.particles[parSys].child_type = 'SIMPLE'
        bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
        bpy.data.particles[parSys].child_nbr = 5
        bpy.data.particles[parSys].rendered_child_count = 45
        bpy.data.particles[parSys].child_length = 0.75
        bpy.data.particles[parSys].child_radius = 0.10
        bpy.data.particles[parSys].roughness_2 = 0.01
        
        #Change default tool settings
        bpy.context.scene.tool_settings.particle_edit.show_particles = True
        bpy.context.scene.tool_settings.particle_edit.draw_step = 3
        bpy.context.scene.tool_settings.particle_edit.tool = 'ADD'
        bpy.context.scene.tool_settings.particle_edit.brush.size = 30
        bpy.context.scene.tool_settings.particle_edit.brush.count = 5
        
        #Turn on hair dynamics
        genPar = bpy.context.object.particle_systems['ParticleSystem']
        genPar.use_hair_dynamics = True
        
        #Hair dynamics settings
        ob.particle_systems[0].cloth.settings.pin_stiffness = 1.75
        ob.particle_systems[0].cloth.settings.mass = 0.25
        ob.particle_systems[0].cloth.settings.bending_stiffness = 0.5
        ob.particle_systems[0].cloth.settings.internal_friction = 0.5
        ob.particle_systems[0].cloth.settings.collider_friction = 0.5
        ob.particle_systems[0].cloth.settings.spring_damping = 4.0
        ob.particle_systems[0].cloth.settings.air_damping = 1
        ob.particle_systems[0].cloth.settings.quality = 4

        return {'FINISHED'}



#CUSTOM BRUSH PANEL=========================================
#Must stay at the bottom or causes conflicts.
#Update brush texture scale option
def texBrushScaleUpdater(self, context):
    if context.image_paint_object:
        brushTex = bpy.context.tool_settings.image_paint.brush.texture_slot
    if context.sculpt_object:
        brushTex = bpy.context.tool_settings.sculpt.brush.texture_slot
        
    #Adjust for percentage display
    val = self.texBrushScale
    val = 3 - (val * 0.03)
    if val == 0:
       val = 0.10
    brushTex.scale[0] = val
    brushTex.scale[1] = val
    brushTex.scale[2] = val
    
class View3DPaintPanel(UnifiedPaintPanel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

class zeroBrushBP(Panel, View3DPaintPanel):
    bl_category = "Tools"
    bl_label = "Zero Brush"

    @classmethod
    def poll(cls, context):
        return cls.paint_settings(context)

    def draw(self, context):
        layout = self.layout

        toolsettings = context.tool_settings
        settings = self.paint_settings(context)
        brush = settings.brush
        
        #Draw "Load Brushes" and "Brush Map Mode" 
        wm = bpy.context.window_manager         
        if context.sculpt_object or context.image_paint_object:
                
            layout = self.layout
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            row.label('Load')
            row.operator('texture.load_single_brush')
            row.operator('texture.load_brushes')
            
            #Different settings for sculpt or texture paint
            try:
                if context.image_paint_object:
                    tex_slot = bpy.context.tool_settings.image_paint.brush.texture_slot
                if context.sculpt_object:
                    tex_slot = bpy.context.tool_settings.sculpt.brush.texture_slot
            
                #Brush map mode button
                if tex_slot.texture:
                    row = layout.row(align=True)
                    row.prop(tex_slot, "tex_paint_map_mode", text="")
                    row.prop(wm,"texBrushScale", text="")
            except:
                pass   

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
            if capabilities.has_strength:
                row = col.row(align=True)

                #if capabilities.has_space_attenuation:
                row.prop(brush, "use_space_attenuation", toggle=True, icon_only=True)

                self.prop_unified_strength(row, context, brush, "strength", text="Strength")
                self.prop_unified_strength(row, context, brush, "use_pressure_strength")

            # auto_smooth_factor and use_inverse_smooth_pressure
            if capabilities.has_auto_smooth:

                row = col.row(align=True)
                row.prop(brush, "use_locked_size", text= "", icon='UNLOCKED')
                row.prop(brush, "auto_smooth_factor", slider=True)
                row.prop(brush, "use_inverse_smooth_pressure", toggle=True, text="")

            # use_original_normal and sculpt_plane
            if capabilities.has_sculpt_plane:
                col.separator()
                row = col.row()
                row = col.row(align=True)
                row.prop(brush, "use_original_normal", toggle=True, icon_only=True)
                row.prop(brush, "sculpt_plane", text="")
                
            # crease_pinch_factor
            if capabilities.has_pinch_factor:
                row = col.row(align=True)
                row.prop(brush, "crease_pinch_factor", slider=True, text="Pinch")
            
             # normal_weight
            if capabilities.has_normal_weight:
                row = col.row(align=True)
                row.prop(brush, "normal_weight", slider=True)
                
            if brush.sculpt_tool == 'MASK':
                col.prop(brush, "mask_tool", text="")

            # plane_offset, use_offset_pressure, use_plane_trim, plane_trim
            if capabilities.has_plane_offset:
                row = col.row(align=True)
                row.prop(brush, "plane_offset", slider=True)
                row.prop(brush, "use_offset_pressure", text="")
                row = col.row()
                
                row.active = brush.use_plane_trim
                row.prop(brush, "plane_trim", slider=True, text="Distance")
                row = col.row()
                row.prop(brush, "use_plane_trim", text="Trim")
                
            # height
            if capabilities.has_height:
                row = col.row()
                row.prop(brush, "height", slider=True, text="Height")

            # use_persistent, set_persistent_base
            if capabilities.has_persistence:
                col.separator()

                ob = context.sculpt_object
                do_persistent = True

                # not supported yet for this case
                for md in ob.modifiers:
                    if md.type == 'MULTIRES':
                        do_persistent = False
                        break

                if do_persistent:
                    col.prop(brush, "use_persistent")
                    col.operator("sculpt.set_persistent_base")

        # Texture Paint Mode 
        elif context.image_paint_object and brush:
            col = layout.column()
            row = col.row(align=True)
            self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")
            self.prop_unified_size(row, context, brush, "use_pressure_size")

            row = col.row(align=True)
            self.prop_unified_strength(row, context, brush, "strength", text="Strength")
            self.prop_unified_strength(row, context, brush, "use_pressure_strength")
            
            if brush.image_tool == 'DRAW':
                row = layout.row()
                row = layout.row()
                box = row.box()
                
                box.template_color_picker(brush, "color", value_slider=True)
                sub = box.row(True)
                sub.prop(brush, "blend", text="")
                sub.prop(brush, "color", text="")

        # Weight Paint Mode #
        elif context.weight_paint_object and brush:

            col = layout.column()
            row = col.row(align=True)
            self.prop_unified_weight(row, context, brush, "weight", slider=True, text="Weight")
            row = col.row(align=True)
            self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")
            self.prop_unified_size(row, context, brush, "use_pressure_size")
            row = col.row(align=True)
            self.prop_unified_strength(row, context, brush, "strength", text="Strength")
            self.prop_unified_strength(row, context, brush, "use_pressure_strength")
            col.prop(brush, "vertex_tool", text="Blend")
            col = layout.column()
            col.prop(toolsettings, "use_auto_normalize", text="Auto Normalize")
            col.prop(toolsettings, "use_multipaint", text="Multi-Paint")

        # Vertex Paint Mode #
        elif context.vertex_paint_object and brush:
            col = layout.column()
            col.template_color_picker(brush, "color", value_slider=True)
            col.prop(brush, "color", text="")
            row = col.row(align=True)
            self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")
            self.prop_unified_size(row, context, brush, "use_pressure_size")
            row = col.row(align=True)
            self.prop_unified_strength(row, context, brush, "strength", text="Strength")
            self.prop_unified_strength(row, context, brush, "use_pressure_strength")
            col.prop(brush, "vertex_tool", text="Blend")
                    

                    
#Draw addon into properties shelf=========================================  
class zbPaint(bpy.types.Panel):
    bl_label = "Zero Brush"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
		#Tidy up variables
        ob = bpy.context.image_paint_object
        layout = self.layout
        wm = context.window_manager
        
        #Change mode buttons===============================================
        row = layout.row(align=True)
        
        row.alignment = 'EXPAND'
        row.operator("object.mode_buttons", text="", icon='OBJECT_DATA').modeButton  = 1
        split = row.split()
        
        row.operator("object.mode_buttons", text="", icon='SCULPTMODE_HLT').modeButton  = 2
        row.operator("object.mode_buttons", text="", icon='BRUSH_DATA').modeButton  = 3
        split = row.split()
        row.operator("object.mode_buttons", text="", icon='PARTICLEMODE').modeButton = 4
        #Fast Mode button
        row.prop(wm, "fast_mode", text="", icon='BLANK1')
        #Go Full Screen.
        row.operator("object.mode_buttons", text="", icon='FULLSCREEN_ENTER').modeButton = 6
        
        
        #Texture Paint===================================================
        try:
            mat = ob.active_material
            ts = mat.texture_slots[mat.active_texture_index]
            if ts:
                row = layout.row() 
                row.label('Blending Mode') 
                col = layout.column(align=True)
                col.prop(ts,'blend_type',text='', icon = 'BRUSH_DATA')
                                                
                if ts.use_map_diffuse:
                    col.prop(ts,'diffuse_factor', text = "Color Brightness", slider = True)
                if ts.use_map_color_diffuse:
                    col.prop(ts,'diffuse_color_factor', text = "Layer Opacity", slider = True)
                if ts.use_map_alpha:
                    col.prop(ts,'alpha_factor', text = "Transparency", slider = True)
                if ts.use_map_translucency:
                    col.prop(ts,'translucency_factor', text = "Translucency", slider = True)
                if ts.use_map_specular:
                    col.prop(ts,'specular_factor', text = "Specular", slider = True)
                if ts.use_map_color_spec:
                    col.prop(ts,'specular_color_factor', text = "Shininess", slider = True)
                if ts.use_map_hardness:
                    col.prop(ts,'hardness_factor', text = "Hardness", slider = True)
                    
                if ts.use_map_normal:
                    col.prop(ts,'normal_factor', text = "Bumpiness", slider = True)
                if ts.use_map_warp:
                    col.prop(ts,'warp_factor', text = "Warp", slider = True)
                if ts.use_map_displacement:
                    col.prop(ts,'displacement_factor', text = "Displacement",  slider = True)  
                    
                if ts.use_map_ambient:
                    col.prop(ts,'ambient_factor', text = "Ambient", slider = True)               
                if ts.use_map_emit:
                    col.prop(ts,'emit_factor', text = "Emit", slider = True)                  
                if ts.use_map_mirror:
                    col.prop(ts,'mirror_factor', text = "Mirror", slider = True)    
                if ts.use_map_raymir:
                    col.prop(ts,'raymir_factor', text = "Ray Mirror", slider = True) 
                row = layout.row()
                row = layout.row()
                                
                #Layer options buttons  
                row.alignment = 'EXPAND'
                row = layout.row(align=True)
                 
                #Texture Layer Options
                row.label('Texture Layers')
                row.prop(wm, "paint_through", text = "", icon ="TPAINT_HLT")
                row.prop(wm, "disable_shading", text = "", icon ="TEXTURE_SHADED")
                row.prop(wm, "disable_shadows", text = "", icon ="LAMP")
                row.operator("object.reset_uvs", text = "", icon ="FILE_REFRESH")         
                row = layout.row()
            
            #Draw Texture Layers
            i = -1    
            for t in mat.texture_slots:
                i+=1
                try:
                    if t.texture.type =='IMAGE':                
                        row = layout.row(align= True)                
                        if t.texture == mat.active_texture:
                            ai =  'BRUSH_DATA'
                        else:
                            ai = 'BLANK1'
                        row.operator('object.set_active_paint_layer', 
                            text = "", icon = ai).tex_index =i   
                        row.prop(t.texture,'name', text = "")
            
                        #Visibility
                        if t.use:
                            ic = 'RESTRICT_VIEW_OFF'
                        else:
                            ic = 'RESTRICT_VIEW_ON'
                            
                        if t.texture == mat.active_texture:
                            #move texture buttons
                            row.operator("object.move_texture", text = "",icon = "TRIA_UP").tex_move_up = 1
                            row.operator("object.move_texture", text = "",icon = "TRIA_DOWN").tex_move_down = 1
                        
                        #Delete texture button
                        row.operator("object.delete_texture", text = "",icon = "X").tex_kill = i
                        #Hide texture button
                        row.prop(t,'use', text = "",icon = ic)
                except:
                    pass
        except:
            pass
        row = layout.row()               
        if bpy.context.mode.startswith('PAINT') is True:
            
            #Draw the add, create, and save layers area
            col = layout.column(align = True)
            box = col.box()
            sub = box.column(True)
        
            sub.operator("object.zb_paint_color", icon='TEXTURE')
            sub.operator("object.zb_paint_bump", icon='TEXTURE')
            sub.operator("object.zb_paint_specular", icon='TEXTURE')
            
            sub = box.column()
            sub = box.column(True)
            sub.operator("object.zb_paint_transparent", icon='TEXTURE')
            sub.operator("object.zb_alpha_mask", icon='TEXTURE')
            
            sub = box.column()
            sub = box.column(True)
            sub.prop(context.window_manager, "imgSize")
            sub.operator("object.zb_save_layers", icon='FILE_TICK')
            sub = box.column(True)
            row = layout.row() 
            
            
		#Sculpt Mode===================================================
        if bpy.context.mode.startswith('SCULPT') is True:
            row = layout.row()
            ob = bpy.context.active_object
            multires = len([mod for mod in ob.modifiers if mod.type == 'MULTIRES'])   
            #Add multires Button.
            col = layout.column(align=True)
            if not multires:
                col.operator("object.multires_add")
                row = layout.row()
            if multires:
                col.operator("object.multires_me_subdivide")
                col.operator("object.generate_base_mesh")
                row = layout.row()
                
            #Brush symmetry 
            row = layout.row(align=True)
            row.label(text="Brush")
            sculpt = context.tool_settings.sculpt
            row.prop(sculpt, "use_symmetry_x", text="X", toggle=True)
            row.prop(sculpt, "use_symmetry_y", text="Y", toggle=True)
            row.prop(sculpt, "use_symmetry_z", text="Z", toggle=True)
            row = layout.row(align=True)
            
        #Particle Strands Mode===================================================
        if bpy.context.mode.startswith('PARTICLE') is True:
            if context.active_object.particle_systems.active:
                row = layout.row()
                row = layout.row()
                row.operator("object.particle_system_remove", text="Delete Strands")


            
#Store properties for buttons and user input
class myBlendProperties(bpy.types.PropertyGroup):
    
    #Property to store blend mode for eraser
    bpy.types.WindowManager.lastBrushBlend = bpy.props.StringProperty(
    name = "Last Brush Blend Mode",
    default = "MIX")

    #Set property for image size. Use float so can use step option
    bpy.types.WindowManager.imgSize = bpy.props.FloatProperty(
    name="New Layer Size",
    description = "The size of the next layer you add (width and height)",
    default = 1024, 
    min = 128,
    precision = 0,
    step = 12800)
    
    #Set property for texture brush scale.
    bpy.types.WindowManager.texBrushScale = bpy.props.IntProperty(
    name="Texture Scale",
    description = "Scales the texture this brush is using",
    default = 100, 
    subtype="PERCENTAGE", min=0, max=100,
    update = texBrushScaleUpdater)
            
    #Properties for texture layer options buttons
    bpy.types.WindowManager.paint_through = bpy.props.BoolProperty(
    name = "Paint Through", description = "Paint or erase all the way through your object",
    update = layerOptions) 
               
    bpy.types.WindowManager.disable_shading = bpy.props.BoolProperty(
    name = "Disable Shading", description = 'Disable shading', update = layerOptions)
    
    bpy.types.WindowManager.disable_shadows = bpy.props.BoolProperty(
    name = "Disable Shadows", description = "Turn off this object's shadows", update = layerOptions) 

    #Fast Mode button
    bpy.types.WindowManager.fast_mode = bpy.props.BoolProperty(
    name = "Fast Mode Toggle", description = "Fast Mode (use if Blender's going to slow)", 
    update = fastModeUpdater)
    
        
#REGISTRATION AND UNREGISTRATION FOR ADDON==================
#Create Keymaps list
addon_keymaps = []
     
def register():
    #Register all classes
    bpy.utils.register_module(__name__)
    
    wm = bpy.context.window_manager
    #Hotkeys: Texture Paint Mode
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    kmi = km.keymap_items.new("paint.shift_eraser", 'LEFT_SHIFT','PRESS')
    kmi = km.keymap_items.new("paint.shift_eraser_up", 'LEFT_SHIFT','RELEASE', shift=True)
    kmi = km.keymap_items.new("paint.image_paint", 'LEFTMOUSE','PRESS', shift=True)
    kmi = km.keymap_items.new("object.select_brush", 'SPACE','PRESS')
    kmi = km.keymap_items.new("view3d.cursor3d", 'LEFTMOUSE','DOUBLE_CLICK', shift = True)
    #Hotkeys: Sculpt Mode
    km = wm.keyconfigs.addon.keymaps.new(name='Sculpt', space_type='EMPTY')
    kmi = km.keymap_items.new("object.select_brush", 'SPACE','PRESS')
    kmi = km.keymap_items.new("object.multires_me_subdivide", 'W','PRESS')
    kmi = km.keymap_items.new("view3d.cursor3d", 'LEFTMOUSE','DOUBLE_CLICK', shift = True)
    #Hotkeys: Particle Edit Mode
    km = wm.keyconfigs.addon.keymaps.new(name='Particle', space_type='EMPTY')
    kmi = km.keymap_items.new("object.select_brush", 'SPACE','PRESS')
    #Append keymap
    addon_keymaps.append(km)
            
def unregister():
    #Unregister all classes
    bpy.utils.unregister_module(__name__)
    
    #Unregister keymaps (takes care of all)
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]
    
if __name__ == "__main__":
    register()


















