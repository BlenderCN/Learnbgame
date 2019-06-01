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

import bpy

# Ghost element's Material
def GhostElementMat(element, image):
    coll = bpy.context.scene.flare_group.coll
    index = bpy.context.scene.flare_group.index
    
    bpy.context.scene.render.engine = 'CYCLES'
    LF_Mat = bpy.data.materials.new("BLF_Material")
    LF_Mat.use_nodes= True
    LF_Mat.node_tree.nodes.clear()
    #Adding new nodes
    add = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeAddShader')
    emission = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeEmission')
    tex_coord = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexCoord')
    tex_image = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
    tex_image2 = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
    output = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    transparent = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeBsdfTransparent')
    mix = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    mix2 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    mix3 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    mix4 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    mix5 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    ramp = LF_Mat.node_tree.nodes.new(type ="ShaderNodeValToRGB")
    mapping = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMapping")
    obj_info = LF_Mat.node_tree.nodes.new(type ="ShaderNodeObjectInfo")
        
    # Properties
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 0.0
    mix.inputs[2].default_value = [1.0,1.0,1.0,1.0]
    
    mix2.blend_type = 'MULTIPLY'
    mix2.inputs[0].default_value = 1.0
    mix2.inputs[2].default_value = coll[index].color
    
    mix3.blend_type = 'SUBTRACT'
    mix3.inputs[0].default_value = 1.0
    
    mix4.blend_type = 'ADD'
    mix4.inputs[0].default_value = 0.0
    
    mix5.blend_type = 'MIX'
    mix5.inputs[1].default_value = [1.0,0.0,0.0,1.0]
    mix5.inputs[2].default_value = [0.0,0.0,1.0,1.0]
    
    mapping.use_min = True    
    mapping.use_max = True    
    if 'circle_smooth.jpg' not in bpy.data.images.keys():
        bpy.ops.image.open(filepath = image)        
        
    tex_image.image = bpy.data.images['circle_smooth.jpg']
    tex_image2.image = bpy.data.images['circle_smooth.jpg']
    
    #links
    LF_Mat.node_tree.links.new(tex_coord.outputs['Generated'], tex_image.inputs[0])
    LF_Mat.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs[0])
    LF_Mat.node_tree.links.new(mapping.outputs[0], tex_image2.inputs[0])
    LF_Mat.node_tree.links.new(tex_image2.outputs[0], mix3.inputs[2])
    LF_Mat.node_tree.links.new(mix3.outputs[0], mix4.inputs[2])
    LF_Mat.node_tree.links.new(mix4.outputs[0], mix.inputs[1])
    LF_Mat.node_tree.links.new(tex_image.outputs['Color'], mix3.inputs[1])
    LF_Mat.node_tree.links.new(tex_image.outputs['Color'], mix4.inputs[1])
    LF_Mat.node_tree.links.new(mix.outputs['Color'], mix2.inputs[1])
    LF_Mat.node_tree.links.new(obj_info.outputs[3], ramp.inputs[0])
    LF_Mat.node_tree.links.new(ramp.outputs[0], mix5.inputs[0])
    LF_Mat.node_tree.links.new(mix5.outputs[0], mix.inputs[2])
    LF_Mat.node_tree.links.new(mix2.outputs['Color'], emission.inputs[0])
    LF_Mat.node_tree.links.new(emission.outputs[0], add.inputs[0])
    LF_Mat.node_tree.links.new(transparent.outputs[0], add.inputs[1])
    LF_Mat.node_tree.links.new(add.outputs[0], output.inputs[0])
    
    # locations
    tex_coord.location = (-520, 0)
    tex_image2.location = (40, 252)
    tex_image.location = (40, 0)
    mix5.location = (40, -250)
    mix3.location = (220, 252)
    mix4.location = (400, 252)
    mix.location = (580, 252)
    mix2.location = (760, 252)
    obj_info.location = (-520, -250)    
    mapping.location = (-320, 252)    
    ramp.location = (-250, -250)    
    emission.location = (920, 252)
    transparent.location = (920, 152)
    add.location = (1100, 252)
    output.location = (1280, 252)
    
    element.data.materials.append(LF_Mat)
    
