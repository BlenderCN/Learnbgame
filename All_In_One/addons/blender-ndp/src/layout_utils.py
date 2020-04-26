import bpy

def draw_prop_row(data, layout:bpy.types.UILayout,
    label:str, prop_names:[], align=True):
    row = layout.row(align=align)
    row.label(text=label)
    for prop_name in prop_names:
        row.prop(data, prop_name, text="")

def draw_prop_array(data, layout:bpy.types.UILayout,
    label:str, prop_array_name:str, prop_indices:[], align=True):
    row = layout.row(align=align)
    row.label(text=label)
    for index in prop_indices:
        row.prop(data, prop_array_name, index=index, text="")