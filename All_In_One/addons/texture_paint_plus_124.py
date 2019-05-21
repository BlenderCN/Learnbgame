bl_info = {
    'name': 'Texture Paint plus',
    'author': 'Bart Crouch',
    'version': (1, 24),
    'blender': (2, 6, 1),
    'api': 42734,
    'location': 'View3D > Texture Paint mode',
    'warning': '',
    'description': 'Several improvements for Texture Paint mode',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Material'}


import bgl
import blf
import bpy
import mathutils
import os
import time
from bpy_extras.io_utils import ImportHelper


##########################################
#                                        #
# Functions                              #
#                                        #
##########################################

# check if any of the images has to be resized
def consolidate_check_resize(image_map):
    resized = False
    for [image, [x_min, y_min, x_max, y_max]] in image_map:
        width = x_max - x_min
        height = y_max - y_min
        if width != image.size[0] or height != image.size[1]:
            resized = True
            break
        
    return(resized)


# create a new image that contains all other images
def consolidate_copy_images(width, height, alpha, image_map, filename, fileformat, restrict_name):
    # get image name
    old_format = bpy.context.scene.render.image_settings.file_format
    bpy.context.scene.render.image_settings.file_format = fileformat
    extension = bpy.context.scene.render.file_extension
    bpy.context.scene.render.image_settings.file_format = old_format
    if len(extension) > len(filename) and filename[-len(extension):].lower() == extension.lower():
        filename = filename[:-len(extension)]
    if restrict_name != "consolidate":
        filename += "_" + restrict_name
    
    width = int(width)
    height = int(height)
    composite_image = bpy.data.images.new(filename, width, height, alpha=alpha)
    composite_image.filepath_raw = filename + extension
    composite_image.file_format = fileformat
    
    composite_buffer = ImageBuffer(composite_image)
    for [image, [x_offset, y_offset, x_max, y_max]] in image_map:
        buffer = ImageBuffer(image)
        for x in range(image.size[0]):
            for y in range(image.size[1]):
                composite_buffer.set_pixel(x+x_offset, y+y_offset, buffer.get_pixel(x, y))
    composite_buffer.update()
    
    # save and reload
    composite_image.save()
    bpy.data.images.remove(composite_image)
    composite_image = bpy.data.images.load(filename + extension)
    
    return(composite_image)


# retrieve list of images and associated data
def consolidate_get_images(meshes, restrict_values, all_ts):
    images = []
    textures = []
    texture_slots = []
    uv_layers = []
    
    def is_within_restriction(texture_slot):
        if not restrict_values:
            return True
        for value in restrict_values:
            if getattr(texture_slot, value, False):
                return True
        return False
    
    for mesh in meshes:
        # scan texture slots
        ts_found = False
        for mat in mesh.materials:
            if not mat:
                continue
            for ts in [ts for ts in mat.texture_slots if ts and ts.texture.type=='IMAGE']:
                if ts.texture_coords == 'UV':
                    ts_found = True
                    if not is_within_restriction(ts):
                        continue
                    if ts in all_ts:
                        # texture slot already done in different consolidated image
                        continue
                    else:
                        texture_slots.append(ts)
                    image = ts.texture.image
                    if image not in images:
                        images.append(image)
                    if ts.texture not in textures:
                        textures.append(ts.texture)
                    uv_layer = ts.uv_layer
                    if not uv_layer:
                        uv_layer = mesh.uv_textures.active
                    else:
                        uv_layer = mesh.uv_textures[uv_layer]
                    uv_layers.append([mesh, image, mat, ts, uv_layer])
        if not ts_found:
            # scan game property assignments
            # not possible anymore since these settings have been moved
            pass
#            for tex in mesh.uv_textures:
#                for face in tex.data:
#                    if face.use_image:
#                        if face.image not in images:
#                            images.append(face.image)
#                            uv_layers.append([mesh, face.image, False, False, tex])
                    
    return(images, textures, texture_slots, ts_found, uv_layers)


# list of meshes for Consolidate Images operator
def consolidate_get_input(input):
    if input == 'active':
        meshes = []
        ob = bpy.context.active_object
        if ob and ob.type == 'MESH':
            mesh = ob.data
            if len(mesh.uv_textures) > 0:
                meshes.append(bpy.context.active_object.data)
    else: # input == 'selected'
        meshes = [ob.data for ob in bpy.context.selected_objects if ob.type=='MESH' and len(ob.data.uv_textures)>0]
        
    return(meshes)


# create a new image that contains all other images
def consolidate_new_image(width, height, alpha, image_map, filename, fileformat, restrict_name):
    # create temporary scene
    temp_scene = bpy.data.scenes.new("temp_scene")
    temp_world = bpy.data.worlds.new("temp_world")
    temp_scene.world = temp_world
    
    # setup the camera
    cam = bpy.data.cameras.new("temp_cam_ob")
    cam.type = 'ORTHO'
    cam.ortho_scale = 1.0
    obj_cam = bpy.data.objects.new("temp_cam", cam)
    obj_cam.location = [0.5, 0.5, 1.0]
    if width < height:
        obj_cam.location[0] = (width/height) / 2
    elif height < width:
        obj_cam.location[1] = (height/width) / 2
    temp_scene.objects.link(obj_cam)
    temp_scene.camera = obj_cam
    obj_cam.layers[0] = True
        
    # render settings
    temp_scene.render.use_raytrace = False
    temp_scene.render.alpha_mode = 'STRAIGHT'
    if alpha:
        temp_scene.render.image_settings.color_mode = 'RGBA'
    else:
        temp_scene.render.image_settings.color_mode = 'RGB'
    temp_scene.render.resolution_x = width
    temp_scene.render.resolution_y = height
    temp_scene.render.resolution_percentage = 100
    temp_scene.render.pixel_aspect_x = 1.0
    temp_scene.render.pixel_aspect_y = 1.0
    temp_scene.render.image_settings.file_format = fileformat
    extension = temp_scene.render.file_extension
    if len(extension) > len(filename) and filename[-len(extension):].lower() == extension.lower():
        filename = filename[:-len(extension)]
    if restrict_name != "consolidate":
        filename += "_" + restrict_name
    temp_scene.render.filepath = filename
    temp_scene.render.antialiasing_samples = '16'
    temp_scene.render.pixel_filter_type = 'MITCHELL'
    temp_scene.render.use_file_extension = True
    temp_scene.render.use_overwrite = True
	
	# materials
    total_object = [0, 0]
    for [img, [x0, y0, x1, y1]] in image_map:
        if x0 > total_object[0]:
            total_object[0] = x0
        if y0 > total_object[1]:
            total_object[1] = y0
        if x1 > total_object[0]:
            total_object[0] = x1
        if y1 > total_object[1]:
            total_object[1] = y1
    xtotal, ytotal = total_object
    
    temp_materials = [[bpy.data.materials.new("temp_mat"), x0, y0, x1, y1] for [img, [x0, y0, x1, y1]] in image_map]
    temp_textures = [bpy.data.textures.new("temp_tex", 'IMAGE') for i in range(len(image_map))]
    for i, [temp_mat, x0, y0, x1, y1] in enumerate(temp_materials):
        temp_mat.use_shadeless = True
        temp_mat.use_face_texture = True
        temp_mat.use_face_texture_alpha = True
        temp_mat.use_transparency = True
        temp_mat.transparency_method = 'Z_TRANSPARENCY'
        temp_mat.alpha = 1.0
        temp_mat.texture_slots.add()
        temp_mat.texture_slots[0].texture = temp_textures[i]
        temp_mat.texture_slots[0].texture.image = image_map[i][0]
        # texture mapping
        xlength = x1 - x0
        xzoom = xtotal/(xlength)
        xoriginoffset = 0.5 - (0.5 / xzoom)
        xtargetoffset = x0 / xtotal
        xoffset = (xtargetoffset - xoriginoffset) * -xzoom
        ylength = y1 - y0
        yzoom = ytotal/(ylength)
        yoriginoffset = 0.5 - (0.5 / yzoom)
        ytargetoffset = y0 / ytotal
        yoffset = (ytargetoffset - yoriginoffset) * -yzoom
        temp_mat.texture_slots[0].offset = [xoffset, yoffset, 0]
        temp_mat.texture_slots[0].scale = [xzoom, yzoom, 1]
    
    # mesh
    temp_mesh = bpy.data.meshes.new("temp_mesh")
    for [temp_mat, x0, y0, x1, y1] in temp_materials:
        temp_mesh.materials.append(temp_mat)
    
    temp_obj = bpy.data.objects.new("temp_object", temp_mesh)
    temp_scene.objects.link(temp_obj)
    temp_obj.layers[0] = True
    
    new_vertices = []
    new_faces = []
    i = 0
    for [img, [x0, y0, x1, y1]] in image_map:
        new_vertices.extend([x0, y0, 0, x1, y0, 0, x1, y1, 0, x0, y1, 0])
        new_faces.extend([i, i+1, i+2, i+3])
        i += 4
    temp_mesh.vertices.add(i)
    temp_mesh.faces.add(i//4)
    temp_mesh.vertices.foreach_set('co', new_vertices)
    temp_mesh.faces.foreach_set('vertices_raw', new_faces)
    temp_mesh.faces.foreach_set("material_index", range(i//4))
    temp_mesh.update(calc_edges=True)
    max_size = max(width, height)
    temp_obj.scale = [1/max_size, 1/max_size, 1]
    
    # render composite image
    data_context = {"blend_data": bpy.context.blend_data, "scene": temp_scene}
    bpy.ops.render.render(data_context, write_still=True)
    
    # cleaning
    bpy.data.scenes.remove(temp_scene)
    bpy.data.objects.remove(obj_cam)
    bpy.data.cameras.remove(cam)
    bpy.data.objects.remove(temp_obj)
    bpy.data.meshes.remove(temp_mesh)
    for [temp_mat, x0, y0, x1, y1] in temp_materials:
        bpy.data.materials.remove(temp_mat)
    for temp_tex in temp_textures:
        bpy.data.textures.remove(temp_tex)
    
    # load composite image into blender's database
    composite_image = bpy.data.images.load(filename + extension)
    
    return(composite_image)


# bin pack images
def consolidate_pack_images(images, image_width, image_height, auto_size):
    image_sizes = [[image.size[0]*image.size[1], image.size[0], image.size[1], image.name, image] for image in images]
    image_sizes.sort()
    total_area = sum([size[0] for size in image_sizes])
    container_zoom = 1.5
    zoom_delta = .1
    fit = 0 # 0 = no fit tried yet, 1 = fit found, 2 = container too small
    searching = True
    image_map = []
    iteration = 0
    
    while searching:
        iteration += 1
        if iteration % 5 == 0:
            # increase the container increase, to speed things up
            zoom_delta *= 2
        temp_map = []
        success = True
        image_area = image_width * image_height
        image_zoom = total_area / image_area
        container_width = image_width * image_zoom * container_zoom
        container_height = image_height * image_zoom * container_zoom
        tree = PackTree([container_width, container_height])
        for area, width, height, name, image in image_sizes:
            uv = tree.insert([width, height])
            if not uv:
                success = False
                if fit == 1:
                    searching = False
                    break
                fit = 2
                container_zoom += zoom_delta
                break
            temp_map.append([image, uv.area])
        if success:
            fit = 1
            image_map = temp_map
            container_zoom -= zoom_delta
    
    width = 0
    height = 0
    for image, [x_min, y_min, x_max, y_max] in image_map:
        if x_max > width:
            width = x_max
        if y_max > height:
            height = y_max
    
    zoom = max([(width / image_width), (height / image_height)])
    if auto_size:
        image_width *= zoom
        image_height *= zoom
    else:
        image_map = [[image, [x_min/zoom, y_min/zoom, x_max/zoom, y_max/zoom]] for image, [x_min, y_min, x_max, y_max] in image_map]
    
    return(image_map, image_width, image_height)


def consolidate_update_textures(textures, uv_layers, image_map, composite_image, restrict_name):
    # create remapped UV layers
    total_width, total_height = composite_image.size
    for [mesh, image, mat, ts, uv_layer] in uv_layers:
        layer_names = [layer.name for layer in mesh.uv_textures]
        new_name = uv_layer.name[:min(8, len(uv_layer.name))]
        if restrict_name == "consolidate":
            new_name += "_remap"
        else:
            new_name += "_" + restrict_name
        if new_name in layer_names:
            # problem, as we need a unique name
            unique = False
            n = 1
            while not unique:
                if new_name + "." + str(n).rjust(3, "0") not in layer_names:
                    new_name += "." + str(n).rjust(3, "0")
                    unique = True
                    break
                else:
                    n += 1
                    if n > 999:
                        # couldn't find unique name
                        unique = True
                        break
        new_layer = mesh.uv_textures.new(new_name)
        if not new_layer:
            continue
        for [old_image, coords] in image_map:
            if image == old_image:
                break
        offset_x, offset_y, x_max, y_max = coords
        new_width = x_max - offset_x
        new_height = y_max - offset_y
        offset_x /= total_width
        offset_y /= total_height
        zoom_x = new_width / total_width
        zoom_y = new_height / total_height
        for i, mface in enumerate(uv_layer.data):
            # get texture face data
            pin_uv = mface.pin_uv
            select_uv = mface.select_uv
            uv_raw = [uv_co for uv_co in mface.uv_raw]
            # remap UVs
            for index in range(0, 8, 2):
                uv_raw[index] = (uv_raw[index] * zoom_x) + offset_x
            for index in range(1, 8, 2):
                uv_raw[index] = (uv_raw[index] * zoom_y) + offset_y
            # set texture face data
            new_layer.data[i].uv_raw = uv_raw
            new_layer.data[i].image = composite_image
            new_layer.data[i].pin_uv = pin_uv
            new_layer.data[i].select_uv = select_uv
        if ts:
            ts.uv_layer = new_layer.name
            #ts.scale[0] /= (image.size[0] / composite_image.size[0])
            #ts.scale[1] /= (image.size[1] / composite_image.size[1])
        else:
            mesh.uv_textures.active_index = len(mesh.uv_textures) - 1
    # replace images with composite_image
    for tex in textures:
        tex.image = composite_image


# draw in 3d-view
def draw_callback(self, context):
    r, g, b = context.tool_settings.image_paint.brush.cursor_color_add
    x0, y0, x1, y1 = context.window_manager["straight_line"]
    
    # draw straight line
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(r, g, b, 1.0)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    bgl.glVertex2i(x0, y0)
    bgl.glVertex2i(x1, y1)
    bgl.glEnd()
    # restore opengl defaults
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


# return a list of all images that are being displayed in an editor
def get_images_in_editors(context):
    images = []
    for area in context.screen.areas:
        if area.type != 'IMAGE_EDITOR':
            continue
        for space in area.spaces:
            if space.type != 'IMAGE_EDITOR':
                continue
            if space.image:
                images.append(space.image)
                area.tag_redraw()
    
    return(images)


# calculate for 3d-view
def sync_calc_callback(self, context, area, region):
    mid_x = region.width/2.0
    mid_y = region.height/2.0
    width = region.width
    height = region.height
    
    region_3d = False
    for space in area.spaces:
        if space.type == 'VIEW_3D':
            region_3d = space.region_3d
    if not region_3d:
        return
    
    view_mat = region_3d.perspective_matrix
    ob_mat = context.active_object.matrix_world
    total_mat = view_mat * ob_mat
    mesh = context.active_object.data
    
    def transform_loc(loc):
        vec = total_mat * loc
        vec = mathutils.Vector([vec[0]/vec[3], vec[1]/vec[3], vec[2]/vec[3]])
        x = int(mid_x + vec[0]*width/2.0)
        y = int(mid_y + vec[1]*height/2.0)
        
        return([x, y])
    
    # vertices
    locs = [mesh.vertices[v].co.to_4d() for v in self.overlay_vertices]
    self.position_vertices = []
    for loc in locs:
        self.position_vertices.append(transform_loc(loc))
    
    # edges
    locs = [[mesh.vertices[mesh.edges[edge].vertices[0]].co.to_4d(), 
        mesh.vertices[mesh.edges[edge].vertices[1]].co.to_4d()] \
        for edge in self.overlay_edges]
    self.position_edges = []
    for v1, v2 in locs:
        self.position_edges.append(transform_loc(v1))
        self.position_edges.append(transform_loc(v2))
    
    # faces
    locs = [[mesh.vertices[mesh.faces[face].vertices[0]].co.to_4d(),
        mesh.vertices[mesh.faces[face].vertices[1]].co.to_4d(),
        mesh.vertices[mesh.faces[face].vertices[2]].co.to_4d(),
        mesh.vertices[mesh.faces[face].vertices[3]].co.to_4d(),] \
        for face in self.overlay_faces]
    self.position_faces = []
    for v1, v2, v3, v4 in locs:
        self.position_faces.append(transform_loc(v1))
        self.position_faces.append(transform_loc(v2))
        self.position_faces.append(transform_loc(v3))
        self.position_faces.append(transform_loc(v4))
    

# draw in 3d-view
def sync_draw_callback(self, context):
    # polling
    if context.mode != "EDIT_MESH":
        return
    
    # draw vertices
    bgl.glColor4f(1.0, 0.0, 0.0, 1.0)  
    bgl.glPointSize(4)
    bgl.glBegin(bgl.GL_POINTS)
    for x, y in self.position_vertices:
        bgl.glVertex2i(x, y)
    bgl.glEnd()
    
    # draw edges
    bgl.glColor4f(1.0, 0.0, 0.0, 1.0)
    bgl.glLineWidth(1.5)
    bgl.glBegin(bgl.GL_LINES)
    for x, y in self.position_edges:
        bgl.glVertex2i(x, y)
    bgl.glEnd()
    bgl.glLineWidth(1)
    
    # draw faces
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 0.0, 0.0, 0.3)
    bgl.glBegin(bgl.GL_QUADS)
    for x, y in self.position_faces:
        bgl.glVertex2i(x, y)
    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)


# draw in image-editor
def sync_draw_callback2(self, context):
    # polling
    if context.mode != "EDIT_MESH":
        return
    
    # draw vertices
    bgl.glColor4f(1.0, 0.0, 0.0, 1.0)  
    bgl.glPointSize(6)
    bgl.glBegin(bgl.GL_POINTS)
    for x, y in self.position2_vertices:
        bgl.glVertex2f(x, y)
    bgl.glEnd()


# draw paint tool and blendmode in 3d-view
def toolmode_draw_callback(self, context):
    # polling
    if context.mode != 'PAINT_TEXTURE':
        return
    
    # draw
    if context.region:
        main_y = context.region.height - 32
    else:
        return
    blend_dic = {"MIX": "Mix",
        "ADD": "Add",
        "SUB": "Subtract",
        "MUL": "Multiply",
        "LIGHTEN": "Lighten",
        "DARKEN": "Darken",
        "ERASE_ALPHA": "Erase Alpha",
        "ADD_ALPHA": "Add Alpha"}
    brush = context.tool_settings.image_paint.brush
    text = brush.name + " - " + blend_dic[brush.blend]
    
    # text in top-left corner
    bgl.glColor3f(0.6, 0.6, 0.6)
    blf.position(0, 21, main_y, 0)
    blf.draw(0, text)
    
    # text above brush
    dt = time.time() - context.window_manager["tpp_toolmode_time"]
    if dt < 1:
        if "tpp_toolmode_brushloc" not in context.window_manager:
            return
        brush_x, brush_y = context.window_manager["tpp_toolmode_brushloc"]
        brush_x -= blf.dimensions(0, text)[0] / 2
        bgl.glColor4f(0.6, 0.6, 0.6, min(1.0, (1.0 - dt)*2))
        blf.position(0, brush_x, brush_y, 0)
        blf.draw(0, text)


# add ID-properties to window-manager
def init_props():
    wm = bpy.context.window_manager
    wm["tpp_automergeuv"] = 0


# remove ID-properties from window-manager
def remove_props():
    wm = bpy.context.window_manager
    del wm["tpp_automergeuv"]
    if "tpp_toolmode_time" in wm:
        del wm["tpp_toolmode_time"]
    if "tpp_toolmode_brushloc" in wm:
        del wm["tpp_toolmode_brusloc"]


##########################################
#                                        #
# Classes                                #
#                                        #
##########################################

class ImageBuffer:
    # based on script by Domino from BlenderArtists
    # licensed GPL v2 or later
    def __init__(self, image):
        self.image = image
        self.x, self.y = self.image.size
        self.buffer = list(self.image.pixels)

    def update(self):
        self.image.pixels = self.buffer

    def _index(self, x, y):
        if x < 0 or y < 0 or x >= self.x or y >= self.y:
            return None
        return (x + y * self.x) * 4

    def set_pixel(self, x, y, colour):
        index = self._index(x, y)
        if index is not None:
            index = int(index)
            self.buffer[index:index + 4] = colour

    def get_pixel(self, x, y):
        index = self._index(x, y)
        if index is not None:
            index = int(index)
            return self.buffer[index:index + 4]
        else:
            return None


# 2d bin packing
class PackTree(object):
    # based on python recipe by S W on ActiveState
    # PSF license, 16 oct 2005. (GPL compatible)
    def __init__(self, area):
        if len(area) == 2:
            area = (0,0,area[0],area[1])
        self.area = area
    
    def get_width(self):
        return self.area[2] - self.area[0]
    width = property(fget=get_width)
    
    def get_height(self):
        return self.area[3] - self.area[1]
    height = property(fget=get_height)
    
    def insert(self, area):
        if hasattr(self, 'child'):
            a = self.child[0].insert(area)
            if a is None:
                return self.child[1].insert(area)
            else:
                return a
        
        area = PackTree(area)
        if area.width <= self.width and area.height <= self.height:
            self.child = [None,None]
            self.child[0] = PackTree((self.area[0]+area.width, self.area[1], self.area[2], self.area[1] + area.height))
            self.child[1] = PackTree((self.area[0], self.area[1]+area.height, self.area[2], self.area[3]))
            return PackTree((self.area[0], self.area[1], self.area[0]+area.width, self.area[1]+area.height))


##########################################
#                                        #
# Operators                              #
#                                        #
##########################################

class AddDefaultImage(bpy.types.Operator):
    '''Create and assign a new default image to the object'''
    bl_idname = "object.add_default_image"
    bl_label = "Add default image"
    
    @classmethod
    def poll(cls, context):
        return(context.active_object and context.active_object.type=='MESH')
    
    def invoke(self, context, event):
        ob = context.active_object
        mat = bpy.data.materials.new("default")
        tex = bpy.data.textures.new("default", 'IMAGE')
        img = bpy.data.images.new("default", 1024, 1024, alpha=True)
        ts = mat.texture_slots.add()
        tex.image = img
        ts.texture = tex
        ob.data.materials.append(mat)
        
        return {'FINISHED'}


class AutoMergeUV(bpy.types.Operator):
    '''Have UV Merge enabled by default for merge actions'''
    bl_idname = "paint.auto_merge_uv"
    bl_label = "AutoMerge UV"
    
    def invoke(self, context, event):
        wm = context.window_manager
        if "tpp_automergeuv" not in wm:
            init_props()
        wm["tpp_automergeuv"] = 1 - wm["tpp_automergeuv"]
        
        km = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
        for kmi in km.keymap_items:
            if kmi.idname == "mesh.merge":
                kmi.properties.uvs = wm["tpp_automergeuv"]
        
        return {'FINISHED'}


class BrushPopup(bpy.types.Operator):
    bl_idname = "paint.brush_popup"
    bl_label = "Brush settings"
    bl_options = {'REGISTER'}
    
    def draw(self, context):
        brush = context.tool_settings.image_paint.brush
        
        # colour buttons
        col = self.layout.column()
        split = col.split(percentage = 0.15)
        split.prop(brush, "color", text="")
        split.scale_y = 1e-6
        col.template_color_wheel(brush, "color", value_slider=True)
        
        # imagepaint tool buttons
        group = col.column(align=True)
        row = group.row(align=True)
        row.prop(brush, "image_tool", expand=True, icon_only=True, emboss=True)
        
        # curve type buttons
        row = group.split(align=True)
        row.operator("brush.curve_preset", icon="SMOOTHCURVE", text="").shape = 'SMOOTH'
        row.operator("brush.curve_preset", icon="SPHERECURVE", text="").shape = 'ROUND'
        row.operator("brush.curve_preset", icon="ROOTCURVE", text="").shape = 'ROOT'
        row.operator("brush.curve_preset", icon="SHARPCURVE", text="").shape = 'SHARP'
        row.operator("brush.curve_preset", icon="LINCURVE", text="").shape = 'LINE'
        row.operator("brush.curve_preset", icon="NOCURVE", text="").shape = 'MAX'
        
        # radius buttons
        col = col.column(align=True)
        row = col.row(align=True)
        row.prop(brush, "size", text="Radius", slider=True)
        row.prop(brush, "use_pressure_size", toggle=True, text="")
        # strength buttons
        row = col.row(align=True)
        row.prop(brush, "strength", text="Strength", slider=True)
        row.prop(brush, "use_pressure_strength", toggle=True, text="")
        # jitter buttons
        row = col.row(align=True)
        row.prop(brush, "jitter", slider=True)
        row.prop(brush, "use_pressure_jitter", toggle=True, text="")
        # spacing buttons
        row = col.row(align=True)
        row.prop(brush, "spacing", slider=True)
        row.prop(brush, "use_space", toggle=True, text="", icon="FILE_TICK")
        
        # alpha and blending mode buttons
        split = col.split(percentage=0.25)
        row = split.row()
        row.active = (brush.blend not in {'ERASE_ALPHA', 'ADD_ALPHA'})
        row.prop(brush, "use_alpha", text="A")
        split.prop(brush, "blend", text="")
    
    def execute(self, context):
        if context.space_data.type == 'IMAGE_EDITOR':
            context.space_data.use_image_paint = True
        return context.window_manager.invoke_popup(self, width=125)


class ChangeSelection(bpy.types.Operator):
    '''Select more or less vertices/edges/faces, connected to the original selection'''
    bl_idname = "paint.change_selection"
    bl_label = "Change selection"
    
    mode = bpy.props.EnumProperty(name="Mode",
        items = (("more", "More", "Select more vertices/edges/faces"),
            ("less", "Less", "Select less vertices/edges/faces")),
        description = "Choose whether the selection should be increased or decreased",
        default = 'more')
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()
    
    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='EDIT')
        if self.mode == 'more':
            bpy.ops.mesh.select_more()
        else: #self.mode == 'less'
            bpy.ops.mesh.select_less()
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        
        return {'FINISHED'}


class ConsolidateImages(bpy.types.Operator):
    '''Pack all texture images into one image'''
    bl_idname = "image.consolidate"
    bl_label = "Consolidate images"
    
    remap = bpy.props.BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return(context.active_object or context.selected_objects)

    def invoke(self, context, event):
        props = context.window_manager.tpp
        meshes = consolidate_get_input(props.consolidate_input)
        if not meshes:
            self.report({'ERROR'}, "No UV textures found")
            return {'CANCELLED'}
        
        if props.consolidate_split:
            restrict = {"diffuse":["use_map_diffuse", "use_map_color_diffuse", "use_map_alpha", "use_map_translucency"],
                "shading":["use_map_ambient", "use_map_emit", "use_map_mirror", "use_map_raymir"],
                "specular":["use_map_specular", "use_map_color_spec", "use_map_hardness"],
                "geometry":["use_map_normal", "use_map_warp", "use_map_displacement"]}
        else:
            restrict = {"consolidate":False}
        
        all_ts = []
        for restrict_name, restrict_values in restrict.items():
            if context.area:
                context.area.header_text_set("Collecting images")
            images, textures, texture_slots, ts_found, uv_layers = consolidate_get_images(meshes, restrict_values, all_ts)
            if not images:
                continue
            all_ts += texture_slots
            if not ts_found:
                restrict_name = "consolidate"
                restrict_values = False
            if context.area:
                context.area.header_text_set("Bin packing images")
            image_map, width, height = consolidate_pack_images(images, props.consolidate_width, props.consolidate_height, props.consolidate_auto_size)
            if context.area:
                context.area.header_text_set("Rendering composite image")
            resized = consolidate_check_resize(image_map)
            if not resized:
                # direct copy from source
                composite_image = consolidate_copy_images(width, height, props.consolidate_alpha, image_map, props.consolidate_filename, props.consolidate_fileformat, restrict_name)
            else:
                # render to enable resizing
                composite_image = consolidate_new_image(width, height, props.consolidate_alpha, image_map, props.consolidate_filename, props.consolidate_fileformat, restrict_name)
            if self.remap:
                if context.area:
                    context.area.header_text_set("Updating textures and UVs")
                consolidate_update_textures(textures, uv_layers, image_map, composite_image, restrict_name)
            if not ts_found:
                break
        
        if context.area:
            context.area.header_text_set()        
        return {'FINISHED'}  


class CycleBlendtype(bpy.types.Operator):
    '''Change the transparency blending mode of the active texture face'''
    bl_idname = "paint.cycle_blendtype"
    bl_label = "Cycle transparency blending mode"
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if not ob or not ob.data:
            return False
        return ob.type == 'MESH'
    
    def invoke(self, context, event):
        object = context.active_object
        mesh = object.data
        old_mode = object.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        
        if context.tool_settings.use_uv_select_sync:
            # use MeshFace selection state
            faces = [[tex, i] for tex in mesh.uv_textures for i, face in enumerate(tex.data) if mesh.faces[i].select]
        else:
            # get MeshTextureFace selection state
            faces = [[tex, i] for tex in mesh.uv_textures for i, face in enumerate(tex.data) if [uv_sel for uv_sel in face.select_uv]==[True,True,True,True]]
        if faces:
            old_type = faces[0][0].data[faces[0][1]].blend_type
            if old_type == 'OPAQUE':
                new_type = 'ALPHA'
            elif old_type == 'ALPHA':
                new_type = 'CLIPALPHA'
            else:
                new_type = 'OPAQUE'
            for [tex, i] in faces:
                tex.data[i].blend_type = new_type
        bpy.ops.object.mode_set(mode=old_mode)
        
        return {'FINISHED'}


class DefaultMaterial(bpy.types.Operator):
    '''Add a default dif/spec/normal material to an object'''
    bl_idname = "object.default_material"
    bl_label = "Default material"
    
    @classmethod
    def poll(cls, context):
        object = context.active_object
        if not object or not object.data:
            return False
        return object.type == 'MESH'
    
    def invoke(self, context, event):
        objects = context.selected_objects
        for ob in objects:
            if not ob.data or ob.type != 'MESH':
                continue
            
        mat = bpy.data.materials.new(ob.name)
        
        # diffuse texture
        tex = bpy.data.textures.new(ob.name+"_D", 'IMAGE')
        ts = mat.texture_slots.add()
        ts.texture_coords = 'UV'
        ts.texture = tex
        # specular texture
        tex = bpy.data.textures.new(ob.name+"_S", 'IMAGE')
        ts = mat.texture_slots.add()
        ts.texture_coords = 'UV'
        ts.use_map_color_diffuse = False
        ts.use_map_specular = True
        ts.texture = tex
        # normal texture
        tex = bpy.data.textures.new(ob.name+"_N", 'IMAGE')
        tex.use_normal_map = True
        ts = mat.texture_slots.add()
        ts.texture_coords = 'UV'
        ts.use_map_color_diffuse = False
        ts.use_map_normal = True
        ts.texture = tex
        
        ob.data.materials.append(mat)
        
        return {'FINISHED'}
    


class DisplayToolMode(bpy.types.Operator):
    '''Display paint tool and blend mode in the 3d-view'''
    bl_idname = "paint.display_tool_mode"
    bl_label = "Tool + Mode"
    
    _handle = None
    _timer = None
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'PAINT_TEXTURE'
    
    def modal(self, context, event):
        if context.window_manager.tpp.toolmode_enabled == -1:
            context.window_manager.event_timer_remove(self._timer)
            context.region.callback_remove(self._handle)
            context.window_manager.tpp.toolmode_enabled = 0
            if context.area:
                context.area.tag_redraw()
            return {'CANCELLED'}
        
        if context.area:
            context.area.tag_redraw()
        
        if event.type == 'TIMER':
            brush = context.tool_settings.image_paint.brush
            if brush.name != context.window_manager.tpp.toolmode_tool:
                context.window_manager.tpp.toolmode_tool = brush.name
                context.window_manager["tpp_toolmode_time"] = time.time()
            if brush.blend != context.window_manager.tpp.toolmode_mode:
                context.window_manager.tpp.toolmode_mode = brush.blend
                context.window_manager["tpp_toolmode_time"] = time.time()
            if time.time() - context.window_manager["tpp_toolmode_time"] < 1:
                x = event.mouse_region_x
                y = event.mouse_region_y + brush.size + 5
                context.window_manager["tpp_toolmode_brushloc"] = (x, y)
        
        return {'PASS_THROUGH'}
    
    def cancel(self, context):
        try:
            context.window_manager.event_timer_remove(self._timer)
            context.region.callback_remove(self._handle)
            context.window_manager.tpp.toolmode_enabled = 0
        except:
            pass
        return {'CANCELLED'}
    
    def invoke(self, context, event):
        if context.window_manager.tpp.toolmode_enabled == 0:
            brush = context.tool_settings.image_paint.brush
            context.window_manager.tpp.toolmode_enabled = 1
            context.window_manager["tpp_toolmode_time"] = time.time()
            context.window_manager.tpp.toolmode_tool = brush.name
            context.window_manager.tpp.toolmode_mode = brush.blend
            context.window_manager.modal_handler_add(self)
            self._handle = context.region.callback_add(toolmode_draw_callback,
                (self, context), 'POST_PIXEL')
            self._timer = context.window_manager.event_timer_add(0.02, context.window)
        else:
            context.window_manager.tpp.toolmode_enabled = -1
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}



