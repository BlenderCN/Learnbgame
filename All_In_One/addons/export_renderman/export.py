
# Blender 2.5 or later to Renderman Exporter
# Copyright (C) 2011 Sascha Fricke

#############################################################################
#                                                                           #
#       Begin GPL Block                                                     #
#                                                                           #
#############################################################################
#                                                                           #
# This program is free software;                                            #
# you can redistribute it and/or modify it under the terms of the           #
# GNU General Public License as published by the Free Software Foundation;  #
# either version 3 of the LicensGe, or (at your option) any later version.  #
#                                                                           #
# This program is distributed in the hope that it will be useful, but       #
# WITHOUT ANY WARRANTY;                                                     #
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A     #
# PARTICULAR PURPOSE.                                                       #
# See the GNU General Public License for more details.                      #
#                                                                           #
# You should have received a copy of the GNU General Public License along   #
# with this program;                                                        #
# if not, see <http://www.gnu.org/licenses/>.                               #
#                                                                           #
#############################################################################
#                                                                           #
#       End GPL Block                                                       #
#                                                                           #
#############################################################################

#Thanks to: Campbell Barton, Eric Back, Nathan Vegdahl

#############################################################################
#                                                                           #
#       Export data functions                                               #
#                                                                           #
#############################################################################

import export_renderman
import export_renderman.rm_maintain
from export_renderman.rm_maintain import *

import bpy
from math import *

exported_instances = []
exported_files = [] 
current_pass = base_archive = active_archive = None
direction = ""

def rib_apnd(*args):
    global active_archive
    active_archive.rib(*args)
    
def ribnl():
    rib_apnd("")

def create_child(data_path, type=""):
    global active_archive
    return Archive(data_path=data_path, parent_archive=active_archive, type=type)


def close_all():
    global base_archive, exported_instances, exported_files
    def close(ar):
        ar.close()
        for ch in ar.child_archives:
            close(ch)
    close(base_archive)
    base_archive = None

def set_parent_active():
    global active_archive
    dbprint("leaving file:", active_archive.filepath, grp="Archive", lvl=2)
    active_archive = active_archive.parent_archive
    dbprint("now writing to file:", active_archive.filepath, grp="Archive", lvl=2)

def check_skip_export():
    global base_archive, exported_files, active_archive
    if active_archive.relative_filepath in exported_files:
        return True

    return not active_archive.rs.overwrite

class Archive():    # if specified open a new archive
                    # otherwise link to the parents file handle
    '''
    Class to manage structure of RIB Archives.
    '''

    def __init__(self,
                 data_path=None,
                 parent_archive=None,
                 filepath="",
                 scene=None,
                 custom_frame=False,
                 frame=0.0,
                 type=""):

        self.rib_code = [] #cached rib code for this archive
        self.child_archives = []
        self.type = ""

        global base_archive, active_archive, direction, current_pass

        #set this archive to the base archive if none is set
        if not base_archive: 
            base_archive = self
            if not data_path:
                data_path = self.data_path = self.scene = scene

        self.type = type
        self.filepath = filepath
        self.data_path = data_path
        self.parent_archive = parent_archive

        active_archive = self #convenient way to access the current rib file

        name = ""
        parent_name = ""
        parent_type =""
        try:
            name = self.data_path.name
            parent_name = self.parent_archive.data_path.name
            parent_type = self.parent_archive.type
        except:
            pass

        dbprint("active archive is", self.type, name, "parent:", parent_type, parent_name, lvl=2, grp="archive")

            
        if scene == None:
            scene = self.scene = base_archive.scene
        else:
            self.scene = scene

        if custom_frame:
            self.frame = frame
        else:
            self.frame = scene.frame_current
        
        rm = scene.renderman_settings
        
        rs_base = rm.rib_structure
        
        types = {'Object': rs_base.objects,
                 'Material': rs_base.materials,
                 'MESH': rs_base.meshes,
                 'LAMP': rs_base.lights,
                 'Pass': rs_base.render_pass,
                 'Settings': rs_base.settings,
                 'World': rs_base.world,
                 'Particle System': rs_base.particles,
                 'Particle Data': rs_base.particle_data,
                 'Frame' : rs_base.frame,
                 'Instances' : rs_base.object_blocks}
           
        base_path = getdefaultribpath(scene)
        if type == "":
            type = self.type = data_path.rna_type.name
            
        self.rs = rs = types[type]
        pname =""
        if type in ["Particle System", "Particle Data"]:
            prop_path = data_path.settings
        elif type == "LAMP" and data_path.type == 'LAMP':
            prop_path = data_path.data
        else:
            prop_path = data_path
            
        
        if self.type in ['Pass', 'Settings', 'World', 'Instances']:
            pname = current_pass.name
        elif self.type in ['MESH', 'Frame']:
            pname = ''
        elif filepath == "":
            dbprint("trying to get linked pass for this object", lvl=2, grp="archive")
            lp = linked_pass(prop_path, current_pass)
            if lp == None:
                return
            pname = lp.name
            dbprint("linked pass is", pname, lvl=2, grp="archive")
        try:
            objname = data_path.name
        except AttributeError:
            objname = ""

        if custom_frame:
            frame_str = str(self.frame)
        else:
            frame_str = framepadding(scene)

        name = getname(rs.filename,
                       name=objname,
                       pass_name=pname,
                       frame=frame_str,
                       scene=scene) + '.rib'

        name = name.replace("[dir]", direction)
        self.relative_filepath = os.path.join(rs.folder, name)
            
        filepath = os.path.join(base_path, self.relative_filepath)
        
        if rs.own_file:
            self.filepath = filepath
            dbprint("new file:", filepath, grp="Archive", lvl=2)
            if parent_archive != None:
                if (type == "MESH"
                    and prop_path.export_type == 'DelayedReadArchive'):
                    bound_box = 'DelayedReadArchive "'
                    bound_box += self.relative_filepath.replace('\\', '\\\\')+ '" ['
                    for bound in obj.bound_box:
                        bound_box +=[" ".join(str(b)) for b in bound] + "]"
                    parent_archive.rib(bound_box)
                else:
                    parent_archive.rib('ReadArchive', '"' + self.relative_filepath.replace('\\', '\\\\')+ '"')
                    
        if parent_archive != None:
            parent_archive.child_archives.append(self)
            
    def rib(self, *args):
        if self.rs.own_file:
            code = []
            for arg in args:
                if type(arg) != type(""):
                    code.append(str(arg))
                else:
                    code.append(arg)
            self.rib_code.append(" ".join(code)+'\n')
        else:
            parent_archive.rib(*args)
        
    def close(self):
        global base_archive, exported_files
        if not os.path.exists(os.path.split(self.filepath)[0]):
            os.mkdir(os.path.split(self.filepath)[0])
        if (self.rs.own_file 
            and (self.rs.overwrite or not os.path.exists(self.filepath))
            and not self.relative_filepath in exported_files):
            file = open(self.filepath, "w")
            file.writelines(self.rib_code)
            file.close()
            exported_files.append(active_archive.relative_filepath)
        if self == base_archive: 
            # if it's the base archive reset the global var back to None
            # because exporting finished
            base_archive = None   


