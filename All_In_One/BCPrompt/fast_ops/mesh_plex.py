import bpy


def main(caller, context):

    print("\n" + ("=" * 50))

    cobject = bpy.context.active_object
    bpy.ops.object.mode_set(mode='OBJECT')

    idx_vert_list = []
    for i in cobject.data.vertices:
        idx_vert_list.append([i.index, i.co])
        # print(i.co, i.index)

    # for i in idx_vert_list:
    #     print(i)

    # existing edges
    print("=== +")
    ex_edges = []
    existing_edges = []
    for i in cobject.data.edges:
        edge_keys = [i.vertices[0], i.vertices[1]]
        ex_edges.append(edge_keys)
        item = [i.index, edge_keys]
        existing_edges.append(item)
        # print(item)

    # proposed edges
    # print("    becomes")
    proposed_edges = []
    num_edges = len(existing_edges)
    for i in range(num_edges):
        item2 = [i, [i, i + 1]]
        proposed_edges.append(item2)
        # print(item2)

    # find first end point, discontinue after finding a lose end.
    current_sequence = []
    iteration = 0
    while(iteration <= num_edges):
        count_presence = 0
        for i in existing_edges:
            if iteration in i[1]:
                count_presence += 1

        # print("iteration: ", iteration, count_presence)
        if count_presence == 1:
            break
        iteration += 1

    init_num = iteration
    # print("end point", init_num)

    # find connected sequence
    seq_list = []
    glist = []

    def generate_ladder(starter, edge_key_list):

        def find_vert_connected(vert, mlist):
            if len(mlist) == 1:
                for g in mlist:
                    for k in g:
                        if k is not vert:
                            return(k, -1)

            for i in mlist:
                if vert in i:
                    idx = mlist.index(i)
                    for m in i:
                        if m is not vert:
                            return(m, idx)

        stairs = []
        while(True):
            stairs.append(starter)
            starter, idx = find_vert_connected(starter,  edge_key_list)
            if idx == -1:
                stairs.append(starter)
                break
            edge_key_list.pop(idx)
        return(stairs)

    seq_list = generate_ladder(init_num, ex_edges)

    # make verts and edges
    Verts = []
    Edges = []

    for i in range(len(idx_vert_list)):
        print(i)
        old_idx = seq_list[i]
        myVec = idx_vert_list[old_idx][1]
        Verts.append((myVec.x, myVec.y, myVec.z))

    # for i in Verts: print(i)

    for i in proposed_edges:
        Edges.append(tuple(i[1]))
    # print(Edges)

    bpy.ops.object.mode_set(mode='OBJECT')

    prof_mesh = bpy.data.meshes.new("test_mesh2")
    prof_mesh.from_pydata(Verts, Edges, [])
    prof_mesh.update()
    cobject.data = prof_mesh

    bpy.ops.object.mode_set(mode='EDIT')


class MeshPlexOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.sort_active_mesh_edgeloop"
    bl_label = "Simple Edge sorting"

    # @classmethod
    # def poll(cls, context):
    #     space = context.space_data
    #     return space.type == 'NODE_EDITOR'

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


def register():
    bpy.utils.register_class(MeshPlexOperator)


def unregister():
    bpy.utils.unregister_class(MeshPlexOperator)


if __name__ == "__main__":
    register()
