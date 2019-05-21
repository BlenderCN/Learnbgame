# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
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

import bpy
from .materials import NodeTree
print("shaders.py")

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


def buildSkinShader(mat, mhMat, scn, cfg):
    print("Creating skin shader", mat.name)
    mat.use_nodes= True
    mat.node_tree.nodes.clear()
    tree = NodeTree(mat.node_tree)
    links = mat.node_tree.links
    texco = tree.addNode(1, 'ShaderNodeTexCoord')

    diffuseTex = tree.addTexImageNode(mhMat, texco, "diffuse_texture", cfg)


def buildSkinShaderGroup(mat):
    print("Creating skin shader group", mat.name)
    mat.use_nodes= True
    mat.node_tree.nodes.clear()
    tree = NodeTree(mat.node_tree)
    links = mat.node_tree.links

    input = tree.addNode(1, 'ShaderNodeBsdfDiffuse')
    input.inputs["Color"].default_value[0:3] =  (1,1,1)
    
    factor = tree.addNode(1, 'ShaderNodeMath')
    factor.operation = 'MULTIPLY'
    #links.new(input.outputs['Scale'], factor.inputs[0])
    factor.inputs[0].default_value = 0.001
    factor.inputs[1].default_value = 1
    
    ssses = []
    for color,scale in [
        ((0.2,0.2,0.9), 0.006),
        ((0.1,0.6,0.6), 0.048),
        ((0.3,0.8,0.1), 0.187),
        ((0.3,0.3,0.2), 0.567),
        ((0.8,0.1,0.1), 1.990),
        ((0.3,0.3,0.2), 7.441)
        ]:
        mult = tree.addNode(2, 'ShaderNodeMixRGB')
        mult.blend_type = 'MULTIPLY'
        mult.inputs["Fac"].default_value = 1.0
        mult.inputs["Color1"].default_value[0:3] = color
        links.new(input.outputs['BSDF'], mult.inputs['Color2'])
        
        sss = tree.addNode(3, 'ShaderNodeSubsurfaceScattering')
        sss.falloff = 'CUBIC'
        links.new(mult.outputs['Color'], sss.inputs['Color'])
        links.new(factor.outputs['Value'], sss.inputs[1])
        #links.new(input.outputs[2], sss.inputs[3])
        #links.new(input.outputs[3], sss.inputs[4])
        
        ssses.append(sss)
        
    adders = []
    for n in range(5):
        add = tree.addNode(4, 'ShaderNodeAddShader')
        adders.append(add)
        
    links.new(ssses[0].outputs['BSSRDF'], adders[0].inputs[0])
    links.new(ssses[1].outputs['BSSRDF'], adders[0].inputs[1])
    links.new(ssses[2].outputs['BSSRDF'], adders[1].inputs[0])
    links.new(ssses[3].outputs['BSSRDF'], adders[1].inputs[1])
    links.new(ssses[4].outputs['BSSRDF'], adders[2].inputs[0])
    links.new(ssses[5].outputs['BSSRDF'], adders[2].inputs[1])
    links.new(adders[0].outputs['Shader'], adders[3].inputs[0])
    links.new(adders[1].outputs['Shader'], adders[3].inputs[1])
    links.new(adders[3].outputs['Shader'], adders[4].inputs[0])
    links.new(adders[2].outputs['Shader'], adders[4].inputs[1])

    output = tree.addNode(5, 'ShaderNodeOutputMaterial')
    links.new(adders[4].outputs['Shader'], output.inputs['Surface'])
            
    
                
class VIEW3D_OT_MakeSkinShaderButton(bpy.types.Operator):
    bl_idname = "mhx2.make_skin_shader"
    bl_label = "Make Skin Shader"
    bl_description = ""
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob and ob.type == 'MESH')

    def execute(self, context):
        me = context.object.data
        if me.materials:
            buildSkinShaderGroup(me.materials[0])
        return{'FINISHED'}
        
print("shaders.py done")
        