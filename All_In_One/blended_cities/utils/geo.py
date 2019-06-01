## geometry
import random
from random import randint as Prandint, uniform as Puniform
import collections
from math import *

import bpy
import mathutils
from mathutils import geometry
from mathutils import *
from blended_cities.core.common import *


## returns the area of a polyline
def area(poly,ptype='coord') :
    if ptype=='vector' : poly=vecToCoord(poly)
    A=0
    poly.append(poly[0])
    for i,c in enumerate(poly) :
        j = (i+1)%(len(poly))
        A += poly[i][0] * poly[j][1]
        A -= poly[i][1] * poly[j][0]
    A /= 2
    return abs(A)


## returns the perimeter of a polyline
def perimeter(poly,ptype="vector") :
    if ptype=="coord" : poly=coordToVec(poly,True)
    L=0
    for i in range(1,len(poly)) :
        l,d=readVec(poly[i])
        L +=l
    return L


## check if there's nested lists in a list. used by functions that need
# list(s) of vertices/faces/edges etc as input
# @param lst a list of vector or a list of list of vectors
# @returns always nested list(s)
# a boolean True if was nested, False if was not
def nested(lst) :
    try :
        t = lst[0][0][0]
        return lst, True
    except :
        return [lst], False

#  @param vertslists a list or a list of lists containing vertices coordinates
#  @param offset the first vert id of the first vertice
#  @return a Counter with z coordinates as key and the number of vertices which have that value as value
def zcoords(vertslists,offset=0) :
    try : test = vertslists[0][0][0]
    except : vertslists = [vertslists]
    zlist = collections.Counter()
    for vertslist in vertslists :
        for v in vertslist :
            zlist[ v[2] + offset ] += 1
    return zlist

## FACES CREATION FUNCS

## returns faces for a loop of vertices
# the index of theses vertices are supposed to be ordered (anticlock)
# @param offset int index of the first vertex of the lie/poly
# @param length int number of verts defining a line or a poly, they are supposed to be ordered
# @param line bool True if is a line, False (default) if is a poly
# @normals (default True) normal directions. anticlock verts order point 'up'
# @param loop TODO number of layers of faces
# @return list of quadratic faces
def facesLoop(offset,length,line=False,normals=True) :
    faces = []
    for v1 in range(length) :
        if v1 == length - 1 :
            if line : return faces
            v2 = 0
        else : v2 = v1 + 1
        if normals : faces.append( ( offset + v1, offset + v2, offset + v2 + length, offset + v1 + length  ) )
        else : faces.append( ( offset + v2, offset + v1, offset + v1 + length, offset + v2 + length ) )
    return faces


## like tessellate but with an optional index offset giving the first vert index
# @param list of vertices. vertices are in Vector format, in anticlock order
# @offset the first vertex index
# @normals (default True) normals point 'up'
# @return list of faces
def fill(vertlist,offset=0,normals=True) :
    if normals : vertlist.reverse()
    faces = geometry.tessellate_polygon([vertlist])
    if offset != 0 :
        for i,f in enumerate(faces) : faces[i] = ( f[0] + offset, f[1] + offset, f[2] + offset )
    return faces


## returns edges for a loop of vertices
# the index of theses vertices are supposed to be ordered (anticlock)
# @param offset int index of the first vertex of the lie/poly
# @param length int number of verts defining a line or a poly, they are supposed to be ordered
# @param line bool True if is a line, False (default) if is a poly
# @param loop TODO number of layers of faces
# @return quad faces
def edgesLoop(offset,length,line=False,loop=1) :
    edges = []
    for v1 in range(length) :
        if v1 == length - 1 :
            if line : return edges
            v2 = 0
        else : v2 = v1 + 1
        edges.append([ offset + v1, offset + v2 ])
    return edges


