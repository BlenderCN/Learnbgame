bl_info = {  
 "name": "Rigify Picker",  
 "author": "Salvador Artero",  
 "version": (1, 0, 0),  
 "blender": (2, 69, 0),  
 "location": "View3D > UI panel > Rigify Picker",
 "description": "Interfaz de selección de controles del personaje",  
 "warning": "Beta testing",  
 "wiki_url": "www.mundrop.com", 
 "tracker_url": "info@mundrop.com",
 "category": "Animation",
 } 


import bpy
from mathutils import Matrix, Vector
from math import acos, pi

rig_id = "f7d8ye5v76235725"
  
###################OPERATORS IK FK  BRAZOS ##################################

class OperadorFKtoIK_BrazoL(bpy.types.Operator):     
    bl_idname = "operador.brazofk2ik_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.rigify_arm_ik2fk_f7d8ye5v76235725(uarm_fk="upper_arm.fk.L", farm_fk="forearm.fk.L", hand_fk="hand.fk.L", uarm_ik="MCH-upper_arm.ik.L", farm_ik="MCH-forearm.ik.L", hand_ik="hand.ik.L", pole="elbow_target.ik.L")
     
     bpy.context.object.pose.bones["hand.ik.L"]["ikfk_switch"] = 1 
     
     bpy.context.object.data.layers[6] = False
     bpy.context.object.data.layers[7] = True
     
     bpy.ops.pose.select_all(action='DESELECT')             
     
     
     
     return {"FINISHED"}
 
class OperadorIKtoFK_BrazoL(bpy.types.Operator):     
    bl_idname = "operador.brazoik2fk_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.rigify_arm_fk2ik_f7d8ye5v76235725(uarm_fk="upper_arm.fk.L", farm_fk="forearm.fk.L", hand_fk="hand.fk.L", uarm_ik="MCH-upper_arm.ik.L", farm_ik="MCH-forearm.ik.L", hand_ik="hand.ik.L")
     
     bpy.context.object.pose.bones["hand.ik.L"]["ikfk_switch"] = 0 
     
     bpy.context.object.data.layers[6] = True
     bpy.context.object.data.layers[7] = False
     
     bpy.ops.pose.select_all(action='DESELECT')             
     
     
     
     return {"FINISHED"}
 
class OperadorFKtoIK_BrazoR(bpy.types.Operator):     
    bl_idname = "operador.brazofk2ik_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.rigify_arm_ik2fk_f7d8ye5v76235725(uarm_fk="upper_arm.fk.R", farm_fk="forearm.fk.R", hand_fk="hand.fk.R", uarm_ik="MCH-upper_arm.ik.R", farm_ik="MCH-forearm.ik.R", hand_ik="hand.ik.R", pole="elbow_target.ik.R")
     
     bpy.context.object.pose.bones["hand.ik.R"]["ikfk_switch"] = 1 
     
     bpy.context.object.data.layers[9] = False
     bpy.context.object.data.layers[10] = True
     
     bpy.ops.pose.select_all(action='DESELECT')             
     
     
     
     return {"FINISHED"}
 
class OperadorIKtoFK_BrazoR(bpy.types.Operator):     
    bl_idname = "operador.brazoik2fk_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.rigify_arm_fk2ik_f7d8ye5v76235725(uarm_fk="upper_arm.fk.R", farm_fk="forearm.fk.R", hand_fk="hand.fk.R", uarm_ik="MCH-upper_arm.ik.R", farm_ik="MCH-forearm.ik.R", hand_ik="hand.ik.R")
     
     bpy.context.object.pose.bones["hand.ik.R"]["ikfk_switch"] = 0 
     
     bpy.context.object.data.layers[9] = True
     bpy.context.object.data.layers[10] = False
     
     bpy.ops.pose.select_all(action='DESELECT')             
     
     
     return {"FINISHED"}
 

###################OPERATORS IK FK  PIERNAS ##################################


class OperadorFKtoIK_PiernaL(bpy.types.Operator):     
    bl_idname = "operador.piernafk2ik_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.rigify_leg_ik2fk_f7d8ye5v76235725(thigh_fk="thigh.fk.L", shin_fk="shin.fk.L", mfoot_fk="MCH-foot.L", thigh_ik="MCH-thigh.ik.L", shin_ik="MCH-shin.ik.L", foot_ik="foot.ik.L", footroll="foot_roll.ik.L", pole="knee_target.ik.L", mfoot_ik="MCH-foot.L.001")
     
     bpy.context.object.pose.bones["foot.ik.L"]["ikfk_switch"] = 1 
     
     bpy.context.object.data.layers[12] = False
     bpy.context.object.data.layers[13] = True
     
     bpy.ops.pose.select_all(action='DESELECT')             
     
     
     
     return {"FINISHED"}
 
class OperadorIKtoFK_PiernaL(bpy.types.Operator):     
    bl_idname = "operador.piernaik2fk_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.rigify_leg_fk2ik_f7d8ye5v76235725(thigh_fk="thigh.fk.L", shin_fk="shin.fk.L", foot_fk="foot.fk.L", mfoot_fk="MCH-foot.L", thigh_ik="MCH-thigh.ik.L", shin_ik="MCH-shin.ik.L", foot_ik="foot.ik.L", mfoot_ik="MCH-foot.L.001")
     
     bpy.context.object.pose.bones["foot.ik.L"]["ikfk_switch"] = 0 
     
     bpy.context.object.data.layers[12] = True
     bpy.context.object.data.layers[13] = False
     
     bpy.ops.pose.select_all(action='DESELECT')             
     
     
     
     return {"FINISHED"}
 
class OperadorFKtoIK_PiernaR(bpy.types.Operator):     
    bl_idname = "operador.piernafk2ik_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.rigify_leg_ik2fk_f7d8ye5v76235725(thigh_fk="thigh.fk.R", shin_fk="shin.fk.R", mfoot_fk="MCH-foot.R", thigh_ik="MCH-thigh.ik.R", shin_ik="MCH-shin.ik.R", foot_ik="foot.ik.R", footroll="foot_roll.ik.R", pole="knee_target.ik.R", mfoot_ik="MCH-foot.R.001")
     
     bpy.context.object.pose.bones["foot.ik.R"]["ikfk_switch"] = 1 
     
     bpy.context.object.data.layers[15] = False
     bpy.context.object.data.layers[16] = True
     
     bpy.ops.pose.select_all(action='DESELECT')             
     
     
     
     return {"FINISHED"}
 
class OperadorIKtoFK_PiernaR(bpy.types.Operator):     
    bl_idname = "operador.piernaik2fk_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.rigify_leg_fk2ik_f7d8ye5v76235725(thigh_fk="thigh.fk.R", shin_fk="shin.fk.R", foot_fk="foot.fk.R", mfoot_fk="MCH-foot.R", thigh_ik="MCH-thigh.ik.R", shin_ik="MCH-shin.ik.R", foot_ik="foot.ik.R", mfoot_ik="MCH-foot.R.001")
     
     bpy.context.object.pose.bones["foot.ik.R"]["ikfk_switch"] = 0 
     
     bpy.context.object.data.layers[15] = True
     bpy.context.object.data.layers[16] = False
     
     bpy.ops.pose.select_all(action='DESELECT')             
     
     
     return {"FINISHED"}
     
              

###################OPERATORS DE SELECCION##################################



######## BRAZO SUM L ########################################### 