class GridTexture(bpy.types.Operator):
    '''Toggle between current texture and UV / Colour grids'''
    bl_idname = "paint.grid_texture"
    bl_label = "Grid texture"
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()
    
    def invoke(self, context, event):
        objects = bpy.context.selected_objects
        meshes = [object.data for object in objects if object.type == 'MESH']
        if not meshes:
            return {'CANCELLED'}
        
        tex_image = []
        for mesh in meshes:
            for mat in mesh.materials:
                for tex in [ts.texture for ts in mat.texture_slots if ts and ts.texture.type=='IMAGE' and ts.texture.image]:
                    tex_image.append([tex.name, tex.image.name])
        if not tex_image:
            return {'CANCELLED'}
        
        first_image = bpy.data.images[tex_image[0][1]]
        if "grid_texture_mode" in first_image:
            mode = first_image["grid_texture_mode"]
        else:
            mode = 1
        
        if mode == 1:
            # original textures, change to new UV grid
            width = max([bpy.data.images[image].size[0] for tex, image in tex_image])
            height = max([bpy.data.images[image].size[1] for tex, image in tex_image])
            new_image = bpy.data.images.new("temp_grid", width=width, height=height)
            new_image.generated_type = 'UV_GRID'
            new_image["grid_texture"] = tex_image
            new_image["grid_texture_mode"] = 2
            for tex, image in tex_image:
                bpy.data.textures[tex].image = new_image
        elif mode == 2:
            # change from UV grid to Colour grid
            first_image.generated_type = 'COLOR_GRID'
            first_image["grid_texture_mode"] = 3
        elif mode == 3:
            # change from Colour grid back to original textures
            if "grid_texture" not in first_image:
                first_image["grid_texture_mode"] = 1
                self.report({'ERROR'}, "Couldn't retrieve original images")
                return {'FINISHED'}
            tex_image = first_image["grid_texture"]
            for tex, image in tex_image:
                if tex in bpy.data.textures and image in bpy.data.images:
                    bpy.data.textures[tex].image = bpy.data.images[image]
            bpy.data.images.remove(first_image)
        
        return {'FINISHED'}


