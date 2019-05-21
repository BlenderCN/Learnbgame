import bpy
from collections import defaultdict
import math
import mathutils
import os


# Define limb parts based on vertex groups
def apply_name_template(template, parts):
    """ Fill in a name template string """
    return [template % part for part in parts]
    
def prefix_dfm(*parts):
    """ Prefix all the group names with 'Dfm' """
    return apply_name_template('Dfm%s', parts)
    
def make_group_side_names(side, parts):
    """ Prefixes group names with L_ or R_ """
    return apply_name_template('%s_' + side, parts)
    
ARM_PARTS = prefix_dfm(
    'Biceps',
    'ElbowFan',
    'ElbowFwd',
    'LoArm1',
    'LoArm2',
    'LoArm3',
    'UpArm1',
    'UpArm2',
    'UpArm3',
    'Wrist-1',
    'Wrist-2',
    'Wrist-3',
)
HAND_PARTS = (
    'Index-1',
    'Index-2',
    'Index-3',
    'Middle-1',
    'Middle-2',
    'Middle-3',
    'Palm-1',
    'Palm-2',
    'Palm-3',
    'Palm-4',
    'Palm-5',
    'Pinky-1',
    'Pinky-2',
    'Pinky-3',
    'Ring-1',
    'Ring-2',
    'Ring-3',
    'Thumb-1',
    'Thumb-2',
    'Thumb-3',
)
UPPER_LEG_PARTS = prefix_dfm(
    'UpLeg1',
    'UpLeg2',
)
LOWER_LEG_PARTS = prefix_dfm(
    'KneeFan',
    'KneeBack',
    'LoLeg',
)
FEET_PARTS = prefix_dfm(
    'Toe',
    'Foot',
)
HEAD_PARTS = (
    'DfmHead',
    'DfmLoLid_L',
    'DfmLoLid_R',
    'DfmUpLid_L',
    'DfmUpLid_R',
    'DfmNeck',
    'Eye_L',
    'Eye_R',
    'TongueBase',
    'TongueMid',
    'TongueTip',
    'Jaw',
)
TORSO_PARTS = prefix_dfm(
    'Clavicle',
    'Breast_L',
    'Breast_R',
    'Hips',
    'LegOut_L',
    'LegOut_R',
    'Pect2_L',
    'Pect2_R',
    'Scapula',
    'Spine1',
    'Spine2',
    'Spine3',
    'Stomach',
    'Trap2',
)
LIMB_CONFIG = [ # order for painter's algorithm
    ('chop_left_arm', make_group_side_names('L', ARM_PARTS)),      
    ('chop_left_hand', make_group_side_names('L', HAND_PARTS)),
    
    ('chop_left_foot', make_group_side_names('L', FEET_PARTS)),
    ('chop_left_lower_leg', make_group_side_names('L', LOWER_LEG_PARTS)),
    ('chop_left_upper_leg', make_group_side_names('L', UPPER_LEG_PARTS)),
    
    ('chop_head', HEAD_PARTS),
    ('chop_torso', TORSO_PARTS),
    
    ('chop_right_foot', make_group_side_names('R', FEET_PARTS)),
    ('chop_right_lower_leg', make_group_side_names('R', LOWER_LEG_PARTS)),
    ('chop_right_upper_leg', make_group_side_names('R', UPPER_LEG_PARTS)),
    
    ('chop_right_arm', make_group_side_names('R', ARM_PARTS)),
    ('chop_right_hand', make_group_side_names('R', HAND_PARTS)),
]


def pose_human(obj):
    """
    Moves the MakeHuman body into a nice position for rendering the constituent limbs.
    """
    left_bone = obj.pose.bones['UpArm_L']
    right_bone = obj.pose.bones['UpArm_R']
    left_bone.matrix *= mathutils.Matrix.Rotation(math.radians(-85.0), 4, 'X')
    right_bone.matrix *= mathutils.Matrix.Rotation(math.radians(-85.0), 4, 'X')


def create_normalmap_material(material_name='normal_material'):
    """
    Creates a material used to generate normal maps.
    """
    material = bpy.data.materials.new(material_name)
    material.use_shadeless = True
    material.diffuse_color = (0.0, 0.0, 0.0)
    texture_slots = material.texture_slots
    # create a blend texture for each axis and add them to slots on the material
    axes = ('x', 'y', 'z')
    for axis in axes:
        slot = texture_slots.add()
        slot.blend_type = 'ADD'
        slot.texture_coords = 'NORMAL'
        for map_axis in axes:
            map_value = 'NONE'
            if map_axis == 'x':
                map_value = axis.upper()
            setattr(slot, 'mapping_' + map_axis, map_value)
        tex_name = '%s_%s' % (material_name, axis)
        tex = bpy.data.textures.new(tex_name, 'BLEND')
        color = []
        for color_axis in axes:
            color_value = 0.0
            if color_axis == axis:
                color_value = 1.0
            color.append(color_value)
        slot.color = color
        slot.texture = tex
    return material


def create_limb_groups(obj, new_group_name, group_names, threshold=0.3):
    """
    Aggregates the named vertex groups on this object into one large group which
    is associated with a MaskModifier to isolate the limb during rendering.
    """
    original_groups = obj.vertex_groups
    relevant_groups = []
    for group_name in group_names:
        this_group = original_groups.get(group_name)
        if this_group is None:
            continue
        relevant_groups.append(this_group)
    mesh = obj.data       
    meta_group = obj.vertex_groups.new(name=new_group_name)
    indices = set()
    for vert in mesh.vertices:
        for group in relevant_groups:
            try:
                this_weight = group.weight(vert.index)
            except RuntimeError: # vertex not in group
                this_weight = -100.0
            if this_weight >= threshold:
                indices.add(vert.index)
    print('adding group and mask %s' % (meta_group.name))
    meta_group.add(list(indices), 1.0, 'ADD')
    mask_modifier = obj.modifiers.new('LimbMask_' + meta_group.name, 'MASK')
    mask_modifier.vertex_group = meta_group.name
    mask_modifier.show_render = mask_modifier.show_viewport = False


