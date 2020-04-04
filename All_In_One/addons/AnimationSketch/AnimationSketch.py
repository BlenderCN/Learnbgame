bl_info = {
    "name": "AnimationSketch",
    "author": "Yadoob",
    "version": (0,2),
    "blender": (2, 75, 0),
    "location": "View3D > Toolshelf > Grease Pencil > Grease Pencil Snap",
    "description": "Snap BendyBones to Grease Pencil",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
    }


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )

from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                      )




class OBJECT_OT_snap_curve(Operator):
    """Snap the Bendy Bones to the Grease Pencil Stroke"""
    bl_idname = "pose.snap_curve"
    bl_label = "Snap To Stroke"
    bl_options = {'REGISTER', 'UNDO'}


    
    def execute(self, context):
        
        curloc = bpy.context.scene.cursor_location
        
        
        obj = context.scene.objects.active
        mytool = context.scene.my_tool
        armLoc = obj.location
       
        
        #be sure taht we are in active pivot point
        
        space = context.space_data
        space.pivot_point = "ACTIVE_ELEMENT"
        
        #create curve  
        
        gp = bpy.context.scene.grease_pencil 
        gp.layers.active.info = "AnimationSketch"
        #check if stroke is visible and not locked
        gp.layers.active.hide = False
        gp.layers.active.lock = False
        GPLname =  gp.layers.active.info
        gp_name = gp.name
        
        # fresh start
        #look for AnimationSketch object and data, erase it
        
        if bpy.data.objects.get(GPLname) is not None:
            cur = bpy.data.objects[GPLname]
            bpy.context.scene.objects.unlink(cur)
            bpy.data.objects.remove(cur)

            
        for block in bpy.data.curves:
            if block.name  == GPLname:
                bpy.data.curves.remove(block)
        
              
        bpy.ops.gpencil.convert(type='CURVE', use_timing_data=True)        
        
    
        gp.layers.remove(gp.layers.active)

        
        #select curve and convert
        
        bpy.context.scene.objects.active = bpy.context.scene.objects[GPLname]
        curve = bpy.context.scene.objects.active
        
        #SuperHack to simplify curve
        
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold   =0.03)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.convert(target='CURVE')
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.spline_type_set(type='BEZIER')

        
            #select first and last point
        
        pts=curve.data.splines[0].bezier_points
        length = len(pts)
        bpy.ops.curve.select_all(action='DESELECT')

        pts[length-1].select_control_point=True
        pts[0].select_control_point=True


            #invert and dissolve
        bpy.ops.curve.select_all(action='INVERT')
        bpy.ops.curve.select_less()
        bpy.ops.curve.dissolve_verts()

            #update curve
        bpy.ops.object.editmode_toggle()
        bpy.context.scene.objects.unlink(curve)
        bpy.context.scene.objects.link(curve)
        context.scene.objects.active = curve
        namecurve = curve.name
                 
            

        bpy.ops.object.editmode_toggle()
        
        #get handles
        pts = curve.data.splines[0].bezier_points

        
        #pass loc/handles value
        curve = bpy.context.scene.objects[GPLname]
        co1 =  Vector(curve.matrix_world *pts[0].co)
        co2 =  Vector(curve.matrix_world *pts[1].co)
        
        
        bpy.ops.object.editmode_toggle()    
        obj.select=True
        context.scene.objects.active = obj
         
            #get bones   
        bone = context.active_bone
        scaleBone = Vector(obj.pose.bones[bone.name].scale)


        headloc = Vector(obj.pose.bones[bone.name].tail)
        bpy.context.scene.cursor_location = headloc


            #add target object
        bpy.context.scene.cursor_location = bpy.data.objects[obj.name].location + context.active_pose_bone.tail
        headloc = Vector(bpy.data.objects[obj.name].location + context.active_pose_bone.tail)
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False)
        plane = bpy.context.active_object
        plane.select=False
        obj.select=True
        context.scene.objects.active = obj
        bpy.context.scene.cursor_location = co2
        
        cstr = obj.pose.bones[bone.name].constraints.new('STRETCH_TO')
        cstr.target = plane
        slength =obj.pose.bones[bone.name].constraints["Stretch To"].rest_length

        
         # get children        
        cl=getchildren(bpy.data.armatures[obj.name],bone)

            #save loc
            
        tailloc = Vector(obj.pose.bones[bone.name].location)
       


            #pass loc
            
        bpy.context.scene.cursor_location = co1
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.data.armatures[obj.name].bones.active=bone
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        

        
        
        bpy.context.scene.cursor_location = co2
        bpy.ops.pose.select_all(action='DESELECT')

        plane.location=co2
        
        #select child bones
        clLocList = []
        

        for child in cl :
            targetclLoc = Vector(obj.pose.bones[child.name].location)
            clLocList.append(targetclLoc)
            child.use_inherit_scale = False
            #bpy.data.objects[obj.name].data.bones[child.name].select = True
            
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        
        
        
        
        
        
        
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.data.armatures[obj.name].bones.active=bone
        
        bonec = context.active_pose_bone

        
        if (mytool.preserveScale == True):
            bonec.constraints.remove( bonec.constraints["Stretch To"] )
            cstr = obj.pose.bones[bonec.name].constraints.new('IK')
            co3 = Vector(obj.pose.bones[bonec.name].tail)
            bonec.constraints.remove( bonec.constraints["IK"] )
            cstr = obj.pose.bones[bonec.name].constraints.new('STRETCH_TO')
            cstr.target = plane
            #slength =obj.pose.bones[bonec.name].constraints["Stretch To"].rest_length
        
        #apply "stretch to" to not mess with rotation


        bpy.ops.pose.visual_transform_apply()
        bonec.constraints.remove( bonec.constraints["Stretch To"] )

        

        obj.pose.bones[bone.name].bone.select=True


        #handles
        curve = bpy.context.scene.objects[GPLname]
        pts=curve.data.splines[0].bezier_points


        armature_ob = bpy.data.objects[obj.name]
        bone_name = bone.name


        inxW = Vector(curve.matrix_world * pts[0].handle_right)
        outyW = Vector(curve.matrix_world * pts[1].handle_left)



        bpy.context.scene.cursor_location = inxW
        
        #get matrix

        mat = matrix_world(armature_ob, bone_name)
        


        pb = bpy.data.objects[obj.name].pose.bones[bone.name]



        inxL = Vector(mat.inverted()*inxW)
        outyL = Vector(mat.inverted()*outyW)

        bpy.context.scene.cursor_location = outyW
        
        editbone = bpy.data.armatures[obj.name].bones[pb.name]
        
        inxL2 = Vector((inxL[0],inxL[2]))
        outyL2 = Vector((outyL[0],outyL[2]))
        pbcurvei = Vector((pb.bbone_curveinx,pb.bbone_curveiny))
        pbcurveo = Vector((pb.bbone_curveoutx,pb.bbone_curveouty))
        inf= mytool.influence

        rpbcurvei = interpolate(inf,pbcurvei,inxL2)
        rpbcurveo = interpolate(inf,pbcurveo,outyL2)

        

        pb.bbone_curveinx = rpbcurvei[0] - (editbone.bbone_curveinx*inf)
        pb.bbone_curveiny = rpbcurvei[1] - (editbone.bbone_curveiny*inf)
        pb.bbone_curveoutx = rpbcurveo[0] - (editbone.bbone_curveoutx*inf)
        pb.bbone_curveouty = rpbcurveo[1] - (editbone.bbone_curveouty*inf)

        
        #re-add stretch to, correct scale
        if(mytool.lockHead == True) :
            obj.pose.bones[bonec.name].scale = scaleBone
        else :
            if (mytool.preserveScale == True): 
                obj.pose.bones[bonec.name].scale = scaleBone
            else :
                scaleBone1 = Vector(obj.pose.bones[bonec.name].scale)
                obj.pose.bones[bonec.name].scale = interpolate(inf ,scaleBone,scaleBone1)
            
        bonec = context.active_pose_bone
        cstr = obj.pose.bones[bonec.name].constraints.new('STRETCH_TO')
        cstr.target = plane  

            
        #move bone
        
        if(mytool.lockHead == True) :
            plane.location = headloc
            #obj.pose.bones[bone.name].constraints["Stretch To"].rest_length =slength
            
        else :
            if (mytool.preserveScale == True):  
                
                transloc = Vector(plane.location)
                
                rhloc = interpolate(inf ,headloc,transloc)
                
                plane.location = rhloc
                
 
            else :
                    
                transloc = Vector(plane.location)
                
                rhloc = interpolate(inf ,headloc,transloc)
                
                plane.location = rhloc
            
            
        if(mytool.lockTail == True) : 

            obj.pose.bones[bone.name].location = tailloc

            
        
        else :
                        
            transloc = Vector(obj.pose.bones[bone.name].location)
            
            rtloc = interpolate(inf,tailloc,transloc)
            
            obj.pose.bones[bone.name].location = rtloc
            
              
        bpy.ops.pose.visual_transform_apply()
        bonec.constraints.remove( bonec.constraints["Stretch To"] )  
        
    
        # move children
        i = 0
        if (mytool.lockHead == False) :
            for child in cl :
                clcurLoc = obj.pose.bones[child.name].location
                clsaveLoc = clLocList[i]              
                clLoc = interpolate(inf ,clsaveLoc,clcurLoc)
                obj.pose.bones[child.name].location = clsaveLoc

                
                i = i+1
                        
                        

    
        
        #add curvature keys
        if (bpy.data.scenes[context.scene.name].tool_settings.use_keyframe_insert_auto  == True):
            curframe = bpy.context.scene.frame_current
            bonec.keyframe_insert(data_path='bbone_curveinx',frame=curframe)
            bonec.keyframe_insert(data_path='bbone_curveiny',frame=curframe)
            bonec.keyframe_insert(data_path='bbone_curveoutx',frame=curframe)
            bonec.keyframe_insert(data_path='bbone_curveouty',frame=curframe)
            
            bpy.data.objects[obj.name].pose.bones[bone.name].keyframe_insert(data_path='location', frame = curframe)
            bpy.data.objects[obj.name].pose.bones[headbone.name].keyframe_insert(data_path='location', frame = curframe)
        
        #clean
        
        pl = bpy.data.objects[plane.name]
        bpy.context.scene.objects.unlink(pl)
        bpy.data.objects.remove(pl)
            
        
            
        bpy.context.scene.update()
        
        bpy.ops.view3d.snap_cursor_to_selected()

                       
        cur = bpy.data.objects[GPLname]
        cu = cur.data  # the curve
        bpy.context.scene.objects.unlink(cur)
        bpy.data.objects.remove(cur)

        bpy.data.curves.remove(cu)
        
        
        return {'FINISHED'}
    
        
    
    
    
