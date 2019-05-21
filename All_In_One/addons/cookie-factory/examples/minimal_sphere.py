import core
from math import sin, cos, pi
PI, TAU = pi, 2*pi


class Composition(core.scene.Scene):
    def setup(self):
        # Create a simple scene with target, camera and sun
        core.simple_scene((0, 0, 0), (0, -13, 0), (-10, -10, 4))

        # Create a list of 3 icospheres
        self.objects = [core.geometry.icosphere(diameter=1.5)
                        for i in range(3)]

    def draw(self):
        t = self.frame / self.frames

        radius = 3
        for i, obj in enumerate(self.objects):
            k = i / len(self.objects)
            phi = TAU*k

            x = radius*sin(TAU*t + PI   + phi)
            y = radius*sin(TAU*t + PI/2 + phi)
            z = radius*sin(TAU*t + PI/3 + phi)

            x_scale = sin(2*TAU*t + phi)*0.25 + 0.5
            y_scale = sin(1*TAU*t + phi)*0.25 + 0.5
            z_scale = sin(3*TAU*t + phi)*0.25 + 0.5

            obj.location = (x, y, z)
            obj.scale = (x_scale, y_scale, z_scale)