class MassLinkAppend(bpy.types.Operator, ImportHelper):
    '''Import objects from multiple blend-files at the same time'''
    bl_idname = "wm.mass_link_append"
    bl_label = "Mass Link/Append"
    bl_options = {'REGISTER', 'UNDO'}
    
    active_layer = bpy.props.BoolProperty(name="Active Layer",
        default=True,
        description="Put the linked objects on the active layer")
    autoselect = bpy.props.BoolProperty(name="Select",
        default=True,
        description="Select the linked objects")
    instance_groups = bpy.props.BoolProperty(name="Instance Groups",
        default=False,
        description="Create instances for each group as a DupliGroup")
    link = bpy.props.BoolProperty(name="Link",
        default=False,
        description="Link the objects or datablocks rather than appending")
    relative_path = bpy.props.BoolProperty(name="Relative Path",
        default=True,
        description="Select the file relative to the blend file")
    
    def execute(self, context):
        directory, filename = os.path.split(bpy.path.abspath(self.filepath))
        files = []
        
        # find all blend-files in the given directory
        for root, dirs, filenames in os.walk(directory):
            for file in filenames:
                if file.endswith(".blend"):
                    files.append([root+os.sep, file])
            break # don't search in subdirectories
        
        # append / link objects
        old_selection = context.selected_objects
        new_selection = []
        print("_______ Texture Paint Plus _______")
        print("You can safely ignore the line(s) below")
        for directory, filename in files:
            # get object names
            with bpy.data.libraries.load(directory + filename) as (append_lib, current_lib):
                ob_names = append_lib.objects
            for name in ob_names:
                append_libs = [{"name":name} for name in ob_names]
            # appending / linking
            bpy.ops.wm.link_append(filepath=os.sep+filename+os.sep+"Object"+os.sep,
                filename=name, directory=directory+filename+os.sep+"Object"+os.sep,
                link=self.link, autoselect=True, active_layer=self.active_layer,
                relative_path=self.relative_path, instance_groups=self.instance_groups,
                files=append_libs)
            if not self.link:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.make_local()
                bpy.ops.object.make_local(type='SELECTED_OBJECTS_DATA')
            new_selection += context.selected_objects
        print("__________________________________")
        bpy.ops.object.select_all(action='DESELECT')
        if self.autoselect:
            for ob in new_selection:
                ob.select = True
        else:
            for ob in old_selection:
                ob.select = True
        
        return {'FINISHED'}


