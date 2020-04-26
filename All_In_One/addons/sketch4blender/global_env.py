from copy     import deepcopy

from .geometry import Transform, Point
from .opts     import Options

def bits(num):
    return 1 << num

class GlobalEnv(object):
    EXTENT   = 0
    BASELINE = 1
    OPTS     = 2
    FRAME    = 3
    SPLIT    = 4
    CAMERA   = 8
    LANGUAGE = 9

    def __init__(self):
        self.set_mask = 0
        self.camera   = Transform.Identity(4)
        self.bb1      = Point()
        self.bb2      = Point()
        self.opts     = None
        self.frame    = ""
        self.language = 0
        self.baseline = 0.0

    def is_set_p(self, num):
        return self.set_mask & bits(num)

    def check_set_p(flag):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if self.is_set_p(flag):
                    return
                self.set_mask |= flag
                func(self, *args, **kwargs)
            return wrapper
        return decorator

    @check_set_p(bits(OPTS))
    def set_opts(self, opts, line):
        self.opts = Options(opts, line)

    @check_set_p(bits(BASELINE))
    def set_baseline(self, baseline, line):
        if baseline == None:
            return
        self.baseline = baseline

    @check_set_p(bits(EXTENT))
    def set_extent(self, p1, p2, line):
        self.bb1 = deepcopy(p1)
        self.bb2 = deepcopy(p2)

    @check_set_p(bits(CAMERA))
    def set_camera(self, camera, line):
        self.camera = camera

    @check_set_p(bits(FRAME))
    def set_frame(self, opts, line):
        self.frame = opts

    @check_set_p(bits(LANGUAGE))
    def set_output_language(self, lang, line):
        self.language = lang

    def get_transformed_extent(self):
        if self.is_set_p(self.EXTENT):
            return None

