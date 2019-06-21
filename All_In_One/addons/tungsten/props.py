import bpy

class MetaProperty:
    prefix = ''
    properties = {}

    def get_properties(self, prefix):
        self.prefix = prefix + '_'
        yield (prefix, self)
        for k, v in self.properties.items():
            yield (self.prefix + k, v)

    def register_properties(self, props, prefix):
        for k, v in self.get_properties(prefix):
            props[k] = v

def meta_propertize(cls):
    for k, v in vars(cls).copy().items():
        if hasattr(v, 'register_properties'):
            for kp, vp in v.get_properties(k):
                setattr(cls, kp, vp)
    return cls

# this class was originally written to be used for a property
# on a material, referencing a texture.
# so: mat is the object owning the property
#     tex is the object the property points to
class FakeIDProperty(MetaProperty):
    ID_NAME = None
    HUMAN_NAME = None
    COLLECTION = None

    @property
    def attr_name(self):
        return self.prefix + self.ID_NAME

    def __init__(self, name, description):
        def update_id(mat, context):
            self.normalize(mat)

        self.properties = {
            self.attr_name: bpy.props.StringProperty(
                name=name,
                description=description + ' ' + self.HUMAN_NAME,
                default='',
                update=update_id,
            ),
        }

    def normalize(self, mat):
        texname = getattr(mat, self.attr_name)
        if not texname:
            return None
        tex = getattr(bpy.data, self.COLLECTION).get(texname)
        if not tex:
            setattr(mat, self.attr_name, '')
            return None
        return tex

    def draw(self, lay, mat, **kwargs):
        self.normalize(mat)
        lay.prop_search(mat, self.attr_name, bpy.data, self.COLLECTION, **kwargs)

class ObjectProperty(FakeIDProperty):
    ID_NAME = 'object'
    HUMAN_NAME = 'Object'
    COLLECTION = 'objects'
