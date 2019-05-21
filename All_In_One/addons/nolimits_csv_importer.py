bl_info = {
    "name": "NoLimits CSV Importer",
    "author": "Ercan Akyürek",
    "version": (0,1,1),
    "blender": (2, 61, 0),
    "location": "Tools > NoLimits CSV Importer",
    "description": "Generate a spline from NoLimit CSV file",
    "wiki_url": "https://github.com/geforcefan/BlenderNoLimitsCSVImporter",
    "category": "Import CSV"
}

import bpy
import csv
import mathutils
import math
import struct
import os

class NoLimitsImporter():
    csvfilepath = ""
    
    vertices = []
    
    def __init__(self, filepath):
        self.csvfilepath = filepath
        self.parse()
    
    def generate(self):
        name = os.path.splitext(os.path.basename(self.csvfilepath))[0]
        
        aCurve = bpy.data.curves.new(name,'CURVE')
        aCurve.twist_mode = 'Z_UP'
        
        aObj = bpy.data.objects.new(name + " Object",aCurve) 
        aObj.location = (0,0,0) 
    
        bpy.context.scene.objects.link(aObj)
        
        aCurve.dimensions = '3D';
        spline = aCurve.splines.new('NURBS')
        
        spline.tilt_interpolation = 'BSPLINE'
        spline.points.add(len(self.vertices)-1) 
        
        i = 0        
        lastRoll = 0
        rollToAdd = 0
        
        for vertex in self.vertices:
            newPoint = spline.points[i]  
            x, z, y = vertex['pos']
            
            newPoint.co = (x * -1, y, z, 1)
            
            actualRoll = math.atan2(-vertex['left'][1], vertex['up'][1])
            diff = lastRoll - actualRoll
            lastRoll = actualRoll
            
            if(math.fabs(diff) >= 358 * math.pi / 180):
                rollToAdd = rollToAdd + diff
            
            roll = rollToAdd + actualRoll
            
            newPoint.tilt = -roll
            
            i = i + 1
        
        return True
        
    def parse(self):
        self.vertices = []
        
        with open(self.csvfilepath, 'r') as csvfile:
            treader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for row in treader:
                try:
                    self.vertices.append({
                        'pos': mathutils.Vector((float(row[1]), float(row[2]) , float(row[3]))), 
                        'front': mathutils.Vector((float(row[4]), float(row[5]) , float(row[6]) )), 
                        'left': mathutils.Vector((float(row[7]) , float(row[8]) , float(row[9]))), 
                        'up': mathutils.Vector((float(row[10]), float(row[11]) , float(row[12])))
                    })
                except ValueError:
                    continue
            
        return True

class FileSelectCSVOperator(bpy.types.Operator):
    bl_idname = "object.file_select_csv"
    bl_label = "Select file..."
 
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
 
    def execute(self, context):
        parser = NoLimitsImporter(self.filepath)
        parser.generate()
        return {'FINISHED'}
 
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class NoLimitsImporterPanel(bpy.types.Panel):
    bl_label = "NoLimits CSV Importer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("object.file_select_csv")
        
###------------------------------------------------------------
# Register

def register():
    bpy.utils.register_class(FileSelectCSVOperator)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_class(FileSelectCSVOperator)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
