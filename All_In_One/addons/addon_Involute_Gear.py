bl_info = {
    "name": "Involute Gear",
    "author": "Ricard Bitriá Ribes",
    "version": (1, 1),
    "blender": (2, 75, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds an involute profile gear",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }


import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector, geometry
from math import (
        atan, acos, cos,
        sin, tan, pi,
        radians, sqrt,
        )

# Conversion polar <=> cartesian coordinate system
def cart2pol(v:Vector):
    v=Vector((v[0],v[1]))
    theta = atan(v.y/v.x)
    rho = v.length
    return theta,rho

def pol2cart(theta,rho, z):
    x = rho*cos(theta)
    y = rho*sin(theta)
    return Vector((x, y, z))

def calc_max_beta(d):
    beta = 0
    for I in range(9):
        inc = 10**-I
        while abs(d) > tan(beta)-beta:
            beta += inc
        beta -= inc
        a=0
    b=pi/2
    beta = (b+a)/2
    for I in range(50):
        y=tan(beta)-beta+d
        if y == 0:
            return beta
        elif y>0:
            b=beta
        else:
            a=beta
        beta = (b+a)/2
    return beta

#Calculates the shape of one tooth, result in polar coordinates
#t      Tooth width
#d      Z axis value
def add_tooth(t, radius, Ra, Rd, base, p_angle, res):
    rinv = radius*cos(p_angle)
    
    k = -t/4-(tan(p_angle)-p_angle)
    max_beta = calc_max_beta(k)
    beta = acos(rinv/(Ra))
    if beta > max_beta:
        beta = max_beta
    A = [k+I*tan(beta)/res for I in range(res+1)]
        
    verts = []
    verts_polar = []
    for ii in A:
        x = rinv*(cos(ii)+(ii-k)*sin(ii))
        y = rinv*(sin(ii)-(ii-k)*cos(ii))
        d = sqrt(x**2+y**2)
        if d > Rd:
            verts.append((x,y))
        
    verts_polar = [(cart2pol(verts[I])) for I in range(len(verts))]

    verts_polar += [(-verts_polar[I][0],verts_polar[I][1])for I in reversed(range(len(verts_polar)))]
    return verts_polar

def add_gear(teethNum, Dp, Ad, De, base, p_angle, t_res, r_res, 
             width=1, skew=0, conangle=0, crown=0.0):
    # Initial calculations
    t=2*pi/teethNum;
    radius = Dp/2
    Ra = radius + Ad
    Rd = radius - De
    Rb = Rd - base
    
    # Generate vertex for single tooth (in polar coordinates)
    verts_pol = add_tooth(t, radius, Ra, Rd, base, p_angle, t_res)
    verts_pol = [(verts_pol[0][0], Rd)] + verts_pol + [(verts_pol[-1][0], Rd)]
    
    # Store the number of vertex per tooth
    tooth_vert_cnt = len(verts_pol)
    
    # Generate vertex for all teeth
    theta = (verts_pol[-1][0]-verts_pol[0][0])/(r_res+1)
    beta = (t-(verts_pol[-1][0]-verts_pol[0][0]))/(r_res+1)
    ring_verts_pol=[]
    verts=[]
    for k in [t*I for I in range(teethNum)]:
        ver_pol = [(verts_pol[I][0]+k, verts_pol[I][1]) for I in range(len(verts_pol))]
        ring_verts_pol.extend([(ver_pol[0][0]+theta*I, Rd) for I in range(1,r_res+1)])
        ring_verts_pol.extend([(ver_pol[-1][0]+beta*I, Rd) for I in range(1,r_res+1)])
        
        verts.extend(pol2cart(ver_pol[I][0], ver_pol[I][1], width) for I in range(len(ver_pol)))
    
    # Generate inner vertex
    ring_verts=[]
    ring_verts.extend(
                [pol2cart(ring_verts_pol[I][0], Rd, width) for I in range(len(ring_verts_pol))]
                )
    ring_verts.extend(
                reversed(
                [pol2cart(ring_verts_pol[I][0], Rd, -width) for I in range(len(ring_verts_pol))]
                ))
    # Store the number of vertex of the deddendum circle
    Rd_circ_cnt = len(ring_verts)
    theta = t/2/(r_res+1)
    alpha = -theta*((r_res+1)/2)
    ring_verts.extend(
                [pol2cart(alpha + theta*I, Rb, width)for I in range(teethNum*(r_res+1)*2)]
                )
    ring_verts.extend(
                reversed(
                [pol2cart(alpha + theta*I, Rb, -width)for I in range(teethNum*(r_res+1)*2)]
                ))
    # Store the number of vertices of the base circle
    Rb_circ_cnt = len(ring_verts) - Rd_circ_cnt
                
    # Store the number of vertex of all teeth (one side only)
    teeth_vert_cnt = len(verts)
    
    verts.extend(reversed([(verts[I][0], verts[I][1], -verts[I][2])for I in range(len(verts))]))
    verts.extend(ring_verts)

# Create faces
  # Create bottom and upper faces 
    # for each tooth 
    faces=[]
    for I in range(teethNum*2):
        if I < teethNum:
            faces.append(list(range(I*tooth_vert_cnt,(I+1)*tooth_vert_cnt)) + 
                        [teeth_vert_cnt*2 + r_res*2*I + J for J in reversed(range(r_res))])
        else:
            faces.append(list(range(I*tooth_vert_cnt,(I+1)*tooth_vert_cnt)) + 
                        [teeth_vert_cnt*2 + r_res*2*I+J for J in reversed(range(r_res, 2*r_res))])
    
    # for th ring
    state = 0
    J = 0
    K = 0
    strt=teeth_vert_cnt*2
    for I in range(teethNum*(r_res+1)*4):
        if I == teethNum*(r_res+1)*2-1:
            if r_res != 0:
                J += r_res
                faces.append([strt+Rd_circ_cnt/2-1, 0, strt+Rd_circ_cnt, strt+Rd_circ_cnt+I])
                state = 0
            else:
                faces.append([teeth_vert_cnt-1, 0, strt, strt+Rd_circ_cnt+I])
                K+=1
        elif I == teethNum*(r_res+1)*4-1:
            if r_res != 0:
                faces.append([strt-1, strt+Rd_circ_cnt/2, strt+Rd_circ_cnt+Rb_circ_cnt/2, len(verts)-1])
            else:
                faces.append([strt-1, teeth_vert_cnt, strt+Rd_circ_cnt+Rb_circ_cnt/2, len(verts)-1 ])
        elif r_res == 0:
            faces.append([tooth_vert_cnt*((K+1)//2)-(K%2), tooth_vert_cnt*((K+2)//2)-((K-1)%2), strt+Rd_circ_cnt+I+1, strt+Rd_circ_cnt+I])
            K += 1
        elif state == 0:
            faces.append([tooth_vert_cnt*((K+1)//2)-(K%2), strt+J, strt+Rd_circ_cnt+I+1, strt+Rd_circ_cnt+I])
            K += 1
        elif state == r_res:
            J += r_res
            faces.append([strt+J-1, tooth_vert_cnt*((K+1)//2)-(K%2), strt+Rd_circ_cnt+I+1, strt+Rd_circ_cnt+I])
            state = -1
            
        else:
            faces.append([strt+J+state-1, strt+J+state, strt+Rd_circ_cnt+I+1, strt+Rd_circ_cnt+I])
            
        state += 1
    
  # Create side faces
    # Outer faces
    for I in range(teethNum):
        for J in range(tooth_vert_cnt-1):
            K= I * tooth_vert_cnt +J
            faces.append([strt-K-1, strt-K-2, K+1, K])
        state = 0
        for J in range(r_res+1):
            if I == teethNum-1 and J == r_res:
                if r_res != 0:
                    faces.append([strt-1, 0, strt-1+(I+1)*2*r_res, strt+Rd_circ_cnt-(I+1)*2*r_res])
                else:
                    faces.append([strt-1, 0, teeth_vert_cnt-1, teeth_vert_cnt])
            elif state == 0:
                if r_res != 0:
                    faces.append([tooth_vert_cnt*(I+1)-1, strt-tooth_vert_cnt*(I+1), strt+Rd_circ_cnt-(I*2+1)*r_res-1, strt+(I*2+1)*r_res])
                else:
                    faces.append([tooth_vert_cnt*(I+1)-1, strt-tooth_vert_cnt*(I+1), strt-tooth_vert_cnt*(I+1)-1, tooth_vert_cnt*(I+1)])
            elif state == r_res:
                faces.append([strt-tooth_vert_cnt*(I+1)-1, tooth_vert_cnt*(I+1), strt-1+(I+1)*2*r_res, strt+Rd_circ_cnt-(I+1)*2*r_res])
            else:
                faces.append([strt+state+(I*2+1)*r_res, strt+state-1+(I*2+1)*r_res, strt+Rd_circ_cnt-(I*2+1)*r_res-state, strt+Rd_circ_cnt-(I*2+1)*r_res-state-1])
            state += 1
            
    #Create inner faces
    strt = strt+Rd_circ_cnt
    for I in range(int(Rb_circ_cnt/2)):
        a=1
        #faces.append([strt+state+(I*2+1)*points, 0,1,2])
    
    return verts,faces

def add_object(self, context):
    verts, faces = add_gear(self.number_of_teeth, self.pitch_diameter, self.addendum, self.dedendum,
                            self.base, self.angle, self.tooth_res, self.ring_res,
                            width=self.width)
    edges = []

    mesh = bpy.data.meshes.new(name="Gear")
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=self)


class OBJECT_OT_add_inv_gear(Operator, AddObjectHelper):
    """Create a new Involute Gear"""
    bl_idname = "mesh.add_inv_gear"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    def teeth_update(self, context):
        if self.pitch_diameter != self.modulus*self.number_of_teeth and self.state == 0:
            self.state = 1
            self.pitch_diameter = self.modulus*self.number_of_teeth
            self.base = self.size_factor*(self.pitch_diameter/2-self.dedendum)
        self.state = 0

    def diameter_update(self, context):
        if self.number_of_teeth != self.pitch_diameter/self.modulus and self.state == 0:
            self.state = 1
            self.number_of_teeth = self.pitch_diameter/self.modulus
            self.base = self.size_factor*(self.pitch_diameter/2-self.dedendum)
        self.state = 0

    def modulus_update(self, context):
        self.state = 1
        self.pitch_diameter = self.modulus * self.number_of_teeth
        self.base = self.size_factor*(self.pitch_diameter/2-self.dedendum)
        
    def base_update(self, context):
        radius = self.pitch_diameter/2
        if self.state == 0:
            self.size_factor = self.base/(radius-self.dedendum)
            if self.base > radius-self.dedendum:
                self.base = radius-self.dedendum
        self.state = 0

    state = IntProperty(
            default = 0
            )
            
    size_factor = FloatProperty(
            default = 0.5,
            min = 0.0,
            max = 1.0
            )
    
    number_of_teeth = IntProperty(
            name="Number of Teeth",
            description="Number of teeth on the gear",
            min=2,
            default=10,
            update = teeth_update
            )

    pitch_diameter = FloatProperty(
            name="Pitch diameter",
            min=0.001,
            default=2.0,
            step=1,
            subtype='DISTANCE',
            description="Diameter of the pitch circle",
            update = diameter_update
            )

    modulus = FloatProperty(
            name="Modulus",
            min=0.01,
            default=0.2,
            step=1,
            subtype='DISTANCE',
            description="Pitch diameter divided by the number of teeth",
            update=modulus_update
            )
    
    addendum = FloatProperty(
            name="Addendum",
            min=0.0001,
            default=0.1,
            subtype='DISTANCE',
            description="Addendum, extent of tooth above radius"
            )
    
    dedendum = FloatProperty(name="Dedendum",
            description="Dedendum, extent of tooth below radius",
            min=0.0001,
            max=100.0,
            subtype='DISTANCE',
            default=0.1
            )
            
    angle = FloatProperty(name="Pressure Angle",
            description="Pressure angle, skewness of tooth tip",
            min=0.0,
            max=radians(45.0),
            subtype='ANGLE',
            default=radians(20.0)
            )
    base = FloatProperty(name="Base",
            description="Base, extent of gear below radius",
            min=0.0001,
            max=100.0,
            subtype='DISTANCE',
            default=0.375,
            update=base_update
            )
    width = FloatProperty(name="Width",
            description="Width, thickness of gear",
            min=0.05,
            max=100.0,
            subtype='DISTANCE',
            default=0.2
            )
            
    tooth_res = IntProperty(name="Tooth resolution",
            description="Subdivision multiplier for tooth calculation",
            min=1,
            max=1024,
            default=8
            )
            
    ring_res = IntProperty(name="Ring resolution",
            description="Subdivision multiplier for circle calculations",
            min=0,
            max=128,
            default=2
            )
            
    manual_mod = BoolProperty(name="Manual mode",
            description="Custom / Automatic gear parameters",
            default = False
            )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'number_of_teeth')
        box.prop(self, 'pitch_diameter')
        box.prop(self, 'modulus')
        
        box = layout.box()
        box.prop(self, 'angle')
        box.prop(self, 'width')
        box.prop(self, 'base')
        
        layout.prop(self, 'manual_mod')
        box = layout.box()
        box.enabled = self.manual_mod
        box.prop(self, 'dedendum')
        box.prop(self, 'addendum')
        
        box = layout.box()
        box.prop(self, 'tooth_res')
        box.prop(self, 'ring_res')

    def execute(self, context):
        radius = self.pitch_diameter/2
        if self.dedendum > radius-self.base:
            self.dedendum = radius-self.base
            
        if self.manual_mod == False:
            self.dedendum = 1.25*self.modulus
            self.addendum = 1*self.modulus
            
        add_object(self, context)

        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_inv_gear.bl_idname,
        text="Involute Gear",
        icon='SCRIPTWIN')


# This allows you to right click on a button and link to the manual
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/dev/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "editors/3dview/object"),
        )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_inv_gear)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_inv_gear)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()
