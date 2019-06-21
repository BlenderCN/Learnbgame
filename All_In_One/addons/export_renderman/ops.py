
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

##################################################################################################################################

                                  
##################################################################################################################################
#                                                                                                                                #
#       Render Engine Preset Class                                                                                               #
#                                                                                                                                #
##################################################################################################################################

import bpy
import export_renderman
from export_renderman.rm_maintain import *
from export_renderman.rm_preset_funcs import *
#import export_renderman.export as rm_export
import os

String = bpy.props.StringProperty
Bool = bpy.props.BoolProperty
Enum = bpy.props.EnumProperty
CollectionProp = bpy.props.CollectionProperty
Pointer = bpy.props.PointerProperty
FloatVector = bpy.props.FloatVectorProperty
IntVector = bpy.props.IntVectorProperty
Int = bpy.props.IntProperty
Float = bpy.props.FloatProperty

def clear_collections(scene):
    global pass_preset_outputs
    pass_preset_outputs = {}
    rmansettings = scene.renderman_settings
    sh = rmansettings.shaders
    shaderpaths = sh.shaderpaths
    attributes = rmansettings.attribute_groups
    options = rmansettings.option_groups
    hiders = rmansettings.hider_list
    shaders = sh.shadercollection
    surfs = sh.surface_collection
    lights = sh.light_collection
    disps = sh.displacement_collection
    imgs = sh.imager_collection
    vols = sh.volume_collection
    
    collections = [shaderpaths,
                   attributes,
                   options,
                   hiders,
                   shaders,
                   surfs,
                   lights,
                   disps,
                   imgs,
                   vols]
    
    def remcollection(coll):
        for i in range(len(coll)): coll.remove(0)
    
    for c in collections: remcollection(c)
    
    for rpass in rmansettings.passes:
        attributes = rpass.attribute_groups
        options = rpass.option_groups
        hiders = rpass.hider_list
        
        collections = [attributes, options, hiders]
        
        for c in collections: remcollection(c)
        
    for t in dir(bpy.types):
        cl = getattr(bpy.types, t)
        if hasattr(cl, "mclient"):
            bpy.utils.unregister_class(cl)
        
class Renderman_OT_force_modal_restart(bpy.types.Operator):
    bl_idname = "renderman.restart"
    bl_label ="restart modal"
    bl_description = "restart modal Operator"
    
    def invoke(self, context, event):
        restart()
        return{'FINISHED'}

class ExecuteRendermanPreset(bpy.types.Operator): ### modified Blenders internal class from /scripts/ops/presets.py
    ''' Executes a preset '''
    bl_idname = "script.execute_rendermanpreset"
    bl_label = "Execute a Python Preset"

    filepath = bpy.props.StringProperty(name="Path", description="Path of the Python file to execute", maxlen=512, default="")

    def execute(self, context):
#        # change the menu title to the most recently chosen option
#        preset_class = getattr(bpy.types, self.menu_idname)
#        preset_class.bl_label = self.preset_name
        scene = context.scene

        scene.renderman_settings.active_engine = os.path.split(self.filepath)[1].replace(".py", "")

        # execute the preset using script.python_file_run
        clear_collections(context.scene)
        for rpass in context.scene.renderman_settings.passes:
            rpass.hider = ""
        bpy.ops.script.python_file_run(filepath=self.filepath)
        pathcoll = scene.renderman_settings.shaders

        if pathcoll.shaderpaths and not pathcoll.shadercollection:
            checkshadercollection(scene)

        initial_load_data(scene)

        passes = scene.renderman_settings.passes
        maintain_beauty_pass(scene)
        maintain_hiders(passes[0], scene)
        maintain_searchpaths(passes[0], scene)
        
        maintain_lists(scene)
        maintain_rib_structure(self, context) 
        return {'FINISHED'}



class AddPresetRenderer(bpy.types.Operator): ### based on /scripts/ops/presets.py
    '''Add a Render Engine Preset'''
    bl_idname = "renderman.renderengine_preset_add"
    bl_label = "Add Renderman Preset"
    bl_options = {'REGISTER'}

    name = bpy.props.StringProperty(name="Name", 
                                    description="Name of the preset, used to make the path name", 
                                    maxlen=64, 
                                    default="")
    
    preset_subdir = "renderman"

    preset_values = [
        "bpy.context.scene.renderman_settings.renderexec",
        "bpy.context.scene.renderman_settings.shaderexec",
        "bpy.context.scene.renderman_settings.textureexec",
        "bpy.context.scene.renderman_settings.shadersource",
        "bpy.context.scene.renderman_settings.shaderbinary",
        "bpy.context.scene.renderman_settings.shaderinfo",
        "bpy.context.scene.renderman_settings.textureext",
        "bpy.context.scene.renderman_settings.disp_ext",
        "bpy.context.scene.renderman_settings.disp_ext_os_default",
        "bpy.context.scene.renderman_settings.displaydrvpath",
        "bpy.context.scene.renderman_settings.drv_identifier",
        "bpy.context.scene.renderman_settings.deepdisplay",
        "bpy.context.scene.renderman_settings.defaultshadow",
        "bpy.context.scene.renderman_settings.default_hider"
    ]
    
    collection_path = []
    
    def _as_filename(self, name): # could reuse for other presets
        name = bpy.path.clean_name(name, replace='_')
        return name.lower()    
    
    def execute(self, context):
        scene = context.scene                        ### Modified AddPresetBase Class to allow CollectionProperties
        if not self.name:
            return {'FINISHED'}
        presetname = self._as_filename(self.name)
        filename = self.name + '.py'

        preset_path = bpy.utils.preset_paths('')[0]
        if not bpy.utils.preset_paths(self.preset_subdir)[0]:
            os.mkdir(os.path.join(preset_path, self.preset_subdir))
        target_path = bpy.utils.preset_paths(self.preset_subdir)[0]

        filepath = os.path.join(target_path, filename)
        checkForPath(target_path)
        
        file_preset = open(filepath, 'w')
        write = file_preset.write
        write("import bpy\n")
            
        for rna_path in self.preset_values:
            try:
                value = eval(rna_path)
                write(rna_path+' = '+repr(value)+'\n')
            except:
                pass
                        
        rmansettings = bpy.context.scene.renderman_settings
        option_groups = rmansettings.option_groups
        attribute_groups = rmansettings.attribute_groups
        hider_list = rmansettings.hider_list
        shaderpaths = rmansettings.shaders.shaderpaths
        displays = rmansettings.displays
        
        def parmgroups(group):      
            path =  'bpy.context.scene.renderman_settings.'+group              
            for g in eval(path):
                write('if not "'+g.name+'" in '+path+':\n')
                write('\t'+path+'.add().name = "'+g.name+'"\n')            
                g_path = path+'["'+g.name+'"]'
                t = {   'attribute_groups' : '.attributes', 
                        'option_groups' : '.options', 
                        'hider_list' : '.options'}
                parms = g_path+t[group]
                for p in eval(parms):
                    parameters(parms, p)
                    
        def parameters(parms, p):
            parmprops = [   ".parametertype", 
                            ".vector_size", 
                            ".input_type",
                            ".use_var",
                            ".export",
                            ".textparameter", 
                            ".colorparameter[0]",
                            ".colorparameter[1]",
                            ".colorparameter[2]",
                            ".float_one[0]",
                            ".float_two[0]",
                            ".float_two[1]",
                            ".float_three[0]",
                            ".float_three[1]",
                            ".float_three[2]",
                            ".int_one[0]",
                            ".int_two[0]",
                            ".int_two[1]",
                            ".int_three[0]",
                            ".int_three[1]",
                            ".int_three[2]"]
            write('if not "'+p.name+'" in '+parms+':\n')
            write('\t'+parms+'.add().name = "'+p.name+'"\n')                    
            p_path = parms+'["'+p.name+'"]'
            for prop in parmprops:
                prop_path = p_path+prop
                if prop in ['.textparameter', '.parametertype', '.input_type']:
                    val = '"'+eval(prop_path)+'"'
                else:
                    try:
                        val = str(eval(prop_path))
                    except:
                        print(prop_path)
                        raise
                write(prop_path + ' = ' + val +'\n')

        
        ##option presets:
        parmgroups("option_groups")
        
        ##attribute presets:    
        parmgroups("attribute_groups")
        
        ##shaderpath presets:
        s_path = "bpy.context.scene.renderman_settings.shaders.shaderpaths"
        for path in shaderpaths:
            write('if not "'+path.name+'" in '+s_path+':\n')
            write('\t'+s_path+'.add().name = "'+path.name+'"\n')
        
        ##hider presets:
        parmgroups("hider_list")
        
        ##displaydriver custom options presets:
        path = "bpy.context.scene.renderman_settings.displays"

        file_preset.close()

        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


