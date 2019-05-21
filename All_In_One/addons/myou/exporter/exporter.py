

from .object import ob_to_json, ob_in_layers, ob_to_json_recursive
from .material import mat_to_json, world_material_to_json, get_shader_lib
from .animation import get_animation_data_strips, action_to_json
from . import image, progress, mat_nodes
from .util_convert import linearrgb_to_srgb
from .optimize_glsl import optimize_glsl

import json
from json import dumps, loads
from collections import defaultdict
import shutil
import tempfile
import os
import struct
from math import *
import re
import gzip

tempdir = tempfile.gettempdir()

def search_scene_used_data(scene):

    used_data = {
        'objects': [],
        'materials': [],
        'material_objects': defaultdict(set),
        'material_use_tangent': {},
        # materials don't have layers, but we'll assume their presence in layers
        # to determine which "this layer only" lights to remove
        'material_layers': {},
        'textures': [],
        'images': [],
        'image_texture_slots': defaultdict(list),
        'image_materials': defaultdict(set),
        'image_is_normal_map': {},
        'meshes': [],
        'actions': [],
        'action_users': {}, # only one user (ob or material) of each, to get the channels
        'sounds': {},
        'cycles_materials_users': 0,
        'binternal_materials_users': 0,
    }

    #recursive search methods for each data type:
    def add_ob(ob, i=0):
        if ob not in used_data['objects']:
            is_in_layers = ob_in_layers(scene, ob)
            print('    '*i+'Ob:', ob.name if is_in_layers else '('+ob.name+' not exported)')

            if is_in_layers:
                used_data['objects'].append(ob)
                if ob.type == 'MESH':
                    add_mesh(ob.data, i+1)

                for s in ob.material_slots:
                    if hasattr(s,'material') and s.material:
                        add_material(s.material, ob.layers, i+1)
                        used_data['material_objects'][s.material.name].add(ob)

                add_animation_data(ob.animation_data, ob, i+1)
                if ob.type=='MESH' and ob.data and ob.data.shape_keys:
                    add_animation_data(ob.data.shape_keys.animation_data, ob, i+1)

        for ob in ob.children:
            add_ob(ob, i+1)

    def add_action(action, i=0):
        if not action in used_data['actions']:
            print('    '*i+'Act:', action.name)
            used_data['actions'].append(action)

    def add_material(m, layers, i=0):
        if not m.name in used_data['material_layers']:
            use_normal_maps = False
            used_data['materials'].append(m)
            used_data['material_layers'][m.name] = list(layers)
            print('    '*i+'Mat:', m.name)
            if scene.render.engine in ['BLENDER_RENDER', 'BLENDER_GAME']:
                for s,enabled in zip(m.texture_slots, m.use_textures):
                    if enabled and hasattr(s, 'texture') and s.texture:
                        use_normal_map = getattr(s.texture, 'use_normal_map', False)
                        add_texture(s.texture, m, i+1, use_normal_map)
                        use_normal_maps = use_normal_maps or use_normal_map
            add_animation_data(m.animation_data, m, i+1)
            if m.use_nodes and m.node_tree:
                use_normal_maps = search_in_node_tree(m.node_tree, m, layers, i-1) or use_normal_maps
                add_animation_data(m.node_tree.animation_data, m.node_tree, i+1)
            used_data['material_use_tangent'][m.name] = used_data['material_use_tangent'].get(m.name, False) or use_normal_maps
        mlayers = used_data['material_layers'][m.name]
        for i,l in enumerate(layers):
            mlayers[i] = l or mlayers[i]
        if mat_nodes.is_blender_pbr_material(m):
            used_data['cycles_materials_users'] += 1
        else:
            used_data['binternal_materials_users'] += 1
        return used_data['material_use_tangent'].get(m.name, False)

    # NOTE: It assumes that there is no cyclic dependencies in node groups.
    def search_in_node_tree(tree, mat, layers, i=0):
        use_normal_map = False
        for n in tree.nodes:
            if (n.bl_idname == 'ShaderNodeMaterial' or n.bl_idname == 'ShaderNodeExtendedMaterial') and n.material:
                use_normal_map = add_material(n.material, layers, i+1) or use_normal_map
            elif n.bl_idname == 'ShaderNodeTexture' and n.texture:
                use_normal_map = use_normal_map or getattr(n.texture, 'use_normal_map', False)
                add_texture(n.texture, mat, i+1)
            elif n.bl_idname in ('ShaderNodeTexImage', 'ShaderNodeTexEnvironment') and n.image:
                add_image(n.image, mat, i+1)
                if n.color_space == 'NONE' and \
                    any([link.to_node.type == 'NORMAL_MAP' for link in n.outputs[0].links]):
                        used_data['image_is_normal_map'][n.image.name] = True
            elif n.bl_idname == 'ShaderNodeTangent':
                if n.direction_type == 'UV_MAP':
                    # TODO: Specify which UV map is the tangent based on!
                    use_normal_map = True
            elif n.bl_idname == 'ShaderNodeNormalMap':
                if n.space == 'TANGENT':
                    # TODO: Specify which UV map is the tangent based on!
                    use_normal_map = True
            elif n.bl_idname == 'ShaderNodeGroup':
                if n.node_tree:
                    if search_in_node_tree(n.node_tree, mat, layers, i+1):
                        use_normal_map = True
        return use_normal_map

    def add_texture(t, mat, i=0, is_normal=False): # internal/game only
        if not t in used_data['textures']:
            print('    '*i+'Tex:', t.name)
            used_data['textures'].append(t)
            if t.type == 'IMAGE' and t.image:
                add_image(t.image, mat, i+1)
                used_data['image_texture_slots'][t.image.name].append(t)
                used_data['image_is_normal_map'][t.image.name] = is_normal

    def add_image(i, mat, indent=0):
        used_data['image_materials'][i.name].add(mat)
        if not i in used_data['images']:
            print('    '*indent+'Img:', i.name)
            used_data['images'].append(i)

    def add_mesh(m,i=0):
        if not m in used_data['meshes']:
            print('    '*i+'Mes:', m.name)
            used_data['meshes'].append(m)

    def add_seq_strip(strip):
        if strip.type=='SOUND':
            used_data['sounds'][strip.sound.name] = strip.sound.filepath

    def add_animation_data(animation_data, user, i=0):
        any_solo = False
        if animation_data and animation_data.nla_tracks:
            any_solo = any([track.is_solo for track in animation_data.nla_tracks])
            for track in animation_data.nla_tracks:
                if (any_solo and not track.is_solo) or track.mute:
                    # solo shot first
                    continue
                for strip in track.strips:
                    if strip.type == 'CLIP' and not strip.mute:
                        add_action(strip.action, i+1)
                        used_data['action_users'][strip.action.name] = user

        action = animation_data and animation_data.action
        if not any_solo and action and action.fcurves:
            add_action(action, i+1)
            used_data['action_users'][action.name] = user

    # Searching and storing stuff in use:
    print('\nSearching used data in the scene: ' + scene.name + '\n')

    # Export background textures(s)
    if scene.world and getattr(scene.world, 'use_nodes'):
        search_in_node_tree(scene.world.node_tree, scene.world, [False]*20)

    for ob in scene.objects:
        if not ob.parent:
            add_ob(ob)

    sequences = (scene.sequence_editor and scene.sequence_editor.sequences_all) or []
    for s in sequences:
        add_seq_strip(s)

    print("\nObjects:", len(used_data['objects']), "Meshes:", \
        len(used_data['meshes']), "Materials:", len(used_data['materials']), \
        "Textures:", len(used_data['textures']), "Images:", len(used_data['images']), \
        "Actions:", len(used_data['actions']))

    print ('\n')

    return used_data

