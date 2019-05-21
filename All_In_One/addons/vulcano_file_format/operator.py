import bpy
import bpy_extras

class VulcanoExporter(
    bpy.types.Operator,
    bpy_extras.io_utils.ExportHelper):
    """Exports current scene to Vulcano File Format (.vmsh)"""
    
    # Unique identifier to be referenced by buttons and menu items
    bl_idname = "vulcano_file_format.vulcano_exporter"
    # Text used by UI elements to display in the interface
    bl_label = "Export Vulcano File (.vffmsh)"
    # Add operator preset options to the File Selection dialog
    bl_options = {"PRESET"}
    
    ############################################################################
    # Operator properties
    ############################################################################  
    
    # Set the file extension (used by ExportHelper internally)
    filename_ext = ".vffmsh"
    
    # File filter
    filter_glob: bpy.props.StringProperty(
        default="*.vffmsh",
        options={"HIDDEN"})
    
    # Export options
    box_title: bpy.props.StringProperty()
    exported_file_type: bpy.props.EnumProperty(
        items=(("EXPORT_FORMAT_BINARY", "Binary",
                "Exports Vulcano File (.vmsh) in binary format"),
               ("EXPORT_FORMAT_ASCII", "ASCII",
                "Exports Vulcano File (.vmsh) in ASCII text format")),
        name="Format:",
        description="Select the exported file format type")
        
    path_mode: bpy_extras.io_utils.path_reference_mode
    
    use_selection: bpy.props.BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=True)
        
    apply_modifiers: bpy.props.BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers",
        default=True)
        
    clear_system_console: bpy.props.BoolProperty(
        name="Clear System Console",
        description="Clear the Blender system console",
        default=True)
    
    ############################################################################
    # Methods
    ############################################################################
    
    def draw(self, context):
        """
        Draws the layout manually. Without this method the UI methods will be
        placed in the layout automatically.
        """ 
        # Draw a box and put the UI elements inside
        box = self.layout.box()
        # A title for the box
        box.label(text="Export Options:", icon="OUTLINER_DATA_MESH")
        # Export options
        box.prop(self, "exported_file_type")
        box.prop(self, "path_mode")
        box.prop(self, "use_selection")
        box.prop(self, "apply_modifiers")
        # Put the rest of the UI elements on a new row
        row = self.layout.row()
        row.prop(self, "clear_system_console")
    
    def execute(self, context):
        """
        Called when running the operator.
        """
        from . import exporter
        exporter.export_VulcanoFileFormatMesh(self, context)
        
        return {"FINISHED"}
    
    ############################################################################
    # Class methods
    ############################################################################
     
    @classmethod
    def poll(cls, context):
        """
        Checks if the operator can run.
        """
        return context.active_object is not None
