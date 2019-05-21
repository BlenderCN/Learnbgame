import types
import sys
import os
import inspect
import importlib
import imp
import copy
import zipimport, zipfile
import shutil
import fnmatch
import configparser
import ast
import functools
import socket
from SDK_utils_types import *
import struct
import _thread
import time
import numpy

ROOT = os.path.dirname(__file__)

def registerpath():
    frame = list(sys._current_frames().values())[0]
    while True:
        try:frame = frame.f_back
        except:break
        module = inspect.getmodule(frame)
        if not module == None:
            sys.path.append(os.path.dirname(module.__file__))
            break
            
def get_stdin(msg=""):
    if sys.stdin.isatty():
        return input(msg)
    return "/n".join(sys.stdin)

def token(value):
    try:
        return ast.literal_eval(value)
    except:
        return value

def parse_args(args):
    default = []
    params = {}
    for i in args:
        if i.startswith("--"):
            value = i.split("=")
            if len(value) == 2:
                params[value[0][2:]] = token(value[1])
        elif i.startswith("-"):
            params[i[1:]] = True
        else:
            default.append(token(i))
    return params, default
    
def load_module(module_name):

    if os.path.exists(module_name):
        sys.path.append(os.path.dirname(module_name))
        module_name = os.path.basename(module_name)
        
    try:
        module = __import__(module_name, globals(), locals())
    except Exception as ex:
        print("Could not load module %s :"%module_name, ex)
        module = module_name
        
    return module

class Node:

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            self.__setattr__(key, value)
        
class Config:
    
    def __init__(self, path, **kwargs):

        self.__file = path
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(path)
        config.add_section("env")

        config.set("env", "ROOT", os.path.dirname(path))
        
        for k,v in kwargs.items():
            config.set("env", k, v)

        for section in config.sections():
            if not section == "DEFAULT":
                self.__setattr__(section, Node(**{k:token(v) for k,v in config.items(section)}))

class Addon:

    @staticmethod
    def list_extentions(path):
        list = []
        for root, dir, files in os.walk(path):
            if "__init__.py" in files:
                full_path = os.path.join(root, "__init__.py")
                addon_name = os.path.basename(root)
                spec = importlib.util.spec_from_file_location(addon_name, full_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                list.append(mod)
        return list

def switch(cls):
    cls.__cases = {}
    cls.__default = None
    @classmethod
    def get_callback(cls,id):
        return cls.__cases.get(id, cls.__default)
    cls.get_callback = get_callback
    for method in cls.__dict__.values   ():
        id = getattr(method, "__id", None)
        if not id == None:
            cls.__cases[id] = method
            continue
        if hasattr(method, "__default"):
            cls.__default = method
    return cls

def case(id):
    def factory(callback):
        callback.__id = id
        return callback
    return factory

def default(callback):
    callback.__default = True
    return callback

class ProtocolStack:
    pass

@switch
class RPC(ProtocolStack):

    def __init__(self, in_port=8001, out_port=8002, password=None, max_buffer=1024):

        self.__in_port = in_port
        self.__out_port = out_port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setblocking(False)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)


        self.__socket.bind(("", in_port))
        #self.__socket.listen(1)
        self.__max_buffer = max_buffer
        self.__connection = None
        self.__address = None
        self.__lock = _thread.RLock()

        #self.connect()

    def connect(self):
        def wait_connection(self):
            conn , addr = self.__socket.accept()
            with self.__lock:
                self.__connection = conn
                self.__address = addr
                self.__connection.setblocking(False)

        _thread.start_new_thread(wait_connection, (self,))
    
    def check_connection(func):
        def wrapper(self):
            with self.__lock:
                if not self.__connection == None:
                    return func(self)
        return wrapper

    #@check_connection
    def update(self):
        while True:
            try:
                data, addr = self.__socket.recvfrom(self.__max_buffer)
            except:
                break

            # if data == b"":
            #     self.__connection.close()
            #     print("disconnected")
            #     self.connect()
            #     break

            callback = self.__class__.__bases__[0].get_callback(data[0])
            if not callback == None:
                callback(self, data[1:])


    def send(self, data):
        if not self.__connection == None:
            self.__socket.sendto(data, ("localhost", self.__out_port))
            #self.__connection.send(data)
    
    @case(CALL)
    def call(self, data):
        function_id = struct.unpack("=H",data[:2])[0]
        callback = self.get_callback(function_id)
        if not callback == None:
            callback(self, data[2:])

    @case(GET)
    def get(self, data):
        format  = data[0]
        key     = data[1:].decode("utf-8")
        if hasattr(self, key):
            value = self.__getattribute__(key)
            self.__connection.send(struct.pack(format, value))
    
    @case(SET)
    def set(self, data):
        fmt_len = data[0]
        format  = data[1:fmt_len].decode("utf-8")
        dat_len = struct.calcsize(format)
        d_start = fmt_len+1
        datas   = struct.unpack(format, data[d_start:dat_len])
        key     = data[d_start + dat_len:]
        if hasattr(self, key):
            if len(datas) == 1:
                datas = datas[0]
            self.__setattr__(key, datas)

