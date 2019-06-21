'''
Created on Jun 30, 2016

@author: ashok
'''
import bpy;
from bpy.props import *;
from chenhan_pp.ChenhanOperator import ChenhanGeodesicsOperator;
from chenhan_pp.IsoContours import IsoContours, SpecifiedIsoContours;

bl_info = {
    "name": "Chenhan Geodesics",
    "version": (1, 0),
    "blender": (2, 7, 6),
    "location": "View3D > Object > Chenhan Geodesics",
    "description": "Chenhan geodesics demonstration using Blender",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp;
    print("Reloaded multifiles");
else:
    print("Imported multifiles")

def get_scene_meshes(self, context):
    templatenames = ["_marker","_joint","_bone","_lines","_cloud", "Template", "Marker"];
    meshes = [(item.name, item.name, item.name) for item in bpy.data.objects if item.type == "MESH" and not any(word in item.name for word in templatenames)];
    meshes = [('None', 'None', 'None')] + meshes; 
    return meshes;


def updateSpecificGRatio(self, context):
    context.scene.isolinesupdated = False;

class IndexItem(bpy.types.PropertyGroup):
    index = bpy.props.IntProperty(name="Index Item", default=-1);

class Location3D(bpy.types.PropertyGroup):
    x = bpy.props.FloatProperty(name="X", description="X coordinate", default=0.0);
    y = bpy.props.FloatProperty(name="Y", description="Y coordinate", default=0.0);
    z = bpy.props.FloatProperty(name="Z", description="Z coordinate", default=0.0);

bpy.utils.register_class(IndexItem);
bpy.utils.register_class(Location3D);

class ChenhanGeodesicsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_chenhangeodesicpanel"
    bl_label = "Chenhan Geodesic";
    bl_space_type = "VIEW_3D";
    bl_region_type = "TOOLS";
    bl_category = "GEODESICS";
    
    def draw(self, context):        
        #The button to load the humma file and do all preprocessing        
        if(context.active_object):
            layout = self.layout;
            
            row = self.layout.row(align=True);
            row.prop(context.object,"reflectormesh",text='Reflector Mesh');
            
            row = layout.row(align=True);
            row.prop(context.active_object, "show_wire", "Wireframe");
                        
            row = layout.row(align=True);
            row.prop(context.active_object, "show_all_edges", "Show All Edges");
            
            row = layout.row(align=True);
            row.prop(context.scene, "path_color", "Path Color");            
            
            row = layout.row(align=True);
            row.prop(context.scene, "temp_path_color", "Temp path color");
            
            row = layout.row(align=True);
            row.operator(ChenhanGeodesicsOperator.bl_idname, text="Geodesics");
            
            row = layout.row(align=True);
            row.prop(context.active_object, "isolines_count", "IsoLines Count");
            
            row = layout.row(align=True);
            row.operator(IsoContours.bl_idname, text="IsoContours");
            
            row = layout.row(align=True);
            row.prop(context.active_object, "specific_distance_ratio", "Show at Distance");
            
            row = layout.row(align=True);
            row.operator(SpecifiedIsoContours.bl_idname, text="Specific Isocontours");

bpy.types.Object.iso_mesh_count = bpy.props.IntProperty(name="Isomesh count", description="Total Isomeshes", default=0);
bpy.types.Object.isolines_count = bpy.props.IntProperty(name="Isolines count", description="Total IsoLines", default=10, min=1, max=100, update=updateSpecificGRatio);
bpy.types.Object.specific_distance_ratio = bpy.props.FloatProperty(name="Specific Distance Ratio", description="Show isolines at distance %", default=0.01, step=0.01, update=updateSpecificGRatio);

bpy.types.Object.reflectormesh = bpy.props.EnumProperty(name="Reflecting mesh",description="Mesh for reflecting the path",items = get_scene_meshes);
bpy.types.Scene.isolinesupdated = bpy.props.BoolProperty(name="Isolines Updated",description="Isolines Updated flag",default=False);


bpy.types.Object.isopoints = bpy.props.CollectionProperty(type=Location3D);
bpy.types.Object.isoindices = bpy.props.CollectionProperty(type=IndexItem);
bpy.types.Object.contourindices = bpy.props.CollectionProperty(type=IndexItem);


bpy.types.Scene.path_color = bpy.props.FloatVectorProperty(
    name = "Geodesic Path Color", 
    subtype='COLOR', 
    default=[0.0,0.0,1.0], 
    description = "Color of the geodesic path from normal mesh");

bpy.types.Scene.temp_path_color = bpy.props.FloatVectorProperty(
    name = "Temp Geodesic Path Color", 
    subtype='COLOR', 
    default=[0.5,1.0,1.0], 
    description = "TEMP Color of the geodesic path from normal mesh");
    
    
def register():
    bpy.utils.register_module(__name__);
 
def unregister():    
    bpy.utils.unregister_module(__name__);
 
if __name__ == "__main__":
    register()
