bl_info = {
"name": "Cleanplate creator",
"author": "Sebastian Koenig",
"version": (1, 0, 1),
"blender": (2, 7, 2),
"location": "",
"description": "",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Learnbgame"
}

import bpy


##### Corner Pin Creator ######

def get_track_empties(context, tracks):
    # the selected empties are assumed to be the linked tracks
    # these ones will be the parents

    for e in context.selected_objects:
        if e.type=="EMPTY":
            tracks.append(e)
            e.empty_draw_size = 0.05
            e.layers = [False] + [True] + [False] * 18


def create_hook_empties(context, tracks, hooks):
    # create the actual hooks at the same position as the tracks

    for t in tracks:
        # create a new empty, assign name and location
        h = bpy.data.objects.new("CTRL_" + t.name, None)
        h.location = t.matrix_world.to_translation()
        h.empty_draw_size = 0.015
        h.empty_draw_type = "CUBE"

        # link it to the scene
        bpy.context.scene.objects.link(h)

        # add the new empty to the list of parents
        hooks.append(h)

        # make the hook empty a child of the parent
        bpy.ops.object.select_all(action='DESELECT')
        t.select = True
        h.select = True
        bpy.context.scene.objects.active = t
        bpy.ops.object.parent_set()
  
    bpy.ops.object.select_all(action='DESELECT')



def get_location(hooks):
    coords=[]
    for h in hooks:
        coords.append(h.location*h.matrix_world)
    return coords



def create_canvas_object(context, name, hooks, cleanobject, cams):
    from bpy_extras.io_utils import unpack_list

    # get all locations of the hooks in the list
    coords=get_location(hooks)

    # create the vertices of the cleanplate mesh
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(coords))
    me.vertices.foreach_set("co", unpack_list(coords))

    # create the object which is using the mesh
    ob = bpy.data.objects.new(name, me)
    ob.location = (0,0,0)

    # link it to the scene and make it active
    bpy.context.scene.objects.link(ob)
    bpy.context.scene.objects.active=ob
    ob.layers = [True] + [False] * 19

    # go into edit mode, select all vertices and create the face
    if not context.object.mode=="EDIT":
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode="OBJECT")

    cleanobject.append(ob)

    bpy.ops.object.select_all(action='DESELECT')
    camera = cams[0]
    ob.select = True
    bpy.context.scene.objects.active = camera
    bpy.ops.object.parent_set()
    camera.select = False



def hook_em_up(hooks, ob):
    # create an yet unassigned hook modifier for each hook in the list
    modlist=[]
    for h in hooks:
        modname="Hook_" + h.name
        modlist.append(modname)
        mod = ob.modifiers.new(name=modname, type="HOOK")
        mod.object=h

    # now for each vertex go to edit mode, select the vertex and assign the modifier
    verts = ob.data.vertices
    for i in range(len(verts)):
        # Deselect Everything in Edit Mode
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        ob.data.vertices[i].select=True
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.object.hook_assign(modifier=modlist[i])

    bpy.ops.object.mode_set(mode = 'OBJECT')



def hooker_cam(context, cams):

    for ob in bpy.data.objects:
        if ob.type=="CAMERA":
            cams.append(ob)
    camera = cams[0]
    camera.rotation_euler=(1.570796251296997, -0.0, 0.0)
    camera.location = (0,-8,2.2)



def setup_scene(context):
    scene = context.scene
    scene.active_clip = context.space_data.clip



####### TEXTURE PROJECTION FUNCTIONS ###########

