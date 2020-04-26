import bpy
import bmesh

from . import path_mesh_loader
from . import path_mesh_exporter

"""
GTA SA: sa_nodes_loader_operator
GTA VC: export_pedpathmesh
GTA IV: iv_nodes_loader_operator
 
"""

#set up blender grid to match path grid
class setup_scene_for_paths_op(bpy.types.Operator):
    bl_idname = "setup.setup_scene_for_paths_op"
    bl_label = "Setup grid to match path nodes"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].clip_end = 100000
                area.spaces[0].grid_lines = 8
                area.spaces[0].grid_scale = 750
                area.spaces[0].grid_subdivisions = 1
        return {'FINISHED'}

class test_nodes_loader_operator(bpy.types.Operator):
    bl_idname = "loader.debug_loader"
    bl_label = "Load test files directly"

    path = bpy.props.StringProperty(name="sa_nodes_path")

    def execute(self, context):
        path_mesh_loader.loadSAPathsAsMesh(self.path)
        return {'FINISHED'}

class sa_nodes_loader_operator(bpy.types.Operator):
    bl_idname = "loader.sa_nodes_loader_operator"
    bl_label = "Load GTA SA Nodes file format"

    directory = bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        path_mesh_loader.loadSAPathsAsMesh(self.directory)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class export_boatpathmesh(bpy.types.Operator):
    """Test exporter which just writes hello world"""
    bl_idname = "loader.export_boatpathmesh"
    bl_label = "Export Selected Path as Ped Mesh"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')
                
    def execute(self, context):
        path_mesh_exporter.exportVehiclePaths(self.filepath, context.selected_objects[0], "car")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
class export_carpathmesh(bpy.types.Operator):
    """Test exporter which just writes hello world"""
    bl_idname = "loader.export_carpathmesh"
    bl_label = "Export Selected Path as Car IPL"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')
                
    def execute(self, context):
        path_mesh_exporter.exportVehiclePaths(self.filepath, context.selected_objects[0], False)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
class export_boatpathmesh(bpy.types.Operator):
    """Test exporter which just writes hello world"""
    bl_idname = "loader.export_boatpathmesh"
    bl_label = "Export Selected Path as Boat IPL"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')
                
    def execute(self, context):
        path_mesh_exporter.exportVehiclePaths(self.filepath, context.selected_objects[0], True)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
class export_pedpathmesh(bpy.types.Operator):
    """Test exporter which just writes hello world"""
    bl_idname = "loader.export_pedpathmesh"
    bl_label = "Export Selected Path as Ped IPL"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')
                
    def execute(self, context):
        #try:
        path_mesh_exporter.exportPedPaths(self.filepath, context.selected_objects[0])
        #except:
        #self.report({'ERROR'}, "Invalid Path Mesh Selected");
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class PathsUltimatumPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Path Ultimatum By Swoorup"
    bl_idname = "OBJECT_PT_PathsUltimatum"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Different sizes in a row
        row = layout.row()
        row.prop(context.scene, 'debug_test_pathbox')
        row = layout.row(align=True)
        props = row.operator("loader.debug_loader")
        props.path = context.scene.debug_test_pathbox

        layout.label(text="Load SA Nodes:")
        row = layout.row(align=True)
        props = row.operator("loader.sa_nodes_loader_operator")

        layout.label(text="Export IPL Paths")
        col = layout.column(align=True)
        col.operator(export_pedpathmesh.bl_idname)
        col.operator(export_boatpathmesh.bl_idname)
        col.operator(export_carpathmesh.bl_idname)

         # Big button
        layout.label(text="Fix ViewPort Settings:")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("setup.setup_scene_for_paths_op")

        row = layout.row()
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        # Create an row where the buttons are aligned to each other.
        layout.label(text=" Aligned Row:")

        row = layout.row(align=True)
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        # Create two columns, by using a split layout.
        split = layout.split()

        # First column
        col = split.column()
        col.label(text="Column One:")
        col.prop(scene, "frame_end")
        col.prop(scene, "frame_start")
        
        # Second column, aligned
        col = split.column(align=True)
        col.label(text="Column Two:")
        col.prop(scene, "frame_start")
        col.prop(scene, "frame_end")

def setupProps():
    bpy.types.Scene.debug_test_pathbox = bpy.props.StringProperty \
    (
    name = "Root Path",
    default = r'E:\scripts\Vanilla\Compiled\SA',
    description = "Define the root path containing all nodes*.dat from GTA San Andreas",
    subtype = 'DIR_PATH'
    )
    
def removeProps():
    del bpy.types.Scene.debug_test_pathbox

    
def register():
    bpy.utils.register_module(__name__)
    setupProps()


def unregister():
    bpy.utils.unregister_module(__name__)
    removeProps()

if __name__ == "__main__":
    register()
