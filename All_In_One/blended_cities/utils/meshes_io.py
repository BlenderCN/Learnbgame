##\file
# meshes_io.py most of this code will become mesh_tools
# set of functions used by builders
import bpy
import mathutils
import random
from mathutils import *

from blended_cities.core.class_main import *
from blended_cities.core.common import *
from blended_cities.utils.geo import *
 
def dprint(str,lvl) :
    print(str)

def matToString(mat) :
    #print('*** %s %s'%(mat,type(mat)))
    #return str(mat).replace('\n       ','')[6:]
    print('matToString : %s'%str(list(mat)))
    return str(list(mat))

#def matToString(mat) :
    #print('*** %s %s'%(mat,type(mat)))
#    return str(mat).replace('\n       ','')[6:]

def stringToMat(string) :
    return Matrix(eval(string))


## retrieve
def outlineRead(obsource) :

            # RETRIEVING

            mat_ori = Matrix(obsource.matrix_world).copy()
            loc, rot, scale = mat_ori.decompose()
            mat = Matrix()
            mat[0][0] *= scale[0]
            mat[1][1] *= scale[1]
            mat[2][2] *= scale[2]
            mat *= rot.to_matrix().to_4x4()

            if len(obsource.modifiers) :
                sce = bpy.context.scene
                source = obsource.to_mesh(sce, True, 'PREVIEW')
            else :
                source=obsource.data

            verts=[ v.co for v in source.vertices[:] ]
            edges=[ e.vertices for e in source.edges[:] ]
            if len(obsource.modifiers) :
                bpy.data.meshes.remove(source)

            # apply world to verts and round them a bit
            for vi,v in enumerate(verts) :
                x,y,z = v * mat #  as global coords
                x = int(x * 1000000) / 1000000
                y = int(y * 1000000) / 1000000
                z = int(z * 1000000) / 1000000
                verts[vi]=Vector((x,y,z))

            # DISCOVERING

            # for each vert, store its neighbour(s) or nothing for dots
            neighList=[[] for v in range(len(verts))]
            for e in edges :
                neighList[e[0]].append(e[1])
                neighList[e[1]].append(e[0])

            # lst is used to know if a vert has been 'analysed' ( = -1 ) or not.
            lst = [ i for i in range(len(verts)) ]
            perims = [ ]
            dots = [ ]
            lines = [ ]
            routers = {}

            # dots : verts with no neighbours
            for i,neighs in enumerate(neighList) :
                if neighs == [] :
                    dots.append(verts[i])
                    lst[i] = -1

            # lines/network
            for vi,neighs in enumerate(neighList) :
                if len(neighs) == 1 or len(neighs) >= 3 : #and lst[i] != -1 :
                    for ni in neighs :
                        if lst[ni] != -1 :
                            line, rm, closed = readLine(vi,ni,verts,neighList)
                            for off in rm : lst[off] = -1
                            if closed : perims.append(line)
                            else : lines.append(line)
                    lst[vi] = -1
                    # this vi is a router with len(neigh) road
                    # ...
                    # ...

            # perimeters
            for vi,neighs in enumerate(neighList) :
                if len(neighs) == 2 and lst[vi] != -1 :
                    ni = neighs[0] if neighs[0] != vi else neighs[1]
                    perim, rm, closed = readLine(vi,ni,verts,neighList)
                    for off in rm : lst[off] = -1
                    lst[vi] = -1
                    perims.append(perim)
                    #print('\n%s\n'%perim)
                    # should add a router for closed perimeter
                    # ...
                    # ...
            # perimeters verts order (must be anticlockwise)
            for i,p in enumerate(perims) :
                t = angleEnlarge(p[0],p[1],p[2],-0.001)
                is_in = pointInPoly(t[0],t[1],p)
                print('point %s,%s is %s'%(t[0],t[1],'in' if is_in else 'out'))
                if is_in == False :
                    perims[i].reverse()
            return mat_ori, perims, lines, dots


