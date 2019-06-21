#!BPY
# -*- coding: utf-8 -*-

import os.path
from math import radians
import bpy, mathutils
from bpy_extras.io_utils import ImportHelper
from . import valkyria

bl_info = {
        "name": "Valkyria Chronicles (.MLX, .HMD, .ABR, .MXE)",
        "description": "Imports model files from Valkyria Chronicles (PS3)",
        "author": "Chrrox, Gomtuu",
        "version": (0, 8),
        "blender": (2, 74, 0),
        "location": "File > Import",
        "warning": "",
        "category": "Learnbgame",
        }


def make_transform_matrix(loc,rot,scale):
    mat_loc = mathutils.Matrix.Translation(loc)
    mat_rot = mathutils.Quaternion(rot).to_matrix().to_4x4()
    mat_scale = mathutils.Matrix()
    mat_scale[0][0], mat_scale[1][1], mat_scale[2][2] = scale[0], scale[1], scale[2]
    return mat_loc * mat_rot * mat_scale


class Texture_Pack:
    def __init__(self):
        self.htsf_images = []
        self.blender_built = False

    def add_image(self, htsf, filename):
        image = HTSF_Image(htsf)
        image.filename = filename + ".dds"
        self.htsf_images.append(image)
        return image

    def build_blender(self):
        for image in self.htsf_images:
            image.build_blender()
        self.blender_built = True


class HTEX_Pack:
    def __init__(self, source_file, htex_id):
        self.F = source_file
        self.htex_id = htex_id
        self.htsf_images = []
        self.blender_built = False

    def add_image(self, htsf):
        htsf_id = len(self.htsf_images)
        image = HTSF_Image(htsf)
        image.filename = "HTEX-{:03}-HTSF-{:03}.dds".format(self.htex_id, htsf_id)
        self.htsf_images.append(image)
        return image

    def read_data(self):
        for htsf in self.F.HTSF:
            image = self.add_image(htsf)
            image.read_data()

    def build_blender(self):
        for image in self.htsf_images:
            image.build_blender()
        self.blender_built = True


class HTSF_Image:
    def __init__(self, source_file):
        self.F = source_file
        assert len(self.F.DDS) == 1
        self.dds = self.F.DDS[0]
        self.dds_data = None

    def write_tmp_dds(self, dds_path):
        tmp_dds = open(dds_path, 'wb')
        tmp_dds.write(self.dds.data)
        tmp_dds.close()

    def convert_dds_to_png(self, dds_path):
        from bpy_extras.image_utils import load_image
        import platform
        import pathlib
        import subprocess
        png_path = dds_path[0:-4] + '.png'
        home = pathlib.Path.home()
        current_os = platform.system()
        if current_os == 'Linux':
            converter = home / 'Compressonator' / 'CompressonatorCLI'
            command = ['sh', str(converter), '-fs', 'BC7', dds_path, png_path]
        if current_os == 'Darwin':
            converter = home / 'Compressonator' / 'CompressonatorCLI.sh'
            command = ['sh', str(converter), '-fs', 'BC7', dds_path, png_path]
        if current_os == 'Windows':
            converter = home / 'texconv' / 'texconv.exe'
            dds_folder = pathlib.Path(dds_path).parent
            command = [str(converter), '-ft', 'png', '-o', str(dds_folder), dds_path]
            png_path = dds_path[0:-4] + '.PNG'
        subprocess.run(command)
        self.image = load_image(png_path)
        self.image.pack()
        os.remove(png_path)

    def build_blender(self):
        from bpy_extras.image_utils import load_image
        tempdir = bpy.app.tempdir
        dds_path = os.path.join(tempdir, self.filename)
        self.write_tmp_dds(dds_path)
        self.image = load_image(dds_path)
        supported = self.image.size[0] > 0 or self.image.size[1] > 0
        self.image.pack()
        if not supported:
            # DDS file is probably BC7, which Blender doesn't support yet.
            self.convert_dds_to_png(dds_path)
        os.remove(dds_path)

    def read_data(self):
        self.dds.read_data()


class MXTL_List:
    def __init__(self, source_file):
        self.F = source_file
        self.texture_packs = []

    def read_data(self):
        self.F.read_data()
        self.texture_lists = self.F.texture_lists


