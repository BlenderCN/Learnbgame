import bpy
bpy.types.Scene.bf_author = "Francois Tarlier"
bpy.types.Scene.bf_class = "Grading"
bpy.types.Scene.bf_description = "F. Tarlier Day to Nit apply the   effect “day to night”"
Scene = bpy.context.scene
Tree = Scene.node_tree

Node_G = bpy.data.node_groups.new("Day_to_Nit", type='COMPOSITE')

Node_1 = Node_G.nodes.new('COLORBALANCE')
Node_1.correction_method = 'LIFT_GAMMA_GAIN'
Node_1.lift = [0.418, 0.461, 0.780]
Node_1.gamma = [0.875, 1.000, 0.750]
Node_1.gain = [0.455, 0.734, 0.840]

Node_2 = Node_G.nodes.new('HUE_SAT')
Node_2.location = (500, -100)
Node_2.color_saturation = 0.920
Node_2.color_value = 0.872
Node_2.color_value = 1.016

Node_G.inputs.new("Source", 'RGBA')
Node_G.outputs.new("Result", 'RGBA')
Node_G.links.new(Node_1.outputs[0], Node_2.inputs[1])
Node_G.links.new(Node_G.inputs[0], Node_1.inputs[1])
Node_G.links.new(Node_G.outputs[0], Node_2.outputs[0])

Tree.nodes.new("GROUP", group = Node_G)
