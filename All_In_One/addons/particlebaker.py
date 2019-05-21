# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Particle Baker",
    "author": "Bassam Kurdali",
    "version": (1, 0),
    "blender": (2, 6, 7),
    "location": "View3D > Specials (W-key)",
    "description": "Make Real Objects from Particles",
    "warning": "",
    "wiki_url": "http://wiki.tube.freefac.org/wiki/Particle_Baker",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import mathutils
from random import random

noanimTypes = (
    int, bool, str, float, list, mathutils.Vector, mathutils.Vector,
    mathutils.Matrix, mathutils.Euler, mathutils.Color, mathutils.Quaternion)

forbidden = [
    'bl_rna', 'library', 'id_data', 'rna_type', 'base', 'relative_key',
    'parent', 'user', 'owner', 'group', 'dupli_group', 'get_from_context',
    'nodes', 'active_material', 'material_slots']

morbidden = ['material_slots']

animstuff = ['animation_data', 'action']


def generic_copy(source, target):
    """ copy attributes from source to target that have string in them """
    for attr in dir(source):
        try:
            setattr(target, attr, getattr(source, attr))
        except:
            pass


def copy_modifiers(source, target):
    """ copy modifiers from source to target """
    for old_modifier in source.modifiers.values():
        new_modifier = target.modifiers.new(
            name=old_modifier.name, type=old_modifier.type)
        generic_copy(old_modifier, new_modifier)


def recursive_copy(path, obj, paths):
    ''' recursively copy an object '''
    attrs = dir(obj)
    for itm in attrs:
        if itm == 'copy' and callable(getattr(obj, itm)):

            paths.append(path)

        elif 'type' not in attrs or ('type' in attrs and obj.type != 'SHADER'):
            if itm not in forbidden and itm not in animstuff and (
                    not itm.startswith('__')):
                subobj = getattr(obj, itm)
                if subobj and (
                        not isinstance(subobj, noanimTypes)) and (
                        not callable(subobj)):
                    recursive_copy('.'.join([path, itm]), subobj, paths)


def anim_from_object(path, obj, actions):
    ''' get all anim_data actions from an object '''
    attrs = dir(obj)
    for itm in attrs:
        if itm == 'animation_data':

            animdata = getattr(obj, itm)
            if animdata:
                action = animdata.action
                if action:
                    actions.append((action, path))

        elif 'type' not in attrs or (
                'type' in attrs and obj.type != 'SHADER'):
            if itm not in forbidden:
                if not itm.startswith('__'):
                    subobj = getattr(obj, itm)
                    if subobj and (
                            not isinstance(subobj, noanimTypes)) and (
                            not callable(subobj)):
                        anim_from_object(
                            '.'.join([path, itm]), subobj, actions)
            elif itm in morbidden:
                subobj = getattr(obj, itm)
                for index, item in enumerate(subobj):
                    anim_from_object(
                        "{}[{}]".format('.'.join([path, itm]), index),
                        item, actions)