def write_sub_preset(grp, sub_path, write):
    for sub in sub_path:
        write_sub_preset_parameter(grp, sub, write)
            
def write_sub_preset_parameter(grp, sub, write):
    export = {True : "1", False : "0"}
    if sub.preset_include:
        float_size = {1 : sub.float_one, 2 : sub.float_two, 3 : sub.float_three}
        int_size = {1 : sub.int_one, 2 : sub.int_two, 3 : sub.int_three}
        type = {"float" : float_size, "int" : int_size}

        ptype = sub.parametertype
        
        write(grp.name + " " + sub.name + " ")
        if ptype == "string":
            write('"'+sub.textparameter+'" ')
        elif ptype == "color":
            r, g, b = sub.colorparameter
            write("("+str(r)+" "+str(g)+" "+str(b)+") ")
        elif ptype in ["float", "int"]:
            v = sub.vector_size
            if v == 1:
                a = type[ptype][v][0]
                write(str(a)+" ")
            elif v == 2:
                a, b = type[ptype][v]
                write("("+str(a)+" "+str(b)+") ")
            elif v == 3:
                a, b, c = type[ptype][v]
                write("("+str(a)+" "+str(b)+" "+str(c)+") ")
        write(export[sub.export]+"\n")
            
            
def write_grp_preset(path, type, write):
    if type == "attr":
        gtype = path.attribute_groups
    else:
        gtype = path.option_groups
                                    
    for grp in gtype:
        export = {True : "1", False : "0"}
        if grp.preset_include:
            write(grp.name+" "+export[grp.export]+"\n")
            stype = {   'attr' : grp.attributes,
                        'opt' : grp.options}               
            write_sub_preset(grp, stype[type], write)
       

class AddAttributePreset(bpy.types.Operator):
    bl_label = "add Preset"
    bl_idname = "attribute.add_preset"
    bl_description = "add preset for current attributes"
    
    obj = bpy.props.StringProperty(default = "", name="Object Name")
    part = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        renderman_settings = context.scene.renderman_settings
        layout = self.layout
        if self.obj == "":
            attribute_groups = getactivepass(context.scene).attribute_groups
        else:
            obj = context.scene.objects[self.obj]
            if self.part != "":
                part = obj.particle_systems[self.part]
                rm = part.settings.renderman[part.settings.renderman_index]
                attribute_groups = rm.attribute_groups
            else:
                rm = obj.renderman[obj.renderman_index]
                attribute_groups = rm.attribute_groups
        for g in attribute_groups:               
            layout.prop(g, "preset_include", text=g.name)
            
            for a in g.attributes:
                row =layout.row()
                if not g.preset_include:
                    row.enabled = False
                row.prop(a, "preset_include", text="- "+a.name)
        layout.prop(renderman_settings, "presetname")
        
    def execute(self, context):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        target_path = bpy.utils.preset_paths("renderman")
        if not target_path:
            return
        target_path = os.path.join(target_path[0], rmansettings.active_engine)
        checkForPath(target_path)
        filename = rmansettings.presetname+".preset"
        rmansettings.presetname = ""
        filename = filename.replace(" ", "_")
        subpreset = os.path.join(target_path, filename)
        
        try:
            file = open(subpreset, "w")
        except:
            print("file not found")
            return {'CANCELLED'}
        
        if self.obj == "":
            rm = getactivepass(context.scene)
        else:
            obj = context.scene.objects[self.obj]
            if self.part != "":
                part = obj.particle_systems[self.part]
                rm = part.settings.renderman[part.settings.renderman_index]
            else:
                rm = obj.renderman[obj.renderman_index]
        
        file = open(subpreset, "w")
        write = file.write
        write_grp_preset(rm, "attr", write)
                    
        return {'FINISHED'}  

class LoadAttributePreset(bpy.types.Operator):
    bl_label = "load Preset"
    bl_idname = "attribute.load"
    bl_description = "load preset"
    
    preset = String(default = "")
    path = String(default = "")
    
    def execute(self, context):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        preset_path = bpy.utils.preset_paths('renderman')
        if not preset_path:
            return
        target_path = os.path.join(preset_path[0], rmansettings.active_engine)

        preset = self.preset
        try:
            path = eval(self.path)
        except:
            print("path:", self.path)
            raise
            
        filename = preset+".preset"
        subpreset = os.path.join(target_path, filename)
        
        try:
            file = open(subpreset, "r")
        except:
            print("file not found")
            return {'CANCELLED'}

        attributes = file.readlines()
        load_grp_preset(attributes, path, "attr", scene)
                    
        return {'FINISHED'}
   
   
class LoadAttributePresetSelected(bpy.types.Operator):
    bl_label = "load Preset"
    bl_idname = "attributes.load_selected"
    bl_description = "load Attribute Preset to selected"
    
    preset = bpy.props.StringProperty()
    
    def execute(self, context):
        preset = self.preset
        for obj in context.scene.objects:
            if obj.select:
                path = 'bpy.context.scene.objects["'+obj.name+'"]'
                if obj.type == "LAMP":
                    path += '.data'
                path += '.renderman['+path+'.renderman_index]'
                bpy.ops.attribute.load(preset = preset, path = path)
                
        return {'FINISHED'}
        
class Renderman_OT_Attributes_remove_all_selected(bpy.types.Operator):
    bl_label = "remove All"
    bl_idname = "attributes.remove_all_selected"
    bl_description = "remove all attributes from selected objects"
    
    def invoke(self, context, event):
        for obj in context.scene.objects:
            if obj.select:
                if obj.type == "LAMP":
                    rm = obj.data.renderman[obj.data.renderman_index]
                else:
                    rm = obj.renderman[obj.renderman_index]
                
                for grp in rm.attribute_groups:
                    rm.attribute_groups.remove(0)
                    
        return {'FINISHED'}
   
##################################################################################################################################
class Renderman_OT_Set_Pass_Index(bpy.types.Operator):
    bl_label = ""
    bl_idname = "renderman.set_pass_index"

    def execute(self, context):
        rm = context.scene.renderman_settings
        rm.passes_index = len(rm.passes)-1
        return {'FINISHED'}

#########################################################################################################
#                                                                                                       #
#       Operators                                                                                       #
#       (mainly for adding/removing and moving items of CollectionProperties)                           #
#                                                                                                       #
#########################################################################################################

#############################################
#                                           #
#   Light Linking Operator                  #
#                                           #
#############################################

class Renderman_OT_LightLinking(bpy.types.Operator):
    bl_label="Light Linking"
    bl_idname="renderman.lightlinking"
    bl_description="Light Linking"

    type = bpy.props.EnumProperty(items = (
                                            ("all", "", ""),
                                            ("none", "", ""),
                                            ("invert", "", "")
                                            ),
                                    default = "all"
                                    )

    def invoke(self, context, event):
        scene = context.scene
        obj = context.object
        light_list = obj.renderman[obj.renderman_index].lightlist
        if self.type == "invert":
            for light in getLightList(scene):
                if light in light_list:
                    light_list.remove(light_list.keys().index(light))
                else:
                    light_list.add().name = light
        if self.type == "all":
            for light in getLightList(scene):
                if not light in light_list:
                    light_list.add().name = light
        elif type == "none":
            for l in light_list:
                light_list.remove(0)
        return {'FINISHED'}

#############################################
#                                           #
#   Display Operator                        #
#                                           #
#############################################

class Renderman_OT_addDisplay(bpy.types.Operator):
    bl_label = "addDisplay"
    bl_idname = "renderman.adddisplay"
    bl_description = "add Display Driver"
    
    def invoke(self, context, event):
        adddisp(getactivepass(context.scene), scene=context.scene)
        return {'FINISHED'}

