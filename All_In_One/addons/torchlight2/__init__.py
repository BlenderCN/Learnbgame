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
    "name": "Torchlight 2 Importer",
    "author": "pink vertex",
    "version": (0, 2),
    "blender": (2, 78, 0),
    "location": "View3D -> Tools -> Torchlight 2 Tab",
    "description": "Import torchlight 2 mesh and animation files using OGRE command line tools.",
    "category": "Import-Export",
    }

import os
import bpy
import math
from bpy.types import AddonPreferences, Operator, OperatorFileListElement, Panel, Scene
from bpy.props import (BoolProperty, FloatProperty, FloatVectorProperty, IntProperty,
                       StringProperty, EnumProperty, CollectionProperty)

from .import_mesh import MeshConverter
from .import_anim import load_animation
from .import_level_chunk import load_level_chunk
from .utils import get_addon_pref, convert_to_xml, get_bone_order
from .export_anim import write_skeleton
from .export_mesh import (
    write_mesh_weapon,
    write_mesh_wardrobe,
    write_mesh_monster,
    convert_to_mesh)

class IMPORT_MESH_OT_tl2(Operator):
    bl_label = "Import Torchlight2 .MESH"
    bl_idname = "import_mesh.tl2"
    bl_options = {'UNDO'}

    filepath = StringProperty(name="MESH Input File", subtype="FILE_PATH")
    filter_glob = StringProperty(default="*.MESH", options={'HIDDEN'})

    material_path = StringProperty(
        name="MATERIAL Input File",
        subtype="FILE_PATH"
    )

    skeleton_path = StringProperty(
        name="SKELETON Input File",
        description="This option overrides the skeleton linked in the mesh file",
        subtype="FILE_PATH",
        options={"SKIP_SAVE"}
    )

    xml_directory = StringProperty(
        name="XML Output Directory",
        subtype="DIR_PATH"
    )

    create_armature = BoolProperty(
        name="Create Armature",
        default=True
    )

    bone_length_default = FloatProperty(
        name="Default Bone Length",
        default=0.1
    )

    def invoke(self, context, event):
        scene = context.scene
        self.filepath = scene.get("tl2_mesh_file", "")
        self.xml_directory = get_addon_pref(context).xml_output
        self.skeleton_path = scene.get("tl2_skel_file", "")
        self.material_path = scene.get("tl2_mat_file", "")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if (not self.filepath or
            not self.xml_directory):
            self.report({"ERROR_INVALID_INPUT"}, "Missing Path")
            return {'CANCELLED'}

        conv = MeshConverter(
            self.filepath,
            self.xml_directory,
            self.skeleton_path,
            self.material_path)

        mesh_obj, mesh_data = conv.create_mesh()
        if self.create_armature:
            conv.create_armature(self.bone_length_default)

        mesh_data['source_file'] = self.filepath
        return {'FINISHED'}


class IMPORT_ANIM_OT_tl2(Operator):
    bl_label = "Import Torchlight2 Animation"
    bl_idname = "import_anim.tl2"
    bl_options = {'UNDO'}

    directory = StringProperty(
        name="Input Directory",
        subtype="DIR_PATH"
        )

    files = CollectionProperty(
        type=OperatorFileListElement,
        name="SKELETON Input Files"
        )

    filter_glob = StringProperty(
        default="*.SKELETON",
        options={'HIDDEN'}
        )

    xml_directory = StringProperty(
        name="XML Output Directory",
        subtype="DIR_PATH"
        )

    frames_per_second = IntProperty(
        name="FPS",
        default=60
        )

    arma_name = StringProperty(
        name="Armature Object"
        )

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == "ARMATURE")

    def invoke(self, context, event):
        self.arma_name = context.active_object.name
        self.xml_directory = get_addon_pref(context).xml_output
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if (not self.files or
            not self.directory or
            not self.xml_directory):
            self.report({"ERROR_INVALID_INPUT"}, "Missing Path")
            return {'CANCELLED'}

        arma_obj = bpy.data.objects[self.arma_name]

        for fileElem in self.files:
            load_animation(
                os.path.join(self.directory, fileElem.name),
                self.xml_directory,
                self.frames_per_second,
                arma_obj)

        return {'FINISHED'}


