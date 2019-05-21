import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper


bl_info = {
    'name': "Four-kb model exporter",
    'author': 'Julian Goldsmith',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': "File > Export",
    'description': "Export Four-kb model",
    'category': 'Import-Export'
}


class MdlExporter(bpy.types.Operator, ExportHelper):
    bl_idname = 'export.fourkb'
    bl_label = 'Export Four-kb'
        
    filename_ext = '.mdl'
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})
        
    def execute(self, context):
        write(self.filepath)
        return {'FINISHED'}
    
        
def menu_export(self, context):
    self.layout.operator(MdlExporter.bl_idname, text="Four-kb model (.mdl)")
    
def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.INFO_MT_file_export.append(menu_export)
    
    
def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.types.INFO_MT_file_export.remove(menu_export)


def faceToTriangles(face):
    triangles = []
    if len(face) == 4:
        triangles.append([face[0], face[1], face[2]])
        triangles.append([face[2], face[3], face[0]])
    else:
        triangles.append(face)
        
    return triangles


def faceValues(face, mesh, matrix):
    fv = []
    for vert in face.vertices:
        fv.append((matrix * mesh.vertices[vert].co)[:])
        
    return fv


def write_verts(file, faces):
    file.write(struct.pack('>H', len(faces) * 3))
    for face in faces:
        for vert in face:
            file.write(struct.pack('>f', vert[0]) 
                + struct.pack('>f', vert[1]) 
                + struct.pack('>f', vert[2]))


def write_triangles(file, faces):
    file.write(struct.pack('>H', len(faces)))
    for fnum, face in enumerate(faces):
        for vnum, vert in enumerate(face):
            vbase = fnum * 9 + vnum * 3
            file.write(struct.pack('>IIIB', vbase, vbase + 1, vbase + 2, 0))
            
            
def write_texcoords(file, faces):
    file.write(struct.pack('>H', len(faces) * 3))
    for face in faces:
        for vert in face:
            file.write(struct.pack('>fff', vert[0], vert[1]))


def write(filepath):
    scene = bpy.context.scene
    
    faces = []
    for obj in bpy.context.selected_objects:
        me = obj.to_mesh(scene, True, "PREVIEW")
        
        matrix = obj.matrix_world.copy()
        for face in me.tessfaces:
            fv = faceValues(face, me, matrix)
            faces.extend(faceToTriangles(fv))

        bpy.data.meshes.remove(me)
            
    file = open(filepath, 'wb')
    write_verts(file, faces)
    write_triangles(file, faces)
    file.close()
    

#if __name__ == "__main__":
#    register()