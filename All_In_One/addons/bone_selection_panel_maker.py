bl_info = {
    "name"     : "Bone Selection Facilitator",
    "category" : "Animation",
    "author"   : "Tamir Lousky",
    "version"  : "1.0"
}

import bpy, time

prefix   = 'bone_selector_'             # Textfile prefix
now_time = time.localtime( time.time()) # Current time
filename = prefix + str(now_time)       # Concatenate prefix and time to create unique name

# Create a new text file in the text editor
bpy.data.texts.new(name=filename)
textfile = bpy.data.texts[filename]

textfile_template = """

import bpy

class bone_selection_panel(bpy.types.Panel):
    bl_idname      = "boneSelectionPanel"
    bl_label       = "Bone Selection Panel"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = 'posemode'

    def draw( self, context) :
        layout = self.layout
        layout.operator("pose.bone_selector_op")

class bone_selector( bpy.types.Operator ):
   bl_idname      = "pose.bone_selector_op"
   bl_label       = "Select predefined bones"
   bl_description = "Selects a group of bones for your convience"
   bl_options     = {'REGISTER', 'UNDO' }  # Enable undo

   @classmethod
   def poll(cls, context):
      # Find out how to check if the armature is in pose mode
      # return context.active_object.mode == 'POSE_MODE'
      return True

   def execute( self, context):
"""
textfile.write(start_string) # Write constant initial string to text file

# List all existing bone names
bone_names     = [ name for bone.name in bpy.context.object.data.bones ]
selected_bones = [ name for bone.name in bpy.context.object.data.bones if bone.select == True ]

for name in bone_names:
   # TODO:
   # Check if you can deslect all bones via bpy operators
   # bpy.ops.armature.select_all(action='DESELECT')

   textfile.write("\t\t") # Double indent   

   if name in selected_bones:
      textfile.write("bpy.context.object.data.bones['%s'].select = True" % bone.name  + "\n")
   else:
      textfile.write("bpy.context.object.data.bones['%s'].select = False" % bone.name  + "\n")
