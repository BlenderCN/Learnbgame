# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import bpy
import os
import time
from mathutils import Matrix, Vector

# Blender imports
# NONE!

# Addon imports
from ..functions import *


class ABS_OT_append_materials(bpy.types.Operator):
    """Append ABS Plastic Materials from external blender file"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "abs.append_materials"                                          # unique identifier for buttons and menu items to reference.
    bl_label = "Append ABS Plastic Materials"                                   # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    # @classmethod
    # def poll(self, context):
    #     return context.scene.render.engine in ("CYCLES", "BLENDER_EEVEE")

    def execute(self, context):
        # initialize variables
        scn = context.scene
        mat_names = getMatNames()  # list of materials to append from 'abs_plastic_materials.blend'
        alreadyImported = [mn for mn in mat_names if bpy.data.materials.get(mn) is not None]
        self.matsToReplace = []
        failed = []
        orig_selection = list(bpy.context.selected_objects)
        outdated_version = len(alreadyImported) > 0 and bpy.data.materials[alreadyImported[0]].abs_plastic_version != bpy.props.abs_plastic_version

        # switch to cycles render engine temporarily
        last_render_engine = scn.render.engine
        scn.render.engine = "CYCLES"

        # define images and node groups to replace
        imagesToReplace = ("ABS Fingerprints and Dust",)
        nodeGroupsToReplace = ("ABS_Absorbtion", "ABS_Basic Noise", "ABS_Bump", "ABS_Dialectric", "ABS_Dialectric 2", "ABS_Fingerprint", "ABS_Fresnel", "ABS_GlassAbsorption", "ABS_Parallel_Scratches", "ABS_PBR Glass", "ABS_Principled", "ABS_Random Value", "ABS_Randomize Color", "ABS_Reflection", "ABS_RotateXYZ", "RotateX", "RotateY", "RotateZ", "ABS_Scale", "ABS_Scratches", "ABS_Specular Map", "ABS_Transparent", "ABS_Uniform Scale", "ABS_Translate")

        # define file paths
        addonPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        blendFileName = "node_groups_2-8.blend" if b280() else "node_groups_2-7.blend"
        blendfile = os.path.join(addonPath, "lib", blendFileName)
        im_path = os.path.join(addonPath, "lib", "ABS Fingerprints and Dust.png")
        nodeDirectory = os.path.join(blendfile, "NodeTree")

        # set cm.brickMaterialsAreDirty for all models in Bricker, if it's installed
        if hasattr(scn, "cmlist"):
            for cm in scn.cmlist:
                if cm.materialType == "Random":
                    cm.brickMaterialsAreDirty = True

        if len(alreadyImported) == 0 or outdated_version:
            # remove existing node groups
            for ng_name in nodeGroupsToReplace:
                ng = bpy.data.node_groups.get(ng_name)
                if ng is not None: bpy.data.node_groups.remove(ng)
            # load node groups from 'node_groups_2-??.blend'
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                for attr in ("node_groups",):
                    setattr(data_to, attr, getattr(data_from, attr))
            bpy.data.node_groups["ABS_Transparent"].use_fake_user = True
            # remove existing bump/specular maps
            for im_name in imagesToReplace:
                im = bpy.data.images.get(im_name)
                if im is not None: bpy.data.images.remove(im)
            # load image from lib/ folder
            bpy.ops.image.open(filepath=im_path)
            im = bpy.data.images.get("ABS Fingerprints and Dust.png")
            im.name = "ABS Fingerprints and Dust"
            # map image nodes to correct image data block
            im.update()
            for gn in ("ABS_Fingerprint", "ABS_Specular Map"):
                ng = bpy.data.node_groups.get(gn)
                for node in ng.nodes:
                    if node.type == "TEX_IMAGE":
                        node.image = im

        for mat_name in mat_names:
            # if material exists, remove or skip
            m = bpy.data.materials.get(mat_name)
            if m is not None:
                if not m.abs_plastic_version != bpy.props.abs_plastic_version:
                    continue
                # mark material to replace
                m.name = m.name + "__replaced"
                self.matsToReplace.append(m)

            # get the current length of bpy.data.materials
            last_len_mats = len(bpy.data.materials)

            # create new material
            m = bpy.data.materials.new(mat_name)
            m.use_nodes = True
            m.abs_plastic_version = bpy.props.abs_plastic_version

            # create/get all necessary nodes
            nodes = m.node_tree.nodes
            nodes.remove(nodes.get("Principled BSDF" if b280() else "Diffuse BSDF"))
            n_shader = nodes.new("ShaderNodeGroup")
            if mat_name.startswith("ABS Plastic Trans-"):
                n_shader.node_tree = bpy.data.node_groups.get("ABS_Transparent")
                n_shader.name = "ABS Transparent"
            else:
                n_shader.node_tree = bpy.data.node_groups.get("ABS_Dialectric")
                n_shader.name = "ABS Dialectric"
            n_bump = nodes.new("ShaderNodeGroup")
            n_bump.node_tree = bpy.data.node_groups.get("ABS_Bump")
            n_bump.name = "ABS Bump"
            n_scale = nodes.new("ShaderNodeGroup")
            n_scale.node_tree = bpy.data.node_groups.get("ABS_Uniform Scale")
            n_scale.name = "ABS Uniform Scale"
            if b280():
                n_displace = nodes.new("ShaderNodeDisplacement")
                n_displace.inputs["Midlevel"].default_value = 0.0
                n_displace.inputs["Scale"].default_value = 0.1
            n_uv = nodes.new("ShaderNodeUVMap")
            n_obj_info = nodes.new("ShaderNodeObjectInfo")
            n_translate = nodes.new("ShaderNodeGroup")
            n_translate.node_tree = bpy.data.node_groups.get("ABS_Translate")
            n_translate.name = "ABS_Translate"
            n_output = nodes.get("Material Output")

            # connect the nodes together
            links = m.node_tree.links
            links.new(n_shader.outputs["Shader"], n_output.inputs["Surface"])
            if b280():
                links.new(n_bump.outputs["Color"], n_displace.inputs["Height"])
            #     links.new(n_displace.outputs["Displacement"], n_output.inputs["Displacement"])
            # else:
            #     links.new(n_bump.outputs["Color"], n_output.inputs["Displacement"])
            links.new(n_uv.outputs["UV"], n_translate.inputs["Vector"])
            links.new(n_obj_info.outputs["Random"], n_translate.inputs["X"])
            links.new(n_obj_info.outputs["Random"], n_translate.inputs["Y"])
            links.new(n_translate.outputs["Vector"], n_scale.inputs["Vector"])
            links.new(n_scale.outputs["Vector"], n_shader.inputs["Vector"])
            links.new(n_scale.outputs["Vector"], n_bump.inputs["Vector"])

            # position the nodes in 2D space
            starting_loc = n_output.location
            n_shader.location = n_output.location - Vector((200, -250))
            n_bump.location = n_output.location - Vector((200, 200))
            if b280():
                n_displace.location = n_output.location - Vector((000, 200))
            n_scale.location = n_output.location - Vector((400, 200))
            n_translate.location = n_output.location - Vector((600, 200))
            n_obj_info.location = n_output.location - Vector((775, 50))
            n_uv.location = n_output.location - Vector((800, 200))

            # set properties
            mat_properties = bpy.props.abs_mat_properties
            if mat_name in mat_properties.keys():
                for k in mat_properties[mat_name].keys():
                    try:
                        n_shader.inputs[k].default_value = mat_properties[mat_name][k]
                    except KeyError:
                        pass
            m.diffuse_color = mat_properties[mat_name]["Color" if mat_name.startswith("ABS Plastic Trans-") else "Diffuse Color"][:4 if b280() else 3]

            # get compare last length of bpy.data.materials to current (if the same, material not imported)
            if len(bpy.data.materials) == last_len_mats:
                self.report({"WARNING"}, "'%(mat_name)s' could not be imported. Try reinstalling the addon." % locals())
                if m in self.matsToReplace:
                    self.matsToReplace.remove(m)
                failed.append(mat_name)
                continue

        # replace old material node trees
        for old_mat in self.matsToReplace:
            origName = old_mat.name.split("__")[0]
            new_mat = bpy.data.materials.get(origName)
            old_mat.user_remap(new_mat)
            bpy.data.materials.remove(old_mat)

        # update subsurf/roughness/etc. amounts
        update_abs_subsurf(self, bpy.context)
        update_abs_roughness(self, bpy.context)
        update_abs_randomize(self, bpy.context)
        update_abs_fingerprints(self, context)
        update_abs_displace(self, bpy.context)
        toggle_save_datablocks(self, bpy.context)

        # # remap node groups to one group
        # for groupName in nodeGroupsToReplace:
        #     continue
        #     firstGroup = None
        #     groups = [g for g in bpy.data.node_groups if g.name.startswith(groupName)]
        #     if len(groups) > 1:
        #         for g in groups[:-1]:
        #             g.user_remap(groups[-1])
        #             bpy.data.node_groups.remove(g)
        #         groups[-1].name = groupName

        # report status
        if len(alreadyImported) == len(mat_names) and not outdated_version:
            self.report({"INFO"}, "Materials already imported")
        elif len(alreadyImported) > 0 and not outdated_version:
            self.report({"INFO"}, "The following Materials were skipped: " + str(alreadyImported)[1:-1].replace("'", "").replace("ABS Plastic ", ""))
        elif len(failed) > 0:
            self.report({"INFO"}, "The following Materials failed to import (try reinstalling the addon): " + str(failed)[1:-1].replace("'", "").replace("ABS Plastic ", ""))
        elif outdated_version:
            self.report({"INFO"}, "Materials updated successfully!")
        else:
            self.report({"INFO"}, "Materials imported successfully!")

        # return to original context
        select(orig_selection)
        scn.render.engine = last_render_engine

        return {"FINISHED"}
