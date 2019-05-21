import bpy
import bpy.utils.previews
import os
from bpy.types import Panel

# ############################################################
# User Interface
# ############################################################

class EVERTimsUIBase:
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_description= ""
    bl_category = "EVERTims"

class EVERTimsToolBar(EVERTimsUIBase, Panel):

    bl_label = "EVERTims"

    @staticmethod

    def draw_header(self, context):
        # Enable layout
        evertims = context.scene.evertims
        self.layout.label(text="", icon_value=custom_icons["evertims_icon"].icon_id)

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        evertims = scene.evertims
        addon_prefs = context.user_preferences.addons[__package__].preferences
        # layout.enabled = True

        # Import elements
        box = layout.box()
        box.label("Import elements", icon='GROUP')
        rowsub = box.row(align=True)
        rowsub.operator("evert.import_template", text="Template scene", icon='MESH_CUBE').arg = 'scene'
        rowsub = box.row(align=True)
        rowsub.operator("evert.import_template", text="Logic", icon='EMPTY_DATA').arg = 'logic'
        rowsub = box.row(align=True)
        rowsub.operator("evert.import_template", text="Room & Materials", icon='MESH_CUBE').arg = 'room'
        rowsub = box.row(align=True)
        rowsub.operator("evert.import_template", text="Source", icon='MESH_CUBE').arg = 'source'
        rowsub = box.row(align=True)
        rowsub.operator("evert.import_template", text="Listener", icon='MESH_CUBE').arg = 'listener'
        rowsub = box.row(align=True)
        rowsub.operator("evert.import_script", text="Materials (.txt)", icon='TEXT').arg = 'materialList'
        rowsub.label("> see Text Editor")

        # Define KX_GameObjects as EVERTims elements
        box = layout.box()
        box.label("Define as EVERTims element", icon='PINNED')        
        col = box.column(align=True)
        col.prop_search(evertims, "room_object", bpy.data, "objects")
        col = box.column(align=True)
        col.prop_search(evertims, "listener_object", bpy.data, "objects")
        col = box.column(align=True)
        col.prop_search(evertims, "source_object", bpy.data, "objects")

        # Network configuration
        box = layout.box()
        box.label("Network", icon='URL')  

        rowsub = box.row(align=True)
        rowsub.label("Blender IP adress & port:")
        rowsub = box.row(align=True)
        split = rowsub.split(percentage=0.6)
        colsub = split.column()
        colsub.prop(evertims, "ip_local", text="")
        colsub = split.column()
        colsub.prop(evertims, "port_read", text="port")

        rowsub = box.row(align=True)
        rowsub.label("Raytracing IP adress & port:")
        rowsub = box.row(align=True)
        split = rowsub.split(percentage=0.6)
        colsub = split.column()
        colsub.prop(evertims, "ip_raytracing", text="")
        colsub = split.column()
        colsub.prop(evertims, "port_write_raytracing", text="port")

        rowsub = box.row(align=True)
        rowsub.label("Auralization IP adress & port:")
        rowsub = box.row(align=True)
        split = rowsub.split(percentage=0.6)
        colsub = split.column()
        colsub.prop(evertims, "ip_auralization", text="")
        colsub = split.column()
        colsub.prop(evertims, "port_write_auralization", text="port")

        # EVERTims auralization engine setup
        box = layout.box()
        box.label("Embedded auralization client", icon='SPEAKER')         
        rowsub = box.row(align=True)
        rowsub.prop(addon_prefs, "auralization_client_path_to_binary", text="exe")

        rowsub = box.row(align=True)
        if not evertims.enable_auralization_client:
            rowsub.operator("evert.evertims_auralization_client", text="START", icon="RADIOBUT_OFF").arg ='PLAY'
        else:
            rowsub.operator("evert.evertims_auralization_client", text="STOP", icon="REC").arg ='STOP'

        # EVERTims raytracing client setup
        box = layout.box()
        box.label("Embedded raytracing client", icon='LAMP_AREA')            
        rowsub = box.row(align=True)
        rowsub.prop(addon_prefs, "raytracing_client_path_to_binary", text="ims")
        rowsub = box.row(align=True)
        rowsub.prop(addon_prefs, "raytracing_client_path_to_matFile", text="mat")
        rowsub = box.row(align=True)
        rowsub.operator("evert.misc_utils", text="Reload mat file", icon='TEXT').arg = 'FLAG_MAT_UPDATE'

        rowsub = box.row(align=True)
        rowsub.label("Reflection order:")
        rowsub = box.row(align=True)
        split = rowsub.split(percentage=0.5)
        colsub = split.column()
        colsub.prop(evertims, "min_reflection_order", text="min")
        colsub = split.column()
        colsub.prop(evertims, "max_reflection_order", text="max")

        rowsub = box.row(align=True)
        rowsub.prop(evertims, "debug_logs_raytracing", text="print raytracing client logs in console")
        rowsub = box.row(align=True)
        if not evertims.enable_raytracing_client:
            rowsub.operator("evert.evertims_raytracing_client", text="START", icon="RADIOBUT_OFF").arg ='PLAY'
        else:
            rowsub.operator("evert.evertims_raytracing_client", text="STOP", icon="REC").arg ='STOP'

        # Simulation Setup
        box = layout.box()
        box.label("On the fly auralization", icon='QUIT')  
        # col.label("Simulation parameters:")
        rowsub = box.row(align=True)
        rowsub.prop(evertims, "debug_rays", text="draw rays in 3DView & BGE")
        rowsub = box.row(align=True)
        rowsub.prop(evertims, "debug_logs", text="print local logs in Blender console")
        rowsub = box.row(align=True)
        rowsub.label("Movement update threshold:")
        rowsub = box.row(align=True)
        split = rowsub.split(percentage=0.5)
        colsub = split.column()
        colsub.prop(evertims, "movement_threshold_loc", text="loc (m)")
        colsub = split.column()
        colsub.prop(evertims, "movement_threshold_rot", text="rot (deg)")

        # Auralization in BPY
        rowsub = box.row(align=True)
        if not evertims.enable_edit_mode:
            rowsub.operator("evert.evertims_in_edit_mode", text="START (bpy mode)", icon="RADIOBUT_OFF").arg ='PLAY'
        else:
            rowsub.operator("evert.evertims_in_edit_mode", text="STOP (bpy mode)", icon="REC").arg ='STOP'
        col = box.column()
        col.label("(avoid using undo while running)")

        # enable upload data to raytracing client in during BGE session
        rowsub = box.row(align=True)
        if not evertims.enable_bge:
            rowsub.operator("evert.evertims_in_bge", text="Enable in BGE", icon="RADIOBUT_OFF").arg ='ENABLE'
        else:
            rowsub.operator("evert.evertims_in_bge", text="Enable in BGE", icon="REC").arg ='DISABLE'        


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(EVERTimsToolBar)

    # register custom icons
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    currentFilePath = os.path.realpath(__file__)
    iconsDirPath = os.path.join(os.path.dirname(currentFilePath), "icons")
    custom_icons.load("evertims_icon", os.path.join(iconsDirPath, "evertims-icon-32x32.png"), 'IMAGE')

def unregister():
    bpy.utils.unregister_class(EVERTimsToolBar)

    # unregister custom icons
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
    bpy.utils.unregister_module(__name__)    
