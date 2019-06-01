import bpy
from traceback import print_exc

SEPARATOR_SCALE_Y = 11 / 18

def tag_redraw(all=False):
    wm = bpy.context.window_manager
    if not wm:
        return

    for w in wm.windows:
        for a in w.screen.areas:
            if all or a.type == 'USER_PREFERENCES':
                for r in a.regions:
                    if all or r.type == 'WINDOW':
                        r.tag_redraw()


def operator(
        layout, operator_id, text=None, icon_id='NONE',
        emboss=True, icon_value=0,
        **kwargs):
    if text is not None:
        properties = layout.operator(
            operator_id, text,
            icon=icon_id, emboss=emboss, icon_value=icon_value)
    else:
        properties = layout.operator(
            operator_id,
            icon=icon_id, emboss=emboss, icon_value=icon_value)

    for k, v in kwargs.items():
        setattr(properties, k, v)

    return properties


class SUV_OT_exec(bpy.types.Operator):
    bl_idname = "suv.exec"
    bl_label = ""
    bl_options = {'INTERNAL'}

    cmd = bpy.props.StringProperty(maxlen=1024)

    def execute(self, context):
        try:
            O = bpy.ops
            C = bpy.context
            exec(self.cmd, globals(), locals())
        except:
            print_exc()

        return {'FINISHED'}


class SUV_OT_exec1(bpy.types.Operator):
    bl_idname = "suv.exec1"
    bl_label = ""
    bl_options = {'INTERNAL'}

    glocals = None

    cmd = bpy.props.StringProperty(maxlen=1024)

    def execute(self, context):
        try:
            O = bpy.ops
            C = bpy.context
            exec(self.cmd, globals(), locals())
            SUV_OT_exec1.glocals = locals()
        except:
            print_exc()
            return {'CANCELLED'}

        return {'FINISHED'}


class SUV_OT_exec2(bpy.types.Operator):
    bl_idname = "suv.exec2"
    bl_label = ""
    bl_options = {'INTERNAL'}

    cmd = bpy.props.StringProperty(maxlen=1024)

    def execute(self, context):
        try:
            O = bpy.ops
            C = bpy.context
            exec(self.cmd, globals(), SUV_OT_exec1.glocals)
        except:
            print_exc()
            return {'CANCELLED'}

        return {'FINISHED'}


class SUV_OT_macro2(bpy.types.Macro):
    bl_idname = "suv.macro2"
    bl_label = ""
    bl_options = {'MACRO', 'INTERNAL'}


def register():
    SUV_OT_macro2.define("SUV_OT_exec1")
    SUV_OT_macro2.define("SUV_OT_exec2")