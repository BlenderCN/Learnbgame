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
#
#
#  Author: Sebastian Schneider
#  Web: http://www.noeol.de
#
#  Update: Apr/02/2012
#
#  tested with:
#  Blender 2.62.0 r44136 
#  MacOS 10.7.3 (64-Bit Intel)
#  Linux (Ubuntu 11.10)
#  




bl_info = {
    'name': "Stereoscopic Camera",
    'author': "Sebastian Schneider <s.schneider@noeol.de>",
    'version': (1, 6, 7),
    'blender': (2, 6, 2),
    'api': 44136,
    'location': "Select a Camera > Properties Panel > Camera Panel > Stereoscopic Camera",
    'description': "Adds an 'Off-Axis', 'Toe-In' or 'Parallel' stereo camera rig",
    'warning': "", 
    'wiki_url': "",
    'tracker_url': "",
    'category': "Object"}



import bpy
import mathutils
from math import *
from bpy.props import *



#
# GUI (Panel)
#
class OBJECT_PT_stereo_camera(bpy.types.Panel):

    bl_label = "Stereoscopic Camera"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    # show this add-on only in the Camera-Data-Panel
    @classmethod
    def poll(self, context):
        return context.active_object.type  == 'CAMERA'

    #
    # Add some custom stereo properties to the selected camera
    #
    bpy.types.Object.stereo_camera_separation = bpy.props.FloatProperty(
        attr="stereo_camera_separation",
        name='stereo_camera_separation',
        description='Camera Separation in 1/1000 Blender Units',
        min=0.0, soft_min=0.0, max=10000, soft_max=10000, default=300)
        
    bpy.types.Object.stereo_focal_distance = bpy.props.FloatProperty(
        attr="stereo_focal_distance",
        name='stereo_focal_distance', 
        description='Distance to the Stereo-Window (Zero Parallax) in Blender Units',
        min=0.0, soft_min=0.0, max=1000, soft_max=1000, default=20)
        
    bpy.types.Object.max_parallax = bpy.props.FloatProperty(
        attr="max_parallax",
        name="max_parallax", 
        description='Max parallax angle in degree. Default 1.0', 
        min=0.0, soft_min=0.0, max=3.0, soft_max=3.0, default=1.0)
        
    bpy.types.Object.near_plane_distance = bpy.props.FloatProperty(
        attr="near_plane_distance",
        name="near_plane_distance", 
        description='Distance to Near-Plane in Blender Units (has no effect on the stereo output)',
        min=0.0, soft_min=0.0, max=100000, soft_max=100000, default=10)
        
    bpy.types.Object.far_plane_distance = bpy.props.FloatProperty(
        attr="far_plane_distance", 
        name="far_plane_distance",
        description='Distance to Far-Plane in Blender Units (has no effect on the stereo output)',
        min=0.0, soft_min=0.0, max=100000, soft_max=100000, default=100)
        
    bpy.types.Object.viewer_distance = bpy.props.FloatProperty(
        attr="viewer_distance",
        name="viewer_distance", 
        description='Distance between Viewer and the Projection Screen (e.g. Theater canvas, Stereo-TV or Display) in inch', 
        min=0.0, soft_min=0.0, max=10000, soft_max=10000, default=20)
        
    bpy.types.Object.stereo_camera_shift_x = bpy.props.FloatProperty(
        attr="stereo_camera_shift_x",
        name="stereo_camera_shift_x")
        
    bpy.types.Object.stereo_camera_delta = bpy.props.FloatProperty(
        attr="stereo_camera_delta", 
        name="stereo_camera_delta")
        
    bpy.types.Object.max_disparity = bpy.props.FloatProperty(
        attr="max_disparity", 
        name="max_disparity")

    bpy.types.Object.toein_angle = bpy.props.FloatProperty(
        attr="toein_angle", 
        name="toein_angle")
    
    bpy.types.Object.screen_ppi = bpy.props.IntProperty(
        attr="screen_ppi",
        name="screen_ppi", 
        description='Pixel per Inch on the Projection Screen (Theater Canvas, Stereo TV or Display)', 
        min=1, soft_min=1, max=1000, soft_max=1000, default=96)
    
    bpy.types.Object.show_stereo_window = bpy.props.BoolProperty(
        attr="show_stereo_window", 
        name="show_stereo_window", 
        default=True)
        
    bpy.types.Object.show_near_far_plane = bpy.props.BoolProperty(
        attr="show_near_far_plane", 
        name="show_near_far_plane", 
        default=False)    
    
    bpy.types.Object.camera_type = bpy.props.EnumProperty(
        attr="camera_type",
        items=( ("OFFAXIS", "Off-Axis", "Default (best stereo result)"),
                ("CONVERGE", "Converge", "Toe-In Camera (could create uncomfortable vertical parallax)"),
                ("PARALLEL", "Parallel", "Simple stereo camera (zero parallax at infinity)")),
        name="camera_type", 
        description="", 
        default="OFFAXIS")

    #
    # draw the gui
    #
    def draw(self, context):
        layout = self.layout

        # get the custom stereo camera properties
        camera = context.scene.camera
        tmp_cam = context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            camera = bpy.data.objects[camera.name[2:]]

        # cam separation input
        row = layout.row()
        row.prop(camera, "camera_type", text="Stereo Camera Type", expand=True)

        # cam separation input
        row = layout.row()
        row.prop(camera, "stereo_camera_separation", text="Camera Separation")

        # OFF-AXIS:
        if(camera.camera_type == "OFFAXIS"):
            # focal distance input
            row = layout.row()
            row.prop(camera, "stereo_focal_distance", text="Zero Parallax")
            
            # show the zero parallax (stereo window as a plane) or not
            col = layout.column(align=True)
            col.prop(camera, "show_stereo_window", text="Show Stereo Window (Zero Parallax)")
            #col.separator()
    
            # boolean: show the near- and far plane or not
            col = layout.column(align=True)
            col.prop(camera, "show_near_far_plane", text="Auto set of Near- and Farplane")
            if(camera.show_near_far_plane):
                split = layout.split()
                
                # near- and far plane distance input
                col = split.column(align=True)
                col.label(text="Max Parallax:")
                col.prop(camera, "max_parallax", text="Angle")
    
                # user parameters for viewer distance and screen resolution          
                col = split.column(align=True)
                col.active = camera.show_near_far_plane
                col.prop(camera, "viewer_distance", text="Dist") # viewer distance in inch
                col.prop(camera, "screen_ppi", text="PPI") # pixel per inch
            
                # show the parallax info
                col = layout.column(align=True)
                col.active = camera.show_near_far_plane
        
        # CONVERGE (Toe-In):
        if(camera.camera_type == "CONVERGE"):
            # focal distance input
            row = layout.row()
            row.prop(camera, "stereo_focal_distance", text="Zero Parallax")
            
            # show the zero parallax (stereo window as a plane) or not
            col = layout.column(align=True)
            col.prop(camera, "show_stereo_window", text="Show Stereo Window (Zero Parallax)")
            #col.separator()
        
        # PARALLEL:
        if(camera.camera_type == "PARALLEL"):
            pass
    
        # 'Set Stereo Camera' button
        row = layout.row()
        row.operator('stereocamera.set_stereo_camera')
        
        # Set active render camera
        col = layout.column(align=True)
        col.separator()
        col.label(text="Active Render Camera: "+tmp_cam.name)

        # Set active render camera
        row = layout.row(align=True) 
        row.operator('stereocamera.set_left_as_render_cam')
        row.operator('stereocamera.set_center_as_render_cam')
        row.operator('stereocamera.set_right_as_render_cam')  
        
        # Create Left and Right Scene
        row = layout.row()
        row.operator('stereocamera.create_left_right_scene')



