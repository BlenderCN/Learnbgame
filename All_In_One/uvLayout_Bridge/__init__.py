bl_info = {
    "name": "Blender2headusUVLayout",
    "author": "Titus Lavrov / HardSurface - Environment artist",
    "version": (0, 5),
    "blender": (2, 79, 0),
    "location": "3D VIEW > TOOLS > uvLayout bridge panel ",
    "description": "Blender to headus UVLayout v2 - bridge for UVs Unwrapping",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://blenderartists.org/forum/showthread.php?441849-Add-on-Blender-lt-gt-UVLayout-bridge",
    "category": "UV"
}

import bpy 
import os
import os.path
import subprocess
import tempfile 
import time 
from sys import platform

from bpy.props import *
from bpy.types import Operator, AddonPreferences, Menu
 
#---Headus uvLayout Export/Import---
def UVL_IO(): 
    
    #---Variables---    
     
    UVLayoutPath = bpy.context.user_preferences.addons[__name__].preferences.filepath  
    
    path = "" + tempfile.gettempdir()
    path = '/'.join(path.split('\\'))
    
    file_Name = "Blender2UVLayout_TMP.obj"
    file_outName = "Blender2UVLayout_TMP.out"
    file_cmdName = "Blender2UVLayout_TMP.cmd"
    uvl_exit_str = "exit"     
       
    expObjs = []
    expMeshes = []
    uvlObjs = []
    Objs = []
    
    #--Get selected objects---
    #---Lists buildUP--- 
    if len(bpy.context.selected_objects) == 0:
        bpy.ops.uvlb.zero_sel()

    elif len(bpy.context.selected_objects) != 0 and bpy.context.scene.uvlb_obj_sel == True:
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                #---Check for UV channels---
                if len(ob.data.uv_textures) < bpy.context.scene.uvlb_uv_channel:                
                    for n in range(bpy.context.scene.uvlb_uv_channel - len(ob.data.uv_textures)):
                        ob.data.uv_textures.new()
                #---Check if Apply modifier is on---
                if bpy.context.scene.uvlb_obj_mod == True:
                    if len(ob.modifiers) != 0:
                        bpy.context.scene.objects.active = bpy.data.objects[ob.name] 
                        for m in ob.modifiers :                                       
                            bpy.ops.object.modifier_apply(apply_as='DATA', modifier = m.name)
                #---Setup uv index and collect Objs---
                ob.data.uv_textures.active_index = (bpy.context.scene.uvlb_uv_channel - 1)
                Objs.append(ob)
    
    elif bpy.context.scene.uvlb_obj_sel == False and len(bpy.context.scene.objects) != 0:
        for ob in bpy.context.scene.objects:
            if ob.type == 'MESH':
                #---Check for UV channels---
                if len(ob.data.uv_textures) < bpy.context.scene.uvlb_uv_channel:                
                    for n in range(bpy.context.scene.uvlb_uv_channel - len(ob.data.uv_textures)):
                        ob.data.uv_textures.new()
                #---Check if Apply modifier is on---
                if bpy.context.scene.uvlb_obj_mod == True:
                    if len(ob.modifiers) != 0:
                        bpy.context.scene.objects.active = bpy.data.objects[ob.name]
                        for m in ob.modifiers :                                         
                            bpy.ops.object.modifier_apply(apply_as='DATA', modifier = m.name)
                #---Setup uv index and collect Objs---                   
                ob.data.uv_textures.active_index = (bpy.context.scene.uvlb_uv_channel - 1)
                Objs.append(ob)
    
    
    if len(Objs) != 0:   
        #---Create and prepare objects for export---
        for ob in Objs:
            if ob.layers_local_view[0] == True:                
                bpy.ops.view3d.localview()                   
                newObj = ob.copy()
                newObj.data = ob.data.copy()
                newObj.animation_data_clear()
                newObj.name = ob.name + "__UVL"
                bpy.context.scene.objects.link(newObj)    
                expObjs.append(newObj)              
                expMeshes.append(newObj.data)
            else:
                newObj = ob.copy()
                newObj.data = ob.data.copy()
                newObj.animation_data_clear()
                newObj.name = ob.name + "__UVL"
                bpy.context.scene.objects.link(newObj)    
                expObjs.append(newObj)              
                expMeshes.append(newObj.data)                
                           
                  #---Texture channels cleanup exept uvlb_uv_channel 
        for ob in expMeshes:                       
            active_index = (bpy.context.scene.uvlb_uv_channel - 1)
            texName=ob.uv_textures[active_index].name 
            uv_textures = ob.uv_textures
            ObjTexs=[]
            for t in uv_textures:
                ObjTexs.append(t.name)    
            for u in ObjTexs:
                if u != texName:                                                    
                    uv_textures.remove(uv_textures[u])
                
        #---Select objects for EXPORT
        bpy.ops.object.select_all(action='DESELECT')     
        for ob in expObjs:
            bpy.data.objects[ob.name].select = True           
                
              
        #---EXPORT---    
        bpy.ops.export_scene.obj(filepath=path + file_Name, 
                                    check_existing = True,
                                    axis_forward = '-Z',
                                    axis_up = 'Y',
                                    filter_glob = "*.obj;*.mtl",
                                    use_selection = True,
                                    use_animation = False, 
                                    use_mesh_modifiers = False, 
                                    use_mesh_modifiers_render = False, 
                                    use_edges = False, 
                                    use_smooth_groups = False, 
                                    use_smooth_groups_bitflags = False, 
                                    use_normals = True, 
                                    use_uvs = True, 
                                    use_materials = False, 
                                    use_triangles = False, 
                                    use_nurbs = False, 
                                    use_vertex_groups = True, 
                                    use_blen_objects = False, 
                                    group_by_object = True, 
                                    group_by_material = False, 
                                    keep_vertex_order = True, 
                                    global_scale = 1, 
                                    path_mode = 'AUTO')   
        
        #---OBJs Clean up and deselect before import
        for ob in expMeshes:        
            bpy.data.meshes.remove(ob,True)
        
        bpy.ops.object.select_all(action='DESELECT')
        
        #-Set uvLayout mode
        if (bpy.context.scene.uvlb_mode == '0'):
            uvlb_mode = 'Poly'
        if (bpy.context.scene.uvlb_mode == '1'):
            uvlb_mode = 'SUBD'              
        #-Set UVs mode
        if (bpy.context.scene.uvlb_uv_mode == '0'):
            uvlb_uv_mode = 'New'
        if (bpy.context.scene.uvlb_uv_mode == '1'):
            uvlb_uv_mode = 'Edit' 
               
        #---OS---
        if platform == "darwin":
            l = os.listdir(UVLayoutPath)
            appName = (str(l).strip("[]")).strip("'")
            uvlayout_proc = subprocess.Popen([UVLayoutPath + appName, '-plugin,' + uvlb_mode + ',' + uvlb_uv_mode, path + file_Name])
        elif platform == "win32":
            uvlayout_proc = subprocess.Popen([UVLayoutPath + 'uvlayout.exe', '-plugin,' + uvlb_mode + ',' + uvlb_uv_mode, path + file_Name])
        
        #---IMPORT---
        while not os.path.isfile(path + file_outName) and uvlayout_proc.poll() != 0:         
            time.sleep(0.5)
            #---Import OBJ---
            if os.path.isfile(path + file_outName) == True:            
                bpy.ops.import_scene.obj(filepath = path + file_outName, 
                                        axis_forward = '-Z', 
                                        axis_up = 'Y', 
                                        filter_glob = "*.obj;*.mtl", 
                                        use_edges = False, 
                                        use_smooth_groups = False, 
                                        use_split_objects = True, 
                                        use_split_groups = True, 
                                        use_groups_as_vgroups = True, 
                                        use_image_search = False, 
                                        split_mode = 'ON', 
                                        global_clamp_size = 0);
                                        
                #---Close UVLAYOUT ---
                f = open(path + file_cmdName, "w+")
                f.write(''.join([uvl_exit_str]))
                f.close()
                
                #---Transfer UVs and CleanUP---
                for ob in bpy.context.selected_objects:
                    uvlObjs.append(ob)
                
                bpy.ops.object.select_all(action='DESELECT') 
                    
                for ob in uvlObjs:
                    #---Get source object name
                    refName=ob.name.split('__UVL')                
                    #---Select source object---                
                    bpy.data.objects[refName[0]].select = True
                    #---Select UVL object
                    bpy.context.scene.objects.active = bpy.data.objects[ob.name]
                    #---Transfer UVs from UVL object to Source object
                    bpy.ops.object.join_uvs()                
                    bpy.ops.object.select_all(action='DESELECT')
                        
                bpy.ops.object.select_all(action='DESELECT')    
            
                for ob in Objs:
                    bpy.context.scene.objects.active = bpy.data.objects[ob.name]
                    bpy.data.objects[ob.name].select = True
                         
                for ob in uvlObjs:         
                    bpy.data.meshes.remove(ob.data,True)
    
    elif len(Objs) == 0:
        bpy.ops.uvlb.zero_sel()            
        
