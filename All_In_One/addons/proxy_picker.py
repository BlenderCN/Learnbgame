bl_info = {
    "name": "Proxy picker",
    "author": "Max Hammond, lucky ",
    "version": (0, 2),
    "blender": (2, 7, 5),
    "location": "Properties Editor > Bone",
    "description": "Enables the proxy picker feature for the rig",     
    "category": "Learnbgame"
}


import bpy
from bpy.app.handlers import persistent



#check if bone is on an active layer
def bone_layer_active(b):
    ob = bpy.context.active_object
    active = False
    for i in range(32):
        if b.layers[i] == True and ob.data.layers[i] == True:
            active = True
            
    return active #return bool

#turn the "selected_pose_bones" into a list of names 
def bone_list(s):
    s = s[1:]
    s = s[:len(s)-1]
    list = s.split(", ")
    s_list = []
    for l in list:
        l = l[l.rfind("[\"")+2:]
        l = l[:l.rfind("\"]")]
        s_list.append(l)
    return s_list

#generate a list of all 32 bools
def bool_list(b_list):
    list = []
    for b in b_list:
        list.append(b)
    return list

#generate a fake string list from a real list
def string_list(list):
    s_list = ""
    i = 0
    for l in list:
        if i == 0:
            s_list = l
        else:
            s_list = s_list + "," + l
        i += 1
    return s_list
        
