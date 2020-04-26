import bpy
import math
from bl_ui import properties_data_camera

from . import base
from .texture import TextureProperty

base.compatify_class(properties_data_camera.DATA_PT_context_camera)
base.compatify_class(properties_data_camera.DATA_PT_camera_display)
base.compatify_class(properties_data_camera.DATA_PT_custom_props_camera)

@base.register_root_panel
class W_PT_camera(properties_data_camera.CameraButtonsPanel, base.RootPanel):
    bl_label = "Tungsten Camera"
    prop_class = bpy.types.Camera

    @classmethod
    def get_object(cls, context):
        return context.camera

    PROPERTIES = {
        'type': bpy.props.EnumProperty(
            name='Type',
            description='Camera Type',
            items=[
                ('pinhole', 'Pinhole', ''),
                ('thinlens', 'Thin Lens', ''),
            ],
            default='pinhole',
        ),
        
        'tonemap': bpy.props.EnumProperty(
            name='Tonemap',
            description='Tonemap',
            items=[
                ('linear', 'Linear Only', ''),
                ('gamma', 'Gamma Only', ''),
                ('reinhard', 'Reinhard', ''),
                ('filmic', 'Filmic', ''),
            ],
            default='filmic',
        ),

        'reconstruction_filter': bpy.props.EnumProperty(
            name='Filter',
            description='Reconstruction Filter',
            items=[
                ('dirac', 'Dirac', ''),
                ('box', 'Box', ''),
                ('tent', 'Tent', ''),
                ('gaussian', 'Gaussian', ''),
                ('mitchell_netravali', 'Mitchell-Netravali', ''),
                ('catmull_rom', 'Catmull-Rom', ''),
                ('lanczos', 'Lanczos', ''),
            ],
            default='tent',
        ),
    }

    @classmethod
    def to_scene_data(self, scene, obj):
        cam = obj.data
        w = cam.tungsten
        rf = w.reconstruction_filter
        d = {
            'type': w.type,
            'tonemap': w.tonemap,
            'fov': math.degrees(cam.angle),
            'reconstruction_filter': rf,
        }

        if d['type'] == 'thinlens':
            # FIXME camera props need object, and obj.tungsten.type
            # does not exist!
            d.update(W_PT_thinlens.to_scene_data(scene, obj))
        #d.update(super().to_scene_data(scene, obj))
        return d

    def draw_for_object(self, cam):
        layout = self.layout
        w = cam.tungsten

        layout.prop(w, 'type', expand=True)
        layout.prop(w, 'tonemap', expand=True)
        row = layout.row(align=True)
        if cam.lens_unit != 'FOV':
            row.prop(cam, 'lens')
        else:
            row.prop(cam, 'angle')
        row.prop(cam, 'lens_unit', text="")

        row = layout.row(align=True)
        row.prop(w, 'reconstruction_filter')

        # Tungsten doesn't use these, but blender's GL view does
        row = layout.row(align=True)
        row.label('Clipping:')
        row.prop(cam, 'clip_start', text='')
        row.prop(cam, 'clip_end', text='')

@base.register_sub_panel
class W_PT_thinlens(W_PT_camera.SubPanel):
    bl_label = "Thin Lens"
    w_type = 'thinlens'

    PROPERTIES = {
        'aperture_size': bpy.props.FloatProperty(
            name='Aperture Size',
            description='Aperture Size',
            min=0,
            default=0.001,
            subtype='DISTANCE',
            unit='LENGTH',
        ),
        
        'aberration': bpy.props.FloatProperty(
            name='Aberration',
            description='Chromatic Aberration',
            min=0,
            soft_max=10,
            default=0,
            subtype='UNSIGNED',
        ),
        
        'cateye': bpy.props.FloatProperty(
            name='Cateye',
            description='Cateye',
            min=0,
            soft_max=10,
            default=0,
            subtype='UNSIGNED',
        ),
        
        'aperture': TextureProperty(
            name='Aperture',
            description='Aperture',
        ),
    }

    @classmethod
    def to_scene_data(cls, scene, obj):
        cam = obj.data
        
        dof_distance = cam.dof_distance
        if cam.dof_object:
            l1 = obj.matrix_world.translation
            l2 = cam.dof_object.matrix_world.translation
            dof_distance = math.sqrt(sum([(a - b)**2 for a, b in zip(l1, l2)]))

        w = cam.tungsten
        d = {
            'aperture_size': w.aperture_size,
            'aberration': w.aberration,
            'cateye': w.cateye,
            'focus_distance': dof_distance,
        }

        t = w.aperture.to_scene_data(scene, w)
        if t:
            d['aperture'] = t

        return d

    def draw_for_object(self, cam):
        layout = self.layout
        w = cam.tungsten
        
        row = layout.row(align=True)
        row.prop(w, 'aperture_size', text='Aperture')
        w.aperture.draw(row, w, text='')
        
        layout.prop(w, 'aberration')
        layout.prop(w, 'cateye')
        layout.label('Focus:')
        row = layout.row()
        row.prop(cam, 'dof_object', text='')
        sub = row.row()
        sub.enabled = not bool(cam.dof_object)
        sub.prop(cam, 'dof_distance', text='Distance')
