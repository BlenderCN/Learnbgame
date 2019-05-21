# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>
lnmod = (39307,(0, 72))

__all__ = (
    "paths",
    "modules",
    "check",
    "enable",
    "disable",
    "reset_all",
    "module_bl_info",
    )

import bpy as _bpy


error_duplicates = False
error_encoding = False

def paths():
    # RELEASE SCRIPTS: official scripts distributed in Blender releases
    paths = _bpy.utils.script_paths("addons")

    # CONTRIB SCRIPTS: good for testing but not official scripts yet
    # if folder addons_contrib/ exists, scripts in there will be loaded too
    paths += _bpy.utils.script_paths("addons_contrib")

    # EXTERN SCRIPTS: external projects scripts
    # if folder addons_extern/ exists, scripts in there will be loaded too
    paths += _bpy.utils.script_paths("addons_extern")

    # COMMUNITY SCRIPTS : scripts from non Blender Foundation sources
    # for wip or not yet submitted addons (use thos ones at your own risk)
    # if folder addons_sandbox/ exists, scripts in there will be loaded too
    paths += _bpy.utils.script_paths("addons_sandbox")

    return paths


def modules(module_cache):
    global error_duplicates
    global error_encoding
    import os

    error_duplicates = False
    error_encoding = False

    path_list = paths()

    # fake module importing
    def fake_module(mod_name, mod_path, speedy=True):
        global error_encoding

        if _bpy.app.debug:
            print("fake_module", mod_path, mod_name)
        import ast
        ModuleType = type(ast)
        file_mod = open(mod_path, "r", encoding='UTF-8')
        if speedy:
            lines = []
            line_iter = iter(file_mod)
            l = ""
            while not l.startswith("bl_info"):
                try:
                    l = line_iter.readline()
                except UnicodeDecodeError as e:
                    if not error_encoding:
                        error_encoding = True
                        print("Error reading file as UTF-8:", mod_path, e)
                    file_mod.close()
                    return None

                if len(l) == 0:
                    break
            while l.rstrip():
                lines.append(l)
                try:
                    l = line_iter.readline()
                except UnicodeDecodeError as e:
                    if not error_encoding:
                        error_encoding = True
                        print("Error reading file as UTF-8:", mod_path, e)
                    file_mod.close()
                    return None

            data = "".join(lines)

        else:
            data = file_mod.read()

        file_mod.close()

        try:
            ast_data = ast.parse(data, filename=mod_path)
        except:
            print("Syntax error 'ast.parse' can't read %r" % mod_path)
            import traceback
            traceback.print_exc()
            ast_data = None

        body_info = None

        if ast_data:
            for body in ast_data.body:
                if body.__class__ == ast.Assign:
                    if len(body.targets) == 1:
                        if getattr(body.targets[0], "id", "") == "bl_info":
                            body_info = body
                            break

        if body_info:
            try:
                mod = ModuleType(mod_name)
                mod.bl_info = ast.literal_eval(body.value)
                mod.__file__ = mod_path
                mod.__time__ = os.path.getmtime(mod_path)
            except:
                print("AST error in module %s" % mod_name)
                import traceback
                traceback.print_exc()
                raise

            return mod
        else:
            return None

    modules_stale = set(module_cache.keys())

    for path in path_list:
        for mod_name, mod_path in _bpy.path.module_names(path):
            modules_stale -= {mod_name}
            mod = module_cache.get(mod_name)
            if mod:
                if mod.__file__ != mod_path:
                    print("multiple addons with the same name:\n  %r\n  %r" %
                          (mod.__file__, mod_path))
                    error_duplicates = True

                elif mod.__time__ != os.path.getmtime(mod_path):
                    print("reloading addon:",
                          mod_name,
                          mod.__time__,
                          os.path.getmtime(mod_path),
                          mod_path,
                          )
                    del module_cache[mod_name]
                    mod = None

            if mod is None:
                mod = fake_module(mod_name, mod_path)
                if mod:
                    module_cache[mod_name] = mod

    # just incase we get stale modules, not likely
    for mod_stale in modules_stale:
        del module_cache[mod_stale]
    del modules_stale

    mod_list = list(module_cache.values())
    mod_list.sort(key=lambda mod: (mod.bl_info['category'],
                                   mod.bl_info['name'],
                                   ))
    return mod_list


