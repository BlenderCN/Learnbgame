import struct
import subprocess
import threading
import platform

if "bpy" in locals():
    import importlib
    importlib.reload(version)
    importlib.reload(connection)
    importlib.reload(utils)
    importlib.reload(operator)

from .version import get_packer_version_array
from .connection import *
from .utils import *
from .operator import UVP_OT_PackOperator, UVP_OT_OverlapCheckOperator, UVP_OT_MeasureAreaOperator, UVP_OT_ValidateOperator, UVP_OT_SelectSimilarOperator

import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty
from bpy.types import AddonPreferences

import mathutils

if platform.system() == 'Linux':
    from .os_linux import *
elif platform.system() == 'Windows':
    from .os_windows import *
elif platform.system() == 'Darwin':
    from .os_mac import *
    
bl_info = {
    "name": "UV: Packmaster",
    "author": "glukoz",
    "version": (1, 91, 3),
    "blender": (2, 80, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UV"}


class UvPackmasterPreferences(AddonPreferences):
    bl_idname = __package__

    # Supporeted features
    FEATURE_demo : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_island_rotation : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_overlap_check : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_packing_depth : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_heuristic_search : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_advanced_heuristic : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_pack_ratio : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_pack_to_others : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_grouped_pack : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_lock_overlapping : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_self_intersect_processing : BoolProperty(
                    name='',
                    description='',
                    default=False)

    FEATURE_validation : BoolProperty(
                    name='',
                    description='',
                    default=False)

    platform_supported : BoolProperty(
                    name='',
                    description='',
                    default=True)
                    
    not_supported_message : StringProperty(
                    name='',
                    description='',
                    default='')

    label_message : StringProperty(
                    name='',
                    description='',
                    default='')

    write_to_file : BoolProperty(
                    name='Write UV data to file',
                    description='',
                    default=False)

    simplify_disable : BoolProperty(
                    name='Simplify Disable',
                    description='',
                    default=False)

    benchmark : BoolProperty(
                    name='Benchmark',
                    description='',
                    default=False)

    multithreaded : BoolProperty(
                    name='Mulithreaded',
                    description='',
                    default=True)

    overlap_check : BoolProperty(
                    name='Automatic Overlap Check',
                    description='Automatically check for overlapping islands after packing is done',
                    default=True)

    area_measure : BoolProperty(
                    name='Automatic Area Measurement',
                    description='Automatically measure islands area after packing is done',
                    default=True)

    iterations : IntProperty(
                    name='Iterations',
                    description='Number describing how exact the algorithm will be when searching for island placement. Too low value may cause islands to overlap',
                    default=200,
                    min=10,
                    max=10000)

    margin : FloatProperty(
                    name='Margin',
                    description='Margin to apply during packing',
                    default=0.005,
                    precision=3)

    rot_enable : BoolProperty(
                    name='Rotation Enable',
                    description='Allow the packer to rotate islands in order to achieve better result',
                    default=True)

    prerot_disable : BoolProperty(
                    name='Pre-Rotation Disable',
                    description='Disable the initial rotatation of islands before generating other orientations. The pre-rotation operation usually optimizes packing, use this option only if you have a good reason',
                    default=False)

    postscale_disable : BoolProperty(
                    name='Post-Scaling Disable',
                    description='Do not scale islands after packing in order to fit them into unit UV square. Enabling this option is not recommended in most cases',
                    default=False)

    rot_step : IntProperty(
                    name='Rotation Step',
                    description="Rotation step in degrees to apply during packing",
                    default=90,
                    min=0,
                    max=180)

    packing_depth : IntProperty(
                    name='Packing Depth',
                    description='',
                    default=1,
                    min=1,
                    max=100)

    tex_ratio : BoolProperty(
                    name='Use Texture Ratio',
                    description='Take into consideration the ratio of the active texture dimensions during packing. WARNING: make sure only one UV editor is opened in the Blender interface when using this option, otherwise the result is undefined',
                    default=False)

    pack_to_others : BoolProperty(
                    name='Pack To Others',
                    description='Add selected islands into those already packed in the unit UV square (no scaling will be applied)',
                    default=False)

    grouped_pack : BoolProperty(
                    name='Group Islands (Experimental)',
                    description="Make sure islands belonging to the same group are packed together. Island groups are defined by the 'Grouping Method' parameter. This feature is experimental: especially it can block when used together with 'Pack To Others' option in case no appropriate place is found for an island in the unit UV square. In such situation simply press ESC in order to cancel the process. For some UV layouts it is required to use the 'Heuristic Search' option in order to obtain a decent result from the grouped packing",
                    default=False)

    grouping_method : EnumProperty(
                    items=((str(UvGroupingMethod.EXTERNAL), 'Material', ''),
                           (str(UvGroupingMethod.SIMILARITY), 'Similarity', '')),
                    name="Grouping Method",
                    description="Grouping method to use")

    lock_overlapping : BoolProperty(
                    name='Lock Overlapping',
                    description='Treat overlapping islands as a single island',
                    default=False)

    extended_topo_analysis : BoolProperty(
                    name='Extended Topology Analysis',
                    description="Use the extended method of topology analysis if basic method fails for a particular island. If add-on reports invalid topology for an island you can enable this option in order to force it to use more sophisticated algorithm and try to process the island anyway. WARNING: enabling this option is not recommended in most cases - if the basic method reports the invalid topology error it probably means that you should verify your topology and fix it. If you enable this option the add-on may not notify you about such issues in your UV map",
                    default=False)

    allow_self_intersect : BoolProperty(
                    name='Process Self-Intersecting UV Faces',
                    description="With this option enabled add-on will try to process self-intersecting UV faces during the extended topology analysis procedure",
                    default=False)

    heuristic_search_time : IntProperty(
                    name='Heuristic Search Time',
                    description="The time in seconds the add-on will spend searching the optimal packing solution using the heuristic algorithm. Value '0' means the feature is disabled. This feature is most useful when a single packing pass doesn't take much time (a few seconds). Use it with a limited number of islands and with limited island orientations considered ('Rotation Step' == 90). The current heuristic algorithm is most efficient for packing UV maps containing limited number of big islands of irregular shape. Before doing a long search it is recommended to run a single packing pass in order to determine whether overlaps are not likely to happen for given 'Iterations' and 'Margin' parameters",
                    default=0,
                    min=0,
                    max=1000)

    advanced_heuristic : BoolProperty(
                    name='Advanced Heuristic',
                    description="Use advanced methods during a heuristic search. With this option enabled add-on will examine a broader set of solutions when searching for an optimal one. As the number of solutions to check is much bigger it is recommended to use longer search times in this mode. Note that in many cases this method provides best results with 'Rotation Step' set to a large value (e.g. 90 degress) because such setting considerably increses the number of packing iterations which can be performed in a given time",
                    default=False)

    similarity_threshold : FloatProperty(
                    name='Similarity Threshold',
                    description="A greater value of this parameter means islands will be more likely recognized as a similar in shape. '0.5' is a good threshold value to start with. Accuracy of the similar islands detection also depends on other factors: 1. 'Rotation Step' paramter: the lower rotation step value the better accuracy of the operation. Rotation step set to 90 should be sufficient in most cases though. 2. 'Iterations' paramter: more iterations means better accuracy. 200 iterations is a sufficient value in most cases. This value should be increased in the first place if the similarity detection returns incorrect results (especially when dealing with really small islands).",
                    default=0.5,
                    min=0.0,
                    precision=3)

    seed : IntProperty(
                    name='Seed',
                    description='',
                    default=0,
                    min=0,
                    max=10000)

    test_param : IntProperty(
                    name='Test Parameter',
                    description='',
                    default=0,
                    min=0,
                    max=10000)




class UVP_PT_PackPanel(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_label = 'UVPackmaster'
    bl_context = ''
    # bl_category = 'UVPackmaster'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'

    def draw(self, context):
        layout = self.layout

        warnings = []

        prefs = get_prefs()
        feature_not_supported_msg = '(Not supported in this packer version)'
        
        #if prefs.label_message != '':
        layout.label(text=prefs.label_message)
            
        col = layout.column(align=True)
        # col.enabled = prefs.enabled

        if in_debug_mode():
            box = col.box()
            box.label(text="Debug options:")
            box.prop(prefs, "write_to_file")
            box.prop(prefs, "simplify_disable")
            box.prop(prefs, "benchmark")

            row = box.row(align=True)
            row.enabled = prefs.FEATURE_packing_depth
            row.prop(prefs, "packing_depth")

            row = box.row(align=True)
            row.prop(prefs, "seed")

            row = box.row(align=True)
            row.prop(prefs, "test_param")
            col.separator()

        box = col.box()
        box.prop(prefs, "multithreaded")

        if not prefs.multithreaded:
            warnings.append('packing will be significantly slower with mulithreading disabled')

        # row = col.row()
        col.prop(prefs, "margin")
        # row = col.row()
        col.prop(prefs, "iterations")

        # Heuristic search
        row = col.row(align=True)
        row.enabled = prefs.FEATURE_heuristic_search

        # Heuristic Search Time
        row.prop(prefs, "heuristic_search_time")
        if not prefs.FEATURE_heuristic_search:
            prefs.heuristic_search_time = 0
            row.label(text=feature_not_supported_msg)

        # Advanced Heuristic
        box = col.box()
        box.enabled = prefs.FEATURE_advanced_heuristic and prefs.heuristic_search_time > 0
        row = box.row()
        row.prop(prefs, "advanced_heuristic")
        if not prefs.FEATURE_advanced_heuristic:
            prefs.advanced_heuristic = False
            row.label(text=feature_not_supported_msg)

        # Rotation Resolution
        box = col.box()
        box.enabled = prefs.FEATURE_island_rotation

        row = box.row()
        row.prop(prefs, "rot_enable")
        if not prefs.FEATURE_island_rotation:
            prefs.rot_enable = False
            row.label(text=feature_not_supported_msg)

        if not prefs.rot_enable:
            warnings.append('packing is not optimal with island rotations disabled')

        row = box.row()
        row.enabled = prefs.rot_enable
        row.prop(prefs, "prerot_disable")

        if prefs.FEATURE_island_rotation and prefs.prerot_disable:
            warnings.append('pre-rotation usually optimizes packing, disable it only if you have a good reason')

        row = col.row(align=True)
        row.enabled = prefs.rot_enable
        row.prop(prefs, "rot_step")

        # Post scale disable
        box = col.box()
        row = box.row()
        row.prop(prefs, "postscale_disable")

        # Overlap check
        box = col.box()
        box.enabled = prefs.FEATURE_overlap_check
        row = box.row()
        row.prop(prefs, "overlap_check")
        if not prefs.FEATURE_overlap_check:
            prefs.overlap_check = False
            row.label(text=feature_not_supported_msg)

        # Area measure
        box = col.box()
        row = box.row()
        row.prop(prefs, "area_measure")

        # Tex ratio
        box = col.box()
        box.enabled = prefs.FEATURE_pack_ratio
        row = box.row()
        row.prop(prefs, "tex_ratio")
        if not prefs.FEATURE_pack_ratio:
            prefs.tex_ratio = False
            row.label(text=feature_not_supported_msg)

        # Pack to others
        box = col.box()
        box.enabled = prefs.FEATURE_pack_to_others
        row = box.row()
        row.prop(prefs, "pack_to_others")
        if not prefs.FEATURE_pack_to_others:
            prefs.pack_to_others = False
            row.label(text=feature_not_supported_msg)

        # Lock overlapping
        box = col.box()
        box.enabled = prefs.FEATURE_lock_overlapping
        row = box.row()
        row.prop(prefs, "lock_overlapping")
        if not prefs.FEATURE_lock_overlapping:
            prefs.lock_overlapping = False
            row.label(text=feature_not_supported_msg)

        # Grouped pack
        box = col.box()
        box.enabled = prefs.FEATURE_grouped_pack
        row = box.row()
        row.prop(prefs, "grouped_pack")
        if not prefs.FEATURE_grouped_pack:
            prefs.grouped_pack = False
            row.label(text=feature_not_supported_msg)

        row  = box.row()
        row.prop(prefs, "grouping_method")
        row.enabled = prefs.grouped_pack

        # Similarity threshold
        col.prop(prefs, "similarity_threshold")

        if prefs.FEATURE_demo:
            op_text = UVP_OT_SelectSimilarOperator.bl_label + " (DEMO)"
        else:
            op_text = UVP_OT_SelectSimilarOperator.bl_label

        row = col.row(align=True)
        row.operator(UVP_OT_SelectSimilarOperator.bl_idname, text=op_text)

        col.separator()
        col.label(text='Topology Options')

        # Extend topo analysis
        box = col.box()
        row = box.row()
        row.prop(prefs, "extended_topo_analysis")

        if prefs.extended_topo_analysis:
            warnings.append('using exteded topology analysys is not recommended in most cases - use it only if you really need it')

        # Allow self intersect
        allow_self_intersect_enabled = prefs.FEATURE_self_intersect_processing and prefs.extended_topo_analysis
        box = col.box()
        box.enabled = allow_self_intersect_enabled

        if not allow_self_intersect_enabled:
            prefs.allow_self_intersect = False

        row = box.row()
        row.prop(prefs, "allow_self_intersect")
        if not prefs.FEATURE_self_intersect_processing:
            prefs.allow_self_intersect = False
            row.label(text=feature_not_supported_msg)

        col.separator()
        row = col.row(align=True)
        row.enabled = prefs.FEATURE_overlap_check
        # row = box.row()
        row.operator(UVP_OT_OverlapCheckOperator.bl_idname)
        if not prefs.FEATURE_overlap_check:
            row.label(text=feature_not_supported_msg)

        col.operator(UVP_OT_MeasureAreaOperator.bl_idname)

        # Validate operator

        row = col.row(align=True)
        row.enabled = prefs.FEATURE_validation
        if prefs.FEATURE_demo:
            op_text = UVP_OT_ValidateOperator.bl_label + " (DEMO)"
        else:
            op_text = UVP_OT_ValidateOperator.bl_label

        row.operator(UVP_OT_ValidateOperator.bl_idname, text=op_text)
        if not prefs.FEATURE_validation:
            row.label(text=feature_not_supported_msg)

        row = col.row(align=True)
        row.scale_y = 1.75

        if prefs.FEATURE_demo:
            op_text = UVP_OT_PackOperator.bl_label + " (DEMO)"
        else:
            op_text = UVP_OT_PackOperator.bl_label

        row.operator(UVP_OT_PackOperator.bl_idname, text=op_text)

        if len(warnings) > 0:
            col.separator()
            col.label(text='WARNINGS:')
            for warn in warnings:
                col.label(text='* ' + warn)

def platform_check():
    err_msg = 'Unsupported platform detected. Supported platforms are Linux 64 bit, Windows 64 bit'
    
    sys = platform.system()
    if sys != 'Linux' and sys != 'Windows' and sys != 'Darwin':
        return False, err_msg
        
    is_64bit = platform.machine().endswith('64')
    if not is_64bit:
        return False, err_msg
        
    return True, ''

def get_packer_version():
    packer_args = [get_packer_path(), '-E', '-o', str(UvPackerOpcode.REPORT_VERSION)]
    packer_proc = subprocess.Popen(packer_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    out_stream = packer_proc.stdin

    raw_uv_data = prepare_raw_uv_topo_data(list(), dict())
    out_stream.write(raw_uv_data)
    out_stream.flush()

    try:
        packer_proc.wait(5)
    except:
        packer_proc.terminate()
        raise

    in_stream = packer_proc.stdout

    version_msg = None
    while True:
        msg = connection_rcv_message(in_stream)
        msg_code = force_read_int(msg)

        if msg_code == UvPackMessageCode.VERSION:
            version_msg = msg
            break

    if version_msg is None:
        raise RuntimeError('Could not read the packer version')

    # TODO: make sure this won't block
    version_major = force_read_int(version_msg)
    version_minor = force_read_int(version_msg)
    version_suffix = struct.unpack('c', version_msg.read(1))[0].decode('utf-8')

    feature_cnt = struct.unpack('i', version_msg.read(4))[0]
    feature_codes = []

    for i in range(feature_cnt):
        feature_codes.append(struct.unpack('c', version_msg.read(1))[0])

    return version_major, version_minor, version_suffix, feature_codes

def parse_feature_codes(feature_codes):
    prefs = get_prefs()

    prefs.FEATURE_demo = False
    prefs.FEATURE_island_rotation = False
    prefs.FEATURE_overlap_check = False
    prefs.FEATURE_packing_depth = False
    prefs.FEATURE_heuristic_search = False
    prefs.FEATURE_pack_ratio = False
    prefs.FEATURE_pack_to_others = False
    prefs.FEATURE_grouped_pack = False
    prefs.FEATURE_lock_overlapping = False
    prefs.FEATURE_advanced_heuristic = False
    prefs.FEATURE_self_intersect_processing = False
    prefs.FEATURE_validation = False


    for code in feature_codes:
        int_code = int.from_bytes(code, 'little')
        if int_code == UvPackerFeatureCode.DEMO:
            prefs.FEATURE_demo = True
        elif int_code == UvPackerFeatureCode.ISLAND_ROTATION:
            prefs.FEATURE_island_rotation = True
        elif int_code == UvPackerFeatureCode.OVERLAP_CHECK:
            prefs.FEATURE_overlap_check = True
        elif int_code == UvPackerFeatureCode.PACKING_DEPTH:
            prefs.FEATURE_packing_depth = True
        elif int_code == UvPackerFeatureCode.HEURISTIC_SEARCH:
            prefs.FEATURE_heuristic_search = True
        elif int_code == UvPackerFeatureCode.PACK_RATIO:
            prefs.FEATURE_pack_ratio = True
        elif int_code == UvPackerFeatureCode.PACK_TO_OTHERS:
            prefs.FEATURE_pack_to_others = True
        elif int_code == UvPackerFeatureCode.GROUPED_PACK:
            prefs.FEATURE_grouped_pack = True
        elif int_code == UvPackerFeatureCode.LOCK_OVERLAPPING:
            prefs.FEATURE_lock_overlapping = True
        elif int_code == UvPackerFeatureCode.ADVANCED_HEURISTIC:
            prefs.FEATURE_advanced_heuristic = True
        elif int_code == UvPackerFeatureCode.SELF_INTERSECT_PROCESSING:
            prefs.FEATURE_self_intersect_processing = True
        elif int_code == UvPackerFeatureCode.VALIDATION:
            prefs.FEATURE_validation = True


def reset_debug_params(prefs):
    prefs.write_to_file = False
    prefs.simplify_disable = False
    prefs.seed = 0

def register():
    bpy.utils.register_class(UvPackmasterPreferences)
    bpy.utils.register_class(UVP_OT_PackOperator)
    bpy.utils.register_class(UVP_OT_MeasureAreaOperator)
    bpy.utils.register_class(UVP_OT_OverlapCheckOperator)
    bpy.utils.register_class(UVP_OT_ValidateOperator)
    bpy.utils.register_class(UVP_OT_SelectSimilarOperator)
    bpy.utils.register_class(UVP_PT_PackPanel)

    prefs = get_prefs()
    prefs.enabled = True

    prefs.platform_supported = True
    prefs.not_supported_message = ''
    prefs.label_message = ''
    reset_debug_params(prefs)

    result, err_msg = platform_check()
    if not result:
        prefs.platform_supported = False
        prefs.not_supported_message = err_msg
    else:
        result, err_msg = os_platform_check(get_packer_path())
        if not result:
            prefs.platform_supported = False
            prefs.not_supported_message = err_msg

    if not prefs.platform_supported:
        prefs.label_message = prefs.not_supported_message
        return

    try:
        version_major, version_minor, version_suffix, feature_codes = get_packer_version()

        if version_major != bl_info['version'][0] or version_minor != bl_info['version'][1]:
            raise RuntimeError('Unexpected packer version detected')

        release_suffix, version_array = get_packer_version_array()
        version_array_tmp = [ver_info for ver_info in version_array if ver_info.suffix == version_suffix]
        if len(version_array_tmp) != 1:
            raise RuntimeError('Unexpected number of versions found')

        version_long_name = version_array_tmp[0].long_name
        version_number_str = '.'.join(map(str, bl_info['version']))

        if release_suffix != '':
            version_number_str += '-' + release_suffix

        prefs.label_message = 'Packer version: {} ({})'.format(version_number_str, version_long_name)

        parse_feature_codes(feature_codes)

    except Exception as ex:
        if in_debug_mode():
            print_backtrace(ex)

        prefs.platform_supported = False
        prefs.not_supported_message = 'Unexpected error'
        prefs.label_message = 'Unexpected error'


def unregister():
    bpy.utils.unregister_class(UVP_PT_PackPanel)
    bpy.utils.unregister_class(UVP_OT_SelectSimilarOperator)
    bpy.utils.unregister_class(UVP_OT_ValidateOperator)
    bpy.utils.unregister_class(UVP_OT_OverlapCheckOperator)
    bpy.utils.unregister_class(UVP_OT_MeasureAreaOperator)
    bpy.utils.unregister_class(UVP_OT_PackOperator)
    bpy.utils.unregister_class(UvPackmasterPreferences)