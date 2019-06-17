import bpy
from bpy.types import PropertyGroup
from bpy.props import *


def context_items(pg, context):
    items = [('TOOL', 'Tool', 'Adjust tool settings', 'TOOL_SETTINGS', 0)]

    active = [
        ('OBJECT', 'Object', 'Adjust object settings', 'OBJECT_DATA', 1),
        ('CONSTRAINT', 'Constraint', 'Adjust constraint settings', 'CONSTRAINT', 2)]

    modifier = ('MODIFIER', 'Modifier', 'Adjust modifier settings', 'MODIFIER', 3)

    mesh = [('DATA', 'Mesh', 'Adjust mesh settings', 'MESH_DATA', 4)]
    curve = [('DATA', 'Curve', 'Adjust curve settings', 'CURVE_DATA', 4)]
    surface = [('DATA', 'Surface', 'Adjust surface settings', 'SURFACE_DATA', 4)]
    meta = [('DATA', 'Meta', 'Adjust meta settings', 'META_DATA', 4)]
    font = [('DATA', 'Font', 'Adjust font settings', 'FONT_DATA', 4)]

    gpencil = [
        ('SHADERFX', 'Effects', 'Adjust effect settings', 'SHADERFX', 4),
        ('DATA', 'Grease Pencil', 'Adjust grease pencil settings', 'GREASEPENCIL', 5)]

    armature = [('DATA', 'Armature', 'Adjust armature settings', 'ARMATURE_DATA', 4)]
    bone = ('BONE', 'Bone', 'Adjust bone settings', 'BONE_DATA', 5)
    bone_constraint = ('BONE_CONSTAINT', 'Bone Constraint', 'Adjust bone constraint settings', 'CONSTRAINT_BONE', 6)
    lattice = [('DATA', 'Lattice', 'Adjust lattice settings', 'LATTICE_DATA', 4)]
    empty = [('DATA', 'Empty', 'Adjust empty settings', 'EMPTY_DATA', 4)]
    speaker = [('DATA', 'Speaker', 'Adjust speaker settings', 'SPEAKER', 4)]
    camera = [('DATA', 'Camera', 'Adjust camera settings', 'CAMERA_DATA', 4)]
    light = [('DATA', 'Light', 'Adjust light settings', 'LIGHT_DATA', 4)]

    light_probe = [('DATA', 'Light Probe', 'Adjust light probe settings', 'LIGHTPROBE_CUBEMAP', 4)]
    material = ('MATERIAL', 'Material', 'Adjust material settings', 'MATERIAL_DATA', 6)

    obj = context.active_object

    if obj:
        for item in active:
            items.append(item)

        if obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'GPENCIL', 'LATTICE'}:
            items.append(modifier)

        for item in locals()[obj.type.lower()]:
            items.append(item)

        if context.workspace.tools_mode in {'POSE', 'EDIT_ARMATURE'}:
            items.append(bone)

            if context.workspace.tools_mode == 'POSE':
                items.append(bone_constraint)

        elif obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'GPENCIL'}:
            items.append(material)

    return items


class Tool(PropertyGroup):
    expand_workflow: BoolProperty(default=True)
    expand_sharp_options: BoolProperty(default=True)
    expand_mirror_options: BoolProperty(default=True)
    expand_operator_options: BoolProperty(default=False)
    expand_status: BoolProperty(default=False)
    expand_mesh_clean_options: BoolProperty(default=False)
    expand_specialoptions : BoolProperty(default=False)


class Object(PropertyGroup):
    expand_transform: BoolProperty(default=False)
    expand_delta_transform: BoolProperty(default=False)
    expand_relations: BoolProperty(default=True)
    expand_display: BoolProperty(default=True)
    expand_display_bounds: BoolProperty(default=True)

    # cycles
    expand_cycles_settings: BoolProperty(default=False)
    expand_cycles_settings_ray_visibility: BoolProperty(default=False)
    expand_cycles_settings_performance: BoolProperty(default=False)


class Constraint(PropertyGroup):
    expand_settings: BoolProperty(default=True)


