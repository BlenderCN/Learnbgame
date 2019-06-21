import bpy
import bmesh
import os
from mathutils import Vector
from . decal import save_uuid, save_blend
from . modifier import add_displace, add_nrmtransfer
from . append import append_material
from . material import get_decal_textures, get_decalgroup_from_decalmat, get_parallaxgroup_from_decalmat, get_heightgroup_from_parallaxgroup, get_decal_texture_nodes
from . registration import get_prefs
from . pil import crop_image, scale_image, change_contrast, create_material2_mask
from . system import open_folder
from . mesh import loop_index_update
from . object import flatten
from . math import create_bbox, get_midpoint



def get_info_decal_geometry(context, scene, sel, debug=False):
    source_objs = []
    all_coords = []

    dg = context.evaluated_depsgraph_get()

    for obj in sel:
        scene.collection.objects.link(obj)
        dg.update()

        mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        source = bpy.data.objects.new(name=obj.name, object_data=mesh)
        source.matrix_world = obj.matrix_world

        scene.collection.objects.link(source)
        scene.collection.objects.unlink(obj)

        source.hide_render = False
        source.hide_viewport = False
        source.hide_select = False

        source_objs.append(source)
        all_coords += [source.matrix_world @ v.co for v in source.data.vertices]

    # create bounding box around selection
    coords, _, _ = create_bbox(coords=all_coords)

    # debug bbox
    if debug:
        for co in coords:
            empty = bpy.data.objects.new("empty", None)
            scene.collection.objects.link(empty)
            empty.location = co

    return source_objs, coords


def get_decal_source_objects(context, scene, sel, active, debug=False):
    source_objs = []
    all_coords = []
    new_active = None

    for obj in sel:
        source = obj.copy()
        source.data = obj.data.copy()

        scene.collection.objects.link(source)

        flatten(source)
        source.data.materials.clear()

        source.hide_render = False
        source.hide_viewport = False
        source.hide_select = False

        if obj == active:
            new_active = source

        source_objs.append(source)
        all_coords += [source.matrix_world @ v.co for v in source.data.vertices]


    # create bounding box around selection
    coords, _, _ = create_bbox(coords=all_coords)

    # debug bbox
    if debug:
        for co in coords:
            empty = bpy.data.objects.new("empty", None)
            scene.collection.objects.link(empty)
            empty.location = co


    return source_objs, new_active, coords


def create_decal_geometry(context, scene, coords, height):
    decal = bpy.data.objects.new("Decal", object_data=bpy.data.meshes.new(name="Decal"))
    scene.collection.objects.link(decal)

    location = get_midpoint(coords[4:])

    decal.location = location

    context.view_layer.objects.active = decal
    decal.select_set(True)

    # it's weird, but only by translating will the decal update properly, obj.data.update() and scene.update() have no effect
    bpy.ops.transform.translate(value=(0, 0, 0))

    # create decal geometry
    bm = bmesh.new()
    bm.from_mesh(decal.data)

    uvs = bm.loops.layers.uv.verify()


    # create verts and face
    verts = []

    for co in coords[4:]:
        v = bm.verts.new()
        v.co = decal.matrix_world.inverted() @ Vector(co)
        verts.append(v)

    face = bm.faces.new(verts)

    # update indices
    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.index_update()
    loop_index_update(bm)

    # create uvs
    for loop in face.loops:
        if loop.index == 0:
            loop[uvs].uv = (0, 0)
        elif loop.index == 1:
            loop[uvs].uv = (1, 0)
        elif loop.index == 2:
            loop[uvs].uv = (1, 1)
        elif loop.index == 3:
            loop[uvs].uv = (0, 1)


    bm.to_mesh(decal.data)

    # move the decal up slighlty to avoid bias issues when baking
    decal.matrix_world.translation.z += height * 0.01

    return decal, location


