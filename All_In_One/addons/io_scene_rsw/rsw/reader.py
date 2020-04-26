from ..io.reader import BinaryFileReader
from .rsw import Rsw
from ..semver.version import Version

RSW_OBJECT_TYPE_MODEL = 1
RSW_OBJECT_TYPE_LIGHT = 2
RSW_OBJECT_TYPE_SOUND = 3
RSW_OBJECT_TYPE_EFFECT = 4


class RswReader(object):
    def __init__(self):
        pass

    @staticmethod
    def from_file(path):
        rsw = Rsw()
        with open(path, 'rb') as f:
            reader = BinaryFileReader(f)
            magic = reader.read('4s')[0]
            if magic != b'GRSW':
                raise RuntimeError('Invalid file type.')
            version = Version(*reader.read('2B'))
            rsw.ini_file = reader.read_fixed_length_null_terminated_string(40)
            rsw.gnd_file = reader.read_fixed_length_null_terminated_string(40)
            if version >= Version(1, 4):
                rsw.gat_file = reader.read_fixed_length_null_terminated_string(40)
            rsw.src_file = reader.read_fixed_length_null_terminated_string(40)
            # WATER
            if version >= Version(1, 3):
                rsw.water.height = reader.read('f')[0]
            if version >= Version(1, 8):
                rsw.water.type = reader.read('I')[0]
                rsw.water.amplitude = reader.read('f')[0]
                rsw.water.phase = reader.read('f')[0]
                rsw.water.surface_curve_level = reader.read('f')[0]
            if version >= Version(1, 9):
                rsw.water.texture_cycling = reader.read('I')[0]
            # LIGHT
            if version >= Version(1, 5):
                rsw.light.longitude, rsw.light.latitude = reader.read('2I')  # garbo? (45, 15)

            rsw.light.diffuse = reader.read('3f')
            rsw.light.ambient = reader.read('3f')
            rsw.light.alpha = reader.read('f')[0]

            # GROUND
            if version >= Version(1, 6):
                top, bottom, left, right = reader.read('4I')
            # unknown = reader.read('I')[0]
            object_count = reader.read('I')[0]
            for i in range(object_count):
                object_type = reader.read('I')[0]
                if object_type == RSW_OBJECT_TYPE_MODEL:
                    model = Rsw.Model()
                    if version >= Version(1, 3):
                        model.name = reader.read_fixed_length_null_terminated_string(40)
                        model.animation_type = reader.read('I')[0]
                        model.animation_speed = reader.read('f')[0]
                        model.block_type = reader.read('I')[0]
                    model.filename = reader.read_fixed_length_null_terminated_string(80)
                    model.node_name = reader.read_fixed_length_null_terminated_string(80)
                    model.position = reader.read('3f')
                    model.rotation = reader.read('3f')
                    model.scale = reader.read('3f')
                    rsw.models.append(model)
                elif object_type == RSW_OBJECT_TYPE_LIGHT:
                    light = Rsw.LightSource()
                    light.name = reader.read_fixed_length_null_terminated_string(80)
                    light.position = reader.read('3f')
                    light.color = reader.read('3I')
                    light.range = reader.read('f')[0]
                    rsw.light_sources.append(light)
                elif object_type == RSW_OBJECT_TYPE_SOUND:
                    sound = Rsw.Sound()
                    sound.name = reader.read_fixed_length_null_terminated_string(80)
                    sound.file_name = reader.read_fixed_length_null_terminated_string(80)
                    sound.position = reader.read('3f')
                    sound.volume = reader.read('f')[0]
                    sound.width = reader.read('I')[0]
                    sound.height = reader.read('I')[0]
                    sound.range = reader.read('I')[0]
                    if version >= Version(2, 0):
                        sound.cycle = reader.read('f')[0]
                    rsw.sounds.append(sound)
                elif object_type == RSW_OBJECT_TYPE_EFFECT:
                    effect = Rsw.Effect()
                    effect.name = reader.read_fixed_length_null_terminated_string(80)
                    effect.position = reader.read('3f')
                    effect.type = reader.read('I')[0]
                    effect.emit_speed = reader.read('f')[0]
                    effect.param = reader.read('4f')
                    rsw.effects.append(effect)
                else:
                    raise RuntimeError('Invalid object type.')
            # QUAD TREE
            if version >= Version(2, 1):
                # Not necessary for our purposes, so just ignore it.
                pass
        return rsw
