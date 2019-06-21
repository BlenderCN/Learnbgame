import bpy
import bpy_extras
import os
from . import addon
from mathutils import Euler
import os.path
import subprocess
import ntpath
import time

class ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load an SMO stage"""
    bl_idname = "import_scene.osi"
    bl_label = "Import Stage"
    bl_options = {'UNDO'}

    filename_ext = ".byml;.szs"
    filter_glob = bpy.props.StringProperty(default="*.byml;*.szs", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(name="File Path", description="Filepath used for importing the stage BYML/SZS file.", maxlen=1024, default="")
    scenarioValue = bpy.props.IntProperty(name="Scenario", description="Scenario to import.", min=0, max=14)
    onlyground = bpy.props.BoolProperty(name="Only Main Ground [WIP]", description="Only import main ground models.")

    @staticmethod
    def menu_func(self, context):
        self.layout.operator(ImportOperator.bl_idname, text="SMO Stage (.byml/.szs)")

    def execute(self, context):
        importer = Importer(self, context, self.properties.filepath, self.properties.scenarioValue, self.properties.onlyground)
        return importer.run()

class Importer:
    def __init__(self, operator, context, filepath, scenarioValue, onlyground):
        self.operator = operator
        self.context = context
        self.filepath = filepath
        self.scenarioValue = scenarioValue
        self.onlyground = onlyground

    def run(self):
        addon.stageFile = self.filepath
        addon.scenario = self.scenarioValue
        addon.groundonly = self.onlyground
        if self.filepath[len(self.filepath) - 3] == 's' and self.filepath[len(self.filepath) - 2] == 'z' and self.filepath[len(self.filepath) - 1] == 's':
            sarcextract_path = os.path.dirname(os.path.realpath(__file__)) + "/SARCExtract/SARCExtract.exe"
            p = subprocess.Popen([sarcextract_path, self.filepath])
            waiting = p.wait()
            self.filepath = self.filepath[:-4]
            addon.stageFile = self.filepath + "/" + ntpath.basename(self.filepath) + ".byml"
        
        exec(addon.osiAddonPreferences.run(addon.osiAddonPreferences))
        return {'FINISHED'}
