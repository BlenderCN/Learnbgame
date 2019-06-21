import os

import bmesh
import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
)
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper, ExportHelper

from .utils import mqo_file as mqo
from .utils.bl_class_registry import BlClassRegistry
from .utils import compatibility as compat


MQO_TO_BLENDER_PROJECTION_TYPE = {0: 'BOX', 1: 'FLAT', 2: 'TUBE', 3: 'SPHERE'}
BLENDER_TO_MQO_PROJECTION_TYPE = {'BOX': 0, 'FLAT': 1, 'TUBE': 2, 'SPHERE': 3}
MQO_TO_BLENDER_MIRROR_TYPE = {0: 'NONE', 1: 'SEPARATE', 2: 'CONNECT'}
MQO_TO_BLENDER_MIRROR_AXIS_INDEX = {1: 0, 2: 1, 4: 2}


def get_outermost_verts(bm):
    return [v for v in bm.verts if len(v.link_faces) != len(v.link_edges)]


def import_material_v279(mqo_mtrl, filepath):
    # construct material
    new_mtrl = bpy.data.materials.new(mqo_mtrl.name)
    new_mtrl.diffuse_color = Vector(mqo_mtrl.color[0:3])
    new_mtrl.diffuse_intensity = mqo_mtrl.diffuse
    new_mtrl.specular_color = Vector(mqo_mtrl.color[0:3])
    new_mtrl.specular_intensity = mqo_mtrl.specular
    new_mtrl.emit = mqo_mtrl.emissive
    new_mtrl.ambient = mqo_mtrl.ambient

    new_image = None
    if mqo_mtrl.texture_map is not None:
        # open image
        image_path = "{}/{}".format(os.path.dirname(filepath),
                                    mqo_mtrl.texture_map)
        new_image = bpy.data.images.load(image_path)

    return {"material": new_mtrl, "image": new_image}


def import_material_v280(mqo_mtrl, filepath):
    # construct material
    new_mtrl = bpy.data.materials.new(mqo_mtrl.name)
    new_mtrl.use_nodes = True
    output_node = new_mtrl.node_tree.nodes["Material Output"]

    # remove unused nodes
    nodes_to_remove = [n for n in new_mtrl.node_tree.nodes if n != output_node]
    for n in nodes_to_remove:
        new_mtrl.node_tree.nodes.remove(n)

    new_image = None
    if mqo_mtrl.texture_map is not None:
        # open image
        image_path = "{}/{}".format(os.path.dirname(filepath),
                                    mqo_mtrl.texture_map)
        new_image = bpy.data.images.load(image_path)

        # make texture node
        texture_node = new_mtrl.node_tree.nodes.new("ShaderNodeTexImage")
        texture_node.image = new_image
        texture_node.projection = MQO_TO_BLENDER_PROJECTION_TYPE[
            mqo_mtrl.projection_type]
        new_mtrl.node_tree.links.new(output_node.inputs["Surface"],
                                     texture_node.outputs["Color"])
    else:
        # make specular node
        specular_node = new_mtrl.node_tree.nodes.new("ShaderNodeEeveeSpecular")
        specular_node.inputs["Base Color"].default_value = mqo_mtrl.color
        specular_node.inputs["Specular"].default_value = [
            mqo_mtrl.specular, mqo_mtrl.specular, mqo_mtrl.specular,
            mqo_mtrl.specular
        ]
        specular_node.inputs["Emissive Color"].default_value = [
            mqo_mtrl.emissive, mqo_mtrl.emissive, mqo_mtrl.emissive,
            mqo_mtrl.emissive
        ]
        new_mtrl.node_tree.links.new(output_node.inputs["Surface"],
                                     specular_node.outputs["BSDF"])

    return {"material": new_mtrl, "image": new_image}


def import_material(mqo_mtrl, filepath):
    if compat.check_version(2, 80, 0) >= 0:
        return import_material_v280(mqo_mtrl, filepath)
    else:
        return import_material_v279(mqo_mtrl, filepath)


def import_materials(mqo_file, filepath, exclude_materials):
    materials_imported = []
    for mqo_mtrl in mqo_file.get_materials():
        if mqo_mtrl.name in exclude_materials:
            materials_imported.append({"material": None, "image": None})
        else:
            materials_imported.append(import_material(mqo_mtrl, filepath,))
    return materials_imported


