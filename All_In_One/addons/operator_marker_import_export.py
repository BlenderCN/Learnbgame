from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import bpy

bl_info = {
    "name": "Import / Export Markers as CSV",
    "author": "Gabriel Montagné Láscaris-Comneno <gabriel@tibas.london>",
    "version": (1, 0, 0),
    "blender": (2, 78),
    "location": "File > Import / File > Export",
    "description": "Add import export operators for timeline markers to CSV files",
    "warning": "",
    "wiki_url": "github.com/gabrielmontagne/blender-addon-import-export-timeline-markers",
    "tracker_url": "github.com/gabrielmontagne/blender-addon-import-export-timeline-markers/issues",
    "category": "Import-Export"
}

class ExportTimelineMarkers(Operator, ExportHelper):
    """Export Timeline Markers to CSV File"""
    bl_idname = "export.timeline_markers"
    bl_label = "Export Timeline Markers to CSV File"
    filename_ext = ".csv"
    filter_glob = StringProperty(default="*.csv", options={'HIDDEN'}, maxlen=255)

    def execute(self, context):
        with open(self.properties.filepath, 'w', encoding='utf-8') as f:
            for marker in context.scene.timeline_markers:
                f.write('{},{}\n'.format(marker.frame, marker.name))

        return {'FINISHED'}

class ImportTimelineMarkers(Operator, ImportHelper):
    """Import Timeline Markers from CSV File"""
    bl_idname = "import.timeline_markers"
    bl_label = "Import Timeline Markers From a CSV File"
    filename_ext = '.csv'
    filter_glob = StringProperty(default='*.csv', options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        self.properties.filepath
        with open(self.properties.filepath, 'r') as f:
            for line in f:
                frame, name = line.split(',')
                context.scene.timeline_markers.new(name.strip(), frame=int(frame))

        return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(ExportTimelineMarkers.bl_idname, text="Export Timeline Markers as CSV")

def menu_func_import(self, context):
    self.layout.operator(ImportTimelineMarkers.bl_idname, text="Import Timeline Markers as CSV")

def register():
    bpy.utils.register_class(ExportTimelineMarkers)
    bpy.utils.register_class(ImportTimelineMarkers)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ExportTimelineMarkers)
    bpy.utils.unregister_class(ImportTimelineMarkers)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
