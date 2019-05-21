import bpy
import bpy_extras
import bmesh


def _dragon(turn):
    flip_count = 0
    cur_bit = turn % 2
    while turn > 0:
        turn = turn // 2
        if turn % 2 is not cur_bit:
            cur_bit = turn % 2
            flip_count += 1
    return flip_count % 4


def _fold(direction):
    if direction == 0:
        return (0, 1)

    if direction == 1:
        return (1, 0)

    if direction == 2:
        return (0, -1)

    if direction == 3:
        return (-1, 0)

    else:
        raise ValueError


def _create_dragon(self, context):
    me = bpy.data.meshes.new('dragonMesh')

    ob = bpy.data.objects.new('DragonCurve', me)

    bpy.context.scene.objects.link(ob)

    bm = bmesh.new()  # create an empty BMesh
    bm.from_mesh(me)  # fill it in from a Mesh

    cur_vec = (0.0, 0.0, 0.0)
    last_v1 = bm.verts.new(cur_vec)
    last_v2 = bm.verts.new((cur_vec[0], cur_vec[1] + 1, cur_vec[2]))

    for cur_turn in range(1, self.count):
        dir_vec = _fold(_dragon(cur_turn))

        cur_vec = (cur_vec[0] + dir_vec[0],
                   cur_vec[1], cur_vec[2] + dir_vec[1])
        cur_v1 = bm.verts.new(cur_vec)
        cur_v2 = bm.verts.new((cur_vec[0], cur_vec[1] + 1, cur_vec[2]))

        bm.verts.index_update()
        bm.faces.new((last_v1, last_v2, cur_v2, cur_v1))

        last_v1 = cur_v1
        last_v2 = cur_v2

    # if self.merge_vertices:
    #    print(str(bpy.context.area.type))
    #    bpy.ops.mesh.remove_doubles()

    bm.to_mesh(me)


class DragonCurve_add_object(bpy.types.Operator,
                             bpy_extras.object_utils.AddObjectHelper):
    """Create a new Dragon Curve"""
    bl_idname = "mesh.add_dragoncurve"
    bl_label = "Add Dragon Curve"
    bl_options = {'REGISTER', 'UNDO'}

    count = bpy.props.IntProperty(
        name="Edge Count",
        default=100,
        min=1,
        soft_min=1,
        subtype='UNSIGNED',
        description="Number of squares the dragon will consist of",
    )

    def iteration_update(self, context):
        self.count = 2 ** self.iteration

    iteration = bpy.props.IntProperty(
        name="Iteration Count",
        default=2,
        min=1,
        soft_min=1,
        soft_max=10,
        subtype='UNSIGNED',
        description="Number of iterations of the dragon curve",
        update=iteration_update)

    merge_vertices = bpy.props.BoolProperty(
        name="Merge vertices",
        description="Remove duplicate vertices",
        default=True
    )

    def execute(self, context):

        _create_dragon(self, context)

        return {'FINISHED'}