#############################################
#                                           #
#   Convert Collection Property items       #
#   into RIB Code                           #
#                                           #
#############################################


def write_attrs_or_opts(groups, attr_opt, tab):
    global current_pass
    for group in groups:
        grp = {"Option" : group.options, "Attribute" : group.attributes}        
        if group.export:
            rib_apnd(tab + attr_opt)
            rib_apnd('\t"'+group.name+'"')
            writeparms(grp[attr_opt], attr_opt=attr_opt, grp=group.name)                                       

def write_custom_code(code, position, type_=""):
    global base_archive, current_pass
    global direction
    if current_pass.environment:
        env = True
    else:
        env = False
    if code:
        for c in code:
            if type_ == "World":
                cpos = c.world_position
            elif type_ == "Particles":
                cpos = c.particle_position
            else:
                cpos = c.position
            if cpos == position:
                if c.foreach or direction == "nz" or not env:
                    write_single_parm(c.parameter, name=c.name)
                
def write_single_parm(parm, name="", attr_opt="Attribute", grp=""):
    global base_archive, current_pass
    scene = base_archive.scene
    rm = scene.renderman_settings
    if attr_opt == "Option" and grp != "":
        master_parm = rm.option_groups[grp].options[parm.name]
    elif grp != "":
        master_parm = rm.attribute_groups[grp].attributes[parm.name]
    else:
        master_parm = parm
    ribnl()
    rib_apnd('\t\t')
    if name == "":
        name = parm.name
    if name.find('[') != -1:
        name = name[:name.find('[')]
    if parm.export:
        if master_parm.parametertype == 'string':
            if master_parm.input_type == "texture":
                texture = bpy.data.textures[parm.textparameter]
                if texture.renderman.type == 'bake':
                    string = os.path.join(getdefaultribpath(scene), texture.name+framepadding(scene)+".bake").replace('\\', '\\\\')
            else:
                string = parm.textparameter
            pname = '"string '+name + '"'
            value = '["' + string + '"]'

        if master_parm.parametertype == 'float':
            if parm.vector_size == 1:
                pname = '"float '+name + '"'
                value = '[' + str(parm.float_one[0]) + ']'
            elif parm.vector_size == 2:
                pname = '"float[2] '+name + '"'
                value = '[' + str(parm.float_two[0]) + ' ' + str(parm.float_two[1]) + ']'
            elif parm.vector_size == 3:
                pname = '"float[3] '+name + '"'
                value = '[' + str(parm.float_three[0]) + ' ' + str(parm.float_three[1]) + ' ' + str(parm.float_three[3]) + ']'
                                                   
        if master_parm.parametertype == 'int':
            if parm.vector_size == 1:
                pname = '"int '+name + '"'
                value = '[' + str(parm.int_one[0]) + ']'
            elif parm.vector_size == 2:
                pname = '"int[2] '+name + '"'
                value = '[' + str(parm.int_two[0]) + ' ' + str(parm.int_two[1]) + ']'
            elif parm.vector_size == 3:
                pname = '"int[3] '+name + '"'
                value = '[' + str(parm.int_three[0]) + ' ' + str(parm.int_three[1]) + ' ' + str(parm.int_three[3]) + ']'
                
        if master_parm.parametertype == 'color':
            colR = parm.colorparameter[0]
            colG = parm.colorparameter[1]
            colB = parm.colorparameter[2]
            pname = '"color '+name + '"'
            value = '[' + str(colR) + " " + str(colG) + " " + str(colB) + "]"
        
        rib_apnd(pname, value)

def writeparms(path, attr_opt="attr", grp=""):
    global base_archive
    scene = base_archive.scene
    for parm in path:
        write_single_parm(parm, attr_opt=attr_opt, grp=grp)
    ribnl()

def writeshaderparameter(parameterlist):
    global current_pass, base_archive
    scene = base_archive.scene
    for i, parm in enumerate(parameterlist):
        if not parm.export:
            continue
        ribnl()
        name = '"'+parm.type+' '+parm.name+'"'
        if parm.parametertype == 'string':
            if parm.input_type == "texture":
                tx = ""
                if parm.textparameter in bpy.data.textures:
                    texture = bpy.data.textures[parm.textparameter]
                    if texture.renderman.type == "file":
                        image = texture.image
                        tx = image_processing(texture.renderman.processing, image.filepath, tex=True)
                    elif texture.renderman.type == "bake":
                        tx = os.path.join(getdefaultribpath(scene), texture.name+framepadding(scene)+".bake").replace('\\', '\\\\')
                value = '["'+tx+'"]'
                        
            else:
                string = parm.textparameter.replace('[frame]', framepadding(scene))
                string = string.replace('[dir]', '')
                value = '["' + string + '"]'
                
        elif parm.parametertype == 'float' and parm.vector_size == 1:
            value = "[" + str(parm.float_one[0]) + ']'
            
        elif parm.parametertype == 'color':
            colR = parm.colorparameter[0]
            colG = parm.colorparameter[1]
            colB = parm.colorparameter[2]
            value = "[" + str(colR) + " " + str(colG) + " " + str(colB) + "]"
            
        elif parm.parametertype == 'float' and parm.vector_size == 3:
            x = str(parm.float_three[0])
            y = str(parm.float_three[1])
            z = str(parm.float_three[2])
            value = "[" + x + " " + y + " " + z + "]"
            
        rib_apnd('\t', name, value)

