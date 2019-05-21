import bpy
import bpy_extras
import bmesh
import mathutils
import math
#import copy

bl_info = {  
     "name": "Viewport Vertex Alignment",  
     "author": "Hades",  
     "version": (0, 2),  
     "blender": (2, 6, 9),  
     "location": "View3D > Mesh Edit > Toolshelf > Vertex Alignment",  
     "description": "Aligns selected vertices based on a best fit algorithm, to the view port.",  
     "warning": "",  
     "wiki_url": "",  
     "tracker_url": "",  
     "category": "Learnbgame"
}  

def debug(msg):
    #print(msg)
    pass

def debug_points(points,rotation):
    r=mathutils.Matrix.Rotation(math.radians(rotation),4,'Z')
    f=open('c:/blender/points.txt','w')
    f.write(str(['x','y','z','w','rx','ry','rz','rw','dx','dy','dz','dw','weight','residual weight']))
    f.write('\n')
    for p in points:
        pr=p['point']*r
        f.write(str([p['point'].x,p['point'].y,p['point'].z,p['point'].w,pr.x,pr.y,pr.z,pr.w,p['delta'].x,p['delta'].y,p['delta'].z,p['delta'].w,p['weight'],p['residual weight']]))
        f.write('\n')
    f.close()
   
def debug_error(error):
    f=open('c:/blender/error.txt','w')
    f.write(str(['error sum','mean','stdev','residuals','devs']))
    f.write('\n')
    for i in range(len(error['residuals'])):
        f.write(str([error['error sum'],error['mean'],error['stdev'],error['residuals'][i],error['devs'][i]]))
        f.write('\n')
    f.close()
   
def main(context,properties):
    #debug("\nVertex Alignment operator:-----")
    #import os
    #os.system('cls')
    obj=bpy.context.object
    if (obj.mode == 'EDIT')and(bpy.context.space_data.type=="VIEW_3D") :
        bm=bmesh.from_edit_mesh(obj.data)
        
        #debug('\nSelected Vertices:')
        vertices = get_vertices(bm)
        #debug([v for v in vertices])
        
        if (len(vertices) <= 2):
            #debug("mesh.vertex_alignment: Not enough vertices selected")
            return {'CANCELLED'}
        
        #debug('\nAxis:')
        axis = get_axis('perspective')
        #debug(axis)
        
        #debug('\nProjection:')
        points = project(vertices,axis)
        #debug([p['point'] for p in points])
        
        #debug('\nFit:')
        points = fit1(properties,points) #points is being updated by ref-- note the right hand assignment is unnecessary !
        #debug([p['delta'] for p in points])
    
        #debug('\nUnproject:')
        vertices_updated = unproject(points,axis,properties)

        #debug([p["v'"] for p in vertices_updated])
        
        #debug("\nUpdate Vertices:")
        
        update_vertices(obj.data,points)
       
    #debug ("\nend function------")
    return {'FINISHED'}    
    
#def filter_outliers(points,rotate,properties,errori):
#    """This function will lower the weight of points with residuals that are outside of one standard deviation"""
#    print("FILTER_OUTLIERS FUNCTION:")
#    print(errori['stdev'])
#    if (errori['stdev']>1.0):
#        ind=0
#        for d in errori['devs']:
#            if (math.sqrt(d) >= errori['stdev']):
#                points[ind]['weight']=0
#                points[ind]['residual weight']=0
#                errori['outliers'] += 1
#                
#            ind+=1
#    return points

def filter_anchor(points,rotate,properties,error):
    """This function will add extreme weighting to the boundary points"""
    #debug('Anchor: shifting weights')
    #this funciton only works because the fit_functions will sort points before this function is called.
    max_weight=10000
    
    points[0]['weight'] = max_weight
    points[-1]['weight'] = max_weight
    points[0]['residual weight'] = 1
    points[-1]['residual weight'] = 1
    return points

def filter_reset_weights(points):
    for p in points:
        p['weight']=1
        p['residual weight']=1
    return points

#def copy_deltas(points):
#    a={}
#    for p in points:
#        a[p['id']]=p['delta']
#    return a

#def paste_deltas(points,best_deltas):
#    for d in points['delta']:
        