class OperadorBrazoSumL(bpy.types.Operator):     
    bl_idname = "operador.brazosum_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="upper_arm.fk.L") 
     bpy.ops.object.select_pattern(pattern="forearm.fk.L") 
     bpy.ops.object.select_pattern(pattern="hand.fk.L") 
     bpy.ops.object.select_pattern(pattern="hand.ik.L") 
     bpy.ops.object.select_pattern(pattern="elbow_target.ik.L") 
     bpy.ops.object.select_pattern(pattern="palm.L") 
     bpy.ops.object.select_pattern(pattern="thumb.L") 
     bpy.ops.object.select_pattern(pattern="f_index.L") 
     bpy.ops.object.select_pattern(pattern="f_middle.L")
     bpy.ops.object.select_pattern(pattern="f_ring.L")
     bpy.ops.object.select_pattern(pattern="thumb.01.L")
     bpy.ops.object.select_pattern(pattern="thumb.02.L")
     bpy.ops.object.select_pattern(pattern="thumb.03.L")
     bpy.ops.object.select_pattern(pattern="f_index.01.L")
     bpy.ops.object.select_pattern(pattern="f_index.02.L")
     bpy.ops.object.select_pattern(pattern="f_index.03.L")
     bpy.ops.object.select_pattern(pattern="f_middle.01.L")
     bpy.ops.object.select_pattern(pattern="f_middle.02.L")
     bpy.ops.object.select_pattern(pattern="f_middle.03.L")
     bpy.ops.object.select_pattern(pattern="f_middle.03.L")
     bpy.ops.object.select_pattern(pattern="f_ring.01.L")
     bpy.ops.object.select_pattern(pattern="f_ring.02.L")
     bpy.ops.object.select_pattern(pattern="f_ring.03.L")
     bpy.ops.object.select_pattern(pattern="upper_arm_hose.L")
     bpy.ops.object.select_pattern(pattern="elbow_hose.L")
     bpy.ops.object.select_pattern(pattern="forearm_hose.L")
     bpy.ops.object.select_pattern(pattern="f_pinky.01.L")
     bpy.ops.object.select_pattern(pattern="f_pinky.02.L")
     bpy.ops.object.select_pattern(pattern="f_pinky.03.L")
     bpy.ops.object.select_pattern(pattern="f_pinky.L")
    
     
     return {"FINISHED"}
 
######## BRAZO SUM R ########################################### 

class OperadorBrazoSumR(bpy.types.Operator):     
    bl_idname = "operador.brazosum_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="upper_arm.fk.R") 
     bpy.ops.object.select_pattern(pattern="forearm.fk.R") 
     bpy.ops.object.select_pattern(pattern="hand.fk.R") 
     bpy.ops.object.select_pattern(pattern="hand.ik.R") 
     bpy.ops.object.select_pattern(pattern="elbow_target.ik.R") 
     bpy.ops.object.select_pattern(pattern="palm.R") 
     bpy.ops.object.select_pattern(pattern="thumb.R") 
     bpy.ops.object.select_pattern(pattern="f_index.R") 
     bpy.ops.object.select_pattern(pattern="f_middle.R")
     bpy.ops.object.select_pattern(pattern="f_ring.R")
     bpy.ops.object.select_pattern(pattern="thumb.01.R")
     bpy.ops.object.select_pattern(pattern="thumb.02.R")
     bpy.ops.object.select_pattern(pattern="thumb.03.R")
     bpy.ops.object.select_pattern(pattern="f_index.01.R")
     bpy.ops.object.select_pattern(pattern="f_index.02.R")
     bpy.ops.object.select_pattern(pattern="f_index.03.R")
     bpy.ops.object.select_pattern(pattern="f_middle.01.R")
     bpy.ops.object.select_pattern(pattern="f_middle.02.R")
     bpy.ops.object.select_pattern(pattern="f_middle.03.R")
     bpy.ops.object.select_pattern(pattern="f_middle.03.R")
     bpy.ops.object.select_pattern(pattern="f_ring.01.R")
     bpy.ops.object.select_pattern(pattern="f_ring.02.R")
     bpy.ops.object.select_pattern(pattern="f_ring.03.R")
     bpy.ops.object.select_pattern(pattern="upper_arm_hose.R")
     bpy.ops.object.select_pattern(pattern="elbow_hose.R")
     bpy.ops.object.select_pattern(pattern="forearm_hose.R")
     bpy.ops.object.select_pattern(pattern="f_pinky.01.R")
     bpy.ops.object.select_pattern(pattern="f_pinky.02.R")
     bpy.ops.object.select_pattern(pattern="f_pinky.03.R")
     bpy.ops.object.select_pattern(pattern="f_pinky.R")
     
     return {"FINISHED"}
 
######## PIERNA SUM L ########################################### 

class OperadorPiernaSumL(bpy.types.Operator):     
    bl_idname = "operador.piernasum_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="thigh.fk.L") 
     bpy.ops.object.select_pattern(pattern="shin.fk.L") 
     bpy.ops.object.select_pattern(pattern="foot.fk.L") 
     bpy.ops.object.select_pattern(pattern="foot.ik.L") 
     bpy.ops.object.select_pattern(pattern="knee_target.ik.L") 
     bpy.ops.object.select_pattern(pattern="thigh_hose.L") 
     bpy.ops.object.select_pattern(pattern="knee_hose.L") 
     bpy.ops.object.select_pattern(pattern="shin_hose.L") 
     bpy.ops.object.select_pattern(pattern="foot_roll.ik.L") 
     bpy.ops.object.select_pattern(pattern="toe.L") 
     return {"FINISHED"}
 
######## PIERNA SUM R ########################################### 

class OperadorPiernaSumR(bpy.types.Operator):     
    bl_idname = "operador.piernasum_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="thigh.fk.R") 
     bpy.ops.object.select_pattern(pattern="shin.fk.R") 
     bpy.ops.object.select_pattern(pattern="foot.fk.R") 
     bpy.ops.object.select_pattern(pattern="foot.ik.R") 
     bpy.ops.object.select_pattern(pattern="knee_target.ik.R") 
     bpy.ops.object.select_pattern(pattern="thigh_hose.R") 
     bpy.ops.object.select_pattern(pattern="knee_hose.R") 
     bpy.ops.object.select_pattern(pattern="shin_hose.R") 
     bpy.ops.object.select_pattern(pattern="foot_roll.ik.R") 
     bpy.ops.object.select_pattern(pattern="toe.R") 
     return {"FINISHED"}
 
######## DEDOS ########################################### 

######## Mano L ########################################### 





 


######## TORSO Y CABEZA ########################################### 



class OperadorCabeza(bpy.types.Operator):     
    bl_idname = "operador.cabeza"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="head") 
     return {"FINISHED"}
 
class OperadorCuello(bpy.types.Operator):     
    bl_idname = "operador.cuello"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context): 
     bpy.ops.pose.select_all(action='DESELECT')       
     bpy.ops.object.select_pattern(pattern="neck")
     return {"FINISHED"}
     
class OperadorCostillas(bpy.types.Operator):     
    bl_idname = "operador.costillas"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context): 
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="chest") 
     
     return {"FINISHED"}
 
 
class OperadorColumna(bpy.types.Operator):     
    bl_idname = "operador.columna"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context): 
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="spine") 
     
     return {"FINISHED"}
 
class OperadorTorso(bpy.types.Operator):     
    bl_idname = "operador.torso"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="torso") 
     
     return {"FINISHED"}

class OperadorCadera(bpy.types.Operator):     
    bl_idname = "operador.cadera"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="hips") 
     
     return {"FINISHED"}

class OperadorClaviculaL(bpy.types.Operator):     
    bl_idname = "operador.clavicula_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="shoulder.L") 
     
     return {"FINISHED"}
 
 
class OperadorClaviculaR(bpy.types.Operator):     
    bl_idname = "operador.clavicula_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):  
     bpy.ops.pose.select_all(action='DESELECT')            
     bpy.ops.object.select_pattern(pattern="shoulder.R") 
     
     return {"FINISHED"}
 
class OperadorAntebrazoFKL(bpy.types.Operator):     
    bl_idname = "operador.antebrazofk_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="forearm.fk.L")
      
     
     return {"FINISHED"}
 
class OperadorAntebrazoFKR(bpy.types.Operator):     
    bl_idname = "operador.antebrazofk_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):     
     bpy.ops.pose.select_all(action='DESELECT')         
     bpy.ops.object.select_pattern(pattern="forearm.fk.R")
     
     
     return {"FINISHED"}
 
 
class OperadorBrazoFKL(bpy.types.Operator):     
    bl_idname = "operador.brazofk_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="upper_arm.fk.L") 
     
     return {"FINISHED"}

class OperadorCodoIKL(bpy.types.Operator):     
    bl_idname = "operador.codoik_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="elbow_target.ik.L") 
     
     return {"FINISHED"}
 
class OperadorCodoIKR(bpy.types.Operator):     
    bl_idname = "operador.codoik_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="elbow_target.ik.R") 
     
     return {"FINISHED"}


class OperadorBrazoFKR(bpy.types.Operator):     
    bl_idname = "operador.brazofk_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):  
     bpy.ops.pose.select_all(action='DESELECT')            
     bpy.ops.object.select_pattern(pattern="upper_arm.fk.R") 
     
     return {"FINISHED"}
 
 
