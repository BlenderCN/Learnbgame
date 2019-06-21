# <pep8-80 compliant>
import bpy
from bpy.props import *
import re
from mathutils import Matrix, Vector, Color, Euler, Quaternion
from math import floor
import itertools
import sys

from sound_drivers.presets import note_from_freq


bpy_collections = ["scenes", "objects", "meshes", "materials", "textures",
        "speakers", "worlds", "curves", "armatures", "particles", "lattices",
        "shape_keys", "lamps", "cameras", "node_groups", "movie_clips", "metaballs"]

'''
# much nicer breaks Restricted Context TODO
bpy_collections = [k.identifier
                   for k in bpy.data.bl_rna.properties
                   if k.type == 'COLLECTION']
'''

def get_collection_from_idobject(obj):
    for col in bpy_collections:
        collection = getattr(bpy.data, col, None)
        if collection and obj.id_data in collection.values():
            return col
    return ""


icons = {'SCENE_DATA': ["scenes", "Scene", 'SCENE'],
         'OBJECT_DATA': ["objects", "Object", 'OBJECT'],
         'MESH_DATA': ["meshes"],
         'OUTLINER_OB_MESH': ["MESH"],
         'MATERIAL': ["materials"],
         'MATERIAL_DATA': ["Material"],
         'OUTLINER_OB_SURFACE': ["SURFACE"],
         'TEXTURE': ["textures", "CLOUDS", "Clouds Texture"],
         'SPEAKER': ["speakers"],
         'OUTLINER_OB_SPEAKER': ["SPEAKER"],
         'WORLD': ["worlds", "World"],
         'OUTLINER_OB_CURVE': ["curves"],
         'OUTLINER_OB_ARMATURE': ["armatures", "Armature", "ARMATURE"],
         'PARTICLES': ["particles", "EMITTER"],
         'OUTLINER_OB_LATTICE': ["lattices", "LATTICE"],
         'OUTLINER_DATA_LATTICE': ["Lattice"],
         'SHAPEKEY_DATA': ["shape_keys", "Key"],
         'OUTLINER_OB_META': ["metaballs"],
         'META_DATA': ["MetaBall", "META"],
         'SURFACE_DATA': ["Surface Curve"],
         'LAMP': ["lamps"],
         'OUTLINER_OB_CAMERA': ["CAMERA"],
         'OUTLINER_OB_FONT': ["FONT"],
         'FONT_DATA': ["Text Curve"],
         'OUTLINER_OB_EMPTY': ["EMPTY"],
         'OUTLINER_OB_LAMP': ["LAMP"],
         'NODETREE': ["node_groups", "NODETREE", "Compositor Node Tree"],
         'NODE': ["NODE"],
         'SEQUENCE': ["SEQUENCE"],
         'LAMP_SUN': ["SUN"],
         'LAMP_SPOT': ["SPOT"],
         'LAMP_HEMI': ["HEMI"],
         'LAMP_POINT': ["POINT"],
         'LAMP_AREA': ["AREA"],
         'MODIFIER': ["Modifier"],
         'CONSTRAINT': ["Constraint"],
         'CAMERA_DATA': ["cameras"]}


def splittime(secs, prec=2):
        t = float(secs)
        minutes = t // 60
        t %= 60
        seconds = floor(t)
        t = round(t - seconds, prec)
        p = 10 ** prec
        fraction = floor(p * (t))
        return (minutes, seconds, fraction % p)


def get_icon(desc):
    choices = [icon_name for icon_name, usage_list in icons.items()
               if desc in usage_list]
    if(len(choices)):
        return choices[0]
    else:
        print("No icon for", desc)
        pass
    return 'QUESTION'


