import bpy
from bl_ui import properties_render
from . import base

base.compatify_class(properties_render.RENDER_PT_render)
base.compatify_class(properties_render.RENDER_PT_dimensions)
base.compatify_class(properties_render.RENDER_PT_performance) # FIXME everything not threads
base.compatify_class(properties_render.RENDER_PT_post_processing)
base.compatify_class(properties_render.RENDER_PT_stamp)
base.compatify_class(properties_render.RENDER_PT_output)

@base.register_root_panel
class W_PT_renderer(properties_render.RenderButtonsPanel, base.RootPanel):
    bl_label = 'Tungsten Renderer'
    prop_class = bpy.types.Scene

    @classmethod
    def get_object(cls, context):
        return context.scene

    PROPERTIES = {
        'adaptive_sampling': bpy.props.BoolProperty(
            name="Adaptive Sampling",
            description="Enable Adaptive Sampling",
            default=True,
        ),
        
        'stratified_sampler': bpy.props.BoolProperty(
            name="Stratified Sampler",
            description="Enable Stratified Sampler",
            default=True,
        ),
        
        'scene_bvh': bpy.props.BoolProperty(
            name="Scene BVH",
            description="Enable Scene BVH",
            default=True,
        ),
        
        'spp': bpy.props.IntProperty(
            name="SPP",
            description="Samples per pixel",
            subtype='UNSIGNED',
            min=1,
            default=32,
        ),
        
        'spp_step': bpy.props.IntProperty(
            name="SPP Step",
            description="SPP step size",
            subtype='UNSIGNED',
            min=1,
            default=4,
        ),        
    }

    @classmethod
    def to_scene_data(cls, wscene, obj):
        w = obj.tungsten
        return {
            'adaptive_sampling': w.adaptive_sampling,
            'stratified_sampler': w.stratified_sampler,
            'scene_bvh': w.scene_bvh,
            'spp': w.spp,
            'spp_step': w.spp_step,
        }

    def draw_for_object(self, obj):
        layout = self.layout
        w = obj.tungsten

        layout.prop(w, 'adaptive_sampling')
        layout.prop(w, 'stratified_sampler')
        layout.prop(w, 'scene_bvh')

        layout.label('Samples Per Pixel')
        row = layout.row(align=True)
        row.prop(w, 'spp', text="Max")
        row.prop(w, 'spp_step', text="Step")

@base.register_root_panel
class W_PT_integrator(properties_render.RenderButtonsPanel, base.RootPanel):
    bl_label = "Tungsten Integrator"
    prop_name = 'tungsten_int'
    prop_class = bpy.types.Scene

    @classmethod
    def get_object(cls, context):
        return context.scene

    PROPERTIES = {
        'type' : bpy.props.EnumProperty(
            name="Integrator Type",
            description="Integrator Type",
            items=(
                ('path_tracer', 'Path Tracer', ''),
                ('light_tracer', 'Light Tracer', ''),
                ('photon_map', 'Photon Map', ''),
                ('progressive_photon_map', 'PPPM', ''),
                ('bidirectional_path_tracer', 'Bidir. Path Tracer', ''),
                ('kelemen_mlt', 'Kelemen MLT', ''),
                ('multiplexed_mlt', 'Multiplexed MLT', ''),
                ('reversible_jump_mlt', 'Reversible Jump MLT', ''),
            ),
            default='path_tracer',
        ),
        
        'light_sampling': bpy.props.BoolProperty(
            name='Light Sampling',
            description='Enable Light Sampling',
            default=True,
        ),
        
        'volume_light_sampling': bpy.props.BoolProperty(
            name='Volume Light Sampling',
            description='Enable Volume Light Sampling',
            default=True,
        ),
        
        'two_sided_shading': bpy.props.BoolProperty(
            name='Two-Sided Shading',
            description='Enable Two-Sided Shading',
            default=True,
        ),
        
        'consistency_checks': bpy.props.BoolProperty(
            name='Consistency Checks',
            description='Enable Consistency Checks',
            default=True,
        ),
        
        'min_bounces': bpy.props.IntProperty(
            name="Minimum Bounces",
            description='Minimum Ray Bounces',
            subtype='UNSIGNED',
            min=0,
            default=0,
        ),
        
        'max_bounces': bpy.props.IntProperty(
            name="Maximum Bounces",
            description='Maximum Ray Bounces',
            subtype='UNSIGNED',
            min=0,
            default=64,
        ),
    }

    @classmethod
    def to_scene_data(cls, wscene, obj):
        w = obj.tungsten_int
        d = {
            'type': w.type,
            'enable_light_sampling': w.light_sampling,
            'enable_volume_light_sampling': w.volume_light_sampling,
            'enable_two_sided_shading': w.two_sided_shading,
            'enable_consistency_checks': w.consistency_checks,
            'min_bounces': w.min_bounces,
            'max_bounces': w.max_bounces,
        }

        d.update(super().to_scene_data(wscene, obj))
        return d

    def draw_for_object(self, obj):
        layout = self.layout
        w = obj.tungsten_int

        layout.prop(w, 'type', text='Type')

        layout.prop(w, 'light_sampling')
        layout.prop(w, 'volume_light_sampling')
        layout.prop(w, 'two_sided_shading')
        layout.prop(w, 'consistency_checks')

        layout.label('Bounces')
        row = layout.row(align=True)
        row.prop(w, 'min_bounces', text="Min")
        row.prop(w, 'max_bounces', text="Max")

