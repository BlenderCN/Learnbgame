import bpy
from bpy.props import BoolProperty
from ... utils.objects import move_modifier_up, apply_modifier, only_select, set_active
from ... material import assign_material


class HOPS_OT_ComplexSplitBooleanOperator(bpy.types.Operator):
    bl_idname = "hops.complex_split_boolean"
    bl_label = "Complex Split Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Split the primary mesh using the secondary mesh"

    split_mesh: BoolProperty(name="Split Mesh",
                             description="Separate the mesh after CSplit",
                             default=True)

    text = "Meshes Separated"
    op_tag = "(C)Slice"
    op_detail = "Meshes split"

    use_bmesh: BoolProperty(name="Use Bmesh Boolean",
                            description="Use new bmesh boolean",
                            default=False)

    @classmethod
    def poll(cls, context):
        if len(cls.get_cutter_objects()) == 0: return False
        if getattr(context.active_object, "type", "") != "MESH": return False
        if getattr(context.active_object, "mode", "") != "OBJECT": return False
        return getattr(context.active_object, "type", "") == "MESH"
        return True

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "split_mesh")
        layout.prop(self, "use_bmesh")

    def execute(self, context):
        original_mesh_objects = [object for object in context.view_layer.objects if object.type == 'MESH' and object != context.active_object]
        target = context.active_object
        cutters = self.get_cutter_objects()
        for cutter in cutters:
            cutter.display_type = "WIRE"
            assign_material(context, cutter, csplit=True)
            self.split(target, cutter, self.use_bmesh)
        if self.split_mesh:
            self.separate_mesh_by_looseparts(target)
        split_objects = [obj for obj in [obj for obj in context.view_layer.objects if obj.type == 'MESH'] if obj not in original_mesh_objects]
        target = self.get_target_object(split_objects, target.data.vertices[:])
        split_objects.remove(target)
        for object in split_objects:
            assign_material(context, object, replace=True)
        only_select(cutters)
        return {'FINISHED'}

    def split(self, object, cutter, use_bmesh, margin=0.0001):
        if margin != 0:
            solidify = cutter.modifiers.new(name="temp", type="SOLIDIFY")
            solidify.thickness = margin
            solidify.offset = 1
        if not object.hops.is_pending_boolean:
            self.cut_object(object, cutter, "DIFFERENCE", use_bmesh)
        if object.hops.status == "CSTEP":
            bpy.ops.hops.complex_sharpen()
        elif object.hops.status == "UNDEFINED":
            pass
        else:
            bpy.ops.hops.complex_sharpen()
        if margin != 0:
            cutter.modifiers.remove(solidify)

    @staticmethod
    def get_cutter_objects():
        selection = bpy.context.selected_objects
        active = bpy.context.active_object
        return [object for object in selection if object != active and object.type == "MESH"]

    @staticmethod
    def separate_mesh_by_looseparts(object):
        set_active(object)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def get_target_object(split_objects, target_verts):
        vert_differences = []
        for obj in split_objects:
            verts = [vert.co for vert in obj.data.vertices[:]]
            vert_difference = [abs(verts[vert].x - target_verts[vert].x) + abs(verts[vert].y - target_verts[vert].y) + abs(verts[vert].z - target_verts[vert].z) for vert in range(len(verts))]
            vert_differences.append(sum(vert_difference))
        return split_objects[vert_differences.index(min(vert_differences))]

    @staticmethod
    def cut_object(object, cutter, operation, use_bmesh):
        modifier = object.modifiers.new(name="temp", type="BOOLEAN")
        modifier.operation = operation

        modifier.object = cutter
        move_modifier_up(modifier)
        apply_modifier(modifier)