class IZCA_Model:
    def __init__(self, source_file):
        self.F = source_file
        self.texture_packs = []
        self.shape_key_sets = []
        self.hmdl_models = []

    def add_hshp(self, hshp):
        hshp_id = len(self.shape_key_sets)
        shape_key_set = HSHP_Key_Set(hshp, hshp_id)
        self.shape_key_sets.append(shape_key_set)
        return shape_key_set

    def add_htex(self, htex):
        htex_id = len(self.texture_packs)
        htex_pack = HTEX_Pack(htex, htex_id)
        self.texture_packs.append(htex_pack)
        return htex_pack

    def add_model(self, hmdl):
        model_id = len(self.hmdl_models)
        model = HMDL_Model(hmdl, model_id)
        self.hmdl_models.append(model)
        return model

    def read_data(self):
        if hasattr(self.F, 'HSHP'):
            for hshp in self.F.HSHP:
                shape_key_set = self.add_hshp(hshp)
                shape_key_set.read_data()
        if getattr(self.F, 'MXTL', False):
            # read HMDL/HTSF associations from MXTL
            mxtl = MXTL_List(self.F.MXTL[0])
            mxtl.read_data()
            for model_i, texture_list in enumerate(mxtl.texture_lists):
                texture_pack = Texture_Pack()
                for htsf_i, filename in texture_list:
                    htsf = texture_pack.add_image(self.F.HTSF[htsf_i], filename)
                    htsf.read_data()
                self.texture_packs.append(texture_pack)
                model = self.add_model(self.F.HMDL[model_i])
                model.read_data()
        else:
            # deduce HMDL/HTEX associations
            for hmd, htx in zip(self.F.HMDL, self.F.HTEX):
                htex_pack = self.add_htex(htx)
                htex_pack.read_data()
                model = self.add_model(hmd)
                model.read_data()

    def build_blender(self):
        for texture_pack, model in zip(self.texture_packs, self.hmdl_models):
            texture_pack.build_blender()
            model.build_blender()
            model.assign_materials(texture_pack.htsf_images)
        for shape_key_set in self.shape_key_sets:
            # TODO: Is there a smarter way to determine which models use shape keys?
            self.hmdl_models[1].build_shape_keys(shape_key_set)

    def finalize_blender(self):
        for model in self.hmdl_models:
            model.finalize_blender()


class IZCA_Poses:
    def __init__(self, source_file):
        self.F = source_file
        self.poses = []

    def read_data(self):
        for hmot in self.F.HMOT:
            hmot.read_data()
            self.poses.append(hmot.bones)

    def pose_from_armature(self, arm, posed_arm):
        # Needs to run multiple times within script window?
        # Even then, bones are rolled incorrectly.
        for bone in arm.pose.bones:
            posed_bone = posed_arm.data.bones[bone.name]
            #posed_vector = posed_bone.tail - posed_bone.head
            #vector = bone.tail - bone.head
            #bone.rotation_quaternion = vector.rotation_difference(posed_vector)
            #bone.rotation_mode = 'QUATERNION'
            bone.matrix = posed_bone.matrix_local

    def pose_model(self, izca_model):
        hmdl = izca_model.hmdl_models[0]
        kfmd = hmdl.kfmd_models[0]
        #i = 0
        for bone in kfmd.bones:
            bone["orig_location"] = bone["location"]
            bone["orig_rotation"] = bone["rotation"]
            bone["orig_scale"] = bone.get("scale", (1, 1, 1))
        for pose_bones in self.poses:
            #j = 0
            for bone, pose_bone in zip(kfmd.bones, pose_bones):
                #print("{:02x} Orig:".format(i), bone["location"], bone["rotation"])
                if "location" not in pose_bone:
                    pose_bone["location"] = None
                if "rotation" not in pose_bone:
                    pose_bone["rotation"] = None
                if "scale" not in pose_bone:
                    pose_bone["scale"] = None
                if pose_bone["location"]:
                    bone["location"] = tuple(map(sum, zip(pose_bone["location"], pose_bone["location_frames"][0])))
                if pose_bone["rotation"]:
                    bone["rotation"] = tuple(map(sum, zip(pose_bone["rotation"], pose_bone["rotation_frames"][0])))
                if pose_bone["scale"]:
                    bone["scale"] = tuple(map(sum, zip(pose_bone["scale"], pose_bone["scale_frames"][0])))
                #print("Pose {:02x} Bone {:02x}:".format(i, j), bone["location"], bone["rotation"], bone["scale"])
                #j += 1
            armature = hmdl.kfmd_models[0].build_armature()
            #i += 1
            #armature.location = ((i % 16) * 10, int(i / 16) * -20, 0)
            #self.pose_from_armature(kfmd.armature, armature)
            for bone in kfmd.bones:
                bone["location"] = bone["orig_location"]
                bone["rotation"] = bone["orig_rotation"]
                bone["scale"] = bone.get("orig_scale", (1, 1, 1))
            break