class OriginSet(bpy.types.Operator):
    '''Set origin while in editmode'''
    bl_idname = "mesh.origin_set"
    bl_label = "Set Origin"
    
    type = bpy.props.EnumProperty(name="Type",
        items = (("GEOMETRY_ORIGIN", "Geometry to Origin", "Move object geometry to object origin"),
            ("ORIGIN_GEOMETRY", "Origin to Geometry", "Move object origin to center of object geometry"),
            ("ORIGIN_CURSOR", "Origin to 3D Cursor", "Move object origin to position of the 3d cursor")),
        default = 'GEOMETRY_ORIGIN')
    center = bpy.props.EnumProperty(name="Center",
        items=(("MEDIAN", "Median Center", ""),
            ("BOUNDS", "Bounds Center", "")),
        default = 'MEDIAN')
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if not ob or not ob.data:
            return False
        return ob.type == 'MESH'
    
    def execute(self, context):
        object = context.active_object
        mesh = object.data
        old_mode = object.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type=self.type, center=self.center)
        bpy.ops.object.mode_set(mode=old_mode)
        
        return {'FINISHED'}


class ReloadImage(bpy.types.Operator):
    '''Reload image displayed in image-editor'''
    bl_idname = "paint.reload_image"
    bl_label = "Reload image"
    
    def invoke(self, context, event):
        images = get_images_in_editors(context)
        for img in images:
            img.reload()
        
        # make the changes immediately visible in 3d-views
        # image editor updating is handled in get_images_in_editors()
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        return{'FINISHED'}


