import random
from random import uniform as Puniform
import bpy
import mathutils
from mathutils import *
from blended_cities.core.class_main import *
from blended_cities.utils.meshes_io import *
from blended_cities.core.ui import *
from blended_cities.utils import  geo
from blended_cities.utils import  geo_tests
from blended_cities.utils.geo_tests import  cutB

class BC_lots(BC_elements,bpy.types.PropertyGroup) :
    bc_label = 'Building Lots'
    bc_description = 'build lots inside perimeters (alpha)'
    bc_collection = 'lots'
    bc_element = 'lot'

    #name = bpy.props.StringProperty()
    parent = bpy.props.StringProperty() #  name of the group it belongs to

    minBuildingSize = bpy.props.FloatProperty(
        default = 5,
        min = 3,
        max = 100,
        update=updateBuild
        )
    maxBuildingSize = bpy.props.FloatProperty(
        default = 15,
        min = 3,
        max = 100,
        update=updateBuild
        )
    minBuildingSideSize = bpy.props.FloatProperty(
        default = 5,
        min = 3,
        max = 100,
        update=updateBuild
        )
    maxBuildingSideSize = bpy.props.FloatProperty(
        default = 15,
        min = 3,
        max = 100,
        update=updateBuild
        )
    minIntervalSize = bpy.props.FloatProperty(
        default = 1,
        min = 0.1,
        max = 10,
        update=updateBuild
        )
    maxIntervalSize = bpy.props.FloatProperty(
        default = 2,
        min = 0.1,
        max = 10,
        update=updateBuild
        )
    stickedBuilding = bpy.props.FloatProperty(
        default = 0.5,
        min = 0.0,
        max = 1.0,
        update=updateBuild
        )

    def build(self,data) :
        '''
                    SISMi[0]=button(SISMi,col34,pos,sx4,sy,'',buildingIntMinSpace_tt)
                    SISMx[0]=button(SISMx,col44,pos,sx4,sy,'',buildingIntMaxSpace_tt)

                    text(buildingFrontWidth_text+" :",col1,pos,'small')
                    text(buildingSticked_text+" :",col22,pos,'small')

        bSizeInt    SBSMi[0]=buildingMinFrontSize_tt
        bSizeInt    SBSMx[0]=buildingMaxSize_tt
                    SBST[0]=button(SBST,col22,pos,sx,sy,"Var  ",buildingSticked_tt)

                    text(buildingDepthWidth_text+" :",col1,pos,'small')
                    text(buildingMinSideSize_text+" :",col22,pos,'small')

        bsSizeInt    SBDMi[0]=button(SBDMi,col1,pos,sx4,sy,'',buildingMinSize_tt)
        bsSizeInt    SBDMx[0]=button(SBDMx,col24,pos,sx4,sy,'',buildingMaxSize_tt)
        '''
        random.seed('abcde')
        pdeb = False
        #vert_offset = 0

        minSideSize = 2        ## bMinSize SBMS
        minBuildingArea = 10   ## bAreaInt[0]
        minBuildingSize = self.minBuildingSize ## bSizeInt[0] SBSMi
        maxBuildingSize = self.maxBuildingSize ## bSizeInt[1] SBSMx
        minBuildingSideSize = self.minBuildingSideSize ## bsSizeInt[0] SBDMi
        maxBuildingSideSize = self.maxBuildingSideSize ## bsSizeInt[1] SBDMx
        minIntervalSize = self.minIntervalSize ## iSizeInt[0] SISMi
        maxIntervalSize = self.maxIntervalSize ## iSizeInt[1] SISMx
        IntervalSize = [minIntervalSize,maxIntervalSize]
        BuildingSize = [minBuildingSize,maxBuildingSize]
        stickedBuilding =  self.stickedBuilding ## bSticked   sticked building chances (1=sticked)
        lotBalance = 0.5
        minl = 0.1
        # the objects generated here will be contained in :
        elements = []
        outlines = []

        verts = []
        faces = []
        mats  = []

        #fof = 0
        #z = self.blockHeight
        perimeters = data['perimeters']

        for bob in perimeters :
            A=area(bob)
            # get rid of areas below the minimum building area
            if A >= minBuildingArea :
                bldgs=[]
                bobevos=[bob[:]]
                bobnewsides=[]
                bobnewside=[]
                # perimeter lenght :
                L=perimeter(bob,ptype="coord")

                bobv=coordToVec(bob)

                #init - build start and end points of the perimeter, reorder
                #aPerim=[vcoords(bob[:-1])]
                aPerim=[bob[:-1]]
                lenght,dir=readVec(aPerim[0][1]-aPerim[0][0])
                if lenght >= minBuildingSize + minIntervalSize :
                    if Puniform(0.0001,1) <= stickedBuilding : li0 = minl
                    else : li0 = Puniform(minIntervalSize,min(lenght,maxIntervalSize))
                    lb0 = Puniform(minBuildingSize,min(lenght-li0,maxBuildingSize))
                else :
                    lb0=lenght-minl
                    li0=minl
                v = writeVec(lb0+li0,dir)
                coordS = aPerim[0][0] + v
                aPerim[0] = [coordS] + aPerim[0][1:] + [aPerim[0][0]] + [coordS]
                ci = 0
                first = True

                while len(aPerim) > 0 :

                    
                    if len(bobnewside) > 0 :
                        # ##############################################
                        # redefine collision area / new starting point #
                        # ##############################################
                        
                        dprint('      .redefine collision area / spawn segments:',level=2)
                        try :
                            bnsori=bobnewside[:]
                            bobnewside=polyUnedge(bobnewside,minSideSize)

                        except :
                            print( 'bug :')
                            print(bobnewside)
                            bobnewside=polyUnedge(bnsori,minSideSize,pdeb=False)
                        if pdeb :
                            print('\nnew col line :\n',bobnewside)
                            print('\ninput aperim :\n',)
                            for aP in aPerim : print(aP)
                            
                        # redefine the spawn/perimeter building segments
                        # according to the new building collision 'yard' line
                        nap=[]
                        for seg in aPerim :
                            seg=polyBool2(seg,bobnewside,IntervalSize,stickedBuilding,minl,pdeb=pdeb)
                            nap.extend(seg)
                        aPerim=[]

                        # exclude segments that are too smalls to build a front
                        for seg in nap :
                            if len(seg)>1 :
                                l,d=readVec(Vector(seg[1])-Vector(seg[0]))
                                if len(seg)>=3 :
                                    l2,d=readVec(Vector(seg[2])-Vector(seg[1]))
                                    l +=l2
                                dprint('      .spawn segment : %.2f,%.2f - %.2f,%.2f (len %s)'%(seg[0][0],seg[0][1],seg[-1][0],seg[-1][1],len(seg)),level=2)
                                #if (len(seg)>=3 and seg[0]!=seg[1]) or (len(seg)==2 and l >= minBuildingSize) :
                                if l >= minBuildingSize and seg[0]!=seg[1] :
                                    aPerim.append(seg)
                                    dprint('      kept',level=2)
                                else :dprint('      removed',level=2)

                        if len(aPerim) > 0 :
                            # define the new collision domain for incoming buildings
                            bobnewsides.extend(bobnewside)
                            bobnewsides=polyUnedge(bobnewsides,minSideSize)
                            bes=bobnewsides[:]
                            
                            # merge new buildings line to the other
                            C=bobnewside[-1]
                            for ci in range(len(bob)-1) :
                                A=bob[ci]
                                B=bob[(ci+1)%(len(bob))]
                                if aligned(A,B,C,True) :break
                            ci +=1
                            if ci != 1 or first :
                                bes.extend(bob[ci:])
                                first=False
                            #print 'bobnewsides :',ci,'\n',bes
                            #print 'main collision domain :'
                            #for b in bes :
                            #    print b
                            #buildingAreas.append(bes[:])
                            bes = polyInter(bes,ptype="coord")
                            bobevos=[]

                            dprint('      .collision domains :',level=2)
                            for b in bes :
                                dprint('%s'%b,level=3)
                                #dprint('      .%.2f,%.2f - %.2f,%.2f (len %s)',(b[0][0],b[0][1],b[-1][0],b[-1][1],len(b)),level=2)
                                keep=False
                                for ci,A in enumerate(b) :
                                    B=b[(ci+1)%(len(b))]
                                    
                                    for seg in aPerim :
                                        l,d=readVec(seg[1]-seg[0])
                                        coord=writeVec(l/2,d)
                                        coord=seg[0]+coord
                                        dprint('      %s'%coord,level=2)
                                        if aligned(A,B,coord,True) :
                                            keep=True
                                            break
                                if keep :
                                    dprint('kept',level=2)
                                    bobevos.append(b)
                                else : dprint('removed',level=2)
                            # no more collision domains (or too small), end of block
                            if len(bobevos)==0 : aPerim=[]

                        # this sidewalk block has been subdivided into several blocks of buildings. remove the smallest ones.
                        #if len(bobevos)>1 :bobevos=polyInCheck(bam,bas,ptype="coord")

                        #if ci==len(bob)-2:
                        #    buildingAreas.append(bobevo)
                    elif pdeb : print( 'no change')

                    if len(aPerim) > 0 :
                        dprint('\n      .current aperim : \n       from %.2f,%.2f to %.2f,%.2f'%(aPerim[0][0][0],aPerim[0][0][1],aPerim[0][-1][0],aPerim[0][-1][1]),level=3)

                        if cfloat(aPerim[0][0],'eq',aPerim[0][1]) :
                            dprint('      .deleted first coord, too close the next one',level=3)
                            del aPerim[0][0]
                        side = aPerim[0][0:3]
                        dprint('      .build spawn segment 1 : \n       from %.2f,%.2f to %.2f,%.2f'%(side[0][0],side[0][1],side[-1][0],side[-1][1]),level=3)

                        lenght0,dir = readVec(side[1]-side[0])
                        if len(side) == 3 :
                        # last point of the last (angle) building
                            lenghts = cutB(lenght0,BuildingSize,IntervalSize,stickedBuilding)
                            lenght,dirn = readVec(side[2]-side[1])
                            # enough lenght
                            if lenght >= minBuildingSize + minIntervalSize:
                                if Puniform(0.0001,1) <= stickedBuilding :
                                    dprint('      .sticked',level=3)
                                    li=minl
                                else : li=Puniform(minIntervalSize,min(lenght,maxIntervalSize))
                                if side[2] == coordS :
                                    dprint('      .last one !',level=3)
                                    ln=lenght-li
                                    del aPerim[0]
                                else :
                                    ln=Puniform(minBuildingSize,min(lenght-li,maxBuildingSize))
                                    v=writeVec(ln+li,dirn)
                                    coord=side[1]+v
                                    aPerim[0]=[coord]+aPerim[0][2:]
                                    dprint('      .lenght ok - next start : %s'%coord,level=3)
                                    if pdeb : print(coord)
                            # side too small
                            else :
                                ln=lenght-minl
                                li=minl
                                aPerim[0]=aPerim[0][2:]
                                dprint('      .too small - next start : %s'%aPerim[0][0],level=3)
                            v=writeVec(ln,dirn)
                            side[2]=side[1]+v
                            if len(aPerim)>0 and len(aPerim[0])==1 :del aPerim[0]

                        else :
                            if lenght0 >= minIntervalSize:
                                if Puniform(0.0001,1) <= stickedBuilding :li=minl
                                else : li=Puniform(minIntervalSize,min(lenght0,minIntervalSize))
                            else :li=minl
                            lenght0 -=li
                            v=writeVec(lenght0,dir)
                            lenghts=cutB(lenght0,BuildingSize,IntervalSize,stickedBuilding)
                            side[1]=side[0]+v
                            del aPerim[0]
                        dprint('      .build spawn segment 2 : \n       from %.2f,%.2f to %.2f,%.2f'%(side[0][0],side[0][1],side[-1][0],side[-1][1]),level=2)
                        dprint('      .left aperim : \n       %s'%(aPerim),level=2)

                        bobnewside=[]
                        coord=side[0]
                        bldgs=[[coord]]

                        # create coords of the building points on the perimeter
                        dprint('      .lenghts :\n       %s'%lenghts,level=2)
                        vl=0
                        for li,l in enumerate(lenghts) :
                            v=writeVec(l,dir)
                            coord=[coord[0]+v[0],coord[1]+v[1],coord[2]+v[2]]
                            if li%2==0 :bldgs[-1].append(coord)    # building 2nd  point
                            else :bldgs.append([coord])            # building 1st point
                            vl +=l
                        dprint('      .lenght check : %s = %s'%(vl,lenght0),level=3)
                        # last point of the last (angle) building
                        if len(side)==3 : bldgs[-1].append(side[2])

                        # #############################
                        # find current colision domain
                        # #############################
                        bk=False
                        for bobevo in bobevos :
                            if pdeb :
                                print('segmented in :')
                                print(bobevo)
                            for ci,a in enumerate(bobevo) :
                                b=bobevo[(ci+1)%(len(bobevo))]
                                if pdeb : print(b)
                                if aligned(a,b,bldgs[0][0],True) :
                                    bk=True
                                    #bobevo=polyUnedge(bobevo,minSideSize) #,minlenght=1,ptype="coord")
                                    #buildingAreas.append(bobevo)
                                    break
                            if bk : break
                        dprint('      .current spawn segment : \n       from %.2f,%.2f to %.2f,%.2f (%s buildings)'%(side[0][0],side[0][1],side[-1][0],side[-1][1],len(bldgs)),level=3)
                        dprint('      .current collision area (%s):\n       from %.2f,%.2f to %.2f,%.2f'%(bk,bobevo[0][0],bobevo[0][1],bobevo[-1][0],bobevo[-1][1]),level=3)
                        
                        # #########################
                        # define building perimeter
                        # #########################
                        for bldgi,bldg in enumerate(bldgs) :
                            if bldgs[bldgi] != 0 :
                                #if len(buildingAreas)+bldgi+1==debugBuilding>=0 : pdeb=True
                                #else : pdeb=False
                                #
                                # building points on the perimeter
                                # 2 or 3 points ?
                                sl = Puniform(minBuildingSize,maxBuildingSize)
                                if len(bldg) == 3 :
                                    if cfloat(bldg[0],'eq',bldg[1]) :
                                        l,d = readVec(bldg[2] - bldg[1])
                                        coord = writeVec(0.1,d)
                                        bldg = [bldg[1] + coord, bldg[2]]
                                        if pdeb : dprint( 'case point too near : 3 -> 2 points : %s'%bldg)
                                    elif cfloat(bldg[1],'eq',bldg[2]) :
                                        l,d = readVec(bldg[0] - bldg[1])
                                        coord = writeVec(0.1,d)
                                        bldg = [bldg[0], bldg[1] + coord]
                                        if pdeb : dprint('case point too near : 3 -> 2 points : %s'%bldg)
                                    else : angle, sz, r = Angle(bldg[0],bldg[1],bldg[2],True)
                                
                                a1 = bldg[-1]
                                b1 = bldg[0]

                                if pdeb : print('---')
                                dprint('        .building %s (%s/%s) at %.2f,%.2f<DOT>'%(len(elements)+bldgi+1,bldgi+1,len(bldgs),b1[0],b1[1]),level=3)
                                #
                                # building points in the area
                                #
                                
                                # 2nd point max pos
                                lmaxa2 = 10000
                                v1 = [ bldg[-2][0] - a1[0], bldg[-2][1] - a1[1], bldg[-2][2] - a1[2] ]
                                l,dir1 = readVec(v1)
                                v1 = writeVec(lmaxa2,dir1-90)
                                a2 = [ a1[0] + v1[0], a1[1] + v1[1], a1[2] + v1[2] ]
                                #ll=10000
                                #lmaxa2=minBuildingSize
                                #dprint('A1 : %.2f,%.2f',(a1[0],a1[1]),level=2)

                                for ci1,c in enumerate(bob) :
                                    ci2=(ci1+1)%(len(bob)-1)

                                    #if aligned(a1,a2,c)==False and aligned(a1,a2,bob[ci2])==False :
                                    if aligned(a1,c,bob[ci2])==False :

                                    #if (bldgi<len(bldgs)-1 and bob[ci2]!=bob[ci+1]) or (bldgi==len(bldgs)-1 and c!=bob[ci+1]):
                                        #print c,bobevo[ci2]
                                        inter=SegmentIntersect(a1,a2,c,bob[ci2])
                                        if inter != False :
                                            if pdeb :print('inter',c,bob[ci2])
                                            v=[inter[0][0]-a1[0],inter[0][1]-a1[1],inter[0][2]-a1[2]]
                                            l,dir=readVec(v)
                                            if l<lmaxa2 :
                                                #ll=Puniform(min(minBuildingSize,l),min(l*0.5,maxBuildingSize))
                                                #dprint('inter with bound %.2f,%.2f /  %.2f,%.2f',(c[0],c[1],bob[ci2][0],bob[ci2][1]))
                                                #if l>=minBuildingSize : sl=ll
                                                lmaxa2=l

                                # 3rd point max pos
                                lmaxb2 = 10000
                                v2=[b1[0]-bldg[1][0],b1[1]-bldg[1][1],b1[2]-bldg[1][2]]
                                l,dir2=readVec(v2)
                                v2=writeVec(lmaxb2,dir2-90)
                                b2=[b1[0]+v2[0],b1[1]+v2[1],b1[2]+v2[2]]

                                dprint('         2 : %.2f,%.2f'%(a1[0],a1[1]),level=2)
                                for ci1,c in enumerate(bob) :
                                    ci2=(ci1+1)%(len(bob)-1)

                                    #if aligned(b1,b2,c)==False and aligned(b1,b2,bob[ci2])==False :
                                    if aligned(b1,c,bob[ci2])==False :
                                        #print c,bobevo[ci2]
                                        inter=SegmentIntersect(b1,b2,c,bob[ci2])
                                        if inter != False :
                                            if pdeb :print('inter',c,bob[ci2])
                                            v=[inter[0][0]-b1[0],inter[0][1]-b1[1],inter[0][2]-b1[2]]
                                            l,dir=readVec(v)
                                            if l<lmaxb2 :
                                                #ll=Puniform(min(minBuildingSize,l),min(l*0.5,maxBuildingSize))
                                                #dprint('inter with bound %.2f,%.2f /  %.2f,%.2f',(c[0],c[1],bob[ci2][0],bob[ci2][1]))
                                                lmaxb2=l
                                    elif pdeb :    print('excluded')

                                # depth calculation preserve rectangular shape
                                l=min(lmaxa2,lmaxb2)
                                dprint('         available lenght : %s'%l,level=3)
                                if l > minBuildingSideSize :
                                    # if l*lotBalance <= minBuildingSideSize : l=l*lotBalance#Puniform(l*lotBalance,minBuildingSideSize)
                                    # else : l=Puniform(minBuildingSideSize,min(l*lotBalance,maxBuildingSideSize))
                                    if l <= maxBuildingSideSize and Puniform(0.0001,1) <= lotBalance :
                                        l = maxBuildingSideSize + 1
                                        dprint('         max (l<max) : %s'%l,level=3)
                                    elif minBuildingSideSize + maxBuildingSideSize > l :
                                        l=Puniform(minBuildingSideSize,l-minBuildingSideSize)
                                        dprint('         reserve space : %s'%l,level=3)
                                    else :
                                        l=Puniform(minBuildingSideSize,maxBuildingSideSize)
                                        dprint('         normal : %s'%l,level=3)

                                else :
                                    # take the whole depth of the part of this area
                                    # is outside. we'll cut later during polybool
                                    # +1 to avoid float errors
                                    l = minBuildingSideSize+1
                                    dprint('         max (l<mim) : %s'%l,level=3)

                                v1=writeVec(l,dir1-90)
                                a2=[a1[0]+v1[0],a1[1]+v1[1],a2[2]+v1[2]]
                                v=writeVec(l,dir2-90)
                                b2=[b1[0]+v[0],b1[1]+v[1],b1[2]+v[2]]
                                dprint('         3 : %.2f,%.2f'%(a2[0],a2[1]),level=2)
                                dprint('         4 : %.2f,%.2f'%(b2[0],b2[1]),level=2)
                                

                                # case when b1 = an angle and b1 outside - cancel
                                #if pointInPoly(b2[0],b2[1],bob)==False :
                                #    print 'b1 angle and b2 outside'
                                #    bldgs[bldgi]=0

                                if bldgs[bldgi]!=0 :
                                    n2=a1
                                    if len(bldg)==3 :
                                        vstart=2
                                        inter=SegmentIntersect(a1,a2,b1,b2)
                                        if inter!=False :
                                            coords=[inter[0]]                                                    

                                        elif angle<=135 :
                                            # 3 side
                                            v=writeVec(300000,dir2-90)
                                            bl2=[b1[0]+v[0],b1[1]+v[1],b1[2]+v[2]]
                                            v=writeVec(300000,dir1-90)
                                            al2=[a1[0]+v[0],a1[1]+v[1],a2[2]+v[2]]
                                            interA=SegmentIntersect(a1,al2,b1,bldg[1])
                                            interB=SegmentIntersect(b1,bl2,bldg[1],a1)
                                            if interA!=False :
                                                if pdeb : print('3 sides')
                                                bldgs[bldgi][0]=interA[0]
                                                coords=[]
                                                #bobnewside.extend([interA[0],a1])
                                            elif interB!=False :
                                                if pdeb : print('3 sides')
                                                bldgs[bldgi][2]=interB[0]
                                                coords=[]
                                                #bobnewside.extend([b1,interB[0]])
                                                n2=interB[0]
                                                n1=bldgs[bldgi][1]
                                            else :
                                                interA=SegmentIntersect(a1,al2,b1,b2)
                                                interB=SegmentIntersect(b1,bl2,a1,a2)
                                                inter=SegmentIntersect(a1,a2,b1,b2)
                                                if interA != False :
                                                    if pdeb : print('4 sides')
                                                    coords=[interA[0]]
                                                    #bobnewside.extend([b1,interA[0],a1])
                                                elif interB != False :
                                                    if pdeb : print('4 sides')
                                                    coords=[interB[0]]
                                                    #bobnewside.extend([b1,interB[0],a1])
                                                elif inter != False :
                                                    if pdeb : print('4 sides')
                                                    coords=[inter[0]]
                                                    #bobnewside.extend([b1,inter[0],a1])
                                                else :
                                                    if pdeb : print('5 sides')
                                                    coords=[a2,b2]
                                                    #bobnewside.extend([b1,b2,a2,a1])

                                        # angle building with 6 sides
                                        else :
                                            if pdeb : print('6 sides')
                                            v=writeVec(10000,dir2-180)
                                            b3=[b2[0]+v[0],b2[1]+v[1],b2[2]+v[2]]
                                            v=writeVec(10000,dir1)
                                            a3=[a2[0]+v[0],a2[1]+v[1],a2[2]+v[2]]
                                            inter=SegmentIntersect(a2,a3,b2,b3)

                                            if inter != False :
                                                coords=[a2,inter[0],b2]
                                                n2=bldgs[bldgi][2]
                                                #bobnewside.extend([b1,b2,inter[0],a2,a1])
                                            else :
                                                inter=SegmentIntersect(a2,a3,b1,b2)
                                                if inter != False :
                                                    coords=[a2,inter[0]]
                                                    n2=bldgs[bldgi][2]
                                                    #bobnewside.extend([b1,inter[0],a2,a1])
                                                else :
                                                    inter=SegmentIntersect(a1,a2,b2,b3)
                                                    if inter != False :
                                                        coords=[inter[0],b2]
                                                        n2=bldgs[bldgi][2]
                                                        #bobnewside.extend([b1,b2,inter[0],a1])
                                                    else :
                                                        coords=[a2,b2]
                                                        n2=bldgs[bldgi][2]
                                                        #bobnewside.extend([b1,b2,a2,a1])

                                    # side building 4 sides
                                    else :
                                        coords=[a2,b2]
                                        #bobnewside.extend([b1,b2,a2,a1])
                                        n2=a1
                                        vstart=1

                                    # append new  coords to building. test collision with other buildings
                                    bldgs[bldgi]=bldg
                                    lb=len(bldgs[bldgi])-1
                                    bldgs[bldgi].extend(coords)

                                    if pdeb :
                                        print(coords)
                                        print('send bldgs :\n %s'%bldgs[bldgi])
                                        print('send bobevo :\n %s'%bobevo)

                                    bldgs[bldgi] = polyBool(bldgs[bldgi],bobevo,start=vstart,pdeb=pdeb)

                                    # reshape the collision poly
                                    bns=bldgs[bldgi][lb:]
                                    bns.reverse()
                                    bns.insert(0,bldgs[bldgi][0])
                                    bobnewside.extend(bns)

                                else :
                                    print('canceled')
                                    if bldgi==len(bldgs)-1 :
                                        coord=bldg[-1]
                                        dir=dirn
                                        print('extend',bldg)
                        bldgs=polyClean(bldgs,ptype="coord")
                        for each in bldgs :
                            #buildingAreas.append([each,pli])
                            edges = edgesLoop(0,len(each))
                            elements.append( ['outline', each, edges, [], [] ] )
                            #vert_offset += len(each)
                #ci +=1
                #pedestrianPath.append(polyIn(bob[:],w/2,ptype="coord"))
                dprint('</DOTS>')
            # keep them for another use
            else :
                #buildingAreas.append([bob,pli])
                edges = edgesLoop(0,len(bob))
                elements.append( ['outline', bob, edges, [], [] ] )
                #vert_offset += len(bob)

        # outlines.append( ['outline', outline_verts, outline_edges, [], [] ] )

        #sidewalks = [ verts, [], faces, [] ]
        #elements.append(sidewalks)
        #elements.extend(outlines)

        return elements

    def height(self,offset=0) :
        return self.blockHeight