class Renderman_OT_removeDisplay(bpy.types.Operator):
    bl_label = "removeDisplay"
    bl_idname = "renderman.remdisplay"
    bl_description = "remove Display Driver"
    
    index = bpy.props.IntProperty(min = -1, max=10000, default=-1)

    def invoke(self, context, event):
        scene = context.scene
        active_pass = getactivepass(scene)
        index = self.index
        active_pass.displaydrivers.remove(index)
        return {'FINISHED'}

class Renderman_OT_adddisplayoption(bpy.types.Operator):
    bl_label = "add option"
    bl_description = "add custom display option"
    bl_idname="displayoption.add"
    
    disp = bpy.props.IntProperty()
        
    def invoke(self, context, event):
        scene = context.scene
        disp = self.disp
        display = scene.renderman_settings.displays[disp]
        defcount = 1
        
        def getdefname(name, count):
            countstr = "0"*(2 - len(str(count))) + str(count)
            defaultname = name+countstr
            return defaultname
    
        defname = "Default01"
    
        for item in display.custom_parameter:
            if item.name == defname:
                defcount +=1
                defname = getdefname("Default", defcount)    
        display.custom_parameter.add().name = defname
        maintain_render_passes(scene)
    
        return {'FINISHED'}          

class Renderman_OT_refreshDisplayOption(bpy.types.Operator):
    bl_label = "Refresh"
    bl_idname = "displayoption.refresh"
    bl_description = "refresh display options"

    def invoke(self, context, event):
        scene = context.scene
        rm = scene.renderman_settings
        for rpass in rm.passes:
            maintain_display_options(rpass, rm)
        return {'FINISHED'}
         
        
class Renderman_OT_removedisplayoption(bpy.types.Operator):
    bl_label = "remove option"
    bl_description = "remove custom display option"
    bl_idname="displayoption.remove"
    
    disp = bpy.props.IntProperty()
    opt = bpy.props.IntProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        disp = self.disp
        opt = self.opt
        displays = scene.renderman_settings.displays
        displays[disp].custom_parameter.remove(opt)
        return {'FINISHED'} 
        
class Renderman_OT_senddisplay(bpy.types.Operator):
    bl_label = "send Display"
    bl_idname = "display.send"
    bl_description = "send display driver to Render Result"
    
    display = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = scene.renderman_settings
        active_pass = getactivepass(scene)

        if active_pass.displaydrivers[self.display].send:
            active_pass.displaydrivers[self.display].send = False
        else:
            
            for disp in active_pass.displaydrivers:                
                disp.send = False
                        
            active_pass.renderresult = self.display
            active_pass.displaydrivers[self.display].send = True
        
        return {'FINISHED'}            
        
#############################################
#                                           #
#   passes Operator                         #
#                                           #
#############################################

