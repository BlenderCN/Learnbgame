bl_info = {
    "name": "Mesh Editing",
    "author": "Marvin K. Breuer ",
    "blender": (2, 68, 1),
    "location": "View3D > Tool Shelf > Mesh Face Tool",
    "description": "Editing the Mesh with Editing Tools",
    "category": "Learnbgame",
}

import bpy

from bpy.props import PointerProperty, EnumProperty, FloatProperty, BoolProperty
from mathutils import Vector
from mathutils.geometry import intersect_point_line, intersect_line_plane

import bmesh
from mathutils import *
import math

class MeshTools (bpy.types.Panel):
    bl_label = "Mesh Editing"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "mesh_edit"
    

    def draw(self, context):
        layout = self.layout
    
        
#-------------Transform----------------------             
        
        
        col = layout.column(align=True)
        col.label(text="Transform:")
        
            
        row = col.row(align=True)
        row.operator("transform.shear",text="Shear")
        row.operator("transform.warp", text="Warp")
        row.operator("transform.tosphere", text="to Sphere")
        
        row = col.row(align=True)
        row.operator("mesh.edgetune", text="Edgetune")
        row.operator("transform.edge_slide", text="Slide Edge")
        row.operator("transform.vert_slide", text="Slide Vertex")
        
        row = col.row(align=True)
        row.operator("transform.mirror", text="Mirror")
        row.operator("transform.shrink_fatten", text="Shrink / Flatten")
        row.operator("transform.push_pull", text="Push / Pull")


#-------------Align------------------------------------------------------------           
        
        
        col = layout.column(align=True)
        col.label(text="Align:")
        
        row = col.row(align=True)  
        row.operator("mesh.vertex_align",text="Align")
        row.operator("transform.resize",text="Resize")
        row.operator("va.op3_id",text="X/Y/Z")
        
        row = col.row(align=True)
        row.operator("mesh.vertex_distribute",text="Distribute")
        row.operator("mesh.edge_rotate",text="Rotate Edge")
        row.operator_menu_enum("mesh.merge", "type")
        
       

        

#-------------Insert------------------------------------------------------------        
        
        
        col = layout.column(align=True)
        col.label(text="Insert:")
               
        row = col.row(align=True)
        row.operator("mesh.inset", text="Inset")
        row.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude Region")
        
                
        row = col.row(align=True)
        row.operator("mesh.insetpoly", text="Inset Poly")
        row.operator("view3d.edit_mesh_extrude_individual_move", text="Extrude Individual")
                  
        
        row = col.row(align=True)
        row.operator('faceinfillet.op0_id', text = 'Inset Fillet')
        row.operator('object.mextrude', text = "Extrude Multi ")
        
        
        row = col.row(align=True)
        row.operator("mesh.insert_edge_ring",text="Edge Ring")
        row.operator("mesh.solidify", text="Solidify")
        row.operator("mesh.bevel", text="Bevel") 
        row.operator("mesh.wireframe", text="Wire")
        
        
        col = layout.column(align=True) 
        row = col.row(align=True)
        OPSP=row.operator("mesh.spin",text="Spin")
        OPSC=row.operator("mesh.screw", text="Screw")
        row = col.row(align=True)
        row.prop(context.scene, "sst", text="Turns")
        row.prop(context.scene, "sss", text="Steps")
        OPSP.steps=context.scene.sss
        OPSP.angle=(context.scene.sst*6.283185307179586476925286766559)
        OPSC.steps=context.scene.sss
        OPSC.turns=context.scene.sst
        

#-------------Fill------------------------------------------------------------        
        
        
        col = layout.column(align=True)
        col.label(text="Fill:")
        
        row = col.row(align=True)
        row.operator("mesh.f2", text="F2")
        row.operator("mesh.fill_grid", text="Grid")
        row.operator("mesh.poke", text="Poke")
        
        row = col.row(align=True)
        row.operator("mesh.beautify_fill", text="Beautify")
        row.operator("mesh.fill_holes", text="Holes")
        row.operator("mesh.bridge_edge_loops",text="Bridge Edges")        



#-------------open------------------------------------------------------------          
        
        
        col = layout.column(align=True)
        col.label(text="Open:")
        
        row = col.row(align=True)  
        row.operator("mesh.rip_move")
        row.operator("mesh.rip_move_fill")
        row.operator("mesh.edge_split")  
        
               

#-------------Symmetry------------------------------------------------------------  
        
             
        col = layout.column(align=True)
        col.label(text="")
        
        
        row = col.row(align=True)
        row.operator("object.vertext_group_add_new", text="Vertex Group")  
        
        
        
       
#-------------Symmetry------------------------------------------------------------  
        
             
        col = layout.column(align=True)
        col.label(text="Symmerty:")
        
        
        row = col.row(align=True)
        row.operator("mesh.symmetrize", text="Add Symmetry")
        row.operator("mesh.symmetry_snap", text="Snap Symmerty")




