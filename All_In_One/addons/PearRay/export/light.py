import math
import mathutils


from .entity import inline_entity_matrix
from .material import export_color


def export_pointlight(exporter, light):
    w = exporter.w

    light_data = light.data
    w.write("; Light %s" % light.name)

    factor = 4*math.pi*light_data.pearray.point_radius*light_data.pearray.point_radius
    color_name = export_color(exporter, light_data, 'color', True, factor)

    light_mat_n = exporter.register_unique_name('MATERIAL', light.name + "_mat")

    w.write("(material")
    w.goIn()

    w.write(":name '%s'" % light_mat_n)
    w.write(":type 'light'")
    w.write(":emission %s" % color_name)
    if not light_data.pearray.camera_visible:
        w.write(":camera_visible false")
    else:
        w.write(":albedo %s" % color_name)

    w.goOut()
    w.write(")")

    w.write("(entity")
    w.goIn()

    w.write(":name '%s'" % light.name)
    w.write(":type 'sphere'")
    w.write(":radius %f" % light_data.pearray.point_radius)# Really?
    w.write(":material '%s'" % light_mat_n)
    inline_entity_matrix(exporter, light)

    w.goOut()
    w.write(")")


def export_arealight(exporter, light):
    w = exporter.w
    light_data = light.data
    w.write("; Light %s" % light.name)

    if light_data.shape == 'SQUARE':
        ysize = light_data.size
    else:
        ysize = light_data.size_y

    color_name = export_color(exporter, light_data, 'color', True, light_data.size * ysize)

    light_mat_n = exporter.register_unique_name('MATERIAL', light.name + "_mat")

    w.write("(material")
    w.goIn()

    w.write(":name '%s'" % light_mat_n)
    w.write(":type 'light'")
    w.write(":emission %s" % color_name)
    if not light_data.pearray.camera_visible:
        w.write(":camera_visible false")
    else:
        w.write(":albedo %s" % color_name)

    w.goOut()
    w.write(")")

    w.write("(entity")
    w.goIn()

    w.write(":name '%s'" % light.name)
    w.write(":type 'plane'")
    w.write(":centering true")
    w.write(":xAxis %f" % light_data.size)
    w.write(":yAxis %f" % (-ysize))
    w.write(":material '%s'" % light_mat_n)
    inline_entity_matrix(exporter, light)

    w.goOut()
    w.write(")")


def export_sunlight(exporter, light):
    w = exporter.w
    light_data = light.data
    w.write("; Light %s" % light.name)

    color_name = export_color(exporter, light_data, 'color', True)
    light_mat_n = exporter.register_unique_name('MATERIAL', light.name + "_mat")

    w.write("(material")
    w.goIn()

    w.write(":name '%s'" % light_mat_n)
    w.write(":type 'light'")
    w.write(":emission %s" % color_name)

    w.goOut()
    w.write(")")

    matrix = exporter.M_WORLD * light.matrix_world
    trans, rot, scale = matrix.decompose()
    direction = rot * mathutils.Vector((0, 0, -1))
    w.write("(light")
    w.goIn()

    w.write(":type 'distant'")
    w.write(":direction [%f, %f, %f]" % direction[:])
    w.write(":material '%s'" % light_mat_n)

    w.goOut()
    w.write(")")


def export_light(exporter, light):
    if light.data.type == 'POINT' or light.data.type == 'SPOT':
        export_pointlight(exporter, light)# Interpret as spherical area light
    elif light.data.type == 'HEMI' or light.data.type == 'AREA':
        export_arealight(exporter, light)
    elif light.data.type == 'SUN':
        export_sunlight(exporter, light)
    else:
        print("PearRay does not support lights of type '%s'" % light.data.type)
