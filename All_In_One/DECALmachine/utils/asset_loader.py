import bpy
import os
from .. import M3utils as m3
from .. operators.update_decal_nodes import update_decal_node


def icons_folder(string, custom=False):
    if custom:
        decalasssets = bpy.context.user_preferences.addons['DECALmachine'].preferences.customassetpath
    else:
        decalasssets = bpy.context.user_preferences.addons['DECALmachine'].preferences.assetpath
    iconsfolder = os.path.join(decalasssets, string, "icons")
    return iconsfolder


def blends_folder(string, custom=False):
    if custom:
        decalasssets = bpy.context.user_preferences.addons['DECALmachine'].preferences.customassetpath
    else:
        decalasssets = bpy.context.user_preferences.addons['DECALmachine'].preferences.assetpath
    blendsfolder = os.path.join(decalasssets, string, "blends")
    return blendsfolder


def share_materials(decalobj):
    decalmat = decalobj.material_slots[0].material
    if "." in decalmat.name:
        basename = decalmat.name[:-4]

        for mat in bpy.data.materials:
            if basename == mat.name:
                decalobj.material_slots[0].material = mat
                bpy.data.materials.remove(decalmat)
                return

    # return the decal group and update it in 2.79
    lastnode = decalmat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node

    if bpy.app.version >= (2, 79, 0):
        update_decal_node(decalmat, lastnode)

    return lastnode


