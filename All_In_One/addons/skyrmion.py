bl_info = {
    "name": "Skyrmion",
    "category": "Object",
}


import bpy
from math import *
import numpy as np

class Geometry(): pass

# square lattice
gsquare = Geometry() # get geometry
gsquare.r = [np.array([0.,0.,0.])] # positions
gsquare.a1 = np.array([1.,0.,0.]) # positions
gsquare.a2 = np.array([0.,1.,0.]) # positions

# triangular lattice
gtri = Geometry() # get geometry
gtri.r = [np.array([0.,0.,0.])] # positions
gtri.a1 = np.array([1.,0.,0.]) # vector
gtri.a2 = np.array([1./2.,np.sqrt(3.)/2.,0.]) # vector



# honeycomb lattice
ghoney = Geometry() # get geometry
ghoney.r = [np.array([-0.5,0.,0.]),np.array([0.5,0.,0.])] # positions
ghoney.a1 = np.array([3./2.,np.sqrt(3.)/2,0.]) # vector
ghoney.a2 = np.array([-3./2.,np.sqrt(3.)/2,0.]) # vector



def supercell(g,nx=1,ny=1):
    """Compute a supercell"""
    rs = [] # empty list
    for ix in range(-nx,nx+1):
      for iy in range(-ny,ny+1):
        for r in g.r: rs.append(r + ix*g.a1 + iy*g.a2)
    return np.array(rs) # return rs



class Skyrmion(bpy.types.Operator):
    """Skyrmion generator"""
    bl_idname = "object.skyrmion"
    bl_label = "Skyrmion"
    bl_options = {'REGISTER', 'UNDO'}

# different parameters
    chirality = bpy.props.IntProperty(name="Chirality", default=1, min=-4, max=4)
    gamma = bpy.props.FloatProperty(name="Gamma", default=0, min=0, max=360,step=1500)
    width = bpy.props.IntProperty(name="Width", default=4, min=1, max=100)
    radius = bpy.props.FloatProperty(name="Radius", default=10, min=1, max=100,step=300)
    space = bpy.props.FloatProperty(name="Spacing", default=4.0, min=0.0, max =20.0,step=50)
    is_circular = bpy.props.BoolProperty(name="Circular")
    elevation = bpy.props.FloatProperty(name="Elevation", default=0.0, min=-10.0, max =10.0,step=100)
    test_items = [
    ("square", "square", "", 1),
    ("triangular", "triangular", "", 2),
    ("honeycomb", "honeycomb", "", 3),
    ]
    enum = bpy.props.EnumProperty(items=test_items)
    def execute(self, context):
      # define here the positions where you want to copy the selected objects
      # in this example we choose a square lattice of size 4
      # ================================================
#      print("hello") 
      pos=[]
      r = self.space
      ng = self.width
