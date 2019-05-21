import bpy
import bmesh
from .addon import prefs


class SUV_OT_uv_snap(bpy.types.Operator):
    bl_idname = "suv.uv_snap"
    bl_label = "Snap UV"
    bl_options = {'REGISTER', 'UNDO'}

    selection = None
    bm = None

    threshold = bpy.props.FloatProperty(min=0)
    delta = bpy.props.IntProperty(options={'SKIP_SAVE'})

    def init_bm(self):
        self.bm = bmesh.from_edit_mesh(bpy.context.edit_object.data)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()

        if not hasattr(self, "face"):
            self.bm.verts.index_update()
            self.bm.edges.index_update()

    def get_selection(self):
        if not self.bm or not self.bm.is_valid:
            self.init_bm()

        uvl = self.bm.loops.layers.uv.verify()
        ret = set()
        for f in self.bm.faces:
            for l in f.loops:
                if l[uvl].select:
                    ret.add(l.index)

        return ret

    def execute(self, context):
        try:
            selection = self.get_selection()
            if context.active_operator and \
                    context.active_operator.bl_idname == self.bl_idname and \
                    self.__class__.selection and \
                    self.__class__.selection == selection:
                bpy.ops.ed.undo()
            bpy.ops.uv.remove_doubles(
                threshold=self.threshold,
                use_unselected=True)
            self.__class__.selection = self.get_selection()
        except:
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        if context.active_operator and \
                context.active_operator.bl_idname == self.bl_idname:
            self.threshold = context.active_operator.threshold + \
                self.delta * prefs().uv_snap_step

        bpy.ops.suv.overlay(
            text="Threshold\t%.2f" % self.threshold)

        return self.execute(context)

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'
