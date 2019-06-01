import bpy
import bmesh
import numpy as np
from mathutils import Vector
from os import path
from .multifile import register_class

DEFORM_RIG_PATH = path.join(path.dirname(path.realpath(__file__)), "Mask Deform Rig.blend")


def create_object_from_bm(bm, matrix_world, name="new_mesh", set_active=False):
    mesh = bpy.data.meshes.new(name=name)
    bm.to_mesh(mesh)
    obj = bpy.data.objects.new(name=name, object_data=mesh)
    obj.matrix_world = matrix_world
    bpy.context.collection.objects.link(obj)
    if set_active:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    return obj


def get_bm_and_mask(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    layer = bm.verts.layers.paint_mask.verify()

    return bm, layer


@register_class
class MaskExtract(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.mask_extract"
    bl_label = "Extract Mask"
    bl_description = "Extract and solidify Masked region as a new object"
    bl_options = {"REGISTER"}
    obj = None
    solidify = None
    smooth = None
    last_mouse = 0
    click_count = 0

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == "MESH"

    def execute(self, context):
        self.last_mode = context.active_object.mode
        self.click_count = 0

        bm, mask = get_bm_and_mask(context.active_object.data)

        bpy.ops.object.mode_set(mode="OBJECT")

        for vert in bm.verts:
            if vert[mask] < 0.5:
                bm.verts.remove(vert)
        remove = []
        dissolve = []
        for vert in bm.verts:
            if len(vert.link_faces) < 1:
                remove.append(vert)
            elif len(vert.link_faces) == 1:
                dissolve.append(vert)
        for vert in remove:
            bm.verts.remove(vert)

        bmesh.ops.dissolve_verts(bm, verts=dissolve)

        self.obj = create_object_from_bm(bm,
                                         context.active_object.matrix_world,
                                         context.active_object.name + "_Shell")
        bm.free()
        self.obj.select_set(True)
        context.view_layer.objects.active = self.obj

        self.displace = self.obj.modifiers.new(type="DISPLACE", name="DISPLACE")
        self.displace.strength = 0
        self.solidify = self.obj.modifiers.new(type="SOLIDIFY", name="Solidify")
        self.solidify.offset = 1
        self.solidify.thickness = 0
        self.smooth = self.obj.modifiers.new(type="SMOOTH", name="SMOOTH")
        self.smooth.iterations = 5

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        dist = context.region_data.view_distance

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            self.click_count += 1
        elif event.type in {"ESC", "RIGHTMOUSE"}:
            self.click_count = 3

        if event.type == "MOUSEMOVE":
            delta = self.last_mouse - event.mouse_y
            self.last_mouse = event.mouse_y
            if self.click_count == 0:
                amount = dist * delta * (0.0001 if event.shift else 0.002)
                self.solidify.thickness += amount
                self.solidify.thickness = max(self.solidify.thickness, 0)

            elif self.click_count == 1:
                self.smooth.factor -= delta * (0.0001 if event.shift else 0.004)
                self.smooth.factor = max(self.smooth.factor, 0)

            elif self.click_count == 2:
                amount = dist * delta * (0.0001 if event.shift else 0.002)
                self.displace.strength -= amount

            elif self.click_count >= 3:
                bpy.ops.object.modifier_apply(modifier=self.displace.name)
                bpy.ops.object.modifier_apply(modifier=self.solidify.name)
                bpy.ops.object.modifier_apply(modifier=self.smooth.name)
                return {"FINISHED"}

        return {"RUNNING_MODAL"}


@register_class
class MaskSplit(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.mask_split"
    bl_label = "Mask Split"
    bl_description = "Split masked and unmasked areas away."
    bl_options = {"REGISTER", "UNDO"}

    keep: bpy.props.EnumProperty(
        name="Keep",
        items=(("MASKED", "Masked", "Keep darkened parts"),
               ("UNMASKED", "Unmasked", "Keep light parts"),
               ("NONE", "None", "Keep both sides in separate objects")),
        default="NONE"
    )

    @classmethod
    def poll(cls, context):
        return context.active_object.data

    def invoke(self, context, event):
        bpy.ops.ed.undo_push()
        bpy.ops.object.mode_set(mode="OBJECT")
        return context.window_manager.invoke_props_dialog(self)

    def remove_half(self, bm, invert=False):
        for face in bm.faces:
            if (face.select and not invert) or (not face.select and invert):
                bm.faces.remove(face)
        for vert in bm.verts:
            if len(vert.link_faces) == 0:
                bm.verts.remove(vert)
        bmesh.ops.holes_fill(bm, edges=bm.edges)
        bmesh.ops.triangulate(bm, faces=[face for face in bm.faces if len(face.verts) > 4])

    def execute(self, context):
        ob = context.active_object
        bm, mask = get_bm_and_mask(ob.data)
        bm.faces.ensure_lookup_table()
        face_mask = []

        for face in bm.faces:
            mask_sum = 0
            for vert in face.verts:
                mask_sum += vert[mask]
            face_mask.append(mask_sum / len(face.verts))

        geom1 = []

        for face in bm.faces:
            if face_mask[face.index] > 0.5:
                geom1.append(face)
                face.select = True
            else:
                face.select = False

        bm1 = bm.copy()

        invert = False
        if self.keep == "MASKED":
            invert = True

        self.remove_half(bm, invert=invert)
        bm.to_mesh(ob.data)

        if self.keep == "NONE":
            self.remove_half(bm1, invert=True)
            bpy.ops.object.duplicate()
            bm1.to_mesh(context.active_object.data)

        return {"FINISHED"}


@register_class
class MaskDeformRemove(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.mask_deform_remove"
    bl_label = "Remove Mask Deform"
    bl_description = "Remove Mask Rig"
    bl_options = {"REGISTER", "UNDO"}

    apply: bpy.props.BoolProperty(
        name="Apply",
        description="Apply Mask deform before remove",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == "MESH"

    def execute(self, context):
        if not context.active_object.get("MASK_RIG", False):
            return {"CANCELLED"}

        if self.apply:
            bpy.ops.object.convert(target="MESH")

        for item in context.active_object["MASK_RIG"]:
            if type(item) == str:
                for md in context.active_object.modifiers:
                    if md.name == md:
                        if self.apply:
                            bpy.ops.object.modifier_apply(modifier=md.name)
                        else:
                            context.active_object.modifiers.remove(md)

            elif type(item) == bpy.types.Object:
                bpy.data.objects.remove(item)
        del context.active_object["MASK_RIG"]
        context.area.tag_redraw()
        return {"FINISHED"}


@register_class
class MaskDeformAdd(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.mask_deform_add"
    bl_label = "Add Mask Deform"
    bl_description = "Add a rig to deform masked region"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == "MESH"

    def create_rig(self, context, ob, vg, location, radius=1):

        md = ob.modifiers.new(type="LATTICE", name="MASK_DEFORM")
        md.vertex_group = vg.name
        with bpy.types.BlendDataLibraries.load(DEFORM_RIG_PATH) as (data_from, data_to):
            data_to.objects = ["Lattice", "DeformPivot", "DeformManipulator"]
        for d_ob in data_to.objects:
            context.collection.objects.link(d_ob)
        md.object = data_to.objects[0]
        data_to.objects[0].hide_viewport = True
        data_to.objects[1].location = location
        ob["MASK_RIG"] = list(data_to.objects)
        ob["MASK_RIG"].append(md.name)

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        ob = context.active_object
        bm, mask = get_bm_and_mask(ob.data)
        vg = ob.vertex_groups.new(name="MASK_TO_VG")
        avg_location = Vector()
        total = 0
        for vert in bm.verts:
            vg.add([vert.index], weight=vert[mask], type="REPLACE")
            avg_location += vert.co * vert[mask]
            total += vert[mask]
        avg_location /= total
        self.create_rig(context, ob, vg, avg_location)

        return {"FINISHED"}


@register_class
class MaskDecimate(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.mask_decimate"
    bl_label = "Mask Decimate"
    bl_description = "Decimate masked region"
    bl_options = {"REGISTER", "UNDO"}

    ratio: bpy.props.FloatProperty(
        name="Ratio",
        description="Amount of decimation",
        default=0.7
    )

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == "MESH"

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.ed.undo_push()
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        bpy.ops.ed.undo_push()
        ob = context.active_object
        vg = ob.vertex_groups.new(name="DECIMATION_VG")

        bm, mask = get_bm_and_mask(ob.data)
        for vert in bm.verts:
            vg.add([vert.index], weight=vert[mask], type="REPLACE")
        ob.vertex_groups.active = vg
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.decimate(ratio=self.ratio, use_vertex_group=True, vertex_group_factor=10)
        bpy.ops.object.mode_set(mode="OBJECT")
        ob.vertex_groups.remove(vg)
        context.area.tag_redraw()
        return {"FINISHED"}


class MaskBlurEngine:
    def __init__(self, obj, max_edges=10):
        bm, mask = get_bm_and_mask(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        self.bm = bm
        self.mask_layer = mask
        self.max_edges = max_edges
        self.n = len(bm.verts)
        self.edges = np.zeros((self.n, max_edges), dtype=np.int_)
        self.edge_counts = np.zeros((self.n,), dtype=np.int_)
        self.mask_values = np.zeros((self.n,), dtype=np.float_)
        self.modified_mask = np.zeros((self.n,), dtype=np.float_)

        for vert in bm.verts:
            i = vert.index
            self.mask_values[i] = vert[mask]
            self.edge_counts[i] = len(vert.link_edges)
            for j, edge in enumerate(vert.link_edges):
                other = edge.other_vert(vert)
                if j > self.max_edges:
                    continue
                self.edges[i, j] = other.index
        self.reset()

    def walk_edges(self, depth=0):
        cols = np.arange(self.n)
        ids = np.random.randint(0, self.max_edges, (self.n,)) % self.edge_counts
        ids = ids.astype(np.int_)
        adjacent_edges = self.edges[cols, ids]
        for _ in range(depth):
            ids = np.random.randint(0, self.max_edges, (self.n,)) % self.edge_counts[adjacent_edges]
            ids = ids.astype(np.int_)
            adjacent_edges = self.edges[adjacent_edges, ids]
        return adjacent_edges

    def reset(self):
        self.modified_mask = self.mask_values.copy()

    def blur(self, iterations=10, jumps=0):
        for i in range(iterations):
            edges = self.walk_edges(jumps)
            self.modified_mask += self.mask_values[edges]
        self.modified_mask /= iterations + 1

    def get_modified_mask_bm(self):
        for vert in self.bm.verts:
            vert[self.mask_layer] = self.modified_mask[vert.index]
        return self.bm


@register_class
class MaskBlur(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.mask_blur_engine"
    bl_label = "Mask Blur"
    bl_description = "testr"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        self.blur_engine = MaskBlurEngine(context.active_object)
        return self.execute(context)

    def execute(self, context):
        print(self.blur_engine)
        # self.blur_engine.blur(10, 10)
        for i in range(100):
            self.blur_engine.blur(10, 0)
            self.blur_engine.mask_values = self.blur_engine.modified_mask.copy()
        bm = self.blur_engine.get_modified_mask_bm()
        bm.to_mesh(context.active_object.data)
        return {"FINISHED"}


@register_class
class ExpandMask(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.expand_mask"
    bl_label = "Expand Mask"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    factor: bpy.props.FloatProperty(
        name="Factor",
        description="Factor",
        default=1
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bm, mask = get_bm_and_mask(context.active_object.data)
        new_mask = {}
        for vert in bm.verts:
            val = vert[mask]
            for edge in vert.link_edges:
                other = edge.other_vert(vert)
                val = max(other[mask], val)
            new_mask[vert] = val * self.factor + vert[mask] * (1 - self.factor)

        for vert in bm.verts:
            vert[mask] = new_mask[vert]
        bm.to_mesh(context.active_object.data)
        context.area.tag_redraw()
        return {"FINISHED"}
