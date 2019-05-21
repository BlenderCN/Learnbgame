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

import bpy
import os


class PointCloud():
    def __init__(self,fname):
        self.fname=fname
        self.header=[]
        self.data=[]
        self.points=[]
        self.headCols={}
        self.X=None
        self.Y=None
        self.Z=None

    def loadPoints(self,fname=None, delim=','):
        """loadPoints(fname=None)
           This is very dumb at the moment.  It simply reads the
           file from disk assuming its a proper .csv file and stores
           it internally without error checking.

           If fname is None and self.fname is none, returns False
           If fname is set, then assigns new filepath to self.fname
        """

        if fname: self.fname=fname
        if not self.fname: return False

        fid=open(self.fname,'r')
        self.header=[v.strip() for v in fid.readline().split(delim)]

        self.headCols={}
        for col,h in enumerate(self.header):
            self.headCols[h]=col

        self.data=[]
        for line in fid.readlines():
            self.data.append([float(v.strip()) for v in line.split(delim)])

        fid.close()

    def getHeader(self):
        """getHeader()
           Returns the header.  Seems silly to have an accessor method
           in python, but I may add some bells and whistles in the future,
           so I recommend using using this function just in case.
        """
        return header

    def assignPoints(self,X=None,Y=None,Z=None):
        """assignPoints(X=None,Y=None,Z=None)
           Assigns specific columns of the data to be X, Y and Z points
           in the point cloud.

           If no column names are give, then the point array is cleared.
        """

        # Clearning out the array no matter what
        self.points=[]

        # Not the nicest thing to do, but if the function isn't passed a
        # valid header, I silently treat it as a None
        if X not in self.header: X=None
        if Y not in self.header: Y=None
        if Z not in self.header: Z=None

        self.X = X
        self.Y = Y
        self.Z = Z

        # Am I being given everything I need to do something, or do I
        # clear the list of points?
        ndim=3
        if X is None: ndim = ndim-1
        if Y is None: ndim = ndim-1
        if Z is None: ndim = ndim-1

        if ndim == 0:
            return 0

        # Get the header positions
        zeroArray=[0]*len(self.data)
        if X is None: xp=-1
        else: xp=self.header.index(X)
        if Y is None: yp=-1
        else: yp=self.header.index(Y)
        if Z is None: zp=-1
        else: zp=self.header.index(Z)

        xx=[v[xp] if xp>=0 else 0 for v in self.data]
        yy=[v[yp] if yp>=0 else 0 for v in self.data]
        zz=[v[zp] if zp>=0 else 0 for v in self.data]

        self.points=[v for v in zip(xx,yy,zz)]

        return len(self.points)
        


class MeshGenerator():
    def __init__(self,pointCloud):
        self.pointCloud=pointCloud
        self.objectTypes=['cubes','icospheres1','icospheres2']

    def createMesh(self,objName):
        """createMesh()
           For now, assumes a proper set of points has been loaded
           and generates the mesh from the first three columns.
        """

        self.scene = bpy.context.scene
        for object in self.scene.objects:
            object.select = False

        self.mesh=bpy.data.meshes.new(objName)
        self.object = bpy.data.objects.new(objName, self.mesh)
        self.scene.objects.link(self.object)
        self.object.select = True


        if self.scene.objects.active is None or self.scene.objects.active.mode == 'OBJECT':
            self.scene.objects.active = self.object

    def populateMesh(self,type='points',scale=1.0):
        for object in self.scene.objects:
            object.select = False
        self.object.select = True
        self.scene.objects.active = self.object

        if type in self.objectTypes:
            bpy.ops.object.mode_set(mode='EDIT')

            for p in self.pointCloud.points:
                xyz=(p[0],p[1],p[2])
                if type == 'cubes':
                    bpy.ops.mesh.primitive_cube_add(location=xyz,radius=scale)
                elif type == 'icospheres1':
                    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,size=scale,location=xyz)
                elif type == 'icospheres2':
                    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,size=scale,location=xyz)

            bpy.ops.object.mode_set()
            self.mesh.update()

        else:
            self.mesh.from_pydata(self.pointCloud.points, [], [])
            self.mesh.update()

        for h in self.pointCloud.header:
            self.mesh.vertex_colors.new(h)

        numItems=len(self.pointCloud.data)
        for key in self.mesh.vertex_colors.keys():
            numVertsPerItem=int(len(self.mesh.vertex_colors[key].data)/numItems)
            for i in range(numItems):
                n=self.pointCloud.data[i][self.pointCloud.headCols[key]]
                for j in range(numVertsPerItem):
                    data=self.mesh.vertex_colors[key].data[j+i*numVertsPerItem]
                    data.color[0]=n
                    data.color[1]=n
                    data.color[2]=n

    def destroyMesh(self):
        for object in self.scene.objects:
            object.select = False
        self.object.select = True
        self.scene.objects.active = self.object

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set()


def read(directory,filepath,X,Y,Z,T,DELIM,SCALE):
    objName = bpy.path.display_name_from_filepath(filepath)

    pCloud=PointCloud(filepath)
    pCloud.loadPoints(delim=DELIM)
    pCloud.assignPoints(X,Y,Z)

    meshGen=MeshGenerator(pCloud)
    meshGen.createMesh(objName)
    meshGen.populateMesh(type=T,scale=SCALE)