## convert an edge into a poly
def edgesEnlarge(lines,width,typep="vector") :
    try :
        a=lines[0][0][0]
        one=False
    except :
        lines=[lines]
        one=True
    newpolys=[]
    #print "IN :",lines[0]
    if typep == "coord" : lines = coordToVec(lines,False)
    #print "OUT :",lines[0]

    for li,line in enumerate(lines) :
        pdeb=False
        if pdeb : dprint("input %s"%line)
        poly2=[]
        v=1
        a=Vector(line[0])
        w=width*0.5
        
        if pdeb : dprint("_____________________________")

        while v < len(line) :
            #dprint( a,v
            sz,rot=readVec(line[v])
            if v==1 :
                if pdeb : dprint( 'start at %s'%a)
                b=a+writeVec(w,rot-90)
                c=b+writeVec(sz-w,rot)
                # first point
                b2=b+writeVec(w,rot)
                poly2.append(b2)
                if len(line)==2 :poly2.append(c)
            else :
                d=a+writeVec(w,rot-90)
                e=d+writeVec(sz-w,rot)
                if pdeb : 
                    dprint( "b %s c %s"%(b,c))
                    dprint( "d %s e %s"%(d,e))
                interlist = geometry.intersect_line_line(b,c,d,e)
                if type(interlist)==tuple and str(interlist[0][0]) != 'nan' :
                    poly2.append(Vector([interlist[0][0],interlist[0][1],line[v][2]]))
                elif pdeb : dprint( "inter rate")
                if v==len(line)-1 :
                    poly2.append(e)
                b=Vector(d[:])
                c=Vector(e[:])
                if pdeb : dprint( poly2)
            a=a+Vector(line[v])
            v +=1
        v=len(line)-1
        if pdeb : dprint( "back")
        while v > 0 :
            #dprint( a,v
            sz,rot=readVec(line[v])
            if v==len(line)-1 :
                b=a+writeVec(w,rot+90)+writeVec(w,rot-180)
                poly2.append(b)
                c=b-writeVec(sz-width,rot)
                if pdeb : dprint( "b %s c %s"%(b,c))
                if len(line)==2 :poly2.append(c)
            else :
                d=a+writeVec(w,rot+90)
                e=d-Vector(line[v])
                if pdeb : 
                    dprint( "b %s c %s"%(b,c))
                    dprint( "d %s e %s"%(d,e))
                interlist = geometry.intersect_line_line(b,c,d,e)
                if type(interlist)==tuple and str(interlist[0][0]) != 'nan' :
                    poly2.append(Vector([interlist[0][0],interlist[0][1],line[v][2]]))
                elif pdeb :  dprint( "inter rate" )
                if v==1 :
                    l,r=readVec(e-d)
                    e=d+writeVec(l-w,r)
                    poly2.append(e)
                
                b=Vector(d[:])
                c=Vector(e[:])
                if pdeb : dprint( poly2 )
            a=a-Vector(line[v])
            v -=1            
            

        if pdeb : dprint( "out : %s \n"%poly2)
        newpolys.append(poly2)

    if one : return newpolys[0]
    else : return newpolys


##############
## CONVERTERS
##############

##  ordered coords ---> ordered vectors
# @param polys list of coordinates or list ot lists of coordinates
# @param ispoly default True : a (list of) polygon is given. False : a (list of) line  is given
# @param nocheck something related to polygon first end coords.. WIP
# @return a list or a list of lists of vectors
def coordToVec(polys,ispoly=True,nocheck=False) :
    polys, nest = nested(polys)
    for ip,poly in enumerate(polys) :
        if len(poly)>1 :
            #dprint( poly
            c=Vector(poly[0])
            vecs=[c]
            if ispoly : l=len(poly)
            else : l=len(poly)-1
            for i in range(l) :
                if ispoly and i==len(poly)-1 : n=0
                else : n=i+1
                c=Vector(poly[n])-Vector(poly[i])
                #if readVec(c)[0] != 0 or nocheck : vecs.append(c) # BC 2.49b
                if c.length != 0 or nocheck : vecs.append(c)
            polys[ip]=vecs

    if nest : return polys
    else : return polys[0]


## ordered vectors ---> ordered coords
# ignore the last vector if it closes the poly
# @param polys list of vectors or list ot lists of vectors
# @param ispoly default True : a (list of) polygon is given. False : a (list of) line  is given
# @param nocheck something related to polygon first end coords.. WIP
# @return a list or a list of lists of coordinates (vector format)
def vecToCoord(polys,ispoly=True,nocheck=False) :
    polys, nest = nested(polys)
    for ip,poly in enumerate(polys) :
        if len(poly)>1 :
            c=Vector([0,0,0])
            coords=[]
            for i,v in enumerate(poly) :
                c = c+Vector(v)
                #if ispoly and i==len(poly)-1 and (nocheck or cfloat(c,'eq',Vector(poly[0]),0.00001)) : pass
                if ispoly and i==len(poly)-1 and (nocheck or c == Vector(poly[0])) : pass
                else :coords.append(c)
            polys[ip]=coords

    if nest : return polys
    else : return polys[0]


## blender units ---> meters
# @param vertslists list of coordinates or list ot lists of coordinates
# @return list of coordinates or list ot lists of coordinates
def buToMeters(vertslists) :
    vertslists, nest = nested(vertslists)
    scale = bpy.context.scene.unit_settings.scale_length
    meterslists = []

    for verts in vertslists :
        meters = []
        for vert in verts :
            meters.append(Vector(vert) * scale)
        meterslists.append(meters)
        
    if nest : return meterslists
    else : return meterslists[0]


