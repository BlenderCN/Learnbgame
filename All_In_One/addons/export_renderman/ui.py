
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

import export_renderman
import export_renderman.rm_maintain
from export_renderman.rm_maintain import *
import bpy
import os

##################################################################################################################################
#########################################################################################################
#                                                                                                       #
#       U I   L A Y O U T                                                                               #
#                                                                                                       #
#########################################################################################################

#########################################################################################################
#                                                                                                       #
#       layout functions                                                                                #
#                                                                                                       #
#########################################################################################################

class DisplayDriverSelector(bpy.types.Operator):
    bl_label = ""
    bl_idname = "renderman.displaydriver_select"
    bl_description  = ""

    display = bpy.props.StringProperty()
    driver = bpy.props.StringProperty()

    def invoke(self, context, event):
        rpass = getactivepass(context.scene)
        rm = context.scene.renderman_settings
        rpass.displaydrivers[self.display].displaydriver = self.driver
        maintain_display_options(rpass, rm)
        maintain_display_drivers(rpass, context.scene)
        return{'FINISHED'}

class DisplayDriverSelectorMenu(bpy.types.Operator):
    bl_label = ""
    bl_idname = "renderman.displaydriver_menu"
    bl_description = ""

    display = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        rm = scene.renderman_settings
        rpass = getactivepass(scene)
        maintain_display_drivers(rpass, scene)
        check_displaydrivers(scene) 
        check_display_variables(scene)

        wm = context.window_manager
        return wm.invoke_popup(self, width=(1 + (len(rm.displays)/20))*150)

    def draw(self, context):
        scene = context.scene
        rm = scene.renderman_settings

        displaydrivers = rm.displays.keys()
        displaydrivers.sort()
        layout = self.layout
        row = layout.row()

        i = 0
        col = row.column(align=True)
        for drv in displaydrivers:
            op = col.operator("renderman.displaydriver_select", text=drv)
            op.driver = drv
            op.display = self.display
            i += 1
            if i == 5:
                col = row.column(align=True)
                i = 0

class ShaderSelector():
    '''Class to create shader select Menus'''

    shader_collection = None
    type_ = ""
    menuname = ""
    idname = ""
    clear_idname =""

    def createOperator(self):
        def invoke_op1(self, context):
            scene = context.scene
            pathcoll = scene.renderman_settings.shaders
            if pathcoll.shaderpaths and not pathcoll.shadercollection:
                checkshadercollection(scene)
                initial_load_data(scene)
            wm = context.window_manager
            return wm.invoke_popup(self, width=(1 + (len(self.shader_collection)/20))*150)

        def draw_op1(self, context):
            layout = self.layout
            row = layout.row()
            scollection = self.shader_collection.keys()
            scollection.sort()
            i = 0
            col = row.column(align=True)
            col.operator(self.clear_idname)
            for sh in scollection:
                col.operator(self.opname, text=sh, icon="LAMP" if self.type_ == "light" else "MATERIAL").shader = sh
                i += 1
                if i == 20:
                    col = row.column(align=True)
                    i = 0

        def set_shader(context, shader):
            if self.type_ == "light":
                path = context.object.data
                rm = path.renderman[path.renderman_index]
                rm.shaderpath = shader
                maintain_lamp_shaders(context.object, context.scene)
                maintain_light(context.object, context.scene)
                
            elif self.type_.find("obj") != -1:
                path = context.material
                rm = path.renderman[path.renderman_index]

                if self.type_ == "objsurf":
                    rm.surface_shader = shader
                elif self.type_ == "objdisp":
                    print("ho")
                    rm.displacement_shader = shader
                elif self.type_ == "objint":
                    rm.interior_shader = shader
                elif self.type_ == "objext":
                    rm.exterior_shader = shader
                elif self.type_ == "objint":
                    rm.interior_shader = shader
                elif self.type_ == "objal":
                    rm.arealight_shader = shader
                
                maintain_material_shaders(context.material, context.scene)

            else:
                path = getactivepass(context.scene)
                if self.type_ == "wimg":
                    path.imager_shader = shader
                elif self.type_ == "wsurf":
                    path.global_shader.surface_shader = shader
                elif self.type_ == "wvol":
                    path.global_shader.atmosphere_shader = shader

                maintain_world_shaders(path, context.scene)
                
        def invoke_op2(self, context, event):
            set_shader(context, self.shader)
            return{'FINISHED'}

        def clear_shader_op(self, context, event):
            set_shader(context, "")
            return{'FINISHED'}

        name = "Renderman_OT_"+self.type_+"_Clear_Shader"
        self.clear_idname = "renderman.clear_"+self.type_+"_shader"
        cls = type(bpy.types.Operator)(name, (bpy.types.Operator,), {"bl_label" : "No Shader",
                                                                        "bl_idname" : self.clear_idname,
                                                                        "type_" : self.type_,
                                                                        "invoke" : clear_shader_op})
        bpy.utils.register_class(cls)
            
        name = "Renderman_OT_"+self.type_+"_Change_Shader"
        self.idname = "renderman.change_"+self.type_+"_shader"
        cls = type(bpy.types.Operator)(name, (bpy.types.Operator,), {"bl_label" : "",
                                                                "bl_idname" : self.idname,
                                                                "type_" : self.type_,
                                                                "shader" : bpy.props.StringProperty(),
                                                                "invoke" : invoke_op2})
        bpy.utils.register_class(cls)

        name = "Renderman_OT_"+self.type_+"_Shader_Menu"
        self.menuname = "renderman."+self.type_+"_shader_menu"
        cls = type(bpy.types.Operator)(name, (bpy.types.Operator,), {"bl_label" : "",
                                                                "bl_idname" : self.menuname,
                                                                #"bl_options" : {'REGISTER'},
                                                                "opname" : self.idname,
                                                                "clear_idname" : self.clear_idname,
                                                                "type_" : self.type_,
                                                                #"shader" : bpy.props.StringProperty(),
                                                                #"shader_filter" : bpy.props.StringProperty(),
                                                                "shader_collection" : self.shader_collection,
                                                                "draw" : draw_op1,
                                                                "execute" : invoke_op1})
        bpy.utils.register_class(cls)

    def insert_into_layout(self, context, layout, shader):
        layout.operator(self.menuname, text=shader if shader != "" else "select shader")

    def __init__(self, shader_collection, type_):
        self.shader_collection = shader_collection
        self.type_ = type_
        self.createOperator()
        

def parmlayout(parm, master_parm, layout, scene, type_=""):
    rm = scene.renderman_settings
    float_size = {  1 : "float_one",
                    2 : "float_two",
                    3 : "float_three"}
                        
    int_size = {    1 : "int_one",
                    2 : "int_two",
                    3 : "int_three"}
                                                                                                
    if master_parm.parametertype == 'string':
        row = layout.row(align=True)
        
        if master_parm.input_type == "texture":
            row.prop_search(parm, "textparameter", bpy.data, "textures", text="")
        elif master_parm.input_type == "display":
            if type_ == "rpass":
                path = getactivepass(scene)
            else:
                path = rm
            row.prop_search(parm, "textparameter", path, "output_images")
        else:
            row.prop(parm, "textparameter", text="")
    if master_parm.parametertype == 'float':
        layout.prop(parm, float_size[master_parm.vector_size])
    if master_parm.parametertype == 'int':
        layout.prop(parm, int_size[master_parm.vector_size])        
    if master_parm.parametertype == 'color':
        layout.prop(parm, "colorparameter", text="") 

def matparm_menu(parm, mname, list_path, client):
    def draw_menu(self, context):
        layout = self.layout
        load_pass_presets(context.scene)
        if client != "":
            layout.label("Request Pass")
            passes_preset_layout(layout, context.scene, client=client, parm_path=list_path)
        else:
            layout.label("Request Pass")
            passes_preset_layout(layout, context.scene, client=client, parm_path=list_path)
        
    cls = type(bpy.types.Menu)(mname, (bpy.types.Menu,), {  "bl_label" : "",
                                                            "mclient" : client,
                                                            "draw" : draw_menu})
    bpy.utils.register_class(cls)


def matparmlayout(context, parmlist, layout, material, rm, shid, client=""):
    if parmlist:
        for active_parameter in parmlist:
            if active_parameter.name in ['from', 'to']: 
                continue
            parmlist_string = repr(parmlist)
            parmlist_string_array = parmlist_string.split(".")
            list_path = parmlist_string_array[len(parmlist_string_array)-1]            
            parm_path = list_path + '["'+active_parameter.name+'"]'
            row = layout.row(align=True)
            
            if active_parameter.parametertype == 'string':
                split1 = row.split(percentage = 0.8)
                
                if active_parameter.input_type == "texture":
                    if material == bpy.data:
                        split1.prop_search(active_parameter, "textparameter", material, "textures", text=active_parameter.name)
                    else:
                        split1.prop_search(active_parameter, "textparameter", material, "texture_slots", text=active_parameter.name)
                        
                elif active_parameter.input_type == "display":
                    split1.prop_search(active_parameter, "textparameter", rm, "output_images", text = active_parameter.name)
                    
                else:
                    split1.prop(active_parameter, "textparameter", text=active_parameter.name)
                    
                mname = active_parameter.name+shid
                if (not mname in dir(bpy.types)
                    or getattr(bpy.types, mname).mclient != client):
                    matparm_menu(active_parameter, mname, parm_path, client)
                request = -1
                if client != "":
                    cl = context.scene.objects[client]
                    for i, r in enumerate(cl.requests):
                        if eval("cl."+r.name) == active_parameter: ##This parm requests a render pass
                            request = i
                if request != -1:
                    op = split1.operator("renderman.deleterequest", text = "", icon='X')
                    op.client = client
                    op.r = request
                else:
                    split2 = split1.split(percentage=0.5)
                    split2.menu(mname, icon="TRIA_DOWN", text= "")
                    split2.prop(active_parameter, "input_type", text = "")

                
                
            if active_parameter.parametertype == 'float':
                if active_parameter.vector_size == 1:
                    row.prop(active_parameter, "float_one", text=active_parameter.name)
                elif active_parameter.vector_size == 3:
                    row.prop(active_parameter, "float_three", text=active_parameter.name)
                    
                    
            if active_parameter.parametertype == 'color':
                row.prop(active_parameter, "colorparameter", text=active_parameter.name)             
    
def checkderived(active_parameter, layout, settings):
    for setting in settings:
        if active_parameter.name == setting:
            layout.prop(active_parameter, "free")
                
grp_menus = {}
attr_menus = {}
def attribute_panel_layout(name, str_path, layout, scene):
    global grp_menus, attr_menus
    active_pass = getactivepass(scene)
    try:
        path = eval(str_path)
        rm = scene.renderman_settings
        row = layout.row(align=True)
        row.operator("attributes.set_as_default", text="set as default", icon="FILE_TICK").path = str_path
        row.operator("attributes.get_default", text="get default", icon="ANIM").path = str_path
        op = row.operator("attributes.remove", text="Remove All")
        op.type = "all"
        op.path = str_path
        attribute_menu(name, str_path)
        row.menu(name+"_attribute_menu", icon="ZOOMIN", text="")
        for group in path.attribute_groups:
            box = layout.box()
            row = box.row(align=True)
            row.prop(group, "expand", text="", icon="TRIA_DOWN" if group.expand else "TRIA_RIGHT", emboss=False)
            row.label(text=group.name)
            box.active = group.export
            #if not group.name in grp_menus:
            mname = attribute_options(name, str_path, "", group.name)
            grp_menus[group.name] = mname
            #else:
            #    mname = grp_menus[group.name]
            row.menu(mname, icon="DOWNARROW_HLT")
            
            if group.expand:
                for attribute in group.attributes:
                    master_attribute = scene.renderman_settings.attribute_groups[group.name].attributes[attribute.name]
                    row = box.row(align=True)
                    row.active = attribute.export
                    row.label(text=master_attribute.name)
                    parmlayout(attribute, master_attribute, row, scene)
                    if not attribute.name in attr_menus:
                        mname = attribute_options(name, str_path, attribute.name, group.name)
                        attr_menus[attribute.name] = mname
                    else:
                        mname = attr_menus[attribute.name]
                    row.menu(mname, icon="DOWNARROW_HLT")
    except IndexError:
        layout.label("No Pass")