class OperadorManoL(bpy.types.Operator):     
    bl_idname = "operador.mano_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context): 
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="hand.ik.L")
     
     return {"FINISHED"}
 
class OperadorManoFKL(bpy.types.Operator):     
    bl_idname = "operador.manofk_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context): 
     bpy.ops.pose.select_all(action='DESELECT')             
     bpy.ops.object.select_pattern(pattern="hand.fk.L") 
     
     return {"FINISHED"}

class OperadorManoR(bpy.types.Operator):     
    bl_idname = "operador.mano_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="hand.ik.R")
     
     return {"FINISHED"}
 
class OperadorManoFKR(bpy.types.Operator):     
    bl_idname = "operador.manofk_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="hand.fk.R") 
     
     
     return {"FINISHED"}
 
 
class OperadorPiernaL(bpy.types.Operator):     
    bl_idname = "operador.pierna_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):  
     bpy.ops.pose.select_all(action='DESELECT')            
     bpy.ops.object.select_pattern(pattern="thigh.fk.L") 
     
     
     return {"FINISHED"}
 
class OperadorPiernaR(bpy.types.Operator):     
    bl_idname = "operador.pierna_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="thigh.fk.R") 
     
     
     return {"FINISHED"}

class OperadorTibiaL(bpy.types.Operator):     
    bl_idname = "operador.tibia_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):  
     bpy.ops.pose.select_all(action='DESELECT')            
     bpy.ops.object.select_pattern(pattern="shin.fk.L") 
     
     
     return {"FINISHED"}
 
 

class OperadorRodillaL(bpy.types.Operator):     
    bl_idname = "operador.rodilla_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="knee_target.ik.L") 
     
     
     return {"FINISHED"}
 
class OperadorRodillaR(bpy.types.Operator):     
    bl_idname = "operador.rodilla_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="knee_target.ik.R") 
     
     
     return {"FINISHED"} 
 
class OperadorTibiaR(bpy.types.Operator):     
    bl_idname = "operador.tibia_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="shin.fk.R") 
     
     
     return {"FINISHED"}
 
 
 
class OperadorPieL(bpy.types.Operator):     
    bl_idname = "operador.pie_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):    
     bpy.ops.pose.select_all(action='DESELECT')          
     bpy.ops.object.select_pattern(pattern="foot.ik.L")  
     
     return {"FINISHED"}

class OperadorPieFKL(bpy.types.Operator):     
    bl_idname = "operador.piefk_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):    
     bpy.ops.pose.select_all(action='DESELECT')          
     bpy.ops.object.select_pattern(pattern="foot.fk.L")
     
     return {"FINISHED"}
     
     
     
     
 
class OperadorPieR(bpy.types.Operator):     
    bl_idname = "operador.pie_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):  
     bpy.ops.pose.select_all(action='DESELECT')            
     
     bpy.ops.object.select_pattern(pattern="foot.ik.R")  
     
     
     return {"FINISHED"}
 
class OperadorPieFKR(bpy.types.Operator):     
    bl_idname = "operador.piefk_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):  
     bpy.ops.pose.select_all(action='DESELECT')            
     bpy.ops.object.select_pattern(pattern="foot..fk.R")
      
     
     
     return {"FINISHED"}
 
 
class OperadorTobilloL(bpy.types.Operator):     
    bl_idname = "operador.tobillo_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="foot_roll.ik.L")
      
     
     
     return {"FINISHED"}
 
class OperadorTobilloR(bpy.types.Operator):     
    bl_idname = "operador.tobillo_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):  
     bpy.ops.pose.select_all(action='DESELECT')            
     bpy.ops.object.select_pattern(pattern="foot_roll.ik.R")
      
     
     
     return {"FINISHED"}
 
 
class OperadorPuntaL(bpy.types.Operator):     
    bl_idname = "operador.punta_l"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):   
     bpy.ops.pose.select_all(action='DESELECT')           
     bpy.ops.object.select_pattern(pattern="toe.L")
      
     
     
     return {"FINISHED"}
 
class OperadorPuntaR(bpy.types.Operator):     
    bl_idname = "operador.punta_r"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):    
     bpy.ops.pose.select_all(action='DESELECT')          
     bpy.ops.object.select_pattern(pattern="toe.R")
      
     
     
     return {"FINISHED"}
 
class OperadorRoot(bpy.types.Operator):     
    bl_idname = "operador.root"     
    bl_label = "The Operator"      
    
    # A dummy bool property     
    dummyBool = bpy.props.BoolProperty(name="Object Bool")      

    def execute(self, context):    
     bpy.ops.pose.select_all(action='DESELECT')          
     bpy.ops.object.select_pattern(pattern="root")
      
     
     
     return {"FINISHED"}
 
 
 
 
 
 


 


 
 
 
################# PANEL #############################################
 