## meters ---> blender units 
# @param vertslists list of coordinates or list ot lists of coordinates
# @return list of coordinates or list ot lists of coordinates
def metersToBu(vertslists) :
    vertslists, nest = nested(vertslists)
    scale = bpy.context.scene.unit_settings.scale_length
    meterslists = []

    for verts in vertslists :
        meters = []
        for vert in verts :
            meters.append(Vector(vert) / scale)
        meterslists.append(meters)
        
    if nest : return meterslists
    else : return meterslists[0]




##  determine if a point is inside a given polygon or not
# z coords are considered planar
# @param x x location of the point
# @param y y location of the point
# @poly perimeter
# @ptype as ordered coord or as ordered vector
# @return True if the point is inside the poly, else False
def pointInPoly(x,y,poly,ptype="coord"):
    inside =False
    if ptype=="vector":poly=vecToCoord(poly)
    p1x,p1y,z = poly[0]
    n = len(poly)
    for i in range(n+1):
        p2x,p2y,z = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside


## returns extruded polygons from polygons
# @param polys
# @param width
# @param ptype
# @param lst
def polyIn(polys,width,ptype="vector",lst=[],pdeb=False) :
    global debug
    pdeb = True
    if pdeb : dprint('polyin :')

    polys, nest = nested(polys)

    if nest :
        # check if the given width is an int applied to each poly or if each poly has its own width
        try:
            a=width[0][0]
            wlist=True
        except :
            wlist=False
            if type(width)==type(int()) or type(width)==type(float()):
                width=[width for p in range(len(polys))]
    else :
        try :
            a=width[0]
            wlist=True
            width=[width]
        except : # fixed width/poly
            wlist=False
            width=[width]

    newpolys = []

    for i,poly in enumerate(polys) :

        newpoly = []
        for ci1,p1 in enumerate(poly) :
            ci0=ci1-1
            ci2=(ci1+1)%(len(poly))
            if ci1 == 0 :
                t = angleEnlarge(poly[ci0],p1,poly[ci2],0.001)
                dir = -1 if pointInPoly(t[0],t[1],poly) else 1
            #w=[pwidth[ci1][0]*s[0],pwidth[ci1][1]*s[0]]
            w=[width[i] * dir, width[i] * dir]
            nc=angleEnlarge(poly[ci0],p1,poly[ci2],w)
            newpoly.append(nc)
        newpolys.append(newpoly)

    if nest : return newpolys
    else : return newpolys[0]


## add/sub/merge operations on 2 polys.
# (I mean, it's the goal..)
def polyBool(polyA,polyB,start=0,ptype="coord",pdeb=False) :
    if ptype=="vector" : 
        polyA=vecToCoord(polyA)
        polyB=vecToCoord(polyB)
    #polyA=vcoords(polyA)
    #polyB=vcoords(polyB)
    newpoly=[]
    polyBo=polyIn(polyB[:],0.1,"coord")
    ncA=[{} for i in polyA]
    ncB=[{} for i in polyB]
    for ciA in range(start,len(polyA)) :
        ciB=(ciA+1)%(len(polyA))
        A=polyA[ciA]
        B=polyA[ciB]
        if pdeb : dprint('-> A : %s %s / B %s %s'%(A[0],A[1],B[0],B[1]))
        for ciC in range(len(polyB)) :
            ciD=(ciC+1)%(len(polyB))
            C=polyB[ciC]
            D=polyB[ciD]
            if aligned(C,D,A,pdeb=pdeb)==False and aligned(C,D,B,pdeb=pdeb)==False:
            #if aligned(A,B,C,pdeb=pdeb)==False and aligned(A,B,D,pdeb=pdeb)==False:
            #if parallel(A,B,C,D,False)==False :#dir,tolerance=0.03,pdeb=False) :
                inter=SegmentIntersect(A,B,C,D)#,point=False)
                if pdeb :
                    dprint(' C %s %s / D %s %s'%(C[0],C[1],D[0],D[1]))
                if inter != False :
                    if pdeb : dprint('* intersect at %s'%inter[0])
                    l,d=readVec(Vector(inter[0])-Vector(A))
                    ncA[ciA][l]=inter[0]
                    l,d=readVec(Vector(inter[0])-Vector(C))
                    ncB[ciC][l]=inter[0]
            elif pdeb :
                dprint(' C %s %s / D %s %s canceled'%(C[0],C[1],D[0],D[1]))

    # append new intersection coords to A
    for ci,c in enumerate(polyA) :
        newpoly.append(c)
        if len(ncA[ci])>0 :
            lsorted = list(ncA[ci].keys())
            lsorted.sort()
            for l in lsorted :
                newpoly.append(ncA[ci][l])
    polyA=newpoly[:]
    newpoly=[]
    # append new intersection coords to B
    for ci,c in enumerate(polyB) :
        newpoly.append(c)
        if len(ncB[ci])>0 :
            lsorted = list(ncB[ci].keys())
            lsorted.sort()
            for l in lsorted :
                newpoly.append(ncB[ci][l])
    polyB=newpoly[:] #-1]
    newpoly=[]

    ciA=0
    ciB=len(polyB)
    A=True
    while ciA>0 or len(newpoly)==0 :
    
        if A :
            c=polyA[ciA]
            if c not in newpoly :
                newpoly.append(c)
            else :
                if pdeb :
                    dprint("loop")
                    dprint('*'*20)
                    dprint(polyA)
                    dprint('*'*20)
                    dprint(polyB)
                    dprint('*'*20)
                ciA=0
                break
            if pdeb : dprint('A : %s %s %s'%(ciA,c[0],c[1]))
            if ciA>1 :
                try :
                    ciB=polyB.index(c)
                    if pdeb : dprint('match B in %s'%ciB)
                    A=False
                    ciB=(ciB+1)%(len(polyB))
                except :
                    ciA=(ciA+1)%(len(polyA))
            else :
                ciA=(ciA+1)%(len(polyA))
        else :
            c=polyB[ciB]
            #if c==newpoly[0] :
                
            if c not in newpoly :
                newpoly.append(c)
            else :
                ciA=0
                if pdeb :
                    dprint("loop")
                    dprint(newpoly)
                    dprint('*'*20)
                    dprint(polyA)
                    dprint('*'*20)
                    dprint(polyB)
                    dprint('*'*20)
                break
            if pdeb : dprint('B : %s %s %s'%(ciB,c[0],c[1]))
            try :
                ciA=polyA.index(c)
                A=True
                if pdeb : dprint('match A in %s'%ciA)
                ciA=(ciA+1)%(len(polyA))
            except :
                #ciB -=1
                ciB=(ciB+1)%(len(polyB))
        #for t in range (1000000) : pass
    if pdeb : dprint('final : \n%s'%(newpoly))
    return newpoly


