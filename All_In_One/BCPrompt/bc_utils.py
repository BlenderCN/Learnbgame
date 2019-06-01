import bpy
import bmesh
from mathutils import Vector
from console_python import add_scrollback

import os
import sys
import json
import shutil
import traceback
import webbrowser
from urllib.request import (urlopen, urlretrieve)

from .sub_util import (
    make_animated_gif,
    make_optimized_animated_gif,
    cmd_controller
)


def center_to_selected(context):

    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    print(dir(bm.verts))
    loc = [v.co for v in bm.verts if v.select]
    if len(loc) == 1:
        loc = loc[0]
    else:
        median = Vector()
        for v in loc:
            median = Vector((median.x + v.x, median.y + v.y, median.z + v.z))
        loc = median / len(loc)
    context.scene.cursor_location = obj.matrix_world * loc


def throw_manual():
    # if i want to do own parsing + stylesheet
    zef = "https://raw.githubusercontent.com/zeffii/"
    ul = zef + "BlenderConsolePrompt/master/README.md"

    path_init = os.getcwd()
    temp_root = os.path.dirname(__file__)
    tmp = os.path.join(temp_root, 'tmp')
    os.chdir(tmp)

    readme_path = os.path.join(tmp, 'README.md')
    urlretrieve(ul, readme_path)

    # generate the markdown json obj first.
    with open(readme_path) as mdfile:
        md_str = repr(''.join(mdfile.readlines()))
        json_str = """var jsonObject = {{"items": {0}}}""".format(md_str)
        with open("bcp_readme.json", 'w') as destjson:
            destjson.writelines(json_str)

    webbrowser.open('README.html')
    os.chdir(path_init)


def bcp_webbrowser(local_path):
    '''sets current dir to tmp, starts the browser, reverts dir.'''
    path_init = os.getcwd()
    temp_root = os.path.dirname(__file__)
    temp_html = os.path.join(temp_root, 'tmp')
    os.chdir(temp_html)
    webbrowser.open(local_path)
    os.chdir(path_init)


def bcp_justbrowse(destination):
    webbrowser.open(destination)


def sv_test():
    try:
        ng = bpy.data.node_groups
    except:
        print('no node SV groups!')
        return

    sv_present = 'sverchok' in globals()
    if not sv_present:
        try:
            import sverchok
            print('Sverchok is now in globals')
        except:
            print('failed to import sverchok')
            return

    return True


def get_sv_times(named_group):

    if not sv_test():
        return

    import sverchok
    ng = bpy.data.node_groups
    upd = bpy.ops.node.sverchok_update_current

    # at this point sverchok should be available.
    # github.com/nortikin/sverchok/issues/500#issuecomment-67337023
    def write_time_graph_json(destination_path):
        m = sverchok.core.update_system.graphs
        atk = {}
        for idx, event in enumerate(m[0]):
            atk[idx] = event

        tk = dict(items=atk)
        tkjson = json.dumps(tk, sort_keys=True, indent=2)
        with open(destination_path, 'w') as time_graph:
            # this augments the first line of the json with a var
            # transforming it into a valid .js file which can be
            # called from the inlet.js
            final_write = "var jsonObject = " + tkjson
            time_graph.writelines(final_write)

    _root = os.path.dirname(__file__)
    fp = os.path.join(_root, 'tmp', 'sverchok_times.json')

    for g in ng:
        if g.bl_idname == 'SverchCustomTreeType':
            if g.name == named_group:
                upd(node_group=named_group)
                print('updating for:', named_group)
                write_time_graph_json(fp)
                bcp_webbrowser('index.html')
                break


def get_sv_times_all():
    if not sv_test():
        return

    grandlist = []
    mn = []

    import sverchok
    ng = bpy.data.node_groups
    upd = bpy.ops.node.sverchok_update_current
    for g in ng:
        if g.bl_idname == 'SverchCustomTreeType':
            upd(node_group=g.name)
            m = sverchok.core.update_system.graphs
            print(g.name)
            print(m)
            mn.append(g.name)
            grandlist.extend(m.copy())
            print('::::')

    ''' Augmented full node tree and subtree json'''

    _root = os.path.dirname(__file__)
    fp_full = os.path.join(_root, 'tmp', 'sverchok_times_full.json')

    full_atk = {}
    print('number of subgraphs:', len(grandlist))
    for index, (graph, graph_name) in enumerate(zip(grandlist, mn)):
        atk = {idx: event for idx, event in enumerate(graph)}
        gtk = dict(items=atk, name=graph_name)
        full_atk[index] = gtk

    final_atk = dict(graphs=full_atk)

    tkjson_full = json.dumps(final_atk, sort_keys=True, indent=2)
    with open(fp_full, 'w') as time_graph:
        final_write = "var jsonObject = " + tkjson_full
        time_graph.writelines(final_write)


