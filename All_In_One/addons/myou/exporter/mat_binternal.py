import bpy, gpu, os, base64, struct, zlib, re
from json import loads, dumps
from pprint import pprint
from random import random
from .shader_lib_extractor import *

# importing exporter here doesn't work in python<3.5 (blender 2.71)
get_animation_data_strips = None

tex_sizes = {}

def get_dynamic_constants(mat, scn, paths, code):
    # Example:
    #paths = [
        #'node_tree.nodes["slicep"].outputs[0].default_value',
        #'node_tree.nodes["slicen"].outputs[0].default_value',
    #]
    restore = []
    sentinels = []
    lookup_data = []
    varnames_types = []
    for p in paths:
        # We're assuming "%f"%sentinel yelds exactly the same string
        # as the code generator (sprintf is used in both cases)
        sentinel = random()
        while ("%f"%sentinel) in code or sentinel in sentinels:
            sentinel = random()
        if p.startswith('nodes['):
            p = 'node_tree.'+p
        try:
            orig_obj = mat.path_resolve(p)
        except ValueError:
            lookup_data.append([0,0,0])
            continue
        obj, attr = ('.'+p).rsplit('.', 1)
        obj = eval('mat'+obj)
        #print(obj, attr)
        value = orig_obj
        is_vector = hasattr(orig_obj, '__getitem__')
        orig_val = None
        if is_vector:
            value = list(orig_obj)
            orig_val = orig_obj[0]
            orig_obj[0] = sentinel
            vlen = len(orig_obj)
        else:
            vlen = 1
            setattr(obj, attr, sentinel)
        lookup_data.append([sentinel, vlen, value])
        restore.append([is_vector,obj,attr,orig_obj,orig_val])

    scn.update()
    sh = gpu.export_shader(scn, mat)
    c = sh['fragment'].rsplit('}', 2)[1]

    for sentinel, vlen, value in lookup_data:
        if not sentinel:
            varnames_types.append([None, None, 0])
            continue
        pos = c.find("%f"%sentinel)
        if pos!=-1:
            varname = c[:pos].rsplit(' ',3)[1]
            varnames_types.append([varname, vlen, value])
        else:
            varnames_types.append([None, vlen, value])

    for is_vector,obj,attr,orig_obj,orig_val in restore:
        # restore original
        if is_vector:
            orig_obj[0] = orig_val
        else:
            setattr(obj, attr, orig_obj)


    if any(varnames_types):
        scn.update()
    #pprint(varnames_types)
    return [varnames_types, sh]