#-------------Selections------------------------------------------------------------        
        
     
        
        col = layout.column(align=True)
        col.label(text="Selections:")
        
        
        row = col.row(align=True)
        row.operator("mesh.f2f_fvnef", text="Vert Neighb.")
        row.operator("mesh.f2f_fef", text="Edge Neighb.")
        row.operator("mesh.conway", text="only Edges")
             
        
        
        row = col.row(align=True)
        row.operator("mesh.select_similar", text="Similar")
        row.operator("mesh.select_random",text="Random")
        row.operator("mesh.select_loose",text="Loose")
        
        row = col.row(align=True)
        row.operator("mesh.select_mirror",text="Mirror")
        row.operator("mesh.select_mirror",text="Sharp Edges")
        row.operator("mesh.select_more",text="+")
        row.operator("mesh.select_less",text="-")
        
        
  




  





#-------------Relax------------------------------------------------------------            
           


        col = layout.column(align=True)
        col.label(text="Relax:")
        
        row = col.row(align=True)
        row.operator("mesh.relax")
        row.operator("mesh.noise")
        row.operator("mesh.vertices_smooth")
        
        row = col.row(align=True)
        row.operator("mesh.polyredux", text="Poly Redux")
        row.operator("mesh.laprelax", text="Laplace Relax")
        
        row = col.row(align=True)
        row.prop(scn, "Repeat", text="Laplace Repeat")
        
        
        


   



 
        
        
  
        
    
   
#-------------Registry------------------------------------------------------------          

  


def register():
    bpy.utils.register_class(MeshTools)


def unregister():
    bpy.utils.unregister_class(MeshTools)


if __name__ == "__main__":
    register()
    
    
    
 
 
# ------------------Vertex align > Author: zmj100 -------------------------------------------------------
    
    # -*- coding: utf-8 -*-

# ------ ------
bl_info = {
    'name': 'vertex align',
    'author': '',
    'version': (0, 1, 6),
    'blender': (2, 6, 1),
    'api': 43085,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    "category": "Learnbgame",
}

# ------ ------


# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

# ------ ------
def get_mesh_data_():
    edit_mode_out()
    ob_act = bpy.context.active_object
    me = ob_act.data    
    edit_mode_in()
    return me    
    
def list_clear_(l):
    l[:] = []
    return l

# -- -- -- --
class va_p_group0(bpy.types.PropertyGroup):

    en0 = EnumProperty( items =( ('opt0', 'Original vertex', ''),
                                 ('opt1', 'Custom coordinates', ''),
                                 ('opt2', 'Line', ''),
                                 ('opt3', 'Plane', '')),
                        name = 'Align to',
                        default = 'opt0' )

    en1 = EnumProperty( items =( ('en1_opt0', 'x', ''),
                                 ('en1_opt1', 'y', ''),
                                 ('en1_opt2', 'z', '')),
                        name = 'Axis',
                        default = 'en1_opt0' )

# ------ ------
class va_buf():
    list_v = []
    list_f = []
    list_0 = []

# ------ panel 0 ------
class va_p0(bpy.types.Panel):

   
   
    
    

    def draw(self, context):
        cen0 = context.scene.va_custom_props.en0
        layout = self.layout
        layout.prop(context.scene.va_custom_props, 'en0', expand = False)
        
        if cen0 == 'opt0':
            row = layout.split(0.60)
            row.label('Store data:')
            row.operator('va.op0_id', text = 'Vertex')
            row1 = layout.split(0.80)
            row1.operator('va.op2_id', text = 'Align')
            row1.operator('va.op7_id', text = '?')
        elif cen0 == 'opt1':
            layout.operator('va.op3_id', text = 'Align')
        elif cen0 == 'opt2':
            row = layout.split(0.40)
            row.label('Store data:')
            row.operator('va.op0_id', text = 'Two vertices')
            layout.operator('va.op5_id', text = 'Align')
        elif cen0 == 'opt3':
            row = layout.split(0.60)
            row.label('Store data:')
            row.operator('va.op1_id', text = 'Face')
            layout.operator('va.op6_id', text = 'Align')

# ------ operator 0 ------
class va_op0(bpy.types.Operator):
    bl_idname = 'va.op0_id'
    bl_label = ''

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(va_buf.list_v)
        for v in me.vertices:
            if v.select:
                va_buf.list_v.append(v.index)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 1 ------
class va_op1(bpy.types.Operator):
    bl_idname = 'va.op1_id'
    bl_label = ''

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(va_buf.list_f)
        for f in me.faces:
            if f.select:
                va_buf.list_f.append(f.index)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 2 ------ align to original
