import bpy
from console_python import add_scrollback, get_console

from .bc_package_manager import in_bpm_commands

from .bc_utils import (
    set_keymap,
    vtx_specials,
    test_dl_run,
    remove_obj_and_mesh,
    github_commits,
    get_sv_times, get_sv_times_all,
    bcp_justbrowse,
    throw_manual,
    center_to_selected,
    write_keys_textfile,
    view_types_to_console,
    make_animated_gif,
    make_optimized_animated_gif,
    cmd_controller,
    iterate_spaces
)

from .bc_text_repr_utils import (
    do_text_glam,
    do_text_synthax,
    do_console_rewriter)

from .bc_search_utils import (
    search_blenderscripting,
    search_bpydocs,
    search_pydocs,
    search_stack,
)

from .bc_gist_utils import (
    find_filenames, to_gist
)

from .bc_scene_utils import (
    select_starting,
    select_starting2,
    distance_check,
    align_view_to_3dcursor,
    parent_selected_to_new_empty,
    add_mesh_2_json,
    crop_to_active,
    v2rdim,
    render_to_filepath,
    process_size_query
)

from .bc_update_utils import (
    peek_builder_org,
    process_zip,
    get_sv
)

from .bc_CAD_utils import (
    perform_face_intersection,
    do_bix2
)

from .bc_theme_utils import (
    set_nodewhite,
    set_3de,
    set_theme
)

from .bc_operator_loaders import run_operator_register

"""
permitted for scrollabck are : INPUT OUTPUT INFO ERROR
"""


history_append = bpy.ops.console.history_append
addon_enable = bpy.ops.preferences.addon_enable


# this to be used for addons which are definitely present..
lazy_dict = {
    '-img2p': [addon_enable, "io_import_images_as_planes"],
    '-bb2': [addon_enable, "BioBlender"],
    '-idxv': [addon_enable, "view3d_idx_view"],
    '-comprendo': [addon_enable, "image_editor_flatten"]
}


def lazy_power_download(mod, dl_url, op_path, op_name, invoke_type=None):
    registers_operator = [op_path, op_name]

    packaged = dict(
        operator=registers_operator,
        module_to_enable=mod,
        url=dl_url
    )

    if invoke_type:
        test_dl_run(packaged)
    else:
        test_dl_run(packaged, invoke_type=invoke_type)


