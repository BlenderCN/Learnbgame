import bpy
import bgl
import blf

from mathutils import Vector
from .func_picker import *
from .utils import intersect_rectangles,point_inside_rectangle,\
point_over_shape,border_over_shape,canevas_space


def draw_polyline_2d_loop(verts,faces,loops,color,contour,width):
    dpi = int(bpy.context.user_preferences.system.pixel_size)

    bgl.glColor4f(*color)
    bgl.glEnable(bgl.GL_BLEND)
    #bgl.glEnable(bgl.GL_LINE_SMOOTH)

    bgl.glColor4f(*color)
    for face in faces :
        bgl.glBegin(bgl.GL_POLYGON)
        for v_index in face :
            coord = verts[v_index]
            bgl.glVertex2f(coord[0],coord[1])
        bgl.glEnd()

    '''
    #antialiasing contour
    bgl.glColor4f(*color)
    bgl.glLineWidth(1)
    for loop in loops :
        if faces :
            bgl.glBegin(bgl.GL_LINE_LOOP)
        else :
            bgl.glBegin(bgl.GL_LINE_STRIP)
        for v_index in loop :
            coord = verts[v_index]
            bgl.glVertex2f(coord[0],coord[1])
        bgl.glEnd()
        '''


    if width :
        bgl.glLineWidth(width*dpi)
        bgl.glColor4f(*contour)

        for loop in loops :
            if faces :
                bgl.glBegin(bgl.GL_LINE_LOOP)
            else :
                bgl.glBegin(bgl.GL_LINE_STRIP)
            for v_index in loop :
                coord = verts[v_index]
                bgl.glVertex2f(coord[0],coord[1])
            bgl.glEnd()

    bgl.glDisable(bgl.GL_BLEND)
    #bgl.glDisable(bgl.GL_LINE_SMOOTH)
    bgl.glEnd()

    return

def draw_border(border) :
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1,1,1,0.2)
    bgl.glBegin(bgl.GL_POLYGON)
    for v in border :
        bgl.glVertex2f(v[0],v[1])

    bgl.glEnd()

    bgl.glColor4f(0.0, 0.0, 0.0, 0.5)
    bgl.glLineWidth(2)
    bgl.glLineStipple(3, 0xAAAA)
    bgl.glEnable(bgl.GL_LINE_STIPPLE)

    bgl.glBegin(bgl.GL_LINE_LOOP)

    for v in border :
        bgl.glVertex2f(v[0],v[1])

    bgl.glEnd()

    bgl.glColor4f(1.0, 1.0, 1.0, 1)
    bgl.glLineWidth(1)
    bgl.glBegin(bgl.GL_LINE_LOOP)
    for v in border :
        bgl.glVertex2f(v[0],v[1])

    bgl.glEnd()
    bgl.glDisable(bgl.GL_LINE_STIPPLE)
    bgl.glDisable(bgl.GL_BLEND)

def draw_text(mouse,text,color) :
    dpi = int(bpy.context.user_preferences.system.pixel_size)

    bgl.glEnable(bgl.GL_BLEND)
    font_id =0  # XXX, need to find out how best to get this.
    # draw some text
    bgl.glColor4f(0,0,0,0.75)
    blf.blur(font_id,5)
    blf.position(font_id, mouse[0]+10*dpi, mouse[1]-20*dpi, 0)
    blf.size(font_id, 9*dpi, 96)
    blf.draw(font_id, text)

    bgl.glEnd()
    bgl.glColor4f(*color)
    blf.blur(font_id,0)
    blf.draw(font_id, text)
    bgl.glDisable(bgl.GL_BLEND)


def select_bone(self,context,event) :
    ob = context.object
    if ob and ob.type =='ARMATURE' and ob.data.UI :
        shape_data = ob.data.UI
        selected_bones = [b for b in ob.pose.bones if b.bone.select]

        if not event.shift and not event.alt :
            for b in ob.pose.bones :
                b.bone.select= False

        for shape in [s for s in shape_data['shapes'] if not s['shape_type']==["DISPLAY"]]:
            points = [canevas_space(p,self.scale,self.offset) for p in shape['points']]
            bound = [canevas_space(p,self.scale,self.offset) for p in shape['bound']]
            loops = shape['loops']

            ## Colision check
            over = False
            if self.is_border :
                if intersect_rectangles(self.border,bound) :  #start check on over bound_box
                    over = border_over_shape(self.border,points,loops)
            else :
                if point_inside_rectangle(self.end,bound) :
                    over = point_over_shape(self.end,points,loops)

            if over :
                if shape['shape_type'] == 'BONE' :
                    bone = context.object.pose.bones.get(shape['bone'])
                    if  bone:
                        if event.alt :
                            bone.bone.select = False
                        else :
                            bone.bone.select = True
                            context.object.data.bones.active = bone.bone

                if shape['shape_type'] == 'FUNCTION' and event.value== 'RELEASE' and not self.is_border:
                    # restore selection
                    for b in selected_bones :
                        b.bone.select = True

                    function = shape['function']
                    if shape.get('variables') :
                        variables=shape['variables'].to_dict()

                    else :
                        variables={}

                    variables['event']=event

                    print(variables)

                    globals()[function](variables)



