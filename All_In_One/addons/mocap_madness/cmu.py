import bpy
import xml.etree.ElementTree as ET
#from math import *  # enable maths functions to be used in default settings 
import re
from os.path import isdir, join, dirname, basename, normpath
from .utils import is_subdir
from . import __name__ as addon_name


class CMUMocaps:
    def cmu_folder(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[addon_name].preferences
        return addon_prefs.cmu_folder

    def subject_from_folder(self, folder):
        '''
        if is_subdir(directory ,self.cmu_folder):
            sub = "%s_01" % basename(normpath(directory))
            found, subject, title = self.namefromcmu(sub)
        '''
        found, subject, title = self.namefromcmu(sub)
        return found, subject, title

    def cmu_check(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[addon_name].preferences
        return addon_prefs.use_cmu_data

    def LoadCMUIndexXML(self):
        Dir = dirname(__file__)
        path = join(Dir, 'CMUIndex.xml')
        #path = "F:\\blender\\cmu_mocap\\cmu-mocap-index-text.xml"
        # load settings from the addon. (can be user saved)

        self.CMUIndexXML = ET.parse(path)


    def subjects(self):
        s = []
        for node in self.CMUIndexXML.getiterator(tag="subject"):
            s.append((node.get("id"), node.get("desc")))
        return s

    def namefromcmu(self, id):
        #global CMUIndexXML
        m = re.match(r'(?P<subject>\d+)_(?P<number>\d+)', id)
        #print("MM", m)
        if m:
            subject = int(m.group("subject"))
            #print(subject)
            if self.CMUIndexXML:
                node = self.CMUIndexXML.find('subject[@id="%02d"]' % subject)
                if node is not None:
                    bnode = node.find('bvh[@id="%s"]' % id)
                    if bnode is not None:
                        return True, node.get("desc"), bnode.get("desc")
        return (False, "NA", id)

    def __init__(self):
        # context in to check against user prefs.
        self.LoadCMUIndexXML()


class CMUImportPanel(CMUMocaps, bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "CMU"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll(cls, context):
        op = context.active_operator
        print("PPPP", op)
        if op is None:
            return False
        print(op.bl_idname)
        return op.bl_idname == "IMPORT_ANIM_OT_bvh_mocap_madness"

    def draw_header(self, context):
        layout = self.layout
        layout.label("EDIT")

    def draw(self, context):
        #print("OP", context.active_operator.bl_idname)
        layout = self.layout

        op = context.active_operator
        sub = "%s_01" % basename(normpath(op.directory))
        found, subject, title = self.namefromcmu(sub)
        layout.menu("mocapmadness.cmu_subject_menu",
                    text="%s" % (subject))
        layout.operator("file.select_all_toggle")
        for f in op.files:
            bvh_name = bpy.path.display_name_from_filepath(f.name)
            found, subject, title = self.namefromcmu(bvh_name)
            layout.label("%s %s" % (bvh_name, title))

class CMUSubjectMenu(CMUMocaps, bpy.types.Menu):
    bl_label = "Choose CMU Folder"
    bl_idname = "mocapmadness.cmu_subject_menu"

    def draw(self, context):
        layout = self.layout

        for id, subject in self.subjects():
            dir = join(self.cmu_folder(context),id)
            row = layout.row()
            row.enabled = isdir(dir)
            op = row.operator("file.select_bookmark",
                                 text="%s %s" % (id, subject))
            op.dir = dir

def register():
    print("reg cmu")
    bpy.utils.register_class(CMUSubjectMenu)
    bpy.utils.register_class(CMUImportPanel)


def unregister():
    bpy.utils.unregister_class(CMUSubjectMenu)
    bpy.utils.unregister_class(CMUImportPanel)