class ReloadImages(bpy.types.Operator):
    '''Reload all images'''
    bl_idname = "paint.reload_images"
    bl_label = "Reload all images"
    
    def invoke(self, context, event):
        reloaded = [0, 0]
        for img in bpy.data.images:
            img.reload()
        
        # make the changes immediately visible in image editors and 3d-views
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR' or area.type == 'VIEW_3D':
                area.tag_redraw()
        
        return {'FINISHED'}


class SampleColor(bpy.types.Operator):
    '''Sample color'''
    bl_idname = "paint.sample_color_custom"
    bl_label = "Sample color"
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()
    
    def invoke(self, context, event):
        mesh = context.active_object.data
        paint_mask = mesh.use_paint_mask
        mesh.use_paint_mask = False
        bpy.ops.paint.sample_color('INVOKE_REGION_WIN')
        mesh.use_paint_mask = paint_mask
        
        return {'FINISHED'}


class SaveImage(bpy.types.Operator):
    '''Save image displayed in image-editor'''
    bl_idname = "paint.save_image"
    bl_label = "Save image"
    
    def invoke(self, context, event):
        images = get_images_in_editors(context)
        for img in images:
            img.save()

        return{'FINISHED'}


class SaveImages(bpy.types.Operator):
    '''Save all images'''
    bl_idname = "wm.save_images"
    bl_label = "Save all images"
    
    def invoke(self, context, event):
        correct = 0
        for img in bpy.data.images:
            try:
                img.save()
                correct += 1
            except:
                # some images don't have a source path (e.g. render result)
                pass
        
        self.report({'INFO'}, "Saved " + str(correct) + " images")
        
        return {'FINISHED'}