def check(module_name):
    """
    Returns the loaded state of the addon.

    :arg module_name: The name of the addon and module.
    :type module_name: string
    :return: (loaded_default, loaded_state)
    :rtype: tuple of booleans
    """
    import sys
    loaded_default = module_name in _bpy.context.user_preferences.addons

    mod = sys.modules.get(module_name)
    loaded_state = mod and getattr(mod, "__addon_enabled__", Ellipsis)

    if loaded_state is Ellipsis:
        print("Warning: addon-module %r found module "
               "but without __addon_enabled__ field, "
               "possible name collision from file: %r" %
               (module_name, getattr(mod, "__file__", "<unknown>")))

        loaded_state = False

    return loaded_default, loaded_state


def enable(module_name, default_set=True):
    """
    Enables an addon by name.

    :arg module_name: The name of the addon and module.
    :type module_name: string
    :return: the loaded module or None on failier.
    :rtype: module
    """

    import os
    import sys
    import imp

    def handle_error():
        import traceback
        traceback.print_exc()

    #print(module_name)
    #print(modules(_bpy.types.USERPREF_PT_addons._addons_fake_modules))
    #print(_bpy.types.USERPREF_PT_addons._addons_fake_modules)
    #print(_bpy.context.user_preferences.addons.keys())

    # reload if the mtime changes
    mod = sys.modules.get(module_name)
    if mod:
        mod.__addon_enabled__ = False
        mtime_orig = getattr(mod, "__time__", 0)
        mtime_new = os.path.getmtime(mod.__file__)
        if mtime_orig != mtime_new:
            print("module changed on disk:", mod.__file__, "reloading...")

            try:
                imp.reload(mod)
            except:
                handle_error()
                del_modules(module_name)
                return "Error while reloading the addon."
            mod.__addon_enabled__ = False

    # Split registering up into 3 steps so we can undo
    # if it fails par way through.
    # 1) try import
    try:
        mod = __import__(module_name)
        mod.__time__ = os.path.getmtime(mod.__file__)
        mod.__addon_enabled__ = False
    except:
        handle_error()
        del_modules(module_name)
        return None

    # 2) check dependencies if any
    if 'dependencies' in mod.bl_info and mod.bl_info['dependencies'] :
        if dependencies(mod,True) == False :
            addons = _bpy.context.user_preferences.addons
            while module_name in addons:
                addon = addons.get(module_name)
                if addon:
                    addons.remove(addon)
            return 'this addon has dependencies (see addon description and console)'

    # 3) try register collected modules
    # removed, addons need to handle own registration now.

    # 3) try run the modules register function
    try:
        ret = mod.register()
        # register() returns something if addon estimates smtg goes wrong.
        if ret != None :
            print("can't enable ", module_name, " : %s"%ret)
            disable(module_name)
            return 'addon complained at register step (see console)'
        
    except:
        handle_error()
        disable(module_name)
        return None

    # * OK loaded successfully! *
    if default_set:
        # just incase its enabled already
        ext = _bpy.context.user_preferences.addons.get(module_name)
        if not ext:
            ext = _bpy.context.user_preferences.addons.new()
            ext.module = module_name

    mod.__addon_enabled__ = True

    if _bpy.app.debug:
        print("\taddon_utils.enable", mod.__name__)

    return mod


