import bpy
import copy
import bmesh
import math
import numpy as np
from mathutils import Matrix, Vector
from .utils.helper_functions import link_to_collection_sibling, get_scale_mat, set_parent, clear_parent


class ProjectObjectProps(bpy.types.PropertyGroup):
    def unbind_grid(self, context):
        bpy.ops.object.unbind_projection()
        if self.projected_obj.name+"_grid" in bpy.data.objects.keys():
            create_grid()

    projected_obj: bpy.props.PointerProperty(name="Projected Obj",description="Usually pocket mesh that will be projected on garment", type=bpy.types.Object)
    projection_target: bpy.props.PointerProperty(name="Target", description="Garment mesh with baked shape key sim, that we want to project pockets onto",  type=bpy.types.Object)
    relaxStrength: bpy.props.IntProperty(name="Smooth Strength", description="Smooth Strength - helps prevent abrupt changes in geometry \n"\
                                                                            "especially when target is much denser than source object", default=2, min = 0, soft_max = 20)
    usePinBoundary: bpy.props.BoolProperty(name="Pin boundary", description="Pin boundary", default=True)
    grid_resolution: bpy.props.IntProperty(name="Grid Resolution", description="Grid Resolution - bigger = more accureate projection", default=10, min=5, soft_max=20, update=unbind_grid)


class GTOOL_OT_ObjectPicker(bpy.types.Operator):
    bl_idname = "object.gt_objectpicker"
    bl_label = "Pick Obj"

    targetPropName:  bpy.props.StringProperty()

    def execute(self, context):
        shape_project = context.scene.shape_project
        if context.active_object:
            shape_project[self.targetPropName] = context.active_object
        return {'FINISHED'}

class GTOOL_PT_ShapeProjectPanel(bpy.types.Panel):
    bl_idname = "GTOOL_PT_ShapeProjectPanel"
    bl_label = "Bind Project"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Garment'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "objectmode"

    def draw(self, context):
        shape_project = context.scene.shape_project
        layout = self.layout

        # row = layout.row(align=True)
        # row.prop(shape_project, 'projected_obj')
        # row.operator('object.gt_objectpicker', text='', icon='EYEDROPPER').targetPropName = 'projected_obj'

        row = layout.row(align=True)
        row.prop(shape_project, 'projection_target')
        row.operator('object.gt_objectpicker', text='', icon='EYEDROPPER').targetPropName = 'projection_target'

        row = layout.row(align=True)
        row.prop(shape_project,"relaxStrength")
        row.prop(shape_project,"grid_resolution")


        row = layout.row(align=True)
        row.prop(shape_project, "usePinBoundary", text="", icon_only=True, emboss=True, icon='LOCKED')
        row.operator("object.shape_project")
        row.operator("object.unbind_projection")


def get_grid_deform_matrix(projected_obj):
    ''' return (center, sizex, sizey, sizez) '''
    points = [v.co for v in projected_obj.data.vertices]

    np_points = np.array(points)
    max_x = np.max(np_points[:, 0])
    max_y = np.max(np_points[:, 1])
    max_z = np.max(np_points[:, 2])
    min_x = np.min(np_points[:, 0])
    min_y = np.min(np_points[:, 1])
    min_z = np.min(np_points[:, 2])

    # center = Vector((max_x+min_x, max_y+min_y, max_z+min_z)) * 0.5
    vec_scale = Vector((max(max_x-min_x, 0.1), max(max_z-min_z, 0.1), max(max_y-min_y, 0.1))) * 6/10
    mat_sca = get_scale_mat(vec_scale)

    mat_rot = Matrix.Rotation(math.radians(90.0), 4, 'X')
    mat_loc = Matrix.Translation(((max_x+min_x)/2, max_y, (max_z+min_z)/2))
    # mat_rot = projected_obj[0].matrix_world.to_quaternion().to_matrix().to_4x4()

    mesh_matrix = mat_sca
    grid_matrix_world = mat_loc @ mat_rot

    return (grid_matrix_world, mesh_matrix, vec_scale)

def create_grid(initialize = False):
    shape_project = bpy.context.scene.shape_project
    projected_obj = shape_project.projected_obj
    me = bpy.data.meshes.new(projected_obj.name+"_grid")  # add a new mesh
    if projected_obj.name+"_grid" in bpy.data.objects.keys():
        grid_obj = bpy.data.objects[projected_obj.name+"_grid"]
        grid_obj.data = me
    else:
        grid_obj = bpy.data.objects.new(projected_obj.name+"_grid", me)  # add a new object using the mesh
    bm = bmesh.new()  # create an empty BMesh

    (grid_matrix_world, mesh_matrix, vec_scale) = get_grid_deform_matrix(projected_obj)

    res_ratio = vec_scale.y/vec_scale.x
    bmesh.ops.create_grid(bm, x_segments=shape_project.grid_resolution, y_segments=shape_project.grid_resolution*res_ratio, size=1, matrix=mesh_matrix, calc_uvs=False)
    bm.to_mesh(me)
    bm.free()  # free and prevent further access
    me.transform(grid_matrix_world)
    link_to_collection_sibling(projected_obj, grid_obj)
    # bpy.context.scene.collection.objects.link(grid_obj)
    if initialize:
        grid_obj.matrix_world = projected_obj.matrix_world 
    grid_obj.show_wire = True
    grid_obj.display_type = 'WIRE'
    grid_obj.show_all_edges = True
    grid_obj.data.update()
    grid_obj.update_from_editmode()
    return grid_obj

