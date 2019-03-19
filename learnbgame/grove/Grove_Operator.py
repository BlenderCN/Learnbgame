# coding=utf-8

""" The Grove. Blender Addon to grow true to nature 3D trees.
    The code in this file is responsible for drawing the UI and handling events from the UI -
    calling the appropriate functionality from Grove.py.

    It also defines all parameters.

    Copyright 2014 - 2018, Wybren van Keulen, The Grove """


import bpy
import bpy.utils.previews
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty, BoolProperty, StringProperty, EnumProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Matrix, Vector, bvhtree, Euler, Quaternion
from math import radians

from .Grove import *
from .Presets import *
from .Translation import t
from .Twigs import list_twigs, append_twigs, check_twigs
from .Textures import list_textures
from .Utils import invoke_user_preferences


class TheGrove6(Operator, AddObjectHelper):
    """ The Grove tree simulator. """

    bl_idname = "mesh.the_grove"
    bl_label = "The Grove "
    bl_options = {'REGISTER', 'UNDO'}

    height = 0.0
    number_of_polygons = 0

    trunks = []  # These are the trees.
    mesh_cache = [None, None, None, None]  # Geometry cache of the last build.

    empties = []
    empties_presets = []
    age = 0
    cursor_location = Vector((0.0, 0.0, 0.0))

    strokes = []
    display_prune_warning = False
    display_vertex_colors_warning = False
    display_vanishing_twig_warning = False
    tree_has_animation = False
    display_empty_twig_warning = False
    display_undo_warning = False

    do_read_preset : BoolProperty(name="Do Load Preset", default=False, options={'HIDDEN'})
    do_not_read_preset : BoolProperty(name="Do Not Read Preset", default=False, options={'HIDDEN'})
    do_update : BoolProperty(name="Do Update", default=True, options={'HIDDEN'})
    do_update_only_twigs : BoolProperty(name="Do Update Twigs", default=False, options={'HIDDEN'})

    global icons
    icons = bpy.utils.previews.new()
    icons_directory = join(dirname(__file__), "Icons")
    icons.load("IconLogo", join(icons_directory, "IconLogo.png"), 'IMAGE')
    icons.load("IconRestart", join(icons_directory, "IconRestart.png"), 'IMAGE')
    icons.load("IconGrow", join(icons_directory, "IconGrow.png"), 'IMAGE')
    icons.load("IconPrune", join(icons_directory, "IconPrune.png"), 'IMAGE')
    icons.load("IconShape", join(icons_directory, "IconShape.png"), 'IMAGE')
    icons.load("IconAdd", join(icons_directory, "IconAdd.png"), 'IMAGE')
    icons.load("IconRemove", join(icons_directory, "IconRemove.png"), 'IMAGE')
    icons.load("IconRename", join(icons_directory, "IconRename.png"), 'IMAGE')
    icons.load("IconWindDirectionNorth", join(icons_directory, "IconWindDirectionNorth.png"), 'IMAGE')
    icons.load("IconWindDirectionEast", join(icons_directory, "IconWindDirectionEast.png"), 'IMAGE')
    icons.load("IconWindDirectionSouth", join(icons_directory, "IconWindDirectionSouth.png"), 'IMAGE')
    icons.load("IconWindDirectionWest", join(icons_directory, "IconWindDirectionWest.png"), 'IMAGE')
    icons.load("IconAnimate", join(icons_directory, "IconAnimate.png"), 'IMAGE')
    icons.load("IconAdvanced", join(icons_directory, "IconAdvanced.png"), 'IMAGE')
    icons.load("IconPlay", join(icons_directory, "IconPlay.png"), 'IMAGE')
    icons.load("IconStop", join(icons_directory, "IconStop.png"), 'IMAGE')
    icons.load("IconNone", join(icons_directory, "IconNone.png"), 'IMAGE')
    icons.load("IconZoom", join(icons_directory, "IconZoom.png"), 'IMAGE')
    icons.load("IconSmooth", join(icons_directory, "IconSmooth.png"), 'IMAGE')
    icons.load("IconPreset", join(icons_directory, "IconPreset.png"), 'IMAGE')

    def update_tree(self, context):
        """ A callback function attached to parameters that require updating the tree model. """
        self.do_update = True

    def do_not_update_tree(self, context):
        """ A callback function attached to parameters that don't require the model to be rebuilt. """
        self.do_update = False

    def presets(self, context):
        """ Fill the presets menu. """
        return enumerate_presets()

    def read_preset(self, context):
        if self.do_not_read_preset:
            self.do_not_read_preset = False
            self.do_read_preset = False
            return
        else:
            self.do_read_preset = True

    presets_menu : EnumProperty(
        name=t('presets_menu'), description=t('presets_menu_tt'),
        items=presets, update=read_preset)

    preset_name : StringProperty(
        name=t('preset_name'), description=t('preset_name_tt'),
        default="", update=do_not_update_tree)

    add_preset : BoolProperty(
        name=t('add_preset'), description=t('add_preset_tt'),
        default=False, update=do_not_update_tree)

    def do_replace_preset(self, context):
        if self.replace_preset:
            self.remove_preset = False
        self.do_update = False

    replace_preset : BoolProperty(
        name=t('replace_preset'), description=t('replace_preset_tt'),
        default=False, update=do_replace_preset)

    replace_preset_cancel : BoolProperty(
        name=t('replace_preset_cancel'), description=t('replace_preset_cancel_tt'),
        default=False,
        update=do_not_update_tree)

    replace_preset_confirm : BoolProperty(
        name=t('replace_preset_confirm'),
        description=t('replace_preset_confirm_tt'),
        default=False,
        update=do_not_update_tree)

    def do_remove_preset(self, context):
        if self.remove_preset:
            self.replace_preset = False
        self.do_update = False

    remove_preset : BoolProperty(
        name=t('remove_preset'), description=t('remove_preset_tt'),
        default=False,
        update=do_remove_preset)

    remove_preset_cancel : BoolProperty(
        name=t('remove_preset_cancel'), description=t('remove_preset_cancel_tt'),
        default=False,
        update=do_not_update_tree)

    remove_preset_confirm : BoolProperty(
        name=t('remove_preset_confirm'), description=t('remove_preset_confirm_tt'),
        default=False,
        update=do_not_update_tree)

    rename_preset : BoolProperty(
        name=t('rename_preset'), description=t('rename_preset_tt'),
        default=False,
        update=do_not_update_tree)

    advanced_ui_presets : BoolProperty(
        name="", description=t('advanced_ui_show_more') + t('advanced_ui_presets_tt'),
        default=False, update=do_not_update_tree)

    advanced_ui_shade : BoolProperty(
        name="", description=t('advanced_ui_show_more') + t('advanced_ui_shade_tt'),
        default=False, update=do_not_update_tree)

    advanced_ui_flow : BoolProperty(
        name="", description=t('advanced_ui_show_more') + t('advanced_ui_flow_tt'),
        default=False, update=do_not_update_tree)

    advanced_ui_drop : BoolProperty(
        name="", description=t('advanced_ui_show_more') + t('advanced_ui_drop_tt'),
        default=False, update=do_not_update_tree)

    advanced_ui_add : BoolProperty(
        name="", description=t('advanced_ui_show_more') + t('advanced_ui_add_tt'),
        default=False, update=do_not_update_tree)

    advanced_ui_turn : BoolProperty(
        name="", description=t('advanced_ui_show_more') + t('advanced_ui_turn_tt'),
        default=False, update=do_not_update_tree)

    advanced_ui_build : BoolProperty(
        name="", description=t('advanced_ui_show_more') + t('advanced_ui_build_tt'),
        default=False, update=do_not_update_tree)

    advanced_ui_thicken : BoolProperty(
        name="", description=t('advanced_ui_show_more') + t('advanced_ui_thicken_tt'),
        default=False, update=do_not_update_tree)

    restart : BoolProperty(
        name=t('restart'), description=t('restart_tt'),
        default=False, update=update_tree)

    manual_prune : BoolProperty(
        name=t('manual_prune'), description=t('manual_prune_tt'),
        default=False,
        update=update_tree)

    smooth : BoolProperty(
        name=t('smooth'), description=t('smooth_tt'),
        default=False,
        update=update_tree)

    smoothing : FloatProperty(
        name=t("smooth"), description=t('smooth_tt'),
        default=radians(20.0), min=radians(5.0), max=radians(90.0), step=500, subtype='ANGLE', unit='ROTATION',
        update=update_tree)

    manual_grow : BoolProperty(
        name='manual_grow', description='manual_grow_tt',
        default=False,
        update=update_tree)

    shape : BoolProperty(
        name=t('shape'), description=t('shape_tt'),
        default=False,
        update=update_tree)

    simulate : BoolProperty(
        name=t('simulate'), description=t('simulate_tt'),
        default=False,
        update=update_tree)

    grow_years : IntProperty(
        name=t('grow_years'), description=t('grow_years_tt'),
        default=4, soft_min=1, soft_max=100,
        update=do_not_update_tree)

    zoom : BoolProperty(
        name=t('zoom'), description=t('zoom_tt'),
        default=False,
        update=do_not_update_tree)

    do_change_number_of_trees : BoolProperty(name="Do Change Trunk Number", default=False, options={'HIDDEN'})

    def change_number_of_trees(self, context):
        self.do_change_number_of_trees = True
        self.do_update = True

    number_of_trees : IntProperty(
        name=t('number_of_trees'),
        default=1, soft_min=1, soft_max=25,
        update=change_number_of_trees,
        description=t('number_of_trees_tt'))

    tree_space : FloatProperty(
        name=t('tree_space'), description=t('tree_space_tt'),
        default=.2, soft_min=0.05, soft_max=5.0, step=25, precision=3, subtype='DISTANCE', unit='LENGTH',
        update=change_number_of_trees)

    # Shade and Prune parameters.
    def update_shade_preview(self, context):
        if self.show_shade_preview:
            self.do_update = True

    shade_leaf_area : FloatProperty(
        name=t('shade_leaf_area'), description=t('shade_leaf_area_tt'),
        default=1.5, min=0.01, soft_min=0.05, soft_max=10.0, step=50,
        update=update_shade_preview)

    shade_samples : IntProperty(
        name=t('shade_samples'),
        default=64, min=1, soft_min=8, soft_max=1600,
        update=update_shade_preview,
        description=t('shade_samples_tt'))

    shade_sensitivity : FloatProperty(
        name=t("shade_sensitivity"), description=t('shade_sensitivity_tt'),
        default=0.5, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    show_shade_preview : BoolProperty(
        name="", description=t('show_shade_preview_tt'),
        default=False,
        update=update_tree)

    show_dead_preview : BoolProperty(
        name="", description=t('show_dead_preview_tt'),
        default=False,
        update=update_tree)

    drop_shaded : FloatProperty(
        name=t('drop_shaded'), description=t('drop_shaded_tt'),
        default=0.0, min=0.0, max=1.0, step=10,
        update=update_shade_preview)

    drop_relatively_weak : FloatProperty(
        name=t('drop_relatively_weak'), description=t('drop_relatively_weak_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=5,
        update=do_not_update_tree)

    keep_dead : FloatProperty(
        name=t('keep_dead'), description=t('keep_dead_tt'),
        default=0.2, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    drop_low : FloatProperty(
        name=t('drop_low'), description=t('drop_low_tt'),
        default=3.0, soft_min=0.0, soft_max=30.0, step=100, precision=3, subtype='DISTANCE', unit='LENGTH',
        update=do_not_update_tree)

    keep_thick : FloatProperty(
        name=t('keep_thick'), description=t('keep_thick_tt'),
        default=0.01, soft_min=0.0, soft_max=0.05, step=0.01, precision=3, unit='LENGTH',
        update=do_not_update_tree)

    # Flow parameters.
    favor_current : FloatProperty(
        name=t('favor_current'), description=t('favor_current_tt'),
        default=0.5, soft_min=-1.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    shade_avoidance : FloatProperty(
        name=t('Avoid Shade'), description=t('avoid_shade_tt'),
        default=0.0, soft_min=-1.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    favor_current_reach : FloatProperty(
        name=t('favor_current_reach'), description=t('favor_current_reach_tt'),
        default=2.0, soft_min=0.0, soft_max=20.0, step=50, precision=2, subtype='DISTANCE', unit='LENGTH',
        update=do_not_update_tree)

    favor_healthy : FloatProperty(
        name=t('favor_healthy'), description=t('favor_healthy_tt'),
        default=0.0, soft_min=-1.0, soft_max=1.3, step=10,
        update=do_not_update_tree)

    favor_rising : FloatProperty(
        name=t('favor_rising'), description=t('favor_rising_tt'),
        default=0.0, soft_min=-1.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    branching_inefficiency : FloatProperty(
        name=t('branching_inefficiency'), description=t('branching_inefficiency_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    photo_range : IntProperty(
        name="Photo Range", description=t('bud_life_tt'),
        default=3, soft_min=1, soft_max=40,
        update=do_not_update_tree)

    peak_height : FloatProperty(
        name=t('peak_height'), description=t('peak_height'),
        default=35.0, soft_min=5.0, soft_max=140.0, step=200, precision=1, subtype='DISTANCE', unit='LENGTH',
        update=do_not_update_tree)

    # Grow parameters.
    number_of_branches : IntProperty(
        name=t(''), description='',
        default=0, soft_min=0, soft_max=100000000,
        update=do_not_update_tree)

    grow_nodes : IntProperty(
        name=t('grow_nodes'), description=t('grow_nodes_tt'),
        default=3, soft_min=0, soft_max=20,
        update=do_not_update_tree)

    grow_length : FloatProperty(
        name=t('grow_length'), description=t('grow_length_tt'),
        default=0.3, soft_min=0.01, soft_max=1.0, subtype='DISTANCE', unit='LENGTH',
        update=do_not_update_tree)

    # WIP R7
    grow_exponent : FloatProperty(
        name='Grow Exponent', description='Todo',
        default=0.3, soft_min=0.01, soft_max=8.0,
        update=do_not_update_tree)

    shade_elongation : FloatProperty(
        name=t('shade_elongation'), description=t('shade_elongation_tt'),
        default=0.0, soft_min=-0.9, soft_max=1.0, step=5,
        update=do_not_update_tree)

    # Branching parameters.
    branching_types = [
        ("1", t('branching_type_single'), t('branching_type_single_tt')),
        ("2", t('branching_type_double'), t('branching_type_double_tt')),
        ("3", t('branching_type_whorl_of_3'), t('branching_type_whorl_of_3_tt')),
        ("4", t('branching_type_whorl_of_4'), t('branching_type_whorl_of_4_tt')),
        ("5", t('branching_type_whorl_of_5'), t('branching_type_whorl_of_5_tt')),
        ("6", t('branching_type_whorl_of_6'), t('branching_type_whorl_of_6_tt'))]

    branching : EnumProperty(
        name=t('branching_types'), description=t('branching_types_tt'),
        items=branching_types,
        default="1",
        update=update_tree)

    branch_chance : FloatProperty(
        name=t("branch_chance"), description=t('branch_chance_tt'),
        default=0.1, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    branch_chance_light_required : FloatProperty(
        name=t('branch_chance_light_threshold'), description=t('branch_chance_light_threshold_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    bud_life : IntProperty(
        name=t("bud_life"), description=t('bud_life_tt'),
        default=3, soft_min=1, soft_max=40,
        update=do_not_update_tree)

    branch_chance_only_terminal : FloatProperty(
        name=t('branch_chance_only_terminal'), description=t('branch_chance_only_terminal_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    regenerative_branch_chance : FloatProperty(
        name=t('regenerative_branch_chance'), description=t('regenerative_branch_chance_tt'),
        default=0.05, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    regenerative_branch_chance_light_required : FloatProperty(
        name=t('regenerative_branch_chance_light_required'),
        description=t('regenerative_branch_chance_light_required_tt'),
        default=0.5, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    apical_bud_fatality : FloatProperty(
        name=t('apical_bud_fatality'), description=t('apical_bud_fatality_tt'),
        default=0.1, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    flower_power : FloatProperty(
        name=t('flower_power'), description=t('flower_power_tt'),
        default=0.1, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    branch_angle : FloatProperty(
        name=t("branch_angle"), description=t('branch_angle_tt'),
        default=radians(45.0), min=radians(1.0), max=radians(90.0), step=500, subtype='ANGLE', unit='ROTATION',
        update=update_tree)

    # Turn, or tropisms.
    phototropism : FloatProperty(
        name=t('phototropism'), description=t('phototropism_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=30,
        update=do_not_update_tree)

    gravitropism : FloatProperty(
        name=t('gravitropism'), description=t('gravitropism_tt'),
        default=0.0, soft_min=-1.0, soft_max=1.0, step=30,
        update=do_not_update_tree)

    gravitropism_shade : FloatProperty(
        name=t('gravitropism_shade'), description=t('gravitropism_shade_tt'),
        default=0.0, soft_min=-1.0, soft_max=1.0, step=30,
        update=do_not_update_tree)

    gravitropism_buds : FloatProperty(
        name=t('gravitropism_buds'), description=t('gravitropism_buds_tt'),
        default=0.0, soft_min=-1.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    gravitropism_buds_randomness : FloatProperty(
        name=t('gravitropism_buds_randomness'), description=t('gravitropism_buds_randomness_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    plagiotropism : FloatProperty(
        name=t("plagiotropism"), description=t('plagiotropism_tt'),
        default=0.0, soft_min=-1.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    plagiotropism_buds : FloatProperty(
        name=t('plagiotropism_buds'), description=t('plagiotropism_buds_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=10,
        update=update_tree)

    random_heading : FloatProperty(
        name=t('random_heading'), description=t('random_heading_tt'),
        default=radians(10.0), min=radians(0.0), max=radians(90.0), step=500, subtype='ANGLE', unit='ROTATION',
        update=do_not_update_tree)

    random_pitch : FloatProperty(
        name=t('random_pitch'), description=t('random_pitch_tt'),
        default=radians(5.0), min=radians(0.0), max=radians(90.0), step=500, subtype='ANGLE', unit='ROTATION',
        update=do_not_update_tree)

    # Interact parameters.
    environment_shade : FloatProperty(
        name=t('environment_shade'), description=t('environment_shade_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    do_environment : BoolProperty(name="Do Environment Interaction", default=False, options={'HIDDEN'})
    do_environment_block : BoolProperty(name="Do Environment Block", default=False, options={'HIDDEN'})

    def check_environment(self, context):
        """ Check if the entered environment object exists. """

        if self.environment_name != "" and self.environment_name not in context.scene.objects:
            self.environment_name = ""

        if self.environment_name != "" and self.force != "6":
            self.do_environment = True
            if self.force in ["1", "3", "5", "7"]:
                self.do_environment_block = True
        else:
            self.do_environment = False
            self.do_environment_block = False
        self.do_update = False

    forces = [
        ("1", t('forces_block'), t('forces_block_tt')),
        ("7", t('forces_shade_plus_block'), t('forces_shade_plus_block_tt')),
        ("2", t('forces_deflect'), t('forces_deflect_tt')),
        ("3", t('forces_deflect_plus_block'), t('forces_deflect_plus_block_tt')),
        ("4", t('forces_attract'), t('forces_attract_tt')),
        ("5", t('forces_attract_plus_block'), t('forces_attract_plus_block_tt')),
        ("6", t('forces_none'), t('forces_none_tt'))]

    force : EnumProperty(
        name=t('force'), description=t('force_tt'),
        items=forces,
        default="6",
        update=check_environment)

    environment_name : StringProperty(
        name=t('environment_name'), description=t('environment_name_tt'),
        default="",
        update=check_environment)

    force_power : FloatProperty(
        name=t('force_power'), description=t('force_power'),
        default=0.1, soft_min=0.0, soft_max=1.0, step=5,
        update=do_not_update_tree)

    force_radius : FloatProperty(
        name=t('force_radius'), description=t('force_radius_tt'),
        default=4.0, soft_min=0.1, soft_max=20.0, step=50,
        update=do_not_update_tree)

    # Bend parameters.
    branch_weight : FloatProperty(
        name=t('branch_weight'), description=t('branch_weight_tt'),
        update=update_tree,
        default=1.0, soft_min=0.0, soft_max=64.0, step=10)

    leaf_weight : FloatProperty(
        name=t('leaf_weight'), description=t('leaf_weight_tt'),
        default=0.2, soft_min=0.0, soft_max=1.0, step=10,
        update=update_tree)

    bake_bend : FloatProperty(
        name=t('bake_bend'), description=t('bake_bend_tt'),
        default=0.1, soft_min=0.0, soft_max=1.0, step=10,
        update=update_tree)

    fatigue : FloatProperty(
        name=t('fatigue'), description=t('fatigue_tt'),
        default=1.0, soft_min=0.0, soft_max=1.0, step=10,
        update=update_tree)

    # Build parameters.
    do_change_build_type : BoolProperty(name="Do Environment Interaction", default=False, options={'HIDDEN'})

    def change_build_type(self, context):
        self.do_change_build_type = True
        self.do_update = True

    build_types = [
        ("2", t('build_type_adaptive_mesh'), t('build_type_adaptive_mesh_tt')),
        ("4", t('build_type_adaptive_mesh_plus_wind'), t('build_type_adaptive_mesh_plus_wind_tt'))]

    build_type : EnumProperty(
        name=t('build_type'), description=t('build_type_tt'),
        items=build_types,
        default="2",
        update=change_build_type)

    display_scale_to_twig_warning : BoolProperty(name="Do Load Preset", default=False, options={'HIDDEN'})

    def change_scale_to_twig(self, context):
        self.do_update = True
        self.display_scale_to_twig_warning = True

    scale_to_twig : FloatProperty(
        name=t('scale_to_twig'),
        default=1.0, min=0.1, soft_min=0.1, soft_max=5.0, step=20,
        update=change_scale_to_twig,
        description=t('scale_to_twig_tt'))

    tip_thickness : FloatProperty(
        name=t('tip_thickness'), description=t('tip_thickness_tt'),
        default=0.01, soft_min=0.003, soft_max=0.02, step=0.01, precision=3, unit='LENGTH',
        update=do_not_update_tree)

    tip_decrease : FloatProperty(
        name=t('tip_decrease'), description=t('tip_decrease_tt'),
        default=0.0, soft_min=0.0, soft_max=1.0, step=10, precision=1,
        update=do_not_update_tree)

    internode_gain : FloatProperty(
        name=t('internode_gain'),
        default=0.0005, soft_min=0.0, soft_max=0.01, step=0.0001, precision=5, unit='LENGTH',
        update=update_tree,
        description=t('internode_gain_tt'))

    join_branches : FloatProperty(
        name=t('join_branches'), description=t('join_branches_tt'),
        default=0.75, soft_min=0.0, soft_max=1.2, step=10, precision=2,
        update=update_tree)

    root_scale : FloatProperty(
        name=t('root_scale'), description=t('root_scale_tt'),
        default=1.2, soft_min=1.0, soft_max=5.0, step=10, precision=1,
        update=update_tree)

    root_bump : FloatProperty(
        name=t('root_bump'), description=t('root_bump_tt'),
        default=2.0, soft_min=0.0, soft_max=10.0, step=20, precision=1,
        update=update_tree)

    root_shape : FloatProperty(
        name=t('root_shape'), description=t('root_shape_tt'),
        default=0.5, soft_min=0.01, soft_max=1.0, step=10, precision=2,
        update=update_tree)

    root_distribution : FloatProperty(
        name=t('root_distribution'), description=t('root_distribution_tt'),
        default=0.4, soft_min=0.01, soft_max=1.0, step=10, precision=2,
        update=update_tree)

    profile_resolution : IntProperty(
        name=t('profile_resolution'), description=t('profile_resolution_tt'),
        default=24, min=3, soft_min=4, soft_max=64,
        update=update_tree)

    profile_resolution_reduction : FloatProperty(
        name=t('profile_resolution_reduction'), description=t('profile_resolution_reduction_tt'),
        default=0.8, soft_min=0.0, soft_max=1.0, step=10, precision=1,
        update=update_tree)

    twist : FloatProperty(
        name=t('twist'), description=t('twist_tt'),
        default=0.1, soft_min=0.0, soft_max=1.0, step=500, precision=2, subtype='ANGLE', unit='ROTATION',
        update=update_tree)

    u_repeat : IntProperty(
        name=t('u_repeat'), description=t('u_repeat_tt'),
        default=2, soft_min=1, soft_max=10,
        update=update_tree)

    def click_wind_direction_n(self, context):
        if not self.wind_direction_n:
            if not(self.wind_direction_e or self.wind_direction_s or self.wind_direction_w):
                self.wind_direction_n = True
        else:
            if self.wind_direction_s:
                self.wind_direction_s = False
                self.wind_direction_n = True
        self.do_update = False

    def click_wind_direction_e(self, context):
        if not self.wind_direction_e:
            if not(self.wind_direction_n or self.wind_direction_s or self.wind_direction_w):
                self.wind_direction_e = True
        else:
            if self.wind_direction_w:
                self.wind_direction_w = False
                self.wind_direction_e = True
        self.do_update = False

    def click_wind_direction_s(self, context):
        if not self.wind_direction_s:
            if not(self.wind_direction_n or self.wind_direction_e or self.wind_direction_w):
                self.wind_direction_s = True
        else:
            if self.wind_direction_n:
                self.wind_direction_n = False
                self.wind_direction_s = True
        self.do_update = False

    def click_wind_direction_w(self, context):
        if not self.wind_direction_w:
            if not(self.wind_direction_n or self.wind_direction_e or self.wind_direction_s):
                self.wind_direction_w = True
        else:
            if self.wind_direction_e:
                self.wind_direction_e = False
                self.wind_direction_w = True
        self.do_update = False

    wind_direction_n : BoolProperty(
        name=t(""), description=t('wind_direction_n_tt'),
        default=False,
        update=click_wind_direction_n)

    wind_direction_e : BoolProperty(
        name=t(""), description=t('wind_direction_e_tt'),
        default=False,
        update=click_wind_direction_e)

    wind_direction_s : BoolProperty(
        name=t(""), description=t('wind_direction_s_tt'),
        default=False,
        update=click_wind_direction_s)

    wind_direction_w : BoolProperty(
        name=t(""), description=t('wind_direction_w_tt'),
        default=True,
        update=click_wind_direction_w)

    wind_force : FloatProperty(
        name=t('wind_force'), description=t('wind_force_tt'),
        default=0.2, soft_min=0.0, soft_max=2.0, step=10,
        update=do_not_update_tree)

    turbulence : FloatProperty(
        name=t('turbulence'), description=t('turbulence_tt'),
        default=0.2, soft_min=0.0, soft_max=1.0, step=10,
        update=do_not_update_tree)

    wind_shapes : IntProperty(
        name=t('wind_shapes'), description=t('wind_shapes_tt'),
        default=10, soft_min=5, soft_max=200, step=10,
        update=do_not_update_tree)

    play_stop : BoolProperty(
        name=t(""),
        default=False,
        update=do_not_update_tree,
        description=t('play_stop_tt'))

    wind_frequency : FloatProperty(
        name=t('wind_frequency'), description=t('wind_frequency_tt'),
        default=1.0, soft_min=0.0, soft_max=2.0,
        update=do_not_update_tree)

    calculate_wind : BoolProperty(
        name=t('calculate_wind'), description=t('calculate_wind_tt'),
        default=False,
        update=update_tree)

    # Twig parameters.
    def update_cached(self, context):
        self.do_update = True
        self.do_update_only_twigs = True

        # Cached build does not work well with the new twig picker.
        if self.twigs_menu != t('pick_objects'):
            self.do_update_only_twigs = False

    def change_twigs_menu(self, context):
        check_twigs(self, context)
        self.do_update = True

    def list_twigs_1(self, context):
        return list_twigs(self, context, icons)

    twigs_menu : EnumProperty(
        name=t('twigs_menu'),
        items=list_twigs_1,
        update=change_twigs_menu,
        description=t('twigs_menu_tt'))

    textures_menu : EnumProperty(
        name=t('textures_menu'),
        items=list_textures,
        update=update_tree,
        description=t('textures_menu_tt'))

    configure_textures_path : BoolProperty(
        name=t('configure_textures_path'), description=t('configure_textures_path_tt'),
        default=False,
        update=do_not_update_tree)

    apical_twig : StringProperty(
        name=t('apical_twig'), description=t('apical_twig_tt'),
        default="", update=update_cached)

    lateral_twig : StringProperty(
        name=t('lateral_twig'), description=t('lateral_twig_tt'),
        default="", update=update_cached)

    lateral_twig_limit : FloatProperty(
        name=t('lateral_twig_limit'), description=t('lateral_twig_limit_tt'),
        default=0.02, soft_min=0.005, soft_max=0.2, unit='LENGTH',
        update=update_tree)

    lateral_twig_chance : FloatProperty(
        name=t('lateral_twig_chance'), description=t('lateral_twig_chance_tt'),
        default=0.2, soft_min=0.0, soft_max=1.0, step=10, precision=1,
        update=update_tree)

    twig_viewport_detail : FloatProperty(
        name=t('twig_viewport_detail'), description=t('twig_viewport_detail_tt'),
        default=0.2, soft_min=0.1, soft_max=1.0, step=10, precision=1,
        update=update_cached)

    do_layer_thickness : BoolProperty(
        name=t('layer_thickness'), description=t('do_layer_thickness_tt'),
        default=True, update=update_tree)
    do_layer_weight : BoolProperty(
        name=t('layer_weight'), description=t('do_layer_weight_tt'),
        default=False, update=update_tree)
    do_layer_health : BoolProperty(
        name=t('layer_health'), description=t('do_layer_health_tt'),
        default=False, update=update_tree)
    do_layer_shade : BoolProperty(
        name=t('layer_shade'), description=t('do_layer_shade_tt'),
        default=False, update=update_tree)
    do_layer_power : BoolProperty(
        name=t('layer_power'), description=t('do_layer_power_tt'),
        default=False, update=update_tree)
    do_layer_generation : BoolProperty(
        name=t('layer_generation'), description=t('do_layer_generation_tt'),
        default=False, update=update_tree)
    do_layer_dead : BoolProperty(
        name=t('layer_dead'), description=t('do_layer_dead_tt'),
        default=True, update=update_tree)
    do_layer_pitch : BoolProperty(
        name=t('layer_pitch'), description=t('do_layer_pitch_tt'),
        default=False, update=update_tree)
    do_layer_apical : BoolProperty(
        name=t('layer_apical'), description=t('do_layer_apical_tt'),
        default=True, update=update_tree)
    do_layer_lateral : BoolProperty(
        name=t('layer_lateral'), description=t('do_layer_lateral_tt'),
        default=True, update=update_tree)

    first_run : BoolProperty(
        name='first_run', description='hidden',
        default=True, update=do_not_update_tree)

    @classmethod
    def poll(cls, context):
        """ Check if in object mode. If not, the add object menu entry is greyed out. """

        return context.mode == 'OBJECT'

    def invoke(self, context, event):
        """ Called once when starting The Grove.
            Load the first preset, get the cursor location, check if there are empties selected and
            make sure that the environment and twig objects selected on a previous run of The Grove
            still exist. """

        # Initialize.
        if context.scene.unit_settings.system == 'NONE':
            if context.preferences.addons[__package__].preferences.set_scene_units:
                context.scene.unit_settings.system = 'METRIC'

        for me in bpy.data.meshes:
            if not me.users:
                if 'the_grove' in me:
                    print(t('clean_old_data') + str(me.name))
                    bpy.data.meshes.remove(me)

        bpy.ops.ed.undo_push(message='The Grove - Set Units and remove old data.')

        if self.first_run:
            # Try setting preset, perhaps it does not exist.
            try:
                self.presets_menu = 'Ash'
            except:
                pass
        self.preset_name = self.presets_menu
        self.remove_preset = False
        self.replace_preset = False
        self.first_run = False

        self.cursor_location = context.scene.cursor.location
        print("")
        print("The Grove")

        # Save selected Empty objects.
        self.empties = []
        self.empties_presets = []
        for ob in bpy.context.selected_objects:
            if ob.type == 'EMPTY':
                print(t('found_an_empty_message') + ob.name)
                self.empties.append(ob.name)

                if "the_grove_preset" in ob:
                    self.empties_presets.append(ob["the_grove_preset"])
                    print(self.empties_presets)

        self.check_environment(context)

        check_twigs(self, context)

        restart(self)  # TODO: Check if still necessary?

        if context.scene.unit_settings.system == 'NONE':
            if context.preferences.addons[__package__].preferences.set_scene_units:
                context.scene.unit_settings.system = 'METRIC'
                print(t('set_units_message'))

        if context.preferences.edit.use_global_undo is False or context.preferences.edit.undo_steps < 8:
            self.display_undo_warning = True

        self.do_update = True
        self.execute(context)

        return {'FINISHED'}

    def execute(self, context):
        """ This code handles UI input. It is called every time a parameter is changed
            or a button is clicked. """

        if not (self.do_update or
                self.do_read_preset or
                self.add_preset or
                self.play_stop or
                self.remove_preset_cancel or
                self.remove_preset_confirm or
                self.rename_preset or
                self.replace_preset_cancel or
                self.replace_preset_confirm or
                self.zoom or
                self.calculate_wind or
                self.configure_textures_path or
                self.smooth):
            return {'PASS_THROUGH'}

        print("")

        self.display_empty_twig_warning = False
        if self.twigs_menu != t('pick_objects') and self.twigs_menu != t('configure_twigs_path'):
            append_twigs(self, context)

            # Not pick_objects and not no_twigs, so the appended twig should have filled in the apical twig.
            if self.apical_twig == "" and self.twigs_menu != t('no_twigs'):
                self.display_empty_twig_warning = True

        # Detect vanishing twigs that were appended manually while the Grove was already running.
        check_twigs(self, context, check_vanishing=True)

        if self.twigs_menu == t('configure_twigs_path'):
            invoke_user_preferences()
            self.twigs_menu = t('pick_objects')

        if self.configure_textures_path:
            invoke_user_preferences()
            self.configure_textures_path = False

        if self.zoom:
            zoom(self, context)
            self.zoom = False
            return {'PASS_THROUGH'}

        if self.do_read_preset:
            if not self.do_not_read_preset:
                name = self.presets_menu
                print(t('read_preset_message') + name)
                read_preset(name, self)
                self.preset_name = name
                self.do_read_preset = False

        if self.replace_preset:
            if self.replace_preset_confirm:
                self.do_not_read_preset = True
                self.replace_preset_confirm = False
                self.replace_preset = False
                self.remove_preset = False
                print(t('replace_preset_message') + self.preset_name)
                if self.preset_name != "":
                    write_preset(self.preset_name, self)
                    return {'PASS_THROUGH'}

            if self.replace_preset_cancel:
                self.replace_preset_cancel = False
                self.replace_preset = False
                return {'PASS_THROUGH'}

        if self.add_preset:
            self.add_preset = False
            self.remove_preset = False
            self.do_not_read_preset = True
            print(t('add_preset_message') + self.preset_name)
            if self.preset_name != "":
                write_preset(self.preset_name, self)
                return {'PASS_THROUGH'}

        if self.remove_preset_cancel:
            self.remove_preset_cancel = False
            self.remove_preset = False
            return {'PASS_THROUGH'}

        if self.remove_preset_confirm:
            name = self.presets_menu
            self.remove_preset_confirm = False
            self.remove_preset = False
            print(t("Remove Preset - ") + name)
            remove_preset(name, self)
            self.execute(context)
            return {'PASS_THROUGH'}

        if self.rename_preset:
            old_name = self.presets_menu
            print(t('rename_preset_message').format(old_name, self.preset_name))
            rename_preset(old_name, self.preset_name, self)
            self.do_read_preset = False
            self.remove_preset = False
            self.rename_preset = False
            self.replace_preset = False
            return {'PASS_THROUGH'}

        if self.play_stop:
            bpy.ops.screen.animation_play()
            self.play_stop = False
            return {'PASS_THROUGH'}

        if self.do_update:
            # When performing a different action, cancel the remove or replace preset action.
            self.remove_preset = False
            self.replace_preset = False

            self.display_prune_warning = False
            self.display_vertex_colors_warning = False
            self.display_vanishing_twig_warning = False

            if self.restart:
                print('The Grove - ' + t('restart'))
                restart(self)
                self.age = 0
                self.restart = False
                self.display_scale_to_twig_warning = False

            if self.do_change_number_of_trees:
                print('The Grove - ' + t('restart_message').format(self.number_of_trees))
                if self.age == 0:
                    restart(self)
                self.do_change_number_of_trees = False

            elif self.manual_prune:
                print('The Grove - ' + t('manual_prune'))
                if self.strokes:
                    manual_prune(self, context.region_data, False)
                    self.manual_prune = False
                else:
                    self.display_prune_warning = True
                    self.manual_prune = False
                    return {'PASS_THROUGH'}

            elif self.shape:
                print('The Grove - ' + t('shape'))
                if self.strokes:
                    manual_prune(self, context.region_data, True)
                    self.shape = False
                else:
                    self.display_prune_warning = True
                    self.shape = False
                    return {'PASS_THROUGH'}

            elif self.smooth:
                print('The Grove - ' + t('smooth_branches_message'))
                smooth_kinks(self)
                self.smooth = False

            elif self.manual_grow:
                print("The Grove - Manual Grow")
                if self.strokes:
                    manual_grow(self, context, context.region_data)
                else:
                    self.display_prune_warning = True
                self.manual_grow = False

            elif self.simulate:
                print("\n\n\n")
                print('The Grove - ' + t('Simulate'))
                print("")
                simulate(self, context)
                print("")

            # Update thicknesses and bend accordingly.
            if not self.simulate:
                for trunk in self.trunks:
                    print(t('Thicken'))
                    exponent = self.join_branches * -2 + 4
                    trunk.thicken(exponent, self.internode_gain, self.tip_decrease)
                    trunk.make_data_relative_to_root(trunk.nodes[0].thickness, trunk.nodes[0].photosynthesis)
                    trunk.weigh(self.leaf_weight, self.lateral_twig_chance, self.lateral_twig_limit,
                                self.branch_weight)

                    print(t('Bend'))
                    parent_diff = -trunk.nodes[0].direction.rotation_difference(trunk.nodes[0].direction)
                    trunk.bend(trunk.nodes[0].pos, parent_diff, self.fatigue)

        self.tree_has_animation = False
        if self.calculate_wind:
            prev_build_type = self.build_type
            self.build_type = '4'

        if self.build_type == '2':
            if self.age == 0 and not self.empties:
                build_placeholders(self, context)
            else:
                build_branches_mesh(self, context)
        elif self.build_type == '4':
            build_branches_mesh(self, context)
            # Set frame to force update of wind shape keys.
            context.scene.frame_set(1)

        if self.calculate_wind:
            self.build_type = prev_build_type
            self.calculate_wind = False
            if not context.screen.is_animation_playing:
                bpy.ops.screen.animation_play()
            self.play_stop = False
            self.tree_has_animation = True

        if self.show_shade_preview:
            shade_preview(self, context)

        self.height = self.trunks[0].find_highest_point(0.0)

        self.simulate = False
        self.do_update = False
        self.do_update_only_twigs = False

        print('\n' + t('done_message'))

        return {'FINISHED'}

    def catch_grease_pencil_strokes(self, context):
        """ Manual Prune. Get grease pencil data for pruning and perhaps guiding.
            The strokes are fleeting things, we need to catch them before the implicit undo erases them.
            The * 1.0 copies the coordinates, necessary because the implicit undo clears the memory
            and makes the pointers unreliable. """

        self.strokes = []
        scene = context.scene
        if scene.grease_pencil and scene.grease_pencil.layers and scene.grease_pencil.layers[-1].active_frame:
            for stroke in scene.grease_pencil.layers[-1].active_frame.strokes:
                if len(stroke.points) < 2:
                    continue
                for i, point in enumerate(stroke.points[:-1]):
                    self.strokes.append([stroke.points[i].co * 1.0, stroke.points[i + 1].co * 1.0])

    def draw_actions(self, box):
        """ Actions. """

        split_zoom_simulate = box.split(factor=0.33, align=True)
        row = split_zoom_simulate.row(align=True)
        row.scale_y = 1.7
        row.prop(self, "zoom", icon_value=icons["IconZoom"].icon_id)
        row = split_zoom_simulate.row(align=True)
        row.scale_y = 1.7
        row.prop(self, "simulate", icon_value=icons["IconGrow"].icon_id)

        row = box.row(align=True)
        row.scale_y = 1.7
        row.prop(self, "restart", icon_value=icons["IconRestart"].icon_id)
        row.prop(self, "shape", icon_value=icons["IconShape"].icon_id)
        row.prop(self, "manual_prune", icon_value=icons["IconPrune"].icon_id)

    def draw_panel_simulate(self, layout, context):
        """ Add the Grove buttons to the interface. """

        box = layout.box()

        header_split = box.split(factor=0.88)
        header_split.label(text=t("Simulate"))
        box.separator()

        row = box.row(align=True)
        row.scale_y = 1.3
        row.prop(self, 'scale_to_twig')

        if len(self.empties):
            box.label(text=t('growing_from_empties_info'), icon='INFO')
        row = box.column(align=True)
        if self.number_of_trees > 1:
            row.scale_y = 1.3
        if len(self.empties):
            row.enabled = False
        row.prop(self, "number_of_trees")
        if self.number_of_trees > 1:
            row.prop(self, "tree_space")

        row = box.row(align=True)
        row.prop(self, "grow_years")

        if self.grow_years > 15:
            box.label(text=t('time_info'), icon='TIME')
            box.separator()

        self.draw_actions(box)

        self.draw_info(context, box)
        box.separator()

    def draw_info(self, context, box):
        """ Draw the info box to the interface.
            The info box displays tips to get started, shows warnings about failed actions and
            displays info on your tree in different languages. """

        box.separator()

        if self.display_prune_warning:
            box.label(text=t('grease_pencil_info'), icon='ERROR')

        elif self.display_scale_to_twig_warning and (len(self.trunks) > 1 or len(self.empties) > 0):
                # Only display the warning when growing from an empty or growing multiple trees together.
                box.label(text=t('scale_to_twig_warning'), icon='ERROR')

        elif self.number_of_trees != len(self.trunks):
            if len(self.empties) != len(self.trunks):
                box.label(text=t('restart_info'), icon='ERROR')

        elif self.number_of_branches == self.number_of_trees:
            box.label(text=t('get_started_info'), icon='INFO')

        elif len(self.trunks) == 1:
            if context.scene.unit_settings.system == 'IMPERIAL':
                box.label(text=t('your_tree_is_info_feet').format(self.age, self.height * self.scale_to_twig / 0.3048,
                                                             self.number_of_branches))
            else:
                box.label(text=t('your_tree_is_info').format(self.age, self.height * self.scale_to_twig,
                                                        self.number_of_branches))
        else:
            if context.scene.unit_settings.system == 'IMPERIAL':
                box.label(text=t('your_trees_are_info_feet').format(self.age, self.height * self.scale_to_twig / 0.3048,
                                                               self.number_of_branches))
            else:
                box.label(text=t('your_trees_are_info').format(self.age, self.height * self.scale_to_twig,
                                                          self.number_of_branches))

    def draw_panel_preset(self, layout, context):
        """ Draw presets panel. """

        box = layout.box()

        header_split = box.split(factor=0.88, align=True)
        header_split.label(text=t("Presets"))
        header_split.prop(self, "advanced_ui_presets", icon_value=icons["IconAdvanced"].icon_id)
        box.separator()

        row = box.row(align=False)
        row.scale_y = 1.0
        row.prop(self, "presets_menu")

        if self.advanced_ui_presets:
            box.prop(self, "preset_name")

            new_name_exists = exists(join(presets_path(), self.preset_name + ".seed"))

            row = box.row(align=True)
            row.scale_y = 1.4
            row.prop(self, "remove_preset", icon_value=icons["IconRemove"].icon_id)
            col = row.column(align=True)
            col.scale_y = 1.4

            if self.presets_menu == self.preset_name or new_name_exists:
                col.enabled = False
            col.prop(self, "rename_preset", icon_value=icons["IconRename"].icon_id)
            if new_name_exists:
                row.prop(self, "replace_preset", icon_value=icons["IconAdd"].icon_id)
            else:
                row.prop(self, "add_preset", icon_value=icons["IconAdd"].icon_id)

            if self.remove_preset:
                box.label(text=t('remove_preset_info').format(self.presets_menu), icon='ERROR')
                row = box.row(align=True)
                row.scale_y = 1.3
                row.prop(self, "remove_preset_cancel", icon_value=icons["IconStop"].icon_id)
                row.prop(self, "remove_preset_confirm", icon_value=icons["IconPlay"].icon_id)

            if self.replace_preset:
                box.label(text=t('overwrite_preset_info').format(self.preset_name), icon='ERROR')
                row = box.row(align=True)
                row.scale_y = 1.3
                row.prop(self, "replace_preset_cancel", icon_value=icons["IconStop"].icon_id)
                row.prop(self, "replace_preset_confirm", icon_value=icons["IconPlay"].icon_id)

        else:
            box.separator()

    def draw_panel_favor(self, layout):
        """ Draw Favor panel. """

        box = layout.box()
        header_split = box.split(factor=0.88)
        header_split.label(text=t("Flow"))
        box.separator()

        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "favor_healthy")
        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "favor_rising")

        col = box.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.6
        row.prop(self, "favor_current")
        row.prop(self, "shade_avoidance")
        row = col.row(align=True)
        row.prop(self, "favor_current_reach")
        box.separator()
        box.prop(self, "branching_inefficiency")

        box.separator()

    def draw_panel_drop(self, layout):
        """ Draw Drop panel. """

        box = layout.box()
        header_split = box.split(factor=0.88)
        header_split.label(text=t("Drop"))
        header_split.prop(self, "advanced_ui_drop", icon_value=icons["IconAdvanced"].icon_id)
        box.separator()

        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "drop_low")
        row.prop(self, "keep_thick")

        box.prop(self, "drop_shaded")
        box.prop(self, "drop_relatively_weak")
        box.prop(self, "flower_power")

        box.separator()
        row = box.split(factor=0.9, align=True)
        row.scale_y = 1.2
        row.prop(self, "keep_dead")
        if not self.show_dead_preview:
            row.prop(self, "show_dead_preview", icon='RESTRICT_VIEW_ON')
        else:
            row.prop(self, "show_dead_preview", icon='RESTRICT_VIEW_OFF')

        if self.advanced_ui_drop:
            box.prop(self, "apical_bud_fatality")

        box.separator()

    def draw_panel_add(self, layout):
        """ Draw Add panel. """

        box = layout.box()
        header_split = box.split(factor=0.88)
        header_split.label(text=t("Add"))
        header_split.prop(self, "advanced_ui_add", icon_value=icons["IconAdvanced"].icon_id)
        box.separator()

        box.prop(self, "branching")
        box.separator()
        if self.advanced_ui_add:
            box.prop(self, "bud_life")

        col = box.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "branch_chance")
        row.prop(self, "branch_chance_light_required")
        row = col.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "branch_chance_only_terminal")

        row = box.row(align=True)
        row.prop(self, "regenerative_branch_chance")
        row.prop(self, "regenerative_branch_chance_light_required")

        box.separator()
        box.label(text='Direction:')
        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "branch_angle")
        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "plagiotropism_buds")
        row = box.row(align=True)
        row.prop(self, "gravitropism_buds")
        row.prop(self, "gravitropism_buds_randomness")


        box.separator()

    def draw_panel_turn(self, layout):
        """ Draw Turn panel. """

        box = layout.box()
        header_split = box.split(factor=0.88)
        header_split.label(text=t("Turn"))

        box.separator()
        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "gravitropism")
        row.prop(self, "gravitropism_shade")
        row = box.row(align=True)
        row.prop(self, "plagiotropism")
        row.prop(self, "phototropism")
        box.prop(self, "twist")
        split = box.split(factor=0.2)
        split.label(text='Random:')
        row = split.row(align=True)
        row.prop(self, "random_pitch")
        row.prop(self, "random_heading")

        box.separator()

    def draw_panel_grow(self, layout):
        """ Draw Grow panel. """

        box = layout.box()
        box.label(text=t("Grow"))
        box.separator()

        row = box.row(align=True)
        row.prop(self, "grow_length")
        row.prop(self, "grow_nodes")
        box.prop(self, "shade_elongation")

        box.separator()

    def draw_panel_interact(self, context, layout):
        """ Draw Interact panel. """

        box = layout.box()
        box.label(text=t("Interact"))
        box.separator()

        box.prop(self, "force")
        if self.force != "6":
            box.prop_search(self, "environment_name", context.scene, "objects")
            if self.force != "1" and self.force != "7":
                row = box.row(align=True)
                row.prop(self, "force_power")
                row.prop(self, "force_radius")

        box.separator()

    def draw_panel_thicken(self, layout):
        """ Draw Thicken panel. """

        box = layout.box()
        header_split = box.split(factor=0.88)
        header_split.label(text=t("Thicken"))
        header_split.prop(self, "advanced_ui_thicken", icon_value=icons["IconAdvanced"].icon_id)
        box.separator()

        row = box.row(align=True)
        row.prop(self, "tip_thickness")
        row.prop(self, "tip_decrease")
        if self.advanced_ui_thicken:
            box.prop(self, "internode_gain")

        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "join_branches")

        if self.advanced_ui_thicken:
            box.separator()
            row = box.row(align=True)
            row.prop(self, "root_scale")
            row.prop(self, "root_shape")
            if self.build_type == '2' or self.build_type == '4':
                box.prop(self, "root_bump")

        box.separator()

    def draw_panel_bend(self, layout):
        """ Draw Bend panel. """

        box = layout.box()
        box.label(text=t("Bend"))
        box.separator()

        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "branch_weight")
        row.prop(self, "leaf_weight")
        row = box.row(align=True)
        row.prop(self, "bake_bend")
        row.prop(self, "fatigue")

        box.separator()

    def draw_panel_shade(self, layout):
        """ Draw Shade panel. """

        box = layout.box()
        header_split = box.split(factor=0.88)
        header_split.label(text=t("Shade"))
        header_split.prop(self, "advanced_ui_shade", icon_value=icons["IconAdvanced"].icon_id)
        box.separator()

        if self.advanced_ui_shade:
            box.separator()
            row = box.split(factor=0.5, align=True)
            row.prop(self, "shade_leaf_area")
            row = row.split(factor=0.8, align=True)
            row.prop(self, "shade_samples")
            if not self.show_shade_preview:
                row.prop(self, "show_shade_preview", icon='RESTRICT_VIEW_ON')
            else:
                row.prop(self, "show_shade_preview", icon='RESTRICT_VIEW_OFF')
        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "shade_sensitivity")

        box.separator()

    def draw_panel_repeat(self, context, layout):
        """ Add the action buttons to the interface. """

        box = layout.box()

        header_split = box.split(factor=0.88)
        header_split.label(text=t("Repeat"))
        box.separator()

        self.draw_actions(box)

        split = box.split(factor=0.33, align=True)
        row = split.row(align=True)
        row.scale_y = 1.7
        row.prop(self, "smooth", icon_value=icons["IconSmooth"].icon_id)
        row = split.row(align=True)
        row.scale_y = 1.7
        row.prop(self, "calculate_wind", icon_value=icons["IconAnimate"].icon_id)

        self.draw_info(context, box)

        box.separator()

    def draw_panel_animate(self, context, layout):
        """ Draw wind panel. """

        box = layout.box()
        header_split = box.split(factor=0.88)
        header_split.label(text=t("Animate"))
        box.separator()

        row = box.split(factor=0.0, align=True)
        row.scale_y = 1.4
        row.prop(self, "wind_direction_w", icon_value=icons["IconWindDirectionWest"].icon_id)
        row.prop(self, "wind_direction_n", icon_value=icons["IconWindDirectionNorth"].icon_id)
        row.prop(self, "wind_direction_e", icon_value=icons["IconWindDirectionEast"].icon_id)
        row.prop(self, "wind_direction_s", icon_value=icons["IconWindDirectionSouth"].icon_id)

        row = box.row(align=True)
        row.scale_y = 1.4
        row.prop(self, "wind_force")
        row.prop(self, "turbulence")

        box.prop(self, "wind_shapes")

        row = box.row(align=True)
        row.scale_y = 1.7
        row.prop(self, "calculate_wind", icon_value=icons["IconAnimate"].icon_id)

        if self.tree_has_animation:
            box.separator()
            box.label(text=t('wind_loop_info').format(self.wind_shapes, self.wind_shapes * 10), icon='INFO')
        box.separator()

    def draw_panel_twigs(self, context, layout):
        """ Twigs panel. """

        box = layout.box()
        box.label(text=t("Twigs"))
        box.separator()

        if self.advanced_ui_build:
            box.separator()

        if self.display_vanishing_twig_warning:
            box.label(text=t('twig_vanished_info'), icon='ERROR')

        if self.twigs_menu == t('no_twigs'):
            box.prop(self, "twigs_menu")
        else:
            row = box.row(align=False)
            row.scale_y = 1.3
            row.prop(self, "twigs_menu")

            if self.display_empty_twig_warning:
                row = box.row(align=False)
                row.scale_y = 1.4
                row.label(text=t('empty_twig_warning'), icon='ERROR')

        if self.twigs_menu != t('no_twigs'):
            if self.twigs_menu != t('pick_objects'):
                row = box.row(align=False)
                row.enabled = False
                row.prop_search(self, "apical_twig", context.scene, "objects", icon='MESH_CUBE')
                row = box.row(align=False)
                row.enabled = False
                row.prop_search(self, "lateral_twig", context.scene, "objects", icon='MESH_CUBE')
            else:
                box.prop_search(self, "apical_twig", context.scene, "objects", icon='MESH_CUBE')
                box.prop_search(self, "lateral_twig", context.scene, "objects", icon='MESH_CUBE')

            if self.lateral_twig != "":
                row = box.row(align=True)
                row.scale_y = 1.4
                row.prop(self, "lateral_twig_chance")
                row.prop(self, "lateral_twig_limit")

            if self.lateral_twig != "" or self.apical_twig != "":
                row = box.row(align=True)
                row.prop(self, "twig_viewport_detail")

        box.separator()

    def draw_panel_build(self, context, layout):
        """ Draw Build panel. """

        box = layout.box()
        header_split = box.split(factor=0.88)
        header_split.label(text=t("Build"))
        box.separator()

        if self.build_type == '2' or self.build_type == '4':
            row = box.row(align=True)
            row.scale_y = 1.4
            row.prop(self, "profile_resolution")
            row.prop(self, "profile_resolution_reduction")

        if self.build_type == '2' or self.build_type == '4':
            row = box.row()
            row.scale_y = 1.4
            if self.number_of_branches == 1:
                row.label(text=t('branch_has_polygons_info').format(self.number_of_branches, self.number_of_polygons))
            else:
                row.label(text=t('branches_have_polygons_info').format(self.number_of_branches, self.number_of_polygons))

        box.separator()
        if self.build_type in ['2', '3', '4']:
            if len(self.textures_menu):
                box.prop(self, "textures_menu")
            else:
                box.prop(self, "configure_textures_path", icon="INFO")
            row = box.row(align=True)
            row.scale_y = 1.4
            row.prop(self, "u_repeat")

        if self.build_type == '4':
            row = box.split(factor=0.0, align=True)
            row.scale_y = 1.4
            row.prop(self, "wind_direction_w", icon_value=icons["IconWindDirectionWest"].icon_id)
            row.prop(self, "wind_direction_n", icon_value=icons["IconWindDirectionNorth"].icon_id)
            row.prop(self, "wind_direction_e", icon_value=icons["IconWindDirectionEast"].icon_id)
            row.prop(self, "wind_direction_s", icon_value=icons["IconWindDirectionSouth"].icon_id)

            row = box.row(align=True)
            row.scale_y = 1.4
            row.prop(self, "wind_force")
            row.prop(self, "turbulence")

            wind_shapes_split = box.split(factor=0.75, align=True)
            wind_shapes_split.prop(self, "wind_shapes")
            if context.screen.is_animation_playing:
                wind_shapes_split.prop(self, "play_stop", icon_value=icons["IconStop"].icon_id)
            else:
                wind_shapes_split.prop(self, "play_stop", icon_value=icons["IconPlay"].icon_id)

            box.separator()
            box.label(text=t('wind_loop_info').format(self.wind_shapes, self.wind_shapes * 10), icon='INFO')

        box.separator()

        if self.build_type == '2' or self.build_type == '4':
            row = box.row()
            if self.build_type == "4":
                row.enabled = False
            row.label(text=t('label_layers') + ':')
            if self.display_vertex_colors_warning:
                box.label(text=t('vertex_color_limit_info'), icon='INFO')
                box.separator()
            row = box.row(align=False)
            row.enabled = False
            row.prop(self, "do_layer_apical")
            row.prop(self, "do_layer_lateral")
            row = box.row(align=False)
            row.prop(self, "do_layer_thickness")
            row.prop(self, "do_layer_dead")
            row = box.row(align=False)
            row.prop(self, "do_layer_shade")
            row.prop(self, "do_layer_pitch")
            row = box.row(align=False)
            row.prop(self, "do_layer_health")
            row.prop(self, "do_layer_power")
            box.separator()

    def draw(self, context):
        """ Draw user interface. """

        self.catch_grease_pencil_strokes(context)

        layout = self.layout

        if self.display_undo_warning:
            layout.separator()
            layout.label(text=t('undo_warning'), icon='ERROR')
            layout.separator()

        if self.empties_presets:
            layout.separator()
            layout.label(text=t('preset_empty_info'), icon='INFO')
            layout.separator()
            self.draw_panel_simulate(layout, context)
            self.draw_panel_interact(context, layout)
            self.draw_panel_build(context, layout)
            layout.separator()
            layout.separator()
            return

        self.draw_panel_preset(layout, context)
        self.draw_panel_twigs(context, layout)
        self.draw_panel_simulate(layout, context)
        self.draw_panel_favor(layout)
        self.draw_panel_drop(layout)
        self.draw_panel_add(layout)
        self.draw_panel_grow(layout)
        self.draw_panel_turn(layout)
        self.draw_panel_thicken(layout)
        self.draw_panel_bend(layout)
        self.draw_panel_shade(layout)
        self.draw_panel_interact(context, layout)
        self.draw_panel_build(context, layout)
        self.draw_panel_animate(context, layout)

        layout.separator()
        layout.separator()


def register():
    bpy.utils.register_class(TheGrove6)



def unregister():
    bpy.utils.unregister_class(TheGrove6)
