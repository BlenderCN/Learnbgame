import bpy

from itertools import chain

def all():
    def make_v1_scope(*args, **kwargs):
        return {
            'SCALE': args,
            'Types': dict(SCALE='3f', version='3i', **kwargs),
            'Name': ('SCALE', 'version'),
            'Type': 'Group',
        }
    v1_0_0 = {
        'SRC': make_v1_scope('to_um', 'to_vox', 'from_mesh'),
        'SUB': make_v1_scope('subvolume', 'offset'),
        'VOL': make_v1_scope('volume', 'origin', tmp='s'),
    }
    return parse({
        (1,0,0): v1_0_0 
    })

def flat(ns_k, ns):
    n_list = ns['Name']
    a_list = sorted(ns['Types'].keys())
    var_k = set(a_list) & set(ns.keys())
    val_k = set(a_list) - set(ns.keys())

    # List all keywords
    lists = {k: ns[k] for k in var_k}
    unpack = lambda k: lists.get(k, [k])
    lists['All'] = tuple(chain(*map(unpack, a_list)))
    lists['Name'] = tuple(chain(*map(unpack, n_list)))
    # Get types for all keywords
    fmt = lambda k: ns['Types'].get(k, 's')
    types = {
        v: fmt(k) for k in var_k for v in lists[k]
    }
    types = dict(types, **{v:fmt(v) for v in val_k})
    
    # Return types and lists
    return {
        'Type': ns['Type'],
        'Types': types,
        'Keys': lists,
        'Name': ns_k,
    }

def parse(versions):
    n_keys = sorted(versions.keys(), reverse=True)
    def read(n_k):
        n = versions.get(n_k)
        n_kv = n.items()
        return {
            'Items': {kv[0]: flat(*kv) for kv in n_kv},
            'Keys': tuple(sorted(n.keys())),
            'Name': n_k,
        }
    return tuple(map(read, n_keys))

def setup(versions):
    bpy_props = {
        '3f': bpy.props.FloatVectorProperty,
        '3i': bpy.props.IntVectorProperty,
        's': bpy.props.StringProperty,
    }
    version = versions[0]
    # All objects targeted by version
    for scope, item in version['Items'].items():
        bpy_type = getattr(bpy.types, item['Type'])
        for key, fmt in item['Types'].items():
            typer = bpy_props[fmt]
            if not hasattr(bpy_type, key):
                setattr(bpy_type, key, typer(key))
