# -*- coding: utf-8 -*-

'''
***** BEGIN BSD LICENSE BLOCK *****

--------------------------------------------------------------------------
3D-HGIS // Archeological Data Manager v1.0 Public release
--------------------------------------------------------------------------

Copyright (c) 2018 Uriel Deveaud All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
4. Neither the name of Uriel Deveaud nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY URIEL DEVEAUD ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL URIEL DEVEAUD BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.

***** END BSD LICENCE BLOCK *****
'''


bl_info = {
    "name": "3D-HGIS // Archeological Data Manager 1.0.0",
    "author": "Uriel Deveaud - Project 3D-HGIS-ADB3",
    "version": (1, 0, 0),
    "blender": (2, 7, 9),
    "location": "Properties space > Scene tab > 3D-HGIS // Archeological Data Manager 1.0 Beta",
    "description": "Archeological contents Importer, CSV database + BLEND library, TIME, GRID and REPORT Tools",
    "warning": "",
    "wiki_url": "https://github.com/KoreTeknology/Blender-Addon-Archeological-data-Manager",
    "tracker_url": "https://github.com/KoreTeknology/Blender-Addon-Archeological-data-Manager",
    "category": "Learnbgame"
}


############################ 
# IMPORT MODULES  
############################ 

import bpy, csv, struct
import datetime
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
                       
from bpy.types import (Panel,
                       Operator,
                       Menu,
                       UIList,
                       AddonPreferences,
                       PropertyGroup,
                       UserPreferences,
                       )


############################ 
# FUNCTIONS DEF
############################ 

#fake report banner
#properties to pass and store the message
bpy.types.Scene.message = bpy.props.StringProperty()
bpy.types.Scene.icon    = bpy.props.StringProperty()

def report(self, context):
    self.layout.label(text=context.scene.message, icon=context.scene.icon, icon_value=0)

# messages
def oops(self, context):
    self.layout.label("You have done something you shouldn't do!")

def clics(self, context):
    self.layout.label("You have clicked")


############################ 
# OPERATORS
############################ 

#timer modal operator
class LoggingOperator(bpy.types.Operator):
    """Log a message to the Info View"""
    bl_idname = "info.log"
    bl_label = "Direct Log message -> Info View"

    _timer = None
    lookup = ['DEBUG', 'INFO', 'WARNING', 'ERROR'] 
    level = bpy.props.IntProperty(name="Level", default=1)
    message = bpy.props.StringProperty(name="Message", default="Reporting : Base message")

    def modal(self, context, event):
        if event.type == 'TIMER':
            self.cancel(context)
            return {'FINISHED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(1, context.window)
        wm.modal_handler_add(self)

        context.scene.icon = self.lookup[self.level]
        context.scene.message = self.message
        bpy.types.INFO_HT_header.append(report)  
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1) #force UI redraw
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        bpy.types.INFO_HT_header.remove(report)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1) #force UI redraw



# open window
class OpenInfoOperator(bpy.types.Operator):
    """Open info window"""
    bl_idname = "info.openinfo"
    bl_label = "Indirect Log > Calls Operator"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT') 
        # Change area type 
        area = bpy.context.window_manager.windows[-1].screen.areas[0] 
        area.type = 'INFO' 

        return {'FINISHED'}

# indirect log
class ForwardLoggingOperator(bpy.types.Operator):
    """Call an operator that logs stuff"""
    bl_idname = "info.log_1"
    bl_label = "Indirect Log > Calls Operator"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        print("Forwarding Operator called")
        bpy.ops.info.log(level=1, message="Forward : Redirected message")
        self.report({'INFO'}, "Redirected message")
        print(context.active_operator )
        
        # create popup info
        bpy.context.window_manager.popup_menu(oops, title="Error step 1", icon='INFO')

        return {'FINISHED'}