# Simple element's Material
def SimElementMat(element, image):
    coll = bpy.context.scene.flare_group.coll
    index = bpy.context.scene.flare_group.index
    
    bpy.context.scene.render.engine = 'CYCLES'
    LF_Mat = bpy.data.materials.new("BLF_Material")
    LF_Mat.use_nodes= True
    LF_Mat.node_tree.nodes.clear()
    #Adding new nodes
    add = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeAddShader')
    emission = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeEmission')
    tex_coord = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexCoord')
    tex_image = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
    output = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    transparent = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeBsdfTransparent')
    mix = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    mix2 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    
    # Properties
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 0.0
    mix.inputs[2].default_value = [1.0,1.0,1.0,1.0]
    
    mix2.blend_type = 'MULTIPLY'
    mix2.inputs[0].default_value = 1.0
    mix2.inputs[2].default_value = coll[index].color    
    
    if 'glow.jpg' not in bpy.data.images.keys():
        bpy.ops.image.open(filepath = image)    
        
    tex_image.image = bpy.data.images['glow.jpg']
    
    #links
    LF_Mat.node_tree.links.new(tex_coord.outputs['Generated'], tex_image.inputs['Vector'])
    LF_Mat.node_tree.links.new(tex_image.outputs['Color'], mix.inputs[1])
    LF_Mat.node_tree.links.new(mix.outputs['Color'], mix2.inputs[1])
    LF_Mat.node_tree.links.new(mix2.outputs['Color'], emission.inputs[0])
    LF_Mat.node_tree.links.new(emission.outputs[0], add.inputs[0])
    LF_Mat.node_tree.links.new(transparent.outputs[0], add.inputs[1])
    LF_Mat.node_tree.links.new(add.outputs[0], output.inputs[0])
    
    # locations
    tex_coord.location = (220, 252)
    tex_image.location = (400, 252)
    mix.location = (580, 252)
    mix2.location = (760, 252)
    emission.location = (920, 252)
    transparent.location = (920, 152)
    add.location = (1100, 252)
    output.location = (1280, 252)       
    
    element.data.materials.append(LF_Mat)
    