class ThePanel(bpy.types.Panel):     
     bl_label = 'Rigify Picker'
     bl_space_type = 'VIEW_3D'
     bl_region_type = 'UI'   
     
     
     
     display = 0
       
     
     height = bpy.props.IntProperty(attr="height")   
     
     _height = 1

     def height_getter(self):
        return self._height

     def height_setter(self, value):
        self._height = value

        height = property(fget = height_getter, fset = height_setter)  
       
     def draw(self, context):
      
      
      
      layout = self.layout
      layout.label("Body:")
      obj = context.object
      row = layout.row() 
      row.scale_x=1.12
      row.scale_y=2
      row.alignment = 'CENTER'
      row.operator("operador.cabeza", text="Head") 
      
      
      layout = self.layout
      obj = context.object
      row = layout.row() 
      row.scale_x=0.8
      row.scale_y=1 
      row.alignment = 'CENTER'                                  
      row.operator("operador.cuello", text="Neck") 
      
      layout = self.layout
      obj = context.object
      row = layout.row(align=False)  
      row.alignment = 'CENTER' 
      
      row.operator("operador.brazosum_r", text="All", icon="TRIA_DOWN")
      row.operator("operador.clavicula_r", text="Shoulder R")
      row.operator("operador.clavicula_l", text="Shoulder L")
      row.operator("operador.brazosum_l", text="All", icon="TRIA_DOWN")
      
      
      
      #Brazo R
      
      layout = self.layout
      obj = context.object
      row = layout.row() 
      col = row.column()
      col.scale_x=0.1
      col.scale_y=2
      row.alignment = 'CENTER'
      row.prop(context.active_object.data, 'layers', index=11, toggle=True, text='tweak')
      
      
      
      col = row.column()
      col.scale_x=0.1
      col.scale_y=2
      row.alignment = 'CENTER'
      col.operator("operador.brazofk_r", text="Arm R")
      col.operator("operador.codoik_r", text="Ik")
      col.operator("operador.antebrazofk_r", text="Forearm R")
      
      
      #Columna
      
      layout = self.layout
      obj = context.object
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=4
      col.scale_y=1.5
      col.operator("operador.costillas", text="Ribs")
      col.operator("operador.columna", text="Spine") 
      col.operator("operador.torso", text="Torso")
      col.operator("operador.cadera", text="Hips")
      
      #Brazo L
      
      layout = self.layout
      obj = context.object
      col = row.column()
      col.scale_x=0.1
      col.scale_y=2
      row.alignment = 'CENTER'
      col.operator("operador.brazofk_l", text="Arm L")
      col.operator("operador.codoik_l", text="Ik")
      row.prop(context.active_object.data, 'layers', index=8, toggle=True, text='tweak')
      col.operator("operador.antebrazofk_l", text="Forearm L")
      
      col = row.column()
      
      
      
                
       
      
      #Manos&Femur 1
      
      layout = self.layout
      obj = context.object
      row = layout.row() 
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=0.123
      col.scale_y=2
      col.operator("operador.brazoik2fk_r", text=">FK", icon = "COLOR_BLUE")
      col.operator("operador.brazofk2ik_r", text=">IK", icon = "COLOR_RED")
      
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=0.3
      col.scale_y=2
      
      
      col.operator("operador.manofk_r", text="Hand FK")
      col.operator("operador.mano_r", text="Hand IK")
      
      out = self.layout
      obj = context.object
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=0.1
      col.scale_y=4.2
      col.operator("operador.pierna_r", text="Thigh L") 
      
      
      
      
      #Manos&Femur 3
      
      layout = self.layout
      obj = context.object
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=0.1
      col.scale_y=4.2
      col.operator("operador.pierna_l", text="Thig R")
      
      
      
      
      #Manos&Femur 4
      
      layout = self.layout
      obj = context.object
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=0.3
      col.scale_y=2
      col.operator("operador.manofk_l", text="Hand FK")
      col.operator("operador.mano_l", text="Hand IK")
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=0.123
      col.scale_y=2
      col.operator("operador.brazoik2fk_l", text=">FK", icon = "COLOR_BLUE")
      col.operator("operador.brazofk2ik_l", text=">IK", icon = "COLOR_RED")
      
      
                      
     
      
      #Piernas Sum R
      
      layout = self.layout
      obj = context.object
      row = layout.row() 
      col = row.column()
      col = row.column()
      
      
      col.alignment = 'CENTER'
      col.scale_x=1
      col.scale_y=1
      col.operator("operador.piernasum_r", text="All", icon="TRIA_RIGHT")
      
      
      
      
      #Tibia R
      
      layout = self.layout
      obj = context.object
      
      
      col = row.column()
      
      col.alignment = 'CENTER'
      col.scale_x=0.3
      col.scale_y=2.5
      col.operator("operador.rodilla_r", text="Ik")
      col.operator("operador.tibia_r", text="Shin R")
      
      
      
      
      
      #Tibia L
      
      layout = self.layout
      obj = context.object
      col = row.column()
      
      col.alignment = 'CENTER'
      col.scale_x=0.3
      col.scale_y=2.5
      col.operator("operador.rodilla_l", text="Ik")
      col.operator("operador.tibia_l", text="Shin L")
      
      
      
      
      #Piernas Sum L
      
      layout = self.layout
      obj = context.object
      col = row.column()
      
      col.alignment = 'CENTER'
      col.scale_x=1
      col.scale_y=1
      col.operator("operador.piernasum_l", text="All", icon="TRIA_LEFT")
      
      col = row.column()
      
      
      
      
      #PIESSSS#
      
      
     #PiePunta L
      
      layout = self.layout
      obj = context.object
      row = layout.row(align=False)
      col = row.column()
      col.scale_x=0.1
      col.scale_y=1
      col.operator("operador.punta_r", text="Toe L")
      
      
      
      #Pie R
      
      layout = self.layout
      obj = context.object
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=0.25
      col.scale_y=1
      col.operator("operador.piefk_r", text="FootFK R")
      
      
      
      #PieRoll L
      
      layout = self.layout
      obj = context.object
      col = row.column()
      col.scale_x=0.1
      col.scale_y=1
      col.operator("operador.tobillo_r", text="Roll R")
      
      
      
      #PieRoll R
      
      layout = self.layout
      obj = context.object
      
      col = row.column()
      col.scale_x=0.1
      col.scale_y=1
      col.operator("operador.tobillo_l", text="Roll L")
      
      
      
      #Pie L
      
      layout = self.layout
      obj = context.object
      col = row.column()
      row.alignment = 'CENTER'
      col.scale_x=0.25
      col.scale_y=1
      col.operator("operador.piefk_l", text="FootFK L")
      
      
      
      #PiePunta R
      
      layout = self.layout
      obj = context.object
      col = row.column()
      col.scale_x=0.1
      col.scale_y=1
      col.operator("operador.punta_l", text="Toe L")
      obj = context.object
      row = layout.row()
    
      
      #PieIK  L & R
      
      layout = self.layout
      obj = context.object
      row.scale_x=1.8
      row.scale_y=0.9
      row.alignment = 'CENTER'
      row.operator("operador.pie_r", text="FootIK R")
      row.operator("operador.pie_l", text="FootIK L")
      obj = context.object
      row = layout.row()
      row.alignment = 'CENTER'
      row.scale_x=1.8
      row.scale_y=0.9
      row.prop(context.active_object.data, 'layers', index=17, toggle=True, text='tweak')
      row.operator("operador.piernafk2ik_r", text="", icon = "COLOR_RED")
      row.operator("operador.piernaik2fk_r", text="", icon = "COLOR_BLUE")
      
      row.operator("operador.piernafk2ik_l", text="", icon = "COLOR_RED")
      row.operator("operador.piernaik2fk_l", text="", icon = "COLOR_BLUE")
      row.prop(context.active_object.data, 'layers', index=14, toggle=True, text='tweak')
      
      row = layout.row()

      
      
      #Root
      
      layout = self.layout
      obj = context.object
      row.scale_x=5
      row.scale_y=1.1
      
      row.operator("operador.root", text="Root")
      
      
      row = layout.row()
      row = layout.row()
      
      #FK to IK Brazo L
      
      layout = self.layout
      obj = context.object
      row.scale_x=5
      row.scale_y=1.1
      row.alignment = 'CENTER'
      
      
############################
## Math utility functions ##
############################

def perpendicular_vector(v):
    """ Returns a vector that is perpendicular to the one given.
        The returned vector is _not_ guaranteed to be normalized.
    """
    # Create a vector that is not aligned with v.
    # It doesn't matter what vector.  Just any vector
    # that's guaranteed to not be pointing in the same
    # direction.
    if abs(v[0]) < abs(v[1]):
        tv = Vector((1,0,0))
    else:
        tv = Vector((0,1,0))

    # Use cross prouct to generate a vector perpendicular to
    # both tv and (more importantly) v.
    return v.cross(tv)


def rotation_difference(mat1, mat2):
    """ Returns the shortest-path rotational difference between two
        matrices.
    """
    q1 = mat1.to_quaternion()
    q2 = mat2.to_quaternion()
    angle = acos(min(1,max(-1,q1.dot(q2)))) * 2
    if angle > pi:
        angle = -angle + (2*pi)
    return angle


#########################################
## "Visual Transform" helper functions ##
#########################################

def get_pose_matrix_in_other_space(mat, pose_bone):
    """ Returns the transform matrix relative to pose_bone's current
        transform space.  In other words, presuming that mat is in
        armature space, slapping the returned matrix onto pose_bone
        should give it the armature-space transforms of mat.
        TODO: try to handle cases with axis-scaled parents better.
    """
    rest = pose_bone.bone.matrix_local.copy()
    rest_inv = rest.inverted()
    if pose_bone.parent:
        par_mat = pose_bone.parent.matrix.copy()
        par_inv = par_mat.inverted()
        par_rest = pose_bone.parent.bone.matrix_local.copy()
    else:
        par_mat = Matrix()
        par_inv = Matrix()
        par_rest = Matrix()

    # Get matrix in bone's current transform space
    smat = rest_inv * (par_rest * (par_inv * mat))

    # Compensate for non-local location
    #if not pose_bone.bone.use_local_location:
    #    loc = smat.to_translation() * (par_rest.inverted() * rest).to_quaternion()
    #    smat.translation = loc

    return smat


def get_local_pose_matrix(pose_bone):
    """ Returns the local transform matrix of the given pose bone.
    """
    return get_pose_matrix_in_other_space(pose_bone.matrix, pose_bone)


def set_pose_translation(pose_bone, mat):
    """ Sets the pose bone's translation to the same translation as the given matrix.
        Matrix should be given in bone's local space.
    """
    if pose_bone.bone.use_local_location == True:
        pose_bone.location = mat.to_translation()
    else:
        loc = mat.to_translation()

        rest = pose_bone.bone.matrix_local.copy()
        if pose_bone.bone.parent:
            par_rest = pose_bone.bone.parent.matrix_local.copy()
        else:
            par_rest = Matrix()

        q = (par_rest.inverted() * rest).to_quaternion()
        pose_bone.location = q * loc


def set_pose_rotation(pose_bone, mat):
    """ Sets the pose bone's rotation to the same rotation as the given matrix.
        Matrix should be given in bone's local space.
    """
    q = mat.to_quaternion()

    if pose_bone.rotation_mode == 'QUATERNION':
        pose_bone.rotation_quaternion = q
    elif pose_bone.rotation_mode == 'AXIS_ANGLE':
        pose_bone.rotation_axis_angle[0] = q.angle
        pose_bone.rotation_axis_angle[1] = q.axis[0]
        pose_bone.rotation_axis_angle[2] = q.axis[1]
        pose_bone.rotation_axis_angle[3] = q.axis[2]
    else:
        pose_bone.rotation_euler = q.to_euler(pose_bone.rotation_mode)