def disable(module_name, default_set=True):
    """
    Disables an addon by name.

    :arg module_name: The name of the addon and module.
    :type module_name: string
    """
    import sys
    mod = sys.modules.get(module_name)
    ret = True
    addon_msg = None
    # possible this addon is from a previous session and didnt load a
    # module this time. So even if the module is not found, still disable
    # the addon in the user prefs.
    if mod:
        # checks if it has childs addon
        if 'childs' not in mod.bl_info or mod.bl_info['childs'] == False :
            #mod.__addon_enabled__ = False
            parents = False

            # this module needs to free its parents
            if 'parents' in mod.bl_info :
                parents = mod.bl_info['parents']
                child = mod.bl_info['name']

            try:
                addon_msg = mod.unregister()
                # unregister() returns False or a string. because the addon refuses to unreg:
                # eg this desobedient addon would need to perform an op. first [modal cases : kill itself before, unsaved file..])
                if addon_msg != None :
                    print("addon_utils.disable", module_name, "still enabled : %s"%addon_msg)
                    return False, addon_msg

            # addon register() failed. continue
            except:
                import traceback
                traceback.print_exc()
                addon_msg = 'disabled with addon errors (see console)'

            # remove the module name from the parents childs list 
            if parents :
                for parent in parents :
                    pmod = sys.modules.get(parent)
                    if pmod != None : # case where the parent addon has failed (line 200)
                        if 'childs' in pmod.bl_info and child in pmod.bl_info['childs'] : # field does not exist if the child addon wad loaded by default
                            del pmod.bl_info['childs'][pmod.bl_info['childs'].index(child)]
                            if pmod.bl_info['childs'] == [] : pmod.bl_info['childs'] = False
                            _bpy.types.USERPREF_PT_addons._addons_fake_modules[parent].bl_info['childs'] = pmod.bl_info['childs']

        # this module has childs to take care of, abort
        else:
            childs = ''
            for n in mod.bl_info["childs"] : childs += '%s, '%(n)
            print("addon_utils.disable", module_name, "in use by %s addons. can't unload"%childs[:-2])
            return False, "in use  by %s addon(s). can't unload"%childs[:-2]
    else:
        print("addon_utils.disable", module_name, "not loaded")

    # could be in more then once, unlikely but better do this just incase.
    addons = _bpy.context.user_preferences.addons

    if default_set:
        while module_name in addons:
            addon = addons.get(module_name)
            if addon:
                addons.remove(addon)

    if _bpy.app.debug:
        print("\taddon_utils.disable", module_name)

    mod.__addon_enabled__ = False 
    del_modules(module_name)
    return ret, addon_msg

# permits to work on multifiles addons without having to restarts blender every 3 min.
def del_modules(module_name, verbose=False) :
    import sys
    if verbose : print("addon_utils.del_modules :")
    for m in dict(sys.modules) :
        if module_name + '.' == m[0:len(module_name) +1 ] :
            if verbose : print('  removing %s child module : %s'%(module_name,m[len(module_name) +1:]))
            del sys.modules[m]
    try : del sys.modules[module_name]
    except : pass


def reset_all(reload_scripts=False):
    """
    Sets the addon state based on the user preferences.
    """
    import sys
    import imp

    paths_list = paths() # path to any addons in RELEASE EXTERN or CONTRIB

    # this mod in order dependencies autoload can act whatever the addon folder is
    for path in paths_list:
        _bpy.utils._sys_path_ensure(path)

    for path in paths_list:
        for mod_name, mod_path in _bpy.path.module_names(path):
            is_enabled, is_loaded = check(mod_name)
            #if is_enabled : print(mod_name, is_enabled, is_loaded)
            # first check if reload is needed before changing state.
            if reload_scripts:
                mod = sys.modules.get(mod_name)
                if mod:
                    imp.reload(mod)

            if is_enabled == is_loaded:
                pass
            elif is_enabled:
                enable(mod_name)
            elif is_loaded:
                print("\taddon_utils.reset_all unloading", mod_name)
                disable(mod_name)


def module_bl_info(mod, info_basis={"name": "",
                                    "author": "",
                                    "version": (),
                                    "blender": (),
                                    "api": 0,
                                    "location": "",
                                    "description": "",
                                    "wiki_url": "",
                                    "tracker_url": "",
                                    "support": 'COMMUNITY',
                                    "category": "",
                                    "warning": "",
                                    "show_expanded": False,
                                    "dependencies": False,
                                    "childs": False
                                    }
                   ):

    addon_info = getattr(mod, "bl_info", {})

    # avoid re-initializing
    if "_init" in addon_info:
        return addon_info

    if not addon_info:
        mod.bl_info = addon_info

    for key, value in info_basis.items():
        addon_info.setdefault(key, value)

    if not addon_info["name"]:
        addon_info["name"] = mod.__name__

    addon_info["_init"] = None
    return addon_info