def in_scene_commands(context, m):
    if m == "cen":
        '''cursor to center'''
        context.scene.cursor_location = (0.0, 0.0, 0.0)

    if m == 'cenv':
        context.scene.cursor_location = (0.0, 0.0, 0.0)
        align_view_to_3dcursor()

    elif m == 'cento':
        center_to_selected(context)

    elif m.startswith("cen="):
        '''
        cursor to coordinate, anything that can be evalled..
        eg: cen=bpy.data.objects[1].data.verts[1].co

        '''
        right = m.split('=')[1]
        context.scene.cursor_location = eval(right)

    elif m == 'wipe':
        remove_obj_and_mesh(context)
        add_scrollback('wiped objects and meshes', 'OUTPUT')
        # history_append(text=m, current_character=0, remove_duplicates=True)
        history_append(text=m, remove_duplicates=True)

    elif m == 'wipe+':
        remove_obj_and_mesh(context)
        [bpy.data.materials.remove(i) for i in bpy.data.materials]
        add_scrollback('wiped objects, meshes, and materials', 'OUTPUT')
        history_append(text=m, remove_duplicates=True)

    elif m == 'wipem':
        [bpy.data.materials.remove(i) for i in bpy.data.materials]
        add_scrollback('wiped materials only', 'OUTPUT')
        history_append(text=m, remove_duplicates=True)

    elif m in {'tt', 'tb'}:
        prefs = context.user_preferences
        method = {'tb': 'TRACKBALL', 'tt': 'TURNTABLE'}.get(m)
        prefs.inputs.view_rotate_method = method
        msg = 'set rotation_method to {0} ({1})'.format(method, m)
        add_scrollback(msg, 'OUTPUT')

    elif m == '123':
        set_keymap()
        add_scrollback('enabled: 1=VERT_SEL, 2=EDGE_SEL, 3=FACE_SEL', 'OUTPUT')

    elif m == 'mesh2json':
        add_mesh_2_json('zup')
        add_scrollback('added mesh 2 json script to text editor! remember to triangulate first', 'OUTPUT')

    elif m == 'mesh2json2':
        add_mesh_2_json('yup')
        add_scrollback('added mesh 2 json (y up) script to text editor! remember to triangulate first', 'OUTPUT')

    elif m == 'v2rdim':
        v2rdim()

    elif m in {'crop to active', 'cta'}:
        crop_to_active()

    elif m == 'dandc':
        v2rdim()
        crop_to_active()
        add_scrollback('set render dims and cropped timeline', 'OUTPUT')

    elif m.startswith('anim '):
        fp = m[5:]
        add_scrollback('going to render to ' + fp, 'OUTPUT')
        render_to_filepath(fp)

    elif m.startswith("gif ") and (len(m) > 5):
        make_animated_gif(m[4:])

    elif m.startswith("ogif ") and (len(m) > 6):
        make_optimized_animated_gif(m[5:])

    elif m.startswith('sizeof'):
        process_size_query(m)

    elif m == 'sel lights':
        for o in bpy.data.objects:
            if o.type == 'LAMP':
                o.select = True

    elif m == 'rm lights':
        objs = bpy.data.objects
        named_lights = []
        for o in objs:
            if o.type == 'LAMP':
                named_lights.append(o.name)
        for n in named_lights:
            o = objs[n]
            o.user_clear()
            bpy.context.scene.objects.unlink(o)
            objs.remove(o)

    elif m in {'frame_end = frame_current', 'fend=fcur', 'fc'}:
        scn = bpy.context.scene
        scn.frame_end = scn.frame_current

    elif m == 'psel':
        new_empty = parent_selected_to_new_empty()
        if new_empty:
            msg = 'parented selected to {0}'
            msg = msg.format(new_empty.name)
            output_type = 'OUTPUT'
        else:
            msg = 'no objects selected to parent to'
            output_type = 'ERROR'
        add_scrollback(msg, output_type)

    elif m == 'bright':
        set_theme(context, 'theme_flatty_light')
        set_nodewhite(context, '')
        set_3de(context, '')

    elif m in {'nodeview white', 'nv white', 'nv111'}:
        set_nodewhite(context, '')

    elif m.startswith('theme') and '_' in m and len(m) > 6:
        set_theme(context, m)        

    elif m in {'3dv easy', '3de', 'sde'}:
        set_3de(context, '')

    else:
        return False

    return True


def in_search_commands(context, m):
    if m.endswith('?bs'):
        search_blenderscripting(m[:-3])

    elif m.endswith('?se'):
        if m.endswith('??se'):
            site = 'stackoverflow'
            search_str = m[:-4]
        else:
            site = 'blender.stackexchange'
            search_str = m[:-3]
        search_stack(search_str, site)

    elif m.endswith('?py'):
        search_pydocs(m[:-3])

    elif m.endswith('?bpy'):
        search_bpydocs(m[:-4])
    else:
        return False

    return True


def in_sverchok_commands(context, m):

    if m.startswith('_svc_'):
            bcp_justbrowse('https://github.com/nortikin/sverchok/commits/master')

    elif m.startswith('_svc'):
        # sv commits
        url = "https://api.github.com/repos/nortikin/sverchok/commits"
        github_commits(url, 5)

    elif m.startswith('times '):
        command, named_group = m.split(' ')
        if not (named_group in bpy.data.node_groups):
            pass
        else:
            get_sv_times(named_group)

    elif m == 'times':
        get_sv_times_all()

    elif m == 'get sverchok':
        get_sv()

    elif m.startswith('sv '):
        addon_name = 'sverchok'
        addon = bpy.context.user_preferences.addons.get(addon_name)
        if not addon:
            add_scrollback('sverchok not found', 'ERROR')
            # end early for sanity for the following code
            return True

        prefs = addon.preferences
        if m == 'sv blossom':
            prefs.sv_theme = 'nipon_blossom'
            bpy.ops.node.sverchok_apply_theme()
            add_scrollback('enabled nipon!', 'OUTPUT')
        elif m == 'sv icons':
            prefs.show_icons = not prefs.show_icons
            add_scrollback('set icons = {0}'.format(prefs.show_icons), 'OUTPUT')

    else:
        return False

    return True


