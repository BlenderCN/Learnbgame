# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "FBX I/O",
    "author": "Thomas Larsson",
    "version": "0.1",
    "blender": (2, 6, 5),
    "api": 40000,
    "location": "View3D > Properties > FBX Test",
    "description": "Yet another FBX exporter/importer",
    "warning": "",
    'wiki_url': "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    print("Reloading FBX importer")
    import imp
    imp.reload(fbx)
    imp.reload(fbx_basic)
    imp.reload(fbx_props)
    imp.reload(fbx_model)

    imp.reload(fbx_image)
    imp.reload(fbx_texture)
    imp.reload(fbx_material)
    imp.reload(fbx_geometry)
    imp.reload(fbx_deformer)
    imp.reload(fbx_constraint)    
    imp.reload(fbx_anim)

    imp.reload(fbx_mesh)
    imp.reload(fbx_nurb)
    imp.reload(fbx_armature)
    imp.reload(fbx_lamp)
    imp.reload(fbx_camera)

    imp.reload(fbx_group)
    imp.reload(fbx_object)
    imp.reload(fbx_null)
    imp.reload(fbx_scene)
    imp.reload(fbx_data)

    imp.reload(fbx_token)
    imp.reload(fbx_export)
    imp.reload(fbx_import)
    imp.reload(fbx_build)
else:
    print("Loading FBX importer")
    import bpy
    from bpy_extras.io_utils import *
    from bpy.props import *
    import os

    from . import fbx
    from . import fbx_basic
    from . import fbx_props
    from . import fbx_model

    from . import fbx_image
    from . import fbx_texture
    from . import fbx_material
    from . import fbx_geometry
    from . import fbx_deformer
    from . import fbx_constraint    
    from . import fbx_anim

    from . import fbx_mesh
    from . import fbx_nurb
    from . import fbx_armature
    from . import fbx_lamp
    from . import fbx_camera

    from . import fbx_group
    from . import fbx_object
    from . import fbx_null
    from . import fbx_scene
    from . import fbx_data

    from . import fbx_token
    from . import fbx_export
    from . import fbx_import
    from . import fbx_build
    

class ImportFBX(bpy.types.Operator, ImportHelper):
    """Import a Filmbox FBX File"""
    bl_idname = "import_scene.fbx_io"
    bl_label = "Import AutoDesk FileBox (.fbx)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".fbx"
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'})

    createNewScene = BoolProperty(name="Create New Scene", default=False)
    zUp = BoolProperty(name="Z up", description="Use Z as global up axis (always Y up in FBX file)", default=True)        
    boneAxis = EnumProperty(
        name="Bone Axis", 
        description="Axis pointing along bone (always X in FBX file)",
        items=(('X','X','X',0),('Y','Y','Y',1),('Z','Z','Z',2)), 
        default = 'X',
    )
    minBoneLength = FloatProperty(name="Minimal Bone Length", min=0.01, max=100.0, default=1.0)
    mirrorFix = BoolProperty(name="Bone Mirror Fix", description="Try to fix problem with mirrored bones", default=True)  
    scale = FloatProperty(name="Scale", min=0.01, max = 100.0, default=1.0)
    
    def execute(self, context):
        fbx.settings.createNewScene = self.createNewScene
        fbx.settings.zUp = self.zUp
        fbx.settings.boneAxis = AxisNumber[self.boneAxis]
        fbx.settings.minBoneLength = self.minBoneLength
        fbx.settings.mirrorFix = self.mirrorFix
        fbx_import.importFbxFile(context, self.filepath, self.scale)
        return {'FINISHED'}
        
    def draw(self, context):
        #self.layout.prop(self, "createNewScene")
        self.layout.prop(self, "zUp")
        self.layout.prop(self, "boneAxis", expand=True)
        self.layout.prop(self, "minBoneLength")
        self.layout.prop(self, "mirrorFix")
        self.layout.prop(self, "scale")


AxisNumber = { 'X' : 0, 'Y' : 1, 'Z' : 2 }


