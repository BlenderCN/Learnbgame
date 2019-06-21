#importdefs
import bpy
from g_tools.bpy_itfc_funcs import mesh_fs
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty 
from bpy.types import Operator

#fdef


#opdef
class bool_cut_select_op(bpy.types.Operator):
    """NODESC"""
    bl_idname = "mesh.bool_cut_select"
    bl_label = "Bool Cut Select"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category ="Tools"
    bl_options = {'UNDO','REGISTER'}
    



    def execute(self, context):
        mesh_fs.bool_cut_select()
        return {'FINISHED'}
class basis_swap_op(bpy.types.Operator):
    """Basis shape key management"""
    bl_idname = "mesh.basis_swap"
    bl_label = "Basis Swap"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category ="Tools"
    bl_options = {'UNDO','REGISTER'}
    



    def execute(self, context):
        mesh_fs.basis_swap()
        return {'FINISHED'}
        
class w_mirror_op(bpy.types.Operator):
    """ウェイトの鏡像化"""
    bl_idname = "mesh.w_mirror"
    bl_label = "Weight mirror"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_options = {'UNDO', 'REGISTER'}

    scale = bpy.props.FloatProperty(default=1.0)
    precision = bpy.props.IntProperty(default=4)
    target_shape_key_index = bpy.props.IntProperty(default=0)
    use_active_shape_key = bpy.props.BoolProperty(default=False)
    do_clear = bpy.props.BoolProperty(description = "Clear original weights on mirror targets",default=True)
    '''
    type = EnumProperty(
            name="Mirroring type",
            description="Choose mirroring type",
            items=(('l>r', "Left to right", "Mirror from left to right"),
                   ('l<r', "Right to left", "Mirror from right to left"),
                   ('both', "Both", "Mirror across both sides")),
            default='both',
            )
    '''

    def execute(self, context):
        mesh_fs.mirror_weights_exec(scale = self.scale, precision = self.precision, do_clear = self.do_clear, target_shape_key_index = self.target_shape_key_index, use_active_shape_key = self.use_active_shape_key,oper = self)
        return {'FINISHED'}

class mirror_sel_op(bpy.types.Operator):
    """機能が拡張（？）された頂点の鏡像選択"""
    bl_idname = "mesh.mirror_sel"
    bl_label = "Alternative mirror select"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_options = {'UNDO', 'REGISTER'}

    extend = bpy.props.BoolProperty(default=True)
    basis = bpy.props.BoolProperty(default=True)
    target_shape_key_index = bpy.props.IntProperty(default=0)
    use_active_shape_key = bpy.props.BoolProperty(default=False)
    cutoff = bpy.props.FloatProperty(description = "Middle cutoff",default=0.001)
    scale = bpy.props.FloatProperty(default=1.0)
    precision = bpy.props.IntProperty(default=4)
    type = EnumProperty(
            name="Mirroring type",
            description="Choose mirroring type",
            items=(('l>r', "Left to right", "Mirror from left to right"),
                   ('l<r', "Right to left", "Mirror from right to left"),
                   ('both', "Both", "Mirror across both sides")),
            default='both',
            )

    def execute(self, context):
        mesh_fs.mirror_sel(cutoff = self.cutoff, scale = self.scale, precision = self.precision, type = self.type, extend = self.extend, target_shape_key_index = self.target_shape_key_index, use_active_shape_key = self.use_active_shape_key)
        return {'FINISHED'}