class Modifier(PropertyGroup):
    expand_settings: BoolProperty(default=True)


class Mesh(PropertyGroup):
    expand_vertex_groups: BoolProperty(default=False)
    expand_shape_keys: BoolProperty(default=False)
    expand_uv_texture: BoolProperty(default=False)
    expand_vertex_colors: BoolProperty(default=False)
    expand_face_maps: BoolProperty(default=False)
    expand_normals: BoolProperty(default=True)
    expand_normals_auto_smooth: BoolProperty(default=True)
    expand_texture_space: BoolProperty(default=False)
    expand_customdata: BoolProperty(default=False)


class Curve(PropertyGroup):
    expand_shape_curve: BoolProperty(default=False)
    expand_geometry_curve: BoolProperty(default=True)
    expand_geometry_curve_bevel: BoolProperty(default=False)
    expand_pathanim: BoolProperty(default=False)
    expand_active_spline: BoolProperty(default=False)
    expand_curve_texture_space: BoolProperty(default=False)
    # expand_font: BoolProperty(default=False)
    # expand_font_transform: BoolProperty(default=False)
    # expand_paragraph: BoolProperty(default=False)
    # expand_paragraph_alignment: BoolProperty(default=False)
    # expand_paragraph_spacing: BoolProperty(default=False)
    # expand_text_boxes: BoolProperty(default=False)
    expand_shape_keys: BoolProperty(default=False)


class Surface(PropertyGroup):
    expand_shape_curve: BoolProperty(default=True)
    expand_active_spline: BoolProperty(default=False)
    expand_curve_texture_space: BoolProperty(default=False)
    expand_shape_keys: BoolProperty(default=False)


class Meta(PropertyGroup):
    expand_metaball: BoolProperty(default=True)
    expand_metaball_element: BoolProperty(default=True)
    expand_mball_texture_space: BoolProperty(default=False)


class Font(PropertyGroup):
    expand_shape_curve: BoolProperty(default=True)
    expand_geometry_curve: BoolProperty(default=True)
    expand_geometry_curve_bevel: BoolProperty(default=True)
    expand_curve_texture_space: BoolProperty(default=False)
    expand_font: BoolProperty(default=False)
    expand_font_transform: BoolProperty(default=False)
    expand_paragraph: BoolProperty(default=False)
    expand_paragraph_alignment: BoolProperty(default=False)
    expand_paragraph_spacing: BoolProperty(default=False)
    expand_text_boxes: BoolProperty(default=False)


class GPencil(PropertyGroup):
    expand_gpencil_layers: BoolProperty(default=True)
    expand_gpencil_layer_adjustments: BoolProperty(default=False)
    expand_gpencil_layer_relations: BoolProperty(default=False)
    expand_gpencil_onion_skinning: BoolProperty(default=False)
    expand_gpencil_vertex_groups: BoolProperty(default=False)
    expand_gpencil_strokes: BoolProperty(default=False)
    expand_gpencil_display: BoolProperty(default=False)
    expand_gpencil_canvas: BoolProperty(default=False)


class Armature(PropertyGroup):
    expand_skeleton: BoolProperty(default=False)
    expand_display: BoolProperty(default=False)
    expand_bone_groups: BoolProperty(default=False)
    expand_pose_library: BoolProperty(default=False)
    expand_iksolver_itasc: BoolProperty(default=False)


class Lattice(PropertyGroup):
    expand_lattice: BoolProperty(default=True)

    # from properties_data_mesh
    expand_vertex_groups: BoolProperty(default=False)
    expand_shape_keys: BoolProperty(default=False)


class Empty(PropertyGroup):
    expand_empty: BoolProperty(default=True)


class Speaker(PropertyGroup):
    expand_speaker: BoolProperty(default=True)
    expand_distance: BoolProperty(default=False)
    expand_cone: BoolProperty(default=False)