class va_op2(bpy.types.Operator):
    bl_idname = 'va.op2_id'
    bl_label = 'Align to original'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.label('Axis:')
        layout.prop(context.scene.va_custom_props, 'en1', expand = True)

    def execute(self, context):

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data
        cen1 = context.scene.va_custom_props.en1
        list_0 = [v.index for v in me.vertices if v.select]

        if len(va_buf.list_v) == 0:
            self.report({'INFO'}, 'Original vertex not stored in memory')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(va_buf.list_v) != 0:
            if len(list_0) == 0:
                self.report({'INFO'}, 'No vertices selected')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(list_0) != 0:
                vo = (me.vertices[va_buf.list_v[0]].co).copy()
                if cen1 == 'en1_opt0':
                    for i in list_0:
                        v = (me.vertices[i].co).copy()
                        me.vertices[i].co = Vector(( vo[0], v[1], v[2] ))
                elif cen1 == 'en1_opt1':
                    for i in list_0:
                        v = (me.vertices[i].co).copy()
                        me.vertices[i].co = Vector(( v[0], vo[1], v[2] ))
                elif cen1 == 'en1_opt2':
                    for i in list_0:
                        v = (me.vertices[i].co).copy()
                        me.vertices[i].co = Vector(( v[0], v[1], vo[2] ))
        edit_mode_in()
        return {'FINISHED'}
    
# ------ operator 3 ------ align to custom coordinates
class va_op3(bpy.types.Operator):
    bl_idname = 'va.op3_id'
    bl_label = ''

    def execute(self, context):
        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data
        list_clear_(va_buf.list_0)
        va_buf.list_0 = [v.index for v in me.vertices if v.select][:]
        if len(va_buf.list_0) == 0:
            self.report({'INFO'}, 'No vertices selected')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(va_buf.list_0) != 0:
            bpy.ops.va.op4_id('INVOKE_DEFAULT')
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 4 ------ align to custom coordinates
class va_op4(bpy.types.Operator):
    bl_idname = 'va.op4_id'
    bl_label = 'Align to custom coordinates'
    bl_options = {'REGISTER', 'UNDO'}
    
    x = y = z = FloatProperty( name = '', default = 0.0, min = -100.0, max = 100.0, step = 1, precision = 3 )
    b_x = b_y = b_z = BoolProperty()

    def draw(self, context):
        layout = self.layout
        row = layout.split(0.25)
        row.prop(self, 'b_x', text = 'x')
        row.prop(self, 'x')
        row = layout.split(0.25)
        row.prop(self, 'b_y', text = 'y')
        row.prop(self, 'y')
        row = layout.split(0.25)
        row.prop(self, 'b_z', text = 'z')
        row.prop(self, 'z')
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 200)

    def execute(self, context):
        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data
            
        for i in va_buf.list_0:
            v = (me.vertices[i].co).copy()
            tmp = Vector((v[0], v[1], v[2]))
            if self.b_x == True:
                tmp[0] = self.x
            if self.b_y == True:
                tmp[1] = self.y
            if self.b_z == True:
                tmp[2] = self.z
            me.vertices[i].co = tmp
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 5 ------ align to line
class va_op5(bpy.types.Operator):
    bl_idname = 'va.op5_id'
    bl_label = 'Align to line'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data
        list_0 = [v.index for v in me.vertices if v.select]
        
        if len(va_buf.list_v) != 2:
            self.report({'INFO'}, 'Two guide vertices must be stored in memory.')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(va_buf.list_v) > 1:
            if len(list_0) == 0:
                self.report({'INFO'}, 'No vertices selected')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(list_0) != 0:
                p1 = (me.vertices[va_buf.list_v[0]].co).copy()
                p2 = (me.vertices[va_buf.list_v[1]].co).copy()
                for i in list_0:
                    v = (me.vertices[i].co).copy()
                    me.vertices[i].co = intersect_point_line( v, p1, p2)[0]
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 6 ------ align to plane
class va_op6(bpy.types.Operator):
    bl_idname = 'va.op6_id'
    bl_label = 'Align to plane'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data
        list_0 = [v.index for v in me.vertices if v.select]
        
        if len(va_buf.list_f) == 0:
            self.report({'INFO'}, 'No face stored in memory')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(va_buf.list_f) != 0:
            if len(list_0) == 0:
                self.report({'INFO'}, 'No vertices selected')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(list_0) != 0:
                f = me.faces[va_buf.list_f[0]]
                for i in list_0:
                    v = (me.vertices[i].co).copy()
                    p = v + ((f.normal).copy() * 0.1)
                    pp = (me.vertices[f.vertices[0]].co).copy()
                    pn = (f.normal).copy()
                    me.vertices[i].co = intersect_line_plane(v, p, pp, pn)
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 7 ------
class va_op7(bpy.types.Operator):

    bl_idname = 'va.op7_id'
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        layout.label('Help:')
        layout.label('To use select whatever you want vertices to be aligned to ')
        layout.label('and click button next to store data label. ')
        layout.label('Select vertices that you want to align and click Align button. ')
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width = 400)

# ------ operator 8 ------
class va_op8(bpy.types.Operator):
    bl_idname = 'va.op8_id'
    bl_label = ''

    def execute(self, context):
        bpy.ops.va.op7_id('INVOKE_DEFAULT')
        return {'FINISHED'}

# ------ ------
class_list = [ va_p0, va_op0, va_op1, va_op2, va_op3, va_op4, va_op5, va_op6,  va_op7, va_op8, va_p_group0 ]

# ------------------ > Author: -------------------------------------------------------


## registring
def register():
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()
    
    
# ------------------LapRelax -------------------------------------------------------    

