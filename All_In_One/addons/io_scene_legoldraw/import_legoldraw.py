# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Script copyright (C) Li Jun (AKA oyster @blenderartists.org, @blendercn.org)
# Contributors: Li Jun



"""
This script imports LDraw DAT File format files to Blender. LDraw is an open
standard for LEGO CAD programs, which can be found on http://www.ldraw.org/

Usage:
Execute this script from the "File->Import" menu and choose a DAT file to
open.

Notes:
Although duplicated verts are removed in this script twice, sometimes you have
to remove the duplicated manually, and I don't know why. And maybe you have to
re-calculate the normals manually even this script has done this process, and I
don't know the reason too.
"""

import os, sys, time
path=os.path.realpath(__file__)
if path not in sys.path:
    sys.path.append(path)

import math
import mathutils

#I use this to debug. If debug is True, the output will be displayed
#on the Console Window
#Is there any tool to debug an addon, which can step in/out/over functons,
#monitor variables
##debug=True
debug=False

try:
    import bpy
except:
    debug=True

try:
    import legocolor
except:
    from . import legocolor

#global useMathutils
global legodatpath, scriptpath
legodatpath=[]

scriptpath=os.path.split(os.path.realpath(__file__))[0]
for i in open('%s/lego.cfg' %(scriptpath)).readlines():
    i=i.strip()
    if i and (i not in legodatpath):
        legodatpath.append(i)

# ==================================
# ==== Vector math              ====
# ==================================
def mat_vec(mat,vec, use_Mathutils):
    '''
    IN:
        mat     matrix
        vec     vector
    OUT:
        matrix * vector
    '''

    if use_Mathutils:
        mat=mathutils.Matrix([mat[:3],mat[3:6],mat[6:]])
        vec=mathutils.Vector(vec)
        return (mat*vec).to_tuple()
    else:
        return (mat[0]*vec[0]+mat[1]*vec[1]+mat[2]*vec[2],
                mat[3]*vec[0]+mat[4]*vec[1]+mat[5]*vec[2],
                mat[6]*vec[0]+mat[7]*vec[1]+mat[8]*vec[2]
               )

def vec_vec(vec1,vec2, use_Mathutils):
    '''addition operation for 2 vectors'''

    if use_Mathutils:
        return (mathutils.Vector(vec1)+mathutils.Vector(vec2)).to_tuple()
    else:
        return (vec1[0]+vec2[0],vec1[1]+vec2[1],vec1[2]+vec2[2])

# ==================================
# ==== Read                     ====
# ==================================
def _readMesh(filename, use_Mathutils):
    '''
    return vlist, flist
    where
    vlist [(x1, y1, z1), (x2, y2, z2), ...]
    flist [(p1 index, p2 index, p3 index, color), (p1 index, p2 index, p3 index, p4 index, color), ...]
    '''
    global legodatpath
    vlist,flist=[],[]

##    print ('in _readMesh')
##    print(filename)
##    print (legodatpath)

    #we have to search the DAT file under all possible directories
    #we have to add the directory where the reference DAT stays in
    tmp=os.path.split(os.path.realpath(filename))[0]
    if tmp not in legodatpath:
        legodatpath.append(tmp)

    foundDatFile=False
    allPossibleFilename=[filename]+list(map(lambda e:e+os.path.sep+filename,legodatpath))
    #print 'filename= ',filename
    for filename in allPossibleFilename:
        if os.path.isfile(filename):
            foundDatFile=True
            break

    if not foundDatFile:
        return [], []

##    print('filename=%s' % filename)
    fileIn=open(filename)


    #I don't konw how to add progressbar
##    lineNum=len(fileIn.readlines())
##    bpy.context.window_manager.progress_begin(0, lineNum + 1)
##    bpy.context.window_manager.progress_update(0)

    fileIn.seek(0)
    for line in fileIn.readlines():
        line=line.strip()
        if not line:    #skip the null line
            continue

        line=line.split()

##        print('line=%s' % line)
##        print(line[0], type(line[0]))

        if line[0]=='0': #a comment or a META command
            #print 'line type 0'
            pass
        elif line[0]=='1':
            #~ print ('line type 1')
            #~ print('line=', line)
            #a file reference. The generic format is:
            #1 <color> x y z a b c d e g f h i <file>

            #~ color=realcolor(line[1])
            color=line[1]

            line1=map(float, line[2:-1])

            x,y,z,a,b,c,d,e,f,g,h,i = line1

            #read vertexices and face LIST from reference DAT file
            #this maybe call _readMesh recursively
            vexList,faceList=_readMesh(line[-1], use_Mathutils)