def prepared_texture_file(file):
    global current_pass, base_archive
    scene = base_archive.scene
    return os.path.splitext(file)[0]+"."+scene.renderman_settings.textureext
    
def image_processing(pr, input, scene=None, env=-1, tex=False):
    envdirections = ["px", "nx", "py", "ny", "pz", "nz"]
    global base_archive
    if not pr.process:
        return ""
    if base_archive != None:
        scene = base_archive.scene
    rm = scene.renderman_settings
    tx = rm.textureext
    txdir = rm.texdir
    output = getname(input,
                     frame=framepadding(scene),
                     scene=scene)
    
    output = os.path.join(txdir, output)
    if not os.path.exists(txdir): os.mkdir(txdir)
    parmsarray = []
    textool = scene.renderman_settings.textureexec
    parmsarray.append(textool)
    if pr.shadow:
        parmsarray.append("-shadow")
        ext = 'shd'
    else:
        if pr.envcube and env == 5:
            parmsarray.append("-envcube")
        ext = tx
    
        parmsarray.append("-filter")
        if pr.filter == "other":
            filter = pr.custom_filter
        else:
            filter = pr.filter
        parmsarray.append(filter)
        if pr.stwidth:
            parmsarray.append("-sfilterwidth")
            parmsarray.append(str(pr.swidth))
            parmsarray.append("-tfilterwidth")
            parmsarray.append(str(pr.twidth))
        else:
            parmsarray.append("-filterwidth")
            parmsarray.append(str(pr.width))
        if pr.custom_parameter != "":
            parmsarray.append(pr.custom_parameter)
    
    inp = input.replace('[frame]', framepadding(scene))
    if env == 5:
        inputs = []
        for dir in envdirections:
            inputs.append(inp.replace('[dir]', dir))
        parmsarray.append(inputs)
    else:
        parmsarray.append(inp)
    output += "."+ext
    output = output.replace('[dir]', '')
    parmsarray.append(output)
    
    parms = " ".join(parmsarray)
    
    command = textool+ ' ' +parms
    dbprint(parmsarray, lvl=2, grp="textures")
    if not os.path.exists(output):
        texprocess = subprocess.Popen(parmsarray, cwd=getdefaultribpath(scene))
        texprocess.wait()
    return output

def get_mb_sampletime(samples, shutterspeed):
    global current_pass
    sampletime = [0]
    for i in range(2, samples+1):
        addtosample = (shutterspeed/samples)*i
        sampletime.append(addtosample)
    return sampletime

def mb_setframe(t):
    global base_archive, current_pass, active_archive
    scene = base_archive.scene
    fps = scene.render.fps
    speed = current_pass.shutterspeed_sec * fps
    start_frame = base_archive.frame
    frame = start_frame - (speed - t)
    mod_frame = modf(frame)
    scene.frame_set(mod_frame[1], mod_frame[0])
    return frame

def motionblur( path,
                function,
                *args,
                frameset=True,
                **keys):
                    
    global current_pass, active_archive
    dbprint("writing motion blur", "active archive is", active_archive.data_path, lvl=2, grp="mb")
    scene = active_archive.scene
    fps = scene.render.fps
    motion_samples = path.motion_samples
    shutterspeed = current_pass.shutterspeed_sec * fps
    
    sampletime = get_mb_sampletime(motion_samples, shutterspeed)
        
    mbbegin = 'MotionBegin['
    mbbegin +=' '.join([str(s) for s in sampletime])
    mbbegin += ']'
    rib_apnd(mbbegin)
    for s in sampletime:
        if frameset:
            mb_setframe(s)
        function(*args, **keys)
    rib_apnd('MotionEnd')

#############################################
#                                           #
#   Write Render Settings                   #
#   (the stuff before World Block begins)   #
#                                           #
#############################################
                    
def writeSettings(camrot):
    global base_archive, direction, current_pass
    dir = direction
    scene = base_archive.scene
    
    settings_archive = create_child(current_pass,
                                    type="Settings")
                                    
    dbprint("write Scene Settings ...", lvl=1, grp="Settings")

    if not current_pass.displaydrivers:
        nodisplay = True
    else:
        nodisplay = False
                
    if current_pass.name == "Beauty" and not current_pass.displaydrivers:
        adddisp(current_pass, scene=scene)
    render = scene.render
   
    if current_pass.camera_object == "":
        camobj = scene.camera.name
    else:
        camobj = current_pass.camera_object
    #print(scene.objects)
    camera = scene.objects[camobj]
    rc = camera.renderman_camera
    if camera.type == "CAMERA":
        nearclipping = camera.data.clip_start
        farclipping = camera.data.clip_end
        shift_x = camera.data.shift_x * 2
        shift_y = camera.data.shift_y * 2
        
        resx = int(render.resolution_x * render.resolution_percentage)*0.01
        resy = int(render.resolution_y * render.resolution_percentage)*0.01

        x = render.resolution_x * render.pixel_aspect_x
        y = render.resolution_y * render.pixel_aspect_y
       
        if x >= y:
            asp_y = y/x
            asp_x = 1.0
        else:
            asp_x = x/y
            asp_y = 1.0

        aspectratio = render.pixel_aspect_x/render.pixel_aspect_y

        left = str(-asp_x+shift_x)
        right = str(asp_x+shift_x)

        top = str(-asp_y+shift_y)
        bottom = str(asp_y+shift_y)

        if rc.depthoffield:
            dof_distance = rc.dof_distance
            if rc.use_lens_length:
                focal_length = scene.camera.data.lens/100
            else:
                focal_length = rc.focal_length
            fstop = rc.fstop
    else:
        left = "-1"
        right = "1"
        top = "-1"
        bottom = "1"
        resx = resy = rc.res
        aspectratio = "1"
        if camera.type == "LAMP":
            nearclipping = camera.data.shadow_buffer_clip_start
            farclipping = camera.data.shadow_buffer_clip_end
        else:
            near_clipping = rc.nearclipping
            far_clipping = rc.farclipping

