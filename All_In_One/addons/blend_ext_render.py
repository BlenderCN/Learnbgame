bl_info = {
        "name": "External obj renderer",
        "author": "Richard Thier (prenex)",
        "version": (0, 9),
        "blender": (2,6,9),
        "description": "Render by exporting an obj scene and notifying an external program over UDP",
        "category": "Render"
}

import bpy,socket

# TODO: the execute will be called many times after
# we change values in non-props dialogs on the T toolbox
# which is not creating a big deal, but unecessary traffic...
class ExternalRenderingOperator(bpy.types.Operator):
    """External obj rendering operator"""
    bl_idname = "render.external_obj_operator"
    bl_label = "Render external obj"
    bl_options = { 'REGISTER', 'PRESET' }

    # Properties - filled on the props dialog...
    obj_path = bpy.props.StringProperty(
           name="Obj path",
           default="/"
    )

    obj_name = bpy.props.StringProperty(
           name="Obj name",
           default="scene.obj"
    )

    udp_ip = bpy.props.StringProperty(
           name="UDP Notif. IP",
           default="127.0.0.1"
    )

    udp_port = bpy.props.IntProperty(
           name="UDP Notif. PORT",
           default=8051
    )

    message = bpy.props.StringProperty(
           name="UDP notification msg",
           default="cmd{${chat)${Blender UDP test!}}"
    )

    def execute(self, context):
        # Export the scene to the given transfer path
        if self.obj_path.endswith("/"):
                export_path=self.obj_path + self.obj_name
        else:
                export_path=self.obj_path + '/' + self.obj_name
        bpy.ops.export_scene.obj(
                filepath=export_path,
                use_normals=True, use_triangles=True, # for objmaster
                path_mode='COPY') # necessary to copy textures and use relpath!

        # Open a socket (closed by GC in python)
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP

        # Send the notification message through UDP
        sock.sendto(bytes(self.message + "\n", "UTF-8"), (self.udp_ip, self.udp_port))

        # Indicate success to blender
        return {'FINISHED'}

    # With this trick, we can show the possibilities as
    # a dialog and only apply their values by calling 
    # execute after user clicks on the OK button!
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

# menu function
def menu_func(self, context):
    self.layout.operator(
        ExternalRenderingOperator.bl_idname,
        text=ExternalRenderingOperator.__doc__,
        icon='PLUGIN')

# Register the operator
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_render.append(menu_func)
def unregister():
    bpy.types.INFO_MT_render.remove(menu_func)
    bpy.utils.unregister_module(__name__)
if __name__ == "__main__":
    register()
