import copy

def collect_render_objects(root):
    robj = {}
    
    for m in root.find('mesh'):
        info = m.get('mesh_header3')
        name = info.ContainerName + '.' + info.MeshName
        robj[name] = m
    for s in root.find('box'):
        robj[s.Name] = s
    for s in root.find('sphere'):
        robj[s.Name] = s
    for s in root.find('ring'):
        robj[s.Name] = s
    
    return robj
    
def make_pivots(root, robj):
    pivotdict = {}
    
    for hroot in root.find('hlod'):
        if hroot is None:
            continue
        
        info = hroot.get('hlod_header')
        
        hierarchy = None
        hname = None
        for h in root.find('hierarchy'):
            hname = h.get('hierarchy_header').Name
            if info.HierarchyName == hname:
                hierarchy = h
                break
        
        if hierarchy is None:
            continue
        
        # Compile pivot data into a proper tree
        pivots = []
        for pdata in hierarchy.get('pivots').pivots:
            p = {
                'index': pivots, 'name': pdata['Name'], 'agname': pdata['Name'],
                'children': [], 'obj': [], 'prx': [], 'lodcount': info.LodCount,
            }
            
            if pdata['ParentIdx'] != 0xffffffff:
                pivots[pdata['ParentIdx']]['children'].append(p)
            else:
                p['name'] = info.Name
                pivotdict[info.Name] = p
            
            p['translation'] = pdata['Translation']
            p['rotation'] = pdata['Rotation']
            pivots.append(p)
        
        # Assign name-lod tuple to pivots
        lod = info.LodCount
        for hlod in hroot.find('hlod_lod_array'):
            lod -= 1
            for h in hlod.find('hlod_sub_object'):
                if h.Name in robj:
                    pivots[h.BoneIndex]['obj'].append((robj[h.Name], lod))
        
        # aggregates appear in all LOD
        for hlod in hroot.find('hlod_aggregate_array'):
            for h in hlod.find('hlod_sub_object'):
                if h.Name in robj:
                    pivots[h.BoneIndex]['obj'].append((robj[h.Name], -1))
        
        # proxy objects are special
        for hlod in hroot.find('hlod_proxy_array'):
            for h in hlod.find('hlod_sub_object'):
                pivots[h.BoneIndex]['prx'].append(h.Name)
    
    return pivotdict
    
def mat_reduce(root, ignore_lightmap):
    materials = []
    mathash = {}
    
    for mesh in root.find('mesh'):
        meshinfo = mesh.get('mesh_header3')
        verts = mesh.get('vertices').vertices
        faces = mesh.get('triangles').triangles
        mpass = mesh.findRec('material_pass')
        texnames = mesh.findRec('texture_name')
        vmnames = mesh.findRec('vertex_material_name')
        vminfos = mesh.findRec('vertex_material_info')
        shaders = mesh.getRec('shaders')
        fmhash = {}
        mesh.Materials = []
        faceidx = 0
        for face in faces:
            
            # Gather face information
            finfo = {}
            
            # get surface
            finfo['surface'] = face['Attributes']
            
            finfo['mpass'] = []
            for p in mpass:
                pinfo = { 'stages': [] }
                
                # get vertex material
                ids = p.get('vertex_material_ids').ids
                pinfo['vmid'] = ids[face['Vindex'][0]] if len(ids) > 1 else ids[0]
                
                # remove lightmaps if not wanted
                if ignore_lightmap and vmnames[pinfo['vmid']].name == 'Lightmap':
                    mpass.remove(p)
                    continue
                
                # get shader
                ids = p.get('shader_ids').ids
                pinfo['sid'] = ids[faceidx] if len(ids) > 1 else ids[0]
                
                # get textures
                stage = p.get('texture_stage')
                if stage is not None:
                    for tex in stage.findRec('texture_ids'):
                        ids = tex.ids
                        pinfo['stages'].append(ids[faceidx] if len(ids) > 1 else ids[0])
                
                finfo['mpass'].append(pinfo)
            
            faceidx += 1
            
            # Reduce face info to materials
            h = make_hash(finfo)
            if h in fmhash:
                face['Mindex'] = fmhash[h]
                continue
            
            # Material are stored in an array with the mesh
            # and material index is stored with face
            face['Mindex'] = len(mesh.Materials)
            fmhash[h] = len(mesh.Materials)
            
            # Compile material
            mat = { 'mpass': [] }
            mat['surface'] = finfo['surface']
            mat['sort_level'] = meshinfo.SortLevel
            
            for pinfo in finfo['mpass']:
                p = { 'vertex_material': {}, 'stages': [] }
                p['shader'] = shaders.shaders[pinfo['sid']]
                p['vertex_material']['name'] = vmnames[pinfo['vmid']].name
                p['vertex_material']['info'] = vminfos[pinfo['vmid']]
                for id in pinfo['stages']:
                    if id < len(texnames):
                        p['stages'].append({ 'name': texnames[id].name })
                mat['mpass'].append(p)
            
            # Reduce materials to share between meshes
            h = make_hash(mat)
            if h in mathash:
                mat = mathash[h]
            else:
                mathash[h] = mat
                materials.append(mat)
            
            mesh.Materials.append(mat)
    
    return materials
    
# thanks jomido @ stackoverflow!
DictProxyType = type(object.__dict__)

def make_hash(o):

    """
    Makes a hash from a dictionary, list, tuple or set to any level, that 
    contains only other hashable types (including any lists, tuples, sets, and
    dictionaries). In the case where other kinds of objects (like classes) need 
    to be hashed, pass in a collection of object attributes that are pertinent. 
    For example, a class can be hashed in this fashion:

        make_hash([cls.__dict__, cls.__name__])

    A function can be hashed like so:

        make_hash([fn.__dict__, fn.__code__])
    """

    if type(o) == DictProxyType:
        o2 = {}
        for k, v in o.items():
            if not k.startswith("__"):
                o2[k] = v
        o = o2    

    if isinstance(o, set) or isinstance(o, tuple) or isinstance(o, list):

        return tuple([make_hash(e) for e in o])        

    elif not isinstance(o, dict):

        return hash(o)

    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)

    return hash(tuple(frozenset(new_o.items())))