# change theme color based on types
class ThemeChangingOperator(bpy.types.Operator):
    """Call an operator that change color theme"""
    bl_idname = "info.colorchange"
    bl_label = "Info panel > Change color"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        # set for color change
        current_theme = bpy.context.user_preferences.themes.items()[0][0]  
        info_newtheme = bpy.context.user_preferences.themes[current_theme].info
        # set conversion method
        def hex_to_rgb(rgb_str):  
            int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str))  
            return tuple([val/255 for val in int_tuple])  
        # define new color charts for Info window
        info_newtheme.info_debug = hex_to_rgb('9D8C12') 
        info_newtheme.info_debug_text = hex_to_rgb('88D48D') 
        info_newtheme.info_error = hex_to_rgb('9458AD') 
        info_newtheme.info_error_text = hex_to_rgb('000000') 
        info_newtheme.info_info = hex_to_rgb('78E564')
        info_newtheme.info_info_text = hex_to_rgb('000000')
        info_newtheme.info_warning = hex_to_rgb('E564DB') 
        info_newtheme.info_warning_text = hex_to_rgb('FFAF50') 
        info_newtheme.info_selected = hex_to_rgb('27A5CD')
        info_newtheme.info_selected_text = hex_to_rgb('000000')
        # change background color and normal text debug
        info_newtheme.space.back = hex_to_rgb('333333') 
        info_newtheme.space.text = hex_to_rgb('999999') 
        # create popup info
        bpy.context.window_manager.popup_menu(clics, title="Info window Theme changed", icon='INFO')

        return {'FINISHED'}

# Theme colors reset
class ThemeResetOperator(bpy.types.Operator):
    """Call an operator that reset color theme"""
    bl_idname = "info.colorreset"
    bl_label = "Info panel > Change color"
    bl_options = {'INTERNAL'}
    

    def execute(self, context):
        # set for color change
        current_theme = bpy.context.user_preferences.themes.items()[0][0]  
        info_newtheme = bpy.context.user_preferences.themes[current_theme].info
        # set conversion method
        def hex_to_rgb(rgb_str):  
            int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str))  
            return tuple([val/255 for val in int_tuple])  
        # define new color charts for Info window
        info_newtheme.info_debug = hex_to_rgb('C4C4C4') 
        info_newtheme.info_debug_text = hex_to_rgb('000000') 
        info_newtheme.info_error = hex_to_rgb('DC0000') 
        info_newtheme.info_error_text = hex_to_rgb('000000') 
        info_newtheme.info_info = hex_to_rgb('00AA00')
        info_newtheme.info_info_text = hex_to_rgb('000000')
        info_newtheme.info_warning = hex_to_rgb('DC8060') 
        info_newtheme.info_warning_text = hex_to_rgb('000000') 
        info_newtheme.info_selected = hex_to_rgb('27A5CD')
        info_newtheme.info_selected_text = hex_to_rgb('000000')
        # change background color and normal text debug
        info_newtheme.space.back = hex_to_rgb('727272') 
        info_newtheme.space.text = hex_to_rgb('000000') 

        return {'FINISHED'}



# OPERATOR to print paths and scene name
class SCENE_OT_PrintFilePath(bpy.types.Operator):
    bl_idname = "scene.file_path_print"
    bl_label = "Print Paths Operator"
    bl_description = "Print in console"
        
    def execute(self, context):
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        scene = bpy.context.scene
        self.report({'INFO'}, "-"*0)
        self.report({'INFO'}, "### Start SYS.CHECK Filepaths ...")
        self.report({'INFO'}, "Result:")
        #self.report({'INFO'}, "> CSV file Path: "+scene.my_tool.path)
        #self.report({'INFO'}, "> BLEND file Path: "+scene.my_tool.path2)
        if scene.my_tool.path == "":
            self.report({'ERROR'}, "ERROR at "+str(t)+" --- CSV file Path is empty !")
        else:
            self.report({'INFO'}, "INFO    at "+str(t)+" --- CSV file Path is "+scene.my_tool.path)
        
        if scene.my_tool.path2 == "":
            self.report({'ERROR'}, "ERROR at "+str(t)+" --- BLEND file Path is empty !")
        else:
            self.report({'INFO'}, "INFO    at "+str(t)+" --- BLEND file Path is "+scene.my_tool.path2)
        
        self.report({'INFO'}, "### SYS CHECK PATH done !")
        self.report({'INFO'}, "."*0)

        return {'FINISHED'}

