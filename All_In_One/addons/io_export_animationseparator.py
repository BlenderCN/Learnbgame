bl_info = {
        "name":         "Fbx Animation Splitter for Xenko",
        "category":     "Import-Export",
        "version":      (0,0,2),
        "blender":      (2,80,0),
        "location":     "File > Import-Export",
        "description":  "Split Animation Export",
        "category":     "Import-Export"
        }
        
import bpy
import os



def main(context):
    startStates = []
    blend_file_path = bpy.data.filepath
    directory = os.path.dirname(blend_file_path)
    
#    target_file = os.path.join(directory, os.path.splitext(context.blend_data.filepath)[0] + '.fbx')
#    bpy.ops.export_scene.fbx(filepath = target_file, check_existing = True, object_types = {'MESH'})
    #record original state
    for i in range(0, len(bpy.data.actions)):
        print(str(i) + " " + str(bpy.data.actions[i]) + " " + str(bpy.data.actions[i].use_fake_user))
        startStates.append(bpy.data.actions[i].use_fake_user)
        bpy.data.actions[i].use_fake_user = False
    
    for i in range(0, len(bpy.data.actions)):
        if bpy.data.actions[i].name == 'ArmatureAction':
            print('skipping')

        elif startStates[i]:
            bpy.data.actions[i].use_fake_user = True
            #export here
            
            context.object.animation_data.action = bpy.data.actions[i]
            context.scene.frame_end = bpy.data.actions[i].frame_range[1]

            target_file = os.path.join(directory, os.path.splitext(context.blend_data.filepath)[0] + '_' + bpy.data.actions[i].name + '.fbx')
            print(str(bpy.data.actions[i].name))
            bpy.ops.export_scene.fbx(filepath = target_file, check_existing = False, object_types = {'ARMATURE', 'MESH'}, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False, bake_anim_force_startend_keying=False)
            bpy.data.actions[i].use_fake_user = False
        
    #revert to what it was
    for i in range(0, len(bpy.data.actions)):
        bpy.data.actions[i].use_fake_user = startStates[i]

class SplitAnimations(bpy.types.Operator):
    """Split and Export Animations"""
    bl_idname = "object.splitanimations"
    bl_label = "Split and Export Animations"
    
    def execute(self, context):
        main(context)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(operator.SplitAnimations.bl_idname, text="SplitAnimations")

def register():
    bpy.utils.register_class(SplitAnimations)
    
def unregister():
    bpy.utils.register_class(SplitAnimations)

if __name__ == "__main__":
    register()