#---UVLayout bridge Settings---

def UVLB_PROPS():
    #---UV Channel selector---
    bpy.types.Scene.uvlb_uv_channel = IntProperty \
			(
			name = "UV channel",
			description = "select a UV channel for editing",
			default = 1,
			min = 1,
			max = 8,
		    )
    #---UVLayout Mode selection---  
    bpy.types.Scene.uvlb_mode = EnumProperty \
            (
            name = "Mode",
            description = "POLY or SUBD",            
            items = [('0', "Poly",'Open as polymesh surface.','OUTLINER_DATA_MESH',0),
                   ('1', "SUBD",'Open as subdivision surface.','MOD_SUBSURF',1),                   
                   ],
            default = '0',            
            )
    #---UVLayout UV Mode selection---        
    bpy.types.Scene.uvlb_uv_mode = EnumProperty \
            (
            name = "UV",
            description="New or Edit",            
            items = [('0', "New", 'Create new UV','TEXTURE_DATA',0),
                   ('1', "Edit", 'Edit current UV','TEXTURE_SHADED',1),                   
                   ],
            default = '0',            
            )
    #---Obj export settings: Selected only---        
    bpy.types.Scene.uvlb_obj_sel = BoolProperty \
            (
            name="Selected objects",
            description = "When enabled:Only send the selected objects. When disabled: Send all scene objects. Minimum one object should be selected.",
            default = True       
            )
    #---Obj export settings: Selected only---        
    bpy.types.Scene.uvlb_obj_mod = BoolProperty \
            (
            name="Apply modifier(s)",
            description="Apply all modifiers. So after UVLayout objects will be without modifiers, be careful.",
            default = False        
            )
     