# a city element panel
class BC_lots_panel(bpy.types.Panel) :
    bl_label = 'Building Lots'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'building_lots'

    @classmethod
    def poll(self,context) :
        return pollBuilders(context,'lots')


    def draw_header(self, context):
        drawHeader(self,'builders')


    def draw(self, context):
        city = bpy.context.scene.city
        modal = bpy.context.window_manager.modal
        scene  = bpy.context.scene
        ob = bpy.context.active_object
        # either the building or its outline is selected : lookup
        #sdw, otl = city.elementGet(ob)
        elm, grp, otl = city.elementGet('active',True)
        blot = grp.asBuilder()

        layout  = self.layout
        layout.alignment  = 'CENTER'

        row = layout.row()
        row.label(text = 'Name : %s / %s'%(blot.objectName(),blot.name))

        split = layout.split()
        col = split.column()
        col.label(text = 'Width :')
        col.label(text = 'Front/Yard :')
        col.label(text = 'Depth :')
        col.label(text = 'Interval :')

        col = split.column()
        col.label(text = 'min/max :')
        row = col.row(align=True)
        row.prop(blot,'minBuildingSize')
        row.prop(blot,'maxBuildingSize')
        row = col.row(align=True)
        row.prop(blot,'minBuildingSideSize')
        row.prop(blot,'maxBuildingSideSize')
        row = col.row(align=True)
        row.prop(blot,'minIntervalSize')
        row.prop(blot,'maxIntervalSize')

        row = layout.row()
        row.label(text = 'Sticked building chances :')
        row.prop(blot,'stickedBuilding')