def import_object(mqo_obj, materials):
    # construct object
    new_mesh = bpy.data.meshes.new(mqo_obj.name)
    new_obj = bpy.data.objects.new(mqo_obj.name, new_mesh)
    new_obj.location = Vector(mqo_obj.translation)
    new_obj.rotation_euler = Vector(mqo_obj.rotation)
    new_obj.scale = Vector(mqo_obj.scale)
    if compat.check_version(2, 80, 0) >= 0:
        bpy.context.scene.collection.objects.link(new_obj)
        bpy.context.view_layer.objects.active = new_obj
        new_obj.select_set(True)
    else:
        bpy.context.scene.objects.link(new_obj)
        bpy.context.scene.objects.active = new_obj
        new_obj.select = True

    # construct material
    for mtrl in materials:
        bpy.ops.object.material_slot_add()
        if mtrl is not None:
            new_obj.material_slots[len(new_obj.material_slots) - 1]\
                .material = mtrl["material"]

    # construct mesh
    new_mesh = bpy.context.object.data
    bm = bmesh.new()

    bm_verts = [bm.verts.new(v) for v in mqo_obj.get_vertices()]
    bm_faces = []
    mqo_faces = mqo_obj.get_faces(uniq=True)

    # create UV map
    has_uvmap = False
    for face in mqo_faces:
        if face.uv_coords is not None:
            has_uvmap = True
    uv_layer = None
    if has_uvmap:
        if bm.loops.layers.uv.items():
            uv_layer = bm.loops.layers.uv[0]
        else:
            uv_layer = bm.loops.layers.uv.new()

    for face in mqo_faces:
        face_verts = []

        # create face
        for j in range(face.ngons):
            face_verts.append(bm_verts[face.vertex_indices[j]])
        bm_face = bm.faces.new(face_verts)

        # set UV if exists
        if face.uv_coords is not None:
            for j in range(face.ngons):
                bm_face.loops[j][uv_layer].uv = face.uv_coords[j]

        bm_faces.append(bm_face)

    bm.to_mesh(new_mesh)
    bm.free()

    # object mode -> edit mode
    bpy.ops.object.editmode_toggle()

    mtrl_map = {}
    for i, face in enumerate(mqo_faces):
        mtrl_idx = face.material
        if mtrl_idx is None:
            continue
        if mtrl_idx not in mtrl_map:
            mtrl_map[mtrl_idx] = []
        mtrl_map[mtrl_idx].append(i)

    for mtrl_idx in mtrl_map:
        bm = bmesh.from_edit_mesh(new_obj.data)
        bm.faces.ensure_lookup_table()
        # set material
        for face in bm.faces:
            face.select = False
        for face_idx in mtrl_map[mtrl_idx]:
            bm.faces[face_idx].select = True
            if has_uvmap and compat.check_version(2, 80, 0) < 0:
                tex_layer = bm.faces.layers.tex.verify()
                bm.faces[face_idx][tex_layer].image = \
                    materials[mtrl_idx]["image"]
        bmesh.update_edit_mesh(new_obj.data)
        new_obj.active_material_index = mtrl_idx
        # if material is not imported, this means to assign None
        new_obj.active_material = materials[mtrl_idx]["material"]
        bpy.ops.object.material_slot_assign()

    bm = bmesh.from_edit_mesh(new_obj.data)
    bm.faces.ensure_lookup_table()
    for face in bm.faces:
        face.select = False
    bmesh.update_edit_mesh(new_obj.data)

    # make vertices and faces for mirror connection
    # pylint: disable=too-many-nested-blocks
    if mqo_obj.mirror is not None:
        if MQO_TO_BLENDER_MIRROR_TYPE[mqo_obj.mirror] == 'CONNECT':
            outermost_verts = get_outermost_verts(bm)

            # make vertices aligned to axis
            axis_aligned_verts = {}
            for ov in outermost_verts:
                new_vert = bm.verts.new(ov.co)
                new_vert.co[MQO_TO_BLENDER_MIRROR_AXIS_INDEX[
                    mqo_obj.mirror_axis]] = 0.0
                axis_aligned_verts[ov] = new_vert

            # make ordered outermost vertices
            rest = outermost_verts
            link_groups = []
            while len(rest) != 0:
                links = []
                cur_vert = rest[0]
                first_vert = rest[0]
                is_vert_loop = False
                has_no_link_edge = False
                is_first_time = True
                while True:
                    rest.remove(cur_vert)
                    # find adjacent vertices
                    for e in cur_vert.link_edges:
                        next_vert = e.other_vert(cur_vert)
                        if next_vert in rest:
                            links.append([cur_vert, next_vert])
                            cur_vert = next_vert
                            break
                    else:  # not found, then check if this is a vertex loop
                        for e in cur_vert.link_edges:
                            next_vert = e.other_vert(cur_vert)
                            if next_vert == first_vert and not is_first_time:
                                is_vert_loop = True
                                links.append([cur_vert, first_vert])
                                break
                        else:  # vertex has no linked edge
                            has_no_link_edge = True
                    is_first_time = False
                    if len(rest) == 0 or is_vert_loop or has_no_link_edge:
                        break
                link_groups.append(links)

            # make faces
            for lo in link_groups:
                for l in lo:
                    face_verts = [
                        l[0], l[1],
                        axis_aligned_verts[l[1]], axis_aligned_verts[l[0]],
                    ]
                    bm.faces.new(face_verts)

    bmesh.update_edit_mesh(new_obj.data)

    # edit mode -> object mode
    bpy.ops.object.editmode_toggle()

    # add mirror modifier
    if mqo_obj.mirror is not None:
        if MQO_TO_BLENDER_MIRROR_TYPE[mqo_obj.mirror] != 'NONE':
            bpy.ops.object.modifier_add(type='MIRROR')
            axis_index = MQO_TO_BLENDER_MIRROR_AXIS_INDEX[mqo_obj.mirror_axis]
            if compat.check_version(2, 80, 0) >= 0:
                for i in new_obj.modifiers["Mirror"].use_axis:
                    new_obj.modifiers["Mirror"].use_axis[i] = False
                new_obj.modifiers["Mirror"].use_axis[axis_index] = True
            else:
                new_obj.modifiers["Mirror"].use_x = False
                new_obj.modifiers["Mirror"].use_y = False
                new_obj.modifiers["Mirror"].use_z = False
                if axis_index == 0:
                    new_obj.modifiers["Mirror"].use_x = True
                elif axis_index == 1:
                    new_obj.modifiers["Mirror"].use_y = True
                elif axis_index == 2:
                    new_obj.modifiers["Mirror"].use_z = True

    return new_obj


