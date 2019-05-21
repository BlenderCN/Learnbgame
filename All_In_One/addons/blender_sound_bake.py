import math
import operator

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty
from bpy_extras.io_utils import ImportHelper

bl_info = {
    "name": "Bake Sound Spectrum",
    "author": "Matt Reid",
    "version": (0, 0, 1),
    "blender": (2, 73, 0),
    "location": "File > Import > Bake Sound Spectrum",
    "description": "Audio visualization with some cubes", 
    "warning": "",
    "category": "Animation",
}

def find_sound_clip():
    vse = bpy.context.scene.sequence_editor
    for clip in vse.sequences_all:
        if clip.type == 'SOUND':
            return clip

def ensure_areas_in_viewport(*args):
    in_viewport = {}
    not_in_viewport = set()
    areas_modified = {}
    screen = bpy.context.screen
    def find_area(area_type):
        for i, area in enumerate(screen.areas):
            if area.type == area_type:
                return i, area
        return None, None
    for arg in args:
        i, area = find_area(arg)
        if i is not None:
            in_viewport[i] = arg
        else:
            not_in_viewport.add(arg)
    for area_type in not_in_viewport:
        _i = None
        _area = None
        for i, area in enumerate(screen.areas):
            if i not in in_viewport:
                _i = i
                _area = area
                break
        areas_modified[_i] = {'old':_area.type, 'current':area_type}
        _area.type = area_type
    return areas_modified
    
def restore_areas(areas_modified):
    screen = bpy.context.screen
    for i, d in areas_modified.items():
        screen.areas[i].type = d['old']
    
def get_screen(screen_type):
    screen = bpy.context.screen
    window = bpy.context.window
    for area in screen.areas:
        if area.type == screen_type:
            return {'window':window, 'screen':screen, 'area':area}
    
def bake_sound(**kwargs):
    obj = kwargs.get('obj')
    sound_file = kwargs.get('file')
    freq_range = kwargs.get('range')
    attack = kwargs.get('attack', .005)
    release = kwargs.get('release', .2)
    def build_keyframe():
        obj.keyframe_insert(data_path='scale', index=2, frame=1)
    def do_bake():
        bpy.ops.graph.sound_bake(filepath=sound_file, low=freq_range[0], high=freq_range[1],
                                 attack=attack, release=release)
    build_keyframe()
    override = get_screen('GRAPH_EDITOR')
    bpy.ops.screen.screen_full_area(override)
    do_bake()
    bpy.ops.screen.back_to_previous()
    

CENTER_FREQUENCY = 1000.
FREQUENCY_RANGE = [20., 20000.]

class FreqBand():
    def __init__(self, **kwargs):
        self.index = kwargs.get('index')
        self.octave_divisor = kwargs.get('octave_divisor', 1.)
        self.center = self.calc_center()
        self.range = self.calc_range()
    def calc_center(self):
        f = CENTER_FREQUENCY
        if self.index == 0.:
            return f
        count = int(self.index)
        if self.index > 0.:
            op = operator.mul
        else:
            op = operator.truediv
            count *= -1
        for i in range(count):
            f = op(f, 2 ** (1. / self.octave_divisor))
        return f
    def calc_range(self):
        f = self.center
        lower = f / (2 ** (1. / self.octave_divisor / 2.))
        upper = f * (2 ** (1. / self.octave_divisor / 2.))
        if lower < FREQUENCY_RANGE[0]:
            lower = FREQUENCY_RANGE[0]
        if upper > FREQUENCY_RANGE[1]:
            upper = FREQUENCY_RANGE[1]
        return [lower, upper]
    def __str__(self):
        return '%s<%s>%s' % (self.range[0], self.center, self.range[1])
class Spectrum():
    def __init__(self, **kwargs):
        self.octave_divisor = kwargs.get('octave_divisor', 1.)
        self.bands = {}
        self.build_bands()
    def build_bands(self):
        center = CENTER_FREQUENCY
        i = 0.
        while center < FREQUENCY_RANGE[1]:
            band = FreqBand(index=i, octave_divisor=self.octave_divisor)
            center = band.center
            if center > FREQUENCY_RANGE[1]:
                break
            self.bands[center] = band
            i += 1.
        center = CENTER_FREQUENCY
        i = 0.
        while center > FREQUENCY_RANGE[0]:
            band = FreqBand(index=i, octave_divisor=self.octave_divisor)
            center = band.center
            if center < FREQUENCY_RANGE[0]:
                break
            i -= 1.
            if center in self.bands:
                continue
            self.bands[center] = band
    def iterkeys(self):
        for key in sorted(self.bands.keys()):
            yield key
    def itervalues(self):
        for key in self.iterkeys():
            yield self.bands[key]
    def iteritems(self):
        for key in self.iterkeys():
            yield key, self.bands[key]
    def keys(self):
        return [key for key in self.iterkeys()]
    def values(self):
        return [val for val in self.itervalues()]
    def items(self):
        return [(key, val) for key, val in self.iteritems()]

