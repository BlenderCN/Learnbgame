bl_info = {
    "name": "Bounce",
    "author": "Kgeogeo",
    "version": (1, 0),
    "blender": (2, 6, 3),
    "location": "Graph editor >> UI panel",
    "description": "Make bounce",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import math
                             
class CreateBounce(bpy.types.Operator):
    bl_idname = "graph.createbounce"
    bl_label = "create bounce"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        def create_list():
            l=[]
            for ob in context.selected_objects:              
                if ob.animation_data:
                    action = ob.animation_data.action        
                    for fc in [fc for fc in action.fcurves if not fc.hide]:
                        prev_kfp = None
                        for kfp in fc.keyframe_points:
                            if kfp.select_control_point:
                                if ob.type == 'ARMATURE':
                                    if ob.pose.bones[fc.group.name].bone.select:
                                        l.append([(ob.name + fc.data_path),kfp,prev_kfp,False,fc])
                                else:
                                    l.append([(ob.name + fc.data_path),kfp,prev_kfp,False,fc])        
                            prev_kfp = kfp
            return l
        
        def init_list(list):
            for l in list:
                l[3] = False

        def create_bounce(list):  
            def factor(i):
                if i[2]:
                    factor = (i[2].co.y-i[1].co.y)/(i[2].co.x-i[1].co.x)
                else:
                    factor = 0
                return factor

            def create_modifier(list,fac_max):
                for i in list:
                    if fac_max != 0:
                        amplitude = factor(i)/fac_max
                    else:
                        amplitude = 0 
                    if amplitude != 0:    
                        mod = i[4].modifiers.new('FNGENERATOR')
                        mod.use_additive = True
                        mod.use_restricted_range = True
                        mod.use_influence = True                        
                        mod.frame_end = i[1].co.x + context.object.decal                        
                        mod.frame_start = i[1].co.x
                        mod.blend_out = context.object.decal                         
                        mod.amplitude = amplitude * 10
                        mod.influence = 1/10
                        mod.phase_offset = 0.0  
                         
            def add_in_group(j,fac_max):
                j[3] = True 
                group.append(j)
                f = factor(j)
                if abs(f) > fac_max:
                    fac_max = abs(f)
                return fac_max    
                            
            for i in list:
                group = []
                if not i[3]:
                    i[3] = True
                    group.append(i)
                    fac_max = abs(factor(i))
                    for j in list:
                         if not j[3] and j[0] == i[0] and j[1].co.x == i[1].co.x:
                             fac_max = add_in_group(j,fac_max)
                    create_modifier(group,fac_max)
  
        list = create_list()
        create_bounce(list)        
        init_list(list)
               
        return {'FINISHED'}

class RemoveBounce(bpy.types.Operator):
    bl_idname = "graph.removebounce"
    bl_label = "remove bounce"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for ob in context.selected_objects:             
            if ob.animation_data:
                action = ob.animation_data.action 
                for fc in [fc for fc in action.fcurves if not fc.hide]:
                    for kfp in [kfp for kfp in fc.keyframe_points if kfp.select_control_point]:
                        for m in [m for m in fc.modifiers if m.frame_start == kfp.co.x]:
                            if ob.type == 'ARMATURE':
                                if ob.pose.bones[fc.group.name].bone.select: 
                                    fc.modifiers.remove(m)
                            else:
                                fc.modifiers.remove(m)        
                            
        context.area.tag_redraw()         
        return {'FINISHED'}


class BouncedPanel(bpy.types.Panel):
    bl_label = "Bounce"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        row = layout.row()
        row.operator('graph.createbounce', text="Create Bounce")
        row = layout.row()
        row.prop(context.object,'influence', text="Influence")
        row = layout.row()
        row.prop(context.object,'phase_multiplier', text="Phase Multiplier")
        row = layout.row()
        row.prop(context.object,'phase_offset', text="Phase Offset")
        row = layout.row()
        row.prop(context.object,'decal', text="Decal")
        row = layout.row()
        row.operator('graph.removebounce', text="Remove Selected Bounce")       

def update_influence(self, context):
        for ob in context.selected_objects:              
            if ob.animation_data:
                action = ob.animation_data.action 
                for fc in [fc for fc in action.fcurves if not fc.hide]:
                    for kfp in [kfp for kfp in fc.keyframe_points if kfp.select_control_point]:
                        for m in [m for m in fc.modifiers if m.frame_start == kfp.co.x]:               
                            if ob.type == 'ARMATURE':
                                if ob.pose.bones[fc.group.name].bone.select:
                                    m.influence = context.object.influence/10
                            else:
                                m.influence = context.object.influence/10            

def update_phase_offset(self, context):
        for ob in context.selected_objects:              
            if ob.animation_data:
                action = ob.animation_data.action 
                for fc in [fc for fc in action.fcurves if not fc.hide]:
                    for kfp in [kfp for kfp in fc.keyframe_points if kfp.select_control_point]:
                        for m in [m for m in fc.modifiers if m.frame_start == kfp.co.x]:               
                            if ob.type == 'ARMATURE':
                                if ob.pose.bones[fc.group.name].bone.select:                 
                                    m.phase_offset = context.object.phase_offset
                            else:
                                m.phase_offset = context.object.phase_offset  

def update_decal(self, context):
        for ob in context.selected_objects:              
            if ob.animation_data:
                action = ob.animation_data.action 
                for fc in [fc for fc in action.fcurves if not fc.hide]:
                    for kfp in [kfp for kfp in fc.keyframe_points if kfp.select_control_point]:
                        for m in [m for m in fc.modifiers if m.frame_start == kfp.co.x]:               
                            if ob.type == 'ARMATURE':
                                if ob.pose.bones[fc.group.name].bone.select:  
                                    m.blend_out = context.object.decal
                                    m.frame_end = m.frame_start + context.object.decal
                            else:
                                    m.blend_out = context.object.decal
                                    m.frame_end = m.frame_start + context.object.decal                                

def update_phase_multiplier(self, context):
        for ob in context.selected_objects:              
            if ob.animation_data:
                action = ob.animation_data.action 
                for fc in [fc for fc in action.fcurves if not fc.hide]:
                    for kfp in [kfp for kfp in fc.keyframe_points if kfp.select_control_point]:
                        for m in [m for m in fc.modifiers if m.frame_start == kfp.co.x]:               
                            if ob.type == 'ARMATURE':
                                if ob.pose.bones[fc.group.name].bone.select:  
                                    m.phase_multiplier = context.object.phase_multiplier
                            else:
                                m.phase_multiplier = context.object.phase_multiplier
                    
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.influence = bpy.props.FloatProperty(default=1.0, min=0.0, max=10.0, update=update_influence)
    bpy.types.Object.phase_offset = bpy.props.FloatProperty(default=0.0, min=-10.0, max=10.0, update=update_phase_offset)
    bpy.types.Object.decal = bpy.props.IntProperty(default=5, min=0, update=update_decal)
    bpy.types.Object.phase_multiplier = bpy.props.FloatProperty(default=1.0, min=-10.0, max=10.0, update=update_phase_multiplier)

def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()