def draw_callback_px(self, context):
    ob = context.object
    if ob and ob.type =='ARMATURE' and ob.data.UI and context.area.as_pointer() == self.adress:
        shape_data = ob.data.UI
        rig_layers = [i for i,l in enumerate(ob.data.layers) if l]

        region = context.region
        self.scale = region.height
        self.offset = (-self.scale/2 + region.width/2,0)
        self.outside_point = (region.x-region.width,region.y-region.height)

        #draw BG
        bg_color = shape_data['shapes'][0]['color']
        bg_point = [(0,region.height),(region.width,region.height),(region.width,0),(0,0)]
        bg_color = [c-0.05 for c in bg_color]+[1]
        draw_polyline_2d_loop(bg_point,[[0,1,2,3]],[[0,1,2,3]],bg_color,(0,0,0,1),0)

        show_tooltip = False
        for shape in shape_data['shapes']:

            color = shape['color']
            points = [canevas_space(p,self.scale,self.offset) for p in shape['points']]
            bound = [canevas_space(p,self.scale,self.offset) for p in shape['bound']]
            loops = shape['loops']
            faces = shape['faces']

            select=None
            contour_color = [0,0,0]
            contour_alpha = 1
            width = 0
            shape_color = [c for c in color]
            shape_alpha = 1


            if shape['shape_type'] == 'DISPLAY' and  not faces:
                width = 1

            if shape['shape_type'] != 'DISPLAY' :
                if shape['shape_type'] == 'BONE' :
                    bone = ob.pose.bones.get(shape['bone'])
                    if bone:
                        b_layers = [i for i,l in enumerate(bone.bone.layers) if l]

                        if bone.bone_group :
                            group_color = list(bone.bone_group.colors.normal)
                            contour_color = [c*0.85 for c in group_color]
                            width = 1

                        if bone.bone.select  :
                            shape_color = [c*1.2+0.1 for c in color]
                            if bone.bone_group :
                                contour_color = [0.05,0.95,0.95]

                        if ob.data.bones.active and shape['bone'] == ob.data.bones.active.name :
                            if bone.bone_group :
                                if bone.bone.select  :
                                    shape_color = [c*1.2+0.2 for c in color]
                                    contour_color = [1,1,1]
                                    width = 1.5
                                else :
                                    shape_color = [c*1.2+0.15 for c in color]
                                    contour_color = [0.9,0.9,0.9]
                                    width = 1


                        if bone.bone.hide or not len(set(b_layers).intersection(rig_layers)) :
                            shape_alpha = 0.33
                            contour_alpha = 0.33

                elif shape['shape_type'] == 'FUNCTION' :
                    if shape['function'] == 'boolean' :
                        path = shape['variables']['data_path']

                        if ob.path_resolve(path) :
                            shape_color = [c*1.4+0.08 for c in color]
                    else :
                        shape_color = [color[0],color[1],color[2]]


                ## On mouse over checking
                over = False
                if self.is_border :
                    if intersect_rectangles(self.border,bound) :  #start check on over bound_box
                        over = border_over_shape(self.border,points,loops)
                else :
                    if point_inside_rectangle(self.end,bound) :
                        over = point_over_shape(self.end,points,loops)

                if over :
                    show_tooltip = True
                    tooltip = shape['tooltip']
                    if not self.press:
                        shape_color = [c*1.02+0.05 for c in shape_color]
                        contour_color = [c*1.03+0.05 for c in contour_color]

            shape_color.append(shape_alpha)
            contour_color.append(contour_alpha)
            draw_polyline_2d_loop(points,faces,loops,shape_color,contour_color,width)

        if show_tooltip :
            draw_text(self.end,tooltip,(1,1,1,1))

        if self.is_border :
            draw_border(self.border)
