import bpy
import os
from bpy_extras.io_utils import ImportHelper, ExportHelper
from shutil import copyfile
from . import msh

import numpy as np
from . import msh
import gzip
import struct
import shutil

from functools import partial
import multiprocessing

import argparse

C = bpy.context
D = bpy.data




class import_mesh_sequence_fds(bpy.types.Operator, ImportHelper):
    bl_idname = "iscd.import_mesh_sequence_fds"
    bl_label  = "Import results from a fds simulation"
    bl_options = {"REGISTER", "UNDO"}

    test_items = [
        ("both", "both", "both"),
        ("flame", "flame", "flame"),
        ("soot", "soot", "soot")
    ]
    simutype = bpy.props.EnumProperty(items=test_items)
    start  = bpy.props.IntProperty( name="startFrame", description="starting frame", default=0, min=0, max=5000)
    end    = bpy.props.IntProperty( name="endFrame",   description="ending   frame", default=10, min=1, max=5001)

    filter_glob = bpy.props.StringProperty(
        default="*.smv",
        options={'HIDDEN'},
    )

    def execute(self, context):



        #Functions (here for the import vtk part...)
        import vtk
        def getGridFromSMV(path):
            with open(path) as f:
                lines = [l.strip() for l in f.readlines()]
                lines = [l for l in lines if l!=""]
            #Get the begin
            begin = [0,0,0]
            for i,l in enumerate(lines):
                for j,kwd in enumerate(["TRNX", "TRNY", "TRNZ"]):
                    if kwd in l:
                        begin[j] = i+2
            #Write the X, Y and Z coords
            currentInd = 0
            X, Y, Z = [], [], []
            for i,l in enumerate(lines):
                if i>=begin[currentInd]:
                    try:
                        if currentInd==0:
                            X.append(float(l.split()[1]))
                        if currentInd==1:
                            Y.append(float(l.split()[1]))
                        if currentInd==2:
                            Z.append(float(l.split()[1]))
                    except:
                        if currentInd == 2:
                            break
                        else:
                            currentInd+=1
            print(len(X), len(Y), len(Z))
            return X,Y,Z
        def createVTKGridFromCoordinates(_x, _y, _z):
            xCoords = vtk.vtkFloatArray()
            for i in _x:
                xCoords.InsertNextValue(i)
            yCoords = vtk.vtkFloatArray()
            for i in _y:
                yCoords.InsertNextValue(i)
            zCoords = vtk.vtkFloatArray()
            for i in _z:
                zCoords.InsertNextValue(i)
            rgrid = vtk.vtkRectilinearGrid()
            rgrid.SetDimensions(len(_x), len(_y), len(_z))
            rgrid.SetXCoordinates(xCoords)
            rgrid.SetYCoordinates(yCoords)
            rgrid.SetZCoordinates(zCoords)
            return rgrid
        def getOutputFilesFromSMV(path):
            with open(path) as f:
                files = []
                lines = [l.strip() for l in f.readlines()]
                lines = [l for l in lines if l!=""]
                for i in range(len(lines)):
                    if lines[i].split()[0]=="SMOKF3D":
                        files.append([lines[i+2].split()[0], lines[i+1].strip()])
                    if lines[i].split()[0]=="SLCF":
                        files.append([lines[i+2].strip(), lines[i+1].strip()])
                return files
        def toInt(byte):
            return int.from_bytes([byte], byteorder='big');#int(byte.encode('hex'), 16)
        def readS3D(s3dfile, frames, start=0, end=None):
            if end is None:
                end = len(frames)

            VALUES = []
            with open(s3dfile, "rb") as f:
                #First offset
                X = 36
                f.seek(X,1)

                #Skipping until the start
                for frame in frames[:start]:
                    f.seek(72-X, 1)
                    f.seek(int(frame[2]), 1)

                #Reading from start to end
                if start!=0 or end!=len(frames):
                    print("Reading the frames " + str(start) + " to " + str(end))
                for ind, frame in enumerate(frames[start:end]):
                    f.seek(72-X, 1)
                    bits  = f.read(int(frame[2]))
                    vals  = []
                    i     = 0
                    while(i<len(bits)):
                        if toInt(bits[i]) == 255:
                            val = toInt(bits[i+1])
                            n   = toInt(bits[i+2])
                            for j in range(n):
                                vals.append(val)
                            i+=3
                        else:
                            val = toInt(bits[i])
                            vals.append(val)
                            i+=1
                    VALUES.append(vals)
            return VALUES
        def writeVTKArray(arr, header, f):
            f.write(header)
            for i in range(len(arr)/6 + 1):
                for j in range(6):
                    if 6*i + j < len(arr):
                        f.write(str(arr[6*i + j]) + " ")
                f.write("\n")
        def exportVTK(filepath, name, x,y,z,values):
            with open(filepath, "w") as f:
                f.write("# vtk DataFile Version 2.0\nSample rectilinear grid\nASCII\nDATASET RECTILINEAR_GRID\n")
                f.write("DIMENSIONS " + " ".join([str(len(_tmp)) for _tmp in [x,y,z]]) + "\n")
                writeVTKArray(x, "X_COORDINATES " + str(len(x)) + " float\n", f)
                writeVTKArray(y, "Y_COORDINATES " + str(len(y)) + " float\n", f)
                writeVTKArray(z, "Z_COORDINATES " + str(len(z)) + " float\n", f)
                writeVTKArray(values, "POINT_DATA " + str(len(values)) + "\nSCALARS " + name + " float\nLOOKUP_TABLE default\n", f)
        def doSomething(rgrid, value, outFile, isoValue):
            # Fill the value array
            signedDistances = vtk.vtkFloatArray()
            signedDistances.SetNumberOfComponents(1)
            signedDistances.SetName("SignedDistances")
            for v in value:
                signedDistances.InsertNextValue(v)

            # Add the value array to the grid
            rgrid.GetPointData().SetScalars(signedDistances)

            # Extract the isosurface
            iso = vtk.vtkContourFilter()
            iso.SetInputData(rgrid)
            iso.SetNumberOfContours(1)
            iso.SetValue(0,isoValue)
            iso.Update()

            #Get verts and triangles
            polydata = iso.GetOutput()
            verts     = np.array([ [polydata.GetPoint(i)[j] if j<3 else 0 for j in range(4)] for i in range(polydata.GetNumberOfPoints()) ])
            tris      = np.array([ [polydata.GetCell(i).GetPointIds().GetId(j) if j<3 else 0 for j in range(4)] for i in range(polydata.GetNumberOfCells()) ])

            #Write a .bobj file
            with gzip.open(outFile, "wb") as f:
                string = struct.pack("i", len(verts))
                f.write(string)
                for v in verts:
                    string=struct.pack("fff", v[0], v[1], v[2])
                    f.write(string)
                string = struct.pack("i", len(verts))
                f.write(string)
                for n in verts:
                    string=struct.pack("fff", n[0], n[1], n[2])
                    f.write(string)
                string = struct.pack("i", len(tris))
                f.write(string)
                for t in tris:
                    string=struct.pack("iii", t[0], t[1], t[2])
                    f.write(string)




        self.directory = os.path.dirname(self.properties.filepath)

        print(self.start, self.end, self.directory)

        # 0 - Argument parsing
        case = (self.properties.filepath.split("/")[-1])[:-4]

        # 1 - Get the grid info
        _x,_y,_z = getGridFromSMV(os.path.join(self.directory, case + ".smv"))
        rgrid    = createVTKGridFromCoordinates(_x, _y, _z)

        # 2 - Get the output data files (.s3d and .sf)
        files = getOutputFilesFromSMV(os.path.join(self.directory, case + ".smv"))

        # 3 - Loop on the data files
        for f in files:
            #Read the .s3d files
            if f[1][-4:] == ".s3d":
                with open( os.path.join(self.directory, f[1] + ".sz") ) as fsz:
                    frames = np.array([[float(x) for x in l.split()] for l in fsz.readlines()[1:]])

                values = readS3D( os.path.join(self.directory,f[1]) , frames , self.start, self.end)

                path = ""
                if (self.simutype == "flame" or self.simutype=="both") and f[0]=="HRRPUV":
                    path = os.path.join(self.directory, "flame")
                elif (self.simutype == "soot" or self.simutype=="both") and f[0]=="SOOT":
                    path = os.path.join(self.directory, "smoke")
                ind = 0
                path += str(ind).zfill(3)
                while os.path.exists(path):
                    ind+=1
                    path = path[:-3] + str(ind).zfill(3)
                os.mkdir(path)

                #Don't write to vtk!!!
                def runThread(X):
                    i    = X[0]
                    v    = X[1]
                    path = X[2]
                    print(f[0] + ": step " + str(i))
                    final   = os.path.join(path , "fluidsurface_final_"   + str(self.start + i).zfill(4) + ".bobj.gz")
                    iso = 100 if f[0]=="SOOT" else 40
                    doSomething(rgrid, v, final, isoValue=iso)
                for i,v in enumerate(values):
                    runThread([i,v,path])

                # 4 - Create the blender smulation object
                def add_simulation(path_to_bobj):
                    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.delete(type='VERT')
                    bpy.ops.object.editmode_toggle()
                    bpy.context.active_object.name = path_to_bobj.split("/")[-1]
                    bpy.ops.object.modifier_add(type='FLUID_SIMULATION')
                    bpy.context.object.modifiers["Fluidsim"].settings.type = 'DOMAIN'
                    bpy.context.object.modifiers["Fluidsim"].settings.viewport_display_mode = 'FINAL'
                    bpy.context.object.modifiers["Fluidsim"].settings.filepath = path_to_bobj
                add_simulation(path)

                """Parallel implementation
                pool      = multiprocessing.Pool(15)
                SETTINGS = []
                for i,v in enumerate(values):
                settings = {
                    "index": i,
                    "value": v,
                    "path":  path,

                }
                pool.map(runThread, [[i,v,path] for i,v in enumerate(values)])
                """

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(import_mesh_sequence_fds)

def unregister() :
    bpy.utils.unregister_class(import_mesh_sequence_fds)