def format_data_path(row, path, icon_only=False, padding=0):
    # look for material / texture in data path

    def rep_spaces(txt, to_spaces=False):
        if to_spaces:
            return txt.replace("+", " ")
        else:
            return txt.replace(" ", "+")

    rexps = [('MATERIAL', r'material_slots\[(\S+)\]\.material\.(\S+)'),
             ('TEXTURE', r'texture_slots\[(\S+)\]\.texture\.(\S+)'),
             ('TEXTURE', r'texture_slots\[(\S+)\]\.(\S+)'),
             ('MODIFIER', r'modifiers\[\"(\S+)\"\]\.(\S+)'),
             ('MODIFIER', r'modifiers\[(\S+)\]\.canvas_settings\.(\S+)'),
             ('CONSTRAINT', r'constraints\[(\S+)\]\.(\S+)'),
             ('SHAPEKEY_DATA', r'key_blocks\[(\S+)\]\.(\S+)'),
             ('COLOR', r'color'),
             ('NODE', r'nodes(\S+).(\S+)'),
             ('SEQUENCE', r'sequence_editor(\S+).(\S+)'),
              ]
    path = rep_spaces(path)
    for icon, regexp in rexps:
        name = ""
        m = re.match(regexp, path)
        # Material match
        if m is not None:
            padding -= 1
            if not icon_only:
                if len(m.groups()):
                    name = "[%s]" % rep_spaces(m.groups()[0], True)
                else:
                    name = "[%s]" % path
            row.label(icon=icon, text=name)
            if len(m.groups()) > 1:
                path = m.groups()[1]

    if not icon_only:
        #col.alignment = 'RIGHT'
        row.label(rep_spaces(path, True))
    if padding > 0:
        for i in range(padding):
            row.label(icon='BLANK1')


def icon_from_bpy_datapath(path):
    #print("ICDP", path)
    icons = ['SCENE', 'OBJECT_DATA', 'OUTLINER_OB_MESH', 'MATERIAL',
            'TEXTURE', 'SPEAKER',
            'WORLD', 'OUTLINER_OB_CURVE', 'OUTLINER_OB_ARMATURE',
            'PARTICLES', 'LATTICE_DATA',
            'SHAPEKEY_DATA', 'LAMP', 'CAMERA_DATA']

    if not len(path):
        return 'BLANK1'
    sp = path.split(".")
    # bug fix on pose bone constraints
    if len(sp) < 3:
        return 'BLANK1'
    
    sp =  sp[2].split('[')

    col = sp[-1].split('[')[0]
    #collection name will be index
    if col not in bpy_collections\
           or bpy_collections.index(col) >= len(icons):
        return 'BLANK1'

    return  icons[bpy_collections.index(col)]


def getAction(speaker, search=False):
    if not speaker:
        return None
    action = None
    if speaker.animation_data:
        action = speaker.animation_data.action
        if action is not None:
            if "bake_error" in action.keys():
                return None
            return action
        if speaker.animation_data.use_nla:
            # XXXXX
            #return speaker.animation_data.nla_tracks[0].strips[0].action
            return None
    return action

#FRAME change method to make the equalizer update live to panel


def getSpeaker(context, action=None):
    space = context.space_data
    if action is not None:
        for s in context.scene.soundspeakers:
            if s.animation_data.action == action\
               or action in [st.action
                        for t in s.animation_data.nla_tracks
                        for st in t.strips]:

                return s
    if space.type == 'PROPERTIES':
        if space.use_pin_id and space.pin_id.rna_type.identifier == 'Speaker':
            return space.pin_id

        if(context.active_object is not None
                and context.active_object.type == 'SPEAKER'):
            return context.active_object.data
    return context.scene.speaker


def strip_expression(exp, fname):
    def args(clist, **kwargs):
        return(clist, ["%s=%s" % (name, str(value))
                       for (name, value) in kwargs.items()])
    if not exp.startswith(fname):
        return [], []
    pe = exp[exp.find('[') + 1: exp.find(']')]

    sexp = exp.replace("[%s]" % pe, str(pe.split(",")))

    return eval(sexp.replace(fname, "args"))