#
# 'Set Left Camera' Operator
#
class OBJECT_OT_set_left_render_camera(bpy.types.Operator):
    bl_label = 'Left'
    bl_idname = 'stereocamera.set_left_as_render_cam'
    bl_description = 'Set Left as active Render Camera'
    bl_options = {'REGISTER', 'UNDO'}

    # on mouse up:
    def invoke(self, context, event):
        camera = bpy.context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[camera.name[2:]]
        else:
            center_cam = camera
            
        active_cam = bpy.data.objects['L_'+center_cam.name]
        bpy.context.scene.camera = active_cam
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = active_cam
        active_cam.select = True
        
        return {'FINISHED'}



#
# 'Set Center Camera' Operator
#
class OBJECT_OT_set_center_render_camera(bpy.types.Operator):
    bl_label = 'Center'
    bl_idname = 'stereocamera.set_center_as_render_cam'
    bl_description = 'Set Center as active Render Camera'
    bl_options = {'REGISTER', 'UNDO'}
    
    # on mouse up:
    def invoke(self, context, event):
        camera = bpy.context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[camera.name[2:]]
        else:
            center_cam = camera
            
        active_cam = bpy.data.objects[center_cam.name]
        bpy.context.scene.camera = active_cam
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = active_cam
        active_cam.select = True
        
        return {'FINISHED'}



#
# 'Set Right Camera' Operator
#
class OBJECT_OT_set_right_render_camera(bpy.types.Operator):
    bl_label = 'Right'
    bl_idname = 'stereocamera.set_right_as_render_cam'
    bl_description = 'Set Right as active Render Camera'
    bl_options = {'REGISTER', 'UNDO'}
    
    # on mouse up:
    def invoke(self, context, event):
        camera = bpy.context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[camera.name[2:]]
        else:
            center_cam = camera
            
        active_cam = bpy.data.objects['R_'+center_cam.name]
        bpy.context.scene.camera = active_cam
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = active_cam
        active_cam.select = True
        
        return {'FINISHED'}


