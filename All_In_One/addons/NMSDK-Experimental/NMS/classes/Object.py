# Primary Object class.
# Each object in blender will be passed into this class. Any children are added
# as child objects.

from .TkSceneNodeData import TkSceneNodeData
from .TkSceneNodeAttributeData import TkSceneNodeAttributeData
from .TkTransformData import TkTransformData
from .TkMaterialData import TkMaterialData
from .TkPhysicsComponentData import TkPhysicsComponentData
from .List import List
from collections import OrderedDict as odict

TYPES = ['MESH', 'LOCATOR', 'COLLISION', 'MODEL', 'REFERENCE']


class Object():
    """ Structure:
    TkSceneNodeData:
        Name
        Type
        Transform (TkTransformData)
        Attributes (List of TkSceneNodeAttributeData). The specific values in
        this will depend on the Type.
        Children (List of TkSceneNodeData)
    end
    """

    def __init__(self, Name, **kwargs):
        # This will be given as a TkTransformData object.
        # If this isn't specified the default value will be used.
        self.Transform = kwargs.get('Transform', TkTransformData())

        # default to None so that it is handled properly if there are none.
        self.Attributes = None

        # just a normal list so it is easier to iterate over
        self.Children = []
        # set to None by default. Every child will have this set to something
        # when it is added as a child.
        self.Parent = None

        # whether or not something is a mesh. This will be modified when the
        # object is created if required.
        self.IsMesh = False

        self.NodeData = None

        # even though these are defined for all Object's, they will only be
        # populated for the Model
        # TODO: make this wayyyy nicer
        # this is a list of all the MESH objects or collisions of type MESH so
        # that we can easily access it.
        self.Meshes = odict()
        # The list will be automatically populated when a child is added to any
        # children of this object.
        self.ListOfEntities = []    # this works similarly to the above...

        self.Name = Name.upper()
        self._Type = ""

        self.ExtraEntityData = kwargs.get('ExtraEntityData', dict())

        if type(self.ExtraEntityData) == str:
            self.EntityData = None
            # this will be the path or name of the file. If just name it will
            # need to be processed later...
            self.EntityPath = self.ExtraEntityData
        else:
            try:
                self.EntityData = dict()
                # there should be only one key...
                entityname = list(self.ExtraEntityData.keys())[0]
                self.EntityPath = entityname
                # this can be populated with any extra stuff that needs to go
                # into the entity.
                self.EntityData[entityname] = List()
                for entity in self.ExtraEntityData[entityname]:
                    self.EntityData[entityname].append(entity)
            except IndexError:
                # in this case we are being passed an empty dictionary.
                # set the entity data to be None
                self.EntityData = None
                self.EntityPath = ''

        # list of provided data streams (only applicable to Mesh type Objects)
        self.provided_streams = set()

    def give_parent(self, parent):
        self.Parent = parent

    def populate_meshlist(self, obj):
        # take the obj and pass it all the way up to the Model object and add
        # the object to it's list of meshes
        if self.Parent is not None:
            # in this case we are a child of something, so pass the object up
            # an order...
            self.Parent.populate_meshlist(obj)
        else:
            # ... until we hit the Model object who is the only object that has
            # no parent.
            self.Meshes[obj.Name] = obj

    def populate_entitylist(self, obj):
        if self.Parent is not None:
            self.Parent.populate_entitylist(obj)
        else:
            self.ListOfEntities.append(obj)

    def add_child(self, child):
        self.Children.append(child)
        child.give_parent(self)     # give the child it's parent
        if child.IsMesh:
            print('{0} is a mesh'.format(self.Name))
            # if the child has mesh data, we want to pass the reference of the
            # object up to the Model object
            self.populate_meshlist(child)
        if child._Type == 'LOCATOR' or child._Type == 'MESH':
            self.populate_entitylist(child)

    def determine_included_streams(self):
        # this will search through the different possible streams and determine
        # which have been provided.
        # we will not include CHVerts as this will be given by default anyway
        # and we don't need to a semantic ID for it
        for name in ['Vertices', 'Indexes', 'UVs', 'Normals', 'Tangents']:
            if self.__dict__.get(name, None) is not None:
                self.provided_streams = self.provided_streams.union(
                    set([name]))

    def get_data(self):
        # returns the NodeData attribute
        return self.NodeData

    def construct_data(self):
        # iterate through all the children and create a TkSceneNode for every
        # child with the appropriate properties.

        # call each child's process function
        if len(self.Children) != 0:
            self.Child_Nodes = List()
            for child in self.Children:
                child.construct_data()
                # this will return the self.NodeData object in the child Object
                self.Child_Nodes.append(child.get_data())
        else:
            self.Child_Nodes = None

        self.NodeData = TkSceneNodeData(Name=self.Name,
                                        Type=self._Type,
                                        Transform=self.Transform,
                                        Attributes=self.Attributes,
                                        Children=self.Child_Nodes)

    def rebuild_entity(self):
        # this is used to rebuild the entity data in case something else is
        # added after the object is created
        if type(self.ExtraEntityData) == str:
            self.EntityData = self.ExtraEntityData
        else:
            self.EntityData = dict()
            # there should be only one key...
            entityname = list(self.ExtraEntityData.keys())[0]
            # this can be populated with any extra stuff that needs to go into
            # the entity.
            self.EntityData[entityname] = List(TkPhysicsComponentData())
            for entity in self.ExtraEntityData[entityname]:
                self.EntityData[entityname].append(entity)


