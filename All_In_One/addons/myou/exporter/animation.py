
def get_animation_data_strips(animation_data): # TODO add prefix?
    if not animation_data:
        return [[],[]]
    strips = []
    any_solo = False
    if animation_data.nla_tracks:
        any_solo = any([track.is_solo for track in animation_data.nla_tracks])
        for track in animation_data.nla_tracks:
            if (any_solo and not track.is_solo) or track.mute:
                # solo shot first
                continue
            for strip in track.strips:
                if strip.type == 'CLIP' and not strip.mute and strip.action:
                    # Strips are added in the correct order of evaluation
                    # (tracks are from bottom to top)
                    strips.append({
                        'type': 'CLIP',
                        'extrapolation': strip.extrapolation,
                        'blend_type': strip.blend_type,
                        'frame_start': strip.frame_start,
                        'frame_end': strip.frame_end,
                        'blend_in': strip.blend_in,
                        'blend_out': strip.blend_out,
                        'reversed': strip.use_reverse,
                        'action': strip.action.name,
                        'action_frame_start': strip.action_frame_start,
                        'action_frame_end': strip.action_frame_end,
                        'scale': strip.scale,
                        'repeat': strip.repeat,
                        'name': strip.name or strip.action.name,
                    })
    action = animation_data.action
    if action and action.fcurves:
        strips.append({
            'type': 'CLIP',
            'extrapolation': 'HOLD',
            'blend_type': 'REPLACE',
            'frame_start': action.frame_range[0],
            'frame_end': action.frame_range[1],
            'blend_in': 0,
            'blend_out': 0,
            'reversed': False,
            'action': action.name,
            'action_frame_start': action.frame_range[0],
            'action_frame_end': action.frame_range[1],
            'scale': 1,
            'repeat': 1,
        })
    drivers = []
    last_path = ''
    if animation_data.drivers:
        for driver in animation_data.drivers:
            if last_path != driver.data_path:
                last_path = driver.data_path
                drivers.append(driver.data_path)
    return [strips, drivers]


def action_to_json(action, ob):
    # ob is any object or material which uses this, to check for use_connect
    # TYPE, NAME, CHANNEL, list of keys for each element
    # 'object', '', 'location', [[x keys], [y keys], [z keys]]
    # 'pose', bone_name, 'location', [...]
    # 'shape', shape_name, '', [[keys]]
    # Format for each channel element: [flat list of point coords]
    # each point is 6 floats that represent:
    # left handle, point, right handle

    channels = {} # each key is the tuple (type, name, channel)

    CHANNEL_SIZES = {'position': 3,
                     'rotation': 4, # quats with W
                     'rotation_euler': 3,
                     'scale': 3,
                     'color': 4}
    for fcurve in action.fcurves:
        path = fcurve.data_path.rsplit('.',1)
        chan = path[-1].replace('location', 'position')\
                       .replace('rotation_quaternion', 'rotation')
        name = ''
        chan_size = 1
        if len(path) == 1:
            type = 'object'
        else:
            if path[0].startswith('pose.'):
                type, name, _ = path[0].split('"')
                type = 'pose'

                if not hasattr(ob.data, 'bones') or not name in ob.data.bones:
                    # don't animate this channel (a bone that no longer exists was animated)
                    continue

                bone = ob.data.bones[name]
                if chan == 'position' and bone.parent and bone.use_connect:
                    # don't animate this channel, in blender it doesn't affect
                    # but in the engine it produces undesired results
                    continue

            elif path[0].startswith('key_blocks'):
                type, name, _ = path[0].split('"')
                type = 'shape'
            elif ob.type in [
                    'SURFACE', 'WIRE', 'VOLUME', 'HALO', # Material
                    'SHADER']: # Material node tree
                type = 'material'
                chan = fcurve.data_path
                chan_size = 0
                for fcurve2 in action.fcurves:
                    if fcurve2.data_path == chan:
                        chan_size = max(fcurve2.array_index, chan_size)
                chan_size += 1
            else:
                print('Unknown fcurve path:', path[0], ob.type)
                continue
        k = type, name, chan
        if not k in channels:
            channels[k] = [[] for _ in range(CHANNEL_SIZES.get(chan, chan_size))]
        idx = fcurve.array_index
        if chan == 'rotation':
            idx = (idx - 1) % 4
        #print(k, fcurve.array_index)
        l = channels[k][idx]
        last_was_linear = False
        for k in fcurve.keyframe_points:
            p = [k.handle_left.x,
                 k.handle_left.y,
                 k.co.x, k.co.y,
                 k.handle_right.x,
                 k.handle_right.y]
            if last_was_linear:
                p[0] = p[2]
                p[1] = p[3]
                last_was_linear = False
            if k.interpolation == 'CONSTANT':
                p[4] = 1e200
                p[5] = p[3]
            elif k.interpolation == 'LINEAR':
                p[4] = p[2]
                p[5] = p[3]
                last_was_linear = True
            l.extend(p)

    final_action = {'type': 'ACTION',
                    'name': action.name,
                    'channels': [list(k)+[v] for (k,v) in channels.items()],
                    'markers': sorted([{
                        'name': m.name,
                        'frame': m.frame,
                        'camera': m.camera and m.camera.name or '',
                    } for m in action.pose_markers], key=lambda m:m['frame']),
    }

    return final_action
