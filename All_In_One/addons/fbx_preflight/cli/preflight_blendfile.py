import argparse
import bpy
import os
import time

import addon_utils


def main():
    # Setup and retrieve arguments
    time_start = time.time()

    parser = argparse.ArgumentParser(
        description='Preflight a blendfile for use in Unity')
    parser.add_argument(
        '--fbx-output', help='Output path for the generated FBX.')
    parser.add_argument('--export-animations',
                        help='Output path for the generated FBX.')

    # Fetch Arguments
    fbx_output = parser.parse_known_args()[0].fbx_output
    export_animations = parser.parse_known_args()[0].export_animations

    # Make Sure Addons are Enabled
    if not check_addons(addons=["fbx_preflight", "io_scene_fbx"]):
        print("Preflight Export Failed.")
        return False

    # Set Output Settings based on CLI
    if fbx_output is not None:
        original_fbx_output = bpy.context.scene.preflight_props.export_location
        bpy.context.scene.preflight_props.export_location = bpy.path.relpath(
            fbx_output)

    if export_animations is not None:
        original_export_animations = bpy.context.scene.preflight_props.export_animations
        bpy.context.scene.preflight_props.export_animations = bpy.path.relpath(
            export_animations)

    # Do Export
    bpy.ops.preflight.export_groups()

    # Restore Original Output Settings
    if fbx_output is not None:
        bpy.context.scene.preflight_props.export_location = original_fbx_output

    if export_animations is not None:
        bpy.context.scene.preflight_props.export_animations = bpy.path.relpath(
            original_export_animations)

    # Report Performance
    print("\n------------------------------------------------------")
    print("Preflight Export Finished i--n: %.4f sec" %
          (time.time() - time_start))
    return True


def check_addons(addons=[]):
    enabled_addons = bpy.context.user_preferences.addons.keys()
    for addon in addons:
        if addon not in enabled_addons:
            print("Enabling Addon: {0}".format(addon))
            enabled = addon_utils.enable(addon, persistent=True)

            if enabled is None:
                print("Could not Enable: {0}".format(addon))
                return False

    return True


if __name__ == "__main__":
    main()