class Camera(PropertyGroup):
    expand_lens: BoolProperty(default=True)
    expand_camera_dof: BoolProperty(default=False)
    expand_camera_dof_aperture: BoolProperty(default=False)
    expand_camera: BoolProperty(default=False)
    expand_camera_steroscopy: BoolProperty(default=False)
    expand_camera_safe_areas: BoolProperty(default=False)
    expand_camera_safe_areas_center_cut: BoolProperty(default=False)
    expand_camera_background_image: BoolProperty(default=False)
    expand_camera_display: BoolProperty(default=False)
    expand_camera_display_passepartout: BoolProperty(default=False)


class Light(PropertyGroup):
    expand_preview: BoolProperty(default=False)
    expand_light: BoolProperty(default=True)
    expand_nodes: BoolProperty(default=True)
    expand_EEVEE_light: BoolProperty(default=True)
    expand_EEVEE_light_distance: BoolProperty(default=False)
    expand_EEVEE_shadow: BoolProperty(default=False)
    expand_EEVEE_shadow_contact: BoolProperty(default=False)
    expand_EEVEE_shadow_cascaded_shadow_map: BoolProperty(default=False)
    expand_area: BoolProperty(default=False)
    expand_spot: BoolProperty(default=False)
    # expand_falloff_curve: BoolProperty(default=False)


class Light_Probe(PropertyGroup):
    expand_lightprobe: BoolProperty(default=True)
    expand_lightprobe_visibility: BoolProperty(default=False)
    expand_lightprobe_parallax: BoolProperty(default=False)
    expand_lightprobe_display: BoolProperty(default=False)


class Data(PropertyGroup):
    mesh: CollectionProperty(type=Mesh)
    curve: CollectionProperty(type=Curve)
    surface: CollectionProperty(type=Surface)
    meta: CollectionProperty(type=Meta)
    font: CollectionProperty(type=Font)
    gpencil: CollectionProperty(type=GPencil)
    armature: CollectionProperty(type=Armature)
    lattice: CollectionProperty(type=Lattice)
    empty: CollectionProperty(type=Empty)
    speaker: CollectionProperty(type=Speaker)
    camera: CollectionProperty(type=Camera)
    light: CollectionProperty(type=Light)
    light_probe: CollectionProperty(type=Light_Probe)


class ShaderFX(PropertyGroup):
    expand_settings: BoolProperty(default=True)


class Bone(PropertyGroup):
    expand_transform: BoolProperty(default=False)
    expand_curved: BoolProperty(default=False)
    expand_relations: BoolProperty(default=True)
    expand_display: BoolProperty(default=True)
    expand_inverse_kinematics: BoolProperty(default=False)
    expand_deform: BoolProperty(default=False)


class BoneConstraint(PropertyGroup):
    expand_settings: BoolProperty(default=True)


class Material(PropertyGroup):
    expand_preview: BoolProperty(default=False)
    expand_surface: BoolProperty(default=False)
    expand_volume: BoolProperty(default=False)
    expand_displacement: BoolProperty(default=False)
    expand_viewport: BoolProperty(default=True)
    expand_settings: BoolProperty(default=False)
    expand_settings_surface: BoolProperty(default=False)
    expand_settings_volume: BoolProperty(default=False)
    expand_material_hops: BoolProperty(default=False)

    # grease pencil
    expand_gpencil_preview: BoolProperty(default=False)
    expand_gpencil_surface: BoolProperty(default=True)
    expand_gpencil_strokecolor: BoolProperty(default=True)
    expand_gpencil_fillcolor: BoolProperty(default=True)
    expand_gpencil_options: BoolProperty(default=False)


class Panels(PropertyGroup):
    tool: CollectionProperty(type=Tool)
    object: CollectionProperty(type=Object)
    constraint: CollectionProperty(type=Constraint)
    modifier: CollectionProperty(type=Modifier)
    data: CollectionProperty(type=Data)
    shaderfx: CollectionProperty(type=ShaderFX)
    bone: CollectionProperty(type=Bone)
    bone_constraint: CollectionProperty(type=BoneConstraint)
    material: CollectionProperty(type=Material)


class HopsHelperOptions(PropertyGroup):

    context: EnumProperty(
        name = 'Context',
        description = 'HOps helper context',
        items = context_items)

    panels: CollectionProperty(type=Panels)
