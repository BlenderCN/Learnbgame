import bpy
import bmesh
from mathutils import *
from math import *
from .ui_constants import *
from bgl import *
from bpy.props import BoolProperty

class LinkHelper():
    def __init__(self):
        self.kd = None
        self.options = {}
        self.options['nFrames'] = 0 
        self.options['displaylist'] = -1

    def __del__(self):
        print("Deleted Link Hlper", self)
        del self.kd
        if self.options['displaylist'] != -1:
            glDeleteLists(self.options['displaylist'], 1)

    # create kd tree based scene acceleration structure
    def create_accl_struct(self, obj): #blender object
        bm = bmesh.from_edit_mesh(obj.data)
        self.kd = kdtree.KDTree( len(bm.edges) )

        for i, e in enumerate (bm.edges):
            center = ( e.verts[0].co + e.verts[1].co ) / 2
            self.kd.insert(center, i)

        self.kd.balance()

    """
    obj: blender object to draw around the link helper
    region_3d: region of the currect scene
    """
    def draw(self, obj, region_3d): 
        glPushMatrix()
        rot = obj.rotation_axis_angle
        glRotatef(degrees(rot[0]), rot[1], rot[2], rot[3])
        glScalef(*obj.scale)
        glTranslatef(*obj.location)

#        """ try to speed up by caching the draw into displaylist
        if self.options['nFrames'] & 1 == 0:
            if self.options['displaylist'] != -1:
                glDeleteLists(self.options['displaylist'], 1)

            self.options['displaylist'] = glGenLists(1)
            glNewList(self.options['displaylist'], GL_COMPILE)
            self.draw_local_immediate(obj, region_3d)
            glEndList()
            glCallList(self.options['displaylist'])
        else:
            glCallList(self.options['displaylist'])
#        """
        
        glPopMatrix()

        self.options['nFrames'] += 1

    def draw_local_immediate(self, obj, region_3d): 
        if self.kd is None:
            self.create_accl_struct(obj) 

        view_mat = region_3d.view_matrix
        cam_pos = view_mat.inverted_safe().translation

        # transform cam pos in object space for spatial acceleration structure search 
        cam_pos = obj.matrix_world.inverted() * cam_pos
