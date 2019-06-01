import bpy
bpy.types.Scene.bf_author = "Gillan"
bpy.types.Scene.bf_class = "Grading"
bpy.types.Scene.bf_description = "Romantic, with this filter is a must use a very soft and clear glow."
Scene = bpy.context.scene
Tree = Scene.node_tree

Node_G = bpy.data.node_groups.new("Romantic", type='COMPOSITE')

Node_1 = Node_G.nodes.new('COLORBALANCE')
Node_1.correction_method = 'LIFT_GAMMA_GAIN'
Node_1.lift = [1.120, 1.022, 1.026]
Node_1.gamma = [1.320, 1.082, 1.128]
Node_1.gain = [0.993, 0.929, 0.889]

Node_2 = Node_G.nodes.new('HUE_SAT')
Node_2.location = (500, 0)
Node_2.color_saturation = 0
Node_2.color_value = 1

Node_G.inputs.new("Source", 'RGBA')
Node_G.outputs.new("Result", 'RGBA')
Node_G.links.new(Node_1.outputs[0], Node_2.inputs[1])
Node_G.links.new(Node_G.inputs[0], Node_1.inputs[1])
Node_G.links.new(Node_G.outputs[0], Node_2.outputs[0])

Tree.nodes.new("GROUP", group = Node_G)