def in_core_dev_commands(context, m):

    if m.endswith('??'):

        m = m[:-2]
        console, stdout, stderr = get_console(hash(context.region))

        if m in console.locals.keys():
            f = str(dir(console.locals[m]))
        else:
            try:
                f = str(eval('dir({0})'.format(m)))
            except:
                f = 'failed to find reference..'

        add_scrollback(f, 'OUTPUT')

    elif m.endswith('!'):
        '''copy current line to clipboard'''
        m = m[:-1]
        context.window_manager.clipboard = m
        add_scrollback('added to clipboard', 'OUTPUT')

    elif m == 'ico':
        try:
            addon_enable(module="development_icon_get")
            add_scrollback('added icons to TextEditor', 'OUTPUT')
        except:
            self.report({'INFO'}, "ico addon not present!")

    elif m == '-keys':
        write_keys_textfile()

    elif m == 'syntax':
        do_text_glam()

    elif m in {'syntax lt', 'syntax dk'}:
        do_text_glam()
        theme = m.split()[1]
        print('theme', theme)
        do_text_synthax(theme)

    elif m.startswith('-gist '):
        # will not upload duplicates of the same file, placed in Set first.

        if m == '-gist -o':
            # send all visible, unnamed.
            pass

        if m.startswith('-gist -o '):
            # like:  "-gist -o test_gist"
            # send all visible, try naming it.
            gname = m[9:].strip()
            gname = gname.replace(' ', '_')
            file_names = find_filenames()
            to_gist(file_names, project_name=gname, public_switch=True)

    elif m.startswith('-sel -t '):
        # starting2 not implemented yet
        # accepts:
        # '-sel -t CU CurveObj56'
        # '-sel -t CU CurveObj 56'
        # '-sel -t CURVE CurveObj 56'
        _type, *find_str = m[8:].split()
        select_starting2(' '.join(find_str), _type)

    elif m.startswith('-sel '):
        find_str = m[5:]
        select_starting(find_str)

    elif m == "-man":
        throw_manual()

    elif m == '-gh':
        import os
        import subprocess
        _root = os.path.dirname(__file__)
        f = [os.path.join(_root, 'tmp', 'github_start.bat')]
        subprocess.call(f)

    elif m == 'bl<':
        view_types_to_console()

    elif m.startswith("!"):
        ''' dispatch a threaded worker '''
        cmd_controller(m[1:])

    elif m.startswith('obj=') or m.startswith('n=') or m.startswith('-fem'):
        do_console_rewriter(context, m)

    elif m == 'git help':
        git_strings = (
            "git pull (--all)",
            "git push (--all)",
            "git add (--all)",
            "git add <specify file>  # do this from inside the right directory",
            "git commit -am \"commit message here\"",
            "git checkout -b <branch_name>  # new_branch_name_based_on_current_branch",
            "git branch -D <branch_name> # deletes branch locally (you must be on a different branch first)",
            "git branch",
            "   ",
            "-- be in master, or branch to merge into",
            "   git merge <branch_to_merge>",
            "   git push --all",
            "   ",
            "   ",
            "To reset unstaged things..:",
            "  git fetch origin",
            "  git reset --hard origin/master",
            "  git clean -f"
        )
        for line in git_strings:
            add_scrollback(line, 'OUTPUT')

    elif m.startswith('aft;'):
        newstr = m[4:]
        if newstr:
            # get active tree, and active node, make sure it's a FrameNode
            def behaviour(nodeview):
                tree = nodeview.edit_tree
                nodes = tree.nodes
                node = nodes.active
                if node and node.bl_idname == 'NodeFrame':
                    node.label = newstr

            iterate_spaces('NODE_EDITOR', behaviour)

    else:
        return False

    return True


