
#Blender 2.5 or later to Renderman Exporter
# Copyright (C) 2011 Sascha Fricke



#############################################################################################
#                                                                                           #
#       Begin GPL Block                                                                     #
#                                                                                           #
#############################################################################################
#                                                                                           #
#This program is free software;                                                             #
#you can redistribute it and/or modify it under the terms of the                            #
#GNU General Public License as published by the Free Software Foundation;                   #
#either version 3 of the LicensGe, or (at your option) any later version.                   #
#                                                                                           #
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;  #
#without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  #
#See the GNU General Public License for more details.                                       #
#                                                                                           #
#You should have received a copy of the GNU General Public License along with this program; #
#if not, see <http://www.gnu.org/licenses/>.                                                #
#                                                                                           #
#############################################################################################
#                                                                                           #
#       End GPL Block                                                                       #
#                                                                                           #
############################################################################################

#Thanks to: Campbell Barton, Eric Back, Nathan Vegdahl

import bpy
import math
import mathutils
import os
import tempfile
import subprocess

import time

import export_renderman
from export_renderman.rm_preset_funcs import *

String = bpy.props.StringProperty
Bool = bpy.props.BoolProperty
Enum = bpy.props.EnumProperty
CollectionProp = bpy.props.CollectionProperty
Pointer = bpy.props.PointerProperty
FloatVector = bpy.props.FloatVectorProperty
IntVector = bpy.props.IntVectorProperty
Int = bpy.props.IntProperty
Float = bpy.props.FloatProperty

##################################################################################################################################
##################################################################################################################################

assigned_shaders = {}
objects_size = -1
light_list = []
light_list_size = -1
obj_passes = {}
pass_disp_len = {}

ACTIVE_MATERIAL = None
TEXTURE_FOLDERS = []

RENDER = ""

DEBUG_LEVEL = 2
DEBUG_GROUP = ["textures"]
                
def restart():
    dbprint("restart modal operator")
    global IS_RUNNING
    IS_RUNNING = False
    
def dbprint(*args, lvl=0, grp=""):
    global DEBUG_LEVEL, DEBUG_GROUP
    if lvl <= DEBUG_LEVEL and (len(DEBUG_GROUP) == 0 or grp in DEBUG_GROUP or grp == ""):
        print(*args)
        
def preview_mat():
    global ACTIVE_MATERIAL, RENDER
    return ACTIVE_MATERIAL, RENDER

def set_preview_mat(mat):
    global ACTIVE_MATERIAL
    ACTIVE_MATERIAL = mat


def adddisp(active_pass, name = "Default", display="framebuffer", var="rgba", is_aov=False, aov="", scene=None):
    defcount = 1

    def getdefname(name, count):
        countstr = "0"*(2 - len(str(count))) + str(count)
        defaultname = name+countstr
        return defaultname

    defname = getdefname(name, defcount)

    for item in active_pass.displaydrivers:
        if item.name == defname:
            defcount +=1
            defname = getdefname(name, defcount)

    active_pass.displaydrivers.add().name = defname
    dispdriver = active_pass.displaydrivers[defname]
    dispdriver.displaydriver = display
    dispdriver.var = var
    dispdriver.is_aov = is_aov
    dispdriver.aov = aov
    maintain_display_drivers(active_pass, scene)
    check_displaydrivers(scene) 
    check_display_variables(scene)
    maintain_display_options(active_pass, scene.renderman_settings)
    return defname

def checkForPath(target_path): # create Presetsdirecory if not found
    try:
        if os.path.exists(target_path):
            pass
        else:
            os.mkdir(target_path)
    except:
        pass
    
def initPasses(scene):
    rmpasses = scene.renderman_settings.passes
    for obj in scene.objects:
        #obj passes
        if obj.type == "MESH":
            atleast_one_pass(obj, rmpasses)
            #material passes
            for mslot in obj.material_slots:
                atleast_one_pass(mslot.material, rmpasses)

            #particle passes
            for psys in obj.particle_systems:
                if not psys.settings.renderman:
                    atleast_one_pass(psys.settings, rmpasses)

        #light passes
        elif obj.type == "LAMP" and not obj.data.renderman:
            atleast_one_pass(obj.data, rmpasses)
            obj.data.renderman[0].shaderpath = "pointlight"
            maintain_lamp_shaders(obj, scene)
            maintain_light(obj, scene)
                    
#########################################################################################################
#                                                                                                       #
#       functions for keeping things up-to-date                                                         #
#                                                                                                       #
#########################################################################################################
def getactivepass(scene):
    rm = scene.renderman_settings
    passes = rm.passes
    try:
        active_pass = passes[rm.passes_index]
    except IndexError:
        return None
    return active_pass
    
    
def getname(raw, name = "", pass_name = "", var = "", driver = "", dir = "", frame = "", scene = None):
    n = raw.replace('[scene]', scene.name)
    if frame != "":
        n = n.replace('[frame]', frame)
    if name != "":
        n = n.replace('[name]', name)
    if pass_name != "":
        n = n.replace('[pass]', pass_name)
    if var != "":
        n = n.replace('[var]', var)
    if driver != "":
        n = n.replace('[driver]', driver)
    if dir != "":
        n = n.replace('[dir]', dir)
    return n

def framepadding(scene):
    currentframe = scene.frame_current
    framestr = str(currentframe)
    length = len(framestr)
    padding = scene.renderman_settings.framepadding - length
    frame = padding*"0" + str(currentframe)
    return frame

def shader_info(shader, collection, scene):
    shaders = scene.renderman_settings.shaders
    shadercollection = shaders.shadercollection
    shaderpaths = shaders.shaderpaths
    if len(shaderpaths) >= 1:
        if len(shadercollection) >= 1:
            if shader in shaders.shadercollection:
                info = shaders.shadercollection[shader].fullpath
            else:
                info="No shader selected"
        else:
            info = "No shader(s) found"
    else:
        info = "No shader path(s) selected" 
        
    return info                                      

def active_layers(data, scene):
    active_layers = []
    for i in range(len(scene.layers)):
        if data.layers[i]:
            active_layers.append(i)
    return active_layers  

