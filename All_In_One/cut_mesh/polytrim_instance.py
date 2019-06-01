'''
Created on Nov 25, 2018

@author: Patrick


This is sample operator where the bas Polytrim segmentation operator can be
modified and customized for a specific purpose
'''

from .op_polytrim.polytrim import CutMesh_Polytrim

# make our own copy of CutMesh_Polytrim so we don't overlap
# any other classes that subclass CutMesh_Polytrim
CutMesh_Polytrim_copy = type(
    'CutMesh_Polytrim_copy',
    CutMesh_Polytrim.__bases__,
    dict(CutMesh_Polytrim.__dict__)
    )

class Custom_Polytrim(CutMesh_Polytrim_copy):
    ''' Cut Mesh Polytrim Modal Editor '''
    ''' Note: the functionality of this operator is split up over multiple base classes '''

    operator_id    = "cut_mesh.custom_polytrim"    # operator_id needs to be the same as bl_idname
                                            # important: bl_idname is mangled by Blender upon registry :(
    bl_idname      = "cut_mesh.custom_polytrim"
    bl_label       = "Polytrim Custom"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'REGISTER','UNDO'}
    
    
    #custom poll:
        #check for existence of particular objects
        #check for certain prerequisites in the work-flow
        
    #customs startup
        #might want to hand the operator a source object in a very prescribed way instead 
        #of context or selection
        
        #set sensitivity, error thresholds etc if know source shape and density
        
        #set destructive/non-destructive mode
        
        #set which operations are allowed after compute cut before end_commit
            #Allow_delete
            #Allow_separate
            #Alloe duplicate
            #In fact all these may be false if the segments have a well defined destination
    
    #Custom end_commit
        #most likely the regions/segments have well defined destination and all the options
        #to delete/split/separate do not need exposure to the user
        
        #for example we may be deleting all segments (Trimming)
        #All segements may have a single obect destination (Appliance)
        #All segments may be have separate object destinations (Cutting Individual Teeth)