def fit1(properties,points):
    """This function applies the fitting function several times, finding the axis rotation that causes the smallest error and returns the points.
        This expects a 1D fit where x is the domain, y is the range (and therefore y is being affected in fit)."""
    #debug("\nFunction Trial:")
    #note: points is being treated as though it's 'by reference'-- inner values such as deltas are being changed on the main object, so be careful on order of operations.
    
    fit_function=properties['function']
    iterations=properties['iterations']
    
    max_error=9999999999999999999999999
    error=[] #list of dictionaries
    smallest_error=max_error
    min_error=0
    
    #best_points=None
    
    min_theta=0
    theta=0
    theta_step_initial=45
    theta_step=theta_step_initial
    theta_forward=True
    
    for i in range(iterations):#angles
        anchor=properties['anchor']
        #outlier_filter=properties['outlier_filter']
        points=filter_reset_weights(points)
        try:
            error.append({'failed':True,'error sum':max_error,'stdev':0,'mean':max_error,'residuals':[max_error],'devs':[0]}) #'outliers':error[i]['outliers']
            while True: #filters
                error[i]={'failed':True,'error sum':max_error,'stdev':0,'mean':max_error,'residuals':[max_error],'devs':[0]}
                
                points=fit_function(points,theta,properties)
                error[i]={'failed':False,'error sum':0,'stdev':0,'mean':0,'residuals':[],'devs':[]} #reset it-- in case an exception is thrown in the fit_function
                SrN=0
                for p in points:
                    error[i]['residuals'].append(
                                                math.pow(
                                                        math.sqrt(
                                                            math.pow(p['delta'].x,2)+math.pow(p['delta'].y,2)+math.pow(p['delta'].z,2)+math.pow(p['delta'].w,2)
                                                                 )
                                                      ,2)*p['residual weight']
                                                )
                    error[i]['error sum'] += error[i]['residuals'][-1]
                    SrN += p['residual weight']
                
                N=SrN #len(error[i]['residuals'])
                #print(N)
                error[i]['mean']=error[i]['error sum'] / N
                for e in error[i]['residuals']:
                    error[i]['devs'].append(math.pow(e - error[i]['mean'],2))
                    error[i]['stdev'] += error[i]['devs'][-1]
                error[i]['stdev'] = math.sqrt(error[i]['stdev']/N)
                
                
                if (not anchor):#or(outlier_filter)):
                    break
                
                #if (outlier_filter):
                #    if ((error[i]['stdev'] <= properties['outlier_filter_target'])or(error[i]['outliers'] >= len(points)-3)):  #you need at least 3 points to attempt to describe a curve.
                #        outlier_filter=False
                #    else:
                #        prev_outliers=error[i]['outliers']
                #        points=filter_outliers(points,theta,properties,error[i])
                #        print(["IF",prev_outliers,error[i]['outliers'],prev_outliers == error[i]['outliers']])
                #        
                #        if (error[i]['outliers'] == prev_outliers): #no more matches were found.
                #            print("NO MORE OUTLIERS")
                #            outlier_filter=False
                    
                if (anchor):
                    points=filter_anchor(points,theta,properties,error)
                    anchor=False
                #print([i,theta,outlier_filter,anchor,error[i]['stdev'],error[i]['outliers']])
            
            if (error[i]['error sum'] < smallest_error):
                smallest_error=error[i]['error sum']
                min_error=i
                min_theta=theta
                #best_points=copy.copy(points)
            
        except ValueError as e:
            print(e)
        except ZeroDivisionError as e:
            print(e)
        
        #angle convergence:
        if (i>360/theta_step_initial): #let it run around the cirlce a full time first, then search for the smallest error
            if (theta_forward):
                if (error[i]['error sum'] == smallest_error):
                    theta+=theta_step
                elif (error[i]['error sum'] > smallest_error):
                    theta_step/=2.0
                    theta-=theta_step
                    theta_forward=False
            else:
                if (error[i]['error sum'] == smallest_error):
                    theta-=theta_step
                elif (error[i]['error sum'] > smallest_error):
                    theta_step/=2.0
                    theta+=theta_step
                    theta_forward=True
        elif (i == 360/theta_step_initial):
            theta=min_theta
            theta_step/=2.0
        else:
            theta+=theta_step
        
        
        if (theta_step <= 0.000000001): #best angle found (or very close !)
            break
        
    #debug_error(error[min_error])
    #debug_points(points,min_theta)
    
    #one more time, the full 2 step procedure (1: dry, 2: filtered);
    anchor=properties['anchor']
    points=filter_reset_weights(points)
    points=fit_function(points,min_theta,properties)
    #if (outlier_filter):
    #    points=filter_outliers(points,min_theta,properties,error[min_error])
    #    outlier_filter=False
    
    if (anchor):
        points=filter_anchor(points,min_theta,properties,error)
        anchor=False
    points=fit_function(points,min_theta,properties)
    #points=best_points

    return points

