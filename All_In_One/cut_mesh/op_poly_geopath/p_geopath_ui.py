'''
Created on Oct 8, 2015

@author: Patrick
'''
import copy

import bpy
import bmesh
from mathutils import Matrix, Vector

from .p_geopath_datastructure import PolyGeodesicPath
from .cache import p_geopath_undo_cache

class PGeopath_UI:
    
    def start_ui(self, context):
        
        self.stroke_smoothing = 0.75          # 0: no smoothing. 1: no change
        self.mode_pos        = (0, 0)
        self.cur_pos         = (0, 0)
        self.mode_radius     = 0
        self.action_center   = (0, 0)
        self.is_navigating   = False
        self.sketch_curpos   = (0, 0)
        self.sketch          = []
        
        self.knife = PolyGeodesicPath(context,context.object)
        context.window.cursor_modal_set('CROSSHAIR')
        context.area.header_text_set("Poly Trim.  Left click to place cut points on the mesh, then press 'C' to preview the cut")
        
    def end_ui(self, context):            
        context.area.header_text_set()
        context.window.cursor_modal_restore()
        
    def cleanup(self, context, cleantype=''):
        '''
        remove temporary object
        '''
        if cleantype == 'commit':
            pass

        elif cleantype == 'cancel':
            pass
    ###############################
    # undo functions
    def create_undo_snapshot(self, action):
        '''
        unsure about all the _timers get deep copied
        and if sel_gedges and verts get copied as references
        or also duplicated, making them no longer valid.
        '''

        p_data = copy.deepcopy(self.polytrim)
        p_geopath_undo_cache.append((p_data, action))

        if len(p_geopath_undo_cache) > 10:
            p_geopath_undo_cache.pop(0)

    def undo_action(self):
        '''
        '''
        if len(p_geopath_undo_cache) > 0:
            data, action = p_geopath_undo_cache.pop()

            self.polytrim = data[0]

    def create_polytrim_from_bezier(self, ob_bezier):
        #TODO, read al the bezier points or interp the bezier?
        return
        
    def create_polytrim_from_vert_loop(self, ob_bezier):
        #TODO, read all the mesh data in and make a polylineknife
        return