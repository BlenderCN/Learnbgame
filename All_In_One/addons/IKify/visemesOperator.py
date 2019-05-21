import bpy

def copyVertexGroups(source_obj, dest_obj, vgroup_names):
    vgroup_ids = {}
    for name in vgroup_names:
        dest_obj.vertex_groups.new(name)
        vgroup_ids[source_obj.vertex_groups[name].index] = name
        
    for i, v in enumerate(source_obj.data.vertices):
        for source_vgroup in v.groups:
            if source_vgroup.group in vgroup_ids:
                dest_vgroup = dest_obj.vertex_groups[vgroup_ids[source_vgroup.group]]
                dest_vgroup.add([i], source_vgroup.weight, 'ADD')
                
def createShapeKeyMap(object):
    name_to_id = {}
    for i in range(len(object.data.shape_keys.key_blocks)):
        name_to_id[object.data.shape_keys.key_blocks[i].name] = i    
    return name_to_id

def createVertexGroupShapeKeys(object, shape_key_map, source_name, upper):
    vertex_group = 'LowerMouth'
    suffix = '_lower'
    if upper == True:
        vertex_group = 'UpperMouth'
        suffix = '_upper'
    
    key = object.data.shape_keys.key_blocks[shape_key_map[source_name]]
    key.value = 1.0
    new_key = object.shape_key_add(name=str(source_name) + suffix, from_mix=True)
    new_key.vertex_group = vertex_group
    shape_key_map[new_key.name] = len(shape_key_map)
    key.value = 0.0
    
def createUpperLowerShapeKeys(object, shape_key_map):
    createVertexGroupShapeKeys(object, shape_key_map, 'Expressions_mouth03_max', True)
    createVertexGroupShapeKeys(object, shape_key_map, 'Expressions_mouth04_max', True)
    createVertexGroupShapeKeys(object, shape_key_map, 'Expressions_mouth04_max', False)
    createVertexGroupShapeKeys(object, shape_key_map, 'Expressions_mouth09_min', True)
    createVertexGroupShapeKeys(object, shape_key_map, 'Expressions_mouth09_min', False)
    createVertexGroupShapeKeys(object, shape_key_map, 'Expressions_mouth09_max', False)
    createVertexGroupShapeKeys(object, shape_key_map, 'Expressions_mouth10_min', False)

def createSingleVisemeShapeKey(object, shape_key_map, mix, viseme_name):
    # first set the values of shape keys
    for name, value in mix.items():
        key = object.data.shape_keys.key_blocks[shape_key_map[name]]
        key.value = value

    # create the new shape key from mix        
    new_key = object.shape_key_add(name=str(viseme_name), from_mix=True)
    shape_key_map[new_key.name] = len(shape_key_map)

    # unset the values of the shape keys    
    for name, value in mix.items():
        key = object.data.shape_keys.key_blocks[shape_key_map[name]]
        key.value = 0.0    

def createVisemeShapeKeys(object, shape_key_map):
    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth04_max': 0.1,
        'Expressions_mouth04_max_upper': 0.4, 'Expressions_mouth12_max': 1.0}, 'Viseme_Neutral')
    
    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth10_min': 0.2,
        'Expressions_mouth09_min_upper': 0.7}, 'Viseme_R_eR')
    
    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth09_max': 0.5}, 'Viseme_M_B_P')
    
    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth04_max': 0.2,
        'Expressions_mouth04_max_upper': 0.15, 'Expressions_mouth10_max': 0.05, 'Expressions_mouth12_min': 0.25},
        'Viseme_N_NG_CH_J_DH_ZH_TH_S_SH')
    
    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth01_min': 0.3,
        'Expressions_mouth09_min': 0.4, 'Expressions_mouth10_max': 0.2, 'Expressions_mouth10_min':0.4},
        'Viseme_AA_AO_OW')
        
    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth02_min': 0.5,
        'Expressions_mouth03_max': 0.6, 'Expressions_mouth03_min': 0.3, 'Expressions_mouth09_max': 0.3,
        'Expressions_mouth10_max': 0.025, 'Expressions_mouth12_min': 0.2}, 'Viseme_IY_EH_Y')
        
    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth04_max': 0.250,
        'Expressions_mouth09_min_lower': 0.4, 'Expressions_mouth10_min': 0.3}, 'Viseme_L_EL')

    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth07_min': 0.7,
        'Expressions_mouth10_min': 0.1, 'Expressions_mouth12_max': 0.4, 'Expressions_mouth09_min_upper':0.3},
        'Viseme_W')

    createSingleVisemeShapeKey(object, shape_key_map, {'Expressions_mouth05_max': 0.5,
        'Expressions_mouth06_max': 0.5, 'Expressions_mouth10_max': 0.3, 'Expressions_mouth09_min_lower': 0.3,
        'Expressions_mouth10_min_upper': 0.5, 'Expressions_mouth04_max_lower': 0.3}, 'Viseme_IH_AE_AH_EY_AY_H:')


class VisemesOperator(bpy.types.Operator):
    """Create all the Visemes Shape Keys"""
    bl_idname = "object.create_visemes"
    bl_label = "Create Visemes shapekeys"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        reference_obj = scene.objects['IKify_reference_mesh_human_female']

        # Copy LowerMouth and UpperMouth vertex groups
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        copyVertexGroups(reference_obj, context.active_object, ['LowerMouth', 'UpperMouth'])
        
        # Create a map from shape key name to its index
        shape_key_map = createShapeKeyMap(context.active_object)

        # Create copies of some existing shape keys, but effecting only upper or lower mouth
        createUpperLowerShapeKeys(context.active_object, shape_key_map)
        
        # Create the Visemes Shape Keys
        createVisemeShapeKeys(context.active_object, shape_key_map)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(VisemesOperator)


def unregister():
    bpy.utils.unregister_class(VisemesOperator)

if __name__ == "__main__":
    register()