class ABRS_Model:
    def __init__(self, source_file):
        self.F = source_file
        self.texture_packs = []
        self.hmdl_models = []

    def add_model(self, hmdl):
        model_id = len(self.hmdl_models)
        model = HMDL_Model(hmdl, model_id)
        self.hmdl_models.append(model)
        return model

    def read_data(self):
        texture_pack = None
        htex_count = 0
        for inner_file in self.F.inner_files:
            if inner_file.ftype == 'HMDL':
                model = self.add_model(inner_file)
                model.read_data()
                texture_pack = Texture_Pack()
                self.texture_packs.append(texture_pack)
            elif inner_file.ftype == 'HTEX':
                if texture_pack:
                    htex_pack = HTEX_Pack(inner_file, htex_count)
                    htex_pack.read_data()
                    for htsf in htex_pack.htsf_images:
                        texture_pack.htsf_images.append(htsf)
                htex_count += 1
        assert len(self.texture_packs) == len(self.hmdl_models)

    def build_blender(self):
        for texture_pack, model in zip(self.texture_packs, self.hmdl_models):
            texture_pack.build_blender()
            model.build_blender()
            model.assign_materials(texture_pack.htsf_images)

    def finalize_blender(self):
        for model in self.hmdl_models:
            model.finalize_blender()


class MXEN_Model:
    # TODO: EV_OBJ_026.MXE causes vertex group error
    def __init__(self, source_file):
        self.F = source_file
        self.texture_packs = []
        self.hmdl_models = []
        self.instances = []

    def add_htex(self, htex):
        htex_id = len(self.texture_packs)
        htex_pack = HTEX_Pack(htex, htex_id)
        self.texture_packs.append(htex_pack)
        return htex_pack

    def add_model(self, hmdl):
        model_id = len(self.hmdl_models)
        model = HMDL_Model(hmdl, model_id)
        self.hmdl_models.append(model)
        return model

    def open_file(self, filename):
        path = os.path.dirname(self.F.filename)
        possible_files = []
        possible_files.append(os.path.join(path, filename))
        possible_files.append(os.path.join(path, filename.lower()))
        possible_files.append(os.path.join(path, filename.upper()))
        possible_files.append(os.path.join(path, '..', 'resource', 'mx', filename.lower()))
        possible_files.append(os.path.join(path, '..', 'resource', 'mx', filename.upper()))
        opened_file = None
        for model_filepath in possible_files:
            try:
                opened_file = valkyria.files.valk_open(model_filepath)[0]
            except FileNotFoundError:
                pass
        if opened_file is None:
            raise FileNotFoundError(filename)
        return opened_file

    def read_data(self):
        mxec = self.F.MXEC[0]
        mxec.read_data()
        if hasattr(mxec, "mmf_file"):
            mmf = self.open_file(mxec.mmf_file["filename"])
            mmf.find_inner_files()
            mmf.read_data()
        if hasattr(mxec, "htr_file"):
            htr = self.open_file(mxec.htr_file["filename"])
            htr.read_data()
        if hasattr(mxec, "merge_htx_file"):
            merge_htx = self.open_file(mxec.merge_htx_file["filename"])
            merge_htx.find_inner_files()
        model_cache = {}
        texture_cache = {}
        for mxec_model in mxec.models:
            if not "model_file" in mxec_model:
                continue
            model_file_desc = mxec_model["model_file"]
            print("Reading", model_file_desc["filename"])
            model = model_cache.get(model_file_desc["filename"], None)
            if model is None:
                if model_file_desc["is_inside"] == 0:
                    hmd = self.open_file(model_file_desc["filename"])
                    hmd.find_inner_files()
                    model = self.add_model(hmd)
                    model.read_data()
                elif model_file_desc["is_inside"] == 0x200:
                    hmd = mmf.named_models[model_file_desc["filename"]]
                    model = self.add_model(hmd)
                    model.read_data()
                model_cache[model_file_desc["filename"]] = model
                model.mxec_filename = model_file_desc["filename"]
            else:
                self.hmdl_models.append(model)
            self.instances.append((
                mathutils.Vector((mxec_model["location_x"], mxec_model["location_y"], mxec_model["location_z"])),
                mathutils.Vector((radians(mxec_model["rotation_x"]), radians(mxec_model["rotation_y"]), radians(mxec_model["rotation_z"]))),
                (mxec_model["scale_x"], mxec_model["scale_y"], mxec_model["scale_z"])
                ))
            texture_file_desc = mxec_model["texture_file"]
            texture_pack = texture_cache.get(texture_file_desc["filename"])
            if texture_pack is None:
                if texture_file_desc["is_inside"] == 0:
                    htx = self.open_file(texture_file_desc["filename"])
                    htx.find_inner_files()
                    texture_pack = self.add_htex(htx)
                    texture_pack.read_data()
                elif texture_file_desc["is_inside"] == 0x100:
                    texture_pack = Texture_Pack()
                    for htsf_i in htr.texture_packs[texture_file_desc["htr_index"]]["htsf_ids"]:
                        texture_filename = "{}-{:03d}".format(texture_file_desc["filename"], htsf_i)
                        htsf = texture_pack.add_image(merge_htx.HTSF[htsf_i], texture_filename)
                        htsf.read_data()
                    self.texture_packs.append(texture_pack)
                texture_cache[texture_file_desc["filename"]] = texture_pack
            else:
                self.texture_packs.append(texture_pack)

    def build_blender(self):
        for texture_pack, model, instance_info in zip(self.texture_packs, self.hmdl_models, self.instances):
            if texture_pack.blender_built:
                pass
            else:
                texture_pack.build_blender()
            if model.empty:
                # Model has already been built and has an "empty" object
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = model.empty
                model.empty.select = True
                bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
                bpy.ops.object.duplicate(linked=True)
                instance = bpy.context.scene.objects.active
            else:
                model.build_blender()
                model.empty.name = model.mxec_filename
                model.assign_materials(texture_pack.htsf_images)
                instance = model.empty
            instance.location = instance_info[0]
            instance.rotation_mode = 'XYZ'
            instance.rotation_euler = instance_info[1]
            instance.scale = instance_info[2]

    def finalize_blender(self):
        for model in self.hmdl_models:
            model.finalize_blender()


