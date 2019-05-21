#####
# Addon for Import/Export of .mesh files
# TODO: add a saving option for sol files
#####

import os
import bpy
import mathutils
import colorsys

from bpy.props import (BoolProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    )
from bpy_extras.io_utils import (ImportHelper,
    ExportHelper,
    unpack_list,
    unpack_face_list,
    axis_conversion,
    )

bl_info = {
    "name": "Mesh 3d models (*.mesh)",
    "description": "Imports and exports 3d models triangulations, with triangles references.",
    "author": "Loïc NORGEOT",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "File > Import-Export",
    "warning": "", # used for warning icon and text in addons panel
    "category": "Learnbgame"
}

class ImportMESH(bpy.types.Operator, ImportHelper):
    """Load a .mesh file"""
    bl_idname = "import_mesh.mesh"
    bl_label = "Import MESH mesh"
    filename_ext = ".mesh"
    filter_glob = StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )

    axis_forward = EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='Y',
            )
    axis_up = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Z',
            )

    def execute(self, context):

        keywords = self.as_keywords(ignore=('axis_forward',
            'axis_up',
            'filter_glob',
        ))
        global_matrix = axis_conversion(from_forward=self.axis_forward,
            from_up=self.axis_up,
            ).to_4x4()

        meshes = load(self, context, **keywords)
        if not meshes:
            return {'CANCELLED'}

        scene = context.scene

        objects = []
        for i,m in enumerate(meshes):
            obj = bpy.data.objects.new(m.name, m)
            bpy.ops.object.select_all(action='DESELECT')
            scene.objects.link(obj)
            scene.objects.active = obj
            mat = bpy.data.materials.new(m.name+"_material_"+str(i))
            mat.diffuse_color = colorsys.hsv_to_rgb(float(i/len(meshes)),1,1)
            obj.data.materials.append(mat)
            objects.append(obj)

        scene.update()
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            o.select=True
        bpy.ops.object.join()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.editmode_toggle()
        
        return {'FINISHED'}

class ExportMESH(bpy.types.Operator, ExportHelper):
    """Save a Mesh file"""
    bl_idname = "export_mesh.mesh"
    bl_label = "Export Mesh file"
    filter_glob = StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext = ".mesh"

    axis_forward = EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='Y',
            )
    axis_up = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Z',
            )

    def execute(self, context):
        keywords = self.as_keywords(ignore=('axis_forward',
            'axis_up',
            'filter_glob',
            'check_existing',
        ))
        global_matrix = axis_conversion().to_4x4()
        keywords['global_matrix'] = global_matrix
        return save(self, context, **keywords)

def menu_func_import(self, context):
    self.layout.operator(ImportMESH.bl_idname, text="Mesh format (.mesh)")