def mat_to_json_try(mat, scn):
    global SHADER_LIB
    global get_animation_data_strips
    if not get_animation_data_strips:
        from . import exporter
        get_animation_data_strips = exporter.get_animation_data_strips

    # NOTE: This export is replaced later
    shader = gpu.export_shader(scn, mat)
    parts = shader['fragment'].rsplit('}',2)
    shader['fragment'] = ('\n'+parts[1]+'}')

    # Stuff for debugging shaders
    # TODO write only when they have changed
    # if os.name != 'nt':
    #     SHM = "/run/shm/"
    #     open(SHM + mat.name+'.v','w').write(shader['vertex'])
    #     open(SHM + mat.name+'.f','w').write(shader['fragment'])
    #     try:
    #         shader['fragment']=open(SHM + mat.name+'.f2').read()
    #     except:
    #         pass
    #from pprint import pprint
    #pprint(shader['attributes'])
    # ---------------------------

    # # Checking hash of main() is not enough
    # code_hash = hash(shader['fragment']) % 2147483648
    #print(shader['fragment'].split('{')[0])

    print(mat.name)
    strips, drivers = get_animation_data_strips(mat.animation_data)
    if mat.node_tree and mat.node_tree.nodes:
        s,d = get_animation_data_strips(mat.node_tree.animation_data)
        strips += s
        drivers += d

    if 1:
        # Dynamic uniforms (for animation, per object variables,
        #                   particle layers or other custom stuff)
        dyn_consts = []
        # Old custom_uniforms API
        block = bpy.data.texts.get('custom_uniforms')
        if block:
            paths = [x for x in block.as_string().split('\n')
                     if x]
            #print(paths)
        else:
            paths = []
        # Animated custom_uniforms
        to_unmute = []
        for strip in strips:
            last_path = ''
            for f in bpy.data.actions[strip['action']].fcurves:
                if not f.mute:
                    f.mute = True
                    to_unmute.append(f)
                if f.data_path != last_path:
                    last_path = f.data_path
                    if last_path not in paths:
                        paths.append(last_path)
        paths += drivers # drivers is a list of data_paths for now
        dyn_consts = []
        dyn_ecounts = []
        dyn_values = []
        # NOTE: This _replaces_ the previously exported shader
        dyn_stuff, shader = get_dynamic_constants(mat, scn, paths, shader['fragment'])
        for a,b,c in dyn_stuff:
            dyn_consts.append(a)
            dyn_ecounts.append(b)
            dyn_values.append(c)
        # We're repeating what we did at the beginning
        shader['fragment'] = ('\n'+shader['fragment'].rsplit('}',2)[1]+'}')
        premain, main = shader['fragment'].split('{')

        # Restore previously muted fcurves
        for f in to_unmute:
            f.mute = False

        # Get list of unknown varyings and save them
        # as replacement strings
        known = ['var'+a['varname'][3:] for a in shader['attributes'] if a['varname']]
        varyings = [x[:-1].split()
                    for x in premain.split('\n')
                    if x.startswith('varying')
                    and len(x) < 21 # this filters varposition/varnormal
                    ]
        replacements = []
        for v in varyings:
            if v[2] not in known:
                replacements.append((' '.join(v),
                    'const {t} {n} = {t}(0.0)'.format(t=v[1], n=v[2])))

    shader['fragment'] = shader['fragment'].replace('sampler2DShadow','sampler2D')\
        .replace('\nin ', '\nvarying ')
    shader['fragment'] = re.sub(r'[^\x00-\x7f]',r'', shader['fragment'])

    if any(dyn_consts):
        # Separate constants from the rest
        #print(mat.name,'===>',premain)
        lines = premain.split('\n')
        # This generates a dictionary with the var name
        # and comma-separated values in a string, like this:
        # {'cons123': '1.23, 4.56, 7.89', ...}
        consts = dict([(c[2], c[3].split('(')[1][:-2]) for c in
                [l.split(' ', 3) for l in lines]
                if c[0]=='const'])

        premain = '\n'.join(l for l in lines if not l.startswith('cons'))

        # Convert them back to constants, except for dynamic ones
        lines = []
        TYPES = ['float', 'vec2', 'vec3', 'vec4', '','','','','mat3','','','','','','','mat4']
        types = [None]*len(dyn_consts)
        for k,v in consts.items():
            t = TYPES[v.count(',')]
            #print(k, dyn_consts, k in dyn_consts)
            if k in dyn_consts:
                lines.append('uniform {0} {1};'.format(t, k))
                # GL type may differ from value
                dyn_ecounts[dyn_consts.index(k)] = v.count(',')+1
            else:
                lines.append('const {0} {1} = {0}({2});'.format(t, k, v))

        shader['fragment'] = '\n'.join(lines) + '\n' + premain + '{' + main

        shader['uniforms'] += [
            # TODO: index is never used as it's always in order,
            # remove it after ensuring in legacy engine
            {'type': -1, 'varname': c or '', 'count': dyn_ecounts[i],
             'index': i, 'path': paths[i], 'value': dyn_values[i]}
        for i,c in enumerate(dyn_consts)]

    # mat['code_hash'] = code_hash

    for a,b in replacements:
        shader['fragment'] = shader['fragment'].replace(a, b)

    if mat.game_settings.alpha_blend == 'CLIP':
        shader['fragment'] = re.sub(
            r'gl_FragColor = ([^;]*)',
            r'if(\1.a < 0.5)discard; gl_FragColor = \1',
            shader['fragment'])

    # Find number of required shape attributes (excluding basis)
    # And number of bones
    num_shapes = 0
    num_bones = 0
    num_partsegments = 0
    weights6 = False
    for ob in scn.objects:
        if ob.type == 'MESH':
            # TODO: manage materials attached to object
            if mat in list(ob.data.materials):
                if ob.data.shape_keys:
                    num_shapes = max(num_shapes, len(ob.data.shape_keys.key_blocks) - 1)
                if ob.particle_systems:
                    num_partsegments = 1  # TODO check correct p systems and segments
                if ob.parent and ob.parent.type == 'ARMATURE' and ob.parent_type != 'BONE' and not ob.get('apply_armature'):
                    #print("Material", mat.name, "has armature", ob.parent.name, "because of mesh", ob.name)
                    num_bones = max(num_bones, len([b for b in ob.parent.data.bones if b.use_deform]))
                    if ob.get('weights6'): weights6 = True
    if num_shapes:
        shader['attributes'].append({'type':99, 'count': num_shapes, 'varname': ''})
    if num_partsegments:
        shader['attributes'].append({'type':77, 'count': num_partsegments, 'varname': ''})
    if num_bones:
        t = 86 if weights6 else 88
        shader['attributes'].append({'type':t, 'count': num_bones, 'varname': ''})

    last_lamp = ""
    param_mats = {}
    for u in shader['uniforms']:
        if 'lamp' in u:
            u['lamp'] = last_lamp = u['lamp'].name
        if 'image' in u:
            # TODO: if the image is used in several textures, how can we know which?
            slots = list(mat.texture_slots)
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type=='MATERIAL' and node.material:
                        slots.extend(node.material.texture_slots)
            texture_slot = [t for t in slots
                if t and t.texture and t.texture.type=='IMAGE' and t.texture.image==u['image']]
            if not texture_slot:
                print("Warning: image %s not found in material %s."%(u['image'].name, mat.name))
                u['filter'] = True
                u['wrap'] = 'R'
            else:
                u['filter'] = texture_slot[0].texture.use_interpolation
                u['wrap'] = 'R' if texture_slot[0].texture.extension == 'REPEAT' else 'C'
            u['size'] = 0
            fpath = bpy.path.abspath(u['image'].filepath)
            if os.path.isfile(fpath):
                u['size'] = os.path.getsize(fpath)
            # u['filepath'] is only used in old versions of the engine
            u['filepath'] = u['image'].name + '.' + u['image'].get('exported_extension', fpath.split('.').pop())
            u['image'] = u['image'].name
            tex_sizes[u['image']] = u['size']
        if 'texpixels' in u:
            # Minimum shadow buffer is 128x128
            if u['texsize'] > 16000:
                # This is a shadow buffer
                u['type'] = gpu.GPU_DYNAMIC_SAMPLER_2DSHADOW
                del u['texpixels'] # we don't need this
                # Assuming a lamp uniform is always sent before this one
                u['lamp'] = last_lamp
                # TODO: send lamp stuff
            else:
                # It's a ramp
                # encode as PNG data URI
                # TODO: Store this in the JSON texture list when the old engine
                # is no longer used
                def png_chunk(ty, data):
                    return struct.pack('>I',len(data)) + ty + data +\
                        struct.pack('>I',zlib.crc32(ty + data))

                u['filepath'] = 'data:image/png;base64,' + base64.b64encode(
                    b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',
                    struct.pack('>IIBBBBB', 256, 1, 8, 6, 0, 0, 0))+
                    png_chunk(b'IDAT', zlib.compress(
                    b'\x00'+u['texpixels'][:1024])) + png_chunk(b'IEND', b'')
                    #for some reason is 257px?
                ).decode()

                u['image'] = hex(hash(u['filepath']))[-15:]
                u['wrap'] = 'C' # clamp to edge
                u['type'] = gpu.GPU_DYNAMIC_SAMPLER_2DIMAGE
                u['size'] = 0
                del u['texpixels']
        if 'material' in u:
            param_mats[u['material'].name] = u['material']
            u['material'] = u['material'].name

    # Detect unused varyings (attributes)
    for line in shader['fragment'].split('\n'):
        # len<22 filters varposition/varnormal
        if len(line) < 22 and line.startswith('varying'):
            _, gltype, name = line[:-1].split(' ')
            used = False
            for attr in shader['attributes']:
                if attr['varname'][3:] == name[3:]:
                    used = True
                    break
            if not used:
                shader['attributes'].append(dict(
                    type=-1, # UNUSED
                    varname=name,
                    gltype=gltype,
                ))

    # Engine builds its own vertex shader
    del shader['vertex']
    shader['double_sided'] = not mat.game_settings.use_backface_culling
    shader['type'] = 'MATERIAL'
    shader['material_type'] = 'BLENDER_INTERNAL'
    shader['name'] = mat.name
    shader['scene'] = scn.name
    shader['params'] = [
        {
            'name': m.name,
            'diffuse_color': list(m.diffuse_color),
            'diffuse_intensity': m.diffuse_intensity,
            'specular_color': list(m.specular_color),
            'specular_intensity': m.specular_intensity,
            'specular_hardness': m.specular_hardness,
            'emit': m.emit,
            'alpha': m.alpha,
        }
        for m in param_mats.values()
    ]

    shader['animation_strips'] = strips

    shader['fragment_hash'] = hash(shader['fragment'])
    ret = loads(dumps(shader))
    # mat['hash'] = hash(ret) % 2147483648
    return ret
