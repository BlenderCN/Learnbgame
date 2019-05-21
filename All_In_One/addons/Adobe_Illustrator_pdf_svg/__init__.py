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

# <pep8 compliant>

bl_info = {
  "name": "Adobe Illustrator / PDF / SVG",
  "author": "Howard Trickey",
  "version": (0, 8),
  "blender": (2, 5, 7),
  "api": 35040,
  "location": "File > Import-Export > Adobe Illustrator/PDF/SVG ",
  "description": "Import Adobe Illustrator, PDF, and SVG",
  "warning": "",
  "wiki_url": \
      "http://http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Import-Export/AI_PDF_SVG",
  "tracker_url": \
      "http://http://projects.blender.org/tracker/index.php?func=detail&aid=27246",
  "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
else:
    from . import geom
    from . import model
    from . import vecfile
    from . import import_vecfile
    from . import offset
    from . import pdf
    from . import svg
    from . import triquad
    from . import art2polyarea

import math
import bpy
from bpy.props import *


class VectorImporter(bpy.types.Operator):
    bl_idname = "import_vec.aipdfsvg"
    bl_label = "Import AI/PDF/SVG"
    bl_options = {"REGISTER", "UNDO"}

    filepath = StringProperty(name="File Path",
      description="Filepath used for importing the vector file",
      maxlen=1024, default="", subtype="FILE_PATH")
    smoothness = IntProperty(name="Smoothness",
        description="How closely to approximate curves",
        default=1,
        min=0,
        max=100)
    scale = FloatProperty(name="Scale",
        description="Scale longer bounding box side to this size",
        default=4.0,
        min=0.1,
        max=100.0,
        unit="LENGTH")
    subdiv_kind = EnumProperty(name="Subdivision Method",
        description="Method for approximating curves with lines",
        items=[ \
          ('UNIFORM', "Uniform",
              "All curves bisected 'smoothness' times"),
          ('ADAPTIVE', "Adaptive",
              "Curves subdivided until flat enough, as" \
              " determined by 'smoothness'"),
          ('EVEN', "Even",
              "Curves subdivided until segments have a common length," \
              " determined by 'smoothness'"),
          ],
        default='ADAPTIVE')
    filled_only = BoolProperty(name="Filled paths only",
        description="Only import filled paths",
        default=True)
    ignore_white = BoolProperty(name="Ignore white-filled",
        description="Do not import white-filled paths",
        default=True)
    combine_paths = BoolProperty(name="Combine paths",
        description="Use all paths when looking for holes",
        default=False)
    use_colors = BoolProperty(name="Use colors",
        description="Use colors from vector file as materials",
        default=False)
    extrude_depth = FloatProperty(name="Extrude depth",
      description="Depth of extrusion, if > 0",
      default=0.0,
      min=0.0,
      max=100.0,
      unit='LENGTH')
    bevel_amount = FloatProperty(name="Bevel amount",
      description="Amount of inward bevel, if > 0",
      default=0.0,
      min=0.0,
      max=1000.0,
      unit='LENGTH')
    bevel_pitch = FloatProperty(name="Bevel pitch",
      description="Angle of bevel from horizontal",
      default=45 * math.pi / 180.0,
      min=0.0,
      max=89.0 * math.pi / 180.0,
      unit='ROTATION')
    cap_back = BoolProperty(name="Cap back",
      description="Cap the back if extruding",
      default=False)
    # some info display properties
    num_verts = IntProperty(name="Number of vertices",
      default=0)
    num_faces = IntProperty(name="Number of faces",
      default=0)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label("Import Options")
        box.prop(self, "filepath")
        box.prop(self, "smoothness")
        box.prop(self, "scale")
        box.prop(self, "subdiv_kind")
        box.prop(self, "filled_only")
        box.prop(self, "ignore_white")
        box.prop(self, "combine_paths")
        box.prop(self, "use_colors")
        box.prop(self, "extrude_depth")
        box.prop(self, "bevel_amount")
        box.prop(self, "bevel_pitch")
        box.prop(self, "cap_back")
        if self.num_verts > 0:
            layout.label(text="Ve:" + str(self.num_verts) + \
              " | Fa:" + str(self.num_faces))

    def action(self, context):
        #convert the filename to an object name
        if not self.filepath:
            return
        objname = self.filepath.split("\\")[-1].split("/")[-1]
        if objname.find(".") > 0:
            objname = objname.split(".")[0]
        options = import_vecfile.ImportOptions()
        options.scaled_side_target = self.scale
        options.quadrangulate = True
        options.extrude_depth = self.extrude_depth
        options.bevel_amount = self.bevel_amount
        options.bevel_pitch = self.bevel_pitch
        options.cap_back = self.cap_back
        options.convert_options.subdiv_kind = self.subdiv_kind
        options.convert_options.smoothness = self.smoothness
        options.convert_options.filled_only = self.filled_only
        options.convert_options.ignore_white = self.ignore_white
        options.convert_options.combine_paths = self.combine_paths
        (mdl, msg) = import_vecfile.ReadVecFileToModel(self.filepath, options)
        if msg:
            self.report({'ERROR'},
                "Problem reading file " + self.filepath + ": " + msg)
            return {'FINISHED'}
        verts = mdl.points.pos
        faces = [f for f in mdl.faces if 3 <= len(f) <= 4]
        mesh = bpy.data.meshes.new(objname)
        mesh.from_pydata(verts, [], faces)
        if self.use_colors:
            add_colors(mesh, mdl.face_data)
        mesh.update()
        self.num_verts = len(verts)
        self.num_faces = len(faces)
        obj = bpy.data.objects.new(objname, mesh)
        context.scene.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        context.scene.objects.active = obj

    def execute(self, context):
        self.action(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action(context)
        return {'FINISHED'}
        # the modal way
        #wm = context.window_manager
        #wm.fileselect_add(self)
        #return {'RUNNING_MODAL'}


def add_colors(mesh, colors):
    # assume colors are parallel to faces in mesh
    if len(colors) < len(mesh.faces):
        return

    # use rgbtoindex to keep track of colors already
    # seen and map them to indices into mesh.materials
    rgbtoindex = {}
    matnameprefix = "VImat." + mesh.name + "."
    for i, c in enumerate(colors):
        print("color for face", i)
        if c not in rgbtoindex:
            matname = matnameprefix + str(len(bpy.data.materials))
            mat = bpy.data.materials.new(matname)
            mat.diffuse_color = c
            mesh.materials.append(mat)
            cindex = len(mesh.materials) - 1
            rgbtoindex[c] = cindex
        else:
            cindex = rgbtoindex[c]
        mesh.faces[i].material_index = cindex


def menu_import(self, context):
    self.layout.operator(VectorImporter.bl_idname,
        text="Vector files (.ai, .pdf, .svg)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_import)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
