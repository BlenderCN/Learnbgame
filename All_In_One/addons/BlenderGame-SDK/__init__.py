import bpy
import types
import sys, os
import inspect
import importlib
import imp
import copy
from bpy.app.handlers import persistent
from . import Preferences
from SDK_utils import  *
import SDK_utils.registerpath

sys.path.append(os.path.join(os.path.dirname(__file__),"lib"))

import ATOM_Types
import utils
import Properties

bl_info = {
    "name": "Game Editor",
    "author": "BluStroke®",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "",
    "description": "Editor for Game Engine",
    "warning": "",
    "wiki_url": "",
    "category": "Engine",
    }

ROOT_PATH = os.path.dirname(__file__)
config = utils.Config(os.path.join(ROOT_PATH, "config.ini"), ADDON_ROOT=ROOT_PATH).config

# if __debug__:
#     extentions = ATOM_utils.Addon.list_extentions(config.EXT_PATH)
# else:
#from editors.legacy import build, input, physic, procedural, render, script, audio, account, network

def register():
    preferences.register()

def unregister():
    preferences.unregister()

if __name__ == "__main__":
    register()


    #addons = ATOM_utils.Addon.install_addons(  config.EXT_SOURCE_PATH if config.DEBUG else config.EXT_PATH, ATOM_Types.InstallMod.LOCAL)

    #bpy.app.handlers.load_post.append(ATOM_utils.Addon.load_addons)

    #ATOM_utils.Addon.pack_addons(  os.path.join(root, r"extentions\legacy\source"),
    #                               os.path.join(root, r"extentions\legacy"))
        ####################### CHECK IF ADDON IS IN AN ADDON FOLDER #######################

        # if config.DEBUG:
            
        #     if not mod_root == None:
        #         if not root.split(mod_root)[0] == "":
        #             mod_root = None
            
        #     if mod_root == None:
        #         if "__init__.py" in files:
        #             spec = importlib.util.spec_from_file_location("__init__", os.path.join(root, "__init__.py"))
        #             mod = importlib.util.module_from_spec(spec)
        #             spec.loader.exec_module(mod)
        #             if hasattr(mod, "bl_info"):
        #                 mod_root = root

#def find_addon():
    # if "__init__.py" in os.listdir(path):
    #     full_path = os.path.join(path, "__init__.py")
    #     if os.path.isfile(full_path):
    #         spec = importlib.util.spec_from_file_location("__init__", full_path)
    #         mod = importlib.util.module_from_spec(spec)
    #         spec.loader.exec_module(mod)
    #         if hasattr(mod, "bl_info"):
    #             addons.append(path)
    # else:
    #     for i in os.listdir(path):
    #         full_path = os.path.join(path, i)
    #         if not os.path.isfile(full_path):
    #             find_addon(full_path)

# def load_local_addons(path):

#     global addons

#     for i in os.listdir(path):
#         full_path = os.path.join(path,i)
#         if os.path.isfile(full_path):

#             if i[-3:] == ".py":
#                 spec = importlib.util.spec_from_file_location("i"[:-3], full_path)
#                 mod = importlib.util.module_from_spec(spec)
#                 spec.loader.exec_module(mod)
#                 if hasattr(mod, "bl_info"):
#                     addons.append(full_path)

#             if i[-4:] == ".zip":
#                 file = zipfile.ZipFile(full_path)
#                 elements = file.namelist()
                
#                 if "__init__.py" in elements:
#                     try:
#                         module = zipimport.load_module(os.path.join(full_path, "__init__.py"))
#                         folder = full_path
#                     except ZipImportError:
#                         module = None
#                 else:
#                     match = fnmatch.filter(elements, "*/__init__.py")
#                     if match:
#                         file_path = os.path.join(full_path, match[0].replace("/", os.path.sep))
#                         folder = file_path[-12:]
#                         try:
#                             module = zipimport.load_module(file_path)
#                         except ZipImportError:
#                             module = None
                    
#                     if not module == None:
#                         if hasattr(module, "bl_info"):
#                             addons.append(folder)

#     find_addon(path)
                        
