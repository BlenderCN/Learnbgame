bl_info = {
	"name": "Export iOS OpenGLES data (.h)",
	"author": "Galbacs Tibor",
	"version": (1, 0),
	"blender": (2, 5, 8),
	#	"api": 35622,
	"location": "File > Export",
	"description": "Export Model to Objective-C Header file",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame"
}

import bpy

def write_some_data(context, filepath, use_some_setting):
    _norm = use_some_setting[0]
    _col = use_some_setting[1]
    print("running write_some_data...")
    f = open(filepath, 'w')
    olist = ""
    #f.write("// context.selected_objects=%s\n" % context.selected_objects)
    for o in context.selected_objects:
        if olist:
            olist = olist + ', ' + o.name
        else:
            olist = o.name
    f.write("/* File: %s */\n" % (filepath))
    f.write("// Objects: %s\n" % (olist))
    f.write("// Setting: %s\n\n" % (use_some_setting))
    f.write('#import "OpenGLCommon.h"\n\n')
    datatype = "Vertex3D"
    if _norm:
        if _col == "OPT_TEX":
            datatype = "TexturedVertexData3D"
            #datatype = "VertexData3D"
        elif _col == "OPT_VCOL":
            datatype = "ColoredVertexData3D"
        else:
            datatype = "VertexData3D"
    # process all selected objects
    for o in context.selected_objects:
        if _col == "OPT_TEX":
            f.write("// Mesh data: %s\n" % (o.name))
            fp = o.data.uv_textures[0].data[0].image.name
            tfn = bpy.path.ensure_ext("%s" % (fp),".png")
            fn = "%s/%s" % (os.path.dirname(filepath), tfn)
            f.write("// texture name: %s\n" % fp)
            f.write("#define \tk%sTextureImageFileName\t\"%s\"\n\n" % (o.name, tfn))
            o.data.uv_textures[0].data[0].image.save_render(fn)
            # acquire vertices and texture uv's by faces
            f.write("static const %s %sData[] = {\n" % (datatype, o.name))
            vcount = 0
            for fa in o.data.faces:
                # faces / texture
                fav = fa.vertices
                if len(fav) > 3:
                    fav = (fav[0], fav[2], fav[1], fav[0], fav[3], fav[2])
                idx = 0
                for vi in fav:
                    v = o.data.vertices[vi]
                    vd = [v.co.x, v.co.y, v.co.z]
                    vt = o.data.uv_textures[0].data[fa.index].uv[idx]
                    idx = idx + 1
                    vcount = vcount + 1
                    f.write("\t{ /*v%03u*/{%f, %f, %f}," % (vi, vd[0], vd[2], -vd[1]))
                    if _norm or True:
                        nv = [v.normal.x, v.normal.y, v.normal.z]
                        f.write(" /*n*/{%f, %f, %f}," % (nv[0], nv[2], -nv[1]))
                    f.write(" /*uv*/{%f, %f}," % (vt[0], vt[1]))
                    f.write(" },\n")
            f.write("\t};\n")
            f.write("#define\tk%sNumberOfVertices\t%u\n\n" % (o.name, vcount))
                    
        else:
            # dump vertices, [normals, [vertexcolors]]
            f.write("// Mesh data: %s\n" % o.name)
            f.write("static const %s %sData[] = {\n" % (datatype, o.name))
            for v in o.data.vertices:
                vd = [v.co.x, v.co.y, v.co.z]
                f.write("\t/*v*/{ {%f, %f, %f}," % (vd[0], vd[2], -vd[1]))
                if _norm:
                    nv = [v.normal.x, v.normal.y, v.normal.z]
                    f.write(" /*n*/{%f, %f, %f}," % (nv[0], nv[2], -nv[1]))
                    #if _col == n'OPT_VCOL':
                        #vc = [v.
                f.write(" },\n")
            f.write("\t};\n")
            f.write("#define\tk%sNumberOfVertices\t%u\n\n" % (o.name, len(o.data.vertices)))
            
            # dump indices and uv mapping
            f.write("// Indices\n")
            f.write("static const GLushort %sDataIndices[] = {\n" % (o.name))
            indices = 0
            for p in o.data.faces:
                if len(p.vertices) == 3:
                    f.write("\t%u, %u, %u,\n" % (p.vertices[0], p.vertices[1], p.vertices[2]))
                    indices += 1
                else:
                    f.write("\t%u, %u, %u,\n" % (p.vertices[0], p.vertices[1], p.vertices[2]))
                    f.write("\t%u, %u, %u,\n" % (p.vertices[0], p.vertices[2], p.vertices[3]))
                    indices += 2
                    
            f.write("\t};\n")
            f.write("#define\tk%sNumberOfIndices\t%u\n\n" % (o.name, indices))
                                
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
import os.path

class ExportOpenGLESData(bpy.types.Operator, ExportHelper):
    '''Save selected objects into iOS - OpenGL ES include file format.  '''
    bl_idname = "export.some_data"  # this is important since its how bpy.ops.export.some_data is constructed
    bl_label = "Export iOS OpenGLES data (.h)"

    # ExportHelper mixin class uses this
    filename_ext = ".h"

    filter_glob = StringProperty(default="*.h", options={'HIDDEN'})
    
    check_existing = True
    
    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_vnormals = BoolProperty(name="Vertex normals", description="Include vertex normals", default=True)
    #use_colors = BoolProperty(name="VCol/UVpos", description="Include vertex colors or UV positions", default=True)

    use_coloring = EnumProperty(items=(('OPT_TEX', "UV coords", "Use UV texture coords"),
                               ('OPT_VCOL', "Vertex colors", "Use vertex colors."),
                               ('OPT_NONE', "None", "No coloring info."),
                               ),
                        name="Painting",
                        description="Choose between vertex colors and texture coords",
                        default='OPT_TEX')

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        return write_some_data(context, self.filepath, [self.use_vnormals, self.use_coloring])

def mutex_options(self, context):
    print(self.use_vnormals)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportOpenGLESData.bl_idname, text="OpenGLES Export")


def register():
    bpy.utils.register_class(ExportOpenGLESData)
    # bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportOpenGLESData)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export.some_data('INVOKE_DEFAULT')