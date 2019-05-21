import bpy
from bpy.props import BoolProperty
from ... utils.objects import apply_modifier
from ... material import assign_material
from ... preferences import get_preferences
from ... utility import collections


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

        if len(context.selected_objects) == 1:
            cutter = context.active_object
            object = bpy.context.object.modifiers["HopsBoolean"].object
            for mod in cutter.modifiers:
                if mod.type == "BOOLEAN":
                    bpy.ops.object.modifier_remove(modifier="HopsBoolean")
            object.select_set(state=True)

        cutters = self.get_cutter_objects(context)
        object = context.active_object
        cutter = cutters[0]
        scene = context.scene.collection

        for f in cutter.data.polygons:
            f.use_smooth = True

        new_obj = object.copy()
        new_obj.data = object.data.copy()
        # new_obj.animation_data_clear()
        # scene.objects.link(new_obj)

        # collections.unlink_obj(context, new_obj)
        collections.link_obj(context, new_obj, 'Collection')

        # support local view
        cutter.hops.status = "BOOLSHAPE"
        cutter.hide_render = True
        cutter.display_type = "WIRE"

        collections.unlink_obj(context, cutter)
        collections.link_obj(context, cutter, 'Hardops')

        modifier_active_obj = object.modifiers.new(name="HopsBoolean", type="BOOLEAN")
        modifier_active_obj.operation = "DIFFERENCE"
        modifier_active_obj.object = cutter

        if get_preferences().workflow == "NONDESTRUCTIVE":
            for modifier in reversed(modifiers_by_name(object)):
                while object.modifiers.find(modifier.name) != 0:
                    bpy.ops.object.modifier_move_up(modifier=modifier.name)

        modifier_new_obj = new_obj.modifiers.new(name="HopsBoolean", type="BOOLEAN")
        modifier_new_obj.operation = "INTERSECT"
        modifier_new_obj.object = cutter

        if get_preferences().workflow == "NONDESTRUCTIVE":
            context.view_layer.objects.active = new_obj
            new_obj.select_set(state=True)
            # set_active(new_obj, select=True, only_select=True)
            for modifier in reversed(modifiers_by_name(object)):
                while new_obj.modifiers.find(modifier.name) != 0:
                    bpy.ops.object.modifier_move_up(modifier=modifier.name)

        if self.prevent_moving:
            object.lock_location[0] = True
            object.lock_location[1] = True
            object.lock_location[2] = True
            object.lock_rotation[0] = True
            object.lock_rotation[1] = True
            object.lock_rotation[2] = True
            object.lock_scale[0] = True
            object.lock_scale[1] = True
            object.lock_scale[2] = True
            new_obj.lock_location[0] = True
            new_obj.lock_location[1] = True
            new_obj.lock_location[2] = True
            new_obj.lock_rotation[0] = True
            new_obj.lock_rotation[1] = True
            new_obj.lock_rotation[2] = True
            new_obj.lock_scale[0] = True
            new_obj.lock_scale[1] = True
            new_obj.lock_scale[2] = True

        if get_preferences().workflow == "DESTRUCTIVE":
            for mod in object.modifiers:
                if mod == modifier_active_obj:
                    apply_modifier(modifier_active_obj)

            for mod in new_obj.modifiers:
                if mod == modifier_new_obj:
                    apply_modifier(modifier_new_obj)

            cutter.select_set(state=False)
            new_obj.select_set(state=True)
            bpy.ops.hops.soft_sharpen()

        elif get_preferences().workflow == "NONDESTRUCTIVE":

            for mod in object.modifiers:
                if mod.type == "BEVEL":
                    mod.limit_method = 'ANGLE'

            for mod in new_obj.modifiers:
                if mod.type == "BEVEL":
                    mod.limit_method = 'ANGLE'

            self.remove_cutters = False

            new_obj.select_set(state=False)
            object.select_set(state=False)
            cutter.select_set(state=True)
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


def modifiers_by_name(obj):
    return [x for x in obj.modifiers if x.type in {"BOOLEAN", "MIRROR", "SOLIDIFY"}]