#the proxy picker mega function
@persistent
def proxy_picker(scene):
    
    ob = None
    try:
        ob = bpy.context.active_object
    except:
        pass
    if ob != None:
        if ob.mode == "POSE":
            if bpy.context.scene.Proxy_Picker.active == True:
                
                #only do stuff if what is selected has been changed
                if bpy.context.scene.Proxy_Picker.last_bones != str(bpy.context.selected_pose_bones) \
                or bpy.context.scene.Proxy_Picker.last_layers != str(bool_list(bpy.context.object.data.layers)):
                    
                    g_name = bpy.context.scene.Proxy_Picker.group #group name
                    
                    button = None # used to give button custom_shape a delay "hacky"
                    
                    #First we will check for button or layer press, and restor selection if true
                    if bpy.context.active_pose_bone is not None:
                        
                        bone = bpy.context.active_pose_bone
                        pbone = bpy.context.active_object.pose.bones[bone.name]
                        b = ob.data.bones[bone.name]
                        
                        #if a button is pressed
                        if pbone.get("button") is not None or pbone.get("layer") is not None: 

                            last = bpy.context.scene.Proxy_Picker.last_bones
                            pressed = pbone.name
                            ob.data.bones[b.name].select = False
                            ob.data.bones.active = None 
                            
                            #Restor selection
                            if last != "[]":
                                for s in bone_list(last):
                                    if s != pressed:
                                        ob.data.bones[s].select = True
                                for b in ob.data.bones:
                                    if b.select == True and b.get("button") is None:
                                        ob.data.bones.active = b
        
                            #run a script or do layers
                            if pbone.get("button") is not None:
                                button = pbone
                                exec(bpy.data.texts[pbone["button"]].as_string()) # this is not ideal, but it makes 
                                                                                  # it easier to add simple scripts 
                                                                                  # and edit them on the fly for
                                                                                  # more complex scripts create a 
                                                                                  # simple script:
                                                                                  # import my_complex_script
                                                                                  # my_complex_script.main()
                            else:
                                layer = bpy.context.object.data.layers[pbone.get("layer")]
                                if layer == False:
                                    bpy.context.object.data.layers[pbone.get("layer")] = True
                                else:
                                    bpy.context.object.data.layers[pbone.get("layer")] = False
                    
                    #Now check for proxy bones selected, not using active incase of border select or nested proxy "Bad"              
                    for b in ob.data.bones:  
                        pbone = ob.pose.bones[b.name]   
                            
                        if pbone.get("proxy") is not None or pbone.get("proxy_list") is not None:
                            #select the real bones if a proxy is selected 
                            if b.select == True:
                                
                                multi = False
                                if b != ob.data.bones.active:
                                    multi = True
                                
                                #First check for proxy's
                                if pbone.get("proxy") is not None:
                                    
                                    proxy_bone = ob.data.bones[b.name]
                                    proxy_bone.select = False
                                    
                                    bone = ob.data.bones[pbone.get("proxy")]
                                    
                                    if bone.select == False and bone_layer_active(bone) == True:
                                        bone.select = True
                                        ob.data.bones.active = bone
                                    elif multi != True:
                                        bone.select = False
                                        for bb in ob.data.bones:
                                            if bb.select == True:
                                                ob.data.bones.active = bb
                                                
                                #Now add any proxy_lists's              
                                if pbone.get("proxy_list") is not None:
                                    
                                    proxy_bone = ob.data.bones[b.name]
                                    proxy_bone.select = False
                                    
                                    list = pbone.get("proxy_list").split(",")
                                    
                                    some = False
                                    for l in list:
                                        if ob.data.bones[l].select == True:
                                            some = True
                                            
                                    all = True
                                    for l in list:
                                        if ob.data.bones[l].select == False:
                                            all = False
                                    
                                    for l in list:
                                        bone = ob.data.bones[l]
                                        
                                        if bone.select == False and bone_layer_active(bone) == True:
                                            bone.select = True
                                            ob.data.bones.active = bone
                                            
                                        elif multi == False and some == False \
                                        or multi == False and all == True:
                                            bone.select = False
                                            for bb in ob.data.bones:
                                                if bb.select == True:
                                                    ob.data.bones.active = bb
                                                    
                    #make sure nothing is selected that should not be ie buttons, proxies or stuff on hidden layers                               
                    for b in ob.data.bones:
                        pbone = ob.pose.bones[b.name]                                 
                        if bone_layer_active(b) == False:
                            b.select = False 
                        if pbone.get("proxy") is not None or pbone.get("proxy_list") is not None \
                        or pbone.get("button") is not None or pbone.get("layer") is not None: 
                            b.select = False 
                            
                    #Finnally we want to set the right custom_shape for every bone :D                               
                    for b in ob.data.bones:  
                        pbone = ob.pose.bones[b.name]  
                        
                        #check if it might need its custom_shape updating
                        if pbone.get("proxy") is not None or pbone.get("proxy_list") is not None \
                        or pbone.get("button") is not None or pbone.get("layer") is not None: 
                            
                            #find the custom_shapes that they should be
                            if pbone.get("select_shape") != "": 
                                if g_name != "":
                                    select_shape = bpy.data.groups[g_name].objects[pbone.get("select_shape")]
                                else:
                                    try:
                                        select_shape = bpy.context.scene.objects[pbone.get("select_shape")]
                                    except:
                                        select_shape = bpy.context.scene.objects[pbone.get("select_shape")+'.001']
                            else:
                                select_shape = None   
                                 
                            if pbone.get("normal_shape") != "":
                                if g_name != "":
                                    normal_shape = bpy.data.groups[g_name].objects[pbone.get("normal_shape")]
                                else:
                                    try:
                                        normal_shape = bpy.context.scene.objects[pbone.get("normal_shape")]
                                    except:
                                        normal_shape = bpy.context.scene.objects[pbone.get("normal_shape")+'.001']
                            else:
                                normal_shape = None
                                
                            #If its a button or layer check if an update is needed
                            if pbone.get("button") is not None or pbone.get("layer") is not None:
                                
                                if pbone.get("button") is not None:
                                    if pbone.custom_shape != normal_shape and button != pbone:
                                        pbone.custom_shape = normal_shape
                                    if button == pbone:
                                        pbone.custom_shape = select_shape #hacky, gives the button a 1 click feedback
                                        
                                else: #must be a layer
                                    layer = bpy.context.object.data.layers[pbone.get("layer")]
                                    if layer == False and pbone.custom_shape != normal_shape:
                                        pbone.custom_shape = normal_shape
                                    elif layer == True and pbone.custom_shape != select_shape:
                                        pbone.custom_shape = select_shape
                                
                            #Now set the proxy and proxy_list custom_shape's    
                            if pbone.get("proxy") is not None or pbone.get("proxy_list") is not None:  
                                #is it a proxy or list
                                proxy_list = False
                                all = True
                                if pbone.get("proxy_list") is not None:
                                    proxy_list = True
                                    blist = pbone.get("proxy_list").split(",")
                                    rb = ob.data.bones[blist[0]]
                                    for l in blist:
                                        if ob.data.bones[l].select == False:
                                            all = False
                                
                                #if its a proxy whats the target?
                                if proxy_list == False:
                                    rb = ob.data.bones[pbone.get("proxy")]
                                  
                                #Assign custom_shapes
                                if rb.select == True and pbone.custom_shape != select_shape and proxy_list == False \
                                or all == True and pbone.custom_shape != select_shape and proxy_list == True:
                                  
                                    pbone.custom_shape = select_shape
                                
                                if rb.select == False and pbone.custom_shape == select_shape and proxy_list == False \
                                or all != True and pbone.custom_shape == select_shape and proxy_list == True:
                                 
                                    pbone.custom_shape = normal_shape
                                                                       
    
                    #update list of selected bones for futer use
                    if button == None: #hacky, if its a button cause the handler to repeat everything 
                        bpy.context.scene.Proxy_Picker.last_layers = str(bool_list(bpy.context.object.data.layers))
                        bpy.context.scene.Proxy_Picker.last_bones = str(bpy.context.selected_pose_bones)
                    else:
                        bpy.context.scene.Proxy_Picker.last_layers = "_update_"
                        bpy.context.scene.Proxy_Picker.last_bones = "_update_"                                      
  