# if intersections,polyB will split polyA in section
# first point of polyA MUST NOT belong to any segment of polyB
def polyBool2(polyA,polyB,iSizeInt,bSticked,minl,op="inter",ptype="coord",pdeb=False) :
    #pdeb=False
    if ptype=="vector" : 
        polyA=vecToCoord(polyA)
        polyB=vecToCoord(polyB)

    if pdeb :
        dprint( "polyA :\n%s"%polyA)
        dprint( "polyB :\n%s"%polyB)

    A=polyA[0]
    B=polyA[1]
    
    #  if aPerim[0] starting point is on bobnewside, modify it before polyBool2()
    for ci in range(len(polyB)-1) :
        B=polyB[ci]
        C=polyB[ci+1]
        if aligned(B,C,A,True) :
            if pdeb : dprint('%s MUST be redefined'%A)
            l,d=readVec(Vector(B)-Vector(A))
            if l>=iSizeInt[0]:
                li=Puniform(iSizeInt[0],min(l,iSizeInt[1]))
            else :
                li=0.1
                if pdeb : dprint( 'small side' )
            v=writeVec(li,d)
            coord=B+v
            polyA=polyA[1:]
            polyA.insert(0,coord)
            if pdeb : 
                dprint( 'redefined polyA :\n%s'%polyA)
                dprint( 'was on %s %s'%(A,B) )
            A=polyA[0]
            B=polyA[1]
            break
    
    newpoly=[]
    ci=0
    ciC=len(polyB)-1
    seg=[]
    start=True
    while ci < len(polyA)-1 and ciC >= 0 :
        
        if start :
            if pdeb : dprint( 'in')
            B=polyA[ci+1]
            seg.append(A)
            if pdeb :
                dprint( '-> A %s %s / B %s %s (ci %s)'%(A[0],A[1],B[0],B[1],ci))
                dprint( seg )
            for ci2 in range(ciC,-1,-1) :
                C=polyB[ci2]
                if pdeb : dprint( 'C %s %s (ci2 %s)'%(C[0],C[1],ci2))            
                if aligned(A,B,C,True) :
                    seg.append(C)
                    if pdeb :dprint( 'ended one : %s'%seg)
                    newpoly.append(seg)
                    seg=[]
                    ciC=ci2
                    Cp=C
                    start=False
                    count=0
                    break
            if start :
                ci +=1
                A=polyA[ci]
        else :
            if pdeb :dprint( 'out')
            ciC -=1
            A=polyA[ci]
            B=polyA[ci+1]
            C=polyB[ciC]
            if pdeb : dprint( '-> A %s %s / B %s %s / C %s %s \n'%(A[0],A[1],B[0],B[1],C[0],C[1]))
            if aligned(A,B,C,True)==False :
                count +=1
                if count==3 or ciC==0:
                    lenght,dir=readVec(B-A)
                    if Puniform(0.0001,1) <= bSticked :
                        dprint('      .sticked [pbool2]',level=3)
                        li=minl
                    else : li=Puniform(iSizeInt[0],min(lenght,iSizeInt[1]))
                    v=writeVec(li,dir)
                    A=Cp+v
                    start=True
            else :
                count=0
                Cp=C
                if C==B : ci +=1
    if start :
        seg.append(B)
        newpoly.append(seg)
    if pdeb :dprint( 'final : \n%s'%newpoly)
    return newpoly


