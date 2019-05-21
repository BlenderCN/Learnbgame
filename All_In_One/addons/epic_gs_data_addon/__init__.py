bl_info = {
    "name" : "EPIC GS data Processor",
    "author" : "David C. King",
    "version" : (2, 79, 0),
    "location" : "View3D > Tools > Create",
    "description" : "Process EPIC.GS data files into full animations: 1 object per cell",
    "tracker_url" : "https://github.com/meekrob/c-blenderi/issues",
    "warning" : "",
    "wiki_url" : "https://github.com/meekrob/c-blenderi/wiki",
    "category" : "3D View"
}

import bpy
from bpy.props import StringProperty
from bpy.props import CollectionProperty
import sys

from mathutils import Vector

from epic_gs_data_addon import trace_lineage

def find_cell_or_parent(cellname):
    while bpy.data.objects.find(cellname) < 0:
        cellname = cellname[:-1]
        if not cellname:
            return -1

    return bpy.data.objects.find(cellname)

# mball elements #######
##object as returned by mball.elements.new: 
##------------------------
##e.g.
#mball= bpy.data.metaballs.new("name")
#el = mball.elements.new()

def mball_el_translate_x(el, x):
    mball_translate(el,Vector((x,0,0)))

def mball_el_translate_y(el, y):
    mball_translate(el,Vector((0,y,0)))

def mball_el_translate_z(el, z):
    mball_translate(el,Vector((0,0,z)))

def mball_el_translate(el, vec):
    el.co = el.co + vec

# mball elements #######

def swap_obj_locations(obj1, obj2):
    loc = obj1.location.copy()
    obj1.location = obj2.location
    obj2.location = loc

def set_active_object(obj, context=bpy.context):
    context.scene.objects.active = obj

def select_only_and_make_active(obj,  context=bpy.context):
    set_active_object(obj, context)
    select_only(obj)

def select_by_prefix(prefix):
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(prefix): obj.select = True

def assign_material_to_selected(material):
    assign_material_to_objects(material, bpy.context.selected_objects)

def assign_material_to_objects(material, objects):
    for obj in objects:
        obj.active_material = material

def assign_parent_to_selected(parent):
    assign_parent_to_objects(parent, bpy.context.selected_objects)

def assign_parent_to_objects(parent, objects):
    for obj in objects:
        obj.parent = parent

def scale_value(inval):
    MINV = 20000
    MAXV = 90000
    margin = MAXV - MINV
    percent_max = (inval - MINV) / margin
    return percent_max