def check_visible(obj, scene):
    active_scene_layers = active_layers(scene, scene)
    active_obj_layers = active_layers(obj, scene)
    is_visible = False
    for active_layer in active_obj_layers:
        if active_layer in active_scene_layers:
            is_visible = True
            
    return is_visible                                  

def check_env(path):
    if path.find("$") != -1:
        path_splitters = ["/", "\\"]
        for path_splitter in path_splitters:
            if path.find(path_splitter) != -1:
                splitted_path = path.split(path_splitter)
        env_var_raw = splitted_path.pop(0)
        env_var = env_var_raw.replace("$", "")
        try:
            final_path = os.environ[env_var]
        except KeyError:
            return
        for dir in splitted_path:
            final_path = os.path.join(final_path, dir)
        return final_path
    else:
        return path 

def getdefaultribpath(scene):
    if bpy.data.filepath:
        filename = bpy.data.filepath
        defpathmain = os.path.split(filename)[0]
    else:
        defpathmain = tempfile.gettempdir()
    defaultpath = os.path.join(defpathmain, scene.name)
    if not os.path.exists(defaultpath): os.mkdir(defaultpath)
    return defaultpath

def getrendererdir(scene):
    if (scene.renderman_settings.use_env_var
        and not scene.renderman_settings.renderenvvar == ""):
        renderdir = os.environ[scene.renderman_settings.renderenvvar]
    else:
        renderdir = scene.renderman_settings.renderpath
    renderdir += "/bin/"
    return renderdir

def CB_maintain_display_drivers(self, context):
    scene = context.scene
    for rpass in scene.renderman_settings.passes:
        maintain_display_drivers(rpass, scene)
            
def maintain_display_drivers(current_pass, scene):
    rmansettings = scene.renderman_settings
        
    quant_presets = {   "8bit" : [0, 255, 0, 255],
                        "16bit" : [0, 65535, 0, 65535],
                        "32bit" : [0, 0, 0, 0]
                    }
                                        
    for display in current_pass.displaydrivers:
        disp_drv = display.displaydriver      

        if display.default_name:
            if current_pass.environment:
                display.raw_name = '[name]_[pass]_[var]_[dir]_[frame].[driver]'
            else:
                display.raw_name = '[name]_[pass]_[var][frame].[driver]'
                
        if display.quantize_presets != "other":
            quant = quant_presets[display.quantize_presets]
            
            display.quantize_min = quant[0]
            display.quantize_max = quant[1]
            display.quantize_black = quant[2]
            display.quantize_white = quant[3]
            
        n = getname(display.raw_name,
                    name = display.name,
                    pass_name = current_pass.name,
                    var = display.var,
                    driver = disp_drv,
                    scene = scene)
                    
        display.filename = n
        display.file = os.path.join(current_pass.imagedir,
                                    n).replace('\\', '\\\\')
        
        if display.processing.default_output:
            ext = checkextension(display.filename)
            disp_pr = display.processing
            finext = 'shd' if disp_pr.shadow else rmansettings.textureext 
            disp_pr.output = display.filename.replace(ext,
                                                      finext)

def update_illuminate_list(obj, scene):
    global light_list
    for objpass in obj.renderman:
        for l in light_list:
            if not l in objpass.light_list:
               objpass.light_list.add().name = l
    
        for killer, light in enumerate(objpass.light_list):
    
            if not light.name in light_list:
                objpass.light_list.remove(killer)
    
        if objpass.lightgroup:
            for item in objpass.light_list:
                if item.name in bpy.data.groups[objpass.lightgroup].objects:
                    item.illuminate = True
                else:
                    item.illuminate = False
            objpass.lightgroup = ""

def getLightList(scene):
    maintain_lists(scene)
    global light_list
    return light_list

def check_displaydrivers(scene):
    rmansettings = scene.renderman_settings
    drv_path_raw = rmansettings.displaydrvpath
    if rmansettings.disp_ext_os_default:
        if os.sys.platform == "Windows":
            drv_ext = "dll"
        else:
            drv_ext = "so"
    else:
        drv_ext = rmansettings.disp_ext
    if drv_path_raw:
        display_drivers = []
        drv_path = check_env(drv_path_raw)
        drv_dir = os.listdir(drv_path)
        for drv in drv_dir:
            if checkextension(drv) == drv_ext:                             
                if rmansettings.drv_identifier:
                    if drv.find(rmansettings.drv_identifier) != -1:
                        driver = drv.replace(rmansettings.drv_identifier, "")
                        driver = driver.replace('.'+drv_ext, "")
                else:
                    driver = drv.replace('.'+drv_ext, "")
                    
                display_drivers.append(driver)
                
        for drv in display_drivers:
            if drv not in rmansettings.displays:
                rmansettings.displays.add().name = drv
                                                                    
        for index, drv in enumerate(rmansettings.displays):
            if drv.name not in display_drivers:
                rmansettings.displays.remove(index)
        

def check_display_variables(scene):
    rmansettings = scene.renderman_settings
    var_collection = rmansettings.var_collection
    
    default_vars = ["rgb", "rgba", "a", "z", "N", 
                    "P", "Ci", "Cs", "Oi", "Os", 
                    "s", "t", "u", "v", "Ng", 
                    "E", "du", "dv", "dPtime", "dPdu", 
                    "dPdv"]
                    
    for var in default_vars:
        if not var in var_collection:
            var_collection.add().name = var
            
            
