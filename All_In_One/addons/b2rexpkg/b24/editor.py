
import bpy
import Blender

class OpenSimProperties(object):
    def __init__(self, bobj):
        self._bobj = bobj
    def __setattr__(self, name, value):
        if name == '_bobj':
            object.__setattr__(self, name, value)
        else:
            if not "opensim" in self._bobj.properties:
                self._bobj.properties["opensim"] = {}
            self._bobj.properties["opensim"][name] = value
    def __getattr__(self, name):
        if not "opensim" in self._bobj.properties:
            return ""
        else:
            if name in self._bobj.properties["opensim"]:
                return self._bobj.properties["opensim"][name]
        return ""

def get_opensim_properties(self):
    return OpenSimProperties(self._obj)

class ProxyObject(object):
    def __init__(self, obj, parent=None):
        self._obj = obj
        self._parent = parent
    def __setattr__(self, name, value):
        if name in ['_obj', '_parent'] or name in self.__class__.__dict__:
            object.__setattr__(self, name, value)
        else:
            setattr(self._obj, name, value)
    def __getattr__(self, name):
        return getattr(self._obj, name)
    def __hasattr__(self, name):
        return hasattr(self._obj, name)

class EditorVertex(ProxyObject):
    def get_co(self):
        return self._obj.co
    def set_co(self, values):
        self._obj.co = Blender.Mathutils.Vector(*values)
    co = property(get_co, set_co)

class EditorFace(ProxyObject):
    def get_smooth(self):
        return self._obj.smooth
    def set_smooth(self, value):
        self._obj.smooth = int(value)
    def get_vertices_raw(self):
        pass
    def set_vertices_raw(self, values):
        mesh = self._parent
        indices = map(lambda s: mesh.verts[s], values)
        self._obj.verts = tuple(indices)
        
    use_smooth = property(get_smooth, set_smooth)
    vertices_raw = property(get_vertices_raw, set_vertices_raw)

class FaceList(ProxyObject):
    def __getitem__(self, idx):
        if idx >= len(self._obj):
            self.add(1)
        return EditorFace(self._obj[idx], self._parent)
    def add(self, nfaces):
        verts = self._parent.verts
        for a in xrange(nfaces):
            self._obj.extend([verts[0],verts[1],verts[2]], ignoreDups=False)

class VertexList(FaceList):
    def __getitem__(self, idx):
        return EditorVertex(self._obj[idx])
    def add(self, nfaces):
        for a in xrange(nfaces):
            self._obj.extend(0.0,0.0,0.0)

class EditorMesh(ProxyObject):
    opensim = property(get_opensim_properties)
    def __setattr__(self, name, value):
        if name in ['_obj', '_parent', 'vertices', 'faces']:
            object.__setattr__(self, name, value)
        else:
            setattr(self._obj, name, value)
    def __init__(self, bmesh):
        ProxyObject.__init__(self, bmesh)
        self.vertices = VertexList(bmesh.verts, bmesh)
        self.faces = FaceList(bmesh.faces, bmesh)
    def calc_normals(self):
        self._obj.calcNormals()

class EditorObject(ProxyObject):
    def __init__(self, bobj):
        ProxyObject.__init__(self, bobj)
        self.data = EditorMesh(bobj.getData(0, True))
    def __setattr__(self, name, value):
        if name in ['_obj', '_parent', 'data'] or name in self.__class__.__dict__:
            object.__setattr__(self, name, value)
        else:
            setattr(self._obj, name, value)
    def link(self, data):
        if isinstance(data, EditorMesh):
            self._obj.link(data._obj)
        else:
            self._obj.link(data)
    def set_location(self, value):
        self._obj.setLocation(*value)
    def get_location(self):
        return self._obj.getLocation()
    def set_scale(self, value):
        self._obj.setSize(*value)
    def get_scale(self):
        return self._obj.getSize()

    def set_parent(self, value):
        if not value:
            self._obj.clrParent()
        else:
            value.makeParent([self._obj])
    def get_parent(self):
        return self._obj.getParent()
    def get_unimplemented(self):
        pass
    def set_unimplemented(self, value):
        pass
    opensim = property(get_opensim_properties)
    parent = property(get_parent, set_parent)
    location = property(get_location, set_location)
    scale = property(get_scale, set_scale)
    draw_type = property(get_unimplemented, set_unimplemented)
    lock_location = property(get_unimplemented, set_unimplemented)
    lock_scale = property(get_unimplemented, set_unimplemented)
    lock_rotation = property(get_unimplemented, set_unimplemented)
    lock_rotations_4d = property(get_unimplemented, set_unimplemented)
    lock_rotation_w = property(get_unimplemented, set_unimplemented)

class EditorMeshes(ProxyObject):
    def __init__(self):
        ProxyObject.__init__(self, bpy.data.meshes)

    def new(self, name):
        return EditorMesh(bpy.data.meshes.new(name))

    def __getitem__(self, name):
        return EditorMesh(bpy.data.meshes[name])


class EditorObjects(ProxyObject):
    def __init__(self):
        ProxyObject.__init__(self, bpy.data.objects)

    def new(self, name, mesh_data):
        obj = Blender.Object.New("Mesh", name)
        if isinstance(mesh_data, EditorMesh):
            obj.link(mesh_data._obj)
        else:
            obj.link(mesh_data)
        return EditorObject(obj)

    def __getitem__(self, name):
        return EditorObject(bpy.data.objects[name])

class EditorData(object):
    def __init__(self):
        self.meshes = EditorMeshes()
        self.textures = bpy.data.textures
        self.objects = EditorObjects()
        self.materials = bpy.data.materials


data = EditorData()

def getSelected():
    return map(lambda s: EditorObject(s), Blender.Object.GetSelected())

def get_loading_state(obj):
    if "opensim" in obj.properties and "state" in obj.properties["opensim"]:
        return obj.properties["opensim"]["state"]
    else:
        return 'LOADING'

def set_loading_state(obj, value):
    """
    Set the loading state for the given blender object.
    """
    if not "opensim" in obj.properties:
        obj.properties["opensim"] = {}
    obj.properties["opensim"]["state"] = value

def getVersion():
    return "Blender "+str(Blender.Get('version'))


