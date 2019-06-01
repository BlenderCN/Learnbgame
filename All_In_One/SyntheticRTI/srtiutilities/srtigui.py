##############
#####GUI######
##############

import bpy
import numpy
import os
from .srtifunc import *
from .srtiproperties import file_lines as file_lines

##list of properties
class Values_UL_items(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#        box = layout.box()
#        row = box.row(align = True)
#        row.alignment = 'LEFT'
        col1 = layout.column()
        col1.prop(item, "name", text="", emboss=False, translate=False, icon='BUTS')
        row2 = col1.row(align = True)
        row2.prop(item,"min")
        row2.prop(item,"max")
        row2.prop(item,"steps")
        col1.separator()

    def invoke(self, context, event):
        pass   

###Create
class SyntheticRTIPanelCreate(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Create"
    bl_idname = "srti.panelCreate"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene

        layout = self.layout
        
        #light
        layout.prop(curr_scene.srti_props, "light_file_path", text = 'Light file', icon = "LAMP_SPOT")
        row = layout.row(align = True)
        row.operator("srti.create_lamps", icon ="OUTLINER_DATA_LAMP")
        row.operator("srti.delete_lamps", icon = "X")
        
        #camera
        row = layout.row(align = True)
        row.operator("srti.create_cameras",icon = "OUTLINER_DATA_CAMERA")
        row.operator("srti.delete_cameras", icon = "X")
        
        #object
        layout.prop(curr_scene.srti_props, "main_object", text = "Object")
        
        #Parameters
        layout.label("Parameters:", icon='ACTION')
        row = layout.row()
        row.template_list("Values_UL_items", "", curr_scene.srti_props, "list_values", curr_scene.srti_props, "selected_value_index", rows=2)
        col = row.column(align=True)
        col.operator("srti.values_uilist", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("srti.values_uilist", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("srti.values_uilist", icon='TRIA_UP', text="").action = 'UP'
        col.operator("srti.values_uilist", icon='TRIA_DOWN', text="").action = 'DOWN'

###Render
class SyntheticRTIPanelRender(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Render"
    bl_idname = "srti.panelRender"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene
        layout = self.layout
        
        #output folder
        box = layout.box()
        if curr_scene.srti_props.overwrite_folder: #if we want to overwrite
            box.label("Output folder = "+curr_scene.srti_props.output_folder, icon = "FILE_FOLDER")          
            box.prop(curr_scene.srti_props, "overwrite_folder")
            box.prop(curr_scene.srti_props, "output_folder", text = 'Output folder')
        else: #standard output taken from the saved blender file
            if context.blend_data.is_saved: # if the file is saved
                box.label("Output folder = "+os.path.dirname(context.blend_data.filepath), icon = "FILE_FOLDER")
            else:
                box.label("Output folder = *Must save the file*", icon = "ERROR")
                
            box.prop(curr_scene.srti_props, "overwrite_folder")

            
        #output name    
        box = layout.box()
        if curr_scene.srti_props.overwrite_name: #if we want to overwrite
            box.label("Output name = "+curr_scene.srti_props.save_name, icon = "SORTALPHA")
            box.prop(curr_scene.srti_props, "overwrite_name")
            box.prop(curr_scene.srti_props, "save_name", text = 'Output name')
        else: #standard name taken from the saved blender file
            if context.blend_data.is_saved: # if the file is saved
                box.label("Output name = "+bpy.path.display_name(context.blend_data.filepath), icon = "SORTALPHA")
            else:
                box.label("Output name = *Must save the file*", icon = "ERROR")
                
            box.prop(curr_scene.srti_props, "overwrite_name")
        
        col = layout.column(align = True)
        col.operator("srti.animate_all", icon ="KEYINGSET")
        col.operator("srti.render_images", icon = "RENDER_ANIMATION")
        col.operator("srti.create_file", icon = "FILE_TEXT")

###Tools
class SyntheticRTIPanelTools(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Tools"
    bl_idname = "srti.panelTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene
        layout = self.layout
        layout.operator("srti.export_lamp", icon = "FILE_TEXT")
        col = layout.column(align = True)
        col.operator("srti.create_export_node", icon = "NODETREE")
        row = col.row(align = True)
        row.operator("srti.render_normals", icon = 'MOD_NORMALEDIT')
        row.operator("srti.render_composite", icon = 'GROUP_VCOL')
        col.operator("srti.reset_nodes", icon = "X")


###Debug
class SyntheticRTIPanelDebug(bpy.types.Panel):
    """Creates a Panel in the Object properties window,"""
    bl_label = "Debug"
    bl_idname = "srti.panelDebug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        curr_scene = context.scene
        layout = self.layout
        num_light = max(len(curr_scene.srti_props.list_lights),1)
        num_cam = len(curr_scene.srti_props.list_cameras)
        num_values = len(curr_scene.srti_props.list_values)
        tot_comb = numpy.prod(list(row.steps for row in curr_scene.srti_props.list_values))

        if curr_scene.srti_props.main_parent:
            main = curr_scene.srti_props.main_parent.name
        else:
            main = "None"

        box = layout.box()
        box.label("Main = %s" % main)
        box.label("Lamps = %i" % num_light)
        box.label("Cameras = %i" % num_cam)
        box.label("Values = %i" % num_values)
        box.label("Combination = %i" % tot_comb)
        box.label("Total frames = %i" % (num_light * num_cam *tot_comb))
        box.label("Total file lines = %i" %len(file_lines))

        