def loop(looptime):
    def factory(func):
        args = inspect.getargspec(func)
        flag = ("deltatime" in args[0] or not args[2] == None)
        def wrapper(*args, **kwargs):
            deltatime = time.clock() - wrapper.starttime
            wrapper.starttime = time.clock()
            if flag:
                kwargs["deltatime"] = deltatime
            ret = func(*args, **kwargs)
            exectime = time.clock() - wrapper.starttime
            time.sleep(max(0,looptime-exectime))
            return ret
        wrapper.__setattr__("starttime", 0)
        return wrapper
    return factory

def feed(var):
    def factory(func):
        def wrapper(*args, **kwargs):
            var = func(*args, **kwargs)
        return wrapper
    return factory

def feed_lock(var, lock):
    def factory(func):
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            with lock:
                var = ret
        return wrapper
    return factory

def lock(lock):
    def factory(func):
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return factory

def repeat(func):
    def wrapper(*args,**kwargs):
        while True:
            func(*args, **kwargs)
    return wrapper

def delay(event, timeout=1):
    def factory(func):
        def wrapper(*args, **kwargs):
            while True:
                flag = event.wait(timeout)
                event.clear()
                if flag is True:
                    continue
                return func(*args, **kwargs)
        return wrapper
    return factory

def sign(x):
    return (x>0)-(x<0)

def Lerp(a, b, bias):
    return a*bias + b*(1-bias)

def length(array):
    return numpy.linalg.norm(array)

def normalize(array):
    vec_len = length(array)
    if not vec_len:
        return array
    return array / vec_len

def main(*args, **kwargs):
    def factory(cls):
        cls(*args, **kwargs)
    return factory

def async(func):
    def wrapper(*args, **kwargs):
        _thread.start_new_thread(func, args, kwargs)
    return wrapper

def enum_variables(text, start="{", end="}"):
    import re
    regex = r"\%s(.*?)\%s"%(start, end)
    matches = re.findall(regex, text)
    for match in matches:
        yield match

def copy_function(func):
    import functools
    new_func = types.FunctionType(  func.__code__,
                                    func.__globals__,
                                    name=func.__name__,
                                    argdefs=func.__defaults__,
                                    closure=func.__closure__)

    new_func = functools.update_wrapper(new_func, func)
    new_func.__kwdefaults__ = func.__kwdefaults__
    return new_func

def register(func):
    setattr(func, "_register")
    return func

def unregister(func):
    setattr(func, "_unregister")
    return func
    