def match_to_base_material(decalgroup):
    groupname = decalgroup.node_tree.name

    if "Subset" in groupname:
        decaltype = "SUBSET"
    elif "Panel" in groupname:
        decaltype = "PANEL"
    else:
        decaltype = "SUBTRACTOR"

    if bpy.app.version >= (2, 79, 0):
        basematparams = {"distribution": m3.DM_prefs().base_distribution,
                         "color": m3.DM_prefs().base_color,
                         "metallic": m3.DM_prefs().base_metallic,
                         "specular": m3.DM_prefs().base_specular,
                         "speculartint": m3.DM_prefs().base_speculartint,
                         "roughness": m3.DM_prefs().base_roughness,
                         "anisotropic": m3.DM_prefs().base_anisotropic,
                         "anisotropicrotation": m3.DM_prefs().base_anisotropicrotation,
                         "sheen": m3.DM_prefs().base_sheen,
                         "sheentint": m3.DM_prefs().base_sheentint,
                         "clearcoat": m3.DM_prefs().base_clearcoat,
                         "clearcoatroughness": m3.DM_prefs().base_clearcoatroughness,
                         "ior": m3.DM_prefs().base_ior,
                         "transmission": m3.DM_prefs().base_transmission}

        if decaltype == "SUBTRACTOR":
            materialshader = decalgroup.node_tree.nodes.get("Principled BSDF")

            materialshader.distribution = basematparams["distribution"]
            decalgroup.inputs["Material Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Material Metallic"].default_value = basematparams["metallic"]
            decalgroup.inputs["Material Specular"].default_value = basematparams["specular"]
            decalgroup.inputs["Material Specular Tint"].default_value = basematparams["speculartint"]
            decalgroup.inputs["Material Roughness"].default_value = basematparams["roughness"]
            decalgroup.inputs["Material Anisotropic"].default_value = basematparams["anisotropic"]
            decalgroup.inputs["Material Anisotropic Rotation"].default_value = basematparams["anisotropicrotation"]
            decalgroup.inputs["Material Sheen"].default_value = basematparams["sheen"]
            decalgroup.inputs["Material Sheen Tint"].default_value = basematparams["sheentint"]
            decalgroup.inputs["Material Clearcoat"].default_value = basematparams["clearcoat"]
            decalgroup.inputs["Material Clearcoat Roughness"].default_value = basematparams["clearcoatroughness"]
            decalgroup.inputs["Material IOR"].default_value = basematparams["ior"]
            decalgroup.inputs["Material Transmission"].default_value = basematparams["transmission"]

        elif decaltype == "SUBSET":
            materialshader = decalgroup.node_tree.nodes.get("Principled BSDF")
            subsetshader = decalgroup.node_tree.nodes.get("Principled BSDF.001")

            materialshader.distribution = basematparams["distribution"]
            decalgroup.inputs["Material Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Material Metallic"].default_value = basematparams["metallic"]
            decalgroup.inputs["Material Specular"].default_value = basematparams["specular"]
            decalgroup.inputs["Material Specular Tint"].default_value = basematparams["speculartint"]
            decalgroup.inputs["Material Roughness"].default_value = basematparams["roughness"]
            decalgroup.inputs["Material Anisotropic"].default_value = basematparams["anisotropic"]
            decalgroup.inputs["Material Anisotropic Rotation"].default_value = basematparams["anisotropicrotation"]
            decalgroup.inputs["Material Sheen"].default_value = basematparams["sheen"]
            decalgroup.inputs["Material Sheen Tint"].default_value = basematparams["sheentint"]
            decalgroup.inputs["Material Clearcoat"].default_value = basematparams["clearcoat"]
            decalgroup.inputs["Material Clearcoat Roughness"].default_value = basematparams["clearcoatroughness"]
            decalgroup.inputs["Material IOR"].default_value = basematparams["ior"]
            decalgroup.inputs["Material Transmission"].default_value = basematparams["transmission"]

            subsetshader.distribution = basematparams["distribution"]
            decalgroup.inputs["Subset Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Subset Metallic"].default_value = basematparams["metallic"]
            decalgroup.inputs["Subset Specular"].default_value = basematparams["specular"]
            decalgroup.inputs["Subset Specular Tint"].default_value = basematparams["speculartint"]
            decalgroup.inputs["Subset Roughness"].default_value = basematparams["roughness"]
            decalgroup.inputs["Subset Anisotropic"].default_value = basematparams["anisotropic"]
            decalgroup.inputs["Subset Anisotropic Rotation"].default_value = basematparams["anisotropicrotation"]
            decalgroup.inputs["Subset Sheen"].default_value = basematparams["sheen"]
            decalgroup.inputs["Subset Sheen Tint"].default_value = basematparams["sheentint"]
            decalgroup.inputs["Subset Clearcoat"].default_value = basematparams["clearcoat"]
            decalgroup.inputs["Subset Clearcoat Roughness"].default_value = basematparams["clearcoatroughness"]
            decalgroup.inputs["Subset IOR"].default_value = basematparams["ior"]
            decalgroup.inputs["Subset Transmission"].default_value = basematparams["transmission"]

        elif decaltype == "PANEL":
            material1shader = decalgroup.node_tree.nodes.get("Principled BSDF")
            material2shader = decalgroup.node_tree.nodes.get("Principled BSDF.001")

            material1shader.distribution = basematparams["distribution"]
            decalgroup.inputs["Material 1 Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Material 1 Metallic"].default_value = basematparams["metallic"]
            decalgroup.inputs["Material 1 Specular"].default_value = basematparams["specular"]
            decalgroup.inputs["Material 1 Specular Tint"].default_value = basematparams["speculartint"]
            decalgroup.inputs["Material 1 Roughness"].default_value = basematparams["roughness"]
            decalgroup.inputs["Material 1 Anisotropic"].default_value = basematparams["anisotropic"]
            decalgroup.inputs["Material 1 Anisotropic Rotation"].default_value = basematparams["anisotropicrotation"]
            decalgroup.inputs["Material 1 Sheen"].default_value = basematparams["sheen"]
            decalgroup.inputs["Material 1 Sheen Tint"].default_value = basematparams["sheentint"]
            decalgroup.inputs["Material 1 Clearcoat"].default_value = basematparams["clearcoat"]
            decalgroup.inputs["Material 1 Clearcoat Roughness"].default_value = basematparams["clearcoatroughness"]
            decalgroup.inputs["Material 1 IOR"].default_value = basematparams["ior"]
            decalgroup.inputs["Material 1 Transmission"].default_value = basematparams["transmission"]

            material2shader.distribution = basematparams["distribution"]
            decalgroup.inputs["Material 2 Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Material 2 Metallic"].default_value = basematparams["metallic"]
            decalgroup.inputs["Material 2 Specular"].default_value = basematparams["specular"]
            decalgroup.inputs["Material 2 Specular Tint"].default_value = basematparams["speculartint"]
            decalgroup.inputs["Material 2 Roughness"].default_value = basematparams["roughness"]
            decalgroup.inputs["Material 2 Anisotropic"].default_value = basematparams["anisotropic"]
            decalgroup.inputs["Material 2 Anisotropic Rotation"].default_value = basematparams["anisotropicrotation"]
            decalgroup.inputs["Material 2 Sheen"].default_value = basematparams["sheen"]
            decalgroup.inputs["Material 2 Sheen Tint"].default_value = basematparams["sheentint"]
            decalgroup.inputs["Material 2 Clearcoat"].default_value = basematparams["clearcoat"]
            decalgroup.inputs["Material 2 Clearcoat Roughness"].default_value = basematparams["clearcoatroughness"]
            decalgroup.inputs["Material 2 IOR"].default_value = basematparams["ior"]
            decalgroup.inputs["Material 2 Transmission"].default_value = basematparams["transmission"]

    else:
        basematparams = {"distribution": m3.DM_prefs().base_distribution,
                         "color": m3.DM_prefs().base_color,
                         "roughness": m3.DM_prefs().base_roughness}

        if decaltype == "SUBTRACTOR":
            materialshader = decalgroup.node_tree.nodes.get("Glossy BSDF")

            materialshader.distribution = basematparams["distribution"]
            decalgroup.inputs["Material Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Material Roughness"].default_value = basematparams["roughness"]

        elif decaltype == "SUBSET":
            materialshader = decalgroup.node_tree.nodes.get("Glossy BSDF")
            subsetshader = decalgroup.node_tree.nodes.get("Glossy BSDF.001")

            materialshader.distribution = basematparams["distribution"]
            decalgroup.inputs["Material Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Material Roughness"].default_value = basematparams["roughness"]

            subsetshader.distribution = basematparams["distribution"]
            decalgroup.inputs["Subset Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Subset Roughness"].default_value = basematparams["roughness"]

        elif decaltype == "PANEL":
            material1shader = decalgroup.node_tree.nodes.get("Glossy BSDF")
            material2shader = decalgroup.node_tree.nodes.get("Glossy BSDF.001")

            material1shader.distribution = basematparams["distribution"]
            decalgroup.inputs["Material 1 Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Material 1 Roughness"].default_value = basematparams["roughness"]

            material2shader.distribution = basematparams["distribution"]
            decalgroup.inputs["Material 2 Color"].links[0].from_socket.default_value = (basematparams["color"][0], basematparams["color"][1], basematparams["color"][2], 1)
            decalgroup.inputs["Material 2 Roughness"].default_value = basematparams["roughness"]


