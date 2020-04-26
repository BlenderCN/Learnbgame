import bpy

solid_show_overlays = True
material_show_overlays = False
rendered_show_overlays = False
wire_show_overlays = False


class ShadeSolid(bpy.types.Operator):
    bl_idname = "machin3.shade_solid"
    bl_label = "Shade Solid"
    bl_description = "Switch to SOLID shading\nIn SOLID shading mode: Toggle Overlays"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global solid_show_overlays

        overlay = context.space_data.overlay
        shading = context.space_data.shading

        # toggle overlays
        if shading.type == 'SOLID':
            solid_show_overlays = not solid_show_overlays
            overlay.show_overlays = solid_show_overlays

        # change shading to SOLID
        else:
            shading.type = 'SOLID'
            overlay.show_overlays = solid_show_overlays

        return {'FINISHED'}


class ShadeMaterial(bpy.types.Operator):
    bl_idname = "machin3.shade_material"
    bl_label = "Shade Material"
    bl_description = "Switch to MATERIAL shading\nIn MATERIAL shading mode: Toggle Overlays"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global material_show_overlays

        overlay = context.space_data.overlay
        shading = context.space_data.shading

        # toggle overlays
        if shading.type == 'MATERIAL':
            material_show_overlays = not material_show_overlays
            overlay.show_overlays = material_show_overlays

        # change shading to MATERIAL
        else:
            shading.type = 'MATERIAL'
            overlay.show_overlays = material_show_overlays

        return {'FINISHED'}


class ShadeRendered(bpy.types.Operator):
    bl_idname = "machin3.shade_rendered"
    bl_label = "Shade Rendered"
    bl_description = "Switch to RENDERED shading\nIn RENDERED shading mode: Toggle Overlays"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global rendered_show_overlays

        overlay = context.space_data.overlay
        shading = context.space_data.shading

        # toggle overlays
        if shading.type == 'RENDERED':
            rendered_show_overlays = not rendered_show_overlays
            overlay.show_overlays = rendered_show_overlays

        # change shading to RENDERED
        else:
            shading.type = 'RENDERED'
            overlay.show_overlays = rendered_show_overlays

        return {'FINISHED'}


class ShadeWire(bpy.types.Operator):
    bl_idname = "machin3.shade_wire"
    bl_label = "Shade Wire"
    bl_description = "Switch to WIRE shading\nIn WIRE shading mode: Toggle Overlays"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global wire_show_overlays

        overlay = context.space_data.overlay
        shading = context.space_data.shading

        # toggle overlays
        if shading.type == 'WIREFRAME':
            wire_show_overlays = not wire_show_overlays
            overlay.show_overlays = wire_show_overlays

        # change shading to WIRE
        else:
            shading.type = 'WIREFRAME'
            overlay.show_overlays = wire_show_overlays

        return {'FINISHED'}