def import_objects(mqo_file, exclude_objects, materials):
    objects_imported = []
    for mqo_obj in mqo_file.get_objects():
        if mqo_obj.name in exclude_objects:
            continue
        objects_imported.append(import_object(mqo_obj, materials))

    return objects_imported


def import_mqo_file(filepath, exclude_objects, exclude_materials,
                    import_prefix):
    mqo_file = mqo.MqoFile()
    mqo_file.load(filepath)

    orig_mode = bpy.context.mode
    if bpy.ops.object.mode_set.poll() and orig_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    materials_imported = import_materials(mqo_file, filepath,
                                          exclude_materials)
    objects_imported = import_objects(mqo_file, exclude_objects,
                                      materials_imported)

    # set import prefix
    for mtrl in materials_imported:
        if mtrl["material"] is None:
            continue
        mtrl["material"].name = "{}{}".format(
            import_prefix, mtrl["material"].name)
    for obj in objects_imported:
        obj.name = "{}{}".format(import_prefix, obj.name)

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=orig_mode)


def export_material_v279(mqo_file, material):
    mqo_mtrl = mqo.Material()
    mqo_mtrl.name = material.name
    mqo_mtrl.color = [*material.diffuse_color[0:3], 1.0]
    mqo_mtrl.diffuse = material.diffuse_intensity
    mqo_mtrl.specular = material.specular_intensity
    mqo_mtrl.emissive = material.emit
    mqo_mtrl.ambient = material.ambient
    mqo_file.add_material(mqo_mtrl)


