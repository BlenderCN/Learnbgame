'''
Created on Oct 10, 2015

@author: Patrick
'''
import math
from ..common.rays import ray_cast_path
from ..common.maths import get_path_length, space_evenly_on_path
from bpy_extras import view3d_utils

class PGeopath_UI_Tools():
    
    def sketch_confirm(self, context, eventd):
        print('sketch confirmed')
        if len(self.sketch) < 5 and self.knife.ui_type == 'DENSE_POLY':
            print('sketch too short, cant confirm')
            return
        x,y = eventd['mouse']
        region = context.region
        rv3d = context.region_data
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, (x,y))
        
        last_hovered = self.knife.hovered[1] #guaranteed to be a point by criteria to enter sketch mode
        
        
        self.knife.hover(context,x,y)
        print('last hovered %i' % last_hovered)
        
        sketch_3d = ray_cast_path(context, self.knife.cut_ob,self.sketch)
        L = get_path_length(sketch_3d)
        n = math.ceil(L/.4)  #maybe go 200
        sketch_3d, eds = space_evenly_on_path(sketch_3d, [(0,1),(1,2)], n)
        if self.knife.hovered[0] == None:  #drawing out into space
            #add the points in
            if last_hovered == len(self.knife.pts) - 1:
                if last_hovered == 0: self.knife.cyclic = False
                
                self.knife.pts += sketch_3d[1:-1] #sketch_3d[0::5]
                self.knife.normals += [view_vector]*len(sketch_3d) #TODO optimize...don't slice twice, you are smart enough to calc this length!
                print('add on to the tail')

                
            else:
                self.knife.pts = self.knife.pts[:last_hovered] + sketch_3d[1:-1]
                self.knife.normals = self.knife.normals[:last_hovered] + [view_vector]*len(sketch_3d[1:-1])
                print('snipped off and added on to the tail')
        
        else:
            print('inserted new segment')
            print('last hovered is %i, now hovered %i' % (last_hovered, self.knife.hovered[1]))
            new_pts = sketch_3d[1:-1]
            if last_hovered > self.knife.hovered[1]:
                
                if self.knife.hovered[1] == 0:
                    self.knife.pts = self.knife.pts[:last_hovered] + new_pts
                    self.knife.normals = self.knife.normals[:last_hovered] + [view_vector]*len(new_pts)
            
                else:
                    new_pts.reverse()
                    self.knife.pts = self.knife.pts[:self.knife.hovered[1]] + new_pts + self.knife.pts[last_hovered:]
                    self.knife.normals = self.knife.normals[:self.knife.hovered[1]] + [view_vector]*len(new_pts) + self.knife.normals[last_hovered:]
            
            else:
                if self.knife.hovered[1] == 0: #drew back into tail
                    self.knife.pts += sketch_3d[1:-1]
                    self.knife.normals += [view_vector]*len(sketch_3d[1:-1])
                    self.knife.cyclic = True
                else:
                    self.knife.pts = self.knife.pts[:last_hovered] + new_pts + self.knife.pts[self.knife.hovered[1]:]
                    self.knife.normals = self.knife.normals[:last_hovered]  + [view_vector]*len(new_pts) + self.knife.normals[self.knife.hovered[1]:]
        self.knife.snap_poly_line()