## custom code
    write_custom_code(current_pass.scene_code, "begin")

## Declare AOVs
    default_vars = ["rgb", "rgba", "a", "z", "N", 
                        "P", "Ci", "Cs", "Oi", "Os", 
                        "s", "t", "u", "v", "Ng", 
                        "E", "du", "dv", "dPtime", "dPdu", 
                        "dPdv"]
    for var in scene.renderman_settings.var_collection:
        if not var.name in default_vars:
            rib_apnd('Declare', '"'+var.name+'" "'+var.type_+'"')


### Display driver
    for dispcount, display in enumerate(current_pass.displaydrivers):
        disp = ""
        disp_value = ""
        if not display.export:
            disp += '#'
        quant_min = str(display.quantize_min)
        quant_black = str(display.quantize_black)
        quant_max = str(display.quantize_max)
        quant_white = str(display.quantize_white)
        gamma = str(float(int(display.gamma*100)/100))
        gain = str(float(int(display.gain*100)/100))
        file = display.file.replace("[frame]",framepadding(scene))
        dbprint(dir, lvl=1, grp="env")
        file = file.replace("[dir]", dir)
        disp += 'Display'
        if dispcount > 0:
            disp_value = '"+'
        else:
            disp_value = '"'
        disp_value += file + '" "' + display.displaydriver + '" "'+display.var+'" '
        disp_value += '"int[4] quantize" [' + quant_min + ' ' + quant_max + ' ' + quant_black + ' ' + quant_white + ']'
        disp_value += ' "float[2] exposure" [' + gain + ' ' + gamma + ']'
        rib_apnd(disp, disp_value)
        if display.custom_options:
            writeshaderparameter(display.custom_options)
        ribnl()

### Format
    rib_apnd('Format', str(int(resx)) +' '+ str(int(resy)) +' '+ str(aspectratio))

### ScreenWindow
    rib_apnd('ScreenWindow', left +' '+ right +' '+ top +' '+ bottom)

### Clipping
    rib_apnd('Clipping', str(nearclipping)+' '+str(farclipping))

### DepthOfField
    dbprint(current_pass.camera_object, lvl=2, grp="Settings")
    if current_pass.camera_object == "" and rc.depthoffield:
        rib_apnd('DepthOfField', str(fstop)+' '+str(focal_length)+' '+str(dof_distance))

### PixelFilter
    filter = current_pass.pixelfilter.filterlist
    fwidth = str(current_pass.pixelfilter.filterwidth)
    fheight = str(current_pass.pixelfilter.filterheight)
    rib_apnd('PixelFilter', '"'+filter+'" '+fwidth+' '+fheight)
    
### PixelSamples
    sampx = str(current_pass.pixelsamples_x)
    sampy = str(current_pass.pixelsamples_y)
    rib_apnd('PixelSamples', sampx+' '+sampy)    

### Options
    write_attrs_or_opts(current_pass.option_groups, "Option", "")
    ribnl()
    
### Hider
    if current_pass.hider != "":
        rib_apnd('Hider', '"'+current_pass.hider+'"')
        hider_parms = current_pass.hider_list[current_pass.hider].options
        writeparms(hider_parms)
        ribnl()   

### Orientation    
    rib_apnd('Orientation "lh"')

### Custom Code
    if current_pass.scene_code:
        for code in current_pass.scene_code:
            rib_apnd(code.name)

    dbprint("Done", lvl=1, grp="Settings")
    
### Camera
    if current_pass.displaydrivers:
        writeCamera(camera, camrot)
        
## custom code
    write_custom_code(current_pass.scene_code, "end")
    
    
    set_parent_active()
      


#############################################
#                                           #
#   Camera Projection and Transformation    #
#                                           #
#############################################

def round(float):
    if math.modf(float)[0] >= 0.5:
        integer = math.ceil(float)
    else:
        integer = math.floor(float)
    return integer

def writetransform(obj, mx = None):
    if mx: matrix = mx
    else: matrix = obj.matrix_world
    str_mx = 'ConcatTransform [\t'
    for i, row in enumerate(matrix):
        for val in row:
            str_mx += " " + str(val)
        if not i == len(matrix)-1: 
            rib_apnd(str_mx)
            str_mx = '\t\t\t\t\t'
    rib_apnd(str_mx+']')

def objtransform(obj, mx = None):
    global base_archive, current_pass
    
    ## transformation blur    
    sampletime = []
    
    objpass = linked_pass(obj, current_pass)
    if objpass and objpass.transformation_blur and current_pass.motionblur:
        motionblur( objpass,
                    writetransform,
                    obj,
                    mx)
    else: writetransform(obj)


def writeCamera(cam, camrot):
    degrees = math.degrees
    global current_pass, direction, base_archive
    dir = direction
    scene = base_archive.scene
    print("write Camera Settings ...")
    
    def writeCameraTransform(trans, cam, camrot):
        matrix = cam.matrix_world
        ribx = str(matrix[3][0]*-1)
        riby = str(matrix[3][1]*-1)
        ribz = str(matrix[3][2]*-1)
        if current_pass.environment:
            rotx, roty, rotz = camrot
        else:
            rotx = degrees(cam.rotation_euler[0])
            roty = degrees(cam.rotation_euler[1])
            rotz = degrees(cam.rotation_euler[2])
            
        transform = {   "RotX" : "Rotate "+str(rotx*-1)+" 1 0 0\n",
                        "RotY" : "Rotate "+str(roty*-1)+" 0 1 0\n",
                        "RotZ" : "Rotate "+str(rotz*-1)+" 0 0 1\n",
                        "Translate" : "Translate "+ribx+" "+riby+" "+ribz+"\n" }
        rib_apnd(transform[trans])
        
    def writePerspective(fov, perspective):
        if perspective:
            typestring = '"perspective" "fov" ['+fov+']\n'
    
        elif not perspective:
            typestring = '"orthographic"\n'

        rib_apnd('Projection', typestring)

    if current_pass.motionblur:
        shutterspeed = current_pass.shutterspeed_sec * scene.render.fps
        rib_apnd('Shutter 0', str(shutterspeed))

    def checkoutFOVnPersp():
        perspective = True
        fov = ""
        if cam.type =='CAMERA':
            lens = degrees(cam.data.angle)
            if cam.data.type == 'PERSP':
                perspective = True
                fov = str(lens)
            else:
                perspective = False
    
        elif cam.type =='LAMP':
            if cam.data.type == 'SPOT':
                lens = math.degrees(cam.data.spot_size)
                fov = str(lens)
                perspective = True
            elif cam.data.type == 'POINT':
                perspective = True
                fov = cam.renderman_camera.fov
            elif cam.data.type == 'SUN':
                perspective = False
        else:
            fov = str(current_pass.renderman_camera.fov)
            perspective = True
        return fov, perspective