bl_info = {
	"name": "LapRelax",
	"author": "Gert De Roost",
	"version": (0, 1, 0),
	"blender": (2, 6, 3),
	"location": "View3D > Tools",
	"description": "Smoothing mesh keeping volume",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
}

if "bpy" in locals():
    import imp




bpy.types.Scene.Repeat = bpy.props.IntProperty(
		name = "Repeat", 
		description = "Repeat how many times",
		default = 1,
		min = 1,
		max = 100)



class LapRelax(bpy.types.Operator):
	bl_idname = "mesh.laprelax"
	bl_label = "LapRelax"
	bl_description = "Smoothing mesh keeping volume"
	bl_options = {"REGISTER", "UNDO"}
	

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

	def invoke(self, context, event):
		
		scn = bpy.context.scene
		
		self.save_global_undo = bpy.context.user_preferences.edit.use_global_undo
		bpy.context.user_preferences.edit.use_global_undo = False
		
		for i in range(scn.Repeat):
			do_laprelax(self)
		
		return {'FINISHED'}


def panel_func(self, context):
	
	scn = bpy.context.scene
	
	self.layout.prop(scn, "Repeat", text="Laplace Repeat")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.MeshTools.append(panel_func)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.MeshTools.remove(panel_func)


if __name__ == "__main__":
	register()




def do_laprelax(self):

	context = bpy.context
	region = context.region  
	area = context.area
	selobj = bpy.context.active_object
	mesh = selobj.data
	bm = bmesh.from_edit_mesh(mesh)
	bmprev = bm.copy()

	for v in bmprev.verts:
		if v.select:
			tot = Vector((0, 0, 0))
			cnt = 0
			for e in v.link_edges:
				if len(e.link_faces) == 1:
					cnt = 1
					break
			if cnt:
				continue
			for e in v.link_edges:
				tot += e.other_vert(v).co
			tot /= len(v.link_edges)
			delta = (tot - v.co)
			if delta.length != 0:
				ang = delta.angle(v.normal)
				deltanor = math.cos(ang) * delta.length
				nor = v.normal
				nor.length = abs(deltanor)
				bm.verts[v.index].co = tot + nor
		
		
	mesh.update()
	bm.free()
	bmprev.free()
	bpy.context.user_preferences.edit.use_global_undo = self.save_global_undo
	bpy.ops.object.editmode_toggle()
	bpy.ops.object.editmode_toggle()
	



bl_info = {
	"name": "DeathGuppie",
	"author": "Gert De Roost",
	"version": (0, 2, 2),
	"blender": (2, 6, 3),
	"location": "View3D > Tools",
	"description": "Deathguppie subdivision operation",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
}

if "bpy" in locals():
    import imp


import bpy
import bmesh


bpy.types.Scene.Smooth = bpy.props.BoolProperty(
		name = "Smoothing", 
		description = "Subdivide smooth",
		default = True)

bpy.types.Scene.Inner = bpy.props.BoolProperty(
		name = "Select inner only", 
		description = "After operation only inner verts selected",
		default = True)


class DeathGuppie(bpy.types.Operator):
	bl_idname = "mesh.deathguppie"
	bl_label = "DeathGuppie"
	bl_description = "Deathguppie subdivision operation"
	bl_options = {"REGISTER", "UNDO"}
	

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

	def invoke(self, context, event):
		
		self.save_global_undo = bpy.context.user_preferences.edit.use_global_undo
		bpy.context.user_preferences.edit.use_global_undo = False
		
		do_deathguppie(self)
		
		return {'FINISHED'}


def panel_func(self, context):
	
	scn = bpy.context.scene
	self.layout.label(text="DeathGuppie:")
	self.layout.operator("mesh.deathguppie", text="Subdivide DG")
	self.layout.prop(scn, "Smooth")
	self.layout.prop(scn, "Inner")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.MeshTools.append(panel_func)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.MeshTools.remove(panel_func)


if __name__ == "__main__":
	register()