def set_pose_scale(pose_bone, mat):
    """ Sets the pose bone's scale to the same scale as the given matrix.
        Matrix should be given in bone's local space.
    """
    pose_bone.scale = mat.to_scale()


def match_pose_translation(pose_bone, target_bone):
    """ Matches pose_bone's visual translation to target_bone's visual
        translation.
        This function assumes you are in pose mode on the relevant armature.
    """
    mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
    set_pose_translation(pose_bone, mat)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def match_pose_rotation(pose_bone, target_bone):
    """ Matches pose_bone's visual rotation to target_bone's visual
        rotation.
        This function assumes you are in pose mode on the relevant armature.
    """
    mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
    set_pose_rotation(pose_bone, mat)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def match_pose_scale(pose_bone, target_bone):
    """ Matches pose_bone's visual scale to target_bone's visual
        scale.
        This function assumes you are in pose mode on the relevant armature.
    """
    mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
    set_pose_scale(pose_bone, mat)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


##############################
## IK/FK snapping functions ##
##############################

def match_pole_target(ik_first, ik_last, pole, match_bone, length):
    """ Places an IK chain's pole target to match ik_first's
        transforms to match_bone.  All bones should be given as pose bones.
        You need to be in pose mode on the relevant armature object.
        ik_first: first bone in the IK chain
        ik_last:  last bone in the IK chain
        pole:  pole target bone for the IK chain
        match_bone:  bone to match ik_first to (probably first bone in a matching FK chain)
        length:  distance pole target should be placed from the chain center
    """
    a = ik_first.matrix.to_translation()
    b = ik_last.matrix.to_translation() + ik_last.vector

    # Vector from the head of ik_first to the
    # tip of ik_last
    ikv = b - a

    # Get a vector perpendicular to ikv
    pv = perpendicular_vector(ikv).normalized() * length

    def set_pole(pvi):
        """ Set pole target's position based on a vector
            from the arm center line.
        """
        # Translate pvi into armature space
        ploc = a + (ikv/2) + pvi

        # Set pole target to location
        mat = get_pose_matrix_in_other_space(Matrix.Translation(ploc), pole)
        set_pose_translation(pole, mat)

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')

    set_pole(pv)

    # Get the rotation difference between ik_first and match_bone
    angle = rotation_difference(ik_first.matrix, match_bone.matrix)

    # Try compensating for the rotation difference in both directions
    pv1 = Matrix.Rotation(angle, 4, ikv) * pv
    set_pole(pv1)
    ang1 = rotation_difference(ik_first.matrix, match_bone.matrix)

    pv2 = Matrix.Rotation(-angle, 4, ikv) * pv
    set_pole(pv2)
    ang2 = rotation_difference(ik_first.matrix, match_bone.matrix)

    # Do the one with the smaller angle
    if ang1 < ang2:
        set_pole(pv1)


def fk2ik_arm(obj, fk, ik):
    """ Matches the fk bones in an arm rig to the ik bones.
        obj: armature object
        fk:  list of fk bone names
        ik:  list of ik bone names
    """
    uarm  = obj.pose.bones[fk[0]]
    farm  = obj.pose.bones[fk[1]]
    hand  = obj.pose.bones[fk[2]]
    uarmi = obj.pose.bones[ik[0]]
    farmi = obj.pose.bones[ik[1]]
    handi = obj.pose.bones[ik[2]]

    # Stretch
    if handi['auto_stretch'] == 0.0:
        uarm['stretch_length'] = handi['stretch_length']
    else:
        diff = (uarmi.vector.length + farmi.vector.length) / (uarm.vector.length + farm.vector.length)
        uarm['stretch_length'] *= diff

    # Upper arm position
    match_pose_rotation(uarm, uarmi)
    match_pose_scale(uarm, uarmi)

    # Forearm position
    match_pose_rotation(farm, farmi)
    match_pose_scale(farm, farmi)

    # Hand position
    match_pose_rotation(hand, handi)
    match_pose_scale(hand, handi)


def ik2fk_arm(obj, fk, ik):
    """ Matches the ik bones in an arm rig to the fk bones.
        obj: armature object
        fk:  list of fk bone names
        ik:  list of ik bone names
    """
    uarm  = obj.pose.bones[fk[0]]
    farm  = obj.pose.bones[fk[1]]
    hand  = obj.pose.bones[fk[2]]
    uarmi = obj.pose.bones[ik[0]]
    farmi = obj.pose.bones[ik[1]]
    handi = obj.pose.bones[ik[2]]
    pole  = obj.pose.bones[ik[3]]

    # Stretch
    handi['stretch_length'] = uarm['stretch_length']

    # Hand position
    match_pose_translation(handi, hand)
    match_pose_rotation(handi, hand)
    match_pose_scale(handi, hand)

    # Pole target position
    match_pole_target(uarmi, farmi, pole, uarm, (uarmi.length + farmi.length))


def fk2ik_leg(obj, fk, ik):
    """ Matches the fk bones in a leg rig to the ik bones.
        obj: armature object
        fk:  list of fk bone names
        ik:  list of ik bone names
    """
    thigh  = obj.pose.bones[fk[0]]
    shin   = obj.pose.bones[fk[1]]
    foot   = obj.pose.bones[fk[2]]
    mfoot  = obj.pose.bones[fk[3]]
    thighi = obj.pose.bones[ik[0]]
    shini  = obj.pose.bones[ik[1]]
    footi  = obj.pose.bones[ik[2]]
    mfooti = obj.pose.bones[ik[3]]

    # Stretch
    if footi['auto_stretch'] == 0.0:
        thigh['stretch_length'] = footi['stretch_length']
    else:
        diff = (thighi.vector.length + shini.vector.length) / (thigh.vector.length + shin.vector.length)
        thigh['stretch_length'] *= diff

    # Thigh position
    match_pose_rotation(thigh, thighi)
    match_pose_scale(thigh, thighi)

    # Shin position
    match_pose_rotation(shin, shini)
    match_pose_scale(shin, shini)

    # Foot position
    mat = mfoot.bone.matrix_local.inverted() * foot.bone.matrix_local
    footmat = get_pose_matrix_in_other_space(mfooti.matrix, foot) * mat
    set_pose_rotation(foot, footmat)
    set_pose_scale(foot, footmat)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def ik2fk_leg(obj, fk, ik):
    """ Matches the ik bones in a leg rig to the fk bones.
        obj: armature object
        fk:  list of fk bone names
        ik:  list of ik bone names
    """
    thigh    = obj.pose.bones[fk[0]]
    shin     = obj.pose.bones[fk[1]]
    mfoot    = obj.pose.bones[fk[2]]
    thighi   = obj.pose.bones[ik[0]]
    shini    = obj.pose.bones[ik[1]]
    footi    = obj.pose.bones[ik[2]]
    footroll = obj.pose.bones[ik[3]]
    pole     = obj.pose.bones[ik[4]]
    mfooti   = obj.pose.bones[ik[5]]

    # Stretch
    footi['stretch_length'] = thigh['stretch_length']

    # Clear footroll
    set_pose_rotation(footroll, Matrix())

    # Foot position
    mat = mfooti.bone.matrix_local.inverted() * footi.bone.matrix_local
    footmat = get_pose_matrix_in_other_space(mfoot.matrix, footi) * mat
    set_pose_translation(footi, footmat)
    set_pose_rotation(footi, footmat)
    set_pose_scale(footi, footmat)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')

    # Pole target position
    match_pole_target(thighi, shini, pole, thigh, (thighi.length + shini.length))


##############################
## IK/FK snapping operators ##
##############################

