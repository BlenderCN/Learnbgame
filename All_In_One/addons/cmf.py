bl_info = {
    "name": "Export Columbus Model Format (CMF) file",
    "category": "Learnbgame",
}

import bpy

class ExportCMF(bpy.types.Operator):
    bl_idname = "export_mesh.cmf"
    bl_label = "Export CMF"
    filename_ext = ".cmf"
    filter_glob = bpy.props.StringProperty(default="*.cmf", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(default="untitled.cmf", subtype='FILE_PATH')

    select_only = bpy.props.BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False)

    write_indexes = bpy.props.BoolProperty(
    		name="Write indexes",
    		description="Create and write indexes",
    		default=False)

    write_positions = bpy.props.BoolProperty(
    		name="Write positions",
    		description="Write vertex positions",
    		default=True)

    write_texcoords = bpy.props.BoolProperty(
    		name="Write texcoords",
    		description="Write texture coordinates",
    		default=True)

    write_normals = bpy.props.BoolProperty(
    		name="Write normals",
    		description="Write normals",
    		default=True)

    write_tangents = bpy.props.BoolProperty(
    		name="Write tangents",
    		description="Write tangents",
    		default=False)

    write_colors = bpy.props.BoolProperty(
    		name = "Write colors",
    		description="Write vertex colors",
    		default=False)

    def execute(self, context):
        import cmf_export

        cmf_export.writeFile(
                self.filepath,
                self.select_only,
                self.write_indexes,
                self.write_positions,
                self.write_texcoords,
                self.write_normals,
                self.write_tangents,
                self.write_colors)
        
        print ('Successfully exported CMF file')
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_export(self, context):
    self.layout.operator(ExportCMF.bl_idname, text="Columbus Model Format (.cmf)")

def register():
    bpy.utils.register_class(ExportCMF)

def unregister():
    bpy.utils.unregister_class(ExportCMF)

if __name__ == "__main__":
    register()




