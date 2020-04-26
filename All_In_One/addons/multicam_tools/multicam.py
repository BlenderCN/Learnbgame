import bpy

from .utils import MultiCamContext

class MultiCamFadeError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
        
class BlendObj(object):
    def __init__(self, **kwargs):
        self.children = set()
        p = self.parent = kwargs.get('parent')
        if p is not None:
            kwargs.setdefault('context', p.context)
        self.context = kwargs.get('context')
        self.blend_obj = kwargs.get('blend_obj')
        if hasattr(self.__class__, 'fcurve_property'):
            self.fcurve_property = self.__class__.fcurve_property
        if not hasattr(self, 'fcurve_property'):
            self.fcurve_property = kwargs.get('fcurve_property')
    @property
    def blend_obj(self):
        return getattr(self, '_blend_obj', None)
    @blend_obj.setter
    def blend_obj(self, value):
        old = self.blend_obj
        if value == old:
            return
        self._blend_obj = value
        self.on_blend_obj_set(value, old)
    def on_blend_obj_set(self, new, old):
        self._fcurve = None
    @property
    def context(self):
        context = getattr(self, '_context', None)
        if context is None:
            context = bpy.context
        return context
    @context.setter
    def context(self, value):
        old = getattr(self, '_context', None)
        if old == value:
            return
        self._context = value
        self.on_context_set(value, old)
    def on_context_set(self, new, old):
        self._fcurve = None
        for obj in self.children:
            obj.context = new
    @property
    def fcurve(self):
        fc = getattr(self, '_fcurve', None)
        if fc is None:
            fc = self._fcurve = self.get_fcurve()
        return fc
    def get_fcurve(self):
        path = self.blend_obj.path_from_id()
        action = self.context.scene.animation_data.action
        if action is None:
            return None
        prop = self.fcurve_property
        for fc in action.fcurves.values():
            if path not in fc.data_path:
                continue
            if fc.data_path.split('.')[-1] != prop:
                continue
            return fc
    def remove_fcurve(self):
        if self.fcurve is None:
            return
        action = self.context.scene.animation_data.action
        action.fcurves.remove(self.fcurve)
        self._fcurve = None
    def iter_keyframes(self):
        for kf in self.fcurve.keyframe_points.values():
            yield kf.co
    def insert_keyframe(self, frame, value, prop=None, **kwargs):
        if prop is None:
            prop = self.fcurve_property
        if self.fcurve is None:
            self.blend_obj.keyframe_insert(prop, frame=frame)
            kf = self.get_keyframe(frame)
            kf.co[1] = value
        else:
            kf = self.fcurve.keyframe_points.insert(frame, value)
        for key, val in kwargs.items():
            setattr(kf, key, val)
        return kf
    def get_keyframe(self, frame):
        for kf in self.fcurve.keyframe_points.values():
            if kf.co[0] == frame:
                return kf
    def add_child(self, cls, **kwargs):
        kwargs.setdefault('parent', self)
        obj = cls(**kwargs)
        self.children.add(obj)
        return obj
    def del_child(self, obj):
        self.children.discard(obj)
    
    
class MultiCam(BlendObj):
    fcurve_property = 'multicam_source'
    def __init__(self, **kwargs):
        super(MultiCam, self).__init__(**kwargs)
        self.mc_fader = self.add_child(MultiCamFade)
        self.cuts = {}
        self.strips = {}
    def bake_strips(self):
        if not len(self.cuts):
            self.build_cuts()
        self.build_strip_keyframes()
        self.blend_obj.mute = True
    def build_cuts(self):
        for frame, channel in self.iter_keyframes():
            self.cuts[frame] = channel
            if channel not in self.strips:
                self.get_strip_from_channel(channel)
    def build_fade(self, fade=None, frame=None):
        if fade is None and frame is not None:
            fade = self.mc_fader.build_fade(frame)
        if fade is None:
            return
        for channel in range(1, self.blend_obj.channel):
            if channel not in self.strips:
                self.get_strip_from_channel(channel)
            if channel not in self.strips:
                continue
            self.strips[channel].build_fade(fade)
    def build_fades(self):
        self.mc_fader.build_fades()
    def build_strip_keyframes(self):
        for strip in self.strips.values():
            strip.build_keyframes()
    def get_strip_from_channel(self, channel):
        for s in self.context.scene.sequence_editor.sequences:
            if s.channel == channel:
                source = self.add_child(MulticamSource, blend_obj=s)
                self.strips[channel] = source
                return source
                