#    ##perspective blur
#    sampletime = []
#    if linked_pass(cam, current_pass).perspective_blur:
#        motion_samples = linked_pass(cam, current_pass).motion_samples
#        current_frame = scene.frame_current  
#        shutterspeed, sampletime = motionblur(motion_samples, current_pass, scene)
#    
#        if current_pass.motionblur:
#            write('MotionBegin[')
#            for s in sampletime:
#                write(str(s)+' ')
#            write(']\n')
#            for s in sampletime:
#                scene.frame_set(current_frame - (shutterspeed - s))
#                fov, perspective = checkoutFOVnPersp()
#                writePerspective(fov, perspective)
#        write('MotionEnd\n')
#                   
#    else:
    fov, perspective = checkoutFOVnPersp()
    writePerspective(fov, perspective)

    if not current_pass.environment:
        rib_apnd("Scale", 1, 1, -1)
        
    ##Camera Transformation Blur

    ts = cam.renderman_camera.transformation_blur
    if ts and current_pass.motion_blur:
        for t in ["RotX", "RotY", "RotZ", "Translate"]:
            motionblur( linked_pass(cam, current_pass),
                        writeCameraTransform,
                        t,
                        cam,
                        camrot)
    else:
        for t in ["RotX", "RotY", "RotZ", "Translate"]:
            writeCameraTransform(t, cam, camrot)
              
    ribnl()
    ribnl()
    print("Done")
    

#############################################
#                                           #
#  World Block                              #
#                                           #
#############################################


def writeWorld():
    global base_archive, current_pass
    scene = base_archive.scene
    
    world_archive = create_child(current_pass, type = "World")
    global_shader = current_pass.global_shader

    rib_apnd("WorldBegin")
    if current_pass.override_shadingrate:
        rib_apnd("ShadingRate", current_pass.shadingrate)
    write_attrs_or_opts(current_pass.attribute_groups, "Attribute", "")
    ribnl()
    ribnl()
    
    ## custom code
    write_custom_code(current_pass.world_code, "begin", type_="World")
            
    writeshader(global_shader.surface_shader, global_shader.surface_shader_parameter, "Surface")
    writeshader(global_shader.atmosphere_shader, global_shader.atmosphere_shader_parameter, "Atmosphere")
            

    if not current_pass.exportobjects and current_pass.lightgroup:
        objects = bpy.data.groups[current_pass.objectgroup].objects
    else:
        objects = scene.objects

    if not current_pass.exportlights and current_pass.lightgroup:
        lights = bpy.data.groups[current_pass.lightgroup].objects
    elif not current_pass.exportlights and not current_pass.lightgroup:
        lights = []
    else:
        lights = scene.objects

    if lights:
        for light in lights:
            writeLight(light)
        ribnl()
        for light in lights:
            al = False
            if light.type != 'LAMP':
                m = light.active_material
                if m:
                    lp = linked_pass(m, current_pass)
                    if lp != None and lp.arealight_shader != "":
                        al = True
            if light.type == 'LAMP' or al and linked_pass(light.data, current_pass) != None:
                rib_apnd('Illuminate', '"'+light.name+'"', 1)
        
    ribnl()

    if objects:
        for obj in objects:
            if (not obj.hide_render
                and not obj.name == current_pass.camera_object
                and check_visible(obj, scene)):
                writeObject(obj)
                writeParticles(obj)
    
    ## custom code
    write_custom_code(current_pass.world_code, "end_inside", type_="World")
    rib_apnd("WorldEnd")
    global active_archive
    write_custom_code(current_pass.world_code, "end_outside", type_="World")


#############################################
#                                           #
#   Lights                                  #
#                                           #
#############################################


def writeLight(light, scene = None):
    global base_archive, current_pass
    if scene == None:
        scene = base_archive.scene
    rmansettings = scene.renderman_settings
    al = False
    if light.type == "LAMP":
        if linked_pass(light.data, current_pass) == None:
            return
    if light.type != 'LAMP' and light.active_material:
        mat = light.active_material
        
        lp = linked_pass(mat, current_pass)
        if lp == None:
            return
        alshader = lp.arealight_shader
            
        if alshader != "":
            al = True
            
    if (light.type == 'LAMP' or al) and not light.hide_render:
        if check_visible(light, scene):
            light_archive = create_child(light,
                                        type = "LAMP")
            
            print("write "+light.name)
            rotx = str(math.degrees(light.rotation_euler.x))
            roty = str(math.degrees(light.rotation_euler.y))
            rotz = str(math.degrees(light.rotation_euler.z))          
    
            ribnl()
            rib_apnd("AttributeBegin")      
            objtransform(light)
            if al:
                write_attrs_or_opts(linked_pass(light, current_pass).attribute_groups, "Attribute", "")
                al_def = 'AreaLightSource '
                parameterlist = linked_pass(mat, current_pass).light_shader_parameter
                al_def += '"'+alshader.replace("."+rmansettings.shaderbinary, "")+'" "'+light.name+'" '
                rib_apnd(al_def)
                writeshaderparameter(parameterlist)
                ribnl()
                export_type = light.data.export_type
                
                if light.data.show_double_sided:
                    rib_apnd('Sides 2')
                    
                if mat: writeMaterial(mat)
                
                if export_type == 'ObjectInstance':
                    rib_apnd('ObjectInstance', '"'+light.data.name+'"')
                else:
                    export_object(light, export_type)
            else:
                write_attrs_or_opts(linked_pass(light.data, current_pass).attribute_groups, "Attribute", "")
                l_def = 'LightSource '
                parameterlist = linked_pass(light.data, current_pass).light_shader_parameter
                l_def += '"'+linked_pass(light.data, current_pass).shaderpath.replace("."+rmansettings.shaderbinary, "")+'" "'+light.name+'" '
                rib_apnd(l_def)      
                writeshaderparameter(parameterlist)
                ribnl()

            rib_apnd('AttributeEnd')
            print("Done")
            
            set_parent_active()