# find polygon auto-intersection
def polyInter(polys,ptype="vector",sameNum=False,list=[]) :
    try :
        a=polys[0][0][0]
        one=False
    except :
        polys=[polys]
        one=True
    if len(list)>0 : list=list[:]
    if ptype=="vector" : 
        polys=vecToCoord(polys)
        if len(list)>0 : list=vecToCoord(list)
    i=0
    pdeb=False
    while i < len(polys) :
        poly=polys[i]
        lp=len(poly)
        s=0
        if pdeb :dprint( '> next poly : %s'%i)
        while s < lp-2 :
            s2=s+2
            lp=len(poly)
            A=Vector(poly[s])
            B=Vector(poly[s+1])
            if pdeb :
                dprint( '> poly : %s'%i)
                dprint( '> A : %s B : %s'%(s,s+1))
                dprint( '> len : %s'%lp)
            while s2<lp :
                C=Vector(poly[s2])
                ciD=(s2+1)%lp
                D=Vector(poly[ciD])
                if pdeb : dprint( '  C : %s D: %s'%(s2,ciD))
                #if s2<lp-1 :D=Vector(poly[s2+1])
                #else :D=Vector(poly[0])
                if s==0 and s2==lp-1 :
                    if pdeb : dprint( 'cancel')
                    pass
                else :
                    inter=SegmentIntersect(A,B,C,D,False)
                    if inter != False :
                        if pdeb :dprint( 'inter : ')
                        polys.append([])
                        polys[-1]=poly[:]
                        if ciD<lp-1 :
                            del polys[-1][s2+1:]
                            del polys[-1][0:s+1]
                            del polys[i][s+1:s2+1]
                            polys[i].insert(s+1,inter[0])
                            polys[-1].insert(0,inter[0])
                            if sameNum :
                                    polys[i].insert(s+1,inter[0])
                                    polys[-1].insert(0,inter[0])
                        else :
                            del polys[i][s2+1:]
                            del polys[i][0:s+1]
                            del polys[-1][s+1:s2+1]
                            polys[-1].insert(s+1,inter[0])
                            polys[i].insert(0,inter[0])
                            if sameNum :
                                    polys[-1].insert(s+1,inter[0])
                                    polys[i].append(inter[0])
                        if pdeb :dprint( 'newpoly :\n%s'%polys[i])
                        s=0
                        break
                if pdeb :dprint('next CD')
                s2 +=1
            else :
                if pdeb :dprint('next AB')
                s +=1
        i +=1

    # remove duplicate coords
    if sameNum == False :
        for pi,p in enumerate(polys) :
            p2=[]
            for c in p :
                c=Vector(c)
                #if c not in p2 :
                if p2==[] or cfloat(c,'in',p2,0.001)==False :
                    p2.append(c)
            polys[pi]=p2
    
    #  remove lines
    for p in polys[:] :
        if len(p) < 3 : polys.remove(p)
    
    if len(list) > 0 :
        for i,poly in enumerate(list) :
            polys.insert(i,poly)
    if ptype=="vector" :polys=coordToVec(polys,True,True)
    if pdeb :
        dprint( 'childs :')
        for p in polys : dprint( '%s\n'%p)
    return polys


