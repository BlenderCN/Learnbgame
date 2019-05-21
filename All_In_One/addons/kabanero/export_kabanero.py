import os
import json
import datetime

import bpy
import mathutils
import bpy_extras.io_utils
# import logging
# logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s',)

from progress_report import ProgressReport, ProgressReportSubstep

def _get_info_block(version):
    info = {
        "blender_version": bpy.app.version_string,
        "blender_file": os.path.basename(bpy.data.filepath),
        "export_timestamp": datetime.datetime.now().isoformat()
    }
    if version:
        info["exporter_version"] = "{}.{}.{}".format(*version)

    return info

def _get_library_name(obj):
    """ gets filename from filepath eg. //testlib.blend => testlib """
    filepath = obj.dupli_group.library.filepath
    s = filepath.rfind("/") + 1
    e = filepath.rfind(".")
    return filepath[s:e]

def _is_prefab(o):
    return o.dupli_type == "GROUP"

def _get_data_dict(obj):
    res = {
        "name":         obj.name,
        "active":       obj.get("kb_active"),
        "visible":      obj.get("kb_visible"),
        "collide":      obj.get("kb_collide"),
        "actor":        obj.get("kb_actor"),
        "transform": {
            "position": {
                "x":    obj.location.x,
                "y":    obj.location.y,
                "z":    obj.location.z
            },
            "scale": {
                "x":    obj.scale.x,
                "y":    obj.scale.y,
                "z":    obj.scale.z
            },
            "rotation": {
                "w":    obj.rotation_quaternion[0],
                "x":    obj.rotation_quaternion[1],
                "y":    obj.rotation_quaternion[2],
                "z":    obj.rotation_quaternion[3]
            }
        }
    }

    if _is_prefab(obj):
        res["library"] = _get_library_name(obj)
        res["object"] = obj.dupli_group.name

    # Remove none values
    res = {k: v for k, v in res.items() if v}

    return res

def _write_file(data, filepath):
    with open(filepath, "w") as f:
        f.write(data)
        f.close()

def save(context, filepath, *, use_selection=True, global_matrix=mathutils.Matrix(), script_version = None):
    scene = context.scene

    # Exit edit mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    if use_selection:
        objects = context.selected_objects
    else:
        objects = scene.objects

    map_data = {
        "info": _get_info_block(script_version),
        "objects": [],
    }

    for o in objects:
        # TODO: Apply global matrix
        map_data["objects"].append(_get_data_dict(o))

    j = json.dumps(map_data, indent=2, sort_keys=True)

    # print(j)

    _write_file(j, filepath)

    return {'FINISHED'}