#def register()
    # for i in modules:
    #     if hasattr(i, "unregister"):
    #         i.unregister()

    # if config.DEBUG:
    #     for i in modules:
    #         importlib.reload(i)

    # def get_priority(name):
    #     name = os.path.basename(name)
    #     if name == "__init__.py":
    #         return "0"
    #     if name == "Properties.py":
    #         return "1"
    #     return name
    
    # list_modules(os.path.dirname(__file__), modules)

    # modules.sort(key=lambda x: os.path.join(os.path.dirname(x), get_priority(x)))

    # for i,m in enumerate(modules):
    #     modules[i] = importlib.machinery.SourceFileLoader(os.path.basename(m)[:-3], m).load_module()

    # for i in modules:
    #     if hasattr(i, "register"):
    #         print(i)
    #         i.register()

# def reload_modules(tree):
    
#     for i,m in enumerate(tree):
#         if not (type(m) is tuple):
#             tree[i] = importlib.reload(m)
#     else:
#         load_modules(tree[i][1])
#AutoReload.register()
# modules = dict(locals())

# def reload(name):

#     for k,v in modules.items():
#         if isinstance(v, types.ModuleType) and k == name:##
#             importlib.reload(v)


    #path_list = path.split("\\")

    # offset = 0

    # for i in os.listdir(path):
    #     if os.path.isfile(os.path.join(path,i)):
    #         if i[-3:] == ".py":
    #             if not (os.path.basename(path) == "ATOM" and i == "__init__.py"):
    #                 if i == "__init__.py":
    #                     tree.insert(0,i)
    #                     offset += 1
    #                     continue
    #                 if i == "Properties.py":
    #                     tree.insert(1,i)
    #                     offset += 1
    #                     continue
    #                 tree.insert(offset,i)
    #     else:
    #         if not i == "lib":
    #             tree.append((i,[]))
    #             list_modules(os.path.join(path,i), tree[-1][1])

#def load_modules(tree):

    # for i,m in enumerate(tree):
    #     if not (type(m) is tuple):
    #         tree[i] = importlib.machinery.SourceFileLoader(m[:-3], 
    #                   os.path.join(path, m)).load_module()
    #     else:
    #         load_modules(os.path.join(path, m[0]), tree[i][1])

                # if i == "Properties.py":
                #     modules.insert(0,path + "\\" + i)
                #else:
                    
                    # for i in path_list:
                    #     match = [folder for folder in path_list if type(folder) is tuple]
                    #     if match:
                    #         match = [folder for folder in match if folder[0] == i]
                    #         if match:
                    #             tmp = match[0][1]
                    #         else:break
                    #     else:break
                            
                                
                    #                tree.append(path + "\\" + i)

        # importlib.reload(SE_Viewport)
        # importlib.reload(tools)
        # importlib.reload(utils)
        # importlib.reload(SE_Types)
        # importlib.reload(UI_Info)
        # #importlib.reload(UI_Property)
        # importlib.reload(Render_Property)
        # importlib.reload(SE_Datas)




        #load_modules(os.path.dirname(__file__), modules)

        
        #for i,m in enumerate(modules):
            #modules[i] = importlib.machinery.SourceFileLoader(m.split("\\")[-1][:-3], m).load_module()
            #spec = importlib.util.spec_from_file_location(m.split("\\")[-1][:-3], m)
            #modules[i] = imp.load_source(m.split("\\")[-1][:-3], m)
            #importlib.reload(i)
            #print(m)
            # if m == "J:\\Program Files\\Blender\\2.78\\scripts\\addons\\ATOM\\modules\\legacy\\ATOM_io\\Properties.py":
            #     modules[i].register()
            #     print("ok")

    

    #Properties.register()
#         for i in modules:
#             print(i)

    # for i in modules:
    #     func = getattr(i, "register", None)
    #     if not func == None:
    #         func()

    # #UI_Property.register()
    # UI_Info.register()
    # Render_Property.register()
    # tools.register()
    # SE_Viewport.register()
    # SE_Datas.register()

    # for i in modules:
    #     func = getattr(i, "unregister", None)
    #     if not func == None:
    #         func()

    # SE_Viewport.unregister()
    # #UI_Property.unregister()
    # UI_Info.unregister()
    # Render_Property.unregister()
    # #tools.unregister()
    # SE_Datas.unregister()


