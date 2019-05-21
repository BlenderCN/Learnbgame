# Several operators useful in dynamic topology sculpting:

# Smooth - applies one iteration of vertex smoothing to unmasked area
# Subdivide - subdivides unmasked polygons
# Subdivide Smooth - subdivides unmasked polygons with smooth factor of 1
#
# NOTE: Undo functionality is supported, but a bit awkward: you'll
# have to undo several times to get your unmodified mesh back
# This is due to sculpt mode having separate undo stack
bl_info = {
    "name": "Sculpt Geometry Tools",
    "author": "Stanislav Blinov",
    "version": (1, 0),
    "blender": (2, 71, 0),
    "location": "View3D > Tool Shelf > Sculpt > Geometry",
    "description": "Apply edit mode operations in sculpt mode",
    "warning": "",
    "wiki_url": "",
    "category": "Sculpting"
}

import bpy

#
# Base classes
#

# Base class for edit mode operators
class SculptEditBase(bpy.types.Operator):
    bl_idname = "sculpt.geometry_edit_base"
    bl_label = "NONE"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.mode == 'SCULPT' \
               and "Multires" not in context.active_object.modifiers

    def execute(self, context):
        wm = context.window_manager
        activeObj = context.active_object

        dyntopo = activeObj.use_dynamic_topology_sculpting

        # Deselect everything in edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.mesh.select_all(action='DESELECT')
        # Hide masked area
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='HIDE', area='MASKED')

        bpy.ops.object.mode_set(mode='EDIT')
        result = {'CANCELLED'}
        try:
            result = self.apply(context)
        finally:
            # Reveal masked area
            bpy.ops.object.mode_set(mode='SCULPT')
            bpy.ops.paint.hide_show(action='SHOW', area='MASKED')
            if dyntopo:
                bpy.ops.sculpt.dynamic_topology_toggle()

        return result

# Base class for operators that apply modifiers
class SculptModifierOperator(bpy.types.Operator):
    bl_idname = "sculpt.geometry_modifier_base"
    bl_label = "NONE"
    bl_options = {'INTERNAL'}

    vgroup_name = "__sculptunmaskedverts"

    md = None
    vg = None
    dyntopo = False

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.mode == 'SCULPT' \
               and 'Multires' not in context.active_object.modifiers

    def create_modifier(self, context):
        pass

    def setup_modifier(self, context):
        pass

    def draw(self, context):
        pass

    def execute(self, context):
        bpy.ops.object.modifier_apply(modifier=self.md.name)
        self.cleanup(context)
        return {'FINISHED'}

    def check(self, context):
        return True

    def cancel(self, context):
        bpy.ops.object.modifier_remove(modifier=self.md.name)
        self.cleanup(context)

    def invoke(self, context, event):
        ob = context.active_object
        try:
            self.dyntopo = ob.use_dynamic_topology_sculpting

            self.vg = ob.vertex_groups.new(self.vgroup_name)
            bpy.ops.object.vertex_group_set_active(group=self.vg.name)
            # Deselect everything in edit mode
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_remove_from()
            bpy.ops.mesh.normals_make_consistent()
            bpy.ops.mesh.select_all(action='DESELECT')
            # Hide masked area
            bpy.ops.object.mode_set(mode='SCULPT')
            bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
            # Select everything (i.e. not masked)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='FACE')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_assign()
            bpy.ops.mesh.select_all(action='DESELECT')
            # Reveal masked area
            bpy.ops.object.mode_set(mode='SCULPT')
            bpy.ops.paint.hide_show(action='SHOW', area='MASKED')

            self.create_modifier(context)
            self.setup_modifier(context)

            return context.window_manager.invoke_props_dialog(self)
        except:
            return {'CANCELLED'}

    def cleanup(self, context):
        bpy.ops.object.vertex_group_set_active(group=self.vg.name)
        bpy.ops.object.vertex_group_remove()
        if self.dyntopo:
            bpy.ops.sculpt.dynamic_topology_toggle()
        self.md = None
        self.vg = None


class SculptEditBeautifyOperator(SculptEditBase):
    """Applies beautify fill to non-masked faces"""
    bl_idname = "sculpt.geometry_beautify_faces"
    bl_label = "Beautify"
    bl_options = {'REGISTER'}

    def apply(self, context):
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.beautify_fill()
        bpy.ops.mesh.select_all(action='DESELECT')
        return {'FINISHED'}

class SculptEditSmoothOperator(SculptEditBase):
    """Applies smoothing to non-masked vertices"""
    bl_idname = "sculpt.geometry_smooth_vertices"
    bl_label = "Smooth"
    bl_options = {'REGISTER'}

    def apply(self, context):
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.vertices_smooth()
        bpy.ops.mesh.select_all(action='DESELECT')
        return {'FINISHED'}

class SculptSubdivideOperator(SculptEditBase):
    """Subdivides non-masked faces"""
    bl_idname = "sculpt.geometry_subdivide_faces"
    bl_label = "Subdivide"
    bl_options = {'REGISTER'}

    def apply(self, context):
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.subdivide()
        bpy.ops.mesh.select_all(action='DESELECT')
        return {'FINISHED'}

class SculptSubdivideSmoothOperator(SculptEditBase):
    """Subdivides non-masked faces"""
    bl_idname = "sculpt.geometry_subdivide_faces_smooth"
    bl_label = "Subdivide Smooth"
    bl_options = {'REGISTER'}

    def apply(self, context):
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.subdivide(smoothness=1.0)
        bpy.ops.mesh.select_all(action='DESELECT')
        return {'FINISHED'}



