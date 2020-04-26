import bpy
from bpy.props import BoolProperty
from ... utils.objects import apply_modifier
from ... material import assign_material
from ... preferences import get_preferences
from ... utility import collections, modifier


class HOPS_OT_Slash(bpy.types.Operator):
    bl_idname = "hops.slash"
    bl_label = "Slash"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Splits the primary mesh using the secondary mesh"

    remove_cutters: BoolProperty(name="Remove Cutters",
                                 description="Remove Cutters",
                                 default=False)

    prevent_moving: BoolProperty(name="Prevent From moving",
                                 description="Prevent From moving",
                                 default=False)

    local_view = False

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        object = context.active_object
        if object is None:
            return False
        if object.mode == "OBJECT" and all(obj.type == "MESH" for obj in selected):
            return True

    def execute(self, context):

        object = context.active_object

        cutters = self.get_cutter_objects(context)
        cutter = cutters[0]
        scene = context.scene.collection

        for f in cutter.data.polygons:
            f.use_smooth = True

        new_obj = object.copy()
        new_obj.data = object.data.copy()

        collections.link_obj(context, new_obj, 'Collection')

        cutter.hops.status = "BOOLSHAPE"
        cutter.hide_render = True
        cutter.display_type = "WIRE"

        collections.unlink_obj(context, cutter)
        collections.link_obj(context, cutter, 'Cutters')

        modifier_active_obj = object.modifiers.new(name="Boolean", type="BOOLEAN")
        modifier_active_obj.operation = "DIFFERENCE"
        modifier_active_obj.object = cutter

        modifier_new_obj = new_obj.modifiers.new(name="Boolean", type="BOOLEAN")
        modifier_new_obj.operation = "INTERSECT"
        modifier_new_obj.object = cutter

        if get_preferences().workflow == "DESTRUCTIVE":
            for mod in object.modifiers:
                if mod == modifier_active_obj:
                    apply_modifier(modifier_active_obj)

            for mod in new_obj.modifiers:
                if mod == modifier_new_obj:
                    apply_modifier(modifier_new_obj)

            cutter.select_set(False)
            new_obj.select_set(True)
            bpy.ops.hops.soft_sharpen()

        elif get_preferences().workflow == "NONDESTRUCTIVE":
            for mod in object.modifiers:
                if mod.type == "BEVEL":
                    mod.limit_method = 'ANGLE'
            for mod in new_obj.modifiers:
                if mod.type == "BEVEL":
                    mod.limit_method = 'ANGLE'

            modifier.sort(context, new_obj)
            modifier.sort(context, object)
            new_obj.select_set(False)
            object.select_set(False)
            cutter.select_set(True)
            context.view_layer.objects.active = cutter

        bpy.context.scene.update()
        assign_material(context, new_obj)
        if self.remove_cutters:
            scene.objects.unlink(cutter)

        return {'FINISHED'}

    def get_cutter_objects(self, context):
        selection = context.selected_objects
        active = context.active_object
        return [object for object in selection if object != active and object.type == "MESH"]