# Lens_dirt element's Material
def LensElementMat(element, image, image2):
    coll = bpy.context.scene.flare_group.coll
    index = bpy.context.scene.flare_group.index
    
    bpy.context.scene.render.engine = 'CYCLES'
    LF_Mat = bpy.data.materials.new("BLF_Material")
    LF_Mat.use_nodes= True
    LF_Mat.node_tree.nodes.clear()
    #Adding new nodes
    add = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeAddShader')
    mix_sh = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeMixShader')
    emission = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeEmission')
    transparent = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeBsdfTransparent')
    transparent2 = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeBsdfTransparent')
    tex_coord = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexCoord')
    tex_image = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
    tex_image2 = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
    ramp = LF_Mat.node_tree.nodes.new(type ="ShaderNodeValToRGB")
    mapping = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMapping")
    mapping2 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMapping")
    mix = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    mix2 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    invert = LF_Mat.node_tree.nodes.new(type="ShaderNodeInvert")    
    output = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    
    
    
    # Properties
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 0.0
    mix.inputs[2].default_value = [1.0,1.0,1.0,1.0]
    
    mix2.blend_type = 'MULTIPLY'
    mix2.inputs[0].default_value = 0.5
    mix2.inputs[2].default_value = coll[index].color
    
    mapping2.use_min = True    
    mapping2.use_max = True    
    
    if 'lens_dirt_4.jpg' not in bpy.data.images.keys():
        bpy.ops.image.open(filepath = image)
    if 'glow.jpg' not in bpy.data.images.keys():
        bpy.ops.image.open(filepath = image2)    
        
    tex_image.image = bpy.data.images['lens_dirt_4.jpg']
    tex_image2.image = bpy.data.images['glow.jpg']
    
    #links
    LF_Mat.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs[0])
    LF_Mat.node_tree.links.new(tex_coord.outputs['Camera'], mapping2.inputs[0])
    LF_Mat.node_tree.links.new(mapping.outputs[0], tex_image.inputs[0])
    LF_Mat.node_tree.links.new(mapping2.outputs[0], tex_image2.inputs[0])
    LF_Mat.node_tree.links.new(tex_image.outputs['Color'], mix.inputs[1])
    LF_Mat.node_tree.links.new(tex_image2.outputs['Color'], ramp.inputs[0])
    LF_Mat.node_tree.links.new(mix.outputs['Color'], mix2.inputs[1])
    LF_Mat.node_tree.links.new(mix2.outputs['Color'], emission.inputs[0])
    LF_Mat.node_tree.links.new(ramp.outputs[0], invert.inputs[1])
    LF_Mat.node_tree.links.new(emission.outputs[0], add.inputs[0])
    LF_Mat.node_tree.links.new(transparent.outputs[0], add.inputs[1])
    LF_Mat.node_tree.links.new(invert.outputs[0], mix_sh.inputs[0])
    LF_Mat.node_tree.links.new(add.outputs[0], mix_sh.inputs[1])
    LF_Mat.node_tree.links.new(transparent2.outputs[0], mix_sh.inputs[2])    
    LF_Mat.node_tree.links.new(mix_sh.outputs[0], output.inputs[0])
    
    # locations
    tex_coord.location = (-140, 35)
    tex_image.location = (400, 252)
    tex_image2.location = (400, -40)
    mapping.location = (40, 252)
    mapping2.location = (40, -40)
    ramp.location = (580, -40)
    invert.location = (920, -40)
    mix.location = (580, 252)
    mix2.location = (760, 252)
    emission.location = (920, 252)
    transparent.location = (920, 152)
    transparent2.location = (1100, -40)
    mix_sh.location = (1280, 252)
    add.location = (1100, 252)
    output.location = (1460, 252)       
    
    element.data.materials.append(LF_Mat)

# Star element's Material
def StarElementMat(element, image, image2):
    coll = bpy.context.scene.flare_group.coll
    index = bpy.context.scene.flare_group.index
    
    bpy.context.scene.render.engine = 'CYCLES'
    LF_Mat = bpy.data.materials.new("BLF_Material")
    LF_Mat.use_nodes= True
    LF_Mat.node_tree.nodes.clear()
    #Adding new nodes
    add = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeAddShader')
    emission = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeEmission')
    tex_coord = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexCoord')
    tex_image = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
    tex_image2 = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
    output = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    transparent = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeBsdfTransparent')
    mix = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    mix2 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    mix3 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    hue = LF_Mat.node_tree.nodes.new(type ="ShaderNodeHueSaturation")
    invert = LF_Mat.node_tree.nodes.new(type ="ShaderNodeInvert")
    mapping = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMapping")
    mapping2 = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMapping")
        
    # Properties
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 0.0
    mix.inputs[2].default_value = [1.0,1.0,1.0,1.0]
    
    mix2.blend_type = 'MULTIPLY'
    mix3.blend_type = 'MULTIPLY'
    mix2.inputs[0].default_value = 1.0
    mix2.inputs[2].default_value = coll[index].color
    mix3.inputs[0].default_value = 0.0
    hue.inputs[0].default_value = 1.0
    mapping.use_min = True    
    mapping.use_max = True 
    mapping2.scale[1] = 0.98 
    
    if 'ray1.jpg' not in bpy.data.images.keys():
        bpy.ops.image.open(filepath = image)
    if 'RGB2.jpg' not in bpy.data.images.keys():
        bpy.ops.image.open(filepath = image2)    
        
    tex_image.image = bpy.data.images['ray1.jpg']
    tex_image2.image = bpy.data.images['RGB2.jpg']
    
    #links
    LF_Mat.node_tree.links.new(tex_coord.outputs['Generated'], tex_image.inputs['Vector'])
    LF_Mat.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    LF_Mat.node_tree.links.new(tex_coord.outputs['Generated'], mapping2.inputs['Vector'])
    LF_Mat.node_tree.links.new(mapping.outputs[0], tex_image2.inputs['Vector'])
    LF_Mat.node_tree.links.new(mapping2.outputs[0], tex_image.inputs['Vector'])
    LF_Mat.node_tree.links.new(tex_image2.outputs['Color'], invert.inputs[1])
    LF_Mat.node_tree.links.new(tex_image.outputs['Color'], mix.inputs[1])
    LF_Mat.node_tree.links.new(invert.outputs[0], hue.inputs['Color'])
    LF_Mat.node_tree.links.new(mix.outputs['Color'], mix2.inputs[1])
    LF_Mat.node_tree.links.new(mix2.outputs['Color'], mix3.inputs[1])
    LF_Mat.node_tree.links.new(hue.outputs[0], mix3.inputs[2])
    LF_Mat.node_tree.links.new(mix3.outputs['Color'], emission.inputs[0])
    LF_Mat.node_tree.links.new(emission.outputs[0], add.inputs[0])
    LF_Mat.node_tree.links.new(transparent.outputs[0], add.inputs[1])
    LF_Mat.node_tree.links.new(add.outputs[0], output.inputs[0])
    
    # locations
    tex_coord.location = (-330, -30)
    mapping.location = (-140, -30)
    mapping2.location = (-140, 252)
    tex_image.location = (220, 252)
    tex_image2.location = (220, -30)
    mix.location = (400, 252)
    mix2.location = (580, 252)
    mix3.location = (760, 252)
    invert.location = (400, -30)
    hue.location = (580, -30)
    emission.location = (920, 252)
    transparent.location = (920, 152)
    add.location = (1100, 252)
    output.location = (1280, 252)       
    
    element.data.materials.append(LF_Mat)