#---UVLayout Bridge UI---
class BL2UVL(bpy.types.Operator):
    """Blender to UVLayout"""
    bl_idname = "uvlb.io"
    bl_label = "uvLayout Bridge"  

    def execute(self, context):        
        UVL_IO()
        self.report ({'INFO'}, 'UVLayout bridge - Done!')              
        return {'FINISHED'}

class BL2UVL_SEL_ZERO(bpy.types.Operator):
    """Blender to UVLayout checker"""
    bl_idname = "uvlb.zero_sel"
    bl_label = "uvLayout Bridge"  

    def execute(self, context):               
        self.report ({'INFO'}, 'Selection is empty! Please select objects! or Scene is empty!')              
        return {'FINISHED'}

class UVLBridge_Panel (bpy.types.Panel):
    """Creates a UVLayout bridge Panel"""
    bl_label = "UVLayout bridge"
    bl_idname = "UVLBridge"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "uvLayout Bridge"
    bl_context = "objectmode"        
    
    @classmethod
    def poll(cls, context):
        # Only allow in Object mode and for a selected mesh.        
        return (context.object is not None and context.object.type == "MESH")
    
    def draw(self, context):
        layout = self.layout        
        scn = bpy.context.scene 
        #---Settings---
        settingsBox = layout.box()
        settingsBox.label("Object Settings:")                
        objExpSettingsCol = settingsBox .column(True)
        objExpSettingsCol.prop(scn, "uvlb_obj_sel")
        objExpSettingsCol.prop(scn, "uvlb_obj_mod")
        
        settingsBox.label("UVLayout Settings:")
        uvlbMode = settingsBox.column(True)
        uvlbMode.prop(scn, "uvlb_mode")
        uvlbUVMode = settingsBox.column(True)
        uvlbUVMode.prop(scn, "uvlb_uv_mode")
        
        #---UV Maps---
        uvMapBox = layout.box()        
        uvMapChannel = uvMapBox.row(align = True)
        uvMapChannel.prop(scn, "uvlb_uv_channel")
                
        #---Send button--- 
        sendButton = layout.row()
        sendButton.scale_y = 2.0
        sendButton.operator(BL2UVL.bl_idname, text = "Send to UVLayout", icon = 'POSE_HLT')