def maintain_searchpaths(current_pass, scene):
    rmansettings = scene.renderman_settings

    if not "searchpath" in rmansettings.option_groups:
        rmansettings.option_groups.add().name = "searchpath"
    if not "searchpath" in current_pass.option_groups:
        current_pass.option_groups.add().name = "searchpath"
    current_pass.option_groups['searchpath'].export = True
          
    master_searchpath = rmansettings.option_groups["searchpath"].options
    slave_searchpath = current_pass.option_groups["searchpath"].options

    def maintain_searchpath(name, value):
        if not name in master_searchpath:
            master_searchpath.add().name = name
        if not name in slave_searchpath:
            slave_searchpath.add().name = name     
        searchpath_option = master_searchpath[name]
        searchpath_option.export = True
        searchpath_option.parametertype = "string"
        searchpath_option.textparameter = value.replace('\\', '\\\\')
        
        slave = current_pass.option_groups["searchpath"].options[name]
        copy_parameter(slave, searchpath_option)
    
    texdir = rmansettings.texdir        ##texture searchpath
    global TEXTURE_FOLDERS
    if not texdir in TEXTURE_FOLDERS:
        TEXTURE_FOLDERS.append(texdir)
    
    if not current_pass.imagedir in TEXTURE_FOLDERS:
        TEXTURE_FOLDERS.append(current_pass.imagedir)
    
    paths = []
    
    texpath = ':'.join(TEXTURE_FOLDERS)
    maintain_searchpath('texture', texpath)                    

    if rmansettings.shaders.shaderpaths:                             ##shader searchpath
        shader_path_value = ""
        for shader_path in rmansettings.shaders.shaderpaths:
            shader_path_value += check_env(shader_path.name)+':'
    else:
        shader_path_value = ''
    shader_path_value += '@:&'                           
    maintain_searchpath('shader', shader_path_value) 


def sort_collection(collection):
    for i in range(len(collection)):
        if i>0:
            while collection[i].name < collection[i-1].name:
                collection.move(i, i-1)
                i -= 1

################################################################### not in use
def layer_name(current_pass, var):
    return current_pass.name  + "_" + var

def create_render_layers(current_pass, scene):
    names = []  
    for display in current_pass.displaydrivers:
        lname = layer_name(current_pass, display.var)
        if not display.displaydriver == "framebuffer":
            names.append(lname)
            
    layers = scene.render.layers            
            
    for i in range(len(names)):
        try:
            layers[i].name = names[i]  
        except:
            bpy.ops.scene.render_layer_add()
            layers[i].name = names[i] 
            
    for i in range(len(layers)):
        if not layers[i].name in names:
            scene.render.layers.active_index = i
            bpy.ops.scene.render_layer_remove()                                             
#################################################################### may delete this ... but we'll what the render api brings
             
def copy_parameters(master_groups, slave_groups, options = True):    
    for master_group in master_groups:
        slave_group = slave_groups[master_group.name]
        if options:
            masters = master_group.options
            slaves = slave_group.options
        else:
            masters = master_group.attributes
            slaves = slave_group.attributes 
                       
        for master in masters:
            slave = slaves[master.name]    
            copy_parameter(master, slave)
            
def copy_parameter(master, slave):
    master.parametertype = slave.parametertype
    master.input_type = slave.input_type
    master.use_var = slave.use_var
    master.vector_size = slave.vector_size
    master.textparameter = slave.textparameter
    master.colorparameter = slave.colorparameter   
    master.int_one[0] = slave.int_one[0]
    master.int_two[0] = slave.int_two[0]
    master.int_two[1] = slave.int_two[1]
    master.int_three[0] = slave.int_three[0]
    master.int_three[1] = slave.int_three[1]
    master.int_three[2] = slave.int_three[2] 
    master.float_one[0] = slave.float_one[0]
    master.float_two[0] = slave.float_two[0]
    master.float_two[1] = slave.float_two[1]
    master.float_three[0] = slave.float_three[0]
    master.float_three[1] = slave.float_three[1]
    master.float_three[2] = slave.float_three[2]                          

def maintain_parameters(master_groups, slave_groups, scene, options = True, obj=False):    
    for master_group in master_groups:
        if options:
            masters = master_group.options
        else:
            masters = master_group.attributes               
             
        if not master_group.name in slave_groups:
            slave_groups.add().name = master_group.name
            slave_group = slave_groups[master_group.name]
            try:
                slave_group.export = master_group.export
            except AttributeError:
                pass

        slave_group = slave_groups[master_group.name]                                      
        
        if options:    
            slaves = slave_group.options
        else:
            slaves = slave_group.attributes                     

        for master in masters:
            if not master.name in slaves:
                slaves.add().name = master.name
                slave = slaves[master.name]
                copy_parameter(slave, master)                          
                            
        sort_collection(slaves)
                            
        for index, slave in enumerate(slaves):
            if slave.name not in masters:
                slaves.remove(index)
            
    for group_index, slave_group in enumerate(slave_groups):
        if slave_group.name not in master_groups:
            dbprint("remove group", slave_group.name, slave_groups, lvl=1, grp="attropt")
            slave_groups.remove(group_index)
            
    if len(slave_groups) != len(master_groups):
        for sg in slave_groups:
            dbprint(slave_groups, len(slave_groups), "!=", master_groups, len(master_groups, lvl=1, grp="attropt"))
            slave_groups.remove(0)            
            
    sort_collection(slave_groups)    
    
def maintain_beauty_pass(scene):
    renderman_settings = scene.renderman_settings
    if len(scene.renderman_settings.passes) == 0:
        renderman_settings.passes.add().name = 'Beauty'
    beauty = renderman_settings.passes[0]
    if not beauty.displaydrivers:
        adddisp(beauty, scene=scene)
        
    if renderman_settings.passes:
        if len(renderman_settings.passes) == 1 and not renderman_settings.searchpass:
            renderman_settings.passes_index = 0
        elif renderman_settings.searchpass != "":
            for i, passes in enumerate(renderman_settings.passes):
                if passes.name == renderman_settings.searchpass:
                    renderman_settings.passes_index = i
                    renderman_settings.searchpass = ""   
        
def atleast_one_pass(path, rmpasses):
    if not path.renderman:
        print(repr(path))
        path.renderman.add().name = "Default01"
    if len(path.renderman) == 1:
        for rpass in rmpasses:
            if not rpass.name in path.renderman[0].links:
                path.renderman[0].links.add().name = rpass.name
    if path.renderman_index == -1 or path.renderman_index > len(path.renderman)-1:
        path.renderman_index = 0
    
def maintain_hiders(current_pass, scene):
    rmansettings =  scene.renderman_settings
    master_hiders = rmansettings.hider_list
    slave_hiders = current_pass.hider_list

    maintain_parameters(master_hiders, slave_hiders, scene)    
    
    if current_pass.hider == '':
        if rmansettings.default_hider in rmansettings.hider_list:
            current_pass.hider = rmansettings.default_hider
            
