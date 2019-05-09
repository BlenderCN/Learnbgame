import argparse

import gltf.converter


def main():
    parser = argparse.ArgumentParser(
        description='CLI tool to convert glTF files to Panda3D BAM files'
    )

    parser.add_argument('src', type=str, help='source file')
    parser.add_argument('dst', type=str, help='destination file')

    parser.add_argument(
        '--physics-engine',
        choices=[
            'builtin',
            'bullet',
        ],
        default='builtin',
        help='the physics engine to build collision solids for'
    )

    parser.add_argument(
        '--print-scene',
        action='store_true',
        help='print the converted scene graph to stdout'
    )

    parser.add_argument(
        '--skip-axis-conversion',
        action='store_true',
        help='do not perform axis-conversion (useful if glTF data is already Z-Up)'
    )

    args = parser.parse_args()

    settings = gltf.GltfSettings(
        physics_engine=args.physics_engine,
        print_scene=args.print_scene,
        skip_axis_conversion=args.skip_axis_conversion,
    )

    gltf.converter.convert(args.src, args.dst, settings)


if __name__ == '__main__':
    main()
