import bpy
from .mesh import convert_mesh
from .phy_mesh import convert_phy_mesh
from .animation import get_animation_data_strips
from .material import get_pass_of_material
from . import mesh_hash
from . import progress
from json import dumps, loads
from collections import defaultdict
import os
import re
from math import *
from pprint import pprint

def ob_to_json(ob, scn, used_data, export_pose=True):
    progress.add()
    scn = scn or [scn for scn in bpy.data.scenes if ob.name in scn.objects][0]
    data = {}
    game_properties = {}
    dimensions = list(ob.dimensions) # to be modified in some cases

    #print(ob.type,ob.name)
    obtype = ob.type
    obname = ob.name
    ob_anim_data = ob.animation_data

    if obtype=='MESH' or obtype == 'FONT':
        if obtype == 'FONT':
            nob = bpy.data.objects.new('', ob.to_mesh(scn, True, 'PREVIEW'))
            scn.objects.link(nob)
            for attr in ('location', 'rotation_euler', 'rotation_quaternion',
                'parent', 'matrix_parent_inverse', 'scale', 'color',
                'rotation_mode'):
                    setattr(nob, attr, getattr(ob, attr))
            for k,v in ob.items():
                nob[k] = v
            ob = nob
        generate_tangents = any([used_data['material_use_tangent'][m.material.name] for m in ob.material_slots if m.material])
        def convert(ob, sort, is_phy=False):
            hash = mesh_hash.mesh_hash(ob, used_data, [sort, generate_tangents, is_phy])
            mesh_cache = scn['game_tmp_path'] + hash + '.mesh'
            metadata_cache = scn['game_tmp_path'] + hash + '.json'
            if not os.path.isfile(mesh_cache):
                progress.add()
                if not is_phy:
                    split_parts = len(ob.data.vertices)//64000 + 1 # first approximation
                    export_data = None
                    while not export_data:
                        export_data = convert_mesh(ob, scn, hash, split_parts, sort, generate_tangents)
                        if split_parts > 10:
                            raise Exception("Mesh "+ob.name+" is too big.")
                        split_parts += 1
                else:
                    export_data = convert_phy_mesh(ob)
                open(metadata_cache,'wb').write(dumps(export_data).encode())
            else:
                export_data = loads(open(metadata_cache,'rb').read().decode())
            scn['exported_meshes'][hash] = mesh_cache
            # Calculate materials and passes
            materials = []
            passes = []
            for i in export_data.get('material_indices', []):
                name = 'EMPTY_MATERIAL_SLOT'
                pass_ = 0
                if i < len(ob.material_slots) and ob.material_slots[i].material:
                    mat = ob.material_slots[i].material
                    name = mat.name
                    pass_ = get_pass_of_material(mat, scn)
                materials.append(name)
                passes.append(pass_)
            del export_data['material_indices']
            export_data['materials'] = materials
            export_data['passes'] = passes or [0]
            return export_data

        print('\nExporting object', ob.name)
        data = convert(ob, sort=bool(ob.get('sort_mesh', True)))
        tri_count = data.get('tri_count', 0)

        if data['can_add_lod']:
            # lod_level_data contains:
            #    [
            #        {factor: 0.20,
            #         hash: 'abcdef',
            #         offsets, uv_multiplier, shape_multiplier}, ...
            #    ]
            # Will be sorted by factor (ratio between original and new tri count)

            lod_level_data = []

            #Exporting lod, phy, embed from modifiers

            lod_modifiers = []
            phy_modifier = None
            embed_modifiers = []

            for m in ob.modifiers:
                if m.type == 'DECIMATE':
                    # Separates modifier names by words and checks
                    # if any of the words is "lod", "phy" or "embed"
                    words = re.sub('[^a-zA-Z]', '.', m.name).split('.')
                    if 'lod' in words:
                        m.show_viewport = False
                        lod_modifiers.append(m)
                    if 'phy' in words:
                        phy_modifier = m
                    if 'embed' in words:
                        embed_modifiers.append(m)

            for m in lod_modifiers:
                m.show_viewport = True
                lod_data = convert(ob, True)
                lod_data['factor'] = lod_data['tri_count']/tri_count
                lod_level_data.append(lod_data)
                if m == phy_modifier:
                    print("This LoD mesh will be used as phy_mesh")
                    data['phy_mesh'] = lod_data
                if m in embed_modifiers:
                    scn['embed_mesh_hashes'][lod_data['hash']] = True
                    embed_modifiers.remove(m)
                m.show_viewport = False

            if phy_modifier and not phy_modifier in lod_modifiers:
                phy_modifier.show_viewport = True
                phy_mesh_data = convert(ob, True, True)
                print('Exported phy mesh with factor:', phy_mesh_data['tri_count']/tri_count)
                if phy_modifier in embed_modifiers:
                    scn['embed_mesh_hashes'][phy_mesh_data['hash']] = True
                    embed_modifiers.remove(m)
                phy_modifier.show_viewport = False

            if embed_modifiers:
                print('TODO! Embed mesh modifier without being LoD or Phy')

            data['lod_levels'] = sorted(lod_level_data, key=lambda e: e['factor'])
        else:
            print("Note: Not trying to export LoD levels")
        # end if data['can_add_lod']
        del data['can_add_lod']

        if not 'zindex' in ob:
            ob['zindex'] = 1
        data['zindex'] = ob['zindex']

        if hasattr(ob, 'probe_type'):
            data['material_defines'] = material_defines = {}
            # follow the probe chain to handle defines
            real_probe_ob = ob
            while real_probe_ob and real_probe_ob.probe_type == 'OBJECT'\
                    and real_probe_ob.probe_object:
                real_probe_ob = real_probe_ob.probe_object
            # handle planar reflections
            is_plane = ob.probe_type == 'PLANE'
            if not is_plane:
                if real_probe_ob and real_probe_ob.probe_type == 'PLANE':
                    is_plane = True
            if is_plane:
                # by default defines without value have the value 0
                # but in this case it doesn't matter and 1 feels more correct than null
                material_defines['PLANAR_PROBE'] = 1
            # follow the probe chain to handle defines (this time also planes)
            while real_probe_ob and real_probe_ob.probe_type in ['OBJECT', 'PLANE']\
                    and real_probe_ob.probe_object:
                real_probe_ob = real_probe_ob.probe_object
                print(real_probe_ob.name)
            # handle probe parallax
            parallax_type = real_probe_ob.probe_parallax_type # NONE, BOX, ELLIPSOID
            material_defines['CORRECTION_'+parallax_type] = 1
            # enable screen space refraction code
            material_defines['SS_REFR'] = 1


    elif obtype=='CURVE':
        curves = []
        for c in ob.data.splines:
            l = len(c.bezier_points)
            handles1 = [0.0]*l*3
            points = [0.0]*l*3
            handles2 = [0.0]*l*3
            c.bezier_points.foreach_get('handle_left', handles1)
            c.bezier_points.foreach_get('co', points)
            c.bezier_points.foreach_get('handle_right', handles2)
            curve = [0.0]*l*9
            for i in range(l):
                i3 = i*3
                i9 = i*9
                curve[i9] = handles1[i3]
                curve[i9+1] = handles1[i3+1]
                curve[i9+2] = handles1[i3+2]
                curve[i9+3] = points[i3]
                curve[i9+4] = points[i3+1]
                curve[i9+5] = points[i3+2]
                curve[i9+6] = handles2[i3]
                curve[i9+7] = handles2[i3+1]
                curve[i9+8] = handles2[i3+2]
            curves.append(curve)

        data = {'curves': curves, 'resolution': ob.data.resolution_u}
        if True:#getattr(ob, 'pre_calc', False):
            data['nodes'] = calc_curve_nodes(data['curves'],data['resolution'])

        #print(curves)
    elif obtype=='CAMERA':
        data = {
            'angle': ob.data.angle,
            'clip_end': ob.data.clip_end,
            'clip_start': ob.data.clip_start,
            'ortho_scale': ob.data.ortho_scale,
            'sensor_fit': ob.data.sensor_fit, # HORIZONTAL VERTICAL AUTO
            'cam_type': ob.data.type          # PERSP ORTHO
        }
    elif obtype=='LAMP':
        size_x = size_y = 0
        if ob.data.type == 'AREA':
            size_x = ob.data.size
            size_y = ob.data.size if ob.data.shape == 'SQUARE' else ob.data.size_y
        elif ob.data.type != 'HEMI':
            size_x = size_y = ob.data.shadow_soft_size
        used_data
        if used_data['binternal_materials_users'] > used_data['cycles_materials_users']:
            color = list(ob.data.color*ob.data.energy)
            energy = 1 # we never modified this in the end
        elif ob.data.use_nodes and ob.data.node_tree and 'Emission' in ob.data.node_tree.nodes:
            # We'll use lamp nodes in the future
            # for now we'll just assume one emission node
            node = ob.data.node_tree.nodes['Emission']
            color = list(node.inputs['Color'].default_value)[:3]
            energy = node.inputs['Strength'].default_value * 0.01
        else:
            color = list(ob.data.color)
            energy = 1
            if ob.data.type == 'SUN':
                energy = 0.01
        data = {
            'lamp_type': ob.data.type,
            'color': color,
            'energy': energy,
            'falloff_distance': ob.data.distance,
            'shadow': getattr(ob.data, 'use_shadow', False),
            'shadow_bias': getattr(ob.data, 'shadow_buffer_bias', 0.001),
            'shadow_buffer_type': getattr(ob.data, 'ge_shadow_buffer_type', 'VARIANCE'),
            'bleed_bias': getattr(ob.data, 'shadow_buffer_bleed_bias', 0.1),
            'tex_size': getattr(ob.data, 'shadow_buffer_size', 512),
            'frustum_size': getattr(ob.data, 'shadow_frustum_size', 0),
            'clip_start': getattr(ob.data, 'shadow_buffer_clip_start', 0),
            'clip_end': getattr(ob.data, 'shadow_buffer_clip_end', 0),
            'size_x': size_x,
            'size_y': size_y,
        }
    elif obtype=='ARMATURE':
        bones = []
        bone_dict = {}
        ordered_deform_names = []
        depends = defaultdict(set)
        num_deform = 0
        for bone in ob.data.bones:
            pos = bone.head_local.copy()
            if bone.parent:
                pos = bone.parent.matrix_local.to_3x3().inverted() * (pos - bone.parent.head_local)
            rot = bone.matrix.to_quaternion()
            bdata = {
                'name': bone.name,
                'parent': (bone.parent.name if bone.parent else ""),
                'position': list(pos),
                'rotation': rot[1:]+rot[0:1],
                'deform_id': -1,
                'constraints': [],
                'blength': bone.length,
            }
            bone_dict[bone.name] = bdata
            if bone.use_deform:
                bdata['deform_id'] = num_deform
                ordered_deform_names.append(bone.name)
                num_deform += 1
            for c in bone.children:
                depends[c.name].add(bone.name)
            depends[bone.name]
        # Each constraint: [function_name, owner idx, target idx, args...]
        # TODO: assuming target is own armature
        if export_pose:
            for bone in ob.pose.bones:
                for c in bone.constraints:
                    if c.mute:
                        continue
                    if c.type.startswith('COPY_') and c.subtarget:
                        axes = [int(c.use_x), int(c.use_y), int(c.use_z)]
                        if axes.count(1)==1 and c.type=='COPY_ROTATION':
                            con = [c.type.lower()+'_one_axis', bone.name, c.subtarget, axes]
                        else:
                            con = [c.type.lower(), bone.name, c.subtarget]
                        bone_dict[bone.name]['constraints'].append(con)

                        depends[bone.name].add(c.subtarget)
                    elif c.type == 'STRETCH_TO' and c.subtarget:
                        bone_dict[bone.name]['constraints'].append(
                            [c.type.lower(), bone.name, c.subtarget, c.rest_length, c.bulge])
                        depends[bone.name].add(c.subtarget)
                    elif c.type == 'IK' and c.subtarget:
                        cl = c.chain_count or 9999
                        bone_dict[bone.name]['constraints'].append(
                            [c.type.lower(), bone.name, c.subtarget, cl, c.iterations])
                        depends[bone.name].add(c.subtarget)
                        # have all children of bones of the chain to depend
                        # on this bone instead of their parent, because their
                        # parents are modified after IK is applied on this
                        last_bone = bone.name
                        while cl > 1 and bone:
                            previous = bone
                            bone = bone.parent
                            if bone:
                                for child in bone.children:
                                    if child != previous:
                                        depends[child.name].difference_update({child.parent.name})
                                        depends[child.name].add(last_bone)
                                        for child2 in child.children_recursive:
                                            depends[child2.name].difference_update({child2.parent.name})
                                            depends[child2.name].add(last_bone)
                            cl -= 1

        final_order = []
        last = set()
        while depends:
            next = set()
            for k,v in list(depends.items()):
                v.difference_update(last)
                if not v:
                    final_order.append(k)
                    next.add(k)
                    del depends[k]
            last = next
            if not next:
                # find cycle
                checked = set()
                cycle = []
                def check(k):
                    if k in checked:
                        raise Exception("Cycle found: "+' '.join(cycle))
                    checked.add(k)
                    cycle.append(k)
                    for k in depends[k]:
                        check(k)
                for k in depends.keys():
                    if k not in checked:
                        cycle = []
                        check(k)
                print("ERROR: cyclic dependencies in", ob.name, "\n      ", ' '.join(depends.keys()))
                # TODO: find bones with less dependencies and no parent dependencies
                break
        bones = [bone_dict[name] for name in final_order]
        ob.data['ordered_deform_names'] = ordered_deform_names
        data = {'bones': bones, 'unfc': num_deform * 4}
        print("Deform bones:",num_deform,"uniforms",num_deform*4)

        if export_pose:
            pose = {}
            for bone in ob.pose.bones:
                pose[bone.name] = {
                    'position': list(bone.location) if not ob.data.bones[bone.name].use_connect else [0,0,0],
                    'rotation': bone.rotation_quaternion[1:]+bone.rotation_quaternion[0:1],
                    'scale': list(bone.scale),
                    'ik_stiffness_x': bone.ik_stiffness_x,
                    'use_ik_limit_x': bone.use_ik_limit_x or bone.lock_ik_x,
                    'ik_min_x': bone.ik_min_x if not bone.lock_ik_x else 0,
                    'ik_max_x': bone.ik_max_x if not bone.lock_ik_x else 0,
                    'ik_stiffness_y': bone.ik_stiffness_y,
                    'use_ik_limit_y': bone.use_ik_limit_y or bone.lock_ik_y,
                    'ik_min_y': bone.ik_min_y if not bone.lock_ik_y else 0,
                    'ik_max_y': bone.ik_max_y if not bone.lock_ik_y else 0,
                    'ik_stiffness_z': bone.ik_stiffness_z,
                    'use_ik_limit_z': bone.use_ik_limit_z or bone.lock_ik_z,
                    'ik_min_z': bone.ik_min_z if not bone.lock_ik_z else 0,
                    'ik_max_z': bone.ik_max_z if not bone.lock_ik_z else 0,
                }
            data['pose'] = pose
        else:
            # We don't want varying dimensions to affect mesh hash
            dimensions = []
    else:
        obtype = 'EMPTY'
        data = {'mesh_radius': ob.empty_draw_size}
        game_properties = {
            '_empty_draw_type': ob.empty_draw_type,
            '_empty_draw_size': ob.empty_draw_size,
        }

    rot_mode = ob.rotation_mode
    if rot_mode=='QUATERNION':
        rot = ob.rotation_quaternion
        rot_mode = 'Q'
    elif rot_mode == 'AXIS_ANGLE':
        print("WARNING: Axis angle not supported yet, converting to quat. Ob: "+ob.name)
        a,x,y,z = list(ob.rotation_axis_angle)
        sin2 = sin(a/2)
        rot = [cos(a/2), x*sin2, y*sin2, z*sin2]
        rot_mode = 'Q'
    elif scn.myou_export_convert_to_quats:
        rot = ob.rotation_euler.to_quaternion()
        rot_mode = 'Q'
    else:
        rot = [0] + list(ob.rotation_euler)

    # used for physics properties
    first_mat = ob.material_slots and ob.material_slots[0].material

    for k,v in ob.items():
        if k not in ['modifiers_were_applied', 'zindex', 'cycles', 'cycles_visibility', '_RNA_UI'] \
                and not isinstance(v, bytes):
            if hasattr(v, 'to_list'):
                v = v.to_list()
            elif hasattr(v, 'to_dict'):
                v = v.to_dict()
            game_properties[k] = v
    for k,v in ob.game.properties.items():
        game_properties[k] = v.value

    if getattr(ob, 'probe_type', 'NONE') != 'NONE':
        game_properties['probe_options'] = dict(
            type=ob.probe_type,
            object=getattr(ob.probe_object, 'name', ''),
            auto_refresh=ob.probe_refresh_auto,
            compute_sh=ob.probe_compute_sh,
            double_refresh=ob.probe_refresh_double,
            same_layers=ob.probe_use_layers,
            size=ob.probe_size,
            sh_quality=ob.probe_sh_quality,
            clip_start=ob.probe_clip_start,
            clip_end=ob.probe_clip_end,
            parallax_type=ob.probe_parallax_type,
            parallax_volume=getattr(ob.probe_parallax_volume, 'name', ''),
            # it may crash if we read this when not needed
            reflection_plane=getattr(ob.probe_reflection_plane, 'name', '') \
                if ob.probe_type=='PLANE' else '',
        )

    parent = ob.parent.name if ob.parent else None
    if parent and ob.parent.proxy:
        parent = ob.parent.proxy.name

    strips = get_animation_data_strips(ob_anim_data)[0]
    if ob.type=='MESH' and ob.data and ob.data.shape_keys:
        strips += get_animation_data_strips(ob.data.shape_keys.animation_data)[0]

    obj = {
        'scene': scn.name,
        'type': ob.type,
        'name': obname,
        'position': list(ob.location),
        'rot': list(rot),
        'rot_mode': rot_mode,
        'properties': game_properties,
        'scale': list(ob.scale),
        'matrix_parent_inverse': sum(list(map(list, ob.matrix_parent_inverse.transposed())),[]),
        'dimensions': dimensions,
        'color' : list(ob.color),
        'parent': parent,
        'parent_bone': ob.parent_bone if parent and ob.parent.type == 'ARMATURE' and ob.parent_type == 'BONE' else '',
        'animation_strips': strips,
        'dupli_group': ob.dupli_group.name
            if ob.dupli_type=='GROUP' and ob.dupli_group else None,

        # Physics
        'phy_type': ob.game.physics_type,
        'visible': not ob.hide_render,
        'radius': ob.game.radius,
        'anisotropic_friction': ob.game.use_anisotropic_friction,
        'friction_coefficients': list(ob.game.friction_coefficients),
        'collision_group': sum([x*1<<i for i,x in enumerate(ob.game.collision_group)]),
        'collision_mask': sum([x*1<<i for i,x in enumerate(ob.game.collision_mask)]),
        'collision_bounds_type': ob.game.collision_bounds_type,
        'collision_margin': ob.game.collision_margin,
        'collision_compound': ob.game.use_collision_compound,
        'mass': ob.game.mass,
        'no_sleeping': ob.game.use_sleep,
        'is_ghost': ob.game.use_ghost,
        'linear_factor': [1 - int(ob.game.lock_location_x), 1 - int(ob.game.lock_location_y), 1 - int(ob.game.lock_location_z)],
        'angular_factor': [1 - int(ob.game.lock_rotation_x), 1 - int(ob.game.lock_rotation_y), 1 - int(ob.game.lock_rotation_z)],
        'form_factor': ob.game.form_factor,
        'friction': first_mat.physics.friction if first_mat else 0.5,
        'elasticity': first_mat.physics.elasticity if first_mat else 0,
    }
    if ob.game.physics_type == 'CHARACTER':
        obj.update({
            'step_height': ob.game.step_height,
            'jump_force': ob.game.jump_speed,
            'max_fall_speed': ob.game.fall_speed
        })
    obj.update(data)
    if obtype == 'FONT':
        scn.objects.unlink(nob)
    return obj

def ob_in_layers(scn, ob):
    return any(a and b for a,b in zip(scn.myou_export_layers, ob.layers))


def ob_to_json_recursive(ob, scn, used_data):
    # TODO: Manage cases where the parent is not exported
    d = [ob_to_json(ob, scn, used_data)]
    for c in ob.children:
        if ob_in_layers(scn, c):
            d += ob_to_json_recursive(c, scn, used_data)
    return d
