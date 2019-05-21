import bpy
from .. import M3utils as m3


class UpdateDecalNodes(bpy.types.Operator):
    bl_idname = "machin3.update_decal_nodes"
    bl_label = "MACHIN3: Update Decal Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.app.version >= (2, 79, 0):
            for mat in bpy.data.materials:
                if mat.use_nodes:

                    lastnode = mat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node

                    if lastnode.type == "GROUP":
                        if "Decal" in lastnode.node_tree.name:
                            update_decal_node(mat, lastnode)

        return {'FINISHED'}


def update_decal_node(mat, decalgroup):
    # always get rid of decal group duplicates, as we don't want to influence any other materials, ever
    if decalgroup.node_tree.users > 1:
        decalgroup.node_tree = decalgroup.node_tree.copy()

    groupname = decalgroup.node_tree.name

    if "Subset" in groupname:
        update_subset_group(mat, decalgroup)
    elif "Panel" in groupname:
        update_panel_group(mat, decalgroup)
    elif "Info" in groupname:
        update_info_group(mat, decalgroup)
    else:
        update_subtractor_group(mat, decalgroup)


def update_subset_group(mat, decalgroup):
    # look for Material Metallic parameter
    try:
        decalgroup.inputs["Material Metallic"]
        # print("Material %s's Decal Node Group already supports Principled BSDF shading." % (mat.name))
        return
    except KeyError:
        print("Updating Material %s's Decal Subset Node Group to support Principled BSDF shading." % (mat.name))

    tree = decalgroup.node_tree

    # add pbr nodes
    materialpbr = tree.nodes.new("ShaderNodeBsdfPrincipled")
    materialpbr.location = (240, 560)
    materialpbr.distribution = "GGX"

    subsetpbr = tree.nodes.new("ShaderNodeBsdfPrincipled")
    subsetpbr.location = (240, -303)
    subsetpbr.distribution = "GGX"

    # add Material Sockets
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Metallic")
    socket.min_value = 0
    socket.max_value = 1
    socket.default_value = 0
    tree.inputs.move(2, 1)  # moves the existing 'Material Roughness' up above 'Subset Color'
    tree.inputs.move(11, 1)  # move the new 'Material Metallic' above 'Material Roughness'

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Specular")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(12, 2)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Specular Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(13, 3)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Anisotropic")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(14, 5)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Anisotropic Rotation")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(15, 6)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Sheen")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(16, 7)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Sheen Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(17, 8)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Clearcoat")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(18, 9)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Clearcoat Roughness")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(19, 10)

    socket = tree.inputs.new("NodeSocketFloat", "Material IOR")
    socket.min_value = 0
    socket.max_value = 1000
    tree.inputs.move(20, 11)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Transmission")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(21, 12)

    # add Subset Sockets
    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Metallic")
    socket.min_value = 0
    socket.max_value = 1
    socket.default_value = 0
    tree.inputs.move(22, 14)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Specular")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(23, 15)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Specular Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(24, 16)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Anisotropic")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(25, 18)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Anisotropic Rotation")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(26, 19)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Sheen")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(27, 20)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Sheen Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(28, 21)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Clearcoat")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(29, 22)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Clearcoat Roughness")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(30, 23)

    socket = tree.inputs.new("NodeSocketFloat", "Subset IOR")
    socket.min_value = 0
    socket.max_value = 1000
    tree.inputs.move(31, 24)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Subset Transmission")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(32, 25)

    # fix the normal strength
    socket = tree.inputs["Normal Strength"]
    socket.min_value = 0
    socket.max_value = 1

    # link sockets to pbr nodes
    groupinput = tree.nodes['Group Input'].outputs
    materialcolor = tree.nodes['Mix.001'].outputs['Color']
    subsetcolor = tree.nodes['Mix.003'].outputs['Color']
    normal = tree.nodes['Normal Map'].outputs['Normal']

    tree.links.new(materialcolor, materialpbr.inputs['Base Color'])
    tree.links.new(groupinput['Material Metallic'], materialpbr.inputs['Metallic'])
    tree.links.new(groupinput['Material Specular'], materialpbr.inputs['Specular'])
    tree.links.new(groupinput['Material Specular Tint'], materialpbr.inputs['Specular Tint'])
    tree.links.new(groupinput['Material Roughness'], materialpbr.inputs['Roughness'])
    tree.links.new(groupinput['Material Anisotropic'], materialpbr.inputs['Anisotropic'])
    tree.links.new(groupinput['Material Anisotropic Rotation'], materialpbr.inputs['Anisotropic Rotation'])
    tree.links.new(groupinput['Material Sheen'], materialpbr.inputs['Sheen'])
    tree.links.new(groupinput['Material Sheen Tint'], materialpbr.inputs['Sheen Tint'])
    tree.links.new(groupinput['Material Clearcoat'], materialpbr.inputs['Clearcoat'])
    tree.links.new(groupinput['Material Clearcoat Roughness'], materialpbr.inputs['Clearcoat Roughness'])
    tree.links.new(groupinput['Material IOR'], materialpbr.inputs['IOR'])
    tree.links.new(groupinput['Material Transmission'], materialpbr.inputs['Transmission'])
    tree.links.new(normal, materialpbr.inputs['Normal'])

    tree.links.new(subsetcolor, subsetpbr.inputs['Base Color'])
    tree.links.new(groupinput['Subset Metallic'], subsetpbr.inputs['Metallic'])
    tree.links.new(groupinput['Subset Specular'], subsetpbr.inputs['Specular'])
    tree.links.new(groupinput['Subset Specular Tint'], subsetpbr.inputs['Specular Tint'])
    tree.links.new(groupinput['Subset Roughness'], subsetpbr.inputs['Roughness'])
    tree.links.new(groupinput['Subset Anisotropic'], subsetpbr.inputs['Anisotropic'])
    tree.links.new(groupinput['Subset Anisotropic Rotation'], subsetpbr.inputs['Anisotropic Rotation'])
    tree.links.new(groupinput['Subset Sheen'], subsetpbr.inputs['Sheen'])
    tree.links.new(groupinput['Subset Sheen Tint'], subsetpbr.inputs['Sheen Tint'])
    tree.links.new(groupinput['Subset Clearcoat'], subsetpbr.inputs['Clearcoat'])
    tree.links.new(groupinput['Subset Clearcoat Roughness'], subsetpbr.inputs['Clearcoat Roughness'])
    tree.links.new(groupinput['Subset IOR'], subsetpbr.inputs['IOR'])
    tree.links.new(groupinput['Subset Transmission'], subsetpbr.inputs['Transmission'])
    tree.links.new(normal, subsetpbr.inputs['Normal'])

    # link pbr nodes to mix shader
    mix = tree.nodes['Mix Shader.001']

    tree.links.new(materialpbr.outputs['BSDF'], mix.inputs[1])
    tree.links.new(subsetpbr.outputs['BSDF'], mix.inputs[2])

    # set up decal group node base values
    decalgroup.inputs["Material Metallic"].default_value = 1
    decalgroup.inputs["Material Specular"].default_value = 0.5
    decalgroup.inputs["Material Roughness"].default_value = 0.5
    decalgroup.inputs["Material Sheen Tint"].default_value = 0.5
    decalgroup.inputs["Material Clearcoat Roughness"].default_value = 0.03
    decalgroup.inputs["Material IOR"].default_value = 1.450

    decalgroup.inputs["Subset Metallic"].default_value = 1
    decalgroup.inputs["Subset Specular"].default_value = 0.5
    decalgroup.inputs["Subset Roughness"].default_value = 0.5
    decalgroup.inputs["Subset Sheen Tint"].default_value = 0.5
    decalgroup.inputs["Subset Clearcoat Roughness"].default_value = 0.03
    decalgroup.inputs["Subset IOR"].default_value = 1.450


