import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty
from .. import M3utils as m3
from .. utils.operators import get_selection


class MatchMaterial(bpy.types.Operator):
    bl_idname = "machin3.match_material"
    bl_label = "MACHIN3: Match Material"
    bl_options = {'REGISTER', 'UNDO'}

    targetmatslot = IntProperty(name="Material Slot", default=0, min=0)

    matchmaterial = BoolProperty(name="Match Material", default=True)
    matchsubset = BoolProperty(name="Match Subset", default=False)
    matchside2 = BoolProperty(name="Match Second Side", default=False)

    decaltype = StringProperty(name="Decal Type", default="")

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        if bpy.app.version >= (2, 79, 0):
            if self.decaltype == "SUBTRACTOR":
                column.label("Subsractor Decal")
            elif self.decaltype == "SUBSET":
                column.label("Subset Decal")
            elif self.decaltype == "PANEL":
                column.label("Panel Decal")
            elif self.decaltype == "INFO":
                column.label("Info Decals can't be matched")

            column.prop(self, "targetmatslot")

            if self.decaltype in ["SUBSET", "PANEL"]:
                column.prop(self, "matchmaterial")

            if self.decaltype == "SUBSET":
                column.prop(self, "matchsubset")

            if self.decaltype == "PANEL":
                column.prop(self, "matchside2")

    def execute(self, context):
        if bpy.app.version >= (2, 79, 0):
            self.match_material()
        else:
            match_material_old(self)

        return {'FINISHED'}

    def match_material(self):
        target, decals = get_selection()

        decal = decals[0]
        decalmat = decal.material_slots[0].material

        # safety checks
        if len(target.data.materials) == 0:
            self.report({'ERROR'}, "Target has no materials applied!")
            return {'FINISHED'}
        else:
            if len(target.material_slots) < self.targetmatslot + 1:
                self.targetmatslot = len(target.material_slots) - 1

            targetmat = target.material_slots[self.targetmatslot].material

            if targetmat is None:
                self.report({'ERROR'}, "Target material slot is empty!")
                return {'FINISHED'}
            elif not targetmat.use_nodes:
                self.report({'ERROR'}, "Target material needs to use nodes!")
                return {'FINISHED'}

            print("Matching Material: '%s'" % (targetmat.name))

        try:
            targetshader = targetmat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node
        except:
            self.report({'ERROR'}, "Material: '%s' - Nothing connected to 'Material Output' node!" % (targetmat.name))
            return {'FINISHED'}

        # look for existing matching materials and create a new one if none is found
        if targetshader.type == "BSDF_GLOSSY":
            targetparams = self.get_glossy(targetshader)

            matchingmat = self.find_matching_decalmat(targetparams, decalmat, "GLOSSY")

            if matchingmat is False:
                return {'FINISHED'}
            elif matchingmat == decalmat:
                print("Matching Decal material is already applied")
            elif matchingmat is None:
                newdecalmat = decalmat.copy()
                decal.material_slots[0].material = newdecalmat
                print("No matching Decal material found in scene, created a new one: '%s'" % (newdecalmat.name))
                self.match(newdecalmat, targetparams, "GLOSSY")
            else:
                print("Found existing matching Decal Material: '%s', applying now" % (matchingmat.name))
                decal.material_slots[0].material = matchingmat

        elif targetshader.type == "BSDF_PRINCIPLED":
            targetparams, m3prop = self.get_pbr(targetshader)

            matchingmat = self.find_matching_decalmat(targetparams, decalmat, "PBR")

            if matchingmat is False:
                return {'FINISHED'}
            elif matchingmat == decalmat:
                print("Matching Decal material is already applied")
            elif matchingmat is None:
                newdecalmat = decalmat.copy()
                decal.material_slots[0].material = newdecalmat
                print("No matching Decal material found in scene, created a new one: '%s'" % (newdecalmat.name))
                self.match(newdecalmat, targetparams, "PBR", m3prop)
            else:
                print("Found existing matching Decal Material: '%s', applying now" % (matchingmat.name))
                decal.material_slots[0].material = matchingmat

        else:
            self.report({'ERROR'}, "Material: '%s' - Glossy or Principled Shader not present or not (directly) connected to 'Material Output' node!" % (targetmat.name))
            return {'FINISHED'}

    def find_matching_decalmat(self, targetparams, decalmat, matchtype):
        print("Looking for existing matching Decal Material\n")

        # get decal base name
        if "." in decalmat.name:
            decalmatbasename = decalmat.name[:-4]
        else:
            decalmatbasename = decalmat.name

        # get all mats of that decal, including other color variations
        samedecaltypes = []
        for mat in bpy.data.materials:
            if decalmatbasename in mat.name:  # avoid replacing a supplied decal with a custom decal
                if decalmatbasename.startswith("c_") and mat.name.startswith("c_"):
                    samedecaltypes.append(mat)
                elif not decalmatbasename.startswith("c_") and not mat.name.startswith("c_"):
                    samedecaltypes.append(mat)

        matchingmat = None
        for mat in samedecaltypes:
            decalparams = self.get_decalmat(mat)

            if decalparams is None:  # INFO decal
                return False

            if decalparams["Type"] == "SUBSET":
                if not any([self.matchmaterial, self.matchsubset]):  # Abort if neither of the subset options are ticked
                    return False

                if self.matchmaterial and self.matchsubset:
                    if matchtype == "GLOSSY":
                        materialparams = {"color": decalparams["Material"]["color"],
                                          "roughness": decalparams["Material"]["roughness"],
                                          "distribution": decalparams["Material"]["glossydistribution"]}

                        subsetparams = {"color": decalparams["Subset"]["color"],
                                        "roughness": decalparams["Subset"]["roughness"],
                                        "distribution": decalparams["Subset"]["glossydistribution"]}

                        materialislinked = decalparams["Material"]["glossyislinked"]
                        subsetislinked = decalparams["Subset"]["glossyislinked"]

                    elif matchtype == "PBR":
                        materialparams = {"color": decalparams["Material"]["color"],
                                          "metallic": decalparams["Material"]["metallic"],
                                          "specular": decalparams["Material"]["specular"],
                                          "speculartint": decalparams["Material"]["speculartint"],
                                          "roughness": decalparams["Material"]["roughness"],
                                          "anisotropic": decalparams["Material"]["anisotropic"],
                                          "anisotropicrotation": decalparams["Material"]["anisotropicrotation"],
                                          "sheen": decalparams["Material"]["sheen"],
                                          "sheentint": decalparams["Material"]["sheentint"],
                                          "clearcoat": decalparams["Material"]["clearcoat"],
                                          "clearcoatroughness": decalparams["Material"]["clearcoatroughness"],
                                          "ior": decalparams["Material"]["ior"],
                                          "transmission": decalparams["Material"]["transmission"],
                                          "distribution": decalparams["Material"]["pbrdistribution"]}

                        subsetparams = {"color": decalparams["Subset"]["color"],
                                        "metallic": decalparams["Subset"]["metallic"],
                                        "specular": decalparams["Subset"]["specular"],
                                        "speculartint": decalparams["Subset"]["speculartint"],
                                        "roughness": decalparams["Subset"]["roughness"],
                                        "anisotropic": decalparams["Subset"]["anisotropic"],
                                        "anisotropicrotation": decalparams["Subset"]["anisotropicrotation"],
                                        "sheen": decalparams["Subset"]["sheen"],
                                        "sheentint": decalparams["Subset"]["sheentint"],
                                        "clearcoat": decalparams["Subset"]["clearcoat"],
                                        "clearcoatroughness": decalparams["Subset"]["clearcoatroughness"],
                                        "ior": decalparams["Subset"]["ior"],
                                        "transmission": decalparams["Subset"]["transmission"],
                                        "distribution": decalparams["Subset"]["pbrdistribution"]}

                        materialislinked = decalparams["Material"]["pbrislinked"]
                        subsetislinked = decalparams["Subset"]["pbrislinked"]

                    # checking if material params match is not enough, we also need to check if the shader nodes are actually connected
                    if materialislinked and subsetislinked:
                        if materialparams == targetparams and subsetparams == targetparams:
                            matchingmat = mat
                            break

                elif self.matchmaterial:
                    sourceparams = self.get_decalmat(decalmat)

                    # material part

                    if matchtype == "GLOSSY":
                        materialparams = {"color": decalparams["Material"]["color"],
                                          "roughness": decalparams["Material"]["roughness"],
                                          "distribution": decalparams["Material"]["glossydistribution"]}

                        materialislinked = decalparams["Material"]["glossyislinked"]

                    elif matchtype == "PBR":
                        materialparams = {"color": decalparams["Material"]["color"],
                                          "metallic": decalparams["Material"]["metallic"],
                                          "specular": decalparams["Material"]["specular"],
                                          "speculartint": decalparams["Material"]["speculartint"],
                                          "roughness": decalparams["Material"]["roughness"],
                                          "anisotropic": decalparams["Material"]["anisotropic"],
                                          "anisotropicrotation": decalparams["Material"]["anisotropicrotation"],
                                          "sheen": decalparams["Material"]["sheen"],
                                          "sheentint": decalparams["Material"]["sheentint"],
                                          "clearcoat": decalparams["Material"]["clearcoat"],
                                          "clearcoatroughness": decalparams["Material"]["clearcoatroughness"],
                                          "ior": decalparams["Material"]["ior"],
                                          "transmission": decalparams["Material"]["transmission"],
                                          "distribution": decalparams["Material"]["pbrdistribution"]}

                        materialislinked = decalparams["Material"]["pbrislinked"]

                    # subset part

                    subsetglossyparams = {"color": decalparams["Subset"]["color"],
                                          "roughness": decalparams["Subset"]["roughness"],
                                          "distribution": decalparams["Subset"]["glossydistribution"]}

                    subsetglossyislinked = decalparams["Subset"]["glossyislinked"]

                    sourcesubsetglossyparams = {"color": sourceparams["Subset"]["color"],
                                                "roughness": sourceparams["Subset"]["roughness"],
                                                "distribution": sourceparams["Subset"]["glossydistribution"]}

                    sourcesubsetglossyislinked = sourceparams["Subset"]["glossyislinked"]

                    subsetpbrparams = {"color": decalparams["Subset"]["color"],
                                       "metallic": decalparams["Subset"]["metallic"],
                                       "specular": decalparams["Subset"]["specular"],
                                       "speculartint": decalparams["Subset"]["speculartint"],
                                       "roughness": decalparams["Subset"]["roughness"],
                                       "anisotropic": decalparams["Subset"]["anisotropic"],
                                       "anisotropicrotation": decalparams["Subset"]["anisotropicrotation"],
                                       "sheen": decalparams["Subset"]["sheen"],
                                       "sheentint": decalparams["Subset"]["sheentint"],
                                       "clearcoat": decalparams["Subset"]["clearcoat"],
                                       "clearcoatroughness": decalparams["Subset"]["clearcoatroughness"],
                                       "ior": decalparams["Subset"]["ior"],
                                       "transmission": decalparams["Subset"]["transmission"],
                                       "distribution": decalparams["Subset"]["pbrdistribution"]}

                    subsetpbrislinked = decalparams["Subset"]["pbrislinked"]

                    sourcesubsetpbrparams = {"color": sourceparams["Subset"]["color"],
                                             "metallic": sourceparams["Subset"]["metallic"],
                                             "specular": sourceparams["Subset"]["specular"],
                                             "speculartint": sourceparams["Subset"]["speculartint"],
                                             "roughness": sourceparams["Subset"]["roughness"],
                                             "anisotropic": sourceparams["Subset"]["anisotropic"],
                                             "anisotropicrotation": sourceparams["Subset"]["anisotropicrotation"],
                                             "sheen": sourceparams["Subset"]["sheen"],
                                             "sheentint": sourceparams["Subset"]["sheentint"],
                                             "clearcoat": sourceparams["Subset"]["clearcoat"],
                                             "clearcoatroughness": sourceparams["Subset"]["clearcoatroughness"],
                                             "ior": sourceparams["Subset"]["ior"],
                                             "transmission": sourceparams["Subset"]["transmission"],
                                             "distribution": sourceparams["Subset"]["pbrdistribution"]}

                    sourcesubsetpbrislinked = sourceparams["Subset"]["pbrislinked"]

                    # determine match

                    if materialislinked:
                        if materialparams == targetparams:
                            # the currently evaluated subset material has a matching connected material node, but we also need to confirm if the unchanged subset part matches

                            if subsetglossyislinked and sourcesubsetglossyislinked:
                                if subsetglossyparams == sourcesubsetglossyparams:
                                    matchingmat = mat
                                    break
                            elif subsetpbrislinked and sourcesubsetpbrislinked:
                                if subsetpbrparams == sourcesubsetpbrparams:
                                    matchingmat = mat
                                    break

                elif self.match_subset_decal:
                    sourceparams = self.get_decalmat(decalmat)

                    # subset part

                    if matchtype == "GLOSSY":
                        subsetparams = {"color": decalparams["Subset"]["color"],
                                        "roughness": decalparams["Subset"]["roughness"],
                                        "distribution": decalparams["Subset"]["glossydistribution"]}

                        subsetislinked = decalparams["Subset"]["glossyislinked"]

                    elif matchtype == "PBR":
                        subsetparams = {"color": decalparams["Subset"]["color"],
                                        "metallic": decalparams["Subset"]["metallic"],
                                        "specular": decalparams["Subset"]["specular"],
                                        "speculartint": decalparams["Subset"]["speculartint"],
                                        "roughness": decalparams["Subset"]["roughness"],
                                        "anisotropic": decalparams["Subset"]["anisotropic"],
                                        "anisotropicrotation": decalparams["Subset"]["anisotropicrotation"],
                                        "sheen": decalparams["Subset"]["sheen"],
                                        "sheentint": decalparams["Subset"]["sheentint"],
                                        "clearcoat": decalparams["Subset"]["clearcoat"],
                                        "clearcoatroughness": decalparams["Subset"]["clearcoatroughness"],
                                        "ior": decalparams["Subset"]["ior"],
                                        "transmission": decalparams["Subset"]["transmission"],
                                        "distribution": decalparams["Subset"]["pbrdistribution"]}

                        subsetislinked = decalparams["Subset"]["pbrislinked"]

                    # material part

                    materialglossyparams = {"color": decalparams["Material"]["color"],
                                            "roughness": decalparams["Material"]["roughness"],
                                            "distribution": decalparams["Material"]["glossydistribution"]}

                    materialglossyislinked = decalparams["Material"]["glossyislinked"]

                    sourcematerialglossyparams = {"color": sourceparams["Material"]["color"],
                                                  "roughness": sourceparams["Material"]["roughness"],
                                                  "distribution": sourceparams["Material"]["glossydistribution"]}

                    sourcematerialglossyislinked = sourceparams["Material"]["glossyislinked"]

                    materialpbrparams = {"color": decalparams["Material"]["color"],
                                         "metallic": decalparams["Material"]["metallic"],
                                         "specular": decalparams["Material"]["specular"],
                                         "speculartint": decalparams["Material"]["speculartint"],
                                         "roughness": decalparams["Material"]["roughness"],
                                         "anisotropic": decalparams["Material"]["anisotropic"],
                                         "anisotropicrotation": decalparams["Material"]["anisotropicrotation"],
                                         "sheen": decalparams["Material"]["sheen"],
                                         "sheentint": decalparams["Material"]["sheentint"],
                                         "clearcoat": decalparams["Material"]["clearcoat"],
                                         "clearcoatroughness": decalparams["Material"]["clearcoatroughness"],
                                         "ior": decalparams["Material"]["ior"],
                                         "transmission": decalparams["Material"]["transmission"],
                                         "distribution": decalparams["Material"]["pbrdistribution"]}

                    materialpbrislinked = decalparams["Material"]["pbrislinked"]

                    sourcematerialpbrparams = {"color": sourceparams["Material"]["color"],
                                               "metallic": sourceparams["Material"]["metallic"],
                                               "specular": sourceparams["Material"]["specular"],
                                               "speculartint": sourceparams["Material"]["speculartint"],
                                               "roughness": sourceparams["Material"]["roughness"],
                                               "anisotropic": sourceparams["Material"]["anisotropic"],
                                               "anisotropicrotation": sourceparams["Material"]["anisotropicrotation"],
                                               "sheen": sourceparams["Material"]["sheen"],
                                               "sheentint": sourceparams["Material"]["sheentint"],
                                               "clearcoat": sourceparams["Material"]["clearcoat"],
                                               "clearcoatroughness": sourceparams["Material"]["clearcoatroughness"],
                                               "ior": sourceparams["Material"]["ior"],
                                               "transmission": sourceparams["Material"]["transmission"],
                                               "distribution": sourceparams["Material"]["pbrdistribution"]}

                    sourcematerialpbrislinked = sourceparams["Material"]["pbrislinked"]

                    # determine match

                    if subsetislinked:
                        if subsetparams == targetparams:
                            # the currently evaluated subset material has a matching connected subset node, but we also need to confirm if the unchanged material part matches

                            if materialglossyislinked and sourcematerialglossyislinked:
                                if materialglossyparams == sourcematerialglossyparams:
                                    matchingmat = mat
                                    break
                            elif materialpbrislinked and sourcematerialpbrislinked:
                                if materialpbrparams == sourcematerialpbrparams:
                                    matchingmat = mat
                                    break

            elif decalparams["Type"] == "PANEL":
                if not any([self.matchmaterial, self.matchside2]):  # Abort if neither of the panel options are ticked
                    return False

                if self.matchmaterial and self.matchside2:
                    if matchtype == "GLOSSY":
                        material1params = {"color": decalparams["Material 1"]["color"],
                                           "roughness": decalparams["Material 1"]["roughness"],
                                           "distribution": decalparams["Material 1"]["glossydistribution"]}

                        material2params = {"color": decalparams["Material 2"]["color"],
                                           "roughness": decalparams["Material 2"]["roughness"],
                                           "distribution": decalparams["Material 2"]["glossydistribution"]}

                        material1islinked = decalparams["Material 1"]["glossyislinked"]
                        material2islinked = decalparams["Material 2"]["glossyislinked"]

                    elif matchtype == "PBR":
                        material1params = {"color": decalparams["Material 1"]["color"],
                                           "metallic": decalparams["Material 1"]["metallic"],
                                           "specular": decalparams["Material 1"]["specular"],
                                           "speculartint": decalparams["Material 1"]["speculartint"],
                                           "roughness": decalparams["Material 1"]["roughness"],
                                           "anisotropic": decalparams["Material 1"]["anisotropic"],
                                           "anisotropicrotation": decalparams["Material 1"]["anisotropicrotation"],
                                           "sheen": decalparams["Material 1"]["sheen"],
                                           "sheentint": decalparams["Material 1"]["sheentint"],
                                           "clearcoat": decalparams["Material 1"]["clearcoat"],
                                           "clearcoatroughness": decalparams["Material 1"]["clearcoatroughness"],
                                           "ior": decalparams["Material 1"]["ior"],
                                           "transmission": decalparams["Material 1"]["transmission"],
                                           "distribution": decalparams["Material 1"]["pbrdistribution"]}

                        material2params = {"color": decalparams["Material 2"]["color"],
                                           "metallic": decalparams["Material 2"]["metallic"],
                                           "specular": decalparams["Material 2"]["specular"],
                                           "speculartint": decalparams["Material 2"]["speculartint"],
                                           "roughness": decalparams["Material 2"]["roughness"],
                                           "anisotropic": decalparams["Material 2"]["anisotropic"],
                                           "anisotropicrotation": decalparams["Material 2"]["anisotropicrotation"],
                                           "sheen": decalparams["Material 2"]["sheen"],
                                           "sheentint": decalparams["Material 2"]["sheentint"],
                                           "clearcoat": decalparams["Material 2"]["clearcoat"],
                                           "clearcoatroughness": decalparams["Material 2"]["clearcoatroughness"],
                                           "ior": decalparams["Material 2"]["ior"],
                                           "transmission": decalparams["Material 2"]["transmission"],
                                           "distribution": decalparams["Material 2"]["pbrdistribution"]}

                        material1islinked = decalparams["Material 1"]["pbrislinked"]
                        material2islinked = decalparams["Material 2"]["pbrislinked"]

                    if material1islinked and material2islinked:
                        if material1params == targetparams and material2params == targetparams:
                            matchingmat = mat
                            break

                # for panel decals there are always two ways to match, depending on the panel flip
                # which way, doesn't really matter, as you can just apply the reverse matching material and flip the panel
                elif self.matchmaterial or self.matchside2:
                    sourceparams = self.get_decalmat(decalmat)

                    material1glossyparams = {"color": decalparams["Material 1"]["color"],
                                             "roughness": decalparams["Material 1"]["roughness"],
                                             "distribution": decalparams["Material 1"]["glossydistribution"]}

                    material1glossyislinked = decalparams["Material 1"]["glossyislinked"]

                    sourcematerial1glossyparams = {"color": sourceparams["Material 1"]["color"],
                                                   "roughness": sourceparams["Material 1"]["roughness"],
                                                   "distribution": sourceparams["Material 1"]["glossydistribution"]}

                    sourcematerial1glossyislinked = sourceparams["Material 1"]["glossyislinked"]

                    material1pbrparams = {"color": decalparams["Material 1"]["color"],
                                          "metallic": decalparams["Material 1"]["metallic"],
                                          "specular": decalparams["Material 1"]["specular"],
                                          "speculartint": decalparams["Material 1"]["speculartint"],
                                          "roughness": decalparams["Material 1"]["roughness"],
                                          "anisotropic": decalparams["Material 1"]["anisotropic"],
                                          "anisotropicrotation": decalparams["Material 1"]["anisotropicrotation"],
                                          "sheen": decalparams["Material 1"]["sheen"],
                                          "sheentint": decalparams["Material 1"]["sheentint"],
                                          "clearcoat": decalparams["Material 1"]["clearcoat"],
                                          "clearcoatroughness": decalparams["Material 1"]["clearcoatroughness"],
                                          "ior": decalparams["Material 1"]["ior"],
                                          "transmission": decalparams["Material 1"]["transmission"],
                                          "distribution": decalparams["Material 1"]["pbrdistribution"]}

                    material1pbrislinked = decalparams["Material 1"]["pbrislinked"]

                    sourcematerial1pbrparams = {"color": sourceparams["Material 1"]["color"],
                                                "metallic": sourceparams["Material 1"]["metallic"],
                                                "specular": sourceparams["Material 1"]["specular"],
                                                "speculartint": sourceparams["Material 1"]["speculartint"],
                                                "roughness": sourceparams["Material 1"]["roughness"],
                                                "anisotropic": sourceparams["Material 1"]["anisotropic"],
                                                "anisotropicrotation": sourceparams["Material 1"]["anisotropicrotation"],
                                                "sheen": sourceparams["Material 1"]["sheen"],
                                                "sheentint": sourceparams["Material 1"]["sheentint"],
                                                "clearcoat": sourceparams["Material 1"]["clearcoat"],
                                                "clearcoatroughness": sourceparams["Material 1"]["clearcoatroughness"],
                                                "ior": sourceparams["Material 1"]["ior"],
                                                "transmission": sourceparams["Material 1"]["transmission"],
                                                "distribution": sourceparams["Material 1"]["pbrdistribution"]}

                    sourcematerial1pbrislinked = sourceparams["Material 1"]["pbrislinked"]

                    material2glossyparams = {"color": decalparams["Material 2"]["color"],
                                             "roughness": decalparams["Material 2"]["roughness"],
                                             "distribution": decalparams["Material 2"]["glossydistribution"]}

                    material2glossyislinked = decalparams["Material 2"]["glossyislinked"]

                    sourcematerial2glossyparams = {"color": sourceparams["Material 2"]["color"],
                                                   "roughness": sourceparams["Material 2"]["roughness"],
                                                   "distribution": sourceparams["Material 2"]["glossydistribution"]}

                    sourcematerial2glossyislinked = sourceparams["Material 2"]["glossyislinked"]

                    material2pbrparams = {"color": decalparams["Material 2"]["color"],
                                          "metallic": decalparams["Material 2"]["metallic"],
                                          "specular": decalparams["Material 2"]["specular"],
                                          "speculartint": decalparams["Material 2"]["speculartint"],
                                          "roughness": decalparams["Material 2"]["roughness"],
                                          "anisotropic": decalparams["Material 2"]["anisotropic"],
                                          "anisotropicrotation": decalparams["Material 2"]["anisotropicrotation"],
                                          "sheen": decalparams["Material 2"]["sheen"],
                                          "sheentint": decalparams["Material 2"]["sheentint"],
                                          "clearcoat": decalparams["Material 2"]["clearcoat"],
                                          "clearcoatroughness": decalparams["Material 2"]["clearcoatroughness"],
                                          "ior": decalparams["Material 2"]["ior"],
                                          "transmission": decalparams["Material 2"]["transmission"],
                                          "distribution": decalparams["Material 2"]["pbrdistribution"]}

                    material2pbrislinked = decalparams["Material 2"]["pbrislinked"]

                    sourcematerial2pbrparams = {"color": sourceparams["Material 2"]["color"],
                                                "metallic": sourceparams["Material 2"]["metallic"],
                                                "specular": sourceparams["Material 2"]["specular"],
                                                "speculartint": sourceparams["Material 2"]["speculartint"],
                                                "roughness": sourceparams["Material 2"]["roughness"],
                                                "anisotropic": sourceparams["Material 2"]["anisotropic"],
                                                "anisotropicrotation": sourceparams["Material 2"]["anisotropicrotation"],
                                                "sheen": sourceparams["Material 2"]["sheen"],
                                                "sheentint": sourceparams["Material 2"]["sheentint"],
                                                "clearcoat": sourceparams["Material 2"]["clearcoat"],
                                                "clearcoatroughness": sourceparams["Material 2"]["clearcoatroughness"],
                                                "ior": sourceparams["Material 2"]["ior"],
                                                "transmission": sourceparams["Material 2"]["transmission"],
                                                "distribution": sourceparams["Material 2"]["pbrdistribution"]}

                    sourcematerial2pbrislinked = sourceparams["Material 2"]["pbrislinked"]

                    if matchtype == "GLOSSY":
                        if material1glossyislinked:
                            if material1glossyparams == targetparams:
                                # the currently evaluated panel material has a matching connected material 1 node, but we also need to confirm if the unchanged marterial 2 part matches

                                if material2glossyislinked and sourcematerial2glossyislinked:
                                    if material2glossyparams == sourcematerial2glossyparams:
                                        matchingmat = mat
                                        break
                                elif material2pbrislinked and sourcematerial2pbrislinked:
                                    if material2pbrparams == sourcematerial2pbrparams:
                                        matchingmat = mat
                                        break
                    elif matchtype == "PBR":
                        if material1pbrislinked:
                            if material1pbrparams == targetparams:
                                # the currently evaluated panel material has a matching connected material 1 node, but we also need to confirm if the unchanged marterial 2 part matches

                                if material2glossyislinked and sourcematerial2glossyislinked:
                                    if material2glossyparams == sourcematerial2glossyparams:
                                        matchingmat = mat
                                        break
                                elif material2pbrislinked and sourcematerial2pbrislinked:
                                    if material2pbrparams == sourcematerial2pbrparams:
                                        matchingmat = mat
                                        break

                    # check the other way around

                    if matchtype == "GLOSSY":
                        if material2glossyislinked:
                            if material2glossyparams == targetparams:
                                # the currently evaluated panel material has a matching connected material 2 node, but we also need to confirm if the unchanged marterial 1 part matches

                                if material1glossyislinked and sourcematerial1glossyislinked:
                                    if material1glossyparams == sourcematerial1glossyparams:
                                        # print("match1")
                                        matchingmat = mat
                                        break
                                elif material1pbrislinked and sourcematerial1pbrislinked:
                                    if material1pbrparams == sourcematerial1pbrparams:
                                        # print("match1")
                                        matchingmat = mat
                                        break
                    elif matchtype == "PBR":
                        if material2pbrislinked:
                            if material2pbrparams == targetparams:
                                # the currently evaluated panel material has a matching connected material 2 node, but we also need to confirm if the unchanged marterial 1 part matches

                                if material1glossyislinked and sourcematerial1glossyislinked:
                                    if material1glossyparams == sourcematerial1glossyparams:
                                        # print("match1")
                                        matchingmat = mat
                                        break
                                elif material1pbrislinked and sourcematerial1pbrislinked:
                                    if material1pbrparams == sourcematerial1pbrparams:
                                        # print("match1")
                                        matchingmat = mat
                                        break

            elif decalparams["Type"] == "SUBTRACTOR":
                if matchtype == "GLOSSY":
                    materialparams = {"color": decalparams["Material"]["color"],
                                      "roughness": decalparams["Material"]["roughness"],
                                      "distribution": decalparams["Material"]["glossydistribution"]}

                    materialislinked = decalparams["Material"]["glossyislinked"]

                elif matchtype == "PBR":
                    materialparams = {"color": decalparams["Material"]["color"],
                                      "metallic": decalparams["Material"]["metallic"],
                                      "specular": decalparams["Material"]["specular"],
                                      "speculartint": decalparams["Material"]["speculartint"],
                                      "roughness": decalparams["Material"]["roughness"],
                                      "anisotropic": decalparams["Material"]["anisotropic"],
                                      "anisotropicrotation": decalparams["Material"]["anisotropicrotation"],
                                      "sheen": decalparams["Material"]["sheen"],
                                      "sheentint": decalparams["Material"]["sheentint"],
                                      "clearcoat": decalparams["Material"]["clearcoat"],
                                      "clearcoatroughness": decalparams["Material"]["clearcoatroughness"],
                                      "ior": decalparams["Material"]["ior"],
                                      "transmission": decalparams["Material"]["transmission"],
                                      "distribution": decalparams["Material"]["pbrdistribution"]}

                    materialislinked = decalparams["Material"]["pbrislinked"]

                if materialislinked:
                    if materialparams == targetparams:
                        matchingmat = mat
                        break

        return matchingmat

    def get_decalmat(self, decalmat):
        decalgroup = decalmat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node
        groupname = decalgroup.node_tree.name

        if "Subset" in groupname:
            self.decaltype = "SUBSET"
            decalmatdict = {"Type": "SUBSET"}

            # fetch Material params
            color = decalgroup.inputs["Material Color"].links[0].from_socket.default_value[:3]
            metallic = decalgroup.inputs["Material Metallic"].default_value
            specular = decalgroup.inputs["Material Specular"].default_value
            speculartint = decalgroup.inputs["Material Specular Tint"].default_value
            roughness = decalgroup.inputs["Material Roughness"].default_value
            anisotropic = decalgroup.inputs["Material Anisotropic"].default_value
            anisotropicrotation = decalgroup.inputs["Material Anisotropic Rotation"].default_value
            sheen = decalgroup.inputs["Material Sheen"].default_value
            sheentint = decalgroup.inputs["Material Sheen Tint"].default_value
            clearcoat = decalgroup.inputs["Material Clearcoat"].default_value
            clearcoatroughness = decalgroup.inputs["Material Clearcoat Roughness"].default_value
            ior = decalgroup.inputs["Material IOR"].default_value
            transmission = decalgroup.inputs["Material Transmission"].default_value

            glossydistribution = decalgroup.node_tree.nodes['Glossy BSDF'].distribution
            pbrdistribution = decalgroup.node_tree.nodes['Principled BSDF'].distribution

            glossyislinked = decalgroup.node_tree.nodes['Glossy BSDF'].outputs['BSDF'].is_linked
            pbrislinked = decalgroup.node_tree.nodes['Principled BSDF'].outputs['BSDF'].is_linked

            decalmatdict["Material"] = {"color": color,
                                        "metallic": metallic,
                                        "specular": specular,
                                        "speculartint": speculartint,
                                        "roughness": roughness,
                                        "anisotropic": anisotropic,
                                        "anisotropicrotation": anisotropicrotation,
                                        "sheen": sheen,
                                        "sheentint": sheentint,
                                        "clearcoat": clearcoat,
                                        "clearcoatroughness": clearcoatroughness,
                                        "ior": ior,
                                        "transmission": transmission,
                                        "glossydistribution": glossydistribution,
                                        "pbrdistribution": pbrdistribution,
                                        "glossyislinked": glossyislinked,
                                        "pbrislinked": pbrislinked}

            # fetch Subset params
            color = decalgroup.inputs["Subset Color"].links[0].from_socket.default_value[:3]
            metallic = decalgroup.inputs["Subset Metallic"].default_value
            specular = decalgroup.inputs["Subset Specular"].default_value
            speculartint = decalgroup.inputs["Subset Specular Tint"].default_value
            roughness = decalgroup.inputs["Subset Roughness"].default_value
            anisotropic = decalgroup.inputs["Subset Anisotropic"].default_value
            anisotropicrotation = decalgroup.inputs["Subset Anisotropic Rotation"].default_value
            sheen = decalgroup.inputs["Subset Sheen"].default_value
            sheentint = decalgroup.inputs["Subset Sheen Tint"].default_value
            clearcoat = decalgroup.inputs["Subset Clearcoat"].default_value
            clearcoatroughness = decalgroup.inputs["Subset Clearcoat Roughness"].default_value
            ior = decalgroup.inputs["Subset IOR"].default_value
            transmission = decalgroup.inputs["Subset Transmission"].default_value

            glossydistribution = decalgroup.node_tree.nodes['Glossy BSDF.001'].distribution
            pbrdistribution = decalgroup.node_tree.nodes['Principled BSDF.001'].distribution

            glossyislinked = decalgroup.node_tree.nodes['Glossy BSDF.001'].outputs['BSDF'].is_linked
            pbrislinked = decalgroup.node_tree.nodes['Principled BSDF.001'].outputs['BSDF'].is_linked

            decalmatdict["Subset"] = {"color": color,
                                      "metallic": metallic,
                                      "specular": specular,
                                      "speculartint": speculartint,
                                      "roughness": roughness,
                                      "anisotropic": anisotropic,
                                      "anisotropicrotation": anisotropicrotation,
                                      "sheen": sheen,
                                      "sheentint": sheentint,
                                      "clearcoat": clearcoat,
                                      "clearcoatroughness": clearcoatroughness,
                                      "ior": ior,
                                      "transmission": transmission,
                                      "glossydistribution": glossydistribution,
                                      "pbrdistribution": pbrdistribution,
                                      "glossyislinked": glossyislinked,
                                      "pbrislinked": pbrislinked}

        elif "Panel" in groupname:
            self.decaltype = "PANEL"
            decalmatdict = {"Type": "PANEL"}

            # fetch Material 1 params
            color = decalgroup.inputs["Material 1 Color"].links[0].from_socket.default_value[:3]
            metallic = decalgroup.inputs["Material 1 Metallic"].default_value
            specular = decalgroup.inputs["Material 1 Specular"].default_value
            speculartint = decalgroup.inputs["Material 1 Specular Tint"].default_value
            roughness = decalgroup.inputs["Material 1 Roughness"].default_value
            anisotropic = decalgroup.inputs["Material 1 Anisotropic"].default_value
            anisotropicrotation = decalgroup.inputs["Material 1 Anisotropic Rotation"].default_value
            sheen = decalgroup.inputs["Material 1 Sheen"].default_value
            sheentint = decalgroup.inputs["Material 1 Sheen Tint"].default_value
            clearcoat = decalgroup.inputs["Material 1 Clearcoat"].default_value
            clearcoatroughness = decalgroup.inputs["Material 1 Clearcoat Roughness"].default_value
            ior = decalgroup.inputs["Material 1 IOR"].default_value
            transmission = decalgroup.inputs["Material 1 Transmission"].default_value

            glossydistribution = decalgroup.node_tree.nodes['Glossy BSDF'].distribution
            pbrdistribution = decalgroup.node_tree.nodes['Principled BSDF'].distribution

            glossyislinked = decalgroup.node_tree.nodes['Glossy BSDF'].outputs['BSDF'].is_linked
            pbrislinked = decalgroup.node_tree.nodes['Principled BSDF'].outputs['BSDF'].is_linked

            decalmatdict["Material 1"] = {"color": color,
                                          "metallic": metallic,
                                          "specular": specular,
                                          "speculartint": speculartint,
                                          "roughness": roughness,
                                          "anisotropic": anisotropic,
                                          "anisotropicrotation": anisotropicrotation,
                                          "sheen": sheen,
                                          "sheentint": sheentint,
                                          "clearcoat": clearcoat,
                                          "clearcoatroughness": clearcoatroughness,
                                          "ior": ior,
                                          "transmission": transmission,
                                          "glossydistribution": glossydistribution,
                                          "pbrdistribution": pbrdistribution,
                                          "glossyislinked": glossyislinked,
                                          "pbrislinked": pbrislinked}

            # fetch Material 2 params
            color = decalgroup.inputs["Material 2 Color"].links[0].from_socket.default_value[:3]
            metallic = decalgroup.inputs["Material 2 Metallic"].default_value
            specular = decalgroup.inputs["Material 2 Specular"].default_value
            speculartint = decalgroup.inputs["Material 2 Specular Tint"].default_value
            roughness = decalgroup.inputs["Material 2 Roughness"].default_value
            anisotropic = decalgroup.inputs["Material 2 Anisotropic"].default_value
            anisotropicrotation = decalgroup.inputs["Material 2 Anisotropic Rotation"].default_value
            sheen = decalgroup.inputs["Material 2 Sheen"].default_value
            sheentint = decalgroup.inputs["Material 2 Sheen Tint"].default_value
            clearcoat = decalgroup.inputs["Material 2 Clearcoat"].default_value
            clearcoatroughness = decalgroup.inputs["Material 2 Clearcoat Roughness"].default_value
            ior = decalgroup.inputs["Material 2 IOR"].default_value
            transmission = decalgroup.inputs["Material 2 Transmission"].default_value

            glossydistribution = decalgroup.node_tree.nodes['Glossy BSDF.001'].distribution
            pbrdistribution = decalgroup.node_tree.nodes['Principled BSDF.001'].distribution

            glossyislinked = decalgroup.node_tree.nodes['Glossy BSDF.001'].outputs['BSDF'].is_linked
            pbrislinked = decalgroup.node_tree.nodes['Principled BSDF.001'].outputs['BSDF'].is_linked

            decalmatdict["Material 2"] = {"color": color,
                                          "metallic": metallic,
                                          "specular": specular,
                                          "speculartint": speculartint,
                                          "roughness": roughness,
                                          "anisotropic": anisotropic,
                                          "anisotropicrotation": anisotropicrotation,
                                          "sheen": sheen,
                                          "sheentint": sheentint,
                                          "clearcoat": clearcoat,
                                          "clearcoatroughness": clearcoatroughness,
                                          "ior": ior,
                                          "transmission": transmission,
                                          "glossydistribution": glossydistribution,
                                          "pbrdistribution": pbrdistribution,
                                          "glossyislinked": glossyislinked,
                                          "pbrislinked": pbrislinked}

        elif "Info" in groupname:
            self.decaltype = "INFO"
            self.report({'ERROR'}, "Material: '%s' - Info Decals can't be matched!" % (decalmat.name))
            return

        else:  # they are called 'Decal Substractor Group' or just 'Decal Group' in the original decals
            self.decaltype = "SUBTRACTOR"
            self.matchmaterial = True

            decalmatdict = {"Type": "SUBTRACTOR"}

            # fetch Material params
            color = decalgroup.inputs["Material Color"].links[0].from_socket.default_value[:3]
            metallic = decalgroup.inputs["Material Metallic"].default_value
            specular = decalgroup.inputs["Material Specular"].default_value
            speculartint = decalgroup.inputs["Material Specular Tint"].default_value
            roughness = decalgroup.inputs["Material Roughness"].default_value
            anisotropic = decalgroup.inputs["Material Anisotropic"].default_value
            anisotropicrotation = decalgroup.inputs["Material Anisotropic Rotation"].default_value
            sheen = decalgroup.inputs["Material Sheen"].default_value
            sheentint = decalgroup.inputs["Material Sheen Tint"].default_value
            clearcoat = decalgroup.inputs["Material Clearcoat"].default_value
            clearcoatroughness = decalgroup.inputs["Material Clearcoat Roughness"].default_value
            ior = decalgroup.inputs["Material IOR"].default_value
            transmission = decalgroup.inputs["Material Transmission"].default_value

            glossydistribution = decalgroup.node_tree.nodes['Glossy BSDF'].distribution
            pbrdistribution = decalgroup.node_tree.nodes['Principled BSDF'].distribution

            glossyislinked = decalgroup.node_tree.nodes['Glossy BSDF'].outputs['BSDF'].is_linked
            pbrislinked = decalgroup.node_tree.nodes['Principled BSDF'].outputs['BSDF'].is_linked

            decalmatdict["Material"] = {"color": color,
                                        "metallic": metallic,
                                        "specular": specular,
                                        "speculartint": speculartint,
                                        "roughness": roughness,
                                        "anisotropic": anisotropic,
                                        "anisotropicrotation": anisotropicrotation,
                                        "sheen": sheen,
                                        "sheentint": sheentint,
                                        "clearcoat": clearcoat,
                                        "clearcoatroughness": clearcoatroughness,
                                        "ior": ior,
                                        "transmission": transmission,
                                        "glossydistribution": glossydistribution,
                                        "pbrdistribution": pbrdistribution,
                                        "glossyislinked": glossyislinked,
                                        "pbrislinked": pbrislinked}

        return decalmatdict

    def match_subtractor_decal(self, decalgroup, targetparams, matchtype, m3prop=None):
        tree = decalgroup.node_tree

        if self.matchmaterial:
            color = decalgroup.inputs['Material Color'].links[0].from_socket
            roughness = decalgroup.inputs['Material Roughness']
            if matchtype == "PBR":
                metallic = decalgroup.inputs['Material Metallic']
                specular = decalgroup.inputs['Material Specular']
                speculartint = decalgroup.inputs['Material Specular Tint']
                anisotropic = decalgroup.inputs['Material Anisotropic']
                anisotropicrotation = decalgroup.inputs['Material Anisotropic Rotation']
                sheen = decalgroup.inputs['Material Sheen']
                sheentint = decalgroup.inputs['Material Sheen Tint']
                clearcoat = decalgroup.inputs['Material Clearcoat']
                clearcoatroughness = decalgroup.inputs['Material Clearcoat Roughness']
                ior = decalgroup.inputs['Material IOR']
                transmission = decalgroup.inputs['Material Transmission']

            # match params
            color.default_value = (targetparams["color"][0], targetparams["color"][1], targetparams["color"][2], 1)
            roughness.default_value = targetparams["roughness"]
            if matchtype == "PBR":
                metallic.default_value = targetparams["metallic"]
                specular.default_value = targetparams["specular"]
                speculartint.default_value = targetparams["speculartint"]
                anisotropic.default_value = targetparams["anisotropic"]
                anisotropicrotation.default_value = targetparams["anisotropicrotation"]
                sheen.default_value = targetparams["sheen"]
                sheentint.default_value = targetparams["sheentint"]
                clearcoat.default_value = targetparams["clearcoat"]
                clearcoatroughness.default_value = targetparams["clearcoatroughness"]
                ior.default_value = targetparams["ior"]
                transmission.default_value = targetparams["transmission"]

            if matchtype == "GLOSSY":
                shadernode = tree.nodes["Glossy BSDF"]
            elif matchtype == "PBR":
                shadernode = tree.nodes["Principled BSDF"]

            # match distribution
            shadernode.distribution = targetparams["distribution"]

            # add the m3 id property
            if matchtype == "PBR" and m3prop:
                shadernode["M3"] = m3prop

            # make sure shader shader node is connected to the mix shader
            shaderoutput = shadernode.outputs['BSDF']
            mixshaderinput = tree.nodes["Mix Shader"].inputs[1]
            tree.links.new(shaderoutput, mixshaderinput)

    def match_subset_decal(self, decalgroup, targetparams, matchtype, m3prop=None):
        tree = decalgroup.node_tree

        if self.matchmaterial:
            color = decalgroup.inputs['Material Color'].links[0].from_socket
            roughness = decalgroup.inputs['Material Roughness']
            if matchtype == "PBR":
                metallic = decalgroup.inputs['Material Metallic']
                specular = decalgroup.inputs['Material Specular']
                speculartint = decalgroup.inputs['Material Specular Tint']
                anisotropic = decalgroup.inputs['Material Anisotropic']
                anisotropicrotation = decalgroup.inputs['Material Anisotropic Rotation']
                sheen = decalgroup.inputs['Material Sheen']
                sheentint = decalgroup.inputs['Material Sheen Tint']
                clearcoat = decalgroup.inputs['Material Clearcoat']
                clearcoatroughness = decalgroup.inputs['Material Clearcoat Roughness']
                ior = decalgroup.inputs['Material IOR']
                transmission = decalgroup.inputs['Material Transmission']

            # match params
            color.default_value = (targetparams["color"][0], targetparams["color"][1], targetparams["color"][2], 1)
            roughness.default_value = targetparams["roughness"]
            if matchtype == "PBR":
                metallic.default_value = targetparams["metallic"]
                specular.default_value = targetparams["specular"]
                speculartint.default_value = targetparams["speculartint"]
                anisotropic.default_value = targetparams["anisotropic"]
                anisotropicrotation.default_value = targetparams["anisotropicrotation"]
                sheen.default_value = targetparams["sheen"]
                sheentint.default_value = targetparams["sheentint"]
                clearcoat.default_value = targetparams["clearcoat"]
                clearcoatroughness.default_value = targetparams["clearcoatroughness"]
                ior.default_value = targetparams["ior"]
                transmission.default_value = targetparams["transmission"]

            if matchtype == "GLOSSY":
                shadernode = tree.nodes["Glossy BSDF"]
            elif matchtype == "PBR":
                shadernode = tree.nodes["Principled BSDF"]

            # match distribution
            shadernode.distribution = targetparams["distribution"]

            # add the m3 id property
            if matchtype == "PBR" and m3prop:
                shadernode["M3"] = m3prop

            # make sure shader shader node is connected to the mix shader
            shaderoutput = shadernode.outputs['BSDF']
            mixshaderinput = tree.nodes["Mix Shader.001"].inputs[1]
            tree.links.new(shaderoutput, mixshaderinput)

        if self.matchsubset:
            color = decalgroup.inputs['Subset Color'].links[0].from_socket
            roughness = decalgroup.inputs['Subset Roughness']
            if matchtype == "PBR":
                metallic = decalgroup.inputs['Subset Metallic']
                specular = decalgroup.inputs['Subset Specular']
                speculartint = decalgroup.inputs['Subset Specular Tint']
                anisotropic = decalgroup.inputs['Subset Anisotropic']
                anisotropicrotation = decalgroup.inputs['Subset Anisotropic Rotation']
                sheen = decalgroup.inputs['Subset Sheen']
                sheentint = decalgroup.inputs['Subset Sheen Tint']
                clearcoat = decalgroup.inputs['Subset Clearcoat']
                clearcoatroughness = decalgroup.inputs['Subset Clearcoat Roughness']
                ior = decalgroup.inputs['Subset IOR']
                transmission = decalgroup.inputs['Subset Transmission']

            # match params
            color.default_value = (targetparams["color"][0], targetparams["color"][1], targetparams["color"][2], 1)
            roughness.default_value = targetparams["roughness"]
            if matchtype == "PBR":
                metallic.default_value = targetparams["metallic"]
                specular.default_value = targetparams["specular"]
                speculartint.default_value = targetparams["speculartint"]
                anisotropic.default_value = targetparams["anisotropic"]
                anisotropicrotation.default_value = targetparams["anisotropicrotation"]
                sheen.default_value = targetparams["sheen"]
                sheentint.default_value = targetparams["sheentint"]
                clearcoat.default_value = targetparams["clearcoat"]
                clearcoatroughness.default_value = targetparams["clearcoatroughness"]
                ior.default_value = targetparams["ior"]
                transmission.default_value = targetparams["transmission"]

            if matchtype == "GLOSSY":
                shadernode = tree.nodes["Glossy BSDF.001"]
            elif matchtype == "PBR":
                shadernode = tree.nodes["Principled BSDF.001"]

            # match distribution
            shadernode.distribution = targetparams["distribution"]

            # add the m3 id property
            if matchtype == "PBR" and m3prop:
                shadernode["M3"] = m3prop

            # make sure shader node is connected to the mix shader
            shaderoutput = shadernode.outputs['BSDF']
            mixshaderinput = tree.nodes["Mix Shader.001"].inputs[2]
            tree.links.new(shaderoutput, mixshaderinput)

    def match_panel_decal(self, decalgroup, targetparams, matchtype, m3prop=None):
        tree = decalgroup.node_tree

        if self.matchmaterial:
            color = decalgroup.inputs['Material 1 Color'].links[0].from_socket
            roughness = decalgroup.inputs['Material 1 Roughness']
            if matchtype == "PBR":
                metallic = decalgroup.inputs['Material 1 Metallic']
                specular = decalgroup.inputs['Material 1 Specular']
                speculartint = decalgroup.inputs['Material 1 Specular Tint']
                anisotropic = decalgroup.inputs['Material 1 Anisotropic']
                anisotropicrotation = decalgroup.inputs['Material 1 Anisotropic Rotation']
                sheen = decalgroup.inputs['Material 1 Sheen']
                sheentint = decalgroup.inputs['Material 1 Sheen Tint']
                clearcoat = decalgroup.inputs['Material 1 Clearcoat']
                clearcoatroughness = decalgroup.inputs['Material 1 Clearcoat Roughness']
                ior = decalgroup.inputs['Material 1 IOR']
                transmission = decalgroup.inputs['Material 1 Transmission']

            # match params
            color.default_value = (targetparams["color"][0], targetparams["color"][1], targetparams["color"][2], 1)
            roughness.default_value = targetparams["roughness"]
            if matchtype == "PBR":
                metallic.default_value = targetparams["metallic"]
                specular.default_value = targetparams["specular"]
                speculartint.default_value = targetparams["speculartint"]
                anisotropic.default_value = targetparams["anisotropic"]
                anisotropicrotation.default_value = targetparams["anisotropicrotation"]
                sheen.default_value = targetparams["sheen"]
                sheentint.default_value = targetparams["sheentint"]
                clearcoat.default_value = targetparams["clearcoat"]
                clearcoatroughness.default_value = targetparams["clearcoatroughness"]
                ior.default_value = targetparams["ior"]
                transmission.default_value = targetparams["transmission"]

            if matchtype == "GLOSSY":
                shadernode = tree.nodes["Glossy BSDF"]
            elif matchtype == "PBR":
                shadernode = tree.nodes["Principled BSDF"]

            # match distribution
            shadernode.distribution = targetparams["distribution"]

            # add the m3 id property
            if matchtype == "PBR" and m3prop:
                shadernode["M3"] = m3prop

            # make sure shader shader node is connected to the mix shader
            shaderoutput = shadernode.outputs['BSDF']
            mixshaderinput = tree.nodes["Mix Shader.001"].inputs[1]
            tree.links.new(shaderoutput, mixshaderinput)

        if self.matchside2:
            color = decalgroup.inputs['Material 2 Color'].links[0].from_socket
            roughness = decalgroup.inputs['Material 2 Roughness']
            if matchtype == "PBR":
                metallic = decalgroup.inputs['Material 2 Metallic']
                specular = decalgroup.inputs['Material 2 Specular']
                speculartint = decalgroup.inputs['Material 2 Specular Tint']
                anisotropic = decalgroup.inputs['Material 2 Anisotropic']
                anisotropicrotation = decalgroup.inputs['Material 2 Anisotropic Rotation']
                sheen = decalgroup.inputs['Material 2 Sheen']
                sheentint = decalgroup.inputs['Material 2 Sheen Tint']
                clearcoat = decalgroup.inputs['Material 2 Clearcoat']
                clearcoatroughness = decalgroup.inputs['Material 2 Clearcoat Roughness']
                ior = decalgroup.inputs['Material 2 IOR']
                transmission = decalgroup.inputs['Material 2 Transmission']

            # match params
            color.default_value = (targetparams["color"][0], targetparams["color"][1], targetparams["color"][2], 1)
            roughness.default_value = targetparams["roughness"]
            if matchtype == "PBR":
                metallic.default_value = targetparams["metallic"]
                specular.default_value = targetparams["specular"]
                speculartint.default_value = targetparams["speculartint"]
                anisotropic.default_value = targetparams["anisotropic"]
                anisotropicrotation.default_value = targetparams["anisotropicrotation"]
                sheen.default_value = targetparams["sheen"]
                sheentint.default_value = targetparams["sheentint"]
                clearcoat.default_value = targetparams["clearcoat"]
                clearcoatroughness.default_value = targetparams["clearcoatroughness"]
                ior.default_value = targetparams["ior"]
                transmission.default_value = targetparams["transmission"]

            if matchtype == "GLOSSY":
                shadernode = tree.nodes["Glossy BSDF.001"]
            elif matchtype == "PBR":
                shadernode = tree.nodes["Principled BSDF.001"]

            # match distribution
            shadernode.distribution = targetparams["distribution"]

            # add the m3 id property
            if matchtype == "PBR" and m3prop:
                shadernode["M3"] = m3prop

            # make sure shader node is connected to the mix shader
            shaderoutput = shadernode.outputs['BSDF']
            mixshaderinput = tree.nodes["Mix Shader.001"].inputs[2]
            tree.links.new(shaderoutput, mixshaderinput)

    def match(self, decalmat, targetparams, matchtype, m3prop=None):
        decalgroup = decalmat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node

        # always get rid of decal group duplicates, as we don't want to influence any other materials, ever
        if decalgroup.node_tree.users > 1:
            decalgroup.node_tree = decalgroup.node_tree.copy()

        groupname = decalgroup.node_tree.name

        if "Subset" in groupname:
            self.decaltype = "SUBSET"
            self.match_subset_decal(decalgroup, targetparams, matchtype, m3prop)
        elif "Panel" in groupname:
            self.decaltype = "PANEL"
            self.match_panel_decal(decalgroup, targetparams, matchtype, m3prop)
        elif "Info" in groupname:
            self.report({'ERROR'}, "Material: '%s' - Info Decals can't be matched!" % (decalmat.name))
            return {'FINISHED'}
        else:  # they are called 'Decal Substractor Group' or just 'Decal Group' in the original decals
            self.decaltype = "SUBSTRACTOR"
            self.matchmaterial = True
            self.match_subtractor_decal(decalgroup, targetparams, matchtype, m3prop)

    def get_pbr(self, pbrshader):
        distribution = pbrshader.distribution
        color = pbrshader.inputs['Base Color'].default_value[:3]
        metallic = pbrshader.inputs['Metallic'].default_value
        specular = pbrshader.inputs['Specular'].default_value
        speculartint = pbrshader.inputs['Specular Tint'].default_value
        roughness = pbrshader.inputs['Roughness'].default_value
        anisotropic = pbrshader.inputs['Anisotropic'].default_value
        anisotropicrotation = pbrshader.inputs['Anisotropic Rotation'].default_value
        sheen = pbrshader.inputs['Sheen'].default_value
        sheentint = pbrshader.inputs['Sheen Tint'].default_value
        clearcoat = pbrshader.inputs['Clearcoat'].default_value
        clearcoatroughness = pbrshader.inputs['Clearcoat Roughness'].default_value
        ior = pbrshader.inputs['IOR'].default_value
        transmission = pbrshader.inputs['Transmission'].default_value

        shaderdict = {"distribution": distribution,
                      "color": color,
                      "metallic": metallic,
                      "specular": specular,
                      "speculartint": speculartint,
                      "roughness": roughness,
                      "anisotropic": anisotropic,
                      "anisotropicrotation": anisotropicrotation,
                      "sheen": sheen,
                      "sheentint": sheentint,
                      "clearcoat": clearcoat,
                      "clearcoatroughness": clearcoatroughness,
                      "ior": ior,
                      "transmission": transmission}

        try:
            m3prop = pbrshader['M3']
        except:
            m3prop = None

        return shaderdict, m3prop

    def get_glossy(self, glossyshader):
        distribution = glossyshader.distribution
        color = glossyshader.inputs['Color'].default_value[:3]
        roughness = glossyshader.inputs['Roughness'].default_value

        shaderdict = {"distribution": distribution,
                      "color": color,
                      "roughness": roughness}

        return shaderdict