class HSHP_Key_Set:
    def __init__(self, source_file, shape_key_set_id):
        self.F = source_file
        self.shape_key_set_id = shape_key_set_id

    def read_data(self):
        self.F.read_data()
        self.shape_keys = self.F.shape_keys


class HMDL_Model:
    def __init__(self, source_file, model_id):
        self.F = source_file
        self.model_id = model_id
        self.kfmd_models = []
        self.empty = None

    def add_model(self, kfmd):
        model_id = len(self.kfmd_models)
        model = KFMD_Model(kfmd, model_id)
        self.kfmd_models.append(model)
        return model

    def read_data(self):
        for kfmd in self.F.KFMD:
            model = self.add_model(kfmd)
            model.read_data()

    def build_blender(self):
        self.empty = bpy.data.objects.new("HMDL-{:03d}".format(self.model_id), None)
        bpy.context.scene.objects.link(self.empty)
        for model in self.kfmd_models:
            model.build_blender()
            model.empty.parent = self.empty

    def assign_materials(self, texture_pack):
        for model in self.kfmd_models:
            model.build_materials(texture_pack)
            model.assign_materials()

    def build_shape_keys(self, shape_key_set):
        # TODO: Is there a smarter way to determine which models use shape keys?
        self.kfmd_models[0].build_shape_keys(shape_key_set)

    def finalize_blender(self):
        for model in self.kfmd_models:
            model.finalize_blender()