def update_panel_group(mat, decalgroup):
    # look for Material Metallic parameter
    try:
        decalgroup.inputs["Material 1 Metallic"]
        # print("Material %s's Decal Node Group already supports Principled BSDF shading." % (mat.name))
        return
    except KeyError:
        print("Updating Material %s's Decal Panel Node Group to support Principled BSDF shading." % (mat.name))

    tree = decalgroup.node_tree

    # add pbr nodes
    material1pbr = tree.nodes.new("ShaderNodeBsdfPrincipled")
    material1pbr.location = (240, 560)
    material1pbr.distribution = "GGX"

    material2pbr = tree.nodes.new("ShaderNodeBsdfPrincipled")
    material2pbr.location = (240, -303)
    material2pbr.distribution = "GGX"

    # add Material Sockets
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Metallic")
    socket.min_value = 0
    socket.max_value = 1
    socket.default_value = 0
    tree.inputs.move(2, 1)  # moves the existing 'Material 1 Roughness' up above 'Subset Color'
    tree.inputs.move(11, 1)  # move the new 'Material 1 Metallic' above 'Material Roughness'

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Specular")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(12, 2)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Specular Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(13, 3)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Anisotropic")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(14, 5)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Anisotropic Rotation")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(15, 6)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Sheen")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(16, 7)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Sheen Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(17, 8)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Clearcoat")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(18, 9)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Clearcoat Roughness")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(19, 10)

    socket = tree.inputs.new("NodeSocketFloat", "Material 1 IOR")
    socket.min_value = 0
    socket.max_value = 1000
    tree.inputs.move(20, 11)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 1 Transmission")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(21, 12)

    # add Subset Sockets
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Metallic")
    socket.min_value = 0
    socket.max_value = 1
    socket.default_value = 0
    tree.inputs.move(22, 14)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Specular")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(23, 15)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Specular Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(24, 16)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Anisotropic")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(25, 18)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Anisotropic Rotation")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(26, 19)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Sheen")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(27, 20)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Sheen Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(28, 21)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Clearcoat")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(29, 22)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Clearcoat Roughness")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(30, 23)

    socket = tree.inputs.new("NodeSocketFloat", "Material 2 IOR")
    socket.min_value = 0
    socket.max_value = 1000
    tree.inputs.move(31, 24)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material 2 Transmission")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(32, 25)

    # fix the normal strength
    socket = tree.inputs["Normal Strength"]
    socket.min_value = 0
    socket.max_value = 1

    # link sockets to pbr nodes
    groupinput = tree.nodes['Group Input'].outputs
    materialcolor = tree.nodes['Mix.001'].outputs['Color']
    subsetcolor = tree.nodes['Mix.003'].outputs['Color']
    normal = tree.nodes['Normal Map'].outputs['Normal']

    tree.links.new(materialcolor, material1pbr.inputs['Base Color'])
    tree.links.new(groupinput['Material 1 Metallic'], material1pbr.inputs['Metallic'])
    tree.links.new(groupinput['Material 1 Specular'], material1pbr.inputs['Specular'])
    tree.links.new(groupinput['Material 1 Specular Tint'], material1pbr.inputs['Specular Tint'])
    tree.links.new(groupinput['Material 1 Roughness'], material1pbr.inputs['Roughness'])
    tree.links.new(groupinput['Material 1 Anisotropic'], material1pbr.inputs['Anisotropic'])
    tree.links.new(groupinput['Material 1 Anisotropic Rotation'], material1pbr.inputs['Anisotropic Rotation'])
    tree.links.new(groupinput['Material 1 Sheen'], material1pbr.inputs['Sheen'])
    tree.links.new(groupinput['Material 1 Sheen Tint'], material1pbr.inputs['Sheen Tint'])
    tree.links.new(groupinput['Material 1 Clearcoat'], material1pbr.inputs['Clearcoat'])
    tree.links.new(groupinput['Material 1 Clearcoat Roughness'], material1pbr.inputs['Clearcoat Roughness'])
    tree.links.new(groupinput['Material 1 IOR'], material1pbr.inputs['IOR'])
    tree.links.new(groupinput['Material 1 Transmission'], material1pbr.inputs['Transmission'])
    tree.links.new(normal, material1pbr.inputs['Normal'])

    tree.links.new(subsetcolor, material2pbr.inputs['Base Color'])
    tree.links.new(groupinput['Material 2 Metallic'], material2pbr.inputs['Metallic'])
    tree.links.new(groupinput['Material 2 Specular'], material2pbr.inputs['Specular'])
    tree.links.new(groupinput['Material 2 Specular Tint'], material2pbr.inputs['Specular Tint'])
    tree.links.new(groupinput['Material 2 Roughness'], material2pbr.inputs['Roughness'])
    tree.links.new(groupinput['Material 2 Anisotropic'], material2pbr.inputs['Anisotropic'])
    tree.links.new(groupinput['Material 2 Anisotropic Rotation'], material2pbr.inputs['Anisotropic Rotation'])
    tree.links.new(groupinput['Material 2 Sheen'], material2pbr.inputs['Sheen'])
    tree.links.new(groupinput['Material 2 Sheen Tint'], material2pbr.inputs['Sheen Tint'])
    tree.links.new(groupinput['Material 2 Clearcoat'], material2pbr.inputs['Clearcoat'])
    tree.links.new(groupinput['Material 2 Clearcoat Roughness'], material2pbr.inputs['Clearcoat Roughness'])
    tree.links.new(groupinput['Material 2 IOR'], material2pbr.inputs['IOR'])
    tree.links.new(groupinput['Material 2 Transmission'], material2pbr.inputs['Transmission'])
    tree.links.new(normal, material2pbr.inputs['Normal'])

    # link pbr nodes to mix shader
    mix = tree.nodes['Mix Shader.001']

    tree.links.new(material1pbr.outputs['BSDF'], mix.inputs[1])
    tree.links.new(material2pbr.outputs['BSDF'], mix.inputs[2])

    # set up decal group node base values
    decalgroup.inputs["Material 1 Metallic"].default_value = 1
    decalgroup.inputs["Material 1 Specular"].default_value = 0.5
    decalgroup.inputs["Material 1 Roughness"].default_value = 0.5
    decalgroup.inputs["Material 1 Sheen Tint"].default_value = 0.5
    decalgroup.inputs["Material 1 Clearcoat Roughness"].default_value = 0.03
    decalgroup.inputs["Material 1 IOR"].default_value = 1.450

    decalgroup.inputs["Material 2 Metallic"].default_value = 1
    decalgroup.inputs["Material 2 Specular"].default_value = 0.5
    decalgroup.inputs["Material 2 Roughness"].default_value = 0.5
    decalgroup.inputs["Material 2 Sheen Tint"].default_value = 0.5
    decalgroup.inputs["Material 2 Clearcoat Roughness"].default_value = 0.03
    decalgroup.inputs["Material 2 IOR"].default_value = 1.450