class HOPS_OT_Slash2(bpy.types.Operator):
    bl_idname = "hops.2slash"
    bl_label = "Complex Split Check"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Splits the primary mesh using the secondary mesh"

    split_mesh: BoolProperty(name="Split Mesh",
                             description="Separate the mesh after CSplit",
                             default=True)

    remove_cutters: BoolProperty(name="Remove Cutters",
                                 description="Remove Cutters",
                                 default=False)

    keep_cutters_origin: BoolProperty(name="Keep Cutters Origin",
                                      description="Remove Cutters",
                                      default=False)

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if len(selected) > 1:
            if object.mode == "OBJECT" and all(obj.type == "MESH" for obj in selected):
                return True
        else:
            if object.hops.is_pending_boolean:
                return True

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.label(text="General Parameters")
        col.prop(self, "split_mesh")

        box = layout.box()
        col = box.column()
        col.label(text="Cutters Parameters")
        col.prop(self, "remove_cutters")
        col.prop(self, "keep_cutters_origin")

    def execute(self, context):
        bpy.context.scene.update()
        selected = bpy.context.selected_objects
        cutters = self.get_cutter_objects()
        object = bpy.context.active_object

        if len(selected) == 1:
            if object.hops.is_pending_boolean:
                for modifier in object.modifiers:
                    if modifier.type == "BOOLEAN":
                        to_add = modifier.object
                        cutters.append(to_add)
                        to_add.select_set(state=True)

        for cutter in cutters:

            cutter.hops.status = "BOOLSHAPE"
            cutter.hide_render = True
            cutter.display_type = "WIRE"
            solidify = cutter.modifiers.new(name="temp_solid", type="SOLIDIFY")
            solidify.thickness = 0.0001
            solidify.offset = 1

            if object.hops.is_pending_boolean:

                for modifier in object.modifiers:
                    if modifier.type == "BOOLEAN":
                        if modifier.object == cutter:
                            apply_modifier(modifier)

            elif not object.hops.is_pending_boolean:

                modifier = object.modifiers.new(name="temp", type="BOOLEAN")
                modifier.operation = "DIFFERENCE"
                modifier.object = cutter
                for mod in object.modifiers:
                    if mod.type == "BOOLEAN":
                        bpy.ops.object.modifier_apply(apply_as="DATA", modifier="temp")

            cutter.modifiers.remove(solidify)

        bpy.ops.hops.soft_sharpen()
        # split_mesh(self, context)

        all_selected = self.get_cutter_objects()
        splited = [x for x in all_selected if x not in cutters]

        bpy.ops.object.select_all(action='DESELECT')
        for obj in splited:
            obj.select_set(state=True)
            assign_material(context, obj)
            bpy.context.view_layer.objects.active = obj
            if obj.hops.status == "CSTEP":
                me = obj.data
                for e in me.edges:
                    e.select_set(state=False)
                    if e.bevel_weight > 0:
                        e.select_set(state=True)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.hide(unselected=True)
                bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        for obj in cutters:
            obj.select_set(state=True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        if self.remove_cutters:
            bpy.ops.object.delete(use_global=False)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = object
        object.select_set(state=True)

        if not self.split_mesh:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

        if object.hops.status == "CSTEP":
            me = object.data
            for e in me.edges:
                if e.bevel_weight > 0:
                    e.select_set(state=True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.hide(unselected=True)
            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

    @staticmethod
    def get_cutter_objects():
        selection = bpy.context.selected_objects
        active = bpy.context.active_object
        return [object for object in selection if object != active and object.type == "MESH"]


def select_inside(self, context):
    selected = bpy.context.selected_objects
    active = bpy.context.active_object
    selected.remove(active)
    max_dist = 1.84467e+19

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    active.select_set(state=False)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    active.select_set(state=True)

    for obj in selected:
        for v in active.data.vertices:
            if is_inside((active.matrix_world @ v.co), max_dist, obj):
                v.select_set(state=True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_linked(delimit=set())
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
    bpy.ops.object.mode_set(mode='OBJECT')


def is_inside(p, max_dist, obj):
    print(obj.data)
    hit, point, normal, face = obj.closest_point_on_mesh(p, distance=max_dist)
    p2 = (obj.matrix_world * point - p)
    v = p2.dot(normal)
    return not(v < 0.0)


def split_mesh(self, context):
    select_inside(self, context)
    if self.split_mesh:
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            bpy.ops.mesh.separate()
        except:
            pass
        bpy.ops.object.mode_set(mode='OBJECT')
