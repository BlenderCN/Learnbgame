import bpy

obj = bpy.context.active_object
obj = bpy.data.objects['terrain2']

filename = '/home/zeffii/Desktop/sw/geom_terrain2.tkg'
filename = '/home/zeffii/Desktop/sw/{0}.tkg'.format(obj.name)

with open(filename, 'w') as ofile:

    # verts
    ofile.write('var {0} = {{\n'.format(obj.name))
    ofile.write('  verts: [')
    verts = obj.data.vertices
    for v in verts[:-1]:
        ofile.write("%.4f, %.4f, %.4f, " % v.co[:])
    ofile.write("%.4f, %.4f, %.4f],\n" % verts[-1].co[:])

    # faces
    ofile.write('  faces: [')
    polygons = obj.data.polygons
    for face in polygons[:-1]:
        ofile.write('%i, %i, %i, ' % face.vertices[:])
    ofile.write('%i, %i, %i],\n' % polygons[-1].vertices[:])

    # edges
    edges_subset = [e for e in obj.data.edges if e.crease == 1.0]
    ofile.write('  edges: [')
    for edge in edges_subset[:-1]:
        ofile.write('%i, %i, ' % edge.vertices[:])
    ofile.write('%i, %i]\n' % edges_subset[-1].vertices[:])

    ofile.write('};\n')