def error_residual1(points, r , rr, properties, line_func, line_parameters):
    """This function is used in the fitting functions to determine the deltas """
    #print("Residual Errors:")
    for p in points:
        pr=p['point']*r
        x = pr.x
        y = pr.y
        yy = line_func(x,line_parameters)
        
        p['delta'] = mathutils.Vector((0,(y - yy),0,0))*rr
        
    return points
    
def sort_index1(points,r):
    """This function sorts points based on their domain (assumed as x axis when rotated) """
    #print("Sorting Indices:")
    points = sorted(points, key=lambda xx: (xx['point']*r).x)
    return points
        

def fit_linear1(points,rotate,properties=None):
    """This function attempts to fit a given set of points to a linear line: y = a1*x + a0"""
    
    r=mathutils.Matrix.Rotation(math.radians(rotate),4,'Z')
    rr=mathutils.Matrix.Rotation(math.radians(-rotate),4,'Z')
    
    Sxy = 0
    Sx = 0
    Sy = 0
    Sx2 = 0
    Sw = 0
    for p in points:
        pr=p['point']*r
        x = pr.x
        y = pr.y
        Sxy += x*y * p['weight']
        Sx += x * p['weight']
        Sy += y * p['weight']
        Sx2 += math.pow(x,2) * p['weight']
        Sw += p['weight']

    N = Sw
    
    a1 = ( N*Sxy - Sx*Sy ) / ( N*Sx2 - math.pow(Sx,2))
    a0 = 1/N * Sy - a1 * 1/N * Sx
    
    def line_func(x,a):
        return a[0] + a[1]*x
    
    points=sort_index1(points,r)
    
    return error_residual1(points,r,rr,properties,line_func,[a0,a1])

def fit_quadratic1(points,rotate,properties=None):
    """This function attempts to fit a given set of points to a quadratic polynomial line: y = a2*x^2 + a1*x + a0"""
    
    r=mathutils.Matrix.Rotation(math.radians(rotate),4,'Z')
    rr=mathutils.Matrix.Rotation(math.radians(-rotate),4,'Z')
    
    Sxy = 0
    Sx = 0
    Sy = 0
    Sx2 = 0
    Sx2y = 0
    Sx3 = 0
    Sx4 = 0
    Sw = 0
    for p in points:
        pr=p['point']*r
        x = pr.x
        y = pr.y
        Sxy = Sxy + x*y * p['weight']
        Sx =  Sx  + x * p['weight']
        Sy =  Sy  + y * p['weight']
        Sx2 = Sx2 + math.pow(x,2) * p['weight']
        Sx2y = Sx2y+ math.pow(x,2)*y * p['weight']
        Sx3 = Sx3 + math.pow(x,3) * p['weight']
        Sx4 = Sx4 + math.pow(x,4) * p['weight']
        Sw += p['weight']
        
    N = Sw
    
    A=[[N, Sx, Sx2,Sy], [Sx, Sx2, Sx3,Sxy], [Sx2, Sx3, Sx4,Sx2y]]
    xM=like_a_gauss(A)
    
    a0=xM[0][3]
    a1=xM[1][3]
    a2=xM[2][3]
    def line_func(x,a):
        return a[0] + a[1]*x + a[2]*math.pow(x,2)
    
    points=sort_index1(points,r)
    
    return error_residual1(points,r,rr,properties,line_func,[a0,a1,a2])