class Rigify_Arm_FK2IK(bpy.types.Operator):
    """ Snaps an FK arm to an IK arm.
    """
    bl_idname = "pose.rigify_arm_fk2ik_" + rig_id
    bl_label = "Rigify Snap FK arm to IK"
    bl_options = {'UNDO'}

    uarm_fk = bpy.props.StringProperty(name="Upper Arm FK Name")
    farm_fk = bpy.props.StringProperty(name="Forerm FK Name")
    hand_fk = bpy.props.StringProperty(name="Hand FK Name")

    uarm_ik = bpy.props.StringProperty(name="Upper Arm IK Name")
    farm_ik = bpy.props.StringProperty(name="Forearm IK Name")
    hand_ik = bpy.props.StringProperty(name="Hand IK Name")

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.user_preferences.edit.use_global_undo
        context.user_preferences.edit.use_global_undo = False
        try:
            fk2ik_arm(context.active_object, fk=[self.uarm_fk, self.farm_fk, self.hand_fk], ik=[self.uarm_ik, self.farm_ik, self.hand_ik])
        finally:
            context.user_preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class Rigify_Arm_IK2FK(bpy.types.Operator):
    """ Snaps an IK arm to an FK arm.
    """
    bl_idname = "pose.rigify_arm_ik2fk_" + rig_id
    bl_label = "Rigify Snap IK arm to FK"
    bl_options = {'UNDO'}

    uarm_fk = bpy.props.StringProperty(name="Upper Arm FK Name")
    farm_fk = bpy.props.StringProperty(name="Forerm FK Name")
    hand_fk = bpy.props.StringProperty(name="Hand FK Name")

    uarm_ik = bpy.props.StringProperty(name="Upper Arm IK Name")
    farm_ik = bpy.props.StringProperty(name="Forearm IK Name")
    hand_ik = bpy.props.StringProperty(name="Hand IK Name")
    pole    = bpy.props.StringProperty(name="Pole IK Name")

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.user_preferences.edit.use_global_undo
        context.user_preferences.edit.use_global_undo = False
        try:
            ik2fk_arm(context.active_object, fk=[self.uarm_fk, self.farm_fk, self.hand_fk], ik=[self.uarm_ik, self.farm_ik, self.hand_ik, self.pole])
        finally:
            context.user_preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class Rigify_Leg_FK2IK(bpy.types.Operator):
    """ Snaps an FK leg to an IK leg.
    """
    bl_idname = "pose.rigify_leg_fk2ik_" + rig_id
    bl_label = "Rigify Snap FK leg to IK"
    bl_options = {'UNDO'}

    thigh_fk = bpy.props.StringProperty(name="Thigh FK Name")
    shin_fk  = bpy.props.StringProperty(name="Shin FK Name")
    foot_fk  = bpy.props.StringProperty(name="Foot FK Name")
    mfoot_fk = bpy.props.StringProperty(name="MFoot FK Name")

    thigh_ik = bpy.props.StringProperty(name="Thigh IK Name")
    shin_ik  = bpy.props.StringProperty(name="Shin IK Name")
    foot_ik  = bpy.props.StringProperty(name="Foot IK Name")
    mfoot_ik = bpy.props.StringProperty(name="MFoot IK Name")

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.user_preferences.edit.use_global_undo
        context.user_preferences.edit.use_global_undo = False
        try:
            fk2ik_leg(context.active_object, fk=[self.thigh_fk, self.shin_fk, self.foot_fk, self.mfoot_fk], ik=[self.thigh_ik, self.shin_ik, self.foot_ik, self.mfoot_ik])
        finally:
            context.user_preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class Rigify_Leg_IK2FK(bpy.types.Operator):
    """ Snaps an IK leg to an FK leg.
    """
    bl_idname = "pose.rigify_leg_ik2fk_" + rig_id
    bl_label = "Rigify Snap IK leg to FK"
    bl_options = {'UNDO'}

    thigh_fk = bpy.props.StringProperty(name="Thigh FK Name")
    shin_fk  = bpy.props.StringProperty(name="Shin FK Name")
    mfoot_fk = bpy.props.StringProperty(name="MFoot FK Name")

    thigh_ik = bpy.props.StringProperty(name="Thigh IK Name")
    shin_ik  = bpy.props.StringProperty(name="Shin IK Name")
    foot_ik  = bpy.props.StringProperty(name="Foot IK Name")
    footroll = bpy.props.StringProperty(name="Foot Roll Name")
    pole     = bpy.props.StringProperty(name="Pole IK Name")
    mfoot_ik = bpy.props.StringProperty(name="MFoot IK Name")

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')

    def execute(self, context):
        use_global_undo = context.user_preferences.edit.use_global_undo
        context.user_preferences.edit.use_global_undo = False
        try:
            ik2fk_leg(context.active_object, fk=[self.thigh_fk, self.shin_fk, self.mfoot_fk], ik=[self.thigh_ik, self.shin_ik, self.foot_ik, self.footroll, self.pole, self.mfoot_ik])
        finally:
            context.user_preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


###################
## Rig UI Panels ##
###################

