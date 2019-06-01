import json
import os
import sys

import bpy #pylint: disable=import-error


def export_gltf(settings, src, dst):
    print('Converting .blend file ({}) to .gltf ({})'.format(src, dst))

    # Lazy-load blendergltf
    scriptdir = os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(scriptdir, 'blendergltf'))
    sys.path.insert(0, os.path.join(scriptdir))
    if 'blendergltf' in sys.modules:
        del sys.modules['blendergltf']
    from gltfexts import ExtMaterialsLegacy #pylint: disable=import-error
    import blendergltf #pylint: disable=import-error

    available_extensions = blendergltf.extensions

    dstdir = os.path.dirname(dst)
    os.makedirs(dstdir, exist_ok=True)

    gltf_settings = {
        'extension_exporters': [
            available_extensions.khr_lights.KhrLights(),
            available_extensions.blender_physics.BlenderPhysics(),
        ],
        'gltf_output_dir': dstdir,
        'images_data_storage': 'REFERENCE',
        'nodes_export_hidden': True,
        'meshes_interleave_vertex_data': False,
    }

    if settings['material_mode'] == 'legacy':
        gltf_settings['extension_exporters'].append(ExtMaterialsLegacy())

    collections = [
        "actions",
        "cameras",
        "images",
        "lamps",
        "materials",
        "meshes",
        "objects",
        "scenes",
        "textures",
    ]
    scene = {
        cname: list(getattr(bpy.data, cname))
        for cname in collections
    }
    gltfdata = blendergltf.blendergltf.export_gltf(scene, gltf_settings)

    with open(dst, 'w') as gltffile:
        json.dump(gltfdata, gltffile, sort_keys=True, indent=4)


def main():
    args = sys.argv[sys.argv.index('--')+1:]

    #print(args)
    settings_fname, srcroot, dstdir, blendfiles = args[0], args[1], args[2], args[3:]

    print('srcroot:', srcroot)
    print('Exporting:', blendfiles)
    print('Export to:', dstdir)

    with open(settings_fname) as settings_file:
        settings = json.load(settings_file)

    for blendfile in blendfiles:
        src = blendfile
        dst = src.replace(srcroot, dstdir).replace('.blend', '.gltf')

        bpy.ops.wm.open_mainfile(filepath=src)
        export_gltf(settings, src, dst)


if __name__ == '__main__':
    main()
