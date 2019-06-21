'''
Created on 06.08.2014

@author: hfrieden
'''
import bpy
import bmesh
from bpy_extras import object_utils
from math import *
from mathutils import *

def CreateProxyPos(obj, pos, path, index, enclose = None):
    v1 = pos
    v2 = pos + Vector((0,0,2))
    v3 = pos + Vector((0,1,0))
    CreateProxy (obj, v1, v2, v3, path, index, enclose)
                      

def CreateProxy(obj, v1,v2,v3, path, index, enclose=None):        
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        i = len(bm.verts)
        v1 = bm.verts.new(v1)
        v2 = bm.verts.new(v2)
        v3 = bm.verts.new(v3)
        
        f = bm.faces.new((v1,v2,v3))
        bm.to_mesh(mesh)
        bm.free()

        vgrp = obj.vertex_groups.new(name = "@@armaproxy")
        vgrp.add([i+0],1,'ADD')
        vgrp.add([i+1],1,'ADD')
        vgrp.add([i+2],1,'ADD')
       
        if enclose != None:
            fnd = obj.vertex_groups.find(enclose)
            if (fnd == -1):
                vgrp2 = obj.vertex_groups.new(name = enclose)
            else:
                vgrp2 = obj.vertex_groups[fnd]
                
            vgrp2.add([i+0],1,'ADD')
            vgrp2.add([i+1],1,'ADD')
            vgrp2.add([i+2],1,'ADD')
            
        p = obj.armaObjProps.proxyArray.add()
        p.name = vgrp.name
        p.index = index
        p.path = path


def CopyProxy(objFrom, objTo, proxyName, enclose = None):
    #print("Copy proxy " + proxyName + " from " + objFrom.name + " to " + objTo.name)
    #if enclose is not None:
    #    print("Enclosed in " + enclose)
    mesh = objFrom.data
    vgrp = objFrom.vertex_groups[proxyName]
    idx = vgrp.index
    
    vertx = []
    
    # find the first vertex of the proxy in the object we want to copy from
    for vert in mesh.vertices:
        grps = [grp for grp in vert.groups if grp.group == idx]
        if len(grps) > 0: # Should only ever be 0 or 1
            vertx.append(vert.index)
    
    # This should be three vertices, and their index should be ascending
    # Make sure
    vertx.sort()
    v1 = mesh.vertices[vertx[0]].co
    v2 = mesh.vertices[vertx[1]].co
    v3 = mesh.vertices[vertx[2]].co
    
    # Gather the data of the proxy
    proxy = objFrom.armaObjProps.proxyArray[proxyName]
    CreateProxy(objTo, v1,v2,v3, proxy.path, proxy.index, enclose)    
    
    return