class RigUI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Rig Main Properties"
    bl_idname = rig_id + "_PT_rig_ui"

    @classmethod
    def poll(self, context):
        if context.mode != 'POSE':
            return False
        try:
            return (context.active_object.data.get("rig_id") == rig_id)
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        pose_bones = context.active_object.pose.bones
        try:
            selected_bones = [bone.name for bone in context.selected_pose_bones]
            selected_bones += [context.active_pose_bone.name]
        except (AttributeError, TypeError):
            return

        def is_selected(names):
            # Returns whether any of the named bones are selected.
            if type(names) == list:
                for name in names:
                    if name in selected_bones:
                        return True
            elif names in selected_bones:
                return True
            return False



        
        main = "torso"
        spine = ['hips', 'spine', 'chest']
        if is_selected([main]+ spine):
            layout.prop(pose_bones[main], '["pivot_slide"]', text="Pivot Slide (" + main + ")", slider=True)
        
        for name in spine[1:-1]:
            if is_selected(name):
                layout.prop(pose_bones[name], '["auto_rotate"]', text="Auto Rotate (" + name + ")", slider=True)
        

        
        fk_leg = ["thigh.fk.L", "shin.fk.L", "foot.fk.L", "MCH-foot.L"]
        ik_leg = ["MCH-thigh.ik.L", "MCH-shin.ik.L", "foot.ik.L", "knee_target.ik.L", "foot_roll.ik.L", "MCH-foot.L.001"]
        if is_selected(fk_leg+ik_leg):
            layout.prop(pose_bones[ik_leg[2]], '["ikfk_switch"]', text="FK / IK (" + ik_leg[2] + ")", slider=True)
            p = layout.operator("pose.rigify_leg_fk2ik_" + rig_id, text="Snap FK->IK (" + fk_leg[0] + ")")
            p.thigh_fk = fk_leg[0]
            p.shin_fk  = fk_leg[1]
            p.foot_fk  = fk_leg[2]
            p.mfoot_fk = fk_leg[3]
            p.thigh_ik = ik_leg[0]
            p.shin_ik  = ik_leg[1]
            p.foot_ik = ik_leg[2]
            p.mfoot_ik = ik_leg[5]
            p = layout.operator("pose.rigify_leg_ik2fk_" + rig_id, text="Snap IK->FK (" + fk_leg[0] + ")")
            p.thigh_fk  = fk_leg[0]
            p.shin_fk   = fk_leg[1]
            p.mfoot_fk  = fk_leg[3]
            p.thigh_ik  = ik_leg[0]
            p.shin_ik   = ik_leg[1]
            p.foot_ik   = ik_leg[2]
            p.pole      = ik_leg[3]
            p.footroll  = ik_leg[4]
            p.mfoot_ik  = ik_leg[5]
        if is_selected(fk_leg):
            try:
                pose_bones[fk_leg[0]]["isolate"]
                layout.prop(pose_bones[fk_leg[0]], '["isolate"]', text="Isolate Rotation (" + fk_leg[0] + ")", slider=True)
            except KeyError:
                pass
            layout.prop(pose_bones[fk_leg[0]], '["stretch_length"]', text="Length FK (" + fk_leg[0] + ")", slider=True)
        if is_selected(ik_leg):
            layout.prop(pose_bones[ik_leg[2]], '["stretch_length"]', text="Length IK (" + ik_leg[2] + ")", slider=True)
            layout.prop(pose_bones[ik_leg[2]], '["auto_stretch"]', text="Auto-Stretch IK (" + ik_leg[2] + ")", slider=True)
        
        hose_leg = ["thigh_hose.L", "knee_hose.L", "shin_hose.L"]
        if is_selected(hose_leg):
            layout.prop(pose_bones[hose_leg[1]], '["smooth_bend"]', text="Smooth Knee (" + hose_leg[1] + ")", slider=True)
        
        if is_selected(fk_leg+ik_leg):
            layout.separator()
        

        
        fk_leg = ["thigh.fk.R", "shin.fk.R", "foot.fk.R", "MCH-foot.R"]
        ik_leg = ["MCH-thigh.ik.R", "MCH-shin.ik.R", "foot.ik.R", "knee_target.ik.R", "foot_roll.ik.R", "MCH-foot.R.001"]
        if is_selected(fk_leg+ik_leg):
            layout.prop(pose_bones[ik_leg[2]], '["ikfk_switch"]', text="FK / IK (" + ik_leg[2] + ")", slider=True)
            p = layout.operator("pose.rigify_leg_fk2ik_" + rig_id, text="Snap FK->IK (" + fk_leg[0] + ")")
            p.thigh_fk = fk_leg[0]
            p.shin_fk  = fk_leg[1]
            p.foot_fk  = fk_leg[2]
            p.mfoot_fk = fk_leg[3]
            p.thigh_ik = ik_leg[0]
            p.shin_ik  = ik_leg[1]
            p.foot_ik = ik_leg[2]
            p.mfoot_ik = ik_leg[5]
            p = layout.operator("pose.rigify_leg_ik2fk_" + rig_id, text="Snap IK->FK (" + fk_leg[0] + ")")
            p.thigh_fk  = fk_leg[0]
            p.shin_fk   = fk_leg[1]
            p.mfoot_fk  = fk_leg[3]
            p.thigh_ik  = ik_leg[0]
            p.shin_ik   = ik_leg[1]
            p.foot_ik   = ik_leg[2]
            p.pole      = ik_leg[3]
            p.footroll  = ik_leg[4]
            p.mfoot_ik  = ik_leg[5]
        if is_selected(fk_leg):
            try:
                pose_bones[fk_leg[0]]["isolate"]
                layout.prop(pose_bones[fk_leg[0]], '["isolate"]', text="Isolate Rotation (" + fk_leg[0] + ")", slider=True)
            except KeyError:
                pass
            layout.prop(pose_bones[fk_leg[0]], '["stretch_length"]', text="Length FK (" + fk_leg[0] + ")", slider=True)
        if is_selected(ik_leg):
            layout.prop(pose_bones[ik_leg[2]], '["stretch_length"]', text="Length IK (" + ik_leg[2] + ")", slider=True)
            layout.prop(pose_bones[ik_leg[2]], '["auto_stretch"]', text="Auto-Stretch IK (" + ik_leg[2] + ")", slider=True)
        
        hose_leg = ["thigh_hose.R", "knee_hose.R", "shin_hose.R"]
        if is_selected(hose_leg):
            layout.prop(pose_bones[hose_leg[1]], '["smooth_bend"]', text="Smooth Knee (" + hose_leg[1] + ")", slider=True)
        
        if is_selected(fk_leg+ik_leg):
            layout.separator()
        

        
        head_neck = ["head", "neck"]
        
        if is_selected(head_neck[0]):
            layout.prop(pose_bones[head_neck[0]], '["isolate"]', text="Isolate (" + head_neck[0] + ")", slider=True)
        
        if is_selected(head_neck):
            layout.prop(pose_bones[head_neck[0]], '["neck_follow"]', text="Neck Follow Head (" + head_neck[0] + ")", slider=True)
        

        
        fk_arm = ["upper_arm.fk.L", "forearm.fk.L", "hand.fk.L"]
        ik_arm = ["MCH-upper_arm.ik.L", "MCH-forearm.ik.L", "hand.ik.L", "elbow_target.ik.L"]
        if is_selected(fk_arm+ik_arm):
            layout.prop(pose_bones[ik_arm[2]], '["ikfk_switch"]', text="FK / IK (" + ik_arm[2] + ")", slider=True)
            props = layout.operator("pose.rigify_arm_fk2ik_" + rig_id, text="Snap FK->IK (" + fk_arm[0] + ")")
            props.uarm_fk = fk_arm[0]
            props.farm_fk = fk_arm[1]
            props.hand_fk = fk_arm[2]
            props.uarm_ik = ik_arm[0]
            props.farm_ik = ik_arm[1]
            props.hand_ik = ik_arm[2]
            props = layout.operator("pose.rigify_arm_ik2fk_" + rig_id, text="Snap IK->FK (" + fk_arm[0] + ")")
            props.uarm_fk = fk_arm[0]
            props.farm_fk = fk_arm[1]
            props.hand_fk = fk_arm[2]
            props.uarm_ik = ik_arm[0]
            props.farm_ik = ik_arm[1]
            props.hand_ik = ik_arm[2]
            props.pole = ik_arm[3]
        if is_selected(fk_arm):
            try:
                pose_bones[fk_arm[0]]["isolate"]
                layout.prop(pose_bones[fk_arm[0]], '["isolate"]', text="Isolate Rotation (" + fk_arm[0] + ")", slider=True)
            except KeyError:
                pass
            layout.prop(pose_bones[fk_arm[0]], '["stretch_length"]', text="Length FK (" + fk_arm[0] + ")", slider=True)
        if is_selected(ik_arm):
            layout.prop(pose_bones[ik_arm[2]], '["stretch_length"]', text="Length IK (" + ik_arm[2] + ")", slider=True)
            layout.prop(pose_bones[ik_arm[2]], '["auto_stretch"]', text="Auto-Stretch IK (" + ik_arm[2] + ")", slider=True)
        
        hose_arm = ["upper_arm_hose.L", "elbow_hose.L", "forearm_hose.L"]
        if is_selected(hose_arm):
            layout.prop(pose_bones[hose_arm[1]], '["smooth_bend"]', text="Smooth Elbow (" + hose_arm[1] + ")", slider=True)
        
        if is_selected(fk_arm+ik_arm):
            layout.separator()
        

        
        fk_arm = ["upper_arm.fk.R", "forearm.fk.R", "hand.fk.R"]
        ik_arm = ["MCH-upper_arm.ik.R", "MCH-forearm.ik.R", "hand.ik.R", "elbow_target.ik.R"]
        if is_selected(fk_arm+ik_arm):
            layout.prop(pose_bones[ik_arm[2]], '["ikfk_switch"]', text="FK / IK (" + ik_arm[2] + ")", slider=True)
            props = layout.operator("pose.rigify_arm_fk2ik_" + rig_id, text="Snap FK->IK (" + fk_arm[0] + ")")
            props.uarm_fk = fk_arm[0]
            props.farm_fk = fk_arm[1]
            props.hand_fk = fk_arm[2]
            props.uarm_ik = ik_arm[0]
            props.farm_ik = ik_arm[1]
            props.hand_ik = ik_arm[2]
            props = layout.operator("pose.rigify_arm_ik2fk_" + rig_id, text="Snap IK->FK (" + fk_arm[0] + ")")
            props.uarm_fk = fk_arm[0]
            props.farm_fk = fk_arm[1]
            props.hand_fk = fk_arm[2]
            props.uarm_ik = ik_arm[0]
            props.farm_ik = ik_arm[1]
            props.hand_ik = ik_arm[2]
            props.pole = ik_arm[3]
        if is_selected(fk_arm):
            try:
                pose_bones[fk_arm[0]]["isolate"]
                layout.prop(pose_bones[fk_arm[0]], '["isolate"]', text="Isolate Rotation (" + fk_arm[0] + ")", slider=True)
            except KeyError:
                pass
            layout.prop(pose_bones[fk_arm[0]], '["stretch_length"]', text="Length FK (" + fk_arm[0] + ")", slider=True)
        if is_selected(ik_arm):
            layout.prop(pose_bones[ik_arm[2]], '["stretch_length"]', text="Length IK (" + ik_arm[2] + ")", slider=True)
            layout.prop(pose_bones[ik_arm[2]], '["auto_stretch"]', text="Auto-Stretch IK (" + ik_arm[2] + ")", slider=True)
        
        hose_arm = ["upper_arm_hose.R", "elbow_hose.R", "forearm_hose.R"]
        if is_selected(hose_arm):
            layout.prop(pose_bones[hose_arm[1]], '["smooth_bend"]', text="Smooth Elbow (" + hose_arm[1] + ")", slider=True)
        
        if is_selected(fk_arm+ik_arm):
            layout.separator()
        