#        print("viewing from: ", cam_pos) 
        for (co, index, dist) in self.kd.find_range(cam_pos, 600):
            bm = bmesh.from_edit_mesh(obj.data)
            e = bm.edges[index]
            vecTo = e.verts[0].co # 0 is the target 
            vecFrom = e.verts[1].co   # 1 is the source
            
            center = co
            
            v = vecTo - vecFrom
            v.normalize()
            
            # if vector is straight pointing up only on z axis ignore it
            if abs(v.x) < 0.0001 and abs(v.y) < 0.0001:
                continue
            
            vPerp1 = Vector((-v.y, v.x, 0.0))
            vPerp2 = Vector((v.y, -v.x, 0.0))
            
            v1 = (vPerp1 - v).normalized()
            v2 = (vPerp2 - v).normalized()
            
            arrow_vertices = (
                (-0.5,-1.0, 0.0 ),
                ( 0.0, 1.0, 0.0 ),
                ( 0.0, 0.0, 0.0 ),
                ( 0.5,-1.0, 0.0 ),
            )
            
            line_vertices = (
                (-0.5, 0.5, 0.0 ) ,     
                (-0.5, -0.5, 0.0 ),
                ( 0.5, -0.5, 0.0 ),
                ( 0.5, 0.5, 0.0 ) ,
            )
            
            SCALE = 1.0
 
            #TODO: Perform by matrix instead
            hAngle = 0
            try:
                hAngle = v.xy.angle_signed(Vector((0,1)))
            except ValueError:
                pass
            # rotate towards x = 0, to find out the signed angle 
            v.rotate(Euler((0.0,0.0,-hAngle)))
            
            vAngle = radians(90)
            try:
                vAngle = v.yz.angle_signed(v.yx)
            except ValueError:
                if v.yz.length == 0.00:
                    continue
                vAngle = v.yz.angle_signed(Vector((1,0)))
                pass
                
            eulerRot = Euler((vAngle, 0.0, hAngle))
            mat = eulerRot.to_matrix().to_4x4()
            mat.translation = center
            
            if dist < 130:
                glColor3f(0.0,0.0,0.0)
                glBegin(GL_TRIANGLE_STRIP)
                for i in arrow_vertices:
                    vert = Vector(i)
                    vert *= SCALE
                    vert = mat * vert
                    glVertex3f(*vert)      
                glEnd()

            lane_width = e[bm.edges.layers.float[EDGE_WIDTH]]
            SCALE = 0.5
            # Lane Information
            glColor3f(0.6,0.6,0.6)
            for j in range(e[bm.edges.layers.int[EDGE_NUMLEFTLANES]]):
                glBegin(GL_LINES)
                for i in line_vertices:
                    vert = Vector(i)
                    vert = Vector((vert.x, vert.y  * (vecTo - vecFrom).length, vert.z)) # scale
                    vert.x -= 0.5
                    vert.x += -1 * (j + 1) - lane_width/2 #left
                    vert = mat * vert
                    glVertex3f(*vert)      
                glEnd()
                
                if dist > 120: 
                    continue

                glBegin(GL_TRIANGLE_STRIP)
                for i in arrow_vertices:
                    vert = Vector(i)
                    vert *= SCALE
                    vert.x += 0.5
                    vert.rotate(Euler((0.0, 0.0, radians(180.0))))
                    vert.x += -1 * (j + 1) - lane_width/2 #left
                    vert = mat * vert
                    glVertex3f(*vert)      
                glEnd()
            
            for j in range(e[bm.edges.layers.int[EDGE_NUMRIGHTLANES]]):
                glBegin(GL_LINES)
                for i in line_vertices:
                    vert = Vector(i)
                    vert = Vector((vert.x, vert.y  * (vecTo - vecFrom).length, vert.z)) # scale
                    vert.x += 0.5
                    vert.x += 1 * (j + 1) + lane_width/2 #left
                    vert = mat * vert
                    glVertex3f(*vert)      
                glEnd()
                
                if dist > 120: 
                    continue

                glBegin(GL_TRIANGLE_STRIP)
                for i in arrow_vertices:
                    vert = Vector(i)
                    vert *= SCALE
                    vert.x += 0.5
                    vert.x += 1 * (j + 1) + lane_width/2 #left
                    vert = mat * vert
                    glVertex3f(*vert)      
                glEnd()

state = {}
state["frame_cb_hnd"] = -1
state["link_helper"] = None

def cb_frame_callback():
    context = bpy.context
    ob = context.edit_object
    if ob is None:
        return

    # 50% alpha, 2 pixel width line
    #glEnable(GL_BLEND)
    glColor4f(1.0, 1.0, 1.0, 0.5)
    #glLineWidth(2)
        
    state["link_helper"].draw(ob, context.space_data.region_3d) 

    glLineWidth(1)
    glDisable(GL_BLEND)
    glColor4f(0.0, 0.0, 0.0, 1.0)

def cb_scene_callback(context):
    edit_obj = bpy.context.edit_object
    if edit_obj is not None and edit_obj.is_updated_data is True:
        print("Edited")
        state["link_helper"].create_accl_struct(edit_obj)

def setup():
    def boolDisplayLaneCallback(self, context):
        if (self.boolDisplayLane):
            if cb_scene_callback not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(cb_scene_callback)
                state["frame_cb_hnd"] = bpy.types.SpaceView3D.draw_handler_add(cb_frame_callback, (), 'WINDOW', 'POST_VIEW')
        else:
            if cb_scene_callback in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.remove(cb_scene_callback)
                bpy.types.SpaceView3D.draw_handler_remove(state["frame_cb_hnd"], 'WINDOW')

    
    bpy.types.Scene.boolDisplayLane = BoolProperty(name="Enable or Disable", description="Should Display Lane Helper?", default=False, update=boolDisplayLaneCallback) 
    state["link_helper"] = LinkHelper()

def cleanup():
    if cb_scene_callback in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(cb_scene_callback)
        bpy.types.SpaceView3D.draw_handler_remove(state["frame_cb_hnd"] , 'WINDOW')

    del bpy.types.Scene.boolDisplayLane
    del state["link_helper"]