def registerclass(cls):
    import inspect

    module = inspect.getmodule(cls)
    
    def register():
        for i in dir(module):
            if inspect.isclass(i):
                reg_func = getattr(i, "_reg_func")
                if not reg_func == None:
                    reg_func(i)
        
    def unregister():
        for i in dir(module):
            if inspect.isclass(i):
                unreg_func = getattr(i, "_unreg_func")
                if not unreg_func == None:
                    unreg_func(i)

    if not hasattr(module, "reregister")
        setattr(module, "register", register)

    if not hasattr(module, "unregister")
        setattr(module, "unregister", unregister)

    import bpy
    reg_func = bpy.utils.register_class
    unreg_func = bpy.utils.unregister_class

    for method in dir(cls):
        if method.__name__.startwith("__"):
            continue
        if hasattr(method, "_register"):
            reg_func = method
        elif hasattr(method, "_unregister"):
            unreg_func = method

    setattr(cls, "_reg_fun", reg_func)
    setattr(cls, "_unreg_fun", unreg_func)

    return cls

    # @persistent
    # def load_addons(dummy):

    #     bpy.ops.wm.addon_refresh()

    #     bpy.app.handlers.load_post.remove(Addon.load_addons)

    #     if ATOM.extentions:
    #         for i in ATOM.extentions:
    #             print(i)
    #             bpy.ops.wm.addon_enable(module=i)
        
    #     bpy.ops.wm.save_userpref()

    #     return None

    # @staticmethod  
    # def check_addon(code):
        
    #     try:
    #         offset = code.index("bl_info")
    #     except ValueError:
    #         return None

    #     if code[offset-1] == "\n":  
    #         no_name = code[offset+7:].replace(" ", "").replace("\t", "").replace("\n","").replace("\r", "")

    #         if no_name[0] == "=" and no_name[1] == "{":  
    #             bracket_count = 0
    #             for i,c in enumerate(no_name[2:]):
    #                 if c == "{":
    #                     bracket_count += 1
    #                     continue
    #                 if c == "}":
    #                     if bracket_count:
    #                         bracket_count -= 1
    #                     else:
    #                         try:
    #                             exec("dic = %s"%no_name[1:i+3])
    #                         except SyntaxError:
    #                             return None
    #                         var = locals()["dic"]
    #                         if isinstance(var, dict):
    #                             if "name" in var:
    #                                 return var

    # if config.DEBUG:
        
    #     @staticmethod
    #     def install_addons(path, mode):

    #         list = []
    #         dest_root = None

    #         def search(path, out):
                
    #             if "__init__.py" in os.listdir(path):
    #                 full_path = os.path.join(path, "__init__.py")
    #                 if os.path.isfile(full_path):
    #                     spec = importlib.util.spec_from_file_location("__init__", full_path)
    #                     mod = importlib.util.module_from_spec(spec)
    #                     spec.loader.exec_module(mod)
    #                     if hasattr(mod, "bl_info"):
    #                         addon_name = os.path.basename(path)
    #                         out_dir = os.path.join(out, addon_name)
    #                         if os.path.exists(out_dir):
    #                             shutil.rmtree(out_dir)
    #                         shutil.copytree(path, out_dir)
    #                         list.append(addon_name)
    #             else:
    #                 for i in os.listdir(path):
    #                     full_path = os.path.join(path, i)
    #                     if os.path.isfile(full_path):
    #                         if i[-3:] == ".py":
    #                             spec = importlib.util.spec_from_file_location(i[:-3], full_path)
    #                             mod = importlib.util.module_from_spec(spec)
    #                             spec.loader.exec_module(mod)
    #                             if hasattr(mod, "bl_info"):
    #                                 shutil.copy(full_path, out)
    #                                 list.append(i[:-3])
    #                     else:
    #                         search(full_path, out)

    #         if mode == ATOM_Types.InstallMod.USER:
    #             dest_root = os.path.join(os.environ['APPDATA'], "Roaming", "Blender Foundation", "Blender", bpy.app.version_string, "scripts", "addons")
    #             if not os.path.exists(dest_root):
    #                 try:
    #                     os.makedirs(dest_root)
    #                 except os.error:
    #                     raise "Cannot create install directory : %s"%sys.exc_info()[1]
                            
    #         if mode == ATOM_Types.InstallMod.LOCAL:
    #             dest_root = os.path.join(bpy.utils.script_path_user(), "addons")
            
    #         if dest_root:
    #             search(path, dest_root)

    #         return list

    # else:
    #     @staticmethod
    #     def install_addons(path, mode):
            
    #         addon_list = []

    #         if mode == ATOM_Types.InstallMod.USER:
    #             dest_root = os.path.join(os.environ['APPDATA'], "Roaming", "Blender Foundation", "Blender", bpy.app.version_string, "scripts", "addons")
    #             if not os.path.exists(dest_root):
    #                 try:
    #                     os.makedirs(dest_root)
    #                 except os.error:
    #                     raise "Cannot create install directory : %s"%sys.exc_info()[1]

    #         if mode == ATOM_Types.InstallMod.LOCAL:
    #             dest_root = os.path.join(bpy.utils.script_path_user(), "addons")

    #         for root, dir, files in os.walk(path):

    #             for file in files:

    #                 full_path = os.path.join(root, file)

    #                 if file[-3:] == ".py" and not file == "__init__.py":
    #                     dic = check_addon(open(full_path, "r").read())
    #                     if not dic == None:
    #                         if 
    #                         shutil.copy(full_path, dest_root)
    #                         addon_list.append(file[:-3])
    #                     continue

    #                 if file[-4:] == ".zip":

    #                     zip_file = zipfile.ZipFile(full_path)
    #                     elements = zip_file.namelist()

    #                     if "__init__.py" in elements:
    #                         out_path = os.path.join(dest_root, file[:-4])
    #                         if check_addon(zip_file.read("__init__.py").decode("utf-8")) == None:
    #                             continue
    #                         else:
    #                             addon_list.append(file[:-4])
    #                         if not os.path.exists(out_path):
    #                             try:
    #                                 os.makedirs(out_path)
    #                             except os.error:
    #                                 raise "Cannot create install directory : %s"%sys.exc_info()[1]
    #                                 continue
    #                     else:
    #                         out_path = dest_root
    #                         match = fnmatch.filter(elements, "*/__init__.py")
    #                         if match:
    #                             folder = os.path.join(full_path, match[0])
    #                             if check_addon(zip_file.read(match[0]).decode("utf-8")) == None:
    #                                 continue
    #                             else:
    #                                 addon_list.append(match[0][:-12])
    #                         else:
    #                             continue

    #                     zip_file.extractall(out_path)
    #                     zip_file.close()

    #         return addon_list

    # @staticmethod
    # def pack_addons(path, out):
        
    #     if "__init__.py" in os.listdir(path):
    #         full_path = os.path.join(path, "__init__.py")
    #         if os.path.isfile(full_path):
    #             spec = importlib.util.spec_from_file_location("__init__", full_path)
    #             mod = importlib.util.module_from_spec(spec)
    #             spec.loader.exec_module(mod)
    #             if hasattr(mod, "bl_info"):
    #                 shutil.make_archive(os.path.join(out,os.path.basename(path)),"zip", path)
    #     else:
    #         for i in os.listdir(path):
    #             full_path = os.path.join(path, i)
    #             if not os.path.isfile(full_path):
    #                 Addon.pack_addons(full_path, out)