

def poweroftwo(minvalue, maxvalue):
    items = []

    while minvalue <= maxvalue:
        items.append(minvalue)
        minvalue *= 2

    return [(str(i), str(i), "") for i in items]


# PREFERENCES

prefs_tab_items = [("GENERAL", "General", ""),
                   ("CREATE", "Decal Creation", ""),
                   ("ABOUT", "About", "")]

prefs_newlibmode_items = [("IMPORT", "Import", ""),
                          ("EMPTY", "Empty", "")]

prefs_decalmode_items = [("INSERT", "Insert", ""),
                         ("REMOVE", "Remove", ""),
                         ("NONE", "None", "")]


# DECAL PROPERTIES

decaltype_items = [("NONE", "None", ""),
                   ("MATERIAL", "Material", ""),
                   ("SIMPLE", "Simple", ""),
                   ("SUBSET", "Subset", ""),
                   ("PANEL", "Panel", ""),
                   ("INFO", "Info", "")]

texturetype_items = [("NONE", "None", ""),
                     ("AO_CURV_HEIGHT", "AO Curvature Height", ""),
                     ("NRM_ALPHA", "Normal Alpha", ""),
                     ("MASKS", "Masks", ""),
                     ("COLOR_ALPHA", "Color Alpha", "")]


# SCENE PROPERTIES - DEFAULTS

interpolation_items = [("Linear", "Linear", "Interpolated"),
                       ("Closest", "Closest", "Pixelated")]

alpha_blendmode_items = [("BLEND", "Blend", "Fast, but  alpha sorted, but faster"),
                         ("HASHED", "Hashed", "Alpha sorted, but slower")]

edge_highlights_items = [("0", "0", ""),
                         ("0.5", "0.5", ""),
                         ("1", "1", "")]

auto_match_items = [("AUTO", "Auto", ""),
                    ("MATERIAL", "Material", ""),
                    ("OFF", "Off", "")]

align_mode_items = [("RAYCAST", "Raycast", ""),
                    ("CURSOR", "Cursor", "")]


# SCENE PROPERTIES - DECCAL CREATION

bake_resolution_items = poweroftwo(64, 1024)

bake_aosamples_items = poweroftwo(128, 512)

bake_supersample_items = [("0", "Off", ""),
                          ("2", "2x", ""),
                          ("4", "4x", "")]


create_decaltype_items = [("SIMPLESUBSET", "Simple/Subset", ""),
                          ("PANEL", "Panel", ""),
                          ("INFO", "Info", "")]

create_infotype_items = [("IMAGE", "Image", ""),
                         ("FONT", "Text", ""),
                         ("GEOMETRY", "Geometry", "")]

create_infotext_align_items = [("left", "Left", ""),
                               ("center", "Center", ""),
                               ("right", "Right", "")]

export_target_items = [("DECALBakeDown", "DECALBakeDown", ""),
                       ("unity3d_bac9_packed_advanced", "Unity3D (Bac9 Packed Advanced)", ""),
                       ("unity3d_machin3", "Unity3D (MACHIN3)", ""),
                       ("unpacked", "Unpacked", ""),
                       ("unreal_engine_4", "Unreal Engine 4", ""),
                       ("substance_painter", "Substance Painter", "")]


# OPERATORS

adjust_mode_items = [("HEIGHT", "Height", ""),
                     ("WIDTH", "Width", ""),
                     ("PARALLAX", "Paralax", ""),
                     ("AO", "Ambient Occlusion", ""),
                     ("STRETCH", "Panel UV Stretch", "")]


# MODIFIERS

mirror_props = ['type',
                'merge_threshold',
                'mirror_object',
                'mirror_offset_u',
                'mirror_offset_v',
                'offset_u',
                'offset_v',
                'show_expanded',
                'show_in_editmode',
                'show_on_cage',
                'show_render',
                'show_viewport',
                'use_axis',
                'use_bisect_axis',
                'use_bisect_flip_axis',
                'use_clip',
                'use_mirror_merge',
                'use_mirror_u',
                'use_mirror_v',
                'use_mirror_vertex_groups']

