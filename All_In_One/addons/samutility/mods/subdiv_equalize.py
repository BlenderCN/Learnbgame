import bpy

class subdivLevelViewFromRender(bpy.types.Operator):
    bl_idname = "samutils.subdiv_view_from_render"
    bl_label = "Subdiv view level from render"
    bl_description = "Subsurf viewport level equals render level\n on all selected objects"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (bpy.context.selected_objects != [])

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type in ('MESH', 'CURVE'):
                for mod in obj.modifiers:
                    if mod.type == 'SUBSURF':
                        if mod.levels != mod.render_levels:
                            print(obj.name, '-', 'viewport =', mod.levels, 'change to', 'render =',  mod.render_levels)
                            mod.levels = mod.render_levels
                        else:
                            pass
                            #print(obj.name, 'already equals')
        return {"FINISHED"}


class subdivLevelRenderFromView(bpy.types.Operator):
    bl_idname = "samutils.subdiv_render_from_view"
    bl_label = "Subdiv render level from view"
    bl_description = "Subsurf render level equals view level\n on all selected objects"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (bpy.context.selected_objects != [])

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type in ('MESH', 'CURVE'):
                for mod in obj.modifiers:
                    if mod.type == 'SUBSURF':
                        if mod.levels != mod.render_levels:
                            print(obj.name, '-', 'render =',  mod.render_levels, 'change to', 'viewport =', mod.levels)
                            mod.render_levels = mod.levels
                        else:
                            pass
                            #print(obj.name, 'already equals')
        return {"FINISHED"}
