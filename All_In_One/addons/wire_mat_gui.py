bl_info = {
    "name": "Setup Wire Materials",
    "autor:" "liero"
    "version": (0, 4, 0),
    "blender": (2, 6, 4),
    "location": "View3D > Tool Shelf",
    "description": "Set up materials for a Wire Render.",
    "category": "Material",
    "url": "http://www.blenderheads.org/forums/es/viewtopic.php?t=932",
}

import bpy

def wire_add(mallas):
    if mallas:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = mallas[0]
        for o in mallas: o.select = True
        bpy.ops.object.duplicate()
        obj, sce = bpy.context.object, bpy.context.scene
        for mod in obj.modifiers: obj.modifiers.remove(mod)
        bpy.ops.object.join()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.wireframe(thickness=0.005)
        bpy.ops.object.mode_set()
        for mat in obj.material_slots: bpy.ops.object.material_slot_remove()
        if 'wire_object' in sce.objects.keys():
            sce.objects.get('wire_object').data = obj.data
            sce.objects.get('wire_object').matrix_world = mallas[0].matrix_world
            sce.objects.unlink(obj)
        else:
            obj.name = 'wire_object'
        obj.data.materials.append(bpy.data.materials.get('mat_wireobj'))

    return{'FINISHED'}

class WireMaterials(bpy.types.Operator):
    bl_idname = 'scene.wire_render'
    bl_label = 'Apply Materials'
    bl_description = 'Set Up Materials for a Wire Render'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = bpy.context.window_manager
        sce = bpy.context.scene

        if 'mat_clay' not in bpy.data.materials:
            mat = bpy.data.materials.new('mat_clay')
            mat.specular_intensity = 0
        else: mat = bpy.data.materials.get('mat_clay')
        mat.diffuse_color = wm.col_clay
        mat.use_shadeless = wm.shadeless_mat

        if 'mat_wire' not in bpy.data.materials:
            mat = bpy.data.materials.new('mat_wire')
            mat.specular_intensity = 0
            mat.use_transparency = True
            mat.type = 'WIRE'
            mat.offset_z = 0.05
        else: mat = bpy.data.materials.get('mat_wire')
        mat.diffuse_color = wm.col_wire
        mat.use_shadeless = wm.shadeless_mat

        try: bpy.ops.object.mode_set()
        except: pass

        if wm.selected_meshes: objetos = bpy.context.selected_objects
        else: objetos = sce.objects

        mallas = [o for o in objetos if o.type == 'MESH' and o.is_visible(sce) and o.name != 'wire_object']

        for obj in mallas:
            sce.objects.active = obj
            print ('procesando >', obj.name)
            obj.show_wire = wm.wire_view
            for mat in obj.material_slots:
                bpy.ops.object.material_slot_remove()
            obj.data.materials.append(bpy.data.materials.get('mat_wire'))
            obj.data.materials.append(bpy.data.materials.get('mat_clay'))
            obj.material_slots.data.active_material_index = 1
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.material_slot_assign()
            bpy.ops.object.mode_set()

        if wm.wire_object:
            if 'mat_wireobj' not in bpy.data.materials:
                mat = bpy.data.materials.new('mat_wireobj')
                mat.specular_intensity = 0
            else: mat = bpy.data.materials.get('mat_wireobj')
            mat.diffuse_color = wm.col_wire
            mat.use_shadeless = wm.shadeless_mat
            wire_add(mallas)

        return{'FINISHED'}

class PanelWMat(bpy.types.Panel):
    bl_label = 'Setup Wire Render'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = bpy.context.window_manager
        layout = self.layout
        layout.operator('scene.wire_render')
        column = layout.column(align=True)
        column.prop(wm, 'col_clay')
        column.prop(wm, 'col_wire')
        column = layout.column(align=True)
        column.prop(wm, 'selected_meshes')
        column.prop(wm, 'shadeless_mat')
        column.label(text='- - - - - - - - - - - - - - - - - - - - - -')
        column.prop(wm, 'wire_view')
        column.prop(wm, 'wire_object')

bpy.types.WindowManager.selected_meshes = bpy.props.BoolProperty(name='Selected Meshes', default=False, description='Apply materials to Selected Meshes / All Visible Meshes')
bpy.types.WindowManager.shadeless_mat = bpy.props.BoolProperty(name='Shadeless', default=False, description='Generate Shadeless Materials')
bpy.types.WindowManager.col_clay = bpy.props.FloatVectorProperty(name='', description='Clay Color', default=(1.0, 0.9, 0.8), min=0, max=1, step=1, precision=3, subtype='COLOR_GAMMA', size=3)
bpy.types.WindowManager.col_wire = bpy.props.FloatVectorProperty(name='', description='Wire Color', default=(0.1 ,0.0 ,0.0), min=0, max=1, step=1, precision=3, subtype='COLOR_GAMMA', size=3)
bpy.types.WindowManager.wire_view = bpy.props.BoolProperty(name='Viewport Wires', default=False, description='Overlay wires display over solid in Viewports')
bpy.types.WindowManager.wire_object = bpy.props.BoolProperty(name='Create Wire Object', default=False, description='Very slow! - Add a Wire Object to scene to be able to render wires in Cycles')

def register():
    bpy.utils.register_class(WireMaterials)
    bpy.utils.register_class(PanelWMat)

def unregister():
    bpy.utils.unregister_class(WireMaterials)
    bpy.utils.unregister_class(PanelWMat)

if __name__ == '__main__':
    register()