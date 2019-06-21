import bpy
import bmesh


bpy.types.Object.exportutil_material_name = bpy.props.StringProperty(
        name="Material Name", default="", description="Material Name for Export")


#class NoopOp(bpy.types.Operator):
#    bl_idname = "object.noopop"
#    bl_label = "noop op"
#
#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None
#
#    def execute(self, context):
#        self.report({"INFO"}, "not implemented yet")
#        return {"FINISHED"}


class RecordFaceSpecificMaterial(bpy.types.Operator):
    bl_idname = "object.exportutil_record_face_specific_material"
    bl_label = "Record Face Specific Material"
    bl_description = "Record the Face Specific Material in Custom Face Property Layer"

    @classmethod
    def poll(cls, context):
        return (context.object.mode == "OBJECT"
                and len(context.selected_objects) > 0)

    def execute(self, context):
        for ob in context.selected_objects:
            record_face_specific_material_in_custom_prop_layer(ob, self.report)

        return {"FINISHED"}


def record_face_specific_material_in_custom_prop_layer(ob, report):
    if ob.type != "MESH":
        report({"INFO"}, "Ignored: {}".format(ob.name))
        return

    if len(ob.data.materials) == 0:
        report({"INFO"}, "Material not Used: {}".format(ob.name))
        return

    bm = bmesh.new()
    bm.from_mesh(ob.data)

    material_name_layer = bm.faces.layers.string.get("material_name")
    if material_name_layer is None:
        material_name_layer = bm.faces.layers.string.new("material_name")
    #print("material_name_layer", material_name_layer)

    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        face_material = ob.data.materials[f.material_index]
        if face_material is None:
            matname = ""
        else:
            matname = face_material.name
        #print("matname:", matname)
        bm.faces[f.index][material_name_layer] = matname.encode()
        #print(">", f.index, f.material_index, bm.faces[f.index][material_name_layer].decode())

    bm.to_mesh(ob.data)
    bm.free()


class RestoreFaceSpecificMaterial(bpy.types.Operator):
    bl_idname = "object.exportutil_restore_face_specific_material"
    bl_label = "Restore Face Specific Material"
    bl_description = "Restore the Face Specific Material from Custom Face Property Layer"

    @classmethod
    def poll(cls, context):
        return (context.object.mode == "OBJECT"
                and len(context.selected_objects) > 0)

    def execute(self, context):
        for ob in context.selected_objects:
            restore_face_specific_material_from_custom_prop_layer(ob, self.report)

        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

        return {"FINISHED"}


def restore_face_specific_material_from_custom_prop_layer(ob, report):
    if ob.type != "MESH":
        report({"INFO"}, "Ignored: {}".format(ob.name))
        return

    #if len(ob.data.materials) == 0:
    #    report({"INFO"}, "Material not Used: {}".format(ob.name))
    #    return

    bm = bmesh.new()
    bm.from_mesh(ob.data)

    material_name_layer = bm.faces.layers.string.get("material_name")
    if material_name_layer is None:
        material_name_layer = bm.faces.layers.string.new("material_name")
    print("material_name_layer", material_name_layer)

    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        matname = bm.faces[f.index][material_name_layer].decode()
        idx = ob.data.materials.find(matname)
        if idx == -1:
            pass
        else:
            f.material_index = idx

    bm.to_mesh(ob.data)
    bm.free()


class AssignMaterialForExport(bpy.types.Operator):
    bl_idname = "object.exportutil_assign_material_for_export"
    bl_label = "Assign Material for Export"
    bl_description = "Assign Material for Export"

    @classmethod
    def poll(cls, context):
        return (context.object.mode == "OBJECT"
                and len(context.selected_objects) > 0)

    def execute(self, context):
        for ob in context.selected_objects:
            assign_material_for_export(ob, self.report)

        return {"FINISHED"}


def assign_material_for_export(ob, report):
    if ob.type != "MESH":
        report({"INFO"}, "Ignored: {}".format(ob.name))
        return

    mat_name = ob.name
    if (hasattr(ob, "exportutil_material_name")
            and ob.exportutil_material_name != ""):
        mat_name = ob.exportutil_material_name

    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)

    mat_idx = ob.data.materials.find(mat_name)
    if mat_idx == -1:
        ob.data.materials.append(mat)
        mat_idx = ob.data.materials.find(mat_name)

    for poly in ob.data.polygons:
        poly.material_index = mat_idx


class ExportUtilCustomPanel(bpy.types.Panel):
    bl_label = "Export Utility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object
        col = layout.column(align=True)
        col.operator(RecordFaceSpecificMaterial.bl_idname, text="Record Face Specific Material")
        #col.operator(NoopOp.bl_idname, text="Bake Face Vertex Color (for ID Map)")
        col = layout.column(align=True)
        col.prop(active_object, "exportutil_material_name", text="Material Name")
        col.operator(AssignMaterialForExport.bl_idname, text="Assign Material for Export")
        col = layout.column(align=True)
        col.operator(RestoreFaceSpecificMaterial.bl_idname, text="Restore Face Specific Material")
