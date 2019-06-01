import addon_utils
import bmesh
import bpy
import mathutils
import os
from mathutils import Euler
import os.path
from . import byml
from . import converting

# ---- Globals ----

objspath = ""
stageFile = ""
scenario = 0
groundonly = False

def osi_colbox(self, data, expand_property):
    # Creates an expandable and collapsible box for the UILayout.
    box = self.box()
    split = box.split(0.5)
    row = split.row(align=True)
    row.prop(data, expand_property, icon="TRIA_DOWN" if getattr(data, expand_property) else "TRIA_RIGHT",
             icon_only=True, emboss=False)
    row.label(getattr(data.rna_type, expand_property)[1]["name"])
    return box, split

# ---- Preferences ----

class osiAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # General
    objs_path = bpy.props.StringProperty(name="Models", description="Path to the Odyssey Editor Models folder.", subtype='DIR_PATH')
    
    def draw(self, context):
        box = self.layout.box()
        box.label("General Options:", icon='FILE_FOLDER')
        box.prop(self, "objs_path")
        if not self.objs_path:
            box.label("Please set this to the Odyssey Editor Models directory path.", icon='ERROR')
        elif not os.path.isdir(os.path.join(self.objs_path, "GameTextures")):
            box.label("Invalid Models directory. It does not have an GameTextures subfolder.", icon='ERROR')
        else:
            box.label("The Models path is valid!", icon='FILE_TICK')
        
    def run(self):
        objs_path = bpy.context.user_preferences.addons[__package__].preferences.objs_path
        f = open(stageFile, "rb")
        data = f.read()
        root = byml.Byml(data).parse()
        a = root[scenario]
        for b in a['ObjectList']:
            if 0 < 1:
                objPath = ""
                szsPath = ""
                objName = ''
                stageName = ''
                resourcePath = ''
                unitConfigName = ''
                objPosX = 0.0
                objPosY = 0.0
                objPosZ = 0.0
                objRotX = 0.0
                objRotY = 0.0
                objRotZ = 0.0
                objScaleX = 0.0
                objScaleY = 0.0
                objScaleZ = 0.0
                for c in b:
                    if c == 'ModelName':
                        objName = str(b['ModelName'])
                    elif c == 'PlacementFilename':
                        stageName = str(b['PlacementFilename'])
                    elif c == 'ResourceCategory':
                        resourcePath = str(b['ResourceCategory'])
                    elif c == 'UnitConfigName':
                        unitConfigName = str(b['UnitConfigName'])
                    elif c == 'Translate':
                        objPosX = float(str(b['Translate']['X']).replace(',', '.'))
                        objPosY = float(str(b['Translate']['Y']).replace(',', '.'))
                        objPosZ = float(str(b['Translate']['Z']).replace(',', '.'))
                    elif c == 'Rotate':
                        objRotX = float(str(b['Rotate']['X']).replace(',', '.'))
                        objRotY = float(str(b['Rotate']['Y']).replace(',', '.'))
                        objRotZ = float(str(b['Rotate']['Z']).replace(',', '.'))
                    elif c == 'Scale':
                        objScaleX = float(str(b['Scale']['X']).replace(',', '.'))
                        objScaleY = float(str(b['Scale']['Y']).replace(',', '.'))
                        objScaleZ = float(str(b['Scale']['Z']).replace(',', '.'))
            
                someString = ''
                someString2 = ''
                if unitConfigName != '':
                    objPath = objs_path + "/" + unitConfigName + ".obj"
                    someString = unitConfigName[len(unitConfigName) - 6]
                    someString += unitConfigName[len(unitConfigName) - 5]
                    someString += unitConfigName[len(unitConfigName) - 4]
                    someString2 = unitConfigName[1]
                    someString2 += unitConfigName[2]
                    someString2 += unitConfigName[3]
                else:
                    objPath = objs_path + "/" + objName + ".obj"
                    someString = objName[len(objName) - 6]
                    someString += objName[len(objName) - 5]
                    someString += objName[len(objName) - 4]
                    someString2 = objName[1]
                    someString2 += objName[2]
                    someString2 += objName[3]
                
                if groundonly == False:
                    someString = 'Gro'
                            
                if someString == 'Gro' or someString == 'und' or someString2 == 'Key' or someString == 'ing' or someString == 'ild' or someString == 'own' or someString == 'ava' or someString == 'Pan' or someString == 'ceL' or (someString == 'tep' and someString2 == 'Lav'):
                    if os.path.isfile(objPath):
                        imported_object = bpy.ops.import_scene.obj(filepath=objPath)
                        obj_object = bpy.context.selected_objects[0]
                        obj_object.location = (objPosX, objPosY, objPosZ)
                        obj_object.rotation_euler = Euler((objRotX, objRotY, objRotZ), 'XYZ')
                        obj_object.scale = (objScaleX, objScaleY, objScaleZ)
              
        print('Done!')