#
# Operator 'Set Stereo Camera'
#
class OBJECT_OT_set_stereo_camera(bpy.types.Operator):
    bl_label = 'Set Stereo Camera'
    bl_idname = 'stereocamera.set_stereo_camera'
    bl_description = 'Setup the Stereoscopic Camera'
    bl_options = {'REGISTER', 'UNDO'}

    # call the operator 'Set Stereo Camera'
    def execute(self, context):
	
        # do the stereoscopic calculation
        self.stereoscopic_calculation(context)

        # do the settings (add or set the left/right camera)
        self.set_left_right_stereo_camera(context)

        return {'FINISHED'}

    #
    # Stereoscopic calculation
    #
    def stereoscopic_calculation(self, context):
        
        import math
        import bpy
    
        # get the custom stereo camera properties
        camera = context.scene.camera
        if(camera.name[:2]=="L_" or camera.name[:2]=="R_"):
            camera = bpy.data.objects[camera.name[2:]]
            
        stereo_base = camera.stereo_camera_separation/1000 # 1/1000 Blender Units
        focal_dist = camera.stereo_focal_distance
        camera_fov = camera.data.angle
        theta = camera.max_parallax
        viewer_dist = camera.viewer_distance
        ppi = camera.screen_ppi
    
    	# get the horizonal render resolution
        render_width = context.scene.render.resolution_x
        render_factor = bpy.context.scene.render.resolution_percentage/100
        render_width = render_width * render_factor
    
        # OFF-AXIS:
        if(camera.camera_type=="OFFAXIS"):
            # calculate delta in pixel at zero parallax:
            camera.stereo_camera_delta = (render_width*stereo_base)/(2*focal_dist*math.tan(camera_fov/2))
            # calculate blenders camera shift_x depending on render resolution and delta in pixel:
            camera.stereo_camera_shift_x = camera.stereo_camera_delta/render_width

            ### DEUBUG ###
            print('')
            print("### Stereoscopic Off-Axis shift ###")
            print("Render Width: "+str(render_width)+" Pixel")
            print("Stereo Base: "+str(stereo_base)+" B.U.")
            print("Focal Distance: "+str(focal_dist)+" B.U.")
            print("Camera Angle FoV: "+str(camera_fov)+ " Radians"+" (or "+str(math.degrees(camera_fov))+" Degree)")
            print("Delta Zero Parallax: "+str(camera.stereo_camera_delta)+ " Pixel")
            print('')
            #### DEBUG ###
           
            if(camera.show_near_far_plane):
                # calculate the maximum parallax in pixel for the given angle
                alpha = math.radians(theta/2)
                beta = math.radians(90-alpha)
                camera.max_disparity = ((math.sin(alpha))*viewer_dist) / ((math.sin(beta)))
                camera.max_disparity = (camera.max_disparity*2)*ppi
                
                ### DEBUG ###
                print("Max. Delta at Near- and Farplane: "+str(camera.max_disparity)+" Pixel")
                ### DEBUG ###

                # calculate near- and farplane distance
                delta = camera.stereo_camera_delta
                disparity = camera.max_disparity
                camera.near_plane_distance = ( ((stereo_base*render_width)/(delta+disparity)) / (math.tan(camera_fov/2)) ) / 2
                ### DEBUG ###
                print("Nearplane Distance: "+str(camera.near_plane_distance)+" B.U.")
                ### DEBUG ###
                if(delta>disparity):
                    camera.far_plane_distance = ( ((stereo_base*render_width)/(delta-disparity)) / (math.tan(camera_fov/2)) ) / 2
                    ### DEBUG ###
                    print("Farplane Distance: "+str(camera.far_plane_distance)+" B.U.")
                    print('')
                    ### DEBUG ###
                else:
                    camera.far_plane_distance = camera.data.clip_end # farplane at infinity
                    ### DEBUG ###
                    print("Farplane Distance: > Camera Clip End at "+str(camera.data.clip_end)+" B.U.")
                    print('')
                    ### DEBUG ###
            
        if(camera.camera_type=="CONVERGE"):
            # calculate (inward-)rotation angle of the left and right camera
            camera.toein_angle = math.degrees( math.atan2((stereo_base/2), focal_dist) )
            ### DEBUG ###
            print('')
            print('### Stereoscopic Converge/Toein camera ###')
            print("Stereo Base: "+str(stereo_base)+" B.U.")
            print("Focal Distance: "+str(focal_dist)+" B.U.")
            print("Camera Angle FoV: "+str(camera_fov)+ " Radians"+' (or '+str(math.degrees(camera_fov))+' Degree)')
            print("Toein Angle: "+str(camera.toein_angle)+' Degree (each camera)')
            print('')
            ### DEBUG ###
            
        if(camera.camera_type=="PARALLEL"):
            pass
            
        return {'FINISHED'}
    
    #
    # Add or Set the Left- and right Camera
    #
    def set_left_right_stereo_camera(op, context):

        import math
        import bpy
    
        tmp_camera = bpy.context.scene.camera 
        if(tmp_camera.name[:2]=="L_" or tmp_camera.name[:2]=="R_"):
            center_cam = bpy.data.objects[tmp_camera.name[2:]]
        else:
            center_cam = tmp_camera
        active_cam = bpy.data.objects[center_cam.name]
        bpy.context.scene.camera = active_cam
        camera = bpy.context.scene.camera 
    
        # check for existing stereocamera objects
        left_cam_exists = 0
        right_cam_exists = 0
        zero_plane_exists = 0
        near_plane_exists = 0
        far_plane_exists = 0
        scn = bpy.context.scene
        for ob in scn.objects:
            if(ob.name == "L_"+center_cam.name):
                left_cam_exists = 1
            if(ob.name == "R_"+center_cam.name):
                right_cam_exists = 1
            if(ob.name == "SW_"+center_cam.name):
                zero_plane_exists = 1
            if(ob.name == "NP_"+center_cam.name):
                near_plane_exists = 1
            if(ob.name == "FP_"+center_cam.name):
                far_plane_exists = 1
    
        # add a new or (if exists) get the left camera
        if(left_cam_exists==0):
            left_cam = bpy.data.cameras.new('L_'+center_cam.name)
            left_cam_obj = bpy.data.objects.new('L_'+center_cam.name, left_cam)
            scn.objects.link(left_cam_obj)
        else:
            left_cam_obj = bpy.data.objects['L_'+center_cam.name]  
            left_cam = left_cam_obj.data 
    
        # add a new or (if exists) get the right camera
        if(right_cam_exists==0):
            right_cam = bpy.data.cameras.new('R_'+center_cam.name)
            right_cam_obj = bpy.data.objects.new('R_'+center_cam.name, right_cam)
            scn.objects.link(right_cam_obj)    
        else:
            right_cam_obj = bpy.data.objects['R_'+center_cam.name]
            right_cam = right_cam_obj.data


        # add a new or (if exists) get the zero parallax plane
        if(zero_plane_exists==0):
            add_plane = bpy.ops.mesh.primitive_plane_add
            add_plane(location=(0,0,0), layers=(True, False, False,False, False, False, False, False, False, False, False, False,False, False, False, False, False, False, False, False))
            zero_plane_obj = bpy.context.active_object
            zero_plane_obj.name = 'SW_'+center_cam.name
        else:
            zero_plane_obj = bpy.data.objects['SW_'+center_cam.name]
        
        # add a new or (if exists) get the near plane
        if(near_plane_exists==0):
            add_plane = bpy.ops.mesh.primitive_plane_add
            add_plane(location=(0,0,0), layers=(True, False, False,False, False, False, False, False, False, False, False, False,False, False, False, False, False, False, False, False))
            near_plane_obj = bpy.context.active_object
            near_plane_obj.name = 'NP_'+center_cam.name
        else:
            near_plane_obj = bpy.data.objects['NP_'+center_cam.name]
        
      	# add a new or (if exists) get the far plane
        if(far_plane_exists==0):
            add_plane = bpy.ops.mesh.primitive_plane_add
            add_plane(location=(0,0,0), layers=(True, False, False,False, False, False, False, False, False, False, False, False,False, False, False, False, False, False, False, False))
            far_plane_obj = bpy.context.active_object
            far_plane_obj.name = 'FP_'+center_cam.name
        else:
            far_plane_obj = bpy.data.objects['FP_'+center_cam.name]         

        # OFF-AXIS:
        if(camera.camera_type=="OFFAXIS"):
            
            # set the left camera
            left_cam.angle = center_cam.data.angle
            left_cam.clip_start = center_cam.data.clip_start
            left_cam.clip_end = center_cam.data.clip_end
            left_cam.dof_distance = center_cam.data.dof_distance
            left_cam.dof_object = center_cam.data.dof_object
            left_cam.shift_y = center_cam.data.shift_y
            left_cam.shift_x = (camera.stereo_camera_shift_x/2)+center_cam.data.shift_x
            left_cam_obj.location = -(camera.stereo_camera_separation/1000)/2,0,0
            left_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset
    
            # set the right camera
            right_cam.angle = center_cam.data.angle
            right_cam.clip_start = center_cam.data.clip_start
            right_cam.clip_end = center_cam.data.clip_end
            right_cam.dof_distance = center_cam.data.dof_distance
            right_cam.dof_object = center_cam.data.dof_object
            right_cam.shift_y = center_cam.data.shift_y
            right_cam.shift_x = -(camera.stereo_camera_shift_x/2)+center_cam.data.shift_x
            right_cam_obj.location = (camera.stereo_camera_separation/1000)/2,0,0
            right_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset
    
            # set the planes
            zero_plane_obj.location = (0,0,-camera.stereo_focal_distance)
            near_plane_obj.location = (0,0,-camera.near_plane_distance)
            far_plane_obj.location = (0,0,-camera.far_plane_distance)
    		
            # set the 'real size' of the planes (frustum) 
            scene = bpy.context.scene
            render_width = scene.render.resolution_x
            render_height = scene.render.resolution_y
            camera_fov = math.degrees(center_cam.data.angle)
            alpha = math.radians(camera_fov/2)
            beta  = math.radians(90-(camera_fov/2))
            # stereo window:
            sw_x = ((math.sin(alpha))*camera.stereo_focal_distance) / ((math.sin(beta)))
            sw_y = (render_height * sw_x) / render_width
            zero_plane_obj.scale[0] = (sw_x)
            zero_plane_obj.scale[1] = (sw_y)
            # near plane:
            sw_x = ((math.sin(alpha))*camera.near_plane_distance) / ((math.sin(beta)))
            sw_y = (render_height * sw_x) / render_width
            near_plane_obj.scale[0] = (sw_x)
            near_plane_obj.scale[1] = (sw_y)   
            # far plane:
            sw_x = ((math.sin(alpha))*camera.far_plane_distance) / ((math.sin(beta)))
            sw_y = (render_height * sw_x) / render_width
            far_plane_obj.scale[0] = (sw_x)
            far_plane_obj.scale[1] = (sw_y)   
                
            # do not render the planes
            zero_plane_obj.hide_render = True
            near_plane_obj.hide_render = True
            far_plane_obj.hide_render = True
            
            # show the zero-parallax-plane (stereo window) or not
            if(camera.show_stereo_window):
                zero_plane_obj.hide = False
            else:
                zero_plane_obj.hide = True
    
            # show the near- and far-plane or not
            if(camera.show_near_far_plane):
                near_plane_obj.hide = False
                far_plane_obj.hide = False
            else:
                near_plane_obj.hide = True
                far_plane_obj.hide = True


            # add the left/right camera and zero-parallax-plane as child
            left_cam_obj.parent = center_cam
            right_cam_obj.parent = center_cam
            zero_plane_obj.parent = center_cam
            near_plane_obj.parent = center_cam
            far_plane_obj.parent = center_cam  
    
        # CONVERGE (Toe-in):
        if(camera.camera_type=="CONVERGE"):
            # set the left camera
            left_cam.angle = center_cam.data.angle
            left_cam.clip_start = center_cam.data.clip_start
            left_cam.clip_end = center_cam.data.clip_end
            left_cam.dof_distance = center_cam.data.dof_distance
            left_cam.dof_object = center_cam.data.dof_object
            left_cam.shift_y = center_cam.data.shift_y
            left_cam.shift_x = center_cam.data.shift_x # reset
            left_cam_obj.location = -(camera.stereo_camera_separation/1000)/2,0,0
            left_cam_obj.rotation_euler = (0.0,-math.radians(camera.toein_angle),0.0)
    
            # set the right camera
            right_cam.angle = center_cam.data.angle
            right_cam.clip_start = center_cam.data.clip_start
            right_cam.clip_end = center_cam.data.clip_end
            right_cam.dof_distance = center_cam.data.dof_distance
            right_cam.dof_object = center_cam.data.dof_object
            right_cam.shift_y = center_cam.data.shift_y
            right_cam.shift_x = center_cam.data.shift_x # reset
            right_cam_obj.location = (camera.stereo_camera_separation/1000)/2,0,0
            right_cam_obj.rotation_euler = (0.0,math.radians(camera.toein_angle),0.0)
    
            # set the zero parallax plane
            zero_plane_obj.location = (0,0,-camera.stereo_focal_distance)
    		
    		# set the 'real size' of the plane (frustum) 
            scene = bpy.context.scene
            render_width = scene.render.resolution_x
            render_height = scene.render.resolution_y
            camera_fov = math.degrees(center_cam.data.angle)
            alpha = math.radians(camera_fov/2)
            beta  = math.radians(90-(camera_fov/2))
    		# stereo window:
            sw_x = ((math.sin(alpha))*camera.stereo_focal_distance) / ((math.sin(beta)))
            sw_y = (render_height * sw_x) / render_width
            zero_plane_obj.scale[0] = (sw_x)
            zero_plane_obj.scale[1] = (sw_y)
                
            # do not render the planes
            zero_plane_obj.hide_render = True
            
            # show the zero-parallax-plane (stereo window) or not
            if(camera.show_stereo_window):
                zero_plane_obj.hide = False
            else:
                zero_plane_obj.hide = True
    
            # do not show the near- and far-plane
            near_plane_obj.hide = True
            far_plane_obj.hide = True
    
            # add the left/right camera and zero-parallax-plane as child
            left_cam_obj.parent = center_cam
            right_cam_obj.parent = center_cam
            zero_plane_obj.parent = center_cam

        # PARALLEL:
        if(camera.camera_type=="PARALLEL"):
            # set the left camera
            left_cam.angle = center_cam.data.angle
            left_cam.clip_start = center_cam.data.clip_start
            left_cam.clip_end = center_cam.data.clip_end
            left_cam.dof_distance = center_cam.data.dof_distance
            left_cam.dof_object = center_cam.data.dof_object
            left_cam.shift_y = center_cam.data.shift_y
            left_cam.shift_x = center_cam.data.shift_x # reset
            left_cam_obj.location = -(camera.stereo_camera_separation/1000)/2,0,0
            left_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset
    
            # set the right camera
            right_cam.angle = center_cam.data.angle
            right_cam.clip_start = center_cam.data.clip_start
            right_cam.clip_end = center_cam.data.clip_end
            right_cam.dof_distance = center_cam.data.dof_distance
            right_cam.dof_object = center_cam.data.dof_object
            right_cam.shift_y = center_cam.data.shift_y
            right_cam.shift_x = center_cam.data.shift_x # reset
            right_cam_obj.location = (camera.stereo_camera_separation/1000)/2,0,0
            right_cam_obj.rotation_euler = (0.0,0.0,0.0) # reset

            # do not show any planes
            zero_plane_obj.hide = True
            near_plane_obj.hide = True
            far_plane_obj.hide = True
                
            # do not render the planes
            zero_plane_obj.hide_render = True
            near_plane_obj.hide_render = True
            far_plane_obj.hide_render = True
    
            # add the left/right camera as child
            left_cam_obj.parent = center_cam
            right_cam_obj.parent = center_cam                    

        # select the center camera (object mode)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.camera = tmp_camera
        bpy.context.scene.objects.active = tmp_camera
        tmp_camera.select = True
        
        return {'FINISHED'} 