class GTOOL_OT_BindProject(bpy.types.Operator):
    bl_idname = "object.shape_project"
    bl_label = "Bind to target"
    bl_description = "Project and bind selected object to target"
    bl_options = {"REGISTER", "UNDO"}

    shift_clicked = False

    @classmethod
    def poll(cls, context):
        shape_project = context.scene.shape_project
        act_obj = context.active_object
        return act_obj and act_obj != shape_project.projection_target and context.mode == "OBJECT"

    def invoke(self, context, event):
        if event.shift:
            self.shift_clicked = True
        return self.execute(context)

    def execute(self, context):
        shape_project = context.scene.shape_project
        deformer_obj = shape_project.projection_target
        if context.active_object.name.endswith('_grid'):
            projected_obj = context.active_object.children[0]
        else:
            projected_obj = context.active_object
        backup_active_obj = context.active_object
        shape_project.projected_obj = projected_obj
        if projected_obj is None:
            self.report({'ERROR'}, 'Select projected object! Cancelling')
            return {'CANCELLED'}
        elif projected_obj.type != 'MESH':
            self.report({'ERROR'}, 'Select projection object is not mesh! Cancelling')
            return {'CANCELLED'}
        if deformer_obj is None:
            self.report({'ERROR'}, 'Select projection target object first! Cancelling')
            return {'CANCELLED'}
        bpy.ops.object.unbind_projection()#to force refresh
        back_show_only_shape_key = deformer_obj.show_only_shape_key
        deformer_obj.show_only_shape_key = True
        active_shape_id_backup = deformer_obj.active_shape_key_index
        deformer_obj.active_shape_key_index = 0
        hidden_mods = []
        for mod in deformer_obj.modifiers: #so that we snap to flatttened version of deformer (cloth)
            if mod.show_viewport:
                mod.show_viewport = False
                hidden_mods.append(mod.name)
        context.scene.update()

        if 'Surface Deform By Grid' not in projected_obj.modifiers.keys():
            deform_by_grid_mod = projected_obj.modifiers.new(name='Surface Deform By Grid', type='SURFACE_DEFORM')
        else:
            deform_by_grid_mod = projected_obj.modifiers['Surface Deform By Grid']

        grid_obj = deform_by_grid_mod.target
        if grid_obj is None or grid_obj.name != projected_obj.name+"_grid": #fixes grid mesh, if it was linked to eg. bad grid mesh (with different name)
            clear_parent(projected_obj)  # cos generated grid will use projected_obj.matrix_world
            context.scene.update() #to refersh the clear parent and matrix above
            grid_obj = create_grid(True)
            deform_by_grid_mod.target = grid_obj
            deform_by_grid_mod.falloff = 2
            set_parent(projected_obj, grid_obj)
            projected_obj.matrix_parent_inverse @= grid_obj.matrix_world.inverted()  # we did  @ projected_obj.matrix_parent on grid, so negate it
        deform_by_grid_mod.show_viewport = True
        
        context.view_layer.objects.active = projected_obj
        if deform_by_grid_mod.is_bound: #unbind - to refresh
            bpy.ops.object.surfacedeform_bind(modifier='Surface Deform By Grid')
        bpy.ops.object.surfacedeform_bind(modifier='Surface Deform By Grid')

        
        if 'Smooth Projection' not in projected_obj.modifiers.keys():
            corr_smooth_mod = projected_obj.modifiers.new(name='Smooth Projection', type='CORRECTIVE_SMOOTH')
        else:
            corr_smooth_mod = projected_obj.modifiers['Smooth Projection']

        corr_smooth_mod.smooth_type = 'LENGTH_WEIGHTED'
        corr_smooth_mod.iterations = shape_project.relaxStrength
        corr_smooth_mod.rest_source = 'BIND'
        corr_smooth_mod.use_pin_boundary = context.scene.shape_project.usePinBoundary
        corr_smooth_mod.show_viewport = True

        # override = {'active_object': projected_obj, 'selected_objects': [projected_obj], 'selected_editable_objects': [projected_obj]}
        context.view_layer.objects.active = projected_obj
        if not corr_smooth_mod.is_bind: 
            bpy.ops.object.correctivesmooth_bind(modifier="Smooth Projection")  # TODO: report bug that it won't update mod state.


        #Setup Grid obj - shrink to deformer, and bind surfance deform
        if 'Shrink Grid To Target' not in grid_obj.modifiers.keys():
            grid_shrink_to_cloth_mod = grid_obj.modifiers.new(name='Shrink Grid To Target', type='SHRINKWRAP')
        else:
            grid_shrink_to_cloth_mod = grid_obj.modifiers['Shrink Grid To Target']

        grid_obj.modifiers['Shrink Grid To Target'].show_viewport = True
        grid_shrink_to_cloth_mod.target = deformer_obj
        grid_shrink_to_cloth_mod.wrap_method = 'PROJECT'
        grid_shrink_to_cloth_mod.use_negative_direction = True


        if 'Grid Deform By Target' not in grid_obj.modifiers.keys():
            grid_bind_to_cloth = grid_obj.modifiers.new(name='Grid Deform By Target', type='SURFACE_DEFORM')
        else:
            grid_bind_to_cloth = grid_obj.modifiers['Grid Deform By Target']
        grid_bind_to_cloth.falloff = 2
        grid_bind_to_cloth.target = deformer_obj
        grid_bind_to_cloth.show_viewport = True

        # override = {'active_object': grid_obj, 'selected_objects': [grid_obj], 'selected_editable_objects': [grid_obj]}
        context.view_layer.objects.active = grid_obj
        if grid_bind_to_cloth.is_bound: #toogle to refresh
            bpy.ops.object.surfacedeform_bind(modifier='Grid Deform By Target')
        bpy.ops.object.surfacedeform_bind(modifier='Grid Deform By Target')
        
        #restore things
        for mod in deformer_obj.modifiers:
            if mod.name in hidden_mods:
                mod.show_viewport = True
        deformer_obj.show_only_shape_key = back_show_only_shape_key
        deformer_obj.active_shape_key_index = active_shape_id_backup
        context.view_layer.objects.active = backup_active_obj
        return {"FINISHED"}


