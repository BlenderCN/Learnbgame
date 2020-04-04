bl_info = {
    "name": "Create Deform Armature from Rig",
    "author": "Tal Hershkovich, Ferran MClar",
    "version" : (0, 3),
    "blender" : (2, 76, 0),
    "location": "Create Deform Armature from Rig in spacebar menu + Bake Actions",
    "description": "copies the deform bones of a rig into a deform armature with Copy Transforms Constraints applied. It also has an operator to bake all the actions into such (or any) armature",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Rigging/DeformArmature",
    "category": "Learnbgame",
}
      
import bpy
from bpy.app.handlers import persistent
   
#updates the action from the action editor's tab onto the ui list 
def action_updated(context):
    ob = bpy.context.object
    action_index = bpy.data.actions.find(ob.animation_data.action.name)
    if action_index != ob.action_list_index:
        #print("action changed")
        ob.action_list_index = action_index       
              
#select the new action when there is a new selection in the ui list and go to the first frame
def update_action_list(self, context):
    ob = bpy.context.object
    ob.animation_data.action = bpy.data.actions[ob.action_list_index]
    bpy.context.scene.frame_current = 1
    
def create_deform_armature(self, context):
    rig = bpy.context.active_object

    if rig.type == "ARMATURE":
        #create a duplicate
        bpy.ops.object.mode_set(mode='OBJECT')
        origin_name = rig.name
        bpy.ops.object.duplicate()
        bpy.context.active_object.name = origin_name+"_deform"
        rig_deform = bpy.context.object
        
        rig_deform.name = origin_name+"_deform" #"Armature_deform"
        rig_deform.data.name = origin_name+"_deform" #"Armature_deform"
        
        remove_bones = []
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.layers_show_all(all=True)
           
        for bone in rig_deform.data.edit_bones:
            if bone.use_deform == False:
                remove_bones.append(bone)
                      
        for bone in remove_bones:     
            rig_deform.data.edit_bones.remove(bone)
        
        #clear all constraints
        for bone in rig_deform.pose.bones:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)
                
        #clear drivers
        rig_deform.animation_data_clear()
        
        #clear all custom properties
        for prop in bpy.context.object.data.items():
            del bpy.context.object.data[prop[0]]
        for prop in bpy.context.object.items():
            del bpy.context.object[prop[0]]
                
        #assign transformation constraints with a target to the original rig relative bones
        for bone in rig_deform.pose.bones:
            constraint = bone.constraints.new(type='COPY_TRANSFORMS')
            constraint.target = bpy.data.objects[rig.name]
            constraint.subtarget = bone.name
            #constraint.owner_space = 'LOCAL'
            #constraint.target_space = 'LOCAL'
            
    bpy.ops.object.mode_set(mode='OBJECT')
    
def optimise_rigify_for_unity(self, context):
    rig = bpy.context.active_object

    if rig.type == "ARMATURE":
        #create a duplicate
        bpy.ops.object.mode_set(mode='OBJECT')
        origin_name = rig.name
        bpy.ops.object.duplicate()
        bpy.context.active_object.name = origin_name+"_deform"
        rig_deform = bpy.context.object
        
        rig_deform.name = origin_name+"_deform" #"Armature_deform"
        rig_deform.data.name = origin_name+"_deform" #"Armature_deform"
        
        remove_bones = []
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.layers_show_all(all=True)
        
        for bone in rig_deform.data.edit_bones:
            if not bone.name.startswith("ORG-"):
                remove_bones.append(bone)
                      
        for bone in remove_bones:     
            rig_deform.data.edit_bones.remove(bone)
        
        #clear all constraints
        for bone in rig_deform.pose.bones:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)
                
        #assign transformation constraints with a target to the original rig relative bones
        for bone in rig_deform.pose.bones:
            constraint = bone.constraints.new(type='COPY_TRANSFORMS')
            constraint.target = bpy.data.objects[rig.name]
            constraint.subtarget = bone.name
            #constraint.owner_space = 'LOCAL'
            #constraint.target_space = 'LOCAL'
            
    bpy.ops.object.mode_set(mode='OBJECT')
    


def set_copy_transform_constraints(self, context):
    flag = True
    for obj in bpy.context.selected_objects:
        if obj.type != 'ARMATURE':
            flag = False
        if obj == bpy.context.active_object:
            rig_deform = obj
        else:
            target = obj.name
        
    if flag == True and len(bpy.context.selected_objects) == 2:
    
        #clear all constraints
        for bone in rig_deform.pose.bones:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)
                
        #assign transformation constraints with a target to the original rig relative bones
        for bone in rig_deform.pose.bones:
            constraint = bone.constraints.new(type='COPY_TRANSFORMS')
            constraint.target = bpy.data.objects[target]
            constraint.subtarget = bone.name
            #constraint.owner_space = 'LOCAL'
            #constraint.target_space = 'LOCAL'
                
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        print('You have to select 2 Armatures for baking')
        
#adding a handler when the checkbox is checked
def my_prop_callback(self, context):
    if bpy.context.scene.action_list:
        if bpy.context.object.animation_data != None:
            #print("added handler")
            bpy.app.handlers.scene_update_post.append(action_updated)
    elif "action_updated" in str(bpy.app.handlers.scene_update_post):
        #print("removed handler")
        bpy.app.handlers.scene_update_post.remove(action_updated)
    