#
# 'Create L and R Scene' Operator
#
class OBJECT_OT_create_left_right_scene(bpy.types.Operator):
    bl_label = 'Create L and R Scene'
    bl_idname = 'stereocamera.create_left_right_scene'
    bl_description = 'Create Left and Right Camera Scene'
    bl_options = {'REGISTER', 'UNDO'}
    
    # on mouse up:
    def execute(self, context):
        camera = bpy.context.scene.camera
        
        # check for existing cameras
        scn = bpy.context.scene
        left_cam_exists = 0
        right_cam_exists = 0
        for ob in scn.objects:
            if(ob.name[:2]=="L_"):
                left_cam_exists = 1
            if(ob.name[:2]=="R_"):
                right_cam_exists = 1
        
        # ok, call the function
        if(left_cam_exists and right_cam_exists):
            self.create_scenes(context)
                    
        return {'FINISHED'}
    
    #
    # create new left and right camera scene
    #
    def create_scenes(self, context):
        
        import bpy
        
        center_scene = context.scene
        center_cam_name = context.scene.camera.name
        
        # delete left and right camera scenes if exists 
        try:
            bpy.data.scenes.remove(bpy.data.scenes['Left_Camera'])
            bpy.data.scenes.remove(bpy.data.scenes['Right_Camera'])
        except:
            pass
            
        # Create Left Scene
        bpy.ops.scene.new(type='LINK_OBJECTS')
        left_scene = context.scene
        left_scene.name = "Left_Camera"
        left_scene.camera = bpy.data.objects["L_"+center_cam_name]
        left_scene.background_set = center_scene

        # Create Right Scene
        bpy.ops.scene.new(type='LINK_OBJECTS')
        right_scene = context.scene
        right_scene.name = "Right_Camera"
        right_scene.camera = bpy.data.objects["R_"+center_cam_name]
        right_scene.background_set = center_scene
        
        # back to the center scene
        context.screen.scene = center_scene
    
        return {'FINISHED'}



