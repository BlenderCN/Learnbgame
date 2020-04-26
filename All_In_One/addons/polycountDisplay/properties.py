import bpy
from bpy.props import IntProperty,FloatVectorProperty,BoolProperty

## initialise the properties

def init_properties(): 
	scene = bpy.types.Scene 
	wm = bpy.types.WindowManager 
  
	scene.polycount_pos_x = IntProperty( 
		name="Pos X", 
		description="Margin on the x axis", 
		default=23, 
		min=0, 
		max=100) 
	scene.polycount_pos_y = IntProperty( 
		name="Pos Y", 
		description="Margin on the y axis", 
		default=20, 
		min=0, 
		max=100) 
	scene.polycount_font_size = IntProperty( 
		name="Font", 
		description="Fontsize", 
		default=15, min=10, max=150) 
	scene.polycount_font_color = FloatVectorProperty( 
		name="Color", 
		description="Font color", 
		default=(1.0, 1.0, 1.0), 
		min=0, 
		max=1, 
		subtype='COLOR')
	   

	wm.polycount_run = BoolProperty(default=False) 
	
	
	# vert/face/edge count global checkboxes
	scene.show_vertex_count = BoolProperty( 
		name="Show vertex count", 
		description = "Shows vertex count",
		default = False) 
		
	scene.show_edge_count = BoolProperty( 
		name="Show edge count", 
		description = "Shows edge count", 
		default = False)		 
	
	scene.show_face_count = BoolProperty( 
		name="Show face count", 
		description = "Shows face count", 
		default = False) 
		
	scene.show_triangle_count = BoolProperty( 
		name="Show triangle count", 
		description = "Shows triangle count", 
		default = False) 
		
   
	# vertex checkBoxes
	scene.vert_count_all = BoolProperty( 
		name="Show all vertex count", 
		description = "Shows all vertex count", 
		default = False)
	scene.vert_count_obj = BoolProperty( 
		name="Show obj vertex count", 
		description = "Shows selected objects vertex count", 
		default = False)
	scene.vert_count_sel = BoolProperty( 
		name="Show selected vertex count", 
		description = "Shows selected vertex count", 
		default = False)	 
	   
	# edge checkBoxes
	scene.edge_count_all = BoolProperty( 
		name="Show all edge count", 
		description = "Shows all edge count", 
		default = False)
	scene.edge_count_obj = BoolProperty( 
		name="Show obj edge count", 
		description = "Shows selected objects edge count", 
		default = False)
	scene.edge_count_sel = BoolProperty( 
		name="Show sel edge count", 
		description = "Shows selected edge count", 
		default = False)	
		
	# face checkBoxes
	scene.face_count_all = BoolProperty( 
		name="Show all face count", 
		description = "Shows all face count", 
		default = False)
	scene.face_count_obj = BoolProperty( 
		name="Show obj face count", 
		description = "Shows selected object face count", 
		default = False)
	scene.face_count_sel = BoolProperty( 
		name="Show sel face count", 
		description = "Shows selected face count", 
		default = False)

	# triangle checkBoxes
	scene.tri_count_all = BoolProperty(
		name="Show all triangle count", 
		description = "Shows all triangle count", 
		default = False)
	scene.tri_count_obj = BoolProperty( 
		name="Show obj face count", 
		description = "Shows selected obj triangle count", 
		default = False)
	scene.tri_count_sel = BoolProperty( 
		name="Show sel face count", 
		description = "Shows selected triangle count", 
		default = False)	 

# clear the properties
# figure this out...


def clear_properties(): 
    props = ["polycount_run", "polycount_pos_x", "polycount_pos_y", 
     "polycount_font_size", "polycount_font_color", 
     "polycount_show_in_3d_view", "show_vertex_count", "show_edge_count", "show_face_count", "show_triangle_count", "vert_count_all", "vert_count_obj", "vert_count_sel", "edge_count_all", "edge_count_obj", "edge_count_sel", "face_count_all", "face_count_obj", "face_count_sel", "tri_count_all", "tri_count_obj", "tri_count_sel" ] 
     
    for p in props: 
        if bpy.context.window_manager.get(p) != None: 
            del bpy.context.window_manager[p] 
        try: 
            x = getattr(bpy.types.WindowManager, p) 
            del x 
        except: 
            pass