def scene_data_to_json(scn=None):
    scn = scn or bpy.context.scene
    if not scn.world:
        bpy.ops.world.new()
    world = scn.world
    sequences = (scn.sequence_editor and scn.sequence_editor.sequences_all) or []
    background_probe = {}
    if hasattr(world, 'probe_size'):
        background_probe = dict(
            type='CUBEMAP',
            object='',
            auto_refresh=world.probe_refresh_auto,
            compute_sh=world.probe_compute_sh,
            double_refresh=False,
            same_layers=False,
            size=world.probe_size,
            sh_quality=world.probe_sh_quality,
            # These are irrelevant as only one quad is rendered
            clip_start=1,
            clip_end=1000,
            parallax_type='NONE',
            parallax_volume='',
            reflection_plane='',
        )
    scene_data = {
        'type':'SCENE',
        'name': scn.name,
        'gravity' : [0,0,-scn.game_settings.physics_gravity], #list(scn.gravity),
        'background_color' : linearrgb_to_srgb([0,0,0], world.horizon_color),
        'ambient_color': linearrgb_to_srgb([0,0,0], world.ambient_color),
        'world_material': world_material_to_json(scn),
        'background_probe': background_probe,
        'debug_physics': scn.game_settings.show_physics_visualization,
        'active_camera': scn.camera.name if scn.camera else 'Camera',
        'stereo': scn.game_settings.stereo == 'STEREO',
        'stereo_eye_separation': scn.game_settings.stereo_eye_separation,
        'frame_start': scn.frame_start,
        'frame_end': scn.frame_end,
        'fps': scn.render.fps,
        'markers': sorted([{
            'name': m.name,
            'frame': m.frame,
            'camera': m.camera and m.camera.name or '',
        } for m in scn.timeline_markers], key=lambda m:m['frame']),
        'sequencer_strips':  sorted([{
            'frame_start': s.frame_start,
            'type': s.type,
            'sound': s.sound.name if s.type=='SOUND' else '',
        } for s in sequences], key=lambda m:m['frame_start']),
        # TODO: Extract these from the main view3D?
        # 'bsdf_samples': space_data.pbr_settings.brdf.samples
        # 'lod_bias': space_data.pbr_settings.brdf.lodbias
    }
    return scene_data