def make_objects_from_particles(
        prefix, particles, scene, actions=None,
        reference_object=None, copyables=None):
    '''
    create real objects from particles
    '''
    if reference_object and reference_object.data:
        data = reference_object.data
    else:
        data = None
    real_particles = []
    bpy.context.window_manager.progress_begin(0, len(particles))
    for idx, particle in enumerate(particles):
        bpy.context.window_manager.progress_update(idx)
        myname = "{}.{}".format(prefix, idx)
        if not myname in scene.objects:
            if data:
                mydata = data.copy()
            else:
                mydata = None
            newob = bpy.data.objects.new(name=myname, object_data=mydata)
            scene.objects.link(newob)
        else:
            newob = bpy.data.objects[myname]
            newob.data = data.copy()
        if copyables:
            for copyable in copyables:

                if copyable:
                    holder = "bpy.data.objects['{}']{}".format(
                        newob.name, copyable)
                    idx = holder.rfind('.')
                    parentholder = holder[:idx]
                    attribute = holder[idx + 1:]
                    if attribute not in ['node_tree', 'shape_keys']:
                        holder = eval(holder).copy()
                        try:
                            setattr(eval(parentholder), attribute, holder)
                        except:
                            print("couldn't set attribute", attribute)

            for material_slot in newob.material_slots:
                material_slot.material = material_slot.material.copy()
                try:
                    material_slot.material.node_tree.nodes[
                        'birth_time'].outputs[0].default_value =\
                        particle.birth_time
                except:
                    print('no birth_time')
        newob.location = particle.location
        newob.scale = [particle.size, particle.size, particle.size]
        newob.rotation_mode = 'QUATERNION'
        newob.rotation_quaternion = particle.rotation
        newob.layers = scene.layers
        if reference_object:
            for vgrp in reference_object.vertex_groups:
                newob.vertex_groups.new(name=vgrp.name)
            copy_modifiers(reference_object, newob)

        if actions:
            for action_pair in actions:
                action = action_pair[0]
                new_action = action_pair[0].copy()

                holder = "bpy.data.objects['{}']{}".format(
                    newob.name, action_pair[1])

                holder = eval(holder)
                if not holder.animation_data:
                    holder.animation_data_create()
                holder.animation_data.action = new_action
                actiontime = get_action_limits(action.fcurves)
                lifetime = (particle.birth_time, particle.die_time)
                remap_action_to_life(
                    action.fcurves, new_action.fcurves,
                    actiontime, lifetime)

        newob.hide_render = newob.hide = True
        for frame in (particle.die_time, 0):
            for prop in ('hide', 'hide_render'):
                newob.keyframe_insert(prop, frame=frame)
        newob.hide_render = newob.hide = False
        for prop in ('hide', 'hide_render'):
            newob.keyframe_insert(prop, frame=particle.birth_time)

        real_particles.append(newob)
    bpy.context.window_manager.progress_end()
    return real_particles


def get_action_limits(curves):
    '''
    return maximum and minimum times from a series of fcurves
    '''
    minimum = 20000000000
    maximum = 0
    for fcurve in curves:
        times = [kp.co[0] for kp in fcurve.keyframe_points]
        minimum = min((minimum, min(times)))
        maximum = max((maximum, max(times)))
    return((minimum, maximum))


def particle_anim_to_objects(particles, reals, scene):
    current_frame = scene.frame_current
    for frame in range(scene.frame_start, scene.frame_end):
        scene.frame_set(frame)
        for idx, particle in enumerate(particles):
            reals[idx].location = particle.location
            reals[idx].rotation_quaternion = particle.rotation
            reals[idx].keyframe_insert('location', group='LocRot')
            reals[idx].keyframe_insert('rotation_quaternion', group='LocRot')
    scene.frame_set(current_frame)


def remap_curve_to_life(old_curve, new_curve, actiontime, lifetime):
    '''
    map a single curve to the particle lfetime
    '''
    for keyframe, newframe in zip(
            old_curve.keyframe_points, new_curve.keyframe_points):
        for attr in ['co', 'handle_left', 'handle_right']:
            new_time =\
                lifetime[0] + (lifetime[1] - lifetime[0]) *\
                (getattr(keyframe, attr)[0] - actiontime[0]) /\
                (actiontime[1] - actiontime[0])
            setattr(newframe, attr, (new_time, getattr(newframe, attr)[1]))


def remap_action_to_life(old_curves, new_curves, actiontime, lifetime):
    '''
    map a series of fcurve to a particle
    '''
    for old_curve, new_curve in zip(old_curves, new_curves):
        remap_curve_to_life(old_curve, new_curve, actiontime, lifetime)


def poster_list(self, context):
    ''' enum prop list of possible objects '''
    scene = context.scene
    obj_list = [ob.name for ob in scene.objects if ob.type == 'MESH']
    obj_list.insert(0, '')  # lets have a default of none
    return ([(ob, ob, ob) for ob in obj_list])


def is_intersect(a, b, limits):
    ''' are the particles intersecting '''
    intersect = True
    for idx, limit in enumerate(limits):
        if limit > 0.0001:
            intersect = intersect and abs(
                a.location[idx] - b.location[idx]) < limit
    return intersect