def arrange_scene_for_rendering(scene, flat_shaded=False):
    """
    Sets up the renderer, camera, and light.
    """
    render = scene.render
    render.alpha_mode = 'STRAIGHT'
    render.image_settings.color_mode = 'RGBA'
    render.use_full_sample = True
    render.use_shadows = not flat_shaded
    render.resolution_x, render.resolution_y = (1080, 1920)
    camera = bpy.data.cameras['Camera']
    camera.type = 'ORTHO'
    camera.ortho_scale = 28.0 # magic
    camera_obj = bpy.data.objects['Camera']
    camera_obj.rotation_euler = (math.radians(90.0), 0.0, -math.radians(90.0))
    camera_obj.location = (-25.0, 0.0, 12.0)
    light = bpy.data.lamps['Lamp']
    light.type = 'SUN'
    light.shadow_method = 'NOSHADOW'
    light_obj = bpy.data.objects['Lamp']
    light_obj.location = (-10.0, 0.0, 10.0)
    light_obj.rotation_euler = (0.0, math.radians(-45.0), 0.0)


def render_limbs(objs, limb_group_names, normal_maps=False, flat_shaded=False):
    """
    Renders each limb in isolation using the masks we created earlier.
    """
    scene = bpy.context.scene
    arrange_scene_for_rendering(scene, flat_shaded=flat_shaded)
    _render_limbs_force_material(
        objs, limb_group_names, flat_shaded=flat_shaded)
    if normal_maps:
        _render_normalmaps(objs, limb_group_names, )


def _render_normalmaps(objs, limb_group_names):
    """
    Creates a normal map material and renders all the limbs with it.
    """
    normalmap_material = create_normalmap_material()
    _render_limbs_force_material(objs, limb_group_names, material=normalmap_material)


def _render_limbs_force_material(objs, limb_group_names, material=None, flat_shaded=False):
    """
    Renders each limb in isolation using the masks we created earlier.
    Allows the mesh material to be overridden and for optional shadeless rendering.
    """
    scene = bpy.context.scene
    # hide all the limbs and optionally add the normalmap material
    for obj in objs:
        for modifier in obj.modifiers:
            if modifier.name.startswith('LimbMask_'):
                modifier.show_render = modifier.show_viewport = False
        if material is None:
            if flat_shaded:
                obj.data.materials[0].use_shadeless = flat_shaded
        else:
            # add the optional material to the mesh and assign it to the faces
            mesh = obj.data
            mesh.materials.append(material)
            material_index = len(mesh.materials) - 1
            for face in mesh.polygons:
                face.material_index = material_index

    # render each limb in isolation
    last_modifiers = []
    for limb_index, limb_group_name in enumerate(limb_group_names):
        # hide the previously displayed limb
        while last_modifiers:
            modifier = last_modifiers.pop()
            modifier.show_render = modifier.show_viewport = False
        for obj in objs:
            mask_name = 'LimbMask_' + limb_group_name
            if not mask_name in obj.modifiers:
                continue
            modifier = obj.modifiers[mask_name]
            modifier.show_render = modifier.show_viewport = True
            last_modifiers.append(modifier)
        # render limb
        target_directory = 'c:/tmp/'
        if material is None:
            filename = '%03d_%s.png' % (limb_index, limb_group_name)
        else:
            filename = '%03d_%s_%s.png' % (limb_index, limb_group_name, material.name)
        filepath = os.path.join(target_directory, filename)
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)

    
def chop(target_objects, group_threshold=0.5):
    """
    Interface for the chop_it operator.
    """
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in target_objects:
        pose_human(obj)
    # create a vertex group for each (sub object, limb)
    for limb_group_name, limb_group in LIMB_CONFIG:
        for root_object in target_objects:
            for subobj in root_object.children:
                if subobj.type.lower() == 'mesh':
                    create_limb_groups(subobj, limb_group_name, limb_group, threshold=group_threshold)


def render(target_objects, flat_shaded=False, normal_maps=False):
    """
    Interface for the render operator.
    """
    relevant_objs = []
    for root_object in target_objects:
        for subobj in root_object.children:
            if subobj.type.lower() == 'mesh':                        
                relevant_objs.append(subobj) 
    render_limbs(
        relevant_objs, [name for name, groups in LIMB_CONFIG],
        flat_shaded=flat_shaded, normal_maps=normal_maps
    )


class ChopHumanOperator(bpy.types.Operator):
    """ The Choperator. """
    bl_idname = 'chophuman.chop_it'
    bl_label = 'Chop'

    def execute(self, context):    
        chop(context.selected_objects, group_threshold=0.0)
        return {'FINISHED'}


class RenderChoppedHumanOperator(bpy.types.Operator):
    """ Render the chopped limbs. """
    bl_idname = 'chophuman.render_limbs'
    bl_label = 'Render'

    output_path = bpy.props.StringProperty(subtype='FILE_PATH', name='Output path')
    flat_shaded = bpy.props.BoolProperty(default=False, name='Flat shaded')
    normal_maps = bpy.props.BoolProperty(default=False, name='Normal maps')

    def execute(self, context):    
        render(context.selected_objects, self.flat_shaded, self.normal_maps)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class ChopHumanPanel(bpy.types.Panel):
    bl_idname = 'ChopHumanPanel'
    bl_label = 'Chop Human'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('chophuman.chop_it')
        row = layout.row()
        row.operator('chophuman.render_limbs')