class KFMD_Model:
    def __init__(self, source_file, model_id):
        self.F = source_file
        self.model_id = model_id
        self.kfms = self.F.KFMS[0]
        self.kfmg = self.F.KFMG[0]
        self.empty = None
        self.oneside = None

    def build_armature(self):
        armature = bpy.data.objects.new("Armature",
            bpy.data.armatures.new("ArmatureData"))
        scene = bpy.context.scene
        scene.objects.link(armature)
        scene.objects.active = armature
        armature.select = True
        bpy.ops.object.mode_set(mode = 'EDIT')
        for bone in self.bones:
            if 'deform_id' in bone:
                bone['name'] = "Bone-{:02x}".format(bone['deform_id'])
            else:
                bone['name'] = "Bone-{:02x}".format(bone['id'])
            bone["matrix"] = make_transform_matrix(bone["location"], bone["rotation"], bone["scale"])
            if bone["parent"]:
                bone["accum_matrix"] = bone["parent"]["accum_matrix"]
                bone["head"] = bone["accum_matrix"] * mathutils.Vector(bone["location"])
                bone["accum_matrix"] = bone["accum_matrix"] * bone["matrix"]
            else:
                bone["accum_matrix"] = bone["matrix"]
                bone["head"] = mathutils.Vector(bone["location"])
        for bone in self.bones:
            if bone["fav_child"]:
                bone["tail"] = bone["fav_child"]["head"]
            else:
                bone["tail"] = bone["accum_matrix"] * mathutils.Vector((0.5, 0, 0))
            if bone["object_ptr1"] and bone["parent"]:
                bone["tail"] = bone["head"]
                bone["head"] = bone["parent"]["head"]
            bone["edit_bpy"] = armature.data.edit_bones.new(bone["name"])
            bone["edit_bpy"].use_connect = False
            if bone["parent"]:
                bone["edit_bpy"].parent = bone["parent"]["edit_bpy"]
            bone["edit_bpy"].head = bone["head"]
            bone["edit_bpy"].tail = bone["tail"]
        bpy.ops.object.mode_set(mode = 'OBJECT')
        return armature

    def build_meshes(self):
        for i, mesh_dict in enumerate(self.meshes):
            # Create mesh object
            mesh = bpy.data.meshes.new("MeshData-{:03d}".format(i))
            mesh_dict["bpy"] = bpy.data.objects.new("Mesh-{:03d}".format(i), mesh)
            bpy.context.scene.objects.link(mesh_dict['bpy'])
            mesh_dict["bpy"].parent = self.armature
            # Create vertices
            mesh.vertices.add(len(mesh_dict['vertices']))
            vertex_array = []
            for vertex in mesh_dict["vertices"]:
                vertex_array.append(vertex["location_x"])
                vertex_array.append(vertex["location_y"])
                vertex_array.append(vertex["location_z"])
            mesh.vertices.foreach_set("co", vertex_array)
            # Create faces
            face_count = len(mesh_dict["faces"])
            mesh.tessfaces.add(face_count)
            face_array = []
            for face in mesh_dict["faces"]:
                face_array.extend(face)
            mesh.tessfaces.foreach_set("vertices_raw", face_array)
            mesh.update()
            # Move accessories to proper places
            parent_bone_id = mesh_dict["object"]["parent_bone_id"]
            parent_bone = self.bones[parent_bone_id]
            if parent_bone["name"] in self.armature.data.bones:
                bone = self.armature.data.bones[parent_bone["name"]]
                bone_matrix = bone.matrix_local * mathutils.Matrix.Translation((0,bone.length,0))
                mesh_dict["bpy"].parent_type = 'BONE'
                mesh_dict["bpy"].parent_bone = parent_bone["name"]
                mesh_dict["bpy"].matrix_parent_inverse = bone_matrix.inverted() * parent_bone["accum_matrix"]
            # Reparent meshes that have vertex groups back to the armature
            if mesh_dict["object"]["parent_is_armature"]:
                bpy.ops.object.select_all(action='DESELECT')
                mesh_dict["bpy"].select = True
                bpy.context.scene.objects.active = self.armature
                bpy.ops.object.parent_set(type='ARMATURE', keep_transform=True)

    def assign_vertex_groups(self):
        for mesh in self.meshes:
            for local_id, vertex_list in mesh["vertex_groups"].items():
                global_id = mesh["vertex_group_map"][local_id]
                vgroup_name = "Bone-{:02x}".format(global_id)
                if vgroup_name in mesh["bpy"].vertex_groups:
                    vgroup = mesh["bpy"].vertex_groups[vgroup_name]
                else:
                    vgroup = mesh["bpy"].vertex_groups.new(vgroup_name)
                for vertex_id, weight in vertex_list:
                    vgroup.add([vertex_id], weight, 'ADD')

    def build_blender(self):
        self.empty = bpy.data.objects.new("KFMD-{:03d}".format(self.model_id), None)
        bpy.context.scene.objects.link(self.empty)
        self.armature = self.build_armature()
        self.armature.parent = self.empty
        self.build_meshes()
        self.assign_vertex_groups()

    def index_vertex_groups(self):
        # TODO: This function and assign_vertex_groups might be a little
        # excessive. Consider doing this all directly when building the mesh.
        for mesh in self.meshes:
            vertex_groups = {}
            for i, vertex in enumerate(mesh["vertices"]):
                if "vertex_group_1" in vertex:
                    if vertex["vertex_group_1"] not in vertex_groups:
                        vertex_groups[vertex["vertex_group_1"]] = []
                    vertex_groups[vertex["vertex_group_1"]].append([i, vertex["vertex_group_weight_1"]])
                if "vertex_group_2" in vertex:
                    if vertex["vertex_group_2"] not in vertex_groups:
                        vertex_groups[vertex["vertex_group_2"]] = []
                    vertex_groups[vertex["vertex_group_2"]].append([i, vertex["vertex_group_weight_2"]])
                if "vertex_group_3" in vertex:
                    if vertex["vertex_group_3"] not in vertex_groups:
                        vertex_groups[vertex["vertex_group_3"]] = []
                    vertex_groups[vertex["vertex_group_3"]].append([i, vertex["vertex_group_weight_3"]])
            mesh["vertex_groups"] = vertex_groups

    def read_data(self):
        self.F.read_data()
        self.bones = self.F.bones
        self.materials = self.F.materials
        self.meshes = self.F.meshes
        self.textures = self.F.textures
        self.index_vertex_groups()

    def create_oneside(self):
        self.oneside = bpy.data.textures.new("OneSide", type='BLEND')
        self.oneside.use_color_ramp = True
        self.oneside.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        self.oneside.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        element0 = self.oneside.color_ramp.elements.new(0.5)
        element0.color = (0.0, 0.0, 0.0, 1.0)
        element1 = self.oneside.color_ramp.elements.new(0.501)
        element1.color = (1.0, 1.0, 1.0, 1.0)

    def build_materials(self, texture_pack):
        if self.kfms.vc_game == 1:
            self.build_materials_old(texture_pack)
        elif self.kfms.vc_game == 4:
            self.build_materials_new(texture_pack)

    def build_materials_new(self, texture_pack):
        for ptr, texture_dict in self.textures.items():
            name = "Texture-{:04x}".format(ptr)
            texture_dict["bpy"] = bpy.data.textures.new(name, type = 'IMAGE')
            texture_dict["bpy"].image = texture_pack[texture_dict["image"]].image
            texture_dict["bpy"].use_alpha = True
        for ptr, material_dict in self.materials.items():
            name = "Material-{:04x}".format(ptr)
            material_dict["bpy"] = material = bpy.data.materials.new(name)
            #material.game_settings.use_backface_culling = material_dict["use_backface_culling"]
            material.diffuse_intensity = 1.0
            material.specular_intensity = 0.0
            if material_dict["texture0_ptr"]:
                slot0 = material.texture_slots.add()
                slot0.texture_coords = 'UV'
                slot0.texture = material_dict["texture0"]["bpy"]
                slot0.use_map_alpha = True
                slot0.alpha_factor = 1.0
            if material_dict["use_transparency"]:
                material.use_transparency = True
                material.transparency_method = 'Z_TRANSPARENCY'
                material.alpha = 0.0
            if material_dict["texture1_ptr"]:
                slot1 = material.texture_slots.add()
                slot1.texture_coords = 'UV'
                slot1.texture = material_dict["texture1"]["bpy"]
            if material_dict["texture2_ptr"]:
                slot2 = material.texture_slots.add()
                slot2.texture_coords = 'UV'
                slot2.texture = material_dict["texture2"]["bpy"]
            if material_dict["texture3_ptr"]:
                slot3 = material.texture_slots.add()
                slot3.texture_coords = 'UV'
                slot3.texture = material_dict["texture3"]["bpy"]
                # This texture slot is (almost?) always used to add shading
                # to a character's eyeball. The texture needs to be multiplied
                # instead of mixed for the shading to look right.
                slot3.blend_type = 'MULTIPLY'
            if material_dict["texture4_ptr"]:
                slot4 = material.texture_slots.add()
                slot4.texture_coords = 'UV'
                slot4.texture = material_dict["texture4"]["bpy"]
            if material_dict["use_backface_culling"]:
                material.use_nodes = True
                material.use_transparency = True
                nodes = material.node_tree.nodes
                nodes['Material'].material = material
                geom = nodes.new('ShaderNodeGeometry')
                math = nodes.new('ShaderNodeMath')
                math.operation = 'MULTIPLY'
                material.node_tree.links.new(nodes['Material'].outputs['Alpha'], math.inputs[0])
                material.node_tree.links.new(geom.outputs['Front/Back'], math.inputs[1])
                material.node_tree.links.new(math.outputs['Value'], nodes['Output'].inputs['Alpha'])

    def build_materials_old(self, texture_pack):
        for ptr, texture_dict in self.textures.items():
            # TODO: Consider doing this another way.
            name = "Texture-{:04x}".format(ptr)
            texture_dict["bpy"] = bpy.data.textures.new(name, type = 'IMAGE')
            texture_dict["bpy"].image = texture_pack[texture_dict["image"]].image
            texture_dict["bpy"].use_alpha = False
            texture_dict["bpy_alpha"] = bpy.data.textures.new(name + "-alpha", type = 'IMAGE')
            texture_dict["bpy_alpha"].image = texture_pack[texture_dict["image"]].image
            texture_dict["bpy_alpha"].use_alpha = True
            texture_dict["bpy_normal"] = bpy.data.textures.new(name + "-normal", type = 'IMAGE')
            texture_dict["bpy_normal"].image = texture_pack[texture_dict["image"]].image
            texture_dict["bpy_normal"].use_alpha = False
            texture_dict["bpy_normal"].use_normal_map = True
        for ptr, material_dict in self.materials.items():
            name = "Material-{:04x}".format(ptr)
            material_dict["bpy"] = material = bpy.data.materials.new(name)
            material.game_settings.use_backface_culling = material_dict["use_backface_culling"]
            material.specular_intensity = 0.0
            if material_dict["texture0_ptr"]:
                slot0 = material.texture_slots.add()
                slot0.texture_coords = 'UV'
                if material_dict["use_alpha"]:
                    slot0.texture = material_dict["texture0"]["bpy_alpha"]
                    slot0.use_map_alpha = True
                    slot0.alpha_factor = 1.0
                else:
                    slot0.texture = material_dict["texture0"]["bpy"]
            if material_dict["use_alpha"]:
                material.use_transparency = True
                material.transparency_method = 'Z_TRANSPARENCY'
                material.alpha = 0.0
            if material_dict["texture1_ptr"]:
                slot1 = material.texture_slots.add()
                slot1.texture_coords = 'UV'
                if material_dict["use_normal"]:
                    slot1.texture = material_dict["texture1"]["bpy_normal"]
                    slot1.use_map_color_diffuse = False
                    slot1.use_map_normal = True
                else:
                    slot1.texture = material_dict["texture1"]["bpy_alpha"]
            if material_dict["use_backface_culling"]:
                slot2 = material.texture_slots.add()
                if self.oneside is None:
                    self.create_oneside()
                slot2.texture = self.oneside
                slot2.texture_coords = 'NORMAL'
                slot2.use_map_color_diffuse = False
                slot2.use_map_alpha = True
                slot2.mapping_x = 'Z'
                slot2.mapping_y = 'NONE'
                slot2.mapping_z = 'NONE'
                slot2.default_value = 0.0
                slot2.use_rgb_to_intensity = True

    def assign_materials(self):
        for mesh in self.meshes:
            material = self.materials[mesh["object"]["material_ptr"]]["bpy"]
            mesh["bpy"].data.materials.append(material)
            u = ["u", "u2"]
            v = ["v", "v2"]
            for slot_i in range(2):
                if hasattr(material.texture_slots[slot_i], "texture") and material.texture_slots[slot_i].texture.type == 'IMAGE':
                    uvname = "UVMap-{}".format(slot_i)
                    uv_texture = mesh["bpy"].data.uv_textures.new(uvname)
                    uv_layer = mesh["bpy"].data.uv_layers[uvname]
                    material.texture_slots[slot_i].uv_layer = uvname
                    image = material.texture_slots[slot_i].texture.image
                    for i, face in enumerate(mesh["faces"]):
                        if u[slot_i] not in mesh["vertices"][face[0]]:
                            break
                        mesh["bpy"].data.polygons[i].use_smooth = 1
                        uv_layer.data[i*3 + 0].uv = (mesh["vertices"][face[0]][u[slot_i]], mesh["vertices"][face[0]][v[slot_i]] + 1)
                        uv_layer.data[i*3 + 1].uv = (mesh["vertices"][face[1]][u[slot_i]], mesh["vertices"][face[1]][v[slot_i]] + 1)
                        uv_layer.data[i*3 + 2].uv = (mesh["vertices"][face[2]][u[slot_i]], mesh["vertices"][face[2]][v[slot_i]] + 1)
                        uv_texture.data[i].image = image

    def build_shape_keys(self, shape_key_set):
        scene = bpy.context.scene
        for mesh, shape_key in zip(self.meshes, shape_key_set.shape_keys):
            if shape_key['vc_game'] == 1:
                shape_vertices = shape_key["vertices"]
                vertex_shift = len(mesh["bpy"].data.vertices) - len(shape_vertices)
            elif shape_key['vc_game'] == 4:
                slice_start = mesh["first_vertex"]
                slice_end = slice_start + mesh["vertex_count"]
                shape_vertices = shape_key["vertices"][slice_start:slice_end]
                vertex_shift = 0
            if "bpy_dup_base" not in mesh:
                bpy.ops.object.select_all(action='DESELECT')
                scene.objects.active = mesh["bpy"]
                mesh["bpy"].select = True
                bpy.ops.object.duplicate()
                mesh["bpy_dup_base"] = scene.objects.active
            bpy.ops.object.select_all(action='DESELECT')
            scene.objects.active = mesh["bpy_dup_base"]
            mesh["bpy_dup_base"].select = True
            bpy.ops.object.duplicate()
            temp_object = scene.objects.active
            temp_object.name = "HSHP-{:02d}".format(shape_key_set.shape_key_set_id)
            for i, vertex in enumerate(shape_vertices):
                if not "translate_x" in vertex:
                    continue
                j = i + vertex_shift
                old = temp_object.data.vertices[j].co
                new = [old[0] + vertex["translate_x"],
                    old[1] + vertex["translate_y"],
                    old[2] + vertex["translate_z"],
                    ]
                temp_object.data.vertices[j].co = new
            scene.objects.active = mesh["bpy"]
            temp_object.select = True
            bpy.ops.object.join_shapes()
            bpy.ops.object.select_all(action='DESELECT')
            temp_object.select = True
            bpy.ops.object.delete()

    def finalize_blender(self):
        for mesh in self.meshes:
            mesh["bpy"].data.update()
            mesh["bpy"].data.use_auto_smooth = True
            normals = [(dict_vertex["normal_x"], dict_vertex["normal_y"], dict_vertex["normal_z"]) for dict_vertex in mesh["vertices"]]
            mesh["bpy"].data.normals_split_custom_set_from_vertices(normals)
            if "bpy_dup_base" in mesh:
                bpy.ops.object.select_all(action='DESELECT')
                mesh["bpy_dup_base"].select = True
                bpy.ops.object.delete()