def readLine(pvi,vi,verts,neigh) :
    start = pvi
    line = [ verts[pvi], verts[vi] ]
    go = True
    rm = []
    while go and len(neigh[vi]) == 2 :
        nvi = neigh[vi][0] if neigh[vi][0] != pvi else neigh[vi][1]
        rm.append(vi)
        if nvi == start : go = False
        else :
            line.append( verts[nvi] )
            pvi = vi
            vi = nvi
    if len(neigh[vi]) == 1 :  rm.append(neigh[vi][0])
    return line, rm, not(go)

'''
def readMeshMap(objectSourceName,atLocation,scale,what='readall') :
    global debug
    pdeb=debug
    scale=float(scale)

    obsource=bpy.data.objects[objectSourceName]
    mat=obsource.matrix_local
    #mat=obsource.matrix_world

    #scaleX, scaleY, scaleZ = obsource.scale
    #rmat=mat.rotationPart().resize4x4()
    #if atLocation :
    #    rmat[3][0]=mat[3][0]/scale
    #    rmat[3][1]=mat[3][1]/scale
    #   rmat[3][2]=mat[3][2]/scale

    # modifiers in outline case :
    # read verts loc from a dupli (1/2 removed below)
    if len(obsource.modifiers) :
        sce = bpy.context.scene
        source = obsource.to_mesh(sce, True, 'PREVIEW')
    else :
        source=obsource.data

    # output :
    coordsList=[]            # list of verts
    edgesList=[]            # list of edges
    edgesWList=[]            # edge width
 
    # COORDSLIST - scaled + obj global param.
    for v in source.vertices :
        x,y,z = v.co * mat
        x = int(x * 1000000) / 1000000
        y = int(y * 1000000) / 1000000
        z = int(z * 1000000) / 1000000
        #y = int(round(y*scale,6) * 1000000)
        #z = int(round(z*scale,6) * 1000000)
        #coordsList.append(Vector([x,y,z]))
        coordsList.append([x,y,z])
        if len(coordsList)==1 :
            xmin=xmax=x
            ymin=ymax=y
            zmin=zmax=z
        else :
            xmin=min(xmin,x)
            ymin=min(ymin,y)
            zmin=min(zmin,z)
            xmax=max(xmax,x)
            ymax=max(ymax,y)
            zmax=max(zmax,z)

    # mods in outline (2/2)
    obsource=bpy.data.objects[objectSourceName]
    if len(obsource.modifiers) :
        #wipeOutObject(bpy.context.scene.objects.active.name)
        #print(selected.name)
        #bpy.ops.object.select_name(name=selected.name)
        bpy.data.meshes.remove(source)

    if what == 'readall' :
        # EDGELIST - raw
        # map road category to each edge
        for e in source.edges :
            edgesList.append([e.vertices[0],e.vertices[1]])
            edgesWList.append(e.crease)
        if pdeb :
            print("RAW :\ncoords :")   
            for i,v in enumerate(coordsList) :print(i,v)
            print("\nedges :")    
            for i,v in enumerate(edgesList) : print(i,v)

        return coordsList,edgesList,edgesWList,[ [xmin,xmax], [ymin,ymax], [zmin,zmax] ]
    else :
        return Vector([xmin,ymin,0]),Vector([xmax-xmin,ymax-ymin,0])
'''
## lock or unlock an object matrix
# @param ob the object to lock/unlock
# @param state True to lock, False to unlock
def objectLock(ob,state=True) :
    for i in range(3) :
        ob.lock_rotation[i] = state
        ob.lock_location[i] = state
        ob.lock_scale[i] = state


