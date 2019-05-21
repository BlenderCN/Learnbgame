import bpy
from sound_drivers.utils import get_context_area, getAction, getSpeaker
from sound_drivers.BGL_draw_visualiser import ScreenAreaAction
from mathutils import Vector

def get_view_action(bl, tr):
    '''
    focus the graph editor to the sound fcurves
    bl bottom left 2d coord
    tr top right
    '''
    view_action = bpy.data.actions.get("view_action")
    
    if view_action is None:
        dp = '["view"]'

        # create one
        view_action = bpy.data.actions.new("view_action")
        fc = view_action.fcurves.new(dp)
        # add 3 keyframe points
        fc.keyframe_points.add(3)
    else:
        fc = view_action.fcurves[0]
            
    (a, b, c) = fc.keyframe_points
    
    a.co = bl
    a.select_control_point = True
    b.co = (bl[0] + tr[0] / 2.0, bl[1])
    b.select_control_point = True 
    c.co = tr
    c.select_control_point = True
    
    return view_action

def focus_areas(context):
    #obj = context.object
    #save_action = obj.animation_data.action
    #obj["view"] = 0.0
    sp = getSpeaker(context)
    sp["view"] = 0.0
    action = getAction(sp)
    wm = context.window_manager

    (x, y) = action.frame_range
    
    c = context.copy()
    s = ScreenAreaAction(context)
    for i, area in enumerate(context.screen.areas):
        if area.type != 'GRAPH_EDITOR':
            continue
        region = area.regions[-1]
        print("SCREEN:", context.screen.name , "[", i, "]")
        if action.normalise == 'NONE':
            (min, max) = (action["min"], action["max"])
        else:
            (min, max) = action.normalise_range
        c["space_data"] = area.spaces.active
        c["area"] = area
        c["region"] = region
        
        dummyaction  = get_view_action((x, min), (y, max))
        #obj.animation_data.action = dummyaction
        sp.animation_data.action = dummyaction

        bgl_area = s.get_area(area)


        bpy.ops.anim.channels_expand(c, all=True)
        bpy.ops.anim.channels_expand(c, all=True)
        if (bgl_area is None  or not wm.bgl_draw_speaker):
            bpy.ops.graph.view_all(c)
            continue
        
        if bgl_area is not None:
    
            ah = area.height
            v2d = region.view2d
            rh = region.height

            pc = bgl_area.GRAPH_EDITOR.height / 100.0
            apc = (bgl_area.GRAPH_EDITOR.loc[1] + (pc * rh)) / ah
            vis_h = (pc + 2) * rh / 100.0 # plus header box

            #(m, n) = Vector(v2d.region_to_view(1,1)) - Vector(v2d.region_to_view(0,0))

            if action.normalise == 'NONE':
                (min, max) = (action["min"], action["max"])
            else:
                (min, max) = action.normalise_range
                
            range = abs(max-min)
            newmin = min - (apc / (1.0 - apc)) * range  
            min = newmin
                
            print(bgl_area)
            print("GRAPH RESIZE", pc, apc, vis_h, min)
            dummyaction  = get_view_action((x, min), (y, max)) 
            #bpy.ops.graph.view_selected(c, include_handles=False)
            bpy.ops.graph.view_all(c)
           

    sp.animation_data.action =  action
            
    
class FocusGraphView2BGL(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "graph.view_all_with_bgl_graph"
    bl_label = "Focus Graph To BGL"

    @classmethod
    def poll(cls, context):
        return True
        return context.active_object is not None

    def execute(self, context):
        focus_areas(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(FocusGraphView2BGL)

def unregister():
    bpy.utils.unregister_class(FocusGraphView2BGL)

