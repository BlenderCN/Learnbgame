import bpy
from ... utility import modifier
from bpy.props import EnumProperty
from ... utils.objects import get_current_selected_status


class HOPS_OT_ApplyModifiers(bpy.types.Operator):
    bl_idname = "hops.apply_modifiers"
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
            #modifier.apply(obj=obj, type=self.modifier_types, kitops=False)
            if obj.hops.status in ("CSHARP", "CSTEP"):
                modifier.apply(obj=obj, type=self.modifier_types)
            elif obj.hops.status == "UNDEFINED":
                bpy.ops.object.convert(target='MESH')
            else:
                pass

        return {"FINISHED"}
