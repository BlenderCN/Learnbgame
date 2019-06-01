
import bpy
import math
import struct
import os


### The new operator ###
class Operator(bpy.types.Operator):
    #everything is scaled down by this factor
    scale = bpy.props.FloatProperty(name="Scale", description="Movements are scaled by this factor", default=100)
    bl_idname = "export_scene.ja_roff"
    bl_label = "Export JA ROFF (.rof)"
    
    #gets set by the file select window - IBM (Internal Blender Magic) or whatever.
    filepath = bpy.props.StringProperty(name="File Path", description="File path used for the ROFF file", maxlen= 1024, default="")
    
    def execute(self, context):
        self.ExportStart(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        windowMan = context.window_manager
        #sets self.properties.filename and runs self.execute()
        windowMan.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def ExportStart(self, context):
        print("\nROFF exporter by Mr. Wonko\n")
        filename = bpy.path.ensure_ext( self.filepath, ".rof" )
        
        if os.path.exists(filename):
            #TODO: Overwrite yes/no
            pass
        
        objlist = bpy.context.selected_objects
        if len(objlist) != 1:
            self.report({"ERROR"}, "Please select exactly one object!")
            return
        obj = objlist[0]
            
        scn = context.scene
        numframes = scn.frame_end - scn.frame_start
        if numframes == 0:
            self.report({"ERROR"}, "Since relative movement is saved, I need more than 1 frame!")
            return
        
        print("Exporting movement of "+obj.name)
        
        try:
            file = open(filename, "wb")
            #ident, version, frames, frame duration in ms, unknown
            file.write(struct.pack("4s4i", b"ROFF", 2, numframes, round(1000/context.scene.render.fps), 0))
            
            prevframe = scn.frame_current
            
            scn.frame_set(scn.frame_start)
            #init these
            lastpos = obj.matrix_world.translation.copy()
            lastrot = obj.matrix_world.to_euler()
            
            #first frame has no change (roff is relative), hence it is skipped
            for curFrame in range(scn.frame_start + 1, scn.frame_end + 1):
                scn.frame_set(curFrame)
                #print("exporting frame {}".format(scn.frame_current))
                
                pos = obj.matrix_world.translation
                rot = obj.matrix_world.to_euler()
                
                #rotation: y z x
                file.write(struct.pack("6f2i", (pos[0] - lastpos[0])*self.scale, (pos[1] - lastpos[1])*self.scale, (pos[2] - lastpos[2])*self.scale, math.degrees(rot[1] - lastrot[1]), math.degrees(rot[2] - lastrot[2]), math.degrees(rot[0] - lastrot[0]), -1, 0))
                
                lastpos = pos.copy()
                lastrot = rot.copy()
                
            scn.frame_current = prevframe
            
            file.close()
        except IOError:
            self.report({"ERROR"}, "Couldn't create file!")
            return

def menu_func(self, context):
    self.layout.operator(Operator.bl_idname, text="JA ROFF (.rof)")