class ValkyriaScene:
    def __init__(self, source_file, name):
        self.source_file = source_file
        self.name = os.path.basename(name)
        self.filename = name
        self.layers_used = 0

    def layer_list(self, layer_num):
        max_layers = 20
        clamped_layer_num = layer_num % max_layers
        if clamped_layer_num + 1 > self.layers_used:
            self.layers_used = clamped_layer_num + 1
        layers_before = [False] * clamped_layer_num
        layers_after = [False] * (max_layers - 1 - clamped_layer_num)
        return layers_before + [True] + layers_after

    def create_scene(self, name):
        self.scene = bpy.data.scenes.new(name)
        for screen in bpy.data.screens:
            screen.scene = self.scene
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.clip_end = 20000
                            space.viewport_shade = 'TEXTURED'
                            if hasattr(space, 'show_backface_culling'):
                                space.show_backface_culling = True
        self.scene.layers = self.layer_list(0)
        self.scene.game_settings.material_mode = 'GLSL'
        self.scene.display_settings.display_device = 'sRGB'

    def create_lamp(self):
        lamp_data = bpy.data.lamps.new("Default Lamp", 'HEMI')
        lamp = bpy.data.objects.new("Default Lamp", lamp_data)
        lamp.layers = [True] * self.layers_used + [False] * (20 - self.layers_used)
        lamp.location = (0.0, 20.0, 15.0)
        lamp.rotation_mode = 'AXIS_ANGLE'
        lamp.rotation_axis_angle = (radians(-22.0), 1.0, 0.0, 0.0)
        self.scene.objects.link(lamp)
        self.scene.update()

    def read_data(self):
        self.source_file.read_data()
        if isinstance(self.source_file, HMDL_Model):
            possible_files = []
            possible_files.append(self.filename[0:-4] + '.htx')
            possible_files.append(self.filename[0:-4] + '.HTX')
            htex = None
            for possible_file in possible_files:
                try:
                    htex = valkyria.files.valk_open(possible_file)[0]
                except FileNotFoundError:
                    continue
            if htex is not None:
                htex.find_inner_files()
                self.hmdl_htex_pack = HTEX_Pack(htex, 0)
                self.hmdl_htex_pack.read_data()

    def build_blender(self):
        self.create_scene(self.name)
        self.create_lamp()
        self.source_file.build_blender()
        self.source_file.finalize_blender()
        if isinstance(self.source_file, HMDL_Model) and hasattr(self, 'hmdl_htex_pack'):
            self.hmdl_htex_pack.build_blender()
            self.source_file.assign_materials(self.hmdl_htex_pack.htsf_images)

    def pose_blender(self, pose_filename):
        poses = IZCA_Poses(valkyria.files.valk_open(pose_filename)[0])
        poses.F.find_inner_files()
        poses.read_data()
        poses.pose_model(self.source_file)