def fit_cubic1(points,rotate,properties=None):
    """This function attempts to fit a given set of points to a cubic polynomial line: y = a3*x^3 + a2*x^2 + a1*x + a0"""
    
    r=mathutils.Matrix.Rotation(math.radians(rotate),4,'Z')
    rr=mathutils.Matrix.Rotation(math.radians(-rotate),4,'Z')
    
    Sxy = 0
    Sx = 0
    Sy = 0
    Sx2 = 0
    Sx2y = 0
    Sx3y = 0
    Sx3 = 0
    Sx4 = 0
    Sx5 = 0
    Sx6 = 0
    Sw = 0
    for p in points:
        pr=p['point']*r
        x = pr.x
        y = pr.y
        Sxy = Sxy + x*y * p['weight']
        Sx =  Sx  + x * p['weight']
        Sy =  Sy  + y * p['weight']
        Sx2 = Sx2 + math.pow(x,2) * p['weight']
        Sx2y = Sx2y+ math.pow(x,2)*y * p['weight']
        Sx3y = Sx3y+ math.pow(x,3)*y * p['weight']
        Sx3 = Sx3 + math.pow(x,3) * p['weight']
        Sx4 = Sx4 + math.pow(x,4) * p['weight']
        Sx5 = Sx5 + math.pow(x,5) * p['weight']
        Sx6 = Sx6 + math.pow(x,6) * p['weight']
        Sw += p['weight']
        
    N = Sw
    
    A=[[N, Sx, Sx2,Sx3,Sy], [Sx, Sx2, Sx3,Sx4,Sxy], [Sx2, Sx3, Sx4, Sx5,Sx2y], [Sx3, Sx4, Sx5, Sx6,Sx3y]]
    xM=like_a_gauss(A)
    
    a0=xM[0][4]
    a1=xM[1][4]
    a2=xM[2][4]
    a3=xM[3][4]
    
    def line_func(x,a):
        return a[0] + a[1]*x + a[2]*math.pow(x,2) + a[3]*math.pow(x,3)
    
    points=sort_index1(points,r)
    
    return error_residual1(points,r,rr,properties,line_func,[a0,a1,a2,a3])
    

def fit_cosine1(points,rotate,properties):
    """This function attempts to fit a given set of points to a cosine curve: y = a0 + a1*cos(w*x) + a2*cos(w*x) """
    
    r=mathutils.Matrix.Rotation(math.radians(rotate),4,'Z')
    rr=mathutils.Matrix.Rotation(math.radians(-rotate),4,'Z')
    
    omega=properties['cosine_omega']
    
    Sycos = 0
    Sysin = 0
    Scos = 0
    Scos2 = 0
    Ssin = 0
    Ssin2 = 0
    Sy = 0
    Scossin = 0
    Sw = 0
    for p in points:
        pr=p['point']*r
        x = pr.x
        y = pr.y
        Sy = Sy + y* p['weight']
        Sycos=Sycos + y * math.cos(omega * x)* p['weight']
        Sysin=Sysin + y * math.sin(omega * x)* p['weight']
        Scos = Scos + math.cos(omega * x)* p['weight']
        Ssin = Ssin + math.sin(omega * x)* p['weight']
        Scos2= Scos2+ math.pow(math.cos(omega * x),2)* p['weight']
        Ssin2= Ssin2+ math.pow(math.sin(omega * x),2)* p['weight']
        Scossin= Scossin+ math.cos(omega * x) * math.sin(omega * x)* p['weight']
        Sw += p['weight']
        
    N = Sw
    
    A=[[N, Scos, Ssin, Sy], [Scos, Scos2, Scossin, Sycos], [Ssin, Scossin, Ssin2, Sysin]]
    
    xM=like_a_gauss(A)
    a0=xM[0][3]
    a1=xM[1][3]
    a2=xM[2][3]
       
    
    def line_func(x,a):
        return a[0] + a[1]*math.cos(a[3] * x) + a[2] * math.sin(a[3] * x);
    
    points=sort_index1(points,r)
    
    return error_residual1(points,r,rr,properties,line_func,[a0,a1,a2,omega])

def get_vertices(mesh):
    """Returns the active list of selected vertices."""
    verts = []
    for v in mesh.verts:
        if v.select:
            verts.append(v)
    return verts
    
def get_axis(type):
    """Gets the axis we will be performing the rotation on. Returns a projection matrix"""
    if (type == 'perspective'):
        region = bpy.context.region
        rv3d = bpy.context.region_data
    else:
        #debug('mesh.vertex_align: get_axis: Unexpected input')
        return None
    
    return {"region":region,"rv3d":rv3d}

