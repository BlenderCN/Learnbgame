import math


from .entity import inline_entity_matrix


def export_camera(exporter, camera):
    w = exporter.w
    scene = exporter.scene

    w.write("(entity")
    w.goIn()

    w.write(":name '%s'" % camera.name)
    w.write(":type 'camera'")

    if camera.data.type == 'ORTHO':
        w.write(":projection 'ortho'")
        w.write(":width %f" % (camera.data.ortho_scale * aspectW))
        w.write(":height %f" % (camera.data.ortho_scale * aspectH))
    else:
        w.write(":width %f" % (camera.data.sensor_width/camera.data.lens))
        w.write(":height %f" % (camera.data.sensor_height/camera.data.lens))

    w.write(":zoom %f" % camera.data.pearray.zoom)
    w.write(":fstop %f" % camera.data.pearray.fstop)
    w.write(":apertureRadius %f" % camera.data.pearray.apertureRadius)
    w.write(":localDirection [0,0,-1]")
    w.write(":localUp [0,-1,0]")
    w.write(":localRight [1,0,0]")
    inline_entity_matrix(exporter, camera)

    w.goOut()
    w.write(")")