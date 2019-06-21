import bpy


class HOPS_OT_Analysis(bpy.types.Operator):
    bl_idname = "hops.analysis"
    bl_label = "Hops Analysis"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "in and out for analysis options"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return(object.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):

        object = context.active_object

        if bpy.context.object.data.show_statvis is False:
            bpy.context.object.data.show_statvis = True
            bpy.context.scene.tool_settings.statvis.type = 'DISTORT'
            # bpy.context.scene.tool_settings.statvis.type = 'INTERSECT'

            modifiers = object.modifiers
            for mod in modifiers:
                mod.show_viewport = False

        else:
            bpy.context.object.data.show_statvis = False

            modifiers = object.modifiers
            for mod in modifiers:
                mod.show_viewport = True

        return {'FINISHED'}
