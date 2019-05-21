'''
Created on Oct 8, 2015

@author: Patrick
'''
from .. import common_drawing


class Slice_UI_Draw():
    def draw_postview(self, context):
        ''' Place post view drawing code in here '''
        self.draw_3d(context)
        pass
    
    def draw_postpixel(self, context):
        ''' Place post pixel drawing code in here '''
        self.draw_2d(context)
        pass
    
    def draw_3d(self,context):
        pass
    
    def draw_2d(self,context):
        self.slice.draw(context)