def update_info_group(mat, decalgroup):
    try:
        decalgroup.inputs["Info Metallic"]
        return
    except KeyError:
        print("Updating Material %s's Decal Info Node Group to support Principled BSDF shading." % (mat.name))

    tree = decalgroup.node_tree

    # update naming of existing sockets
    tree.inputs['Material Color'].name = "Info Color"
    tree.inputs['Material Roughness'].name = "Info Roughness"

    # add pbr node
    infopbr = tree.nodes.new("ShaderNodeBsdfPrincipled")
    infopbr.location = (240, 560)
    infopbr.distribution = "GGX"

    # add info sockets
    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Metallic")
    socket.min_value = 0
    socket.max_value = 1
    socket.default_value = 0
    tree.inputs.move(4, 1)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Specular")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(5, 3)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Specular Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(6, 4)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Anisotropic")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(7, 5)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Anisotropic Rotation")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(8, 6)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Sheen")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(9, 7)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Sheen Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(10, 8)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Clearcoat")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(11, 9)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Clearcoat Roughness")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(12, 10)

    socket = tree.inputs.new("NodeSocketFloat", "Info IOR")
    socket.min_value = 0
    socket.max_value = 1000
    tree.inputs.move(13, 11)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Info Transmission")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(14, 12)

    # link sockets to pbr nodes
    groupinput = tree.nodes['Group Input'].outputs
    infocolor = tree.nodes['Invert.001'].outputs['Color']

    tree.links.new(infocolor, infopbr.inputs['Base Color'])
    tree.links.new(groupinput['Info Metallic'], infopbr.inputs['Metallic'])
    tree.links.new(groupinput['Info Specular'], infopbr.inputs['Specular'])
    tree.links.new(groupinput['Info Specular Tint'], infopbr.inputs['Specular Tint'])
    tree.links.new(groupinput['Info Roughness'], infopbr.inputs['Roughness'])
    tree.links.new(groupinput['Info Anisotropic'], infopbr.inputs['Anisotropic'])
    tree.links.new(groupinput['Info Anisotropic Rotation'], infopbr.inputs['Anisotropic Rotation'])
    tree.links.new(groupinput['Info Sheen'], infopbr.inputs['Sheen'])
    tree.links.new(groupinput['Info Sheen Tint'], infopbr.inputs['Sheen Tint'])
    tree.links.new(groupinput['Info Clearcoat'], infopbr.inputs['Clearcoat'])
    tree.links.new(groupinput['Info Clearcoat Roughness'], infopbr.inputs['Clearcoat Roughness'])
    tree.links.new(groupinput['Info IOR'], infopbr.inputs['IOR'])
    tree.links.new(groupinput['Info Transmission'], infopbr.inputs['Transmission'])

    # link pbr nodes to mix shader
    mix = tree.nodes['Mix Shader']

    tree.links.new(infopbr.outputs['BSDF'], mix.inputs[1])

    # set up decal group node base values
    decalgroup.inputs["Info Metallic"].default_value = 0.3
    decalgroup.inputs["Info Specular"].default_value = 0.5
    decalgroup.inputs["Info Roughness"].default_value = 0.2
    decalgroup.inputs["Info Sheen Tint"].default_value = 0.5
    decalgroup.inputs["Info Clearcoat Roughness"].default_value = 0.03
    decalgroup.inputs["Info IOR"].default_value = 1.450


