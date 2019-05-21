import bpy
import bmesh
from ... utils.modifiers import apply_modifiers, remove_modifiers
from ... utils.objects import set_active
from ... preferences import get_preferences


class HOPS_OT_CutIn(bpy.types.Operator):
    bl_idname = "hops.cut_in"
    bl_label = "Cut In"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Destructively cuts into the primary mesh using the secondary mesh. Respects marking"

    @classmethod
    def poll(cls, context):
        if len(cls.get_cutter_objects()) == 0: return False
        if getattr(context.active_object, "type", "") != "MESH": return False
        if getattr(context.active_object, "mode", "") != "OBJECT": return False
        return getattr(context.active_object, "type", "") == "MESH"
        return True

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        active = bpy.context.active_object
        active.select_set(state=False)
        bpy.ops.object.duplicate()
        duplicate = bpy.context.active_object
        boolobjects = bpy.context.selected_objects

        if not get_preferences().keep_cutin_bevel:
            remove_modifiers(boolobjects, "BEVEL")

        active.select_set(state=True)
        bpy.ops.hops.bool_difference()

        set_active(active, True, True)

        bpy.ops.hops.soft_sharpen()

        active.select_set(state=False)
        for obj in boolobjects:
            print(obj)
            obj.select_set(state=True)

        # createdobj = bpy.context.selected_objects
        duplicates = bpy.context.selected_objects

        for a in duplicates:
            duplicate = a
        set_active(duplicate, True, True)
        apply_modifiers(duplicates, "BEVEL")

        obj = bpy.context.active_object
        me = obj.data

        bm = bmesh.new()
        bm.from_mesh(me)

        cr = bm.edges.layers.crease.verify()
        bw = bm.edges.layers.bevel_weight.verify()

        alledges = [e for e in bm.edges if len(e.link_faces) == 2]

        for e in alledges:
            e[cr] = 0
            e.smooth = True
            e.seam = False
            e[bw] = 0

        bm.to_mesh(me)
        bm.free()

        set_active(active, True, True)
        selection = bpy.context.selected_objects
        apply_modifiers(selection, "BOOLEAN")
        bpy.ops.hops.soft_sharpen()

        set_active(duplicate, True, True)
        bpy.ops.object.delete()

        return {'FINISHED'}

    @staticmethod
    def get_cutter_objects():
        selection = bpy.context.selected_objects
        active = bpy.context.active_object
        return [object for object in selection if object != active and object.type == "MESH"]