def select_only(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    return obj

def dup_obj_return_new(obj):
    select_only(obj)
    bpy.ops.object.duplicate() # the duplicate becomes the only selected object
    new_obj = bpy.context.selected_objects[0]
    return new_obj
    
DIVISIONS_ONLY = True

class OBJECT_OT_epic(bpy.types.Operator):
    """Epic processing button"""
    bl_label = "Process file"
    bl_idname = "object.epic"
    bl_options = {'REGISTER'}

    run_this_shit = False

    def execute(self, context):
        if context.scene.render.engine != 'CYCLES':
            context.scene.render.engine = 'CYCLES'

        if context.scene.epic_gs_filename == '':
            self.report({'ERROR_INVALID_INPUT'}, "Need to specify a file")
            return {'CANCELLED'}

        self.report(
            {'INFO'}, 
            """Processing context.scene.epic_gs_filename: %s,\n context.scene.embryo_parent: %s,\n context.scene.default_cell_template: %s,\n context.scene.default_cell_material: %s""" %     
            (context.scene.epic_gs_filename, context.scene.embryo_parent, context.scene.default_cell_template, context.scene.default_cell_material)
        )
        infilename = context.scene.epic_gs_filename
        # key the cell divisions only
        key_divisions_only = context.scene.key_divisions_only

        # set up the scene
        if not context.scene.default_cell_template:
            # add an object
            bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=layers_tuple())
            context.scene.default_cell_template = context.object

        cell_template = bpy.data.objects.get( context.scene.default_cell_template.name )

        if context.scene.E_cell_template:
            e_cell_template = bpy.data.objects.get( context.scene.E_cell_template.name )
        else:
            e_cell_template = cell_template
    
        if context.scene.MS_cell_template:
            ms_cell_template = bpy.data.objects.get( context.scene.MS_cell_template.name )
        else:
            ms_cell_template = cell_template

        if context.scene.P_cell_template:
            p_cell_template = bpy.data.objects.get( context.scene.P_cell_template.name )
        else:
            p_cell_template = p_cell_template

        # process data
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 2000
        min_time, max_time, big_data = trace_lineage.load_gs_epic_file(infilename)
        for celltype in trace_lineage.ALL_END_PNTS:
            current_cell_type_char = ''
            cell_type_char = celltype[0]
            print("Doing", celltype, file=sys.stderr)
            print("==============", file=sys.stderr)
            ### E cells
            if celltype.startswith('E'):
                new_cell = dup_obj_return_new(e_cell_template)
                new_mat = bpy.context.scene.e_cell_material
            ### MS cells
            elif celltype.startswith('MS'):
                new_cell = dup_obj_return_new(ms_cell_template)
                new_mat = bpy.context.scene.ms_cell_material
            ### P --> Z cells
            elif celltype.startswith('P') or celltype.startswith('Z'):
                new_cell = dup_obj_return_new(p_cell_template)
                new_mat = bpy.context.scene.p_cell_material
            else:
                new_cell = dup_obj_return_new(cell_template)
                new_mat = bpy.context.scene.default_cell_material

            new_cell.name = celltype
            new_cell.parent = context.scene.embryo_parent
            new_cell.active_material = new_mat
            do_thing(new_cell, celltype, min_time, max_time, big_data, key_divisions_only)

        # set active object to parent
        if context.scene.embryo_parent:
           set_active_object( context.scene.embryo_parent, context )
           select_only( context.scene.embryo_parent )

        return {'FINISHED'}
import time
NTICKS = 4

def do_thing(object, end_cell, min_time, max_time, big_data, key_divisions_only = True):
    last_cell = ''
    timer = time.time()
    for timepnt, row, found_cell in trace_lineage.search_gs_epic_file([end_cell], min_time, max_time, big_data):
        frame = timepnt *12
        print("%s: at cell division" % end_cell, str(timepnt) + ",", last_cell, "==>", found_cell, "in %.4f seconds" % (time.time() - timer), file=sys.stderr)

        synchronize = False
        if frame % 512 == 0: 
            synchronize = True
        if timepnt == max_time:
            synchronize = True

        # cell divisions determined by "found_cell" being different from the last iteration, since it traverses a lineage tree in the search
        in_a_cell_division = False
        if found_cell != last_cell:
            print("%s: =========== AT CELL DIVISION ===========" % end_cell, file=sys.stderr)
            ticker = NTICKS
            timer = time.time()
            in_a_cell_division = True

        # always insert keyframes at synchronization points
        if synchronize:
            print("%s: =========== key_divisions_only %s, in_a_cell_division %s. SYNCHRONIZING ===========" 
                        % (end_cell, key_divisions_only, in_a_cell_division), 
                        file=sys.stderr
            )
            pass
        # skip intermediate keyframes
        elif key_divisions_only and not in_a_cell_division:
            print("%s: =========== key_divisions_only %s, in_a_cell_division %s. continuing ===========" 
                        % (end_cell, key_divisions_only, in_a_cell_division), 
                        file=sys.stderr
            )
            continue


        last_cell = found_cell

        if not row: continue

        bpy.context.scene.frame_current = frame
        object.location = (row['x']/100,row['y']/100,row['z']/10)
        size = row['size']/200
        object.scale = (size,size,size)
        object.keyframe_insert('scale')
        object.keyframe_insert('location')
        # do something with the material
        curMat = object.active_material
        #if 'ecdf' in row:
        if False:
            if False:
                curMat.node_tree.nodes['ColorRamp'].inputs[0].default_value = row['ecdf']
            else:
                curMat.node_tree.nodes['ColorRamp'].inputs[0].default_value = scale_value(row['value'])
            curMat.node_tree.nodes['ColorRamp'].inputs[0].keyframe_insert("default_value", frame = frame )