def objectBuild(elm, verts, edges=[], faces=[], matslots=[], mats=[], uvs=[] ) :
    #print('build element %s (%s)'%(elm,elm.className()))
    dprint('object build',2)
    city = bpy.context.scene.city
    # apply current scale
    verts = metersToBu(verts)
    
    if type(elm) != str :
        obname = elm.objectName()
        if obname == 'not built' :
            obname = elm.name
    else : obname= elm

    obnew = createMeshObject(obname, True, verts, edges, faces, matslots, mats, uvs)
    #elm.asElement().pointer = str(ob.as_pointer())
    if type(elm) != str :
        if elm.className() == 'outlines' :
            obnew.lock_scale[2] = True
            if elm.parent :
                obnew.parent = elm.Parent().object()
        else :
            #otl = elm.asOutline()
            #ob.parent = otl.object()
            objectLock(obnew,True)
        #ob.matrix_local = Matrix() # not used
        #ob.matrix_world = Matrix() # world
    return obnew

## material MUST exist before creation of material slots
## map only uvmap 0 to its image defined in mat  for now (multitex view)
def createMeshObject(name, replace=False, 
verts=[], edges=[], faces=[], 
matslots=[], mats=[], uvs=[]) :

    if replace :
        # naming consistency for mesh w/ one user
        if name in bpy.data.objects :
            mesh = bpy.data.objects[name].data
            if mesh :
                if mesh.users == 1 : mesh.name = name
            else : 
                dprint('createMeshObject : object %s found with no mesh (%s) '%(name,type(mesh)),2)
                wipeOutObject(bpy.data.objects[name])
        # update mesh/object
        if name in bpy.data.meshes :
            mesh = bpy.data.meshes[name]
            mesh.user_clear()
            wipeOutData(mesh)

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, faces)
    mesh.update()

    # material slots
    matimage=[]
    if len(matslots) > 0 :
        for matname in matslots :
            '''
            if matname not in bpy.data.materials :
                mat = bpy.data.materials.new(name=matname)
                mat.diffuse_color=( random.uniform(0.0,1.0),random.uniform(0.0,1.0),random.uniform(0.0,1.0))
                mat.use_fake_user = True
                warn.append('Created missing material : %s'%matname)
            else :
            '''
            mat = bpy.data.materials[matname]
            mesh.materials.append(mat)
            texslot_nb = len(mat.texture_slots)
            if texslot_nb :
                texslot = mat.texture_slots[0]
                if type(texslot) != type(None) :
                    tex = texslot.texture
                    if tex.type == 'IMAGE' :
                        img = tex.image
                        if type(img) != type(None) :
                            matimage.append(img)
                            continue
            matimage.append(False)

    # map a material to each face
    if len(mats) > 0 :
        for fi,f in enumerate(mesh.polygons) :
            f.material_index = mats[fi]

    # uvs
    if len(uvs) > 0 :
        uvwrite(mesh, uvs, matimage)
        '''
        for uvi, uvlist in enumerate(uvs) :
            uv = mesh.uv_textures.new()
            uv.name = 'UV%s'%uvi
            for uvfi, uvface in enumerate(uvlist) :
                #uv.data[uvfi].use_twoside = True # 2.60 changes mat ways
                mslotid = mesh.faces[uvfi].material_index
                #mat = mesh.materials[mslotid]
                #tex = mat.texture_slots[0].texture
                #img = tex.image
                if matimage[mslotid] :
                    img = matimage[mslotid]
                    uv.data[uvfi].image=img
                    #uv.data[uvfi].use_image = True
                uv.data[uvfi].uv1 = Vector((uvface[0],uvface[1]))
                uv.data[uvfi].uv2 = Vector((uvface[2],uvface[3]))
                uv.data[uvfi].uv3 = Vector((uvface[4],uvface[5]))
                if len(uvface) == 8 :
                    uv.data[uvfi].uv4 = Vector((uvface[6],uvface[7]))
        '''

    if name not in bpy.data.objects or replace == False :
        ob = bpy.data.objects.new(name=name, object_data=mesh)
        dprint('  create object %s'%ob.name,2)
    else :
        ob = bpy.data.objects[name]
        ob.data = mesh
        ob.parent = None
        ob.matrix_local = Matrix()
        dprint('  reuse object %s'%ob.name,2)
    if  ob.name not in bpy.context.scene.objects.keys() :
        bpy.context.scene.objects.link(ob)
    return ob

