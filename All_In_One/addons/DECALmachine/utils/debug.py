import bpy
from mathutils import Vector, Matrix
import gpu
from gpu_extras.batch import batch_for_shader
import bgl


def debug_location_and_direction_in_world_space(self, location, direction):
    dircube = bpy.data.objects.get("dir")

    loc, rot, sca = dircube.matrix_world.decompose()
    newloc = Matrix.Translation(location)
    newrot = direction.to_track_quat('Z', 'X').to_matrix().to_4x4()
    newsca = Matrix()
    for i in range(3):
        newsca[i][i] = sca[i]

    newmx = newloc @ newrot @ newsca

    dircube.matrix_world = newmx



def draw_vector(vector, origin=Vector((0, 0, 0)), color=(1, 1, 1)):
    def draw():
        coords = [origin, origin + vector]

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()

        # bgl.glEnable(bgl.GL_BLEND)
        bgl.glDepthFunc(bgl.GL_ALWAYS)

        shader.uniform_float("color", (*color, 1))
        batch = batch_for_shader(shader, 'LINES', {"pos": coords})
        batch.draw(shader)

    bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_point(coords, color=(1, 1, 1)):
    def draw():
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()

        # bgl.glEnable(bgl.GL_BLEND)
        bgl.glDepthFunc(bgl.GL_ALWAYS)

        shader.uniform_float("color", (*color, 1))
        batch = batch_for_shader(shader, 'POINTS', {"pos": [coords]})
        batch.draw(shader)

    bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')
