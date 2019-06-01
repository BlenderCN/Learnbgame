import bpy
import os.path as op
import sys
import glob
import importlib
import inspect
import traceback
import mmvt_utils as mu


def _addon():
    return ScriptsPanel.addon


def set_param(param_name, val):
    script_name = bpy.context.scene.scripts_files.replace(' ', '_')
    set_param_func = get_func(ScriptsPanel.libs[script_name], 'set_{}'.format(param_name))
    if set_param_func is not None:
        return set_param_func(val)
    set_param_func = get_func(ScriptsPanel.libs[script_name], 'set_param')
    if set_param_func is not None:
        return set_param_func(param_name, val)
    else:
        print('The script {} does not have the set_param func!'.format(script_name))
        try:
            bpy.context.scene[param_name] = val
        except:
            print(traceback.format_exc())
        return None


def get_param(param_name):
    script_name = bpy.context.scene.scripts_files.replace(' ', '_')
    get_param_func = get_func(ScriptsPanel.libs[script_name], 'get_{}'.format(param_name))
    if get_param_func is not None:
        return get_param_func()
    get_param_func = get_func(ScriptsPanel.libs[script_name], 'get_param')
    if get_param_func is not None:
        return get_param_func(param_name)
    else:
        print('The script {} does not have the get_param func!'.format(script_name))
        try:
            return bpy.context.scene[param_name]
        except:
            print(traceback.format_exc())
        return None


def set_script(script_name):
    bpy.context.scene.scripts_files = script_name.replace('_', ' ')


def scripts_items_update(self, context):
    script_name = bpy.context.scene.scripts_files.replace(' ', '_')
    run_func, init_func, draw_func, params = ScriptsPanel.funcs[script_name]
    # func_params = [str(p) for p in params]
    # ScriptsPanel.cb_min_max_exist = 'cb_min' in func_params and 'cb_max' in func_params
    # ScriptsPanel.threshold_exist = 'threshold' in func_params
    if init_func is not None:
        init_func(_addon())


def check_script(script_name, return_all=False):
    try:
        lib = importlib.import_module(script_name)
        importlib.reload(lib)
        run_func = getattr(lib, 'run')
        func_signature = inspect.signature(run_func)
        if len(func_signature.parameters) >= 1:
            init_func = get_func(lib, 'init')
            draw_func = get_func(lib, 'draw')
            ScriptsPanel.funcs[script_name] = (run_func, init_func, draw_func, func_signature.parameters)
            ScriptsPanel.libs[script_name] = lib
            if return_all:
                return lib, ScriptsPanel.funcs[script_name]
            else:
                return True
        else:
            return None if return_all else False
    except:
        return None if return_all else False


def get_func(lib, func_name):
    try:
        func = getattr(lib, func_name)
    except:
        func = None
    return func


def run_script(script_name=''):
    if script_name != '' and bpy.context.scene.scripts_files != script_name:
        bpy.context.scene.scripts_files = script_name
    try:
        script_name = bpy.context.scene.scripts_files.replace(' ', '_')
        run_func, init_func, draw_func, params = ScriptsPanel.funcs[script_name]
        # if ScriptsPanel.cb_min_max_exist and ScriptsPanel.threshold_exist:
        #     run_func(_addon(), cb_min=bpy.context.scene.scripts_cb_min, cb_max=bpy.context.scene.scripts_cb_max,
        #              threshold=bpy.context.scene.scripts_threshold)
        # elif ScriptsPanel.threshold_exist:
        #     run_func(_addon(), threshold=bpy.context.scene.scripts_threshold)
        run_func(_addon())
        # if len(params) == 2:
        #     run_func(_addon(), bpy.context.scene.scripts_overwrite)
        # elif len(params) == 1:
        #     run_func(_addon())
        # else:
        #     print('run_script: The script {} has {} params!'.format(len(params)))
        #     print(params)
    except:
        print("run_script: Can't run {}!".format(script_name))
        print(traceback.format_exc())


def get_overwrite():
    return bpy.context.scene.scripts_overwrite


def get_scripts_names():
    return ScriptsPanel.scripts_names


