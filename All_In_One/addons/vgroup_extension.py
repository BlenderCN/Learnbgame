bl_info = {
    "name": "Vertex groups extensions",
    "author": "Tal Hershkovich",
    "version" : (0, 1),
    "blender" : (2, 72, 0),
    "location": "Object Data > vertex groups specials, and Info Header",
    "description": "Adds more vertex groups options",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}
    
import bpy

#apply new functions inside the vertex groups options
def draw_func_vgroup_specials(self, layout):
    layout = self.layout
    layout.separator()
    layout.operator("vertexgroups.remove_empty", text="Remove empty vertex groups", icon='X')
    layout.operator("vertexgroups.remove_zero", text="Remove zero vertex", icon='X')
    layout.operator("vertexgroups.in_armature", text="Find vertex groups not in armature")
    
#display number of vertex groups in the info header    
def draw_func_vgroup_count(self, layout):
    layout = self.layout
    ob = bpy.context.object
  
    if ob.type == "MESH":
            vgroups =  "Vgroups:" + str(len(ob.vertex_groups))
            layout.label(vgroups)
            
#check which vertex groups are not use by the influencing armature
def search_vgroups(self, context):
    obj = bpy.context.active_object
    if obj.type == 'MESH':
        bone_list = []
        if obj.find_armature() != None:
            rig = obj.find_armature().name
            
            for v_group in obj.vertex_groups: 
                if v_group.name not in bpy.data.objects[rig].data.bones:
                   bone_list.append(v_group.name)
            if len(bone_list) > 0:
                self.report({'INFO'}, "bones that are not included are " + str(bone_list))
            elif len(obj.vertex_groups) == 0:
                self.report({'INFO'}, "There are no vertex groups")
            else:
                self.report({'INFO'}, "All groups are included in armature")
        else:
            self.report({'INFO'}, "No armatures found")

#remove empty group with a threshold for minimum vertex weight        
def removeEmptyGroups(self, context):
    thres = self.threshold
    obj = bpy.context.active_object
    if obj.type == 'MESH':     
        z = []
        count = 0
        for v in obj.data.vertices:
            for g in v.groups:
                if g.weight > thres:
                    if g not in z:
                        z.append(obj.vertex_groups[g.group])
        for r in obj.vertex_groups:
            if r not in z:
                obj.vertex_groups.remove(r)
                count +=1
        self.report({'INFO'}, str(count)+" groups are removed")
    else:
        self.report({'INFO'}, "Object is not a Mesh")

#remove zero vertex with a threshold for minimum vertex weight    
def removeZeroVerts(self, context):
    thres = self.threshold
    obj = bpy.context.active_object
    if obj.type == 'MESH': 
        for v in obj.data.vertices:
            z = []
            for g in v.groups:
                if not g.weight > thres:
                    z.append(g)
            for r in z:
                obj.vertex_groups[g.group].remove([v.index])


 
class Vgroups_not_in_armature(bpy.types.Operator):
    bl_idname = 'vertexgroups.in_armature'
    bl_label = 'Groups not included in Armature'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        search_vgroups(self, context)
        return {'FINISHED'}
    
class RemoveEmptyGroups(bpy.types.Operator):
    bl_idname = 'vertexgroups.remove_empty'
    bl_label = 'Remove empty groups'
    bl_options = {'REGISTER', 'UNDO'}
    
    threshold = bpy.props.FloatProperty(min = 0, max = 1)
    
    def execute(self, context):
        removeEmptyGroups(self, context)
        return {'FINISHED'}
    
class RemoveZeroVertex(bpy.types.Operator):
    bl_idname = 'vertexgroups.remove_zero'
    bl_label = 'Remove zero vertex'
    bl_options = {'REGISTER', 'UNDO'}
    
    threshold = bpy.props.FloatProperty(min = 0, max = 1)
    
    def execute(self, context):
        removeZeroVerts(self, context)
        return {'FINISHED'}
  
    
def register():
    bpy.types.INFO_HT_header.append(draw_func_vgroup_count)
    bpy.types.MESH_MT_vertex_group_specials.append(draw_func_vgroup_specials)
    bpy.utils.register_class(Vgroups_not_in_armature)
    bpy.utils.register_class(RemoveEmptyGroups)
    bpy.utils.register_class(RemoveZeroVertex)
    
    
def unregister():
    bpy.types.INFO_HT_header.remove(draw_func_vgroup_count)
    bpy.types.MESH_MT_vertex_group_specials.remove(draw_func_vgroup_specials)
    bpy.utils.unregister_class(Vgroups_not_in_armature)
    bpy.utils.unregister_class(RemoveEmptyGroups)
    bpy.utils.unregister_class(RemoveZeroVertex)
    


if __name__ == "__main__":  # only for live edit.
    register()
