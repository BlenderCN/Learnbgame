import bpy
from .camera import export_camera as export_camera
from .light import export_light as export_light
from .material import export_default_materials as export_default_materials
from .material import export_material as export_material 
from .mesh import export_mesh as export_mesh
from .spectral import write_spectral_color
from .settings import export_settings


def is_renderable(scene, ob):
    return (not ob.hide_render)


def renderable_objects(scene):
    return [ob for ob in bpy.data.objects if is_renderable(scene, ob)]


def is_allowed_mesh(ob):
    return (not ob.type in {'META', 'FONT', 'ARMATURE', 'LATTICE', 'EMPTY', 'CAMERA', 'LAMP', 'SPEAKER'})


def write_scene(exporter, pr):
    w = exporter.w
    scene = exporter.scene

    res_x = exporter.render.resolution_x * exporter.render.resolution_percentage * 0.01
    res_y = exporter.render.resolution_y * exporter.render.resolution_percentage * 0.01

    # Exporters
    def export_scene():
        w.write(":name '_from_blender'")
        w.write(":renderWidth %i" % res_x)
        w.write(":renderHeight %i" % res_y)
        w.write(":camera '%s'" % scene.camera.name)


    def export_outputs():
        def start_output(str):
            w.write("(output")
            w.goIn()
            w.write(":name '%s'" % str)
            w.write("(channel")
            w.goIn()

        def end_output():
            w.goOut()
            w.write(")")
            w.goOut()
            w.write(")")

        def raw_output(str):
            start_output(str)
            w.write(":type '%s'" % str)
            end_output()
            
        rl = scene.render.layers.active
        if rl.use_pass_combined:
            start_output('image')
            w.write(":type 'rgb'")
            w.write(":gamma '%s'" % (scene.pearray.linear_rgb if 'none' else 'srgb'))
            w.write(":mapper 'none'")
            end_output()
        
        if rl.use_pass_z:
            raw_output('depth')
        if rl.use_pass_normal:
            raw_output('norm')
        if rl.use_pass_vector:
            raw_output('dpdt')
        if rl.use_pass_uv:
            raw_output('uv')
        if rl.use_pass_object_index:
            raw_output('id')
        if rl.use_pass_material_index:
            raw_output('mat')

        rl2 = scene.pearray_layer
        if rl2.aov_ng:
            raw_output('ng')
        if rl2.aov_nx:
            raw_output('nx')
        if rl2.aov_ny:
            raw_output('ny')
        if rl2.aov_p:
            raw_output('p')
        if rl2.aov_dpdu:
            raw_output('dpdu')
        if rl2.aov_dpdv:
            raw_output('dpdv')
        if rl2.aov_dpdw:
            raw_output('dpdw')
        if rl2.aov_dpdx:
            raw_output('dpdx')
        if rl2.aov_dpdy:
            raw_output('dpdy')
        if rl2.aov_dpdz:
            raw_output('dpdz')
        if rl2.aov_t:
            raw_output('t')
        if rl2.aov_q:
            raw_output('q')
        if rl2.aov_samples:
            raw_output('samples')

        if rl2.raw_spectral:
            w.write("(output_spectral")
            w.goIn()
            w.write(":name 'spectral'")
            w.goOut()
            w.write(")")

    
    def export_background():# TODO: Add texture support
        background_mat_n = exporter.register_unique_name('MATERIAL', '_blender_world_background')

        if exporter.world:
            color = exporter.world.horizon_color
            if color.r > 0 or color.g > 0 or color.b > 0:
                background_spec_n = write_spectral_color(exporter, "%s_spec" % background_mat_n, color)
                w.write("(material")
                w.goIn()

                w.write(":name '%s'" % background_mat_n)
                w.write(":type 'light'")
                w.write(":emission '%s'" % background_spec_n)

                w.goOut()
                w.write(")")

                w.write("(light")
                w.goIn()
                w.write(":type 'env'")
                w.write(":material '%s'" % background_mat_n)
                w.goOut()
                w.write(")")

    # Block
    objs = renderable_objects(scene)

    w.write("(scene")
    w.goIn()

    export_scene()
    w.write("; Settings")
    export_settings(exporter, pr,scene)
    w.write("; Outputs")
    export_outputs()
    w.write("; Default Materials")
    export_default_materials(exporter)
    w.write("; Camera")
    export_camera(exporter, scene.camera)
    w.write("; Background")
    export_background()
    w.write("; Lights")
    for light in objs:
        if light.type == 'LAMP':
            export_light(exporter, light)
    w.write("; Meshes")
    for obj in objs:
        if is_allowed_mesh(obj):
            export_mesh(exporter, obj)
    w.write("; Materials")
    for obj in objs:
        if is_allowed_mesh(obj):
            for m in obj.data.materials:
                export_material(exporter, m)

    w.goOut()
    w.write(")")