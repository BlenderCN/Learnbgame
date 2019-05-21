
from bpy.props import IntProperty, BoolProperty, EnumProperty
from mathutils import Vector
import bgl
import bpy
bl_info = {
    "name": "Smart Edit Mode",
    "description": "Automatically switch to edit mode when selecting vertex, edge or polygon mode",
    "author": ("Tilapiatsu"),
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}


class TILA_smart_editmode(bpy.types.Operator):
    bl_idname = "view3d.tila_smart_editmode"
    bl_label = "Smart Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}

    mode = bpy.props.IntProperty(name='mode', default=0)
    use_extend = bpy.props.BoolProperty(name='use_extend', default=False)
    use_expand = bpy.props.BoolProperty(name='use_expand', default=False)
    alt_mode = bpy.props.BoolProperty(name='alt_mode', default=False)

    mesh_mode = ['VERT', 'EDGE', 'FACE']
    gpencil_mode = ['POINT', 'STROKE', 'SEGMENT']
    uv_mode = ['VERTEX', 'EDGE', 'FACE', 'ISLAND']

    def modal(self, context, event):
        pass

    def invoke(self, context, event):
        def switch_mesh_mode(self, current_mode):
            if self.mesh_mode[self.mode] == current_mode:
                bpy.ops.object.editmode_toggle()
            else:
                bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

        def switch_gpencil_mode(self, current_mode):
            if self.gpencil_mode[self.mode] == current_mode:
                bpy.ops.gpencil.editmode_toggle()
            else:
                bpy.context.scene.tool_settings.gpencil_selectmode = self.gpencil_mode[self.mode]

        def switch_uv_mode(self, current_mode):
            if bpy.context.scene.tool_settings.use_uv_select_sync:
                switch_mesh_mode(self, self.mesh_mode[mesh_mode_link(self, current_mode)])
            else:
                bpy.context.scene.tool_settings.uv_select_mode = self.uv_mode[self.mode]

        def mesh_mode_link(self, mode):
            for m in self.mesh_mode:
                if mode in m:
                    return self.mesh_mode.index(m)
                else:
                    return 0

        if bpy.context.mode == 'OBJECT':
            if bpy.context.active_object is None:
                return {'CANCELLED'}
            if bpy.context.active_object.type == 'MESH':
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_mode(use_extend=self.use_extend, use_expand=self.use_expand, type=self.mesh_mode[self.mode])

            elif bpy.context.active_object.type == 'GPENCIL':
                if self.alt_mode:
                    bpy.ops.gpencil.paintmode_toggle()
                else:
                    bpy.ops.gpencil.editmode_toggle()
                    bpy.context.scene.tool_settings.gpencil_selectmode = self.gpencil_mode[self.mode]

        elif bpy.context.mode == 'EDIT_MESH':
            if self.alt_mode:
                bpy.ops.object.editmode_toggle()
            else:
                method = None
                if bpy.context.space_data.type == 'IMAGE_EDITOR':
                    method = switch_uv_mode
                    if bpy.context.scene.tool_settings.uv_select_mode == 'VERTEX':
                        method(self, 'VERTEX')
                    elif bpy.context.scene.tool_settings.uv_select_mode == 'EDGE':
                        method(self, 'EDGE')
                    elif bpy.context.scene.tool_settings.uv_select_mode == 'FACE':
                        method(self, 'FACE')
                    elif bpy.context.scene.tool_settings.uv_select_mode == 'ISLAND':
                        method(self, 'ISLAND')
                else:
                    method = switch_mesh_mode
                    if bpy.context.scene.tool_settings.mesh_select_mode[0]:
                        method(self, 'VERT')
                    elif bpy.context.scene.tool_settings.mesh_select_mode[1]:
                        method(self, 'EDGE')
                    elif bpy.context.scene.tool_settings.mesh_select_mode[2]:
                        method(self, 'FACE')

        elif bpy.context.mode in ['EDIT_GPENCIL', 'PAINT_GPENCIL', 'SCULPT_GPENCIL', 'WEIGHT_GPENCIL']:
            if self.alt_mode:
                bpy.ops.gpencil.paintmode_toggle()
            else:
                switch_gpencil_mode(self, bpy.context.scene.tool_settings.gpencil_selectmode)

        else:
            bpy.ops.object.editmode_toggle()

        return {'FINISHED'}


classes = (
    TILA_smart_editmode
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
