import bpy, os
from bpy.types import Operator

bl_info = {
    "name": "Setup Good Defaults for Scultping",
    "description": "Set several defaults for sculpting from the basic startup file. Based on YanSculpts suggestions",
    "author": "Johnny Matthews - johnny.matthews@gmail.com",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "3D View > View > Setup YanSculpts Defaults",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

def createClayShader(name):

    #Create the Clay shader from scratch

    # Create the material and turn on nodes, then delete default nodes
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links

    nodes.remove(nodes[0])
    nodes.remove(nodes[0])

    # Create the nodes 
    nodes.new("ShaderNodeOutputMaterial")
    nodes.new("ShaderNodeMixShader")
    nodes.new("ShaderNodeMixShader")
    nodes.new("ShaderNodeMixShader")
    nodes.new("ShaderNodeBsdfTranslucent")
    nodes.new("ShaderNodeFresnel")
    nodes.new("ShaderNodeBsdfDiffuse")
    nodes.new("ShaderNodeBsdfGlossy")

    # Set default values
    nodes[6].inputs[0].default_value = [0.8,0.566,0.403,1.0]

    # Try to lay them out somewhat nicely
    mul = 160
    mulh = 140

    nodes[0].location = [6*mul,     -1  * mulh]
    nodes[1].location = [4.5*mul,   -1  * mulh]
    nodes[2].location = [3*mul,     -3  * mulh]
    nodes[3].location = [1.5*mul,   -3  * mulh]
    nodes[4].location = [1.5*mul,-  4.5 * mulh]
    nodes[5].location = [0,         0   * mulh]
    nodes[6].location = [0,         -1.5* mulh]
    nodes[7].location = [0,         -3  * mulh]

    # Create Links
    links.new(nodes[1].outputs[0],nodes[0].inputs[0])
    links.new(nodes[2].outputs[0],nodes[1].inputs[2])
    links.new(nodes[3].outputs[0],nodes[1].inputs[1])
    links.new(nodes[5].outputs[0],nodes[1].inputs[0])
    links.new(nodes[5].outputs[0],nodes[3].inputs[0])
    links.new(nodes[6].outputs[0],nodes[3].inputs[1])
    links.new(nodes[7].outputs[0],nodes[3].inputs[2])
    links.new(nodes[3].outputs[0],nodes[2].inputs[1])
    links.new(nodes[4].outputs[0],nodes[2].inputs[2])

    mat.use_fake_user = True

    return mat

def setup(context):

    # Create Object
    #bpy.ops.view3d.snap_cursor_to_center()
    #bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
 
    # Create Material and Assign to Object
    clayExists = False
    for material in bpy.data.materials:
        if material.name == "YanSculptsClay":
            clayExists = True
    
    if clayExists == False:
        material = createClayShader("YanSculptsClay")
        
        #bpy.ops.object.material_slot_add()
        #slot = bpy.context.active_object.material_slots[0]
        #slot.material = material

    # View Settings
    bpy.context.space_data.use_matcap = True
    bpy.context.space_data.matcap_icon = '06'
    bpy.context.space_data.show_only_render = True
    bpy.context.space_data.fx_settings.use_ssao = True
    bpy.context.space_data.lens = 80    
    
    # Brush Settings
    bpy.data.brushes["Grab"].strength = 0.1
    
    points = bpy.data.brushes["Scrape/Peaks"].curve.curves[0].points
    while len(points) > 2:
        points.remove(points[1])            
    points[0].location = [0,1]
    points[1].location = [1,1]
    bpy.data.brushes["Scrape/Peaks"].curve.update()
    
    if bpy.context.mode != "SCULPT":
        bpy.ops.sculpt.sculptmode_toggle()

    bpy.context.scene.tool_settings.sculpt.detail_size = 8
    bpy.ops.sculpt.dynamic_topology_toggle()


    # Scene Settings
    bpy.context.scene.cycles.film_transparent = True

    # Create Detail Brush
    addDetailExists = False
    for b in bpy.data.brushes:
        if b.name == "Add Detail":
            addDetailExists = True
    
    if addDetailExists == False:
        brush = bpy.data.brushes.new("Add Detail","SCULPT")
        brush.strength = 0.0
        brush.use_custom_icon = True
        path = bpy.utils.script_path_user()
        brush.icon_filepath = os.path.join(path,"addons","setup_sculpt.png")

    return {'FINISHED'}

# Setup Basic Script Stuff from Template

class SetupSculpting(Operator):
    bl_idname = "setup.sculptingdefaults"  
    bl_label = "Setup Good Sculpting Defaults"

    def execute(self, context):
        return setup(context)

def menu_func_import(self, context):
    self.layout.operator(SetupSculpting.bl_idname, text="Setup YanSculpts Defaults")


def register():
    bpy.utils.register_class(SetupSculpting)
    bpy.types.VIEW3D_MT_view.append(menu_func_import)


def unregister():
    upath = bpy.utils.script_path_user()
    file1 = os.join(upath,"setup_sculpt","add_detail.png")
    os.unlink(file1)

    bpy.utils.unregister_class(SetupSculpting)
    bpy.types.VIEW3D_MT_view.remove(menu_func_import)


if __name__ == "__main__":
    register()