def menu_func_export(self, context):
    self.layout.operator(ExportMESH.bl_idname, text="Mesh format (.mesh)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

def load(operator, context, filepath):
    # Parse mesh from MESH file
    filepath = os.fsencode(filepath)
    file = open(filepath, 'r')

    verts,triangles,quads = [],[],[]
    refsT, refsQ = [], []
    nV = nT = nQ = 0
    readVertices = readTriangles = readQuads = False
    iV = iT = iQ = 0

    with open(filepath, 'r') as f:

        for line in f:

            #Vertices reading
            if (readVertices and (nV>0)):
                if(iV<nV):
                    try:
                        px, py, pz = [float(x) for x in line.split()[:3]]
                        id = int(line[3])
                    except ValueError:
                        print(line.split()[:3])
                    iV += 1
                    verts.append((px, py, pz))
                else:
                    readVertices = False

            #Triangles reading
            if (readTriangles and (nT>0)):
                if(iT<nT):
                    try:
                        px, py, pz, r = [int(x)-1 for x in line.split()[:4]]
                    except ValueError:
                        print(line.split()[:3])
                    iT += 1
                    triangles.append((px, py, pz,r))
                    refsT.append(r)
                else:
                    readTriangles = False
    
            #Triangles reading
            if (readQuads and (nQ>0)):
                if(iQ<nQ):
                    try:
                        px, py, pz, pa, r = [int(x)-1 for x in line.split()[:5]]
                    except ValueError:
                        print(line.split()[:4])
                    iQ += 1
                    quads.append((px, py, pz,pa,r))
                    refsQ.append(r)
                else:
                    readQuads = False
    
            #Number recording
            if (readVertices and (nV == 0)):
                nV = int(line.split()[0])
            if (readTriangles and (nT == 0)):
                nT = int(line.split()[0])
            if (readQuads and (nQ == 0)):
                nQ = int(line.split()[0])
        
            #Reading activation
            try:
                if (line.split() == ["Vertices"]):
                    readVertices = True
                if (line.split() == ["Triangles"]):
                    readTriangles = True
                if (line.split() == ["Quadrilaterals"]):
                    readQuads = True
            except:
                print("Aight")

        print("FILE OPENED")
        print("NUMBER OF VERTICES  = ", nV)
        print("NUMBER OF TRIANGLES = ", nT)
        print("NUMBER OF QUADS = ", nQ)

    meshes = []

    REFS = set(refsT+refsQ)
    for i,r in enumerate(REFS):
        refFaces = [t[:-1] for t in triangles+quads if t[-1]==r]
        mesh_name = bpy.path.display_name_from_filepath(filepath)
        mesh = bpy.data.meshes.new(name=mesh_name)
        meshes.append(mesh)
        mesh.from_pydata(verts, [], refFaces)
        mesh.validate()
        mesh.update()

    return meshes


def save(operator, context, filepath, global_matrix = None):
    
    #Get the selected object
    APPLY_MODIFIERS = True
    if global_matrix is None:
        global_matrix = mathutils.Matrix()
    scene = context.scene
    bpy.ops.object.duplicate()
    obj = scene.objects.active

    #Convert the big n-gons in triangles if necessary
    bpy.context.tool_settings.mesh_select_mode=(False,False,True) #optional
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.editmode_toggle()

    #Get the mesh
    mesh = obj.to_mesh(scene, APPLY_MODIFIERS, 'PREVIEW')
    verts = mesh.vertices[:]
    triangles = [ f for f in mesh.polygons if len(f.vertices) == 3 ]
    quads = [ f for f in mesh.polygons if len(f.vertices) == 4 ]

    #Open and write the .mesh file header
    meshFile = os.fsencode(filepath)
    fp = open(meshFile, 'w')
    fp.write('MeshVersionFormatted 1\nDimension 3\n')
    #VERTICES
    fp.write("Vertices\n")
    fp.write(str(len(verts)))
    fp.write("\n")
    for v in verts:
        fp.write(str(v.co[0]) + " " + str(v.co[1]) + " " + str(v.co[2]) + " " + str(0) + "\n")
    #TRIANGLES
    fp.write("Triangles\n")
    fp.write(str(len(triangles))) 
    fp.write("\n")
    for t in triangles:
        for v in t.vertices:
            fp.write(str(v+1))
            fp.write(" ")
        fp.write(str(t.material_index    ))
        fp.write('\n')
    #QUADRILATERALS
    fp.write("Quadrilaterals\n")
    fp.write(str(len(quads)))
    fp.write("\n")
    for t in quads:
        for v in t.vertices:
            fp.write(str(v+1))
            fp.write(" ")
        fp.write(str(t.material_index))
        fp.write('\n')
    fp.close()

    #Solutions according to the weight paint mode (0 to 1 by default)
    vgrp = bpy.context.active_object.vertex_groups.keys()
    #If a vertex group is present
    if(len(vgrp)>0):
        vmin = 0
        vmax = 1
        try:
            T = bpy.context.scene.my_tool
            vmin = T.hmin/100.0 * max(bpy.context.object.dimensions)
            vmax = T.hmax/100.0 * max(bpy.context.object.dimensions)
        except:
            print("The mmg addon is not installed, values set from 0 to 1")
        #Open and write the .sol file
        solFile = filepath[:-5] + ".sol"
        fp = open( os.fsencode(solFile), 'w')
        fp.write("MeshVersionFormatted 2\n")
        fp.write("Dimension 3\n")
        fp.write("SolAtVertices\n")
        fp.write(str(len(verts)))
        fp.write("\n1 1\n")
        GROUP = bpy.context.active_object.vertex_groups.active
        cols = [1.0] * len(verts)
        for i,t in enumerate(triangles):
            for j,v in enumerate(t.vertices):
                try:
                    cols[v] = float(1.0 - GROUP.weight(v))
                except:
                    continue
        for c in cols:
            fp.write('%.8f' % (vmin + c * (vmax-vmin)))
            fp.write("\n")
        fp.close()

    bpy.ops.object.delete()

    return {'FINISHED'}


if __name__ == "__main__":
    register()
