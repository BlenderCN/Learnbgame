if "bpy" in locals():
    import importlib
    importlib.reload(uav_data)
    importlib.reload(update_mats)
else:
    from . import uav_data
    from . import update_mats

import bpy
import bmesh
import sys

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from mathutils import Vector


class ParserError(Exception):
    pass


class ParserWarning(Exception):
    pass


def make_drone_material(name, target_id):
    """ Create Drone material that blinks/solids/etc. """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat["DRONE"] = 1  # needed for update handler
    tree = mat.node_tree
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    links.clear()
    # build cycles and internal nodetrees
    for name, node in uav_data.mat_nodes.items():
        mat_node = nodes.new(type=node['bl_idname'])
        mat_node.name = name
        for property, value in node.items():
            if not property == 'bl_idname':
                setattr(mat_node, property, value)
    for link in uav_data.mat_links:
        input = nodes[
            link['from_node']['name']].outputs[link['from_socket']['index']]
        output = nodes[
            link['to_node']['name']].inputs[link['to_socket']['index']]
        mat_link = links.new(input, output)
    # add animation data
    animation_data = mat.node_tree.animation_data_create()
    # add drivers
    for driver in uav_data.mat_drivers:
        mat_driver = update_mats.driver_add(
            tree, driver['data_path'], driver['array_index'])
        while mat_driver.modifiers:
            mat_driver.modifiers.remove(mat_driver.modifiers[-1])
        for prop, value in driver['driver'].items():
            setattr(mat_driver.driver, prop, value)
        while mat_driver.driver.variables:
            mat_driver.driver.variables.remove(mat_driver.driver.variables[-1])
        for variable in driver['variables']:
            driver_variable = mat_driver.driver.variables.new()
            for prop, value in variable.items():
                if not prop == 'targets':
                    setattr(driver_variable, prop, value)
            for i, target in enumerate(variable['targets']):
                variable_target = driver_variable.targets[i]
                variable_target.id = target_id
                for prop, value in target.items():
                    if not prop == 'id':
                        setattr(variable_target, prop, value)
        update_mats.copy_keyframes_to_curve(
            mat_driver, driver["keyframe_points"])
    # add animation_curves
    action = bpy.data.actions.new("{}NodeTreeAction".format(name))
    tree.animation_data.action = action
    for fcurve in uav_data.mat_fcurves:
        mat_fcurve = update_mats.fcurve_add(
            action, fcurve['data_path'], fcurve['array_index'])
        update_mats.copy_keyframes_to_curve(
            mat_fcurve, fcurve["keyframe_points"])
        for modifier in fcurve['modifiers']:
            fcurve_mod = mat_fcurve.modifiers.new(modifier['type'])
            for name, value in modifier.items():
                if not name == 'type':
                    setattr(fcurve_mod, name, value)
    return mat


class ImportInitialUAVs(Operator, ImportHelper):
    """Import UAVs with IDs and initial locations as Empties from yaml file"""
    bl_idname = "object.magiclab_uav_input"
    bl_label = "Magiclab Way-point Import"

    filename_ext = ".yaml"

    filter_glob = StringProperty(
            default="*.yaml",
            options={'HIDDEN'},
            maxlen=255,
            )

    def execute(self, context):

        packages_path = ""
        try:
            prefs = context.user_preferences.addons['magiclab_uav_io']
        except KeyError:
            print("couldn't import pref")
        else:
            packages_path = prefs.preferences.module_path
        try:
            import yaml
        except ImportError:
            sys.path.append(packages_path)
            try:
                import yaml
            except ImportError:
                class yaml:
                    """ Dummy yaml Class just for waypoints format """
                    def load(data):
                        """ super hackish special loader when no yaml lib """
                        print("Warning: hackish parser")
                        initial_character = '-'
                        keys  = ("id", "channel", "initialPosition")
                        eval_funcs = (int, int, eval)
                        lines = data.split('\n')
                        lines = [
                            ''.join(line.split()) for line in lines
                            if ''.join(line.split())]
                        struct = {"crazyflies":[]}
                        getting_crazyflies = False
                        found_all_crazyflies = False
                        in_fly = False
                        current_crazy_fly = {k: None for k in keys}
                        while lines and not found_all_crazyflies:
                            if lines[0].startswith('crazyflies'):
                                lines.pop(0)
                                getting_crazyflies = True
                            elif (
                                    lines[0].startswith(initial_character) and
                                    getting_crazyflies and not in_fly):
                                lines[0] = lines[0][1:]
                                in_fly = True
                            elif (
                                    getting_crazyflies and in_fly and
                                    any(lines[0].startswith(k) for k in keys)):
                                values = lines[0].split(':')
                                idx = keys.index(values[0])
                                current_crazy_fly[values[0]] = eval_funcs[idx](
                                    values[-1])
                                if all(
                                        None != v
                                        for v in current_crazy_fly.values()):
                                    struct["crazyflies"].append(
                                        current_crazy_fly)
                                    current_crazy_fly = {k: None for k in keys}
                                    in_fly = False
                                lines.pop(0)
                            elif (
                                    getting_crazyflies and in_fly
                                    and lines[0].startswith(initial_character)):
                                raise ParserError
                                break
                            elif (
                                    getting_crazyflies
                                    and any(
                                        lines[0].startswith(k) for k in keys)
                                    and not in_fly):
                                lines.pop(0)
                            elif getting_crazyflies:
                                lines.pop(0)
                                getting_crazyflies = False
                            else:
                                lines.pop(0)
                        return struct

        scene = context.scene
        f = open(self.filepath, 'r', encoding='utf-8')
        data = f.read()
        f.close()
        try:
            structs = yaml.load(data)
        except ParserError:
            self.report({'ERROR'}, "Parser Failure")
            return {'CANCELLED'}
        try:
            uav_dict = structs['crazyflies']
        except KeyError:
            self.report({'ERROR'}, "No crazyflies found in file")
            return {'CANCELLED'}
        uav_obs = []
        if uav_dict:
            # create the mesh first:
            mesh = bpy.data.meshes.new("UAV")
            bm = bmesh.new()
            for v_co in uav_data.sphere_verts:
                bm.verts.new(v_co)
            bm.verts.ensure_lookup_table()
            for f_idx in uav_data.sphere_faces:
                bm.faces.new([bm.verts[i] for i in f_idx])
            bm.to_mesh(mesh)
            mesh.update()
            for uav in uav_dict:
                uav_ob = bpy.data.objects.new(str(uav['id']), mesh)
                uav_ob['channel'] = uav['channel']
                scene.objects.link(uav_ob)
                uav_ob.empty_draw_size = 0.1
                uav_ob.layers = scene.layers
                uav_ob.location = uav['initialPosition']
                uav_obs.append(uav_ob)
                uav_ob.glow = 0.0
                uav_mat = make_drone_material(
                    "uav_material_{}".format(uav['id']), uav_ob)
                uav_ob.active_material = None
                uav_ob.material_slots[0].link = 'OBJECT'
                uav_ob.material_slots[0].material = uav_mat

            if context.space_data and context.space_data.type == 'VIEW_3D':
                context.space_data.viewport_shade = 'SOLID'
            context.scene.render.engine = 'CYCLES'
            update_mats.drive_drone_solids(context.scene)

        else:
            self.report({'ERROR'}, "Empty File")
            return {'CANCELLED'}
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(
        ImportInitialUAVs.bl_idname, text="Magiclab Way-point Import")


def register():
    bpy.utils.register_class(ImportInitialUAVs)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportInitialUAVs)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