class OBJECT_OT_custompath(bpy.types.Operator):
    #bl_label = "Select epic.gs data file"
    bl_label = "Process EPIC.GS file"
    bl_idname = "object.custom_path"
    __doc__ = ""

    bl_options = {'REGISTER'}

    filename_ext = "*.csv"
    filter_glob = StringProperty(
        name = "Filename",
        description = "File to Process",
        default=filename_ext, options={'HIDDEN'}
    )    

    filepath = StringProperty(
        name="File Path", 
        description="Filepath used for importing txt files", 
        maxlen= 1024, 
        default= "")

    def execute(self, context):
        print("FILEPATH %s"%self.properties.filepath)#display the file name and current path        
        context.scene.epic_gs_filename = self.properties.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class file_processing_panel(bpy.types.Panel):
    """File processing panel"""
    bl_label = "Epic.gs.data processer"
    bl_idname = "OBJECT_PT_file_process"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"
    bl_context = "objectmode"

    def draw(self, context):
        #obj = bpy.context.scene.objects.get("embryo_parent")
        scene = bpy.context.scene

        layout = self.layout
        row = layout.row()
        row.label(text="Open and process an epic.gs.data file:")
        row = layout.row(align=True)
        row.prop( context.scene, "epic_gs_filename", text="")
        p = row.operator( OBJECT_OT_custompath.bl_idname, text="", icon = "FILESEL")
        p.filepath = context.scene.epic_gs_filename 

        row = layout.row()
        row.label(text="Setup:")

        row = layout.row()
        row.label(text="Smooth animation")
        row.prop(bpy.context.scene, "key_divisions_only", text="")

        # empty parent for everything
        row = layout.row()
        row.label(text="Embryo parent")
        row.prop_search(bpy.context.scene, "embryo_parent", bpy.context.scene, "objects", text="")

        # cell type object templates
        row = layout.row()
        row.label(text="Object template for cell types:")

        # default
        row = layout.row()
        split = row.split()
        col = split.column()
        col.label(text="Mesh template")
        col.prop_search(bpy.context.scene, "default_cell_template", bpy.context.scene, "objects", text="")
        col = split.column()
        col.label(text="Material template")
        col.prop_search(scene, "default_cell_material", bpy.data, "materials", text="")

        # E cell row
        row = layout.row()
        split = row.split()
        col = split.column()
        col.label(text="E cell:")
        col.prop(bpy.context.scene, "E_cell_template", text="")
        col = split.column()
        col.label(text="E cell material")
        col.prop_search(scene, "e_cell_material", bpy.data, "materials", text="")

        # MS cell row
        row = layout.row()
        split = row.split()
        col = split.column()
        col.label(text="MS cell:")
        col.prop_search(bpy.context.scene, "MS_cell_template", bpy.context.scene, "objects", text="")
        col = split.column()
        col.label(text="MS cell material")
        col.prop_search(scene, "ms_cell_material", bpy.data, "materials", text="")

        # P/Z cell row
        row = layout.row()
        split = row.split()
        col = split.column()
        col.label(text="P/Z cells:")
        col.prop_search(bpy.context.scene, "P_cell_template", bpy.context.scene, "objects", text="")
        col = split.column()
        col.label(text="P/Z cell material")
        col.prop_search(scene, "p_cell_material", bpy.data, "materials", text="")

        # Functions
        row = layout.row()
        row.label(text="Operations:")
        row = layout.row()
        p = row.operator(OBJECT_OT_epic.bl_idname)
        


def process_epic_gs_button(self, context):
    self.layout.operator('file.select_all_toggle',        
        OBJECT_OT_custompath.bl_idname,
        icon = "FILESEL"
    )

def layers_tuple(selected=0):
    layer_list = [False] * 20
    layer_list[0] = True
    return tuple(layer_list)


