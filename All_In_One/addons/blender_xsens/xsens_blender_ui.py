import bpy

class XSensPanel(bpy.types.Panel):
    """
    A panel for the XSens interaction
    """
    bl_label = "XSens Mocap"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "posemode"
    
    def draw(self, context):
        layout = self.layout
        #layout.label(text="Record Data")
        layout.operator("xsens.record", text='record')

class OBJECT_OT_RecordButton(bpy.types.Operator):
    bl_idname = "xsens.record"
    bl_label = "Record"
 
    def execute(self, context):
        print("starting record")
        return{'FINISHED'}    