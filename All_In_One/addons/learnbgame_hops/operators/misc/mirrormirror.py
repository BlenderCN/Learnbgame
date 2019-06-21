import bpy
import mathutils
from ... preferences import get_preferences
from ... utils.context import ExecutionContext


# Do the Basic Union, Difference and Intersection operations


def operation(context, _operation, x, y, z, zx, zy, zz, direction, used_axis):

        object = bpy.context.active_object
        object.select_set(state=True)
        if(len(bpy.context.selected_objects)) == 1:  # one is selected , add mirror mod immediately to that object#
            if object.type == "MESH":
                if get_preferences().Hops_mirror_modes == "MODIFIER":
                    with ExecutionContext(mode="OBJECT", active_object=object):
                        mirror_mod = None
                        for modifier in object.modifiers:
                            if modifier.name == "hops_mirror":
                                mirror_mod = modifier
                        if mirror_mod is None:
                            mirror_mod = object.modifiers.new("hops_mirror", "MIRROR")
                            mirror_mod.use_clip = True
                            mirror_mod.use_axis[0] = False
                            mirror_mod.use_axis[1] = False
                            mirror_mod.use_axis[2] = False

                elif get_preferences().Hops_mirror_modes == "BISECT":
                    with ExecutionContext(mode="OBJECT", active_object=object):
                        if get_preferences().Hops_mirror_direction == "+":
                            clear_inner = True
                            clear_outer = False
                        elif get_preferences().Hops_mirror_direction == "-":
                            clear_inner = False
                            clear_outer = True

                        bpy.ops.object.mode_set(mode='EDIT')
                        if object.hops.status == "CSTEP":
                            bpy.ops.mesh.reveal()
                        bpy.ops.mesh.select_all(action='SELECT')
                        #bisection happens
                        bpy.ops.mesh.bisect(plane_co=(x, y, z), plane_no=(zx, zy, zz), clear_inner=clear_inner, clear_outer=clear_outer)
                        bpy.ops.mesh.select_all(action='DESELECT')
                        if object.hops.status == "CSTEP":
                            bpy.ops.mesh.select_all(action='TOGGLE')
                            bpy.ops.mesh.hide(unselected=False)
                        bpy.ops.object.mode_set(mode='OBJECT')
                        object = bpy.context.active_object
                        mirror_mod = None
                        for modifier in object.modifiers:
                            if modifier.name == "hops_mirror":
                                mirror_mod = modifier
                        if mirror_mod is None:
                            mirror_mod = object.modifiers.new("hops_mirror", "MIRROR")
                            mirror_mod.use_clip = True
                            mirror_mod.use_axis[0] = False
                            mirror_mod.use_axis[1] = False
                            mirror_mod.use_axis[2] = False

                elif get_preferences().Hops_mirror_modes == "SYMMETRY":
                    with ExecutionContext(mode="EDIT", active_object=object):
                        bpy.ops.mesh.select_all(action='SELECT')
                        if get_preferences().Hops_Mir2_symmetrize_type == "Machin3" and "MESHmachine" in bpy.context.preferences.addons.keys():
                            bpy.ops.machin3.symmetrize(axis=direction.split("_")[1], direction=direction.split("_")[0])
                        else:
                            bpy.ops.mesh.symmetrize(direction=direction)
                        bpy.ops.mesh.select_all(action='DESELECT')

                if get_preferences().Hops_mirror_modes in {"BISECT", "MODIFIER"}:
                    if _operation == "MIRROR_X":
                        mirror_mod.use_axis[0] = True
                        if get_preferences().Hops_mirror_modes == "MODIFIER":
                            mirror_mod.use_bisect_axis[0] = True
                            if get_preferences().Hops_mirror_direction == "-":
                                mirror_mod.use_bisect_flip_axis[0] = True
                            else:
                                mirror_mod.use_bisect_flip_axis[0] = False
                            mirror_mod.show_on_cage = True
                    elif _operation == "MIRROR_Y":
                        mirror_mod.use_axis[1] = True
                        if get_preferences().Hops_mirror_modes == "MODIFIER":
                            mirror_mod.use_bisect_axis[1] = True
                            if get_preferences().Hops_mirror_direction == "-":
                                mirror_mod.use_bisect_flip_axis[1] = True
                            else:
                                mirror_mod.use_bisect_flip_axis[1] = False
                            mirror_mod.show_on_cage = True
                    elif _operation == "MIRROR_Z":
                        mirror_mod.use_axis[2] = True
                        if get_preferences().Hops_mirror_modes == "MODIFIER":
                            mirror_mod.use_bisect_axis[2] = True
                            if get_preferences().Hops_mirror_direction == "-":
                                mirror_mod.use_bisect_flip_axis[2] = True
                            else:
                                mirror_mod.use_bisect_flip_axis[2] = False
                            mirror_mod.show_on_cage = True

        else:
            if get_preferences().Hops_mirror_modes_multi == "VIA_ACTIVE":
                with ExecutionContext(mode="OBJECT", active_object=object):
                    mirror_ob = bpy.context.active_object  # last ob selected
                    for obj in bpy.context.selected_objects:
                        if obj != mirror_ob:
                            if obj.type == "MESH":

                                mirror_ob.select_set(state=False)  # pop object from sel_stack
                                object = obj

                                mirror_mod_multi = None
                                for modifier in object.modifiers:
                                    if modifier.name == "hops_mirror_via_active":
                                        mirror_mod_multi = modifier
                                if mirror_mod_multi is None:
                                    mirror_mod_multi = object.modifiers.new("hops_mirror_via_active", "MIRROR")
                                    mirror_mod_multi.use_axis[0] = False
                                    mirror_mod_multi.use_axis[1] = False
                                    mirror_mod_multi.use_axis[2] = False
                                    mirror_mod_multi.use_clip = True
                                    mirror_mod_multi.mirror_object = mirror_ob
                                    mirror_mod_multi.use_mirror_u = True

                                if _operation == "MIRROR_X":
                                    mirror_mod_multi.use_axis[0] = True
                                    if get_preferences().Hops_mirror_direction == "-":
                                        mirror_mod_multi.use_bisect_axis[0] = True
                                    else:
                                        mirror_mod_multi.use_bisect_axis[0] = False
                                elif _operation == "MIRROR_Y":
                                    mirror_mod_multi.use_axis[1] = True
                                    if get_preferences().Hops_mirror_direction == "-":
                                        mirror_mod_multi.use_bisect_axis[1] = True
                                    else:
                                        mirror_mod_multi.use_bisect_axis[1] = False
                                elif _operation == "MIRROR_Z":
                                    mirror_mod_multi.use_axis[2] = True
                                    if get_preferences().Hops_mirror_direction == "-":
                                        mirror_mod_multi.use_bisect_axis[2] = True
                                    else:
                                        mirror_mod_multi.use_bisect_axis[2] = False

            elif get_preferences().Hops_mirror_modes_multi == "SYMMETRY":
                selected = bpy.context.selected_objects
                for obj in selected:
                    print("aa")
                    bpy.context.view_layer.objects.active = obj
                    with ExecutionContext(mode="EDIT", active_object=obj):
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.symmetrize(direction=direction)
                        bpy.ops.mesh.select_all(action='DESELECT')
        # mirror_ob.select = 1
        # object.select = 1
        bpy.context.view_layer.objects.active = object