# registration
def register():
    print("-register-", file=sys.stderr)

    """
    # While trying to activate as an add-on
    # AttributeError: '_RestrictContext' object has no attribute 'scene'
    if bpy.context.scene.objects.find("embryo_parent") < 0:
        bpy.ops.object.empty_add(
            type='PLAIN_AXES', 
            view_align=False, 
            location=(0, 0, 0), 
            layers=layers_tuple()
        )
        bpy.context.object.name = "embryo_parent"
    """
    bpy.types.Scene.key_divisions_only = bpy.props.BoolProperty(
        name = "Key Divisions Only",
        default = True,
        description = "Only insert keyframes at divisions (smoother animation)"
    )

    bpy.types.Scene.epic_gs_filename = bpy.props.StringProperty(
        name = "Epic filename",
        default = "",
        description = "Epic gs name"
    )

    bpy.types.Scene.embryo_parent = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "Embryo object parent",
        description = "All added objects are parented to this object",
        poll = empty_check_function
    )


    bpy.types.Scene.default_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "Default object to use for all cells",
        description = "This object will be cloned to produce any cells",
        poll = mesh_check_function
    )

    bpy.types.Scene.C_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "C Cell Object template",
        description = "This object will be cloned to produce all of the C cells in the data file",
        poll = mesh_check_function

    )
    bpy.types.Scene.D_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "D Cell Object template",
        description = "This object will be cloned to produce all of the D cells in the data file",
        poll = mesh_check_function

    )
    bpy.types.Scene.E_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "E Cell Object template",
        description = "This object will be cloned to produce all of the E cells in the data file",
        poll = mesh_check_function
    )
    bpy.types.Scene.MS_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "MS Cell Object template",
        description = "This object will be cloned to produce all of the MS cells in the data file",
        poll = mesh_check_function
    )
    bpy.types.Scene.P_cell_template = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name = "P-->Z Cell Object template",
        description = "This object will be cloned to produce all of the P and Z cells in the data file",
        poll = mesh_check_function

    )
    bpy.types.Scene.default_cell_material = bpy.props.PointerProperty(
        type=bpy.types.Material,
        name = "Default cell material",
        description = "This material will be assigned to all cells",
        poll = material_check_function
    )

    bpy.types.Scene.e_cell_material = bpy.props.PointerProperty(
        type=bpy.types.Material,
        name = "E cell material",
        description = "This material will be assigned to all E cells",
        poll = material_check_function
    )

    bpy.types.Scene.ms_cell_material = bpy.props.PointerProperty(
        type=bpy.types.Material,
        name = "E cell material",
        description = "This material will be assigned to all E cells",
        poll = material_check_function
    )

    bpy.types.Scene.p_cell_material = bpy.props.PointerProperty(
        type=bpy.types.Material,
        name = "P/Z cell material",
        description = "This material will be assigned to all P and Z cells",
        poll = material_check_function
    )

    bpy.utils.register_module(__name__)
    #bpy.utils.register_class(OBJECT_OT_epic)
    #bpy.utils.register_class(OBJECT_OT_custompath)
    #bpy.utils.register_class(file_processing_panel)
    bpy.types.INFO_MT_mesh_add.append(process_epic_gs_button)

def mesh_check_function(self, obj):
    return obj.type == 'MESH'

def empty_check_function(self, obj):
    return obj.type == 'EMPTY'

def material_check_function(self, obj):
    return obj.type in ['SURFACE', 'WIRE', 'VOLUME', 'HALO'] # possible "material" types

def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.utils.unregister_class(OBJECT_OT_epic)
    #bpy.utils.unregister_class(OBJECT_OT_custompath)
    #bpy.utils.unregister_class(file_processing_panel)
    bpy.types.INFO_MT_mesh_add.remove(process_epic_gs_button)

    del bpy.types.Scene.key_divisions_only

    del bpy.types.Scene.epic_gs_filename
    del bpy.types.Scene.embryo_parent

    del bpy.types.Scene.default_cell_template
    del bpy.types.Scene.default_cell_material

    del bpy.types.Scene.C_cell_template
    del bpy.types.Scene.D_cell_template

    del bpy.types.Scene.E_cell_template
    del bpy.types.Scene.e_cell_material

    del bpy.types.Scene.MS_cell_template
    del bpy.types.Scene.ms_cell_material

    del bpy.types.Scene.P_cell_template
    del bpy.types.Scene.p_cell_material

if __name__ == "__main__":
    register()

