import bpy

# switch watched palette
class PaletteSwitchNodePalette(bpy.types.Operator):
    bl_idname = "palette.switch_node_palette"
    bl_label = "Select Node Palette"
    bl_description = "Select this Node Palette as Node Output"
    bl_options = {"REGISTER", "UNDO"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        prop.palette_list=prop.palettes[self.index].name
        return {"FINISHED"}
    
# get nodegroup
class PaletteGetShaderNodeGroup(bpy.types.Operator):
    bl_idname = "palette.get_shader_node_group"
    bl_label = "NodeGroup"
    bl_description = "Get Palette NodeGroup"
    bl_options = {"REGISTER", "UNDO"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        area=bpy.context.area
        for s in area.spaces:
            if s.type=='NODE_EDITOR':
                space=s
        nodetree=space.id.node_tree
        grouptoget=bpy.data.node_groups[prop.palettes[self.index].name]
        group=nodetree.nodes.new('ShaderNodeGroup')
        group.node_tree=grouptoget
        group.location[0]=100
        group.location[1]=400
        return {"FINISHED"}