def embed_meshes(scn):
    r = []
    for hash in scn['embed_mesh_hashes'].keys():
        mesh_bytes = open(scn['exported_meshes'][hash],'rb').read()
        if len(mesh_bytes)%4 != 0:
            mesh_bytes += bytes([0,0])
        int_list = struct.unpack('<'+str(int(len(mesh_bytes)/4))+'I', mesh_bytes)
        r.append({'type': 'EMBED_MESH', 'hash': hash, 'int_list': int_list})
    return r

def whole_scene_to_json(scn, used_data, textures_path):
    previous_scn = None
    if scn != bpy.context.screen.scene:
        # TODO: This never worked with materials
        # check if it works with the current version
        previous_scn = bpy.context.screen.scene
        bpy.context.screen.scene = scn

    # TODO: scene doesn't change back
    # Possible quirks of not changing scene:
    # * Meshes can't be exported
    # * Materials with custom uniforms can't be exported
    # Those are or may be cached to mitigate the issue

    was_editing = bpy.context.mode == 'EDIT_MESH'
    if was_editing:
        bpy.ops.object.editmode_toggle()
    # exported_meshes and embed_mesh_hashes will be filled
    # while exporting meshes from ob_to_json_recursive below
    scn['exported_meshes'] = {}
    scn['embed_mesh_hashes'] = {}
    scn['game_tmp_path'] = get_scene_tmp_path(scn) # TODO: have a changed_scene function

    # Start exporting scene settings, then the objects
    world_mat_list = []
    ret = [scene_data_to_json(scn)]
    if ret[0]['world_material']:
        world_mat_list = [ret[0]['world_material']]
    for ob in used_data['objects']:
        if ob.parent:
            continue
        ret += ob_to_json_recursive(ob, scn, used_data)
    # This uses embed_mesh_hashes created above then filled in ob_to_json_recursive
    ret += embed_meshes(scn)
    # TODO: this is not currently used
    for group in bpy.data.groups:
        ret.append(
                {'type': 'GROUP',
                'name': group.name,
                'scene': scn.name,
                'offset': list(group.dupli_offset),
                'objects': [o.name for o in group.objects],
                })
    # Export shader lib, textures (images), materials, actions
    image_json = image.export_images(textures_path, used_data)
    mat_json = [mat_to_json(mat, scn, used_data)
                    for mat in used_data['materials']]
    act_json = [action_to_json(action, used_data['action_users'][action.name])
                    for action in used_data['actions']]
    # Export ramps and curve mappings and remove them from materials
    # (for de-duplication)
    ramps = {}
    for mat in mat_json:
        ramps.update(mat['ramps'])
        del mat['ramps']
    for name,ramp in ramps.items():
        image_json.append({
            'type': 'TEXTURE',
            'name': str(name),
            'formats': {'raw_pixels': {
                'width': len(ramp) / 4,
                'height': 1,
                'pixels': ramp,
            }},
            'wrap': 'C',
        })
    # We must export shader lib after materials, but engine has to read it before
    shader_lib = get_shader_lib(mat_json+world_mat_list)
    if scn.myou_export_optimize_glsl:
        for mat in mat_json + world_mat_list:
            mat['fragment'] = optimize_glsl([shader_lib, mat['fragment']])
    else:
        ret.append({"type":"SHADER_LIB","code": shader_lib})
    ret += image_json + mat_json + act_json
    # Final JSON encoding, without spaces
    retb = dumps(ret, separators=(',',':')).encode('utf8')
    retb_gz = gzip.compress(retb)
    size = len(retb)
    size_gz = len(retb_gz)
    # TODO empty scn['exported_meshes']?
    # for mesh_hash, fpath in scn['exported_meshes'].items():
    #     if mesh_hash not in scn['embed_mesh_hashes']:
    #         size += os.path.getsize(fpath)
    print('Scene JSON size: %.3f MiB (%.3f MiB compressed)' %
          (size/1048576, size_gz/1048576))
    scn['total_size'] = size
    if was_editing:
        bpy.ops.object.editmode_toggle()
    if previous_scn:
        bpy.context.screen.scene = previous_scn
    return [retb, retb_gz]


