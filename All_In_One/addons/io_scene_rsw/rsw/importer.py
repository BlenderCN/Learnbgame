import os
import bpy
import bpy_extras
from mathutils import Vector, Matrix, Quaternion
from bpy.props import StringProperty, BoolProperty, FloatProperty
from ..utils.utils import get_data_path
from ..rsw.reader import RswReader
from ..gnd.importer import GndImportOptions, GndImportOperator
from ..rsm.importer import RsmImportOptions, RsmImportOperator

class RswImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_rsw.rsw_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import Ragnarok Online RSW'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = ".rsw"

    filter_glob = StringProperty(
        default="*.rsw",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    data_path = StringProperty(
        default='',
        maxlen=255,
        subtype='DIR_PATH'
    )

    should_import_gnd = BoolProperty(default=True)
    should_import_models = BoolProperty(default=True)

    def execute(self, context):
        # Load the RSW file
        rsw = RswReader.from_file(self.filepath)

        # Find the data path.
        data_path = get_data_path(self.filepath)

        # TODO: create an EMPTY object that is the RSW parent object

        # Load the GND file and import it into the scene.
        if self.should_import_gnd:
            gnd_path = os.path.join(data_path, rsw.gnd_file)
            try:
                options = GndImportOptions()
                gnd_object = GndImportOperator.import_gnd(gnd_path, options)
            except FileNotFoundError:
                self.report({'ERROR'}, 'GND file ({}) could not be found in directory ({}).'.format(rsw.gnd_file, data_path))
                return {'CANCELLED'}
        if self.should_import_models:
            # Load up all the RSM files and import them into the scene.
            models_path = os.path.join(data_path, 'model')
            rsm_options = RsmImportOptions()
            model_data = dict()
            for rsw_model in rsw.models:
                if rsw_model.filename in model_data:
                    model_object = bpy.data.objects.new(rsw_model.name, model_data[rsw_model.filename])
                    bpy.context.scene.objects.link(model_object)
                else:
                    rsm_path = os.path.join(models_path, rsw_model.filename)
                    try:
                        model_object = RsmImportOperator.import_rsm(rsm_path, rsm_options)
                        model_data[rsw_model.filename] = model_object.data
                    except FileNotFoundError:
                        self.report({'ERROR'}, 'RSM file ({}) could not be found in directory ({}).'.format(rsw_model.filename, models_path))
                        return {'CANCELLED'}
                x, z, y = rsw_model.position
                model_object.location += Vector((x, y, -z))
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(RswImportOperator.bl_idname, text='Ragnarok Online RSW (.rsw)')
