import bpy
import bmesh
from mathutils import Vector

def store_ui_data(objects,canevas,rig):
    gamma = 1/2.2

    worldCanevasPoints = [canevas.matrix_world * Vector((p.co[0],p.co[1],0)) for p in canevas.data.splines[0].points]

    canevasX = [p[0] for p in worldCanevasPoints]
    canevasY = [p[1] for p in worldCanevasPoints]

    if rig.data.get('UI') :
        del rig.data['UI']

    for ob in objects :

        data = ob.to_mesh(bpy.context.scene,False,'PREVIEW')

        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.beautify_fill(bm,faces = bm.faces,edges=bm.edges)
        bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
        bmesh.ops.dissolve_limit(bm, angle_limit=0.001, verts=bm.verts, edges=bm.edges)

        bmesh.ops.connect_verts_concave(bm, faces=bm.faces)

        bm.to_mesh(data)
        data.update()
        bm.clear()


        points = []
        faces = []
        edges = []

        for p in data.vertices :
            point  = ob.matrix_world * Vector((p.co[0],p.co[1],0))

            x = (point[0]-min(canevasX)) / (max(canevasX)-min(canevasX))

            y = (point[1]-min(canevasY)) / (max(canevasY)-min(canevasY))

            points.append((round(x,5),round(y,5)))

        for f in data.polygons :
            faces.append(tuple([v for v in f.vertices]))

        if not faces :
            for e in data.edges :
                edges.append(tuple([v for v in e.vertices]))

        #print(points,faces,edges)


        colors = ob.data.materials[0].node_tree.nodes['Emission'].inputs['Color'].default_value
        color = (round(pow(colors[0],gamma),4),round(pow(colors[1],gamma),4),round(pow(colors[2],gamma),4))

        index = round(ob.matrix_world[2][3]-canevas.matrix_world[2][3],5)

        rig.data.UI[ob.name] = {'points':points, 'faces':faces, 'edges' : edges,'color':color,'index' : index}

        if ob.name.endswith('.operator'):
            rig.data.UI[ob.name]['operator'] =  ob['operator']
            rig.data.UI[ob.name]['variables'] = ob['variables']