class StraightLine(bpy.types.Operator):
    '''Paint a straight line'''
    bl_idname = "paint.straight_line"
    bl_label = "Straight line"
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()
    
    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            context.region.callback_remove(self.handle)
            x0, y0, x1, y1 = context.window_manager["straight_line"]
            x1, y1 = [event.mouse_region_x, event.mouse_region_y]
            bpy.ops.paint.image_paint(stroke=[{"name":"", "pen_flip":False,
                "is_start":False, "location":(0,0,0), "mouse":(x0, y0),
                "pressure":1, "time":0},
                {"name":"", "pen_flip":False, "is_start":False,
                "location":(0,0,0), "mouse":(x1, y1), "pressure":1,
                "time":1}])
            return {'FINISHED'}
        
        elif event.type == 'MOUSEMOVE':
            x0, y0, x1, y1 = context.window_manager["straight_line"]
            x1, y1 = [event.mouse_region_x, event.mouse_region_y]
            context.window_manager["straight_line"] = [x0, y0, x1, y1]
        
        if context.area:
            context.area.tag_redraw()
        
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        context.window_manager["straight_line"] = [event.mouse_region_x,
            event.mouse_region_y, event.mouse_region_x, event.mouse_region_y]
        context.window_manager.modal_handler_add(self)
        self.handle = context.region.callback_add(draw_callback,
            (self, context), 'POST_PIXEL')
        
        return {'RUNNING_MODAL'}


class SyncSelection(bpy.types.Operator):
    '''Sync selection from uv-editor to 3d-view'''
    bl_idname = "uv.sync_selection"
    bl_label = "Sync selection"
    
    _timer = None
    _selection_3d = []
    handle1 = None
    handle2 = None
    handle3 = None
    area = None
    region = None
    overlay_vertices = []
    overlay_edges = []
    overlay_faces = []
    position_vertices = []
    position_edges = []
    position_faces = []
    position2_vertices = []
    position2_edges = []
    position2_edges = []
    
    @classmethod
    def poll(cls, context):
        return(context.active_object and context.active_object.mode=='EDIT')
    
    def modal(self, context, event):
        if self.area:
            self.area.tag_redraw()
        if context.area:
            context.area.tag_redraw()
        
        if context.window_manager.tpp.sync_enabled == -1:
            self.region.callback_remove(self.handle1)
            self.region.callback_remove(self.handle2)
            context.region.callback_remove(self.handle3)
            self.area = None
            self.region = None
            context.window_manager.tpp.sync_enabled = 0
            return {"CANCELLED"}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.window_manager.tpp.sync_enabled < 1:
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    self.area = area
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            self.region = region
                            context.window_manager.tpp.sync_enabled = 1
                            
                            # getting overlay selection
                            old_sync = context.tool_settings.use_uv_select_sync
                            old_select_mode = [x for x in context.tool_settings.mesh_select_mode]
                            context.tool_settings.mesh_select_mode = [True, False, False]
                            bpy.ops.object.mode_set(mode='OBJECT')
                            mesh = context.active_object.data
                            self._selection_3d = [v.index for v in mesh.vertices if v.select]
                            tfl = mesh.uv_textures.active
                            selected = []
                            for mface, tface in zip(mesh.faces, tfl.data):
                                selected += [mface.vertices[i] for i, x in enumerate(tface.select_uv) if x]
                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.mesh.select_all(action='DESELECT')
                            bpy.ops.object.mode_set(mode='OBJECT')
                            context.tool_settings.use_uv_select_sync = True
                            for v in selected:
                                mesh.vertices[v].select = True
                            
                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.object.mode_set(mode='OBJECT')
                            
                            # indices for overlay in 3d-view
                            self.overlay_vertices = [vertex.index for vertex in mesh.vertices if vertex.select]
                            self.overlay_edges = [edge.index for edge in mesh.edges if edge.select]
                            self.overlay_faces = [face.index for face in mesh.faces if face.select]
                            
                            # overlay positions for image editor
                            dict_vertex_pos = dict([[i, []] for i in range(len(mesh.vertices))])
                            tfl = mesh.uv_textures.active
                            for mface, tface in zip(mesh.faces, tfl.data):
                                for i, vert in enumerate(mface.vertices):
                                    dict_vertex_pos[vert].append([co for co in tface.uv[i]])
                            
                            self.position2_vertices = []
                            for v in self.overlay_vertices:
                                for pos in dict_vertex_pos[v]:
                                    self.position2_vertices.append(pos)
                            
                            # set everything back to original state
                            bpy.ops.object.mode_set(mode='EDIT')
                            context.tool_settings.use_uv_select_sync = old_sync
                            bpy.ops.mesh.select_all(action='DESELECT')
                            bpy.ops.object.mode_set(mode='OBJECT')
                            for v in self._selection_3d:
                                mesh.vertices[v].select = True
                            bpy.ops.object.mode_set(mode='EDIT')
                            context.tool_settings.mesh_select_mode = old_select_mode
                            
                            
                            # 3d view callbacks
                            context.window_manager.modal_handler_add(self)
                            self.handle1 = region.callback_add(sync_calc_callback,
                                (self, context, area, region), "POST_VIEW")
                            self.handle2 = region.callback_add(sync_draw_callback,
                                (self, context), "POST_PIXEL")
                            
                            # image editor callback
                            self.handle3 = context.region.callback_add(sync_draw_callback2,
                                (self, context), "POST_VIEW")
                            
                            break
                    break
        else:
            context.window_manager.tpp.sync_enabled = -1
        
        return {'RUNNING_MODAL'}


class ToggleAddMultiply(bpy.types.Operator):
    '''Toggle between Add and Multiply blend modes'''
    bl_idname = "paint.toggle_add_multiply"
    bl_label = "Toggle add/multiply"
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()
    
    def invoke(self, context, event):
        brush = context.tool_settings.image_paint.brush
        if brush.blend != 'ADD':
            brush.blend = 'ADD'
        else:
            brush.blend = 'MUL'
        
        return {'FINISHED'}


