###OPERATORS###
import bpy
import numpy
import itertools
import os
from ..srtifunc import *
from ..srtiproperties import file_lines as file_lines
####ANIMATION########
class animate_all(bpy.types.Operator):
    """Animate all lights, cameras and parameter"""
    bl_idname = "srti.animate_all"
    bl_label = "Animate all"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Animate all features"""
        print("- Animating features ---")
        #index
        index_light = 0
        index_cam = 0
        index_prop = 0

        #global var
        curr_scene = context.scene
        lamp_list = curr_scene.srti_props.list_lights
        camera_list = curr_scene.srti_props.list_cameras
        value_list = curr_scene.srti_props.list_values
        object = curr_scene.srti_props.main_object
        file_name = curr_scene.srti_props.save_name
        global file_lines

        #generated lists
        all_values = []
        material_list = []
        val_names = {}

        #set renderer to cycle (could be written in a setting file)
        curr_scene.render.engine = 'CYCLES'

        #Check if objects have been deleted from scene
        #check lamps
        print("-- Check for lamps")
        if lamp_list:
            for index, obj in sorted(enumerate(lamp_list), reverse=True):
                print("--- Lamp %i: %s"%(index,obj.light.name))
                if curr_scene not in obj.light.users_scene:
                    print("---- Deleted")
                    self.report({'WARNING'}, "light %s has been deleted." %obj.light.name)
                    lamp_list.remove(index)

        print("-- Check for cameras")
        #check cameras
        if camera_list:
            for index, obj in sorted(enumerate(camera_list), reverse=True):
                print("--- Camera %i: %s"%(index,obj.camera.name))
                if curr_scene not in obj.camera.users_scene:
                    print("---- Deleted")
                    self.report({'WARNING'}, "Camera %s has been deleted." %obj.camera.name)
                    camera_list.remove(index)

        #if no camera and no lamp: delete main
        check_lamp_cam(curr_scene)


        #generated value
        tot_light = max(len(lamp_list),1) #at least we want to iterate one frame over the camera when there are no lights
        tot_cam = len(camera_list)
            
        #Abort if no camera in scene
        if tot_cam < 1:
            self.report({'ERROR'}, "There are no cameras in the scene.")
            return{'CANCELLED'}

        #Clear file lines
        file_lines.clear()

        #If there is no object selected we only iterate over cameras and lamps
        if not object:
            self.report({'WARNING'}, "No object selected for values.")
            tot_comb = 1
            file_lines.append("image,x_lamp,y_lamp,z_lamp")
        else:
            #add or update value node to all materials enabling nodes fore each
            #global material_list and delete all animation data
            file_lines.append("image,x_lamp,y_lamp,z_lamp,"+",".join(value.name for value in value_list))
            for material_slot in object.material_slots:
                if material_slot.material:
                    
                    material_slot.material.use_nodes = True
                    material_slot.material.node_tree.animation_data_clear() #delete animation
                    node_list=[]
                    index = 0

                    for value in value_list:
                        #for every value chek if node exist otherwise create a new one
                        node_name = "srti_" + value.name
                        if node_name in material_slot.material.node_tree.nodes:
                            node = material_slot.material.node_tree.nodes[node_name]
                        else:
                            node = material_slot.material.node_tree.nodes.new("ShaderNodeValue")
                            node.name = node_name
                            node.label = value.name
                            node.location = (0, -100*index)
                        node_list.append(node)
                        index += 1
                    material_list.append(node_list)

            #Creation of values array
            values = curr_scene.srti_props.list_values
            #global all_values
            index_name = 0
            for val in values:
                all_values.append(numpy.linspace(val.min,val.max,val.steps))
                val_names.update({val.name:index_name})
                index_name += 1
            print (all_values)
            tot_comb = numpy.prod(list(row.steps for row in values))

        print("--- output list: ")
        print("---- materials: ")
        print(material_list)
        print("---- values: ")
        print(all_values)
        print("---- file lines: ")
        print(file_lines)

        #Set animation boundaries
        tot_frames = tot_cam * tot_light * tot_comb
        curr_scene.frame_start = 1
        curr_scene.frame_end = tot_frames
        #val_combination = list(itertools.product(*all_values))

        #Delete animations for cameras and lamps
        for cam in camera_list:
            cam.camera.animation_data_clear()

        for lamp in lamp_list:
            lamp.light.animation_data_clear()

        #delete markers
        curr_scene.timeline_markers.clear()
        
        for curr_val in itertools.product(*all_values) if object else [0]: #Loop for every value combination (if no object we only do once)
            for material in material_list if object else []: #loop over every object's materials if there is an object              
                for val_node in material: #loop for every value node
                    #TODO add a marker name for parameters
                    curr_frame = (index_prop * tot_cam * tot_light)
                    val_node.outputs[0].keyframe_insert(data_path = "default_value", frame = curr_frame )
                    val_node.outputs[0].default_value = curr_val[val_names[val_node.name[5:]]]
                    val_node.outputs[0].keyframe_insert(data_path = "default_value", frame = curr_frame + 1)
            for cam in camera_list: #loop every camera
                curr_frame = index_prop*tot_cam*tot_light + index_cam * tot_light + 1
                mark = curr_scene.timeline_markers.new(cam.camera.name, curr_frame) # create a marker
                mark.camera = cam.camera

                if not lamp_list: #create the list when there aren't lights
                    string = "{0}_{1},,,".format(file_name, format_index(curr_frame,tot_frames))
                    if curr_val:
                        string +=","+",".join(str(x) for x in curr_val)
                    file_lines.append(string)
                    print(string)
                    
                for lamp in lamp_list: #loop every lamp
                    lamp = lamp.light
                    #animate lamps
                    curr_frame = (index_prop * tot_cam * tot_light) + (index_cam * tot_light) + index_light + 1
                    #hide lamp on theprevious and next frame
                    lamp.hide_render = True
                    lamp.hide = True
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame - 1)
                    lamp.keyframe_insert(data_path = 'hide', frame = curr_frame - 1)
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame + 1)
                    lamp.keyframe_insert(data_path = 'hide', frame = curr_frame + 1)
                    #rendo visibile la lampada solo nel suo frame
                    lamp.hide_render = False
                    lamp.hide = False
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame)
                    lamp.keyframe_insert(data_path = 'hide', frame = curr_frame)

                    #add a line for the files with all the details
                    #filename will be added at export time in create_export_file
                    string = "-%s,%f,%f,%f" % (format_index(curr_frame, tot_frames), lamp.location[0], lamp.location[1], lamp.location[2])
                    if curr_val:
                        string += ","+ ",".join(str(x) for x in curr_val)
                    file_lines.append(string)
                    print(string)
                    index_light += 1

                index_cam += 1
                index_light = 0
            
            index_cam = 0
            index_prop += 1

        #self.report({'INFO'}, "Animation complete, total frames = %i" % tot_frames)
            
        return{'FINISHED'}

#####RENDERING######
class render_images(bpy.types.Operator):
    """Render all images"""
    bl_idname = "srti.render_images"
    bl_label = "Set Render"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        curr_scene = context.scene
        
        save_dir = get_export_folder_path(context)
        file_name = get_export_name(context)
        
        #error if file path not set
        if save_dir == '':
            self.report({'ERROR'}, "File path not set!")
            return{'CANCELLED'}
        else: 
            #calculate max numbers of digit for file name
            max_digit = len(str(calculate_tot_frame(context)))
            
            #set render path for local rendering
            curr_scene.render.filepath = "{0}/EXR/{1}-{2}".format(save_dir,file_name,"#"*max_digit)

            #set render settings
            set_render_exr(curr_scene)
            
            self.report({'INFO'}, "Render output set.")

            return{'FINISHED'}

class create_export_file(bpy.types.Operator):
    """Create a .csv file with all the images name and parameters"""
    bl_idname = "srti.create_file"
    bl_label = "Create file"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        #if we have no lines we 
        return len(file_lines) != 0
    
    def execute(self, context):
        curr_scene = context.scene
        
        save_dir = get_export_folder_path(context)
        file_name = get_export_name(context)
        
        #error if file path not set
        if save_dir == '':
            self.report({'ERROR'}, "File path not set!")
            return{'CANCELLED'}
        else:       
            #create the file
            file_path = bpy.path.abspath(save_dir+'/'+file_name+".csv")
            file = open(file_path, "w")
            
            #first we print the firt line with headers
            file.write(file_lines[0])
            file.write('\n')
            
            #then we write all the others line with added images names (image index already added in animate_all function)
            for line in file_lines[1:]:
                file.write(file_name+line)
                file.write('\n')
            file.close()
            
            self.report({'INFO'}, "File %s successfully written."%file_path)

            return{'FINISHED'}
