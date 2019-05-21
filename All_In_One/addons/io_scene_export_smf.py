import bpy, os, bpy_extras.io_utils, json
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 path_reference_mode,
                                 axis_conversion,
                                 )
from bpy.props import *

bl_info = {
    "name": "SMF model exporter",
    "author": "KaadmY",
    "blender": (2, 69, 0),
    "location": "File > Import-Export",
    "description": "Export SMF mesh",
    "warning": "",
    "category": "Learnbgame"
}

def name(n):
    n=n.replace(" ", "_")
    return n

def faceToTriangles(face):
    triangles = []
    if len(face) == 4:
        triangles.append([face[0], face[1], face[2]])
        triangles.append([face[2], face[3], face[0]])
    else:
        triangles.append(face)

    return triangles

def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

def export_obj(scene, obj):
    out=""

    me=obj.to_mesh(scene, True, 'PREVIEW', calc_tessface=False)
    mesh_triangulate(me)

    verts=me.vertices[:]
    texcoords=me.uv_layers.active.data[:]
    
    vert_out=face_out=texcoord_out=""

    active_UVLayer=me.uv_layers.active

    material_slots=[m.name if m else None for m in me.materials[:]]

    for i in range(len(me.vertices)):
        v=me.vertices[i]
        vert_out+="vertex %.6f %.6f %.6f\n" % (v.co.x, v.co.y, v.co.z)

    for i in range(len(active_UVLayer.data)):
        texcoord_out+="texcoord %.6f %.6f\n" % (active_UVLayer.data[i].uv.x, active_UVLayer.data[i].uv.y)

    for f in range(len(me.polygons)):
        indices=[]
        for i in range(3):
            index=me.polygons[f].vertices[i]
            indices.append(index)
            v=me.vertices[index]

        face_out+="face %d %d %d %d %d %d %s\n" % (indices[0], indices[1], indices[2], me.polygons[f].loop_indices[0], me.polygons[f].loop_indices[1], me.polygons[f].loop_indices[2], name(material_slots[me.polygons[f].material_index]))

    bpy.data.meshes.remove(me)
    
    out+=vert_out
    out+=texcoord_out
    out+=face_out

    return out

def export(context, options):
    file=open(options["filepath"], "w")
    out={}
    if context.active_object.type == "MESH":
        out=export_obj(context.scene, context.active_object)
    else:
        raise ValueError("Active object not a mesh")
    file.write(out)
    file.close()
    

class ExportSMFMesh(bpy.types.Operator, ExportHelper):
    """Export SMF mesh"""
    bl_idname="export_scene.smf"
    bl_label="Export SMF mesh"
    bl_options={"PRESET"}

    filename_ext=".smf"
    filter_glob=StringProperty(
        default="*.smf",
        options={"HIDDEN"},
        )

    def execute(self, context):
        export(context, self.as_keywords())
        return {"FINISHED"}

def menu_func_export(self, context):
    self.layout.operator(ExportSimplemeshformatMesh.bl_idname, text="JSON Simple mesh format export")

def register():
    bpy.utils.register_module(__name__)

#    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

#    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
