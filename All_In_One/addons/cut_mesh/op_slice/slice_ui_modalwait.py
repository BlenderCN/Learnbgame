'''
Created on Oct 11, 2015

@author: Patrick
'''
class Slice_UI_ModalWait():
    
    def modal_wait(self,context,eventd):
        # general navigation
        nmode = self.modal_nav(context, eventd)
        if nmode != '':
            return nmode  #stop here and tell parent modal to 'PASS_THROUGH'

        #after navigation filter, these are relevant events in this state
        if eventd['press'] == 'G':
            if self.slice.grab_initiate():
                return 'grab'
            else:
                #need to select a point
                return 'main'
        
        if  eventd['press'] == 'LEFTMOUSE':
            x,y = eventd['mouse']
            
            if self.slice.seed != None:
                self.slice.click_add_target(context, x,y)
            else:
                self.slice.click_add_seed(context, x,y)  #takes care of selection too
            return 'main'
        
        if eventd['press'] == 'RIGHTMOUSE':
            
            return 'main'
        
        if eventd['press'] == 'X':
            
            return 'main'
        
        if eventd['press'] == 'C':
            return 'main' 
        if eventd['press'] == 'D':
            return 'main' 
            
        if eventd['press'] == 'E':                
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
            self.slice.grab_confirm()
            return 'main'
        
        elif eventd['press'] in {'RIGHTMOUSE', 'ESC'}:
            #put it back!
            self.slice.grab_cancel()
            return 'main'
        
        elif eventd['type'] == 'MOUSEMOVE':
            #update the b_pt location
            x,y = eventd['mouse']
            self.slice.grab_mouse_move(context,x, y)
            return 'grab'
