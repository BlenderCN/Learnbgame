import os
import bpy
from .para_temp import Property_add_subproperty
# from . import discrete_types
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty
        )
property_adder = Property_add_subproperty()


import json
discrete_methods = []
json_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "para_temp.json")
with open(json_file, "r") as para_temp:
    methods = json.load(para_temp)

#declear common paras
common_paras = methods['common']
class physika_common(bpy.types.PropertyGroup):
    pass
for para, value in common_paras.items():
    if type(value) == float:
        property_adder.add_float_parameter(physika_common, para, attr_default = value)
    elif type(value) == int:
        property_adder.add_int_parameter(physika_common, para, attr_default = value)
    elif type(value) == str:
        #TODO: add enum
        pass
                

#declear special paras
for method, cates in methods.items():
    if(method == "common"):
        continue
    discrete_methods.append(method)            
    exec('class physika_' + method + '(bpy.types.PropertyGroup):pass')
    for cate, paras in cates.items():
        exec('class ' + method + "_" + cate + '(bpy.types.PropertyGroup):pass')
        for para, value in paras.items():
            if(cate == 'blender'):
                property_adder.add_string_parameter(eval(method + '_' + cate), para, value)
            else:    
                if type(value) == float:
                    exec('property_adder.add_float_parameter(' + method + '_' + cate + ', para, attr_default = value)')
                elif type(value) == int:
                    exec('property_adder.add_int_parameter(' + method + '_' + cate + ', para, attr_default = value)')
                elif type(value) == str:
                    exec('property_adder.add_enum_parameter(' + method + '_' + cate + ', para, value)')
                elif type(value) == bool:
                    exec('property_adder.add_bool_parameter(' + method + '_' + cate + ', para, value)')                    

                    #TODO: add enum
                    pass
        exec('setattr(physika_' + method + ', "' + cate + '", PointerProperty(type = ' + method + '_' + cate +'))')


        
types = tuple(((method, method, method) for method in discrete_methods))

class physika_para(bpy.types.PropertyGroup):
    
    @classmethod
    def register(cls):
        print(types)
        cls.physika_discrete = EnumProperty(
            name = "Setting physika discreting method",
            items = types,
            default = 'meshless'
        )

        for method, cates in methods.items():
            exec('cls.' + method + ' = PointerProperty(type = physika_' + method + ')')
    

    def _update_frame_rate(self, context):
        if self.frame_rate >  1/self.delt_t:
            self.frame_rate = int(1/self.delt_t)
            
            
        
    @classmethod
    def unregister(cls):
        pass
        # del bpy.types.Scene.physika_discrete
        




def register():
    bpy.utils.register_class(physika_common)
    for method, cates in methods.items():
        if(method == "common"):
            continue
        for cate,paras in cates.items():
            exec('bpy.utils.register_class(' + method + '_' + cate + ')')
        exec('bpy.utils.register_class(physika_' + method + ')')
    bpy.utils.register_class(physika_para)
    from ...properties.object_properties import PhysiKaObjectProperties
    
    PhysiKaObjectProperties.physika_para = PointerProperty(type=physika_para)
def unregister():
    bpy.utils.unregister_class(physika_common)
    for method, cates in methods.items():
        if(method == "common"):
            continue
        for cate,paras in cates.items():
            exec('bpy.utils.unregister_class(' + method + '_' + cate + ')')
        exec('bpy.utils.unregister_class(physika_' + method + ')')
    bpy.utils.unregister_class(physika_para)
    # del bpy.types.Scene.physika_para

