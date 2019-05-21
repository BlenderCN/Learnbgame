import bpy, os
from ..extensions_framework import util as efutil

from .. core.util import get_worldscale
from .. export import indigo_log, exportutil, xml_builder

def aspect_ratio(context,p):
    return context.render.resolution_x / context.render.resolution_y

def f_stop(context, p):
    return p.fstop

def lens_sensor_dist(context,p):
    import math
    
    aspect = aspect_ratio(context,p)
    
    film = 0.001 * context.camera.data.sensor_width
    
    FOV = context.camera.data.angle
    if aspect < 1.0:
        FOV = FOV*aspect
    
    lsd = film/( 2.0*math.tan( FOV/2.0 ))
    #print('Lens Sensor Distance: %f'%lsd)
    return lsd

def aperture_radius(context,p):
    ar = lens_sensor_dist(context,p) / (2.0*f_stop(context,p))
    #print('Aperture Radius: %f' % ar)
    return ar

properties = [
    {
        'type': 'bool',
        'attr': 'autofocus',
        'name': 'Auto Focus',
        'description': 'Auto Focus',
        'default': True,
    },
    {
        'type': 'bool',
        'attr': 'vignetting',
        'name': 'Vignetting',
        'description': '',
        'default': True,
    },
    {
        'type': 'bool',
        'attr': 'autoexposure',
        'name': 'Auto Exposure',
        'description': 'Auto Exposure',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'ad',
        'name': 'Aperture Diffraction',
        'description': 'Aperture Diffraction',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'ad_post',
        'name': 'AD Post-Process',
        'description': 'AD Post-Process',
        'default': False,
    },
    {
        'type': 'int',
        'attr': 'iso',
        'name': 'Film ISO',
        'description': 'Film ISO',
        'default': 100,
        'min': 25,
        'soft_min': 25,
        'max': 10000,
        'soft_max': 10000,
    },
    {
        'type': 'float',
        'attr': 'exposure',
        'name': 'Exposure 1/',
        'description': 'Exposure 1/',
        'default': 125,
        'min': 0.001,
        'soft_min': 0.001,
        'max': 8000,
        'soft_max': 8000,
        'compute': lambda c, self: 1 / self.exposure
    },
    {
        'type': 'float',
        'attr': 'fstop',
        'name': 'f/Stop',
        'description': 'f/Stop',
        'default': 8,
        'min': 1,
        'soft_min': 1,
        'max': 128,
        'soft_max': 128,
    },
    {
        'type': 'enum',
        'attr': 'whitebalance',
        'name': 'White Balance',
        'description': 'White Balance Standard',
        'items': [
            ('E','E','E'),
            ('D50','D50','D50'),
            ('D55','D55','D55'),
            ('D65','D65','D65'),
            ('D75','D75','D75'),
            ('A','A','A'),
            ('B','B','B'),
            ('C','C','C'),
            ('9300','9300','9300'),
            ('F2','F2','F2'),
            ('F7','F7','F7'),
            ('F11','F11','F11'),
            ('Custom','Custom','Custom'),
        ],
    },
    {
        'type': 'float',
        'attr': 'whitebalanceX',
        'name': 'X',
        'description': 'Whitebalance X',
        #'slider': True,
        'precision': 5,
        'default': 0.33333,
        'min': 0.1,
        'soft_min': 0.1,
        'max': 0.5,
        'soft_max': 0.5,
    },
    {
        'type': 'float',
        'attr': 'whitebalanceY',
        'name': 'Y',
        'description': 'Whitebalance Y',
        #'slider': True,
        'precision': 5,
        'default': 0.33333,
        'min': 0.1,
        'soft_min': 0.1,
        'max': 0.5,
        'soft_max': 0.5,
    },
    {
        'type': 'bool',
        'attr': 'motionblur',
        'name': 'Camera MB',
        'description': 'Enable Camera Motion Blur',
        'default': False
    },
    {
        'type': 'enum',
        'attr': 'ad_type',
        'name': 'AD Type',
        'description': 'Aperture Diffraction Type',
        'items': [
            ('image', 'Image', 'image'),
            ('generated', 'Generated', 'generated'),
            ('circular', 'Circular', 'circular'),
        ],
    },
    {
        'type': 'int',
        'attr': 'ad_blades',
        'name': 'Blades',
        'description': 'Number of blades in the aperture',
        'default': 5,
        'min': 3,
        'soft_min': 3,
        'max': 20,
        'soft_max': 20,
    },
    {
        'type': 'float',
        'attr': 'ad_offset',
        'name': 'Offset',
        'description': 'Aperture blade offset',
        'default': 0.4,
        'min': 0,
        'soft_min': 0,
        'max': 0.5,
        'soft_max': 0.5,
    },
    {
        'type': 'int',
        'attr': 'ad_curvature',
        'name': 'Curvature',
        'description': 'Aperture blade curvature',
        'default': 3,
        'min': 0,
        'soft_min': 0,
        'max': 10,
        'soft_max': 10,
    },
    {
        'type': 'float',
        'attr': 'ad_angle',
        'name': 'Angle',
        'description': 'Aperture blade angle',
        'default': 0.2,
        'min': 0,
        'soft_min': 0,
        'max': 2,
        'soft_max': 2,
    },
    {
        'type': 'string',
        'attr': 'ad_image',
        'name': 'Image',
        'description': 'Image to use as the aperture opening. Must be power of two square, >= 512',
        'subtype': 'FILE_PATH',
    },
    {
        'type': 'string',
        'attr': 'ad_obstacle',
        'name': 'Obstacle Map',
        'description': 'Image to use as the aperture obstacle map. Must be power of two square, >= 512',
        'subtype': 'FILE_PATH',
    },
]

