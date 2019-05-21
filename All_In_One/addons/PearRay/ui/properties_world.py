import bpy


from bl_ui import properties_world
properties_world.WORLD_PT_custom_props.COMPAT_ENGINES.add('PEARRAY_RENDER')
del properties_world


class WorldButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return context.world and (rd.use_game_engine is False) and (rd.engine in cls.COMPAT_ENGINES)


class WORLD_PT_pr_preview(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Preview"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        self.layout.template_preview(context.world)


class WORLD_PT_pr_background(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Background"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        layout = self.layout

        world = context.world
        
        layout.prop(world, "horizon_color", text="Color")