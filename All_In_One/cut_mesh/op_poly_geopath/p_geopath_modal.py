'''
Created on Oct 8, 2015

@author: Patrick
'''
from ..modaloperator import ModalOperator
from .p_geopath_ui           import PGeopath_UI
from .p_geopath_ui_modalwait  import PGeopath_UI_ModalWait
from .p_geopath_ui_draw       import PGeopath_UI_Draw
from .p_geopath_ui_tools     import PGeopath_UI_Tools


class CutMesh_PGeopath(ModalOperator, PGeopath_UI, PGeopath_UI_ModalWait, PGeopath_UI_Tools, PGeopath_UI_Draw):
    ''' Cut Mesh Polytrim Modal Editor '''
    ''' Note: the functionality of this operator is split up over multiple base classes '''
    
    operator_id    = "cut_mesh.polygeopath" # operator_id needs to be the same as bl_idname
                                            # important: bl_idname is mangled by Blender upon registry :(
    bl_idname      = "cut_mesh.polygeopath"
    bl_label       = "Poly Geopath"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'REGISTER','UNDO'}
    
    def __init__(self):
        FSM = {}
        FSM['sketch']  = self.modal_sketch
        FSM['grab']    = self.modal_grab
        FSM['inner']   = self.modal_inner

        ModalOperator.initialize(self, FSM)
    
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