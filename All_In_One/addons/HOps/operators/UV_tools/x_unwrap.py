import bpy
from bpy.props import FloatProperty, BoolProperty
from . uv_draw import hops_draw_uv
from ... utils.bmesh import selectSmoothEdges


class HOPS_OT_XUnwrapF(bpy.types.Operator):
    bl_idname = "hops.xunwrap"
    bl_label = "XUnwrap"
    bl_description = "Unwrap mesh using automated unwrapping and draw UVs in the 3d view"
    bl_options = {"REGISTER", "UNDO"}

    angle_limit: FloatProperty(name="Angle limit",
                               default=45,
                               min=0.0,
                               max=90)

    rmargin: FloatProperty(name="Margin",
                           default=0.0002,
                           min=0.0,
                           max=1)
    user_area_weight: FloatProperty(name="User area weight",
                                    default=0.03,
                                    min=0.0,
                                    max=1)

    rmethod: BoolProperty(default=True)
    bweight_as_seams: BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if object.mode == "OBJECT" and all(obj.type == "MESH" for obj in selected):
            return True

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "angle_limit")
        box.prop(self, 'bweight_as_seams', text="convert bevel weight to seams")
        box.prop(self, "rmargin")
        box.prop(self, "user_area_weight")
        box.prop(self, 'rmethod', text="use smart method")

    def invoke(self, context, event):
        self.execute(context)
        #hops_draw_uv()

        return {"FINISHED"}

    def parameter_getter(self):
        return self.rmargin

    def execute(self, context):
        if self.bweight_as_seams:
            for obj in bpy.context.selected_objects:
                bpy.context.view_layer.objects.active = obj
                me = obj.data
                #me.show_edge_crease = True

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(type="EDGE")
                selectSmoothEdges(self, me)
                bpy.ops.mesh.mark_seam(clear=False)
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

        if self.rmethod:
            bpy.ops.uv.smart_project(angle_limit=self.angle_limit, island_margin=self.rmargin, user_area_weight=self.user_area_weight)

        else:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=self.rmargin)
            bpy.ops.object.mode_set(mode='OBJECT')

        return {"FINISHED"}
