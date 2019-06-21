import bpy
import os


def rounder (vector):
    return(round(vector[0],2),round(vector[1],2),round(vector[2],2))

# OPERADOR DUMMY
def reportMeshes(self, context):
    with open("%s" % (bpy.data.filepath.replace(".blend",".txt")), mode="w") as file:
        for ob in bpy.context.selected_objects:
            warning = 0
            
            status = {"location": True, "rotation": True, "scale": True, "fgons": True}
            
            if ob.type == "MESH":
                file.write("%s\n" % (ob.name))
                
                if rounder(ob.location[:]) != (0,0,0):
                    file.write("LOCATION WARNING <----------  \n")
                    warning += 1
                file.write("location: %s \n" % (str(rounder(ob.location[:]))))
                
                if rounder(ob.rotation_euler[:]) != (0,0,0):
                    file.write("ROTATION WARNING <----------  \n")  
                    warning += 1            
                file.write("rotation: %s \n" % (str(rounder(ob.rotation_euler[:]))))
                
                if rounder(ob.scale[:]) != (1,1,1):
                    file.write("SCALE WARNING <----------  \n")   
                    warning += 1  
                    
               
                file.write("scale: %s \n" % (str(rounder(ob.scale[:]))))            
                file.write("vertices: %s \n" % (str(len(ob.data.vertices))))
                file.write("edges: %s \n" % (str(len(ob.data.edges))))
                file.write("faces: %s \n" % (str(len(ob.data.polygons))))
                
                tris = 0
                quads = 0
                fgons = 0
                for poly in ob.data.polygons:
                    if len(poly.vertices) == 3:
                        tris += 1
                    if len(poly.vertices) == 4:
                        quads += 1
                    if len(poly.vertices) > 4:
                        fgons += 1            
                
                        
                file.write("tris: %s \n" % (tris))    
                file.write("quads: %s \n" % (quads)) 
                if fgons > 0:
                    file.write("FGONS WARNING <----------  \n")  
                    warning += 1 
                file.write("fgons: %s \n" % (fgons))  
                
                
                if len(bpy.context.object.data.uv_layers) == 0:
                    file.write("UVS WARNING <---------- \n")                 
                    warning += 1 
                file.write("uvs: %s \n" % (len(bpy.context.object.data.uv_layers)))      
                
                 
                try:
                    file.write("shapes: %s \n" % (len(ob.data.shape_keys.key_blocks)-1))
                except:  
                    file.write("shapes: %s \n" % ("0"))  
                
                if warning == 0:
                    file.write("OBJECT OK :)")
                else:
                    file.write("OBJECT WARNINGS: %s" % (warning))     
                     
                file.write("\n")
                file.write("\n")
                 


class CelesteReportMeshes (bpy.types.Operator):
    """Create a new Mesh Object"""
    bl_idname = "file.celeste_report_meshes"
    bl_label = "Celeste Report Meshes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reportMeshes(self, context)
        return {'FINISHED'}

    
## ---------------------