def export_material_v280(mqo_file, material):
    if not material.use_nodes:
        return

    mqo_mtrl = mqo.Material()
    mqo_mtrl.name = material.name
    output_node = material.node_tree.nodes["Material Output"]

    links = output_node.inputs['Surface'].links
    if len(links) != 1:
        return

    material_node = links[0].from_node
    if material_node.type == 'EEVEE_SPECULAR':
        mqo_mtrl.color = material_node.inputs["Base Color"].default_value
        mqo_mtrl.specular = material_node.inputs["Specular"].default_value[0]
        mqo_mtrl.emissive =\
            material_node.inputs["Emissive Color"].default_value[0]
    elif material_node.type == 'TEX_IMAGE':
        mqo_mtrl.texture_map = bpy.path.basename(material_node.image.filepath)
        mqo_mtrl.projection_type = BLENDER_TO_MQO_PROJECTION_TYPE[
            material_node.projection]

    mqo_file.add_material(mqo_mtrl)


def export_material(mqo_file, material):
    if compat.check_version(2, 80, 0) >= 0:
        return export_material_v280(mqo_file, material)
    else:
        return export_material_v279(mqo_file, material)


def export_materials(mqo_file, exclude_materials):
    materials_to_export = [mtrl for mtrl in bpy.data.materials]
    for mtrl in materials_to_export:
        if mtrl.name in exclude_materials:
            continue
        export_material(mqo_file, mtrl)


# pylint: disable=unused-argument
def attach_texture_to_material_v280(mqo_file, exclude_objects,
                                    exclude_materials, export_objects):
    pass


def attach_texture_to_material_v279(mqo_file, exclude_objects,
                                    exclude_materials, export_objects):
    # objects
    for obj in export_objects:
        if obj.name in exclude_objects:
            continue

        # object mode -> edit mode
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='EDIT')

        # materials
        for mtrl_idx, mtrl_slot in enumerate(obj.material_slots):
            if mtrl_slot.material.name in exclude_materials:
                continue   # does not export material index

            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()

            for face in bm.faces:
                face.select = False
            bmesh.update_edit_mesh(obj.data)

            mtrl = mtrl_slot.material
            obj.active_material_index = mtrl_idx
            obj.active_material = mtrl
            bpy.ops.object.material_slot_select()

            # find material index for mqo
            for i, mqo_mtrl in enumerate(mqo_file.get_materials()):
                if mtrl.name == mqo_mtrl.name:
                    mqo_mtrl_idx = i
                    break
            else:
                continue

            for face in bm.faces:
                if face.select:
                    image_face = face
                    break
            else:
                continue

            if not bm.faces.layers.tex.items():
                continue

            # attch texture to material
            tex_layer = bm.faces.layers.tex.verify()
            texture_path = bpy.path.basename(
                image_face[tex_layer].image.filepath)
            mqo_file.get_materials()[mqo_mtrl_idx].texture_map = texture_path

        # edit mode -> object mode
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')


def attach_texture_to_material(mqo_file, exclude_objects, exclude_materials,
                               export_objects):
    if compat.check_version(2, 80, 0) >= 0:
        attach_texture_to_material_v280(
            mqo_file, exclude_objects, exclude_materials, export_objects)
    else:
        attach_texture_to_material_v279(
            mqo_file, exclude_objects, exclude_materials, export_objects)