class Renderman_OT_addPassPreset(bpy.types.Operator):
    bl_label = "Add Preset"
    bl_idname = "renderman.addpasspreset"
    bl_description = "add Pass Preset"
    
    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        wm.invoke_popup(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rmansettings = scene.renderman_settings
        layout.prop(rmansettings, "preset_subfolder", text="Folder")
        layout.prop(rmansettings, "presetname", text="Name")
        layout.operator("renderman.writepasspreset")
        

class Renderman_OT_writePassPreset(bpy.types.Operator):
    bl_label = "Write Preset"
    bl_idname = "renderman.writepasspreset"
    bl_description = "write Pass Preset"
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = scene.renderman_settings
        active_pass = getactivepass(scene)
        active_engine = scene.renderman_settings.active_engine
        preset_path = bpy.utils.preset_paths('') 
        if not bpy.utils.preset_paths('renderman'):
            os.mkdir(os.path.join(preset_path, 'renderman'))
        main_preset_path = bpy.utils.preset_paths('renderman')[0]
        sub_preset_path = os.path.join(main_preset_path, active_engine)
        checkForPath(sub_preset_path)
        preset = rmansettings.presetname
        subfolder = rmansettings.preset_subfolder
        preset_path = os.path.join(sub_preset_path, subfolder)
        checkForPath(preset_path)
        rmansettings.preset_subfolder = ""
        rmansettings.presetname = ""
        
        preset_file = os.path.join(preset_path, preset)+'.pass'
        
        file = open(preset_file, "w")

        e = ' = '
        a_pass = 'bpy.context.scene.renderman_settings.passes["'+active_pass.name+'"].'
        def w(slist): 
            for s in slist:
                val_raw = eval(a_pass+s)
                if type(val_raw) == type(""): val = '"'+val_raw+'"'
                else: val = str(val_raw)
                file.write(s + e + val + '\n')
        
        ## Settings
        #imagedir
        file.write('##ImageFolder\n')
        w(['imagedir'])
        file.write('##\n\n')
        
        # Quality
        file.write('##Quality\n')
        w([ 'pixelsamples_x',
            'pixelsamples_y',
            'pixelfilter.filterlist',
            'pixelfilter.filterheight',
            'pixelfilter.filterwidth',
            'pixelfilter.customfilter',
            'override_shadingrate',
            'shadingrate'])
        file.write('##\n\n')
        
        # Motion Blur
        file.write('##Motion Blur\n')
        w([ 'motionblur',
            'shutterspeed_sec',
            'shutterspeed_ang'])
        file.write('##\n\n')
        
        # Export Objects
        file.write('##Export Objects\n')
        w([ 'exportobjects',
            'objectgroup'])
        file.write('##\n\n')
        
        # Export Lights
        file.write('##Export Lights\n')
        w([ 'exportlights',
            'lightgroup'])
        file.write('##\n\n')
        
        # Animate Pass
        file.write('##Animate Pass\n')
        w(['exportanimation'])
        file.write('##\n\n')
        
        ## Options
        file.write('##Options\n')
        write_grp_preset(active_pass, "opt", file.write)
        file.write('##\n\n')
        
        ## Hider
        hider = active_pass.hider
        if hider in scene.renderman_settings.hider_list:
            file.write('##Hider\n')
            file.write(hider+'\n')
            curr_hider = active_pass.hider_list[hider]
            write_sub_preset(curr_hider, curr_hider.options, file.write)
            file.write('##\n\n')
        
        ## Display Driver
        file.write('##Displays\n')
        for disp in active_pass.displaydrivers:
            file.write('NewDisplay '+disp.name+'\n')
            disppath = 'displaydrivers["'+disp.name+'"].'
            prpath = disppath + 'processing.'
            w([ disppath+'name',
                disppath+'displaydriver',
                disppath+'default_name',
                disppath+'file',
                disppath+'filename',
                disppath+'raw_name',
                disppath+'gain',
                disppath+'gamma',
                disppath+'quantize_presets',
                disppath+'quantize_black',
                disppath+'quantize_white',
                disppath+'quantize_min',
                disppath+'quantize_max',
                disppath+'send',
                disppath+'var',
                prpath+'process',
                prpath+'output',
                prpath+'default_output',
                prpath+'filter',
                prpath+'custom_filter',
                prpath+'width',
                prpath+'swidth',
                prpath+'twidth',
                prpath+'stwidth',
                prpath+'envcube',
                prpath+'fov',
                prpath+'shadow',
                prpath+'custom_parameter'])
            file.write('#Custom Options\n')
            write_sub_preset(disp, disp.custom_options, file.write)
        file.write('##\n\n')
        
        ## Custom Pass Rib Code
        file.write('##Custom Scene RIB Code\n')
        for sc in active_pass.scene_code:
            file.write('NewCode '+sc.name+'\n')
            scpath = 'scene_code["'+sc.name+'"].'
            w([ scpath + 'foreach',
                scpath + 'position',
                scpath + 'world_position',
                scpath + 'all_dirs',
                scpath + 'makesahdow',
                scpath + 'makecubefaceenv',
                scpath + 'output',
                scpath + 'default_output',
                scpath + 'filter',
                scpath + 'custom_filter',
                scpath + 'width',
                scpath + 'swidth',
                scpath + 'twidth',
                scpath + 'stwidth',
                scpath + 'blur',
                scpath + 'fov'])
            write_sub_preset_parameter(sc, sc.parameter, write)
        file.write('##\n\n')
        
        ## Custom World Rib Code
        file.write('##Custom World RIB Code\n')
        for wc in active_pass.world_code:
            file.write('NewCode '+wc.name+'\n')
            wcpath = 'scene_code["'+wc.name+'"].'
            w([ wcpath + 'foreach',
                wcpath + 'position',
                wcpath + 'world_position',
                wcpath + 'all_dirs',
                wcpath + 'makesahdow',
                wcpath + 'makecubefaceenv',
                wcpath + 'output',
                wcpath + 'default_output',
                wcpath + 'filter',
                wcpath + 'custom_filter',
                wcpath + 'width',
                wcpath + 'swidth',
                wcpath + 'twidth',
                wcpath + 'stwidth',
                wcpath + 'blur',
                wcpath + 'fov'])
            write_sub_preset_parameter(wc, wc.parameter, write)
        file.write('##\n\n')
        
        ## World Attribute Preset World Shading Rate, etc. Settings(overrides for Objects)
        file.write('##Attributes\n')
        write_grp_preset(active_pass, "attr", file.write)
        file.write('##\n\n')
        
        ##World Shaders
        file.write('##World Shaders\n')
        gshad = active_pass.global_shader
        g = 'global_shader.'
        w([ 'imager_shader',
            g+'surface_shader',
            g+'atmosphere_shader'])
        file.write('##\n\n')

        def shader_presets(shader_parameter, shad_path):
            for parm in shader_parameter:
                parm_path = shad_path+'["'+parm.name+'"].'
                w([ parm_path+"textparameter",
                    parm_path+"vector_size",
                    parm_path+"parametertype",
                    parm_path+"float_one[0]",
                    parm_path+"float_two[0]",
                    parm_path+"float_two[1]",
                    parm_path+"float_three[0]",
                    parm_path+"float_three[1]",
                    parm_path+"float_three[2]",
                    parm_path+"int_one[0]",
                    parm_path+"int_two[0]",
                    parm_path+"int_two[1]",
                    parm_path+"int_three[0]",
                    parm_path+"int_three[1]",
                    parm_path+"int_three[2]",
                    parm_path+"input_type",
                    parm_path+"colorparameter[0]",
                    parm_path+"colorparameter[1]",
                    parm_path+"colorparameter[2]"])
                file.write('##\n\n')
                        
        ##Imager
        if active_pass.imager_shader != "":
            file.write('##Imager\n')        
            shader_presets(active_pass.imager_shader_parameter, 'imager_shader_parameter')                        

        ##Surface
        if gshad.surface_shader != "":
            file.write('##Surface\n')        
            shader_presets(gshad.surface_shader_parameter, g+'surface_shader_parameter')
            
        ##Atmosphere
        if gshad.atmosphere_shader != "":
            file.write('##Atmosphere\n')        
            shader_presets(gshad.atmosphere_shader_parameter, g+'atmosphere_shader_parameter')
        file.write('##\n\n')                  
        return {'FINISHED'}
       
class Renderman_OT_loadPresetPass(bpy.types.Operator):
    bl_label = "Load Pass Preset"
    bl_idname = "renderman.loadpresetpass"
    bl_description = "load Preset Pass"
    
    props = bpy.props
    
    preset = props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        current_pass = getactivepass(scene)
       
        preset = self.preset
        
        invoke_preset(current_pass, preset, scene)
        return {'FINISHED'}

class Renderman_OT_delete_request(bpy.types.Operator):
    bl_label = "delete Request"
    bl_idname = "renderman.deleterequest"
    bl_description = "Delete requested Render Pass"
    
    r = bpy.props.IntProperty(min=-1, max=1000, default=-1)
    client = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        client = context.scene.objects[self.client]
        req = client.requests[self.r]
        dirs = ['px', 'nx', 'py', 'ny', 'pz', 'nz']
        env = False
        for dir in dirs:
            if req.name.find(dir) != -1:
                env = True
                path_base = req.name[:req.name.find(dir)]
        if env:
            i = 0
            while i < len(client.requests):
                r = client.requests[i]
                if r.name.find(path_base) != -1:
                    parm = eval("client."+r.name)
                    parm.textparameter = ""
                    client.requests.remove(i)
                    i -= 1
                i += 1
                    
        else:
            parm = eval("client."+req.name)
            client.requests.remove(self.r)
            parm.textparameter = ""

            for rpass in context.scene.renderman_settings.passes:
                maintain_client_passes_remove(context.scene)
        return {'FINISHED'}

class Renderman_OT_requestPresetPass(bpy.types.Operator):
    bl_label = "request Pass"
    bl_idname = "renderman.requestpresetpass"
    bl_description =  "request a Preset Pass"
    
    preset = bpy.props.StringProperty()
    output = bpy.props.StringProperty()
    client = bpy.props.StringProperty()
    client_path = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        preset = self.preset
        cl_rpass = ""
        request_pass = ""
        if self.client != "":
            client = scene.objects[self.client.split()[0]]
            cl_requests = client.requests
            if client.type == 'LAMP':
                string = "data.renderman["+str(client.data.renderman_index)+"]"
                rm = eval("client."+string)
            else:
                if len(self.client.split()) > 1:
                    part = 'particle_systems["'+self.client.split()[1]+'"]'
                    string = part + ".settings.renderman["+str(eval("client."+part+".settings.renderman_index"))+"]"
                    rm = eval("client."+string)
                else:
                    string = "active_material.renderman["+str(client.renderman_index)+"]"
                    rm = eval("client."+string)
            
            request_pass = rm.name       
            for rpass in scene.renderman_settings.passes:
                if rpass.name in rm.links:
                    cl_rpass = rpass.name
                    break
        else: 
            cl_requests = scene.renderman_settings.requests
            request_pass = getactivepass(scene).name
            cl_rpass = getactivepass(scene).name
            
        def addreq(clp):
            if not clp in client.requests:
                path = string+'.'+clp
                cl_requests.add().name = path
                cl_r = cl_requests[path]
                cl_r.output = self.output
                cl_r.preset = self.preset
                cl_r.render_pass = cl_rpass
                cl_r.request_pass = request_pass
                cl_r.client = self.client
        
        dirs = ['px', 'nx', 'py', 'ny', 'pz', 'nz']
        env = False
        for dir in dirs:
            if self.client_path.find(dir) != -1:
                env = True
                path_dir = dir
        if env:
            for dir in dirs:
                client_path = self.client_path.replace(path_dir, dir)
                addreq(client_path)
        else:
            addreq(self.client_path)

        maintain_client_passes_add(context.object, scene)
        
        return {'FINISHED'}
        
        
class Renderman_OT_addPresetPass(bpy.types.Operator):
    bl_label = "Add Pass"
    bl_idname = "renderman.addpresetpass"
    bl_description = "add Preset Pass"
    
    props = bpy.props
    
    preset = props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        passes = scene.renderman_settings.passes
       
        preset = self.preset
        name = preset
        defcount = 1
        defname = name+"01"
        print(name)
        for item in passes:
            if item.name == defname:
                defcount += 1
                defname = name + "0"*(2 - len(str(defcount))) + str(defcount)
        passes.add().name = defname
        maintain_render_passes(passes[defname], scene)
        invoke_preset(passes[defname], preset, scene)
        
        return {'FINISHED'}
        
class Renderman_OT_remPass(bpy.types.Operator):
    bl_label = "Remove Pass"
    bl_idname = "renderman.rempass"
    bl_description = "Remove Renderman Pass"
    
    path = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        rm = context.scene.renderman_settings
        if self.path == "":
            path = rm.passes
            index = rm.passes_index
        else:
            path = eval(self.path)
            index = eval(self.path+'_index')
        path.remove(index)
        
        return {'FINISHED'}
          

class Renderman_OT_addPass(bpy.types.Operator):
    bl_label = "addPass"
    bl_idname = "renderman.addpass"
    bl_description = "add render Pass"
    
    path = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        rm = scene.renderman_settings
        passes = eval(self.path)
        name = "Default"
        defcount = 1
        defname = "Default01"
        for item in passes:
            if item.name == defname:
                defcount += 1
                defname = name + "0"*(2 - len(str(defcount))) + str(defcount)
        passes.add().name = defname
        if passes == rm.passes:
            maintain_hiders(passes[defname], scene)
            maintain_searchpaths(passes[defname], scene)
        else:
            if len(passes) == 1:
                bpy.ops.renderman.link_pass(path=self.path, rpass=rm.passes[0].name)
        maintain_rib_structure(self, context) 
        return{'FINISHED'}

class Renderman_OT_movepass(bpy.types.Operator):
    bl_label = "movepass"
    bl_idname = "renderman.movepass"
    bl_description = "move Pass"

    direction = bpy.props.EnumProperty(items = (
                                                    ("up", "up", "up"),
                                                    ("down", "down", "down")
                                                ),
                                        default = "up",
                                        name = "Direction",
                                        description = "Direction to move Pass")

    def invoke(self, context, event):
        renderman_settings = context.scene.renderman_settings
        index = renderman_settings.passes_index
        if self.direction == "up":
            renderman_settings.passes.move(index, index-1)
        elif self.direction == "down":
            renderman_settings.passes.move(index, index+1)
        return{'FINISHED'}


#############################################
#                                           #
#   Render Operator                         #
#                                           #
#############################################


class Renderman_OT_addOptionGroup(bpy.types.Operator):
    bl_label = "addOptionGroup"
    bl_idname = "renderman.addoptiongroup"
    bl_description = "add Renderman Option Group"
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        master_option_groups = rmansettings.option_groups
        master_option_groups.add()
        return {'FINISHED'}
    
class Renderman_OT_removeOptionGroup(bpy.types.Operator):
    bl_label = "removeOptionGroup"
    bl_idname = "renderman.removeoptiongroup"
    bl_description = "remove Renderman Option Group"
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        index = rmansettings.option_groups_index
        master_option_groups = rmansettings.option_groups
        master_option_groups.remove(index)
    
        return {'FINISHED'}              

class Renderman_OT_addOption(bpy.types.Operator):
    bl_label = "addOption"
    bl_idname = "renderman.addoption"
    bl_description = "add Renderman Option"

    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        group_index = rmansettings.option_groups_index
        master_options = rmansettings.option_groups[group_index].options
        master_options.add()
        return {'FINISHED'}

class Renderman_OT_removeOption(bpy.types.Operator):
    bl_label = "removeOption"
    bl_idname = "renderman.remoption"
    bl_description = "remove Option"

    index = bpy.props.IntProperty(min = -1, max = 10000, default = -1)

    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        group_index = rmansettings.option_groups_index
        master_options = rmansettings.option_groups[group_index].options
        index = self.index
        master_options.remove(index)
        return {'FINISHED'} 
 

class Renderman_OT_set_all_as_default(bpy.types.Operator):
    bl_label = "set_as_default"
    bl_idname = "options.set_as_default"
    bl_description = "set values of all options as default for new passes"

    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        copy_parameters(rmansettings.option_groups, getactivepass(context.scene).option_groups)  
        return {'FINISHED'}  
    
class Renderman_OT_get_all_defaults(bpy.types.Operator):
    bl_label = "get_default"
    bl_idname = "options.get_default"
    bl_description = "get the default values for options in active pass"

    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        copy_parameters(getactivepass(context.scene).option_groups, rmansettings.option_groups)
        return {'FINISHED'}   


class Renderman_OT_set_current_default(bpy.types.Operator):
    bl_label = "set current option defaults"
    bl_idname = "option.set_default"
    bl_description = "set current value as default"
   
    
    grp = bpy.props.StringProperty()
    attr = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        grp = self.grp
        opt = self.attr
        
        master_option = rmansettings.option_groups[grp].options[opt]
        slave_option = getactivepass(context.scene).option_groups[grp].options[opt]
    
        copy_parameter(master_option, slave_option)
    
        return {'FINISHED'}          
    
class Renderman_OT_get_current_default(bpy.types.Operator):
    bl_label = "get current option defaults"
    bl_idname = "option.get_default"
    bl_description = "get default value"
    
    grp = bpy.props.StringProperty()
    attr = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        grp = self.grp
        opt = self.attr
        
        master_option = rmansettings.option_groups[grp].options[opt]
        slave_option = getactivepass(context.scene).option_groups[grp].options[opt]
    
        copy_parameter(slave_option, master_option) 
    
        return {'FINISHED'}          
        
class Renderman_OT_get_group_default(bpy.types.Operator):
    bl_label = "get group defaults"
    bl_idname = "option_group.get_default"
    bl_description = "get defaults for current group"
    
    grp = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        grp = self.grp
        master_group = rmansettings.option_groups[grp]
        slave_group = getactivepass(context.scene).option_groups[grp]
    
        for master_option in master_group.options:
            slave_option = slave_group.options[master_option.name]
            copy_parameter(slave_option, master_option)  
    
        return {'FINISHED'}              
            
class Renderman_OT_set_group_default(bpy.types.Operator):
    bl_label = "set group defaults"
    bl_idname = "option_group.set_default"
    bl_description = "set defaults for current group"
    
    grp = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        grp = self.grp
        master_group = rmansettings.option_groups[grp]
        slave_group = getactivepass(context.scene).option_groups[grp]
    
        for master_option in master_group.options:
            slave_option = slave_group.options[master_option.name]
            copy_parameter(master_option, slave_option)                                                                                                                
    
        return {'FINISHED'}  
    
#############################################
#                                           #
#  World Operator                           #
#                                           #
#############################################  
class Renderman_OT_addnew_Attribute(bpy.types.Operator):
    bl_label = ""
    bl_idname = "attributes.add_new"
    bl_description = "add new attribute"
    
    grp = String()
    attr = String()
    path = String()
    
    def execute(self, context):
        rm = context.scene.renderman_settings
        if self.path != "":
            path = eval(self.path)
            master_grp = rm.attribute_groups[self.grp]
            mparameters = master_grp.attributes
            grps = path.attribute_groups
        else:
            master_grp = rm.option_groups[self.grp]
            mparameters = master_grp.options
            grps = getactivepass(context.scene).option_groups
            
        master_attr = mparameters[self.attr]

        
        if not self.grp in grps:
            grps.add().name = self.grp
        grp = grps[self.grp]
        grp.export = master_grp.export
        if self.path != "":
            sparameters = grp.attributes
        else:
            sparameters = grp.options
        if not self.attr in sparameters:
            sparameters.add().name = self.attr
        attr = sparameters[self.attr]
        copy_parameter(attr, master_attr)
        return {'FINISHED'}
    

class Renderman_OT_remove_Attribute(bpy.types.Operator):
    bl_label = ""
    bl_idname = "attributes.remove"
    bl_description = "remove attribute"
    
    type = bpy.props.EnumProperty(default = "all", items = (("all", "All", ""),
                                                            ("attrgrp", "Group", ""),
                                                            ("optgrp", "Group", ""),
                                                            ("attr", "Attribute", ""),
                                                            ("opt", "Options", "")))
    grp = String()
    attr = String()
    path = String()
    
    def invoke(self, context, event):
        try:
            path = eval(self.path)
        except:
            print(self.path)
            raise
        type = self.type
        if type in ["opt", "optgrp"]:
            grps = path.option_groups
        else:
            grps = path.attribute_groups
        if self.grp != "":
            grp = grps[self.grp]
        
        if type == "all":
            for g in grps:
                grps.remove(0)
                
        elif type in ["opt", "attr"]:
            if type == "opt":
                p = grp.options
            else:
                p = grp.attributes
            for i, a in enumerate(p):
                if a.name == self.attr:
                    p.remove(i)
        else:
            for i, g in enumerate(grps):
                if g.name == self.grp:
                    grps.remove(i)
        return {'FINISHED'}
            

class Renderman_OT_addAttributeGroup(bpy.types.Operator):
    bl_label = "addAttributeGroup"
    bl_idname = "renderman.addattributegroup"
    bl_description = "add Renderman Attribute Group"
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        master_attribute_groups = rmansettings.attribute_groups
        master_attribute_groups.add()
        return {'FINISHED'}
    
class Renderman_OT_removeAttributeGroup(bpy.types.Operator):
    bl_label = "removeAttributeGroup"
    bl_idname = "renderman.removeattributegroup"
    bl_description = "remove Renderman Attribute Group"
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        index = rmansettings.attribute_groups_index
        master_attribute_groups = rmansettings.attribute_groups
        master_attribute_groups.remove(index)
    
        return {'FINISHED'}          

class Renderman_OT_addAttribute(bpy.types.Operator):
    bl_label = "addAttribute"
    bl_idname = "renderman.addattribute"
    bl_description = "add Attribute"

    def invoke(self, context, event):
        renderman_settings = context.scene.renderman_settings 
        group_index = renderman_settings.attribute_groups_index
        attributes = renderman_settings.attribute_groups[group_index].attributes
        attributes.add()
        return {'FINISHED'}

class Renderman_OT_removeAttribute(bpy.types.Operator):
    bl_label = "removeAttribute"
    bl_idname = "renderman.remattribute"
    bl_description = "remove Attribute"

    index = bpy.props.IntProperty(min=-1, max=10000, default=-1)

    def invoke(self, context, event):
        renderman_settings = context.scene.renderman_settings
        group_index = renderman_settings.attribute_groups_index
        attributes = renderman_settings.attribute_groups[group_index].attributes    
        index = self.index
        attributes.remove(index)
        return {'FINISHED'}


class Renderman_OT_attributes_set_as_default(bpy.types.Operator):
    bl_label = "attributes_set_as_default"
    bl_idname = "attributes.set_as_default"
    bl_description = "set values of all attributes as default for new passes"

    path = String()

    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        path = eval(self.path)
        copy_parameters(rmansettings.attribute_groups, path.attribute_groups, False)
        return {'FINISHED'}  
    
class Renderman_OT_attributes_get_default(bpy.types.Operator):
    bl_label = "get_default_attributes"
    bl_idname = "attributes.get_default"
    bl_description = "get the default values for attributes in active pass"

    path = String()

    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        path = eval(self.path)
        copy_parameters(path.attribute_groups, rmansettings.attribute_groups, False)
        return {'FINISHED'}  
    
    
class Renderman_OT_get_current_attribute_default(bpy.types.Operator):
    bl_label = "get current attribute defaults"
    bl_idname = "attribute.get_default"
    bl_description = "get default value"
    
    grp = String()
    attr = String()
    path = String()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        grp = self.grp
        attr = self.attr
        path = eval(self.path)
        
        master_attribute = rmansettings.attribute_groups[grp].attributes[attr]
        slave_attribute = path.attribute_groups[grp].attributes[attr]
    
        copy_parameter(slave_attribute, master_attribute)
    
        return {'FINISHED'}          
        
class Renderman_OT_set_current_attribute_default(bpy.types.Operator):
    bl_label = "set current attribute defaults"
    bl_idname = "attribute.set_default"
    bl_description = "set current value as default"
   
    
    grp = String()
    attr = String()
    path = String()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        grp = self.grp
        attr = self.attr
        path = eval(self.path)
        
        master_attribute = rmansettings.attribute_groups[grp].attributes[attr]
        slave_attribute = path.attribute_groups[grp].attributes[attr]
    
        copy_parameter(master_attribute, slave_attribute)    
    
        return {'FINISHED'}          
        
class Renderman_OT_get_attr_group_default(bpy.types.Operator):
    bl_label = "get group defaults"
    bl_idname = "attribute_group.get_default"
    bl_description = "get defaults for current group"
    
    grp = String()
    path = String()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        grp = self.grp
        path = eval(self.path)
        master_group = rmansettings.attribute_groups[grp]
        slave_group = path.attribute_groups[grp]
        
        slave_group.export = master_group.export
        for master_attribute in master_group.attributes:
            if master_attribute.name in slave_group.attributes:
                slave_attribute = slave_group.attributes[master_attribute.name]
                copy_parameter(slave_attribute, master_attribute)
    
        return {'FINISHED'}              
            
class Renderman_OT_set_attr_group_default(bpy.types.Operator):
    bl_label = "set group defaults"
    bl_idname = "attribute_group.set_default"
    bl_description = "set defaults for current group"
    
    grp = String()
    path = String()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        grp = self.grp
        path = eval(self.path)
        master_group = rmansettings.attribute_groups[grp]
        slave_group = path.attribute_groups[grp]
    
        master_group.export = slave_group.export
        for master_attribute in master_group.attributes:
            if master_attribute.name in slave_group.attributes:
                slave_attribute = slave_group.attributes[master_attribute.name]
                copy_parameter(master_attribute, slave_attribute)                   
    
        return {'FINISHED'}  

class RENDERMAN_OT_Attribute_Menu_OP(bpy.types.Operator):
    bl_label = ""
    bl_idname = "object.renderman_menu_attr_op"
    bl_description = ""

    path = bpy.props.StringProperty()
    name = bpy.props.StringProperty()
    selected = bpy.props.BoolProperty(default=False)

    def draw(self, context):
        obj = ""
        part = ""
        if self.name.find("object") != -1:
            obj = context.object.name
        elif self.name.find("particles") != -1:
            obj = context.object.name
            part = context.particle_system.name
        layout = self.layout
        layout.menu("attribute_"+self.name)
        layout.menu(name+"_attributepresets", text="Presets")
        if path != "":
            op = layout.operator("attribute.add_preset", text="save preset")
            op.obj = obj
            op.part = part
        if selected:
            layout.operator("attributes.remove_all_selected")

    def execute(self, context):
        scene = context.scene
    
        self.create_menus(scene.renderman_settings)
        
        wm = context.window_manager
        return wm.invoke_popup(self)


    def create_menus(self, rm):
        ## Attributes 
        def attrMenuDraw(self, context):
            layout = self.layout
            rman = context.scene.renderman_settings
            if name.find("Options") != -1:
                groups = rman.option_groups
                sub = groups[self.grp_name].options
            else:
                groups = rman.attribute_groups
                sub = groups[self.grp_name].attributes
            
            for attr in sub:
                attrname = attr.name
                if selected:
                    op = layout.operator("attributes.add_new_selected", text=attrname)
                else:
                    op = layout.operator("attributes.add_new", text=attrname)
                    op.path = path
                op.grp = self.grp_name
                op.attr = attrname
        
        mtype = bpy.types.Menu
        if self.name.find("Options") != -1:
            t = "option"
            groups = rm.option_groups
        else:
            t = "attribute"
            groups = rm.attribute_groups

        for grp in groups:
            mname = grp.name+"add"+t
            cls = type(mtype)(mname, (mtype,), {  "bl_label" : grp.name, 
                                            "grp_name" : grp.name, 
                                            "draw" : attrMenuDraw,
                                            "path" : self.path})
            bpy.utils.register_class(cls)

#############################################
#                                           #
#   Object Operators                        #
#                                           #
#############################################

class Renderman_OT_lightLinking_refresh(bpy.types.Operator):
    bl_label  =""
    bl_idname = "renderman.lightlinking_refresh"
    bl_description = ""

    def invoke(self, context, event):
        scene = context.scene
        maintain_lists(scene)
        update_illuminate_list(context.object, scene)
        return{'FINISHED'}
        
class Renderman_OT_LinkLight(bpy.types.Operator):
    bl_label="Link Light"
    bl_idname="renderman.link_light"
    bl_description="Link Light to this Object"
    
    light = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        obj = context.object
        rm = obj.renderman[obj.renderman_index]
        if not self.light in rm.lightlist:
            rm.lightlist.add().name=self.light
        else:
            lightlist = rm.lightlist.keys()
            rm.lightlist.remove(lightlist.index(self.light))
        return {'FINISHED'}

class Renderman_OT_LightLinking_selected(bpy.types.Operator):
    bl_label = "Link Lights"
    bl_idname = "renderman.light_linking"
    bl_description = "Link Lights to Objects"
    
    type = Enum(items = (   ("add", "add Lights", "add selected lights"),
                            ("remove", "remove Lights", "remove selected lights"),
                            ("exclusive", "only selected", "exlusively use selected lights")),
                default = "add")
    
    def invoke(self, context, event):
        t = self.type
        selected_lights = []
        for l in context.scene.selected_objects:
            al = False
            if l.active_material:
                for rm in l.active_material.renderman:
                    if rm.arealight_shader != '':
                        al = True
            if (l.type == 'LAMP' or al):
                selected_lights.append(l.name)
                
        for obj in context.scene.objects:
            if obj.type == "LAMP":
                continue

            lightlist = obj.renderman[obj.renderman_index]
            for l in getLightList(context.scene):
                if l.name in selected_lights:
                    if t in ["add", "exclusive"]:
                        if not l.name in lightlist:
                            lightlist.add().name = l.name
                    elif t == "remove":
                        if l.name in lightlist:
                            lightlist.remove(lightlist.keys().index(l.name))
                else: ## this isn't slected
                    if t == "exclusive":
                        if l.name in lightlist:
                            lightlist.remove(lightlist.keys().index(l.name))
        return {'FINISHED'}

        
class Renderman_OT_addAttributeSelected(bpy.types.Operator):
    bl_label = "add Attribute"
    bl_idname = "attributes.add_new_selected"
    bl_description = "add Attribute to selected"
    bl_options = {'REGISTER'}
    
    grp = bpy.props.StringProperty(options = {'HIDDEN'})
    attr = bpy.props.StringProperty(options = {'HIDDEN'})
    
    def draw(self, context):
        from export_renderman.ui import parmlayout
        layout = self.layout
        grp = context.scene.renderman_settings.attribute_groups[self.grp]
        attr = grp.attributes[self.attr]
        layout.prop(grp, "export", text = 'Export Group "'+grp.name+'"')
        parmlayout(attr, attr, layout, context.scene)
        layout.prop(attr, "export", text = "Export")
        
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        grp = self.grp
        attr = self.attr
        for obj in context.scene.objects:
            path = 'bpy.context.scene.objects["'+obj.name+'"].renderman'
            path += '['+path+'_index]'
            if obj.select:
                bpy.ops.attributes.add_new(grp = grp, attr = attr, path=path)
                
        return {'FINISHED'}
    

class Renderman_OT_changeLinking(bpy.types.Operator):
    bl_label = ""
    bl_idname = "renderman.change_pass_linking"
    bl_description = "change Pass linking"
    
    path = String()
    type = Enum(items = (   ("all", "All", "all"),
                            ("none", "None", "none"),
                            ("active", "Active", "active"),
                            ("invert", "Invert", "invertcd my")),
                default = "all")
                
    def  invoke(self, context, event):
        path = eval(self.path)
        type = self.type
        curr_pass = path[eval(self.path+'_index')]
        rm = context.scene.renderman_settings
    
        if type == "all":
            for l in curr_pass.links:
                curr_pass.links.remove(0)
            for global_pass in rm.passes:
                bpy.ops.renderman.link_pass(path = self.path, rpass = global_pass.name)
            
        elif type == "none":
            for l in curr_pass.links:
                curr_pass.links.remove(0)
            
        elif type == "active":
            bpy.ops.renderman.link_pass(path = self.path, rpass = rm.passes[rm.passes_index].name)
        
        elif type == "invert":
            for global_pass in rm.passes:
                bpy.ops.renderman.link_pass(path = self.path, rpass = global_pass.name)
        return {'FINISHED'}
            
        
class Renderman_OT_link_pass(bpy.types.Operator):
    bl_label = ""
    bl_idname = "renderman.link_pass"
    bl_description = "Link/Unlink Object Pass to this Render Pass"
    
    rpass = String()
    path = String()
    
    def execute(self, context):
        rm = context.scene.renderman_settings
        path = eval(self.path)
        rpass = self.rpass
        curr_pass = path[eval(self.path+'_index')]
        for opass in path:
            links = opass.links
            if rpass in links:
                for i, p in enumerate(links):
                    if p.name == rpass: links.remove(i)
            elif opass == curr_pass:
                links.add().name = rpass
        return{'FINISHED'}
        
class Renderman_OT_link_pass_selected(bpy.types.Operator):
    bl_label = ""
    bl_idname = "renderman.link_pass_selected"
    bl_description =""
    
    rpass = bpy.props.StringProperty()
    
    def execute(self, context):
        for obj in context.selected_objects:
            path = 'bpy.data.objects["'+obj.name+'"]'
            if obj.type == "LAMP":
                path += ".data.renderman"
            else:
                path += ".renderman"
            bpy.ops.renderman.link_pass(rpass=self.rpass, path=path)
        return{'FINISHED'}
        
class Renderman_OT_set_shadingrate_selected(bpy.types.Operator):
    bl_label="set Shading Rate"
    bl_idname="renderman.set_shading_rate_selected"
    bl_description="set ShadingRate for selected Objects"
    
    rate = bpy.props.FloatProperty(min=0, max=100, default=1)
    
    def draw(self, context):
        self.layout.prop(self, "rate")
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        for obj in context.scene.objects:
            if obj.select:
                if obj.type != "LAMP":
                    rm = obj.renderman[obj.renderman_index]
                    rm.shadingrate = self.rate
        return{'FINISHED'}
    
    
class Renderman_OT_addpass_selected(bpy.types.Operator):
    bl_label="add new Pass"
    bl_idname="renderman.add_pass_selected"
    bl_description="add new pass to selected objects"
    bl_options = {'REGISTER'}
    
    name = bpy.props.StringProperty(options={'HIDDEN'})
    defname = bpy.props.BoolProperty(name="Default Name", default=True)
    linking = bpy.props.EnumProperty(name="Linking", items=(("all", "All", ""),
                                                            ("none", "None", ""),
                                                            ("active", "Active", ""),
                                                            ("selected", "Selected", "")),
                                                    default="all")
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "defname")
        layout.prop(self, "name", text="Name")
        layout.prop(self, "linking")
        for rpass in context.scene.renderman_settings.passes:
            layout.prop(rpass, "linkToMe", text=rpass.name)
        
        
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "LAMP":
                rm = obj.data.renderman
            else:
                rm = obj.renderman

            if self.defname:
                name = "Default"
                defcount = 1
                defname = "Default01"
                for item in rm:
                    if item.name == defname:
                        defcount += 1
                        defname = name + "0"*(2 - len(str(defcount))) + str(defcount)
                rm.add().name = defname
                newpass = rm[defname]
            else:
                rm.add().name=self.name
                newpass = rm[self.name]

            if self.linking == "all":
                for rpass in context.scene.renderman_settings.passes:
                    newpass.links.add().name = rpass.name
            elif self.linking == "active":
                rpass = getactivepass(context.scene)
                if rpass != None:
                    rm.links.add().name = rpass.name
            elif self.linking == "selected":
                for rpass in context.scene.renderman_settings.passes:
                    if rpass.linkToMe:
                        rm.links.add().name = rpass.name

            if obj.type == "LAMP":
                obj.data.renderman_index = len(rm)-1
            else:
                obj.renderman_index = len(rm)-1
        return{'FINISHED'}


