import bpy
from gpu_extras.batch import batch_for_shader


# get circle vertices on pos 2D by segments
def GenerateCircleVerts(position, radius, segments):
    from math import sin, cos, pi
    coords = []
    coords.append(position)
    mul = (1.0 / segments) * (pi * 2)
    for i in range(segments):
        coord = (sin(i * mul) * radius + position[0], cos(i * mul) * radius + position[1])
        coords.append(coord)
    return coords


# get circle triangles by segments
def GenerateCircleTris(segments, startID):
    triangles = []
    tri = startID
    for i in range(segments-1):
        tricomp = (startID, tri + 1, tri + 2)
        triangles.append(tricomp)
        tri += 1
    tricomp = (startID, tri, startID+1)
    triangles.append(tricomp)
    return triangles


# draw a circle on scene
def draw_circle_fill_2d(position, color, radius, segments=8, alpha=False):
    import gpu
    import bgl

    if alpha:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
    # create vertices
    coords = GenerateCircleVerts(position, radius, segments)
    # create triangles
    triangles = GenerateCircleTris(segments, 0)
    # set shader and draw
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=triangles)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


# draw multiple circle in one batch on screen
def draw_multicircles_fill_2d(positions, color, radius, segments=8, alpha=False):
    import gpu
    import bgl

    if alpha:
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

    coords = []
    triangles = []
    # create vertices
    for center in positions:
        actCoords = GenerateCircleVerts(center, radius, segments)
        coords.extend(actCoords)
    # create triangles
    for tris in range(len(positions)):
        actTris = GenerateCircleTris(segments, tris*(segments+1))
        triangles.extend(actTris)
    # set shader and draw
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=triangles)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
