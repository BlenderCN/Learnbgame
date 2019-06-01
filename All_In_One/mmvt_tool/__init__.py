bl_info = {
    "name": "Multi-modal visualization tool",
    "author": "Ohad Felsenstein & Noam Peled",
    "version": (1, 2),
    "blender": (2, 7, 2),
    "api": 33333,
    "location": "View3D > Add > Mesh > Say3D",
    "description": "Multi-modal visualization tool",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
import os
import os.path as op
import sys
import importlib
import traceback
import logging
import atexit
import time
import warnings
# Warning: this is dangerous!
warnings.filterwarnings("ignore")

import mmvt_utils
importlib.reload(mmvt_utils)
import colors_utils
importlib.reload(colors_utils)
import show_hide_panel
importlib.reload(show_hide_panel)
import transparency_panel
importlib.reload(transparency_panel)
import coloring_panel
importlib.reload(coloring_panel)
import connections_panel
importlib.reload(connections_panel)
import play_panel
importlib.reload(play_panel)
import dti_panel
importlib.reload(dti_panel)
import electrodes_panel
importlib.reload(electrodes_panel)
import freeview_panel
importlib.reload(freeview_panel)
import search_panel
importlib.reload(search_panel)
import appearance_panel
importlib.reload(appearance_panel)
import where_am_i_panel
importlib.reload(where_am_i_panel)
import fMRI_panel
importlib.reload(fMRI_panel)
import meg_panel
importlib.reload(meg_panel)
import render_panel
importlib.reload(render_panel)
import listener_panel
importlib.reload(listener_panel)
import data_panel
importlib.reload(data_panel)
import selection_panel
importlib.reload(selection_panel)
import vertex_data_panel
importlib.reload(vertex_data_panel)
import filter_panel
importlib.reload(filter_panel)
import stim_panel
importlib.reload(stim_panel)
import streaming_panel
importlib.reload(streaming_panel)
import colorbar_panel
importlib.reload(colorbar_panel)
# import load_results_panel
# importlib.reload(load_results_panel)
import pizco_panel
importlib.reload(pizco_panel)
import load_results_panel
importlib.reload(load_results_panel)
import list_panel
importlib.reload(list_panel)
import slicer_panel
importlib.reload(slicer_panel)
import skull_panel
importlib.reload(skull_panel)
# import dell_panel
# importlib.reload(dell_panel)
import reports_panel
importlib.reload(reports_panel)
import labels_panel
importlib.reload(labels_panel)
import scripts_panel
importlib.reload(scripts_panel)
# import three_d_view_panel
# importlib.reload(three_d_view_panel)
# import moshes_panel
# importlib.reload(moshes_panel)
# import logo_panel
# importlib.reload(logo_panel)


print("mmvt addon started!")
# todo: should change that in the code!!!
# Should be here bpy.types.Scene.maximal_time_steps
# T = 2500
# bpy.types.Scene.maximal_time_steps = T

# LAYERS
(TARGET_LAYER, LIGHTS_LAYER, EMPTY_LAYER, BRAIN_EMPTY_LAYER, ROIS_LAYER, ACTIVITY_LAYER, INFLATED_ROIS_LAYER,
 INFLATED_ACTIVITY_LAYER, ELECTRODES_LAYER, CONNECTIONS_LAYER, EEG_LAYER, MEG_LAYER, SKULL_LAYER) = range(13)

(WIC_MEG, WIC_MEG_LABELS, WIC_FMRI, WIC_FMRI_DYNAMICS, WIC_FMRI_LABELS, WIC_FMRI_CLUSTERS, WIC_EEG, WIC_MEG_SENSORS,
WIC_ELECTRODES, WIC_ELECTRODES_DISTS, WIC_ELECTRODES_SOURCES, WIC_ELECTRODES_STIM, WIC_MANUALLY, WIC_GROUPS, WIC_VOLUMES,
 WIC_CONN_LABELS_AVG, WIC_CONTOURS, WIC_LABELS_DATA) = range(18)

bpy.types.Scene.python_cmd = bpy.props.StringProperty(name='python cmd', default='python')
bpy.types.Scene.mmvt_initialized = bpy.props.BoolProperty(default=False)
settings = None

bpy.types.Scene.view_rotations_x = bpy.props.FloatProperty()
bpy.types.Scene.view_rotations_y = bpy.props.FloatProperty()
bpy.types.Scene.view_rotations_z = bpy.props.FloatProperty()

electrodes_panel_parent = electrodes_panel.PARENT_OBJ_NAME
electrodes_panel_parent_obj = bpy.data.objects.get(electrodes_panel_parent, None)
meg_panel_parent = meg_panel.PARENT_OBJ_NAME
ANGLES_DICT = show_hide_panel.ANGLES_DICT
ANGLES_NAMES_DICT = show_hide_panel.ANGLES_NAMES_DICT
# Remove double definition (also in show_hide_panel)
(ROT_SAGITTAL_LEFT, ROT_SAGITTAL_RIGHT, ROT_CORONAL_ANTERIOR, ROT_CORONAL_POSTERIOR, ROT_AXIAL_SUPERIOR,
 ROT_AXIAL_INFERIOR, ROT_MEDIAL_LEFT, ROT_MEDIAL_RIGHT) = range(8)

utils = mmvt_utils
colors = colors_utils
scene = bpy.context.scene
tmp = mmvt_utils.get_3d_spaces(only_neuro=True)
view_region = tmp.__next__().region_3d
q=view_region.view_rotation.to_euler()
bpy.context.scene.view_rotations_x = view_region.view_rotation.to_euler()[0]
bpy.context.scene.view_rotations_y = view_region.view_rotation.to_euler()[1]
bpy.context.scene.view_rotations_z = view_region.view_rotation.to_euler()[2]



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Data links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
data = data_panel
import_brain = data_panel.import_brain
add_data_to_parent_obj = data_panel.add_data_to_parent_obj
add_data_to_brain = data_panel.add_data_to_brain
import_electrodes = data_panel.import_electrodes
eeg_data_and_meta = data_panel.eeg_data_and_meta
load_meg_labels_data = data_panel.load_meg_labels_data
load_electrodes_data = data_panel.load_electrodes_data
load_electrodes_dists = data_panel.load_electrodes_dists
import_meg_sensors = data_panel.import_meg_sensors
import_eeg_sensors = data_panel.import_eeg_sensors
add_data_to_meg_sensors = data_panel.add_data_to_meg_sensors
add_data_to_eeg_sensors = data_panel.add_data_to_eeg_sensors
add_fmri_dynamics_to_parent_obj = data_panel.add_fmri_dynamics_to_parent_obj
create_empty_if_doesnt_exists = data_panel.create_empty_if_doesnt_exists
get_electrodes_radius = data_panel.get_electrodes_radius
create_electrode = data_panel.create_electrode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Selection links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
selection = selection_panel
select_brain_objects = selection_panel.select_brain_objects
select_all_connections = selection_panel.select_all_connections
select_all_electrodes = selection_panel.select_all_electrodes
select_all_eeg_sensors = selection_panel.select_all_eeg_sensors
select_only_subcorticals = selection_panel.select_only_subcorticals
select_all_rois = selection_panel.select_all_rois
select_all_meg_sensors = selection_panel.select_all_meg_sensors
deselect_all = selection_panel.deselect_all
set_selection_type = selection_panel.set_selection_type
conditions_diff = selection_panel.conditions_diff
both_conditions = selection_panel.both_conditions
spec_condition = selection_panel.spec_condition
fit_selection = selection_panel.fit_selection
select_roi = selection_panel.select_roi
curves_sep_update = selection_panel.curves_sep_update
calc_best_curves_sep = selection_panel.calc_best_curves_sep
set_connection_files_exist = selection_panel.set_connection_files_exist
de_select_object = selection_panel.de_select_object
clear_labels_selection = selection_panel.clear_labels_selection
ClearSelection = selection_panel.ClearSelection
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Coloring links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
coloring = coloring_panel
set_current_time = coloring_panel.set_current_time
get_current_time = coloring_panel.get_current_time
object_coloring = coloring_panel.object_coloring
color_objects = coloring_panel.color_objects
get_obj_color = coloring_panel.get_obj_color
clear_subcortical_fmri_activity = coloring_panel.clear_subcortical_fmri_activity
clear_cortex = coloring_panel.clear_cortex
clear_object_vertex_colors = coloring_panel.clear_object_vertex_colors
color_objects_homogeneously = coloring_panel.color_objects_homogeneously
init_activity_map_coloring = coloring_panel.init_activity_map_coloring
load_faces_verts = coloring_panel.load_faces_verts
load_meg_subcortical_activity = coloring_panel.load_meg_subcortical_activity
activity_map_coloring = coloring_panel.activity_map_coloring
meg_labels_coloring = coloring_panel.meg_labels_coloring
labels_coloring_hemi = coloring_panel.labels_coloring_hemi
plot_activity = coloring_panel.plot_activity
fmri_subcortex_activity_color = coloring_panel.fmri_subcortex_activity_color
activity_map_obj_coloring = coloring_panel.activity_map_obj_coloring
color_manually = coloring_panel.color_manually
color_subcortical_region = coloring_panel.color_subcortical_region
clear_subcortical_regions = coloring_panel.clear_subcortical_regions
color_electrodes = coloring_panel.color_electrodes
color_electrodes_sources = coloring_panel.color_electrodes_sources
get_elecctrodes_sources = coloring_panel.get_elecctrodes_sources
clear_colors_from_parent_childrens = coloring_panel.clear_colors_from_parent_childrens
default_coloring = coloring_panel.default_coloring
get_fMRI_activity = coloring_panel.get_fMRI_activity
get_faces_verts = coloring_panel.get_faces_verts
clear_colors = coloring_panel.clear_colors
clear_and_recolor = coloring_panel.clear_and_recolor
set_lower_threshold = coloring_panel.set_lower_threshold
get_lower_threshold = coloring_panel.get_lower_threshold
create_inflated_curv_coloring = coloring_panel.create_inflated_curv_coloring
calc_colors = coloring_panel.calc_colors
init_meg_labels_coloring_type = coloring_panel.init_meg_labels_coloring_type
color_connections = coloring_panel.color_connections
plot_meg = coloring_panel.plot_meg
plot_stc_t = coloring_panel.plot_stc_t
plot_stc = coloring_panel.plot_stc
init_meg_activity_map = coloring_panel.init_meg_activity_map
# plot_label = coloring_panel.plot_label
plot_fmri_file = coloring_panel.plot_fmri_file
get_activity_values = coloring_panel.get_activity_values
get_vertex_value = coloring_panel.get_vertex_value
color_prev_colors = coloring_panel.color_prev_colors
get_prev_colors = coloring_panel.get_prev_colors
get_activity_colors = coloring_panel.get_activity_colors
recreate_coloring_layers = coloring_panel.recreate_coloring_layers
ClearColors = coloring_panel.ClearColors
what_is_colored = coloring_panel.what_is_colored
add_to_what_is_colored = coloring_panel.add_to_what_is_colored
set_use_abs_threshold = coloring_panel.set_use_abs_threshold
color_labels_data = coloring_panel.color_labels_data
color_hemi_data = coloring_panel.color_hemi_data
coloring_panel_initialized = coloring_panel.panel_initialized
get_no_plotting = coloring_panel.get_no_plotting
set_no_plotting = coloring_panel.set_no_plotting
plot_fmri = coloring_panel.plot_fmri
init_labels_colorbar = coloring_panel.init_labels_colorbar
get_meg_data_minmax = coloring_panel.get_meg_data_minmax
get_meg_files = coloring_panel.get_meg_files
set_meg_files = coloring_panel.set_meg_files
get_activity_types = coloring_panel.get_activity_types
add_activity_type = coloring_panel.add_activity_type
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Filtering links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
filter = filter_panel
find_obj_with_val = filter_panel.find_obj_with_val
filter_draw = filter_panel.filter_draw
clear_filtering = filter_panel.clear_filtering
de_select_electrode_and_sensor = filter_panel.de_select_electrode_and_sensor
filter_roi_func = filter_panel.filter_roi_func
filter_electrode_or_sensor = filter_panel.filter_electrode_or_sensor
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Rendering links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
render = render_panel
load_camera = render_panel.load_camera
grab_camera = render_panel.grab_camera
set_render_quality = render_panel.set_render_quality
set_render_output_path = render_panel.set_render_output_path
set_render_smooth_figure = render_panel.set_render_smooth_figure
render_image = render_panel.render_image
render_lateral_medial_split_brain = render_panel.render_lateral_medial_split_brain
render_in_queue = render_panel.render_in_queue
finish_rendering = render_panel.finish_rendering
update_camera_files = render_panel.update_camera_files
set_lighting = render_panel.set_lighting
get_rendering_in_the_background = render_panel.get_rendering_in_the_background
set_rendering_in_the_background = render_panel.set_rendering_in_the_background
init_rendering = render_panel.init_rendering
camera_mode = render_panel.camera_mode
save_image = render_panel.save_image
set_to_camera_view = render_panel.set_to_camera_view
exit_from_camera_view = render_panel.exit_from_camera_view
save_all_views = render_panel.save_all_views
get_output_path = render_panel.get_output_path
set_output_path = render_panel.set_output_path
get_output_type = render_panel.get_output_type
set_output_type = render_panel.set_output_type
get_figure_format = render_panel.get_figure_format
set_figure_format = render_panel.set_figure_format
get_full_output_fname = render_panel.get_full_output_fname
get_save_views_with_cb = render_panel.get_save_views_with_cb
save_views_with_cb = render_panel.save_views_with_cb
get_save_split_views = render_panel.get_save_split_views
set_save_split_views = render_panel.set_save_split_views
set_background_color_name = render_panel.set_background_color_name
set_background_color = render_panel.set_background_color
get_background_rgb_string = render_panel.get_background_rgb_string
get_resolution_percentage = render_panel.get_resolution_percentage
set_resolution_percentage = render_panel.set_resolution_percentage
get_view_distance = render_panel.get_view_distance
set_view_distance = render_panel.set_view_distance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Show Hide links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
show_hide = show_hide_panel
show_hide_hierarchy = show_hide_panel.show_hide_hierarchy
show_hide_hemi = show_hide_panel.show_hide_hemi
rotate_brain = show_hide_panel.rotate_brain
start_rotating = show_hide_panel.start_rotating
stop_rotating = show_hide_panel.stop_rotating
zoom = show_hide_panel.zoom
show_hide_sub_corticals = show_hide_panel.show_hide_sub_corticals
hide_subcorticals = show_hide_panel.hide_subcorticals
show_subcorticals = show_hide_panel.show_subcorticals
show_sagital = show_hide_panel.show_sagital
show_coronal = show_hide_panel.show_coronal
show_axial = show_hide_panel.show_axial
split_view = show_hide_panel.split_view
view_all = show_hide_panel.view_all
rotate_view = show_hide_panel.rotate_view
view_name = show_hide_panel.view_name
show_hemis = show_hide_panel.show_hemis
hide_hemis = show_hide_panel.hide_hemis
show_head = show_hide_panel.show_head
hide_head = show_hide_panel.hide_head
set_normal_view = show_hide_panel.set_normal_view
hide_hemi = show_hide_panel.hide_hemi
show_hemi = show_hide_panel.show_hemi
hide_cerebellum = show_hide_panel.hide_cerebellum
show_cerebellum = show_hide_panel.show_cerebellum
subcorticals_are_hiding = show_hide_panel.subcorticals_are_hiding
show_meg_sensors = appearance_panel.show_meg_sensors
hide_meg_sensors = appearance_panel.hide_meg_sensors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Appearance links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
appearance = appearance_panel
setup_layers = appearance_panel.setup_layers
change_view3d = appearance_panel.change_view3d
show_rois = appearance_panel.show_rois
show_activity = appearance_panel.show_activity
show_electrodes = appearance_panel.show_electrodes
show_hide_electrodes = appearance_panel.show_electrodes
show_hide_eeg_sensors = appearance_panel.show_hide_eeg_sensors
show_hide_meg_sensors = appearance_panel.show_hide_meg_sensors
show_hide_connections = appearance_panel.show_hide_connections
change_to_rendered_brain = appearance_panel.change_to_rendered_brain
change_to_solid_brain = appearance_panel.change_to_solid_brain
make_brain_solid_or_transparent = appearance_panel.make_brain_solid_or_transparent
set_layers_depth_trans = appearance_panel.set_layers_depth_trans
update_solidity = appearance_panel.update_solidity
connections_visible = appearance_panel.connections_visible
show_hide_connections = appearance_panel.show_hide_connections
show_pial = appearance_panel.show_pial
show_inflated = appearance_panel.show_inflated
set_inflated_ratio = appearance_panel.set_inflated_ratio
get_inflated_ratio = appearance_panel.get_inflated_ratio
show_flat = appearance_panel.show_flat
is_pial = appearance_panel.is_pial
is_inflated = appearance_panel.is_inflated
is_activity = appearance_panel.is_activity
is_rois = appearance_panel.is_rois
is_solid = appearance_panel.is_solid
is_rendered = appearance_panel.is_rendered
set_closest_vertex_and_mesh_to_cursor = appearance_panel.set_closest_vertex_and_mesh_to_cursor
get_closest_vertex_and_mesh_to_cursor = appearance_panel.get_closest_vertex_and_mesh_to_cursor
clear_closet_vertex_and_mesh_to_cursor = appearance_panel.clear_closet_vertex_and_mesh_to_cursor
snap_cursor = appearance_panel.snap_cursor
cursor_is_snapped = appearance_panel.cursor_is_snapped
set_cursor_pos = appearance_panel.set_cursor_pos
flat_map_exists = appearance_panel.flat_map_exists
move_cursor_according_to_vert = appearance_panel.move_cursor_according_to_vert
set_panels_background_color = appearance_panel.set_panels_background_color
get_panels_background_color = appearance_panel.get_panels_background_color
set_transparency = appearance_panel.set_transparency
set_layers_depth_trans = appearance_panel.set_layers_depth_trans
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Play links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
play = play_panel
set_play_type = play_panel.set_play_type
set_play_from = play_panel.set_play_from
set_play_to = play_panel.set_play_to
set_play_dt = play_panel.set_play_dt
capture_graph = play_panel.capture_graph
render_movie = play_panel.render_movie
get_current_t = play_panel.get_current_t
set_current_t = play_panel.set_current_t
plot_something = play_panel.plot_something
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ electrodes links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
electrodes = electrodes_panel
color_the_relevant_lables = electrodes_panel.color_the_relevant_lables
get_leads = electrodes_panel.get_leads
get_lead_electrodes = electrodes_panel.get_lead_electrodes
set_current_electrode = electrodes_panel.set_current_electrode
set_electrodes_labeling_file = electrodes_panel.set_electrodes_labeling_file
set_show_only_lead = electrodes_panel.set_show_only_lead
is_current_electrode_marked = electrodes_panel.is_current_electrode_marked
get_electrodes_names = electrodes_panel.get_electrodes_names
electode_was_manually_selected = electrodes_panel.electode_was_manually_selected
clear_electrodes_selection = electrodes_panel.clear_electrodes_selection
init_electrodes_labeling = electrodes_panel.init_electrodes_labeling
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ colorbar links~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
colorbar = colorbar_panel
show_cb_in_render = colorbar_panel.show_cb_in_render
set_colorbar_max_min = colorbar_panel.set_colorbar_max_min
set_colorbar_min_max = colorbar_panel.set_colorbar_min_max
set_colorbar_max = colorbar_panel.set_colorbar_max
set_colorbar_min = colorbar_panel.set_colorbar_min
set_colorbar_title = colorbar_panel.set_colorbar_title
get_cm = colorbar_panel.get_cm
get_colorbar_max_min = colorbar_panel.get_colorbar_max_min
get_colorbar_max = colorbar_panel.get_colorbar_max
get_colorbar_min = colorbar_panel.get_colorbar_min
get_colorbar_title = colorbar_panel.get_colorbar_title
set_colormap = colorbar_panel.set_colormap
colorbar_values_are_locked = colorbar_panel.colorbar_values_are_locked
get_colormap = colorbar_panel.get_colormap
get_colorbar_figure_fname = colorbar_panel.get_colorbar_figure_fname
lock_colorbar_values = colorbar_panel.lock_colorbar_values
set_colorbar_prec = colorbar_panel.set_colorbar_prec
get_colorbar_prec = colorbar_panel.get_colorbar_prec
set_colorbar_defaults = colorbar_panel.set_colorbar_defaults
set_colorbar_default_cm = colorbar_panel.set_colorbar_default_cm
change_colorbar_default_cm = colorbar_panel.change_colorbar_default_cm
get_colorbar_ticks = colorbar_panel.get_colorbar_ticks
get_colorbar_ticks_num = colorbar_panel.get_colorbar_ticks_num
get_cb_ticks_num = colorbar_panel.get_cb_ticks_num
set_cb_ticks_num = colorbar_panel.set_cb_ticks_num
get_cb_ticks_font_size = colorbar_panel.get_cb_ticks_font_size
set_cb_ticks_font_size = colorbar_panel.set_cb_ticks_font_size
save_colorbar = colorbar_panel.save_colorbar
PERC_FORMATS = colorbar_panel.PERC_FORMATS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ fMRI links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
fmri = fMRI_panel
fMRI_clusters_files_exist = fMRI_panel.fMRI_clusters_files_exist
find_closest_cluster = fMRI_panel.find_closest_cluster
find_fmri_files_min_max = fMRI_panel.find_fmri_files_min_max
get_clusters_file_names = fMRI_panel.get_clusters_file_names
# get_clusters_files = fMRI_panel.get_clusters_files
plot_all_blobs = fMRI_panel.plot_all_blobs
load_fmri_cluster = fMRI_panel.load_fmri_cluster
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ connections links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
connections = connections_panel
connections_exist = connections_panel.connections_exist
get_connections_data = connections_panel.get_connections_data
plot_connections = connections_panel.plot_connections
vertices_selected = connections_panel.vertices_selected
create_connections = connections_panel.create_connections
filter_nodes = connections_panel.filter_nodes
get_connections_parent_name = connections_panel.get_connections_parent_name
select_connection = connections_panel.select_connection
get_connections_width = connections_panel.get_connections_width
set_connections_width = connections_panel.set_connections_width
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ transparency links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
transparency = transparency_panel
set_brain_transparency = transparency_panel.set_brain_transparency
set_light_layers_depth = transparency_panel.set_light_layers_depth
set_head_transparency = transparency_panel.set_head_transparency
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ where_am_i_panel links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
where_am_i = where_am_i_panel
set_mni = where_am_i_panel.set_mni
set_tkreg_ras = where_am_i_panel.set_tkreg_ras
set_voxel = where_am_i_panel.set_voxel
set_ct_coo = where_am_i_panel.set_ct_coo
find_closest_obj = where_am_i_panel.find_closest_obj
create_slices = where_am_i_panel.create_slices
slices_were_clicked = where_am_i_panel.slices_were_clicked
get_slices_cursor_pos = where_am_i_panel.get_slices_cursor_pos
set_slicer_state = where_am_i_panel.set_slicer_state
get_slicer_state = where_am_i_panel.get_slicer_state
set_ct_intensity = where_am_i_panel.set_ct_intensity
set_t1_value = where_am_i_panel.set_t1_value
set_t2_value = where_am_i_panel.set_t2_value
create_slices_from_vox_coordinates = where_am_i_panel.create_slices_from_vox_coordinates
find_closest_label = where_am_i_panel.find_closest_label
get_annot_files = where_am_i_panel.get_annot_files
calc_tkreg_ras_from_snapped_cursor = where_am_i_panel.calc_tkreg_ras_from_snapped_cursor
calc_tkreg_ras_from_cursor = where_am_i_panel.calc_tkreg_ras_from_cursor
get_tkreg_ras = where_am_i_panel.get_tkreg_ras
get_ras = where_am_i_panel.get_ras
get_T1_voxel = where_am_i_panel.get_T1_voxel
get_ct_voxel = where_am_i_panel.get_ct_voxel
get_labels_contours = where_am_i_panel.get_labels_contours
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ vertex_data_panel links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
vertex_data = vertex_data_panel
find_closest_vertex_index_and_mesh = vertex_data_panel.find_closest_vertex_index_and_mesh
set_vertex_data = vertex_data_panel.set_vertex_data
get_vertex_data = vertex_data_panel.get_vertex_data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ freeview_panel links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
freeview = freeview_panel
save_cursor_position = freeview_panel.save_cursor_position
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ slicer_panel links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
slicer = slicer_panel
clear_slice = slicer_panel.clear_slice
slice_brain = slicer_panel.slice_brain
ct_exist = slicer_panel.ct_exist
slices_zoom = slicer_panel.slices_zoom
get_slices_modality = slicer_panel.get_slices_modality
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ skull_panel links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
skull = skull_panel
find_point_thickness = skull_panel.find_point_thickness
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ meg_panel links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
meg = meg_panel
select_meg_cluster = meg_panel.select_meg_cluster
get_selected_clusters_data = meg_panel.get_selected_clusters_data

eeg_sensors_exist = meg_panel.eeg_sensors_exist
meg_sensors_exist = meg_panel.meg_sensors_exist

get_meg_sensors_data = meg_panel.get_meg_sensors_data
get_meg_sensors_file = meg_panel.get_meg_sensors_file
set_meg_sensors_file = meg_panel.set_meg_sensors_file
# get_meg_sensors_types = meg_panel.get_meg_sensors_types
# set_meg_sensors_types = meg_panel.set_meg_sensors_types
get_meg_sensors_conditions = meg_panel.get_meg_sensors_conditions
set_meg_sensors_conditions = meg_panel.set_meg_sensors_conditions

color_meg_sensors = meg_panel.color_meg_sensors

get_eeg_sensors_data = meg_panel.get_eeg_sensors_data
color_eeg_sensors = meg_panel.color_eeg_sensors

color_eeg_helmet = meg_panel.color_eeg_helmet
color_meg_helmet = meg_panel.color_meg_helmet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ dell_panel links ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# dell = dell_panel
# dell_ct_electrode_was_selected = dell_panel.dell_ct_electrode_was_selected
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ load_results panel ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
results = load_results_panel
load_surf_files = load_results_panel.load_surf_files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ labels_panel ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
labels = labels_panel
load_labels_data = labels_panel.load_labels_data
color_contours = labels_panel.color_contours
clear_contours = labels_panel.clear_contours
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ reports_panel ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
reports = reports_panel
set_report_name = reports_panel.set_report_name
get_report_name = reports_panel.get_report_name
get_report_files = reports_panel.get_report_files
get_report_fields = reports_panel.get_report_fields
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ scripts_panel ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
scripts = scripts_panel
get_scripts_names = scripts_panel.get_scripts_names
run_script = scripts_panel.run_script
set_script = scripts_panel.set_script
set_param = scripts_panel.set_param
get_param = scripts_panel.get_param


def get_max_time_steps(default_val=2500):
    # Check if there is animation data in MEG
    # try:
    #     return bpy.context.scene.maximal_time_steps
    # except:
    #     print('No preperty maximal_time_steps in bpy.types.Scene')
    found = False
    try:
        hemi = bpy.data.objects['Cortex-lh']
        # Takes the first child first condition fcurve
        fcurves = hemi.children[0].animation_data.action.fcurves[0]
        bpy.types.Scene.maximal_time_steps = len(fcurves.keyframe_points) - 3
        found = True
    except:
        print('No MEG data')

    if not found:
        try:
            fcurves = bpy.data.objects['fMRI'].animation_data.action.fcurves[0]
            bpy.types.Scene.maximal_time_steps = len(fcurves.keyframe_points) - 2
            found = True
        except:
            print('No dynamic fMRI data')

    if not found:
        try:
            parent_obj = bpy.data.objects['Deep_electrodes']
            if not parent_obj.animation_data is None:
                fcurves = parent_obj.animation_data.action.fcurves
            else:
                fcurves = parent_obj.children[1].animation_data.action.fcurves
            # else:
            #     fcurves = parent_obj.children[0].animation_data.action.fcurves[0]
            bpy.types.Scene.maximal_time_steps = len(fcurves[0].keyframe_points) - 2
            found = True
        except:
            print('No deep electrodes data')

    if not found:
        try:
            functional_maps = bpy.data.objects['Functional maps']
            for obj in functional_maps.children:
                if obj.name.startswith('connections') and obj.animation_data is not None:
                    fcurves = parent_obj.animation_data.action.fcurves
            bpy.types.Scene.maximal_time_steps = len(fcurves[0].keyframe_points)
            found = True
        except:
            pass
    try:
        if not found:
            bpy.types.Scene.maximal_time_steps = default_val
        print('max time steps: {}'.format(bpy.types.Scene.maximal_time_steps))
        return bpy.types.Scene.maximal_time_steps
    except:
        print('No property maximal_time_steps in bpy.types.Scene')
        return default_val


def get_max_t():
    return bpy.context.scene.maximal_time_steps


_listener_in_queue, _listener_out_queue = None, None


def start_listener():
    cmd = 'python {}'.format(op.join(mmvt_utils.current_path(), 'addon_listener.py'))
    listener_in_queue, listener_out_queue = mmvt_utils.run_command_in_new_thread(cmd)
    return listener_in_queue, listener_out_queue


# def init_pizco(mmvt):
#     try:
#         from pizco import Server
#         mmvt.c = mmvt_utils.get_graph_context()
#         mmvt.s = mmvt.c['scene']
#         Server(mmvt, 'tcp://127.0.0.1:8000')
#     except:
#         print('No pizco')


def make_all_fcurve_visible():
    for obj in bpy.data.objects:
        try:
            for cur_fcurve in obj.animation_data.action.fcurves:
                cur_fcurve.hide = False
        except:
            pass


def init(addon_prefs):
    global settings
    run_faulthandler()
    print('filepath: {}'.format(bpy.data.filepath))
    set_play_to(get_max_time_steps())
    mmvt_utils.view_all_in_graph_editor(bpy.context)
    bpy.context.window.screen = bpy.data.screens['Neuro']
    bpy.context.scene.atlas = mmvt_utils.get_atlas()
    bpy.context.scene.python_cmd = addon_prefs.python_cmd
    # bpy.data.screens['Neuro'].areas[1].spaces[0].region_3d.view_rotation = [1, 0, 0, 0]
    make_all_fcurve_visible()
    # set default values
    figures_fol = op.join(mmvt_utils.get_user_fol(), 'figures')
    mmvt_utils.make_dir(figures_fol)
    set_render_output_path(figures_fol)
    set_render_quality(60)
    mmvt_utils.set_show_textured_solid()
    mmvt_utils.hide_relationship_lines()
    code_fol = mmvt_utils.get_parent_fol(mmvt_utils.get_parent_fol())
    settings = mmvt_utils.read_config_ini()
    os.chdir(code_fol)
    bpy.context.scene.mmvt_initialized = True
    init_freesurfer_env()


def run_faulthandler():
    import faulthandler
    logs = op.join(mmvt_utils.get_user_fol(), 'logs')
    mmvt_utils.make_dir(logs)
    fault_handler = open(op.join(logs, 'faulthandler_{}.txt'.format(mmvt_utils.rand_letters(5))), 'w')
    faulthandler.enable(fault_handler)


@mmvt_utils.tryit()
def fix_scale():
    for hemi in mmvt_utils.HEMIS:
        hemi_obj = bpy.data.objects.get(hemi, None)
        if hemi_obj is not None:
            for i in range(3):
                hemi_obj.scale[i] = 0.1
        if bpy.data.objects.get('Cortex-{}'.format(hemi), None) is not None:
            for label_obj in bpy.data.objects['Cortex-{}'.format(hemi)].children:
                for i in range(3):
                    label_obj.scale[i] = 0.1
        if bpy.data.objects.get('Cortex-inflated-{}'.format(hemi), None) is not None:
            for label_obj in bpy.data.objects['Cortex-inflated-{}'.format(hemi)].children:
                for i in range(3):
                    label_obj.scale[i] = 0.1
        inf_hemi = bpy.data.objects.get('inflated_{}'.format(hemi), None)
        if inf_hemi is not None:
            for i in range(3):
                inf_hemi.scale[i] = 0.1

    if bpy.data.objects.get('Subcortical_structures', None) is not None:
        for sub_obj in bpy.data.objects['Subcortical_structures'].children:
            for i in range(3):
                sub_obj.scale[i] = 0.1

    for sub_obj in bpy.data.objects['Subcortical_fmri_activity_map'].children:
        _fix_scale(sub_obj.name)

    for obj_name in ['inner_skull', 'outer_skull', 'eeg_helmet', 'meg_helmet', 'seghead']:
        _fix_scale(obj_name)
    # _fix_scale('skull_plane')


def _fix_scale(obj_name):
    obj = bpy.data.objects.get(obj_name, None)
    if obj is not None:
        for i in range(3):
            obj.scale[i] = 0.1


def get_classes():
    classes = (
        appearance_panel.AppearanceMakerPanel,
        show_hide_panel.ShowHideObjectsPanel
    )
    return classes


def get_panels(first_time=False):
    panels = [data_panel, appearance_panel, show_hide_panel, selection_panel, coloring_panel, colorbar_panel, play_panel, filter_panel,
            render_panel, freeview_panel, transparency_panel, where_am_i_panel, search_panel, load_results_panel,
            electrodes_panel, streaming_panel, stim_panel, fMRI_panel, meg_panel, connections_panel, vertex_data_panel, dti_panel,
            slicer_panel, skull_panel, reports_panel, labels_panel, scripts_panel, pizco_panel]#, ] #, , dell_panel, moshes_panel)
    # dell_exist = op.isfile(op.join(mmvt_utils.get_parent_fol(__file__), 'dell', 'find_electrodes_in_ct.py'))
    # if not mmvt_utils.IS_WINDOWS and not first_time and dell_exist:
    #     panels.append(dell_panel)
    return panels


# @mmvt_utils.profileit('cumtime', op.join(mmvt_utils.get_user_fol()))
def load_all_panels(addon_prefs=None, first_time=False):
    mmvt = sys.modules[__name__]
    # check_empty_subject_version()
    # fix_cortex_labels_material()
    for panel in get_panels(first_time):
        if panel is freeview_panel:
            panel.init(mmvt, addon_prefs)
        else:
            now = time.time()
            panel.init(mmvt)
            print('{} took {:.5f}s to initialize'.format(panel.__name__, time.time() - now))
    if bpy.data.objects.get('rh'):
        split_view(0)
        split_view(0)
        fix_scale()
    show_activity()
    show_pial()
    # view_all()
    # show_electrodes(False)
    # show_hide_connections(False)
    # show_activity(False)
    mmvt_utils.select_layer(BRAIN_EMPTY_LAYER, False)
    mmvt_utils.unfilter_graph_editor()
    lock_colorbar_values(False)
    for hemi in ['lh', 'rh']:
        if bpy.data.objects.get(hemi):
            bpy.data.objects[hemi].hide = True
            bpy.data.objects[hemi].hide_render = True
    set_colorbar_defaults()
    mmvt_utils.center_view()
    mmvt_utils.select_time_range(0, bpy.context.scene.maximal_time_steps)


def init_freesurfer_env():
    if os.environ.get('FREESURFER_HOME', '') != '':
        os.environ['SUBJECTS_DIR'] = mmvt_utils.get_subjects_dir()


# @mmvt_utils.profileit('cumtime', op.join(mmvt_utils.get_user_fol()))
def main(addon_prefs=None):
    # atexit.register(my_cleanup_code)
    # check if the use_scripts_auto_execute is checked (so the mmvt_addon could run automatically)
    if not bpy.context.user_preferences.system.use_scripts_auto_execute:
        bpy.context.user_preferences.system.use_scripts_auto_execute = True
        bpy.ops.wm.save_userpref()
        # bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
        # bpy.ops.wm.revert_mainfile(use_scripts=True)

    init(addon_prefs)
    try:
        mmvt = sys.modules[__name__]
        for panel in get_panels():
            panel.unregister()
        if bpy.data.objects.get('rh', None) is None:
            data_panel.init(mmvt)
            scripts_panel.init(mmvt)
            # appearance_panel.init(mmvt)
            # transparency_panel.init(mmvt)
            # render_panel.init(mmvt)
        else:
            if addon_prefs is not None:
                load_all_panels(addon_prefs)
        mmvt_utils._addon = mmvt
        if bpy.data.objects.get('rh') and bpy.data.objects.get('lh'):
            for hemi in ['lh', 'rh']:
                bpy.data.objects[hemi].hide = True
                bpy.data.objects[hemi].hide_render = True
                inflated_obj = bpy.data.objects.get('inflated_{}'.format(hemi))
                if inflated_obj:
                    inflated_obj.active_material = bpy.data.materials['Activity_map_mat']
                # if inflated_obj.data.vertex_colors.get('blank') is None:
                #     inflated_obj.data.vertex_colors.new('blank')
                #     for vert in inflated_obj.data.vertex_colors['blank'].data:
                #         vert.color = (1.0, 1.0, 1)
    except:
        print('The classes are already registered!')
        print(traceback.format_exc())


def check_empty_subject_version():
    import shutil
    resources_dir = mmvt_utils.get_resources_dir()
    mmvt_dir = mmvt_utils.get_mmvt_dir()
    resources_empty_brain = op.join(resources_dir, 'empty_subject.blend')
    mmvt_empty_brain = op.join(mmvt_dir, 'empty_subject.blend')
    if not op.isfile(mmvt_empty_brain):
        print('Copying new empty brain')
        shutil.copy(resources_empty_brain, mmvt_empty_brain)
    else:
        empty_brain_resources_mod_time = mmvt_utils.file_modification_time(resources_empty_brain)
        empty_brain_mmvt_mod_time = mmvt_utils.file_modification_time(mmvt_empty_brain)
        if empty_brain_resources_mod_time > empty_brain_mmvt_mod_time:
            print('Copying new empty brain')
            shutil.copy(resources_empty_brain, mmvt_empty_brain)


if __name__ == "__main__":
    main()