class Renderman_OT_addRendermanLight(bpy.types.Operator):
    bl_label =""
    bl_description = ""
    bl_idname="renderman.add_light"

    shader = bpy.props.StringProperty()

    def invoke(self, context, event):
        rpasses = context.scene.renderman_settings.passes
        ldata = bpy.data.lamps.new(name=self.shader, type="POINT")
        lamp = bpy.data.objects.new(name=self.shader, object_data=ldata)
        context.scene.objects.link(lamp)
        atleast_one_pass(ldata, rpasses)
        ldata.renderman[0].shaderpath = self.shader
        maintain_lamp_shaders(lamp, context.scene)
        maintain_light(lamp, context.scene)
        lamp.location = context.scene.cursor_location
        for obj in context.scene.objects: obj.select = False
        lamp.select = True
        context.scene.objects.active = lamp
        return{'FINISHED'}


class Renderman_OT_removepass_selected(bpy.types.Operator):
    bl_label="Remove Pass"
    bl_idname = "renderman.remove_pass_selected"
    bl_description ="remove pass from selected objects"
    
    name = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        for obj in context.scene.objects:
            if obj.type == "LAMP":
                rm = obj.data.renderman
            else:
                rm = obj.renderman
            index = -1
            for i, r in enumerate(rm):
                if r.name == self.name:
                    index = i
            if obj.select:
                rm.remove(i)
        return{'FINISHED'}
        