class RigLayers(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Rig Layers"
    bl_idname = rig_id + "_PT_rig_layers"

    @classmethod
    def poll(self, context):
        try:
            return (context.active_object.data.get("rig_id") == rig_id)
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=0, toggle=True, text='head')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=2, toggle=True, text='Torso')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=4, toggle=True, text='Fingers')
        row.prop(context.active_object.data, 'layers', index=5, toggle=True, text='(Tweak)')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=6, toggle=True, text='Arm.L (FK)')
        row.prop(context.active_object.data, 'layers', index=9, toggle=True, text='Arm.R (FK)')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=7, toggle=True, text='Arm.L (IK)')
        row.prop(context.active_object.data, 'layers', index=10, toggle=True, text='Arm.R (IK)')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=8, toggle=True, text='Arm.L (Tweak)')
        row.prop(context.active_object.data, 'layers', index=11, toggle=True, text='Arm.R (Tweak)')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=12, toggle=True, text='Leg.L (FK)')
        row.prop(context.active_object.data, 'layers', index=15, toggle=True, text='Leg.R (FK)')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=13, toggle=True, text='Leg.L (IK)')
        row.prop(context.active_object.data, 'layers', index=16, toggle=True, text='Leg.R (IK)')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=14, toggle=True, text='Leg.L (Tweak)')
        row.prop(context.active_object.data, 'layers', index=17, toggle=True, text='Leg.R (Tweak)')

        row = col.row()
        row.separator()
        row = col.row()
        row.separator()

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=28, toggle=True, text='Root')



      
      
      
      
def register():
      
        bpy.utils.register_class(OperadorCabeza) 
        bpy.utils.register_class(OperadorCuello)
        bpy.utils.register_class(OperadorCostillas)
        bpy.utils.register_class(OperadorClaviculaL) 
        bpy.utils.register_class(OperadorClaviculaR)   
        bpy.utils.register_class(OperadorColumna)
        bpy.utils.register_class(OperadorTorso)  
        bpy.utils.register_class(OperadorCadera)
        bpy.utils.register_class(OperadorBrazoFKL)
        bpy.utils.register_class(OperadorBrazoFKR)
        bpy.utils.register_class(OperadorAntebrazoFKL)
        bpy.utils.register_class(OperadorAntebrazoFKR)
        bpy.utils.register_class(OperadorManoL)
        bpy.utils.register_class(OperadorManoR)
        bpy.utils.register_class(OperadorManoFKL)
        bpy.utils.register_class(OperadorManoFKR)
        bpy.utils.register_class(OperadorBrazoSumL)
        bpy.utils.register_class(OperadorBrazoSumR)
        bpy.utils.register_class(OperadorPiernaSumL)
        bpy.utils.register_class(OperadorPiernaSumR)
        bpy.utils.register_class(OperadorCodoIKR)
        bpy.utils.register_class(OperadorCodoIKL)
        bpy.utils.register_class(OperadorPiernaL)
        bpy.utils.register_class(OperadorPiernaR)
        bpy.utils.register_class(OperadorTibiaL)
        bpy.utils.register_class(OperadorTibiaR)
        bpy.utils.register_class(OperadorPieL)
        bpy.utils.register_class(OperadorPieFKL)
        bpy.utils.register_class(OperadorPieR)
        bpy.utils.register_class(OperadorPieFKR)
        bpy.utils.register_class(OperadorTobilloL)
        bpy.utils.register_class(OperadorTobilloR)
        bpy.utils.register_class(OperadorPuntaL)
        bpy.utils.register_class(OperadorPuntaR)
        bpy.utils.register_class(OperadorRodillaL)
        bpy.utils.register_class(OperadorRodillaR)
        bpy.utils.register_class(ThePanel) 
        bpy.utils.register_class(OperadorRoot) 
        bpy.utils.register_class(OperadorFKtoIK_BrazoL) 
        bpy.utils.register_class(OperadorIKtoFK_BrazoL) 
        bpy.utils.register_class(OperadorFKtoIK_BrazoR)
        bpy.utils.register_class(OperadorIKtoFK_BrazoR)
        bpy.utils.register_class(OperadorFKtoIK_PiernaL) 
        bpy.utils.register_class(OperadorIKtoFK_PiernaL) 
        bpy.utils.register_class(OperadorFKtoIK_PiernaR)
        bpy.utils.register_class(OperadorIKtoFK_PiernaR)
        bpy.utils.register_class(Rigify_Arm_FK2IK)
        bpy.utils.register_class(Rigify_Arm_IK2FK)
        bpy.utils.register_class(Rigify_Leg_FK2IK)
        bpy.utils.register_class(Rigify_Leg_IK2FK)
        bpy.utils.register_class(RigUI)
        bpy.utils.register_class(RigLayers)
        
        
        

def unregister():

        bpy.utils.unregister_class(OperadorCabeza) 
        bpy.utils.unregister_class(OperadorCuello)
        bpy.utils.unregister_class(OperadorCostillas)
        bpy.utils.unregister_class(OperadorClaviculaL) 
        bpy.utils.unregister_class(OperadorClaviculaR)   
        bpy.utils.unregister_class(OperadorColumna)
        bpy.utils.unregister_class(OperadorTorso)  
        bpy.utils.unregister_class(OperadorCadera)
        bpy.utils.unregister_class(OperadorBrazoFKL)
        bpy.utils.unregister_class(OperadorBrazoFKR)
        bpy.utils.unregister_class(OperadorAntebrazoFKL)
        bpy.utils.unregister_class(OperadorAntebrazoFKR)
        bpy.utils.unregister_class(OperadorManoL)
        bpy.utils.unregister_class(OperadorManoR)
        bpy.utils.unregister_class(OperadorManoFKL)
        bpy.utils.unregister_class(OperadorManoFKR)
        bpy.utils.unregister_class(OperadorBrazoSumL)
        bpy.utils.unregister_class(OperadorBrazoSumR)
        bpy.utils.unregister_class(OperadorPiernaSumL)
        bpy.utils.unregister_class(OperadorPiernaSumR)
        bpy.utils.unregister_class(OperadorCodoIKR)
        bpy.utils.unregister_class(OperadorCodoIKL)
        bpy.utils.unregister_class(OperadorPiernaL)
        bpy.utils.unregister_class(OperadorPiernaR)
        bpy.utils.unregister_class(OperadorTibiaL)
        bpy.utils.unregister_class(OperadorTibiaR)
        bpy.utils.unregister_class(OperadorPieL)
        bpy.utils.unregister_class(OperadorPieFKL)
        bpy.utils.unregister_class(OperadorPieR)
        bpy.utils.unregister_class(OperadorPieFKR)
        bpy.utils.unregister_class(OperadorTobilloL)
        bpy.utils.unregister_class(OperadorTobilloR)
        bpy.utils.unregister_class(OperadorPuntaL)
        bpy.utils.unregister_class(OperadorPuntaR)
        bpy.utils.unregister_class(OperadorRodillaL)
        bpy.utils.unregister_class(OperadorRodillaR)
        bpy.utils.unregister_class(ThePanel)  
        bpy.utils.unregister_class(OperadorRoot) 
        bpy.utils.unregister_class(OperadorFKtoIK_BrazoL) 
        bpy.utils.unregister_class(OperadorIKtoFK_BrazoL)
        bpy.utils.unregister_class(OperadorFKtoIK_BrazoR)
        bpy.utils.unregister_class(OperadorIKtoFK_BrazoR)
        bpy.utils.unregister_class(OperadorFKtoIK_PiernaL) 
        bpy.utils.unregister_class(OperadorIKtoFK_PiernaL) 
        bpy.utils.unregister_class(OperadorFKtoIK_PiernaR)
        bpy.utils.unregister_class(OperadorIKtoFK_PiernaR)
        bpy.utils.unregister_class(Rigify_Arm_FK2IK)
        bpy.utils.unregister_class(Rigify_Arm_IK2FK)
        bpy.utils.unregister_class(Rigify_Leg_FK2IK)
        bpy.utils.unregister_class(Rigify_Leg_IK2FK)
        bpy.utils.unregister_class(RigUI)
        bpy.utils.unregister_class(RigLayers)
        
if __name__ == "__main__":
    register()

        






    
    
    

     
    

 
      
     
      
     
      
      
      
      
      
      
      