#############################################
#                                           #
#   Materials                               #
#                                           #
#############################################
def writeshader(shader, parms, type):
    global base_archive
    scene = base_archive.scene
    rmansettings = scene.renderman_settings
    if shader:
        shader = shader.replace("."+rmansettings.shaderbinary, "")
        rib_apnd(type, '"'+shader+'"')
        writeshaderparameter(parms)
        ribnl()             

def writeMaterial(mat, mat_archive=None, active_matpass=False):
    global active_archive
    if active_matpass:
        mat_pass=mat.renderman[mat.renderman_index]
    else:
        mat_pass = linked_pass(mat, current_pass)
    if mat_pass == None:
        return
    scene = active_archive.scene
    p = active_archive
    if mat_archive == None:
        mat_archive = Archive(data_path=mat, parent_archive=p)
    rmansettings = scene.renderman_settings
    
    if mat_pass.matte:
        rib_apnd('Matte 1')
    ## Color & Opacity Motion Blur
    def writeColor():  
        colR = mat_pass.color.r
        colG = mat_pass.color.g
        colB = mat_pass.color.b
        rib_apnd('Color', '[', colR, colG, colB, ']')
       
    def writeOpacity():
        opR, opG, opB = mat_pass.opacity    
        rib_apnd('Opacity', '[', opR, opG, opB, ']')
        


    def matblur(function, *args):     
        motionblur( mat_pass,
                    function,
                    *args)

    if mat_pass.color_blur:                
        matblur(writeColor)
    else:
        writeColor()
        
    if mat_pass.opacity_blur:        
        matblur(writeOpacity)
    else:
        writeOpacity()

    surface_shader = mat_pass.surface_shader
    surface_parameter = mat_pass.surface_shader_parameter 
    displacement_shader = mat_pass.displacement_shader
    displacement_parameter = mat_pass.disp_shader_parameter 
    interior_shader = mat_pass.interior_shader
    interior_parameter = mat_pass.interior_shader_parameter
    exterior_shader = mat_pass.exterior_shader
    exterior_parameter = mat_pass.exterior_shader_parameter    
  
    if mat_pass.shader_blur:
        matblur(writeshader, displacement_shader, displacement_parameter, "Displacement")
        matblur(writeshader, surface_shader, surface_parameter, "Surface")
        matblur(writeshader, interior_shader, interior_parameter, "Interior")
        matblur(writeshader, exterior_shader, exterior_parameter, "Exterior")
    else:
        writeshader(displacement_shader, displacement_parameter, "Displacement")
        writeshader(surface_shader, surface_parameter, "Surface")
        writeshader(interior_shader, interior_parameter, "Interior")
        writeshader(exterior_shader, exterior_parameter, "Exterior")
    set_parent_active()


#############################################
#                                           #
#   Particles                               #
#                                           #
#############################################
matrices = []

def writeParticles(obj):
    global base_archive, current_pass
    scene = base_archive.scene
    rmansettings = scene.renderman_settings
    pfiles = []

    if len(obj.particle_systems) > 0:
        for psystem in obj.particle_systems:
            if psystem.settings.type == 'EMITTER':
                rman = linked_pass(psystem.settings, current_pass)
                if not rman:
                    return

                particle_archive = create_child(psystem)
                ribnl()
                rib_apnd("AttributeBegin ##Particle System")
                rib_apnd('Attribute', '"identifier"', '"name"', '["'+obj.name+'_'+psystem.name+'"]')
                
                ## custom code
                write_custom_code(rman.custom_code, "begin", type_="Particles")
                ribnl()
                try:
                    mat = obj.material_slots[rman.material_slot]
                except IndexError:
                    mat = None
                if mat: writeMaterial(mat.material)
                write_attrs_or_opts(linked_pass(psystem.settings, current_pass).attribute_groups, "Attribute", "")
                
                if current_pass.motionblur and rman.motion_blur:
                    locations, sizes, frames = mb_gather_point_locations(psystem)
                    shutterspeed = current_pass.shutterspeed_sec * scene.render.fps
                    sampletime = get_mb_sampletime(rman.motion_samples, shutterspeed)
                    mbstr = 'MotionBegin['
                    mbstr += ' '.join([str(s) for s in sampletime])
                    mbstr += ']'
                    rib_apnd(mbstr)
                    for i, s in enumerate(sampletime):
                        writeParticle_data(psystem, 
                                            locs=locations, 
                                            sizes=sizes, 
                                            frames=frames,
                                            sample=i)
                    rib_apnd('MotionEnd')
                else:
                    writeParticle_data(psystem)
                 ## custom code
                write_custom_code(rman.custom_code, "end", type_="Particles")
                rib_apnd('AttributeEnd')
                set_parent_active()
                
def mb_gather_point_locations(psystem):
    locations = []
    sizes = []
    frames = []
    global active_archive, current_pass
    scene = active_archive.scene
    rman = linked_pass(psystem.settings, current_pass)
    shutterspeed = current_pass.shutterspeed_sec * scene.render.fps
    sampletime = get_mb_sampletime(rman.motion_samples, shutterspeed)
    
    ## gather locations and size for each motion sample
    for s in sampletime:
        loc_sample = []
        siz_sample = []
        start_frame = base_archive.frame
        frame = start_frame - (shutterspeed - s)
        frames.append(frame)
        for part in psystem.particles:
            loc_sample.append(compute_particle_location(part, s))
            if rman.constant_size:
                size = str(part.size * rman.size_factor)
                siz_sample.append(size)
        locations.append(loc_sample)
        sizes.append(siz_sample)
        
    return locations, sizes, frames