class Renderman_OT_set_active_pass_selected(bpy.types.Operator):
    bl_label="set active Pass"
    bl_idname ="renderman.set_active_pass_selected"
    bl_description="set active Pass for selected objects"
    
    name = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        for obj in context.scene.objects:
            if obj.select:
                index = -1
                if obj.type == "LAMP":
                    path = obj.data
                else:
                    path = obj
                    
                for i, r in enumerate(path.renderman):
                    if r.name == self.name:
                        index = i
                path.renderman_index = index
        return{'FINISHED'}
            
#############################################
#                                           #
#   Shader Paths Operator                   #
#                                           #
#############################################


class Renderman_OT_RefreshShaderList(bpy.types.Operator):
    bl_label = "Refresh Shader List"
    bl_idname = "renderman.refreshshaderlist"
    bl_description = "Refresh Shader List"

    def invoke(self, context, event):
        checkshadercollection(context.scene)
        initial_load_data(context.scene)
        return {'FINISHED'}


class Renderman_OT_Shaderpaths(bpy.types.Operator):
    bl_label = "Shader Paths"
    bl_idname = "renderman.pathaddrem"
    bl_description = "adds or removes Shader Path"

    add = bpy.props.BoolProperty(default = True)

    def invoke(self, context, event):
        scene = context.scene
        rm = context.scene.renderman_settings
        shaders = rm.shaders
        spaths = shaders.shaderpaths
        if self.add:
            if os.path.exists(rm.shaderpath):
                def addpath(path):
                    spaths.add().name = path
                    if rm.shaderpath_recursive:
                        for dir in os.listdir(path):
                            fullpath = os.path.join(path, dir)
                            if os.path.isdir(fullpath) and not fullpath in spaths:
                                addpath(fullpath)
                addpath(rm.shaderpath)
            
            checkshadercollection(context.scene)

        elif not self.add:
            index = shaders.shaderpathsindex
            shaders.shaderpaths.remove(index)

        return {'FINISHED'}


