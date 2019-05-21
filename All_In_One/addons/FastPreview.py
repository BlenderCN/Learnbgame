import bpy
from mathutils import Vector

bl_info = {    
    'name': 'Playback Preview',
    'author': 'Bay Raitt',
    'version': (0, 1),
    'blender': (2, 80, 0),
    'category': 'Animation',
    'location': 'Timeline  > Preview Toggle',
    'wiki_url': ''}

playing = "False"
brCurframe = 0
brStartRange = 1              
brEndRange = 72

class BR_OT_fastPreview(bpy.types.Operator):
    """play range and return to current frame on stop"""
    bl_idname   = "screen.fast_preview"
    bl_label   = "Preview"
    bl_description = "start playback from the first frame"
    def execute(self, context):
        global playing
        if playing == "False":
            global brCurframe                     
            brCurframe = bpy.context.scene.frame_current
            context = bpy.context
            c = context.copy()
            previewStart = bpy.context.scene.frame_start 
            previewEnd = bpy.context.scene.frame_end 
            for i, area in enumerate(context.screen.areas):
                if area.type != 'GRAPH_EDITOR':
                    continue
                region = area.regions[-1]
                print("SCREEN:", context.screen.name , "[", i, "]")
                c["space_data"] = area.spaces.active
                c["area"] = area
                c["region"] = region            
                h = region.height # screen
                w = region.width  # 
                bl = region.view2d.region_to_view(0, 0)
                tr = region.view2d.region_to_view(w, h)
                previewStart = int(bl[0])
                previewEnd = int(tr[0])
            bpy.context.scene.use_preview_range = True
            bpy.context.scene.frame_preview_start =  previewStart
            bpy.context.scene.frame_preview_end =  previewEnd
            bpy.context.scene.frame_current = previewStart


            #bpy.context.scene.frame_current = bpy.context.scene.frame_start            
            bpy.ops.screen.animation_play()
            playing = "True"   
        elif playing == "True":
            brCurframe

            bpy.context.scene.frame_preview_start =  bpy.context.scene.frame_start
            bpy.context.scene.frame_preview_end =  bpy.context.scene.frame_end

            bpy.context.scene.use_preview_range = False

            
            bpy.ops.screen.animation_cancel(restore_frame=False)
            bpy.context.scene.frame_current = brCurframe
                                    
            playing = "False"  
            print ("woo")   
          
        return {'FINISHED'}


def menu_draw(self, context):
    self.layout.operator(BR_OT_fastPreview.bl_idname)

def register():
    from bpy.utils import register_class
    register_class(BR_OT_fastPreview)
    bpy.types.TIME_HT_editor_buttons.prepend(menu_draw)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(BR_OT_fastPreview)
    bpy.types.TIME_HT_editor_buttons.remove(menu_draw)

    if __name__ != "__main__":
        bpy.types.TIME_HT_editor_buttons.remove(menu_draw)
                
if __name__ == "__main__":
    register()