def project(vertices,axis):
    """Project the vertices onto a plane of the given axis."""
    points = []
    for v in vertices:
        vec = mathutils.Vector(v.co)
        p = bpy_extras.view3d_utils.location_3d_to_region_2d(axis['region'],axis['rv3d'],vec).to_4d()
        depth = vec
        points.append({"id":v,"point":p,"delta":None,"v'":None,"depth":depth,"weight":1.0,"residual weight":1.0,'index':None}) #id=original vert reference, point=project point on plane, d=delta changes by fit function, v' = Vector of final 3d vert position, depth=depth vector needed for unprojecting, weight=how much a point impacts the fit, residual weight=how much a points varience should be counted in the error.
        
    return points

def unproject(points,axis,properties):
    """Unproject points on a plane to vertices in 3d space."""
    for p in points:
        new_p = p['point']-p['delta']*properties['influence']
        
        old_v = p['id'].co
        new_v = bpy_extras.view3d_utils.region_2d_to_location_3d(axis['region'],axis['rv3d'],new_p.to_2d(),p['depth'])
        p["v'"]=new_v
    
    return points

def update_vertices(mesh,points):
    """Update the active set of selected vertices with their fitted positions."""
    for p in points:
        p['id'].co = p["v'"].to_3d().to_tuple() 
    bmesh.update_edit_mesh(mesh)

def like_a_gauss(mat):
    """
    Implementation of the Gaussian Elimination Algorithm for finding the row-reduced echelon form of a given matrix.
    No pivoting is done.
    Requires Python 3 due to the different behaviour of the division operation in earlier versions of Python.
    Released under the Public Domain (if you want it - you probably don't)
    https://gist.github.com/zhuowei/7149445
    Changes mat into Reduced Row-Echelon Form.
    """
    # Let's do forward step first.
    # at the end of this for loop, the matrix is in Row-Echelon format.
    for i in range(min(len(mat), len(mat[0]))):
        # every iteration, ignore one more row and column
        for r in range(i, len(mat)):
            # find the first row with a nonzero entry in first column
            zero_row = mat[r][i] == 0
            if zero_row:
                continue
            # swap current row with first row
            mat[i], mat[r] = mat[r], mat[i]
            # add multiples of the new first row to lower rows so lower
            # entries of first column is zero
            first_row_first_col = mat[i][i]
            for rr in range(i + 1, len(mat)):
                this_row_first = mat[rr][i]
                scalarMultiple = -1 * this_row_first / first_row_first_col
                for cc in range(i, len(mat[0])):
                	mat[rr][cc] += mat[i][cc] * scalarMultiple
            break

    # At the end of the forward step
    
    # Now reduce
    for i in range(min(len(mat), len(mat[0])) - 1, -1, -1):
        # divide last non-zero row by first non-zero entry
        first_elem_col = -1
        first_elem = -1
        for c in range(len(mat[0])):
            if mat[i][c] == 0:
                continue
            if first_elem_col == -1:
                first_elem_col = c
                first_elem = mat[i][c]
            mat[i][c] /= first_elem
        # add multiples of this row so all numbers above the leading 1 is zero
        for r in range(i):
            this_row_above = mat[r][first_elem_col]
            scalarMultiple = -1 * this_row_above
            for cc in range(len(mat[0])):
                mat[r][cc] += mat[i][cc] * scalarMultiple
        # disregard this row and continue
    return mat

