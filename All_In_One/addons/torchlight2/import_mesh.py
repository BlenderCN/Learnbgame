import re
from collections import deque

from .utils import *
from .matlib import matlib

# TODO
# - option to create only one texture per image file
# - improve material parsing
# - refactor and cleanup

def edge_hash(edge):
    # limited to 32 bit indices
    return (edge[0] + (edge[1] << 32) if edge[0] < edge[1] else
            edge[1] + (edge[0] << 32))

def create_material(mat_name, tex_img=None, use_alpha=False):
    mat = (bpy.data.materials.get(mat_name) or
           bpy.data.materials.new(mat_name))

    tex = (bpy.data.textures.get("tex_" + mat_name) or
           bpy.data.textures.new("tex_" + mat_name, "IMAGE"))

    tex_slot = (mat.texture_slots[0] or
                mat.texture_slots.add())

    tex_slot.texture = tex
    tex_slot.texture_coords = "UV"
    tex_slot.uv_layer = "UV"
    mat.use_shadeless = True

    if tex_img:
        tex.image = tex_img

    if use_alpha:
        mat.use_transparency = True
        mat.transparency_method = "Z_TRANSPARENCY"
        mat.alpha = 0.0
        tex_slot.use_map_alpha = True

    return mat

# Axis Conversion from Ogre to Blender
# x=x, y=-z, z=y
# u=u, v=1-v

class Vertex(object):
    __slots__ = ("index", "position", "normal", "texcoord", "color_diffuse", "color_specular")

    def __init__(self, index):
        self.index          = index
        self.position       = None
        self.normal         = None
        self.color_diffuse  = None
        self.color_specular = None
        self.texcoord       = None

    def set_position(self, domElem):
        self.position = Vector(getVecAttr(domElem, "xyz"))

    def set_normal(self, domElem):
        self.normal = Vector(getVecAttr(domElem, "xyz"))

    def set_colour_diffuse(self, domElem):
        self.color_diffuse = tuple(float(val)
            for val in domElem.getAttribute("value").split())

    def set_colour_specular(self, domElem):
        self.color_specular = Color(float(val)
            for val in domElem.getAttribute("value").split())

    def set_texcoord(self, domElem):
        attributes = "uvwx"
        dim = sum(domElem.hasAttribute(attr) for attr in attributes)
        co = Vector(getVecAttr(domElem, attributes[:dim]))

        if not self.texcoord: self.texcoord = [co]
        else:                 self.texcoord.append(co)


class Submesh(object):
    def __init__(self, domElem, offset):
        self.offset = offset

        if domElem.tagName == "submesh":
            if (domElem.hasAttribute("usesharedvertices") and
                domElem.getAttribute("usesharedvertices") == "true"):
                offset = 0

            faceElements = find(domElem, "faces")
            if faceElements:
                self.facecount = getIntAttr(faceElements, "count")
                self.faces = [
                    [getIntAttr(faceElem, attr) + offset for attr in ("v1", "v2", "v3")]
                        for faceElem in child_iter(faceElements, "face")]

            self.material = domElem.getAttribute("material")
            geoElem = find(domElem, "geometry")

        elif domElem.tagName == "sharedgeometry":
            geoElem = domElem
            self.faces = None
            self.facecount = 0
            self.material = "sharedgeometry"

        else:
            raise ValueError("Invalid tagName %s" % domElem.tagName)

        if geoElem:
            self.vertcount = getIntAttr(geoElem, "vertexcount")
            self.vertices = [Vertex(i + offset) for i in range(self.vertcount)]

            for vertexbuffer in child_iter(geoElem, "vertexbuffer"):
                for i, vertex in enumerate(child_iter(vertexbuffer, "vertex")):
                    for elem in child_iter(vertex):
                        if elem.tagName in ("tangent", "binormal"): continue
                        getattr(self.vertices[i], "set_" + elem.tagName)(elem)

        else:
            self.vertcount = 0
            self.vertices  = None

        baElements = find(domElem, "boneassignments")
        if baElements:
            self.boneassignments = deque()
            for vbaElem in child_iter(baElements, "vertexboneassignment"):
                self.boneassignments.append((
                    getIntAttr(vbaElem, "vertexindex") + offset,
                    getIntAttr(vbaElem, "boneindex"),
                    getFloatAttr(vbaElem, "weight")
                    ))
        else:
            self.boneassignments = None

    def has_vert(self, index):
        return self.offset <= index < self.offset + self.vertcount

    def get_vert(self, index):
        return self.vertices[index - self.offset]