# ------------------- OPERATOR CLASSES ------------------------------
# Mirror Tool


class HOPS_OT_MirrorX(bpy.types.Operator):
    bl_idname = "hops.mirror_mirror_x"
    bl_label = "Mirror X"
    bl_description = "Mirror On the X Axis"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout

        layout.prop(get_preferences(), "Hops_mirror_direction")
        layout.prop(get_preferences(), "Hops_mirror_modes")

    @classmethod
    def poll(cls, context):
        # selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if object.mode in {"OBJECT", "EDIT"}:
            return True

    def execute(self, context):
        x, y, z = bpy.context.object.location
        zx, zy, zz = bpy.context.object.rotation_euler

        if get_preferences().Hops_mirror_direction == "+":
            direction = "POSITIVE_X"
        elif get_preferences().Hops_mirror_direction == "-":
            direction = "NEGATIVE_X"
        used_axis = "X"

        vec = mathutils.Vector((1, 0, 0))
        mat = mathutils.Matrix.Rotation(zx, 4, "X")
        vec.rotate(mat)
        mat = mathutils.Matrix.Rotation(zy, 4, "Y")
        vec.rotate(mat)
        mat = mathutils.Matrix.Rotation(zz, 4, "Z")
        vec.rotate(mat)

        nx = vec[0]
        ny = vec[1]
        nz = vec[2]

        operation(context, "MIRROR_X", x, y, z, nx, ny, nz, direction, used_axis)

        return {'FINISHED'}