#class UVLBridge_ExportSettings_Panel(bpy.types.Panel):
#    """Creates a UVLayout bridge Panel"""
#    bl_label = "Export settings"
#    #bl_idname = "UVLBridge"
#    bl_space_type = 'VIEW_3D'
#    bl_region_type = 'TOOLS'
#    bl_category = "uvLayout Bridge"
#    bl_context = "objectmode"
#    bl_options = {'DEFAULT_CLOSED'}
#    
#    @classmethod
#    def poll(cls, context):
#        # Only allow in Object mode and for a selected mesh.        
#        return (context.object is not None and context.object.type == "MESH")
#    
#    def draw(self, context):
#        layout = self.layout        
#        scn = bpy.context.scene
#    #---Export settings---
#        exportSettings = layout.box()        
#        objExpSettingsCol = exportSettings.column(True)
#        objExpSettingsCol.prop(scn, "uvlb_obj_sel")
#        objExpSettingsCol.prop(scn, "uvlb_obj_mod")  

#---Pie Menu    
class UVLBridge_menu (bpy.types.Menu):
    """Creates a UVLayout simple menu"""
    bl_idname = "UVLBridge_menu"
    bl_label = "UVLayout bridge menu"
    
   
    @classmethod
    def poll(cls, context):
        # Only allow in Object mode and for a selected mesh.        
        return (context.object is not None and context.object.type == "MESH")
    
    def draw(self, context):
        
        layout = self.layout        
        scn = bpy.context.scene
         
        layout.operator(scn, "uvlb_uv_channel")
        layout.operator(BL2UVL.bl_idname, text = "Send to UVLayout", icon = 'POSE_HLT')
        
        
        
#---Addon Prefs---
class Blender2UVLayoutAddonPreferences(AddonPreferences):
    bl_idname = __name__

    filepath = StringProperty \
            (
            name = "Path:",
            subtype = 'DIR_PATH',
        )

    def draw(self, context):
        layout = self.layout
        layout.label(text = "Set the path to the Headus UVLayout v2.")
        layout.prop(self, "filepath")


class OBJECT_OT_b2uvl_addon_prefs(Operator):
    bl_idname = "object.b2uvl_addon_prefs"
    bl_label = "Addon Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        info = ("Path: %s" % (addon_prefs.filepath))

        self.report({'INFO'}, info)
        print(info)
        
        return {'FINISHED'}


    

addon_keymaps = []
             
def register():
    UVLB_PROPS()
#    bpy.utils.register_class(BL2UVL)
#    bpy.utils.register_class(UVLBridge_Panel)
#    bpy.utils.register_class(UVLBridge_menu)
    bpy.utils.register_module(__name__)
    #---handle the keymap---
#    wm = bpy.context.window_manager
#    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='VIEW_3D')
#    kmi = km.keymap_items.new(UVLBridge_menu.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
#    kmi.properties.total = 4
#    addon_keymaps.append(km)    

def unregister():
#    bpy.utils.unregister_class(BL2UVL)
#    bpy.utils.unregister_class(UVLBridge_Panel)
#    bpy.utils.unregister_class(UVLBridge_menu)
    bpy.utils.unregister_module(__name__)
    
    #---handle the keymap---
#    wm = bpy.context.window_manager
#    for km in addon_keymaps:
#        wm.keyconfigs.addon.keymaps.remove(km)
#    # clear the list
#    del addon_keymaps[:]
    

if __name__ == "__main__":
    register()
    
    