# Background element's Material
def BackgroundElementMat(element, image):
    coll = bpy.context.scene.flare_group.coll
    index = bpy.context.scene.flare_group.index
    
    bpy.context.scene.render.engine = 'CYCLES'
    LF_Mat = bpy.data.materials.new("BLF_Material")
    LF_Mat.use_nodes= True
    LF_Mat.node_tree.nodes.clear()
    #Adding new nodes
    mix_shader = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeMixShader')
    emission = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeEmission')
    tex_coord = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexCoord')
    tex_image = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
    output = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    transparent = LF_Mat.node_tree.nodes.new(type = 'ShaderNodeBsdfTransparent')
    mix = LF_Mat.node_tree.nodes.new(type ="ShaderNodeMixRGB")
    
    
    # Properties       
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 0.0
    mix.inputs[2].default_value = coll[index].color
    mix.name = 'Mix.001'
    
    
    if 'black_BG.jpg' not in bpy.data.images.keys():
        bpy.ops.image.open(filepath = image)
    tex_image.image = bpy.data.images['black_BG.jpg']
    tex_image.image_user.use_auto_refresh = True
    
     
    #links
    LF_Mat.node_tree.links.new(tex_coord.outputs['Generated'], tex_image.inputs['Vector'])
    LF_Mat.node_tree.links.new(tex_image.outputs['Color'], mix.inputs[1])    
    LF_Mat.node_tree.links.new(mix.outputs['Color'], emission.inputs[0])
    LF_Mat.node_tree.links.new(emission.outputs[0], mix_shader.inputs[2])
    LF_Mat.node_tree.links.new(transparent.outputs[0], mix_shader.inputs[1])
    LF_Mat.node_tree.links.new(mix_shader.outputs[0], output.inputs[0])
    
    # locations
    tex_coord.location = (400, 252)
    tex_image.location = (580, 252)
    mix.location = (760, 252)    
    emission.location = (920, 152)
    transparent.location = (920, 252)
    mix_shader.location = (1100, 252)
    output.location = (1280, 252)       
    
    element.data.materials.append(LF_Mat)          