class OBJECT_OT_new_gplayer(Operator):
    """Create a new Mesh Object"""
    bl_idname = "mesh.new_gplayer"
    bl_label = "Creat new GP layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execture(self,context) :
        
        bpy.ops.gpencil.layer_add()
        
        return {"FINISHED"}


def getchildren(armature, bone) :
    
    #get all bones
    bs = armature.bones
    childlist = []
    for b in bs :
        prt = b.parent_recursive

        if bone in prt and b not in childlist :
            childlist.append(b)

    return (childlist)
        
        
        
    
def matrix_world(armature_ob, bone_name):
        local = armature_ob.data.bones[bone_name].matrix_local
        basis = armature_ob.pose.bones[bone_name].matrix_basis

        parent = armature_ob.pose.bones[bone_name].parent
        if parent == None:
            return  armature_ob.matrix_world*local * basis
        else:
            parent_local = armature_ob.data.bones[parent.name].matrix_local
            return matrix_world(armature_ob, parent.name) *(parent_local.inverted() * local) * basis    
        
        
def interpolate(t, vector_a, vector_b):
# t is from interval <0, 1>
    return (1 - t) * vector_a + t * vector_b





########################## UI

def draw_curve_button(self, context):
    self.layout.operator(
        OBJECT_OT_draw_curve.bl_idname,
        text="Draw",
        icon='PLUGIN')