#      self.ng = 2 
#      self.r = 4.0
      for i in range(-ng,ng+1):
        for j in range(-ng,ng+1):
          if self.is_circular: # if desired circular skyrmion
            if i*i+j*j>ng*ng: continue # if too large, next iteration
          pos=pos+[[r*i,r *j,0]]
      if self.enum=="square": g = gsquare # triangular lattice
      elif self.enum=="triangular": g = gtri # triangular lattice
      elif self.enum=="honeycomb": g = ghoney # triangular lattice
      pos = supercell(g,nx=ng,ny=ng)
      pos = pos*r # scale the positions
      # here put the direction of the object in each point, (0,0,1) corresponds
      # to no rotation, so the vector refers to the new direction
      # of a characteristic axis,  The vectors will be
      # normalized so do not worry :)
      
      
      # in this example we create the vectors of a two dimensional kink
      # located in the origin
      
      nrep=float(len(pos))
      tpi=6.28
      direc=[]
      for ii in range(len(pos)):
        p=pos[ii]
        # distance to the origin
        r=p[0]*p[0]+p[1]*p[1]
        phi=atan2(p[1],p[0])
        r=sqrt(r)
        theta = tanh(r/self.radius)*np.pi # radial envelop
        # theta and phi angles
        phi = phi*self.chirality + self.gamma*np.pi/180. # times the chirality
        st,ct = np.sin(theta),np.cos(theta)
        sp,cp = np.sin(phi),np.cos(phi)
        # 1 near the origin, 1 far from the origin
        rr=1.0-2.0*tanh(0.2*r)
        # radial canting
        direc=direc+[[st*cp,st*sp,ct]]
        # modify the elevation 
        pos[ii][2] += (.5-theta/np.pi)*self.elevation       
 
      # rest of the program that you do not have to edit
      # ================================================
      # ================================================
      
      
      
      
      # normalize rotation vectors
      for iv in range(len(direc)):
        vec=direc[iv]
        norm=vec[0]*vec[0]+vec[1]*vec[1]+vec[2]*vec[2]
        norm=1.0/sqrt(norm)
        for ic in range(3):
          vec[ic]=vec[ic]*norm
      
      # get angles
      ang=[]
      for vec in direc:
        # calculate rho
        r=vec[0]*vec[0]+vec[1]*vec[1]
        r=sqrt(r)
        # calculate theta angle  
        at=atan2(r,vec[2])
        # calculate phi angle
        ap=atan2(vec[1],vec[0])
        # save angles in list
        ang=ang+[[at,ap]]
      
      
        
      # objects
      objects=bpy.data.objects
      
      # duplicate
      def duplicate():
        bpy.ops.object.duplicate()
      # deselect
      def deselect():
        bpy.ops.object.select_all(action = 'DESELECT')
      # active object
      active=bpy.context.scene.objects.active
      obj_master=bpy.context.scene.objects.active
      # translate active object
      def trans(x=0.0,y=0.0,z=0.0):
        bpy.ops.transform.translate(value=(x,y,z))
      
      
      # rotate active object
      def rot(value=0.0,axis=(0,0,0)):
        bpy.ops.transform.rotate(value=value,axis=axis)
      
      # translate and rotate
      replicas = [] 
      for ip in range(len(pos)):
      # position and rotation
        p=pos[ip]
        alp=ang[ip]
        at=alp[0]
        ap=alp[1]
      # translate and rotate
#        trans(x=p[0],y=p[1],z=p[2])
#        rot(value=at,axis=(0,1,0))
#        rot(value=ap,axis=(0,0,1))
        obj_new = obj_master.copy() # copy object
        replicas.append(obj_new) # store in list
        bpy.context.scene.objects.link(obj_new) # new object
        bpy.ops.object.select_all(action = 'DESELECT') # desellect all
        obj_new.select = True # select
        bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS") # origin
        bpy.ops.transform.rotate(value=at,axis=(0,1,0))
        bpy.ops.transform.rotate(value=ap,axis=(0,0,1))
        obj_new.select = False # select
        obj_new.location = p # move to its position
      # set the parent
      bpy.ops.object.select_all(action = 'DESELECT') # desellect all
      for obj in replicas:
        obj.select = True # select
      obj_master.select = True # select
      bpy.ops.object.parent_set(type='OBJECT',keep_transform=True)
      bpy.ops.object.select_all(action = 'DESELECT') # desellect all
      obj_master.select = True # select
      #  obj_new.parent = obj_master # set the parent
#        obj_new.rotation_mode = 'AXIS_ANGLE'
#        obj_new.rotation_mode = 'ZXY'
#        obj_new.rotation_euler = at,ap,0.
#        duplicate()
      
      #  scene.objects.link(obj_new)
      # destranslate and desrotate
#        active.location = np.array(active.location) - np.array(p)
#        trans(x=-p[0],y=-p[1],z=-p[2])
#        rot(value=-ap,axis=(0,0,1))
#        rot(value=-at,axis=(0,1,0))
      return {'FINISHED'}
      

def menu_func(self, context):
    self.layout.operator(Skyrmion.bl_idname)


# store keymaps here to access after registration
addon_keymaps = []



def register():
    bpy.utils.register_class(Skyrmion)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
#    kmi = km.keymap_items.new(Skyrmion.bl_idname, 'SPACE', 'PRESS')
#    kmi.properties.width = 2
    addon_keymaps.append(km)

def unregister():
    bpy.utils.unregister_class(Skyrmion)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    # handle the keymap
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    # clear the list
    del addon_keymaps[:]


if __name__ == "__main__":
    register()

      
#