#
# Stereoscopic Node presets
#    
class NODE_EDITOR_PT_preset(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Stereoscopic presets"

    @classmethod
    def poll(cls, context):
        view = context.space_data
        return (view)

    def draw(self, context):
        scn = bpy.context.scene
        view = context.space_data

        if (view.tree_type == 'COMPOSITING') and (view.id.use_nodes):    
            layout = self.layout
            col = layout.column()
            row = col.row()
            row.prop(scn, 'stereo_comp_presets')
        
            row = layout.row()
            row.operator('stereocamera.add_stereo_node_preset')
        else:
            layout = self.layout
            row = layout.row() 
            row.label(text="Info: ")
            row = layout.row() 
            row.label(text="Select 'COMPOSITING'")
            row = layout.row()
            row.label(text="and check 'Use Nodes'")



#
# Operator 'Add stereoscopic preset'
#
class OBJECT_OT_add_stereo_node_preset(bpy.types.Operator):
    bl_label = 'Add nodes'
    bl_idname = 'stereocamera.add_stereo_node_preset'
    bl_description = 'Adds a stereoscopic node preset'

    # on mouse up:
    def invoke(self, context, event):

        # add the selected preset
        self.add_preset(context)

        return {'FINISHED'}

    #
    # add the node presets
    #
    def add_preset(self, context):
        
        import bpy
        
        scene = bpy.context.scene
        
        tree = scene.node_tree
        
        render_factor = bpy.context.scene.render.resolution_percentage/100
        
        res_x = int(scene.render.resolution_x * render_factor)
        res_y = int(scene.render.resolution_y * render_factor)
     
        #
        # Side-by-Side
        #
        if(scene.stereo_comp_presets == "SIDEBYSIDE"):
     
            # create a background canvas to get the final image(or sequence) output bigger than the render resolution
            try:
                canvas_img = bpy.data.images['canvas'+str(res_x*2)+'x'+str(res_y)]
            except:
                bpy.ops.image.new(name='canvas'+str(res_x*2)+'x'+str(res_y), width=(res_x*2), height=res_y, color=(0,0,0,1))
                canvas_img = bpy.data.images['canvas'+str(res_x*2)+'x'+str(res_y)]

            if(canvas_img.generated_width != (res_x*2) or canvas_img.generated_height != res_y):
                bpy.ops.image.new(name='canvas'+str(res_x*2)+'x'+str(res_y), width=(res_x*2), height=res_y, color=(0,0,0,1))
                canvas_img = bpy.data.images['canvas'+str(res_x*2)+'x'+str(res_y)]    

            # scene render layer (will not be used but has to be in the node tree to handle animations)
            center_render_layer = tree.nodes.new('R_LAYERS')
            center_render_layer.location = (-20,450)

            # set the camvas image node
            canvas_node = tree.nodes.new('IMAGE')
            canvas_node.location = (-800,150)
            canvas_node.image = bpy.data.images['canvas'+str(res_x*2)+'x'+str(res_y)]
            
            # set the left image node
            #left_view = tree.nodes.new('IMAGE')
            #left_view.location = (-600,270)
            left_render_layer = tree.nodes.new('R_LAYERS')
            left_render_layer.location = (-600,270)
            try: 
                left_render_layer.scene = bpy.data.scenes['Left_Camera']
            except:
                pass
            
            # set the right image node 
            #right_view = tree.nodes.new('IMAGE')
            #right_view.location = (-600,0)
            right_render_layer = tree.nodes.new('R_LAYERS')
            right_render_layer.location = (-600,0)
            try: 
                right_render_layer.scene = bpy.data.scenes['Right_Camera']
            except:
                pass
            
            # shift the left image to the left
            left_translate = tree.nodes.new('TRANSLATE')
            left_translate.location = (-400, 250)
            left_translate.inputs[1].default_value = -(int(res_x/2))
            left_translate.inputs[2].default_value = 0
            
            # shift the right image to the right
            right_translate = tree.nodes.new('TRANSLATE')
            right_translate.location = (-400, -20)
            right_translate.inputs[1].default_value = (int(res_x/2))
            right_translate.inputs[2].default_value = 0
           
            # mix 1
            mix_1 = tree.nodes.new('MIX_RGB')
            mix_1.location = (-190,250)
            mix_1.blend_type = 'SCREEN'
            mix_1.inputs[0].default_value = 1.0
            
            # mix 2
            mix_2 = tree.nodes.new('MIX_RGB')
            mix_2.location = (-10,100)
            mix_2.blend_type = 'SCREEN'
            mix_2.inputs[0].default_value = 1.0
            
            # file output
            file_output_node = tree.nodes.new('OUTPUT_FILE')
            file_output_node.location = (200, 100)
            
            # comp output (not needed)
            composite_node = tree.nodes.new('COMPOSITE')
            composite_node.location = (200, 400)
            
            # noodle from left view to left translate
            #tree.links.new(left_view.outputs[0], left_translate.inputs[0])
            tree.links.new(left_render_layer.outputs[0], left_translate.inputs[0]) 
               
            # noodle from right view to right translate
            #tree.links.new(right_view.outputs[0], right_translate.inputs[0])
            tree.links.new(right_render_layer.outputs[0], right_translate.inputs[0])
            
            # noodle from canvas to mix 1
            tree.links.new(canvas_node.outputs[0],mix_1.inputs[1])
            
            # noodle from left translate to mix 1
            tree.links.new(left_translate.outputs[0],mix_1.inputs[2])
            
            # noodle from right translate to mix 2
            tree.links.new(right_translate.outputs[0],mix_2.inputs[2])
            
            # noodle from mix 1 to mix 2
            tree.links.new(mix_1.outputs[0],mix_2.inputs[1])
            
            # noodle from mix 2 to file output node
            tree.links.new(mix_2.outputs[0],file_output_node.inputs[0])
            
            #noodle from mix 2 to comp node (but shows not the side-by-side image size)
            tree.links.new(mix_2.outputs[0],composite_node.inputs[0])

        #
        # Side-by-Side squashed
        #
        if(scene.stereo_comp_presets == "SQUASHED"):
            
            scale_x = res_x*0.5
            
            # create a background canvas to get the final image(or sequence) output
            try:
                canvas_img = bpy.data.images['canvas'+str(res_x)+'x'+str(res_y)]
            except:
                bpy.ops.image.new(name='canvas'+str(res_x)+'x'+str(res_y), width=res_x, height=res_y, color=(0,0,0,1))
                canvas_img = bpy.data.images['canvas'+str(res_x)+'x'+str(res_y)]

            if(canvas_img.generated_width != res_x or canvas_img.generated_height != res_y):
                bpy.ops.image.new(name='canvas'+str(res_x)+'x'+str(res_y), width=res_x, height=res_y, color=(0,0,0,1))
                canvas_img = bpy.data.images['canvas'+str(res_x)+'x'+str(res_y)] 
                
            # scene render layer (will not be used but has to be in the node tree to handle animations)
            center_render_layer = tree.nodes.new('R_LAYERS')
            center_render_layer.location = (180,400)   

            # set the camvas image node
            canvas_node = tree.nodes.new('IMAGE')
            canvas_node.location = (-800,150)
            canvas_node.image = bpy.data.images['canvas'+str(res_x)+'x'+str(res_y)]
            
            # set the left image node
            #left_view = tree.nodes.new('IMAGE')
            #left_view.location = (-600,270)
            left_render_layer = tree.nodes.new('R_LAYERS')
            left_render_layer.location = (-600,270)
            try: 
                left_render_layer.scene = bpy.data.scenes['Left_Camera']
            except:
                pass         
                        
            # set the right image node 
            #right_view = tree.nodes.new('IMAGE')
            #right_view.location = (-600,0)
            right_render_layer = tree.nodes.new('R_LAYERS')
            right_render_layer.location = (-600,0)
            try: 
                right_render_layer.scene = bpy.data.scenes['Right_Camera']
            except:
                pass
            
            # scale the left image
            left_scale = tree.nodes.new('SCALE')
            left_scale.location = (-400, 250)
            left_scale.space = 'RELATIVE'
            left_scale.inputs[1].default_value = 0.5

            # scale the right image
            right_scale = tree.nodes.new('SCALE')
            right_scale.location = (-400, 0)
            right_scale.space = 'RELATIVE'
            right_scale.inputs[1].default_value = 0.5
            
            # shift the left image to the left
            left_translate = tree.nodes.new('TRANSLATE')
            left_translate.location = (-200, 250)
            left_translate.inputs[1].default_value = -(scale_x/2)
            left_translate.inputs[2].default_value = 0
            
            # shift the right image to the right
            right_translate = tree.nodes.new('TRANSLATE')
            right_translate.location = (-200, -20)
            right_translate.inputs[1].default_value = (scale_x/2)
            right_translate.inputs[2].default_value = 0
           
            # mix 1
            mix_1 = tree.nodes.new('MIX_RGB')
            mix_1.location = (0,200)
            mix_1.blend_type = 'SCREEN'
            mix_1.inputs[0].default_value = 1.0
            
            # mix 2
            mix_2 = tree.nodes.new('MIX_RGB')
            mix_2.location = (180,100)
            mix_2.blend_type = 'SCREEN'
            mix_2.inputs[0].default_value = 1.0
        
            # comp output
            composite_node = tree.nodes.new('COMPOSITE')
            composite_node.location = (400, 100)
            
            # noodle from left view to left scale
            #tree.links.new(left_view.outputs[0], left_scale.inputs[0])
            tree.links.new(left_render_layer.outputs[0], left_scale.inputs[0])
               
            # noodle from right view to right scale
            #tree.links.new(right_view.outputs[0], right_scale.inputs[0])
            tree.links.new(right_render_layer.outputs[0], right_scale.inputs[0])

            # noodle from left scale to left translate
            tree.links.new(left_scale.outputs[0], left_translate.inputs[0]) 
               
            # noodle from right scale to right translate
            tree.links.new(right_scale.outputs[0], right_translate.inputs[0])
            
            # noodle from left translate to mix 1
            tree.links.new(left_translate.outputs[0],mix_1.inputs[2])
            
            # noodle from canvas to mix 1
            tree.links.new(canvas_node.outputs[0],mix_1.inputs[1])
            
            # noodle from mix 1 to mix 2
            tree.links.new(mix_1.outputs[0],mix_2.inputs[1])
            
            # noodle from right translate to mix 2
            tree.links.new(right_translate.outputs[0],mix_2.inputs[2])
            
            #noodle from mix 2 to comp node
            tree.links.new(mix_2.outputs[0],composite_node.inputs[0])

        #
        # Above-Under
        #   
        if(scene.stereo_comp_presets == "ABOVEUNDER"):
     
            # create a background canvas to get the final image(or sequence) output bigger than the render resolution
            try:
                canvas_img = bpy.data.images['canvas'+str(res_x)+'x'+str(res_y*2)]
            except:
                bpy.ops.image.new(name='canvas'+str(res_x)+'x'+str(res_y*2), width=res_x, height=(res_y*2), color=(0,0,0,1))
                canvas_img = bpy.data.images['canvas'+str(res_x)+'x'+str(res_y*2)]

            if(canvas_img.generated_width != res_x or canvas_img.generated_height != (res_y*2)):
                bpy.ops.image.new(name='canvas'+str(res_x)+'x'+str(res_y*2), width=res_x, height=(res_y*2), color=(0,0,0,1))
                canvas_img = bpy.data.images['canvas'+str(res_x)+'x'+str(res_y*2)]    

            # scene render layer (will not be used but has to be in the node tree to handle animations)
            center_render_layer = tree.nodes.new('R_LAYERS')
            center_render_layer.location = (-20,450)

            # set the camvas image node
            canvas_node = tree.nodes.new('IMAGE')
            canvas_node.location = (-800,150)
            canvas_node.image = bpy.data.images['canvas'+str(res_x)+'x'+str(res_y*2)]
            
            # set the left image node
            #left_view = tree.nodes.new('IMAGE')
            #left_view.location = (-600,270)
            left_render_layer = tree.nodes.new('R_LAYERS')
            left_render_layer.location = (-600,270)
            try: 
                left_render_layer.scene = bpy.data.scenes['Left_Camera']
            except:
                pass
           
            # set the right image node 
            #right_view = tree.nodes.new('IMAGE')
            #right_view.location = (-600,0)
            right_render_layer = tree.nodes.new('R_LAYERS')
            right_render_layer.location = (-600,0)
            try: 
                right_render_layer.scene = bpy.data.scenes['Right_Camera']
            except:
                pass
            
            # shift the left image to the top
            left_translate = tree.nodes.new('TRANSLATE')
            left_translate.location = (-400, 250)
            left_translate.inputs[1].default_value = 0
            left_translate.inputs[2].default_value = int(res_y/2)
            
            # shift the right image to the bottom
            right_translate = tree.nodes.new('TRANSLATE')
            right_translate.location = (-400, -20)
            right_translate.inputs[1].default_value = 0
            right_translate.inputs[2].default_value = -(int(res_y/2))
           
            # mix 1
            mix_1 = tree.nodes.new('MIX_RGB')
            mix_1.location = (-190,250)
            mix_1.blend_type = 'SCREEN'
            mix_1.inputs[0].default_value = 1.0
            
            # mix 2
            mix_2 = tree.nodes.new('MIX_RGB')
            mix_2.location = (-10,100)
            mix_2.blend_type = 'SCREEN'
            mix_2.inputs[0].default_value = 1.0
            
            # file output
            file_output_node = tree.nodes.new('OUTPUT_FILE')
            file_output_node.location = (200, 100)
            
            # comp output (not needed)
            composite_node = tree.nodes.new('COMPOSITE')
            composite_node.location = (200, 400)
            
            # noodle from left view to left translate
            #tree.links.new(left_view.outputs[0], left_translate.inputs[0]) 
            tree.links.new(left_render_layer.outputs[0], left_translate.inputs[0]) 
               
            # noodle from right view to right translate
            #tree.links.new(right_view.outputs[0], right_translate.inputs[0])
            tree.links.new(right_render_layer.outputs[0], right_translate.inputs[0])
            
            # noodle from canvas to mix 1
            tree.links.new(canvas_node.outputs[0],mix_1.inputs[1])
            
            # noodle from left translate to mix 1
            tree.links.new(left_translate.outputs[0],mix_1.inputs[2])
            
            # noodle from right translate to mix 2
            tree.links.new(right_translate.outputs[0],mix_2.inputs[2])
            
            # noodle from mix 1 to mix 2
            tree.links.new(mix_1.outputs[0],mix_2.inputs[1])
            
            # noodle from mix 2 to file output node
            tree.links.new(mix_2.outputs[0],file_output_node.inputs[0])
            
            #noodle from mix 2 to comp node (but shows not the side-by-side image size)
            tree.links.new(mix_2.outputs[0],composite_node.inputs[0])            

        #
        # Interlaced (left image first)
        #
        if(scene.stereo_comp_presets == "INTERLACED"):
            
            # 1. create an 'interlaced image' as alpha mask
            #    this image has just one(two) column and (resolution) y rows
            #    with one pixel black -> next white -> next black -> and so on 
            #
            # create empty image (width: 2 pixel (why two pixle?, see comment above the loop), height: y render size)
            #
            try:
                interlaced_mask = bpy.data.images['interlaced_'+str(res_y)]
            except:
                bpy.ops.image.new(name='interlaced_'+str(res_y), width=2, height=res_y)
                interlaced_mask = bpy.data.images['interlaced_'+str(res_y)]
    
            #
            # set pixel function
            #
            def setpixel(img, x ,y, rgba):
                width = img.size[0]        
                height = img.size[1]
                img.pixels[((y * width + x) * 4) + 0] = rgba[0]
                img.pixels[((y * width + x) * 4) + 1] = rgba[1]
                img.pixels[((y * width + x) * 4) + 2] = rgba[2]
                img.pixels[((y * width + x) * 4) + 3] = rgba[3]

            #
            # first (top-left) pixel should be black, so set a boolean if this is the case for the given vertical resolution
            #
            if(res_y % 2 == 0):
                black_first = False
            else:
                black_first = True 

            #
            # write pixels
            #
            i = 0
            j = 0
            for i in range(res_y):
                # blender's compositor can't handle images with only one column, it needs at least two,
                # so that the interlaced-mask-image can be streched via scale-node without killing blender
                for j in range(2): 
                    # setpixel() writes from bottom-left to top-right (and is horrible slow)
                    if(black_first):
                        if i % 2 == 0:
                            # black pixel
                            setpixel(interlaced_mask, j, i, (0.0, 0.0, 0.0, 1.0)) 
                        else:
                            # white pixel
                            setpixel(interlaced_mask, j, i, (1.0, 1.0, 1.0, 1.0))
                    else:
                        if i % 2 == 0:
                            # white pixel
                            setpixel(interlaced_mask, j, i, (1.0, 1.0, 1.0, 1.0)) 
                        else:
                            # black pixel
                            setpixel(interlaced_mask, j, i, (0.0, 0.0, 0.0, 1.0))


            # 2. the nodes
            #    
            # scene render layer (will not be used but has to be in the node tree to handle animations)
            center_render_layer = tree.nodes.new('R_LAYERS')
            center_render_layer.location = (250,400)   

            # set the interlaced alpha mask image node
            alpha_mask_node = tree.nodes.new('IMAGE')
            alpha_mask_node.location = (-800,150)
            alpha_mask_node.image = bpy.data.images['interlaced_'+str(res_y)]
            
            # set the left image node
            #left_view = tree.nodes.new('IMAGE')
            #left_view.location = (-600,270)
            left_render_layer = tree.nodes.new('R_LAYERS')
            left_render_layer.location = (-600,370)
            try: 
                left_render_layer.scene = bpy.data.scenes['Left_Camera']
            except:
                pass

            # set the right image node 
            #right_view = tree.nodes.new('IMAGE')
            #right_view.location = (-600,0)
            right_render_layer = tree.nodes.new('R_LAYERS')
            right_render_layer.location = (-600,0)
            try: 
                right_render_layer.scene = bpy.data.scenes['Right_Camera']
            except:
                pass

            # scale the interlaced alpha mask
            alpha_mask_scale = tree.nodes.new('SCALE')
            alpha_mask_scale.location = (-400, 140)
            alpha_mask_scale.space = 'ABSOLUTE'
            alpha_mask_scale.inputs[1].default_value = res_x
            alpha_mask_scale.inputs[2].default_value = res_y
            
            # set alpha for the right view
            set_alpha_node = tree.nodes.new('SETALPHA')
            set_alpha_node.location = (-170, 20)
            
            # alpha over node to combine left and right
            alpha_over_node = tree.nodes.new('ALPHAOVER')
            alpha_over_node.location = (50, 250)
            alpha_over_node.use_premultiply = True
            
            # comp output
            composite_node = tree.nodes.new('COMPOSITE')
            composite_node.location = (300, 100)
       
            # noodle from interlaced alpha mask to scale node
            tree.links.new(alpha_mask_node.outputs[0], alpha_mask_scale.inputs[0])                        
            # noodle from scale node to set alpha
            tree.links.new(alpha_mask_scale.outputs[0], set_alpha_node.inputs[1])

            # noodle from right view to set alpha
            tree.links.new(right_render_layer.outputs[0], set_alpha_node.inputs[0])
       
            # noodle from left view to alphaover
            tree.links.new(left_render_layer.outputs[0], alpha_over_node.inputs[1])
               
            # noodle from right set alpha to alphaover
            tree.links.new(set_alpha_node.outputs[0], alpha_over_node.inputs[2]) 
           
            #noodle from alphaover to comp node
            tree.links.new(alpha_over_node.outputs[0],composite_node.inputs[0])


        #
        # Red Cyan Anaglyph
        #   
        if(scene.stereo_comp_presets == "REDCYAN"):
            
            # scene render layer (will not be used but has to be in the node tree to handle animations)
            center_render_layer = tree.nodes.new('R_LAYERS')
            center_render_layer.location = (-900,120)
            
            # set the left image node
            #left_view = tree.nodes.new('IMAGE')
            #left_view.location = (-600,270)
            left_render_layer = tree.nodes.new('R_LAYERS')
            left_render_layer.location = (-600,270)
            try: 
                left_render_layer.scene = bpy.data.scenes['Left_Camera']
            except:
                pass
            
            # set the right image node 
            #right_view = tree.nodes.new('IMAGE')
            #right_view.location = (-600,0)
            right_render_layer = tree.nodes.new('R_LAYERS')
            right_render_layer.location = (-600,0)
            try: 
                right_render_layer.scene = bpy.data.scenes['Right_Camera']
            except:
                pass
            
            # seperate red from the left image
            left_seperate = tree.nodes.new('SEPRGBA')
            left_seperate.location = (-400,250)
           
            # seperate green and blue from the right image
            right_seperate = tree.nodes.new('SEPRGBA')
            right_seperate.location = (-400,-20)
            
            # combine red and cyan
            combine_node = tree.nodes.new('COMBRGBA')
            combine_node.location = (-150, 100)
            
            # comp output
            composite_node = tree.nodes.new('COMPOSITE')
            composite_node.location = (0, 100)
            
            # noodle from left view to seperate red
            #tree.links.new(left_view.outputs[0],left_seperate.inputs[0])
            tree.links.new(left_render_layer.outputs[0],left_seperate.inputs[0])
            
            # noodle from right view to seperate green and blue
            #tree.links.new(right_view.outputs[0],right_seperate.inputs[0]) 
            tree.links.new(right_render_layer.outputs[0],right_seperate.inputs[0])  
            
            # noodle from red seperate to combine
            tree.links.new(left_seperate.outputs[0],combine_node.inputs[0])  
            
            # noodle from cyan seperate to compine
            tree.links.new(right_seperate.outputs[1],combine_node.inputs[1])
            tree.links.new(right_seperate.outputs[2],combine_node.inputs[2])
            
            # noddle from combine to comp output 
            tree.links.new(combine_node.outputs[0],composite_node.inputs[0])        
           
        #
        # Amber BLue Anaglyph (ColorCode like)
        #   
        if(scene.stereo_comp_presets == "AMBERBLUE"):
            
            # scene render layer (will not be used but has to be in the node tree to handle animations)
            center_render_layer = tree.nodes.new('R_LAYERS')
            center_render_layer.location = (-900,120)
            
            # set the left image node
            #left_view = tree.nodes.new('IMAGE')
            #left_view.location = (-600,270)
            left_render_layer = tree.nodes.new('R_LAYERS')
            left_render_layer.location = (-600,270)
            try: 
                left_render_layer.scene = bpy.data.scenes['Left_Camera']
            except:
                pass            
            
            # set the right image node 
            #right_view = tree.nodes.new('IMAGE')
            #right_view.location = (-600,0)  
            right_render_layer = tree.nodes.new('R_LAYERS')
            right_render_layer.location = (-600,0) 
            try: 
                right_render_layer.scene = bpy.data.scenes['Right_Camera']
            except:
                pass         

            # seperate red and green from the left image
            left_seperate = tree.nodes.new('SEPRGBA')
            left_seperate.location = (-400,250)
            
            # de-saturation of the right image
            saturation_node = tree.nodes.new('HUE_SAT')
            saturation_node.location = (-400,-20)
            saturation_node.color_saturation = 0.0
            
            # combine yellow and blue
            combine_node = tree.nodes.new('COMBRGBA')
            combine_node.location = (-150, 100)  
            
            # comp output
            composite_node = tree.nodes.new('COMPOSITE')
            composite_node.location = (0, 100)          

            # noodle from left view to seperate red
            #tree.links.new(left_view.outputs[0],left_seperate.inputs[0])
            tree.links.new(left_render_layer.outputs[0],left_seperate.inputs[0])
            
            # noodle from right view to de-saturation node
            #tree.links.new(right_view.outputs[0],saturation_node.inputs[1]) 
            tree.links.new(right_render_layer.outputs[0],saturation_node.inputs[1]) 
            
            # noodle from de-saturation to combine
            tree.links.new(saturation_node.outputs[0],combine_node.inputs[2])  
            
            # noodle from yellow seperate to compine
            tree.links.new(left_seperate.outputs[0],combine_node.inputs[0])
            tree.links.new(left_seperate.outputs[1],combine_node.inputs[1])
            
            # noddle from combine to comp output 
            tree.links.new(combine_node.outputs[0],composite_node.inputs[0])                         
  
            
#
# Register
#
def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.stereo_comp_presets = bpy.props.EnumProperty(attr="stereo_comp_preset",
        items=[ ("SIDEBYSIDE", "Side by Side", "Side by Side"),
                ("SQUASHED", "Side by Side squashed", "Side by Side squashed"),
                ("ABOVEUNDER", "Above Under", "Above Under"),
                ("REDCYAN", "Red Cyan Anaglyph", "Red Cyan Anaglyph"),
                ("AMBERBLUE", "Amber Blue (ColorCode like)", "Amber Blue (ColorCode like)"),
                ("INTERLACED", "Interlaced (Left Field First)", "Interlaced (Left Field First)")],
        name="Presets", 
        description="Select a node preset", 
        default="SIDEBYSIDE")

	
def unregister():
    bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
    register()