def export_mqo_file(filepath, exclude_objects, exclude_materials,
                    export_prefix):
    mqo_file = mqo.MqoFile()
    mqo_file.version = "1.1"
    mqo_file.format = "Text"

    scene = mqo.Scene()
    scene.set_default_params()
    mqo_file.scene = scene

    export_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    orig_mode = bpy.context.mode
    if bpy.ops.object.mode_set.poll() and orig_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # materials
    export_materials(mqo_file, exclude_materials)

    # attach texture on materials
    attach_texture_to_material(mqo_file, exclude_objects, exclude_materials,
                               export_objects)

    # objects
    for obj in export_objects:
        if obj.name in exclude_objects:
            continue

        # copy object
        copied_obj = obj.copy()
        copied_obj.data = obj.data.copy()
        if compat.check_version(2, 80, 0) >= 0:
            bpy.context.scene.collection.objects.link(copied_obj)
            bpy.context.view_layer.objects.active = copied_obj
            copied_obj.select_set(True)
        else:
            bpy.context.scene.objects.link(copied_obj)
            bpy.context.scene.objects.active = copied_obj
            copied_obj.select = True

        # apply all modifiers
        for mod in copied_obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=mod.name)

        # object mode -> edit mode
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='EDIT')

        mqo_obj = mqo.Object()
        mqo_obj.name = obj.name
        bm = bmesh.from_edit_mesh(copied_obj.data)

        # vertices
        for v in bm.verts:
            mqo_obj.add_vertex([v.co[0], v.co[1], v.co[2]])

        # faces
        for face in bm.faces:
            mqo_face = mqo.Face()
            mqo_face.ngons = len(face.verts)
            mqo_face.vertex_indices = [v.index for v in face.verts]
            if len(bm.loops.layers.uv.keys()) > 0:
                uv_layer = bm.loops.layers.uv.verify()
                for l in face.loops:
                    if mqo_face.uv_coords is None:
                        mqo_face.uv_coords = []
                    mqo_face.uv_coords.append([l[uv_layer].uv[0],
                                               l[uv_layer].uv[1]])
            mqo_obj.add_face(mqo_face)

        # materials
        for mtrl_idx, mtrl_slot in enumerate(copied_obj.material_slots):
            if mtrl_slot.material.name in exclude_materials:
                continue   # does not export material index

            bm = bmesh.from_edit_mesh(copied_obj.data)
            bm.faces.ensure_lookup_table()
            # set material
            for face in bm.faces:
                face.select = False
            bmesh.update_edit_mesh(copied_obj.data)

            mtrl = mtrl_slot.material
            copied_obj.active_material_index = mtrl_idx
            copied_obj.active_material = mtrl
            bpy.ops.object.material_slot_select()

            # find material index for mqo
            mqo_mtrl_idx = -1
            for i, mqo_mtrl in enumerate(mqo_file.get_materials()):
                if mtrl.name == mqo_mtrl.name:
                    mqo_mtrl_idx = i
                    break
            # set material index
            for bm_face, mqo_face in zip(bm.faces, mqo_obj.get_faces()):
                if bm_face.select:
                    mqo_face.material = mqo_mtrl_idx

        # edit mode -> object mode
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        mqo_file.add_object(mqo_obj)

        if compat.check_version(2, 80, 0) >= 0:
            bpy.context.scene.collection.objects.unlink(copied_obj)
        else:
            bpy.context.scene.objects.unlink(copied_obj)
        bpy.data.objects.remove(copied_obj)

    # set export prefix
    for mqo_obj in mqo_file.get_objects():
        mqo_obj.name = "{}{}".format(export_prefix, mqo_obj.name)
    for mqo_mtrl in mqo_file.get_materials():
        mqo_mtrl.name = "{}{}".format(export_prefix, mqo_mtrl.name)

    mqo_file.save(filepath)
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=orig_mode)


@compat.make_annotations
class BoolPropertyCollection(bpy.types.PropertyGroup):
    checked = BoolProperty(name="", default=True)


@BlClassRegistry()
@compat.make_annotations
class BLMQO_OT_ImportMqo(bpy.types.Operator, ImportHelper):

    bl_idname = "import_scene.blmqo_ot_import_mqo"
    bl_label = "Import Metasequoia file (.mqo)"
    bl_description = "Import a Metasequoia file"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo")

    import_objects = BoolProperty(name="Import Objects", default=True)
    import_materials = BoolProperty(name="Import Materials", default=True)
    add_import_prefix = BoolProperty(name="Add Import Prefix", default=True)
    import_prefix = StringProperty(name="Prefix", default="[Imported] ")

    bool_prop_collection = CollectionProperty(type=BoolPropertyCollection)
    objects_to_import = []
    materials_to_import = []
    loaded_file = ""

    def draw(self, _):
        layout = self.layout

        if compat.check_version(2, 80, 0) < 0:
            # TODO: dynamic loading is not supported in <2.79
            return

        if self.loaded_file != self.properties.filepath:
            mqo_file = mqo.MqoFile()
            try:
                mqo_file.load(self.properties.filepath)
                loaded = True
            except:
                loaded = False

            self.objects_to_import = []
            self.materials_to_import = []
            self.bool_prop_collection.clear()
            if loaded:
                for obj in mqo_file.get_objects():
                    item = self.bool_prop_collection.add()
                    self.objects_to_import.append(
                        {"name": obj.name, "item": item})
                for mtrl in mqo_file.get_materials():
                    item = self.bool_prop_collection.add()
                    self.materials_to_import.append(
                        {"name": mtrl.name, "item": item})
            self.loaded_file = self.properties.filepath

        layout.label(text="File: {}".format(self.loaded_file))

        layout.prop(self, "import_objects")
        if self.import_objects and len(self.objects_to_import) > 0:
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()     # spacer
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for d in self.objects_to_import:
                box.prop(d["item"], "checked", text=d["name"])

        layout.prop(self, "import_materials")
        if self.import_materials and len(self.materials_to_import) > 0:
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()  # spacer
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for m in self.materials_to_import:
                box.prop(m["item"], "checked", text=m["name"])

        layout.prop(self, "add_import_prefix")
        if self.add_import_prefix:
            layout.prop(self, "import_prefix")

    def execute(self, _):
        exclude_objects = [o["name"]
                           for o in self.objects_to_import
                           if not o["item"].checked]
        exclude_materials = [m["name"]
                             for m in self.materials_to_import
                             if not m["item"].checked]
        import_mqo_file(self.properties.filepath, exclude_objects,
                        exclude_materials,
                        self.import_prefix if self.add_import_prefix else "")

        self.report({'INFO'},
                    "Imported from {}".format(self.properties.filepath))

        return {'FINISHED'}

    def invoke(self, context, _):
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


