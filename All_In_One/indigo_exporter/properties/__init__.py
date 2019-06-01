import bpy
def parse_properties(properties, target):
    # parse properties dict and add them to target property group
    for property in properties:
        prop = property.copy()
        
        ptype = prop['type']
        del prop['type']
        
        if ptype == 'bool':
            t = bpy.props.BoolProperty
            a = {k: v for k,v in prop.items() if k in ["name",
                    "description","default","options","subtype","update"]}
        elif ptype == 'bool_vector':
            t = bpy.props.BoolVectorProperty
            a = {k: v for k,v in prop.items() if k in ["name",
                    "description","default","options","subtype","size",
                    "update"]}
        elif ptype == 'collection':
            t = bpy.props.CollectionProperty
            prop['type'] = prop['ptype']
            del prop['ptype']
            
            a = {k: v for k,v in prop.items() if k in ["type","name",
                    "description","default","options"]}
        elif ptype == 'enum':
            t = bpy.props.EnumProperty
            a = {k: v for k,v in prop.items() if k in ["items","name",
                    "description","default","options","update"]}
        elif ptype == 'float':
            t = bpy.props.FloatProperty
            a = {k: v for k,v in prop.items() if k in ["name",
                    "description","default","min","max","soft_min","soft_max",
                    "step","precision","options","subtype","unit","update", "get", "set"]}
        elif ptype == 'float_vector':
            t = bpy.props.FloatVectorProperty
            a = {k: v for k,v in prop.items() if k in ["name",
                    "description","default","min","max","soft_min","soft_max",
                    "step","precision","options","subtype","size","update"]}
        elif ptype == 'int':
            t = bpy.props.IntProperty
            a = {k: v for k,v in prop.items() if k in ["name",
                    "description","default","min","max","soft_min","soft_max",
                    "step","options","subtype","update"]}
        elif ptype == 'int_vector':
            t = bpy.props.IntVectorProperty
            a = {k: v for k,v in prop.items() if k in ["name",
                    "description","default","min","max","soft_min","soft_max",
                    "options","subtype","size","update"]}
        elif ptype == 'pointer':
            t = bpy.props.PointerProperty
            prop['type'] = prop['ptype']
            del prop['ptype']
            
            a = {k: v for k,v in prop.items() if k in ["type", "name",
                    "description","options","update"]}
        elif ptype == 'string':
            t = bpy.props.StringProperty
            a = {k: v for k,v in prop.items() if k in ["name",
                    "description","default","maxlen","options","subtype",
                    "update"]}
        else:
            continue

        #a = {k: v for k,v in prop.items()}
        #del a['attr']
        setattr(target, prop['attr'], t(**a))

def register_properties_dict(cls):
    # use as decorator for PropertyGroup subclasses to automatically parse properties dict
    parse_properties(cls.properties, cls)
    return cls
    