def get_scene_tmp_path(scn):
    dir = os.path.join(tempdir, 'scenes', scn.name + os.sep)
    for p in (os.path.join(tempdir, 'scenes'), dir):
        try:
            os.mkdir(p)
        except FileExistsError:
            pass
    return dir

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

class MyouEngineExporter(bpy.types.Operator, ExportHelper):
    """Export scene as a HTML5 WebGL page."""
    bl_idname = "export_scene.myou"
    bl_label = "Export Myou"

    filename_ext = ".myou"
    filter_glob = StringProperty(default="*", options={'HIDDEN'})

    def execute(self, context):
        export_myou(self.filepath, context.scene)
        return {'FINISHED'}

def menu_export(self, context):
    self.layout.operator(MyouEngineExporter.bl_idname, text="Myou Engine")

def try_mkdir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)

def export_myou(path, scn):
    progress.reset()

    join = os.path.join

    if path.endswith('.myou'):
        path = path[:-5]
    data_dir = os.path.basename(path.rstrip('/').rstrip('\\').rstrip(os.sep))
    if data_dir:
        data_dir += os.sep
    full_dir = os.path.realpath(join(os.path.dirname(path), data_dir))
    old_export = ''

    scenes_path = join(full_dir, 'scenes')
    textures_path = join(full_dir, 'textures')
    sounds_path = join(full_dir, 'sounds')

    try_mkdir(full_dir)
    try_mkdir(scenes_path)
    try_mkdir(textures_path)
    try_mkdir(sounds_path)

    if os.path.exists(full_dir):
        if 0:
            # Delete whole folder
            shutil.rmtree(full_dir, ignore_errors=False)
        else:
            # Delete scene folders to be exported
            for scene in bpy.data.scenes:
                scn_dir = join(scenes_path, scene.name)
                if os.path.exists(scn_dir):
                    shutil.rmtree(scn_dir, ignore_errors=False)
    try:
        for scene in bpy.data.scenes:
            used_data = search_scene_used_data(scene)
            scn_dir = join(scenes_path, scene.name)
            try_mkdir(scn_dir)
            scene_json, scene_json_gz = whole_scene_to_json(scene, used_data, textures_path)
            print('Copying files...')
            open(join(scn_dir, 'all.json'), 'wb').write(scene_json)
            if scn.myou_export_compress_scene:
                open(join(scn_dir, 'all.json.gz'), 'wb').write(scene_json_gz)
            for mesh_file in scene['exported_meshes'].values():
                shutil.copy(mesh_file, scn_dir)
                if scn.myou_export_compress_scene:
                    shutil.copy(mesh_file+'.gz', scn_dir)
            for name,filepath in used_data['sounds'].items():
                apath = bpy.path.abspath(filepath)
                shutil.copy(apath, join(sounds_path, name))
            blend_dir = bpy.data.filepath.rsplit(os.sep, 1)[0]#.replace('\\','/')
            for fname in scene.myou_export_copy_files.split(' '):
                if fname:
                    apath = join(blend_dir, fname)
                    oname = fname.replace(os.sep, '/').replace('../','')
                    if os.path.isfile(apath):
                        shutil.copy(apath, join(full_dir, oname))
                    else:
                        print("Warning: File doesn't exist: "+apath)
        # Delete unused textures
        used_textures = set()
        for scene_name in os.listdir(join(full_dir, 'scenes')):
            json_path = join(full_dir, 'scenes', scene_name, 'all.json')
            if os.path.exists(json_path):
                jsonf = open(json_path)
                textures = [img['file_name']+suffix
                    for tex in json.load(jsonf) if tex['type'] == 'TEXTURE'
                        for fmt in tex['formats'].values()
                            for img in fmt
                                for suffix in ['', '.gz']
                                    if hasattr(img, 'keys') and 'file_name' in img
                ]
                used_textures.update(textures)
                jsonf.close()
        for tex in os.listdir(textures_path):
            tex_abs = join(textures_path, tex)
            if tex not in used_textures and os.path.isfile(tex_abs):
                os.remove(tex_abs)
        print('=== Export has finished successfully ===')
    except:
        import datetime
        # shutil.move(full_dir, full_dir+'_FAILED_'+str(datetime.datetime.now()).replace(':','-').replace(' ','_').split('.')[0])
        # shutil.move(old_export, full_dir)
        # print("EXPORT HAS FAILED, but old folder has been restored")
        raise

    bpy.ops.file.make_paths_relative()
