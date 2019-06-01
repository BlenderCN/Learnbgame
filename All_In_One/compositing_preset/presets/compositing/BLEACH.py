import bpy
bpy.types.Scene.bf_author = "Gillan"
bpy.types.Scene.bf_class = "Grading"
bpy.types.Scene.bf_description = "Bleach bypass, the result is a black and white image over a color image. The images usually would have reduced saturation and exposure latitude, along with increased contrast and graininess. It usually is used to maximal effect in conjunction with a one-stop underexposure."
Scene = bpy.context.scene
Tree = Scene.node_tree

Node_G = bpy.data.node_groups.new("Bleach", type='COMPOSITE')

Node_1 = Node_G.nodes.new('BRIGHTCONTRAST')

Node_2 = Node_G.nodes.new('HUE_SAT')
Node_2.location = (200, -100)
Node_2.color_saturation = 0.0

Node_3 = Node_G.nodes.new('INVERT')
Node_3.location = (400, 0)

Node_4 = Node_G.nodes.new('MIX_RGB')
Node_4.location = (600, 100)
Node_4.blend_type = 'COLOR'

Node_G.inputs.new("Source", 'RGBA')
Node_G.outputs.new("Result", 'RGBA')
Node_G.links.new(Node_1.outputs[0], Node_2.inputs[1])
Node_G.links.new(Node_2.outputs[0], Node_3.inputs[1])
Node_G.links.new(Node_3.outputs[0], Node_4.inputs[0])
Node_G.links.new(Node_2.outputs[0], Node_4.inputs[1])
Node_G.links.new(Node_1.outputs[0], Node_4.inputs[2])
Node_G.links.new(Node_G.inputs[0], Node_1.inputs[0])
Node_G.links.new(Node_G.outputs[0], Node_4.outputs[0])

Tree.nodes.new("GROUP", group = Node_G)