def maintain_display_options(rpass, rm):
    for disp in rpass.displaydrivers:
        if disp.displaydriver in rm.displays:
            for opt in rm.displays[disp.displaydriver].custom_parameter:
                if not opt.name in disp.custom_options:
                    disp.custom_options.add().name = opt.name
                    copt = disp.custom_options[opt.name]
                    copy_parameter(copt, opt)
                else:
                    copt = disp.custom_options[opt.name]
                    copt.parametertype = opt.parametertype
                    copt.type = opt.parametertype
                    copt.input_type = opt.input_type
                    copt.use_var = opt.use_var
                    copt.vector_size = opt.vector_size

            for i, copt in enumerate(disp.custom_options):
                if copt.use_var:
                    copt.textparameter = disp.var
                if copt.name not in rm.displays[disp.displaydriver].custom_parameter:
                    disp.custom_options.remove(i)


def maintain_light(light, scene):
    if light.type == "LAMP":
        global obj_passes, assigned_shaders
        rm = light.data.renderman
        if not light.name in obj_passes: obj_passes[light.name] = []
        if len(rm) != len(obj_passes[light.name]):
            if light.name in assigned_shaders:
                lshaders = assigned_shaders[light.name]
                for l in lshaders:
                    if not l in rm:
                        assigned_shaders[light.name].pop(l)
                        break
                        
        for lpass in rm:
            if not lpass.name in obj_passes[light.name]:
                obj_passes[light.name].append(lpass.name)
            shader = lpass.shaderpath
            
            parameter = lpass.light_shader_parameter
            active_parameter = light.data.renderman[light.data.renderman_index].light_shader_parameter
            light_shaders = scene.renderman_settings.shaders.light_collection
            if shader != "" and shader in light_shaders:
                type = light_shaders[shader].lamp_type
            else:
                type = "point"
            
            if type == 'spot':
                light.data.type = 'SPOT'
                light.data.shadow_method = "BUFFER_SHADOW"
        
            lrotx = light.rotation_euler[0]
            lroty = light.rotation_euler[1]
            lrotz = light.rotation_euler[2]   
            topoint = (0, 0, 1)
            
            
            cos = math.cos
            sin = math.sin
            abs = math.fabs
            radians = math.radians
            
            
            def maintainitem(name, value):
                if name in parameter:
                    active_parameter = parameter[name]
                    type = active_parameter.parametertype
                    if type == "color":
                        active_parameter.colorparameter = value
                    elif type == "float":
                        if active_parameter.vector_size == 1:
                            active_parameter.float_one[0] = value
                        elif active_parameter.vector_size == 3:
                            active_parameter.float_three[0] = value[0]
                            active_parameter.float_three[1] = value[1]
                            active_parameter.float_three[2] = value[2]
                    elif type == "integer":
                        active_parameter.int_one[0] = value
                    elif type == "string":                                       
                        active_parameter.textparameter = value
                        
            if type == 'point':
                light.data.type = 'POINT'
                if "lightcolor" in active_parameter:
                    light.data.color = active_parameter["lightcolor"].colorparameter
                if "intensity" in active_parameter:
                    light.data.energy = active_parameter["intensity"].float_one[0]
            
            elif type == 'spot':
                if "lightcolor" in active_parameter:
                    light.data.color = active_parameter["lightcolor"].colorparameter
                if "intensitiy" in active_parameter:
                    light.data.energy = active_parameter["intensity"].float_one[0]
                if "coneangle" in active_parameter:
                    if active_parameter["coneangle"].float_one[0] <= 0:
                        active_parameter["coneangle"].float_one[0] = radians(1)
                    light.data.spot_size = active_parameter["coneangle"].float_one[0]
                if "conedeltaangle" in active_parameter:
                    light.data.spot_blend = active_parameter["conedeltaangle"].float_one[0]/active_parameter["coneangle"].float_one[0]
                maintainitem("to", [0, 0, -1])
                maintainitem("from", [0, 0, 0])                
            
            elif type == 'directional':
                light.data.type = 'SUN'
                if "lightcolor" in active_parameter:
                    light.data.color = active_parameter["lightcolor"].colorparameter
                if "intensity" in active_parameter:
                    light.data.energy = active_parameter["intensity"].float_one[0]
                maintainitem("to", [0, 0, -1])     
                maintainitem("from", [0, 0, 0])                       

def objpass(p):
    try:
        rpass = p.renderman[p.renderman_index]
    except IndexError:
        rpass = None
    return rpass

def linked_pass(p, rpass):
    lpass = None
    for lp in p.renderman:
        if rpass.name in lp.links:
            lpass = lp
            
    return lpass
        

def maintain_lists(scene):
    global light_list, objects_size, assigned_shaders
    dbprint("objects in scene", objects_size, lvl=2, grp="lists")
    if not len(scene.objects) == objects_size:
        objects_size = len(scene.objects)
        assigned_shaders = {}
        dbprint("assigned_shaders reset at maintain_list()", lvl=2, grp="assigned_shaders")
        try:
            for obj in scene.objects:
                if not obj.type == 'LAMP':
                    al = False
                    if obj.active_material:
                        m = obj.active_material
                        if (objpass(m) != None) and objpass(m).arealight_shader != "":
                            al = True
                if (obj.type == 'LAMP' or al) and not obj.name in light_list:
                    light_list.append(obj.name)
                    
        except UnicodeDecodeError:
            pass
        
    for i, obj in enumerate(light_list):
        if not obj in scene.objects:
            light_list.pop(i)
        else:
            object = scene.objects[obj]
            if object.type != "LAMP":
                am = object.active_material
                if not am or objpass(am).arealight_shader == "":
                    light_list.pop(i)

class Renderman_OT_set_Active_Camera(bpy.types.Operator):
    bl_label = ""
    bl_idname = "renderman.set_active_camera"
    
    cam = String()
    
    def execute(self, context):
        context.scene.camera = context.scene.objects[self.cam]
        return {'FINISHED'}

def sync_BI_dimensions(scene):
    apass = getactivepass(scene)
    rd = scene.render
    rc = apass.renderman_camera
    rd.resolution_x = rc.resx
    rd.resolution_y = rc.resy
    rd.resolution_percentage = rc.respercentage   

