'''
Created on Oct 1, 2017

@author: Patrick
'''
import os
import bpy
import itertools
from mathutils import Matrix
from io_mesh_stl import stl_utils, blender_utils


def write_some_data(context, filepath, use_some_setting):
    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write("Hello World %s" % use_some_setting)
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper, orientation_helper_factory, axis_conversion
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator
import tracking

IOSTLOrientationHelper = orientation_helper_factory("IOSTLOrientationHelper", axis_forward='Y', axis_up='Z')

class APGExportBlock(Operator, ExportHelper, IOSTLOrientationHelper):
    """Use this to export your splint"""
    bl_idname = "apg.export_block"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export APG Block STL"

    # ExportHelper mixin class uses this
    filename_ext = ".stl"

    filter_glob = StringProperty(
            default="*.stl",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )


    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )
    global_scale = FloatProperty(
            name="Scale",
            min=0.01, max=1000.0,
            default=1.0,
            )

    use_scene_unit = BoolProperty(
            name="Scene Unit",
            description="Apply current scene's unit (as defined by unit scale) to exported data",
            default=False,
            )
    ascii = BoolProperty(
            name="Ascii",
            description="Save the file in ASCII file format",
            default=False,
            )
    use_mesh_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Apply the modifiers before saving",
            default=True,
            )
    batch_mode = EnumProperty(
            name="Batch Mode",
            items=(('OFF', "Off", "All data in one file"),
                   ('OBJECT', "Object", "Each object as a file"),
                   ))
    
    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "use_selection",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            "use_scene_unit",
                                            "use_mesh_modifiers",
                                            "batch_mode"
                                            ))

        scene = context.scene
        
        Block = bpy.data.objects.get('Templates Base')
        if not Block:
            self.report({'ERROR'}, 'You have not created your block yet')
            return {'CANCEL'}
        
        
        #TODO, maybe give option to export the sweep surface or convex surface
        data_seq = [Block]

        # Take into account scene's unit scale, so that 1 inch in Blender gives 1 inch elsewhere! See T42000.
        global_scale = self.global_scale
        if scene.unit_settings.system != 'NONE' and self.use_scene_unit:
            global_scale *= scene.unit_settings.scale_length

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4() * Matrix.Scale(global_scale, 4)

        if self.batch_mode == 'OFF':
            faces = itertools.chain.from_iterable(
                    blender_utils.faces_from_mesh(ob, global_matrix, self.use_mesh_modifiers)
                    for ob in data_seq)

            stl_utils.write_stl(faces=faces, **keywords)
        elif self.batch_mode == 'OBJECT':
            prefix = os.path.splitext(self.filepath)[0]
            keywords_temp = keywords.copy()
            for ob in data_seq:
                faces = blender_utils.faces_from_mesh(ob, global_matrix, self.use_mesh_modifiers)
                keywords_temp["filepath"] = prefix + bpy.path.clean_name(ob.name) + ".stl"
                stl_utils.write_stl(faces=faces, **keywords_temp)
        
        filename = os.path.basename(self.filepath).split('.')[0]
        tracking.trackUsage("apgExportBlock", param = filename)
        return {'FINISHED'}

class APGExportAbutment(Operator, ExportHelper, IOSTLOrientationHelper):
    """Use this to export your designed abutment"""
    bl_idname = "apg.export_abutment"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export APG abutment STL"

    # ExportHelper mixin class uses this
    filename_ext = ".stl"

    filter_glob = StringProperty(
            default="*.stl",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )


    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )
    global_scale = FloatProperty(
            name="Scale",
            min=0.01, max=1000.0,
            default=1.0,
            )

    use_scene_unit = BoolProperty(
            name="Scene Unit",
            description="Apply current scene's unit (as defined by unit scale) to exported data",
            default=False,
            )
    ascii = BoolProperty(
            name="Ascii",
            description="Save the file in ASCII file format",
            default=False,
            )
    use_mesh_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Apply the modifiers before saving",
            default=True,
            )
    batch_mode = EnumProperty(
            name="Batch Mode",
            items=(('OFF', "Off", "All data in one file"),
                   ('OBJECT', "Object", "Each object as a file"),
                   ))
    
    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "use_selection",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            "use_scene_unit",
                                            "use_mesh_modifiers",
                                            "batch_mode"
                                            ))

        scene = context.scene
        
        Abut = bpy.data.objects.get('Abutment:Master')
        if not Abut:
            self.report({'ERROR'}, 'You have not created an abutment yet')
            return {'CANCELLED'}
        
        
        #TODO, maybe give option to export the sweep surface or convex surface
        data_seq = [Abut]

        # Take into account scene's unit scale, so that 1 inch in Blender gives 1 inch elsewhere! See T42000.
        global_scale = self.global_scale
        if scene.unit_settings.system != 'NONE' and self.use_scene_unit:
            global_scale *= scene.unit_settings.scale_length

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4() * Matrix.Scale(global_scale, 4)

        if self.batch_mode == 'OFF':
            faces = itertools.chain.from_iterable(
                    blender_utils.faces_from_mesh(ob, global_matrix, self.use_mesh_modifiers)
                    for ob in data_seq)

            stl_utils.write_stl(faces=faces, **keywords)
        elif self.batch_mode == 'OBJECT':
            prefix = os.path.splitext(self.filepath)[0]
            keywords_temp = keywords.copy()
            for ob in data_seq:
                faces = blender_utils.faces_from_mesh(ob, global_matrix, self.use_mesh_modifiers)
                keywords_temp["filepath"] = prefix + bpy.path.clean_name(ob.name) + ".stl"
                stl_utils.write_stl(faces=faces, **keywords_temp)

        filename = os.path.basename(self.filepath).split('.')[0]
        tracking.trackUsage("apgExportAbutment", param = filename)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(APGExportBlock)
    bpy.utils.register_class(APGExportAbutment)

def unregister():
    bpy.utils.unregister_class(APGExportBlock)
    bpy.utils.register_class(APGExportAbutment)

