import bpy
from bpy.props import BoolProperty
from .. utils.registration import get_addon


class Mirror(bpy.types.Operator):
    bl_idname = "machin3.mirror"
    bl_label = "MACHIN3: Mirror"
    bl_options = {'REGISTER', 'UNDO'}

    use_x: BoolProperty(name="X", default=True)
    use_y: BoolProperty(name="Y", default=False)
    use_z: BoolProperty(name="Z", default=False)

    bisect_x: BoolProperty(name="Bisect", default=False)
    bisect_y: BoolProperty(name="Bisect", default=False)
    bisect_z: BoolProperty(name="Bisect", default=False)

    flip_x: BoolProperty(name="Flip", default=False)
    flip_y: BoolProperty(name="Flip", default=False)
    flip_z: BoolProperty(name="Flip", default=False)

    DM_mirror_u: BoolProperty(name="U", default=True)
    DM_mirror_v: BoolProperty(name="V", default=False)

    # hidden
    init: BoolProperty()

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row(align=True)
        row.prop(self, "use_x", toggle=True)
        row.prop(self, "use_y", toggle=True)
        row.prop(self, "use_z", toggle=True)

        if len(context.selected_objects) == 1 and context.active_object in context.selected_objects:
            row = column.row(align=True)
            r = row.row()
            r.active = self.use_x
            r.prop(self, "bisect_x")
            r = row.row()
            r.active = self.use_y
            r.prop(self, "bisect_y")
            r = row.row()
            r.active = self.use_z
            r.prop(self, "bisect_y")

            row = column.row(align=True)
            r = row.row()
            r.active = self.use_x
            r.prop(self, "flip_x")
            r = row.row()
            r.active = self.use_y
            r.prop(self, "flip_y")
            r = row.row()
            r.active = self.use_z
            r.prop(self, "flip_y")


        DMenabled, _, _, _ = get_addon("DECALmachine")
        if DMenabled:
            column.separator()

            column.label(text="DECALmachine - UVs")
            row = column.row(align=True)
            row.prop(self, "DM_mirror_u", toggle=True)
            row.prop(self, "DM_mirror_v", toggle=True)

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        sel = context.selected_objects
        active = context.active_object

        if self.init and len(sel) > 1:
            self.bisect_x = self.bisect_y = self.bisect_z = False
            self.flip_x = self.flip_y = self.flip_z = False

        self.mirror(context, active, sel)

        return {'FINISHED'}

    def mirror(self, context, active, sel):
        if len(sel) == 1 and active in sel:
            if active.type in ["MESH", "CURVE"]:
                self.mirror_mesh_obj(context, active)

            elif active.type == "EMPTY" and active.instance_collection:
                self.mirror_grouppro(context, active)

        elif len(sel) > 1 and active in sel:
            sel.remove(active)

            for obj in sel:
                if obj.type in ["MESH", "CURVE"]:
                    self.mirror_mesh_obj(context, obj, active)

                elif obj.type == "EMPTY" and obj.instance_collection:
                    self.mirror_grouppro(context, obj, active)

            context.view_layer.objects.active = active

    def mirror_mesh_obj(self, context, obj, active=None):
        mirror = obj.modifiers.new(name="Mirror", type="MIRROR")
        mirror.use_axis = (self.use_x, self.use_y, self.use_z)
        mirror.use_bisect_axis = (self.bisect_x, self.bisect_y, self.bisect_z)
        mirror.use_bisect_flip_axis = (self.flip_x, self.flip_y, self.flip_z)

        if active:
            mirror.mirror_object = active

        DMenabled, _, _, _ = get_addon("DECALmachine")

        if DMenabled:
            if obj.DM.isdecal:
                mirror.use_mirror_u = self.DM_mirror_u
                mirror.use_mirror_v = self.DM_mirror_v

                nrmtransfer = obj.modifiers.get("NormalTransfer")

                # make a copy of the nrmtransfer mod, add it to the end of the stack and remove the old one
                if nrmtransfer:
                    new = obj.modifiers.new("temp", "DATA_TRANSFER")
                    new.object = nrmtransfer.object
                    new.use_loop_data = True
                    new.data_types_loops = {'CUSTOM_NORMAL'}
                    new.loop_mapping = 'POLYINTERP_LNORPROJ'
                    new.show_expanded = False
                    new.show_render = nrmtransfer.show_render
                    new.show_viewport = nrmtransfer.show_viewport

                    obj.modifiers.remove(nrmtransfer)
                    new.name = "NormalTransfer"

    def mirror_grouppro(self, context, obj, active=None):
        mirrorempty = bpy.data.objects.new("mirror_empty", None)

        col = obj.instance_collection

        if active:
            mirrorempty.matrix_world = active.matrix_world

        mirrorempty.matrix_world = obj.matrix_world.inverted() @ mirrorempty.matrix_world

        col.objects.link(mirrorempty)

        meshes = [obj for obj in col.objects if obj.type == "MESH"]

        for obj in meshes:
            self.mirror_mesh_obj(context, obj, mirrorempty)


class Unmirror(bpy.types.Operator):
    bl_idname = "machin3.unmirror"
    bl_label = "MACHIN3: Unmirror"
    bl_description = "Removes the last modifer in the stack of the selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

        column = layout.column()

    @classmethod
    def poll(cls, context):
        mirror_meshes = [obj for obj in context.selected_objects if obj.type == "MESH" and any(mod.type == "MIRROR" for mod in obj.modifiers)]
        if mirror_meshes:
            return True

        groups = [obj for obj in context.selected_objects if obj.type == "EMPTY" and obj.instance_collection]
        if groups:
            return [empty for empty in groups if any(obj for obj in empty.instance_collection.objects if any(mod.type == "MIRROR" for mod in obj.modifiers))]

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type in ["MESH", "CURVE"]:
                self.unmirror_mesh_obj(obj)

            elif obj.type == "EMPTY" and obj.instance_collection:
                col = obj.instance_collection

                targets = set()

                for obj in col.objects:
                    target = self.unmirror_mesh_obj(obj)

                    if target and target.type == "EMPTY":
                        targets.add(target)

                if len(targets) == 1:
                    bpy.data.objects.remove(list(targets)[0], do_unlink=True)

        return {'FINISHED'}

    def unmirror_mesh_obj(self, obj):
        mirrors = [mod for mod in obj.modifiers if mod.type == "MIRROR"]

        if mirrors:
            target = mirrors[-1].mirror_object
            obj.modifiers.remove(mirrors[-1])
            return target
