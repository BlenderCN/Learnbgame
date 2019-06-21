bl_info = {
    "name": "Proxy picker",
    "author": "Max Hammond, artell ",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "location": "Properties Editor > Bone",
    "description": "Enables the proxy picker feature for the rig",     
    "category": "Animation"}


import bpy
from bpy.app.handlers import persistent
from mathutils import *



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
    
@persistent
def proxy_picker(scene):
    
	ob = None
	try:
		ob = bpy.context.active_object
	except:
		pass
		
	# loop
	if ob != None:
		if ob.mode == "POSE":
			if bpy.context.scene.Proxy_Picker.active == True:
		
				#only do stuff if what is selected has been changed
				if bpy.context.scene.Proxy_Picker.last_bones != str(bpy.context.selected_pose_bones) or bpy.context.scene.Proxy_Picker.last_layers != str(bool_list(bpy.context.object.data.layers)):
					
					g_name = bpy.context.scene.Proxy_Picker.group 
					
					button = None
					
					#First we will check for button or layer press, and restor selection if true
					if bpy.context.active_pose_bone:
						
						bone = bpy.context.active_pose_bone
						pbone = bpy.context.active_object.pose.bones[bone.name]
						b = ob.data.bones[bone.name]
						
						#if a button is pressed
						if pbone.get("button") or pbone.get("layer") != None: 

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
							if pbone.get("button"):
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
							
						if pbone.get("proxy") or pbone.get("proxy_list"):
							#select the real bones if a proxy is selected 
							if b.select:
								
								multi = False
								if b != ob.data.bones.active:
									multi = True
								
								#First check for proxy's
								if pbone.get("proxy"):
									
									proxy_bone = ob.data.bones[b.name]
									proxy_bone.select = False                   
				  
									bname = pbone.get("proxy")
									if ob.data.bones.get(bname):
										bone = ob.data.bones[bname]
									
										if bone.select == False and bone_layer_active(bone) == True:
											bone.select = True
											ob.data.bones.active = bone
										elif multi != True:
											bone.select = False
											for bb in ob.data.bones:
												if bb.select == True:
													ob.data.bones.active = bb
												
								#Now add any proxy_lists's              
								if pbone.get("proxy_list"):
									
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
													
					# Make sure nothing is selected that should not be ie buttons, proxies or stuff on hidden layers                                  
					for b in ob.data.bones:
						pbone = ob.pose.bones[b.name]                                 
						if bone_layer_active(b) == False:
							b.select = False 
						if pbone.get("proxy") or pbone.get("proxy_list") \
						or pbone.get("button") or pbone.get("layer") != None: 
							b.select = False 
							
					 # Finally set the bones group color to highlight selected          
					for b in ob.data.bones:  
						pbone = ob.pose.bones[b.name]  
						
						#check if the bone group must be updated          
						if pbone.get("proxy") or pbone.get("proxy_list") or pbone.get("button") or pbone.get("layer") != None: 
							
							#find the bone group color highlighted
							if pbone.bone_group:
								name_split = pbone.bone_group.name.split('_')
								group_normal_color = None
								group_select_color = None
								if name_split[len(name_split)-1] != "sel":
									group_normal_color = pbone.bone_group
								else:
									group_normal_color = ob.pose.bone_groups.get(pbone.bone_group.name[:-4])
									
								group_select_color = ob.pose.bone_groups.get(group_normal_color.name + "_sel")
								
								if not group_select_color:
									group_select_color = ob.pose.bone_groups.new(name=group_normal_color.name + "_sel")
									group_select_color.colors.normal = group_normal_color.colors.normal 
									group_select_color.colors.select = group_normal_color.colors.select
									group_select_color.colors.active = group_normal_color.colors.active
									for i in range(0,3):
										group_select_color.colors.normal[i] += 0.3
										group_select_color.colors.select[i] += 0.3
										group_select_color.colors.active[i] += 0.3
										
									group_select_color.color_set = 'CUSTOM'
									print("Created bone group", group_select_color.name)
								
														
								#If its a button or layer check if an update is needed
								if pbone.get("button") or pbone.get("layer") != None:                                       
									if pbone.get("button"):
										if pbone.bone_group != group_normal_color and button != pbone:
											pbone.bone_group = group_normal_color
										if button == pbone:
											pbone.bone_group = group_select_color
											
									else: #must be a layer
										layer = bpy.context.object.data.layers[pbone.get("layer")]
										if layer == False and pbone.bone_group != group_normal_color:
											pbone.bone_group = group_normal_color
										elif layer == True and pbone.bone_group != group_select_color:
											pbone.bone_group = group_select_color
								
							# Now set the proxy and proxy_list groups
							rb = None
							if pbone.get("proxy") or pbone.get("proxy_list"):  
								#is it a proxy or list
								proxy_list = False
								all = True
								if pbone.get("proxy_list"):
									proxy_list = True
									blist = pbone.get("proxy_list").split(",")
									rb = ob.data.bones[blist[0]]
									for l in blist:
										if ob.data.bones[l].select == False:
											all = False
								
								#if its a proxy whats the target?                                   
								if proxy_list == False:                  
									if ob.pose.bones.get(pbone.get("proxy")):
										rb = ob.data.bones[pbone.get("proxy")]                                          
									else:
										rb = None                                           
								  
								#Assign color groups
								if rb:
									if rb.select and pbone.bone_group != group_select_color and proxy_list == False \
									or all == True and pbone.bone_group != group_select_color and proxy_list == True:                               
										pbone.bone_group = group_select_color                                           
									
									if rb.select == False and pbone.bone_group == group_select_color and proxy_list == False \
									or all != True and pbone.bone_group == group_select_color and proxy_list == True:
									 
										pbone.bone_group = group_normal_color
																	   

					#update list of selected bones for futer use
					if button == None: #hacky, if its a button cause the handler to repeat everything 
						bpy.context.scene.Proxy_Picker.last_layers = str(bool_list(bpy.context.object.data.layers))
						bpy.context.scene.Proxy_Picker.last_bones = str(bpy.context.selected_pose_bones)
					else:
						bpy.context.scene.Proxy_Picker.last_layers = "_update_"
						bpy.context.scene.Proxy_Picker.last_bones = "_update_"       
						
    
     

        

    
            