#Delete all the properties on this Bone that are to do with Proxy_picker                                          
class Delete_Proxy(bpy.types.Operator):
    """Remove Proxy Picker from this bone"""
    bl_idname = "pp.delete_proxy"
    bl_label = "Delete Proxy"

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone is not None

    def execute(self, context):
        bone = bpy.context.active_pose_bone
        pbone = bpy.context.active_object.pose.bones[bone.name]
        
        for p in pbone.keys():
            if p not in '_RNA_UI':
                if p == "button": 
                    del pbone[p]
                if p == "layer": 
                    del pbone[p]
                if p == "proxy": 
                    del pbone[p]
                if p == "proxy_list": 
                    del pbone[p]
                if p == "normal_shape": 
                    del pbone[p]
                if p == "select_shape": 
                    del pbone[p]
        return {'FINISHED'}  
     
#Make the bone a button    
class Add_Button(bpy.types.Operator):
    """Make this bone a button"""
    bl_idname = "pp.add_button"
    bl_label = "Add Button"
    
    mode = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone is not None

    def execute(self, context):
        bone = bpy.context.active_pose_bone
        pbone = bpy.context.active_object.pose.bones[bone.name]
        
        if self.mode == "button":
            bpy.types.PoseBone.button = bpy.props.StringProperty()
            pbone.button = ""
        elif self.mode == "layer":
            bpy.types.PoseBone.layer = bpy.props.IntProperty(min = 0, max = 31)
            pbone.layer = 0
             
        bpy.types.PoseBone.normal_shape = bpy.props.StringProperty()
        bpy.types.PoseBone.select_shape = bpy.props.StringProperty()

        n_shape = bpy.context.scene.Proxy_Picker.normal
        if pbone.get("custom_shape") is not None:
            if pbone.custom_shape.name != "":
                print("Test")
                n_shape = pbone.custom_shape.name

        s_shape = bpy.context.scene.Proxy_Picker.select
        if s_shape == "":
            s_shape = n_shape
  
        pbone.normal_shape = n_shape
        pbone.select_shape = s_shape
        
        return {'FINISHED'}  

#Auto make this bone a proxy from selection                               
class Auto_Proxy(bpy.types.Operator):
    """Make this bone a Proxy Picker"""
    bl_idname = "pp.auto_proxy"
    bl_label = "Auto Proxy"

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone is not None

    def execute(self, context):
        bone = bpy.context.active_pose_bone
        pbone = bpy.context.active_object.pose.bones[bone.name]
        ob = bpy.context.active_object

        blist = []
        list = False
        if len(bpy.context.selected_pose_bones) > 2:
            list = True
            
        for b in bpy.context.selected_pose_bones:
            if b != pbone:
                blist.append(b.name)

        if list == False:
            bpy.types.PoseBone.proxy = bpy.props.StringProperty()
            if len(blist) != 0:
                pbone.proxy = blist[0]
            else:
                pbone.proxy = ""

        else:
            bpy.types.PoseBone.proxy_list = bpy.props.StringProperty()
            pbone.proxy_list = string_list(blist)
        
        bpy.types.PoseBone.normal_shape = bpy.props.StringProperty()
        bpy.types.PoseBone.select_shape = bpy.props.StringProperty()

        n_shape = bpy.context.scene.Proxy_Picker.normal
        if pbone.get("custom_shape") is not None:
            if pbone.custom_shape.name != "":
                print("Test")
                n_shape = pbone.custom_shape.name
                
        if pbone.get("normal_shape") is not None:
            if pbone.normal_shape != "":
                n_shape = pbone.normal_shape

        s_shape = bpy.context.scene.Proxy_Picker.select
        if pbone.get("select_shape") is not None:
            if pbone.select_shape != "":
                s_shape = pbone.select_shape
        
        if s_shape == "":
            s_shape = n_shape
  
        pbone.normal_shape = n_shape
        pbone.select_shape = s_shape
        return {'FINISHED'}                                  