def prepare_mesh(context, ob, size, canvas, clip):

    me = ob.data
    # see if object is already prepared.das
    if not "is_prepared" in ob:
        # set Edit mode if needed
        if not context.object.mode=="EDIT":
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action='SELECT')

        # make sure mesh is dense enough for projection
        if len(me.vertices)<64:
            sub = ob.modifiers.new(name="Subsurf", type="SUBSURF")
            sub.subdivision_type="SIMPLE"
            sub.levels=4
            sub.render_levels=4
            bpy.context.object.modifiers["Subsurf"].subdivision_type = 'SIMPLE'

        # unwrap and go back to object mode
        bpy.ops.uv.smart_project(island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")

        # make sure we have something to paint on
        if len(list(me.uv_textures)) > 0:
            if not me.uv_textures.get("projection"):
                me.uv_textures.new(name="projection")
        else:
            me.uv_textures.new(name="UVMap")
            me.uv_textures.new(name="projection")

        # put a canvas onto the mesh for bake and paint
        for t in  me.uv_textures:
            if t.active:
                uvtex = t.data
                for f in me.polygons:
                    #check that material had an image!
                    uvtex[f.index].image = canvas

        me.update()
        ob["is_prepared"] = True
        # create the uv-project modifier
        if not ob.modifiers.get("UVProject"):
            projector = ob.modifiers.new(name="UVProject", type="UV_PROJECT")
            projector.uv_layer = "projection"
            projector.aspect_x=clip.size[0]
            projector.aspect_y=clip.size[1]
            projector.projectors[0].object = bpy.data.objects["Camera"]
            projector.uv_layer="projection"



def change_viewport_background_for_painting(context, clip):
    # prepare the viewport for painting
    # changing from movie to image will make it updates.
    space = context.space_data

    for img in space.background_images:
        if img.source == 'MOVIE_CLIP':
            path = img.clip.filepath
            length = img.clip.frame_duration
            start = img.clip.frame_start
            offset = img.clip.frame_offset
            if bpy.data.images.get(clip.name):
                clipimage=bpy.data.images[clip.name]
            else:
                clipimage = bpy.data.images.load(path)
            print(clipimage)
            
            img.show_on_foreground = True
            img.source = "IMAGE"
            img.image=clipimage
            img.image.colorspace_settings.name=clip.colorspace_settings.name
            backimg = img.image_user

            configure_video_image(context, clip, backimg)



def set_cleanplate_brush(context, clip, canvas, ob):
    me = ob.data
    
    paint_settings = bpy.context.tool_settings.image_paint
    ps = paint_settings
    ps.brush=bpy.data.brushes['Clone']
    ps.brush.strength=1
    ps.use_clone_layer=True
    ps.mode="IMAGE"
    ps.canvas=canvas
    ps.clone_image = bpy.data.images[clip.name]
    ps.use_normal_falloff=False
    me.uv_texture_clone = me.uv_textures.get("projection")



def configure_video_image(context, clip, image):
    # prepare an image that uses the same parameters as the movievclip
    image.use_auto_refresh=True
    image.frame_duration = clip.frame_duration
    image.frame_start = clip.frame_start
    image.frame_offset = clip.frame_offset



def prepare_clean_bake_mat(context, ob, clip, size, movietype):
    projection_tex = "projected texture"
    projection_mat = "projected clip material"

    # create texture if needed and assign
    if not bpy.data.textures.get(projection_tex):
        bpy.data.textures.new(name=projection_tex, type="IMAGE")
    tex = bpy.data.textures[projection_tex]

    # create image if needed
    if not bpy.data.images.get(clip.name):
        bpy.data.images.new(clip.name, size, size)

    # assign image to texture
    tex.image = bpy.data.images[clip.name]
    tex.image.filepath=clip.filepath
    tex.image.source=movietype
    tex.image.colorspace_settings.name=clip.colorspace_settings.name

    # configure the image
    configure_video_image(context, clip, tex.image_user)

    # create a material 
    mat = bpy.data.materials.get(projection_mat)
    if not bpy.data.materials.get(projection_mat):
        mat = bpy.data.materials.new(projection_mat)
        mat = bpy.data.materials[projection_mat]
        mat.use_shadeless=True

    # configure material
    if not mat.texture_slots.get(tex.name):
            mtex=mat.texture_slots.add()
            mtex.texture = tex
            mtex.texture_coords = 'UV'
            mtex.uv_layer = 'projection'
            mtex.use_map_color_diffuse = True

    # assign the material to material slot 0 of ob
    if not len(list(ob.material_slots)) > 0:
        ob.data.materials.append(mat)
    else:
        ob.material_slots[0].material = mat



def ma_baker(context):
    bpy.context.scene.render.bake_type = 'TEXTURE'
    bpy.ops.object.bake_image()



def set_baked_mat(context, ob, clip, canvas, movietype):
    suffix = "_" + ob.name
    clean_tex = "clean_texture" + suffix
    clean_mat = "clean_material" + suffix

    # create texture if needed and assign
    
    if not bpy.data.textures.get(clean_tex):
        bpy.data.textures.new(name=clean_tex, type="IMAGE")
    tex = bpy.data.textures[clean_tex]

    # assign image to texture
    tex.image = canvas
    
    # create a material 
    mat = bpy.data.materials.get(clean_mat)
    if not bpy.data.materials.get(clean_mat):
        mat = bpy.data.materials.new(clean_mat)
        mat = bpy.data.materials[clean_mat]
        mat.use_shadeless=True

        mtex=mat.texture_slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'
        mtex.uv_layer = 'UVMap'
        mtex.use_map_color_diffuse = True

    # assign the material to material slot 0 of ob
    if not len(list(ob.material_slots)) > 0:
        ob.data.materials.append(mat)
    else:
        ob.material_slots[0].material = mat



######## CORNER PIN CLASSES ############

class VIEW3D_OT_track_hooker(bpy.types.Operator):
    bl_idname = "clip.track_hooker"
    bl_label = "John Lee Hooker"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'CLIP_EDITOR'

    def execute(self, context):

        name="canvas"

        hooks=[]
        tracks=[]
        cleanobject=[]
        cams=[]
        
        setup_scene(context)
        # setup the camera
        hooker_cam(context, cams)

        # create the empties
        bpy.ops.clip.track_to_empty()

        # collect all empties that are selected (which is automatically the case after creating the track empties)
        get_track_empties(context, tracks)

        # create empties that will be the hooks and parent them to the tracks
        create_hook_empties(context, tracks, hooks)

        # get the position of the tracks, create a new object there and parent it to the camera
        create_canvas_object(context, name, hooks, cleanobject, cams)

        # make the cleaned object active via list, to avoid confusion
        ob = bpy.data.objects.get(cleanobject[0].name)
        bpy.context.scene.objects.active = ob

        #finally create the hooks 
        hook_em_up(hooks, ob)

        return {'FINISHED'}



class CLIP_PT_corner_hooker(bpy.types.Panel):
    bl_idname = "clip.corner_hooker"
    bl_label = "Corner Hoocker"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("clip.track_hooker")



################ TEXTURE PROJECT CLASSES ##########################

class VIEW3D_texture_extraction_setup(bpy.types.Operator):
    bl_idname="object.texture_extraction_setup"
    bl_label="Texture Extractor"

    def execute(self, context):
        clip = context.scene.active_clip
        cleaned_object = context.active_object

        clean_name = "cleanplate" + "_" + cleaned_object.name
        size = 2048
        movietype = clip.source

        # create a canvas to paint and bake on
        if not bpy.data.images.get(clean_name):
            canvas = bpy.data.images.new(clean_name, size, size)
        else:
            canvas=bpy.data.images[clean_name]

        prepare_mesh(context, cleaned_object, size, canvas, clip)

        prepare_clean_bake_mat(context, cleaned_object, clip, size, movietype)

        ma_baker(context)

        set_baked_mat(context, cleaned_object, clip, canvas, movietype)
        
        context.space_data.show_textured_solid = True
        
        return{"FINISHED"}



class VIEW3D_cleanplate_painter_setup(bpy.types.Operator):
    bl_idname = "object.cleanplate_painter_setup"
    bl_label = "Cleanplate Paint Setup"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'VIEW_3D'

    def execute(self, context):

        clip = context.scene.active_clip
        cleaned_object = context.active_object

        clean_name = "cleanplate" + "_" + cleaned_object.name
        size = 2048
        movietype = clip.source

        # create a canvas to paint and bake on
        if not bpy.data.images.get(clean_name):
            canvas = bpy.data.images.new(clean_name, size, size)
        else:
            canvas=bpy.data.images[clean_name]

        prepare_mesh(context, cleaned_object, size, canvas, clip)
        change_viewport_background_for_painting(context, clip)
        set_cleanplate_brush(context, clip, canvas, cleaned_object)

        context.space_data.viewport_shade="SOLID"
        context.space_data.show_textured_solid = True
    
        if not context.object.mode=="TEXTURE_PAINT":
            bpy.ops.object.mode_set(mode="TEXTURE_PAINT")
        
        return {'FINISHED'}



class VIEW3D_cleanplate_creator(bpy.types.Panel):
    bl_idname = "object.cleanplate_creator_setup"
    bl_label = "Cleanplate Creator" 
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.texture_extraction_setup")
        col.operator("object.cleanplate_painter_setup")



########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_OT_track_hooker)
    bpy.utils.register_class(CLIP_PT_corner_hooker)
    bpy.utils.register_class(VIEW3D_texture_extraction_setup)
    bpy.utils.register_class(VIEW3D_cleanplate_painter_setup)
    bpy.utils.register_class(VIEW3D_cleanplate_creator)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Clip', space_type='CLIP_EDITOR')
    kmi = km.keymap_items.new('clip.track_hooker', 'J', 'PRESS')



def unregister():

    bpy.utils.unregister_class(VIEW3D_OT_track_hooker)
    bpy.utils.unregister_class(CLIP_PT_corner_hooker)
    bpy.utils.unregister_class(VIEW3D_texture_extraction_setup)
    bpy.utils.unregister_class(VIEW3D_cleanplate_painter_setup)
    bpy.utils.unregister_class(VIEW3D_cleanplate_creator)


if __name__ == "__main__":
    register()
