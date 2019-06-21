import bpy
from bpy.props import *
from . import_thps4 import THPS4ScnToScene, THPS4ColToScene
from . import_thug1 import THUG1ScnToScene
from . import_thug2 import THUG2ScnToScene, THUG2ColToScene
from . import_park import ImportTHUGPrk
from . import_thps2 import THPS2PsxToScene
from . tex import THUGImgToImages
from . qb import THUGImportLevelQB
from . skeleton import THUGImportSkeleton
from . scene_props import *
import bgl
from . constants import *
from . material import *
from . collision import *
from . export_thug1 import *
from . export_thug2 import *
from . export_shared import *
from . import_nodes import *
from . presets import *
from . import script_template
from mathutils import Vector

# PROPERTIES
#############################################
draw_stuff_display_list_id = bgl.glGenLists(1)
draw_stuff_dirty = True
draw_stuff_objects = set()
draw_handle = None

# METHODS
#############################################
@bpy.app.handlers.persistent
def draw_stuff_post_update(scene):
    # print("draw_stuff_post_update")
    global draw_stuff_dirty, draw_stuff_objects
    if draw_stuff_dirty: return

    if not draw_stuff_objects:
        draw_stuff_dirty = True
        return

    # import time
    # print(time.clock())
    scn_objs = { ob.name: ob for ob in scene.objects }
    for ob in draw_stuff_objects:
        ob = scn_objs.get(ob) # scene.objects.get(ob)
        if (not ob) or ob.is_updated or ob.is_updated_data:
            draw_stuff_dirty = True
            return
    # print(time.clock())

#----------------------------------------------------------------------------------
@bpy.app.handlers.persistent
def draw_stuff_pre_load_cleanup(*args):
    # print("draw_stuff_post_update")
    global draw_stuff_dirty, draw_stuff_objects
    draw_stuff_dirty = True
    draw_stuff_objects = set()