def maintain_rib_structure(self, context):
    scene = context.scene
    rm = scene.renderman_settings
    rs = rm.rib_structure
    
    types = {   rs.render_pass : ["[pass]_[dir][frame]", "Passes"],
                rs.settings : ["[pass]_Settings_[dir][frame]", "Settings"],
                rs.world : ["[pass]_World_[dir][frame]", "Worlds"],
                rs.objects : ["[name]_[pass][frame]", "Objects"],
                rs.lights : ["[name]_[pass][frame]", "Lights"],
                rs.meshes : ["[name][frame]", "Meshes"],
                rs.particles : ["[name]_[pass][frame]", "Particles"],
                rs.particle_data : ["[name]_[pass][frame]", "Particle_Data"],
                rs.materials : ["[name]_[pass][frame]", "Materials"],
                rs.object_blocks : ["instances_[pass][frame]", "Instances"],
                rs.frame : ["[frame]", ""]}
    
    for p in types:            
        if p.filename == "" or p.default_name:
            p.filename = types[p][0]
        if p.folder == "":
            p.folder = types[p][1]

def maintain_world_shaders(rpass, scene):
    gs = rpass.global_shader
    cs = checkshaderparameter
    world_shaders = (   ("worldi", rpass, rpass.imager_shader, rpass.imager_shader_parameter),
                        ("worlds", rpass, gs.surface_shader, gs.surface_shader_parameter),
                        ("worlda", rpass, gs.atmosphere_shader, gs.atmosphere_shader_parameter))
    for ws in world_shaders:
        cs(ws[0], ws[1], ws[2], ws[3], scene)
        
def maintain_material_shaders(m, scene):
    cs = checkshaderparameter
    rm = m.renderman[m.renderman_index]
    obm_shd = ( (m.name+"surf", rm, rm.surface_shader, rm.surface_shader_parameter),
                (m.name+"disp", rm, rm.displacement_shader, rm.disp_shader_parameter),
                (m.name+"int", rm, rm.interior_shader, rm.interior_shader_parameter),
                (m.name+"ext", rm, rm.exterior_shader, rm.exterior_shader_parameter),
                (m.name+"al", rm, rm.arealight_shader, rm.light_shader_parameter))
    for os in obm_shd:
        cs(os[0], os[1], os[2], os[3], scene)

def maintain_lamp_shaders(l, scene):
    cs = checkshaderparameter                                
    ld = l.data
    try:
        rm = ld.renderman[ld.renderman_index]
        dbprint("check light", l.name, ":", rm.name, lvl=2, grp="maintain_lamp_shaders")
        cs(l.name, rm, rm.shaderpath, rm.light_shader_parameter, scene) 
    except IndexError:
        pass

def maintain_custom_code(rpass, rm):
    oirpass = rpass.output_images
    if rpass.world_code:
        for wc in rpass.world_code:
            p = wc.parameter
            if (p.input_type == 'display'
                and p.textparameter in oirpass
                and wc.default_output):
                txt = p.textparameter
                if wc.makeshadow:
                    wc.name = "MakeShadow"
                    wc.output = txt.replace(checkextension(txt), '.shd')
                elif wc.makecubefaceenv:
                    wc.name = "MakeCubeFaceEnvironment"
                    txt = txt.replace(checkextension(txt),
                                      '.' + rm.textureext)
                    txt = txt.replace("[dir]", "")
                    wc.output = txt

def maintain_output_images(rm, rpass):
    oirpass = rpass.output_images
    oi = rm.output_images
    for disp in rpass.displaydrivers:
        if disp.displaydriver != "framebuffer":
            if disp.processing.process and disp.processing.output != "":
                output = disp.processing.output
            else:
                output = disp.filename
            if not output in oirpass:
                oirpass.add().name = output
                oirpass[output].render_pass = rpass.name
            
            if rpass.world_code:
                for wc in rpass.world_code:
                    if (wc.parameter.input_type == 'display'
                        and wc.parameter.textparameter in oirpass
                        and (wc.makeshadow or wc.makecubefaceenv)):
                            output = wc.output
            
            if not output in oi:
                oi.add().name = output
                oi[output].render_pass = rpass.name

    for i, img in enumerate(oirpass):
        erase = True
        if img.render_pass != "" and img.render_pass in rm.passes:
            erase = False
        for disp in rpass.displaydrivers:
            if disp.processing.process and disp.processing.output != "":
                output = disp.processing.output
            else:
                output = disp.filename
            if img.name == output:
                erase = False
        if erase:
            oirpass.remove(i)    
    
    for i, img in enumerate(oi):
        erase = True
        if img.render_pass != "" and img.render_pass in rm.passes:
            erase = False
            if img.render_pass == rpass.name:
                erase = True
                for disp in rpass.displaydrivers:
                    if disp.processing.process and disp.processing.output != "":
                        output = disp.processing.output
                    else:
                        output = disp.filename
                        
                    if rpass.world_code:
                        for wc in rpass.world_code:
                            if (wc.parameter.input_type == 'display'
                                and wc.parameter.textparameter in oirpass
                                and (wc.makeshadow or wc.makecubefaceenv)):
                                    output = wc.output
                                
                    if img.name == output:
                        erase = False
        if erase:
            oi.remove(i)

