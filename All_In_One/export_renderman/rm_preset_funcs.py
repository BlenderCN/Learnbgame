
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
import export_renderman.rm_maintain

import os

def invoke_preset(rpass, preset, scene):
    rm = scene.renderman_settings
    active_engine = rm.active_engine
    export_renderman.rm_maintain.maintain_hiders(rpass, scene)
    export_renderman.rm_maintain.maintain_searchpaths(rpass, scene)

    preset_path = bpy.utils.preset_paths('') 
    if not bpy.utils.preset_paths('renderman'):
        os.mkdir(os.path.join(preset_path, 'renderman'))
    main_preset_path = bpy.utils.preset_paths('renderman')[0]
    sub_preset_path = os.path.join(main_preset_path, active_engine)
    
    preset_width_subdirs = preset.split("/")
    for pr in preset_width_subdirs:
        sub_preset_path = os.path.join(sub_preset_path, pr)
    
    preset_file = sub_preset_path+'.pass'

    pass_path = 'bpy.context.scene.renderman_settings.passes["'+rpass.name+'"].'
    
    try:
        file = open(preset_file, "r")
    except:
        print("file not found")
        return 0

    def eval_preset(ei, plines):
        pi = ei
        while True:
            pi += 1
            pline = plines[pi]
            if pline == '##\n': break
            else:
                prop = pass_path + pline
                try:
                    exec(prop)
                except:
                    print(prop)
                    raise
    def eval_sub_preset(ei, plines, type):                
        subs = []
        pi = ei
        while True:
            pi += 1
            line = lines[pi]
            if line == '##\n': break
            else:
                subs.append(line)
        load_grp_preset(subs, rpass, type, scene)                
    
    lines = file.readlines()
    
    for i, line in enumerate(lines):
        if line in ['##Quality\n',
                    '##ImageFolder\n'
                    '##Motion Blur\n', 
                    '##Export Objects\n', 
                    '##Export Lights\n', 
                    '##Animate Pass\n',
                    '##ImageFolder\n']:
            eval_preset(i, lines)
            
        elif line == '##World Shaders\n':
            eval_preset(i, lines)
            export_renderman.rm_maintain.maintain_world_shaders(rpass, scene)
            
        elif line == '##Attributes\n':
            eval_sub_preset(i, lines, "attr")
            
        elif line == '##Options\n':
            eval_sub_preset(i, lines, "opt")
        
        elif line == '##Hider\n':
            pi = i
            pi += 1
            hider = lines[pi].replace('\n', '')
            rpass.hider = hider
            while True:
                pi += 1
                hline = lines[pi]
                if hline == '##\n': break
                else:
                    mhl = rm.hider_list
                    load_sub_preset(rpass.hider_list[hider].options, mhl[hider].options, hline)
            
        elif line == '##Displays\n':
            disp_name = ""
            disp = None
            disp_path = ""
            co = False
            pi = i
            while True:
                pi += 1
                dline = lines[pi]
                if dline == '##\n': break
                else:               
                    if dline.find('NewDisplay') != -1:
                        disp_name = dline.split()[1]
                        if not disp_name in rpass.displaydrivers:
                            rpass.displaydrivers.add().name = disp_name
                        disp = rpass.displaydrivers[disp_name]
                        disp_path = pass_path + 'displaydrivers["'+disp_name+'"].'
                        co = False
                    elif dline == '#Custom Options\n': 
                        co = True
                    elif co:
                        load_sub_preset(disp.custom_options,
                                        rm.displays[disp.displaydriver].custom_parameter, dline)
                    else:
                        prop = pass_path + dline
                        exec(prop)
                        
        elif line == '##Custom Scene RIB Code\n':
            pi = i
            while True:
                pi += 1
                pline = lines[pi]
                if pline == '##\n': break
                else:
                    if not pline in rpass.scene_code:
                        rpass.scene_code.add().name = pline
                    
        elif line == '##Custom World RIB Code\n':
            pi = i
            while True:
                pi += 1
                pline = lines[pi]
                if pline == '##\n': break
                else:
                    if not pline in rpass.world_code:
                        rpass.world_code.add().name = pline
                    
        elif line in ['##Imager\n', '##Surface\n', '##Atmosphere\n']:
            eval_preset(i, lines)                  

def load_sub_preset(sub_path, master_sub_path, line):
    export = {"1" : True, "0" : False}
    raw_value = ""
    if line.find("(") != -1:
        raw_value = line[line.find("("):line.find(")")].replace("(", "")
        line = line.replace("("+raw_value+")", "")
        val = raw_value.split()
        grp_name, sub_name, ex = line.split()
    elif line.find('"') != -1:
        val = line[line.find('"')+1:line.rfind('"')]
        line = line.replace(val, "")
        line = line.replace('"', '')
        try:
            grp_name, sub_name, ex = line.split()
        except:
            print(line)
    else:
        grp_name, sub_name, val, ex = line.split()

    
    if not sub_name in sub_path:
        sub_path.add().name = sub_name
    sub = sub_path[sub_name]
    master_sub = master_sub_path[sub_name]
    
    ptype = master_sub.parametertype
    float_size = {1 : sub.float_one, 2 : sub.float_two, 3 : sub.float_three}
    int_size = {1 : sub.int_one, 2 : sub.int_two, 3 : sub.int_three}
                    
    sub.export = export[ex]
    if ptype == "string": sub.textparameter = val
    
    if ptype == "color":
        for i, v in enumerate(val): 
            sub.colorparameter[i] = float(v)        
                                         
    elif ptype == "float":
        if sub.vector_size > 1:
            for i, v in enumerate(val):
                float_size[sub.vector_size][i] = float(v)
        else:                       
            float_size[sub.vector_size][0] = float(val[0])
        
    elif ptype == "int":
        if sub.vector_size > 1:
            for i, v in enumerate(val):
                int_size[sub.vector_size][i] = int(v)
        else:
            int_size[sub.vector_size][0] = int(val[0])

                   
def load_grp_preset(prs, path, type, scene):
    if type == "attr": grps = path.attribute_groups
    else: grps = path.option_groups
    
    export = {"0" : False, "1" : True}
        
    for line in prs:              
        if len(line.split()) == 2:
            grp_name, grp_export = line.split()
            if not grp_name in grps: grps.add().name = grp_name
            grps[grp_name].export = export[grp_export]
            
        else:
            if type == "attr":
                mgrps = scene.renderman_settings.attribute_groups
            else:
                mgrps = scene.renderman_settings.option_groups
            stype = {   "attr" : [grps[grp_name].attributes, mgrps[grp_name].attributes],
                        "opt" : [grps[grp_name].options, mgrps[grp_name].options]}
            sub = stype[type]
            load_sub_preset(sub[0], sub[1], line)

