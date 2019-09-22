__author__ = 'fra'
__version__ = "0.1"

# import Classes
import bpy
import bmesh


def createMeshFromData(name, hdata):
    origin = (0,0,0)
    verts = hdata.points
    faces = hdata.primitive

    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True

    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True

    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update()
    return ob

def createUVFromData(object):
    attrData    = object.data['attributes']
    pos         = object.attributes[0]['Value']
    uv_value    = attrData[pos[0]][pos[1]][1][7][5]
    """
    UV Handling
    """
    # create bmesh
    me = bpy.context.object.data
    bm = bmesh.new()
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bm.from_mesh(me)
    bpy.ops.mesh.uv_texture_add()
    bm.loops.layers.uv.new("uv")
    uv_lay = bm.loops.layers.uv["uv"]
    count = 0
    # @todo there is a bug that puts all the UV's to the same spot but with any cide of data WTF
    for f in bm.faces:
        for idx,loop in enumerate(f.loops):
            uv = loop[uv_lay]
            t = object.topology[count]
            uvval = uv_value[t]
            uv.uv[0] = uvval[0]
            uv.uv[1] = uvval[1]
            count += 1
            print(uv.uv)

    bmesh.update_edit_mesh(me)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(me)  

def createGroupFromData(hdata):
    if(hdata.group == ''):
        return 0
    for item in hdata.group:
        print(item)
    print()


def setAttributeToObject(data):
    for attr in h2c.hdata.attributes:
        Name = attr["Name"]
        Type = attr["Type"]
        if ("UV" == str(Name).upper()):
            createUVFromData(data)
        else:
            print("This Attribute: {0} with this Format: {1} doesnt get imported", Name, type)

def load(hdata):
	createMeshFromData("test", hdata)
