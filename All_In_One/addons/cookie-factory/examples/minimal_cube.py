import core
from math import pi
PI, TAU = pi, 2*pi


class Composition(core.scene.Scene):
    def setup(self):
        # Create a simple scene with target, camera and sun
        core.simple_scene((0, 0, 0), (-5, -13, 5), (-10, -10, 4))

        # Create a cube object of size 5
        self.obj = core.geometry.cube(size=5)

    def draw(self):
        # Set t to be in the range between 0 and 1
        t = self.frame / self.frames

        # Rotate the cube for one full rotation on two rotation axis
        self.obj.rotation_euler = (0, t*TAU, t*TAU)
