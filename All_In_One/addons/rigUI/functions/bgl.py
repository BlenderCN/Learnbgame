import bpy
import bgl

from mathutils import Vector
from mathutils.geometry import intersect_line_line_2d
from math import fmod



def draw_polyline_2d_loop(context, points,faces,edges,scale, offset, color):
    region = context.region
    #rv3d = context.space_data.region_3d
    bgl.glColor4f(*color)  #black or white?
    for face in faces :
        bgl.glColor4f(*color)

        bgl.glBegin(bgl.GL_POLYGON)
        for point in face :
            coord = points[point]

            #for coord in points:

            bgl.glVertex2f(scale*coord[0]+offset[0], scale*coord[1] + offset[1])
        bgl.glEnd()

    bgl.glEnd()

    bgl.glLineWidth(1)
    for edge in edges :
        bgl.glBegin(bgl.GL_LINES)

        for point in edge :
            coord = points[point]

            #for coord in points:

            bgl.glVertex2f(scale*coord[0]+offset[0], scale*coord[1] + offset[1])



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


def point_inside_loop(verts, outside_point,mouse, scale, offset):
    nverts= len(verts)

    out = Vector(outside_point)

    pt = Vector(mouse)

    intersections = 0
    for i in range(0,nverts):
        a = scale*Vector(verts[i-1]) + Vector(offset)
        b = scale*Vector(verts[i]) + Vector(offset)
        if intersect_line_line_2d(pt,out,a,b):
            intersections += 1

    inside = False
    if intersections%2 == 1 : #chek if the nb of intersection is odd
        inside = True

    return inside

def point_inside_border(verts,border, scale, offset):

    min_x = min(border[0][0],border[1][0])
    max_x = max(border[0][0],border[1][0])
    min_y = min(border[0][1],border[2][1])
    max_y = max(border[0][1],border[2][1])

    nverts= len(verts)

    inside = False
    for v in verts :
        co = scale*Vector(v) + Vector(offset)
        if min_x<=co[0]<= max_x and min_y<=co[1]<= max_y :
            inside = True
            break

    if not inside :
        for i in range(0,nverts) :
            a = scale*Vector(verts[i-1]) + Vector(offset)
            b = scale*Vector(verts[i]) + Vector(offset)

            for j in range(0,4):
                c = border[j-1]
                d = border[j]
                if intersect_line_line_2d(a,b,c,d):
                    inside = True
                    break

    return inside


def select_bone(self,context,event) :
    if context.object and context.object.type =='ARMATURE' and context.object.data.UI:
        if not event.shift and not event.alt :
            for b in context.selected_pose_bones :
                b.bone.select= False

        button_data = bpy.context.object.data.UI
        region = bpy.context.region
        #rv3d = bpy.context.space_data.region_3d
        width = region.width
        height = region.height

        menu_width = (height)

        #origin of menu is bottom left corner
        menu_loc = (-height/2 + width/2,0)

        border = ((self.start_x,self.start_y),(self.end_x,self.start_y),(self.end_x,self.end_y),(self.start_x,self.end_y))

        mouse = (self.end_x,self.end_y)
        outside_point = (region.x-width,region.y-height)


        for key,value in button_data.items(): #each of those is a loop
            select = False
            if not key.endswith(".display"):
                for point in border : #check for border points if inside the button
                    select = point_inside_loop(value['points'],outside_point,mouse,menu_width, menu_loc)
                    if select :
                        if key.endswith('.operator') and event.value== 'RELEASE':
                            limb = str(eval(value['variables'])[0])
                            way = str(eval(value['variables'])[1])

                            bpy.ops.rigui.snap_ikfk(limb=limb,way=way)

                        break

                if not select :
                    select = point_inside_border(value['points'],border,menu_width, menu_loc)


                if select:

                    bone = bpy.context.object.pose.bones.get(key)
                    if  bone:
                        if event.alt :
                            bone.bone.select = False
                        else :
                            bone.bone.select = True


def draw_callback_px(self, context):
    #if context.space_data.as_pointer() == adress :
    if context.object and context.object.type =='ARMATURE' and context.object.data.UI:
        button_data = context.object.data.UI

        region = context.region
        #rv3d = context.space_data.region_3d
        width = region.width
        height = region.height

        menu_width = (height)
        menu_loc = (-height/2 + width/2,0)
        outside_point = (region.x-width,region.y-height)

        #draw all the buttons
        indexButton= sorted([(value['index'], key) for key,value in button_data.items()])

        border = ((self.start_x,self.start_y),(self.end_x,self.start_y),(self.end_x,self.end_y),(self.start_x,self.end_y))

        mouse = (self.end_x,self.end_y)
        outside_point = (region.x-width,region.y-height)#use for checking collision

        for value in indexButton: #each of those is a loop

            GColor = button_data[value[1]]['color']
            Color = (GColor[0],GColor[1],GColor[2])

            verts = button_data[value[1]]['points']
            faces = button_data[value[1]]['faces']
            edges = button_data[value[1]]['edges']

            if not value[1].endswith('.display') :

                select = point_inside_loop(verts,outside_point,mouse,menu_width, menu_loc)

                bone = bpy.context.object.pose.bones.get(value[1])

                if bone and bone.bone.select == True :
                    color = (0.9,0.9,0.9,1)

                    if select :
                        color = (1,1,1,1)

                else :
                    color = (Color[0],Color[1],Color[2],1)

                    if select:
                        color = (Color[0]*1.2,Color[1]*1.2,Color[2]*1.2,1)


                draw_polyline_2d_loop(context, verts, faces,edges,menu_width, menu_loc, color)
                #color = (1.0,1.0,1.0,1.0) # ADDED

            else :
                color = (Color[0],Color[1],Color[2],1)
                #color = (1,1,1,1)
                draw_polyline_2d_loop(context, verts, faces,edges,menu_width, menu_loc, color)

        if self.border :
            print('toto')
            draw_border(border)
