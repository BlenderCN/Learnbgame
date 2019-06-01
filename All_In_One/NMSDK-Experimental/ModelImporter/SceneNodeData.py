import math


class SceneNodeData():
    def __init__(self, info, parent=None):
        self.info = info
        self.parent = parent
        self.verts = dict()
        self.idxs = list()
        self.bounded_hull = None
        # The metadata will be read from the geometry file later.
        self.metadata = None
        self.children = list()
        children = self.info.pop('Children')
        for child in children:
            self.children.append(SceneNodeData(child, self))

# region public methods

    def Attribute(self, name):
        # Doesn't support AltID's
        for attrib in self.info['Attributes']:
            if attrib['Name'] == name:
                return attrib['Value']

    def iter(self):
        """ Returns an ordered iterable list of SceneNodeData objects. """
        objs = [self]
        for child in self.children:
            objs.extend(child.iter())
        return objs

    def get(self, ID):
        """ Return the SceneNodeData object with the specified ID. """
        for obj in self.iter():
            # Sanitize input ID for safety
            if isinstance(obj.Name, str):
                if obj.Name.upper() == ID.upper():
                    return obj

# region private methods

    def _generate_bounded_hull(self, bh_data):
        self.bounded_hull = bh_data[int(self.Attribute('BOUNDHULLST')):
                                    int(self.Attribute('BOUNDHULLED'))]

    def _generate_geometry(self):
        """ Generate the faces and edge data. """
        if len(self.idxs) == 0 or len(self.verts.keys()) == 0:
            raise ValueError('Something has gone wrong!!!')
        self.faces = list(zip(self.idxs[0::3],
                              self.idxs[1::3],
                              self.idxs[2::3]))
        self.edges = list()
        for face in self.faces:
            edges = [(face[0], face[1]),
                     (face[1], face[2]),
                     (face[2], face[0])]
            self.edges.extend(edges)

# region properties

    @property
    def Name(self):
        return self.info['Name']

    @property
    def Transform(self):
        trans = (float(self.info['Transform']['TransX']),
                 float(self.info['Transform']['TransY']),
                 float(self.info['Transform']['TransZ']))
        rot = (math.radians(float(self.info['Transform']['RotX'])),
               math.radians(float(self.info['Transform']['RotY'])),
               math.radians(float(self.info['Transform']['RotZ'])))
        scale = (float(self.info['Transform']['ScaleX']),
                 float(self.info['Transform']['ScaleY']),
                 float(self.info['Transform']['ScaleZ']))
        return {'Trans': trans, 'Rot': rot, 'Scale': scale}

    @property
    def Type(self):
        return self.info['Type']
