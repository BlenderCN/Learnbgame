import bpy
import struct, base64, zlib
from itertools import combinations

from . import semver
from . import sizer
from . import log

def to_name_hash(_format, _values):
    name_bytes = struct.pack(_format, *_values)
    name_zip = zlib.compress(name_bytes)
    name_hash = base64.encodebytes(name_zip)
    return name_hash.decode('utf-8').rstrip('\n')

def get_name(given, item, keys=[]):
    name_fmt = ''
    name_vals = []
    if not keys:
        keys = item['Keys']['Name']
    # Add all name keywords
    for key in keys:
        name_vals += given[key]
        name_fmt += item['Types'][key]
    # Compress values into a unique name
    uniq = to_name_hash(name_fmt, name_vals)
    return "{}:{}".format(item['Name'], uniq)

def match(given, item, att=[]):
    # Attributes that may match
    if not att:
        att = item['Keys']['Name']
    att = set(att) & set(given.keys())
    n_att = len(att)
    # All possible groups
    bpy_groups = bpy.data.groups
    group_keys = bpy_groups.keys()
    def is_item(g):
        return g.startswith(item['Name'])
    group_keys = sorted(filter(is_item, group_keys))
    unmatched = set(map(bpy_groups.get, group_keys))
    # Check all combinations
    for d in range(n_att):
        # If combos differ by d attributes
        for c in combinations(att, n_att-d):
            name_c = get_name(given, item, c)
            # Yield any group that matches
            for g in unmatched:
                name_g = get_name(g, item, c)
                if name_g == name_c:
                    yield g, (n_att-d, n_att)
                    unmatched -= g
    # Yield unmatched groups
    for g in unmatched:
        yield g, (0, n_att)
    yield {}, (0, n_att)

def keywords(version, arg):
    given = sizer.get_scale(arg)
    # Add version number to given details
    given['tmp'] = getattr(arg,'tmp','tmp')
    given['version'] = version['Name']

    return given
    
def groups(versions, arg):

    version = versions[0]
    given = keywords(version, arg)
    # Get the size of world units
    world_um = max(given['to_um'])

    # Name, keys, values for all groups
    for scope, item in version['Items'].items():
        # Name group, get all keys and vlues
        props = {k:given[k] for k in item['Keys']['All']}
        name = get_name(given, item)
        if item['Type'] == 'Group':
            make_group(name, props)
            yield scope, name
        # Log keys and values for scale 
        for k in item['Keys']['SCALE']:
            log_scale(k, given[k], '%d μm' % world_um)

def make_group(name, props):
    msg = 'Using {}'
    # Create new group if no group matches
    if name not in bpy.data.groups.keys():
        bpy.ops.group.create(name=name)
        new_group = bpy.data.groups[name]
        # Fill all properties in group   
        for key, val in props.items():
            setattr(new_group, key, val)
        msg = 'Made new {}'

    log.yaml('Debug', msg.format(name))

def log_scale(k, v, world='1 BU'):
    default_fmt = '{1:g},{2:g},{3:g} × {0}'
    fmts = {
        'from': '1 {u} unit = {1:g},{2:g},{3:g} x {0}',
        'to': '{0} = {1:g},{2:g},{3:g} × {u} unit',
    }
    kw = k.split('_')
    fmt = fmts.get(kw[0], default_fmt)
    msg = fmt.format(world, *v, u=kw[-1])
    log.yaml(k, msg)