def process_for_export(mesh, do_copy=True):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)

    def vec_equals(a, b):
        return (a - b).magnitude < 5e-2

    # split vertices with multiple uv coordinates
    seams = []
    tag_verts = set()
    layer_uv = bm.loops.layers.uv.active

    for edge in bm.edges:
        if not edge.is_manifold: continue

        uvs   = [None] * 2
        loops = [None] * 2

        loops[0] = list(edge.link_loops)
        loops[1] = [loop.link_loop_next for loop in loops[0]]

        for i in range(2):
            uvs[i] = list(map(lambda l: l[layer_uv].uv, loops[i]))

        results = (vec_equals(uvs[0][0], uvs[1][1]),
                   vec_equals(uvs[0][1], uvs[1][0]))

        if not all(results):
            if results[0]: tag_verts.add(loops[0][0].vert)
            if results[1]: tag_verts.add(loops[0][1].vert)
            seams.append(edge)

    tag_verts = list(tag_verts)
    bmesh.ops.split_edges(bm, edges=seams, verts=tag_verts, use_verts=True)

    # triangulate
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
    mesh_export = bpy.data.meshes.new(mesh.name + "_EXPORT") if do_copy else mesh
    bm.to_mesh(mesh_export)
    bm.free()

    return mesh_export

class EXPORT_MESH_OT_tl2weapon(Operator):
    bl_label = "Export Torchlight 2 Weapon MESH"
    bl_idname = "export_mesh.tl2weapon"
    bl_options = set()

    filepath = StringProperty(name="MESH output file", subtype="FILE_PATH")
    filename = StringProperty(name="File Name", default="", subtype="FILE_NAME")

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == "MESH" and
            len(context.active_object.data.uv_layers) == 1 and
            len(context.active_object.data.materials) >  0)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        mesh = context.active_object.data
        mesh_export = process_for_export(mesh, False)

        mesh_output = self.filepath
        xml_output = os.path.join(
            get_addon_pref(context).xml_output,
            self.filename.rsplit(".")[0] + "_EXPORT_MESH.xml")

        xml_stream = open(xml_output, "w")
        write_mesh_weapon(xml_stream, mesh_export)
        convert_to_mesh(xml_output, mesh_output)
        return {'FINISHED'}


class Export_Skinned_Mesh_Base:
    filepath = StringProperty(name="XML output file", subtype="FILE_PATH")
    filename = StringProperty(name="File Name", default="", subtype="FILE_NAME")
    skeletonlink = StringProperty(name="skeletonlink", subtype="FILE_NAME")

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == "MESH" and
            len(context.active_object.data.uv_layers) == 1 and
            len(context.active_object.data.materials) >  0)

    def invoke(self, context, event):
        obj = context.active_object
        self.skeletonlink = obj.get("skeletonlink", obj.name + ".skeleton")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = context.active_object

        if (len(obj.modifiers) > 0 and
            obj.modifiers[0].type == "ARMATURE" and
            obj.modifiers[0].object):

            def list_index(l, i):
                try:               return l.index(i)
                except ValueError: return -1

            arma_obj = obj.modifiers[0].object
            bone_order = get_bone_order(arma_obj.data)
            vgi_to_bi = {vg.index: list_index(bone_order, vg.name) for vg in obj.vertex_groups} # might use list instead of dict if order is guaranteed
        else:
            self.report({'ERROR'}, "No Armature Modifier Found")
            return {'CANCELLED'}

        process_for_export(obj.data, False)

        mesh_output = self.filepath
        xml_output = os.path.join(
            get_addon_pref(context).xml_output,
            self.filename.rsplit(".")[0] + "_EXPORT_MESH.xml")

        xml_stream = open(xml_output, "w")
        self.__class__._write_skinned_mesh(
            xml_stream,
            obj.data,
            vgi_to_bi,
            self.skeletonlink
        )

        convert_to_mesh(xml_output, mesh_output)
        return {'FINISHED'}


