import bpy
from ... utility import modifier
from bpy.props import EnumProperty


mods_types = [
    ('BOOLEAN', '', '', 'MOD_BOOLEAN', 1),
    ('MIRROR', '', '', 'MOD_MIRROR', 2),
    ('BEVEL', '', '', 'MOD_BEVEL', 3),
    ('SKIN', '', '', 'MOD_SKIN', 4),
    ('SOLIDIFY', '', '', 'MOD_SOLIDIFY', 5),
    ('SUBSURF', '', '', 'MOD_SUBSURF', 6),
    ('DECIMATE', '', '', 'MOD_DECIM', 7),
    ('DISPLACE', '', '', 'MOD_DISPLACE', 8),
    ('WEIGHTED_NORMAL', '', '', 'MOD_NORMALEDIT', 9),
    ('SHRINKWRAP', '', '', 'MOD_SHRINKWRAP', 10),
    ('SCREW', '', '', 'MOD_SCREW', 11),
    ('WIREFRAME', '', '', 'MOD_WIREFRAME', 12),
    ('CAST', '', '', 'MOD_CAST', 13),
    ('TRIANGULATE', '', '', 'MOD_TRIANGULATE', 14),
    ('LATTICE', '', '', 'MOD_LATTICE', 15),
    ('EDGE_SPLIT', '', '', 'MOD_EDGESPLIT', 16),
    ('ARRAY', '', '', 'MOD_ARRAY', 17)]



class HOPS_OT_MOD_Apply(bpy.types.Operator):
    bl_idname = "hops.mod_apply"
    bl_label = "Apply Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Apply Modifiers

"""
    modifier_types: EnumProperty(
        name='Start Operation',
        description='Start with the previously used settings of operation',
        items=mods_types,
        options={"ENUM_FLAG"},
        default={'BOOLEAN', 'MIRROR', 'BEVEL', 'SKIN', 'SOLIDIFY', 'SUBSURF', 'DECIMATE', 'DISPLACE', 'WEIGHTED_NORMAL', 'SHRINKWRAP', 'SCREW', 'WIREFRAME', 'CAST', 'LATTICE', 'EDGE_SPLIT', 'ARRAY'})

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.scale_x = 1.4
        col.scale_y = 1.4
        row = col.row()
        row.prop(self, "modifier_types", expand=True)

    def execute(self, context):
        for object in context.selected_objects:
            modifier.apply(object, type=self.modifier_types)

        return {"FINISHED"}