shader_count = -1
def load_shaders(scene):
    rm = scene.renderman_settings
    global shader_sorted, shader_count
    scollection = rm.shaders.shadercollection

    surf_coll = rm.shaders.surface_collection
    disp_coll = rm.shaders.displacement_collection
    vol_coll = rm.shaders.volume_collection
    l_coll = rm.shaders.light_collection
    img_coll = rm.shaders.imager_collection
    
    sl = len(surf_coll)
    dl = len(disp_coll)
    vl = len(vol_coll)
    ll = len(l_coll)
    il = len(img_coll)
    listslen = sl + dl + vl + ll + il

    def copy_shader(shdname, dest):
        src_shd = scollection[shdname]
        if not shdname in dest:
            dest.add().name = shdname
            dest_shd = dest[shdname]
            dest_shd.fullpath = src_shd.fullpath
        dest_shd = dest[shdname]
        if shdname.find("distant") != -1: dest_shd.lamp_type = "directional"
        elif shdname.find("spot") != -1: dest_shd.lamp_type = "spot"
    
    if len(scollection) != shader_count or len(scollection) != listslen:
        shader_count = len(scollection)
        i = -1
        for s in scollection:
            i += 1
            tmpfile = get_shaderinfo(s.name, scollection, scene)
            if tmpfile:
                info = open(tmpfile, "r")
                i = -1
                shadertype = ""
                while True:
                    i += 1
                    line = info.readline()
                    if line != "":
                        data = line.split()
                        if len(data) == 2:
                            shadertype = data[0]
                            break
                    ## emergency break if something is wrong with the info:
                    if i > 4: break
                
                if shadertype == "surface":
                    copy_shader(s.name, surf_coll)
                elif shadertype == "volume":
                    copy_shader(s.name, vol_coll)
                elif shadertype == "light":
                    copy_shader(s.name, l_coll)
                elif shadertype == "imager":
                    copy_shader(s.name, img_coll)
                elif shadertype == "displacement":
                    copy_shader(s.name, disp_coll)

pass_preset_outputs = {}
def load_pass_presets(scene):
    active_engine = scene.renderman_settings.active_engine
    if not bpy.utils.preset_paths('renderman'):
        return;
    main_preset_path = bpy.utils.preset_paths('renderman')[0]
    preset_dir = os.path.join(main_preset_path, active_engine)

    def read_outputs(p):
        global pass_preset_outputs
        preset = p.replace(preset_dir, "")
        preset = preset.replace("\\", "/")
        preset = preset.replace(".pass", "")

        if not preset in pass_preset_outputs: ##TODO: bake textures
            outputs = []
            f = open(p, "r")
            lines = f.readlines()

            for l in lines:
                if l.find("NewDisplay") != -1:
                    outputs.append(l.split()[1])
            pass_preset_outputs[preset] = outputs
            f.close()

    def look(prdir):
        for pr in os.listdir(prdir):
            path = os.path.join(prdir, pr)
            if os.path.isdir(path):
                look(path)
            else:
                read_outputs(path)
                
    if os.path.exists(preset_dir):
        look(preset_dir)

                    
def initial_load_data(scene):
    rm = scene.renderman_settings
    load_shaders(scene)

def linkpass(rpass, scene):
    rmpasses = scene.renderman_settings.passes
    initPasses(scene)
    for obj in scene.objects:
        #obj passes
        if obj.type == "MESH":
            if linked_pass(obj, rpass) == None:
                obj.renderman[0].links.add().name = rpass.name
                
            #material passes
            for mslot in obj.material_slots:
                if mslot.material:
                    if linked_pass(mslot.material, rpass) == None:
                        mslot.material.renderman[0].links.add().name = rpass.name

            #particle passes
            for psys in obj.particle_systems:
                if linked_pass(psys.settings, rpass) == None:
                    psys.settings.renderman[0].links.add().name = rpass.name

        #light passes
        elif obj.type == "LAMP":
            if linked_pass(obj.data, rpass) == None:
                obj.data.renderman[0].links.add().name = rpass.name


def maintain_client_passes_add(obj, scene):
    rm = scene.renderman_settings
    for request_index, request in enumerate(obj.requests):
        request.index = request_index
        request.client = obj.name
        try:
            parm_path = eval('obj.'+request.name)
            output = request.output
            parm_name = parm_path.name
            dirs = ['px', 'nx', 'py', 'ny', 'pz', 'nz']
            parmdir = ""
            for dir in dirs:
                parm_name = parm_name.replace(dir, "")
                if parm_path.name.find(dir) != -1:
                    parmdir = dir
            rpass_name = "_".join([request.client, parm_name, output])
            request.pass_name = rpass_name
            if not rpass_name in rm.passes:
                dbprint(rpass_name, lvl=1, grp="rpass")
                rm.passes.add().name = rpass_name
                rpass = rm.passes[rpass_name]
                rpass.client = obj.name
                rpass.camera_object = obj.name
                rpass.requested = True
                invoke_preset(rpass, request.preset, scene)
                linkpass(rpass, scene)
                maintain_render_passes(scene)
                
                cl_pass_index = -1
                render_pass_index = -1
                for i in range(len(rm.passes)):
                    if rm.passes[i] == rpass:
                        cl_pass_index = i
                    elif rm.passes[i].name == request.render_pass:
                        render_pass_index = i
                rm.passes.move(cl_pass_index, render_pass_index)
                
            rpass = rm.passes[rpass_name]

            if obj.type == 'LAMP':
                objpass = obj.data.renderman[request.request_pass]
                objshader = rm.shaders.light_collection[objpass.shaderpath]
            if ((obj.type not in ["CAMERA", "LAMP"])
               or (obj.type == "LAMP" and objshader.lamp_type not in ['directional', 'spot'])):
                rpass.environment = True
            else:
                rpass.environment = False
                    
            dbprint(request.name, lvl=1, grp="requests")
            out_disp = rpass.displaydrivers[output]
            if out_disp.processing.process and out_disp.processing.output != "":
                o = out_disp.processing.output
            else:
                o = out_disp.filename
            parm_path.textparameter = o.replace("[dir]", parmdir)
        except KeyError:
            obj.requests.remove(request_index)
    
def maintain_client_passes_remove(scene):
    rm = scene.renderman_settings
    for i, rpass in enumerate(rm.passes):
        if rpass.requested:
            if rpass.client != "" and (not rpass.client in scene.objects):
                dbprint("removing", rpass, "01", lvl=1, grp="requests")
                scene.renderman_settings.passes.remove(i)
            elif rpass.client != "":
                exists = False
                for request in scene.objects[rpass.client].requests:
                    if request.pass_name == rpass.name:
                        exists = True
                if not exists:
                    scene.renderman_settings.passes.remove(i)
                    dbprint("removing", rpass, "02", lvl=1, grp="requests")
            else: ##a rpass is a client
                exists = False
                for request in scene.renderman_settings.requests:
                    if rpass.name == request.pass_name:
                        exists = True
                if not exists:
                    scene.renderman_settings.passes.remove(i)
                    dbprint("removing", rpass, "03", lvl=1, grp="requests")

