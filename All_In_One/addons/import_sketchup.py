
bl_info = {
    "name": "SketchUp Collada and KMZ format",
    "author": "Heikki Salo",
    "version": (1, 0, 4),
    "blender": (2, 70, 0),
    "location": "File > Import-Export",
    "description": "Import SketchUp .dae and .kmz files",
    "category": "Import-Export"
}

import bpy
import mathutils
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

import zipfile
import shutil
import os

DUPLICATE_THRESHOLD = 0.0001
RENAME_UV_MAP_NAME = "imported_map"

def cleanup_kmz(temp_dir):
    #Ignore all file related errors
    try:
        shutil.rmtree(temp_dir)
    except:
        pass

    try:
        os.mkdir(temp_dir)
    except:
        pass

def extract_kmz(filepath, target):
    kmz = zipfile.ZipFile(filepath)
    kmz.extractall(target)

def find_collada(temp_dir):
    for root, dirs, files in os.walk(temp_dir):
        for name in files:
            if name.lower().endswith(".dae"):
                return os.path.join(root, name)
    return "NOT_FOUND"

def get_images():
    return set(bpy.data.images[:])

def get_imported_objects(context):
    #Collada importer leaves imported objects selected
    return [m for m in context.selected_objects]

def filter_objects(objects, tp):
    return [obj for obj in objects if obj.type == tp]

def pack_loaded_images(old_images):
    new_images = get_images()
    for img in new_images:
        if img not in old_images:
            img.pack()

def create_ktree(mesh):
    size = len(mesh.data.vertices)
    kdt = mathutils.kdtree.KDTree(size)
    for v in mesh.data.vertices:
        kdt.insert(v.co, v.index)
    kdt.balance()
    return kdt

def find_vertex_duplicate_faces(mesh, kdt, face):
    matches = set()
    for i in face.vertices:
        for (co, index, dist) in kdt.find_range(mesh.data.vertices[i].co, DUPLICATE_THRESHOLD):
            if index != i:
                matches.add(index)

    results = []
    if len(matches) > 0:
        for poly in mesh.data.polygons:
            if poly.index != face.index and matches.issuperset(poly.vertices):
                #Both faces share vertex locations so there might be z-fighting.
                results.append(poly.index)

    return results

def find_duplicate_faces(mesh, fix_duplicate_vertices):
    kdt = None
    if fix_duplicate_vertices:
        kdt = create_ktree(mesh)

    found = {}
    for face in mesh.data.polygons:
        facevertsorted = str(sorted(face.vertices[:]))
        if facevertsorted in found:
            found[facevertsorted].append(face.index)
        else:
            found[facevertsorted] = [face.index]

        if fix_duplicate_vertices:
            found[facevertsorted].extend(find_vertex_duplicate_faces(mesh, kdt, face))

    results = {}
    for k, v in found.items():
        if len(v) > 1:
            results[k] = v

    return results

def find_best_face(mesh, indices):
    best = indices[1]
    for index in indices:
        mat = mesh.data.materials[mesh.data.polygons[index].material_index]
        if mat and mat.active_texture:
            #Prefer textured faces
            best = index
            break

    return best

def fix_models(context, models, fix_duplicate_vertices, validate_models):
    for i, obj in enumerate(models):
        print("Processing object %i of %i" % (i + 1, len(models)))

        if validate_models and obj.data.validate():
            print("Invalid mesh validated: %s" % obj.name)

        context.scene.objects.active = obj #Make obj active to do operations on it
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False) #Set 3D View to Object Mode (probably redundant)
        bpy.ops.object.mode_set(mode="EDIT", toggle=False) #Set 3D View to Edit Mode
        context.tool_settings.mesh_select_mode = [False, False, True] #Set to face select in 3D View Editor
        bpy.ops.mesh.select_all(action="DESELECT") #Make sure all faces in mesh are unselected
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False) #You have to be in object mode to select faces

        duplicates = find_duplicate_faces(obj, fix_duplicate_vertices)
        for face in duplicates:
            indices = duplicates[face]
            for index in indices:
                obj.data.polygons[index].select = True

            #Save the best face
            obj.data.polygons[find_best_face(obj, indices)].select = False

        bpy.ops.object.mode_set(mode="EDIT", toggle=False)      #Set to Edit Mode AGAIN
        bpy.ops.mesh.delete(type="FACE")                        #Delete double faces
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)      #Recalculate normals
        bpy.ops.mesh.remove_doubles(threshold=DUPLICATE_THRESHOLD, use_unselected=False) #Remove doubles
        bpy.ops.mesh.normals_make_consistent(inside=False)      #Recalculate normals (this one or two lines above is redundant)
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)    #Set to Object Mode AGAIN