##            print('vexList', list(vexList), 'type(vexList)', type(vexList))
##            print ('faceList= ',faceList)
##            print ('(a,b,c,d,e,f,g,h,i)= ', (a,b,c,d,e,f,g,h,i))
##            print ('(x,y,z)= ',(x,y,z))


            vexList=list(map(lambda ee:mat_vec((a,b,c,d,e,f,g,h,i),ee, use_Mathutils),vexList))
##            print('vexList', list(vexList))

            vexList=list(map(lambda e:vec_vec((x,y,z),e, use_Mathutils),vexList))
##            print('vexList', list(vexList))


            #re-assign the vertex index in every face
            oldVerIndx=0
            for oneVex in vexList:
                if oneVex not in vlist:
                    vlist.append(oneVex)
                newVerIndx=vlist.index(oneVex)
                #print ('newVerIndx= ',newVerIndx)

                #we have to use "- newVerIndx", else it will be replaced in the
                #subsequent re-assignment.
                #and we must change the face color to the current one, in other
                #word, drop the original color in refernce DAT file
                faceList=[
                    list(
                        map(
                            lambda e: - newVerIndx if e==oldVerIndx else e,
                            _[:-1]
                            )
                        )+[color]
                    for _ in faceList
                    ]

                oldVerIndx+=1
##            print('faceList=', faceList)

            #now we fix the vertex
            faceList=[
                        list(map(abs,_[:-1])) + [_[-1]]
                        for _ in faceList
                    ]
            #print 'face= ',face
##            print('faceList=', faceList)

            #do we need to omit duplicated face?
            #will this produce "hole" on the model surface?
            for _ in faceList:
                if _ not in flist:
                    flist.append(_)

            #print 'vlist= ',vlist
            #print 'flist= ',flist

        elif line[0]=='2':
            #print 'line type 2'
            #a line drawn between two points.
            #2 <color> x1 y1 z1 x2 y2 z2
            #~ color=realcolor(line[1])
            color=line[1]
            line1=map(float, line[2:])

            f1, f2, f3, f4, f5, f6= line1

            if (f1, f2, f3) not in vlist:
                vlist.append((f1, f2, f3))
            if (f4, f5, f6) not in vlist:
                vlist.append((f4, f5, f6))
            flist.append(
                (vlist.index((f1, f2, f3)),vlist.index((f4, f5, f6)),color)
                        )
            '''
            print 'vlist= ',vlist
            print 'flist= ',flist
            '''

        elif line[0]=='3':
##            print ('line type 3')
            #a filled triangle drawn between three points.
            #3 <color> x1 y1 z1 x2 y2 z2 x3 y3 z3
            #~ color=realcolor(line[1])
            color=line[1]

            [x1, y1, z1, x2, y2, z2, x3, y3, z3]=[float(i) for i in line[2:]]

            [f1, f2, f3, f4, f5, f6, f7, f8, f9] = \
                [x1, y1, z1, x2, y2, z2, x3, y3, z3]
            if (f1, f2, f3) not in vlist:
                vlist.append((f1, f2, f3))
            if (f4, f5, f6) not in vlist:
                vlist.append((f4, f5, f6))
            if (f7, f8, f9) not in vlist:
                vlist.append((f7, f8, f9))

            flist.append(
                (
                    vlist.index((f1, f2, f3)),vlist.index((f4, f5, f6)),
                    vlist.index((f7, f8, f9)),color
                )
                )

        elif line[0]=='4':
##            print ('line type 4')
            #a filled quadrilateral drawn between four points.
            #4 <color> x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4
            #~ color=realcolor(line[1])
            color=line[1]
            [x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4]=\
                [float(i) for i in line[2:]]
            f1, f2, f3, f4, f5, f6, f7, f8, f9, fa, fb, fc = \
                [x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4]
            if (f1, f2, f3) not in vlist:
                vlist.append((f1, f2, f3))
            if (f4, f5, f6) not in vlist:
                vlist.append((f4, f5, f6))
            if (f7, f8, f9) not in vlist:
                vlist.append((f7, f8, f9))
            if (fa, fb, fc) not in vlist:
                vlist.append((fa, fb, fc))

            flist.append(
                (
                    vlist.index((f1, f2, f3)),vlist.index((f4, f5, f6)),
                    vlist.index((f7, f8, f9)),vlist.index((fa, fb, fc)),color
                )
                )

        elif line[0]=='5':
            #print 'line type 5'
            #a filled conditional or optional line.
            #5 <color> x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4
            pass