@base.register_sub_panel
class W_PT_photon_map(W_PT_integrator.SubPanel):
    bl_label = "Tungsten Photon Map"
    w_types = {'photon_map', 'progressive_photon_map'}

    PROPERTIES = {
        'photon_count': bpy.props.IntProperty(
            name="Photon Count",
            description='Photon Count',
            subtype='UNSIGNED',
            min=0,
            default=1000000,
        ),
        
        'volume_photon_count': bpy.props.IntProperty(
            name="Volume Photon Count",
            description='Photon Count (for volumes)',
            subtype='UNSIGNED',
            min=0,
            default=100000,
        ),
        
        'gather_photon_count': bpy.props.IntProperty(
            name="Gather Count",
            description='Photon Gather Count',
            subtype='UNSIGNED',
            min=0,
            default=20,
        ),
        
        'gather_radius': bpy.props.FloatProperty(
            name="Gather Radius",
            description='Gather Radius',
            subtype='DISTANCE',
            unit='LENGTH',
            min=0,
            default=1,
        ),
    }

    @classmethod
    def to_scene_data(cls, wscene, obj):
        w = obj.tungsten_int
        return {
            'photon_count': w.photon_count,
            'volume_photon_count': w.volume_photon_count,
            'gather_photon_count': w.gather_photon_count,
            'gather_radius': w.gather_radius,
        }

    def draw_for_object(self, obj):
        layout = self.layout
        w = obj.tungsten_int

        layout.label('Photon Count')
        row = layout.row()
        row.prop(w, 'photon_count', text="Normal")
        row.prop(w, 'volume_photon_count', text="Volume")
        
        layout.label('Gather')
        row = layout.row()
        row.prop(w, 'gather_photon_count', text="Count")
        row.prop(w, 'gather_radius', text="Radius")

@base.register_sub_panel
class W_PT_pppm(W_PT_integrator.SubPanel):
    bl_label = "Tungsten PPPM"
    w_type = 'progressive_photon_map'

    PROPERTIES = {
        'pppm_alpha': bpy.props.FloatProperty(
            name='PPPM Alpha',
            description='PPPM Alpha parameter',
            min=0,
            max=1,
            default=0.3,
        ),
        
        'fixed_volume_radius': bpy.props.BoolProperty(
            name='Fixed Volume Radius',
            description='Enable Fixed Volume Radius',
            default=False,
        ),
        
        'volume_gather_radius': bpy.props.FloatProperty(
            name='Volume Gather Radius',
            description='Volume Gather Radius',
            subtype='DISTANCE',
            unit='LENGTH',
            min=0,
            default=1,
        ),
    }

    @classmethod
    def to_scene_data(cls, wscene, obj):
        w = obj.tungsten_int
        return {
            'alpha': w.pppm_alpha,
            'fixed_volume_radius': w.fixed_volume_radius,
            'volume_gather_radius': w.volume_gather_radius,
        }

    def draw_for_object(self, obj):
        layout = self.layout
        w = obj.tungsten_int

        layout.prop(w, 'pppm_alpha', slider=True)
        layout.prop(w, 'fixed_volume_radius')
        layout.prop(w, 'volume_gather_radius')