@BlClassRegistry()
@compat.make_annotations
class BLMQO_OT_ExportMqo(bpy.types.Operator, ExportHelper):

    bl_idname = "export_scene.blmqo_ot_export_mqo"
    bl_label = "Export Metasequoia file (.mqo)"
    bl_description = "Export a Metasequoia file"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo")

    export_objects = BoolProperty(name="Export Objects", default=True)
    export_materials = BoolProperty(name="Export Materials", default=True)
    add_export_prefix = BoolProperty(name="Add Export Prefix", default=True)
    export_prefix = StringProperty(name="Prefix", default="[Exported] ")

    bool_prop_collection = CollectionProperty(type=BoolPropertyCollection)
    objects_to_export = []
    materials_to_export = []
    initialized = False

    def draw(self, _):
        layout = self.layout

        if not self.initialized:
            self.objects_to_export = []
            self.materials_to_export = []
            self.bool_prop_collection.clear()
            for obj in bpy.data.objects:
                if obj.type != 'MESH':
                    continue
                item = self.bool_prop_collection.add()
                self.objects_to_export.append(
                    {"name": obj.name, "item": item})
            for mtrl in bpy.data.materials:
                item = self.bool_prop_collection.add()
                self.materials_to_export.append(
                    {"name": mtrl.name, "item": item})
            self.initialized = True

        layout.prop(self, "export_objects")
        if self.export_objects and len(self.objects_to_export) > 0:
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()     # spacer
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for d in self.objects_to_export:
                box.prop(d["item"], "checked", text=d["name"])

        layout.prop(self, "export_materials")
        if self.export_materials and len(self.materials_to_export) > 0:
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()  # spacer
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for m in self.materials_to_export:
                box.prop(m["item"], "checked", text=m["name"])

        layout.prop(self, "add_export_prefix")
        if self.add_export_prefix:
            layout.prop(self, "export_prefix")

    def execute(self, _):
        exclude_objects = [o["name"]
                           for o in self.objects_to_export
                           if not o["item"].checked]
        exclude_materials = [m["name"]
                             for m in self.materials_to_export
                             if not m["item"].checked]
        export_mqo_file(self.properties.filepath, exclude_objects,
                        exclude_materials,
                        self.export_prefix if self.add_export_prefix else "")

        self.report({'INFO'},
                    "Exported to {}".format(self.properties.filepath))

        return {'FINISHED'}

    def invoke(self, context, _):
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


def topbar_mt_file_import_fn(self, _):
    layout = self.layout

    layout.operator(BLMQO_OT_ImportMqo.bl_idname,
                    text="Metasequoia (.mqo)",
                    icon='PLUGIN')


def topbar_mt_file_export_fn(self, _):
    layout = self.layout

    layout.operator(BLMQO_OT_ExportMqo.bl_idname,
                    text="Metasequoia (.mqo)",
                    icon='PLUGIN')
