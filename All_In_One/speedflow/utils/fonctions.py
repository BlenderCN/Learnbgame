import bpy
import os
from bpy_extras import view3d_utils


def get_addon_preferences():
    addon_name = os.path.basename(os.path.dirname(os.path.abspath(__file__).split("utils")[0]))
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[addon_name].preferences 
    
    return addon_prefs

    
def add_smooth(): 
    bpy.ops.object.shade_smooth()
    bpy.context.object.data.use_auto_smooth = True
    bpy.context.object.data.auto_smooth_angle = 1.0472
    

def add_edge_bevel_weight():
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
    bpy.ops.transform.edge_bevelweight(value=1)
    bpy.ops.mesh.select_all(action='DESELECT')


def clean_mesh():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.select_all(action='DESELECT')
    
    
def prepare_bool_apply(act_obj, bool_obj, bool_bevel):
    bpy.context.scene.objects.active = bool_obj
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Bevel')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    if bool_bevel:
        bpy.ops.transform.edge_bevelweight(value=-1)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = act_obj
    

def apply_boolean(self, act_obj, bool_obj, bool_count):
    MPM = bpy.context.window_manager.MPM
    bool_bevel = False
    for mod in bool_obj.modifiers:
        if mod.type == 'BEVEL':
            bool_bevel = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    if bool_count > 1:
        prev_bool_obj = bpy.context.active_object.modifiers[MPM.boolean_name].object
        prepare_bool_apply(act_obj, bool_obj, bool_bevel)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=MPM.boolean_name)
        MPM.boolean_name = get_modifier_list(bpy.context.active_object, 'BOOLEAN')[-1]
        new_bool_obj = bpy.context.active_object.modifiers[MPM.boolean_name].object
        prev_bool_obj.select=False
        new_bool_obj.select=True
        update_bevel(act_obj, bool_bevel)
        clean_mesh()
        bpy.ops.object.mode_set(mode=self.mode)
     
    else:
        prepare_bool_apply(act_obj, bool_obj, bool_bevel)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=MPM.boolean_name)
        MPM.boolean_enabled = False
        update_bevel(act_obj, bool_bevel)
        clean_mesh()
        bpy.ops.object.mode_set(mode=self.mode)
        bool_obj.select=False
        if bool_obj.name.startswith("BB_"):
            bool_obj.hide=True
        
    

def prepare_reverse_bool(self, act_obj, bool_obj, bool_count):
    MPM = bpy.context.window_manager.MPM
    bpy.ops.object.select_all(action='DESELECT')
    act_obj.select=True
    bpy.ops.object.duplicate_move()
    rev_bool = bpy.context.active_object
    rev_bool.modifiers[MPM.boolean_name].operation = 'INTERSECT'
    for mod in rev_bool.modifiers:
        if mod.type == 'BOOLEAN' and mod.name != MPM.boolean_name:
            bpy.ops.object.modifier_remove(modifier=mod.name)
            
    bpy.ops.object.select_all(action='DESELECT')

    apply_boolean(self, rev_bool, bool_obj, 1)
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
    bpy.ops.transform.edge_bevelweight(value=1)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    bpy.context.scene.objects.active = act_obj
    act_obj.select=True
    apply_boolean(self, act_obj, bool_obj, bool_count)
    
    
        
def update_bevel(act_obj, bool_bevel):
    act_bevel=False
    for mod in act_obj.modifiers:
        if mod.type == 'BEVEL':
            act_bevel=True
    if act_bevel:
        modifier = act_obj.modifiers["Bevel"]
        if modifier.segments == 2 and modifier.profile == 1.0:
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.region_to_loop()
            bpy.ops.transform.edge_bevelweight(value=1)
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        else:
            # clear
#            bpy.ops.object.mode_set(mode = 'EDIT')
#            bpy.ops.mesh.select_all(action='SELECT')
#            bpy.ops.mesh.mark_sharp(clear=True)
#            bpy.ops.transform.edge_crease(value=-1)
#            bpy.ops.transform.edge_bevelweight(value=-1)
#            bpy.ops.mesh.select_all(action='DESELECT')
            
            # refresh
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
            bpy.ops.mesh.mark_sharp()
            bpy.ops.transform.edge_crease(value=1)
            bpy.ops.transform.edge_bevelweight(value=1)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode="OBJECT")
            
        add_smooth()
            

def get_modifier_list(obj, mod_type):
    mod_name = []
    
    for mod in obj.modifiers:
        if mod.type == mod_type:
            mod_name.append(mod.name)
    
    return mod_name