# copy of bel.uv.write
def uvwrite(me, uvs, matimage = False) :
    uvs, nest = nested(uvs)
    newuvs = []
    # uvi : uvlayer id  uvlist : uv coordinates list
    for uvi, uvlist in enumerate(uvs) :

        uv = me.uv_textures.new()
        uv.name = 'UV%s'%uvi
        
        uvlayer = me.uv_layers[-1].data
        
        for uvfi, uvface in enumerate(uvlist) :
            #uv.data[uvfi].use_twoside = True # 2.60 changes mat ways
            mslotid = me.polygons[uvfi].material_index
            #mat = mesh.materials[mslotid]
            if matimage :
                if matimage[mslotid] :
                    img = matimage[mslotid]
                    uv.data[uvfi].image=img
            
            vi = 0
            for fi in me.polygons[uvfi].loop_indices :
                uvlayer[fi].uv = Vector((uvface[vi],uvface[vi+1]))
                vi += 2
                
        newuvs.append(uv)
    if nest : return newuvs
    return newuvs[0]

def materialsCheck(bld) :
    if hasattr(bld,'materialslots') == False :
        #print(bld.__class__.__name__)
        builderclass = eval('bpy.types.%s'%(bld.__class__.__name__))
        builderclass.materialslots=[bld.className()]

    matslots = bld.materialslots
    if len(matslots) > 0 :
        for matname in matslots :
            if matname not in bpy.data.materials :
                mat = bpy.data.materials.new(name=matname)
                mat.use_fake_user = True
                if hasattr(bld,'mat_%s'%(matname)) :
                    method = 'defined by builder'
                    matdef = eval('bld.mat_%s'%(matname))
                    mat.diffuse_color = matdef['diffuse_color']
                else :
                    method = 'random'
                    mat.diffuse_color=( random.uniform(0.0,1.0),random.uniform(0.0,1.0),random.uniform(0.0,1.0))
                dprint('Created missing material %s (%s)'%(matname,method),2)

# face are squared or rectangular, 
# any orientation
# vert order width then height 01 and 23 = x 12 and 03 = y
# normal default when face has been built
def uvrow(vertices,faces,normals=True) :
    uvs = []
    for face in faces :
        v0 = vertices[face[0]]
        v1 = vertices[face[1]]
        v2 = vertices[face[-1]]
        print(v0,v1)
        lx = (v1 - v0).length
        ly = (v2 - v0).length
        # init uv
        if len(uvs) == 0 :
            x = 0
            y = 0
        elif normals :
            x = uvs[-1][2]
            y = uvs[-1][3]
        else :
            x = uvs[-1][0]
            y = uvs[-1][1]
        if normals : uvs.append([x,y,x+lx,y,x+lx,y+ly,x,y+ly])
        else : uvs.append([x+lx,y,x,y,x,y+ly,x+lx,y+ly])
    return uvs



def updateChildHeight(otl,height) :
    dprint('** update childs of %s : %s'%(otl.name,otl.childs ),2)
    city = bpy.context.scene.city
    for otl_child in otl.Childs() :
        dprint(' . %s'%otl_child.name,3)
        #verts, edges, edgesW , bounds = readMeshMap(childname,True,1)
        #otl_child = city.outlines[child.name]
        # force re-read of data
        otl_child.dataRead()
        data = otl_child.dataGet()
        for perimeter in data :
            for vert in perimeter :
                vert[2] = height
        otl_child.dataSet(data)
        otl_child.dataWrite()
        bld_child = otl_child.peer()
        #bld_child.build(True)
        city.builders.build(bld_child)