def prepare_scene(scene):
    # set snapping
    settings = scene.tool_settings
    settings.snap_element = 'FACE'
    settings.use_snap_align_rotation = True
    settings.snap_target = 'MEDIAN'

    # make sure cycles is the renderer
    autocycles = bpy.context.user_preferences.addons['DECALmachine'].preferences.autocycles

    if autocycles is True and scene.render.engine != "CYLCES":
        bpy.context.scene.render.engine = "CYCLES"

    # switch to material view
    automaterialshading = bpy.context.user_preferences.addons['DECALmachine'].preferences.automaterialshading

    if automaterialshading is True:
        bpy.context.space_data.viewport_shade = 'MATERIAL'


def adjust_scale(obj):
    scenescale = m3.get_scene_scale()

    if scenescale != 1.0:
        obj.scale /= scenescale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        displace = obj.modifiers.get("Displace")
        offset = 0.0001 / scenescale  # for a scene scale of 1.0 the offset 0.0001 and hence a mid_level of 0.9999 work great
        midlevel = 1 - offset

        # for midlevel values > 0.99999, cycles will still render the transparent areas black, probably precision related
        if midlevel > 0.99999:
            midlevel = 0.99999

        displace.mid_level = midlevel


def update_asset_loaders(category="ALL"):
    if category == "ALL":
        from .. assets.previews_decals01 import register_and_load_decals01, unregister_and_unload_decals01
        from .. assets.previews_decals02 import register_and_load_decals02, unregister_and_unload_decals02
        from .. assets.previews_info01 import register_and_load_info01, unregister_and_unload_info01
        from .. assets.previews_paneling01 import register_and_load_paneling01, unregister_and_unload_paneling01

        unregister_and_unload_decals01()
        unregister_and_unload_decals02()
        unregister_and_unload_info01()
        unregister_and_unload_paneling01()

        register_and_load_decals01()
        register_and_load_decals02()
        register_and_load_info01()
        register_and_load_paneling01()
    elif category == "decals01":
        from .. assets.previews_decals01 import register_and_load_decals01, unregister_and_unload_decals01
        unregister_and_unload_decals01()
        register_and_load_decals01()
    elif category == "decals02":
        from .. assets.previews_decals02 import register_and_load_decals02, unregister_and_unload_decals02
        unregister_and_unload_decals02()
        register_and_load_decals02()
    elif category == "info01":
        from .. assets.previews_info01 import register_and_load_info01, unregister_and_unload_info01
        unregister_and_unload_info01()
        register_and_load_info01()
    elif category == "paneling01":
        from .. assets.previews_paneling01 import register_and_load_paneling01, unregister_and_unload_paneling01
        unregister_and_unload_paneling01()
        register_and_load_paneling01()