def rename_uv_texture_maps(models, name):
    for m in models:
        for uv in m.data.uv_textures:
            #Usually there should only be one
            uv.name = name
            break

def reparent(context, models, root_name):
    mesh = bpy.data.meshes.new("Placeholder")
    root = bpy.data.objects.new(root_name, mesh)
    context.scene.objects.link(root)

    for obj in models:
        if not obj.parent:
            obj.parent = root

def import_collada(path):
    bpy.ops.wm.collada_import(filepath=path)

def load(operator, context, **args):
    filepath = args["filepath"]
    fix_duplicate_faces = args["fix_duplicate_faces"]
    fix_duplicate_vertices = args["fix_duplicate_vertices"]
    validate_models = args["validate_models"]
    add_parent = args["add_parent"]
    rename_uvs = args["rename_uvs"]
    pack_images = args["pack_images"]

    name = os.path.split(filepath)[-1].split(".")[0]
    parts = os.path.splitext(filepath)
    ext = parts[1].lower()

    old_images = get_images()

    if ext == ".kmz":
        #Extract archive contents into a directory
        temp_dir = os.path.join(*parts[:-1])

        cleanup_kmz(temp_dir)
        extract_kmz(filepath, temp_dir)
        import_collada(find_collada(temp_dir))
    elif ext == ".dae":
        import_collada(filepath)
    else:
        raise RuntimeError("Unknown extension: %s" % ext)

    objects = get_imported_objects(context)
    models = filter_objects(objects, "MESH")

    if rename_uvs:
        rename_uv_texture_maps(models, RENAME_UV_MAP_NAME)

    if fix_duplicate_faces:
        fix_models(context, models, fix_duplicate_vertices, validate_models)

    if pack_images:
        pack_loaded_images(old_images)

    if add_parent:
        reparent(context, objects, name)

    return {"FINISHED"}


class ImportSketchUp(bpy.types.Operator, ImportHelper):
    """Load a Google SketchUp .dae or .kmz file"""
    bl_idname = "import_scene.sketchup"
    bl_label = "Import"
    bl_options = {"PRESET", "UNDO"}

    filename_ext = ".kmz"
    filter_glob = StringProperty(
            default="*.kmz;*.dae",
            options={"HIDDEN"})

    fix_duplicate_faces = BoolProperty(
            name="Fix duplicate faces",
            description="Remove duplicate faces from imported objects. Can be slow.",
            default=True)

    fix_duplicate_vertices = BoolProperty(
            name="Fix duplicate vertices (SLOW)",
            description="Remove duplicate vertices from imported objects.",
            default=False)

    validate_models = BoolProperty(
            name="Validate models",
            description="Validate imported models to make sure they are sane",
            default=False)

    add_parent = BoolProperty(
            name="Add a parent object",
            description="Add a parent root object for imported objects.",
            default=True)

    rename_uvs = BoolProperty(
            name="Rename UV maps",
            description="Renames UV maps for better join functionality.",
            default=True)

    pack_images = BoolProperty(
            name="Pack images",
            description="Pack imported images into the .blend file.",
            default=True)

    def execute(self, context):
        keywords = self.as_keywords()
        return load(self, context, **keywords)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "fix_duplicate_faces")

        row = col.row()
        row.enabled = self.fix_duplicate_faces
        row.prop(self, "fix_duplicate_vertices")

        row = col.row()
        row.enabled = self.fix_duplicate_faces
        row.prop(self, "validate_models")

        col.prop(self, "add_parent")
        col.prop(self, "rename_uvs")
        col.prop(self, "pack_images")

def menu_func_import(self, context):
    self.layout.operator(ImportSketchUp.bl_idname, text="SketchUp (.kmz/.dae)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
