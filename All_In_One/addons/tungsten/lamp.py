import bpy
import math
from mathutils import Matrix, Vector
from bl_ui import properties_data_lamp

from . import base

base.compatify_class(properties_data_lamp.DATA_PT_context_lamp)
base.compatify_class(properties_data_lamp.DATA_PT_preview)
base.compatify_class(properties_data_lamp.DATA_PT_custom_props_lamp)

# used to flip -y to +y (and also -x to +x to preserve det == 1)
mf = Matrix.Scale(-1, 4, Vector((0, 1, 0)))
mf *= Matrix.Scale(-1, 4, Vector((1, 0, 0)))

def get_lamp_for_w(w):
    for lamp in bpy.data.lamps:
        if lamp.tungsten == w:
            return lamp
    raise RuntimeError('could not find lamp for w')

# keep the size up to date with diameter
def update_diameter(self, context):
    lamp = get_lamp_for_w(self)
    lamp.size = self.diameter

@base.register_root_panel
class W_PT_lamp(properties_data_lamp.DataButtonsPanel, base.RootPanel):
    bl_label = "Tungsten Lamp"
    prop_class = bpy.types.Lamp

    @classmethod
    def get_object(cls, context):
        return context.lamp

    @classmethod
    def get_object_type(cls, obj):
        return obj.type

    PROPERTIES = {
        'emission': bpy.props.FloatVectorProperty(
            name='Emission',
            description='Emission',
            subtype='COLOR',
            min=0.0,
            soft_max=1.0,
            default=(100000, 100000, 100000),
        ),

        # used in a few specialties
        'diameter': bpy.props.FloatProperty(
            name='Diameter',
            description='Diameter or Size',
            min=0,
            default=0.1,
            subtype='DISTANCE',
            unit='LENGTH',
            update=update_diameter,
        ),
    }

    @classmethod
    def to_scene_data(self, scene, lamp):
        w = lamp.tungsten
        d = {
            'bsdf': {'type': 'null'},
            'emission': list(w.emission),
        }
        d.update(super().to_scene_data(scene, lamp))
        return d

    def draw_for_object(self, lamp):
        layout = self.layout
        w = lamp.tungsten

        layout.prop(lamp, 'type', expand=True)
        layout.prop(w, 'emission')

@base.register_sub_panel
class W_PT_lamp_point(W_PT_lamp.SubPanel):
    bl_label = "Point"
    w_type = 'POINT'

    @classmethod
    def to_scene_data(self, scene, lamp):
        w = lamp.tungsten
        return {
            'type': 'sphere',
            'transform': Matrix.Scale(w.diameter / 2, 4),
        }

    def draw_for_object(self, lamp):
        layout = self.layout
        w = lamp.tungsten

        layout.prop(w, 'diameter')

@base.register_sub_panel
class W_PT_lamp_sun(W_PT_lamp.SubPanel):
    bl_label = "Sun"
    w_type = 'SUN'

    PROPERTIES = {
        'sun_sample': bpy.props.BoolProperty(
            name='Sample',
            description='Do Sample',
            default=True,
        ),

        'sun_angle': bpy.props.FloatProperty(
            name='Angle',
            description='Sun Angle (diameter)',
            subtype='ANGLE',
            min=0,
            max=2 * math.pi,
            default=(1/18) * math.pi,
        ),
    }

    @classmethod
    def to_scene_data(self, scene, lamp):
        w = lamp.tungsten
        return {
            'type': 'infinite_sphere_cap',
            'sample': w.sun_sample,
            # blender canonically uses diameters, tungsten uses radius
            'cap_angle': math.degrees(w.sun_angle) / 2,
        }

    def draw_for_object(self, lamp):
        layout = self.layout
        w = lamp.tungsten

        layout.prop(w, 'sun_sample')
        layout.prop(w, 'sun_angle')