def get_driver_settings_xxx(fcurve):
    reg_exps = [r'SoundDrive\(\[(\S+) \]\,(\S+)\)', r'SoundDrive\(\[(\S+)\]\)',
                r'SoundDrive\((\S+)\)']
    expression = fcurve.driver.expression
    return strip_expression(expression, "SoundDrive")

    match = False
    for i, regex in enumerate(reg_exps):
        m = re.match(regex, expression)
        if m is not None:
            match = True
            break

    channels = []  # Channels from expression
    var_channels = []  # channels from vars
    args = []

    if not match:
        pass

    elif i == 0:  # list only match
        channels.extend(m.groups()[0].split(","))
        args.extend(m.groups()[1].split(","))
    elif i == 1:  # list with vars
        channels.extend(m.groups()[0].split(","))
    elif i == 2:  # single var
        channels.append(m.groups()[0].split(",")[0])
        args = m.groups()[0].split(",")[1:]

    driver = fcurve.driver
    speakers = [speaker.id_data
                for speaker in bpy.data.speakers
                if speaker.get("vismode") is not None]

    var_channels = [var.name
                    for var in driver.variables
                    if expression.startswith("SoundDrive")
                    and var.targets[0] is not None
                    and var.targets[0].id in speakers]

    #TODO check lists fix expression remove dead vars
    return var_channels, args


def get_channel_index(channel_name):
    channel_name = channel_name.strip('"[').strip(']"')
    ch = [''.join(x[1])\
          for x in itertools.groupby(channel_name, lambda x: x.isalpha())]
    return ch[0], int(ch[1])


def get_driver_settings(fcurve):
    s = fcurve.driver.expression
    d = s.find("SoundDrive")
    if d > -1:
        m = s.find(")", d) + 1
        sdexpr = s[d:m][:]
        fmt = s.replace(sdexpr, "%s")
        s = sdexpr
    else:
        fmt = "%s"
    if not s.startswith("SoundDrive"):
        return([], [])
    # strip out whitespace
    s = re.sub(r'\s', '', s)

    driver_f = s[0:s.find('(')]

    s = s.strip("%s(" % driver_f)
    s = s[0:-1]

    # strip out channel_list

    pe = s[1:s.find(']')]

    channels = pe.split(",")
    d = [("==", "EQ"),
         (">=", "GTE"),
         ("<=", "LTE"),
         ("<", "LT"),
         (">", "GT")]
    #kwargs
    s = s.strip("[%s]" % pe)
    s = s.strip(",")
    for c, r in d:
        s = s.replace(c, r)
    kwargs = s.split(",")
    if kwargs == ['']:
        kwargs = []
    l = [a.split("=") for a in kwargs]

    return channels, kwargs


def driver_expr(expr, channels, args):
    #make a new driver expression from the channels and args
    s = expr
    ctxt = str(channels).replace("'", "").replace(" ", "")
    x = s.find("SoundDrive")
    if x > -1:
        m = s.find(")", x) + 1
        fmt = s.replace(s[x:m], "%s")
    else:
        fmt = "%s"
    new_expr = 'SoundDrive(%s' % (ctxt)
    for arg in args:
        new_expr = '%s,%s' % (new_expr, arg)
    new_expr = "%s)" % new_expr
    new_expr = new_expr.replace('[,', '[')  # no channels fecks things up
    return fmt % new_expr


def driver_filter_draw(layout, context):
    scene = context.scene
    if scene is None:
        return None
    object = context.object
    if object is None:
        return None
    drivers = False
    if object.animation_data and len(object.animation_data.drivers):
        drivers = True
    settings = scene.speaker_tool_settings
    row = layout.row(align=True)
    row.prop(settings, "use_filter", text="", icon="FILTER", toggle=True)
    row.label("FILTER")
    if not drivers and settings.filter_context:
        row.template_ID(context.scene.objects, 'active')
    else:
        row.prop(settings, "filter_object", icon='OBJECT_DATA', toggle=True,
            text="")
        if settings.filter_object:
            row.prop(settings, "filter_context", toggle=True,
                text="CONTEXT")
    row.prop(settings, "filter_world", icon='WORLD', toggle=True,
            text="")
    row.prop(settings, "filter_material", icon='MATERIAL', toggle=True,
            text="")
    row.prop(settings, "filter_texture", icon='TEXTURE', toggle=True,
            text="")
    row.prop(settings, "filter_monkey", icon='MONKEY', toggle=True,
            text="")
    row.prop(settings, "filter_speaker", icon='SPEAKER', toggle=True,
            text="")


