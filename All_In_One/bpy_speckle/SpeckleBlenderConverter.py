import bpy, bmesh
import base64, hashlib
from time import strftime, gmtime

#from speckle import SpeckleResource

def SetGeometryHash(data):
    code = hashlib.md5(data.encode('utf-8')).hexdigest()
    return code

def SpeckleMesh_to_Lists(o):
    #check if o is valid Speckle mesh
    #assert SpeckleResource.isSpeckleMesh(o);
    verts = []
    faces = []
    uv = []

    if 'properties' in o.keys() and o['properties'] is not None and 'texture_coordinates' in o['properties'].keys():
    #if hasattr(o, 'properties') and o.properties is not None and hasattr(o.properties, 'texture_coordinates'):
        try:
            decoded = base64.b64decode(o['properties']['texture_coordinates']).decode("utf-8")
            s_uvs = decoded.split()
              
            if int(len(s_uvs) / 2) == int(len(o['vertices']) / 3):
                for i in range(0, len(s_uvs), 2):
                    uv.append((float(s_uvs[i]), float(s_uvs[i+1])))
            else:
                print (len(s_uvs) * 2)
                print (len(o['vertices']) /3)
                print ("Failed to match UV coordinates to vert data.")
        except:
            pass
    
    if 'vertices' in o.keys() and len(o['vertices']) > 0:
        for i in range(0, len(o['vertices']), 3):
            verts.append((float(o['vertices'][i]), float(o['vertices'][i + 1]), float(o['vertices'][i + 2])))

    if 'faces' in o.keys() and len(o['faces']) > 0:
        i = 0
        while (i < len(o['faces'])):
            if (o['faces'][i] == 0):
                i += 1
                faces.append((int(o['faces'][i]), int(o['faces'][i + 1]), int(o['faces'][i + 2])))
                i += 3
            elif (o['faces'][i] == 1):
                i += 1
                faces.append((int(o['faces'][i]), int(o['faces'][i + 1]), int(o['faces'][i + 2]), int(o['faces'][i + 3])))
                i += 4
            else:
                print("Invalid face length.\n" + str(o['faces'][i]))
                return

    return verts, faces, uv

def Lists_to_Mesh(verts, faces, uv, name, scale=1.0):

    if name is None or name=="":
        name = "SpeckleMesh"
    mesh = bpy.data.meshes.new(name)

    #mesh.from_pydata(verts, [], faces)

    
    bm = bmesh.new()
    
    # Make verts
    for v in verts:
        bm.verts.new(tuple([x * scale for x in v]))
        
    bm.verts.ensure_lookup_table()

    # Make faces
    for f in faces:
            bm.faces.new([bm.verts[x] for x in f])
            
    bm.faces.ensure_lookup_table()
    bm.verts.index_update()
           
    # Make UVs
    if len(uv) == len(verts):
        uv_layer = bm.loops.layers.uv.verify()
        bm.faces.layers.tex.verify()
        
        for f in bm.faces:
            for l in f.loops:
                luv = l[uv_layer]
                luv.uv = uv[l.vert.index]


    bm.to_mesh(mesh)
    bm.free()

    return mesh

def SpeckleMesh_to_MeshObject(smesh, scale=1.0):
    if smesh['name'] is None or smesh['name'] == "":
        smesh['name'] = "SpeckleMesh"
    verts, faces, uv = SpeckleMesh_to_Lists(smesh)
    mesh = Lists_to_Mesh(verts, faces, uv, smesh['geometryHash'], scale)

    obj = bpy.data.objects.new(smesh['name'], mesh)
    obj.speckle.object_id = smesh['_id']
    obj.speckle.enabled = True

        # Add material if there is one
    if 'properties' in smesh.keys()  and smesh['properties'] is not None:

        if 'material' in smesh['properties'].keys():
            material_name = smesh['properties']['material']['name']
            print ("bpySpeckle: Found material: %s" % material_name)

            mat = bpy.data.materials.get(material_name)

            if mat is None:
                mat = bpy.data.materials.new(name=material_name)
            obj.data.materials.append(mat)
            del smesh['properties']['material']
        
        if  'texture_coordinates' in smesh['properties'].keys() :
            del smesh['properties']['texture_coordinates']

        for key in smesh['properties'].keys():
            attr = smesh['properties'][key]
            obj[key] = attr

    return obj