def create_info_decal_texture(context, dm, templatepath, bakepath, scene, decal, source_objs, bbox_coords, width, depth, padding):
    def bake(context, path, scene, decal, size, bake, bakename="", colorspace="sRGB", samples=1, supersample=2):
        image_width, image_height = size

        scene.cycles.samples = samples
        # context.view_layer.cycles.use_denoising = True

        # prepare for baking
        image = bpy.data.images.new("BakeImage", width=image_width, height=image_height)
        image.file_format = 'PNG'
        image.colorspace_settings.name = colorspace

        mat = bpy.data.materials.new(name="BakeMat")
        mat.use_nodes = True

        decal.data.materials.append(mat)

        node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        node.select = True
        mat.node_tree.nodes.active = node
        node.image = image

        if not bakename:
            bakename = bake.lower()

        bakepath = os.path.join(path, bakename + ".png")
        image.filepath = bakepath

        print(" » Baking decal %s map." % (bakename))

        bpy.ops.object.bake(type=bake, use_clear=True, use_selected_to_active=True, margin=0, normal_space='TANGENT')
        image.save()

        # remove
        bpy.data.materials.remove(mat, do_unlink=True)
        decal.data.materials.clear()

        bpy.data.images.remove(image, do_unlink=True)

        if supersample:
            scale_image(bakepath, 1 / supersample)

        return bakepath

    supersample = int(dm.bake_supersample)
    resolution = int(dm.bake_resolution)

    inspect = dm.bake_inspect

    # determine image size, used when packing for empty channels
    resolution = resolution * supersample if supersample else resolution


    ratio = width / depth
    size = (resolution, int(resolution / ratio)) if ratio >= 1 else (int(resolution * ratio), resolution)

    # add padding
    if padding != (0, 0):
        scalex = 1 + width / size[0] * padding[0]
        scaley = 1 + depth / size[1] * padding[1]

        bm = bmesh.new()
        bm.from_mesh(decal.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        bmesh.ops.scale(bm, vec=(scalex, scaley, 1), verts=bm.verts)

        bm.to_mesh(decal.data)
        bm.clear()

        # recalulate the size
        size = (int(size[0] * scalex), int(size[1] * scaley))


    textures = []

    for obj in source_objs:
        obj.select_set(True)

    # BAKE DIFFUSE

    scene.render.bake.use_pass_direct = False
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_pass_color = True

    textures.append(bake(context, bakepath, scene, decal, size, 'DIFFUSE', colorspace="sRGB", supersample=supersample))

    # BAKE ALPHA

    for obj in source_objs:
        obj.data.materials.clear()

    alphamat = append_material(templatepath, "EMISSIVE")
    mattemat = append_material(templatepath, "MATTE")

    for obj in source_objs:
        obj.data.materials.append(alphamat)
        obj.data.materials.append(mattemat)

    textures.append(bake(context, bakepath, scene, decal, size, "EMIT", "alpha", supersample=supersample))

    bpy.data.materials.remove(alphamat, do_unlink=True)
    bpy.data.materials.remove(mattemat, do_unlink=True)


    # remove source objs and bake scene
    for obj in source_objs:
        bpy.data.meshes.remove(obj.data, do_unlink=True)

    # remove bake world and delete bake scene
    bpy.data.worlds.remove(scene.world, do_unlink=True)

    bpy.ops.scene.delete()

    # open bakes folder
    if inspect:
        open_folder(bakepath)

    # return the texture paths and the proper image size

    return textures, tuple(int(s / supersample) for s in size) if supersample else size


def create_decal_textures(context, dm, templatepath, bakepath, scene, decal, active, source_objs, bbox_coords, width, depth):
    def flatten_alpha_normals(active, boundary):
        active.data.calc_normals_split()

        loop_normals = []
        for loop in active.data.loops:
            loop_normals.append(loop.normal)


        bm = bmesh.new()
        bm.from_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        # set sharps
        active.data.use_auto_smooth = True

        for e in bm.edges:
            if e.calc_face_angle(0) > active.data.auto_smooth_angle:
                e.smooth = False

        # get verts to set custom normals on
        verts = []

        for f in bm.faces:
            # look for faces pointing up in world space
            dot = round((active.matrix_world.to_3x3() @ f.normal).normalized().dot(Vector((0.0, 0.0, 1.0))), 6)

            if dot == 1:
                # then check of those faces are on z = 0 in local space
                if all([round(v.co[2], 6) == 0 for v in f.verts]):
                    if all([e.smooth for e in f.edges]):
                        if boundary:
                            if any([not e.is_manifold for e in f.edges]):
                                verts.extend(f.verts)
                        else:
                            verts.extend(f.verts)

        for v in verts:
            for loop in v.link_loops:
                loop_normals[loop.index] = Vector((0, 0, 1))

        bm.to_mesh(active.data)
        bm.clear()

        active.data.normals_split_custom_set(loop_normals)

    def create_panel_dups(scene, active, source_objs, width):
        dups = []

        for obj in source_objs:
            dup = active.copy()
            dup.data = active.data.copy()
            dup.matrix_world.translation.x += width
            scene.collection.objects.link(dup)
            dup.select_set(True)
            dups.append(dup)

            dup = active.copy()
            dup.data = active.data.copy()
            dup.matrix_world.translation.x -= width
            scene.collection.objects.link(dup)
            dup.select_set(True)
            dups.append(dup)

        return dups

    def bake(context, path, scene, decal, size, bake, bakename="", colorspace="Non-Color", samples=1, supersample=2, contrast=1, passimage=False):
        image_width, image_height = size

        scene.cycles.samples = samples
        # context.view_layer.cycles.use_denoising = True

        # prepare for baking
        image = bpy.data.images.new("BakeImage", width=image_width, height=image_height)
        image.file_format = 'PNG'
        image.colorspace_settings.name = colorspace

        mat = bpy.data.materials.new(name="BakeMat")
        mat.use_nodes = True

        decal.data.materials.append(mat)

        node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        node.select = True
        mat.node_tree.nodes.active = node
        node.image = image

        if not bakename:
            bakename = bake.lower()

        print(" » Baking decal %s map." % (bakename))

        bakepath = os.path.join(path, bakename + ".png")

        image.filepath = bakepath
        bpy.ops.object.bake(type=bake, use_clear=True, use_selected_to_active=True, margin=0, normal_space='TANGENT')

        # remove
        bpy.data.materials.remove(mat, do_unlink=True)
        decal.data.materials.clear()

        if passimage:
            return image

        else:
            image.save()

            if contrast != 1:
                change_contrast(bakepath, contrast)

            if supersample:
                scale_image(bakepath, 1 / supersample)

            bpy.data.images.remove(image, do_unlink=True)

            return bakepath

    def prepare_height_bake(templatepath, source_objs, active, coords, distance, debug=False):
        heightmat = append_material(templatepath, "POSITIONHEIGHT")

        for obj in source_objs:
            obj.data.materials.append(heightmat)

        active_z = active.matrix_world.translation.z
        min_z = coords[0][2]
        max_z = coords[4][2]

        distance_bottom = active_z - min_z
        distance_top = max_z - active_z

        distance_max = max([distance_bottom, distance_top])

        if distance and distance > distance_max:
            distance_max = distance

        if debug:
            print("active z:", active_z)
            print("min z:", min_z)
            print("max z:", max_z)
            print("distance bottom:", distance_bottom)
            print("distance top:", distance_top)
            print("distance max:", distance_max)

        node_scale = heightmat.node_tree.nodes.get("Scale")
        node_offset = heightmat.node_tree.nodes.get("Offset")

        if node_scale and node_offset:
            node_scale.inputs[1].default_value = 2 * distance_max
            node_offset.inputs[1].default_value = - active_z / 2 * distance_max

        return heightmat

    def create_curvature_map(context, path, scene, decal, size, supersample, curvaturewidth, panel, contrast=1):
        normal = bake(context, path, scene, decal, (size[0] * 3, size[1]) if panel else size, 'NORMAL', colorspace="Linear", supersample=supersample, passimage=True)

        # create curvatue map in compositing from baked normal map
        node_normal = context.scene.node_tree.nodes.get("Normal Map")
        node_normal.image = normal

        node_nrm2curv = context.scene.node_tree.nodes.get("Normal2Curvature")
        node_nrm2curv.inputs[1].default_value = curvaturewidth

        scene.render.resolution_x = normal.size[0]
        scene.render.resolution_y = normal.size[1]

        # set render output filename
        curvaturepath = os.path.join(path, "curvature.png")
        scene.render.filepath = curvaturepath

        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'BW'

        bpy.ops.render.render(write_still=True)

        # crop away curvature border and get back to single panel texture size
        if panel:
            crop_image(imagepath=scene.render.filepath, cropbox=(size[0], 0, 2 * size[0], scene.render.resolution_y))

        if contrast != 1:
            change_contrast(curvaturepath, contrast)

        if supersample:
            scale_image(scene.render.filepath, 1 / supersample)

        bpy.data.images.remove(normal, do_unlink=True)

        bpy.data.node_groups.remove(node_nrm2curv.node_tree, do_unlink=True)

        return curvaturepath

    def prepare_alpha_bake(templatepath, source_objs, active, boundary):
        alphamat = append_material(templatepath, "EMISSIVE")
        mattemat = append_material(templatepath, "MATTE")

        for obj in source_objs:
            obj.data.materials.append(alphamat)
            obj.data.materials.append(mattemat)

        if active:
            source_objs = [active]

        for obj in source_objs:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            for f in bm.faces:
                f.material_index = 0
                # look for faces pointing up in world space
                dot = round((obj.matrix_world.to_3x3() @ f.normal).normalized().dot(Vector((0.0, 0.0, 1.0))), 6)

                if dot == 1:
                    # then check of those faces are on z = 0 in local space
                    if all([round(v.co[2], 6) == 0 for v in f.verts]):
                        if boundary:
                            if any([not e.is_manifold for e in f.edges]):
                                f.material_index = 1
                        else:
                            f.material_index = 1


            bm.to_mesh(obj.data)
            bm.clear()

        return alphamat, mattemat

    def create_material2_map(path, context, size, supersample, scene, decal, active, source_objs, alphamat, mattemat):
        active.data.materials.clear()
        active.data.materials.append(alphamat)
        active.data.materials.append(mattemat)

        subsets = [obj for obj in source_objs if obj != active]

        for obj in subsets:
            obj.hide_viewport = True

        bm = bmesh.new()
        bm.from_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        seamedges = [e for e in bm.edges if e.seam]

        if seamedges:
            # get faces on the top
            for f in bm.faces:
                f.select = False

            northvert = sorted([v for v in bm.verts], key=lambda x: (active.matrix_world @ x.co).y, reverse=True)[0]

            face = northvert.link_faces[0]
            faces = []
            check = [face]

            while check:
                face = check[0]
                faces.append(face)

                # look for new faces across edges that aren't seams
                new_faces = [face for e in face.edges if not e.seam for face in e.link_faces if face not in check and face not in faces]

                check += new_faces
                check.remove(face)


            for f in bm.faces:
                if f in faces:
                    f.material_index = 0
                else:
                    f.material_index = 1

            bm.to_mesh(active.data)
            bm.clear()

            mat2path = bake(context, path, scene, decal, size, "EMIT", "material2", samples=1, supersample=supersample)

            for obj in subsets:
                obj.hide_viewport = False

        else:
            mat2path = os.path.join(path, "material2.png")
            create_material2_mask(mat2path, *(tuple(int(s / supersample) for s in size) if supersample else size))

        return mat2path

    supersample = int(dm.bake_supersample)
    supersamplealpha = dm.bake_supersamplealpha
    resolution = int(dm.bake_resolution)

    aosamples = int(dm.bake_aosamples)
    aocontrast = dm.bake_aocontrast

    curvaturewidth = dm.bake_curvaturewidth * supersample if supersample else dm.bake_curvaturewidth
    curvaturecontrast = dm.bake_curvaturecontrast

    heightdistance = dm.bake_heightdistance

    limit_alpha_to_active = dm.bake_limit_alpha_to_active
    limit_alpha_to_boundary = dm.bake_limit_alpha_to_boundary
    flatten_normals = dm.bake_flatten_alpha_normals
    inspect = dm.bake_inspect
    panel = dm.create_decaltype == "PANEL"
    maskmat2 = dm.bake_maskmat2

    # determine image size, used when packing for empty channels
    resolution = resolution * supersample if supersample else resolution

    ratio = width / depth
    size = (resolution, int(resolution / ratio)) if ratio >= 1 else (int(resolution * ratio), resolution)

    textures = []

    for obj in source_objs:
        obj.select_set(True)


    # flatten alpha normals
    if flatten_normals:
        flatten_alpha_normals(active, boundary=limit_alpha_to_boundary)

    # add reapeating geo to the left and right for panel ao and curvature bakes
    if panel:
        paneldups = create_panel_dups(scene, active, source_objs, width)


    # BAKE AO

    # textures.append(bake(context, bakepath, scene, decal, size, 'AO', colorspace="Non-Color", samples=samples, supersample=supersample))
    textures.append(bake(context, bakepath, scene, decal, size, 'AO', colorspace="sRGB", samples=aosamples, supersample=supersample, contrast=aocontrast))


    # BAKE NORMAL

    textures.append(bake(context, bakepath, scene, decal, size, 'NORMAL', supersample=supersample))


    # BAKE HEIGHT (position based)

    heightmat = prepare_height_bake(templatepath, source_objs, active, bbox_coords, heightdistance, debug=False)

    textures.append(bake(context, bakepath, scene, decal, size, "EMIT", "height", supersample=supersample))

    for obj in source_objs:
        obj.data.materials.clear()

    bpy.data.materials.remove(heightmat, do_unlink=True)


    # CREATE CURVATURE

    if panel:
        decal.scale.x = 3

    textures.append(create_curvature_map(context, bakepath, scene, decal, size, supersample, curvaturewidth, panel, contrast=curvaturecontrast))

    if panel:
        decal.scale.x = 1

        for obj in paneldups:
            bpy.data.meshes.remove(obj.data, do_unlink=True)


    # BAKE ALPHA

    alphamat, mattemat = prepare_alpha_bake(templatepath, source_objs, active=active if limit_alpha_to_active else False, boundary=limit_alpha_to_boundary)

    textures.append(bake(context, bakepath, scene, decal, size if supersamplealpha or not supersample else tuple(int(s / supersample) for s in size), "EMIT", "alpha", supersample=supersample if supersamplealpha else 0))


    # BAKE SUBSET MASK

    if len(source_objs) > 1:
        active.data.materials.pop(index=0)

        textures.append(bake(context, bakepath, scene, decal, size, "EMIT", "subset", supersample=supersample))


    # BAKE/CREATE MATERIAL2 MASK

    if panel and maskmat2:
        textures.append(create_material2_map(bakepath, context, size, supersample, scene, decal, active, source_objs, alphamat, mattemat))


    bpy.data.materials.remove(alphamat, do_unlink=True)
    bpy.data.materials.remove(mattemat, do_unlink=True)


    # remove source objs and bake scene
    for obj in source_objs:
        bpy.data.meshes.remove(obj.data, do_unlink=True)

    bpy.data.scenes.remove(scene, do_unlink=True)


    # open bakes folder
    if inspect:
        open_folder(bakepath)

    # return the texture paths and the proper image size

    return textures, tuple(int(s / supersample) for s in size) if supersample else size


def create_decal_blend(context, templatepath, decalpath, packed, decaltype, decalobj=None, size=None, uuid=''):
    bpy.ops.scene.new(type='NEW')
    decalscene = context.scene
    decalscene.name = "Decal Asset"

    # link existing decalobj to collection
    if decalobj:
        decalscene.collection.objects.link(decalobj)

        # scale the decal mesh according to the texture res, it's already in proportion
        factor = size[0] / decalobj.dimensions[0] / 1000

        bm = bmesh.new()
        bm.from_mesh(decalobj.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        bmesh.ops.scale(bm, vec=(factor, factor, factor), verts=bm.verts)

        bm.to_mesh(decalobj.data)
        bm.clear()

        decalobj.location = (0, 0, 0)

    # create new decalobj
    else:
        bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), rotation=(0, 0, 0))

        decalobj = context.active_object
        size = packed['SIZE']

        # scale the plane geo according to the image size
        bm = bmesh.new()
        bm.from_mesh(decalobj.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        bmesh.ops.scale(bm, vec=(size[0] / 2000, size[1] / 2000, 1), verts=bm.verts)

        bm.to_mesh(decalobj.data)
        bm.clear()


    # set isdecal prop
    decalobj.DM.isdecal = True

    # displace
    add_displace(decalobj)

    # normal transfer
    add_nrmtransfer(decalobj)


    # determine basic props
    library = "LIBRARY"
    basename = "DECAL"

    decalmatname = "%s_%s" % (library, basename)
    decalname = decalmatname

    # append decal material
    decalmat = append_material(templatepath, "TEMPLATE_%s" % decaltype.upper())

    if decalmat:
        decalobj.data.materials.append(decalmat)

        decalmatname = "%s_%s" % (library, basename)
        decalname = decalmatname

        # set the decal props and names
        decalobj.name = decalname
        decalobj.data.name = decalname
        decalmat.name = decalmatname

        textures = get_decal_textures(decalmat)

        for component in [decalobj] + [decalmat] + list(textures.values()):
            component.DM.uuid = uuid
            component.DM.decaltype = decaltype
            component.DM.decallibrary = library
            component.DM.decalname = decalname
            component.DM.decalmatname = decalmatname
            component.DM.creator = get_prefs().decalcreator

        decalgroup = get_decalgroup_from_decalmat(decalmat)
        decalgroup.name = "%s.%s" % (decaltype.lower(), decalmatname)
        decalgroup.node_tree.name = "%s.%s" % (decaltype.lower(), decalmatname)

        parallaxgroup = get_parallaxgroup_from_decalmat(decalmat)

        if parallaxgroup:
            parallaxgroup.name = "parallax.%s" % (decalmatname)
            parallaxgroup.node_tree.name = "parallax.%s" % (decalmatname)
            decalmat.DM.parallaxnodename = "parallax.%s" % (decalmatname)

            heightgroups = get_heightgroup_from_parallaxgroup(parallaxgroup, getall=True)

            if heightgroups:
                for idx, hg in enumerate(heightgroups):
                    if idx == 0:
                        hg.node_tree.name = "height.%s" % (decalmatname)

                    hg.name = "height.%s" % (decalmatname)

        else:
            decalmat.DM.parallaxnodename = ""


        imgnodes = get_decal_texture_nodes(decalmat, height=True)

        for textype, node in imgnodes.items():
            node.name = "%s_%s" % (decalmatname, textype.lower())

            if textype != "HEIGHT":
                node.image.name = ".%s_%s" % (decalmatname, textype.lower())
                node.image.filepath = packed[textype]

        # create uuid file
        save_uuid(decalpath, uuid)

        # write the new blend file
        save_blend(decalobj, decalpath, decalscene)

    return decalobj, decalmat, size


def pack_textures(dm, decalpath, textures, size=None, crop=False, padding=0):
    ao = None
    curv = None
    height = None

    color = None
    nrm = None
    alpha = None

    subset = None
    mat2 = None

    diffuse = None

    for path in textures:
        basename = os.path.splitext(os.path.basename(path))[0]

        if basename == "ao":
            ao = path

        elif basename == "curvature":
            curv = path

        elif basename == "height":
            height = path

        elif basename == "normal":
            nrm = path

        elif basename == "alpha":
            alpha = path

        elif basename == "subset":
            subset = path

        elif basename == "material2":
            mat2 = path

        elif basename == "diffuse":
            diffuse = path

        elif dm.create_decaltype == 'INFO':
            color = path

    from PIL import Image, ImageFile


    packed = {}

    if ao and curv and height:
        ao = Image.open(ao).convert('L')
        curv = Image.open(curv)
        height = Image.open(height).convert('L')

        # debug output to learn about "size masmatch" errors when merging
        print("ao size:", ao.size)
        print("curv size:", curv.size)
        print("height size:", height.size)

        ao_curv_height = Image.merge("RGB", (ao, curv, height))
        ao_curv_height_path = os.path.join(decalpath, "ao_curv_height.png")
        ao_curv_height.save(ao_curv_height_path)

        packed['AO_CURV_HEIGHT'] = ao_curv_height_path

    if nrm and alpha:
        nrm = Image.open(nrm)
        alpha = Image.open(alpha).convert('L')

        # debug output to learn about "size masmatch" errors when merging
        print("nrm size:", nrm.size)
        print("alpha size:", alpha.size)

        nrm_alpha = Image.merge("RGBA", (*nrm.split(), alpha))
        nrm_alpha_path = os.path.join(decalpath, "nrm_alpha.png")
        nrm_alpha.save(nrm_alpha_path)

        packed['NRM_ALPHA'] = nrm_alpha_path

    if subset or dm.create_decaltype == "PANEL":
        empty = Image.new("L", size, 0)
        subset = Image.open(subset).convert('L') if subset else empty
        mat2 = Image.open(mat2).convert('L') if mat2 else empty

        # debug output to learn about "size masmatch" errors when merging
        print("subset size:", subset.size)
        print("mat2 size:", mat2.size)
        print("empty size:", empty.size)

        masks = Image.merge("RGB", (subset, mat2, empty))
        masks_path = os.path.join(decalpath, "masks.png")
        masks.save(masks_path)

        packed['MASKS'] = masks_path

    if diffuse and alpha:
        diffuse = Image.open(diffuse)
        alpha = Image.open(alpha).convert('L')

        # debug output to learn about "size masmatch" errors when merging
        print("diffuse size:", diffuse.size)
        print("alpha size:", alpha.size)

        color_alpha = Image.merge("RGBA", (*diffuse.split(), alpha))
        color_alpha_path = os.path.join(decalpath, "color_alpha.png")
        color_alpha.save(color_alpha_path)

        packed['COLOR_ALPHA'] = color_alpha_path

    if color:
        img = Image.open(color)

        # see https://github.com/python-pillow/Pillow/issues/1510
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        # TODO: jpgs still fail (all?), because they come out black. confirm this is also happenign on windows and if so, remove the ability to use jpgs

        if img.mode != 'RGBA':
            img.convert('RGBA')

        color_alpha_path = os.path.join(decalpath, "color_alpha.png")

        if crop and padding:
            size = crop_image(img, imagepath=color_alpha_path, padding=padding)

            # for info decals, also add the size to the packed dict
            packed['SIZE'] = size

        else:
            img.save(color_alpha_path)

            # for info decals, also add the size to the packed dict
            packed['SIZE'] = img.size

        packed['COLOR_ALPHA'] = color_alpha_path


    decaltype = 'PANEL' if dm.create_decaltype == 'PANEL' else 'INFO' if dm.create_decaltype == 'INFO' else 'SUBSET' if subset else 'SIMPLE'

    return packed, decaltype