class MultiCamFade(BlendObj):
    def __init__(self, **kwargs):
        self.multicam = kwargs.get('parent', kwargs.get('multicam'))
        self.fade_props = {}
        self.fades = {}
        super(MultiCamFade, self).__init__(**kwargs)
        if self.blend_obj is None:
            self.blend_obj = self.get_fade_prop_group()
    def on_blend_obj_set(self, new, old):
        for prop in self.fade_props.values():
            self.del_child(prop)
        self.fade_props.clear()
        self.fades.clear()
        if new is None:
            return
        self.get_fade_props()
    def get_fade_prop_group(self):
        mc_data_path = self.multicam.blend_obj.path_from_id()
        return self.context.scene.multicam_fader_properties.get(mc_data_path)
    def get_fade_props(self):
        action = self.context.scene.animation_data.action
        group_name = 'Multicam Fader (%s)' % (self.multicam.blend_obj.name)
        group = action.groups.get(group_name)
        for fc in group.channels:
            key = fc.data_path.split('.')[-1]
            fade_prop = self.add_child(MultiCamFadeProp, fcurve_property=key)
            self.fade_props[key] = fade_prop
    def build_fade(self, frame):
        self.build_fades(frame)
        return self.fades.get(frame)
    def build_fades(self, fade_frame=None):
        prop_iters = {}
        for key, prop in self.fade_props.items():
            prop_iters[key] = prop.iter_keyframes()
        def find_next_fade(frame=None):
            prop_vals = {'start':{}, 'end':{}}
            start_frame = None
            try:
                for key, prop in prop_iters.items():
                    frame, value = next(prop)
                    if start_frame is None:
                        start_frame = frame
                    elif frame != start_frame:
                        raise MultiCamFadeError('keyframes are not aligned: %s' % ({'frame':frame, 'prop_vals':prop_vals}))
                    prop_vals['start'][key] = value
            except StopIteration:
                return None, None, None
            end_frame = None
            for key, prop in prop_iters.items():
                frame, value = next(prop)
                if end_frame is None:
                    end_frame = frame
                elif frame != end_frame:
                    raise MultiCamFadeError('keyframes are not aligned: %s' % ({'frame':frame, 'prop_vals':prop_vals}))
                prop_vals['end'][key] = value
            return start_frame, end_frame, prop_vals
        while True:
            need_update = False
            start_frame, end_frame, prop_vals = find_next_fade()
            if start_frame is None:
                break
            if fade_frame is not None and fade_frame != start_frame:
                continue
            d = {
                'start_frame':start_frame, 
                'end_frame':end_frame, 
                'start_source':prop_vals['start']['start_source'], 
                'next_source':prop_vals['start']['next_source'], 
            }
            if start_frame not in self.fades:
                need_update = True
                self.fades[start_frame] = d
            else:
                for key, val in self.fades[start_frame].items():
                    if d[key] != val:
                        need_update = True
                        self.fades[start_frame][key] = d[key]
            if need_update:
                self.multicam.build_fade(d)
            if fade_frame is not None:
                break
            
class MultiCamFadeProp(BlendObj):
    def __init__(self, **kwargs):
        super(MultiCamFadeProp, self).__init__(**kwargs)
        self.blend_obj = self.parent.blend_obj
        
class MulticamSource(BlendObj):
    fcurve_property = 'blend_alpha'
    def __init__(self, **kwargs):
        super(MulticamSource, self).__init__(**kwargs)
        self.multicam = self.parent
        self.mc_fader = self.multicam.mc_fader
        self._keyframe_data = None
    @property
    def keyframe_data(self):
        d = self._keyframe_data
        if d is None:
            d = self._keyframe_data = self.build_keyframe_data()
        return d
    def build_keyframe_data(self):
        d = {}
        cuts = self.multicam.cuts
        channel = self.blend_obj.channel
        is_active = False
        is_first_keyframe = True
        for frame in sorted(cuts.keys()):
            cut = cuts[frame]
            if cut == channel:
                d[frame] = True
                is_active = True
            elif is_active:
                d[frame] = False
                is_active = False
            elif is_first_keyframe:
                d[frame] = False
            is_first_keyframe = False
        return d
    def build_fade(self, fade):
        channel = self.blend_obj.channel
        start_frame = fade['start_frame']
        end_frame = fade['end_frame']
        start_ch = fade['start_source']
        end_ch = fade['next_source']
        if channel < min([start_ch, end_ch]):
            ## this strip won't be affected
            return
        if start_ch == channel:
            if end_ch < channel:
                values = [1., 0.]
            else:
                values = [1., 1.]
        elif end_ch == channel:
            if start_ch < channel:
                values = [0., 1.]
            else:
                values = [1., 1.]
        elif channel > max([start_ch, end_ch]) or channel < max([start_ch, end_ch]):
            values = [0., 0.]
        else:
            return
        self.insert_keyframe(start_frame, values[0], interpolation='BEZIER')
        self.insert_keyframe(end_frame, values[1], interpolation='CONSTANT')
        self.insert_keyframe(end_frame+1, 1., interpolation='CONSTANT')
    def build_fades(self):
        for start_frame in sorted(self.mc_fader.fades.keys()):
            fade = self.mc_fader.fades[start_frame]
            self.build_fade(fade)
    def build_keyframes(self):
        self.remove_fcurve()
        for frame, is_active in self.keyframe_data.items():
            if is_active:
                value = 1.
            else:
                value = 0.
            self.insert_keyframe(frame, value, interpolation='CONSTANT')
    
class MultiCamBakeStrips(bpy.types.Operator, MultiCamContext):
    '''Bakes the mulicam source into the affected strips using opacity'''
    bl_idname = 'sequencer.bake_multicam_strips'
    bl_label = 'Bake Multicam Strips'
    def execute(self, context):
        mc = MultiCam(blend_obj=self.get_strip(context), 
                      context=context)
        mc.bake_strips()
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(MultiCamBakeStrips)
    
def unregister():
    bpy.utils.unregister_class(MultiCamBakeStrips)
