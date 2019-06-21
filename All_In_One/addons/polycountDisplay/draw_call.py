import bpy, bgl ,blf

def get_display_location(context): 
    scene = context.scene 
  
    width = context.region.width 
    height = context.region.height 
  
    pos_x = scene.polycount_pos_x 
    pos_y = height - scene.polycount_pos_y 
  
    return(pos_x, pos_y) 
  
def draw_callback_px(self, context): 
    wm = context.window_manager 
    sc = context.scene 
  
    if not wm.polycount_run: 
        return
  
    font_size  = sc.polycount_font_size 
    pos_x, pos_y = get_display_location(context) 
  
    # draw text in the 3d-view 
    # ======================== 
    blf.size(0, sc.polycount_font_size, 72) 
    r, g, b = sc.polycount_font_color 
    bgl.glColor3f(r, g, b) 
  
    view3dId = get_space_id(context.space_data) 
      
#    text = "All               Obj              Sel"
#    blf.position(0, pos_x + 15, pos_y, 0)
#    blf.draw(0, text)    
#    

######## vertex Drawing
    
    if sc.show_vertex_count == True:
        text = "V"
        blf.position(0, pos_x , pos_y, 0)
        blf.draw(0, text)

        if vert_count_all == True:
            all_vert_count = polyCountOperator.all_edge_count.get(view3dId, -1)
            if all_vert_count > 0:
                text = format(all_tri_count, ',d')
                text3width = blf.dimensions(0, text)[0] 

                blf.position(0, pos_x + 135 , pos_y , 0) 
                blf.draw(0, text)               
            else:
                text = "0"  	  
                blf.position(0, pos_x + 135, pos_y , 0) 
                blf.draw(0, text)
        else:
            text = "X"
            blf.position(0, pos_X, pos_y - 20, 0)
            blf.draw(o,text)

        if vert_count_obj == True:
            obj_vert_count = polyCountOperator.all_edge_count.get(view3dId, -1)
            if obj_vert_count > 0:
                text = format(obj_vert_count, ',d')
                text3width = blf.dimensions(0, text)[0] 

                blf.position(0, pos_x + 135 , pos_y , 0) 
                blf.draw(0, text)
            else:
                text = "0"  	  
                blf.position(0, pos_x + 135, pos_y , 0) 
                blf.draw(0, text)
        else:
            text = "X"
            blf.position(0, pos_X, pos_y - 20, 0)
            blf.draw(o,text)			

        if vert_count_sel == True:
            sel_vert_count = polyCountOperator.all_edge_count.get(view3dId, -1)
            if sel_vert_count > 0:
                text = format(sel_vert_count, ',d')
                text3width = blf.dimensions(0, text)[0] 

                blf.position(0, pos_x + 135 , pos_y , 0) 
                blf.draw(0, text)
            else:
                text = "0"  	  
                blf.position(0, pos_x + 135, pos_y , 0) 
                blf.draw(0, text)
        else:
            text = "X"
            blf.position(0, pos_X, pos_y - 20, 0)
            blf.draw(o,text)	
def get_triangle_count_edit(object):
    obj = bpy.context.active_object
    if obj.mode == 'OBJECT':
        sel_tris = 0
    else:
        bm = bmesh.from_edit_mesh(obj.data)
        sel_faces = [face for face in bm.faces if face.select]
        sel_tris = sum([len(sel_faces[i].verts)-2 for i in range(0,len(sel_faces))])
#    print(sel_tris)
    return sel_tris


def get_triangle_count(object):
    triangle_count = 0
    decimateIdx = -1

    for modifierIdx, modifier in enumerate(list(object.modifiers)):
        if modifier.type == 'DECIMATE' and modifier.show_viewport:
            triangle_count = modifier.face_coun
            decimateIdx = modifierIdx

    if decimateIdx == -1:
        for p in object.data.polygons:
            count = p.loop_total
            if count > 2:
                triangle_count += count - 2

    for modifierIdx, modifier in enumerate(list(object.modifiers)):
        if modifier.type == 'MIRROR' and modifier.show_viewport and modifierIdx > decimateIdx:
            if modifier.use_x:
                triangle_count *= 2
            if modifier.use_y:
                triangle_count *= 2
            if modifier.use_z:
                triangle_count *= 2

    return triangle_count

def get_vertex_count(object):
    return len(object.data.vertices)
			
'''			
######## edge drawing        
    text = "E"
    blf.position(0, pos_x , pos_y - 20, 0)
    blf.draw(0, text)
    
    all_edge_count = PolyCountOperator.all_edge_count.get(view3dId, -1) 
    
    if all_edge_count > 0:
        text = format(all_edge_count, 'd')
        text1height = blf.dimensions(0, text)[1]

        blf.position(0, pos_x + 15, pos_y , 0)
        blf.draw(0, text)
    else:
        text = "0"  
        text1height = blf.dimensions(0, text)[1] 
  
        blf.position(0, pos_x + 15, pos_y , 0) 
        blf.draw(0, text)

######## face drawing
    text = "F"
    blf.position(0, pos_x , pos_y - 40, 0)
    blf.draw(0, text)
    
    all_face_count = PolyCountOperator.all_face_count.get(view3dId, -1) 
    
    
####### triangle Drawing    

    text = "T"
    blf.position(0, pos_x , pos_y  - 60, 0)
    blf.draw(0, text)
    
    # all triangle count
    all_tri_count = PolyCountOperator.all_triangle_count.get(view3dId, -1) 

    if all_tri_count > -1:
        text = format(all_tri_count, 'd')
        text1height = blf.dimensions(0, text)[1]

        blf.position(0, pos_x + 15, pos_y , 0)
        blf.draw(0, text)
    else:
        text = "0"  
        text1height = blf.dimensions(0, text)[1] 
  
        blf.position(0, pos_x + 15, pos_y , 0) 
        blf.draw(0, text)
        
    #object triangle count  
    obj_tri_count = PolyCountOperator.obj_triangle_count.get(view3dId, -1)
  
    if obj_tri_count > 0: 
        text = format(obj_tri_count, ',d')
        text2width = blf.dimensions(0, text)[0] 
        
        blf.position(0, pos_x + 75 , pos_y , 0) 
        blf.draw(0, text)
    else:
        text = "0"  
        text2width = blf.dimensions(0, text)[0] 
  
        blf.position(0, pos_x + 75 , pos_y  , 0) 
        blf.draw(0, text)

    # selected triangle count
    sel_tri_count = PolyCountOperator.sel_triangle_count.get(view3dId, -1)
    
    if sel_tri_count > 0:
        text = format(sel_tri_count, ',d')
        text3width = blf.dimensions(0, text)[0] 
  
        blf.position(0, pos_x + 135 , pos_y , 0) 
        blf.draw(0, text)
    else:
        text = "0"  
        text3width = blf.dimensions(0, text)[0] 
  
        blf.position(0, pos_x + 135, pos_y , 0) 
        blf.draw(0, text)