@base.register_sub_panel
class W_PT_lamp_spot(W_PT_lamp.SubPanel):
    bl_label = "Spot"
    w_type = 'SPOT'

    @classmethod
    def to_scene_data(self, scene, lamp):
        w = lamp.tungsten
        return {
            'type': 'disk',
            'transform': Matrix.Scale(w.diameter / 2, 4) * mf,
            # blender uses a diameter, tungsten a radius
            'cone_angle': math.degrees(lamp.spot_size) / 2,
        }

    def draw_for_object(self, lamp):
        layout = self.layout
        w = lamp.tungsten

        layout.prop(w, 'diameter')
        layout.prop(lamp, 'spot_size')
        layout.prop(lamp, 'show_cone')

@base.register_sub_panel
class W_PT_lamp_hemi(W_PT_lamp.SubPanel):
    bl_label = "Hemi"
    w_type = 'HEMI'

    PROPERTIES = {
        'hemi_sample': bpy.props.BoolProperty(
            name='Sample',
            description='Do Sample',
            default=True,
        ),

        'hemi_temperature': bpy.props.FloatProperty(
            name='Temperature',
            description='Temperature (K)',
            min=0,
            default=5777,
        ),

        'hemi_gamma_scale': bpy.props.FloatProperty(
            name='Gamma Scale',
            description='Gamma Scale',
            min=0,
            default=1,
        ),

        'hemi_turbidity': bpy.props.FloatProperty(
            name='Turbidity',
            description='Turbidity',
            min=0,
            default=3,
        ),

        'hemi_intensity': bpy.props.FloatProperty(
            name='Intensity',
            description='Intensity',
            min=0,
            default=2,
        ),
    }

    @classmethod
    def to_scene_data(self, scene, lamp):
        w = lamp.tungsten
        return {
            'type': 'skydome',
            'sample': w.hemi_sample,
            'temperature': w.hemi_temperature,
            'gamma_scale': w.hemi_gamma_scale,
            'turbidity': w.hemi_turbidity,
            'intensity': w.hemi_intensity,
        }

    def draw_for_object(self, lamp):
        layout = self.layout
        w = lamp.tungsten

        layout.prop(w, 'hemi_sample')
        layout.prop(w, 'hemi_temperature')
        layout.prop(w, 'hemi_gamma_scale')
        layout.prop(w, 'hemi_turbidity')
        layout.prop(w, 'hemi_intensity')

def update_area_type(self, context):
    lamp = get_lamp_for_w(self)
    lamp.shape = 'SQUARE' if self.area_type == 'CIRCLE' else self.area_type

@base.register_sub_panel
class W_PT_lamp_area(W_PT_lamp.SubPanel):
    bl_label = "Area"
    w_type = 'AREA'

    PROPERTIES = {
        'area_type': bpy.props.EnumProperty(
            name='Type',
            description='Area Type',
            items=[
                ('SQUARE', 'Square', ''),
                ('RECTANGLE', 'Rectangle', ''),
                ('CIRCLE', 'Circle', ''),
            ],
            default='SQUARE',
            update=update_area_type,
        )
    }

    @classmethod
    def to_scene_data(self, scene, lamp):
        w = lamp.tungsten
        if w.area_type == 'SQUARE':
            return {
                'type': 'quad',
                'transform': Matrix.Scale(w.diameter, 4),
            }
        elif w.area_type == 'RECTANGLE':
            mx = Matrix.Scale(w.diameter, 4, Vector((1, 0, 0)))
            my = Matrix.Scale(lamp.size_y, 4, Vector((0, 0, 1)))
            return {
                'type': 'quad',
                'transform': mx * my,
            }
        elif w.area_type == 'CIRCLE':
            return {
                'type': 'disk',
                'transform': Matrix.Scale(w.diameter / 2, 4) * mf,
                'cone_angle': 90,
            }

    def draw_for_object(self, lamp):
        layout = self.layout
        w = lamp.tungsten

        layout.prop(w, 'area_type', expand=True)

        if w.area_type == 'SQUARE':
            layout.prop(w, 'diameter', text='Size')
        elif w.area_type == 'RECTANGLE':
            row = layout.row()
            row.prop(w, 'diameter', text='Size X')
            row.prop(lamp, 'size_y')
        elif w.area_type == 'CIRCLE':
            layout.prop(w, 'diameter')
