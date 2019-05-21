'''bl_info = {
    "name": "Add Airfoil",
    "description": "Creates the profile for the 4-digit NACA series",
    "author": "David Wehr",
    "version": (0, 0, 2),
    "blender": (2, 5, 9),
    "api": 33411, #Not certain on the API version
    "location": "View3D > Add > Mesh > Airfoil",
    "warning": "",
    "category": "Learnbgame"
}
'''
import math as M
import bpy

class MakeAirfoil(bpy.types.Operator):
    bl_idname = "mesh.make_airfoil"
    bl_label = "NACA Airfoil"
    bl_description = "Creates a 4-digit NACA Airfoil"
    bl_options = {"REGISTER", "UNDO"}
    
    #Properties that define the airfoil
    m = bpy.props.IntProperty (
        name = "Max Camber",
        description = "Maximum Camber (% of chord)",
        default = 0,
        min = 0,
        max = 9)
    p = bpy.props.IntProperty (
        name = "Camber Pos",
        description = "Position of Camber (% of chord)",
        default = 0,
        min = 0,
        max = 9)
    t = bpy.props.IntProperty (
        name = "Thickness",
        description = "Maximum thickness (% of chord)",
        default = 12,
        min = 0,
        max = 99)
    res = bpy.props.IntProperty (
        name = "Resolution",
        description = "Number of x coordinates to calculate for",
        default = 100,
        min = 0)
    
    #Layout of the script UI    
    def draw(self, context):
        Col = self.layout.column(align = True)
        Col.prop(self, "m")
        Col.prop(self, "p")
        Col.prop(self, "t")
        Col.prop(self, "res")
    
    #This runs every time a parameter is modified
    def action_common(self, context):
        
        #Convert percentages to decimals
        m = self.m*0.01
        p = self.p*0.1
        t = self.t*0.01
        
        
        #Each x value to calculate for
        x_values = []
        #The camber line y values
        camb_values = []
        #The thickness distribution
        thick_values = []
        #Coordinates for the upper and lower parts of the airfoil
        cords_u = []
        cords_l = []
        
        #Creates a list with all the x_values to be calculated for
        for iter in range(self.res+1):
            x_values.append((1/self.res) * iter)
            
        
        #Calculate the thickness distribution along the chord for each x value
        for x in x_values:
            cnst = t/0.2
            y = cnst*( (0.2969*M.sqrt(x)) - (0.1260*x) - (0.3516*(x**2)) + (0.2843*(x**3)) - (0.1015*(x**4)) )
            thick_values.append(y)
            
        #For each x value, calculate the location of y for the camber line
        iter = -1
        for x in x_values:
            iter += 1  #gives us access to the list index for the thickness values
            
            #Use a different formula if x is less than or greater than p
            if x > p:
                constant = m/((1-p)**2)
                camb_y = constant *( (1-(2*p)) + (2*p*x) - (x**2) )

                #Angle of the tangent to the curve.  Lets us map the thickness to the camber line
                angle = M.atan(constant * ((2*p) - (2*x)))
                
                #Determine the final coordinates
                xu = x - (M.sin(angle) * thick_values[iter])
                yu = camb_y + (M.cos(angle) * thick_values[iter])
                xl = x + (M.sin(angle) * thick_values[iter])
                yl = camb_y - (M.cos(angle) * thick_values[iter])
                
                cords_u.append([xu, yu])
                cords_l.append([xl, yl])
                
            if x <= p:
                #Create an exception for if p = 0 (Division by zero)
                try:
                    constant = m/(p **2)
                except:
                    constant = 0
                camb_y = constant*((2*p*x) - (x**2))
                
                angle = M.atan(constant * ((2*p) - (2*x)))
                
                xu = x - (M.sin(angle) * thick_values[iter])
                yu = camb_y + (M.cos(angle) * thick_values[iter])
                xl = x + (M.sin(angle) * thick_values[iter])
                yl = camb_y - (M.cos(angle) * thick_values[iter])
                
                cords_u.append([xu, yu])
                cords_l.append([xl, yl])
                
            camb_values.append(camb_y)
        
        #Y location to place vertices on    
        y = 0
        
        #List of all the vertices and faces
        vertices = []
        faces = []
        
        #Add each vertex to the list of vertices
        for index in range(self.res+1):
            vertices.append([cords_u[index][0], y, cords_u[index][1]])
            vertices.append([cords_l[index][0], y, cords_l[index][1]])
        
        #The basic face
        base = [0, 1, 3, 2]
        
        #Create the list of faces.    
        for index in range(self.res):
            faces.append([i + (2*(index)) for i in base])
            
        #Create a new mesh and link the vertex and face data to it
        airfoil_mesh = bpy.data.meshes.new("airfoil")
        airfoil_mesh.from_pydata(vertices, [], faces)
        
        #Update the displayed mesh with the new data
        airfoil_mesh.update()
        
        #The object name depends on what NACA airfoil it is, so it dynamically
        #changes the object name depending on the parameters
        obj_name = "NACA " + str(int(m*100)) + str(int(p*10)) + str(int(t*100))
        airfoil_obj = bpy.data.objects.new(obj_name, airfoil_mesh)
        
        #Link object to the scene
        context.scene.objects.link(airfoil_obj)
        
        bpy.ops.object.select_all(action = "DESELECT")
        airfoil_obj.select = True
        context.scene.objects.active = airfoil_obj
    
    #Runs the main script    
    def execute(self, context):
        self.action_common(context)
        return {"FINISHED"}
    
    def invoke(self, context, event):
        self.action_common(context)
        return {"FINISHED"}
    
    
#Register the script with Blender, so it's recognized
def add_to_menu(self, context):
    self.layout.operator("mesh.make_airfoil", icon = "PLUGIN")

    
def register():
    bpy.utils.register_class(MakeAirfoil)
    bpy.types.INFO_MT_mesh_add.append(add_to_menu)
        
        
def unregister() :
    bpy.utils.unregister_class(MakeAirfoil)
    bpy.types.INFO_MT_mesh_add.remove(add_to_menu)
    
if __name__ == "__main__":
    register()