class Proxy_Picker(bpy.types.PropertyGroup):
    active = bpy.props.BoolProperty(default = True)
    group = bpy.props.StringProperty()
    normal = bpy.props.StringProperty()
    select = bpy.props.StringProperty()
    last_bones = bpy.props.StringProperty()
    last_layers = bpy.props.StringProperty()
    
                               
class Proxy_Maker(bpy.types.Panel):
    """Make a Proxy Picker"""
    bl_label = "Proxy Picker"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    
    @classmethod
    def poll(cls, context):
        scene = context.space_data
        ob = context.active_object
        return scene and ob and ob.type == 'ARMATURE' and ob.mode == 'POSE'

    def draw_header(self, context):

        self.layout.prop(bpy.context.scene.Proxy_Picker, "active", text="")
    
    def draw(self, context):
        
        bone = bpy.context.active_pose_bone
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="Linked Group Name:")
        row = layout.row(align=True)
        row.prop(bpy.context.scene.Proxy_Picker, "group", text="")
        row = layout.row(align=True)
        
        box = row.box()
        row = box.row()
        
        if bone is not None:
            pbone = bpy.context.active_object.pose.bones[bone.name]
            
            
            
            if pbone.get("proxy") is not None or pbone.get("proxy_list") is not None \
            or pbone.get("button") is not None or pbone.get("layer") is not None:
            
                if pbone.get("proxy") is not None: 
                    row.prop_search(bone, "[\"proxy\"]", context.armature, "bones", text="Pick Bone")
                    
                elif pbone.get("proxy_list") is not None:
                    row.prop(bone, "[\"proxy_list\"]", text="Pick Bone")
                    
                elif pbone.get("button") is not None:
                    row.prop_search(bone, "[\"button\"]", bpy.data, "texts", text="Pick Text")
                    
                elif pbone.get("layer") is not None:
                    row.prop(bone, "[\"layer\"]", text="Pick Layer")
                    
                row = layout.row(align=True)
                row = box.row()
                row.prop_search(bone, "[\"normal_shape\"]", bpy.context.scene, "objects", text="Normal Shape")
                row = layout.row(align=True)
                row = box.row()
                row.prop_search(bone, "[\"select_shape\"]", bpy.context.scene, "objects", text="Select Shape")
                row = layout.row(align=True)
                row = box.row()
                row.operator("pp.delete_proxy", text="Delete Proxy") 
                
            else:
                
                if bpy.context.scene.Proxy_Picker.active == True:
                    row.enabled = False
                row.operator("pp.auto_proxy", text="Add Proxy")
                row.operator("pp.add_button", text="Add Button").mode = "button"
                row.operator("pp.add_button", text="Add Layer").mode = "layer"
                row = layout.row(align=True)
                row = box.row()
                row.prop_search(bpy.context.scene.Proxy_Picker, "normal", bpy.context.scene, "objects", text="Normal Shape")
                row = layout.row(align=True)
                row = box.row()
                row.prop_search(bpy.context.scene.Proxy_Picker, "select", bpy.context.scene, "objects", text="Select Shape")
  
#hack to make custom shapes display the right color             
def custom_shape_hack():
    foo = "bar"
    
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.Proxy_Picker = bpy.props.PointerProperty(type=Proxy_Picker)    
    bpy.app.handlers.scene_update_pre.append(proxy_picker)

def unregister():
    bpy.utils.unregister_module(__name__)
    if bpy.context.scene.get("proxy_picker") is not None:
        del bpy.context.scene.proxy_picker
   
    bpy.app.handlers.scene_update_pre.remove(proxy_picker)
    
if __name__ == "__main__":
    register()