def scripts_draw(self, context):
    layout = self.layout
    layout.prop(context.scene, 'scripts_files', text='')
    # row = layout.row(align=0)
    script_name = bpy.context.scene.scripts_files.replace(' ', '_')
    _, _, draw_func, _ = ScriptsPanel.funcs[script_name]
    if draw_func is not None:
        draw_func(self, context)
    layout.operator(RunScript.bl_idname, text="Run script", icon='POSE_HLT')
    layout.operator(UpdateScripts.bl_idname, text="Update scripts", icon='PREFERENCES')
    # layout.prop(context.scene, 'scripts_overwrite', 'Overwrite')
    # if ScriptsPanel.threshold_exist:
    #     layout.prop(context.scene, 'scripts_threshold', 'threshold')
    # if ScriptsPanel.cb_min_max_exist:
    #     layout.prop(context.scene, 'scripts_cb_min', 'cb min')
    #     layout.prop(context.scene, 'scripts_cb_max', 'cb max')


class RunScript(bpy.types.Operator):
    bl_idname = "mmvt.scripts_button"
    bl_label = "Scripts botton"
    bl_description = 'Runs the selected script above.\n\nScript: mmvt.scripts.run_script()'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        run_script()
        return {'PASS_THROUGH'}


class UpdateScripts(bpy.types.Operator):
    bl_idname = "mmvt.update_scripts"
    bl_label = "Scripts update"
    bl_description = 'Update the scripts.\n\nScript: mmvt.scripts.init(mmvt, False)'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        init(_addon(), False)
        return {'PASS_THROUGH'}


bpy.types.Scene.scripts_files = bpy.props.EnumProperty(items=[],
    description='List of script in the folder:\n..\mmvt_root\mmvtcode\src\examples\scripts\n\nCurrent script')
bpy.types.Scene.scripts_overwrite = bpy.props.BoolProperty(default=False)
# bpy.types.Scene.scripts_threshold = bpy.props.FloatProperty(default=0)
# bpy.types.Scene.scripts_cb_min = bpy.props.FloatProperty(default=0)
# bpy.types.Scene.scripts_cb_max = bpy.props.FloatProperty(default=0)


class ScriptsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Scripts"
    addon = None
    init = False
    funcs = {}
    libs = {}
    scripts_names = []
    cb_min_max_exist = False

    def draw(self, context):
        if ScriptsPanel.init:
            scripts_draw(self, context)


def init(addon, first=True):
    ScriptsPanel.addon = addon
    user_fol = mu.get_user_fol()
    scripts_files = glob.glob(op.join(mu.get_mmvt_code_root(), 'src', 'examples', 'scripts', '*.py'))
    scripts_files_names = [mu.namebase(f) for f in scripts_files]
    scripts_files += [f for f in glob.glob(op.join(mu.get_parent_fol(user_fol), 'scripts', '*.py'))
                      if mu.namebase(f) not in scripts_files_names]
    if len(scripts_files) == 0:
        return None
    sys.path.append(op.join(mu.get_mmvt_code_root(), 'src', 'examples', 'scripts'))
    sys.path.append(op.join(mu.get_parent_fol(user_fol), 'scripts'))
    scripts_files = sorted([f for f in scripts_files if check_script(mu.namebase(f))])[::-1]
    ScriptsPanel.scripts_names = files_names = [mu.namebase(fname).replace('_', ' ') for fname in scripts_files]
    scripts_items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
    bpy.types.Scene.scripts_files = bpy.props.EnumProperty(
        items=scripts_items, update=scripts_items_update,
        description='List of script in the folder:\n..\mmvt_root\mmvtcode\src\examples\scripts\n\nCurrent script')
    bpy.context.scene.scripts_files = files_names[0]
    bpy.context.scene.scripts_overwrite = True
    try:
        bpy.context.scene.report_use_script = bpy.context.scene.reports_files in ScriptsPanel.scripts_names
    except:
        pass
    # bpy.context.scene.scripts_threshold = 2
    # bpy.context.scene.scripts_cb_min = 2
    # bpy.context.scene.scripts_cb_max = 6
    if first:
        register()
    ScriptsPanel.init = True


def register():
    try:
        unregister()
        bpy.utils.register_class(ScriptsPanel)
        bpy.utils.register_class(RunScript)
        bpy.utils.register_class(UpdateScripts)
    except:
        print("Can't register Scripts Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(ScriptsPanel)
        bpy.utils.unregister_class(RunScript)
        bpy.utils.unregister_class(UpdateScripts)
    except:
        pass
