import bpy
import bmesh
import statistics
from mathutils import Vector


class HOPS_OT_MOD_Lattice(bpy.types.Operator):
    bl_idname = "hops.mod_lattice"
    bl_label = "Add Lattice Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Lattice Modifier
LMB + CTRL - Add new lattice Modifier

"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        cursor_loc = context.scene.cursor.location.copy()

        for object in context.selected_objects:

            if event.ctrl:
                lattice_object = self.add_lattice_obj(context, object)
                self.add_lattice_modifier(context, object, lattice_object)
            else:
                if not self.lattice_modifiers(object):
                    lattice_object = self.add_lattice_obj(context, object)
                    self.add_lattice_modifier(context, object, lattice_object)

        context.scene.cursor.location = cursor_loc
        return {"FINISHED"}

    @staticmethod
    def lattice_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "LATTICE"]

    def add_lattice_modifier(self, context, object, lattice_object):
        lattice_modifier = object.modifiers.new(name="Lattice", type="LATTICE")
        lattice_modifier.object = lattice_object
        if context.mode == 'EDIT_MESH':
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            lattice_modifier.vertex_group = vg.name

    def add_lattice_obj(self, context, object):
        lattice_data = bpy.data.lattices.new('lattice')
        lattice_obj = bpy.data.objects.new('lattice', lattice_data)
        bpy.data.collections['Collection'].objects.link(lattice_obj)
        if context.mode == 'EDIT_MESH':

            me = object.data
            bm = bmesh.from_edit_mesh(me)
            coords = [v.co for v in bm.verts if v.select]
            bmesh.update_edit_mesh(me)

            bpy.ops.view3d.snap_cursor_to_selected()
            lattice_obj.location = context.scene.cursor.location
            lattice_obj.scale = self.scale(coords)

        else:
            lattice_obj.location = object.location
            lattice_obj.rotation_euler = object.rotation_euler
            lattice_obj.dimensions = object.dimensions

        return lattice_obj

    @staticmethod
    def scale(coordinates):
        x = [coordinate[0] for coordinate in coordinates]
        y = [coordinate[1] for coordinate in coordinates]
        z = [coordinate[2] for coordinate in coordinates]
        minimum = Vector((min(x), min(y), min(z)))
        maximum = Vector((max(x), max(y), max(z)))
        scale = maximum - minimum

        return scale