class HOPS_OT_MirrorY(bpy.types.Operator):
    bl_idname = "hops.mirror_mirror_y"
    bl_label = "Mirror Y"
    bl_description = "Mirror On the Y Axis"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout

        layout.prop(get_preferences(), "Hops_mirror_direction")
        layout.prop(get_preferences(), "Hops_mirror_modes")

    @classmethod
    def poll(cls, context):
        # selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if object.mode in {"OBJECT", "EDIT"}:
            return True

    def execute(self, context):
        x, y, z = bpy.context.object.location
        zx, zy, zz = bpy.context.object.rotation_euler

        if get_preferences().Hops_mirror_direction == "+":
            direction = "POSITIVE_Y"
        elif get_preferences().Hops_mirror_direction == "-":
            direction = "NEGATIVE_Y"
        used_axis = "Y"

        vec = mathutils.Vector((0, 1, 0))
        mat = mathutils.Matrix.Rotation(zx, 4, "X")
        vec.rotate(mat)
        mat = mathutils.Matrix.Rotation(zy, 4, "Y")
        vec.rotate(mat)
        mat = mathutils.Matrix.Rotation(zz, 4, "Z")
        vec.rotate(mat)

        nx = vec[0]
        ny = vec[1]
        nz = vec[2]

        operation(context, "MIRROR_Y", x, y, z, nx, ny, nz, direction, used_axis)

        return {'FINISHED'}


class HOPS_OT_MirrorZ(bpy.types.Operator):
    bl_idname = "hops.mirror_mirror_z"
    bl_label = "Mirror Z"
    bl_description = "Mirror On the Z Axis"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout

        layout.prop(get_preferences(), "Hops_mirror_direction")
        layout.prop(get_preferences(), "Hops_mirror_modes")

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        if object.mode in {"OBJECT", "EDIT"}:
            return True

    def execute(self, context):
        x, y, z = bpy.context.object.location
        zx, zy, zz = bpy.context.object.rotation_euler

        if get_preferences().Hops_mirror_direction == "+":
            direction = "POSITIVE_Z"
        elif get_preferences().Hops_mirror_direction == "-":
            direction = "NEGATIVE_Z"
        used_axis = "Z"

        vec = mathutils.Vector((0, 0, 1))
        mat = mathutils.Matrix.Rotation(zx, 4, "X")
        vec.rotate(mat)
        mat = mathutils.Matrix.Rotation(zy, 4, "Y")
        vec.rotate(mat)
        mat = mathutils.Matrix.Rotation(zz, 4, "Z")
        vec.rotate(mat)

        nx = vec[0]
        ny = vec[1]
        nz = vec[2]

        operation(context, "MIRROR_Z", x, y, z, nx, ny, nz, direction, used_axis)

        return {'FINISHED'}
