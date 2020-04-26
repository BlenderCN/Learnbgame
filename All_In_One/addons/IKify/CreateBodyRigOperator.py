import bpy
from .utils import createLayerArray
from .utils import createGizmo
from .utils import setCustomShape
from .ikRig import addOneLegIK
from .ikRig import addOneArmIK
from .fkRig import addOneFKControl
from .fkRig import addHeadNeckRig
from .fkRig import addTorsoRig
from .fkRig import addOneFingerRig
from .fkRig import addPalmRig
from .gizmoData import *

def createFKControls(context, object):
    gizmo_obj = bpy.data.objects['GZM_Circle']
    
    thigh_L_FK = addOneFKControl(context, object, 'thigh_L', gizmo_obj, 1, 1.0, 'pelvis', False)
    thigh_R_FK = addOneFKControl(context, object, 'thigh_R', gizmo_obj, 1, 1.0, 'pelvis', False)
    calf_L_FK = addOneFKControl(context, object, 'calf_L', gizmo_obj, 1, 0.8, thigh_L_FK)
    calf_R_FK = addOneFKControl(context, object, 'calf_R', gizmo_obj, 1, 0.8, thigh_R_FK)
    foot_L_FK = addOneFKControl(context, object, 'foot_L', gizmo_obj, 1, 1.5, calf_L_FK)
    foot_R_FK = addOneFKControl(context, object, 'foot_R', gizmo_obj, 1, 1.5, calf_R_FK)    
    addOneFKControl(context, object, 'toes_L', gizmo_obj, 1, 2.0, foot_L_FK)
    addOneFKControl(context, object, 'toes_R', gizmo_obj, 1, 2.0, foot_R_FK)
    
    # in the case of upper arms, we don't pass parent information. The addOneFKControl function
    # will create a isolate rotation socket rig and set parents accordingly.
    upperarm_L_FK = addOneFKControl(context, object, 'upperarm_L', gizmo_obj, 2, 1.0, '')
    upperarm_R_FK = addOneFKControl(context, object, 'upperarm_R', gizmo_obj, 2, 1.0, '')    
    lowerarm_L_FK = addOneFKControl(context, object, 'lowerarm_L', gizmo_obj, 2, 0.8, upperarm_L_FK)
    lowerarm_R_FK = addOneFKControl(context, object, 'lowerarm_R', gizmo_obj, 2, 0.8, upperarm_R_FK)
    addOneFKControl(context, object, 'hand_L', gizmo_obj, 2, 4.5, lowerarm_L_FK)
    addOneFKControl(context, object, 'hand_R', gizmo_obj, 2, 4.5, lowerarm_R_FK)
    
    addTorsoRig(context, object, gizmo_obj)
    addHeadNeckRig(context, object, gizmo_obj)

    for finger in ['thumb', 'index', 'middle', 'ring', 'pinky']:
        addOneFingerRig(context, object, finger, 'L', gizmo_obj)
        addOneFingerRig(context, object, finger, 'R', gizmo_obj)

    addPalmRig(context, object, 'L')
    addPalmRig(context, object, 'R')    

def createIKControls(context, object):
    addOneLegIK(context, object, 'L')
    addOneLegIK(context, object, 'R')
    addOneArmIK(context, object, 'L')
    addOneArmIK(context, object, 'R')
    
def createAllGizmos(context):
    # Create Gizmos parent
    gizmos_parent = None
    if 'Gizmos' not in bpy.data.objects:
        gizmos_parent = bpy.data.objects.new('Gizmos', None)
        context.scene.objects.link(gizmos_parent)
        gizmos_parent.layers = createLayerArray([19], 20)
    else:
        gizmos_parent = bpy.data.objects['Gizmos']    
    
    # Create all the gizmo meshes
    createGizmo(context, 'GZM_Circle', circleGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_root', rootGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_shoulder', shoulderGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_breasts', breastsGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_chest', chestGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_spine', spineGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_pelvis', pelvisGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Hand_L_IK', handLIkGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Hand_R_IK', handRIkGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Elbow_L', elbowLGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Elbow_R', elbowRGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Foot_IK', footIkGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Foot_Roll_IK', footRollIkGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Toes_IK', toesIkGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Finger', fingerGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Thumb', thumbGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Palm_L', palmLGizmoData(), gizmos_parent)
    createGizmo(context, 'GZM_Palm_R', palmRGizmoData(), gizmos_parent)    
       
class BodyRigController(bpy.types.Operator):
    """Create the body rig"""
    bl_idname = "ikify.body_rig"
    bl_label = "Create Body Rig"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        # Reset pose for all bones
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        bpy.ops.pose.select_all(action='DESELECT')
        
        # Set visibility for armature
        obj = context.active_object
        obj.show_x_ray = True
        armature = obj.data
        armature.show_bone_custom_shapes = True
        
        # Create all the gizmo objects
        createAllGizmos(context)
        
        # Create the FK rig
        createFKControls(context, obj)
        # Create the IK rig
        createIKControls(context, obj)
        
        
        # Make Root bone visible in layer 16
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        root_bone = obj.data.edit_bones['root']
        root_bone.layers[16] = True

        # Eventually move to POSE mode
        bpy.ops.object.mode_set(mode='POSE', toggle=False)        

        # Set all remaining custom shapes for pose bones
        setCustomShape(obj, 'root', 'GZM_root', 1.0)

        # Set layer visibility to only newly added controls
        bpy.ops.armature.armature_layers(layers=createLayerArray([1,2,3,4,5,6,16], 32))

        return {'FINISHED'}

