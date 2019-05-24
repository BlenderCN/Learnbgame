bl_info = {
"name": "Texture Extractor",
"author": "Sebastian Koenig",
"version": (1, 0),
"blender": (2, 7, 2),
"location": "",
"description": "",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Learnbgame",
}

import bpy


# create node setup
# button for nodes
# create retouching setup
# create setup with shadow catching: 2 renderlayers
# set object with hooks: select hooks, create mesh with vertices near empties
# for all empties: write position
# for all vertices: if position is close to empty, --> position == empty, mark as hook
# for all vertices: create hook



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




################ CLASSES ##########################

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
    bpy.utils.register_class(VIEW3D_texture_extraction_setup)
    bpy.utils.register_class(VIEW3D_cleanplate_painter_setup)
    bpy.utils.register_class(VIEW3D_cleanplate_creator)



def unregister():

    bpy.utils.unregister_class(VIEW3D_texture_extraction_setup)
    bpy.utils.unregister_class(VIEW3D_cleanplate_painter_setup)
    bpy.utils.unregister_class(VIEW3D_cleanplate_creator)

if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name="mesh.mesh_operators")