def maintain_textures(scene):
    for tex in bpy.data.textures:
        if tex.renderman.type == "file":
            image = tex.image
            if image.source == 'GENERATED':
                image.filepath = os.path.join(getdefaultribpath(scene), image.name)
                image.save()

def maintain_render_passes(scene):
    #scene = context.scene
    rm = scene.renderman_settings
    maintain_textures(scene)
    for rpass in rm.passes:
        #maintain_shutter_types(rpass, scene)
        #maintain_world_shaders(rpass, scene)
        maintain_display_drivers(rpass, scene)
        maintain_output_images(rm, rpass)
        #maintain_hiders(rpass, scene)
#       create_render_layers(rpass, scene)
        maintain_searchpaths(rpass, scene)
        maintain_display_options(rpass, rm)
        maintain_custom_code(rpass, rm)

def CB_m_render_passes(self, context):
    maintain_render_passes(context.scene)
    

def maintain_shutter_types(self, context):
    rpass = context.scene.renderman_settings.passes[context.scene.renderman_settings.passes_index]
    fps = context.scene.render.fps
    ang = math.degrees(rpass.shutterspeed_ang)
    sec = rpass.shutterspeed_sec
    if rpass.shutter_type == "angle":
        rpass.shutterspeed_sec = (ang/360) * (1/fps)
    else:
        rpass.shutterspeed_ang = math.radians(360 * fps * sec)

def maintain_max_shutterspeed(self, context):
    rpass = context.scene.renderman_settings.passes[context.scene.renderman_settings.passes_index]
    fps = context.scene.render.fps
    ang = math.degrees(rpass.shutterspeed_ang)
    sec = rpass.shutterspeed_sec
    if sec > 1/fps:
        rpass.shutterspeed_sec = 1/fps
        
def maintain_surface_color(mat):
    rm = mat.renderman[mat.renderman_index]
    mat.diffuse_color = rm.color
    
def maintain_texture_type(context, scene):
    for tex in bpy.data.textures:
        types_dict = {"file" : "IMAGE", "none" : "NONE", "bake" : "NONE"}
        if hasattr(tex, "renderman"):
            tex.type = types_dict[tex.renderman.type]
        
def maintain(scene):
    if scene.render.engine == 'RENDERMAN':
        global RENDER

        rm = scene.renderman_settings
        
        ##### Render Passes
        for i, rpass in enumerate(rm.passes):
            maintain_render_passes(rpass, scene)

        ##### Objects
        for obj in scene.objects:
            atleast_one_pass(obj, rm.passes)
            maintain_client_passes_add(obj, scene)
            ###### Lights
            if obj.type == 'LAMP':
                pass
    
            else:
                ##### Particle Systems
                for ps in obj.particle_systems:
                    atleast_one_pass(ps.settings, rm.passes)
                ##### Materials
                for m in obj.material_slots:
                    atleast_one_pass(m.material, rm.passes)
                    maintain_surface_color(m.material)
                    maintain_material_shaders(m.material, scene)
                    for t in m.material.texture_slots:
                        if hasattr(t, "texture"):
                            maintain_texture_type(t.texture)
                update_illuminate_list(obj, scene)
            
        sort_collection(scene.renderman_settings.hider_list)
        for hider in scene.renderman_settings.hider_list:
            sort_collection(hider.options)  


def checkextension(file):
    if file.find(".") == -1: return file
    file_array = file.split(".")
    file_array_len = len(file_array)
    file_extension = file_array[file_array_len-1]
    return file_extension


def write_shaderinfo(shader_path, tmp_path, shadinfo):
    file = open(tmp_path, "w")
    dbprint("preparing shader", shader_path, lvl=1, grp="shaderinfo")
    subprocess.Popen([shadinfo, shader_path], stdout=file).communicate()
    file.close()


def get_shaderinfo(shader, shadercollection, scene):
    tmpdir = tempfile.gettempdir()
    tmpfilename = shader+".tmp"
    fulltmpname = os.path.join(tmpdir, tmpfilename)
    mod_time = shadercollection[shader].mod_time
    shadinfo = scene.renderman_settings.shaderinfo
        
    ###### Binary Shader
    try:
        fullshaderpath = shadercollection[shader].fullpath
    except:
        fullshaderpath = ""      
        clear_shader_parameter(shader_parameter)
        
    if fullshaderpath:
        if not os.path.exists(fulltmpname):
            write_shaderinfo(fullshaderpath, fulltmpname, shadinfo)
            return fulltmpname
        else:
            modtime_new = math.floor(os.path.getmtime(fullshaderpath))
            if modtime_new != mod_time:
                write_shaderinfo(fullshaderpath, fulltmpname, shadinfo)
                scene.renderman_settings.shaders.shadercollection[shader].mod_time = modtime_new
    return fulltmpname


def checkshadercollection(scene):
    try:
        shaders = scene.renderman_settings.shaders

        for shader in shaders.shadercollection:
            shaders.shadercollection.remove(0)
    except:
        return

    try:
        shadbin = scene.renderman_settings.shaderbinary
    except:
        return

    def addshader(path):
        for item in os.listdir(path):
            fullpath = os.path.join(path, item)
            shadext = checkextension(item)
            if shaders.shadercollection:
                exist = False
                for shader in shaders.shadercollection:
                    if fullpath == shader.fullpath:
                        exist = True

                if not exist and shadext == shadbin:
                    shaders.shadercollection.add().fullpath = fullpath
            else:
                if shadext and shadext == shadbin:
                    shaders.shadercollection.add().fullpath = fullpath


    for path in shaders.shaderpaths:
        path_name = check_env(path.name)
        if os.path.exists(path_name):
            current_path = path_name
            checksubdir = True

            addshader(path_name)

    
    for item in shaders.shadercollection:
        if item.name == "":
            item.name = os.path.split(item.fullpath)[1].replace('.'+shadbin, '')

def clear_shader_parameter(shader_parameter):
    for i in range(len(shader_parameter)):
        shader_parameter.remove(0)

