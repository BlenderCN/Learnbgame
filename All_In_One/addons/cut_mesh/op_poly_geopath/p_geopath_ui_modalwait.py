'''
Created on Oct 11, 2015

@author: Patrick
'''
from ..common.blender import show_error_message

class PGeopath_UI_ModalWait():
    
    def modal_wait(self,context,eventd):
        # general navigation
        nmode = self.modal_nav(context, eventd)
        if nmode != '':
            return nmode  #stop here and tell parent modal to 'PASS_THROUGH'

        #after navigation filter, these are relevant events in this state
        if eventd['press'] == 'G':
            context.area.header_text_set("'MoveMouse'and 'LeftClick' to adjust node location, Right Click to cancel the grab")
            if self.knife.grab_initiate():
                return 'grab'
            else:
                #need to select a point
                return 'main'
        
        if  eventd['type'] == 'MOUSEMOVE':
            x,y = eventd['mouse']
            self.knife.hover(context, x, y)    
            return 'main'
        
        if  eventd['press'] == 'LEFTMOUSE':
            x,y = eventd['mouse']
            self.knife.click_add_point(context, x,y)  #takes care of selection too
            if self.knife.ui_type == 'DENSE_POLY' and self.knife.hovered[0] == 'POINT':
                self.sketch = [(x,y)]
                return 'sketch'
            return 'main'
        
        if eventd['press'] == 'RIGHTMOUSE':
            if self.knife.start_edge != None and self.knife.hovered[1] == 0:
                show_error_message('Can not delete the first point for this kind of cut.')
                return 'main'
            self.knife.click_delete_point(mode = 'mouse')
            if len(self.knife.new_cos):
                self.knife.make_geodesic_cut()
            return 'main'
                
        if eventd['press'] == 'C':
            if self.knife.start_edge != None and self.knife.end_edge == None:
                show_error_message('Cut starts on non manifold boundary of mesh and must end on non manifold boundary')
            
            if self.knife.start_edge == None and not self.knife.cyclic:
                show_error_message('Cut starts within mesh.  Cut must be closed loop.  Click the first point to close the loop')
                    
            self.knife.make_geodesic_cut()
            context.area.header_text_set("Red segments have cut failures, modify polyline to fix.  When ready press 'S' to set seed point")
        
            return 'main' 
            
        if eventd['press'] == 'K':     
            if self.knife.split and self.knife.face_seed and len(self.knife.ed_map):
                self.knife.split_geometry(eventd['context'], mode = 'KNIFE')
                return 'finish' 
        
        if eventd['press'] == 'P':
            #self.knife.preview_mesh(eventd['context'])
            self.knife.split_geometry(eventd['context'], mode = 'SEPARATE')
            return 'finish'
        
        if eventd['press'] == 'X':
            self.knife.split_geometry(eventd['context'], mode = 'DELETE')
            return 'finish'
        
        if eventd['press'] == 'Y':
            self.knife.split_geometry(eventd['context'], mode = 'SPLIT')
            return 'finish'
        
        if eventd['press'] == 'SHIFT+D':
            self.knife.split_geometry(eventd['context'], mode = 'DUPLICATE')
            return 'finish'
            
        if eventd['press'] == 'S':
            if len(self.knife.bad_segments) != 0:
                show_error_message('Cut has failed segments shown in red.  Move the red segment slightly or add cut nodes to avoid bad part of mesh')
                context.area.header_text_set("Fix Red segments by moving control points then press 'S'")
                return 'main'
            
            if self.knife.start_edge == None and not self.knife.cyclic:
                show_error_message('Finish closing cut boundary loop')
                return 'main'
            elif self.knife.start_edge != None and self.knife.end_edge == None:
                show_error_message('Finish cutting to another non-manifold boundary/edge of the object')
                return 'main'
            elif len(self.knife.new_cos) == 0:
                show_error_message('Press "C" to preview the cut success before setting the seed')
                return 'main'
            
            context.window.cursor_modal_set('EYEDROPPER')
            context.area.header_text_set("Left Click Region to select area to cut")
            return 'inner'
          
        if eventd['press'] == 'RET' :
            self.knife.confirm_cut_to_mesh()
            return 'finish'
            
        elif eventd['press'] == 'ESC':
            return 'cancel' 

        return 'main'
    
    def modal_grab(self,context,eventd):
        # no navigation in grab mode
        
        if eventd['press'] == 'LEFTMOUSE':
            #confirm location
            self.knife.grab_confirm()
            
            if len(self.knife.bad_segments):
                self.knife.make_geodesic_cut()
            elif len(self.knife.new_cos) and (self.knife.cyclic or (self.knife.start_edge != None and self.knife.end_edge != None)):
                self.knife.make_geodesic_cut()
            
            if len(self.knife.new_cos) and len(self.knife.bad_segments) == 0:
                context.area.header_text_set("Poly Trim.  When cut is satisfactory, press 'S' then 'LeftMouse' in region to cut")
            elif len(self.knife.new_cos) and len(self.knife.bad_segments) != 0:
                context.area.header_text_set("Poly Trim.  Fix Bad segments so that no segments are red!")
            
            else: 
                context.area.header_text_set("Poly Trim.  Left click to place cut points on the mesh, then press 'C' to preview the cut")
            
            return 'main'
        
        elif eventd['press'] in {'RIGHTMOUSE', 'ESC'}:
            #put it back!
            self.knife.grab_cancel()
            
            if len(self.knife.new_cos):
                context.area.header_text_set("Poly Trim.  When cut is satisfactory, press 'S' then 'LeftMouse' in region to cut")
            elif len(self.knife.new_cos) and len(self.bad_segments) != 0:
                context.area.header_text_set("Poly Trim.  Fix Bad segments so that no segments are red!")
            else: 
                context.area.header_text_set("Poly Trim.  Left click to place cut points on the mesh, then press 'C' to preview the cut")
            return 'main'
        
        elif eventd['type'] == 'MOUSEMOVE':
            #update the b_pt location
            x,y = eventd['mouse']
            self.knife.grab_mouse_move(context,x, y)
            return 'grab'
    
    def modal_sketch(self,context,eventd):
        if eventd['type'] == 'MOUSEMOVE':
            x,y = eventd['mouse']
            if not len(self.sketch):
                return 'main'
            (lx, ly) = self.sketch[-1]
            ss0,ss1 = self.stroke_smoothing ,1-self.stroke_smoothing
            self.sketch += [(lx*ss0+x*ss1, ly*ss0+y*ss1)]
            return 'sketch'
        
        elif eventd['release'] == 'LEFTMOUSE':
            self.sketch_confirm(context, eventd)
            self.sketch = []
            return 'main'
        
    def modal_inner(self,context,eventd):
        
        if eventd['press'] == 'LEFTMOUSE':
            
            x,y = eventd['mouse']
            result = self.knife.click_seed_select(context, x,y) 
            if result == 1:
                context.window.cursor_modal_set('CROSSHAIR')
                
                if len(self.knife.new_cos) and len(self.knife.bad_segments) == 0 and not self.knife.split:
                    self.knife.confirm_cut_to_mesh_no_ops()
                    context.area.header_text_set("X:delete, P:separate, SHIFT+D:duplicate, K:knife, Y:split")
                return 'main'
            
            elif result == -1:
                show_error_message('Seed is too close to cut boundary, try again more interior to the cut')
                return 'inner'
            else:
                show_error_message('Seed not found, try again')
                return 'inner'
        
        if eventd['press'] in {'RET', 'ESC'}:
            return 'main'
            
        if eventd['press'] == 'S':
            return 'main'
          
        if eventd['press'] == 'RET' :
            return 'finish'
            
        elif eventd['press'] == 'ESC':
            return 'cancel' 

        return 'main'
    
    def modal_grab(self,context,eventd):
        # no navigation in grab mode
        
        if eventd['press'] == 'LEFTMOUSE':
            #confirm location
            self.geopath.grab_confirm()
            return 'main'
        
        elif eventd['press'] in {'RIGHTMOUSE', 'ESC'}:
            #put it back!
            self.geopath.grab_cancel()
            return 'main'
        
        elif eventd['type'] == 'MOUSEMOVE':
            #update the b_pt location
            x,y = eventd['mouse']
            self.geopath.grab_mouse_move(context,x, y)
            return 'grab'
