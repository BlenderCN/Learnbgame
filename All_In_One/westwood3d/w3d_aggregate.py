import os
from . import w3d_struct

def aggregate(root, paths):
    ag_rec(root, root, paths)

def ag_rec(node, root, paths, loaded={}):
    expfiles = {}
    impfiles = {}
    
    # load aggregates
    ag = node.get('aggregate')
    if ag is not None:
        loaded[ag.get('aggregate_header').Name] = True
        
        ainfo = ag.get('aggregate_info')
        expfiles[ainfo.BaseModelName] = True
        for s in ainfo.Subobjects:
            expfiles[s['SubobjectName']] = True
    
    # mark hierarchy as loaded
    hierarchy = node.get('hierarchy')
    if hierarchy is not None:
        loaded[hierarchy.get('hierarchy_header').Name] = True
    
    # hlod
    hlod = node.get('hlod')
    if hlod is not None:
        
        # hierarchy
        hinfo = hlod.get('hlod_header')
        loaded[hinfo.Name] = True
        
        impfiles[hinfo.HierarchyName] = True
        
        for lod in hlod.find('hlod_lod_array'):
            for h in lod.find('hlod_sub_object'):
                s = h.Name.split('.')
                impfiles[s[0]] = True
        
        for lod in hlod.find('hlod_aggregate_array'):
            for h in lod.find('hlod_sub_object'):
                expfiles[h.Name] = True
    
    # Implicit aggregation
    for f in impfiles.keys():
        if f not in loaded:
            loaded[f] = True
            n = ag_load(f, paths)
            
            # remove hlod
            ch = n.get('hlod')
            if ch is not None:
                n.children.remove(ch)
            
            root.children += n.children
            ag_rec(n, root, paths, loaded)
            
    # Explicit aggregation
    for f in expfiles.keys():
        if f not in loaded:
            loaded[f] = True
            n = ag_load(f, paths)
            root.children += n.children
            ag_rec(n, root, paths, loaded)
    
def ag_load(file, paths):
    root = None
    
    for path in paths:
        filename = os.path.join(path, file.lower() + '.w3d')
        try:
            root = w3d_struct.load(filename)
            break
        except:
            pass
    
    if root is None:
        print('MISSING: ' + file.lower() + '.w3d')
    
    return root