#----------------------------------------------------------------------------------
@bpy.app.handlers.persistent
def draw_stuff():
    # print("draw_stuff")
    # FIXME this should use glPushAttrib
    from bgl import glColor3f, glVertex3f, glBegin, glEnd, GL_POLYGON, GL_LINES
    global draw_stuff_dirty, draw_stuff_objects
    ctx = bpy.context
    if not len(ctx.selected_objects) and not ctx.object:
        return
    if not bpy.context.window_manager.thug_show_face_collision_colors:
        return

    VERT_FLAG = FACE_FLAGS["mFD_VERT"]
    WALLRIDABLE_FLAG = FACE_FLAGS["mFD_WALL_RIDABLE"]
    TRIGGER_FLAG = FACE_FLAGS["mFD_TRIGGER"]
    NON_COLLIDABLE_FLAG = FACE_FLAGS["mFD_NON_COLLIDABLE"]

    bgl.glPushAttrib(bgl.GL_ALL_ATTRIB_BITS)
    try:
        _tmp_buf = bgl.Buffer(bgl.GL_FLOAT, 1)
        bgl.glGetFloatv(bgl.GL_POLYGON_OFFSET_FACTOR, _tmp_buf)
        old_offset_factor = _tmp_buf[0]
        bgl.glGetFloatv(bgl.GL_POLYGON_OFFSET_UNITS, _tmp_buf)
        old_offset_units = _tmp_buf[0]
        del _tmp_buf

        objects = set([ob.name for ob in ctx.selected_objects] if ctx.mode == "OBJECT" else [ctx.object.name])
        if draw_stuff_objects != objects:
            draw_stuff_dirty = True
        # print("draw_stuff2")

        if not draw_stuff_dirty:
            bgl.glCallList(draw_stuff_display_list_id)
            bgl.glPolygonOffset(old_offset_factor, old_offset_units)
            bgl.glDisable(bgl.GL_POLYGON_OFFSET_FILL)
            bgl.glDisable(bgl.GL_CULL_FACE)
            return

        bm = None
        bgl.glNewList(draw_stuff_display_list_id, bgl.GL_COMPILE_AND_EXECUTE)
        try:
            bgl.glCullFace(bgl.GL_BACK)
            bgl.glEnable(bgl.GL_CULL_FACE)
            bgl.glEnable(bgl.GL_POLYGON_OFFSET_FILL)
            #bgl.glEnable(bgl.GL_POLYGON_OFFSET_LINE)
            bgl.glPolygonOffset(-2, -2)

            bgl.glEnable(bgl.GL_BLEND)
            bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA);

            prefs = ctx.user_preferences.addons[ADDON_NAME].preferences

            bgl.glLineWidth(prefs.line_width)

            draw_stuff_objects = objects
            bdobs = {ob.name: ob for ob in bpy.data.objects}
            for ob in objects:
                ob = bdobs[ob]
                if not bm: bm = bmesh.new()
                if (ob and
                        ob.type == "CURVE" and
                        ob.data.splines and
                        ob.data.splines[-1].points and
                        ob.thug_path_type == "Rail" and
                        ob.thug_rail_connects_to):
                    connects_to = bdobs[ob.thug_rail_connects_to]
                    if (connects_to and
                            connects_to.type == "CURVE" and
                            connects_to.data.splines and
                            connects_to.data.splines[0].points):
                        glBegin(GL_LINES)
                        bgl.glColor4f(*prefs.rail_end_connection_color)
                        v = ob.matrix_world * ob.data.splines[-1].points[-1].co.to_3d()
                        glVertex3f(v[0], v[1], v[2])
                        v = connects_to.matrix_world * connects_to.data.splines[0].points[0].co.to_3d()
                        glVertex3f(v[0], v[1], v[2])
                        glEnd()

                # Draw previews for area lights - tube/sphere lights and area lights
                if (ob and ob.type == 'LAMP'):
                    if ob.data.thug_light_props.light_type == 'TUBE':
                        if ob.data.thug_light_props.light_end_pos != (0, 0, 0):
                            glBegin(GL_LINES)
                            bgl.glColor4f(1.0, 0.75, 0.25, 1.0)
                            glVertex3f(ob.location[0], ob.location[1], ob.location[2])
                            glVertex3f(ob.location[0] + ob.data.thug_light_props.light_end_pos[0], ob.location[1] + ob.data.thug_light_props.light_end_pos[1], ob.location[2] + ob.data.thug_light_props.light_end_pos[2])
                            glEnd()
                        continue
                    elif ob.data.thug_light_props.light_type == 'SPHERE':
                        continue
                    elif ob.data.thug_light_props.light_type == 'AREA':
                        continue
                    else:
                        continue
                elif (ob and ob.type == 'EMPTY'):
                    if ob.thug_empty_props.empty_type == 'LightVolume' or ob.thug_empty_props.empty_type == 'CubemapProbe':
                        # Draw light volume bbox!
                        bbox, bbox_min, bbox_max, bbox_mid = get_bbox_from_node(ob)
                        
                        # 50% alpha, 2 pixel width line
                        bgl.glEnable(bgl.GL_BLEND)
                        bgl.glColor4f(1.0, 0.0, 0.0, 0.5)
                        bgl.glLineWidth(4)
                        
                        glBegin(bgl.GL_LINE_STRIP)
                        bgl.glVertex3f(*bbox[0])
                        bgl.glVertex3f(*bbox[1])
                        bgl.glVertex3f(*bbox[2])
                        bgl.glVertex3f(*bbox[3])
                        bgl.glVertex3f(*bbox[0])
                        bgl.glVertex3f(*bbox[4])
                        bgl.glVertex3f(*bbox[5])
                        bgl.glVertex3f(*bbox[6])
                        bgl.glVertex3f(*bbox[7])
                        bgl.glVertex3f(*bbox[4])
                        bgl.glEnd()

                        bgl.glBegin(bgl.GL_LINES)
                        bgl.glVertex3f(*bbox[1])
                        bgl.glVertex3f(*bbox[5])
                        bgl.glVertex3f(*bbox[2])
                        bgl.glVertex3f(*bbox[6])
                        bgl.glVertex3f(*bbox[3])
                        bgl.glVertex3f(*bbox[7])
                        glEnd()
                        
                if not ob or ob.type != "MESH":
                    continue

                if ob.mode == "EDIT":
                    bm.free()
                    bm = bmesh.from_edit_mesh(ob.data).copy()
                else:
                    bm.clear()
                    if ob.modifiers:
                        final_mesh = ob.to_mesh(bpy.context.scene, True, "PREVIEW")
                        try:
                            bm.from_mesh(final_mesh)
                        finally:
                            bpy.data.meshes.remove(final_mesh)
                    else:
                        bm.from_mesh(ob.data)

                arl = bm.edges.layers.int.get("thug_autorail")
                if arl:
                    bgl.glColor4f(*prefs.autorail_edge_color)
                    glBegin(GL_LINES)
                    for edge in bm.edges:
                        if edge[arl] == AUTORAIL_NONE:
                            continue

                        for vert in edge.verts:
                            v = ob.matrix_world * vert.co
                            glVertex3f(v[0], v[1], v[2])
                    glEnd()

                cfl = bm.faces.layers.int.get("collision_flags")
                flag_stuff = ((VERT_FLAG, prefs.vert_face_color),
                              (WALLRIDABLE_FLAG, prefs.wallridable_face_color),
                              (TRIGGER_FLAG, prefs.trigger_face_color),
                              (NON_COLLIDABLE_FLAG, prefs.non_collidable_face_color))
                if cfl:
                    bmesh.ops.triangulate(bm, faces=bm.faces)

                    for face in bm.faces:
                        drawn_face = False
                        if prefs.show_bad_face_colors:
                            if (face[cfl] & (VERT_FLAG | WALLRIDABLE_FLAG | NON_COLLIDABLE_FLAG) not in
                                (VERT_FLAG, WALLRIDABLE_FLAG, NON_COLLIDABLE_FLAG, 0)):
                                bgl.glColor4f(*prefs.bad_face_color)
                                glBegin(GL_POLYGON)
                                for vert in face.verts:
                                    v = ob.matrix_world * vert.co
                                    glVertex3f(v[0], v[1], v[2])
                                glEnd()
                                continue

                        for face_flag, face_color in flag_stuff:
                            if face[cfl] & face_flag and (not drawn_face or prefs.mix_face_colors):
                                bgl.glColor4f(*face_color)
                                drawn_face = True

                                glBegin(GL_POLYGON)
                                for vert in face.verts:
                                    v = ob.matrix_world * vert.co
                                    glVertex3f(v[0], v[1], v[2])
                                glEnd()
        finally:
            draw_stuff_dirty = False
            bgl.glEndList()
            if bm: bm.free()
            bgl.glPolygonOffset(old_offset_factor, old_offset_units)
            bgl.glDisable(bgl.GL_POLYGON_OFFSET_FILL)
    finally:
        bgl.glPopAttrib()



