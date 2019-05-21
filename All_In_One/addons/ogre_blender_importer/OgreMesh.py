try:
    from OgreSubMesh import OgreSubMesh

except ImportError as e:
    directory = os.path.dirname(os.path.realpath(__file__));    
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreSubMesh.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))


class OgreMesh:
    """
    Resource holding data about 3D mesh.
    @remarks
        This class holds the data used to represent a discrete
        3-dimensional object. Mesh data usually contains more
        than just vertices and triangle information; it also
        includes references to materials (and the faces which use them),
        level-of-detail reduction information, convex hull definition,
        skeleton/bones information, keyframe animation etc.
        However, it is important to note the emphasis on the word
        'discrete' here. This class does not cover the large-scale
        sprawling geometry found in level / landscape data.
    @par
        Multiple world objects can (indeed should) be created from a
        single mesh object - see the Entity class for more info.
        The mesh object will have it's own default
        material properties, but potentially each world instance may
        wish to customise the materials from the original. When the object
        is instantiated into a scene node, the mesh material properties
        will be taken by default but may be changed. These properties
        are actually held at the SubMesh level since a single mesh may
        have parts with different materials.
    @par
        As described above, because the mesh may have sections of differing
        material properties, a mesh is inherently a compound construct,
        consisting of one or more SubMesh objects.
        However, it strongly 'owns' it's SubMeshes such that they
        are loaded / unloaded at the same time. This is contrary to
        the approach taken to hierarchically related (but loosely owned)
        scene nodes, where data is loaded / unloaded separately. Note
        also that mesh sub-sections (when used in an instantiated object)
        share the same scene node as the parent.
    """
    def __init__(self,name):
        self._subMeshList = [];
        self._blender_mesh = bpy.data.meshes.new(name);
        self.skeletonName = "";
        self.blender_object = None;


    @property
    def name(self):
        return self.blender_mesh.name;

    @property
    def blender_mesh(self):
        return self._blender_mesh;

    def createSubMesh(self, name=None):
        sub = OgreSubMesh(self);
        self._subMeshList.append(sub);

        if name is not None:
            raise NotImplementedError;

        return sub;
