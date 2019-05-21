from .spectral import write_spectral_color, write_spectral_temp
from .texture import export_texture


def inline_material_defaults(exporter, material):
    exporter.w.write(":name '%s'" % material.name)

    if not material.pearray.cast_shadows:
        exporter.w.write(":shadow false")

    if not material.pearray.cast_self_shadows:
        exporter.w.write(":self_shadow false")

    if not material.pearray.is_shadeable:
        exporter.w.write(":shadeable false")

    if not material.pearray.is_camera_visible:
        exporter.w.write(":camera_visible false")


def export_material_diffuse(exporter, material):
    diff_name = export_color(exporter, material, 'diffuse_color', True)
    em_name = export_color(exporter, material, 'emission_color', False)

    exporter.w.write("(material")
    exporter.w.goIn()

    inline_material_defaults(exporter, material)

    if em_name:
        exporter.w.write(":emission %s" % em_name)

    exporter.w.write(":type 'diffuse'")
    exporter.w.write(":albedo %s" % diff_name)

    exporter.w.goOut()
    exporter.w.write(")")


def export_material_orennayar(exporter, material):
    diff_name = export_color(exporter, material, 'diffuse_color', True)
    em_name = export_color(exporter, material, 'emission_color', False)

    exporter.w.write("(material")
    exporter.w.goIn()

    inline_material_defaults(exporter, material)

    if em_name:
        exporter.w.write(":emission %s" % em_name)

    exporter.w.write(":type 'orennayar'")
    exporter.w.write(":albedo %s" % diff_name)
    exporter.w.write(":roughness %f" % material.roughness)

    exporter.w.goOut()
    exporter.w.write(")")


def export_material_ward(exporter, material):
    diff_name = export_color(exporter, material, 'diffuse_color', True)
    spec_name = export_color(exporter, material, 'specular_color', True)
    em_name = export_color(exporter, material, 'emission_color', False)

    exporter.w.write("(material")
    exporter.w.goIn()

    inline_material_defaults(exporter, material)

    if em_name:
        exporter.w.write(":emission %s" % em_name)

    exporter.w.write(":type 'ward'")
    exporter.w.write(":albedo %s" % diff_name)
    exporter.w.write(":specularity %s" % spec_name)
    exporter.w.write(":reflectivity %f" % material.pearray.reflectivity)

    if material.pearray.spec_roughness_x == material.pearray.spec_roughness_y:
        exporter.w.write(":roughness %f" % material.pearray.spec_roughness_x)
    else:
        exporter.w.write(":roughness_x %f" % material.pearray.spec_roughness_x)
        exporter.w.write(":roughness_y %f" % material.pearray.spec_roughness_y)

    exporter.w.goOut()
    exporter.w.write(")")


def export_material_cook_torrance(exporter, material):
    diff_name = export_color(exporter, material, 'diffuse_color', True)
    spec_name = export_color(exporter, material, 'specular_color', True)
    em_name = export_color(exporter, material, 'emission_color', False)
    if material.pearray.specular_ior_type == 'COLOR':
        ior_name = write_spectral_color(exporter, "%s_ior" % material.name,
                                    material.pearray.specular_ior_color)

    exporter.w.write("(material")
    exporter.w.goIn()

    inline_material_defaults(exporter, material)

    if em_name:
        exporter.w.write(":emission %s" % em_name)

    exporter.w.write(":type 'cook_torrance'")

    exporter.w.write(
        ":fresnel_mode '%s'" % material.pearray.ct_fresnel_mode.lower())
    exporter.w.write(":distribution_mode '%s'" %
                     material.pearray.ct_distribution_mode.lower())
    exporter.w.write(
        ":geometry_mode '%s'" % material.pearray.ct_geometry_mode.lower())

    exporter.w.write(":albedo %s" % diff_name)
    exporter.w.write(":diffuse_roughness %f" % material.roughness)

    exporter.w.write(":specularity %s" % spec_name)

    if material.pearray.specular_ior_type == 'COLOR':
        exporter.w.write(":index '%s'" % ior_name)
    else:
        exporter.w.write(":index %f" % material.pearray.specular_ior_value)
    exporter.w.write(":conductor_absorption %s" % diff_name)

    exporter.w.write(":reflectivity %f" % material.pearray.reflectivity)

    if material.pearray.spec_roughness_x == material.pearray.spec_roughness_y:
        exporter.w.write(
            ":specular_roughness %f" % material.pearray.spec_roughness_x)
    else:
        exporter.w.write(
            ":specular_roughness_x %f" % material.pearray.spec_roughness_x)
        exporter.w.write(
            ":specular_roughness_y %f" % material.pearray.spec_roughness_y)

    exporter.w.goOut()
    exporter.w.write(")")


