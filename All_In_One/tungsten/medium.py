import bpy

from . import props, base, node

class TungstenMediumNode(node.TungstenNode):
    w_type = None

    PROPERTIES = {
        'phase_function': bpy.props.EnumProperty(
            name='Phase',
            description='Phase Function',
            items=[
                ('isotropic', 'Isotropic', ''),
                ('henyey_greenstein', 'Henyey-Greenstein', ''),
                ('rayleigh', 'Rayleigh', ''),
            ],
            default='isotropic',
        ),
        'phase_g': bpy.props.FloatProperty(
            name='G',
            description='Phase G',
            min=-1.0,
            max=1.0,
            default=0.0,
        ),
        'max_bounces': bpy.props.IntProperty(
            name='Max Bounces',
            description='Max Bounces',
            subtype='UNSIGNED',
            min=1,
            default=1024,
        ),
    }

    def _init(self, context):
        self.outputs.new('TungstenMediumSocket', 'Medium')

    def _to_scene_data(self, scene):
        return {
            'type': self.w_type,
            'phase_function': self.phase_function,
            'phase_g': self.phase_g,
            'max_bounces': self.max_bounces,
        }

    def _draw_buttons(self, context, layout):
        layout.prop(self, 'phase_function')
        if self.phase_function == 'henyey_greenstein':
            layout.prop(self, 'phase_g')
        layout.prop(self, 'max_bounces')

@node.TungstenNodeTree.register_node('Mediums')
class TungstenHomogeneousMediumNode(TungstenMediumNode):
    bl_label = 'Homogeneous'
    w_type = 'homogeneous'

    PROPERTIES = {
        'sigma_a': bpy.props.FloatVectorProperty(
            name='Sigma A',
            description='Sigma A',
            min=0.0,
            default=(0.0, 0.0, 0.0),
        ),
        'sigma_s': bpy.props.FloatVectorProperty(
            name='Sigma S',
            description='Sigma S',
            min=0.0,
            default=(0.0, 0.0, 0.0),
        ),
    }

    def _to_scene_data(self, scene):
        return {
            'sigma_a': list(self.sigma_a),
            'sigma_s': list(self.sigma_s),
        }

    def _draw_buttons(self, context, layout):
        layout.prop(self, 'sigma_a')
        layout.prop(self, 'sigma_s')

def update_use_clouds(self, context):
    inputname = 'Cloud Thickness'
    if self.use_clouds and not inputname in self.inputs:
        self.inputs.new('TungstenTextureSocket', inputname)
        self.inputs[inputname].tex_type = 'VALUE'
    elif not self.use_clouds and inputname in self.inputs:
        self.inputs.remove(self.inputs[inputname])

@node.TungstenNodeTree.register_node('Mediums')
class TungstenAtmosphericMediumNode(TungstenMediumNode):
    bl_label = 'Atmospheric'
    w_type = 'atmosphere'

    PROPERTIES = {
        'pivot': props.ObjectProperty(
            name='Pivot',
            description='Pivot',
        ),
        'background_sigma_s': bpy.props.FloatVectorProperty(
            name='Sigma S',
            description='Sigma S',
            min=0.0,
            default=(0.0, 0.0, 0.0),
        ),
        'use_clouds': bpy.props.BoolProperty(
            name='Clouds',
            description='Use Clouds',
            default=False,
            update=update_use_clouds,
        ),
        'cloud_density': bpy.props.FloatProperty(
            name='Density',
            description='Cloud Density',
            default=1.0,
        ),
        'cloud_albedo': bpy.props.FloatProperty(
            name='Albedo',
            description='Cloud Albedo',
            default=0.9,
        ),
        'cloud_shift': bpy.props.FloatProperty(
            name='Shift',
            description='Cloud Shift',
            default=0.0,
        ),
        'cloud_min_radius': bpy.props.FloatProperty(
            name='Min',
            description='Cloud Min Radius',
            default=0.9,
        ),
        'cloud_max_radius': bpy.props.FloatProperty(
            name='Max',
            description='Cloud Max Radius',
            default=1.0,
        ),
    }

    def _to_scene_data(self, scene):
        d = {
            'background_sigma_s': list(self.background_sigma_s),
        }

        pivot = self.pivot.normalize(self)
        if pivot:
            Rg = 6360.0 * 1e3;
            d['pos'] = list(pivot.matrix_world.translation)
            d['scale'] = Rg / max(pivot.matrix_world.to_scale())

        if self.use_clouds:
            d['cloud_thickness'] = self.inputs['Cloud Thickness'].to_scene_data(scene)
            d['cloud_density'] = self.cloud_density
            d['cloud_albedo'] = self.cloud_albedo
            d['cloud_shift'] = self.cloud_shift
            d['cloud_min_radius'] = self.cloud_min_radius
            d['cloud_max_radius'] = self.cloud_max_radius

        return d

    def _draw_buttons(self, context, layout):
        self.pivot.draw(layout, self)
        layout.prop(self, 'background_sigma_s')
        layout.prop(self, 'use_clouds')
        if self.use_clouds:
            row = layout.row()
            row.prop(self, 'cloud_density')
            row.prop(self, 'cloud_albedo')
            row.prop(self, 'cloud_shift')
            row = layout.row()
            row.prop(self, 'cloud_min_radius')
            row.prop(self, 'cloud_max_radius')