class Locator(Object):
    def __init__(self, Name, **kwargs):
        super(Locator, self).__init__(Name, **kwargs)
        self._Type = "LOCATOR"
        self.HasAttachment = kwargs.get('HasAttachment', False)

    def create_attributes(self, data):
        if data is not None:
            self.Attributes = List(TkSceneNodeAttributeData(
                Name='ATTACHMENT', Value=data['ATTACHMENT']))


class Light(Object):
    def __init__(self, Name, **kwargs):
        super(Light, self).__init__(Name, **kwargs)
        self._Type = "LIGHT"

        self.Intensity = kwargs.get('Intensity', 40000)
        self.Colour = kwargs.get('Colour', (1, 1, 1))
        self.FOV = kwargs.get('FOV', 360.0)

    def create_attributes(self, data):
        self.Attributes = List(
            TkSceneNodeAttributeData(Name='FOV',
                                     Value=self.FOV),
            TkSceneNodeAttributeData(Name='FALLOFF',
                                     Value='quadratic'),
            TkSceneNodeAttributeData(Name='INTENSITY',
                                     Value=self.Intensity),
            TkSceneNodeAttributeData(Name='COL_R',
                                     Value=self.Colour[0]),
            TkSceneNodeAttributeData(Name='COL_G',
                                     Value=self.Colour[1]),
            TkSceneNodeAttributeData(Name='COL_B',
                                     Value=self.Colour[2]),
            TkSceneNodeAttributeData(Name='MATERIAL',
                                     Value='MATERIALS/LIGHT.MATERIAL.MBIN'))


class Joint(Object):
    def __init__(self, Name, **kwargs):
        super(Joint, self).__init__(Name, **kwargs)
        self._Type = "JOINT"
        self.JointIndex = kwargs.get("JointIndex", 1)

    def create_attributes(self, data):
        self.Attributes = List(TkSceneNodeAttributeData(
            Name='JOINTINDEX', Value=self.JointIndex))


class Emitter(Object):
    def __init__(self, Name, **kwargs):
        super(Emitter, self).__init__(Name, **kwargs)
        self._Type = "EMITTER"

    def create_attributes(self, data):
        if data is not None:
            self.Attributes = List(TkSceneNodeAttributeData(
                Name='MATERIAL', Value=data['MATERIAL']),
                                   TkSceneNodeAttributeData(
                Name='DATA', Value=data['DATA']))