def polyClean(polys,ptype="vector",p=True,mark=False,pdeb=False) :
    pdab=pdeb
    if pdeb : dprint( "\npolyClean :")
    try :
        a=polys[0][0][0]
        one=False
    except :
        polys=[polys]
        one=True
    if ptype=="coord" : polys=coordToVec(polys,p)
    newpolys=[]
    deads=[]
    if p and pdeb : dprint( "ispoly")
    for ip,polyvec in enumerate(polys) :
        if pdab :
            if ip==7:pdeb=False
            else :pdeb=False
        dead=[]
        polycond=len(polyvec)>1 and p
        linecond=len(polyvec)>2 and p==False
        if p and linecond==False and pdeb : dprint( "abort. len : %s"%(len(polyvec)))
        if linecond or polycond :
            lp=len(polyvec)
            i=1
            l=0
            delete=0
            newpoly=[polyvec[0][:]]
            pos=polyvec[0][:]
            if pdeb :
                dprint( "------\npoly %s : depart %s"%(ip,pos))
                dprint( "%s\n------"%(polyvec))
            for i,vec in enumerate(polyvec) :
                if i>0 :
                    #if pdeb : dprint( vec,":"
                    vl,vd=readVec(vec)
                    if i==1 :
                        pvec=polyvec[-1-delete]
                        j=len(polyvec)-1-delete
                    else :
                        pvec=polyvec[i-1-delete]
                        j=i-1-delete
                    pvl,pvd=readVec(pvec)
                    #if pdeb : dprint( "-1 :",pvd,"0 :",vd,"len :",pvl,vl
                    add=False
                    # delete null and too small vectors
                    if cfloat(vl,'eq',0,0.0001) :
                        delete=1
                        l +=vl
                        if mark : dead.append(j)
                    else :
                        #dprint( vec
                        delete=0
                        pos=[pos[0]+vec[0],pos[1]+vec[1],pos[2]+vec[2]]
                        # don't add the last closing vector
                        #if i==lp-1 and polyvec[i]==pos :add=False
                        # merge vectors with the same orientation
                        if cfloat(vd,'eq',pvd,0.1) and (p or (p==False and i>1)):
                            l += vl
                            if pdeb : dprint( "merge")
                            if i==1 : 
                                l += pvl
                                newpoly[0]=[newpoly[0][0]-pvec[0],newpoly[0][1]-pvec[1],newpoly[0][2]]
                            if mark and i>1 : dead.append(j)
                            #dprint( "gotcha**%s %s %s %s"%(i,polyvec[i],pvec,l)
                        elif i>1 :
                            nvec=writeVec(l,pvd)
                            l=vl
                            add=True
                        else : l=vl
                        if add :
                            if pdeb : dprint( "added %s"%nvec)
                            newpoly.append(nvec)
            if p==False :
                nvec=writeVec(l,vd)
                newpoly.append(nvec)
            if pdeb : dprint( "cleaned : %s\n"%(newpoly))
        #else : newpoly=[[]]
        elif p : newpoly=[[]]
        else : newpoly=polyvec
        if pdeb :dprint( newpoly)
        newpolys.append(newpoly)
        if mark : deads.append(dead)    
    # return it, the same type than input type
    if ptype=="vector" :
        # lazzy : just to add last vector to close poly, if none
        newpolys=vecToCoord(newpolys)
        newpolys=coordToVec(newpolys)
    if ptype=="coord" : 
        newpolys=vecToCoord(newpolys,p)
        #dprint( newpolys[7]
    if one:
        if mark : return newpolys[0],deads
        else : return newpolys[0]
    else :
        if mark : return newpolys,deads
        else : return newpolys


# reshape polys whom edges are too thin
def polyUnedge(poly,minlenght=1,ptype="coord",pdeb=False) :
    dprint('* polyUnedge')
    if pdeb : dprint(poly)
    if len(poly) < 4 : return poly
    if ptype == "vector" : poly = vecToCoord(poly)
    test=True
    while test :
        lp=len(poly)#-1
        test=False
        #for ciB,B in enumerate(poly) :
        for ciB in range(len(poly)-2) :
            ciC=(ciB+1)%lp
            #B=Vector(poly[ciB]).resize3D()
            #C=Vector(poly[ciC]).resize3D()
            B, C = Vectors([poly[ciB],poly[ciC]])
            lBC,dBC = readVec(C-B)
            if lBC < minlenght :
                ciA=(ciB-1)%lp
                ciD=(ciB+2)%lp
                #A=Vector(poly[ciA]).resize3D()
                #D=Vector(poly[ciD]).resize3D()
                A, D = Vectors([poly[ciA],poly[ciD]])
                if pdeb :
                    dprint( 'C-B too short')
                    dprint( 'A %s %s'%(ciA,A))
                    dprint( 'B %s %s'%(ciB,B))
                    dprint( 'C %s %s'%(ciC,C))
                    dprint( 'D %s %s'%(ciD,D))
                para,dir=parallel(A,B,C,D,True)
                if para and dir==False :
                    if pdeb : dprint( 'AB CD //')
                    lAB,d=readVec(B-A)
                    lCD,d=readVec(D-C)
                    if lAB <= lCD :
                        N=A+(C-B)
                    else :
                        N=D-(C-B)
                    del poly[ciC]
                    del poly[ciB]
                    poly.insert(ciB,N)
                    test=True
                    break
    if ptype=="vector" :poly=coordToVec(poly)
    return poly