def remove_too_close(keep_list, kill_list, limits):
    for particle in keep_list:
        others = (p for p in keep_list if not p is particle)
        for p in others:
            if is_intersect(p, particle, limits):
                kill_list.append(particle)
                break
        keep_list.remove(particle)


def cull(particles, limits):
    ''' cull too close particles '''
    start_times = [(p.birth_time, p) for p in particles]
    start_times.sort()
    alive_particles = []
    kill_list = []
    for time in start_times:
        alive_particles.append(time[1])
        for particle in alive_particles:
            if particle.die_time < time[0]:
                alive_particles.remove(particle)
        keep_list = [p for p in alive_particles if not p in kill_list]
        remove_too_close(keep_list, kill_list, limits)
    return [p for p in particles if p not in kill_list]


def density_particles(particles, density):
    ''' change the birth rate based on density '''
    reparticles = []
    if type(density) == bpy.types.FCurve:
        for particle in particles:
            if random() <= density.evaluate(particle.birth_time):
                reparticles.append(particle)
    else:
        for particle in particles:
            if random() <= density:
                reparticles.append(particle)

    return reparticles


class BakeParticles(bpy.types.Operator):
    '''Tube Project Errror/Warning checker'''
    bl_idname = "object.bake_particles"
    bl_label = "Make Particles Real"
    bl_options = {'REGISTER', 'UNDO'}
    prefix = bpy.props.StringProperty(name="prefix", default="Player")
    animated_particles = bpy.props.BoolProperty(default=False)
    animated_object = bpy.props.BoolProperty(default=True)
    source_object = bpy.props.EnumProperty(
        items=poster_list)
    cull = bpy.props.BoolProperty(default=False)
    limits = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0))

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.type == 'MESH' and len(ob.particle_systems) > 0

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        props = self.properties
        prefix = props.prefix
        object = props.source_object
        active = context.active_object
        scene = context.scene
        particles = []
        for system in active.particle_systems:
            particles += system.particles
        density = active.particle_density
        if active.animation_data and active.animation_data.action:
            dcurve = [
                curve for curve in active.animation_data.action.fcurves if
                curve.data_path == 'particle_density']
            if dcurve:
                density = dcurve[0]
        particles = density_particles(particles, density)
        if props.cull:
            particles = cull(particles, props.limits)
        actions = []
        copyables = []
        if object in scene.objects:
            reference_object = scene.objects[object]
            obdata = reference_object.data
            if props.animated_object:
                anim_from_object('', scene.objects[object], actions)
                recursive_copy('', scene.objects[object], copyables)
        else:
            copyables = actions = obdata = reference_object = None
        reals = make_objects_from_particles(
            prefix, particles, scene, actions, reference_object, copyables)
        if props.animated_particles:
            particle_anim_to_objects(particles, reals, scene)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        props = self.properties
        row = layout.row()
        row.prop(props, "prefix")
        row.prop(props, "animated_particles", text="particle anim")
        row = layout.row()
        row.prop(props, "source_object")
        row.prop(props, "animated_object", text="use object anim")
        row = layout.row()
        row.prop(props, "cull", text="density cull")
        row.prop(props, "limits", text="density limits")


# Registration

def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator("object.bake_particles")


def my_draw(self, context):
    self.layout.prop(
        context.object, 'particle_density', text="Particle Density")


def register():
    bpy.types.Object.particle_density = bpy.props.FloatProperty(
        default=1.0, max=1.0, min=0.0)
    bpy.types.PARTICLE_PT_emission.append(my_draw)
    bpy.utils.register_class(BakeParticles)
    bpy.types.VIEW3D_MT_object_specials.prepend(menu_func)


def unregister():
    bpy.types.PARTICLE_PT_emission.remove(my_draw)

    bpy.types.VIEW3D_MT_object_specials.remove(menu_func)
    bpy.utils.unregister_class(BakeParticles)
    del(bpy.types.Object.particle_density)

if __name__ == "__main__":
    register()