class GTOOL_OT_UnBindProjection(bpy.types.Operator):
    bl_idname = "object.unbind_projection"
    bl_label = "Unbind"
    bl_description = "Unbind projection. Shift click to unbind all projected objects"
    bl_options = {"REGISTER","UNDO"}

    shift_clicked = False

    @classmethod
    def poll(cls, context):
        return context.active_object
    
    def invoke(self, context, event):
        if event.shift:
            self.shift_clicked = True
        return self.execute(context)

    def execute(self, context):
        shape_project = context.scene.shape_project
        backup_active_obj = context.active_object
        if self.shift_clicked:
            objs = [obj for obj in context.scene.objects if obj.name.endswith('_grid') and obj.type == 'MESH']
        else:
            objs = [context.active_object]

        def disable_grid_obj(grid_obj):
            grid_obj.modifiers['Shrink Grid To Target'].show_viewport = False
            if 'Grid Deform By Target' in grid_obj.modifiers.keys():
                if grid_obj.modifiers['Grid Deform By Target'].is_bound:  # unbound
                    context.view_layer.objects.active = grid_obj
                    bpy.ops.object.surfacedeform_bind(modifier='Grid Deform By Target')

        for obj in objs:
            if obj.name.endswith('_grid'):
                projected_obj = obj.children[0] if obj.children and obj.children[0].name in context.scene.objects.keys() else None
                disable_grid_obj(obj)  # assume it is the grid we created
            else:
                projected_obj = obj
            shape_project.projected_obj = projected_obj
            if projected_obj is None:
                print('No projected object! Skipping')
                continue
            elif projected_obj.type != 'MESH':
                print('Select projection object is not mesh! Cancelling')
                continue

            if 'Surface Deform By Grid' in projected_obj.modifiers.keys():
                grid_obj = projected_obj.modifiers['Surface Deform By Grid'].target
                if grid_obj:
                    disable_grid_obj(grid_obj)
            
            if 'Surface Deform By Grid' in projected_obj.modifiers.keys():
                if projected_obj.modifiers['Surface Deform By Grid'].is_bound:
                    # override = {'active_object': projected_obj, 'selected_objects': [projected_obj]}
                    context.view_layer.objects.active = projected_obj
                    bpy.ops.object.surfacedeform_bind(modifier='Surface Deform By Grid')

            if 'Smooth Projection' in projected_obj.modifiers.keys():
                if projected_obj.modifiers['Smooth Projection'].is_bind:
                    # override = {'active_object': projected_obj, 'selected_objects': [projected_obj]}
                    context.view_layer.objects.active = projected_obj
                    bpy.ops.object.correctivesmooth_bind(modifier="Smooth Projection")
        context.view_layer.objects.active = backup_active_obj

        return {"FINISHED"}

