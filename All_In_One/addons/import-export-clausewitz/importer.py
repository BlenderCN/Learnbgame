from pathlib import Path
import os
import io
import math
import mathutils
import random

import bpy
import bmesh

from . import (pdx_data, utils)

class PdxFileImporter:
    def __init__(self, filename):
        utils.Log.info("------------------------------------")
        utils.Log.info("Importing: " + filename + "\n\n\n\n\n")
        self.file = pdx_data.PdxFile(filename)
        self.file.read()

        self.mat_rot_simple = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')

        self.mat_rot = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
        self.mat_rot *= mathutils.Matrix.Scale(-1, 4, (1,0,0))

        self.mat_rot_inverse = self.mat_rot.copy()
        self.mat_rot_inverse.invert()

    def import_mesh(self):
        #Rotation Matrix to Transform from Y-Up Space to Z-Up Space

        for node in self.file.nodes:
            if isinstance(node, pdx_data.PdxAsset):
                utils.Log.info("Importer: PDXAsset")
                utils.Log.info("PDXAsset Version " + str(node.version[0]) + "." + str(node.version[1]))
            elif isinstance(node, pdx_data.PdxWorld):
                for shape in node.objects:
                    bpy.ops.object.select_all(action='DESELECT')
                    if isinstance(shape, pdx_data.PdxShape):
                        name = shape.name

                        obj = None

                        collisionShape = False
                        skeletonPresent = False

                        boneNames = None

                        if isinstance(shape.skeleton, pdx_data.PdxSkeleton):
                            skeletonPresent = True
                            boneNames = [""] * len(shape.skeleton.joints)

                            amt = bpy.data.armatures.new(name)
                            amt.draw_type = 'STICK'
                            obj = bpy.data.objects.new(name, amt)

                            scn = bpy.context.scene
                            scn.objects.link(obj)
                            scn.objects.active = obj
                            obj.select = True

                            for joint in shape.skeleton.joints:
                                boneNames[joint.index] = joint.name

                            bpy.ops.object.mode_set(mode='EDIT')

                            for joint in shape.skeleton.joints:
                                #Head of the Bone is the PdxJoint.
                                #Tail only goes to next Bone
                                bone = amt.edit_bones.new(joint.name)

                                #Transformation Matrix
                                transformationMatrix = mathutils.Matrix()
                                transformationMatrix[0][0:4] = joint.transform[0], joint.transform[3], joint.transform[6], 0
                                transformationMatrix[1][0:4] = joint.transform[1], joint.transform[4], joint.transform[7], 0
                                transformationMatrix[2][0:4] = joint.transform[2], joint.transform[5], joint.transform[8], 0
                                transformationMatrix[3][0:4] = 0, 0, 0, 1

                                #Position with applied Rotation and Scaling
                                joint_position = -mathutils.Vector((joint.transform[9], joint.transform[10], joint.transform[11], 1))
                                joint_position = joint_position * transformationMatrix * self.mat_rot

                                print(joint_position)

                                #Apply Postion to Bone
                                bone.head = joint_position[0:3]

                                #Applying Default Position for tail
                                p = joint_position + mathutils.Vector((0, 0.1, 0, 1)) * transformationMatrix * self.mat_rot
                                bone.tail = p[0:3]

                                if joint.parent >= 0:
                                    #Does have a Parent

                                    #Setting Parent
                                    parent = amt.edit_bones[boneNames[joint.parent]]
                                    bone.parent = parent

                            bpy.ops.object.mode_set(mode='OBJECT')

                        mesh = bpy.data.meshes.new(name)
                        meshObj = bpy.data.objects.new(name, mesh)

                        scn = bpy.context.scene
                        scn.objects.link(meshObj)
                        scn.objects.active = meshObj
                        meshObj.select = True
                        if not(obj is None):
                            meshObj.parent = obj

                        for meshData in shape.meshes:
                            if isinstance(meshData, pdx_data.PdxMesh):
                                sub_mesh = bpy.data.meshes.new(name)
                                sub_object = bpy.data.objects.new(name, sub_mesh)

                                scn = bpy.context.scene
                                scn.objects.link(sub_object)
                                scn.objects.active = sub_object
                                sub_object.select = True

                                sub_mesh.from_pydata(meshData.verts, [], meshData.faces)
                                #sub_mesh.normals_split_custom_set_from_vertices(meshData.normals)

                                if skeletonPresent:
                                    for name in boneNames:
                                        sub_object.vertex_groups.new(name)

                                    if meshData.skin is not None:
                                        utils.Log.info("BPV: " + str(meshData.skin.bonesPerVertice))
                                        bpv = meshData.skin.bonesPerVertice
                                        bpv = 4

                                        for i in range(len(meshData.skin.indices) // bpv):
                                            for j in range(bpv):
                                                indice = meshData.skin.indices[i * bpv + j]
                                                if indice >= 0:
                                                    bName = boneNames[indice]
                                                    weight = meshData.skin.weight[i * bpv + j]
                                                    sub_object.vertex_groups[bName].add([i], weight, 'REPLACE')
                                    else:
                                        utils.Log.warning("No Skinning Data")

                                bm = bmesh.new()
                                bm.from_mesh(sub_mesh)

                                for vert in bm.verts:
                                    vert.co = vert.co * self.mat_rot
                                    vert.normal = vert.normal * self.mat_rot_inverse

                                bm.normal_update()
                                bm.verts.ensure_lookup_table()
                                bm.verts.index_update()
                                bm.faces.index_update()

                                if meshData.material.shader == "Collision":
                                    collisionShape = True
                                else:
                                    uv_layer = bm.loops.layers.uv.new(name + "_uv")

                                    for face in bm.faces:
                                        face.smooth = True
                                        for loop in face.loops:
                                            loop[uv_layer].uv[0] = meshData.uv_coords[loop.vert.index][0]
                                            loop[uv_layer].uv[1] = 1 - meshData.uv_coords[loop.vert.index][1]

                                    mat = bpy.data.materials.new(name=name + "_material")
                                    mat.diffuse_color = (random.random(), random.random(), random.random())
                                    sub_object.data.materials.append(mat)

                                    tex = bpy.data.textures.new(shape.name + "_tex", 'IMAGE')
                                    tex.type = 'IMAGE'

                                    img_file = Path(os.path.join(os.path.dirname(self.file.filename), meshData.material.diff))
                                    altImageFile = Path(os.path.join(os.path.dirname(self.file.filename), os.path.basename(self.file.filename).replace(".mesh", "") + "_diffuse.dds"))

                                    if img_file.is_file():
                                        img_file.resolve()
                                        image = bpy.data.images.load(str(img_file))
                                        tex.image = image
                                    elif altImageFile.is_file():
                                        altImageFile.resolve()
                                        image = bpy.data.images.load(str(altImageFile))
                                        tex.image = image
                                    else:
                                        utils.Log.info("No Texture File was found.")

                                    slot = mat.texture_slots.add()
                                    slot.texture = tex
                                    slot.bump_method = 'BUMP_ORIGINAL'
                                    slot.mapping = 'FLAT'
                                    slot.mapping_x = 'X'
                                    slot.mapping_y = 'Y'
                                    slot.texture_coords = 'UV'
                                    slot.use = True
                                    slot.uv_layer = uv_layer.name

                                bm.to_mesh(sub_mesh)
                            else:
                                utils.Log.info("ERROR ::: Invalid Object in Shape: " + str(meshData))

                        scn.objects.active = meshObj
                        bpy.ops.object.join()

                        if collisionShape:
                            meshObj.draw_type = "WIRE"

                        if skeletonPresent:
                            bpy.ops.object.modifier_add(type='ARMATURE')
                            bpy.context.object.modifiers["Armature"].object = obj

                    else:
                        utils.Log.info("ERROR ::: Invalid Object in World: " + str(shape))
            elif isinstance(node, pdx_data.PdxLocators):
                parent_locator = bpy.data.objects.new('Locators', None)
                bpy.context.scene.objects.link(parent_locator)

                for locator in node.locators:
                    obj = bpy.data.objects.new(locator.name, None)
                    bpy.context.scene.objects.link(obj)
                    obj.parent = parent_locator
                    obj.empty_draw_size = 2
                    obj.empty_draw_type = 'SINGLE_ARROW'
                    obj.location = mathutils.Vector((locator.pos[0], locator.pos[1], locator.pos[2])) * self.mat_rot
                    obj.rotation_mode = 'QUATERNION'
                    obj.rotation_quaternion = locator.quaternion
                    obj.rotation_mode = 'XYZ'

                    #TODO Locator Parenting
                    #parentBoneName = locator.parent

                    #constraint = obj.constraints.new('CHILD_OF')
                    #constraint.target = parentBoneName
            else:
                utils.Log.info("ERROR ::: Invalid node found: " + str(node))

    def getRecursiveBoneMatrix(self, bone):
        if bone.parent is None:
            return bone.matrix.copy()
        else:
            parent_inv = bone.parent.matrix.copy()
            parent_inv.invert()

            return bone.matrix.copy() * parent_inv

    def import_anim(self):
        scn = bpy.context.scene

        tJoints = []
        qJoints = []
        sJoints = []
        joints = []
        samples = None

        armature = None

        for obj in bpy.data.objects:
            if obj.type == "ARMATURE" and obj.select:
                armature = obj
                break

        for node in self.file.nodes:
            if isinstance(node, pdx_data.PdxAsset):
                utils.Log.info("Importer: PDXAsset")#TODOs
                utils.Log.info("PDXAsset Version " + str(node.version[0]) + "." + str(node.version[1]))
            elif isinstance(node, pdx_data.PdxAnimInfo):
                utils.Log.info("Loading AnimInfo...")
                utils.Log.info("FPS: " + str(node.fps))
                scn.render.fps = node.fps
                utils.Log.info("Samples: " + str(node.samples))
                scn.frame_start = 1
                scn.frame_end = node.samples
                utils.Log.info("Joints: " + str(node.jointCount))

                for joint in node.animJoints:
                    utils.Log.info("Mode: " + joint.sampleMode)
                    joints.append(joint)
                    if "t" in joint.sampleMode:
                        utils.Log.info("T")
                        tJoints.append(joint)
                    if "q" in joint.sampleMode:
                        utils.Log.info("Q")
                        qJoints.append(joint)
                    if "s" in joint.sampleMode:
                        utils.Log.info("S")
                        sJoints.append(joint)

            elif isinstance(node, pdx_data.PdxAnimSamples):
                samples = node

        if (len(tJoints) > 0 or len(qJoints) > 0 or len(sJoints) > 0) and samples != None:
            utils.Log.info("Animation detected!")
            utils.Log.info("T: " + str(len(tJoints)) + "|" + str(len(samples.t) / (scn.frame_end * 3)))
            utils.Log.info("Q: " + str(len(qJoints)) + "|" + str(len(samples.q) / (scn.frame_end * 4)))
            utils.Log.info("S: " + str(len(sJoints)) + "|" + str(len(samples.s) / (scn.frame_end * 1)))

            bpy.context.scene.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')

            for joint in joints:
                print(joint.name)
                bone = armature.pose.bones[joint.name]
                bone.rotation_mode = 'QUATERNION'

                bonematrix = self.getRecursiveBoneMatrix(bone)
                print("\nRAW:")
                print(bone.matrix)
                print("\nCalculated:")
                print(bonematrix)
                bonematrix.invert()

                print("\nT:")
                t = mathutils.Vector((joint.translation[0], joint.translation[1], joint.translation[2], 1))
                print(t * self.mat_rot)
                bone.location = (bonematrix * (t * self.mat_rot)).to_3d()
                print(bone.location)
                #if joint in tJoints:
                #    i = tJoints.index(joint)
                #    for f in range(scn.frame_end):
                #        t = mathutils.Vector((samples.t[(f * len(tJoints) + i) * 3 + 0], samples.t[(f * len(tJoints) + i) * 3 + 1], samples.t[(f * len(tJoints) + i) * 3 + 2], 1))
                #        bone.location = (bonematrix * (t * self.mat_rot)).to_3d()
                #        bone.keyframe_insert(data_path="location", frame=f+1)

                #print("\nQ:")
                #q = mathutils.Quaternion((joint.quaternion[3], joint.quaternion[0], joint.quaternion[1], joint.quaternion[2]))
                #print(q)
                #print((q.to_matrix().to_4x4() * self.mat_rot).to_quaternion())
                #bone.rotation_quaternion = (bonematrix * (q.to_matrix().to_4x4() * self.mat_rot)).to_quaternion()
                #print(bone.rotation_quaternion)
                #if joint in qJoints:
                #    i = qJoints.index(joint)
                #    for f in range(scn.frame_end):
                #        q = mathutils.Vector((samples.q[(f * len(qJoints) + i) * 4 + 3], samples.q[(f * len(qJoints) + i) * 4 + 0], samples.q[(f * len(qJoints) + i) * 4 + 1], samples.q[(f * len(qJoints) + i) * 4 + 2]))
                #        bone.rotation_quaternion = bonematrix * (q * self.mat_rot)
                #        bone.keyframe_insert(data_path="rotation_quaternion", frame=f+1)
                
                #print("\nS:")
                #s = mathutils.Vector((joint.size, joint.size, joint.size, 0))
                #print(s * self.mat_rot)
                #bone.scale = (bonematrix * (s * self.mat_rot)).to_3d()
                #print(bone.scale)
                #if joint in sJoints:
                #    i = sJoints.index(joint)
                #    for f in range(scn.frame_end):
                #        s = mathutils.Vector((samples.s[f * len(qJoints) + i], samples.s[f * len(qJoints) + i], samples.s[f * len(qJoints) + i], 0))
                #        bone.scale = (bonematrix * (s * self.mat_rot)).to_3d()
                #        bone.keyframe_insert(data_path="scale", frame=f+1)

            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            utils.Log.info("Invalid File (Joints or Samples missing)")