def MeshObject_to_SpeckleMesh(obj, scale=1.0):
    if obj.data.tessfaces is None or len(obj.data.tessfaces) < 1:
        obj.data.calc_tessface()
    verts = [x.co * scale for x in obj.data.vertices]

    # TODO: add n-gon support, using tessfaces for now
    faces = [x.vertices for x in obj.data.tessfaces]
    #faces = [x.vertices for x in obj.data.polygons]

    #sm = SpeckleResource.createSpeckleMesh()
    sm = {'vertices':[], 'faces':[]}

    for v in verts:
        sm['vertices'].extend(v)

    for f in faces:
        if len(f) == 3:
            sm['faces'].append(0)
        elif len(f) == 4:
            sm['faces'].append(1)
        else:
            continue

        sm['faces'].extend(f)

    # Add properties and custom data
    sm['properties'] = {}
    for key in obj.keys():
        #print (key)
        if key == "speckle" or key == "_RNA_UI":
            continue
        if hasattr(obj[key], 'to_dict'):
            sm['properties'][key] = obj[key].to_dict()
        else:            
            sm['properties'][key] = obj[key]

    # Set object transform
    sm['transform'] = [y for x in obj.matrix_world for y in x]
    #setattr(sm, 'transform', [y for x in obj.matrix_world for y in x])

    # This is still needed until there is a way to access the transform property in 
    # other programs.
    sm['properties']['transform'] = str([y for x in obj.matrix_world for y in x])
    #sm.properties['transform'] = [[y for y in x] for x in obj.matrix_world]

    # Add texture coordinates
    # TODO: make switchable

    # Using tessfaces for now - possible future n-gon support
    #if obj.data.uv_layers.active is not None:
    if obj.data.tessface_uv_textures.active is not None:
        uvs = [x.uv for x in obj.data.tessface_uv_textures.active.data]
        uv_string_list = ["%f %f" % (x[0][0], x[0][1]) for x in uvs]
        uv_string = ' '.join(uv_string_list)
        sm['properties']['texture_coordinates'] = base64.encodestring(uv_string.encode("utf-8")).decode("utf-8")

    sm['name'] = obj.name   
    sm['_id'] = obj.speckle.object_id
    sm['geometryHash'] = SetGeometryHash(str(sm))[:12]
    sm['hash'] = SetGeometryHash(str(sm) + strftime("%Y-%m-%d %H:%M:%S", gmtime()))[:12]
    sm['type'] = 'Mesh'
    sm['colors'] = []

    return sm

def Blender_to_Speckle(obj, scale=1.0):
    if obj.type == 'MESH':
        return MeshObject_to_SpeckleMesh(obj, scale)
    elif obj.type == 'CURVE':
        print ("bpySpeckle: This is a curve.")
    else:
        print ("bpySpeckle: Non-supported object type.")
    return None

def Speckle_to_Blender(obj, scale=1.0):
    if obj['type'] == "Mesh":
        return SpeckleMesh_to_MeshObject(obj, scale)
    elif obj['type'] == "Curve":
        print("bpySpeckle: Curves not supported at this time.") 
    elif obj['type'] == "Placeholder":
        print("bpySpeckle: Placeholder found. Try to get the actual object.")
    elif obj['type'] == "Brep":
        # transfer name and properties to displayValue
        obj['displayValue']['name'] = obj['name']
        obj['displayValue']['_id'] = obj['_id']
        obj['displayValue']['properties'] = obj['properties']
        #setattr(obj.displayValue, 'name', obj.name)
        #setattr(obj.displayValue, '_id', obj._id)
        #setattr(obj.displayValue, 'properties', obj.properties)

        return SpeckleMesh_to_MeshObject(obj['displayValue'], scale)

    return None  

def UpdateObject(client, obj):
    if obj.speckle.enabled:
        if obj.speckle.send_or_receive == 'send':
            print("bpySpeckle: Updating with send...")
            sobj = Blender_to_Speckle(obj, 1 / bpy.context.scene.speckle.scale)
            if sobj is not None:
                print ("bpySpeckle: Updating remote object...")
                res = client.ObjectUpdateAsync(sobj._id, sobj)
        elif obj.speckle.send_or_receive == 'receive':
            print ("bpySpeckle: Updating with receive...")
            sobj = client.ObjectGetAsync(obj.speckle.object_id)
            if sobj is not None:
                print ("bpySpeckle: Updating local object... ")
                verts, faces, uv = SpeckleMesh_to_Lists(sobj['resource'])
                name = obj.data.name
                obj.data.name = "x" + obj.data.name
                mesh = Lists_to_Mesh(verts, faces, uv, name, bpy.context.scene.speckle.scale)
                print (mesh)
                obj.data = mesh
            else:
                print ("bpySpeckle: Failed to update object.")

def UpdateStream(client, stream_id):
    res = client.StreamGetAsync(stream_id)
    if res is None: return False

    objects = [x for x in res['resource']['objects']]
    stream = {"objects":objects}

    res = client.StreamUpdateAsync(stream_id, stream)