def do_deathguppie(self):
		
	global smoothset, cornerlist, innerlist, vselset

	context = bpy.context
	region = context.region  
	area = context.area
	selobj = bpy.context.active_object

	bpy.ops.object.editmode_toggle()
	bpy.ops.object.duplicate()
	projobj = bpy.context.active_object
	bpy.ops.object.editmode_toggle()
	bpy.ops.mesh.subdivide(number_cuts=5, smoothness=1.0)
	bpy.ops.object.editmode_toggle()
	projobj.hide = 1
	bpy.context.scene.objects.active = selobj
	bpy.ops.object.editmode_toggle()

	mesh = selobj.data
	bm = bmesh.from_edit_mesh(mesh)
	bmkeep = bm.copy()

	facelist = []
	for f1 in bm.faces:
		if f1.select:
			linked = []
			for e in f1.edges:
				for f2 in e.link_faces:
					if f2 != f1:
						if f2.select:
							linked.append(f2.index)
							break
			facelist.insert(0, [])
			facelist[0].append(f1)
			facelist[0].append(linked)
	

	transfer = {}
	holdlist = []	
	for [f, linked] in facelist:
		bpy.ops.mesh.select_all(action="DESELECT")
		f.select = 1
		transfer[f.calc_center_median()[:]] = [f.index, linked]
		bpy.ops.mesh.split()
				
	bpy.ops.object.editmode_toggle()
	bpy.ops.object.editmode_toggle()
	bm = bmesh.from_edit_mesh(mesh)
	facelist = []
	for f in bm.faces:
		num = 0
		for e in f.edges:
			if len(e.link_faces) == 1:
				num += 1
		if num == 4:
			if f.calc_center_median()[:] in transfer.keys():
				f.select = 1
				facelist.insert(0, [])
				facelist[0].append(f)
				facelist[0].append(transfer[f.calc_center_median()[:]])
				

	def createinnerlists(f):
	
		global smoothset, cornerlist, innerlist, vselset
		
		for l in f.loops:
			cornerlist.append(l.vert)
			vselset.add(l.vert)
			v1 = l.vert
			vnext = l.link_loop_next.vert
			vprev = l.link_loop_prev.vert
			vnextnext = l.link_loop_next.link_loop_next.vert
			vprevprev = l.link_loop_prev.link_loop_prev.vert
			tempco1 = v1.co + (vprev.co - v1.co) / 3
			tempco2 = vnext.co + (vnextnext.co - vnext.co) / 3
			vert = bm.verts.new(tempco1 + ((tempco2 - tempco1) / 3))
			innerlist.append(vert)
			smoothset.add(vert)
	
	scn = bpy.context.scene
	vselset = set([])
	fselset = set([])
	smoothset = set([])
	for [f, [foldidx, linked]] in facelist:
		fold = bmkeep.faces[foldidx]
		linked2 = []
		for idx in linked:
			linked2.append(bmkeep.faces[idx])
		cornerlist = []
		innerlist = []
		if len(linked) == 4:
			createinnerlists(f)
			for e in f.edges:
				ne, vert1 = bmesh.utils.edge_split(e, e.verts[0], 0.66)		
				ne, vert2 = bmesh.utils.edge_split(ne, vert1, 0.5)
				vselset.add(vert1)
				vselset.add(vert2)
				smoothset.add(vert1)
				smoothset.add(vert2)
			for idx in range(len(cornerlist)):
				cv = cornerlist[idx]
				for l in f.loops:
					if l.vert == cv:
						fs = bm.faces.new((cv, l.link_loop_next.vert, innerlist[idx], l.link_loop_prev.vert))
						fselset.add(fs)
						fs = bm.faces.new((l.link_loop_prev.vert, l.link_loop_prev.link_loop_prev.vert, innerlist[idx - 1], innerlist[idx]))
						fselset.add(fs)
			fs = bm.faces.new((innerlist[0], innerlist[1], innerlist[2], innerlist[3]))
			fselset.add(fs)
			bm.faces.remove(f)
		elif len(linked) == 3:
			fedges = fold.edges[:]
			for e1 in fedges:
				for f1 in e1.link_faces:
					if len(e1.link_faces) == 1 or (f1 != fold and not(f1 in linked2)):
						edge = f.edges[fedges.index(e1)]
			createinnerlists(f)
			for e in f.edges:
				if e != edge:
					ne, vert1 = bmesh.utils.edge_split(e, e.verts[0], 0.66)		
					ne, vert2 = bmesh.utils.edge_split(ne, vert1, 0.5)
					vselset.add(vert1)
					vselset.add(vert2)
					smoothset.add(vert1)
					smoothset.add(vert2)
			for l in edge.link_loops:
				if l.face == f:
					if l.edge == edge:
						v1 = l.vert
						vnext = l.link_loop_next.vert
						vprev = l.link_loop_prev.vert
						vnextnext = l.link_loop_next.link_loop_next.vert
						vprevprev = l.link_loop_prev.link_loop_prev.vert
						for idx in range(4):
							if cornerlist[idx] == v1:
								co1 = innerlist[idx].co + ((innerlist[idx].co - innerlist[idx-1].co) / 2)
								co2 = innerlist[idx-3].co + ((innerlist[idx-3].co - innerlist[idx-2].co) / 2)
								sidev1 = bm.verts.new(co1)
								sidev2 = bm.verts.new(co2)
								fs = bm.faces.new((v1, vnext, sidev2, sidev1))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((v1, sidev1, innerlist[idx], vprev))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((sidev2, vnext, vnextnext, innerlist[idx-3]))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((sidev1, sidev2, innerlist[idx-3], innerlist[idx]))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((innerlist[idx], innerlist[idx-1], vprevprev, vprev))
								fselset.add(fs)
						cornerlist[cornerlist.index(v1)] = None
						cornerlist[cornerlist.index(vnext)] = None
						break
			for idx in range(len(cornerlist)):
				cv = cornerlist[idx]
				if cv != None:
					for l in f.loops:
						if l.vert == cv:
							fs = bm.faces.new((cv, l.link_loop_next.vert, innerlist[idx], l.link_loop_prev.vert))
							fselset.add(fs)
							fs = bm.faces.new((l.link_loop_prev.vert, l.link_loop_prev.link_loop_prev.vert, innerlist[idx - 1], innerlist[idx]))
							fselset.add(fs)
			fs = bm.faces.new((innerlist[0], innerlist[1], innerlist[2], innerlist[3]))
			fselset.add(fs)
			bm.faces.remove(f)
			smoothset.add(sidev1)
			smoothset.add(sidev2)
		elif len(linked) == 2:
			case = "bridge"
			for vert in linked2[0].verts:
				if vert in linked2[1].verts:
					case = "corner"
					break
			if case == "corner":
				fedges = fold.edges[:]
				edges = []
				for e1 in fedges:
					for f1 in e1.link_faces:
						if len(e1.link_faces) == 1 or (f1 != fold and not(f1 in linked2)):
							edges.append(f.edges[fedges.index(e1)])
				for l in edges[1].link_loops:
					if l.face == f:
						if l.edge == edges[1] and l.link_loop_next.edge == edges[0]:
							edges.reverse()
							break
				createinnerlists(f)			
				for e in f.edges:
					if not(e in edges):
						ne, vert1 = bmesh.utils.edge_split(e, e.verts[0], 0.66)		
						ne, vert2 = bmesh.utils.edge_split(ne, vert1, 0.5)
						vselset.add(vert1)
						vselset.add(vert2)
						smoothset.add(vert1)
						smoothset.add(vert2)
				for l in edges[0].link_loops:
					if l.face == f:
						if l.edge == edges[0]:
							if l.link_loop_next.edge == edges[1]:
								v1 = l.vert
								vnext = l.link_loop_next.vert
								vprev = l.link_loop_prev.vert
								vnextnext = l.link_loop_next.link_loop_next.vert
								vnnn = l.link_loop_next.link_loop_next.link_loop_next.vert
								vprevprev = l.link_loop_prev.link_loop_prev.vert
								vppp = l.link_loop_prev.link_loop_prev.link_loop_prev.vert
								vpppp = l.link_loop_prev.link_loop_prev.link_loop_prev.link_loop_prev.vert
								for idx in range(4):
									if cornerlist[idx] == v1:
										delta1 = (innerlist[idx].co - innerlist[idx-1].co) / 2
										co1 = innerlist[idx].co + delta1
										delta2 = (innerlist[idx-3].co - innerlist[idx].co) / 2
										delta3 = (innerlist[idx-3].co - innerlist[idx-2].co) / 2
										co2 = innerlist[idx-3].co + delta1 + delta2
										sidev1 = bm.verts.new(co1)
										sidev2 = bm.verts.new(co2)
										sidev3 = bm.verts.new(innerlist[idx-2].co + ((innerlist[idx-2].co - innerlist[idx-1].co) / 2))
										
										fs = bm.faces.new((v1, vnext, sidev2, sidev1))
										if not(scn.Inner):
											fselset.add(fs)
										fs = bm.faces.new((sidev3, sidev2, vnext, vnextnext))
										if not(scn.Inner):
											fselset.add(fs)
										fs = bm.faces.new((v1, sidev1, innerlist[idx], vprev))
										if not(scn.Inner):
											fselset.add(fs)
										fs = bm.faces.new((innerlist[idx-2], sidev3, vnextnext, vnnn))
										if not(scn.Inner):
											fselset.add(fs)
										fs = bm.faces.new((sidev1, sidev2, innerlist[idx-3], innerlist[idx]))
										if not(scn.Inner):
											fselset.add(fs)
										fs = bm.faces.new((sidev2, sidev3, innerlist[idx-2], innerlist[idx-3]))
										if not(scn.Inner):
											fselset.add(fs)
										fs = bm.faces.new((vprevprev, vprev, innerlist[idx], innerlist[idx-1]))
										fselset.add(fs)
										fs = bm.faces.new((vpppp, vppp, vprevprev, innerlist[idx-1]))
										fselset.add(fs)
										fs = bm.faces.new((vnnn, vpppp, innerlist[idx-1], innerlist[idx-2]))
										fselset.add(fs)
										break
								break
				fs = bm.faces.new((innerlist[0], innerlist[1], innerlist[2], innerlist[3]))
				fselset.add(fs)
				bm.faces.remove(f)
				smoothset.add(sidev1)
				smoothset.add(sidev2)
				smoothset.add(sidev3)
			else:
				fedges = fold.edges[:]
				edges = []
				for e1 in fedges:
					for f1 in e1.link_faces:
						if len(e1.link_faces) == 1 or (f1 != fold and not(f1 in linked2)):
							edges.append(f.edges[fedges.index(e1)])
				createinnerlists(f)			
				for e in f.edges:
					if not(e in edges):
						ne, vert1 = bmesh.utils.edge_split(e, e.verts[0], 0.66)		
						ne, vert2 = bmesh.utils.edge_split(ne, vert1, 0.5)
						vselset.add(vert1)
						vselset.add(vert2)
						smoothset.add(vert1)
						smoothset.add(vert2)
				for l in f.loops:
					if l.edge == edges[0]:
						v1 = l.vert
						vnext = l.link_loop_next.vert
						vprev = l.link_loop_prev.vert
						vnextnext = l.link_loop_next.link_loop_next.vert
						vnnn = l.link_loop_next.link_loop_next.link_loop_next.vert
						vnnnn = l.link_loop_next.link_loop_next.link_loop_next.link_loop_next.vert
						vprevprev = l.link_loop_prev.link_loop_prev.vert
						vppp = l.link_loop_prev.link_loop_prev.link_loop_prev.vert
						vpppp = l.link_loop_prev.link_loop_prev.link_loop_prev.link_loop_prev.vert
						for idx in range(4):
							if cornerlist[idx] == v1:
								delta1 = (innerlist[idx].co - innerlist[idx-1].co) / 2
								co1 = innerlist[idx].co + delta1
								sidev1 = bm.verts.new(co1)
								delta2 = (innerlist[idx-3].co - innerlist[idx-2].co) / 2
								co2 = innerlist[idx-3].co + delta2
								sidev2 = bm.verts.new(co2)
								delta3 = (innerlist[idx-2].co - innerlist[idx-3].co) / 2
								co3 = innerlist[idx-2].co + delta3
								sidev3 = bm.verts.new(co3)
								delta4 = (innerlist[idx-1].co - innerlist[idx].co) / 2
								co4 = innerlist[idx-1].co + delta4
								sidev4 = bm.verts.new(co4)
								fs = bm.faces.new((v1, vnext, sidev2, sidev1))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((v1, sidev1, innerlist[idx], vprev))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((vnext, vnextnext, innerlist[idx-3], sidev2))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((sidev1, sidev2, innerlist[idx-3], innerlist[idx]))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((vppp, sidev4, sidev3, vnnnn))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((vppp, vprevprev, innerlist[idx-1], sidev4))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((sidev3, innerlist[idx-2], vnnn, vnnnn))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((sidev3, sidev4, innerlist[idx-1], innerlist[idx-2]))
								if not(scn.Inner):
									fselset.add(fs)
								fs = bm.faces.new((vprevprev, vprev, innerlist[idx], innerlist[idx-1]))
								fselset.add(fs)
								fs = bm.faces.new((vnextnext, vnnn, innerlist[idx-2], innerlist[idx-3]))
								fselset.add(fs)
								
				fs = bm.faces.new((innerlist[0], innerlist[1], innerlist[2], innerlist[3]))
				fselset.add(fs)
				bm.faces.remove(f)
				smoothset.add(sidev1)
				smoothset.add(sidev2)
				smoothset.add(sidev3)
				smoothset.add(sidev4)
				
				
		elif len(linked) == 1:
			fedges = fold.edges[:]
			edges = []
			for e1 in fedges:
				for f1 in e1.link_faces:
					if len(e1.link_faces) == 1 or (f1 != fold and not(f1 in linked2)):
						edges.append(f.edges[fedges.index(e1)])
			for l in f.loops:
				if not(l.edge in edges):
					edges = [l.link_loop_next.edge, l.link_loop_next.link_loop_next.edge, l.link_loop_next.link_loop_next.link_loop_next.edge]
			createinnerlists(f)			
			for e in f.edges:
				if not(e in edges):
					ne, vert1 = bmesh.utils.edge_split(e, e.verts[0], 0.66)		
					ne, vert2 = bmesh.utils.edge_split(ne, vert1, 0.5)
					vselset.add(vert1)
					vselset.add(vert2)
					smoothset.add(vert1)
					smoothset.add(vert2)
			for l in f.loops:
				if l.edge == edges[0]:
					v1 = l.vert
					vnext = l.link_loop_next.vert
					vprev = l.link_loop_prev.vert
					vnextnext = l.link_loop_next.link_loop_next.vert
					vnnn = l.link_loop_next.link_loop_next.link_loop_next.vert
					vprevprev = l.link_loop_prev.link_loop_prev.vert
					vppp = l.link_loop_prev.link_loop_prev.link_loop_prev.vert
					vpppp = l.link_loop_prev.link_loop_prev.link_loop_prev.link_loop_prev.vert
					for idx in range(4):
						if cornerlist[idx] == v1:
							delta1 = (innerlist[idx].co - innerlist[idx-1].co) / 2
							co1 = innerlist[idx].co + delta1
							delta2 = (innerlist[idx-3].co - innerlist[idx].co) / 2
							delta3 = (innerlist[idx-3].co - innerlist[idx-2].co) / 2
							co2 = innerlist[idx-3].co + delta1 + delta2
							sidev1 = bm.verts.new(co1)
							sidev2 = bm.verts.new(co2)
							delta4 = (innerlist[idx-2].co - innerlist[idx-1].co) / 2
							delta5 = (innerlist[idx-2].co - innerlist[idx-3].co) / 2
							co3 = innerlist[idx-2].co + delta4 + delta5
							sidev3 = bm.verts.new(co3)
							delta6 = (innerlist[idx-1].co - innerlist[idx].co) / 2
							co4 = innerlist[idx-1].co + delta6
							sidev4 = bm.verts.new(co4)
							fs = bm.faces.new((v1, vnext, sidev2, sidev1))
							if not(scn.Inner):
								fselset.add(fs)
							fs = bm.faces.new((sidev3, sidev2, vnext, vnextnext))
							if not(scn.Inner):
								fselset.add(fs)
							fs = bm.faces.new((v1, sidev1, innerlist[idx], vprev))
							if not(scn.Inner):
								fselset.add(fs)
							fs = bm.faces.new((sidev1, sidev2, innerlist[idx-3], innerlist[idx]))
							if not(scn.Inner):
								fselset.add(fs)
							fs = bm.faces.new((sidev2, sidev3, innerlist[idx-2], innerlist[idx-3]))
							if not(scn.Inner):
								fselset.add(fs)
							fs = bm.faces.new((sidev4, sidev3, vnextnext, vppp))
							if not(scn.Inner):
								fselset.add(fs)
							fs = bm.faces.new((innerlist[idx-2], innerlist[idx-1], sidev4, sidev3))
							if not(scn.Inner):
								fselset.add(fs)
							fs = bm.faces.new((vprevprev, vppp, sidev4, innerlist[idx-1]))
							if not(scn.Inner):
								fselset.add(fs)
							fs = bm.faces.new((vprev, vprevprev, innerlist[idx-1], innerlist[idx]))
							fselset.add(fs)
			fs = bm.faces.new((innerlist[0], innerlist[1], innerlist[2], innerlist[3]))
			fselset.add(fs)
			bm.faces.remove(f)
			smoothset.add(sidev1)
			smoothset.add(sidev2)
			smoothset.add(sidev3)
			smoothset.add(sidev4)
				
		elif len(linked) == 0:
			createinnerlists(f)			
			l = f.loops[0]
			v1 = l.vert
			vnext = l.link_loop_next.vert
			vprev = l.link_loop_prev.vert
			vnextnext = l.link_loop_next.link_loop_next.vert
			for idx in range(4):
				if cornerlist[idx] == v1:
					sidev1 = bm.verts.new((cornerlist[idx].co + innerlist[idx].co) / 2)
					sidev2 = bm.verts.new((cornerlist[idx-3].co + innerlist[idx-3].co) / 2)
					sidev3 = bm.verts.new((cornerlist[idx-2].co + innerlist[idx-2].co) / 2)
					sidev4 = bm.verts.new((cornerlist[idx-1].co + innerlist[idx-1].co) / 2)
					fs = bm.faces.new((v1, vnext, sidev2, sidev1))
					if not(scn.Inner):
						fselset.add(fs)
					fs = bm.faces.new((sidev3, sidev2, vnext, vnextnext))
					if not(scn.Inner):
						fselset.add(fs)
					fs = bm.faces.new((sidev4, sidev3, vnextnext, vprev))
					if not(scn.Inner):
						fselset.add(fs)
					fs = bm.faces.new((sidev1, sidev4, vprev, v1))
					if not(scn.Inner):
						fselset.add(fs)
					fs = bm.faces.new((sidev1, sidev2, innerlist[idx-3], innerlist[idx]))
					if not(scn.Inner):
						fselset.add(fs)
					fs = bm.faces.new((sidev2, sidev3, innerlist[idx-2], innerlist[idx-3]))
					if not(scn.Inner):
						fselset.add(fs)
					fs = bm.faces.new((sidev3, sidev4, innerlist[idx-1], innerlist[idx-2]))
					if not(scn.Inner):
						fselset.add(fs)
					fs = bm.faces.new((sidev4, sidev1, innerlist[idx], innerlist[idx-1]))
					if not(scn.Inner):
						fselset.add(fs)
			fs = bm.faces.new((innerlist[0], innerlist[1], innerlist[2], innerlist[3]))
			fselset.add(fs)
			bm.faces.remove(f)
			smoothset.add(sidev1)
			smoothset.add(sidev2)
			smoothset.add(sidev3)
			smoothset.add(sidev4)
	
	
	scn = bpy.context.scene
	if scn.Smooth:
		for v in smoothset:
			v.co = projobj.closest_point_on_mesh(v.co)[0]
		
	bpy.ops.mesh.select_all(action="SELECT")
	bm.normal_update()
	bpy.ops.mesh.normals_make_consistent()
	bpy.ops.mesh.select_all(action="DESELECT")
	for f in fselset:
		f.select = 1
		for e in f.edges:
			e.select = 1
		for v in f.verts:
			v.select = 1
	for e in bm.edges:
		if len(e.link_faces) == 1:
			e.verts[0].select = 1
			e.verts[1].select = 1
	bpy.ops.mesh.remove_doubles()
	for e in bm.edges:
		if len(e.link_faces) == 1:
			e.verts[0].select = 0
			e.verts[1].select = 0
			e.select = 0
					
	mesh.update()
	bm.free()
	bmkeep.free()
	bpy.context.user_preferences.edit.use_global_undo = self.save_global_undo
	bpy.ops.object.editmode_toggle()
	bpy.ops.object.select_all(action="DESELECT")
	bpy.context.scene.objects.active = projobj
	projobj.hide = 0
	bpy.ops.object.delete()
	selobj.select = 1
	bpy.context.scene.objects.active = selobj
	bpy.ops.object.editmode_toggle()
	
