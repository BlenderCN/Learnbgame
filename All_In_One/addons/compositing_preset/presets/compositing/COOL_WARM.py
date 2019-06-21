import bpy
bpy.types.Scene.bf_author = "Francois Tarlier"
bpy.types.Scene.bf_class = "Grading"
bpy.types.Scene.bf_description = "All the action movies today have these colors ( transformers,iron man etc.) , it works well (as in this case) combined with glow and glare filters and edge enhanced."
Scene = bpy.context.scene
Tree = Scene.node_tree

Node_G = bpy.data.node_groups.new("Cool_Warm", type='COMPOSITE')

Node_1 = Node_G.nodes.new('COLORBALANCE')
Node_1.correction_method = 'LIFT_GAMMA_GAIN'
Node_1.lift = [0.870, 0.951, 1.000]
Node_1.gamma = [0.954, 1.000, 0.946]
Node_1.gain = [1.120, 1.073, 0.842]

Node_G.inputs.new("Source", 'RGBA')
Node_G.outputs.new("Result", 'RGBA')
Node_G.links.new(Node_G.inputs[0], Node_1.inputs[1])
Node_G.links.new(Node_G.outputs[0], Node_1.outputs[0])

Tree.nodes.new("GROUP", group = Node_G)
