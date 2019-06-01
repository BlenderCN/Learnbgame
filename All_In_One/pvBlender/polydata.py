import bpy
import bmesh
import paraview
import paraview.simple
import paraview.servermanager

vtknodes_tmp_mesh = {}

def PolyDataMesh(pdata, ob):
        print("replace mesh ...")
        me = ob.data
        ob.data = vtknodes_tmp_mesh
        bpy.data.meshes.remove(me,do_unlink=True)
        me = bpy.data.meshes.new(ob.name + "Mesh")
        ob.data = me
        verts = []
        faces = []
        for i in range(pdata.GetNumberOfPoints()):
            point = pdata.GetPoint(i)
            verts.append([point[0],point[1],point[2]])
        for i in range(pdata.GetNumberOfCells()):
            cell = pdata.GetCell(i)
            if pdata.GetCellType(i)==5:
                faces.append([cell.GetPointId(0),cell.GetPointId(1),cell.GetPointId(2)])
            if pdata.GetCellType(i)==9:
                faces.append([cell.GetPointId(0),cell.GetPointId(1),cell.GetPointId(2),cell.GetPointId(3)])
        me.from_pydata(verts, [], faces)
        print("replaced ...")
        bpy.context.scene.objects.active = ob    


def polydata_ids(cell):
    return [ cell.GetPointId(i) for i in range(cell.GetNumberOfPoints()) ]
def polydata_point(point):
    return [ point[i] for i in range(3) ]
def polydata_vertex(bm, pdata,lays,i):
    vert = bm.verts.new(polydata_point(pdata.GetPoint(i)))
    vert[lays[0]] = pdata.GetPoint(i)[0]
    return(vert)

def bmesh_from_polydata(bm, pdata):
    bm.clear()
    lays = [ bm.verts.layers.float.new('G') ]
    verts = [ polydata_vertex(bm, pdata,lays,i) for i in range(pdata.GetNumberOfPoints()) ]
    for i in range(pdata.GetNumberOfCells()):
        cell = pdata.GetCell(i)
        if pdata.GetCellType(i)==5:
            bm.faces.new((verts[i] for i in polydata_ids(cell)))
        if pdata.GetCellType(i)==9:
            bm.faces.new((verts[i] for i in polydata_ids(cell)))
#            bm.faces.new((cell.GetPointId(0),cell.GetPointId(1),cell.GetPointId(2),cell.GetPointId(3)))


def post_init(something):
    global vtknodes_tmp_mesh
    if "vtknodes_tmp_mesh" in bpy.data.meshes:
        vtknodes_tmp_mesh = bpy.data.meshes["vtknodes_tmp_mesh"]
    else:
        vtknodes_tmp_mesh = bpy.data.meshes.new("vtknodes_tmp_mesh")
