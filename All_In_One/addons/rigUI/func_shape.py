import bpy
import bmesh
from mathutils import Vector
from bpy_extras import mesh_utils
from .utils import bound_box_center,border_loops

def store_ui_data(objects,canevas,rig):
    shapes_list = []
    gamma = 1/2.2

    if rig.data.get('UI') :
        del rig.data['UI']

    if canevas.type =='CURVE' :
        canevas_points = canevas.data.splines[0].points
    else :
        canevas_points = canevas.data.vertices

    world_canevas_points = [canevas.matrix_world * Vector((p.co[0],p.co[1],0)) for p in canevas_points]

    canevasX = [p[0] for p in world_canevas_points]
    canevasY = [p[1] for p in world_canevas_points]

    objects.append(canevas)

    #sorted by their z axes
    for ob in sorted(objects,key = lambda x : bound_box_center(x)[2]) :
        print(ob)
        data = ob.to_mesh(bpy.context.scene,True,'PREVIEW')

        bm = bmesh.new()
        bm.from_mesh(data)
        #bmesh.ops.beautify_fill(bm,faces = bm.faces,edges=bm.edges)
        bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
        bmesh.ops.dissolve_limit(bm, angle_limit=0.001745, verts=bm.verts, edges=bm.edges)

        vertex_count = [v.index for v in bm.verts]
        bm_loops = border_loops(bm,0,[],vertex_count)
        loops = [[l.index for l in L] for L in bm_loops]

        bmesh.ops.connect_verts_concave(bm, faces=bm.faces)
        bm.to_mesh(data)
        data.update()
        bm.clear()

        points = []

        faces = []

        for p in data.vertices :
            point  = ob.matrix_world * Vector((p.co[0],p.co[1],0))

            x = (point[0]-min(canevasX)) / (max(canevasX)-min(canevasX))

            y = (point[1]-min(canevasY)) / (max(canevasY)-min(canevasY))

            points.append([round(x,5),round(y,5)])

        for f in data.polygons :
            faces.append([v for v in f.vertices])

        try :
            colors = ob.data.materials[0].node_tree.nodes['Emission'].inputs['Color'].default_value
            color = [round(pow(colors[0],gamma),4),round(pow(colors[1],gamma),4),round(pow(colors[2],gamma),4)]
        except :
            color = [0.5,0.5,0.5]

        verts_x = [v[0] for v in points]
        verts_y = [v[1] for v in points]
        bound = [(min(verts_x),max(verts_y)),(max(verts_x),max(verts_y)),(max(verts_x),min(verts_y)),(min(verts_x),min(verts_y))]


        shape = {'tooltip':ob.UI.name,'points':points, 'faces':faces,
                    'loops' : loops,'bound' : bound,'color':color,
                        'shape_type': ob.UI.shape_type}

        if ob.UI.shape_type =='FUNCTION':
            shape['function'] =  ob.UI.function
            if ob.UI.arguments :
                shape['variables'] = eval(ob.UI.arguments)
            if ob.UI.shortcut :
                shape['shortcut'] = ob.UI.shortcut

        elif ob.UI.shape_type =='BONE':
            shape['bone'] =  ob.UI.name

        shapes_list.append(shape)

    print(shapes_list)

    rig.data.UI['shapes'] = shapes_list
