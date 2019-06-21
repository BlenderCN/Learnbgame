import bpy
from bpy.props import BoolProperty


class Select(bpy.types.Operator):
    bl_idname = "machin3.select_decals"
    bl_label = "MACHIN3: Select Decals"
    bl_options = {'REGISTER', 'UNDO'}

    keep_parents_selected: BoolProperty(name="Keep Decal Parents Selected", default=False)

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "keep_parents_selected")

    def execute(self, context):
        sel = context.selected_objects

        if sel:
            decals = [obj for obj in context.visible_objects if obj.DM.isdecal and obj.parent in sel]

            if decals:
                if not self.keep_parents_selected:
                    for obj in sel:
                        obj.select_set(False)

                for decal in decals:
                    decal.select_set(True)

                context.view_layer.objects.active = decals[0]

        return {'FINISHED'}
