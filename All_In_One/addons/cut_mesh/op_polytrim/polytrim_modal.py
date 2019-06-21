'''
Created on Oct 8, 2015

@author: Patrick
'''
from ..modaloperator import ModalOperator
from .polytrim_ui            import Polytrim_UI
from .polytrim_ui_modalwait  import Polytrim_UI_ModalWait
from .polytrim_ui_tools      import Polytrim_UI_Tools
from .polytrim_ui_draw       import Polytrim_UI_Draw


class CutMesh_Polytrim(ModalOperator, Polytrim_UI, Polytrim_UI_ModalWait, Polytrim_UI_Tools, Polytrim_UI_Draw):
    ''' Cut Mesh Polytrim Modal Editor '''
    ''' Note: the functionality of this operator is split up over multiple base classes '''
    
    operator_id    = "cut_mesh.polytrim"    # operator_id needs to be the same as bl_idname
                                            # important: bl_idname is mangled by Blender upon registry :(
    bl_idname      = "cut_mesh.polytrim"
    bl_label       = "Polytrim"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'REGISTER','UNDO'}
    
    def __init__(self):
        FSM = {}
        FSM['sketch']  = self.modal_sketch
        FSM['grab']    = self.modal_grab
        FSM['select']  = self.modal_select
        FSM['inner']   = self.modal_inner
        self.initialize(FSM)
    
    def start_poll(self, context):
        ''' Called when tool is invoked to determine if tool can start '''
                
        if context.mode != 'OBJECT':
            #show_error_message('Object Mode please')
            return False
        
        if not context.object:
            return False
        
        if context.object.type != 'MESH':
            #show_error_message('Must select a mesh object')
            return False
        
        
        return True
    
    def start(self, context):
        ''' Called when tool is invoked '''
        self.start_ui(context)
    
    def end(self, context):
        ''' Called when tool is ending modal '''
        self.end_ui(context)
    
    def end_commit(self, context):
        ''' Called when tool is committing '''
        
        
        self.cleanup(context, 'commit')
    
    def end_cancel(self, context):
        ''' Called when tool is canceled '''
        self.cleanup(context, 'cancel')
        pass
    
    def update(self, context):
        pass