from .. import export
from .. core.util import PlatformInformation, getInstallPath
from . import register_properties_dict
@register_properties_dict
class Indigo_Camera_Properties(bpy.types.PropertyGroup, export.xml_builder):
    properties = properties
    
    # xml_builder members
    def build_xml_element(self, scene, matrix_list):
        xml = self.Element('camera')
        
        xml_format = {
            'aperture_radius': [aperture_radius(scene, self)],
            'sensor_width': [scene.camera.data.sensor_width / 1000.0],
            'lens_sensor_dist': [lens_sensor_dist(scene, self)],
            'aspect_ratio': [aspect_ratio(scene, self)],
            'exposure_duration': 'exposure',
        }
        
        if self.whitebalance == 'Custom':
            xml_format['white_point'] = {
                'chromaticity_coordinates': {
                    'x': [self.whitebalanceX],
                    'y': [self.whitebalanceY],
                }
            }
        else:
            xml_format['white_balance'] = 'whitebalance',
        
        ws = get_worldscale(scene)
        
        if(scene.camera.data.type == 'ORTHO'):
            xml_format['camera_type'] = ['orthographic']
            xml_format['sensor_width'] = [scene.camera.data.ortho_scale * ws] # Blender seems to use 'ortho_scale' for the sensor width.
        
        mat = matrix_list[0][1].transposed()
        
        xml_format['pos']        = [ i*ws for i in mat[3][0:3]]
        xml_format['forwards']    = [-i*ws for i in mat[2][0:3]]
        xml_format['up']        = [ i*ws for i in mat[1][0:3]]
        
        if len(matrix_list) > 1:
            # Remove pos, conflicts with keyframes.
            del(xml_format['pos'])
        
            keyframes = exportutil.matrixListToKeyframes(scene, scene.camera, matrix_list)
                
            xml_format['keyframe'] = tuple(keyframes)
        
        if self.autofocus:
            xml_format['autofocus'] = '' # is empty element
            xml_format['focus_distance'] = [10.0]  # any non-zero value will do
        else:
            if scene.camera.data.dof_object is not None:
                xml_format['focus_distance'] = [((scene.camera.matrix_world.translation - scene.camera.data.dof_object.matrix_world.translation).length*ws)]
            elif scene.camera.data.dof_distance > 0:
                xml_format['focus_distance'] = [scene.camera.data.dof_distance*ws]
            else: #autofocus
                xml_format['autofocus'] = '' # is empty element
                xml_format['focus_distance'] = [10.0]  # any non-zero value will do
        
        if self.ad:
            xml_format.update({
                'aperture_shape': {}
            })
            if self.ad_obstacle != '':
                ad_obstacle = efutil.filesystem_path(self.ad_obstacle)
                if os.path.exists(ad_obstacle):
                    xml_format.update({
                        'obstacle_map': {
                            'path': [efutil.path_relative_to_export(ad_obstacle)]
                        }
                    })
                else:
                    indigo_log('WARNING: Camera Obstacle Map specified, but image path is not valid')
            
            if self.ad_type == 'image':
                ad_image = efutil.filesystem_path(self.ad_image)
                if os.path.exists(ad_image):
                    xml_format['aperture_shape'].update({
                        'image': {
                            'path': [efutil.path_relative_to_export(ad_image)]
                        }
                    })
                else:
                    indigo_log('WARNING: Camera Aperture Diffraction type "Image" selected, but image path is not valid')
            
            elif self.ad_type == 'generated':
                xml_format['aperture_shape'].update({
                    'generated': {
                        'num_blades': [self.ad_blades],
                        'start_angle': [self.ad_angle],
                        'blade_offset': [self.ad_offset],
                        'blade_curvature_radius': [self.ad_curvature]
                    }
                })
            elif self.ad_type == 'circular':
                xml_format['aperture_shape'][self.ad_type] = {}
        
        aspect = aspect_ratio(scene, self)
        if scene.camera.data.shift_x != 0:
            sx = scene.camera.data.shift_x * 0.001*scene.camera.data.sensor_width
            if aspect < 1.0:
                sx /= aspect
            xml_format['lens_shift_right_distance'] = [sx]
            
        if scene.camera.data.shift_y != 0:
            sy = scene.camera.data.shift_y * 0.001*scene.camera.data.sensor_width
            if aspect < 1.0:
                sy /= aspect
            xml_format['lens_shift_up_distance'] = [sy]
        
        self.build_subelements(scene, xml_format, xml)
        
        return xml
    
