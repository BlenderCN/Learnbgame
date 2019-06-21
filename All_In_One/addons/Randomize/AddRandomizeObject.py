import bpy
from rna_prop_ui import rna_idprop_ui_prop_get  # For setting custom property constraints
import random

def count_randomize_objs():
    # Count randomize objects
    k = .000
    next_k = '.001'
    while 'Randomize Obj' + next_k in bpy.context.scene.objects:
        k = k + .001
        if k + .001 > .009:
            next_k = str(k + .001).lstrip('0') + '0'
        else:
            next_k = str(k + .001).lstrip('0')
    if (k < 0.001):
        ending = ''
    else:
        if k > .009:
            ending = str(k).lstrip('0') + '0'
        else:
            ending = str(k).lstrip('0')
    return ending

def update_callback(self, context):
    if bpy.context.active_object is not None:
        if bpy.context.active_object.name.split('.')[0] == 'Randomize Obj':
            randomize_obj = bpy.context.active_object
            props = randomize_obj.random_props
            if len(randomize_obj.children) > 0:
                random.seed(props.seed_location)
                for obj in randomize_obj.children:
                    obj.delta_location.x = float(props.location_enabled) * props.location[0] * (random.random() - 0.5)
                    obj.delta_location.y = float(props.location_enabled) * props.location[1] * (random.random() - 0.5)
                    obj.delta_location.z = float(props.location_enabled) * props.location[2] * (random.random() - 0.5)

                random.seed(props.seed_rotation)
                for obj in randomize_obj.children:
                    obj.delta_rotation_euler.x = float(props.rotation_enabled) * props.rotation[0] * (random.random() - 0.5)
                    obj.delta_rotation_euler.y = float(props.rotation_enabled) * props.rotation[1] * (random.random() - 0.5)
                    obj.delta_rotation_euler.z = float(props.rotation_enabled) * props.rotation[2] * (random.random() - 0.5)

                random.seed(props.seed_scale)
                for obj in randomize_obj.children:
                    if props.uniform_scale_enabled:
                        obj.delta_scale.x = float(props.scale_enabled) * props.uniform_scale * (random.random() - 0.5)
                        obj.delta_scale.y = obj.delta_scale.x
                        obj.delta_scale.z = obj.delta_scale.x
                    else:
                        obj.delta_scale.x = float(props.scale_enabled) * props.scale[0] * (random.random() - 0.5)
                        obj.delta_scale.y = float(props.scale_enabled) * props.scale[1] * (random.random() - 0.5)
                        obj.delta_scale.z = float(props.scale_enabled) * props.scale[2] * (random.random() - 0.5)
    return

class RandomizeObjProperties(bpy.types.PropertyGroup):
    location = bpy.props.FloatVectorProperty(name='location', description='Amount of location randomness', update=update_callback)
    rotation = bpy.props.FloatVectorProperty(name='rotation', description='Amount of rotation randomness', update=update_callback)
    scale = bpy.props.FloatVectorProperty(name='scale', description='Amount of scale randomness', update=update_callback)

    location_enabled = bpy.props.BoolProperty(name='location_enabled', description='Toggle location randomness', default=True, update=update_callback)
    rotation_enabled = bpy.props.BoolProperty(name='rotation_enabled', description='Toggle rotation randomness', default=True, update=update_callback)
    scale_enabled = bpy.props.BoolProperty(name='scale_enabled', description='Toggle scale randomness', default=True, update=update_callback)

    uniform_scale_enabled = bpy.props.BoolProperty(name='uniform_scale_enabled', description='Toggle uniform scale', default=False, update=update_callback)
    uniform_scale = bpy.props.FloatProperty(name='uniform_scale', description='Amount of scale randomness', update=update_callback)

    seed_location = bpy.props.IntProperty(name='seed_location', description='Seed for pseudorandom number generation', min=0, soft_min=0, update=update_callback)
    seed_rotation = bpy.props.IntProperty(name='seed_rotation', description='Seed for pseudorandom number generation', min=0, soft_min=0, update=update_callback)
    seed_scale = bpy.props.IntProperty(name='seed_scale', description='Seed for pseudorandom number generation', min=0, soft_min=0, update=update_callback)

class AddRandomizeObject(bpy.types.Operator):
    bl_idname = "object.add_randomize_object"
    bl_label = "Add Randomize Object"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # Create randomize object (empty object)
        randomize_obj = bpy.data.objects.new('Randomize Obj', object_data=None)
        bpy.context.scene.objects.link(randomize_obj)
        if len(randomize_obj.name) > 15:
            ending = randomize_obj.name.split('.')[1]
        else:
            ending = ''

        # Using a PropertyGroup
        randomize_obj.random_props.location = [0.0, 0.0, 0.0]
        randomize_obj.random_props.rotation = [0.0, 0.0, 0.0]
        randomize_obj.random_props.scale = [0.0, 0.0, 0.0]

        randomize_obj.random_props.location_enabled = True
        randomize_obj.random_props.rotation_enabled = True
        randomize_obj.random_props.scale_enabled = True

        randomize_obj.random_props.uniform_scale_enabled = False
        randomize_obj.random_props.uniform_scale = 0.0

        randomize_obj.random_props.seed_location = 0
        randomize_obj.random_props.seed_rotation = 0
        randomize_obj.random_props.seed_scale = 0

        return {'FINISHED'}

def set_prop_constraint(obj, prop, minimum, maximum):
    obj_name = obj.name
    data_path = "data.objects[obj_name]"
    item = eval("bpy.%s" % data_path)
    prop_type = type(item[prop])
    prop_ui = rna_idprop_ui_prop_get(item, prop)
    
    if prop_type in (float, int):
        prop_ui['soft_min'] = prop_ui['min'] = prop_type(minimum)
        prop_ui['soft_max'] = prop_ui['max'] = prop_type(maximum)

def register():
    bpy.utils.register_class(RandomizeObjProperties)
    bpy.types.Object.random_props = bpy.props.PointerProperty(type=RandomizeObjProperties)
    bpy.utils.register_class(AddRandomizeObject)

def unregister():
    bpy.utils.unregister_class(AddRandomizeObject)
    bpy.utils.unregister_class(RandomizeObjProperties)
