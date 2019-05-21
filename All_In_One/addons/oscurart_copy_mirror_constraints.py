bl_info = {
    "name": "Copy Mirror Constraints",
    "author": "Oscurart",
    "version": (1, 1),
    "blender": (2, 5, 9),
    "api": 40600,
    "location": "Pose > Constraints > Copy Mirror Constraints",
    "description": "Copy Mirror Constraints",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


import bpy

def RENAMECONSTRAINT(self, BONE, SIDE, ACTOBJ, SELSIDE):

    for CONSTRAINT in bpy.data.objects[ACTOBJ.name].pose.bones[BONE.name.replace(SELSIDE, SIDE)].constraints:
        ## TYPES WITH SUBTARGET ONLY
        print (CONSTRAINT.type)
        if CONSTRAINT.type == "COPY_LOCATION" or CONSTRAINT.type ==  "COPY_ROTATION" or CONSTRAINT.type == "COPY_SCALE" or CONSTRAINT.type == "COPY_TRANSFORMS" or CONSTRAINT.type == "LIMIT_DISTANCE" or CONSTRAINT.type == "TRANSFORM" or CONSTRAINT.type == "DAMPED_TRACK" or CONSTRAINT.type == "LOCKED_TRACK" or CONSTRAINT.type == "STRETCH_TO" or CONSTRAINT.type == "TRACK_TO" or CONSTRAINT.type == "ACTION" or CONSTRAINT.type == "CHILD_OF" or CONSTRAINT.type == "FLOOR" or CONSTRAINT.type == "PIVOT" :
            CONSTRAINT.subtarget = CONSTRAINT.subtarget.replace(SELSIDE, SIDE)
        
        if CONSTRAINT.type == "IK":
            CONSTRAINT.subtarget = CONSTRAINT.subtarget.replace(SELSIDE, SIDE)
            CONSTRAINT.pole_subtarget = CONSTRAINT.pole_subtarget.replace(SELSIDE, SIDE)
            

        
    
    
def copy_mirror_constraint(self):
    SELBON = bpy.context.selected_pose_bones
    ACTOBJ = bpy.context.active_object
    
    
    for BONE in SELBON:
        bpy.ops.pose.select_all(action='DESELECT')
        if BONE.name.count("_L"): 
            ACTOBJ.data.bones[BONE.name.replace("_L" ,"_R")].select=1
            ACTOBJ.data.bones.active = bpy.data.armatures[ACTOBJ.data.name].bones[BONE.name]
            SIDE="_R"
            SELSIDE="_L"
        else:
            ACTOBJ.data.bones[BONE.name.replace("_R" ,"_L")].select=1
            ACTOBJ.data.bones.active = bpy.data.armatures[ACTOBJ.data.name].bones[BONE.name] 
            SIDE="_L" 
            SELSIDE="_R"
               

        ## COPY CONSTRAINTS          
        bpy.ops.pose.constraints_copy()
        ## EXECUTE DEF
        RENAMECONSTRAINT(self, BONE, SIDE, ACTOBJ, SELSIDE)
        


class OBJECT_OT_add_object(bpy.types.Operator):
    bl_idname = "pose.copy_constraints_mirror"
    bl_label = "Copy Mirror Constraints"
    bl_description = "Mirror Constraints in PoseBones"
    bl_options = {'REGISTER', 'UNDO'}



    def execute(self, context):

        copy_mirror_constraint(self)

        return {'FINISHED'}


# Registration

def add_object_copy_mirrcns_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Copy Mirror Constraints",
        icon="PLUGIN")


def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.types.VIEW3D_MT_pose_constraints.append(add_object_copy_mirrcns_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.types.VIEW3D_MT_pose_constraints.append(add_object_copy_mirrcns_button)


if __name__ == '__main__':
    register()
