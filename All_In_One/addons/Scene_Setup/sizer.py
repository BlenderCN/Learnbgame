from functools import reduce
from operator import mul

from . import err

# 10um per world unit
UM = 10

def raise_nonzero(key, value):
    if 0 in value:
        msg = 'Cannot have zeros in {}'.format(key)
        raise err.ListParseError(msg, key, value)

def parse_list(_list, _len=None, _log='', _neg=False):
    LIST = []
    for val in _list.split(':'):
        pos = val.lstrip('-')
        if pos.isdigit():
            if _neg and '-' in val:
                LIST += [-int(pos)]
                continue
            LIST += [int(pos)]
    if _len is not None:
        if _len is not len(LIST):
            msg = 'Must have {} numbers'.format(_len)
            raise err.ListParseError(msg, _log, LIST)
    return LIST

def convert(given, mults=[], denoms=[]):
    result = []
    mz, my, mx = [[],[],[]]
    qz, qy, qx = [[],[],[]]
    if len(mults):
        # Error if any m gives a list shorter than 3
        mz, my, mx = zip(*(given[m] for m in mults))
    if len(denoms):
        # Error if any d gives a list shorter than 3
        qz, qy, qx = zip(*(given[d] for d in denoms))
    try:
        result += [reduce(mul, mz, 1) / reduce(mul, qz, 1)]
        result += [reduce(mul, my, 1) / reduce(mul, qy, 1)]
        result += [reduce(mul, mx, 1) / reduce(mul, qx, 1)]
    except ZeroDivisionError:
        axis = [qz, qy, qx][len(result) % 3]
        keys = (k for k,v in zip(denoms, axis) if v == 0)
        key = next(keys, 'any input')
        value = given.get(key, given)
        msg = 'Cannot have zeros in {}'.format(key)
        raise err.ListParseError(msg, key, value)
    return result

def get_scale(arg):
    nm_w = UM * 1000
    given = { 
        'um/world': [UM,] * 3,
        'nm/world': [nm_w,] * 3,
        'nm/vox': parse_list(arg.nm, 3, 'nm/vox'),
        'vox/mesh': parse_list(arg.vox, 3, 'vox/mesh'),
        'um/VOL': parse_list(arg.VOL, 3, 'um/VOL'),
        'um/XYZ': parse_list(arg.XYZ, 3, 'um/XYZ', True),
        'vol/VOL': parse_list(arg.vol, 3, 'vol/VOL'),
        'vol/xyz': parse_list(arg.xyz, 3, 'vol/xyz'),
    }
    # Define origin and volume size in world units
    world_XYZ = convert(given, ['um/XYZ'], ['um/world'])
    world_VOL = convert(given, ['um/VOL'], ['um/world'])
    given['world/VOL'] = world_VOL

    # Calculate subvolume size and offset in world units
    given['world/vol'] = convert(given, ['world/VOL'], ['vol/VOL'])
    world_xyz = convert(given, ['world/vol', 'vol/xyz'])
    world_vol = given['world/vol']

    # World per mesh and vox per world
    mul_scale = ['vox/mesh', 'nm/vox']
    world_mesh = convert(given, mul_scale, ['nm/world'])
    vox_world = convert(given, ['nm/world'], ['nm/vox'])

    # Assert nonzero scale and shape
    for key in ['vox/mesh', 'um/VOL']:
        raise_nonzero(key, given[key])

    # Assert subvolume offset within full volume
    if any([v>=V for v,V in zip(world_xyz, world_VOL)]):
        msg = 'vol/xyz must be below {}'.format(given['vol/VOL'])
        raise err.ListParseError(msg, 'vol/xyz', given['vol/xyz'])

    # Relabel output 
    return {
        'origin': world_XYZ,
        'offset': world_xyz,
        'volume': world_VOL,
        'subvolume': world_vol,
        'from_mesh': world_mesh,
        'to_um': given['um/world'],
        'to_vox': vox_world,
    }