def checkshaderparameter(identifier, active_pass, shader, shader_parameter, scene):
    var_collection = scene.renderman_settings.var_collection
    global assigned_shaders
            
    def addparameter(parameter, shader_parameter, value):
        parmname = parameter[0]
        for i, p in enumerate(parameter):
            if p.find("parameter") != -1 or p.find("output") != -1:
                parameter.pop(i)

        type = parameter[1] + " " + parameter[2]
        shader_parameter.add().name = parmname
        ap = shader_parameter[parmname]
        ap.type = type
        if "color" in parameter:
            ap.parametertype = "color"
            value = value.split()
            ap.colorparameter[0] = float(value[0])
            ap.colorparameter[1] = float(value[1])
            ap.colorparameter[2] = float(value[2])
        elif "float" in parameter:
            ap.parametertype = "float"
            ap.vector_size = 1
            ap.float_one[0] = float(value)
            
        elif "point" in parameter or "normal" in parameter or "vector" in parameter:
            ap.parametertype  = "float"
            ap.vector_size = 3
            value = value.split()
            ap.float_three[0] = float(value[0])
            ap.float_three[1] = float(value[1])
            ap.float_three[2] = float(value[2])

        elif "string" in parameter:
            dbprint(parameter, lvl=2, grp="addshaderparameter")
            value = value.replace('"', "")
            value = value.replace(" ", "")
            value = value.replace("\t", "")
            value = value.replace("\n", "")
            ap.textparameter = value

    def readparms():
        parameters = []
        values = []
        tmpfile = open(fulltmpname, "r")
        textlines = tmpfile.readlines()
        tmpfile.close()
        for i, line in enumerate(textlines):
            if len(line.split()) == 0:
                textlines.pop(i)
        try:       
            textlines.pop(0)
        except IndexError:
            assigned_shaders = {}
            dbprint("assigned_shaders reset at readparms()", lvl=2, grp="assigned_shaders")
            return 0
        [parameters.append(p) for p in textlines if p.find("Default value") == -1]
        parameters = [parameter.replace('\n', '') for parameter in parameters]
        parameters = [parameter.replace('\t', '') for parameter in parameters]
        parameters = [parameter.replace('"', '') for parameter in parameters]
        [values.append(v) for v in textlines if not v.find("Default value") == -1]
        
        if shader_parameter:
            old_removed = False
            i = -1
            removing = False
            while not old_removed:
                i += 1
                if i < len(shader_parameter):
                    there = False
                    p = shader_parameter[i]
                    for parameter in parameters:
                        try:
                            pname = parameter.split()[0]
                        except:
                            dbprint(parameter, lvl=2, grp="readshaderparameter")
                        if pname == p.name:
                            there = True
                    if not there:
                        dbprint("removing", shader_parameter[i], lvl=2, grp="removeshaderparameter")
                        shader_parameter.remove(i)
                        removing = True
                else:
                    if not removing:
                        old_removed = True
                        break
                    else:
                        removing = False
                        i = -1
        
        index = 0
        aovs = 0
        for p in parameters:
            if p.find("output") != -1:
                p = p.split()
                pname = p.pop(0).replace('"', '')
                for i, pp in enumerate(p):
                    if pp.find("output") != -1:
                        p.pop(i)
                if not pname in var_collection:
                    var_collection.add().name = pname
                aovar = var_collection[pname]
                type = " ".join(p).replace("parameter", "")
                dbprint(type, pname, lvl=2, grp="aov")
                aovar.type_ = type[1:]
                aovs += 1
            
            
        while True:
            dbprint(len(parameters)-aovs, len(shader_parameter), index, lvl=2, grp="addshaderparameter")
            if len(parameters)-aovs <= len(shader_parameter):
                break
            parameter = parameters[index]
            try:
                value = values[index]
            except:
                break
            
            value = value.replace("Default value:", "")
            if value.find('[') != -1:
                value = value[value.find("["):value.find("]")]
                value = value.replace('[', '')
            
            parm = parameter.split()
            dbprint(parm[0], lvl=2, grp="shader")
            if not parm[0] in shader_parameter and parameter.find("output") == -1:
                dbprint("adding parameter", parm, shader_parameter, active_pass, lvl=2, grp="addshaderparameter")
                addparameter(parm, shader_parameter, value)
            if index == len(parameters)-1:
                index = 0
            else:
                index += 1
        
        parmnames = []
        [parmnames.append(parm.split()[0]) for parm in parameters]
        for killer, item in enumerate(shader_parameter):
            if item.name not in parmnames:
                shader_parameter.remove(killer) 
        return parameters, values
                
    def check_curr_shader(current_shader):
        if not active_pass.name in current_shader or current_shader[active_pass.name] != shader:
            dbprint("reading03", "shaders of curr. id:",current_shader, "pass:",active_pass, "id:",identifier, lvl=2, grp="checkshaderparameter")
            readparms()
            current_shader[active_pass.name] = shader
        return current_shader

    shadercollection = scene.renderman_settings.shaders.shadercollection
    if not shader in shadercollection:
        clear_shader_parameter(shader_parameter)
        return
    
    tmpdir = tempfile.gettempdir()
    tmpfilename = shader+".tmp"
    fulltmpname = os.path.join(tmpdir, tmpfilename)
    mod_time = shadercollection[shader].tmp_mod_time 
        
    if fulltmpname:
        if not os.path.exists(fulltmpname):
            get_shaderinfo(shader, shadercollection, scene)
            dbprint("reading01", lvl=2, grp="shaderinfo")
            readparms()
        else:
            modtime_new = math.floor(os.path.getmtime(fulltmpname))
            dbprint(assigned_shaders, lvl=2, grp="assigned_shaders")
            if modtime_new != mod_time:
                get_shaderinfo(shader, shadercollection, scene)
                dbprint("reading02", modtime_new, "!=", mod_time, "of", shader, "at", identifier, ",", active_pass, lvl=2, grp="shaderinfo")
                readparms()
                scene.renderman_settings.shaders.shadercollection[shader].tmp_mod_time = modtime_new
                
            if not identifier in assigned_shaders or assigned_shaders[identifier] != check_curr_shader(assigned_shaders[identifier]):
                dbprint("check_curr_shader() for", identifier, lvl=2, grp="checkshaderparameter")
                cs = check_curr_shader({})
                assigned_shaders[identifier] = cs
                
    sort_collection(shader_parameter)                   

##################################################################################################################################


    