mcount = {}
mcount_refresh = 10
def attribute_options(name, str_path, attr, grp):
    path = eval(str_path)
    if attr == "": is_grp = True 
    else: is_grp = False
    if name.find("Hider") != -1:
        hider = True
        t = "opt"
    elif name.find("Options") != -1:
        hider = False
        t = "opt"
    else:
        hider = False
        t = "attr"
    if hider:
        grps = path.hider_list
    else:
        if t == "attr":
            grps = path.attribute_groups
        else:
            grps = path.option_groups
            
    if is_grp: ex_path = grps[grp]
    else:
        if t == "opt":
            ex_path = grps[grp].options[attr]
        else:
            ex_path = grps[grp].attributes[attr]
    
    ## add/remove/defaults for attributes
    def draw_attr_options(self, context):
        layout = self.layout
        
        if not hider:
            op = layout.operator("attributes.remove", text = "Remove")
            if is_grp:
                op.type = t+"grp"
            else:
                op.type = t
            op.path = str_path
            op.attr = attr
            op.grp = grp
        
        layout.prop(ex_path, "export", text = "export")
        
        if is_grp:
            if t == "opt":
                opname = "option_group.get_default"
            else:
                opname = "attribute_group.get_default"
        else:
            if t == "opt":
                if hider:
                    opname = "hider_option.get_default"
                else:
                    opname = "option.get_default"
            else:
                opname = "attribute.get_default"
            
        op = layout.operator(opname, text="get default")
        op.grp = grp
        if not is_grp:
            op.attr = ex_path.name
        if t != "opt":
            op.path = str_path

        if is_grp:
            if t == "opt":
                opname = "option_group.set_default"
            else:
                opname = "attribute_group.set_default"
        else:
            if t == "opt":
                if hider:
                    opname = "hider_option.set_default"
                else:
                    opname = "option.set_default"
            else:
                opname = "attribute.set_default"
                    
        op = layout.operator(opname, text="set default")
        op.grp = grp
        if not is_grp:
            op.attr = ex_path.name
        if t != "opt":
            op.path = str_path
   
    if is_grp:
        mname = name+'_'+grp
    else:
        if hider:
            mname = name+"_"+ex_path.name+"hopt"
        else:
            if t == "opt":
                mname = name+"_"+ex_path.name+"opt"
            else:
                mname = name+"_"+ex_path.name+"aopt"
    global mcount, mcount_refresh
    if not mname in mcount: mcount[mname] = 0
    mcount[mname] +=1
    dbprint(mname, mcount[mname], lvl=2, grp="attrui")
    if not mname in dir(bpy.types) or mcount[mname] >= mcount_refresh:
        mcount[mname] = 0
        dbprint("recreating menu", mname, lvl=2, grp="attrui")
        cls = type(bpy.types.Menu)(mname, (bpy.types.Menu,), {"bl_label" : "",
                                                        "draw" : draw_attr_options})
        bpy.utils.register_class(cls)
    return mname


def passes_linking_layout(name, str_path, layout, scene):
    path = eval(str_path)
    row = layout.row()
    col = row.column(align=True)
    renderman_settings = scene.renderman_settings

    if len(path.renderman) < 15:
        rows = len(path.renderman)+1
    else:
        rows = 15
    
    passes_str_path = str_path+'.renderman'
    col.template_list(path, "renderman", path, "renderman_index", rows=rows)
    col = row.column(align = True)
    col.operator("renderman.addpass", icon="ZOOMIN", text="").path = passes_str_path
    col.operator("renderman.rempass", icon="ZOOMOUT", text ="").path = passes_str_path
    ri = path.renderman_index
    if ri < len(path.renderman) and ri >= 0:
        curr_pass = path.renderman[path.renderman_index]
        layout.prop(curr_pass, "name")
    
        col = layout.column(align=True)
        box = col.box()
        row = box.row(align=True)
        row.label("Link to Pass:")
            
        op = row.operator("renderman.change_pass_linking", text="All")
        op.path = passes_str_path
        op.type = "all"
        op = row.operator("renderman.change_pass_linking", text="None")
        op.path = passes_str_path
        op.type = "none"
        op = row.operator("renderman.change_pass_linking", text="Invert")
        op.path = passes_str_path
        op.type = "invert"
        op = row.operator("renderman.change_pass_linking", text="Active")
        op.path = passes_str_path
        op.type = "active"
                                            
        box = col.box()
        for rpass in renderman_settings.passes:
            row = box.row()
            row.label(rpass.name)
            ap = getactivepass(scene)
            row.label(text = "", icon = "RESTRICT_VIEW_OFF" if ap.name == rpass.name else "RESTRICT_VIEW_ON")
            op_col = row.column()
            op = op_col.operator("renderman.link_pass", icon="LINKED" if rpass.name in curr_pass.links else "BLANK1")
            op.rpass = rpass.name
            op.path = passes_str_path

                                                        
def attribute_menu(name, path="", selected=False): ### create the attribute Menus
    mtype = bpy.types.Menu
    if name.find("Options") != -1:
        t = "option"
    else:
        t = "attribute"

    ## presets
    def draw_menu(self, context):
        rmansettings = context.scene.renderman_settings
        target_path = os.path.join(bpy.utils.preset_paths("renderman")[0], rmansettings.active_engine)
        for preset in os.listdir(target_path):
            if preset.find(".preset") != -1:
                p = preset.replace(".preset", "")
                if selected:
                    self.layout.operator("attributes.load_selected", text=p.replace("_", " ")).preset = p
                else:
                    op = self.layout.operator("attribute.load", text=p.replace("_", " "))
                    op.preset = p
                    op.path = path

    ## root menu
    def draw_root_menu(self, context):
        obj = ""
        part = ""
        if name.find("object") != -1:
            obj = context.object.name
        elif name.find("particles") != -1:
            obj = context.object.name
            part = context.particle_system.name
        layout = self.layout
        layout.menu("attribute_"+name)
        layout.menu(name+"_attributepresets", text="Presets")
        if path != "":
            op = layout.operator("attribute.add_preset", text="save preset")
            op.obj = obj
            op.part = part
        if selected:
            layout.operator("attributes.remove_all_selected")

    ## add Attribute:
    ## Groups   
    def draw_groups(self, context):        
        layout = self.layout
        rman = context.scene.renderman_settings
        if name.find("Options") != -1:
            groups = rman.option_groups
        else:
            groups = rman.attribute_groups
        for grp in groups:
            mname = grp.name+"add"+t
            if not mname in dir(bpy.types):
                cls = type(mtype)(mname, (mtype,), {  "bl_label" : grp.name, 
                                                "grp_name" : grp.name, 
                                                "draw" : draw_attributes,
                                                "path" : path})
                bpy.utils.register_class(cls)
            layout.menu(mname)
                                                                
    ## Attributes 
    def draw_attributes(self, context):
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


    ##create menus
    ##attribute groups
    mname = t+"_"+name     

    if not mname in dir(bpy.types):
        cls = type(mtype)(mname, (mtype,), {  "bl_label" : "New Attribute",
                                        "draw" : draw_groups})

        bpy.utils.register_class(cls)
    if name.find("Options") == -1:
        ##root menu
        mname = name+"_attribute_menu"
        if not mname in dir(bpy.types):
            cls = type(mtype)(mname, (mtype,), {  "bl_label" : "",
                                                "draw" : draw_root_menu})
            bpy.utils.register_class(cls)
    
        ## presets                                       
        mname = name+"_attributepresets"
        if not mname in dir(bpy.types):
            cls = type(mtype)(mname, (mtype,), {  "bl_label" : "Presets",
                                            "draw" : draw_menu})
            bpy.utils.register_class(cls)
        

def dimensions_layout(layout, obj, env=False):
    rc = obj.renderman_camera
    col = layout.column(align = True)
    row = col.row(align = True)
    row = col.row(align=True)
    if obj.type == "CAMERA":
        row.prop(rc, "depthoffield")
        row = col.row(align=True)
        row.enabled = rc.depthoffield
        row.prop(rc, "dof_distance")
        row.prop(rc, "fstop")
        row = col.row()
        row.enabled = rc.depthoffield
        row.prop(rc, "use_lens_length")
        row = col.row()
        row.enabled = rc.depthoffield and not rc.use_lens_length
        row.prop(rc, "focal_length")
        row = col.row(align=True)
        row.prop(obj.data, "clip_start")
        row.prop(obj.data, "clip_end")
        row = col.row(align=True)
        row.prop(obj.data, "shift_x")
        row.prop(obj.data, "shift_y")
    elif obj.type not in ['CAMERA', 'LAMP']:
        row.prop(rc, "res")
        row = col.row(align=True)
        row.prop(rc, "near_clipping", text="Near")
        row.prop(rc, "far_clipping", text="Far")
        row=col.row(align=True)
        row.prop(rc, "fov")
    else:
        row.prop(rc, "res")
        row = col.row(align=True)
        if obj.data.shadow_method == "BUFFER_SHADOW":
            row = col.row(align=True)
            row.prop(obj.data, "shadow_buffer_clip_start", text="clip start")
            row.prop(obj.data, "shadow_buffer_clip_end", text="clip end")


def passes_preset_sub_menu(mname, prdir, client="", parm_path=""):
    def draw_menu(self, context):
        layout = self.layout
        scene = context.scene
        passes_preset_layout(layout, scene, preset_dir=prdir, parm_path=parm_path, client=client)

    if (not mname in dir(bpy.types)
        or getattr(bpy.types, mname).mclient != client):
        cls = type(bpy.types.Menu)(mname, (bpy.types.Menu,), { "bl_label" : os.path.split(prdir)[1],
                                                        "mclient" : client,
                                                         "draw" : draw_menu })
        bpy.utils.register_class(cls)

def pass_preset_output_menu(mname, pr, parm_path, client):
    def draw_menu(self, context):
        global pass_preset_outputs
        layout = self.layout
        scene = context.scene
        outputs = pass_preset_outputs[pr]

        for o in outputs:
            op = layout.operator("renderman.requestpresetpass", text=o)
            op.preset = pr
            op.client = client
            op.client_path = parm_path
            op.output = o

    if (not mname in dir(bpy.types)
        or getattr(bpy.types, mname).mclient != client):
        cls = type(bpy.types.Menu)(mname, (bpy.types.Menu,),{"bl_label" : pr,
                                                       "mclient" : client,
                                                      "draw" : draw_menu})
        bpy.utils.register_class(cls)
        
        