class EXPORT_MESH_OT_tl2wardrobe(Export_Skinned_Mesh_Base, Operator):
    bl_label = "Export Torchlight 2 Wardrobe MESH"
    bl_idname = "export_mesh.tl2wardrobe"
    bl_options = set()
    _write_skinned_mesh = write_mesh_wardrobe


class EXPORT_MESH_OT_tl2monster(Export_Skinned_Mesh_Base, Operator):
    bl_label = "Export Torchlight 2 Monster MESH"
    bl_idname = "export_mesh.tl2monster"
    bl_options = set()
    _write_skinned_mesh = write_mesh_monster


class EXPORT_ANIM_OT_tl2anim(Operator):
    bl_label = "Export Torchlight 2 SKELETON Animation"
    bl_idname = "export_anim.tl2anim"
    bl_options = set()

    filepath = StringProperty(name="SKELETON output file", subtype="FILE_PATH")
    filename = StringProperty(name="File Name", default="", subtype="FILE_NAME")
    bind_pose = BoolProperty(name="Bind Pose", default=False, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == "ARMATURE")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = context.active_object
        if not self.bind_pose and (obj.animation_data is None or obj.animation_data.action is None):
            self.report({'ERROR'}, "No action assigned to the armature")
            return {'CANCELLED'}

        skel_output = self.filepath
        xml_output = os.path.join(
            get_addon_pref(context).xml_output,
            self.filename.rsplit(".")[0] + "_EXPORT_ANM.xml")

        xml_stream = open(xml_output, "w")
        write_skeleton(xml_stream, obj, self.bind_pose)
        convert_to_xml(xml_output, skel_output)
        return {'FINISHED'}


class MATERIAL_OT_tl2_assign_wardrobe_textures(Operator):
    bl_label = "Assign wardrobe textures"
    bl_description = "Guess images by name and assign them to the corresponding slots"
    bl_idname = "material.tl2_assign_wardrobe_textures"
    bl_options = set()

    directory = StringProperty(name="Directory", subtype="DIR_PATH",  description="Directory of the file")

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == "MESH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        mat_to_tex = {
            'Chest':     'CHEST',
            'ExChest':   'CHEST',
            'Thighs':    'PANT',
            'MidLeg':    'PANT',
            'Calf':      'BOOT',
            'ExCalf':    'BOOT',
            'Foot':      'BOOT',
            'MidArm':    'CHEST',
            'ExForearm': 'GLOVE',
            'Forearm':   'GLOVE',
            'Hand':      'GLOVE',
            'EXHand':    'GLOVE',
            'Pauldrons': 'EXTRA',
            'Helmet':    'EXTRA'
        }

        textures = tuple(filter(
            lambda f: f.endswith(".PNG"),
            os.listdir(self.directory)
        ))

        mesh = context.active_object.data

        for mat in mesh.materials:
            tex = mat.texture_slots[0].texture
            if tex.image and tex.image.name == "NULL_01.DDS":
                prefixes = "Hum_F", "HuF"
                use_female = any(mat.name.startswith(prefix) for prefix in prefixes)
                tex_prefix = "HUF_" if use_female else "HUM_"
                mat_suffix = mat.name.rsplit("/")[1]
                try:
                    tex_suffix = mat_to_tex[mat_suffix]
                except KeyError:
                    self.report({'WARNING'}, "No texture suffix found for " + mat_suffix)
                    continue

                for tex_file in textures:
                    if ((tex_file.startswith(tex_prefix) or
                         tex_file.startswith("HU_")) and
                        (tex_file.endswith(tex_suffix +  ".PNG") or
                         tex_file.endswith(tex_suffix + "S.PNG"))):

                        tex_filepath = os.path.join(self.directory, tex_file)
                        tex.image = (bpy.data.images.get(tex_file) or
                                     bpy.data.images.load(tex_filepath))
                        break

        return {'FINISHED'}