class MeshConverter(object):
    def __init__(self, mesh_input, xml_dir, skel_input=None, mat_file=None, use_existing_xml=False):
        #==========================================================================================
        #-----------------------------------CONVERT TO XML-----------------------------------------
        #==========================================================================================

        self.stem = os.path.basename(mesh_input).rsplit(".")[0]
        xml_output = os.path.join(xml_dir, self.stem + "_mesh.xml")

        convert_to_xml(mesh_input, xml_output, overwrite=not use_existing_xml)
        meshElem = xml.dom.minidom.parse(xml_output).documentElement

        #==========================================================================================
        #--------------------------------------READ SKELETON---------------------------------------
        #==========================================================================================

        sklLinkElem = find(meshElem, "skeletonlink")
        if sklLinkElem:
            self.skeletonlink = sklLinkElem.getAttribute("name")
            skel_input = skel_input or os.path.join(os.path.dirname(mesh_input), self.skeletonlink.upper())
            xml_output = os.path.join(xml_dir, os.path.basename(skel_input).rsplit('.')[0] + "_skel.xml")

            convert_to_xml(skel_input, xml_output, overwrite=not use_existing_xml)

            self.bones = deque()
            self.bone_dict = dict()

            skelElem = xml.dom.minidom.parse(xml_output).documentElement
            boneElements = find(skelElem, "bones")
            for boneElem in child_iter(boneElements, "bone"):
                bone = Bone(boneElem)
                self.bones.append(bone)
                self.bone_dict[bone.name] = bone

            hierarchyElem = find(skelElem, "bonehierarchy")
            for relElem in child_iter(hierarchyElem, "boneparent"):
                child  = self.bone_dict[relElem.getAttribute("bone")]
                parent = self.bone_dict[relElem.getAttribute("parent")]
                child.parent = parent
                parent.children_count += 1

            bone_list = self.bones
            self.bones = [None] * len(bone_list)
            for bone in bone_list:
                self.bones[bone.id] = bone
                # bone.name = bone.name.replace(" ", "_")
                bone.children = [None] * bone.children_count

            for bone in self.bones:
                if bone.parent:
                    bone.parent.children[bone.parent.children.index(None)] = bone
        else:
            self.bones = None

        #==========================================================================================
        #----------------------------------------READ MESH-----------------------------------------
        #==========================================================================================

        sharedGeoElem = find(meshElem, "sharedgeometry")
        self.submeshes = deque()

        if sharedGeoElem:
            self.sharedgeometry = Submesh(sharedGeoElem, 0)
            self.submeshes.append(self.sharedgeometry)
            offset = self.sharedgeometry.vertcount
        else:
            offset = 0

        for domElem in child_iter(find(meshElem, "submeshes"), "submesh"):
            sm = Submesh(domElem, offset)
            self.submeshes.append(sm)
            offset += sm.vertcount

        baElements = find(meshElem, "boneassignments")
        if baElements:
            self.boneassignments = deque()
            for vbaElem in child_iter(baElements, "vertexboneassignment"):
                self.boneassignments.append((
                    getIntAttr(vbaElem, "vertexindex"),
                    getIntAttr(vbaElem, "boneindex"),
                    getFloatAttr(vbaElem, "weight")
                    ))
        else:
            self.boneassignments = None

        self.submeshes = tuple(self.submeshes)

        #==========================================================================================
        #--------------------------------------READ MATERIALS--------------------------------------
        #==========================================================================================

        self.materials = tuple(sm.material for sm in self.submeshes if not sm.material == "sharedgeometry")

        self.re_material = re.compile("material (?P<name>.*)$")
        self.re_alpha    = re.compile("\\t*scene_blend alpha_blend$")
        self.re_texture  = re.compile("\\t*texture (?P<file>.*)$")

        if not mat_file:
            mat_file = mesh_input.rsplit(".")[0] + ".MATERIAL"

        if os.path.exists(mat_file):
            self.tex_links = deque()
            self.read_material(mat_file)
        else:
            mat_files = matlib.get_files(mesh_input, self.materials)
            if mat_files:
                self.tex_links = deque()
                for mat_file in mat_files:
                    self.read_material(mat_file)
            else:
                print("No *.MATERIAL Files found")
                self.tex_links = None

    def read_material(self, mat_file):
        dir_input = os.path.dirname(mat_file)
        print("Open Material:", mat_file)
        mat_name = ""
        use_alpha = False

        with open(mat_file, 'r', encoding="utf8") as fobj:
            for line in fobj:
                mo = self.re_material.match(line)
                if mo:
                    mat_name = mo.group("name")
                    if mat_name not in self.materials:
                        mat_name = ""
                    print("Matched material", mat_name)

                if mat_name:
                    mo = self.re_alpha.match(line)
                    if mo:
                        use_alpha = True
                        mo = None

                    mo = self.re_texture.match(line)
                    if mo:
                        tex_file = os.path.join(dir_input, mo.group("file").upper().replace("\\", "/"))
                        tex_file = os.path.normpath(tex_file)
                        self.tex_links.append((mat_name, tex_file, use_alpha))
                        mat_name = ""
                        use_alpha = False
                        print("Added texture link", tex_file)

    def __del__(self):
        if self.bones:
            # break references
            for bone in self.bones:
                bone.parent = None
                bone.children = None

    def get_vert(self, current, index):
        if current.has_vert(index): return current.get_vert(index)

        for sm in self.submeshes:
            if sm.has_vert(index):
                return sm.get_vert(index)
        else:
            raise ValueError("Vertex %d not Found" % index)

    def create_mesh(self):
        name = self.stem
        mesh = bpy.data.meshes.new(name)
        mesh.uv_textures.new("UV")

        materials = []
        for sm in self.submeshes:
            if not sm.material == "sharedgeometry" and not sm.material in materials:
                materials.append(sm.material)

        if self.tex_links:
            tex_images  = [None] * len(materials)
            flags_alpha = [None] * len(materials)

            for mat, tex_file, use_alpha in self.tex_links:
                if mat in materials:
                    if not os.path.exists(tex_file): tex_file = tex_file.rsplit(".")[0] + ".DDS"
                    if not os.path.exists(tex_file): continue

                    index = materials.index(mat)
                    tex_images[index] = (
                        bpy.data.images.get(os.path.basename(tex_file)) or
                        bpy.data.images.load(tex_file))
                    flags_alpha[index] = use_alpha

        total_verts = sum(sm.vertcount for sm in self.submeshes)
        total_faces = sum(sm.facecount for sm in self.submeshes)

        mesh.vertices.add(total_verts)
        mesh.loops.add(total_faces * 3)
        mesh.polygons.add(total_faces)

        edge_dict = dict()
        loops = [None] * (total_faces * 3)

        offset = 0
        edge_index = 0
        loop_index = 0

        for sm in self.submeshes:
            if sm.vertices:
                for v in sm.vertices:
                    mv = mesh.vertices[v.index]
                    mv.co = v.position.copy()
                    mv.normal = v.normal.copy()

            if sm.faces:
                mat_index = materials.index(sm.material)

                for i, f in enumerate(sm.faces):
                    edges = (
                        (f[0], f[1]),
                        (f[1], f[2]),
                        (f[2], f[0])
                    )

                    for j, e in enumerate(edges):
                        eh = edge_hash(e)
                        val = edge_dict.get(eh)
                        if val is None:
                            edge_dict[eh] = val = (edge_index, e)
                            edge_index += 1

                        loop = mesh.loops[loop_index + j]
                        loop.vertex_index = f[j]
                        loop.edge_index = val[0]

                    p = mesh.polygons[i + offset]
                    p.loop_start = loop_index
                    p.loop_total = 3
                    p.vertices = f
                    p.use_smooth = True
                    p.material_index = mat_index

                    for j in range(3):
                        vert = self.get_vert(sm, f[j])
                        loops[loop_index + j] = vert

                    loop_index += 3
            offset += sm.facecount

        mesh.edges.add(len(edge_dict))
        for val in edge_dict.values():
            mesh.edges[val[0]].vertices = val[1]

        # retrieve the uv_layer after the geometry has been added
        # otherwise blender will crash
        uv_layer = mesh.uv_layers["UV"]
        for i, v in enumerate(loops):
            if v and v.texcoord:
                co = v.texcoord[0].copy()
                co.y = 1.0 - co.y
                uv_layer.data[i].uv = co

        for i, mat in enumerate(materials):
            tex_img   =  tex_images[i] if self.tex_links else None
            use_alpha = flags_alpha[i] if self.tex_links else None
            mesh.materials.append(create_material(mat, tex_img, use_alpha))

        obj = bpy.data.objects.new(name, mesh)
        obj.rotation_euler = Euler((math.pi / 2.0, 0.0, 0.0))

        if self.bones:
            obj['skeletonlink'] = self.skeletonlink
            self.modifier = obj.modifiers.new("Armature", "ARMATURE")
            bone_count = len(self.bones)
            vertex_groups = [obj.vertex_groups.new(bone.name) for bone in self.bones]

            for sm in self.submeshes:
                if sm.boneassignments:
                    for vi, bi, weight in sm.boneassignments:
                        # safety check
                        # some wardrobe meshes link to skeleton files
                        # with missing bones
                        if bi < bone_count:
                            vertex_groups[bi].add((vi,), weight, "ADD")

            if self.boneassignments:
                for vi, bi, weight in self.boneassignments:
                    if bi < bone_count:
                        vertex_groups[bi].add((vi,), weight, "ADD")

        bpy.context.scene.objects.link(obj)
        return obj, mesh

    def create_armature(self, bone_length_default):
        if not self.bones: return

        arm = bpy.data.armatures.new(self.stem)
        obj = bpy.data.objects.new("Arma_" + self.stem, arm)
        bpy.context.scene.objects.link(obj)

        ZERO  = Vector()
        VEC_X = Vector((1.0, 0.0, 0.0))
        VEC_Y = Vector((0.0, 1.0, 0.0))
        VEC_Z = Vector((0.0, 0.0, 1.0))
        QUAT_ID  = Quaternion((1.0, 0.0, 0.0, 0.0))

        def create_edit_bones(parent, bone_data, pos, quat):
            pos = pos + quat * bone_data.position
            quat = quat * bone_data.rotation

            eb = arm.edit_bones.new(bone_data.name)
            eb.head = pos.copy()
            eb.parent = parent
            eb.tail = pos + bone_length_default * (quat * VEC_X)
            eb.align_roll(quat * VEC_Z)

            for child in bone_data.children:
                create_edit_bones(eb, child, pos, quat)

        def no_parent(bone): return bone.parent is None
        def no_tag(eb): return not eb.name.startswith("tag")

        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")

        for root in filter(no_parent, self.bones):
            create_edit_bones(None, root, ZERO, QUAT_ID)

        for eb in arm.edit_bones:
            if len(eb.children) == 1:
                child = eb.children[0]
            elif sum(1 for child in filter(no_tag, eb.children)) == 1:
                child = next(filter(no_tag, eb.children))
            else:
                continue

            head_to_head = child.head - eb.head
            projection = head_to_head.project(eb.y_axis)
            if eb.y_axis.dot(projection) > 5e-2:
                eb.tail = eb.head + projection

        for eb in arm.edit_bones:
            for child in eb.children:
                if (eb.tail - child.head).magnitude < 5e-4:
                    child.use_connect = True

        bpy.ops.object.mode_set(mode="OBJECT")

        arm['tl2_id'] = tuple(bone.name for bone in self.bones)

        obj.show_x_ray = True
        obj.rotation_euler = Euler((math.pi / 2.0, 0.0, 0.0))
        if hasattr(self, "modifier"): self.modifier.object = obj
        return obj, arm