class OPS_MESH_hd_viewport_vertexalign(bpy.types.Operator):
    """Align Vertices based on a least squares algorithm, based on the active view port."""
    bl_idname = "mesh.hd_viewport_vertex_align"
    bl_label = "3D Viewport Vertex Alignment"
    bl_options = {'REGISTER', 'UNDO'}
    
    function = bpy.props.EnumProperty(
                        items=[('LINEAR1','1D Linear','Linear Least Squares Method'),
                                ('QUADRATIC1','1D Parabolic','Quadratic Polynomial Least Squares Method'),
                                ('CUBIC1','1D Cubic', 'Cubic Polynomial Least Squares Method'),
                                ('COSINE1','1D Cosine', 'Cosine Least Squares Method')],
                        name="Fit type",
                        description="Select the method to align the vertices by.",
                        default='LINEAR1')
                        
    cosine_omega = bpy.props.FloatProperty(
                        name="Omega",
                        description="Angular frequency",
                        default=0.01,
                        min=0.0001,
                        step=0.001,
                        soft_min=0.001)
                        
    influence = bpy.props.FloatProperty(
                        name="Influence",
                        description="How much the best fit solution is applied.",
                        default=1,
                        soft_max=1,
                        soft_min=0,
                        step=0.01)
                        
    #outlier_filter = bpy.props.BoolProperty(
    #                    name="Outlier Filter",
    #                    description="Should vertices that are outside of the standard deviation be filtered out of the fitting function?",
    #                    default=True)
                        
    #outlier_filter_target = bpy.props.FloatProperty(
    #                    name="Standard Deviation target for error deviation.",
    #                    description="How far is too far from a fitted line?",
    #                    default=10,
    #                    min=0.1,
    #                    step=0.5)
    
    iterations = bpy.props.IntProperty(
                        name="Max Iterations",
                        description="Max number of iterations to try and solve.",
                        default=180,
                        soft_max=180,
                        min=1)
                        
    anchor = bpy.props.BoolProperty(
                        name="Anchor Boundaries",
                        description="Should the start and end vertices be anchored?",
                        default=True)
                        
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        if (self.function == 'LINEAR1'):
            fit_function=fit_linear1
        elif (self.function == 'QUADRATIC1'):
            fit_function=fit_quadratic1
        elif (self.function == 'CUBIC1'):
            fit_function=fit_cubic1
        elif (self.function == 'COSINE1'):
            fit_function=fit_cosine1
        else:
            #debug('unexpected input for "function" in mesh.vertex_align')
            fit_function=fit_linear1
        #,"max_error":math.pow(self.max_error,0.5),,"outlier_filter":self.outlier_filter,"outlier_filter_target":self.outlier_filter_target
        properties={"function":fit_function,"cosine_omega":self.cosine_omega,"influence":self.influence,"iterations":self.iterations,"anchor":self.anchor}
        return main(context,properties)


class ViewportVertexAlignMenu(bpy.types.Menu):
    bl_label = "Vertex Alignment"
    bl_idname = "MESH_MT_edit_mesh_hd_viewport_vertex_align" 

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.hd_viewport_vertex_align",text="Linear",icon='CURVE_PATH').function='LINEAR1'
        layout.operator("mesh.hd_viewport_vertex_align",text="Parabolic",icon='CURVE_BEZCURVE').function='QUADRATIC1'
        layout.operator("mesh.hd_viewport_vertex_align",text="Cubic",icon='CURVE_BEZCURVE').function='CUBIC1'
        layout.operator("mesh.hd_viewport_vertex_align",text="Cosine",icon='CURVE_BEZCURVE').function='COSINE1'

def draw_item(self, context):
    layout = self.layout
    layout.menu(ViewportVertexAlignMenu.bl_idname)

def menu_specials(self, context):
    self.layout.menu("MESH_MT_edit_mesh_hd_viewport_vertex_align")
    self.layout.separator()
    
class ViewportVertexAlignPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "3D Viewport Vertex Alignment"
    bl_idname = "VIEW3D_PT_hd_viewport_vertex_alignment"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.operator("mesh.hd_viewport_vertex_align")

def register():
    bpy.utils.register_class(OPS_MESH_hd_viewport_vertexalign)
    bpy.utils.register_class(ViewportVertexAlignMenu)
    bpy.utils.register_class(ViewportVertexAlignPanel)
    
    bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_specials)
    bpy.types.INFO_HT_header.append(draw_item)
    
def unregister():
    bpy.utils.unregister_class(OPS_MESH_hd_viewport_vertexalign)
    bpy.utils.unregister_class(ViewportVertexAlignMenu)
    bpy.utils.unregister_class(ViewportVertexAlignPanel)
    
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_specials)

    bpy.types.INFO_HT_header.remove(draw_item)



if __name__ == "__main__":
    register()
    #unregister()
    #register()
    # test call
    #bpy.ops.wm.call_menu(name=ViewportVertexAlignMenu.bl_idname)
    #unregister()

    