class ToggleAlphaMode(bpy.types.Operator):
    '''Toggle between Add Alpha and Erase Alpha blend modes'''
    bl_idname = "paint.toggle_alpha_mode"
    bl_label = "Toggle alpha mode"
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()
    
    def invoke(self, context, event):
        brush = context.tool_settings.image_paint.brush
        if brush.blend != 'ERASE_ALPHA':
            brush.blend = 'ERASE_ALPHA'
        else:
            brush.blend = 'ADD_ALPHA'
        
        return {'FINISHED'}


class ToggleImagePaint(bpy.types.Operator):
    '''Toggle image painting in the UV/Image editor'''
    bl_idname = "paint.toggle_image_paint"
    bl_label = "Image Painting"
    
    @classmethod
    def poll(cls, context):
        return(context.space_data.type == 'IMAGE_EDITOR')
    
    def invoke(self, context, event):
        context.space_data.use_image_paint = not context.space_data.use_image_paint
        
        return {'FINISHED'}

class ToggleUVSelectSync(bpy.types.Operator):
    '''Toggle use_uv_select_sync in the UV editor'''
    bl_idname = "uv.toggle_uv_select_sync"
    bl_label = "UV Select Sync"
    
    @classmethod
    def poll(cls, context):
        return(context.space_data.type == 'IMAGE_EDITOR')
    
    def invoke(self, context, event):
        context.tool_settings.use_uv_select_sync = not context.tool_settings.use_uv_select_sync
        
        return {'FINISHED'}


##########################################
#                                        #
# User interface                         #
#                                        #
##########################################

# panel with consolidate image options
class VIEW3D_PT_tools_consolidate(bpy.types.Panel):
    bl_label = "Consolidate Images"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        props = context.window_manager.tpp
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(props, "consolidate_filename", text="")
        col.prop(props, "consolidate_fileformat", text="")
        col = layout.column(align=True)
        col.prop(props, "consolidate_input", text="")
        row = col.row()
        col_left = row.column(align=True)
        col_left.active = not props.consolidate_auto_size
        col_right = row.column()
        col_left.prop(props, "consolidate_width")
        col_left.prop(props, "consolidate_height")
        col_right.prop(props, "consolidate_auto_size")
        col_right.prop(props, "consolidate_alpha")
        layout.prop(props, "consolidate_split")
        col = layout.column(align=True)
        col.operator("image.consolidate", text="Consolidate")
        col.operator("image.consolidate", text="Consolidate + remap").remap = True


# property group containing all properties of the add-on
class TexturePaintPlusProps(bpy.types.PropertyGroup):
    consolidate_alpha = bpy.props.BoolProperty(name = "Alpha",
        description = "Determines if consolidated image has an alpha channel",
        default = True)
    consolidate_auto_size = bpy.props.BoolProperty(name = "Auto",
        description = "Automatically determine size of consolidated image, no resizing is done",
        default = False)
    consolidate_fileformat = bpy.props.EnumProperty(name = "Fileformat",
        items = (("BMP", "BMP", "Output image in bitmap format"),
            ("IRIS", "Iris", "Output image in (old!) SGI IRIS format"),
            ("PNG", "PNG", "Output image in PNG format"),
            ("JPEG", "JPEG", "Output image in JPEG format"),
            ("TARGA", "Targa", "Output image in Targa format"),
            ("TARGA_RAW", "Targa Raw", "Output image in uncompressed Targa format"),
            ("CINEON", "Cineon", "Output image in Cineon format"),
            ("DPX", "DPX", "Output image in DPX format"),
            ("MULTILAYER", "MultiLayer", "Output image in multilayer OpenEXR format"),
            ("OPEN_EXR", "OpenEXR", "Output image in OpenEXR format"),
            ("HDR", "Radiance HDR", "Output image in Radiance HDR format"),
            ("TIFF", "TIFF", "Output image in TIFF format")),
        description = "File format to save the rendered image as",
        default = 'TARGA')
    consolidate_filename = bpy.props.StringProperty(name = "Filename",
        description = "Location where to store the consolidated image",
        default = "//consolidate",
        subtype = 'FILE_PATH')
    consolidate_height = bpy.props.IntProperty(name = "Y",
        description = "Image height",
        min = 1,
        default = 1024)
    consolidate_input = bpy.props.EnumProperty(name = "Input",
        items = (("active", "Only active object", "Only combine the images of the active object"),
            ("selected", "All selected objects", "Combine the images of all selected objects")),
        description = "Objects of which the images will be consolidated into a single image",
        default = 'selected')
    consolidate_split = bpy.props.BoolProperty(name = "Split by type",
        description = "Consolidate Diffuse, Shading, Specular and Geometry influences into different images",
        default = True)
    consolidate_width = bpy.props.IntProperty(name = "X",
        description = "Image width",
        min = 1,
        default = 1024)
    sync_enabled = bpy.props.IntProperty(name = "Enabled",
        description = "internal use",
        default = 0)
    toolmode_enabled = bpy.props.IntProperty(name = "Enabled",
        description = "internal use",
        default = 0)
    toolmode_mode = bpy.props.StringProperty(name = "Mode",
        description = "internal use",
        default = "")
    toolmode_tool = bpy.props.StringProperty(name = "Tool",
        description = "internal use",
        default = "")


classes = [AddDefaultImage,
    AutoMergeUV,
    BrushPopup,
    ChangeSelection,
    ConsolidateImages,
#    CycleBlendtype,
    DefaultMaterial,
    DisplayToolMode,
    GridTexture,
    MassLinkAppend,
    OriginSet,
    ReloadImage,
    ReloadImages,
    SampleColor,
    SaveImage,
    SaveImages,
    StraightLine,
    SyncSelection,
    ToggleAddMultiply,
    ToggleAlphaMode,
    ToggleImagePaint,
    ToggleUVSelectSync,
    VIEW3D_PT_tools_consolidate,
    TexturePaintPlusProps]


def menu_func(self, context):
    layout = self.layout
    wm = context.window_manager
    if "tpp_automergeuv" not in wm:
        automergeuv_enabled = False
    else:
        automergeuv_enabled = wm["tpp_automergeuv"]
    
    if automergeuv_enabled:
        layout.operator("paint.auto_merge_uv", icon="CHECKBOX_HLT")
    else:
        layout.operator("paint.auto_merge_uv", icon="CHECKBOX_DEHLT")


def menu_mesh_select_mode(self, context):
    layout = self.layout
    layout.separator()
    
    prop = layout.operator("wm.context_set_value", text="Vertex + Edge", icon='EDITMODE_HLT')
    prop.value = "(True, True, False)"
    prop.data_path = "tool_settings.mesh_select_mode"
    
    prop = layout.operator("wm.context_set_value", text="Vertex + Face", icon='ORTHO')
    prop.value = "(True, False, True)"
    prop.data_path = "tool_settings.mesh_select_mode"
    
    prop = layout.operator("wm.context_set_value", text="Edge + Face", icon='SNAP_FACE')
    prop.value = "(False, True, True)"
    prop.data_path = "tool_settings.mesh_select_mode"
    
    layout.separator()
    
    prop = layout.operator("wm.context_set_value", text="All", icon='OBJECT_DATAMODE')
    prop.value = "(True, True, True)"
    prop.data_path = "tool_settings.mesh_select_mode"


def menu_snap(self, context):
    layout = self.layout
    layout.separator()
    
    layout.operator("mesh.origin_set", text="Geometry to Origin")
    layout.operator("mesh.origin_set", text="Origin to Geometry").type = 'ORIGIN_GEOMETRY'
    layout.operator("mesh.origin_set", text="Origin to 3D Cursor").type = 'ORIGIN_CURSOR'