def compute_particle_location(part, sampletime):
    deltaloc = part.prev_location - part.location 
    mb_sample_loc =   part.location + deltaloc * (1 - sampletime)
    return [str(mb_sample_loc.x), str(mb_sample_loc.y), str(mb_sample_loc.z)]
    

def writeParticle_data(psystem, locs = [], sizes = [], frames=[], sample = -1):
    global active_archive, current_pass
    scene = active_archive.scene
    shutterspeed = current_pass.shutterspeed_sec * scene.render.fps
    try:
        frame = frames[sample]
        customfr = True
    except IndexError:
        frame = 0.0
        customfr = False
    rman = linked_pass(psystem.settings, current_pass)
    if rman:
        pdata_archive = Archive(psystem, 
                                type="Particle Data", 
                                parent_archive=active_archive, 
                                custom_frame=customfr,
                                frame=frame)
        if check_skip_export():
            set_parent_active()
            return

         ## custom code
        write_custom_code(rman.custom_code, "begin_data", type_="Particles")
        ## Points
        if rman.render_type == "Points":
            rib_apnd('Points')
            rib_apnd('"P" [')
            if locs:
                for i, loc in enumerate(locs[sample]):
                    if psystem.particles[i].alive_state == 'ALIVE':
                        rib_apnd(*loc)
            else:
                for part in psystem.particles:
                    if part.alive_state == 'ALIVE':
                        rib_apnd(*part.location)
            rib_apnd(']')
            
            if not rman.constant_size:
                rib_apnd('"width" [') 
                if sizes:
                    for i, size in enumerate(sizes[sample]):
                        if psystem.particles[i].alive_state == 'ALIVE':
                            rib_apnd(size)
                else:
                    for part in psystem.particles:
                        if part.alive_state == 'ALIVE':
                            rib_apnd(part.size)
                rib_apnd(']')
            else:
                rib_apnd('"constantwidth" [', rman.size_factor, ']')

            ## custom variables
            if rman.export_vars:
                for var in rman.export_vars:
                    rib_apnd('"'+var.name+'" [')
                    for part in psystem.particles:
                        rib_apnd(eval("part."+var.path))
                    rib_apnd(']')

            ## custom code
            write_custom_code(rman.custom_code, "end_data", type_="Particles")
        ## Objects
        elif rman.render_type == "Object":
            part_obj = scene.objects[rman.object]
            
            
        #~ def transform(part):          
                #~ mx_new = mathutils.Matrix()
                #~ trans = part.location
                #~ mx_trans = mx_new.Translation(trans)
                #~ mx_rot = part.rotation.to_matrix().to_4x4()
                #~ mx_scale = mx_new.Scale(part.size, 4)
                #~ mx = mx_trans * mx_scale * mx_rot
                #~ return mx
        #~ 
        #~ def mb_trans_particles(matrices, i):
            #~ for m in matrices:
                #~ objtransform(None, mx = matrices.pop(0)[i])
        #~ 
        #~ matrices = []
        #~ mx_set = []
        #~ for i, part in enumerate(psystem.particles):
            #~ mx_set.append(transform(part))
        #~ matrices.append(mx_set)                   
        #~ 
        #~ for i, part in enumerate(psystem.particles):
            #~ if scene.frame_current >= part.birth_time:
                #~ write('AttributeBegin\n')
                #~ 
                #~ if rman.motion_blur and current_pass.motionblur:
                    #~ motionblur( rman,
                                #~ mb_trans_particles,
                                #~ matrices,
                                #~ i,
                                #~ frameset = 0)
                #~ else:
                    #~ mb_trans_particles
                                            #~ 
                #~ writeObject(part_obj) 
            #~ 
                #~ write('AttributeEnd\n')
        
        set_parent_active()
                                

#############################################
#                                           #
#   Objects                                 #
#                                           #
#############################################
    
def writeObject(obj):
    global base_archive, current_pass
    scene = base_archive.scene

    if obj.type in ['MESH']:
        al = False
        m = obj.active_material
        if m:
            lp = linked_pass(m, current_pass)
            if lp != None and lp.arealight_shader != "":
                al = True
        obj_pass = linked_pass(obj, current_pass)
        if obj_pass and not al:               
            obj_archive = create_child(obj)
            mat = obj.active_material            
            
            rib_apnd("##"+obj.name)
            if obj.parent:
                rib_apnd('#child of '+obj.parent.name)
            rib_apnd("AttributeBegin")
            
            for light in obj_pass.lightlist:
                rib_apnd('Illuminate', 0)
                
            rib_apnd('Attribute',  '"identifier"',  '"name"', '["'+obj.name+'"]')
            write_attrs_or_opts(obj_pass.attribute_groups, "Attribute", "")
                
            objtransform(obj)
            rmansettings = scene.renderman_settings

            if mat: writeMaterial(mat)
            
            if obj.data.show_double_sided:
                rib_apnd('Sides 2')
                
            if not current_pass.override_shadingrate:
                rib_apnd('ShadingRate', obj_pass.shadingrate)
            
            export_type = obj.data.export_type
            if export_type == 'ObjectInstance':
                rib_apnd('ObjectInstance', '"'+obj.data.name+'"')
            else:
                export_object(obj, export_type)
            rib_apnd("AttributeEnd")
            ribnl()
            set_parent_active()
        


#############################################
#                                           #
#   Mesh data (own RIB file)                #
#                                           #
#############################################