#Checkbox property for the action list ui
bpy.types.Scene.action_list = bpy.props.BoolProperty(name="Action List", description="View all actions UI", default=False, options={'HIDDEN'}, update=my_prop_callback)


@persistent
def load_post_handler(scene):
    #print("Event: load_post")
    if hasattr(bpy.context.scene, "action_list"):
        #print("found ", bpy.context.scene.action_list)
        bpy.context.scene.action_list = False
        #print(bpy.context.scene.action_list)
    
########################################

class DeformArmature(bpy.types.Operator):
    bl_idname = 'armature.copy_deform'
    bl_label = 'Create Deform Armature from Rig'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        create_deform_armature(self, context)
        return {'FINISHED'}

class OptimisedArmature(bpy.types.Operator):
    bl_idname = 'armature.optimise_for_unity'
    bl_label = 'Optimise Armature for Unitys avatar System'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        optimise_rigify_for_unity(self, context)
        return {'FINISHED'}

class SetConstraints(bpy.types.Operator):
    bl_idname = 'armature.set_constraints'
    bl_label = 'Set constraints from given rig'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        set_copy_transform_constraints(self, context)
        return {'FINISHED'}
        
class BakeActions(bpy.types.Operator):
    bl_idname = 'armature.bake_actions'
    bl_label = 'bake actions from selected to active (2 armatures only)'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        old_actions = list(bpy.data.actions)
        flag = True

        for obj in bpy.context.selected_objects:
            if obj.type != 'ARMATURE':
                flag = False
            if obj == bpy.context.active_object:
                armature = obj
            else:
                rig = obj

        #check that only 2 armatures are selected with one activated
        if flag == True and len(bpy.context.selected_objects) == 2:

            for act in old_actions:
                bpy.context.active_object.select = False
                rig.select = True
                bpy.context.scene.objects.active = rig
                bpy.ops.object.posemode_toggle()
                bpy.context.object.animation_data.action = act
                #store the original name of the action
                name = act.name
                #rename the old action from the control rig
                bpy.context.object.animation_data.action.name = act.name + "_control"
                
                bpy.ops.object.posemode_toggle()
                bpy.context.active_object.select = False
                armature.select = True
                bpy.context.scene.objects.active = armature
                
                bpy.ops.nla.bake(frame_start=act.frame_range[0], frame_end=act.frame_range[1], only_selected=False, visual_keying=True, bake_types={'POSE'})
                
                #store the new action with the name of the original action
                bpy.context.object.animation_data.action.name = name
                bpy.context.object.animation_data.action.use_fake_user = True
            
            #remove all the old actions   
            for old_act in old_actions:
                for act in bpy.data.actions:
                    if old_act == act:
                        act.user_clear()
            
            
            #remove constraints from armature    
            armature.select = True
            bpy.ops.object.posemode_toggle()
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.constraints_clear()
    
        else:
            print('You have to select 2 Armatures for baking')
        
        return {'FINISHED'}

class ACTION_UI_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            pass
                
class DeformArmature_Panel(bpy.types.Panel):
    bl_label = "Armature Deform Panel"
    bl_idname = "_armaturedeform"
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Armature_Utils"

    

    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects)!= 0:
            return bpy.context.active_object.type == "ARMATURE"
        else:
            return False

    def draw(self, context):
        layout = self.layout
        

        newArmature = layout.row()
        newArmature.operator('armature.copy_deform', text="Create Deform Armature from Rig", icon = 'MOD_ARMATURE')
        optimiseArmature = layout.row()
        optimiseArmature.operator('armature.optimise_for_unity', text="Optimise Rigify Rig for Unity", icon = 'MOD_ARMATURE')
        setConstraints = layout.row()
        setConstraints.operator('armature.set_constraints', text="Create constraints", icon = 'MODIFIER')
        bake = layout.row()
        bake.operator("armature.bake_actions", text="Bake actions", icon = 'REC')
        layout.prop(context.scene, 'action_list')
        layout.separator()
        
        if bpy.context.scene.action_list:
            layout.template_list("ACTION_UI_list", "", bpy.data, "actions", context.object, "action_list_index")
           


def register():
    bpy.types.Object.action_list_index = bpy.props.IntProperty(update=update_action_list)
    bpy.utils.register_class(DeformArmature)
    bpy.utils.register_class(OptimisedArmature)
    bpy.utils.register_class(SetConstraints)
    bpy.utils.register_class(BakeActions)
    bpy.utils.register_class(ACTION_UI_list)
    bpy.utils.register_class(DeformArmature_Panel)
    bpy.app.handlers.load_post.append(load_post_handler)
    
    
    #bpy.utils.register_module(__name__)
    
    
def unregister():
    bpy.utils.unregister_class(DeformArmature)
    bpy.utils.unregister_class(OptimisedArmature)
    bpy.utils.unregister_class(SetConstraints)
    bpy.utils.unregister_class(BakeActions)
    bpy.utils.unregister_class(ACTION_UI_list)
    bpy.utils.unregister_class(DeformArmature_Panel)
    bpy.app.handlers.load_post.remove(load_post_handler)
    del bpy.types.Object.action_list_index
    

if __name__ == "__main__":  # only for live edit.
    register()
