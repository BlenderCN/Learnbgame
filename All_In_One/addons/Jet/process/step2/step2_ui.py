import bpy
from ... common_utils import get_hotkey

#Panel
class VIEW3D_PT_jet_step2(bpy.types.Panel):
    bl_label = "2. Optimization"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Jet"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.Jet.info, "optimization", text="", icon="INFO")

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("mesh.merge", text="Merge - " + get_hotkey(context, "mesh.merge"))

        # Error: EXCEPTION_ACCESS_VIOLATION:
        """
        Couldn't unmap memory
        Traceback (most recent call last):
          File "\AppData\Roaming\Blender Foundation\Blender\2.79\scripts\addons\Jet\process\step2\step2_ui.py", line 26, in draw
            col.operator("mesh.merge", text="Collapse").type = 'COLLAPSE'
        TypeError: bpy_struct: item.attr = val: enum "COLLAPSE" not found in ()
        
        location: <unknown location>:-1
        
        location: <unknown location>:-1
        Error: EXCEPTION_ACCESS_VIOLATION    
        """
        # In object mode, put the cursor over the button and release it.
        # When it releases from the button, the error comes out
        #col.operator("mesh.merge", text="Collapse").type = 'COLLAPSE'

        col.operator("jet_merge.btn", text="Collapse - " + get_hotkey(context, "mesh.merge")).type = "COLLAPSE"
        col.operator("mesh.f2", text="Dissolve Faces - " + get_hotkey(context, "mesh.f2"))

        col.operator("jet_delete_menu.btn", text="Delete Element - " + "X or Del")
        op = col.operator("mesh.dissolve_mode", text="Delete Element and keep mesh - " + get_hotkey(context, "mesh.dissolve_mode"))
        op.use_verts=True
        op.use_face_split = False
        op.use_boundary_tear = False

#Operators
class VIEW3D_OT_jet_merge(bpy.types.Operator):
    bl_idname = "jet_merge.btn"
    bl_label = ""
    bl_description = ""

    type = bpy.props.StringProperty(default="COLLAPSE")

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        bpy.ops.mesh.merge(type=self.type)
        return {'FINISHED'}

class VIEW3D_OT_jet_delete_menu(bpy.types.Operator):
    bl_idname = "jet_delete_menu.btn"
    bl_label = ""
    bl_description = ""

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        bpy.ops.wm.call_menu(name="VIEW3D_MT_edit_mesh_delete")
        return {'FINISHED'}