class Mesh(Object):
    def __init__(self, Name, **kwargs):
        super(Mesh, self).__init__(Name, **kwargs)
        self._Type = "MESH"
        self.Vertices = kwargs.get('Vertices', None)
        self.Indexes = kwargs.get('Indexes', None)
        self.LodLevel = kwargs.get('LodLevel', 0)
        # This will be given as a TkMaterialData object or a string.
        self.Material = kwargs.get('Material', TkMaterialData(Name="EMPTY"))
        self.UVs = kwargs.get('UVs', None)
        self.Normals = kwargs.get('Normals', None)
        self.Tangents = kwargs.get('Tangents', None)
        self.CHVerts = kwargs.get('CHVerts', None)
        self.IsMesh = True
        # this will be a list of length 2 with each element being a 4-tuple.
        self.BBox = kwargs.get('BBox', None)
        self.HasAttachment = kwargs.get('HasAttachment', False)
        self.AnimData = kwargs.get('AnimData', None)    # the animation data

        # find out what streams have been provided
        self.determine_included_streams()

    def create_attributes(self, data):
        # data will be just the information required for the Attributes
        self.Attributes = List(
            TkSceneNodeAttributeData(Name='BATCHSTARTPHYSI',
                                     Value=data['BATCHSTART']),
            TkSceneNodeAttributeData(Name='VERTRSTARTPHYSI',
                                     Value=data['VERTRSTART']),
            TkSceneNodeAttributeData(Name='VERTRENDPHYSICS',
                                     Value=data['VERTREND']),
            TkSceneNodeAttributeData(Name='BATCHSTARTGRAPH',
                                     Value=0),
            TkSceneNodeAttributeData(Name='BATCHCOUNT',
                                     Value=data['BATCHCOUNT']),
            TkSceneNodeAttributeData(Name='VERTRSTARTGRAPH',
                                     Value=0),
            TkSceneNodeAttributeData(Name='VERTRENDGRAPHIC',
                                     Value=(data['VERTREND'] -
                                            data['VERTRSTART'])),
            TkSceneNodeAttributeData(Name='FIRSTSKINMAT',
                                     Value=0),
            TkSceneNodeAttributeData(Name='LASTSKINMAT',
                                     Value=0),
            TkSceneNodeAttributeData(Name='LODLEVEL',
                                     Value=self.LodLevel),
            TkSceneNodeAttributeData(Name='BOUNDHULLST',
                                     Value=data.get('BOUNDHULLST', 0)),
            TkSceneNodeAttributeData(Name='BOUNDHULLED',
                                     Value=data.get('BOUNDHULLED', 0)),
            TkSceneNodeAttributeData(Name='AABBMINX',
                                     Value=data.get('AABBMINX', 0)),
            TkSceneNodeAttributeData(Name='AABBMINY',
                                     Value=data.get('AABBMINY', 0)),
            TkSceneNodeAttributeData(Name='AABBMINZ',
                                     Value=data.get('AABBMINZ', 0)),
            TkSceneNodeAttributeData(Name='AABBMAXX',
                                     Value=data.get('AABBMAXX', 0)),
            TkSceneNodeAttributeData(Name='AABBMAXY',
                                     Value=data.get('AABBMAXY', 0)),
            TkSceneNodeAttributeData(Name='AABBMAXZ',
                                     Value=data.get('AABBMAXZ', 0)),
            TkSceneNodeAttributeData(Name='HASH',
                                     Value=data.get('HASH', 0)),
            TkSceneNodeAttributeData(Name='MATERIAL',
                                     Value=data['MATERIAL']),
            TkSceneNodeAttributeData(Name='MESHLINK',
                                     Value=self.Name + 'Shape'))
        if self.HasAttachment:
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='ATTACHMENT',
                                         Value=data['ATTACHMENT']))


