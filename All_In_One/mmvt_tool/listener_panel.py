import bpy
import traceback
import numpy as np
import mmvt_utils as mu


class TestListener(bpy.types.Operator):
    bl_idname = "mmvt.test_listening"
    bl_label = "Open TestListening"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        try:
            ret = mu.conn_to_listener.send_command(dict(cmd='plot',data=dict(x=np.arange(10), y=np.arange(10)*3)))
            if not ret:
                mu.message(self, 'Listener was stopped! Try to restart')
        except:
            print("Can't close connection to listener")
            print(traceback.format_exc())
        return {'PASS_THROUGH'}


class StartListening(bpy.types.Operator):
    bl_idname = "mmvt.start_listening"
    bl_label = "Open StartListening"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        if not bpy.context.scene.listen_to_port:
            ret = self.init_listener()
        else:
            mu.conn_to_listener.close()
            ret = True
        if ret:
            bpy.context.scene.listen_to_port = not bpy.context.scene.listen_to_port
        return {'PASS_THROUGH'}

    def init_listener(self):
        ret = False
        tries = 0
        while not ret and tries < 3:
            try:
                ret = mu.conn_to_listener.init()
                if ret:
                    mu.conn_to_listener.send_command('Hey!\n')
                else:
                    mu.message(self, 'Error initialize the listener. Try again')
            except:
                print("Can't open connection to listener")
                print(traceback.format_exc())
            tries += 1
        return ret


class ListenerPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Listener Panel"
    addon = None

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=0)
        if not bpy.context.scene.listen_to_port:
            row.operator(StartListening.bl_idname, text="Start", icon='COLOR_GREEN')
        else:
            row.operator(StartListening.bl_idname, text="Stop", icon='COLOR_RED')
        row.operator(TestListener.bl_idname, text="Test", icon='FORCE_HARMONIC')


bpy.types.Scene.listen_to_port = bpy.props.BoolProperty(default=False)


def init(addon):
    ListenerPanel.addon = addon
    bpy.context.scene.listen_to_port = False
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(ListenerPanel)
        bpy.utils.register_class(StartListening)
        bpy.utils.register_class(TestListener)
        # print('Listener Panel was registered!')
    except:
        print("Can't register Listener Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(ListenerPanel)
        bpy.utils.unregister_class(StartListening)
        bpy.utils.unregister_class(TestListener)
    except:
        pass
        # print("Can't unregister Listener Panel!")