##        bpy.context.window_manager.progress_update(1)

    fileIn.close()


    return vlist,flist



def readMesh(filename, objName, use_Mathutils):
    if not debug:
        mesh = bpy.data.meshes.new(objName)

##    print('in readMesh')
    vlist,faces=_readMesh(filename, use_Mathutils)
##    print (vlist)
##    print (faces)
##    print ('*'*10)

    # Generate verts and faces lists, without duplicates
    verts = []
    coords = {}
    index_tot = 0
    faces_indices = []

    index_face=0
    polygons_index_mat={}
    for f_color in faces:
        faceVerteciesIndex=f_color[:-1]
        f=[vlist[i] for i in faceVerteciesIndex]
##        print('f', f)
        color=f_color[-1]
        #~ print('color=', color, legocolor.legocolor2rgba(color))

        if not debug:
            matNew = bpy.data.materials.get(legocolor.legocolor2name(color))
            if matNew == None:
                matNew = bpy.data.materials.new(legocolor.legocolor2name(color))

            r,g,b,a=legocolor.legocolor2rgba(color)
            matNew.diffuse_color =(r,g,b)
            if a!=1.0:
                matNew.use_transparency = True
                matNew.alpha=a
            matNew.diffuse_intensity = 1.0
            matNew.emit = 2.0
            if mesh.materials.find(legocolor.legocolor2name(color)) == -1:
                mesh.materials.append(matNew)
            else:
                pass

        fi = []
        for i, v in enumerate(f):
            index = coords.get(v)

            if index is None:
                index = coords[v] = index_tot
                index_tot += 1
                verts.append(v)

            fi.append(index)

        faces_indices.append(fi)

        if not debug:
            polygons_index_mat[index_face]=mesh.materials.find(
                legocolor.legocolor2name(color)
                )
        index_face+=1
##    print('verts=',verts,faces_indices)

    if not debug:
        mesh.from_pydata(verts, [], faces_indices)

        for i in range(len(mesh.polygons)):
            try:
                mesh.polygons[i].material_index=polygons_index_mat[i]
            except:
                pass


        return mesh


def addMeshObj(mesh, objName):
    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False

    mesh.update()
    mesh.validate()

    nobj = bpy.data.objects.new(objName, mesh)
    scn.objects.link(nobj)
    nobj.select = True

    if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
        scn.objects.active = nobj



def read(filepath, scale, use_Mathutils, removeDoubles, use_Editmode):
    print('Start to load %s' % filepath)
    st=time.time()
    scn = bpy.context.scene

    #convert the filename to an object name
    objName = bpy.path.display_name_from_filepath(filepath)
    mesh = readMesh(filepath, objName, use_Mathutils)
    addMeshObj(mesh, objName)

    bpy.ops.object.mode_set(mode='EDIT')

##    bpy.ops.mesh.flip_normals()
##    mesh.calc_normals()
    #so strange, after normals_make_consistent, ctrl+n still can get a
    #different result
    bpy.ops.mesh.normals_make_consistent()
    mesh.update()
    mesh.validate()

    if removeDoubles:
        #bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.select_all(action = 'SELECT')
        print('Remove doubles for the 1st time')
        bpy.ops.mesh.remove_doubles()
        mesh.update()
        mesh.validate()

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        #so strange, for the official ldraw\models\car.dat, there is still doubles
        #remained after 2 remove_doubles
        print('Remove doubles for the 2nd time')
        bpy.ops.mesh.remove_doubles()
        mesh.update()
        mesh.validate()

    #to match the coordinates between LDraw and Blender
    bpy.ops.transform.rotate(value=-math.pi/2, axis=(1, 0, 0))

    bpy.ops.transform.resize(value=(scale, scale, scale))

    #~ print('useEditmode=', use_Editmode)
    bpy.ops.object.mode_set(mode=use_Editmode)

    mesh.update()
    mesh.validate()
    scn.update()

    et=time.time()
    print('Import %s in %.3f seconds' %(filepath, et-st))


if __name__=='__main__':
    filename=r'e:\my_project\blender\io\lego\testType1.dat'
##    filename=r'e:\greensoft\3d\lego\ldraw\models\pyramid.dat'
    readMesh(filename, '')