def writeMesh(mesh):
    subsurf = False
    ptype = mesh.data.primitive_type
    subsurf = ptype == 'subdivisionmesh'
    smoothshade = False
    global active_archive
    mesh_archive = create_child(mesh.data, type = "MESH")
    scene = mesh_archive.scene
    dbprint("This Polygon Object is a", ptype, grp="Export", lvl=2)

    #Apply Modifiers
    export_mesh = mesh.to_mesh(scene, True, 'RENDER')
    dbprint("apllied modifiers:", export_mesh, lvl=2, grp="Export")
    
    
    if subsurf:
        rib_apnd('SubdivisionMesh', '"catmull-clark"')
    elif ptype == 'pointspolygons':
        rib_apnd("PointsPolygons")
    elif ptype == 'points':
        rib_apnd('Points')        
    vindices = []
    if ptype in ['subdivisionmesh', 'pointspolygons']:
        #write Polygon Vertex Count
        poly_init_str = "["
        poly_init_str += " ".join([str(len(face.vertices)) for face in export_mesh.faces])
        poly_init_str += "]"
        rib_apnd(poly_init_str)
    
        #write Polygon Vertex Index
        vindex = "["
        for face in export_mesh.faces:
            for v in face.vertices:
                vindex += str(v.real)+" "
                vindices.append(v.real)
        vindex += "]"
        rib_apnd(vindex)
    
        if subsurf:
            rib_apnd('["interpolateboundary"] [0 0] [] []')

        
    #write Normals
    if mesh.data.export_normals:
        rib_apnd('"N"')
        rib_apnd("[")
        for vindex, n in enumerate(export_mesh.vertices):
            for f in export_mesh.faces:
                for fv in f.vertices:
                    if vindex == fv.real:
                        if f.use_smooth:
                            normal = n.normal
                        else:
                            normal = f.normal
            rib_apnd(*normal)
        rib_apnd(']')
    
    #write Vertex Coordinates
    rib_apnd('"P"')
    rib_apnd('[')
    for vindex, v in enumerate(export_mesh.vertices):
        if vindex in vindices or ptype == 'points': #make sure vertex is in a polygon, as otherwise renderman cries
            rib_apnd(v.co.x, v.co.y, v.co.z)                
    rib_apnd("]")

    p_scale = mesh.data.points_scale
    
    if ptype == "points" and mesh.data.size_vgroup != "":
        rib_apnd('"width"')
        rib_apnd('[')
        for vert in mesh.data.vertices:
            i = mesh.vertex_groups[mesh.data.size_vgroup].index
            size_value = vert.groups[i].weight
            rib_apnd(size_value*p_scale)
        rib_apnd(']')
    elif ptype == "points":
        rib_apnd('"constantwidth"', '['+str(p_scale)+']')       
    
    #write UV coordinates        
    uv = False
    for uvlayer, uv_texture in enumerate(export_mesh.uv_textures):
        if uvlayer == 0:
            s = "s"
            t = "t"
        else:
            s = "s"+str(uvlayer)
            t = "t"+str(uvlayer)
        if scene.renderman_settings.facevertex:
            rib_apnd('"facevertex float[2] '+s+t+'"')
            rib_apnd('[')
        else:
            rib_apnd('"facevarying float[2] '+s+t+'"')
            rib_apnd('[')
        for face in uv_texture.data:
            for co in face.uv:
                rib_apnd(co[0], 1-co[1])
        rib_apnd("]")
    bpy.data.meshes.remove(export_mesh)
    set_parent_active()

#############################################
#                                           #
#   gather data and                         #
#   execute all export functions            #
#                                           #
#############################################

def export_object(obj, type = "ReadArchive"):
    global current_pass, active_archive
    obj_pass =linked_pass(obj, current_pass)
    if obj_pass == None:
        return
    
    if type == 'ObjectInstance':
        inst = True
    else:
        inst = False
        
    if inst:
        global exported_instances
        if obj.data.name in exported_instances: return 0
        exported_instances.append(obj.data.name)
        rib_apnd('ObjectBegin', '"'+obj.data.name+'"')

    if obj_pass.deformation_blur and current_pass.motionblur:
        motionblur(obj_pass,
                   writeMesh,
                   obj)
    else:
        writeMesh(obj)
        
    if inst: rib_apnd('ObjectEnd')
        
#########################            

            

def export(rpass, scene):
    global current_pass, direction, base_archive, exported_instances, active_archive
    exported_instances = []
    current_pass = rpass
    degrees = math.degrees
    rs = scene.renderman_settings.rib_structure.render_pass
    path = getdefaultribpath(scene)
    path = os.path.join(path, rs.folder)
    if current_pass.environment:
        camera = scene.objects[current_pass.camera_object]
        envrots = [ [180, 90, 180],
                    [180, -90, 180],
                    [90, -180, 180],
                    [-90, -180, 180],
                    [0, 0, 0],
                    [0, 180, 0]]
        envdirections = ["px", "nx", "py", "ny", "pz", "nz"]
        for i, dir in enumerate(envdirections):
            direction = dir            
            camrot = envrots[i]
            rib_apnd("FrameBegin", scene.frame_current)
            pass_archive = create_child(scene, type="Pass")
            writerib(camera, camrot, dir = dir)
            active_archive = base_archive
            rib_apnd("FrameEnd")
            invoke_renderer(filepath.replace('[dir]', dir), scene)
            
            check_disps_processing(rpass, scene, env=i)
        direction = ""
        
    else:
        if current_pass.camera_object == "":
            camobj = scene.camera.name
        else:
            camobj = current_pass.camera_object
        camera = scene.objects[camobj]
        rot = camera.rotation_euler
                        
        camrot = [degrees(rot[0]), degrees(rot[1]), degrees(rot[2])]    
        rib_apnd("FrameBegin", scene.frame_current)
        pass_archive = create_child(scene, type="Pass")
        writerib(camera, camrot, dir = "")
        active_archive=base_archive
        rib_apnd("FrameEnd")

def check_disps_processing(current_pass, scene, env=-1):
    for disp in current_pass.displaydrivers:
        filepath = disp.file
        pr = disp.processing
        image_processing(pr, filepath, scene=scene, env=env)

def getfinalpath(subfolder):
    return os.path.join(getdefaultribpath(scene), subfolder)

    #Write RIB Files
def writerib(camera, camrot, dir = ""):
    global base_archive
    scene = base_archive.scene
    rm = scene.renderman_settings
    instarchive = create_child(scene, type="Instances")
    for obj in scene.objects:
        if obj.type in ['MESH']:
            if obj.data.export_type == 'ObjectInstance':
                export_object(obj, type = obj.data.export_type)
    set_parent_active()
    writeSettings(camrot)
    writeWorld()

def invoke_renderer(rib, scene):
    rndr = scene.renderman_settings.renderexec
    os.system('"'+rndr+'" "'+ rib+'"')
    
