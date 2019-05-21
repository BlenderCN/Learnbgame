import bpy
import struct
from bpy.types import Panel
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty,  FloatProperty, IntProperty
from bpy.types import Operator
import os, sys

"""
0.4
v4motion add on 
fixed header: bytesize from 8 to 4

0.5
pdated header : T or RT  (only Translation (absolute) or Rotation and Translation (relative) per bone
added option : nla select 
added option : rotation + translation for bones
added progress coutning in console

0.6
add bones names and count to offset bytes in vvvv

0.7
add matrix data option

0.8 
fix selected bones (constantly appending names)

changed matrix order:
a00 a01 a02 a03            a00 a02 a01 a03
a10 a11 a12 a13     ---->  a20 a22 a21 a23
a20 a21 a22 a23            a10 a12 a11 a13
a30 a31 a32 a33            a30 a32 a31 a33

TODO: add bone to clear animation data before importing
"""
bl_info = {
    "name": "v4Motion",
    "author": "c nisidis",
    "version": (0, 0, 8),
    "blender": (2, 78, 0),
    "location": "View3D",
    "description": "Blender Armature to Moving Points exporter",
	"warning": "Be aware of long duration exports",
    "wiki_url": "",
	"tracker_url": "",
    "category": "Import-Export"
}

os.system("cls")



def WriteData(context, filepath, settings, v4mData, selected_bones):
    
    type = 0
    sel_bones = ','.join(selected_bones)
    sel_bones_bytes = sel_bones.encode('utf-8')
    sel_bones_bytes_len = (len(sel_bones_bytes)).to_bytes(4, byteorder = 'little')
    if context.scene.bool_type == True and context.scene.bool_matrix==False:
        type = 1
        safe_frame = 0
    elif context.scene.bool_matrix == True:
        type = 2
        safe_frame = 0
    else :
        safe_frame = context.scene.float_input
    
    FileType = type.to_bytes(4, byteorder='little')
    FPS = context.scene.render.fps.to_bytes(4, byteorder='little')
    s_frame = context.scene.frame_start.to_bytes(4, byteorder = 'little')
    e_frame = context.scene.frame_end.to_bytes(4, byteorder = 'little')
    safe = safe_frame.to_bytes(4, byteorder = 'little')    
    
    if type >= 1 :
        header =  FileType + FPS + s_frame + e_frame +safe + sel_bones_bytes_len + sel_bones_bytes
    else :
        header = FileType + FPS + s_frame + e_frame +safe
    
    if context.scene.add_header:
        content = header + v4mData
    else :
        content = v4mData
    #print(len(sel_bones_bytes))
    print(header) 
    
    f = open(filepath, "wb+")
    f.truncate(0)
    f.write(content)

    f.close()
    print("Done")
    return {'FINISHED'}

class EXPORT_OT_ExporterCustomBVH(Operator, ExportHelper):
    bl_idname = "v4motion.bvh"
    bl_label = "Export Custom BVH File"
    
    filename_ext = ".bvh"
    
    def execute(self, context):
        
        s_frame = context.scene.frame_start
        e_frame = context.scene.frame_end
        safe = context.scene.float_input
        
        s_frame = s_frame - safe
        e_frame = e_frame + safe
        
        path=self.properties.filepath
        self.report({'INFO'}, path)
        bpy.ops.export_anim.bvh('EXEC_REGION_WIN', filepath=path, frame_start = s_frame, frame_end = e_frame)
        return {'FINISHED'}


    
