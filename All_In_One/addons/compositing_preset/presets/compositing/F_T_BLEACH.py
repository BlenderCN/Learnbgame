import bpy
bpy.types.Scene.bf_author = "Francois Tarlier"
bpy.types.Scene.bf_class = "Grading"
bpy.types.Scene.bf_description = "The version of F. Tarlier of Bleach Bypass."
Scene = bpy.context.scene
Tree = Scene.node_tree

Node_G = bpy.data.node_groups.new("F_T_Bleach", type='COMPOSITE')

Node_1 = Node_G.nodes.new('COLORBALANCE')
Node_1.correction_method = 'LIFT_GAMMA_GAIN'
Node_1.lift = [0.433, 0.748, 0.920]
Node_1.gamma = [1.280, 1.280, 1.280]
Node_1.gain = [1.020, 0.915, 0.736]

Node_2 = Node_G.nodes.new('HUE_SAT')
Node_2.location = (500, -100)
Node_2.color_saturation = 0.456
Node_2.color_value = 1.016

Node_G.inputs.new("Source", 'RGBA')
Node_G.outputs.new("Result", 'RGBA')
Node_G.links.new(Node_1.outputs[0], Node_2.inputs[1])
Node_G.links.new(Node_G.inputs[0], Node_1.inputs[1])
Node_G.links.new(Node_G.outputs[0], Node_2.outputs[0])

Tree.nodes.new("GROUP", group = Node_G)