def build_base_cube(**kwargs):
    name = kwargs.get('name', 'soundbake.cube')
    data_name = kwargs.get('data_name', 'soundbake.cube')
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = data_name
    obj.location = [0., 0., 0.]
    return obj
    
class Cube():
    def __init__(self, **kwargs):
        self.band = kwargs.get('band')
        self.offset_index = kwargs.get('offset_index', 0)
        self.parent = kwargs.get('parent')
        self.mesh = kwargs.get('mesh')
        self.material = kwargs.get('material')
        self.name = 'soundbake.cube.%s.%03d' % (self.band.center, self.offset_index)
        if self.mesh is None:
            self.obj = build_base_cube(name=self.name)
            self.mesh = self.obj.data
            if self.material is None:
                bpy.ops.material.new()
                self.material = bpy.data.materials[len(bpy.data.materials)-1]
                self.material.name = 'soundbake.cube'
            self.mesh.materials.append(self.material)
        else:
            bpy.ops.object.add(type='MESH')
            self.obj = bpy.context.active_object
            self.obj.data = self.mesh
            self.obj.name = self.name
        self.update_scene()
        y = self.offset_index * 2.
        if isinstance(self.parent, Cube):
            x = 0.
            pobj = self.parent.obj
        else:
            x = self.band.index * 2.
            self.obj.delta_scale = [1., 1., math.log10(self.band.center)]
            pobj = self.parent
        self.obj.location = [x, y, 0.]
        self.obj.parent = pobj
        self.update_scene()
    @property
    def need_update(self):
        return self.obj.is_updated or self.obj.is_updated_data
    def update_scene(self):
        if not self.need_update:
            return
        bpy.context.scene.update()
    def set_slow_parent(self):
        self.update_scene()
        self.obj.use_slow_parent = True
        self.obj.use_extra_recalc_object = True
        self.obj.slow_parent_offset = self.offset_index / 2.
        self.update_scene()
    
    
class BakedCube(Cube):
    def __init__(self, **kwargs):
        super(BakedCube, self).__init__(**kwargs)
        self.offset_count = kwargs.get('offset_count', 10)
        self.children = {}
        ckwargs = dict(parent=self, band=self.band, mesh=self.mesh)
        for i in range(1, self.offset_count + 1):
            ckwargs['offset_index'] = i
            cube = Cube(**ckwargs)
            self.children[i] = cube
    def bake_sound(self, filename):
        for obj in bpy.context.selected_objects:
            obj.select = False
        self.obj.select = True
        bake_sound(obj=self.obj, file=filename, range=self.band.range)
        self.update_scene()
        for i in sorted(self.children):
            child = self.children[i]
            child.set_slow_parent()
        
def setup_scene(**kwargs):
    areas_modified = ensure_areas_in_viewport('VIEW_3D', 'GRAPH_EDITOR')
    octave_divisor = kwargs.get('octave_divisor', 1.)
    offset_count = kwargs.get('offset_count', 10)
    filepath = kwargs.get('filepath')
    bpy.ops.object.add(type='EMPTY', location=[0., 0., 0.])
    parent = bpy.context.active_object
    spectrum = Spectrum(octave_divisor=octave_divisor)
    cubes = []
    ckwargs = dict(parent=parent, offset_count=offset_count)
    for key, band in spectrum.iteritems():
        ckwargs['band'] = band
        cube = BakedCube(**ckwargs)
        cubes.append(cube)
        if ckwargs.get('mesh') is None:
            ckwargs['mesh'] = cube.mesh
    if filepath is None:
        clip = find_sound_clip()
        filepath = clip.filepath
    for cube in cubes:
        cube.bake_sound(filepath)
    #bpy.context.scene.frame_end = clip.frame_final_duration
    restore_areas(areas_modified)
    
class BakeSoundSpectrum(Operator, ImportHelper):
    """Bake a sound file into an audio visualization"""
    bl_idname = 'bake_sound.spectrum'
    bl_label = 'Bake Sound Spectrum'
    bl_options = {'REGISTER', 'UNDO'}
    octave_divisor = FloatProperty(name='Band Divisor', 
        description='Divisor to use for each band (Use "1" for a full octave, "3" for 3rd octave).\nHigher values will make more cubes', 
        default=1.)
    offset_count = IntProperty(name='Offset Count', 
        description='Number of cubes to add behind each band with an animation offset', 
        default=10)
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label('Options:')
        row = box.row()
        row.prop(self, 'octave_divisor')
        row = box.row()
        row.prop(self, 'offset_count')
    def execute(self, context):
        setup_scene(octave_divisor=self.octave_divisor, 
                    offset_count=self.offset_count, 
                    filepath=self.filepath)
        return {'FINISHED'}
    
def menu_func_import(self, context):
    self.layout.operator(BakeSoundSpectrum.bl_idname, text='Bake Sound Spectrum')
    
def register():
    bpy.utils.register_class(BakeSoundSpectrum)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    
def unregister():
    bpy.utils.unregister_class(BakeSoundSpectrum)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    
if __name__ == '__main__':
    register()