def passes_preset_layout(layout, scene, preset_dir="", client="", parm_path=""):
    global pass_preset_outputs
    
    if parm_path != "":
            s = parm_path.split(".")
            s = s[len(s)-1]
            s = s.replace("[", "")
            s = s.replace("]", "")
            s = s.replace('"', "")
    
    active_engine = scene.renderman_settings.active_engine
    main_preset_path = bpy.utils.preset_paths('renderman')[0]
    preset_base_dir = os.path.join(main_preset_path, active_engine)
    
    if preset_dir == "": preset_dir = preset_base_dir
        
    for dir in os.listdir(preset_dir):
        fullpath = os.path.join(preset_dir, dir)
        path_string = fullpath.replace(preset_base_dir, "")
        path_string = path_string.replace("\\", "_")
        path_string = path_string.replace("/", "_")
        if os.path.isdir(fullpath):
            mname = "MT_prm_"+path_string
            if parm_path != "":
                mname += s
            passes_preset_sub_menu(mname, fullpath, parm_path = parm_path, client=client)
            layout.menu(mname)
        else:
            file = dir
            if checkextension(file) == 'pass':
                path_string = path_string.replace("_", "/")
                preset = path_string.replace(".pass", "")
                if parm_path != "" and len(pass_preset_outputs[preset]) > 1:
                    mname = "MT_pp_"+preset+"_outputs"+s
                    pass_preset_output_menu(mname, preset, parm_path, client)
                    layout.menu(mname)
                else:
                    if parm_path == "":
                        op = layout.operator("renderman.addpresetpass", text=preset)
                    else:
                        op = layout.operator("renderman.requestpresetpass", text=preset)
                        op.client = client
                        op.client_path = parm_path
                        op.output = pass_preset_outputs[preset][0]
                    op.preset = preset
                
def custom_code_layout(type_, context, layout):
        scene = context.scene
        rm = scene.renderman_settings
        active_pass = getactivepass(scene)
        if type_ == "world":
            path = active_pass
            prop = "world_code"
        elif type_ == "scene":
            path = active_pass
            prop = "scene_code"
        elif type_ == "object":
            try:
                path = context.object.renderman[context.object.renderman_index]
            except IndexError:
                path = None
                layout.label("No Pass")
                return
            prop = "custom_code"
        elif type_ == "particles":
            ps = context.particle_system.settings
            try:
                path = ps.renderman[ps.renderman_index]
            except IndexError:
                path = None
                layout.label("No Pass")
                return
            prop = "custom_code"
        code = eval("path."+prop)
        if active_pass:
            if type_ in ["world", "scene"] and active_pass.environment:
                env = True
            else:
                env = False
            row = layout.row()
            code_length = len(code)
            rows = code_length if code_length < 10 else 10        
            row.template_list(path, prop, path, prop+'_index', rows=rows)
            col = row.column(align=True)
            op = col.operator("renderman.custom_code", text="", icon="ZOOMIN")
            op.add = True
            op.type = type_
            op = col.operator("renderman.custom_code", text="", icon="ZOOMOUT")
            op.add = False
            op.type = type_
            if code:
                row = layout.row(align = True)      
                line = eval("path."+prop)[eval("path."+prop+'_index')]
                row.prop(line, "name", text = "")
                parm = line.parameter
                if type_ == "world":
                    row.prop(line, "world_position", text = "")
                elif type_=="particles":
                    row.prop(line, "particle_position", text="")
                else:
                    row.prop(line, "position", text = "")
                row = layout.row(align = True)
                if parm.parametertype == "float" or parm.parametertype == "int":
                    row.prop(parm, "vector_size", text="")
                row = layout.row()
                row.prop(parm, "parametertype", text="type")
                if parm.parametertype == 'string':
                    row = layout.row()
                    row.prop(parm, "input_type", text="input")
                parmlayout(parm, parm, layout, scene, type_="rpass")
                if env:
                    row = layout.row()
                    row.prop(line, "foreach")
                    if parm.input_type == "display":
                        row = layout.row()
                        row.prop(line, "all_dirs")
                        row = layout.row()
                        row.prop(line, "makecubefaceenv")
                if parm.input_type == "display" and type_ == "world":
                    row = layout.row()
                    row.prop(line, "makeshadow")
                if line.makeshadow or line.makecubefaceenv:
                    row = layout.row()
                    col = row.column()
                    col.prop(line, "default_output")
                    if line.default_output:
                        col.label(line.output)
                    else:
                        col.prop(line, "output")
                    col.label("Filter:")
                    col.prop(line, "filter", text="")
                    if line.filter == "other":
                        col.prop(line, "custom_filter", text="")
                    col.prop(line, "width")
                    col.prop(line, "stwidth")
                    scol = col.column(align=True)
                    scol.enabled = line.stwidth
                    scol.prop(line, "swidth")
                    scol.prop(line, "twidth")
                    
                    if line.makecubefaceenv:
                        col.prop(line, "fov")
        else:
            layout.label("No Render Pass")

def image_processing_layout(pr, lay):
    lay.prop(pr, "process")
    row = lay.row()
    col = row.column()
    col.enabled = pr.process
    col.prop(pr, "default_output")
    if pr.default_output:
        col.label(pr.output)
    else:
        col.prop(pr, "output")
    col.label("Filter:")
    col.prop(pr, "filter", text="")
    if pr.filter == "other":
        col.prop(pr, "custom_filter", text="")
    col.prop(pr, "width")
    col.prop(pr, "stwidth")
    scol = col.column(align=True)
    scol.enabled = pr.stwidth
    scol.prop(pr, "swidth")
    scol.prop(pr, "twidth")
    
    col.prop(pr, "envcube")
    if pr.envcube:
        col.prop(pr, "fov")
    col.prop(pr, "shadow")
    col.prop(pr, "custom_parameter", text="Custom")

#########################################################################################################
#                                                                                                       #
#      World Panels                                                                                     #
#                                                                                                       #
#########################################################################################################

class WorldButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.world) and (not rd.use_game_engine) and (rd.engine in cls.COMPAT_ENGINES)

class World_PT_RendermanPassesPanel(WorldButtonsPanel, bpy.types.Panel):
    bl_label="Passes"    
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        renderman_settings = scene.renderman_settings
        layout = self.layout
        row = layout.row()
        col = row.column(align=True)
        try:
            active_pass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
            return

        if len(renderman_settings.passes) < 15:
            rows = len(renderman_settings.passes)+1
        else:
            rows = 15
    
        col.template_list(renderman_settings, "passes", renderman_settings, "passes_index", rows=rows)

