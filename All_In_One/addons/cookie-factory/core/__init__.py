# ##### BEGIN LGPL LICENSE BLOCK #####
#
#  Copyright (C) 2018 Nikolai Janakiev
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this library; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END LGPL LICENSE BLOCK #####


from . import geometry
from . import materials
from . import scene

import bpy
import bmesh
from mathutils import Color
from math import sin
import logging

logger = logging.getLogger(__name__)


# map, constrain from: https://github.com/processing/processing/blob/master/core%2Fsrc%2Fprocessing%2Fcore%2FPApplet.java
def map_range(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

def constrain(t, a, b):
    return (t if a < t else a) if t < b else b

def sin_range(phi, a, b):
    return (0.5*sin(phi) + 0.5)*(b - a) + a


def track_to_constraint(obj, name, target, track_axis='TRACK_NEGATIVE_Z', up_axis='UP_Y', owner_space='LOCAL', target_space='LOCAL'):
    cns = obj.constraints.new('TRACK_TO')
    cns.name = name
    cns.target = target
    cns.track_axis = track_axis
    cns.up_axis = up_axis
    cns.owner_space = owner_space
    cns.target_space = target_space


def empty(location=(0,0,0)):
    empty = bpy.data.objects.new('Empty', None)
    empty.location = location
    bpy.context.scene.objects.link(empty)
    return empty


def camera(location, target=None, lens=35, clip_start=0.1, clip_end=200):
    # Create object and camera
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    cam.clip_start = clip_start
    cam.clip_end = clip_end
    obj = bpy.data.objects.new("CameraObj", cam)
    obj.location = location
    # Link object to scene
    bpy.context.scene.objects.link(obj)

    if target: track_to_constraint(obj, 'TrackConstraint', target)

    # Make this the current camera
    bpy.context.scene.camera = obj
    return obj


def lamp(location, type='POINT', energy=1, color=(1,1,1), target=None):
    # Lamp types: 'POINT', 'SUN', 'SPOT', 'HEMI', 'AREA'
    lamp = bpy.data.lamps.new('Lamp', type=type)
    lamp.energy = energy
    lamp.color = color

    obj = bpy.data.objects.new("CameraObj", lamp)
    obj.location = location
    bpy.context.scene.objects.link(obj)

    if target: track_to_constraint(obj, 'TrackConstraint', target)
    return obj


def simple_scene(target_location, camera_location, sun_location, lens=35):
    target = empty(target_location)
    cam    = camera(camera_location, target, lens)
    sun    = lamp(sun_location, 'SUN', target=target)

    return target, cam, sun


def recalc_face_normals(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()


def smooth_object(obj, smooth=True, subsurf=False, levels=2, render_levels=3):
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = smooth

    if subsurf:
        modifier = obj.modifiers.new('Subsurf', 'SUBSURF')
        modifier.levels = levels
        modifier.render_levels = render_levels


def edge_split(obj, use_edge_angle=True, use_edge_sharp=True, split_angle=0.5236):
    modifier = obj.modifiers.new('EdgeSplit', 'EDGE_SPLIT')
    modifier.use_edge_angle = use_edge_angle
    modifier.use_edge_sharp = use_edge_sharp
    modifier.split_angle = split_angle


def remove_object(obj):
    if obj.type == 'MESH':
        if obj.data.name in bpy.data.meshes:
            bpy.data.meshes.remove(obj.data)
        if obj.name in bpy.context.scene.objects:
            bpy.context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    else:
        raise NotImplementedError('Other types not implemented yet besides \'MESH\'')


def remove_all(type=None):
    # Possible type: ‘MESH’, ‘CURVE’, ‘SURFACE’, ‘META’, ‘FONT’, ‘ARMATURE’, ‘LATTICE’, ‘EMPTY’, ‘CAMERA’, ‘LAMP’
    if type:
        if type == 'MESH':
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    if obj.name in bpy.context.scene.objects:
                        bpy.context.scene.objects.unlink(obj)
                    bpy.data.objects.remove(obj)
            for mesh in bpy.data.meshes:
                bpy.data.meshes.remove(mesh)
        elif type == 'CURVE':
            for obj in bpy.data.objects:
                if obj.type == 'CURVE':
                    if obj.name in bpy.context.scene.objects:
                        bpy.context.scene.objects.unlink(obj)
                    bpy.data.objects.remove(obj)
            for curve in bpy.data.curves:
                bpy.data.curves.remove(curve)
        else:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_by_type(type=type)
            bpy.ops.object.delete()
    else:
        # Remove all elements in scene
        for obj in bpy.data.objects:
            if obj.name in bpy.context.scene.objects:
                bpy.context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)

        for mesh in bpy.data.meshes:     bpy.data.meshes.remove(mesh)
        for lamp in bpy.data.lamps:      bpy.data.lamps.remove(lamp)
        for cam in bpy.data.cameras:     bpy.data.cameras.remove(cam)
        for mat in bpy.data.materials:   bpy.data.materials.remove(mat)
        for tex in bpy.data.textures:    bpy.data.textures.remove(tex)
        for curve in bpy.data.curves:    bpy.data.curves.remove(curve)


def world_settings(ao=False, samples=5, blend_type='ADD', horizon_color=(0.051, 0.051, 0.051), use_mist=False):
    # TODO reset all world settings
    bpy.context.scene.world.light_settings.use_ambient_occlusion = ao
    bpy.context.scene.world.light_settings.ao_blend_type = blend_type
    bpy.context.scene.world.light_settings.samples = samples
    bpy.context.scene.world.mist_settings.use_mist = use_mist
    bpy.context.scene.world.horizon_color = horizon_color


def ambient_occlusion(ambient_occulusion=True, samples=5, blend_type = 'ADD'):
    # blend_type options: 'ADD', 'MULTIPLY'
    bpy.context.scene.world.light_settings.use_ambient_occlusion = ambient_occulusion
    bpy.context.scene.world.light_settings.ao_blend_type = blend_type
    bpy.context.scene.world.light_settings.samples = samples


def background_color(horizon_color=(0.051, 0.051, 0.051), zenith_color=(0.01, 0.01, 0.01), ambient_color=(0,0,0), paper_sky=True, blend_sky=False, real_sky=False):
    # Horizon Color: RGB color at the horizon
    # Zenith Color : RGB color at the zenith (overhead)
    scn = bpy.context.scene
    scn.world.horizon_color = horizon_color
    scn.world.zenith_color  = zenith_color
    scn.world.ambient_color = ambient_color

    # horizon is clipped in the image
    scn.world.use_sky_paper = paper_sky
    # background color is blended from horizon to zenith
    scn.world.use_sky_blend = blend_sky
    # gradient has two transitions: nadir to horizon to zenith
    scn.world.use_sky_real  = real_sky


def background_color_HSV(horizon_color=(0.0, 0.0, 0.051), zenith_color=(0, 0, 0.01), ambient_color=(0,0,0), paper_sky=True, blend_sky=False, real_sky=False):
    h, z, a = Color(), Color(), Color()
    h.hsv = horizon_color
    z.hsv = zenith_color
    a.hsv = ambient_color
    background(h, z, a, paper_sky, blend_sky, real_sky)


def cycles(cycles=True):
    if(cycles):
        bpy.context.scene.render.engine = 'CYCLES'
    else:
        bpy.context.scene.render.engine = 'BLENDER_RENDER'


def shadow_plane(location=(0,0,0), size=10):
    bpy.ops.mesh.primitive_plane_add(radius=size, location=location)
    obj = bpy.context.object

    mat = bpy.data.materials.new("OnlyShadowMaterial")
    mat.use_transparency = True
    mat.use_only_shadow = True

    obj.data.materials.append(mat)

    return obj


def mist(intensity=0, start=5, depth=25, height=0, falloff='QUADRATIC', mist=True):
    # Falloff options: 'QUADRATIC', 'LINEAR', 'INVERSE_QUADRATIC'
    bpy.context.scene.world.mist_settings.use_mist = mist
    bpy.context.scene.world.mist_settings.intensity = intensity
    bpy.context.scene.world.mist_settings.start = start
    bpy.context.scene.world.mist_settings.depth = depth
    bpy.context.scene.world.mist_settings.height = height
    bpy.context.scene.world.mist_settings.falloff = falloff


def shapekey_animation(obj, data, verbose=False):
    # modified from http://blender.stackexchange.com/questions/36902/how-to-keyframe-mesh-vertices-in-python
    for i_frame in range(bpy.context.scene.frame_end):
        if(verbose): logger.debug("Shapekey for frame %i" % (i_frame + 1))

        block = obj.shape_key_add(name=str(i_frame), from_mix=False)  # returns a key_blocks member
        block.value = 1.0
        block.mute = True

        # Iterate for each frame
        for (vert, co) in zip(block.data, data[i_frame]):
            vert.co = co

        # keyframe off on frame zero
        block.mute = True
        block.keyframe_insert(data_path='mute', frame=0, index=-1)

        block.mute = False
        block.keyframe_insert(data_path='mute', frame=i_frame + 1, index=-1)

        block.mute = True
        block.keyframe_insert(data_path='mute', frame=i_frame + 2, index=-1)


def gamma_correction(color, is256=False):
    if is256:
        return tuple(pow(float(c)/255, 2.2) for c in color)
    else:
        return tuple(pow(c, 2.2) for c in color)


def render_stamp(text, detailed=False, foreground=(0, 0, 0, 1), background=(1, 1, 1, 0), font_size=10):
    scn = bpy.context.scene
    scn.render.use_stamp       = True
    scn.render.use_stamp_note  = True
    scn.render.stamp_note_text = text
    scn.render.stamp_font_size = font_size

    # Settings for all the elements which should be displayed
    scn.render.use_stamp_camera          = False
    scn.render.use_stamp_time            = False
    scn.render.use_stamp_scene           = False
    scn.render.use_stamp_filename        = False
    scn.render.use_stamp_frame           = False
    scn.render.use_stamp_lens            = False
    scn.render.use_stamp_marker          = False
    scn.render.use_stamp_sequencer_strip = False
    scn.render.use_stamp_date            = detailed
    scn.render.use_stamp_render_time     = detailed

    # Color settings, add alpha value if missing
    if(len(foreground) == 3): foreground = tuple(foreground) + (1,)
    if(len(background) == 3): background = tuple(background) + (0,)

    scn.render.stamp_foreground = foreground
    scn.render.stamp_background = background
