
from io import IOBase
from io import SEEK_SET
import sys
import os

def printMeshSerializerUsage():
    print("usage: blender --python OgreMeshSerializer.py -- file.mesh");

try:
    import bpy;
    import mathutils;
except ImportError:
    print("You need to execute this script using blender");
    printMeshSerializerUsage();

try:
    from OgreMeshSerializerImpl import *
    from OgreSerializer import OgreSerializer
    from OgreMeshVersion import OgreMeshVersion
    from OgreMesh import OgreMesh

except ImportError as e:
    directory = os.path.dirname(os.path.realpath(__file__));
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreMeshSerializerImpl.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))
    srcfile="OgreSerializer.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))
    srcfile="OgreMeshVersion.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))
    srcfile="OgreMesh.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))

class OgreMeshSerializer(OgreSerializer):
    """
    Class for serialising mesh data to/from an OGRE .mesh file.
    @remarks
        This class allows exporters to write OGRE .mesh files easily, and allows the
        OGRE engine to import .mesh files into instantiated OGRE Meshes.
        Note that a .mesh file can include not only the Mesh, but also definitions of
        any Materials it uses (although this is optional, the .mesh can rely on the
        Material being loaded from another source, especially useful if you want to
        take advantage of OGRE's advanced Material properties which may not be available
        in your modeller).
    @par
        To export a Mesh:<OL>
        <LI>Use the MaterialManager methods to create any dependent Material objects, if you want
            to export them with the Mesh.</LI>
        <LI>Create a Mesh object and populate it using it's methods.</LI>
        <LI>Call the exportMesh method</LI>
        </OL>
    @par
        It's important to realise that this exporter uses OGRE terminology. In this context,
        'Mesh' means a top-level mesh structure which can actually contain many SubMeshes, each
        of which has only one Material. Modelling packages may refer to these differently, for
        example in Milkshape, it says 'Model' instead of 'Mesh' and 'Mesh' instead of 'SubMesh',
        but the theory is the same.
    """

    HEADER_CHUNK_ID = 0x1000;

    class _MeshVersionData:
        def __init__(self, _ver, _string, _impl):
            self.version=_ver;
            self.versionString=_string;
            self.impl=_impl;

    def __init__(self):
        OgreSerializer.__init__(self);
        self.listener=None;
        self._versionData = [];
        self._versionData.append(OgreMeshSerializer._MeshVersionData(OgreMeshVersion.MESH_VERSION_1_10, "[MeshSerializer_v1.100]",OgreMeshSerializerImpl()));
        self._versionData.append(OgreMeshSerializer._MeshVersionData(OgreMeshVersion.MESH_VERSION_1_8, "[MeshSerializer_v1.8]",OgreMeshSerializerImpl_v1_8()));
        
        
    def importMesh(self, stream, filename=None):
        assert(issubclass(type(stream),IOBase));

        #Check mesh name validity
        if (filename is None):
            if (hasattr(stream,'name')):
                filename = stream.name;
            elif (hasattr(stream, 'filename')):
                filename = stream.filename;
            else:
                raise ValueError("Cannot determine the filename of the stream please add filename parameter")

        filename = os.path.basename(filename);
        mesh_name = os.path.splitext(filename)[0];
        if mesh_name in bpy.data.meshes.keys():
            raise ValueError("Mesh with name " + mesh_name + " already exists in blender");

        #Check header and select impl
        self._determineEndianness(stream);
        headerID = self._readUShorts(stream,1)[0];
        if (headerID != OgreMeshSerializer.HEADER_CHUNK_ID):
            raise ValueError("File header not found");
        ver = OgreSerializer.readString(stream);
        stream.seek(0,SEEK_SET);
        impl = None;
        for i in self._versionData:
            if (i.versionString == ver):
                impl = i.impl;
                break;
        if (impl is None):
            print(ver);
            raise ValueError("Cannot find serializer implementation for "
                             "mesh version " + ver);

        #Create the blender mesh and import the mesh
        mesh = OgreMesh(mesh_name);
        impl.importMesh(stream,mesh,self.listener);

        #Check if newer version
        if (ver != self._versionData[0].versionString):
            print("Warning: "
                  " older format (" + ver + "); you should upgrade it as soon as possible" +
                  " using the OgreMeshUpgrade tool.");

        #Probably useless
        if (self.listener is not None):
            listener.processMeshCompleted(mesh);

    def enableValidation(self):
        OgreSerializer.enableValidation(self);
        for i in self._versionData:
            i.impl.enableValidation();


    def disableValidation(self):
        OgreSerializer.disableValidation(self);
        for i in self._versionData:
            i.impl.disableValidation();

if __name__ == "__main__":
    argv = sys.argv;
    try:
        argv = argv[argv.index("--")+1:];  # get all args after "--"
    except:
        printMeshSerializerUsage();
        sys.exit();

    if (len(argv) > 0):
        filename = argv[0];
        meshfile = open(filename,mode='rb');
        meshserializer = OgreMeshSerializer();
        meshserializer.disableValidation();
        meshserializer.importMesh(meshfile);
    else:
        printMeshSerializerUsage();