class MySettings(PropertyGroup):

    lockHead = BoolProperty(
        name="Enable or Disable",
        description="Lock the head position of the bone",
        default = False
        )
    lockTail = BoolProperty(
        name="Enable or Disable",
        description="Lock the tail position of the bone",
        default = False
        )
    lockChildren = BoolProperty(
        name="Enable or Disable",
        description="Lock children bones positions",
        default = False
        )
    preserveScale = BoolProperty(
        name="",
        description="Preserve the scale of the bone",
        default = True
        )
    influence = FloatProperty(
        name="Enable or Disable",
        description="Influence of the stroke",
        default = 1.00,
        soft_min = 0.00,
        soft_max = 1.00
        )
    


class UIListPanelExample(Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = 'OBJECT_PT_my_panel'
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Grease Pencil Snap"
    bl_category="Grease Pencil" 

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene
        mytool = scn.my_tool
        
        rows = 2
        row = layout.row(align=True)
        row.prop(mytool, "preserveScale",  icon='ARROW_LEFTRIGHT')
        row.operator("pose.snap_curve")
        row = layout.row(align=True)
        
        row.prop(mytool, "influence", text="Influence", emboss=True)
        row = layout.row(align=True)
        row.prop(mytool, "lockTail",  icon='NDOF_DOM', text="Tail")
        row.prop(mytool, "lockHead",  icon='NDOF_DOM', text="Head")
        #row = layout.row(align=True)
        #row.prop(mytool, "lockChildren",  icon='GROUP_BONE', text="Lock Children")
        
        
########################## REGISTRATION

def register():
    bpy.utils.register_class(OBJECT_OT_snap_curve)
    bpy.utils.register_class(OBJECT_OT_new_gplayer)
    bpy.utils.register_class(UIListPanelExample)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)
    #bpy.types.VIEW3D_MT_view.append(snap_curve_button)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_snap_curve)
    bpy.utils.unregister_class(OBJECT_OT_new_gplayer)
    bpy.utils.unregister_class(UIListPanelExample)
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool
    #bpy.types.VIEW3D_MT_view.remove(snap_curve_button)


if __name__ == "__main__" :
    register()