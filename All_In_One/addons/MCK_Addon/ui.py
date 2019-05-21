import bpy

from bpy.props import *



# Custom types
# DATA
bpy.types.Scene.checkResult = StringProperty(
    name="Result",
    default = 'waiting...')

# CHECK SEND OR NOT
bpy.types.Scene.sendData = BoolProperty(
        name = "Send",
        default = False,
        description = "True or False?")

# CHECK DEBUG PRINT TO CONSOLE OR NOT        
bpy.types.Scene.printSendData = BoolProperty(
        name = "Print send",
        default = False,
        description = "True or False?")

# CHECK RECIEVE DATA IR NOT        
bpy.types.Scene.recieveData = BoolProperty(
        name = "Recieve",
        default = False,
        description = "True or False?")

# CHECK ONLY ONE CURREND FRAME DATA
bpy.types.Scene.currentFrame = BoolProperty(
        name = "Only current frame",
        default = False,
        description = "True or False?")

# CHECK FOR SPEED ERRORS
bpy.types.Scene.checkLimit = BoolProperty(
        name = "Check speed errors",
        default = False,
        description = "True or False?")

# PRINT AXIES IN UI
bpy.types.Scene.printA = StringProperty(
    name="Result",
    default = 'AXIES')
  

# A1
bpy.types.Scene.A_1 = FloatProperty(
    name="A1",
    default = 0.0)
# A2
bpy.types.Scene.A_2 = FloatProperty(
    name="A2",
    default = 0.0)
# A3
bpy.types.Scene.A_3 = FloatProperty(
    name="A3",
    default = 0.0)
# A4
bpy.types.Scene.A_4 = FloatProperty(
    name="A4",
    default = 0.0)
# A5
bpy.types.Scene.A_5 = FloatProperty(
    name="A5",
    default = 0.0)
# A6
bpy.types.Scene.A_6 = FloatProperty(
    name="A6",
    default = 0.0)
############################### MODAL ###########################
# ERROR
bpy.types.Scene.modalErrors = StringProperty(
    name="Result",
    default = 'waiting...')
  
# CHECK FOR MODAL PRINT
bpy.types.Scene.modalPrint = BoolProperty(
        name = "RT print",
        default = False,
        description = "Print in real time")


class MotionControl(bpy.types.Panel):
    bl_idname = "test_panel"
    bl_label = "Motion Control"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "KUKA"
    
    def draw(self, context):
        obj = context.active_object
        scene = context.scene
        layout = self.layout
        
        row = layout.row()
        row.label(text="", icon='CAMERA_DATA')
        row.prop(obj, "name", text="Select")
        
        col = layout.column(align=True)

        col.label(text="Check data:")
        row = col.row(align=True)
        row.operator("object.checking_data", text = 'Check path', icon = 'OUTLINER_OB_CAMERA')
        row = col.row(align=True)
        row.operator("object.check_a1_to_a6", text = 'Check A1 to A6', icon = 'MANIPUL')
        #layout.prop(scene, 'checkResult')
        

class DebugPanel(bpy.types.Panel):
    bl_idname = "debug_panel"
    bl_label = "Debug Data"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "KUKA"
    
    def draw(self, context):
        obj = context.active_object
        scene = context.scene
        
        layout = self.layout
        layout.label(str(scene.checkResult))
        
        col = layout.column()
        row = col.row(align=True)
        row.prop(scene, 'sendData', icon = 'FORWARD')
        row.prop(scene,'printSendData',icon = 'SCULPT_DYNTOPO')
        
        row = col.row(align=True)
        row.prop(scene,'recieveData',icon = 'BACK')
        
        row = col.row(align=True)
        row.prop(scene, 'currentFrame', icon = 'FRAME_NEXT')
        row = col.row(align=True)
        row.prop(scene, 'checkLimit', icon = 'ERROR')
        
        col = layout.column()
        col.label(text="DATA:")
        #col.prop(scene, "frame_current", text="FRAME")
        col.label(text='FRAME: ' + str(scene.frame_current))
        #col.label(text=str(scene.modalErrors))
        col = layout.column()
        row = col.row(align=True)
        row.prop(scene, 'modalPrint', text = 'REAL TIME', icon = 'REC')
        row.operator("object.rt_print_to_ui", text = 'Print A1-A6', icon = 'PLAY')
        
####### A1 TO A6
        row = col.row(align=True)
        row.prop(scene, 'A_1')
        #row.label(text = '0')
        
        row = col.row(align=True)
        row.prop(scene, 'A_2')
        #row.label(text = '-90')
        
        row = col.row(align=True)
        row.prop(scene, 'A_3')
        #row.label(text = '90')
        
        row = col.row(align=True)
        row.prop(scene, 'A_4')
        #row.label(text = '0')
        
        row = col.row(align=True)
        row.prop(scene, 'A_5')
        #row.label(text = '90')
        
        row = col.row(align=True)
        row.prop(scene, 'A_6')
        #row.label(text = '0')
        
        col = layout.column()
        col.label(text="ERROR:")
        if scene.modalErrors == '=(':
            col.label(text=str(scene.modalErrors), icon = 'CANCEL')
        else:
            col.label(text=str(scene.modalErrors), icon = 'FILE_TICK')
        