class MATERIAL_OT_tl2_assign_body_textures(Operator):
    bl_label = "Assign body textures"
    bl_idname = "material.tl2_assign_body_textures"
    bl_options = set()

    multilayer = BoolProperty(name="Multilayered Texture", default=False)
    gender = EnumProperty(name="Gender", items=(
        ("MALE",      "Male",      "", 0),
        ("FEMALE",    "Female",    "", 1)))


    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == "MESH")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, 400, 400)

    def execute(self, context):
        mesh = context.active_object.data
        gender_dir = "HUM_M" if self.gender == "MALE" else "HUM_F"
        tex_file = "BODY.PNG"
        tex_filepath = os.path.join(get_addon_pref(context).tl2_media_dir, "MODELS", "PCS", gender_dir, tex_file)
        img = bpy.data.images.load(tex_filepath, True)

        if self.multilayer:
            tex_body = bpy.data.textures.get("tex_body")
            if tex_body is None:
                tex_body = bpy.data.textures.new("tex_body", "IMAGE")
                tex_body.image = img

        for mat in mesh.materials:
            tex_slot_zero = mat.texture_slots[0]
            tex = tex_slot_zero.texture
            if tex.image and tex.image.name == "NULL_01.DDS":
                tex.image = img

            elif self.multilayer and not tex_slot_zero.use_map_alpha:
                tex_slot_new = mat.texture_slots.add()
                tex_slot_new.texture_coords = "UV"
                tex_slot_new.uv_layer = "UV"
                tex_slot_new.texture = tex_slot_zero.texture
                tex_slot_zero.texture = tex_body

        return {'FINISHED'}


class SCENE_OT_tl2_set_skeleton_path(Operator):
    bl_label = "Set Skeleton Path"
    bl_idname = "scene.tl2_set_skeleton_path"
    bl_options = set()

    gender = EnumProperty(name="Gender", items=(
        ("MALE",      "Male",      "", 0),
        ("FEMALE",    "Female",    "", 1),
        ("CLEAR",     "Clear",     "", 2)))

    def execute(self, context):
        if self.gender == "CLEAR":
            context.scene['tl2_skel_file'] = ""
            return {'FINISHED'}

        gender_dir = "HUM_M" if self.gender == "MALE" else "HUM_F"
        skel_file = gender_dir + ".SKELETON"
        context.scene['tl2_skel_file'] = os.path.join(get_addon_pref(context).tl2_media_dir, "MODELS", "PCS", gender_dir, skel_file)
        return {'FINISHED'}


class IMPORT_SCENE_OT_tl2_import_level_chunk(Operator):
    bl_label = "Import Level Chunk"
    bl_idname = "import_scene.tl2_import_level_chunk"
    bl_options = set()

    xml_path = StringProperty(name="XML Output Directory", subtype="DIR_PATH")
    tl2_path = StringProperty(name="Torchlight 2 Directory", subtype="DIR_PATH")
    filepath = StringProperty(name="Chunk Path",  subtype="FILE_PATH", options={'SKIP_SAVE'})
    filter_glob = StringProperty(default="*.LAYOUT", options={'HIDDEN'})

    def invoke(self, context, event):
        self.xml_path = get_addon_pref(context).xml_output
        self.tl2_path = os.path.dirname(get_addon_pref(context).tl2_media_dir)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not all((self.xml_path, self.tl2_path)):
            return {'CANCELLED'}

        load_level_chunk(
            self.xml_path,
            self.tl2_path,
            os.path.relpath(self.filepath, self.tl2_path)
        )
        return {'FINISHED'}


class PROPERTIES_PT_import_tl2(Panel):
    bl_label = "Torchlight 2 Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Torchlight2"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("import_mesh.tl2", "Import Mesh")
        col.operator("import_anim.tl2", "Import Animation")
        col.operator("export_mesh.tl2weapon",   "Export Weapon Mesh")
        col.operator("export_mesh.tl2wardrobe", "Export Wardrobe Mesh")
        col.operator("export_mesh.tl2monster",  "Export Monster Mesh")
        col.operator("export_anim.tl2anim", "Export Animation")
        col.operator("material.tl2_assign_wardrobe_textures")
        col.operator("material.tl2_assign_body_textures")
        col.operator_menu_enum("scene.tl2_set_skeleton_path", "gender")
        col.operator("import_scene.tl2_import_level_chunk")
        col.alignment = "RIGHT"

        scene = context.scene
        col = self.layout.column(align=True)
        col.prop(scene, "tl2_mesh_file")
        col.prop(scene, "tl2_skel_file")
        col.prop(scene, "tl2_mat_file")
        col.prop(get_addon_pref(context), "xml_output")


