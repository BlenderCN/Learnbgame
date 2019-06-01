
import bpy
import time
from bpy_extras import io_utils
from . import stalker_object
from . import importer
from . import parse_object


class OperatorImportObject(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = 'stalker.import_object'
    bl_label = 'Import *.Object'
    bl_description = 'Imports X-Ray Engine *.object files'
    bl_options = {'UNDO'}

    filename_ext = '.object'
    filter_glob = bpy.props.StringProperty(default='*.object', options={'HIDDEN'})
    filepath = bpy.props.StringProperty(name='File Path', maxlen=1024, default='')
    smoothing_groups_type = bpy.props.EnumProperty(items=[
                         ('SOC', 'SoC', ''),
                         ('CS_COP', 'CS\CoP', '')],
                         default='SOC',
                         name='Smooth Group Type')

    def draw(self, context):
        split = self.layout.split(percentage=0.6)
        split.label('Smooth Group Type:')
        split.row().prop(self.properties, 'smoothing_groups_type', expand=True)

    def execute(self, context):
        startTime = time.time()
        file = open(self.properties.filepath, 'rb')
        fileData = file.read()
        file.close()
        so = stalker_object.StalkerObject()
        so.context.operator = self
        so.context.texture_folder = context.user_preferences.addons['io_scene_stalker_object'].preferences.texture_folder
        so.context.smoothing_groups_type = self.properties.smoothing_groups_type
        so.name = self.properties.filepath.split('\\')[-1][:-len('.object')]
        parse_object.read_object(fileData, so)
        importer.import_object(so)
        print('total time: {0:.3}'.format(time.time() - startTime))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