def parent_list(fields) :
    #print(fields)
    if type(fields) == str : fields = [fields]
    if type(fields) != list :
        return False, 'the dependencies field is wrong. must be either a list or a string.'
    for fi, field in enumerate(fields) :
        if type(field) == str :
            try :
                v0 = field.rindex('(')
                o = 1 if field[v0-1] == ' ' else 0
                addon = field[:v0-o]
                version = eval(field[v0:])
                if type(version) != tuple :
                    return False, 'wrong version format in the dependencies field.'
                fields[fi] = [addon,version]
            except :
                return False, 'wrong or missing version format in the dependencies field.'
        # previous syntax
        elif type(field) == list :
            try :
                addon,version = field
                if type(addon) != str :
                    return False, 'addon name or module name must be a string in the dependencies field.'
                if type(version) != tuple :
                    return False, 'wrong version format in the dependencies field.'
            except :
                return False, "at least one parent description in the dependencies field is wrong. syntax is 'addon name (1,2)' "
        else :
            return False, 'at least one parent description in the dependencies field is wrong. must be either a list or a string.'
    return fields, 'ok'
            

def dependencies(childmodule,verbose=False) :
    module_name = childmodule.bl_info['name']
    needed, msg = parent_list(childmodule.bl_info['dependencies'])
    if verbose : print('checking %s dependencies...'%module_name)
    if needed == False :
        if verbose : print('  %s'%msg)
        return False
    import bpy as _bpy
    import sys as _sys

    mods = modules({})
    mods_names = {} #[ addon_utils.module_bl_info(mod)['name'] for mod in addon_utils.modules({}) ]
    mods_files = {}
    mods_id = []
    parents = []
    for i, mod in enumerate(mods) :
        mods_names[ module_bl_info(mod)['name']] = mod.__name__
        mods_files[mod.__name__] = [ module_bl_info(mod)['name'], i ]
    go = True
    for addon,version in needed :
        v = '.'.join(str(x) for x in version )
        if addon in mods_names or addon in mods_files :
            if addon in mods_files :
                file = addon
            else :
                file = mods_names[addon]
            mod = mods[ mods_files[file][1] ]
            addon = mod.bl_info['name']

            # version check
            cversion = mod.bl_info['version']
            cv = '.'.join(str(x) for x in cversion )
            if verbose : log = ('  . %s v%s (%s) :'%(addon,cv,file))
            if version > cversion :
                if verbose : print("%s a newer version is required, at least v%s."%(log,v))
                if mod.bl_info['wiki_url'] != '' and verbose : print("check %s"%(mod.bl_info['wiki_url']))
                go = False

            # parent check : add it to enabled addons, start it if needed
            else :
                loaded_default, loaded_state = check(file)
                if loaded_default == False :
                    #if verbose : print("%s not started."%file)
                    ext = _bpy.context.user_preferences.addons.new()
                    ext.module = file

                if _sys.modules.get(file) == None :
                    if hasattr(enable(file),'__name__') :
                            print("%s just enabled."%(log))
                            parents.append(mod.__name__)
                    # parent is buggy : no go
                    else :
                        if verbose : print("%s failed."%(log))
                        go = False
                else :
                    if verbose : print("%s enabled."%(log))
                    parents.append(mod.__name__)
        else :
            if verbose : print("  . %s v%s addon is missing. can't run."%(addon,v))
            go = False
    if go :
        childmodule.bl_info['parents'] = parents
        for parent in parents :
            mod = _sys.modules.get(parent)
            if mod == None :
                # this shouldn't occur any longer
                try : print(_bpy.types.USERPREF_PT_addons._addons_fake_modules[parent])
                except : print("%s won't display %s as user (loaded by default)\n"%(parent,module_name))
                continue
            else :
                if 'childs' not in mod.bl_info or mod.bl_info['childs'] == False :
                    mod.bl_info['childs'] = [ module_name ]
                else : 
                    mod.bl_info['childs'].append( module_name )
                ## this to update the user preferences ui
                # when blender ithe fake module dict. is complete, we can modify the faked bl_info
                try :
                    _bpy.types.USERPREF_PT_addons._addons_fake_modules[parent].bl_info['childs'] = mod.bl_info['childs']
                # but at boot time, fake module dict is empty, so we add the parent to it in order the ui can reflect dependencies for parent addons
                except :
                    #print('%s missing in fake module '%parent)
                    #print(_bpy.types.USERPREF_PT_addons._addons_fake_modules)
                    pmod = mods[ mods_files[parent][1] ]
                    pmod.bl_info['childs'] = mod.bl_info['childs']
                    _bpy.types.USERPREF_PT_addons._addons_fake_modules[parent] = pmod
    elif verbose : print("%s needs to fill the conditions above.\n"%(module_name))

    return go

