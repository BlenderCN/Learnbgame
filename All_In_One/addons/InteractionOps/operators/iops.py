import bpy


class IOPS(bpy.types.Operator):
    bl_idname = "iops.main"
    bl_label = "IOPS"
    bl_options = {"REGISTER", "UNDO"}

    modes_3d = {0: "VERT", 1: "EDGE", 2: "FACE"}
    modes_uv = {0: "VERTEX", 1: "EDGE", 2: "FACE", 3: "ISLAND"}
    modes_gpen = {0: "EDIT_GPENCIL", 1: "PAINT_GPENCIL", 2: "SCULPT_GPENCIL"}
    modes_curve = {0: "EDIT_CURVE"}
    modes_text = {0: "EDIT_TEXT"}
    modes_meta = {0: "EDIT_META"}
    modes_lattice = {0: "EDIT_LATTICE"}
    modes_armature = {0: "EDIT", 1: "POSE"}
    supported_types = {"MESH", "CURVE", "GPENCIL", "EMPTY", "TEXT", "META", "ARMATURE", "LATTICE"}

    # Current mode
    _mode_3d = ""
    _mode_uv = ""
    _mode_gpen = ""
    _mode_curve = ""
    _mode_text = ""
    _mode_meta = ""
    _mode_armature = ""
    _mode_lattice = ""

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def get_mode_3d(self, tool_mesh):
        mode = ""
        if tool_mesh[0]:
            mode = "VERT"
        elif tool_mesh[1]:
            mode = "EDGE"
        elif tool_mesh[2]:
            mode = "FACE"
        return mode

    def execute(self, context):
        # Object <-> Mesh
        scene = bpy.context.scene
        tool = bpy.context.tool_settings
        tool_mesh = scene.tool_settings.mesh_select_mode

        active_object = bpy.context.view_layer.objects.active

        if active_object.type == "MESH":
            _mode_3d = self.get_mode_3d(tool_mesh)
            if (bpy.context.area.type == "VIEW_3D" or
                (bpy.context.area.type == "IMAGE_EDITOR" and
                 tool.use_uv_select_sync is True)):
                # Same modes for active sync in UV
                # Go to Edit Mode
                if bpy.context.mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.select_mode(type=self._mode_3d)
                    _mode_3d = self._mode_3d
                    # self.report({"INFO"}, _mode_3d)
                    return{"FINISHED"}

                # Switch selection modes
                # If activated same selection mode again switch to Object Mode
                if (bpy.context.mode == "EDIT_MESH" and self._mode_3d != _mode_3d):
                    bpy.ops.mesh.select_mode(type=self._mode_3d)
                    _mode_3d = self._mode_3d
                    # self.report({"INFO"}, _mode_3d)
                    return{"FINISHED"}
                else:
                    bpy.ops.object.mode_set(mode="OBJECT")
                    # self.report({"INFO"}, "OBJECT MODE")
                    return{"FINISHED"}

            # UV <-> Mesh
            if bpy.context.area.type == "IMAGE_EDITOR":
                # Go to Edit Mode and Select All
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.select_all(action="SELECT")
                    tool.uv_select_mode = self._mode_uv
                    _mode_uv = self._mode_uv
                    # self.report({"INFO"}, _mode_uv)
                    return{"FINISHED"}

            elif self._mode_uv != _mode_uv:
                    tool.uv_select_mode = self._mode_uv
                    _mode_uv = self._mode_uv
                    # self.report({"INFO"}, _mode_uv)
                    return{"FINISHED"}
            else:
                    bpy.ops.object.mode_set(mode="OBJECT")
                    # self.report({"INFO"}, "OBJECT MODE")
                    return{"FINISHED"}

        # Object <-> Curve
        if active_object.type == "CURVE":
            _mode_curve = "EDIT" if bpy.context.mode != "EDIT_CURVE" else "OBJECT"
            bpy.ops.object.mode_set(mode=_mode_curve)
            # self.report({"INFO"}, _mode_curve)
            return{"FINISHED"}

        # Object <-> GPencil
        if active_object.type == "GPENCIL":
            _mode_gpen = active_object.mode
            if (bpy.context.area.type == "VIEW_3D"):
                if bpy.context.mode == "OBJECT":
                    _mode_gpen = self._mode_gpen
                    bpy.ops.object.mode_set(mode=_mode_gpen)
                    # self.report({"INFO"}, _mode_gpen)
                    return{"FINISHED"}
                elif self._mode_gpen != _mode_gpen:
                    bpy.ops.object.mode_set(mode=self._mode_gpen)
                    _mode_gpen = self._mode_gpen
                    # self.report({"INFO"}, _mode_gpen)
                    return{"FINISHED"}
                else:
                    bpy.ops.object.mode_set(mode="OBJECT")
                    # self.report({"INFO"}, "OBJECT MODE")
                    return{"FINISHED"}
            return{"FINISHED"}

        # Object <-> Text
        if active_object.type == "FONT":
            _mode_text = "EDIT" if bpy.context.mode != "EDIT_TEXT" else "OBJECT"
            bpy.ops.object.mode_set(mode=_mode_text)
            # self.report({"INFO"}, _mode_text)
            return{"FINISHED"}

        # Object <-> Meta
        if active_object.type == "META":
            _mode_meta = "EDIT" if bpy.context.mode != "EDIT_META" else "OBJECT"
            # bpy.ops.object.mode_set(mode=_mode_meta)
            bpy.ops.object.editmode_toggle()
            # self.report({"INFO"}, _mode_meta)
            return{"FINISHED"}

        # Object <-> Armature
        if active_object.type == "ARMATURE":
            _mode_armature = active_object.mode
            if (bpy.context.area.type == "VIEW_3D"):
                if bpy.context.mode == "OBJECT":
                    _mode_armature = self._mode_armature
                    bpy.ops.object.mode_set(mode=_mode_armature)
                    # self.report({"INFO"}, _mode_armature)
                    return{"FINISHED"}
                elif self._mode_armature != _mode_armature:
                    bpy.ops.object.mode_set(mode=self._mode_armature)
                    _mode_armature = self._mode_armature
                    # self.report({"INFO"}, _mode_armature)
                    return{"FINISHED"}
                else:
                    bpy.ops.object.mode_set(mode="OBJECT")
                    # self.report({"INFO"}, "OBJECT MODE")
                    return{"FINISHED"}
            return{"FINISHED"}

        # Object <-> Lattice
        if active_object.type == "LATTICE":
            _mode_lattice = "EDIT" if bpy.context.mode != "EDIT_LATTICE" else "OBJECT"
            bpy.ops.object.mode_set(mode=_mode_lattice)
            # self.report({"INFO"}, _mode_lattice)
            return{"FINISHED"}

        # Unsupported Types
        if active_object.type not in self.supported_types:
            self.report({"INFO"}, "Object type " + str(active_object.type) + " not supported by iOps!")
            return{"FINISHED"}
        return{"FINISHED"}