class Torchlight2Preferences(AddonPreferences):
    bl_idname = __name__

    tl2_media_dir = StringProperty(name="Torchlight 2 Media Directory", subtype="DIR_PATH")
    ogre_xml_converter = StringProperty(name="Ogre XML Converter", subtype="FILE_PATH")
    xml_output = StringProperty(name="XML Output Directory", subtype="DIR_PATH")
    use_cmd_args = BoolProperty(name="Use Command Line Arguments", default=True)
    cmd_args_mesh_export = StringProperty(
        name="Command Line Arguments",
        description="Command Line Arguments to OgreXMLConverter.exe (1.7.2) for Mesh Export",
        default="-l 0 -e -r"
    )

    def draw(self, context):
        self.layout.prop(self, "tl2_media_dir")
        self.layout.prop(self, "ogre_xml_converter")
        self.layout.prop(self, "xml_output")
        self.layout.prop(self, "use_cmd_args")
        if self.use_cmd_args:
            self.layout.prop(self, "cmd_args_mesh_export")


def register():
    Scene.tl2_mesh_file = StringProperty(name="Mesh File", subtype="FILE_PATH")
    Scene.tl2_skel_file = StringProperty(name="Skeleton File", subtype="FILE_PATH")
    Scene.tl2_mat_file  = StringProperty(name="Material File", subtype="FILE_PATH")

    bpy.utils.register_class(Torchlight2Preferences)
    bpy.utils.register_class(IMPORT_MESH_OT_tl2)
    bpy.utils.register_class(MATERIAL_OT_tl2_assign_wardrobe_textures)
    bpy.utils.register_class(MATERIAL_OT_tl2_assign_body_textures)
    bpy.utils.register_class(SCENE_OT_tl2_set_skeleton_path)
    bpy.utils.register_class(IMPORT_SCENE_OT_tl2_import_level_chunk)
    bpy.utils.register_class(IMPORT_ANIM_OT_tl2)
    bpy.utils.register_class(EXPORT_MESH_OT_tl2weapon)
    bpy.utils.register_class(EXPORT_MESH_OT_tl2wardrobe)
    bpy.utils.register_class(EXPORT_MESH_OT_tl2monster)
    bpy.utils.register_class(EXPORT_ANIM_OT_tl2anim)
    bpy.utils.register_class(PROPERTIES_PT_import_tl2)

def unregister():
    bpy.utils.unregister_class(PROPERTIES_PT_import_tl2)
    bpy.utils.unregister_class(IMPORT_MESH_OT_tl2)
    bpy.utils.unregister_class(MATERIAL_OT_tl2_assign_wardrobe_textures)
    bpy.utils.unregister_class(MATERIAL_OT_tl2_assign_body_textures)
    bpy.utils.unregister_class(SCENE_OT_tl2_set_skeleton_path)
    bpy.utils.unregister_class(IMPORT_SCENE_OT_tl2_import_level_chunk)
    bpy.utils.unregister_class(IMPORT_ANIM_OT_tl2)
    bpy.utils.unregister_class(EXPORT_MESH_OT_tl2weapon)
    bpy.utils.unregister_class(EXPORT_MESH_OT_tl2wardrobe)
    bpy.utils.unregister_class(EXPORT_MESH_OT_tl2monster)
    bpy.utils.unregister_class(EXPORT_ANIM_OT_tl2anim)
    bpy.utils.unregister_class(Torchlight2Preferences)

    del Scene.tl2_mesh_file
    del Scene.tl2_skel_file
    del Scene.tl2_mat_file
