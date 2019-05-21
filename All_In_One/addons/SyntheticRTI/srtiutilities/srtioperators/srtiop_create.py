###OPERATORS###
import bpy
import os
from ..srtifunc import *
from mathutils import Vector
from ..srtiproperties import file_lines as file_lines

#########LAMP#########
class create_lamps(bpy.types.Operator):
    """Create lamps from file"""
    bl_idname = "srti.create_lamps"
    bl_label = "Create Lamps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):


        curr_scene = context.scene
        file_path = curr_scene.srti_props.light_file_path

        if not os.path.isfile(file_path) or os.path.splitext(file_path)[1] != ".lp":
            self.report({'ERROR'}, 'No valid file selected on '+file_path)
            return {'CANCELLED'}

        bpy.ops.srti.delete_lamps() #delete exsisting lamps

        #create the main parent
        create_main(curr_scene)
        main_parent = curr_scene.srti_props.main_parent

        file = open(file_path)
        rows = file.readlines() #copy all lines in memory
        file.close()
        
        n_lights = int(rows[0].split()[0])#in the first row there is the total count of lights
        print("- Creating %i lamps ---"%n_lights)
        
        ##Use standars light, TODO add a differente object
        lamp_data = bpy.data.lamps.new(name="Project_light", type='SUN') # Create new lamp datablock.  It s going to be created outside
        
        for lamp in range(1, n_lights + 1): #step trought all lamps
            valori_riga = rows[lamp].split() #split values
            lmp_x = float(valori_riga[1])
            lmp_y = float(valori_riga[2])
            lmp_z = float(valori_riga[3])
            direction = Vector((lmp_x, lmp_y, lmp_z))

            print("-- ", lamp , 'x=', lmp_x, 'y=', lmp_y, 'z=', lmp_z) #print all values
            lamp_object = bpy.data.objects.new(name="Lamp_{0}".format(format_index(lamp, n_lights)), object_data=lamp_data) # Create new object with our lamp datablock
            curr_scene.objects.link(lamp_object) # Link lamp object to the scene so it'll appear in this scene
            lamp_object.parent = main_parent
            lamp_object.location = (lmp_x, lmp_y, lmp_z) # Place lamp to a specified location
            
            lamp_object.rotation_mode = 'QUATERNION'
            lamp_object.rotation_quaternion = direction.to_track_quat('Z','Y')
            
            ##change the name
            lamp = curr_scene.srti_props.list_lights.add()
            lamp.light = lamp_object

        self.report({'INFO'},"Created %i lamps."%n_lights)
        return{'FINISHED'}

class delete_lamps(bpy.types.Operator):
    """Delete all lamps"""
    bl_idname = "srti.delete_lamps"
    bl_label = "Delete Lamps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        lamp_list = context.scene.srti_props.list_lights
        print("- Deleting all lamps ---")
        bpy.ops.object.select_all(action='DESELECT')

        if lamp_list:
            for obj in lamp_list:
                obj.light.hide = False
                obj.light.select = True
    
        bpy.ops.object.delete()

        self.report({'INFO'},"Deleted all lamps.")

        context.scene.srti_props.list_lights.clear() #delete the idlist
        check_lamp_cam(context.scene)
        return{'FINISHED'}

#DEPRECATED
class delete_active_lamp(bpy.types.Operator):
    """Delete selected lamp"""
    bl_idname = "srti.delete_active_lamp"
    bl_label = "Delete Active Lamp"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        lamp_list = context.scene.srti_props.list_lights
        active_lamp = context.active_object 

        bpy.ops.object.select_all(action='DESELECT')

        if lamp_list:
            for index, obj in enumerate(lamp_list):
                if obj.light == active_lamp: 
                    print (obj)
                    lamp_list.remove(index)
                    active_lamp.select = True
                    bpy.ops.object.delete()
                    break
        check_lamp_cam(context.scene)
        return{'FINISHED'}

########CAMERA########
class create_cameras(bpy.types.Operator):
    """Create cameras"""
    bl_idname = "srti.create_cameras"
    bl_label = "Create Camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        curr_scene = context.scene
        print("- Creating new camera ---")
        #create the main parent
        create_main(curr_scene)
        main_parent = curr_scene.srti_props.main_parent

        camera_data = bpy.data.cameras.new("Camera")
        camera_object = bpy.data.objects.new("Camera", camera_data)
        curr_scene.objects.link(camera_object)

        camera_object.parent = main_parent
        camera_object.location = (0, 0, 2)

        camera = curr_scene.srti_props.list_cameras.add()
        camera.camera = camera_object

        self.report({'INFO'},"Created camera: %s."%camera.camera.name)
        return{'FINISHED'}

class delete_cameras(bpy.types.Operator):
    """Delete all cameras"""
    bl_idname = "srti.delete_cameras"
    bl_label = "Delete Cameras"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        curr_scene = context.scene
        camera_list = curr_scene.srti_props.list_cameras
        print("- Deleting all cameras ---")
        bpy.ops.object.select_all(action='DESELECT')

        if camera_list:
            for obj in camera_list:
                obj.camera.select = True

        bpy.ops.object.delete()

        context.scene.srti_props.list_cameras.clear() #delete the idlist
        check_lamp_cam(context.scene)
        self.report({'INFO'},"Deleted all cameras")
        return{'FINISHED'}


#DEPRECATED
class delete_active_camera(bpy.types.Operator):
    """Delete selected camera"""
    bl_idname = "srti.delete_active_camera"
    bl_label = "Delete Active Camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        camera_list = context.scene.srti_props.list_cameras
        active_cam = context.active_object

        bpy.ops.object.select_all(action='DESELECT')

        if camera_list:
            for index, obj in enumerate(camera_list):
                if obj.camera == active_cam: 
                    print (obj)
                    camera_list.remove(index)
                    active_cam.select = True
                    bpy.ops.object.delete()
                    break

        check_lamp_cam(context.scene)

        return{'FINISHED'}



# ui list item actions
class values_UIList(bpy.types.Operator):
    bl_idname = "srti.values_uilist"
    bl_label = "Values List"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.srti_props.selected_value_index

        try:
            item = scn.srti_props.list_values[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(scn.srti_props.list_values) - 1:
                item_next = scn.srti_props.list_values[idx+1].name
                scn.srti_props.list_values.move(idx, idx + 1)
                scn.srti_props.selected_value_index += 1
                info = 'Item %d selected' % (scn.srti_props.selected_value_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.srti_props.list_values[idx-1].name
                scn.srti_props.list_values.move(idx, idx-1)
                scn.srti_props.selected_value_index -= 1
                info = 'Item %d selected' % (scn.srti_props.selected_value_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item %s removed from list' % (scn.srti_props.list_values[scn.srti_props.selected_value_index].name)
                scn.srti_props.selected_value_index -= 1
                self.report({'INFO'}, info)
                scn.srti_props.list_values.remove(idx)

        if self.action == 'ADD':
            item = scn.srti_props.list_values.add()
            #item.id = len(scn.srti_props.list_values)
            item.name = "Value" # assign name of selected object scn.srti_props.list_values
            scn.srti_props.selected_value_index = (len(scn.srti_props.list_values)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}
    