class Collision(Object):
    def __init__(self, Name, **kwargs):
        super(Collision, self).__init__(Name, **kwargs)
        self._Type = "COLLISION"
        self.CType = kwargs.get("CollisionType", "Mesh")
        if self.CType == "Mesh":
            # get the relevant bits of data from the kwargs
            self.IsMesh = True
            self.Vertices = kwargs.get('Vertices', None)
            self.Indexes = kwargs.get('Indexes', None)
            self.Material = None
            self.UVs = kwargs.get('UVs', None)
            self.Normals = kwargs.get('Normals', None)
            self.Tangents = kwargs.get('Tangents', None)
            self.CHVerts = kwargs.get('CHVerts', None)

            # find out what streams have been provided
            self.determine_included_streams()
        else:
            # just give all 4 values. The required ones will be non-zero (deal
            # with later in the main file...)
            self.Width = kwargs.get('Width', 0)
            self.Height = kwargs.get('Height', 0)
            self.Depth = kwargs.get('Depth', 0)
            self.Radius = kwargs.get('Radius', 0)

    def create_attributes(self, data):
        self.Attributes = List(TkSceneNodeAttributeData(Name="TYPE",
                                                        Value=self.CType))
        if self.CType == 'Mesh':
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='BATCHSTART',
                                         Value=data['BATCHSTART']))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='BATCHCOUNT',
                                         Value=data['BATCHCOUNT']))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='VERTRSTART',
                                         Value=data['VERTRSTART']))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='VERTREND',
                                         Value=data['VERTREND']))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='FIRSTSKINMAT',
                                         Value=0))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='LASTSKINMAT',
                                         Value=0))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='BOUNDHULLST',
                                         Value=data.get('BOUNDHULLST', 0)))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name='BOUNDHULLED',
                                         Value=data.get('BOUNDHULLED', 0)))
        elif self.CType == 'Box':
            self.Attributes.append(
                TkSceneNodeAttributeData(Name="WIDTH",
                                         Value=data['WIDTH']))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name="HEIGHT",
                                         Value=data['HEIGHT']))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name="DEPTH",
                                         Value=data['DEPTH']))
        elif self.CType == 'Sphere':
            self.Attributes.append(
                TkSceneNodeAttributeData(Name="RADIUS",
                                         Value=data['RADIUS']))
        elif self.CType == 'Capsule' or self.CType == 'Cylinder':
            self.Attributes.append(
                TkSceneNodeAttributeData(Name="RADIUS",
                                         Value=data['RADIUS']))
            self.Attributes.append(
                TkSceneNodeAttributeData(Name="HEIGHT",
                                         Value=data['HEIGHT']))


class Model(Object):
    def __init__(self, Name, **kwargs):
        super(Model, self).__init__(Name, **kwargs)
        self._Type = "MODEL"

    def create_attributes(self, data):
        # data will be just the information required for the Attributes
        self.Attributes = List(
            TkSceneNodeAttributeData(Name='GEOMETRY',
                                     Value=data['GEOMETRY']),
            TkSceneNodeAttributeData(Name='NUMLODS',
                                     Value=data.get('NUMLODS', 1)))


class Reference(Object):
    def __init__(self, Name, **kwargs):
        # this will need to recieve SCENEGRAPH as an argument to be used.
        # Hopefully this casn be given by blender? Maybe have the user enter it
        # in or select the path from a popup??
        super(Reference, self).__init__(Name, **kwargs)
        self._Type = "REFERENCE"

        self.Scenegraph = kwargs.get("Scenegraph",
                                     "Enter in the path of the SCENE.MBIN you "
                                     "want to reference here.")

    def create_attributes(self, data):
        self.Attributes = List(TkSceneNodeAttributeData(Name='SCENEGRAPH',
                                                        Value=self.Scenegraph))