def update_subtractor_group(mat, decalgroup):
    # look for Material Metallic parameter
    try:
        decalgroup.inputs["Material Metallic"]
        # print("Material %s's Decal Node Group already supports Principled BSDF shading." % (mat.name))
        return
    except KeyError:
        print("Updating Material %s's Decal Subtractor Node Group to support Principled BSDF shading." % (mat.name))

    if "Decal Group" in decalgroup.node_tree.name:
        decalgroup.node_tree.name = decalgroup.node_tree.name.replace("Decal Group", "Decal Subtractor Group")
        print("Fixing Decal Subtractor Node Group's name.")

    tree = decalgroup.node_tree

    # add pbr nodes
    materialpbr = tree.nodes.new("ShaderNodeBsdfPrincipled")
    materialpbr.location = (240, 560)
    materialpbr.distribution = "GGX"

    # add Material Sockets
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Metallic")
    socket.min_value = 0
    socket.max_value = 1
    socket.default_value = 0
    tree.inputs.move(8, 1)  # move the new 'Material Metallic' above 'Material Roughness'

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Specular")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(9, 2)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Specular Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(10, 3)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Anisotropic")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(11, 5)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Anisotropic Rotation")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(12, 6)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Sheen")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(13, 7)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Sheen Tint")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(14, 8)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Clearcoat")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(15, 9)
    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Clearcoat Roughness")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(16, 10)

    socket = tree.inputs.new("NodeSocketFloat", "Material IOR")
    socket.min_value = 0
    socket.max_value = 1000
    tree.inputs.move(17, 11)

    socket = tree.inputs.new("NodeSocketFloatFactor", "Material Transmission")
    socket.min_value = 0
    socket.max_value = 1
    tree.inputs.move(18, 12)

    # fix the normal strength
    socket = tree.inputs["Normal Strength"]
    socket.min_value = 0
    socket.max_value = 1

    # link sockets to pbr nodes
    groupinput = tree.nodes['Group Input'].outputs
    materialcolor = tree.nodes['Mix.001'].outputs['Color']
    normal = tree.nodes['Normal Map'].outputs['Normal']

    tree.links.new(materialcolor, materialpbr.inputs['Base Color'])
    tree.links.new(groupinput['Material Metallic'], materialpbr.inputs['Metallic'])
    tree.links.new(groupinput['Material Specular'], materialpbr.inputs['Specular'])
    tree.links.new(groupinput['Material Specular Tint'], materialpbr.inputs['Specular Tint'])
    tree.links.new(groupinput['Material Roughness'], materialpbr.inputs['Roughness'])
    tree.links.new(groupinput['Material Anisotropic'], materialpbr.inputs['Anisotropic'])
    tree.links.new(groupinput['Material Anisotropic Rotation'], materialpbr.inputs['Anisotropic Rotation'])
    tree.links.new(groupinput['Material Sheen'], materialpbr.inputs['Sheen'])
    tree.links.new(groupinput['Material Sheen Tint'], materialpbr.inputs['Sheen Tint'])
    tree.links.new(groupinput['Material Clearcoat'], materialpbr.inputs['Clearcoat'])
    tree.links.new(groupinput['Material Clearcoat Roughness'], materialpbr.inputs['Clearcoat Roughness'])
    tree.links.new(groupinput['Material IOR'], materialpbr.inputs['IOR'])
    tree.links.new(groupinput['Material Transmission'], materialpbr.inputs['Transmission'])
    tree.links.new(normal, materialpbr.inputs['Normal'])

    # link pbr nodes to mix shader
    mix = tree.nodes['Mix Shader']

    tree.links.new(materialpbr.outputs['BSDF'], mix.inputs[1])

    # set up decal group node base values
    decalgroup.inputs["Material Metallic"].default_value = 1
    decalgroup.inputs["Material Specular"].default_value = 0.5
    decalgroup.inputs["Material Roughness"].default_value = 0.5
    decalgroup.inputs["Material Sheen Tint"].default_value = 0.5
    decalgroup.inputs["Material Clearcoat Roughness"].default_value = 0.03
    decalgroup.inputs["Material IOR"].default_value = 1.450