class ExportFBX(bpy.types.Operator, ExportHelper):
    """Export a Filmbox FBX File"""
    bl_idname = "export_scene.fbx_io"
    bl_label = "Export AutoDesk FileBox (.fbx)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".fbx"
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'} )
    
    zUp = BoolProperty(name="Z Up", description="Use Z as global up axis (always Y up in FBX file)", default=True)        
    includePropertyTemplates = BoolProperty(name="Include Property Templates", description="Include property templates in exported file", default=True)
    makeSceneNode = BoolProperty(name="Make Scene Node", default=False)
    selectedOnly = BoolProperty(name="Selected Objects Only", default=True)
    scale = FloatProperty(name="Scale", min=0.01, max = 100.0, default=1.0)

    def execute(self, context):
        fbx.settings.zUp = self.zUp
        fbx.settings.includePropertyTemplates = self.includePropertyTemplates
        fbx.settings.makeSceneNode = self.makeSceneNode
        fbx.settings.selectedOnly = self.selectedOnly
        fbx_export.exportFbxFile(context, self.filepath, scale=self.scale)
        return {'FINISHED'}
 
    def draw(self, context):
        self.layout.prop(self, "includePropertyTemplates")
        #self.layout.prop(self, "makeSceneNode")
        self.layout.prop(self, "selectedOnly")
        self.layout.prop(self, "zUp")
        self.layout.prop(self, "minBoneLength")
        self.layout.prop(self, "mirrorFix")
        self.layout.prop(self, "scale")


#------------------------------------------------------------------
#   Testing
#------------------------------------------------------------------

class VIEW3D_OT_TestImportButton(bpy.types.Operator):
    bl_idname = "fbx.test_import"
    bl_label = "Test Import"
    bl_options = {'UNDO'}    
    filepath = StringProperty()
    
    def execute(self, context):
        scn = context.scene
        fbx.settings.zUp = scn.FbxZUp
        fbx.settings.boneAxis = AxisNumber[scn.FbxBoneAxis]
        fbx_import.importFbxFile(context, self.filepath, scn.FbxScale)
        return {'FINISHED'}


class VIEW3D_OT_TestExportButton(bpy.types.Operator):
    bl_idname = "fbx.test_export"
    bl_label = "Test Export"
    bl_options = {'UNDO'}
    filepath = StringProperty()
    
    def execute(self, context):
        scn = context.scene
        fbx.settings.Zup = scn.FbxZUp
        fbx.settings.boneAxis = AxisNumber[scn.FbxBoneAxis]
        fbx_export.exportFbxFile(context, self.filepath)
        return {'FINISHED'}

 
class FbxTestPanel(bpy.types.Panel):
    bl_label = "FBX Test"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):    
        scn = context.scene
        #self.layout.operator("fbx.preset", text="Maya Presets").preset="Maya"
        #self.layout.operator("fbx.preset", text="Blender Presets").preset="Blender"
        self.layout.prop(scn, "FbxFile")
        self.layout.prop(scn, "FbxZUp")
        self.layout.prop(scn, "FbxBoneAxis", expand=True)
        self.layout.prop(scn, "FbxScale")
        self.layout.operator("fbx.test_export").filepath="/home/myblends/fbx-stuff/test.fbx"
        self.layout.operator("fbx.test_import").filepath=("/home/myblends/fbx-stuff/%s.fbx" % scn.FbxFile)
        self.layout.operator("fbx.test_import", text="Test Import foo").filepath="/Users/Thomas/Documents/makehuman/exports/foo/foo.fbx"
        self.layout.operator("fbx.test_build")

#------------------------------------------------------------------
#   Init and register
#------------------------------------------------------------------

def menu_func_import(self, context):
    self.layout.operator(ImportFBX.bl_idname, text="AutoDesk FilmBox (.fbx)")


def menu_func_export(self, context):
    self.layout.operator(ExportFBX.bl_idname, text="AutoDesk FilmBox (.fbx)")


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.FbxFile = StringProperty(name="File", default="test")    
    bpy.types.Scene.FbxZUp = BoolProperty(
        name="Z up", 
        description="Use Z as global up axis (always Y up in FBX file)", 
        default=True)        
    bpy.types.Scene.FbxBoneAxis = EnumProperty(
        name="Bone Axis", 
        description="Axis pointing along bone (always X in FBX file)",
        items=(('X','X','X',0),('Y','Y','Y',1),('Z','Z','Z',2)), 
        default = 'X',
    )
    bpy.types.Scene.FbxScale = FloatProperty(name="Scale", min=0.01, max = 100.0, default=1.0)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

