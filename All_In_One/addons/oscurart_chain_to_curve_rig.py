# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Chain to Curve Rig",
    "author": "Oscurart",
    "version": (1,0),
    "blender": (2, 7, 1),
    "api": 3900,
    "location": "Add > Curve > Chain To Curve Rig",
    "description": "Create a curve rig from a chain.",
    "warning": "",
    "wiki_url": "oscurart.blogspot.com",
    "tracker_url": "",
    "category": "Learnbgame"
}



import bpy



def des(points):
    for vert in points:
        vert.select = False

def driver(objeto, huesonombre, armatureob,pointlocation,boneside):
    # x
    objeto.data.animation_data.drivers[-5].driver.expression = "var" 
    var = objeto.data.animation_data.drivers[-5].driver.variables.new()
    var.targets[0].id = armatureob
    var.targets[0].data_path = 'pose.bones["%s"].%s[0]' % (huesonombre,boneside)    

    # z
    objeto.data.animation_data.drivers[-4].driver.expression = "var" 
    var = objeto.data.animation_data.drivers[-4].driver.variables.new()
    var.targets[0].id = armatureob
    var.targets[0].data_path = 'pose.bones["%s"].%s[1]' % (huesonombre,boneside)     
    
    # z
    objeto.data.animation_data.drivers[-3].driver.expression = "var" 
    var = objeto.data.animation_data.drivers[-3].driver.variables.new()
    var.targets[0].id = armatureob
    var.targets[0].data_path = 'pose.bones["%s"].%s[2]' % (huesonombre,boneside)  
    
    # tilt
    objeto.data.animation_data.drivers[-1].driver.expression = "var" 
    var = objeto.data.animation_data.drivers[-1].driver.variables.new()
    var.targets[0].id = armatureob
    var.targets[0].data_path = 'pose.bones["%s"].rotation_euler.y' % (huesonombre) 


def curve_from_chain():   
          
    armatureob = bpy.context.object
    apb = bpy.context.active_pose_bone
    bonelist = [(apb.head,apb.name),(apb.tail,apb.name)]
    for bone in apb.children_recursive:
        bonelist.append((bone.tail,bone.name))
        
    bpy.ops.object.mode_set(mode='OBJECT')

    cur=bpy.data.curves.new("curve_data",type='CURVE')
    obcur=bpy.data.objects.new("Curve_Rig",cur)
    bpy.context.scene.objects.link(obcur)
    spline = cur.splines.new("NURBS")

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.scene.objects[obcur.name].select = 1
    bpy.context.scene.objects.active = obcur


    for i, pointco in enumerate(bonelist): 
        print(i)
        des(spline.points)   
        spline.points[-1].select = True
        spline.points[-1].co = (pointco[0][0],pointco[0][1],pointco[0][2],1)
        spline.points[-1].driver_add("co")  
        spline.points[-1].driver_add("tilt") 
        if len(bonelist) != i+1:
            point = spline.points.add()
        if i == 0:
            driver(obcur,pointco[1],armatureob,pointco[0],"head")
        else:
            driver(obcur,pointco[1],armatureob,pointco[0],"tail")  
            
    cur.dimensions='3D' # CURVA 3D
    spline.use_endpoint_u = True # EL SPLINE LLEGA HASTA EL FINAL
    spline.order_u = 6 # SUAVIZADO      


class ChainToCurve(bpy.types.Operator):
    '''Chain To Curve'''
    bl_idname = "curve.chain_to_curve"
    bl_label = "Chain To Curve Rig"
    bl_options = {'REGISTER', 'UNDO'}

    """
       
    @classmethod
    def poll(cls, context):
        return(bpy.context.active_object.type == "ARMATURE") 

    """
    def execute(self, context):
        curve_from_chain()
        return {'FINISHED'}


def menu_chain_to_curve(self, context):
    self.layout.operator(ChainToCurve.bl_idname, icon='PLUGIN')


def register():
    bpy.utils.register_class(ChainToCurve)
    bpy.types.INFO_MT_curve_add.append(menu_chain_to_curve)


def unregister():
    bpy.utils.unregister_class(ChainToCurve)
    bpy.types.INFO_MT_curve_add.remove(menu_chain_to_curve)

if __name__ == "__main__":
    register()