# OPERATOR to print scene name and group name
class SCENE_OT_PrintSceneInfos(bpy.types.Operator):
    bl_idname = "scene.scene_infos_print"
    bl_label = "Print Scene infos Operator"
    bl_description = "Print in console"
    
    def execute(self, context):
        scene = bpy.context.scene
        group = bpy.data.groups.new("Database Group")
        group

        self.report({'INFO'}, "-"*0)
        self.report({'INFO'}, "### SYS.CHECK Scene Infos ...")
        self.report({'INFO'}, "> Scene name: "+scene.name)
        self.report({'INFO'}, "> Group name: "+bpy.data.groups[0].name)
        self.report({'WARNING'}, "> Objects in scene: ")

        for obj in scene.objects :
            self.report({'WARNING'}, "   - %s"%obj.name)

        self.report({'INFO'}, "### SYS CHECK SCENE done")  
        self.report({'INFO'}, "-"*0) 

        return {'FINISHED'}
    


############################ 
# MAIN OPERATORS 
############################ 

# OPERATOR to open csv file and import data
class SCENE_OT_ImportDataFromCSV(bpy.types.Operator):
    bl_idname = "scene.csv_data_import"
    bl_label = "Import csv data from files"
    bl_description = "Import CSV database"
       
    def execute(self, context):
        scene = bpy.context.scene
        # Create groups if no exist
        group = bpy.data.groups.new("Database Group")
        group
        group_empties = bpy.data.groups.new("Empty Group")
        group_empties
        group_texts = bpy.data.groups.new("Text Group")
        group_texts
        
        # import data from db file
        with open( scene.my_tool.path ) as csvfile:
            rdr = csv.reader( csvfile )
            for i, row in enumerate( rdr ):
                if i == 0: continue
                name, lon, lat, elev, type, shape, fs, fe = row[1:9] # columns data
                
                # check if object exist with same name
                if bpy.data.objects.get(name) is not None:
                    self.report({'ERROR'}, "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    self.report({'ERROR'}, "The object "+ name+" exist !!! Stop Loading...")
                    continue
                else:
                    self.report({'INFO'}, "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    self.report({'INFO'}, "### The object "+ name+" don't exist, Start Loading...")
                    #self.report({'INFO'}, "Initialize import for "+ name)

                # generate Empty object at x = lon and y = lat and z = elev 
                bpy.ops.object.empty_add( type='ARROWS', location = ( float(lon), float(lat), float(elev) ) )
                
                # select and customize new created empty object
                new_target = bpy.context.selected_objects[0]
                new_target.name = "" + name + ""
                bpy.ops.transform.resize(value=(0.3, 0.3, 0.3), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
                #new_target.show_bounds = True
                #new_target.show_axis = True
                self.report({'INFO'}, "# New Empty added on DB location for: "+new_target.name)
                
                # assign to group
                empty_grp = bpy.data.groups.get('Empty Group')
                empty_grp.objects.link(new_target)    
                empty_grp.name = "Empty Group"
                self.report({'INFO'}, "# Empty "+new_target.name+" have been added to "+empty_grp.name)
                
                empty_object = new_target
                Row = row
                
                # add other data to empty
                OBlocation = new_target.location
                bpy.ops.object.text_add(location=OBlocation)
                
                bpy.ops.transform.translate(value=(0, 0, 0.7), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
                bpy.ops.transform.resize(value=(0.05, 0.05, 0.05), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
                bpy.context.active_object.rotation_mode = 'XYZ'
                bpy.context.active_object.rotation_euler = (1.5708,0,1.5708)
                bpy.context.active_object.rotation_euler[1] = 0
                bpy.context.active_object.draw_type = 'WIRE'

                bpy.ops.object.editmode_toggle()
                bpy.ops.font.delete()
                bpy.ops.font.text_insert(text="Object: "+Row[1])
                bpy.ops.transform.resize(value=(0.451466, 0.451466, 0.451466), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
                bpy.ops.font.line_break()
                bpy.ops.font.text_insert(text="- Type: " + Row[5])
                bpy.ops.font.line_break()
                bpy.ops.font.text_insert(text="- Shape: " + Row[6])
                bpy.ops.font.line_break()
                bpy.ops.font.text_insert(text="- from: " + Row[7]+" to "+ Row[8]+" AD")
                bpy.ops.object.editmode_toggle()
                
                txt_target = bpy.context.selected_objects[0]
                txt_target.show_x_ray = True
                txt_target.show_bounds = True

                text_grp = bpy.data.groups.get('Text Group')
                text_grp.objects.link(txt_target) 
                
                # new variable : name of new created empty object
                tn = new_target.name
                text_grp.name = "Text Group"
                
                self.report({'INFO'}, "# New Text Object added on DB location for "+tn)
                self.report({'INFO'}, "# Text Object "+new_target.name+" have been added to "+text_grp.name)
                
                # load objects from library selected with db name column               
                with bpy.data.libraries.load(scene.my_tool.path2, link=False) as (data_from, data_to):
                    data_to.objects = [name for name in data_from.objects if name.startswith(tn)]
                    
                # load imported objects to the scene at empties location      
                for obj in data_to.objects:
                    if obj is not None:
                        scene.objects.link(obj)
                    obj.location = new_target.location 
                    #obj.show_name = True  
                    obj.show_axis = True  
                    obj.show_texture_space = True
                    obj.name =  "" + name + "-OBJ"
                    
                    # print imported object name
                    on = obj.name
        
                    self.report({'INFO'}, "# Object imported from library: "+ on)
                    
                    # insert keyframes at data position frame/year
                    frm_start = int(fs)
                    frm_end = int(fe)
                    frm_pre = int(fs)-1
                    scn = bpy.context.scene
                    
                    scn.frame_set(frm_pre)
                    obj.hide = True
                    obj.keyframe_insert(data_path="hide")
                    empty_object.keyframe_insert(data_path="hide")

                    scn.frame_set(frm_start)
                    obj.hide = False
                    obj.keyframe_insert(data_path="hide")
                    empty_object.keyframe_insert(data_path="hide")

                    scn.timeline_markers.new(obj.name, frame=frm_start)

                    scn.frame_set(frm_end)
                    obj.hide = True
                    obj.keyframe_insert(data_path="hide")
                    empty_object.keyframe_insert(data_path="hide")
                    
                    self.report({'INFO'}, "# Object is added on frame "+ str(frm_start)+" and removed on frame "+ str(frm_end))
                    
                    scn.frame_set(frm_start)
                    
                    # add to group
                    # !!! works ONLY if group is created, a group is created within this loop
                    grp = bpy.data.groups.get('Database Group')
                    grp.objects.link(obj)                 
                    
                    # deselect objects
                    #bpy.ops.object.select_all(action='TOGGLE')                   
                    bpy.ops.object.select_all(action='DESELECT') #deselect all object
                    obj.select = True
                    txt_target.select = True
                    new_target.select = True
                    bpy.context.scene.objects.active = new_target    #the active object will be the parent of all selected object
                    bpy.ops.object.parent_set()

                    bpy.ops.object.select_all(action='DESELECT')
                    
                    self.report({'INFO'}, "# Object is assign to group: "+grp.name)
                    self.report({'INFO'}, "### "+name+" loaded with success !")
                    
        return {'FINISHED'}


        


############################ 
# UI SETTING PROPERTIES
############################  
 
# CLASS group of settings
class MySettings(PropertyGroup):

    path = StringProperty(
        name="path",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
        )
        
    path2 = StringProperty(
        name="path2",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
        )
        
   
############################ 
# UI DRAW PANEL
############################ 
 
class SCENE_PT_FilePathPrinter(bpy.types.Panel):

    bl_label = "3D-HGIS // Archeological Data Manager"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"    
    
    def draw(self, context):
        
        scene = bpy.context.scene
        lay = self.layout
        #col1 = lay.column()
        
        ob_cols = []
        db_cols = []
        objects = bpy.data.objects
        
        box = lay.box()
        col = box.column(align=True)
        col.label("Database Path (.csv):",icon='RNA_ADD')
        col.prop(scene.my_tool, "path", text="")
        col.label("Objects Library Path (.blend):",icon='LINK_BLEND')
        col.prop(scene.my_tool, "path2", text="")
        col.label(text="Help: If you notice an error, check the report!", icon='QUESTION')
        col.separator()
        row2 = col.row(align=True)
        row2.scale_y = 1.5
        row2.operator("scene.csv_data_import", icon="LOAD_FACTORY", text="Import Library")
        

        # Timeline Section
        lay = self.layout
        box = lay.box()
        col1 = box.column(align=True)
        row2 = col1.row(align=True)
        
        if scene.show_options_timeline:
            row2.prop(scene, "show_options_timeline", icon="DOWNARROW_HLT", text="", emboss=False)
        else:
            row2.prop(scene, "show_options_timeline", icon="RIGHTARROW", text="", emboss=False)

        row2.label('Timeline', icon="SEQ_SEQUENCER")
        
        if scene.show_options_timeline:
            row2 = col1.row(align=True)
            #row2.label('Time range', icon="ACTION_TWEAK")
            
            row2.separator()
            
            row2 = col1.row(align=True)
            #split = col1.split(percentage=0.5)
            row2.prop(scene, 'frame_start', text='Start Year')
            row2.prop(scene, 'use_preview_range', text='')
            row2 = col1.row(align=True)
            row2.prop(scene, 'frame_end', text='End Year')
            row2.prop(scene, 'lock_frame_selection_to_range', text='')
            col1 = box.column(align=True)
            #row2 = col1.row(align=True)
            
            row2 = col1.row(align=True)
            #split = col1.split(percentage=0.5)
            row2.prop(scene, 'frame_current', text='Current Year')
            
            userpref = context.user_preferences
            edit = userpref.edit
            
            col1.separator()
            row2 = col1.row(align=True)
            row2.prop(edit, "use_negative_frames", text="Use Negative values")
 
        # Report Section
        lay = self.layout
        box = lay.box()
        col1 = box.column(align=True)
        row2 = col1.row(align=True)
        
        if scene.show_options_report:
            row2.prop(scene, "show_options_report", icon="DOWNARROW_HLT", text="", emboss=False)
        else:
            row2.prop(scene, "show_options_report", icon="RIGHTARROW", text="", emboss=False)

        row2.label('Reports Tools', icon="SHORTDISPLAY")
        
        if scene.show_options_report:
            col3 = box.column(align=True)
            row2 = col3.row(align=True)
            row2.operator("info.openinfo", text="Open", icon="SAVE_COPY")
            row2.operator("info.colorchange", text="Dark Theme")
            row2.operator("info.colorreset", text="Reset Theme")
            row2 = col3.row(align=True)
            row2.prop(bpy.context.user_preferences.view, "ui_scale",toggle=True, text="UI Scale")
            # add control from csv importer script !
            col3 = box.column(align=True)
            #row2 = col3.row(align=True)
            col3.label(text="Checking Data Options", icon='SAVE_PREFS')
            row2 = col3.row(align=True)
            row2.operator("scene.file_path_print", text="Files Path Log")
            #row2 = col3.row(align=True)
            row2.operator("scene.scene_infos_print", text="Data Scene Log")
            row2 = col3.row(align=True)
            #row2.operator("info.log")
            #row2 = col3.row(align=True)
            #row2.operator("info.log_1")
            # Show direct message
            # show info in panel
            #lay.template_reports_banner()
        
        # Release Section
        lay = self.layout
        box = lay.box()
        col1 = box.column(align=True)
        row2 = col1.row(align=True)
        
        if scene.show_options_infos:
            row2.prop(scene, "show_options_infos", icon="DOWNARROW_HLT", text="", emboss=False)
        else:
            row2.prop(scene, "show_options_infos", icon="RIGHTARROW", text="", emboss=False)

        row2.label('Release Infos', icon="INFO")
        
        if scene.show_options_infos:
            col1.label(text="Release 1.0.0 'AngelFire'", icon='RADIO')
            col1.label(text="Archeology Blender Addon", icon='OOPS')
            col1.label(text="Next Release: 11/01/2019", icon='OUTLINER_OB_FORCE_FIELD')
            col1.label(text="Author: Uriel Deveaud - 2018", icon='POSE_HLT')
            
 
            
############################ 
# REGISTER 
############################ 
                      
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)
    bpy.types.Scene.show_options_timeline = bpy.props.BoolProperty(name='Show Timeline panel', default=False)
    bpy.types.Scene.show_options_infos = bpy.props.BoolProperty(name='Show Infos panel', default=False)
    bpy.types.Scene.show_options_report = bpy.props.BoolProperty(name='Show Report panel', default=False)
       
def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.show_options_timeline
    del bpy.types.Scene.show_options_infos
    del bpy.types.Scene.show_options_grid
    del bpy.types.Scene.show_options_report

if __name__ == '__main__':
    register()
    
   