def match_material_old(self):
    selection = m3.selected_objects()

    if len(selection) == 2:
        target = m3.get_active()
        selection.remove(target)
        decal = selection[0]

        decalmat = decal.material_slots[-1].material

        try:
            targetmat = target.material_slots[-1].material
        except:
            self.report({'ERROR'}, "Target has no material applied!")
            return

        # check if target material is compatible
        # it needs to have a glossy shader and have use_nodes enabled
        targetcompatible = False
        if targetmat.use_nodes:
            for node in targetmat.node_tree.nodes:
                if "Glossy BSDF" in node.name:
                    targetcompatible = True
                    # colorr, colorg, colorb, colora = node.inputs[0].default_value
                    targetcolor = node.inputs[0].default_value
                    targetrough = node.inputs[1].default_value
            if not targetcompatible:
                self.report({'ERROR'}, "Material matching currently only supports Cycle's Glossy Shaders. Glossy shader not found in material '%s'" % (targetmat.name))
        else:
            self.report({'ERROR'}, "Enable 'use nodes' for your matching material. 'Use nodes' is currently disabled for material '%s'." % (targetmat.name))

        # assign or create and assign a matching material
        # first we create the material base name, without potential instance/duplicate numeration like '.001' etc
        if targetcompatible:
            if "." in decalmat.name:
                decalmatbasename = decalmat.name[:-4]
            else:
                decalmatbasename = decalmat.name

            # looking for an existing material that matches our needs(the same color and roughness like the target)
            existingmatch = False
            for mat in bpy.data.materials:
                if decalmatbasename in mat.name:
                    if "decal" in decalmat.name:
                        matcolor1 = mat.node_tree.nodes['RGB'].outputs["Color"].default_value
                        try:
                            matcolor2 = mat.node_tree.nodes['RGB.001'].outputs["Color"].default_value
                        except:
                            matcolor2 = None
                        matrough1 = mat.node_tree.nodes['Group'].inputs["Material Roughness"].default_value
                        if matcolor2 is not None:
                            matrough2 = mat.node_tree.nodes['Group'].inputs["Subset Roughness"].default_value
                    elif "paneling" in decalmat.name:
                        matcolor1 = mat.node_tree.nodes['RGB'].outputs["Color"].default_value
                        matcolor2 = mat.node_tree.nodes['RGB.001'].outputs["Color"].default_value
                        matrough1 = mat.node_tree.nodes['Group'].inputs["Material 1 Roughness"].default_value
                        matrough2 = mat.node_tree.nodes['Group'].inputs["Material 2 Roughness"].default_value

                    if "paneling" in decalmat.name or "decal" in decalmat.name:
                        if tuple(matcolor1) == tuple(targetcolor):
                            if matcolor2 is None:
                                # subtractor color match
                                if matrough1 == targetrough:
                                    # subtractor roughness match
                                    if decalmat == mat:
                                        print("Decal and target materials are already matching!")
                                        existingmatch = True
                                    else:
                                        # if a color and rougness match, we assign the matching material
                                        print("A matching material for this decal exists already! Assigning '%s'." % (mat.name))
                                        existingmatch = True
                                        decal.material_slots[-1].material = mat
                            else:
                                if tuple(matcolor1) != (tuple(matcolor2)):  # because if its they are the same, we dont want to apply it using vmatch! this is what set material is for!
                                    # subset/paneling color match!
                                    if matrough1 == targetrough:
                                        # if matrough1 != matrough2:
                                        # subset/paneling roughness match!
                                        if decalmat == mat:
                                            print("Decal and target materials are already matching!")
                                            existingmatch = True
                                        else:
                                            # if a color and rougness match, we assign the matching material
                                            print("A matching material for this decal exists already! Assigning '%s'." % (mat.name))
                                            existingmatch = True
                                            decal.material_slots[-1].material = mat

            if existingmatch is False:
                # create a new material, assign it and change its color and roughness to be the same as the target
                dupmat = decalmat.copy()
                decal.material_slots[-1].material = dupmat
                print("A new material for this decal was created! Assigning '%s'." % (dupmat.name))

                if "paneling" in dupmat.name:
                    dupmat.node_tree.nodes['RGB'].outputs["Color"].default_value = targetcolor
                    dupmat.node_tree.nodes['Group'].inputs["Material 1 Roughness"].default_value = targetrough
                if "decal" in dupmat.name:
                    dupmat.node_tree.nodes['RGB'].outputs["Color"].default_value = targetcolor
                    dupmat.node_tree.nodes['Group'].inputs["Material Roughness"].default_value = targetrough

        target.select = False
        decal.select = False

    else:
        self.report({'ERROR'}, "Select exactly two objects: the decal and the target to receive the material from!")
