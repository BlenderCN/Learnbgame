import bpy
bpy.types.Scene.bf_author = "Gillan"
bpy.types.Scene.bf_class = "Grading"
bpy.types.Scene.bf_description = "Seppia is the classic sepia."
Scene = bpy.context.scene
Tree = Scene.node_tree

Node_G = bpy.data.node_groups.new("Seppia", type='COMPOSITE')

Node_1 = Node_G.nodes.new('HUE_SAT')
Node_1.color_saturation = 0

Node_2 = Node_G.nodes.new('COLORBALANCE')
Node_2.location = (200, 100)
Node_2.correction_method = 'LIFT_GAMMA_GAIN'
Node_2.lift = [0.880, 0.774, 0.722]
Node_2.gamma = [1.058, 0.998, 0.939]
Node_2.gain = [1.012, 0.991, 0.995]

Node_G.inputs.new("Source", 'RGBA')
Node_G.outputs.new("Result", 'RGBA')
Node_G.links.new(Node_1.outputs[0], Node_2.inputs[1])
Node_G.links.new(Node_G.inputs[0], Node_1.inputs[1])
Node_G.links.new(Node_G.outputs[0], Node_2.outputs[0])

Tree.nodes.new("GROUP", group = Node_G)