#Delete all the properties on this Bone that are to do with Proxy_picker                                          
class PP_OT_delete_proxy(bpy.types.Operator):
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
                #if p == "normal_shape": 
                #    del pbone[p]
                #if p == "select_shape": 
                #    del pbone[p]
        return {'FINISHED'}  
     
#Make the bone a button    
class PP_OT_add_button(bpy.types.Operator):
    """Make this bone a button"""
    bl_idname = "pp.add_button"
    bl_label = "Add Button"
    
    mode : bpy.props.StringProperty()

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
             
        #bpy.types.PoseBone.normal_shape = bpy.props.StringProperty()
        #bpy.types.PoseBone.select_shape = bpy.props.StringProperty()

    
        return {'FINISHED'}  

#Auto make this bone a proxy from selection                               
class PP_OT_auto_proxy(bpy.types.Operator):
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
        
        #bpy.types.PoseBone.normal_shape = bpy.props.StringProperty()
        #bpy.types.PoseBone.select_shape = bpy.props.StringProperty()
           

     
        return {'FINISHED'}                                  

class Proxy_Picker(bpy.types.PropertyGroup):
    active : bpy.props.BoolProperty(default = True)
    group : bpy.props.StringProperty()
    normal : bpy.props.StringProperty()
    select : bpy.props.StringProperty()
    last_bones : bpy.props.StringProperty()
    last_layers : bpy.props.StringProperty()
    
                               
class PP_PT_proxy_maker(bpy.types.Panel):
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
            
            
            
            if pbone.get("proxy") or pbone.get("proxy_list") or pbone.get("button") or pbone.get("layer") != None:
            
                if pbone.get("proxy"): 
                    row.prop_search(bone, "[\"proxy\"]", context.armature, "bones", text="Pick Bone")
                    
                elif pbone.get("proxy_list"):
                    row.prop(bone, "[\"proxy_list\"]", text="Pick Bone")
                    
                elif pbone.get("button"):
                    row.prop_search(bone, "[\"button\"]", bpy.data, "texts", text="Pick Text")
                    
                elif pbone.get("layer") != None:
                    row.prop(bone, "[\"layer\"]", text="Pick Layer")
                    
                row = layout.row(align=True)
                row = box.row()
                #row.prop_search(bone, "[\"normal_shape\"]", bpy.context.scene, "objects", text="Normal Shape")
                row = layout.row(align=True)
                row = box.row()
                #row.prop_search(bone, "[\"select_shape\"]", bpy.context.scene, "objects", text="Select Shape")
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
                #row.prop_search(bpy.context.scene.Proxy_Picker, "normal", bpy.context.scene, "objects", text="Normal Shape")
                row = layout.row(align=True)
                row = box.row()
                #row.prop_search(bpy.context.scene.Proxy_Picker, "select", bpy.context.scene, "objects", text="Select Shape")
  
  

  
classes = (PP_OT_delete_proxy, PP_OT_add_button, PP_OT_auto_proxy, PP_PT_proxy_maker, Proxy_Picker)

    
def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls) 
        
    bpy.types.Scene.Proxy_Picker = bpy.props.PointerProperty(type=Proxy_Picker)   
    #bpy.types.Scene.pp_modal_started = bpy.props.BoolProperty(name="Picker started", default=False, options={'SKIP_SAVE'})

    bpy.app.handlers.depsgraph_update_pre.append(proxy_picker)
    
    

def unregister():
    from bpy.utils import unregister_class
    
    for cls in reversed(classes):
        unregister_class(cls)   
    
    del bpy.types.Scene.Proxy_Picker
    #del bpy.types.Scene.pp_modal_started
    if bpy.context.scene.get("proxy_picker") is not None:
        del bpy.context.scene.proxy_picker
        
    bpy.app.handlers.depsgraph_update_pre.remove(proxy_picker)  
    
if __name__ == "__main__":
    register()