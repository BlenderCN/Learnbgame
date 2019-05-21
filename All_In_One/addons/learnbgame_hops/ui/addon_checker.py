import bpy
from .. utils.addons import addon_exists
 
used_addons = [
    ("BoxCutter",           "BoxCutter",        "https://gumroad.com/l/BoxCutter/iamanoperative"),
    ("DECALmachine",        "DECALmachine",     "https://gumroad.com/l/DECALmachine/"),
    ("MESHmachine",         "MESHmachine",      "https://gumroad.com/l/MESHmachine/decalarmy"),
    ("mira_tools",          "Mira Tools",       "http://blenderartists.org/forum/showthread.php?366107-MiraTools")
]
 
recommended_addons = [
    ("GroupPro",            "Group Pro",        "https://gumroad.com/l/GroupPro/for_operatives#"),
    ("Batch Operations",    "Batch Operations", "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/BatchOperations"),
    ("power_snapping_pies", "Snapping Pies",    "https://github.com/sebastian-k/scripts/blob/master/power_snapping_pies.py"),
    ("Fidget",              "Fidget",           "https://gumroad.com/l/fidget_b3d#")
]
 
def draw_addon_diagnostics(layout, columns = 4):
    col = layout.column()
    col.label(text="Recommended Addons:")
    draw_addon_table(col, used_addons, columns, True)
 
    col = layout.column()
    col.label(text="Additional Addons:")
    draw_addon_table(col, recommended_addons, columns, False)
 
def draw_addon_table(layout, addons, columns, show_existance):
    col = layout.column()
    for i, (identifier, name, url) in enumerate(addons):
        if i % columns == 0: row = col.row()
        icon = addon_icon(identifier, show_existance)
        row.operator("wm.url_open", text=name, icon = icon).url = url
 
    if len(addons) % columns != 0:
        for i in range(0, columns - len(addons) % columns):
            row.label(text="")
 
def addon_icon(addon_identifier, show_existance):
    if show_existance:
        if addon_exists(addon_identifier): return "FILE_TICK"
        else: return "ERROR"
    else:
        return "NONE"
 
