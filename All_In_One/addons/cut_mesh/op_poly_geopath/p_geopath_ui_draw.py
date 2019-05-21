'''
Created on Oct 8, 2015

@author: Patrick
'''
from .. import common_drawing


class PGeopath_UI_Draw():
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
        self.knife.draw(context)
        
        if len(self.sketch):
            common_drawing.draw_polyline_from_points(context, self.sketch, (.8,.3,.3,.8), 2, "GL_LINE_SMOOTH")