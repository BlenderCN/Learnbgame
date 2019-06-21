
class Rsw(object):
    class Water(object):
        def __init__(self):
            self.height = 0.0
            self.type = 0
            self.amplitude = 0.0
            self.phase = 0.0
            self.surface_curve_level = 0.0
            self.texture_cycling = 0

    class Lighting(object):
        def __init__(self):
            self.longitude = 45
            self.latitude = 45
            self.ambient = (0.0, 0.0, 0.0)
            self.diffuse = (0.0, 0.0, 0.0)
            self.shadow = (0.0, 0.0, 0.0)
            self.alpha = 0.0

    class LightSource(object):
        def __init__(self):
            pass

    class Sound(object):
        def __init__(self):
            pass

    class Effect(object):
        def __init__(self):
            pass

    class Model(object):
        def __init__(self):
            self.name = ''
            self.filename = ''
            self.reserved = ''
            self.type = ''
            self.sound = ''
            self.position = (0.0, 0.0, 0.0)
            self.rotation = (0.0, 0.0, 0.0)
            self.scale = (1.0, 1.0, 1.0)

    def __init__(self):
        self.ini_file = ''
        self.gnd_file = ''
        self.gat_file = ''
        self.src_file = ''
        self.water = Rsw.Water()
        self.light = Rsw.Lighting()
        self.models = []
        self.light_sources = []
        self.sounds = []
        self.effects = []
        pass
