import bpy

#CTRL+W
class OpToggleWireframe(bpy.types.Operator):
    bl_idname = "ndp.toggle_wireframe"
    bl_label = "Toggle Wireframe on Object"
    bl_description = "Turns on and off wireframe over the object."
    bl_options = {'UNDO'}

    toggle_mode : bpy.props.EnumProperty(
        items = (
            ('TOGGLE', "Toggle", "Inverts the visibility of a wireframe over object."),
            ('TURN_ON', "Turn On", "Turns on wireframe over object"),
            ('TURN_OFF', "Turn Off", "Turns off wireframe over object")),
        name = "Toggle mode:")

    @classmethod
    def poll(self, context):
        if (context.area is not None) and (context.area.type != 'VIEW_3D'):
            return False
        
        return context.active_object

    def execute(self, context):
        obj = context.active_object
        try:
            if self.toggle_mode == 'TOGGLE':
                obj.show_wire = not obj.show_wire
            elif self.toggle_mode == 'TURN_ON':
                obj.show_wire = True
            else:
                obj.show_wire = False
        except:
            pass
        return {'FINISHED'}

#ALT+C
class OpConvert(bpy.types.Operator):
    bl_idname = "ndp.convert"
    bl_label = "Convert options"
    bl_description = "Convert options"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if (context.area is not None) and (context.area.type != 'VIEW_3D'):
            return False
        
        if not context.active_object:
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        ndp_props = obj.data.ndp_props
        if ndp_props.is_ndp:
            bpy.ops.ndp.convert_ndp('INVOKE_DEFAULT')
        else:
            bpy.ops.wm.call_menu(name="NDP_MT_menu_convert")
        
        return {'FINISHED'}

class OpConvertNdp(bpy.types.Operator):
    bl_idname = "ndp.convert_ndp"
    bl_label = "Convert NDP to Mesh"
    bl_description = "Convert Non Destructive Prim to a regular mesh."
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(self, context):
        if (context.area is not None) and (context.area.type != 'VIEW_3D'):
            return False
        
        try:
            return context.active_object.data.ndp_props.is_ndp
        except:
            return False

    def invoke(self, context,event):
        obj = context.active_object
        ndp_props = obj.data.ndp_props
        wm : bpy.types.WindowManager = context.window_manager
        
        return wm.invoke_confirm(self, event)
    
    def execute(self, context):
        context.active_object.data.ndp_props.is_ndp = False
        return {'FINISHED'}

class MenuConvert(bpy.types.Menu):
    bl_idname = "NDP_MT_menu_convert"
    bl_label = "Convert to:"

    def draw(self, context):
        layout:bpy.types.UILayout = self.layout
        convert_a = layout.operator('OBJECT_OT_convert',
            text="Curve from Mesh/Text", icon='OUTLINER_OB_CURVE')
        convert_a.target = 'CURVE'
        convert_b = layout.operator('OBJECT_OT_convert',
            text="Curve from Curve/Meta/Surf/Text", icon='OUTLINER_OB_MESH')
        convert_b.target = 'MESH'

CLASSES = [
    MenuConvert,
    OpToggleWireframe,
    OpConvert,
    OpConvertNdp,
]