class selectorator_op(bpy.types.Operator):
    """NODESC"""
    bl_idname = "mesh.selectorator"
    bl_label = "Selectorator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category ="Tools"
    bl_options = {'UNDO','REGISTER'}
    
    modes = ("cross_loops","chain_loop","3d_cursor","lattice_loop","dot","vector","index")
    def make_enum_data(modes):
        lenmodes = len(modes)
        names = tuple(" ".join(map(lambda n: (n[0].upper() + n[1::]),n.split("_"))) for n in modes)
        tooltips = tuple(names)
        enum_data = tuple(map(lambda i: (modes[i],names[i],tooltips[i]),range(lenmodes)))
        return enum_data
    selection_mode = bpy.props.EnumProperty(name = "Selection type",items = make_enum_data(modes))
    
    '''
    selection_mode = bpy.props.EnumProperty(name = "Value type to pass",items = (
    ('cross_loops','Vertices','Vertices'),
    ('e','Edges','Edges'),
    ('f','Faces','Faces'),
    ('spl','Splines','Splines'),
    ('fpts','First spline\'s points','First spline\'s points'),
    ('obn','Object bones','Armature object\'s object mode bones'),
    ('pbn','Pose bones','Armature object\'s pose mode bones'),
    ('ebn','Edit bones','Armature object\'s edit mode bones'),))
    '''
    #selection_mode = bpy.props.StringProperty(description = 'Selection type',default = "cross_loops")
    index_count = bpy.props.IntProperty(description = 'Count for index select',default = 50)
    index_offset = bpy.props.IntProperty(description = 'Offset for index select',default = 0)
    index_step = bpy.props.IntProperty(description = 'Step for index and cross select',default = 1)
    lattice_reverse = bpy.props.BoolProperty(description = 'Reverse lattice select direction',default = False)
    lattice_limit = bpy.props.BoolProperty(description = 'Limit lattice loop select to lattice bounds',default = False)

    index_part_type = bpy.props.EnumProperty(name = "Value type to pass",items = (
    ('v','Vertices','Vertices'),
    ('e','Edges','Edges'),
    ('f','Faces','Faces'),
    ('spl','Splines','Splines'),
    ('fpts','First spline\'s points','First spline\'s points'),
    ('obn','Object bones','Armature object\'s object mode bones'),
    ('pbn','Pose bones','Armature object\'s pose mode bones'),
    ('ebn','Edit bones','Armature object\'s edit mode bones'),))

    lattice_step_direction = bpy.props.EnumProperty(name = "Axis for lattice loop select",items = (
    ('x','X','X'),
    ('y','Y','Y'),
    ('z','Z','Z'),
    ))

    def execute(self, context):
        check_dict = {i:"MESH" for i in self.modes}
        check_dict.update({"lattice_loop":"LATTICE",})
        mesh_fs.selectorate(
        selection_mode = self.selection_mode,
        index_count = self.index_count,
        index_step = self.index_step,
        index_offset = self.index_offset,
        index_part_type = self.index_part_type,
        lattice_step_direction = self.lattice_step_direction,
        lattice_reverse = self.lattice_reverse,
        lattice_limit = self.lattice_limit,
        check_dict = check_dict,
        oper = self)
        return {'FINISHED'}
        
#opdef
class clean_vertex_groups_op(bpy.types.Operator):
    """頂点グループ欄を見やすくする為にウェイト情報がない頂点グループをメッシュから削除する"""
    bl_idname = "mesh.sclean_vertex_groups"
    bl_label = "Clean vertex groups"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        mesh_fs.clean_vertex_groups()
        return {'FINISHED'}

#opdef
class parts_to_vgroups_op(bpy.types.Operator):
    """メッシュのパーツそれぞれを頂点グループとして登録する"""
    bl_idname = "mesh.parts_to_vgroups"
    bl_label = "Parts to vertex groups"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_options = {'UNDO', 'REGISTER'}

    vg_name = bpy.props.StringProperty(default="part_group_")

    def execute(self, context):
        mesh_fs.parts_to_vgroups(vg_name = self.vg_name)
        return {'FINISHED'}

class GMeshPanel(bpy.types.Panel):
    """Creates a Panel in the 3D View"""
    bl_label = "GMesh"    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "G Tools"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        row = layout.row()
        row.operator("mesh.basis_swap")
        
        row = layout.row()
        row.operator("mesh.w_mirror")
        
        row = layout.row()
        row.operator("mesh.mirror_sel")
        
        row = layout.row()
        row.operator("mesh.sclean_vertex_groups")
        
        row = layout.row()
        row.operator("mesh.parts_to_vgroups")
        
        row = layout.row()
        row.operator("mesh.selectorator")
        

def register():
    #regdef
    bpy.utils.register_class(basis_swap_op)
    bpy.utils.register_class(w_mirror_op)
    bpy.utils.register_class(mirror_sel_op)
    bpy.utils.register_class(clean_vertex_groups_op)
    bpy.utils.register_class(parts_to_vgroups_op)
    bpy.utils.register_class(selectorator_op)
    bpy.utils.register_class(GMeshPanel)

def unregister():
    #unregdef
    bpy.utils.unregister_class(basis_swap_op)
    bpy.utils.unregister_class(w_mirror_op)
    bpy.utils.unregister_class(mirror_sel_op)
    bpy.utils.register_class(clean_vertex_groups_op)
    bpy.utils.register_class(parts_to_vgroups_op)
    bpy.utils.register_class(selectorator_op)
    bpy.utils.unregister_class(GMeshPanel)
    
            row = layout.row()
        row.operator("mesh.bool_cut_select")
    bpy.utils.register_class(bool_cut_select_op)
    bpy.utils.unregister_class(bool_cut_select_op)