def register():
    # register classes
    init_props()
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.tpp = bpy.props.PointerProperty(\
        type = TexturePaintPlusProps)
    
    # add Image Paint keymap entries
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Image Paint']
    kmi = km.keymap_items.new("paint.toggle_alpha_mode", 'A', 'PRESS')
#    kmi = km.keymap_items.new("paint.cycle_blendtype", 'A', 'PRESS',
#        ctrl=True)
    kmi = km.keymap_items.new("wm.context_toggle", 'B', 'PRESS')
    kmi.properties.data_path = "user_preferences.system.use_mipmaps"
    kmi = km.keymap_items.new("paint.toggle_add_multiply", 'D', 'PRESS')
    kmi = km.keymap_items.new("paint.display_tool_mode", 'F', 'PRESS',
        ctrl=True)
    kmi = km.keymap_items.new("paint.grid_texture", 'G', 'PRESS')
    kmi = km.keymap_items.new("paint.straight_line", 'LEFTMOUSE', 'PRESS',
        shift=True)
    kmi = km.keymap_items.new("paint.change_selection", 'NUMPAD_MINUS', 'PRESS',
        ctrl=True)
    kmi.properties.mode = 'less'
    kmi = km.keymap_items.new("paint.change_selection", 'NUMPAD_PLUS', 'PRESS',
        ctrl=True)
    kmi = km.keymap_items.new("wm.context_set_enum", 'Q', 'PRESS')
    kmi.properties.data_path = "tool_settings.image_paint.brush.blend"
    kmi.properties.value = 'MIX'
    kmi = km.keymap_items.new("wm.context_toggle", 'R', 'PRESS')
    kmi.properties.data_path = "active_object.show_wire"
    kmi = km.keymap_items.new("paint.reload_image", 'R', 'PRESS',
        alt=True)
    kmi = km.keymap_items.new("paint.sample_color_custom", 'RIGHTMOUSE', 'PRESS')
    kmi = km.keymap_items.new("wm.context_toggle", 'S', 'PRESS')
    kmi.properties.data_path = "active_object.data.use_paint_mask"
    kmi = km.keymap_items.new("paint.save_image", 'S', 'PRESS',
        alt=True)
    kmi = km.keymap_items.new("paint.brush_popup", 'W', 'PRESS')
    kmi = km.keymap_items.new("paint.toggle_image_paint", 'W', 'PRESS',
        shift=True)
    
    # add 3D View keymap entry
    km = bpy.context.window_manager.keyconfigs.default.keymaps['3D View']
    kmi = km.keymap_items.new("object.add_default_image", 'Q', 'PRESS')
    kmi = km.keymap_items.new("object.default_material", 'X', 'PRESS',
        alt=True, ctrl=True)
    
    # add Mesh keymap entry
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
#    kmi = km.keymap_items.new("paint.cycle_blendtype", 'A', 'PRESS',
#        ctrl=True)
    
    # add UV Editor keymap entries
    km = bpy.context.window_manager.keyconfigs.default.keymaps['UV Editor']
    kmi = km.keymap_items.new("uv.sync_selection", 'F', 'PRESS')
    kmi = km.keymap_items.new("uv.toggle_uv_select_sync", 'F', 'PRESS',
        shift=True)
    kmi = km.keymap_items.new("transform.snap_type", 'TAB', 'PRESS',
        ctrl=True, shift=True)
    kmi = km.keymap_items.new("paint.toggle_image_paint", 'W', 'PRESS',
        shift=True)
    
    # deactivate to prevent clashing
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Window']
    for kmi in km.keymap_items:
        if kmi.type == 'S' and not kmi.any and not kmi.shift and kmi.ctrl and kmi.alt and not kmi.oskey:
            kmi.active = False
    
    # add Window keymap entry
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Window']
    kmi = km.keymap_items.new("wm.mass_link_append", 'F1', 'PRESS',
        alt=True)
    kmi = km.keymap_items.new("paint.reload_images", 'R', 'PRESS',
        alt=True, ctrl=True)
    kmi = km.keymap_items.new("wm.save_images", 'S','PRESS',
        alt=True, ctrl=True)
    
    # deactivate and remap to prevent clashing
    if bpy.context.user_preferences.inputs.select_mouse == 'RIGHT':
        right_mouse = ['RIGHTMOUSE', 'SELECTIONMOUSE']
    else: #'LEFT'
        right_mouse = ['RIGHTMOUSE', 'ACTIONMOUSE']
    km = bpy.context.window_manager.keyconfigs.default.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.type in right_mouse and kmi.alt and not kmi.ctrl and not kmi.shift:
            # deactivate
            kmi.active = False
    for kmi in km.keymap_items:
        if kmi.type in right_mouse and not kmi.alt and not kmi.ctrl and not kmi.shift:
            # remap
            kmi.alt = True
    
    # add menu entries
    bpy.types.VIEW3D_MT_edit_mesh.prepend(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_select_mode.append(menu_mesh_select_mode)
    bpy.types.VIEW3D_MT_snap.append(menu_snap)


def unregister():
    # remove menu entries
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_select_mode.remove(menu_mesh_select_mode)
    bpy.types.VIEW3D_MT_snap.remove(menu_snap)
    
    # remove Image Paint keymap entries
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Image Paint']
    for kmi in km.keymap_items:
        if kmi.idname in ["paint.brush_popup", "paint.straight_line", "paint.toggle_alpha_mode", "paint.sample_color_custom", "paint.change_selection", "paint.cycle_blendtype", "paint.toggle_image_paint",
        "paint.toggle_add_multiply", "paint.grid_texture", "paint.display_tool_mode", "paint.reload_image", "paint.save_image"]:
            km.keymap_items.remove(kmi)
        elif kmi.idname == "wm.context_toggle":
            if getattr(kmi.properties, "data_path", False) in ["active_object.data.use_paint_mask", "active_object.show_wire", "user_preferences.system.use_mipmaps"]:
                km.keymap_items.remove(kmi)
        elif kmi.idname == "wm.context_set_enum":
            if getattr(kmi.properties, "data_path", False) in ["tool_settings.image_paint.brush.blend"]:
                km.keymap_items.remove(kmi)
    
    # remove 3D View keymap entry
    km = bpy.context.window_manager.keyconfigs.default.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname in ["object.add_default_image", "object.default_material"]:
            km.keymap_items.remove(kmi)
    
    # remove Mesh keymap entry
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname in ["paint.cycle_blendtype"]:
            km.keymap_items.remove(kmi)

    # remove UV Editor keymap entries
    km = bpy.context.window_manager.keyconfigs.default.keymaps['UV Editor']
    for kmi in km.keymap_items:
        if kmi.idname in ["transform.snap_type", "uv.sync_selection", "uv.toggle_uv_select_sync", "paint.toggle_image_paint"]:
            km.keymap_items.remove(kmi)

    # remove Window keymap entry
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Window']
    for kmi in km.keyamp_items:
        if kmi.idname in ["wm.mass_link_append", "paint.reload_images", "wm.save_images"]:
            km.keymap_items.remove(kmi)
    
    # remap and reactivate original items
    if bpy.context.user_preferences.inputs.select_mouse == 'RIGHT':
        right_mouse = ['RIGHTMOUSE', 'SELECTIONMOUSE']
    else: #'LEFT'
        right_mouse = ['RIGHTMOUSE', 'ACTIONMOUSE']
    km = bpy.context.window_manager.keyconfigs.default.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.type in right_mouse and kmi.alt and not kmi.ctrl and not kmi.shift:
            if kmi.active:
                # remap
                kmi.alt = False
            else:
                # reactivate
                kmi.active = True
    
    # reactive original item
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Window']
    for kmi in km.keymap_items:
        if kmi.type == 'S' and not kmi.any and not kmi.shift and kmi.ctrl and kmi.alt and not kmi.oskey:
            kmi.active = True
    
    # unregister classes
    remove_props()
    for c in classes:
        bpy.utils.unregister_class(c)
    try:
        del bpy.types.WindowManager.tpp
    except:
        pass


if __name__ == "__main__":
    register()