class Renderman_PT_WorldPanel(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "General World Settings"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        try:
            active_pass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
            return
        row = layout.row()
        col = row.column()
        col.prop(active_pass, "exportobjects", text="Export All Objects")
        col = row.column(align=True)
        col.enabled = not active_pass.exportobjects
        col.prop_search(active_pass, "objectgroup", bpy.data, "groups", text="")
        row = layout.row()
        row.prop(active_pass, "exportlights", text="Export All Lights")
        col  = row.column()
        col.enabled = not active_pass.exportlights
        col.prop_search(active_pass, "lightgroup", bpy.data, "groups", text="", icon="LAMP")   
            
class Renderman_PT_world_overrides(WorldButtonsPanel, bpy.types.Panel):
    bl_label="Overrides"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        layout = self.layout
        scene =context.scene
        try:
            apass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
            return
        layout.prop(apass, "override_shadingrate")
        row = layout.row()
        row.enabled = apass.override_shadingrate
        row.prop(apass, "shadingrate")

IMGSHADER = None
class Render_PT_ImagershaderPanel(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Imager Shader Parameters"

    COMPAT_ENGINES = {'RENDERMAN'}
    

    def draw(self, context):
        scene = context.scene
        renderman_settings = scene.renderman_settings
        if renderman_settings.passes:
            active_pass = getactivepass(scene)
            layout = self.layout
            row = layout.row(align=True)
            shaders = context.scene.renderman_settings.shaders

            global IMGSHADER
            if IMGSHADER == None:
                IMGSHADER = ShaderSelector(shaders.imager_collection, "wimg")
            IMGSHADER.insert_into_layout(context, row, active_pass.imager_shader)
            #row.prop_search(active_pass, "imager_shader", shaders, "imager_collection", icon='MATERIAL', text="")
            row.operator("renderman.refreshshaderlist", text="", icon='FILE_REFRESH')            
            

            layout.label(text=shader_info(active_pass.imager_shader,
                                          active_pass.imager_shader_parameter,
                                          scene))              

            matparmlayout(context,
                          active_pass.imager_shader_parameter,
                          layout,
                          bpy.data,
                          renderman_settings,
                          "wi"+active_pass.name)

WSURFSHADER = None
class World_PT_SurfaceShaderPanel(bpy.types.Panel, WorldButtonsPanel):
    bl_label = "Surface Shader"
    
    COMPAT_ENGINES = {'RENDERMAN'}

    def draw(self, context):
        scene = context.scene
        #maintain(scene)
        layout = self.layout
        try:
            active_pass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
            return
        shaders = context.scene.renderman_settings.shaders

        row = layout.row(align = True)
        global WSURFSHADER
        if WSURFSHADER == None:
            WSURFSHADER = ShaderSelector(shaders.surface_collection, "wsurf")
        WSURFSHADER.insert_into_layout(context, row, active_pass.global_shader.surface_shader)
        #row.prop_search(active_pass.global_shader, "surface_shader", shaders, "surface_collection", text="", icon='MATERIAL')
        row.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
        
        layout.label(text=shader_info(active_pass.global_shader.surface_shader,
                                      active_pass.global_shader.surface_shader_parameter,
                                      scene))

        matparmlayout(context,
                      active_pass.global_shader.surface_shader_parameter,
                      layout,
                      bpy.data,
                      scene.renderman_settings,
                      "ws"+active_pass.name)

WVOLSHADER = None
class World_PT_AtmosphereShaderPanel(bpy.types.Panel, WorldButtonsPanel):
    bl_label = "Atmosphere Shader"
    
    COMPAT_ENGINES = {'RENDERMAN'}

    def draw(self, context):
        scene = context.scene
        ##maintain(scene)
        layout = self.layout
        try:
            active_pass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
            return
        shaders = context.scene.renderman_settings.shaders

        row = layout.row(align = True)
        global WVOLSHADER
        if WVOLSHADER == None:
            WVOLSHADER = ShaderSelector(shaders.volume_collection, "wvol")
        WVOLSHADER.insert_into_layout(context, row, active_pass.global_shader.atmosphere_shader)
        #row.prop_search(active_pass.global_shader, "atmosphere_shader", shaders, "volume_collection", text="", icon='MATERIAL')
        row.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
        
        layout.label(text=shader_info(active_pass.global_shader.atmosphere_shader,
                                      active_pass.global_shader.atmosphere_shader_parameter,
                                      scene))
        

        matparmlayout(context,
                      active_pass.global_shader.atmosphere_shader_parameter,
                      layout,
                      bpy.data,
                      scene.renderman_settings,
                      "wa"+active_pass.name)


class Renderman_PT_world_Attribute_Panel(bpy.types.Panel, WorldButtonsPanel):
    bl_label = "Attributes"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        try:
            active_pass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
            return
        string = "bpy.context.scene.renderman_settings.passes"
        string += "["+string+"_index]"
        if active_pass:
            attribute_panel_layout("world"+active_pass.name, string, layout, scene)
            
class Renderman_PT_CustomWorldCodePanel(bpy.types.Panel, WorldButtonsPanel):
    bl_label = "Custom Code"
    bl_options = {"DEFAULT_CLOSED"}
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        custom_code_layout("world", context, self.layout)

##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      Render Panels                                                                                    #
#                                                                                                       #
#########################################################################################################
class Renderman_OT_set_hider(bpy.types.Operator):
    bl_label="set hider"
    bl_idname="hider.set"
    bl_description="set hider for current pass"

    hider = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        rmansettings = context.scene.renderman_settings
        hider = self.hider
        getactivepass(context.scene).hider = hider
    
        return {'FINISHED'}
            
    
class Renderman_MT_hiderlist(bpy.types.Menu):
    bl_label="set hider"
    
    def draw(self, context):
        for hider in getactivepass(context.scene).hider_list:
            self.layout.operator("hider.set", text=hider.name, icon="GHOST_ENABLED").hider = hider.name    

class  RENDERMan_MT_renderenginepresets(bpy.types.Menu):
    bl_label = "Renderengine Presets"
    preset_subdir = "renderman"
    preset_operator = "script.execute_rendermanpreset"

    def draw(self, context):
        layout = self.layout
        main_preset_path = bpy.utils.preset_paths('renderman')[0]
        for file in os.listdir(main_preset_path):
            filepath = os.path.join(main_preset_path, file)
            if os.path.isfile(filepath):
                layout.operator(self.preset_operator, text=file.replace(".py", "")).filepath = filepath

class RenderButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.scene and rd.use_game_engine is False) and (rd.engine in cls.COMPAT_ENGINES)
    

#class Renderman_PT_Animation(RenderButtonsPanel, bpy.types.Panel):
    #bl_label = "Animation"
    
    #COMPAT_ENGINES = {'RENDERMAN'}
    
    #def draw(self, context):
        ##block_blender()
        #scene = context.scene
        #layout = self.layout
        #split = layout.split(percentage = 0.5)
        #col = split.column(align = True)
        #col.label("Frame Range:")
        #col.prop(scene, "frame_start", text="Start")
        #col.prop(scene, "frame_end", text="End")
        #col.prop(scene, "frame_step", text="Step")
        #col = split.column(align = True)
        #col.label("Frame Rate:")
        #col.prop(scene.render, "fps")
        #col.prop(scene.render, "fps_base", text="/")
        #row = col.row(align = True)
        #row.prop(scene.render, "frame_map_old", text="Old")
        #row.prop(scene.render, "frame_map_new", text = "New")
    
    
class Renderman_PT_Render(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Render"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        #block_blender()
        rm = context.scene.renderman_settings
        layout = self.layout
        layout.prop(rm, "bi_render", text="Use BI Render Operator")
        row = layout.row()
        if rm.bi_render:
            row.operator("render.render", text="Image", icon="RENDER_STILL")
            row.operator("render.render", text="Animation", icon="RENDER_ANIMATION").animation = True
        else:
            row.operator("renderman.render", text="Image", icon="RENDER_STILL")
            row.operator("renderman.render", text="Animation", icon="RENDER_ANIMATION").anim = True
        row = layout.row()
        row.prop(context.scene.renderman_settings, "exportallpasses")
        row.prop(rm, "exportonly", text="Export Only")
        if rm.exportonly:
            row = layout.row()
            row.prop(rm, "shellscript_create")
            if rm.shellscript_create:
                row = layout.row()
                row.prop(rm, "shellscript_append")
                row = layout.row()
                row.prop(rm, "shellscript_file")
                
        row = layout.row()
        row.prop(context.scene.render, "display_mode")

class Render_PT_RendermanSettings(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Renderman Settings"
    bl_idname = "RenderSettingsPanel"
    bl_options = {'DEFAULT_CLOSED'}

    COMPAT_ENGINES = {'RENDERMAN'}
    

    def draw(self, context):
        #block_blender()
        scene = context.scene
        rmansettings = scene.renderman_settings
        layout = self.layout
        row = layout.row(align = True)
        row.menu("RENDERMan_MT_renderenginepresets", text=rmansettings.active_engine)
        row.operator("renderman.renderengine_preset_add", text="", icon="ZOOMIN")
        
        ## basic render settings (executables, etc.)
        row = layout.row()
        col = row.column(align=True)
        renderer_label_box = col.box()        

        row = renderer_label_box.row(align=True)
        row.prop(rmansettings, "basic_expand", text="", icon="TRIA_DOWN" if rmansettings.basic_expand else "TRIA_RIGHT", emboss=False)
        row.label(text="Basic Settings", icon="PREFERENCES")
        if rmansettings.basic_expand:
            renderer_box = col.box()
            row = renderer_box.row(align=True)            
            col = row.column(align=True)
            col.label(text="Executables:")        
            col.prop(scene.renderman_settings, "renderexec", text="Renderer")
            col.prop(scene.renderman_settings, "shaderexec", text="Compiler")
            col.prop(scene.renderman_settings, "shaderinfo", text="Info")
            col.prop(scene.renderman_settings, "textureexec", text="Texture")
            col = row.column(align=True)
            col.label(text="Extensions:")        
            col.prop(scene.renderman_settings, "shadersource", text="source")
            col.prop(scene.renderman_settings, "shaderbinary", text="binary")
            col.prop(scene.renderman_settings, "textureext", text="texture")

            row = renderer_box.row(align=True)
            col = row.column(align = True)
            col.label(text = "Display Drivers:")   
            col.prop(scene.renderman_settings, "disp_ext_os_default", text="OS Default LIB extension")
            row = col.row(align=True)
            row.prop(scene.renderman_settings, "disp_ext", text="Extension")
            row.enabled = not scene.renderman_settings.disp_ext_os_default
            col.prop(scene.renderman_settings, "displaydrvpath", text="folder")
            col.prop(scene.renderman_settings, "drv_identifier", text="identifier")
            row = renderer_box.row()
            row.prop(scene.renderman_settings, "facevertex", text='Export UVs as "facevertex"')
        
        ## Hider settings
        col = layout.column(align=True)
        hider_label_box = col.box()
        row = hider_label_box.row(align=True)
        row.prop(rmansettings, "hider_expand", text="", icon="TRIA_DOWN" if rmansettings.hider_expand else "TRIA_RIGHT", emboss=False)
        row.label(text="Hider and Hider Options", icon="PREFERENCES")
        if rmansettings.hider_expand:
            hider_box = col.box()            
            row = hider_box.row()            
            rows = len(scene.renderman_settings.hider_list)+1
            row.template_list(scene.renderman_settings, "hider_list", scene.renderman_settings, "hider_list_index", rows=rows)
            col = row.column(align=True)
            col.operator("renderman.addremhider", icon='ZOOMIN', text="")
            col.operator("renderman.addremhider", icon='ZOOMOUT', text="").add = False
            
            if scene.renderman_settings.hider_list:
                ogindex = rmansettings.hider_list_index
                if ogindex >= len(rmansettings.hider_list): oqindex = 0   
                selected_hider = scene.renderman_settings.hider_list[ogindex]                
                col.label(text="", icon="FILE_TICK" if (selected_hider.name == rmansettings.default_hider and rmansettings.default_hider != "") else "BLANK1")
                row = hider_box.row(align=True)

                row.operator("renderman.addhideroption", text="", icon='ZOOMIN')
                row.prop(selected_hider, "name", text="")
                row.operator("hider.set_default", text="", icon="FILE_TICK").hider = selected_hider.name
                row = hider_box.row()
                hider_option_index = -1                
                for hider_option in selected_hider.options:
                    hider_option_index += 1
                    row = hider_box.row(align=True)
                    row.prop(hider_option, "name", text="")
                    if hider_option.parametertype == "float" or hider_option.parametertype == "int":
                        row.prop(hider_option, "vector_size", text="")
                    row.prop(hider_option, "parametertype", text="") 
                    row.operator("renderman.remhideroption", text="", icon="ZOOMOUT").index = hider_option_index                   
        ## Options
        col = layout.column(align=True)
        option_label_box = col.box()
        row = option_label_box.row(align=True)
        row.prop(rmansettings, "options_expand", text="", icon="TRIA_DOWN" if rmansettings.options_expand else "TRIA_RIGHT", emboss=False)
        row.label(text="Options", icon = "PREFERENCES")
        if rmansettings.options_expand:
            option_box = col.box()
            row = option_box.row()
            rows = len(rmansettings.option_groups)+1
            row.template_list(rmansettings, "option_groups", rmansettings, "option_groups_index", rows=rows)
            col = row.column(align=True)
            col.operator("renderman.addoptiongroup", text="", icon='ZOOMIN')
            col.operator("renderman.removeoptiongroup", text="", icon='ZOOMOUT')
            if rmansettings.option_groups:
                ogindex = rmansettings.option_groups_index
                if ogindex >= len(rmansettings.option_groups): oqindex = 0           
                selected_group = rmansettings.option_groups[ogindex]
                row = option_box.row(align=True)
                row.operator("renderman.addoption", text="", icon="ZOOMIN")
                row.prop(selected_group, "name", text="")
                option_index = -1
                for option in selected_group.options:
                    option_index += 1
                    row = option_box.row(align=True)
                    row.prop(option, "name", text="")
                    if option.parametertype == "float" or option.parametertype == "int":
                        row.prop(option, "vector_size", text="")
                    row.prop(option, "parametertype", text="")
                    row.operator("renderman.remoption", text="", icon='ZOOMOUT').index = option_index
                    
        ## Attributes
        col = layout.column(align=True)                
        attribute_label_box = col.box()
        row = attribute_label_box.row(align = True)
        row.prop(rmansettings, "attributes_expand", text="", icon="TRIA_DOWN" if rmansettings.attributes_expand else "TRIA_RIGHT", emboss=False)
        row.label(text="Attributes", icon="PREFERENCES")
        if rmansettings.attributes_expand:
            attribute_box = col.box()
            row = attribute_box.row()
            rows = len(rmansettings.attribute_groups)+1
            row.template_list(rmansettings, "attribute_groups", rmansettings, "attribute_groups_index", rows=rows)
            col = row.column(align=True)
            col.operator("renderman.addattributegroup", text="", icon='ZOOMIN')
            col.operator("renderman.removeattributegroup", text="", icon='ZOOMOUT')
            if rmansettings.attribute_groups:
                agindex = rmansettings.attribute_groups_index
                if agindex >= len(rmansettings.attribute_groups): aqindex = 0
                selected_group = rmansettings.attribute_groups[agindex]
                row = attribute_box.row(align = True)
                row.operator("renderman.addattribute", text="", icon='ZOOMIN')
                row.prop(selected_group, "name", text="")
                for attribute_index, attribute in enumerate(selected_group.attributes):
                    row = attribute_box.row(align=True)
                    row.prop(attribute, "name", text="")
                    if attribute.parametertype == "float" or attribute.parametertype == "int":
                        row.prop(attribute, "vector_size", text="")
                    row.prop(attribute, "parametertype", text="")
                    if attribute.parametertype == 'string':
                        row.prop(attribute, "input_type", text="")                    
                    row.operator("renderman.remattribute", text="", icon='ZOOMOUT').index = attribute_index                        
                
        ## Shader Search Paths
        col = layout.column(align=True)
        shader_label_box = col.box()
        row = shader_label_box.row(align=True)
        row.prop(rmansettings, "shader_expand", text="", icon="TRIA_DOWN" if rmansettings.shader_expand else "TRIA_RIGHT", emboss=False)
        row.label(text = "Shader Paths", icon="PREFERENCES")
        if rmansettings.shader_expand:
            shader_box = col.box()
            row = shader_box.row()
            row.template_list(scene.renderman_settings.shaders, "shaderpaths", scene.renderman_settings.shaders, "shaderpathsindex")
            col = row.column()
            sub = col.column(align=True)
            sub.operator("renderman.pathaddrem", text="", icon="ZOOMIN").add = True
            sub.operator("renderman.pathaddrem", text="", icon="ZOOMOUT").add = False
            sub.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
            row = shader_box.row()
            row.prop(scene.renderman_settings, "shaderpath", text="")
            row = shader_box.row()
            row.prop(scene.renderman_settings, "shaderpath_recursive")
            
        ## Output Folders
        col = layout.column(align=True)
        dir_label_box = col.box()
        row = dir_label_box.row(align=True)
        row.prop(rmansettings, "dir_expand", text="", icon="TRIA_DOWN" if rmansettings.dir_expand else "TRIA_RIGHT", emboss=False)
        row.label(text = "Output Folders", icon="PREFERENCES")
        if rmansettings.dir_expand:
            dir_box = col.box()
            row = dir_box.row()
            col = row.column(align=True)    
            col.label(getdefaultribpath(scene)+"/...")
            col.prop(scene.renderman_settings, "texdir", text="Texture maps")
            col.prop(scene.renderman_settings, "bakedir", text="Bakefiles")
            row = dir_box.row(align=True)
            row.prop(scene.renderman_settings, "framepadding", text="Frame Padding")
            
        ## Custom Driver Options
        col = layout.column(align=True)                
        driver_label_box = col.box()
        row = driver_label_box.row(align = True)
        row.prop(rmansettings, "drivers_expand", text="", icon="TRIA_DOWN" if rmansettings.drivers_expand else "TRIA_RIGHT", emboss=False)
        row.label(text="Custom Driver Options", icon="PREFERENCES")
        if rmansettings.drivers_expand:
            driver_box = col.box()
            row = driver_box.row()
            rows = len(rmansettings.displays)+1
            row.template_list(rmansettings, "displays", rmansettings, "display_index", rows=rows)
            if rmansettings.displays:
                dindex = rmansettings.display_index
                if dindex >= len(rmansettings.displays): dindex = 0
                selected_disp = rmansettings.displays[dindex]
                row = driver_box.row(align = True)
                row.operator("displayoption.add", text="", icon='ZOOMIN').disp = dindex
                row.prop(selected_disp, "name", text="")
                row.operator("displayoption.refresh", text="", icon="FILE_REFRESH")
                for di, opt in enumerate(selected_disp.custom_parameter):
                    row = driver_box.row(align=True)
                    row.prop(opt, "name", text="")
                    if opt.parametertype == "float" or opt.parametertype == "int":
                        row.prop(opt, "vector_size", text="")
                    row.prop(opt, "parametertype", text="")
                    if opt.parametertype == 'string':
                        row.prop(opt, "input_type", text="")
                        row.prop(opt, "use_var")
                    op = row.operator("displayoption.remove", text="", icon='ZOOMOUT')
                    op.disp = dindex
                    op.opt = di


class Renderman_MT_loadPassPreset(bpy.types.Menu):
    bl_label = "Pass Presets"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        passes_preset_layout(layout, scene)

            
class Renderman_MT_addPresetPass(bpy.types.Menu):
    bl_label="Presets"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        passes_preset_layout(layout, scene)       

class Renderman_MT_addPassMenu(bpy.types.Menu):
    bl_label = ""
    
    def draw(self, context):
        layout = self.layout
        layout.operator("renderman.addpass", text="New").path = "bpy.context.scene.renderman_settings.passes"
        layout.menu("Renderman_MT_addPresetPass")
        layout.operator("renderman.addpasspreset", text = "Save Preset") 

class Renderman_PT_RIB_Structure(bpy.types.Panel, RenderButtonsPanel):
    bl_label = "Rib Structure"
    bl_options = {'DEFAULT_CLOSED'}
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw_archive_panel(self, layout, context, pa, name, base=False):
        rm = context.scene.renderman_settings
        rs = rm.rib_structure
        p = eval('rs.'+pa)
                
        mcol = layout.column(align=True)
        row = mcol.row(align=True)
        row.prop(p, "expand", text = "", icon = "TRIA_DOWN" if p.expand else "TRIA_RIGHT", emboss=False)
        row.label(name)
        if p.expand:
            if not base:
                row = mcol.row()
                row.prop(p, "own_file", text="Export to own Archive")
            row = mcol.row()
            row.enabled = p.own_file
            row.prop(p, "default_name")
            row = mcol.row(align=True)
            split = row.split(align=True, percentage = 0.7)
            row.enabled = not p.default_name
            split.prop(p, "filename", text="")
            split.prop(p, "folder", text="")
            row = mcol.row()
            row.prop(p, "overwrite", text="overwrite existing")
        return p.expand
        
    def draw(self, context):
        #block_blender()
        dap = self.draw_archive_panel
        lay = self.layout
        col = lay.column()
        frame_box = col.box()
        if dap(frame_box, context, 'frame', 'Frame', base=True):
            pass_box = frame_box.box()
            
            if dap(pass_box, context, 'render_pass', "Passes"):
                dap(pass_box, context, 'object_blocks', 'Instances')
                dap(pass_box, context, 'settings', "Settings")
                if dap(pass_box, context, 'world', 'Worlds'):
                    world_box = pass_box.box()
                    if dap(world_box, context, 'objects', 'Objects'):
                        obj_box = world_box.box()
                        dap(obj_box, context, 'materials', 'Materials')
                    dap(world_box, context, 'lights', 'Lights')
                    if dap(world_box, context, 'particles', 'Particle Systems'):
                        dap(world_box, context, "particle_data", 'Particle Data')
            frame_box.label("May be a child of Objects or Instances:")
            mesh_box = frame_box.box()
            dap(mesh_box, context, 'meshes', 'Meshes')
            
class Render_PT_RendermanPassesPanel(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Renderman Passes"
    bl_idname = "RenderPassesPanel"
    bl_default_closed = False

    COMPAT_ENGINES = {'RENDERMAN'}
    

    def draw(self, context):
        #block_blender()
        scene = context.scene
        renderman_settings = scene.renderman_settings
        layout = self.layout
        
        row = layout.row()
        col = row.column(align=True)

        if len(renderman_settings.passes) < 15:
            rows = len(renderman_settings.passes)+1
        else:
            rows = 15
    
        col.template_list(renderman_settings, "passes", renderman_settings, "passes_index", rows=rows)

        col = row.column(align=True)

        col.menu("Renderman_MT_addPassMenu", icon="ZOOMIN")
        col.operator("renderman.rempass", text="", icon="ZOOMOUT")
        col.operator("renderman.movepass", icon='TRIA_UP', text="").direction = "up"
        col.operator("renderman.movepass", icon='TRIA_DOWN', text="").direction = "down"

        maintain_lists(scene)
        try:
            active_pass = getactivepass(scene)
            if active_pass == None:
                raise IndexError
        except IndexError:
            layout.label("No Render Pass")
            return
        
        row = layout.row(align=True) 
        if renderman_settings.passes:
            row.prop(active_pass, "name", text="")
            row.prop(active_pass, "export", text="")
        
        
class Renderman_PT_PassCamera(bpy.types.Panel, RenderButtonsPanel):
    bl_label = "Camera"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        layout = self.layout
        apass = getactivepass(context.scene)
        if apass == None:
            layout.label("No Render Pass")
            return
        row = layout.row()
        row.prop_search(apass, "camera_object", context.scene, "objects", text = "Camera")
        row = layout.row()
        row.prop(apass, "environment", text="Environment")
        #if apass.camera_object != "" and apass.camera_object in context.scene.objects:
            #rc = apass.renderman_camera
            #dimensions_layout(layout, rc, context.scene, apass.environment)


class Renderman_PT_QualityPanel(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Quality"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene    
        active_pass = getactivepass(scene)
        if active_pass == None:
            layout.label("No Render Pass")
            return
        row = layout.row(align=True)
        row.prop(active_pass.pixelfilter, "filterlist", text="")
        row.prop(active_pass, "pixelsamples_x", text="X Samples")                                                                       
        row.prop(active_pass, "pixelsamples_y", text="Y Samples")
        if active_pass.pixelfilter.filterlist == "other":
            row.prop(active_pass.pixelfilter, "customfilter")
        row=layout.row(align=True)                            
        row.prop(active_pass.pixelfilter, "filterwidth", text = "Filter width")
        row.prop(active_pass.pixelfilter, "filterheight", text = "Filter height")

class Renderman_PT_MotionBlurPanel(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Motion Blur"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        #block_blender()
        ##maintain()
        layout = self.layout
        scene = context.scene
        current_pass = getactivepass(scene)
        if current_pass == None:
            layout.label("No Render Pass")
            return
        row = layout.row()
        row.prop(current_pass, "motionblur")
        row = layout.row(align = True)
        row.enabled = current_pass.motionblur
        if current_pass.shutter_type == "angle":
            row.prop(current_pass, "shutterspeed_ang", text="degrees")
        else:
            row.prop(current_pass, "shutterspeed_sec", text="seconds")
        row.prop(current_pass, "shutter_type", text="")

        
    
class RENDERMANRender_PT_OptionsPanel(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Options"
    bl_idname = "options"
    bl_default_closed = True

    COMPAT_ENGINES = {'RENDERMAN'}
    

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        render = scene.render
        renderman_settings = scene.renderman_settings

        active_pass = getactivepass(scene)
        if active_pass == None:
            layout.label("No Render Pass")
            return
        render = scene.render
        row = layout.row(align=True)
        row.operator("options.set_as_default", text="set as default", icon="FILE_TICK")
        row.operator("options.get_default", text="get default", icon="ANIM")
        attribute_menu("Options")
        row.menu("option_Options", text = "", icon = "ZOOMIN")
        
        for group in active_pass.option_groups:
            master_options = renderman_settings.option_groups[group.name].options            
            group_box = layout.box()
            group_box.active = group.export
            row = group_box.row(align=True)
            row.prop(group, "expand", text="", icon="TRIA_DOWN" if group.expand else "TRIA_RIGHT", emboss=False)
            row.label(text = group.name)
            str = "bpy.context.scene.renderman_settings.passes"
            str += "["+str+"_index]"
            mname = attribute_options("Options"+active_pass.name, str, "", group.name)
            row.menu(mname, text = "", icon = "DOWNARROW_HLT")
            if group.expand:
                for option in group.options:
                    master_option = master_options[option.name]
                    row = group_box.row(align=True)
                    row.active = option.export
                    row.label(master_option.name)            
                    parmlayout(option, master_option, row, scene)
                
                    mname = attribute_options("Options"+active_pass.name, str, option.name, group.name)
                    row.menu(mname, text = "", icon = "DOWNARROW_HLT")
                        
class Render_PT_RendermanHiderPanel(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Hider"
    bl_idname = "hider"

    COMPAT_ENGINES = {'RENDERMAN'}
    

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        renderman_settings = scene.renderman_settings
        active_pass = getactivepass(scene)
        if active_pass == None:
            layout.label("No Render Pass")
            return
        layout.menu("Renderman_MT_hiderlist", text=active_pass.hider, icon="GHOST_ENABLED")
        if active_pass.hider != "":
            row = layout.row(align=True)
            row.operator("hider.get_default_values", text="get default", icon="ANIM").hider = active_pass.hider
            row.operator("hider.set_default_values", text="set default", icon="FILE_TICK").hider = active_pass.hider
            for master_option in renderman_settings.hider_list[active_pass.hider].options:
                slave_option = getactivepass(scene).hider_list[active_pass.hider].options[master_option.name]
                row = layout.row(align=True)
                row.label(text=master_option.name)
                row.active = slave_option.export
                parmlayout(slave_option, master_option, row, scene)
                str = "bpy.context.scene.renderman_settings.passes"
                str += "['"+active_pass.name+"']"
                mname = attribute_options("Hider"+active_pass.name, str, master_option.name, active_pass.hider)
                row.menu(mname, text = "", icon = "DOWNARROW_HLT")

    
class Render_PT_RendermanDisplayPanel(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Display"
    bl_idname = "display"

    COMPAT_ENGINES = {'RENDERMAN'}
    

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        renderman_settings = scene.renderman_settings
        active_pass = getactivepass(scene)
        if active_pass == None:
            layout.label("No Render Pass")
            return
        layout.prop(active_pass, "imagedir", text="Image Folder")
        layout.operator("renderman.adddisplay", text="", icon="ZOOMIN")
        for display_index, display in enumerate(active_pass.displaydrivers):
            main_box = layout.box()
            row = main_box.row(align=True)
            col = row.column()
            sub_row = col.row(align=True)
            sub_row.label(text="", icon = "FILE_TICK" if display.send else "BLANK1")                  
            sub_row.operator("display.send", icon="IMAGE_COL", text="").display = display.name
            if display.displaydriver == "framebuffer":
                sub_row.enabled = False
            else:
                sub_row.enabled = True                    
                                        
            row.prop(display, "expand", text="", icon="TRIA_DOWN" if display.expand else "TRIA_RIGHT", emboss=False)
            row.prop(display, "name", text="")
            row.operator("renderman.displaydriver_menu", text=display.displaydriver).display = display.name
            #row.prop_search(display, "displaydriver", renderman_settings, "displays", text="", icon="FILE_SCRIPT")
            row.prop_search(display, "var", renderman_settings, "var_collection", text="", icon="RENDER_RESULT")
            row.operator("renderman.remdisplay", text="", icon="ZOOMOUT").index = display_index
            row.prop(display, "export", text="")
            row.active = display.export
            if display.expand:
                row = main_box.row()
                split = row.split(percentage = 0.25)
                split.prop(display, "default_name")
                col = split.column()

                col.label(text=display.filename)
                r = col.row()
                r.prop(display, "raw_name")
                r.enabled = not display.default_name
                box = main_box.box()
                row = box.row(align=True)
                row.prop(display, "quantize_expand", text="", icon="TRIA_DOWN" if display.quantize_expand else "TRIA_RIGHT", emboss=False)
                row.label(text="Quantize:")
                if display.quantize_expand:                        
                    row = box.row(align=True)
                    row.prop(display, "quantize_presets", text="")                        
                    row.prop(display, "quantize_min", text="")
                    row.prop(display, "quantize_max", text="")
                    row.prop(display, "quantize_black", text="")
                    row.prop(display, "quantize_white", text="") 
                box = main_box.box()
                row = box.row(align=True)
                row.prop(display, "exposure_expand", text="", icon="TRIA_DOWN" if display.exposure_expand else "TRIA_RIGHT", emboss=False)
                row.label(text="Exposure:")
                if display.exposure_expand:
                    row = box.row(align=True)
                    row.prop(display, "gain")                                                
                    row.prop(display, "gamma")
                for i, co in enumerate(display.custom_options):
                    box = main_box.box()
                    row = box.row(align=True)
                    if co.parametertype == "string" and co.use_var:
                        row.label(co.name+": "+co.textparameter)
                        row.prop(co, "export", text="")
                    else:
                        row.prop(co, "expand", text="", icon="TRIA_DOWN" if co.expand else "TRIA_RIGHT", emboss=False)
                        row.label(co.name+':')                        
                        if co.expand:
                            row = box.row(align=True)
                            parmlayout(co, co, row, scene)
                            row.active = co.export                            
                            row.prop(co, "export", text="")
                box = main_box.box()
                row = box.row(align=True)
                row.prop(display, "processing_expand", text="", icon="TRIA_DOWN" if display.processing_expand else "TRIA_RIGHT", emboss=False)
                row.label(text="Image Processing:")
                if display.processing_expand:
                    row = box.row(align=True)
                    col = row.column()
                    pr = display.processing
                    image_processing_layout(pr, col)


class Renderman_PT_CustomSceneCodePanel(bpy.types.Panel, RenderButtonsPanel):
    bl_label = "Custom Code"
    bl_options = {"DEFAULT_CLOSED"}
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        custom_code_layout("scene", context, self.layout)

##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      Texture Panels                                                                                   #
#                                                                                                       #
#########################################################################################################


class TextureButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    @classmethod
    def poll(cls, context):
        tex = context.texture
        if not tex:
            return False
        engine = context.scene.render.engine
        return (tex.type) and (engine in cls.COMPAT_ENGINES)
    
class RENDERMAN_PT_context_texture(TextureButtonsPanel, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'RENDERMAN'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if not hasattr(context, "texture_slot"):
            return False
        return ((context.material or context.world or context.lamp or context.brush or context.texture)
            and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        slot = context.texture_slot
        node = context.texture_node
        space = context.space_data
        tex = context.texture
        if context.material:
            idblock = context.material
        elif context.lamp:
            idblock = context.lamp
        elif context.world:
            idblock = context.world
        else:
            idblock = context.brush

        tex_collection = type(idblock) != bpy.types.Brush and not node

        if tex_collection:
            row = layout.row()

            row.template_list(idblock, "texture_slots", idblock, "active_texture_index", rows=2)

            col = row.column(align=True)
            col.operator("texture.slot_move", text="", icon='TRIA_UP').type = 'UP'
            col.operator("texture.slot_move", text="", icon='TRIA_DOWN').type = 'DOWN'
            col.menu("TEXTURE_MT_specials", icon='DOWNARROW_HLT', text="")

        row = layout.row()
        if tex_collection:
            row.template_ID(idblock, "active_texture", new="texture.new")
        elif node:
            row.template_ID(node, "texture", new="texture.new")
        elif idblock:
            row.template_ID(idblock, "texture", new="texture.new")

#        if space.pin_id:
        row.template_ID(space, "pin_id")

        col = row.column()

        col.prop(space, "texture_context", text="", toggle=True)

        if tex:
            split = layout.split(percentage=0.2)

            if tex.use_nodes:

                if slot:
                    split.label(text="Output:")
                    split.prop(slot, "output_node", text="")

            else:
                split.label(text="Type:")
                if type(idblock) == bpy.types.Brush:
                    split.prop(tex, "type", text="")
                else:
                    split.prop(tex.renderman, "type", text="", icon="TEXTURE")
                    

class TextureTypePanel(TextureButtonsPanel):

    @classmethod
    def poll(cls, context):
        tex = context.texture
        engine = context.scene.render.engine
        return tex and ((tex.renderman.type == cls.tex_type and not tex.use_nodes) and (engine in cls.COMPAT_ENGINES))
        
   
class Renderman_TextureFilterPanel(bpy.types.Panel, TextureTypePanel):
    bl_label = "Renderman Filtering"
    tex_type = 'file'
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        lay = self.layout
        tex = context.texture
        pr = tex.renderman.processing
        image_processing_layout(pr, lay)


##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      Material Panels                                                                                  #
#                                                                                                       #
#########################################################################################################

current_scene = bpy.context.scene

class MaterialButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material) and (engine in cls.COMPAT_ENGINES)
        
        
class Renderman_OT_set_material_preview(bpy.types.Operator):
    bl_label =""
    bl_idname = "renderman.set_material_preview"
    bl_description=""
    
    scene = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        mat = context.material
        rm = mat.renderman[mat.renderman_index]
        rm.preview_scene = self.scene
        return{'FINISHED'}
        
class Renderman_MT_materialPreview(bpy.types.Menu):
    bl_label=""
    
    def draw(self, context):
        rmprdir = bpy.utils.preset_paths("renderman")[0]
        mat_preview_path = os.path.join(rmprdir, "material_previews")
        for dir in os.listdir(mat_preview_path):
            if os.path.isdir(os.path.join(mat_preview_path, dir)):
                self.layout.operator("renderman.set_material_preview", text=dir).scene = dir
                
    
class Renderman_PT_materialPreview(bpy.types.Panel, MaterialButtonsPanel):
    bl_label ="Preview"
    COMPAT_ENGINES = {'RENDERMAN'}
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        mat = context.material
        set_preview_mat(mat)
        if -1 < mat.renderman_index < len(mat.renderman):
            rm = mat.renderman[mat.renderman_index]
            self.layout.prop(rm, "preview", text="")
    
    def draw(self, context):
        mat = context.material
        set_preview_mat(mat)
        if -1 < mat.renderman_index < len(mat.renderman):
            rm = mat.renderman[mat.renderman_index]
            if rm.preview:
                current_scene = bpy.context.scene
                self.layout.template_preview(context.material, show_buttons=False)
                self.layout.menu("Renderman_MT_materialPreview", text=rm.preview_scene)

class RENDERMAN_PT_context_material(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = " "
    bl_show_header = False
    COMPAT_ENGINES = {'RENDERMAN'}

    @classmethod
    def poll(cls, context):
        # An exception, dont call the parent poll func because
        # this manages materials for all engine types

        engine = context.scene.render.engine
        return (context.material or context.object) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        #maintain(scene)

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data
        split = layout.split(percentage=0.65)
        row = layout.row()

        if ob:
            row.template_list(ob, "material_slots", ob, "active_material_index", rows=2)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")
            split.template_ID(ob, "active_material", new="material.new")
            row = split.row()
            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()
        else:
            if ob:
                layout.template_ID(ob, "active_material", new="material.new")
            elif mat:
                layout.template_ID(space, "pin_id")


class Renderman_PT_Material_Passes(bpy.types.Panel, MaterialButtonsPanel):
    bl_label = "Passes"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        passes_linking_layout("material", "bpy.context.material", self.layout, context.scene)
        
class RendermanMaterial_PT_MatteFlag(bpy.types.Panel, MaterialButtonsPanel):
    bl_label = "Matte"
    bl_options = {"HIDE_HEADER"}
    
    COMPAT_ENGINES = {'RENDERMAN'}
        
    def draw(self, context):
        mat = context.material
        try:
            rm = mat.renderman[mat.renderman_index]
            self.layout.prop(rm, "matte")
        except IndexError:
            self.layout.label("No Pass")

class RENDERMANMaterial_PT_MotionBlurPanel(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "MotionBlur"

    COMPAT_ENGINES = {'RENDERMAN'}
    

    def draw(self, context):
        layout = self.layout
        ##maintain(context.scene)
        try:
            apass = getactivepass(context.scene)
        except IndexError:
            layout.label("No Render Pass")
            return
        m = context.material
        try:
            mat = m.renderman[m.renderman_index]
            row = layout.row()
            col = row.column(align=True)
            row.enabled = apass.motionblur
            col.prop(mat, "color_blur")
            col.prop(mat, "opacity_blur")
            col.prop(mat, "shader_blur")
            col = row.column()
            col.prop(mat, "motion_samples")
        except IndexError:
            layout.label("No Material Pass")

class Renderman_OT_set_diffuse_color(bpy.types.Operator):
    bl_label = "set diffuse color"
    bl_idname =  "renderman.set_diffuse"
    
    mat = bpy.props.StringProperty()
    color = bpy.props.FloatVectorProperty(subtype = 'COLOR')
    
    def execute(self, context):
        mat = bpy.data.materials[self.mat]
        col = self.color
        mat.diffuse_color = col
        return {'FINISHED'}

SURFSHADER = None
class RENDERMANMaterial_PT_SurfaceShaderPanel(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Surface Shader"
    bl_idname = "SurfaceShaderPanel"

    COMPAT_ENGINES = {'RENDERMAN'}
    

    def draw(self, context):
        scene = context.scene
        ##maintain(scene)
        m = context.material
        if len(m.renderman) > m.renderman_index and m.renderman_index != -1:
            mat = m.renderman[m.renderman_index]
            layout = self.layout
            shaders = context.scene.renderman_settings.shaders

            row = layout.row(align = True)
            col = row.column()
            col.label(text="Color")
            col.prop(mat, "color", text="")
            col = row.column()
            col.label(text="Opacity")
            col.prop(mat, "opacity", text="")

            row= layout.row(align=True)
            global SURFSHADER
            if SURFSHADER == None:
                SURFSHADER = ShaderSelector(shaders.surface_collection, "objsurf")
            SURFSHADER.insert_into_layout(context, row, mat.surface_shader)
            #row.prop_search(mat, "surface_shader", shaders, "surface_collection", text="", icon='MATERIAL')
            row.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
            
            layout.label(text=shader_info(mat.surface_shader,
                                          mat.surface_shader_parameter,
                                          scene))
            

            matparmlayout(context,
                          mat.surface_shader_parameter,
                          layout,
                          context.material,
                          scene.renderman_settings,
                          "ms"+m.name+mat.name,
                          client = context.object.name)

DISPSHADER = None
class RENDERMANMaterial_PT_DisplacementShaderPanel(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Displacement Shader"
    bl_idname = "DisplacementShaderPanel"

    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        ##maintain(scene)
        m = context.material
        if len(m.renderman) > m.renderman_index and m.renderman_index != -1:
            mat = m.renderman[m.renderman_index]
            layout = self.layout
            row = layout.row(align=True)
            shaders = context.scene.renderman_settings.shaders

            global DISPSHADER
            if DISPSHADER == None:
                DISPSHADER = ShaderSelector(shaders.displacement_collection, "objdisp")
            DISPSHADER.insert_into_layout(context, row, mat.displacement_shader)
            #row.prop_search(mat, "displacement_shader", shaders, "displacement_collection", text="", icon='MATERIAL')
            row.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
            layout.label(text=shader_info(mat.displacement_shader, mat.disp_shader_parameter, scene))
            

            matparmlayout(  context,
                            mat.disp_shader_parameter,
                            layout,
                            context.material,
                            scene.renderman_settings,
                            "md"+m.name+mat.name,
                            client = context.object.name) 
    
INTSHADER = None
class RENDERMANMaterial_PT_InteriorShaderPanel(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Interior Shader"
    bl_idname = "InteriorShaderPanel"

    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        ##maintain(scene)
        m = context.material
        if len(m.renderman) > m.renderman_index and m.renderman_index != -1:
            mat = m.renderman[m.renderman_index]
            layout = self.layout
            row = layout.row(align=True)
            shaders = context.scene.renderman_settings.shaders
            global INTSHADER
            if INTSHADER == None:
                INTSHADER = ShaderSelector(shaders.volume_collection, "objint")
            INTSHADER.insert_into_layout(context, row, mat.interior_shader)
            #row.prop_search(mat, "interior_shader", shaders, "volume_collection", text="", icon="MATERIAL")
            row.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
            layout.label(text=shader_info(mat.interior_shader, mat.interior_shader_parameter, scene))

            matparmlayout(context,
                          mat.interior_shader_parameter,
                          layout,
                          context.material,
                          scene.renderman_settings,
                          "mi"+m.name+mat.name,
                          client = context.object.name)


EXTSHADER = None
class RENDERMANMaterial_PT_ExteriorShaderPanel(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Exterior Shader"
    bl_idname = "ExteriorShaderPanel"

    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        ##maintain(scene)
        m = context.material
        if len(m.renderman) > m.renderman_index and m.renderman_index != -1:        
            mat = m.renderman[m.renderman_index]
            layout = self.layout
            row = layout.row(align=True)
            shaders = context.scene.renderman_settings.shaders
            global EXTSHADER
            if EXTSHADER == None:
                EXTSHADER = ShaderSelector(shaders.volume_collection, "objext")
            EXTSHADER.insert_into_layout(context, row, mat.exterior_shader)
            #row.prop_search(mat, "exterior_shader", shaders, "volume_collection", text="", icon="MATERIAL")
            row.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
            layout.label(text=shader_info(mat.exterior_shader, mat.exterior_shader_parameter, scene))

            matparmlayout(context,
                          mat.exterior_shader_parameter,
                          layout,
                          context.material,
                          scene.renderman_settings,
                          "me"+m.name+mat.name,
                          client = context.object.name)
        
ALIGHTSHADER = None
class RENDERMANMaterial_PT_AreaLightShaderPanel(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Area Light Shader"
    bl_idname = "AreaLightShaderPanel"

    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        ##maintain(scene)
        m = context.material
        if len(m.renderman) > m.renderman_index and m.renderman_index != -1:
            mat = m.renderman[m.renderman_index]
            layout = self.layout
            row = layout.row(align=True)
            shaders = context.scene.renderman_settings.shaders
            global ALIGHTSHADER
            if ALIGHTSHADER == None:
                ALIGHTSHADER = ShaderSelector(shaders.light_collection, "objal")
            ALIGHTSHADER.insert_into_layout(context, row, mat.arealight_shader)
            #row.prop_search(mat, "arealight_shader", shaders, "light_collection", text="", icon="MATERIAL")
            row.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
            layout.label(text=shader_info(mat.arealight_shader, mat.light_shader_parameter, scene))

            matparmlayout(context,
                          mat.light_shader_parameter,
                          layout,
                          context.material,
                          scene.renderman_settings,
                          "ma"+m.name+mat.name,
                          client = context.object.name)


        
##################################################################################################################################




################################################################################################################################## 

#########################################################################################################
#                                                                                                       #
#      Light Panels                                                                                     #
#                                                                                                       #
#########################################################################################################


class LightDataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.lamp) and (rd.engine in cls.COMPAT_ENGINES)


class Renderman_PT_Light_Passes(bpy.types.Panel, LightDataButtonsPanel):
    bl_label = "Passes"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        lbp = 'bpy.context.object.data'
        passes_linking_layout("light", lbp, self.layout, context.scene)    

LIGHTMENU = None
class LAMP_PT_RendermanLight(LightDataButtonsPanel, bpy.types.Panel):
    bl_label = "Renderman Settings"

    COMPAT_ENGINES = {'RENDERMAN'}

    def draw(self, context):
        #maintain(context.scene)
        layout = self.layout
        light = context.object
        scene = context.scene
        light_shaders = scene.renderman_settings.shaders.light_collection
        try:
            lamp = light.data.renderman[light.data.renderman_index]
            type = light.data.type
            renderman = lamp

            row=layout.row(align=True)

            shaders = context.scene.renderman_settings.shaders

            global LIGHTMENU
            if LIGHTMENU == None:
                LIGHTMENU = ShaderSelector(shaders.light_collection, "light")
            LIGHTMENU.insert_into_layout(context, row, lamp.shaderpath)
            
            #row.prop_search(lamp, "shaderpath", shaders, "light_collection", text="")
            #if lamp.shaderpath in light_shaders:
                #row.prop(light_shaders[lamp.shaderpath], "lamp_type", text="")
                
            row.operator("renderman.refreshshaderlist", text="", icon="FILE_REFRESH")
            layout.label(text=shader_info(lamp.shaderpath, lamp.light_shader_parameter, scene))

            matparmlayout(context,
                          lamp.light_shader_parameter,
                          layout,
                          bpy.data,
                          scene.renderman_settings,
                          "l"+light.name+lamp.name,
                          client = light.name)
            dimensions_layout(layout, light)
        except IndexError:
            layout.label("No Pass")
        
class Renderman_PT_light_Attribute_Panel(bpy.types.Panel, LightDataButtonsPanel):
    bl_label = "Attributes"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        path = "bpy.context.object.data.renderman"
        lamp = context.object
        path += "["+path+"_index]"
        layout = self.layout
        scene = context.scene
        try:
            active_pass = getactivepass(scene)
            if active_pass and lamp.data.renderman:
                attribute_panel_layout("light"+lamp.name+eval(path).name, path, layout, scene)
        except IndexError:
            layout.label("No pass")

##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      Object Panels                                                                                    #
#                                                                                                       #
#########################################################################################################

class ObjectButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.object) and (rd.engine in cls.COMPAT_ENGINES) and not (context.object.type in ["LAMP", "CAMERA"])  


class Renderman_PT_Object_Passes(bpy.types.Panel, ObjectButtonsPanel):
    bl_label = "Passes"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        passes_linking_layout("object", "bpy.context.object", self.layout, context.scene)    


class Object_PT_MotionBlurPanel(ObjectButtonsPanel, bpy.types.Panel):
    bl_label ="Motion Blur"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        ##maintain(scene)
        obj = context.object
        try:
            rman = obj.renderman[obj.renderman_index]
        except IndexError:
            return
    
        layout = self.layout
        try:
            apass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
            return
        row = layout.row()
        col = row.column()
        col.enabled = getactivepass(scene).motionblur
        col.prop(rman, "transformation_blur")
        col.prop(rman, "deformation_blur")
        col.prop(rman, "motion_samples")

class Mesh_PT_IlluminatePanel(ObjectButtonsPanel, bpy.types.Panel):
    bl_label="Renderman Light Linking"

    COMPAT_ENGINES = {'RENDERMAN'}

    def draw(self, context):
        scene = context.scene
        #maintain(scene)
        layout = self.layout
        object = context.object
        try:
            rm = object.renderman[object.renderman_index]
            row=layout.row(align=True)
            row.operator("renderman.lightlinking", text="All").type = "all"
            row.operator("renderman.lightlinking", text="none").type = "none"
            row.operator("renderman.lightlinking", text="invert").type = "invert"
            row.operator("renderman.lightlinking_refresh", text="", icon="FILE_REFRESH")
            row = layout.row()
            col = row.column(align=True)
            header_box = col.box()
            header_box.label("Light List:", icon="LAMP")
            body_box = col.box()
            body_col = body_box.column(align=True)
            for light in getLightList(scene):
                row = body_col.row()
                row.label(light)
                row.operator("renderman.link_light", icon='OUTLINER_OB_LAMP' if light in rm.lightlist else 'LAMP', text="").light = light
        except IndexError:
            layout.label("no pass")

class Renderman_PT_object_Attribute_Panel(bpy.types.Panel, ObjectButtonsPanel):
    bl_label = "Attributes"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        path = "bpy.context.object.renderman"
        path += "["+path+"_index]"
        layout = self.layout
        obj = context.object
        scene = context.scene
        try:
            attribute_panel_layout("object"+obj.name+eval(path).name, path, layout, scene)  
        except IndexError:
            layout.label("No Render Pass")
            return

class Mesh_PT_GeneralSettings(ObjectButtonsPanel, bpy.types.Panel):
    bl_label ="General Settings"
    bl_idname  ="generalsettings"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        object = context.object
        if getactivepass(scene) == None or len(object.renderman) == 0 or object.renderman_index == -1:
            layout.label("No Render Pass")
            return
        layout.prop(object.data, "show_double_sided")
        layout.prop(object.renderman[object.renderman_index], "shadingrate")
        
        
class Renderman_PT_CustomObjectCodePanel(bpy.types.Panel, ObjectButtonsPanel):
    bl_label = "Custom Code"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        custom_code_layout("object", context, self.layout)
    
#########################################################################################################
#                                                                                                       #
#      Mesh Panels                                                                                      #
#                                                                                                       #
#########################################################################################################

class MeshDataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.mesh) and (rd.engine in cls.COMPAT_ENGINES)

obp = 'bpy.context.object.data'

onp = obp+'.name'
        
class Mesh_PT_exportOptions(bpy.types.Panel, MeshDataButtonsPanel):

    bl_label = 'Export Options'
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mesh = context.object.data
        row = layout.row()
        row.prop(mesh, "export_normals")
        row.prop(mesh, "primitive_type")
        row = layout.row(align=True)
        row.enabled = mesh.primitive_type == 'Points'
        row.prop_search(mesh, "size_vgroup", context.object, "vertex_groups", text="")
        row.prop(mesh, 'points_scale', text="")
        row = layout.row()        
        row.prop(mesh, "export_type")
        
        
##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      Camera Panels                                                                                    #
#                                                                                                       #
#########################################################################################################


class CameraDataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = "WINDOW"
    bl_context = "data"    
    bl_label=""

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.camera) and (rd.engine in cls.COMPAT_ENGINES)

class Camera_PT_dimensions(bpy.types.Panel, CameraDataButtonsPanel):
    bl_label = "Dimensions"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        camera = context.object
        cam = camera.data
        scene = context.scene
        layout = self.layout
        try:
            apass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
            return
        rc = camera.renderman_camera
        dimensions_layout(layout, camera)
        row = layout.row()
        row.prop(rc, "depthoffield", text="Depth Of Field")
        row = layout.row()
        row.enabled = rc.depthoffield
        cola = row.column(align=True)
        cola.prop(rc, "dof_distance", text="Focus Distance")
        cola.prop(rc, "fstop")
        cola.prop(rc, "use_lens_length")
        row = layout.row()
        row.enabled = rc.depthoffield and not rc.use_lens_length
        row.prop(rc, "focal_length")

        row = layout.row(align=True)
        row.prop(cam, "type", text="")

        row.prop(cam, "lens_unit", text = "")
        if cam.lens_unit == "MILLIMETERS":
            row.prop(cam, "lens", text="")
        else:
            row.prop(cam, "angle", text="")
            
        #row = layout.row()
        #col = row.column()
        #col.enabled = getactivepass(scene).motionblur
        #col.prop(camera.renderman[camera.renderman_index], "transformation_blur")
        #col.prop(camera.renderman[camera.renderman_index], "perspective_blur")
        #row = col.row()
        #transformation_blur = camera.renderman[camera.renderman_index].transformation_blur
        #row.enabled = transformation_blur
        #row.prop(camera.renderman[camera.renderman_index], "motion_samples")  
    

#class Renderman_PT_CameraLens(CameraDataButtonsPanel, bpy.types.Panel):
    #bl_label = "Renderman Lens Settings"
    #bl_idname = "rendermanlens"

    #COMPAT_ENGINES = {'RENDERMAN'}
    
    #def draw(self, context):
        #scene = context.scene
        ##maintain(scene)
        #camera = scene.camera
        #layout = self.layout

        #row = layout.row()
        #col = row.column(align=True)
        #col.prop(camera.data, "clip_start")
        #col.prop(camera.data, "clip_end")
        #col = row.column(align=True)
        #col.prop(camera.data, "shift_x")
        #col.prop(camera.data, "shift_y")


##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      Particle Panels                                                                                  #
#                                                                                                       #
#########################################################################################################

from bl_ui import properties_particle
class ParticleButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "particle"
    
    @classmethod
    def poll(cls, context):
        return properties_particle.particle_panel_poll(cls, context)


class Renderman_PT_Particle_Passes(bpy.types.Panel, ParticleButtonsPanel):
    bl_label = "Passes"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        obp = "bpy.context.particle_system"
        if eval(obp) == None:
            return

        passes_linking_layout("particle", obp+'.settings', self.layout, context.scene)     


class Renderman_PT_ParticleMBPanel(bpy.types.Panel, ParticleButtonsPanel):
    bl_label = "Motion Blur"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        psystem = context.particle_system
        if psystem == None:
            return

        try:
            rman =psystem.settings.renderman[psystem.settings.renderman_index]
        
            layout.prop(rman, "motion_blur")
            layout.prop(rman, "motion_samples")
        except IndexError:
            layout.label("No Pass")
                        
    
class Renderman_PT_ParticleRenderSettings(bpy.types.Panel, ParticleButtonsPanel):
    bl_label = "Render"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        try:
            active_pass = getactivepass(scene)
        except IndexError:
            layout.label("No Render Pass")
        shaders = context.scene.renderman_settings.shaders
        
        psystem = context.particle_system
        if psystem == None:
            return

        obj = context.object
        if psystem.settings.renderman:
            rman = psystem.settings.renderman[psystem.settings.renderman_index]
    
            row = layout.row()
            
            row.prop(rman, "material_slot")
                
            row.prop(rman, "render_type")
            if rman.render_type == "Object":
                psystem.settings.render_type = 'OBJECT'
                #if rman.object in scene.objects:
                #    psystem.settings.dupli_object = scene.objects[rman.object]
                #TODO: use callback layout.prop_search(rman, "object", scene, "objects") elif rman.render_type == "Archive":
                layout.prop(rman, "archive")
            elif rman.render_type == "Group":
                layout.prop_search(rman, "group", bpy.data, "groups")

            row = layout.row()
            row.prop(rman, "size_factor")
            row.prop(rman, "constant_size")

            layout.operator("renderman.add_particle_var")

            for i, var in enumerate(rman.export_vars):
                row = layout.row()
                row.prop(var, "name")
                row.prop(var, "path")
                row.operator("renderman.remove_particle_var").index = i

### Attributes
class Renderman_PT_particles_Attribute_Panel(bpy.types.Panel, ParticleButtonsPanel):
    bl_label = "Attributes"
    
    COMPAT_ENGINES = {'RENDERMAN'}
    
    def draw(self, context):
        path =  "bpy.context.particle_system.settings"
        rm = path+".renderman["+path+".renderman_index]"
        if context.object == None:
            return

        obj = context.object.name
        layout = self.layout
        scene = context.scene
        if context.particle_system:
            psystem = context.particle_system.name
            try:
                attribute_panel_layout("particles"+obj+psystem+eval(rm).name, rm, layout, scene)
            except IndexError:
                layout.label("No Pass")
            
            
            
class Renderman_PT_particles_Custom_code_Panel(bpy.types.Panel, ParticleButtonsPanel):
    bl_label = "Custom Code"
   
    COMPAT_ENGINES = {'RENDERMAN'}
   
    def draw(self, context):
        layout = self.layout
        psystem = context.particle_system
        if not psystem: return
        if psystem.settings.renderman:
            custom_code_layout("particles", context, layout)
        else:
            layout.label("No Render Pass")



##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      Empty Panels                                                                                     #
#                                                                                                       #
#########################################################################################################   


#class EmptyButtonsPanel():
#    bl_space_type = "PROPERTIES"
#    bl_region_type = "WINDOW"
#    bl_context = "Object"
#    
#    def poll(cls, context):
#        return 
#    def draw(self, context):
#        layout = self.layout
                                                              
    
##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      Text Editor Panels                                                                               #
#                                                                                                       #
#########################################################################################################


class Renderman_PT_RendermanShaderPanel(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "RSL"
    
    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return rd.engine == 'RENDERMAN'

    def draw(self, context):
        #maintain(context.scene)
        layout = self.layout
        layout.operator("text.compileshader")


##################################################################################################################################

#########################################################################################################
#                                                                                                       #
#      3D View                                                                                          #
#                                                                                                       #
#########################################################################################################
class Renderman_MT_remove_pass_selected(bpy.types.Menu):
    bl_label="remove Pass"
    
    def draw(self, context):
        matches = []
        for obj in context.selected_objects:
            if obj.type == "LAMP":
                rm = obj.data.renderman
            else:
                rm = obj.renderman
            for r in rm:
                dbprint("Menu:checking", r.name, lvl=2, grp="specials")
                matching = True
                for o in context.selected_objects:
                    if o.type == "LAMP":
                        if not r.name in o.data.renderman:
                            dbprint("Menu:", r.name, "not in lamps:", o.name,"passes", lvl=2, grp="specials")
                            matching = False
                    else:
                        if not r.name in o.renderman:
                            dbprint("Menu:", r.name, "not in objects:", o.name, "passes", lvl=2, grp="specials")
                            matching = False
                if matching and not r.name in matches:
                    matches.append(r.name)
        for m in matches:
            self.layout.operator("renderman.remove_pass_selected", text=m).name = m
            
class Renderman_MT_set_active_pass_selected(bpy.types.Menu):
    bl_label="set active Pass"
    
    def draw(self, context):
        matches = []
        for obj in context.selected_objects:
            if obj.type == "LAMP":
                rm = obj.data.renderman
            else:
                rm = obj.renderman
            for r in rm:
                dbprint("Menu:checking", r.name, lvl=2, grp="specials")
                matching = True
                for o in context.selected_objects:
                    if o.type == "LAMP":
                        if not r.name in o.data.renderman:
                            dbprint("Menu:", r.name, "not in lamps:", o.name,"passes", lvl=2, grp="specials")
                            matching = False
                    else:
                        if not r.name in o.renderman:
                            dbprint("Menu:", r.name, "not in objects:", o.name, "passes", lvl=2, grp="specials")
                            matching = False
                if matching and not r.name in matches:
                    matches.append(r.name)
        for m in matches:
            self.layout.operator("renderman.set_active_pass_selected", text=m).name = m
            
            
class Renderman_MT_link_pass_selected(bpy.types.Menu):
    bl_label = "link active to Render Pass"
    
    def draw(self, context):
        rm = context.scene.renderman_settings
        for p in rm.passes: 
            self.layout.operator("renderman.link_pass_selected", text=p.name).rpass = p.name

#class Renderman_MT_object_specials(bpy.types.Menu):
    #bl_label = "Renderman"
    
    #def draw(self, context):
        #attribute_menu('obj_selected', '', selected = True)
        #self.layout.menu("obj_selected_attribute_menu", text="Attributes")
        #self.layout.menu("Renderman_MT_LightLinking")
        #self.layout.operator("renderman.set_shading_rate_selected")
        #self.layout.menu("Renderman_MT_set_active_pass_selected")
        #self.layout.menu("Renderman_MT_link_pass_selected")
        #self.layout.operator("renderman.add_pass_selected")
        #self.layout.menu("Renderman_MT_remove_pass_selected")
        
class Renderman_MT_LightLinking(bpy.types.Menu):
    bl_label="Light Linking"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("renderman.light_linking", text = "Add").type = "add"
        layout.operator("renderman.light_linking", text = "Remove").type = "remove"
        layout.operator("renderman.light_linking", text = "Exclusive").type = "exclusive"        

def draw_obj_specials_rm_menu(self, context):
    #self.layout.menu("Renderman_MT_object_specials")
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.separator()
    self.layout.label("Renderman:")
    self.layout.operator("renderman.add_pass_selected")
    self.layout.menu("Renderman_MT_remove_pass_selected")
    self.layout.menu("Renderman_MT_link_pass_selected")
    self.layout.menu("Renderman_MT_set_active_pass_selected")

    self.layout.separator()
    attribute_menu('obj_selected', '', selected = True)
    self.layout.menu("obj_selected_attribute_menu", text="Attributes")
    self.layout.menu("Renderman_MT_LightLinking")
    self.layout.operator("renderman.set_shading_rate_selected")


class Renderman_MT_obj_selected_attributepresets(bpy.types.Menu):
    bl_label = "Load Attribute Preset"
    
    def draw(self, context):
        rmansettings = context.scene.renderman_settings
        target_path = os.path.join(bpy.utils.preset_paths("renderman")[0], rmansettings.active_engine)
        for preset in os.listdir(target_path):
            if preset.find(".preset") != -1:
                p = preset.replace(".preset", "")
                self.layout.operator("attribute.load_selected", text=p.replace("_", " ")).preset = p


class Renderman_MT_addRendermanLight(bpy.types.Menu):
    bl_label = "Renderman Light"

    def draw(self, context):
        scene = context.scene
        rm = scene.renderman_settings
        lcollection = rm.shaders.light_collection
        scollection = lcollection.keys()
        scollection.sort()
        self.layout.operator("renderman.refreshshaderlist", text="Refresh List")
        for sh in scollection:
            self.layout.operator("renderman.add_light", text=sh).shader = sh


def draw_rm_add_light(self, context):
    self.layout.menu("Renderman_MT_addRendermanLight")

