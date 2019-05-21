import bpy
import math
import json


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class operator_anim_export(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "mcanim.export"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Minecraft Animation (.mcanim)"

    # ExportHelper mixin class uses this
    filename_ext = ".mcanim"

    filter_glob = StringProperty(
            default="*.mcanim",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    looping = BoolProperty(
            name="Looping",
            description="Should this animation loop?",
            default=True,
            )

    resetWhenDone = BoolProperty(
            name="Reset when done",
            description="Should this reset to starting position when done?",
            default=False,
            )

    id = StringProperty(
            name="ID",
            description="Unique numerical ID that Minecraft will refer to this animation by",
            default='0',
            )


    def execute(self, context):
        return export(context, self.id, self.looping, self.resetWhenDone, self.filepath)
    
# specific export function for menu
def export(context, id, looping, resetWhenDone, path):
    return write_mcanim(context, context.scene.objects.active, int(id), looping, resetWhenDone, path)

# write animation to disk
def write_mcanim(context, object, id, looping, resetWhenDone, path):
    
    frames = []
    
    # output all frames into frames array
    for i in range(context.scene.frame_start, context.scene.frame_end):
       frames.append(write_frame(context,object,i))
    
    # add additional metadata to file
    output = {
        "version": "0.2",
        "id": id,
        "looping": looping,
        "resetPos": resetWhenDone,
        "frames": frames
    }
    
    # create json string
    formatted = json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))
    
    # output to file
    file = open(path, "w")
    file.write(formatted)
    file.close
    
    print("Outputted to: "+path)
    return {'FINISHED'}

# returns a dictionary with a single frame of animation
def write_frame(context, object, frame):
    
    # make sure we're on the right frame
    context.scene.frame_set(frame)
    
    # get all the bones in the armature
    bones = object.pose.bones
    
    # get values from said bones
    body = convert_array(get_rotation(bones['body']), False)
    left_arm = convert_array(get_rotation(bones['left_arm']), False)
    right_arm = convert_array(get_rotation(bones['right_arm']), False)
    left_leg = convert_array(get_rotation(bones['left_leg']), False)
    right_leg = convert_array(get_rotation(bones['right_leg']), False)
    head = convert_array(get_rotation(bones['head']), True)
    location = [round(bones['root'].location[0], 2), round(bones['root'].location[1], 2),  round(bones['root'].location[2], 2)]
    rotation = round(math.degrees(get_rotation(bones['root'])[1]), 2) 
	
    # output found values to dictionary
    output = {
        "body": body,
        "left_arm": left_arm,
        "right_arm": right_arm,
        "left_leg": left_leg,
        "right_leg": right_leg,
        "head": head,
        "location": location,
        "rotation": rotation
    }
    
    return output
   
# returns the rotation in euler, no matter what it was initially in 
def get_rotation(input):
    if input.rotation_mode == 'QUATERNION':
        return input.rotation_quaternion.to_euler()
    else:
        return input.rotation_euler
 

# takes an array attained by armature.pose.bones[bone].rotation_euler, converts it to degrees, and does correct formulas.
def convert_array(array, isHead):
    
    if isHead:
        new_array = [array[0]*-1, array[1]*-1, array[2]]
    else:
        new_array = [array[2], array[1], array[0]*-1]  
        
    new_array[0] = round(math.degrees(new_array[0]), 2)
    new_array[1] = round(math.degrees(new_array[1]), 2)
    new_array[2] = round(math.degrees(new_array[2]), 2)
    
    return new_array

# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(operator_anim_export.bl_idname, text="Minecraft Animation (.mcanim)")


def register():
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