class SculptDecimateOperator(SculptModifierOperator):
    """Decimate faces"""
    bl_idname = "sculpt.geometry_decimate"
    bl_label = "Decimate"
    bl_options = {'REGISTER'}

    modifier_name = "__sculptdecimate"

    def create_modifier(self, context):
        self.md = context.active_object.modifiers.new(self.modifier_name, 'DECIMATE')

    def setup_modifier(self, context):
        self.md.vertex_group = self.vg.name
        self.md.use_collapse_triangulate = True

    def draw(self, context):
        layout = self.layout

        # Plagiarized from Blender's UI code
        # (properties_data_modifier.py)
        row = layout.row()
        row.prop(self.md, "decimate_type", expand=True)

        decimate_type = self.md.decimate_type

        if decimate_type == 'COLLAPSE':
            layout.prop(self.md, "ratio")
        elif decimate_type == 'UNSUBDIV':
            layout.prop(self.md, "iterations")
        else:  # decimate_type == 'DISSOLVE':
            layout.prop(self.md, "angle_limit")
            layout.prop(self.md, "use_dissolve_boundaries")
            layout.label("Delimit:")
            row = layout.row()
            row.prop(self.md, "delimit")

        layout.label(text=("Face Count: %d") % self.md.face_count, translate=False)

class SculptSmoothOperator(SculptModifierOperator):
    """Smooth vertices"""
    bl_idname = "sculpt.geometry_smooth"
    bl_label = "Smooth"
    bl_options = {'REGISTER'}

    modifier_name = "__sculptsmooth"

    def create_modifier(self, context):
        self.md = context.active_object.modifiers.new(self.modifier_name, 'SMOOTH')

    def setup_modifier(self, context):
        self.md.vertex_group = self.vg.name

    def draw(self, context):
        layout = self.layout

        # Plagiarized from Blender's UI code
        # (properties_data_modifier.py)
        split = layout.split(percentage=0.25)

        col = split.column()
        col.label(text="Axis:")
        col.prop(self.md, "use_x")
        col.prop(self.md, "use_y")
        col.prop(self.md, "use_z")

        col = split.column()
        col.prop(self.md, "factor")
        col.prop(self.md, "iterations")

class SculptLaplacianSmoothOperator(SculptModifierOperator):
    """Laplacian Smooth"""
    bl_idname = "sculpt.geometry_laplacian_smooth"
    bl_label = "Laplacian Smooth"
    bl_options = {'REGISTER'}

    modifier_name = "__sculptlaplaciansmooth"

    def create_modifier(self, context):
        self.md = context.active_object.modifiers.new(self.modifier_name, 'LAPLACIANSMOOTH')

    def setup_modifier(self, context):
        self.md.vertex_group = self.vg.name

    def draw(self, context):
        layout = self.layout

        # Plagiarized from Blender's UI code
        # (properties_data_modifier.py)
        layout.prop(self.md, "iterations")

        split = layout.split(percentage=0.25)

        col = split.column()
        col.label(text="Axis:")
        col.prop(self.md, "use_x")
        col.prop(self.md, "use_y")
        col.prop(self.md, "use_z")

        col = split.column()
        col.label(text="Lambda:")
        col.prop(self.md, "lambda_factor", text="Factor")
        col.prop(self.md, "lambda_border", text="Border")

        col.separator()
        col.prop(self.md, "use_volume_preserve")
        col.prop(self.md, "use_normalized")

class SculptDisplaceModifier(SculptModifierOperator):
    """Displace geometry"""
    bl_idname = "sculpt.geometry_displace"
    bl_label = "Displace"
    bl_options = {'REGISTER'}

    modifier_name = "__sculptdisplace"

    def create_modifier(self, context):
        self.md = context.active_object.modifiers.new(self.modifier_name, 'DISPLACE')

    def setup_modifier(self, context):
        self.md.vertex_group = self.vg.name

    def draw(self, context):
        layout = self.layout
        ob = context.active_object

        # Plagiarized from Blender's UI code
        # (properties_data_modifier.py)
        has_texture = (self.md.texture is not None)

        col = layout.column(align=True)
        col.label(text="Texture:")
        col.template_ID(self.md, "texture")

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Direction:")
        col.prop(self.md, "direction", text="")

        col = split.column(align=True)
        col.active = has_texture
        col.label(text="Texture Coordinates:")
        col.prop(self.md, "texture_coords", text="")
        if self.md.texture_coords == 'OBJECT':
            col.label(text="Object:")
            col.prop(self.md, "texture_coords_object", text="")
        elif self.md.texture_coords == 'UV' and ob.type == 'MESH':
            col.label(text="UV Map:")
            col.prop_search(self.md, "uv_layer", ob.data, "uv_textures", text="")

        layout.separator()

        row = layout.row()
        row.prop(self.md, "mid_level")
        row.prop(self.md, "strength")

class SculptGeometryPanel(bpy.types.Panel):
    """UI panel for the various Sculpt->Edit->Sculpt buttons"""
    bl_label = "Geometry"
    bl_idname = "OBJECT_PT_sculpt_geometry"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Sculpt'

    def draw(self, context):
        layout = self.layout

        # Smooth
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("sculpt.geometry_smooth", text="Smooth")

        # Laplacian Smooth
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("sculpt.geometry_laplacian_smooth", text="Laplacian Smooth")

        # Decimate
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("sculpt.geometry_decimate", text="Decimate")

        # Displace
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("sculpt.geometry_displace", text="Displace")

        # Subdivide
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("sculpt.geometry_subdivide_faces", text="Subdivide")

        # Subdivide Smooth
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("sculpt.geometry_subdivide_faces_smooth", text="Subdivide Smooth")

        # Beautify
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("sculpt.geometry_beautify_faces", text="Beautify")


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

