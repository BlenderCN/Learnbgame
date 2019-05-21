
try:
    from OgreVertexIndexData import *
except ImportError as e:
    directory = os.path.dirname(os.path.realpath(__file__));
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreVertexIndexData.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))



class OgreSubMesh:
    """
    Defines a part of a complete mesh.
        @remarks
            Meshes which make up the definition of a discrete 3D object
            are made up of potentially multiple parts. This is because
            different parts of the mesh may use different materials or
            use different vertex formats, such that a rendering state
            change is required between them.
        @par
            Like the Mesh class, instantiations of 3D objects in the scene
            share the SubMesh instances, and have the option of overriding
            their material differences on a per-object basis if required.
            See the SubEntity class for more information.
    """
    def __init__(self, parent):
        self.parent = parent;
        self.useSharedVertices = True;
        self.indexData = OgreIndexData();
        self.vertexData = parent.sharedVertexData;
        self.materialName = "";