def export_material_glass(exporter, material):
    spec_name = export_color(exporter, material, 'specular_color', True)
    em_name = export_color(exporter, material, 'emission_color', False)
    if material.pearray.specular_ior_type == 'COLOR':
        ior_name = write_spectral_color(exporter, "%s_ior" % material.name,
                                        material.pearray.specular_ior_color)

    exporter.w.write("(material")
    exporter.w.goIn()

    inline_material_defaults(exporter, material)

    if em_name:
        exporter.w.write(":emission %s" % em_name)

    exporter.w.write(":type 'glass'")
    exporter.w.write(":specularity %s" % spec_name)

    if material.pearray.specular_ior_type == 'COLOR':
        exporter.w.write(":index '%s'" % ior_name)
    else:
        exporter.w.write(":index %f" % material.pearray.specular_ior_value)

    if material.pearray.glass_is_thin:
        exporter.w.write(":thin true")

    exporter.w.goOut()
    exporter.w.write(")")


def export_material_mirror(exporter, material):
    spec_name = export_color(exporter, material, 'specular_color', True)
    em_name = export_color(exporter, material, 'emission_color', False)
    if material.pearray.specular_ior_type == 'COLOR':
        ior_name = write_spectral_color(exporter, "%s_ior" % material.name,
                                        material.pearray.specular_ior_color)

    exporter.w.write("(material")
    exporter.w.goIn()

    inline_material_defaults(exporter, material)

    if em_name:
        exporter.w.write(":emission %s" % em_name)

    exporter.w.write(":type 'mirror'")
    exporter.w.write(":specularity %s" % spec_name)
    
    if material.pearray.specular_ior_type == 'COLOR':
        exporter.w.write(":index '%s'" % ior_name)
    else:
        exporter.w.write(":index %f" % material.pearray.specular_ior_value)

    exporter.w.goOut()
    exporter.w.write(")")


def export_material_grid(exporter, material):
    exporter.w.write("(material")
    exporter.w.goIn()

    inline_material_defaults(exporter, material)

    exporter.w.write(":type 'grid'")
    exporter.w.write(":first '%s'" % material.pearray.grid_first_material)
    exporter.w.write(":second '%s'" % material.pearray.grid_second_material)
    exporter.w.write(":gridCount '%i'" % material.pearray.grid_count)
    exporter.w.write(":tileUV '%s'" % material.pearray.grid_tile_uv)

    exporter.w.goOut()
    exporter.w.write(")")


def export_color(exporter, material, type, required, factor=1):
    name = "%s_%s" % (material.name, type)

    attr_col = type
    attr_temp = "%s_temp" % type
    attr_temp_type = "%s_temp_type" % type
    attr_temp_factor = "%s_temp_factor" % type
    attr_type = "%s_type" % type
    attr_tex_slot = "%s_tex_slot" % type

    sub_mat = material
    if not hasattr(material, attr_col):
        sub_mat = material.pearray

    if getattr(material.pearray, attr_type) == 'COLOR':
        color = getattr(sub_mat, attr_col)
        if required or color.r > 0 or color.g > 0 or color.b > 0:
            return "'%s'" % write_spectral_color(exporter, name,
                                                 factor * color)
    elif getattr(material.pearray, attr_type) == 'TEX':
        if len(material.texture_slots) <= 0:
            if required:
                return "''"
            else:
                return ""

        tex_slot = getattr(material.pearray, attr_tex_slot)
        if not tex_slot or tex_slot >= len(material.texture_slots):
            tex_slot = 0
        return "(texture '%s')" % export_texture(
            exporter, material.texture_slots[tex_slot].texture)
    else:
        temp = getattr(material.pearray, attr_temp)
        if required or temp > 0:
            return "'%s'" % write_spectral_temp(
                exporter, name, temp, getattr(material.pearray,
                                              attr_temp_type),
                factor * getattr(material.pearray, attr_temp_factor))

    if required:
        return "''"
    else:
        return ""


def export_material(exporter, material):
    if not material:
        return

    if material.name in exporter.instances['MATERIAL']:
        return

    exporter.register_unique_name('MATERIAL', material.name)

    bsdf = material.pearray.bsdf

    if bsdf == 'DIFFUSE':
        export_material_diffuse(exporter, material)
    elif bsdf == 'ORENNAYAR':
        export_material_orennayar(exporter, material)
    elif bsdf == 'WARD':
        export_material_ward(exporter, material)
    elif bsdf == 'COOK_TORRANCE':
        export_material_cook_torrance(exporter, material)
    elif bsdf == 'GLASS':
        export_material_glass(exporter, material)
    elif bsdf == 'MIRROR':
        export_material_mirror(exporter, material)
    elif bsdf == 'GRID':
        export_material_grid(exporter, material)
    else:
        print("UNKNOWN BSDF %s\n" % bsdf)


def export_default_materials(exporter):
    exporter.MISSING_MAT = exporter.register_unique_name(
        'MATERIAL', "_missing_mat")

    missing_spec_n = write_spectral_color(
        exporter, "%s_spec" % exporter.MISSING_MAT, (10, 7, 8))

    exporter.w.write("(material")
    exporter.w.goIn()

    exporter.w.write(":name '%s'" % exporter.MISSING_MAT)
    exporter.w.write(":type 'diffuse'")
    exporter.w.write(":emission '%s'" % missing_spec_n)

    exporter.w.goOut()
    exporter.w.write(")")
