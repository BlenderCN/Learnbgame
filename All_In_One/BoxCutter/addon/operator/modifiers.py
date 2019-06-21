import bpy

from bpy.props import EnumProperty

from .. utility import modifier


class BC_OT_ApplyModifiers(bpy.types.Operator):
    bl_idname = "bc.apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Apply modifiers"""

    modifier_types: EnumProperty(
        name='Modifier Types',
        description='Settings to display',
        items=[
            ('NONE', 'All', ''),
            ('BOOLEAN', 'Boolean', ''),
            ('MIRROR', 'Mirror', ''),
            ('BEVEL', 'Bevel', ''),
            ('SOLIDIFY', 'Solidify', ''),
            ('ARRAY', 'Array', '')],
        default='BOOLEAN')

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Modifiers Applied")
        colrow = col.row(align=True)
        colrow.prop(self, "modifier_types", expand=True)

    def execute(self, context):
        selected = context.selected_objects

        for obj in selected:
            modifier.apply(obj=obj, type=self.modifier_types)

        return {"FINISHED"}