## from a vector, returns its length and its direction in degrees
# direction is planar, from x y components
def readVec(side) :
    a=side[0]
    c=side[1]
    try :
        lenght=sqrt((a*a)+(c*c))
    except :
        dprint('error lenght (except readvec): %s'%(side),4)
        if str(a)=='-1.#IND00' : a=0
        if str(c)=='-1.#IND00' : c=0
        lenght=0
    if str(lenght)=='nan' :
        dprint('error lenght (readvec): %s'%(side),4)
        a=c=0
    rot=atan2( c, a )*(180/pi)
    if str(rot)=='nan' :
        dprint('error rot (readvec) : %s %s'%(side,lenght),4)
    #return lenght,fixfloat(rot)
    return lenght,rot

## from a length and a direction in degrees, returns a vector
# direction is planar, from x y components
def writeVec(lenght,alpha,z=0) :
    beta=radians((90-alpha))
    alpha=radians(alpha)
    x=(lenght * sin(beta)) / sin(alpha+beta)
    y=(lenght * sin(alpha)) / sin(alpha+beta)
    if cfloat(x,'eq',round(x),0.0001) :x=round(x)
    if cfloat(y,'eq',round(y),0.0001) :y=round(y)
    return Vector([x,y,z])


## float/list comparison
# x and y are either floats or 2 lists of same lenght (2 verts for example)
def cfloat(x,comp,y,floattest=0.1) :
    try :t=y[0]
    except :
        x=[float(x)]
        y=[float(y)]
    if comp=="in" :
        for f in y :
            try :
                t=f[0]
                for v in y :
                    for ci,c in enumerate(x) :
                        #if str(abs(c-v[ci])) > str(floattest) : break
                        if abs(c-v[ci]) > floattest : break
                    else : return True        
                return False
            except :
                #if str(abs(x-f)) <= str(floattest) : return True
                if abs(x-f) <= floattest : return True
        return False
    else :
        for i in range(len(x)) :
            if comp=="eq" and abs(x[i]-y[i]) > floattest : return False
            elif comp=="not" and abs(x[i]-y[i]) <= floattest : return False
        return True


def angleEnlarge(c0,c1,c2,w) :
    try :t=w[0]        # variable width
    except :w=[w,w] # uniform offset
    c0=Vector(c0)
    c1=Vector(c1)
    c2=Vector(c2)
    
    v0=c1-c0
    v1=c2-c1
    
    sz, rot = readVec(v0)
    b = writeVec(w[0],rot-90)
    b = b + c0
    c = b + v0
    
    sz, rot = readVec(v1)
    d = writeVec(w[1],rot-90)
    d = d + c1
    e = d + v1    
    # TODO line_line always returns a tuple (never a None like line_2d)
    interlist = geometry.intersect_line_line(b,c,d,e)
    print(interlist)
    if type(interlist) != type(None) :
        return interlist[0]
    else :
        return c

# return angle of c1 where c0,c1,c2 are coords
# the coords order define which angle you want (anti-clockwise)
# TODO compare with mathutils Vector() :  v1.angle(v2,fallback) returns radians or fallback when given
# Zero length vectors raise an AttributeError
def Angle(c0,c1,c2,all=False,ptype='coord') :
    sz=[0,0,0]
    r=[0,0,0]
    if ptype=='coord' :
        sz[0],r[0]=readVec([c1[0]-c0[0],c1[1]-c0[1]])
        sz[1],r[1]=readVec([c2[0]-c1[0],c2[1]-c1[1]])
        sz[2],r[2]=readVec([c2[0]-c0[0],c2[1]-c0[1]])
    else :
        sz[0],r[0]=readVec(Vector(c0))
        sz[1],r[1]=readVec(Vector(c1))
        sz[2],r[2]=readVec(Vector(c0)+Vector(c1))
        
    angle=degrees(acos( (sz[0]**2+sz[1]**2-sz[2]**2) / (2*sz[0]*sz[1]) ))

    if r[0]>0 and r[1]<0 : d=r[1]+360
    else : d=r[1]
    
    if r[0] < d and d < r[0]+180 : pass
    else :angle = 360-angle
    """
    angle=r[1]-r[0]
    if angle<-180 : angle +=360
    if angle>180 : angle -=360
    if angle>0 : angle -=180
    else : angle +=180
    if angle<0 : angle=abs(angle)
    else : angle -=360
    """
    if all : return angle,sz,r
    else :return angle