def f(freq):
    #output a format in Hz or kHz
    if freq < 10:
        mHz = freq * 1000
        return("%dmHz" % mHz)
    if freq < 100:
        return("%.2fHz" % freq)
    if freq < 1000:
        return("%.1fHz" % freq)
    elif freq < 1000000:
        khz = freq / 1000
        return("%.2fkHz" % khz)
    return(" ")


def set_channel_idprop_rna(channel,
                           speaker_rna,
                           low,
                           high,
                           fc_range,
                           map_range,
                           is_music=False):
    #speaker_rna : saved on the action action min and max
    min_, max_ = min(fc_range), max(fc_range)
    map_min, map_max = min(map_range), max(map_range)

    # set the channel UI properties
    note = "C"
    if is_music:
        note = note_from_freq(low)
        desc = "%s (%s) (min:%.2f, max:%.2f)" %\
                    (note, f(low), min_, max_)
    else:
        desc = "Frequency %s to %s (min:%.2f, max:%.2f)" %\
                    (f(low),  f(high), min_, max_)
    speaker_rna[channel] = {"min": map_min,
                            "max": map_max,
                            "soft_min": map_min,
                            "soft_max": map_max,
                            "description": desc,
                            "low": low,
                            "high": high,
                            "a": min_,
                            "b": max_}

    # ugly hack for MIDI
    if is_music:
        speaker_rna[channel]["note"] = note

    return None

# utility function to remove all handlers by their string function name


def remove_handlers_by_prefix(prefix):
    handlers = bpy.app.handlers
    my_handlers = [getattr(handlers, name)
                   for name in dir(handlers)
                   if isinstance(getattr(handlers, name), list)]

    for h in my_handlers:
        fs = [f for f in h if callable(f) and f.__name__.startswith(prefix)]
        for f in fs:
            h.remove(f)