#----------------------------------------------------------------------------------
def import_menu_func(self, context):
    self.layout.operator(THUG2ColToScene.bl_idname, text=THUG2ColToScene.bl_label, icon='PLUGIN')
    self.layout.operator(THUG2ScnToScene.bl_idname, text=THUG2ScnToScene.bl_label, icon='PLUGIN')
    self.layout.operator(THUG1ScnToScene.bl_idname, text=THUG1ScnToScene.bl_label, icon='PLUGIN')
    self.layout.operator(THPS4ScnToScene.bl_idname, text=THPS4ScnToScene.bl_label, icon='PLUGIN')
    self.layout.operator(THPS4ColToScene.bl_idname, text=THPS4ColToScene.bl_label, icon='PLUGIN')
    self.layout.operator(THPS2PsxToScene.bl_idname, text=THPS2PsxToScene.bl_label, icon='PLUGIN')
    self.layout.operator(THUGImportLevelQB.bl_idname, text=THUGImportLevelQB.bl_label, icon='PLUGIN')
    self.layout.operator(THUGImportSkeleton.bl_idname, text=THUGImportSkeleton.bl_label, icon='PLUGIN')
    self.layout.operator(ImportTHUGPrk.bl_idname, text=ImportTHUGPrk.bl_label, icon='PLUGIN')
    self.layout.operator(THUGImgToImages.bl_idname, text=THUGImgToImages.bl_label, icon='PLUGIN')
#----------------------------------------------------------------------------------    
def export_menu_func(self, context):
    #self.layout.operator(SceneToTHPS4Files.bl_idname, text="Scene to THPS4 level files", icon='PLUGIN')
    #self.layout.operator(SceneToTHPS4Model.bl_idname, text=SceneToTHPS4Model.bl_label, icon='PLUGIN')
    self.layout.operator(SceneToTHUGFiles.bl_idname, text="Scene to THUG1 level files", icon='PLUGIN')
    self.layout.operator(SceneToTHUGModel.bl_idname, text="Scene to THUG1 model", icon='PLUGIN')
    self.layout.operator(SceneToTHUG2Files.bl_idname, text="Scene to THUG2 level files", icon='PLUGIN')
    self.layout.operator(SceneToTHUG2Model.bl_idname, text="Scene to THUG2 model", icon='PLUGIN')
#----------------------------------------------------------------------------------
def add_menu_func(self, context):
    self.layout.menu(THUGPresetsMenu.bl_idname, text="THUG", icon='PLUGIN')
#----------------------------------------------------------------------------------
def register_menus():
    bpy.types.INFO_MT_file_import.append(import_menu_func)
    bpy.types.INFO_MT_file_export.append(export_menu_func)
    addPresetNodes()
    addPresetMesh()
    bpy.types.INFO_MT_add.append(add_menu_func)
    script_template.init_templates()
#----------------------------------------------------------------------------------
def unregister_menus():
    bpy.types.INFO_MT_file_import.remove(import_menu_func)
    bpy.types.INFO_MT_file_export.remove(export_menu_func)
    bpy.types.INFO_MT_add.remove(add_menu_func)
    clearPresetNodes()
    clearPresetMesh()