## check if 3 points are aligned
def aligned(p1,p2,p3,Cin=False,pdeb=False) :
    if pdeb :
        dprint('aligned :')
        dprint('p1 : %s'%p1)
        dprint('p2 : %s'%p2)
        dprint('p3 : %s'%p3)
    p1=[float(p1[0]),float(p1[1])]
    p2=[float(p2[0]),float(p2[1])]
    p3=[float(p3[0]),float(p3[1])]
    tolerance=0.0009
    if Cin :
        if p3[0] < min(p1[0],p2[0]) - tolerance or p3[0] > max(p1[0],p2[0]) + tolerance or \
           p3[1] < min(p1[1],p2[1]) - tolerance or p3[1] > max(p1[1],p2[1]) + tolerance :
            if pdeb : dprint('C not in [AB]')
            return False
    var=0.005
    if cfloat(p1[0],'not',p2[0],var) :
        if pdeb : dprint('A not null')
        a=(p2[1]-p1[1])/(p2[0]-p1[0])
    elif cfloat(p1[1],'eq',p2[1],var) : return True
    elif cfloat(p3[0],'eq',p1[0],var) : return True
    else : a=0
    b=p1[1]-a*p1[0]
    if pdeb :
        dprint('%s %s'%(a,b))
        dprint('%s %s'%(p3[1],p3[0]*a+b))
    if cfloat(p3[1],'eq',p3[0]*a+b,var) : return True
    else : return False


# check if (AB) // (CD) (degree comparison)
# check directions of vectors too.
# merged lines return True
def parallel(A,B,C,D,dir=False,tolerance=0.03,pdeb=False) :

    A,B,C,D = Vectors([A,B,C,D])

    l,dAB=readVec(B-A)
    l,dBA=readVec(A-B)
    l,dCD=readVec(D-C)

    abcd=cfloat(dAB,'eq',dCD,tolerance)
    bacd=cfloat(dBA,'eq',dCD,tolerance)
    if abcd or bacd :
        if pdeb :
            dprint('%s %s and %s %s'%(A,B,C,D))
            dprint('%s %s or %s %s'%(dAB,dCD,dBA,dCD))
            dprint('%s %s'%(abcd,bacd))
            dprint('are parallel')
        if dir == False : return True
        elif abcd :
            if pdeb : dprint('same dir')
            return True,True
        else :
            if pdeb : dprint('inverse dir')
            return True,False
    elif dir : return False,False
    else : return False

## convert list of list/tuple into vector / change vector dimensions
def Vectors(vlist,dim = 3) :
    nvlist = []
    for v in vlist :
        #if type(v) == list or type(v) == tuple : v = Vector(v)
        if type(v) != Vector : v = Vector(v)
        if len(v) != dim :
            if dim == 2 : v.resize_2d()
            elif dim == 3 : v.resize_3d()
            elif dim == 4 : v.resize_4d()
            else : v.resize_3d()
        nvlist.append(v)
    return nvlist

# returns coordinate of segments [A,B] and [C,D] intersection, on a XY plan (not world !)
# input segment [AB] and segment [CD]. each can be either vector or list x,y / x,y,z
# return either false or the LineIntersect results. LineIntersect(A,B,C,D)[0] is the intersection coord.
def SegmentIntersect(A,B,C,D,point=True,more=False,pdeb=False) :

    A,B,C,D = Vectors([A,B,C,D])
    #"l,dAB=readVec(B-A)
    #l,dBA=readVec(A-B)
    #l,dCD=readVec(D-C)
    dec=0.03
    #if cfloat(dAB,'not',dCD,dec) and cfloat(dBA,'not',dCD,dec) :
    if parallel(A,B,C,D,False)==False :
        if (( signedarea(A, B, C) * signedarea(A, B, D) <= 0) and ( signedarea(C, D, A) * signedarea(C, D, B) <= 0)) :
            #inter=LineIntersect(A,B,C,D)
            inter = geometry.intersect_line_line(A,B,C,D)
            # if (AB)=(CD) : return none
            #if type(inter)!=type(tuple()) :
            #    if pdeb :print 'nonetype'
            #    return False
            # if (AB)=(CD) bis : return -1.#IND
            #elif str(inter[0][0])=='-1.#IND' :
            #    if pdeb :print '-1#IND'
            #    return False
            
            # if (AB)=(CD) : return none
            if type(inter) != type(tuple()) or str(inter[0][0]) == 'nan':
                if pdeb : dprint('parrallel')
                return False
            # inter is equal to A,B,C or D : shall we include them ?
            elif point == False and \
                ( cfloat(inter[0],'eq',A,dec) or \
                cfloat(inter[0],'eq',B,dec) or \
                cfloat(inter[0],'eq',C,dec) or \
                cfloat(inter[0],'eq',D,dec)) :
                    if pdeb : dprint('canceled : %s is an extremity'%inter[0])
                    return False
            # ok
            else : return inter
        elif pdeb : dprint('segments')
    # segments doesn't cross ( parralel or merged )
    elif more :
        if pdeb : dprint('parallels')
        return False,True
    return False

# segmentintersect sub-function
def signedarea(A,B,C) :
    sa=((B.x-A.x)*(C.y-A.y) - (B.y-A.y)*(C.x-A.x))/2
    if cfloat(sa,'eq',0,0.001) : sa=0
    return sa