def selected_bbox(context):
    fmin = -sys.float_info.max
    fmax = sys.float_info.max
    sel = context.selected_objects
    if sel:
        bbox = [fmax, fmin, fmax, fmin, fmax, fmin]
        for ob in sel:
            mat = Matrix(ob.matrix_world)
            ob_bbox = ob.bound_box
            for k in range(0, 8):
                v = Vector(ob_bbox[k])
                v = mat * v
                bbox[0] = min(bbox[0], v[0])
                bbox[1] = max(bbox[1], v[0])
                bbox[2] = min(bbox[2], v[1])
                bbox[3] = max(bbox[3], v[1])
                bbox[4] = min(bbox[4], v[2])
                bbox[5] = max(bbox[5], v[2])
    else:
        bbox = (0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
    return bbox


def bbdim(b):
    bl = Vector((b[0], b[2], b[4]))
    tr = Vector((b[1], b[3], b[5]))
    v = tr - bl
    m = max(v)
    if m < 0.00001:
        m = 1
    for axis, val in enumerate(v):
        if abs(val) < 0.00001:
            v[axis] = m
    return v


def hasparent(obj, parent):
    while obj.parent:
        if obj.parent == parent:
            return True
        obj = obj.parent
    return False


def copy_sound_action(speaker, newname):
    '''
    Copy a sound action
    replace datapaths on speaker and action with new channel_name
    '''
    spk = speaker
    original_action = getAction(spk)
    action = original_action.copy()
    action.name = "SOUND_%s_%s" % (newname, speaker.sound.name)
    #spk.animation_data.action = action
    #action.name = 'FX'
    cn = action['channel_name']
    newname = unique_name(speaker.channels, newname)
    action["channel_name"] = newname

    channels = action['Channels']

    for fcurve in action.fcurves:
        dp = fcurve.data_path
        fcurve.data_path = dp.replace(cn, newname)

    action["rna"] = original_action["rna"].replace(cn, newname)
    spk['_RNA_UI'].update(eval(action["rna"]))
    # make new properties for the speaker.
    for i in range(channels):
        opn = "%s%d" % (cn, i)
        pn = "%s%d" % (newname, i)
        spk[pn] = spk[opn]
        continue
        oprop = spk['_RNA_UI'].get(opn)
        print("OPROP", oprop)
        if oprop:
            print("OPROP")
            ui_props = spk['_RNA_UI'].get(pn)
            if not ui_props:
                spk['_RNA_UI'][pn] = {}
            for k, v in oprop.items():
                if type(v) is float:
                    v = round(v, 4)
                spk['_RNA_UI'][pn][k] = v
                #ui_props[k] = v
    return action


def nla_drop(obj, action, frame, name, multi=False):
    if not multi:
        #check if there is already a strip with this action
        tracks = [s for t in obj.animation_data.nla_tracks
                  for s in t.strips
                  if s.action == action]
        if len(tracks):
            return None
    #add nla track (name) with action at frame
    nla_track = obj.animation_data.nla_tracks.new()
    nla_track.name = name
    strip = nla_track.strips.new(name, frame, action)


def validate_channel_name(context):
    '''
    return valid channel name
    '''
    chstr = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    speakers = [s.data for s in context.scene.objects if s.type == 'SPEAKER']
    channels = [c for sp in speakers for c in sp.channels]

    speaker = getSpeaker(context)
    sound = speaker.sound
    channel_name = sound.bakeoptions.channel_name

    flag = channel_name[0] in chstr\
        and (channel_name.isalpha())\
        and len(channel_name) == 2\
        and channel_name not in channels

    return flag


def unique_name(channels, ch, j=1):
    '''
    Return a unique 2 character name
    '''
    #leaving in O & I
    chstr = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    #removed numeric character, channel name A0 channel 0 => A00 yuck.
    #chstr = chstr if not j else "%s%s" % ("0123456789", chstr)

    gidx = chstr.find(ch[j])
    if ch in channels:
        for k in range(len(chstr)):
            idx = chstr.find(ch[j])
            idx = idx + 1
            if idx >= len(chstr):
                idx = 0

            if j:
                ch = "%c%c" % (ch[0], chstr[idx])
            else:
                ch = "%c%c" % (chstr[idx], ch[1])
            if idx == 0:
                j = 0
            else:
                j = 1
            return unique_name(channels, ch, j=j)
    return ch


def propfromtype(propdict, op):
    def default_array(p):
        return [v for v in p]

    ''' return a bpy.props.XxxProp from a bpy.types.XxxProp'''

    for key, p in op.bl_rna.properties.items():
        if key.startswith("filter_") or key in ["bl_rna"]:
            continue
        if hasattr(p, "options") and 'SKIP_SAVE' in getattr(p, "options"):
            continue

        prop_type = p.rna_type.identifier
        f = getattr(bpy.props, prop_type)

        if prop_type.startswith("String"):
            propdict[key] = f(name=getattr(p, "name"),
                            description=getattr(p, "description"),
                            default=getattr(p, "default"))

        if isinstance(p, bpy.types.IntProperty):
            propdict[key] = IntProperty(name=getattr(p, "name"),
                            description=getattr(p, "description"),
                            min=getattr(p, "hard_min"),
                            soft_min=getattr(p, "soft_min"),
                            max=getattr(p, "hard_max"),
                            soft_max=getattr(p, "soft_max"),

                            default=getattr(p, "default"))

        if prop_type.startswith("Float"):
            if getattr(p, "array_length", 0) > 1:
                default = default_array(getattr(p, "default_array"))
                f = FloatVectorProperty
                propdict[key] = f(name=getattr(p, "name"),
                                description=getattr(p, "description"),
                                min=getattr(p, "hard_min"),
                                soft_min=getattr(p, "soft_min"),
                                max=getattr(p, "hard_max"),
                                soft_max=getattr(p, "soft_max"),
                                subtype=getattr(p, 'subtype'),
                                size=getattr(p, "array_length"),
                                default=default)
            else:
                default = getattr(p, "default")
                propdict[key] = f(name=getattr(p, "name"),
                                description=getattr(p, "description"),
                                min=getattr(p, "hard_min"),
                                soft_min=getattr(p, "soft_min"),
                                max=getattr(p, "hard_max"),
                                soft_max=getattr(p, "soft_max"),
                                subtype=getattr(p, 'subtype'),
                                default=default)

        if prop_type.startswith("Bool"):
            if getattr(p, "array_length", 0) > 1:
                default = default_array(getattr(p, "default_array"))
                f = BoolVectorProperty
                subtype = getattr(p, 'subtype')
                if subtype == 'LAYER_MEMBERSHIP':
                    subtype = 'LAYER'

                propdict[key] = f(name=getattr(p, "name"),
                        description=getattr(p, "description"),
                        default=default,
                        size=getattr(p, "array_length"),
                        subtype=subtype)
            else:
                default = getattr(p, "default")
                propdict[key] = f(name=getattr(p, "name"),
                                description=getattr(p, "description"),
                                default=getattr(p, "default"),
                                )


def get_context_area(context, context_dict, area_type='GRAPH_EDITOR',
                     context_screen=False):
    '''
    context : the current context
    context_dict : a context dictionary. Will update area, screen, scene, 
                   area, region
    area_type: the type of area to search for
    context_screen: Boolean. If true only search in the context screen.
    '''
    if not context_screen:  # default
        screens = bpy.data.screens
    else:
        screens = [context.screen]
    for screen in screens:
        for area_index, area in screen.areas.items():
            if area.type == area_type:
                for region in area.regions:
                    if region.type == 'WINDOW':
                        context_dict["area"] = area
                        context_dict["screen"] = screen
                        context_dict["scene"] = context.scene
                        context_dict["window"] = context.window
                        context_dict["region"] = region
                        return area
    return None


def replace_speaker_action(speaker, action, new_action):
    speaker.animation_data.action = new_action
    strips = [s for t in speaker.animation_data.nla_tracks for s in t.strips if s.action == action]
    for s in strips:
        s.action = new_action
    action['wavfile'] = "TRASH"
    action.use_fake_user = False
    bpy.data.actions.remove(action)
    return None


def copy_driver(from_driver, target_fcurve):
    ''' copy driver '''
    td = target_fcurve.driver
    fd = from_driver.fcurve.driver
    td.type = fd.type
    td.expression = fd.expression
    for var in fd.variables:
        v = td.variables.new()
        v.name = var.name
        v.type = var.type
        if from_driver.is_monkey:
            continue
        for i, target in var.targets.items():
            if var.type == 'SINGLE_PROP':
                v.targets[i].id_type = target.id_type
                v.targets[i].data_path = target.data_path
            v.targets[i].id = target.id
            v.targets[i].transform_type = target.transform_type
            v.targets[i].transform_space = target.transform_space
            v.targets[i].bone_target = target.bone_target

def interp(value, f, t):
    m = (value - f[0]) / (f[1] - f[0])
    return t[0] + m * (t[1] - t[0])

def remove_draw_pend(paneltype, prefix):
    '''
    remove all functions with name beginning with prefix (pre/ap)pended to paneltype
    '''

    draw_funcs = [f for f in paneltype._dyn_ui_initialize()
                  if f.__name__.startswith(prefix)]
    
    for f in draw_funcs:
        paneltype.remove(f)

def split_path(data_path):
    '''
    Split a data_path into parts
    '''
    if not len(data_path):
        return []
     # remove all collection names   
    match = re.findall(r'\[\"(.*?)\"\]\.', data_path)

    namedic = {}
    for i, m in enumerate(match):
        key = "Collection___NAME________%d" % i # surely not lol.
        data_path = data_path.replace(m, key, 1)
        namedic[key] = m

    parts = data_path.rpartition(".")
    props = []
    while parts[0] != parts[1] != '':
        dp = parts[0]
        props.append(parts[2])
        parts = dp.rpartition(".")

    props.append(parts[2])

    # replace the names
    propstring = ",".join(props)
    for key, name in namedic.items():
        propstring = propstring.replace(key, name)
    props = propstring.split(",")

    # reverse list
    props.reverse()
    return props
    
def scale_actions(action1, action2):
    if action1 is None or action2 is None:
        return None
    scale = action1.frame_range.length / action2.frame_range.length
    #print(scale)
    for fcurve in action2.fcurves:
        for kfp in fcurve.keyframe_points:
            kfp.co.x *= scale