class Renderman_OT_CompileShader(bpy.types.Operator):
    bl_label = "Compile Shader"
    bl_idname = "text.compileshader"
    bl_description = "Compile Renderman Shader"
    COMPAT_ENGINES = {'RENDERMAN'}

    @classmethod
    def poll(cls, context):
        text = context.space_data.text
        return text

    def invoke(self, context, event):
        scene = context.scene
        shaders = scene.renderman_settings.shaders
        text = context.space_data.text
        sc = context.scene.renderman_settings.shaderexec
        if not text.filepath:
            bpy.ops.text.save_as()

        shader = os.path.split(text.filepath)
        if not shader[0] in shaders.shaderpaths:
            shaders.shaderpaths.add().name = shader[0]
        os.chdir(shader[0])
        os.system('"'+sc+'" "'+shader[1]+'"')
        checkshadercollection(scene)
        self.report('DEBUG', 'test')

        return {'FINISHED'}
        
#############################################
#                                           #
#   Hider List Operator                     #
#                                           #
#############################################

class Renderman_OT_addremhider(bpy.types.Operator):
    bl_label="add or remove hider"
    bl_idname="renderman.addremhider"
    bl_description = "add or remove Hider"
    
    add = bpy.props.BoolProperty(default = True)
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        add = self.add
        if add:
            rmansettings.hider_list.add()
        else:
            index = rmansettings.hider_list_index
            rmansettings.hider_list.remove(index)
            
        return {'FINISHED'}  
    