class EXPORT_OT_ExporterV4Motion(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "v4motion.export"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export V4Motion"
    
    # ExportHelper mixin class uses this
    filename_ext = ".v4m"

    filter_glob = StringProperty(
            default="*.v4m",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    use_setting = BoolProperty(
            name="AllBones (WIP)",
            description="Export All Bones",
            default=True,
            )

    type = EnumProperty(
            name="WIP",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )
    
    def execute(self, context):
        #return write_some_data(context, self.filepath, self.use_setting)
        print("execute..")
        """
        copy + paste code from init file
        """
        #def Parse(selected):
        selection = bpy.context.selected_objects
        
        for selected in selection:
            if selected is None:
                return {'CANCELLED'}
            elif selected.type == 'ARMATURE':
                continue
            else:
                print("selection is not an armature")
                return {'CANCELLED'}
        
        selected_bones=[]
        bones = selected.pose.bones
        for bone in bones:
            selected_bones.append(bone.name)
            
        ad = selected.animation_data
        nla_tracks = ad.nla_tracks
        stp = None
        
        for track in ad.nla_tracks:
            if track.active == True:
                for strip in track.strips:
                    if strip.select == True:
                        stp = strip
        
        if (bones is None):
            print("There is no any pose in this armature")
            #add return function for OT
            return {'CANCELLED'}
        
        if stp is not None:
            
            print('strip found')
            start_frame = int(stp.frame_start)
            context.scene.frame_start  =start_frame
            
            end_frame = int(stp.frame_end)
            context.scene.frame_end = end_frame
            
            safeFrames = 0
                
        else:
            start_frame = context.scene.frame_start
            end_frame = context.scene.frame_end
            safeFrames = context.scene.float_input 
        
        
        
        bones_names =[]
        positions =[]
        duration_in_frames = (end_frame+safeFrames) - (start_frame-safeFrames)
        bones_as_bytes = b''    
        print("Wait...")
        type = context.scene.bool_type
        is_matrix = context.scene.bool_matrix
        
        #TODO:
        #subtract float_input from start_frame and add it to end_frame 
        for frame in range(start_frame-safeFrames, end_frame+safeFrames):
                
            bpy.context.scene.frame_set(frame)    
            #selected_bones.append(bone.name)
            
            #if bone.name in bones_names or len(bones_names)==0 or bone.bone.select == True:
            for bone in bones:                    
                    

                #SET FRAME
                
                
                #DEBUG
                vec = bone.head
                
                rot = bone.rotation_euler
                loc = bone.location
                
                
                #convert the array of floats to bytes
                if type == True and is_matrix==False:
                    pos = [vec.x, vec.y, vec.z, loc.x, loc.y, loc.z, rot.x, rot.y, rot.z]
                    bone_position = struct.pack('%sf' % len(pos), *pos)
                elif type == True and is_matrix==True:
                    matrix = bone.matrix 
                    pos = [vec.x, vec.y, vec.z, matrix[0][0], matrix[0][2], matrix[0][1], matrix[0][3],
                                                
                                                matrix[2][0], matrix[2][2], matrix[2][1], matrix[2][3],
                                                matrix[1][0], matrix[1][2], matrix[1][1], matrix[1][3],
                                                
                                                matrix[3][0], matrix[3][2], matrix[3][1], matrix[3][3], ]
                    bone_position = struct.pack('%sf' % len(pos), *pos)
                else:
                    pos = [vec.x, vec.y, vec.z]
                    bone_position = struct.pack('%sf' % len(pos), *pos)
            
                bones_as_bytes += bone_position
            progress = (frame / duration_in_frames)*100
            sys.stdout.write("Download progress: %d%%   \r" % (progress) )
            sys.stdout.flush()
                    

        
        WriteData(context, self.filepath, self.use_setting, bones_as_bytes, selected_bones)
        return {'FINISHED'}

class V4Motion(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'vvvv Motion'
    bl_category = 'vvvv'
    
    safeFrames = bpy.props.FloatProperty(name="safe")
    
    
    #Add UI elements
    def draw(self, context):
        
        
        
        
        scene = context.scene

        layout = self.layout
        #layout.operator("v4motion.export", text="Export v4 motion data")
        
         # Create a simple row.
        layout.label(text="Frames:")

        row = layout.row()
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")
        
        row = layout.row()
        row.prop(scene, "float_input")
        
        # Big render button
        #layout.label(text="Export")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("v4motion.export", text="Export v4 motion data")
        
        row = layout.row()
        row.scale_y = 3.0
        row.operator("v4motion.bvh", text="Export BVH")
        
        layout.label(text="Options")        
        row = layout.row()
        row.prop(scene, "add_header")
        row = layout.row()
        row.prop(scene, "bool_nla")
        
        
        layout.label(text="Extended Type")        
        row = layout.row()
        row.prop(scene, "bool_type") #type = 1
        row = layout.row()
        row.prop(scene, "bool_matrix") #type = 2
        

    


    
#For Dynamic Menu
#def menu_func_export(self, context):
#    self.layout.operator(ExporterV4Motion.bl_idname, text="V4 Motion Export Data")

#Register
def register():

    bpy.utils.register_class(V4Motion)
    bpy.utils.register_class(EXPORT_OT_ExporterV4Motion)
    bpy.utils.register_class(EXPORT_OT_ExporterCustomBVH)
    bpy.types.Scene.float_input = bpy.props.IntProperty(
        name = "SafeFrames (start/end)",
        description = "Set float",
        default = 400,
        min = 0,
        max = 999999
    )
    bpy.types.Scene.add_header = bpy.props.BoolProperty(
        name = "Header",
        default = True 

    )
    bpy.types.Scene.bool_type = bpy.props.BoolProperty(
        name = "T + R (relative)",
        default = True 

    )
    bpy.types.Scene.bool_nla = bpy.props.BoolProperty(
        name = "OnlyNLA",
        default = True 

    )
    bpy.types.Scene.bool_matrix = bpy.props.BoolProperty(
        name = "Matrix",
        default = True 

    )
    

#Unregister
def unregister():

    bpy.utils.unregister_class(V4Motion)
    bpy.utils.unregister_class(EXPORT_OT_ExporterV4Motion)
    bpy.utils.unregister_class(EXPORT_OT_ExporterCustomBVH)
    del bpy.types.Scene.float_input
    del bpy.types.Scene.add_header  
    del bpy.types.Scene.bool_type
    del bpy.types.Scene.bool_nla
    del bpy.types.Scene.bool_matrix

# Need to run script from Text Editor
if __name__ == "__main__":
    register()