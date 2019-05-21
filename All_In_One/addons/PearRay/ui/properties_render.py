import bpy


from bl_ui import properties_render
properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add('PEARRAY_RENDER')
del properties_render


class RenderButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (rd.use_game_engine is False) and (rd.engine in cls.COMPAT_ENGINES)


class RENDER_PT_pr_render(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Render"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        scene = context.scene

        row = layout.row(align=True)
        row.operator("render.render", text="Render", icon='RENDER_STILL')
        row.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True
        row.operator("pearray.run_rayview", text="RayView", icon='EXPORT')

        split = layout.split(percentage=0.33)

        split.label(text="Display:")
        row = split.row(align=True)
        row.prop(rd, "display_mode", text="")
        row.prop(rd, "use_lock_interface", icon_only=True)

        layout.separator()

        split = layout.split(percentage=0.33)
        split.label(text="Tile Mode:")
        row = split.row(align=True)
        row.prop(context.scene.pearray, "render_tile_mode", expand=True)

        layout.separator()

        layout.prop(scene.pearray, "integrator")
        layout.prop(scene.pearray, "max_ray_depth")


class RENDER_PT_pr_performance(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Performance"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Threads:")
        col.row(align=True).prop(rd, "threads_mode", expand=True)
        sub = col.column(align=True)
        sub.enabled = rd.threads_mode == 'FIXED'
        sub.prop(rd, "threads")

        col.label(text="Tile Size:")
        col.prop(rd, "tile_x", text="X")
        col.prop(rd, "tile_y", text="Y")


class RENDER_PT_pr_output(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Output"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        layout.prop(rd, "filepath", text="")


class RENDER_PT_pr_sampler(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Sampler"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(scene.pearray, "sampler_aa_mode", text="AA")
        layout.prop(scene.pearray, "sampler_max_aa_samples")
        layout.separator()
        layout.prop(scene.pearray, "sampler_lens_mode", text="Lens")
        layout.prop(scene.pearray, "sampler_max_lens_samples")
        layout.separator()
        layout.prop(scene.pearray, "sampler_time_mode", text="Time")
        layout.prop(scene.pearray, "sampler_max_time_samples")
        layout.prop(scene.pearray, "sampler_time_mapping_mode", expand=True)
        layout.prop(scene.pearray, "sampler_time_scale")
        layout.separator()
        layout.prop(scene.pearray, "sampler_spectral_mode", text="Spectral")
        layout.prop(scene.pearray, "sampler_max_spectral_samples")
        layout.separator()
        layout.label(text="Max Samples: %i" % 
            (scene.pearray.sampler_max_aa_samples *
             scene.pearray.sampler_max_lens_samples *
             scene.pearray.sampler_max_time_samples *
             scene.pearray.sampler_max_spectral_samples))


class RENDER_PT_pr_integrator(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Integrator"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if scene.pearray.integrator == 'VISUALIZER':
            layout.prop(scene.pearray, "debug_mode")
        else:
            if scene.pearray.integrator != 'AO':
                layout.prop(scene.pearray, "max_diffuse_bounces")

            if scene.pearray.integrator == 'DIRECT' or scene.pearray.integrator == 'BIDIRECT' or scene.pearray.integrator == 'AO':
                layout.prop(scene.pearray, "max_light_samples")

            if scene.pearray.integrator == 'BIDIRECT':
                layout.prop(scene.pearray, "max_light_depth")

            if scene.pearray.integrator == 'AO':
                layout.prop(scene.pearray, "ao_use_materials")

            if scene.pearray.integrator == 'PPM':
                layout.separator()
                layout.prop(scene.pearray, "photon_count")
                layout.prop(scene.pearray, "photon_passes")
                col = layout.column(align=True)
                col.label("Gathering:")
                col.prop(scene.pearray, "photon_gather_radius")
                col.prop(scene.pearray, "photon_max_gather_count")
                col.prop(scene.pearray, "photon_gathering_mode", text="")
                col.prop(scene.pearray, "photon_squeeze")
                col.prop(scene.pearray, "photon_ratio")
                col = layout.column(align=True)


class RENDER_PT_pr_export_settings(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Export Settings"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw_header(self, context):
        pass

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(scene.pearray, "keep_prc")
        layout.prop(scene.pearray, "beautiful_prc")
        layout.prop(scene.pearray, "linear_rgb")
    