def in_modeling_tools(context, m):
    if m in {'vtx', 'xl'}:
        vtx_specials(self, m)

    elif m == '-dist':
        msg = distance_check()
        add_scrollback(msg, 'INFO')

    elif m == '-steps':
        registers_operator = [bpy.ops.mesh, 'steps_add']
        module_to_enable = 'mesh_add_steps'
        url_prefix = 'https://raw.githubusercontent.com/zeffii/'
        url_repo = 'rawr/master/blender/scripts/addons_contrib/'
        file_name = 'mesh_add_steps.py'
        dl_url = url_prefix + url_repo + file_name

        packaged = dict(
            operator=registers_operator,
            module_to_enable=module_to_enable,
            url=dl_url
        )

        test_dl_run(packaged)

    elif m == '-debug':  # formerly -debug_mesh

        if 'index_visualiser' in dir(bpy.ops.view3d):
            # bpy.ops.wm.addon_enable(module='view3d_idx_view')
            # msg = 'enabled modified debugger in N panel'
            # add_scrollback(msg, 'OUTPUT')
            return True

        registers_operator = [bpy.ops.view3d, 'index_visualiser']
        module_to_enable = 'view3d_idx_view'
        url_prefix = 'https://gist.githubusercontent.com/zeffii/9451340/raw'
        hasher = '/205610d27968305dfd88b0a521fe35aced83db32/'
        file_name = 'view3d_idx_view.py'
        dl_url = url_prefix + hasher + file_name

        packaged = dict(
            operator=registers_operator,
            module_to_enable=module_to_enable,
            url=dl_url
        )

        test_dl_run(packaged)

    elif m == '-snaps':
        url_prefix = "https://raw.githubusercontent.com/Mano-Wii/Snap-Utilities-Line/master/"
        module_to_enable = "mesh_snap_utilities_line"
        dl_url = url_prefix + (module_to_enable + '.py')

        registers_operator = [bpy.ops.mesh, 'snap_utilities_line']

        packaged = dict(
            operator=registers_operator,
            module_to_enable=module_to_enable,
            url=dl_url
        )

        test_dl_run(packaged)

    elif m == '-or2s':
        url_prefix = "https://gist.githubusercontent.com/zeffii/"
        burp = "5844379/raw/01515bbf679f3f7a7c965d732004086dd40e64c0/"
        mod = "space_view3d_move_origin"
        dl_url = url_prefix + burp + mod + '.py'
        lazy_power_download(mod, dl_url, bpy.ops.object, 'origin_to_selected')

        msg = 'start with space-> Origin Move To Selected'
        add_scrollback(msg, 'INFO')

    elif m == 'get comprendo':
        url_prefix = "https://gist.githubusercontent.com/zeffii/"
        burp = "eff101fca227ac706d9b/raw/53360a0e4ac6af8d371ed2d91c77ea6d83e12ad0/"
        mod = "image_editor_flatten"
        dl_url = url_prefix + burp + mod + '.py'
        lazy_power_download(mod, dl_url, bpy.ops.image, 'tkd_callback_operator')

        msg = 'downloaded or checked if composite+render is present'
        add_scrollback(msg, 'INFO')

    elif m in lazy_dict:
        try:
            f, cmd = lazy_dict[m]
            f(module=cmd)
            msg = 'enabled: ' + cmd
            add_scrollback(msg, 'OUTPUT')
        except:
            rt = 'failed to do: ' + str(lazy_dict[m])

    elif m == '-itx':
        perform_face_intersection()

    elif m.startswith('enable '):
        command, addon = m.split()
        t = addon_enable(module=addon)
        if t == {'FINISHED'}:
            msg = 'enabled {0}'.format(addon)
        elif t == {'CANCELLED'}:
            msg = 'addon not enabled, is it spelled correctly?'
        add_scrollback(msg, 'INFO')

    elif m == '-bix2':
        do_bix2()

    else:
        return False

    return True


def in_upgrade_commands(context, m):
    if m.startswith("-up "):
        # inputs            | argument result
        # ------------------+-------------------
        # -up win32         | option = ['win32']
        # -up win64 berry   | option = ['win64', 'berry']
        cmd, *option = m.split(' ')
        res = peek_builder_org(option)
        if res:
            for line in res:
                add_scrollback(line, 'OUTPUT')
            add_scrollback('', 'OUTPUT')

        if len(res) == 1:
            process_zip(res[0])
        else:
            msg = 'too many zips, narrow down!'
            add_scrollback(msg, 'INFO')
    else:
        return False

    return True


def in_fast_ops_commands(context, m):
    if m.startswith('--plex'):
        run_operator_register("fast_ops", "node_plex.py")
    elif m.startswith('--sort'):
        run_operator_register("fast_ops", "mesh_plex.py")
    else:
        return False

    return True