def github_commits(url, num_items):
    found_ref = found_json = urlopen(url)
    try:
        found_json = found_ref.readall().decode()
    except:
        found_json = found_ref.read().decode()

    wfile = json.JSONDecoder()
    wjson = wfile.decode(found_json)
    for idx, i in enumerate(wjson):
        commit = i['commit']

        print(commit['committer']['name'])
        for line in commit['message'].split('\n'):
            if not line:
                continue
            print('  ' + line)
        print()
        if idx > num_items:
            break


def do_text_glam():

    def set_props(s):
        # s = context.space_data
        s.show_line_numbers = True
        s.show_word_wrap = True
        s.show_syntax_highlight = True
        s.show_margin = True

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:

            if not area.type == 'TEXT_EDITOR':
                continue

            for s in area.spaces:
                if s.type == 'TEXT_EDITOR':
                    set_props(s)


def set_keymap():

    # script to map 1, 2, 3 to vertex, edge, face selection for 3dview
    wm = bpy.context.window_manager

    if True:
        deactivate_list = ['ONE', 'TWO', 'THREE']
        view3d_km_items = wm.keyconfigs.default.keymaps['3D View'].keymap_items
        for j in view3d_km_items:
            if j.type in deactivate_list and j.name == 'Layers':
                j.active = False

    if True:
        my_keymap = {
            'ONE': "True, False, False",
            'TWO': "False, True, False",
            'THREE': "False, False, True"
        }

        km = wm.keyconfigs.default.keymaps['Mesh']
        for k, v in my_keymap.items():
            new_shortcut = km.keymap_items.new('wm.context_set_value', k, 'PRESS')
            new_shortcut.properties.data_path = 'tool_settings.mesh_select_mode'
            new_shortcut.properties.value = v

    print('complete')


def vtx_specials(self, m):
    '''
    [1] checks if the addon is enabled by testing a known operator
    [2] if operator is not present, tries to enable the addon.
    [3] If it fails to enable the addon the function returns early.
        [ arguably this should suggest download + install + enable ]
    [4] If the function is found, it calls the specified function.
    '''
    addon_enabled = 'autovtx' in dir(bpy.ops.view3d)  # hasattr will fail.

    if not addon_enabled:
        try:
            bpy.ops.preferences.addon_enable(module="mesh_tinyCAD")
        except:
            print('tinyCAD addon not found.')
            return

    if m == 'vtx':
        bpy.ops.view3d.autovtx()
    elif m == 'xl':
        bpy.ops.mesh.intersectall()


def remove_obj_and_mesh(context):
    scene = context.scene
    objs = bpy.data.objects
    meshes = bpy.data.meshes
    for obj in objs:
        if obj.type == 'MESH':
            scene.objects.unlink(obj)
            objs.remove(obj)
    for mesh in meshes:
        meshes.remove(mesh)


def test_dl_run(packaged, invoke_type=None):
    '''
    This implementation:
    - test if the operator already exists in bpy.ops.xxxx
    - if yes, run
    - if no, try (enable and run).
    - if failed to enable then the packaged dict includes a download url
    - attempts a download and then (enable and run)

    Restrictions:
    - Expects only a single download file not a folder structure yet.
    '''

    _ops, _name = packaged['operator']
    _module = packaged['module_to_enable']
    _url = packaged['url']

    # first check if the operator exists.
    addon_enabled = _name in dir(_ops)

    def run_addon(_ops, _name, invoke_type):
        if invoke_type:
            getattr(_ops, _name)(invoke_type)
        else:
            getattr(_ops, _name)()

    if not addon_enabled:
        try:
            bpy.ops.preferences.addon_enable(module=_module)
            # getattr(_ops, _name)()
            run_addon(_ops, _name, invoke_type)
            return
        except:
            print('\'{0}\' addon not found.'.format(_module))
            print('will attempt download: ')

            # I only want the shortest path.
            script_paths = bpy.utils.script_paths()
            sp = list(sorted(script_paths, key=len))[0]
            contrib_path = os.path.join(sp, 'addons_contrib')

            if not os.path.isdir(contrib_path):
                print('attempting to make path...')
                shutil.os.mkdir(contrib_path)

            # path should exist now.
            print('downloading from:', _url)
            filename = _url.split('/')[-1]
            py_destination = os.path.join(contrib_path, filename)
            urlretrieve(_url, py_destination)

            # must happen or the new script isn't found.
            bpy.utils.refresh_script_paths()

        # try one last time to enable and run.
        try:
            bpy.ops.preferences.addon_enable(module=_module)
            # getattr(_ops, _name)()
            run_addon(_ops, _name, invoke_type)
            return
        except:
            msg = 'blender console has failed miserably, let me know'
            print(msg)

    else:
        # the ops is present, just call it.
        print('STEP 6 operator is present, simply call operator')
        # getattr(_ops, _name)()  # get and call
        run_addon(_ops, _name, invoke_type)


