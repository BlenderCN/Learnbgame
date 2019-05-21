import math

if __name__ is not None and "." in __name__:
    from .lsystem.literal_semantic import (DrawTerminal, MoveTerminal, PopTerminal,
                                           PushTerminal, RotateTerminal)
    from .lsystem.lsystem_class import Lsystem
    from .util.timer import Timer
    from .util.vector import Vector
else:
    from lsystem.literal_semantic import (DrawTerminal, MoveTerminal, PopTerminal,
                                          PushTerminal, RotateTerminal)
    from lsystem.lsystem_class import Lsystem
    from util.timer import Timer
    from util.vector import Vector


try:
    import bpy
except ImportError:
    print("Could not locate blender python module, testing environment only")


class FractalUpdate:
    """Helper to update the callback"""

    def __init__(self, max_count, callback):
        self._update_callback = callback

        self._max_count = max_count
        self._tick_count = max(self._max_count // 100, 1)
        self._ticks = 0
        self._count = 0

    def __enter__(self):
        print("Expected ticks: " + str(self._max_count))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Needed ticks: " + str(self._ticks * self._tick_count + self._count))

    def update_tick(self):
        self._count += 1
        if self._count > self._tick_count:
            self._ticks += self._count // self._tick_count
            self._count = self._count % self._tick_count
            self._update_callback(self._ticks)


class FractalGen:

    def __init__(self, level: int, lsystem: Lsystem, update_callback, start_point=(0, 0, 0)):

        self._lsystem = lsystem
        self._level = level

        self._updater = FractalUpdate(
            self._lsystem.approx_steps(level), update_callback)

        self.position_stack = [Vector(*start_point)]
        self.rotation_stack = [Vector(0, 1, 0)]
        self.look_at_stack = [Vector(1, 0, 0)]
        self.verts_stack = [0]

        self.moved = False

        self.verts = [self.position_stack[-1].values]
        self.edges = []

        self.stacks = [self.position_stack,
                       self.rotation_stack,
                       self.look_at_stack,
                       self.verts_stack]

        self._timings = {x: 0 for x in (
            "Rotate", "Move", "Draw", "Push", "Pop")}

    def _move(self, terminal: MoveTerminal):
        self.moved = True
        self.position_stack[-1] += self.rotation_stack[-1] * terminal.distance

    def _draw(self, terminal: DrawTerminal):
        if self.moved:
            self.verts.append(self.position_stack[-1].values)
            self.verts_stack[-1] = len(self.verts) - 1
            self.moved = False
        self.position_stack[-1] += self.rotation_stack[-1] * terminal.distance
        self.verts.append(self.position_stack[-1].values)
        self.edges.append((self.verts_stack[-1], len(self.verts) - 1))
        self.verts_stack[-1] = len(self.verts) - 1


    @staticmethod
    def _axis_rotate(rot_axis, axis, degree):
        return rot_axis * (rot_axis * axis) + \
            math.cos(math.radians(degree)) * (rot_axis.cross(axis)).cross(rot_axis) + \
            math.sin(math.radians(degree)) * (rot_axis.cross(axis))

    def _rotate(self, rotation: RotateTerminal):
        self.rotation_stack[-1] = \
            self._axis_rotate(self.look_at_stack[-1],
                              self.rotation_stack[-1],
                              rotation[0])

        if rotation[1] != 0:
            rot_axis = self.rotation_stack[-1].cross(self.look_at_stack[-1])
            self.rotation_stack[-1] = \
                self._axis_rotate(rot_axis,
                                  self.rotation_stack[-1],
                                  rotation[1])

            self.look_at_stack[-1] = \
                self._axis_rotate(rot_axis,
                                  self.look_at_stack[-1],
                                  rotation[1])

    def _push(self, _terminal: PushTerminal):
        for stack in self.stacks:
            stack.append(stack[-1])

    def _pop(self, _terminal: PopTerminal):
        for stack in self.stacks:
            stack.pop()

    _terminal_mapping = {RotateTerminal: ("Rotate", _rotate),
                         MoveTerminal: ("Move", _move),
                         DrawTerminal: ("Draw", _draw),
                         PushTerminal: ("Push", _push),
                         PopTerminal: ("Pop", _pop)}

    def _handle_command(self, command):
        if type(command) not in FractalGen._terminal_mapping:
            raise RuntimeError(str(command))

        handler_name, handler_func = FractalGen._terminal_mapping[type(
            command)]

        timer = Timer()
        with timer:
            handler_func(self, command)
        self._timings[handler_name] += timer.msecs

    def _print_timings(self):
        for command in self._timings:
            print("%7s: %.4f" % (command, self._timings[command]))

    def _apply_node(self):
        profile_mesh = bpy.data.meshes.new("FractalMesh")
        profile_mesh.from_pydata(self.verts, self.edges, [])
        profile_mesh.update()

        profile_object = bpy.data.objects.new("Fractal", profile_mesh)
        profile_object.data = profile_mesh

        scene = bpy.context.scene
        scene.objects.link(profile_object)
        profile_object.select = True

    def draw_vertices(self):
        """Generates the vertices based on the given lsystem and level"""

        with self._updater:
            with Timer("Node gen", True):
                for command in self._lsystem.start.iterate(self._level):
                    self._updater.update_tick()
                    self._handle_command(command)


        self._print_timings()

        with Timer("Node apply", True):
            self._apply_node()
