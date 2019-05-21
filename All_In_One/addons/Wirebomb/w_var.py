error_101 = False  # no mesh selected
error_301 = False  # no name for new scene

# if checkboxes are active
cb_composited_active = None
cb_clay_only_active = None
cb_mat_wire_active = None
cb_mat_clay_active = None

# render layer names
rlname = ''
rlname_other = ''

# objects selected
objects_affected = set()
objects_other = set()
objects_all_used = set()
is_any_affected = False

# from interface:
# wireframe type
wireframe_method = None

# checkboxes
cb_backup = None
cb_clear_rlayers = None
cb_clear_materials = None
cb_composited = None
cb_only_selected = None
cb_ao = None
cb_clay = None
cb_clay_only = None
cb_mat_wire = None
cb_mat_clay = None

# colors set
color_wire = None
color_clay = None

# materials set (names)
mat_wire_name = None
mat_clay_name = None

# sliders
slider_wt_freestyle = 0.0
slider_wt_modifier = 0.0

# layers selected
layer_numbers_affected = set()
layer_numbers_other = set()

# affected and other layers together
layer_numbers_all_used = set()

# scene name set
scene_name_1 = ''