def set_datablock_of_active_textwindow(textname):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:

            if not area.type == 'TEXT_EDITOR':
                continue

            for s in area.spaces:
                if s.type == 'TEXT_EDITOR':
                    print(dir(s))
                    s.text = bpy.data.texts[textname]


def write_keys_textfile():
    arp = """\
‘NONE’,
‘LEFTMOUSE’    ‘MIDDLEMOUSE’,  ‘RIGHTMOUSE’      ‘MOUSEROTATE’
‘BUTTON4MOUSE’ ‘BUTTON5MOUSE’, ‘BUTTON6MOUSE’,   ‘BUTTON7MOUSE’
‘ACTIONMOUSE’  ‘SELECTMOUSE’,  ‘MOUSEMOVE’,      ‘INBETWEEN_MOUSEMOVE’
‘WHEELUPMOUSE’, ‘WHEELDOWNMOUSE’, ‘WHEELINMOUSE’, WHEELOUTMOUSE’

 A B C D E ...Z

 ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE

‘LEFT_CTRL’,  ‘RIGHT_CTRL’
‘LEFT_ALT’,   ‘RIGHT_ALT’
‘LEFT_SHIFT’, ‘RIGHT_SHIFT’

‘OSKEY’, ‘GRLESS’, ‘ESC’, ‘TAB’, ‘RET’, ‘SPACE’, ‘LINE_FEED’, ‘BACK_SPACE’, ‘DEL’
‘SEMI_COLON’, ‘PERIOD’, ‘COMMA’, ‘QUOTE’, ‘ACCENT_GRAVE’
‘MINUS’, ‘SLASH’, ‘BACK_SLASH’, ‘EQUAL’, ‘LEFT_BRACKET’, ‘RIGHT_BRACKET’
‘LEFT_ARROW’, ‘DOWN_ARROW’, ‘RIGHT_ARROW’, ‘UP_ARROW’

 NUMPAD_{0..9}

‘NUMPAD_PERIOD’, ‘NUMPAD_SLASH’, ‘NUMPAD_ASTERIX’
‘NUMPAD_0’, ‘NUMPAD_MINUS’, ‘NUMPAD_ENTER’, ‘NUMPAD_PLUS’

 F1   F2   F3   F4   F5   F6   F7   F8   F9   F10   F11
 F12  F13  F14  F15  F16  F17  F18  F19

‘PAUSE’, ‘INSERT’, ‘HOME’, ‘PAGE_UP’, ‘PAGE_DOWN’, ‘END’,
‘TRACKPADPAN’  ‘TRACKPADZOOM’ """

    new_text = bpy.data.texts.new('key codes')
    new_text.from_string(arp)
    set_datablock_of_active_textwindow(new_text.name)


def view_types_to_console():
    content = """\
bl_<prop>      | allowed
---------------+-------------------------------------------------------------
bl_space_type  | 'CLIP_EDITOR', 'CONSOLE', 'DOPESHEET_EDITOR', 'EMPTY',
               | 'FILE_BROWSER', 'GRAPH_EDITOR', 'IMAGE_EDITOR', 'INFO',
               | 'LOGIC_EDITOR', 'NLA_EDITOR', 'NODE_EDITOR', 'OUTLINER',
               | 'PROPERTIES', 'SEQUENCE_EDITOR', 'TEXT_EDITOR', 'TIMELINE',
               | 'USER_PREFERENCES', 'VIEW_3D'
---------------+-------------------------------------------------------------
bl_region_type | 'CHANNELS', 'HEADER', 'PREVIEW', 'TEMPORARY', 'TOOLS',
               | 'TOOL_PROPS', 'UI', 'WINDOW'
---------------+-------------------------------------------------------------
bl_context     | 'armature_edit', 'curve_edit', 'imagepaint', 'lattice_edit',
               | 'mball_edit', 'mesh_edit', 'objectmode', 'particlemode',
               | 'posemode', 'sculpt_mode', 'surface_edit', 'text_edit',
               | 'vertexpaint', 'weightpaint'
"""
    add_scrollback(content, 'OUTPUT')


def print_addon_msg(origin, msg):
    can_paint = os.name in {'posix'}
    with_color = "\033[1;32m{0}\033[0m" if can_paint else "{0}"
    print(with_color.format(origin), end='')
    print(msg)


def iterate_spaces(AREA, behaviour, end_early=True):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:

            if not area.type == AREA:
                continue

            for s in area.spaces:
                if s.type == AREA:
                    behaviour(s)
                    if end_early:
                        return