class ImportValkyria(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_scene.import_valkyria'
    bl_label = 'Valkyria Chronicles (.MLX, .HMD, .ABR, .MXE)'
    filename_ext = "*.mlx"
    filter_glob = bpy.props.StringProperty(
            default = "*.mlx;*.hmd;*.abr;*.mxe",
            options = {'HIDDEN'},
            )

    def import_file(self, filename):
        vfile = valkyria.files.valk_open(filename)[0]
        vfile.find_inner_files()
        if vfile.ftype == 'IZCA':
            model = IZCA_Model(vfile)
        elif vfile.ftype == 'HMDL':
            model = HMDL_Model(vfile, 0)
        elif vfile.ftype == 'ABRS':
            model = ABRS_Model(vfile)
        elif vfile.ftype == 'MXEN':
            model = MXEN_Model(vfile)
        self.valk_scene = ValkyriaScene(model, filename)
        try:
            self.valk_scene.read_data()
        except FileNotFoundError as e:
            message = 'This model requires a separate file which could not be found:\n'
            message += '    ' + str(e)
            message += '\nTry finding the file manually and copying it into the same folder as the model you attempted to open.'
            self.report({'ERROR'}, message)
        self.valk_scene.build_blender()
        #pose_filename = os.path.join(os.path.dirname(filename), "VALCA02AD.MLX")
        #self.valk_scene.pose_blender(pose_filename)

    def execute(self, context):
        self.import_file(self.filepath)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ImportValkyria.bl_idname)

def register():
    bpy.utils.register_class(ImportValkyria)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ImportValkyria)
    bpy.types.INFO_MT_file_import.remove(menu_func)
