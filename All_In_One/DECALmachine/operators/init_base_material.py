import bpy
from .. import M3utils as m3


class InitBaseMaterial(bpy.types.Operator):
    bl_idname = "machin3.init_base_material"
    bl_label = "MACHIN3: Init Base Material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = m3.selected_objects()

        init_base_material(selection, clearout=True)

        return {'FINISHED'}


def init_base_material(selection, clearout=False):
    # there's 3 possible scenarios:
    # 1. no material slots > add slot and base material
    # 2. material slot but no material > add base material
    # 3. material slot and material > only add base material when clearout is True, which also gets rid of all existing slots
    #    because we init_base_material will be fired automatically with clearout=false by decal_project and decal_slice
    #    launching it from the pie manually will fire it with clearnout = True and so get rid of all existing materials

    for obj in selection:
        if obj.type == "MESH":
            m3.make_active(obj)

            if clearout:  # remove all slots
                print("Removing any existing materials from '%s'." % (obj.name))
                for slot in obj.material_slots:
                    bpy.ops.object.material_slot_remove()

            # adding one slot, if there isn't any
            if len(obj.material_slots) == 0:
                bpy.ops.object.material_slot_add()

            # only look for and apply base material, if there's no material applied already
            if obj.material_slots[0].material is None:
                # look for existing material called 'base'
                basemat = None
                basematname = "base"
                for mat in bpy.data.materials:
                    if mat.name == basematname:
                        print("Found existing '%s' material in scene." % (basematname))
                        basemat = mat
                        break

                # create 'base' material from scratch
                if not basemat:
                    if bpy.app.version >= (2, 79, 0):
                        basemat = create_base_mat(basematname)
                    else:
                        basemat = create_base_mat_old(basematname)

                # if obj.material_slots[0].material is None:
                print("Applying '%s' material." % (basematname))
                obj.material_slots[0].material = basemat

                # MACHIN3tools material viewport compensation
                if bpy.app.version >= (2, 79, 0):
                    if m3.M3_check():
                        if m3.M3_prefs().viewportcompensation:
                            bpy.ops.machin3.adjust_principled_pbr_node(isdecal=False)


def create_base_mat(basematname):
    print("Creating new '%s' material." % (basematname))
    basemat = bpy.data.materials.new(basematname)
    basemat.use_nodes = True
    tree = basemat.node_tree

    output = tree.nodes['Material Output']
    outputSurfaceInput = output.inputs["Surface"]

    diffuse = tree.nodes.get("Diffuse BSDF")

    pbr = tree.nodes.new("ShaderNodeBsdfPrincipled")
    pbr.location = diffuse.location
    pbrout = pbr.outputs['BSDF']

    pbr.distribution = m3.DM_prefs().base_distribution
    pbr.inputs['Base Color'].default_value = (m3.DM_prefs().base_color[0], m3.DM_prefs().base_color[1], m3.DM_prefs().base_color[2], 1)
    pbr.inputs['Metallic'].default_value = m3.DM_prefs().base_metallic
    pbr.inputs['Specular'].default_value = m3.DM_prefs().base_specular
    pbr.inputs['Specular Tint'].default_value = m3.DM_prefs().base_speculartint
    pbr.inputs['Roughness'].default_value = m3.DM_prefs().base_roughness
    pbr.inputs['Anisotropic'].default_value = m3.DM_prefs().base_anisotropic
    pbr.inputs['Anisotropic Rotation'].default_value = m3.DM_prefs().base_anisotropicrotation
    pbr.inputs['Sheen'].default_value = m3.DM_prefs().base_sheen
    pbr.inputs['Sheen Tint'].default_value = m3.DM_prefs().base_sheentint
    pbr.inputs['Clearcoat'].default_value = m3.DM_prefs().base_clearcoat
    pbr.inputs['Clearcoat Roughness'].default_value = m3.DM_prefs().base_clearcoatroughness
    pbr.inputs['IOR'].default_value = m3.DM_prefs().base_ior
    pbr.inputs['Transmission'].default_value = m3.DM_prefs().base_transmission

    tree.links.new(input=outputSurfaceInput, output=pbrout)
    tree.nodes.remove(diffuse)

    return basemat


def create_base_mat_old(basematname):
    print("Creating new '%s' material." % (basematname))
    basemat = bpy.data.materials.new(basematname)
    basemat.use_nodes = True
    tree = basemat.node_tree

    output = tree.nodes['Material Output']
    outputSurfaceInput = output.inputs["Surface"]

    diffuse = tree.nodes.get("Diffuse BSDF")

    glossy = tree.nodes.new("ShaderNodeBsdfGlossy")
    glossy.location = diffuse.location
    glossyout = glossy.outputs['BSDF']

    glossy.distribution = m3.DM_prefs().base_distribution
    glossy.inputs['Color'].default_value = (m3.DM_prefs().base_color[0], m3.DM_prefs().base_color[1], m3.DM_prefs().base_color[2], 1)
    glossy.inputs['Roughness'].default_value = m3.DM_prefs().base_roughness

    tree.links.new(input=outputSurfaceInput, output=glossyout)
    tree.nodes.remove(diffuse)

    return basemat
