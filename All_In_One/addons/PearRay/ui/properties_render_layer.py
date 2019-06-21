import bpy


from bl_ui.properties_render_layer import RenderLayerButtonsPanel


from bl_ui import properties_render_layer
properties_render_layer.RENDERLAYER_PT_layers.COMPAT_ENGINES.add('PEARRAY_RENDER')
del properties_render_layer



class RENDERLAYER_PT_pr_layer_options(RenderLayerButtonsPanel, bpy.types.Panel):
    bl_label = "Layer"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        rd = scene.render
        rl = rd.layers.active

        split = layout.split()

        col = split.column()
        col.prop(scene, "layers", text="Scene")
        col.prop(rl, "layers_exclude", text="Exclude")

        col = split.column()
        col.prop(rl, "layers", text="Layer")
        col.prop(rl, "layers_zmask", text="Mask Layer")

        split = layout.split()

        col = split.column()
        col.label(text="Material:")
        col.prop(rl, "material_override", text="")


class RENDERLAYER_PT_pr_layer_aovs(RenderLayerButtonsPanel, bpy.types.Panel):
    bl_label = "AOVs"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    # Custom passes do not work well with animation and other render layers. :/
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        rd = scene.render
        rl = rd.layers.active
        rl2 = scene.pearray_layer# Not satisfiying

        split = layout.split()

        col = split.column()
        col.prop(rl, "use_pass_combined")
        col.prop(rl, "use_pass_z")
        col.prop(rl, "use_pass_normal")
        col.prop(rl2, "aov_ng")
        col.prop(rl2, "aov_nx")
        col.prop(rl2, "aov_ny")
        col.prop(rl, "use_pass_vector")
        col.prop(rl, "use_pass_uv")
        col.prop(rl, "use_pass_object_index")
        col.prop(rl, "use_pass_material_index")

        col = split.column()
        col.prop(rl2, "aov_p")
        col.prop(rl2, "aov_dpdu")
        col.prop(rl2, "aov_dpdv")
        col.prop(rl2, "aov_dpdw")
        col.prop(rl2, "aov_dpdx")
        col.prop(rl2, "aov_dpdy")
        col.prop(rl2, "aov_dpdz")
        col.prop(rl2, "aov_t")
        col.prop(rl2, "aov_q")
        col.prop(rl2, "aov_samples")

        layout.separator()
        split = layout.split()
        split.prop(rl2, "raw_spectral")

    