class Renderman_OT_addhideroption(bpy.types.Operator):
    bl_label = "add hider option"
    bl_idname="renderman.addhideroption"
    bl_description = "add hider specific option"
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        hider = rmansettings.hider_list[rmansettings.hider_list_index]
        hider.options.add()
        
        return {'FINISHED'}
    
class Renderman_OT_remhideroption(bpy.types.Operator):
    bl_label = "remove hider option"
    bl_idname = "renderman.remhideroption"
    bl_description = "remove hider specific option"
    
    index = bpy.props.IntProperty(min = 0, max=10000, default=0)
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        index = self.index
        hider = rmansettings.hider_list[rmansettings.hider_list_index]
        hider.options.remove(index)
        
        return {'FINISHED'}                           


class Renderman_OT_hider_set_default_values(bpy.types.Operator):
    bl_label = "set default"
    bl_idname = "hider.set_default_values"
    bl_description = "set current values as default for current hider"
    
    hider = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        hider = self.hider        
        master_hider = rmansettings.hider_list[hider]
        slave_hider = getactivepass(context.scene).hider_list[hider]
    
        for master_option in master_hider.options:
            slave_option = slave_hider.options[master_option.name]
            copy_parameter(master_option, slave_option)
            
        return {'FINISHED'}
    
    
class Renderman_OT_hider_get_default_values(bpy.types.Operator):
    bl_label = "get default"
    bl_idname = "hider.get_default_values"
    bl_description = "get default values for current hider"
    
    hider = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        hider = self.hider        
        master_hider = rmansettings.hider_list[hider]
        slave_hider = getactivepass(context.scene).hider_list[hider]
    
        for master_option in master_hider.options:
            slave_option = slave_hider.options[master_option.name]
            copy_parameter(slave_option, master_option)
            
        return {'FINISHED'}    
    
    
class Renderman_OT_hider_option_set_default(bpy.types.Operator):
    bl_label = "set default"
    bl_idname = "hider_option.set_default"
    bl_description = "set current value as default"
    
    grp = bpy.props.StringProperty()
    attr =  bpy.props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        hider = self.grp
        option = self.attr
        master_option = rmansettings.hider_list[hider].options[option]
        slave_option = getactivepass(context.scene).hider_list[hider].options[option]
    
        copy_parameter(master_option, slave_option)
            
        return {'FINISHED'} 
    
    
class Renderman_OT_hider_option_get_default(bpy.types.Operator):
    bl_label = "get default"
    bl_idname = "hider_option.get_default"
    bl_description = "get default value"
    
    grp = bpy.props.StringProperty()
    attr = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        hider = self.grp
        option = self.attr
        master_option = rmansettings.hider_list[hider].options[option]
        slave_option = getactivepass(context.scene).hider_list[hider].options[option]
    
        copy_parameter(slave_option, master_option)
            
        return {'FINISHED'}   
    
    
class Renderman_OT_hider_set_default(bpy.types.Operator):
    bl_label="set default"
    bl_idname="hider.set_default"    
    bl_description="set this hider as default for new passes"

    hider = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        scene = context.scene
        rmansettings = context.scene.renderman_settings
        hider = self.hider
        rmansettings.default_hider = hider
        return {'FINISHED'}     


#############################################
#                                           #
#   Custom RIB Code Operators               #
#                                           #
#############################################
        
class Renderman_OT_addCustomRIBCode(bpy.types.Operator):
    bl_label = "World RIB Code"
    bl_idname = "renderman.custom_code"
    bl_description = "add or remove custom rib code"
    
    type = bpy.props.EnumProperty(items = ( ("scene", "Scene", ""),
                                            ("world", "World", ""),
                                            ("object", "Object", ""),
                                            ("particles", "Particles", "")))
            
    add = bpy.props.BoolProperty(default = True)
    
    def invoke(self, context, event):
        scene = context.scene
        active_pass = getactivepass(scene)
        if self.type == "scene":
            code = active_pass.scene_code
            i = active_pass.scene_code_index
        elif self.type == "world":
            code = active_pass.world_code
            i = active_pass.world_code_index
        elif self.type == "object":
            obj = context.object
            rm = obj.renderman[obj.renderman_index]
            code = rm.custom_code
            i = rm.custom_code_index
        elif self.type == "particles":
            ps = context.particle_system.settings
            rm = ps.renderman[ps.renderman_index]
            code = rm.custom_code
            i = rm.custom_code_index
        add = self.add
        if add:
            code.add()
        else:
            code.remove(i)        
        return {'FINISHED'}  


class Renderman_OT_AddParticleAttribute(bpy.types.Operator):
    bl_label="Add Attribute"
    bl_idname="renderman.add_particle_var"
    bl_description="Add a new Particle Variable"

    def invoke(self, context, event):
        ps = context.particle_system
        rm = ps.settings.renderman[ps.settings.renderman_index]

        rm.export_vars.add()
        return {'FINISHED'}
         
class Renderman_OT_RemoveParticleAttribute(bpy.types.Operator):
    bl_label=""
    bl_idname="renderman.remove_particle_var"
    bl_description="Remove Particle Variable"

    index = bpy.props.IntProperty(min=0, max=100, default=0)

    def invoke(self, context, event):
        ps = context.particle_system
        rm = ps.settings.renderman[ps.settings.renderman_index]

        rm.export_vars.remove(self.index)
        return {'FINISHED'}
