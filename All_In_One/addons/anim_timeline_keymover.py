bl_info = { "name":"Timeline Key Mover",
            "author":"Joel Daniels",
            "category": "Learnbgame",
            "version":(0,3),
            "blender": (2, 80, 0),
            "location":"Timeline header",
            "description":"Move keyframes associated with the selected object directly in the timeline."}

import bpy
from bpy.props import IntProperty
event_types = {'NUMPAD_3': 3, 'ONE': 1, 'NINE': 9, 'ZERO': 0, 'THREE': 3, 'NUMPAD_2': 2, 'NUMPAD_5': 5, 'NUMPAD_8': 8, 'NUMPAD_9': 9, 'NUMPAD_4': 4, 'NUMPAD_6': 6, 'NUMPAD_1': 1, 'NUMPAD_0': 0, 'TWO': 2, 'FOUR': 4, 'SIX': 6, 'EIGHT': 8, 'FIVE': 5, 'SEVEN': 7, 'NUMPAD_7': 7}

#-------------------------------------------
class TIMELINE_OT_KeyMover(bpy.types.Operator):
    """Translate keyframes on the current frame directly in the timeline"""
    bl_idname = "timeline.key_mover"
    bl_label = "Timeline Keymover"

    offset = IntProperty(name="Offset")

    def execute(self, context):
        scene = context.scene
        timeline = context.space_data
        
        keys = self._keys
        for kp in keys:
            if kp:
                #Move key
                kp.co.x = self._keys[kp][0] + self.offset
                #Move handle left
                kp.handle_left.x = self._keys[kp][0] + self.offset + keys[kp][1]
                #Move handle right
                kp.handle_right.x = self._keys[kp][0] + self.offset + keys[kp][2]
                if scene.tl_frame_follow:
                    scene.frame_current = self._initial_frame + self.offset
                
    def modal(self, context, event):
        timeline = context.space_data
        scene = context.scene
        
        if event.type == 'MOUSEMOVE':
            self.offset = (self._initial_mouse - event.mouse_x) * -(scene.tl_mouse_sens)
            self.execute(context)
            context.area.header_text_set("Moving keys by offset %d" % self.offset)
        
        if event.type in event_types:
            self.offset = event_types[event.type]
            self.execute(context)
            context.area.header_text_set("Moving keys by offset %d" % self.offset)
            
        if event.type in {'LEFTMOUSE', 'NUMPAD_ENTER', 'RET'}:
            context.area.header_text_set()
            return {'FINISHED'}

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            scene.frame_current = self._initial_frame
            for kp in self._keys:
                if kp:
                    kp.co.x = self._keys[kp][0]
                    kp.handle_left.x = self._keys[kp][0] + self._keys[kp][1]
                    kp.handle_right.x = self._keys[kp][0] + self._keys[kp][2]
            context.area.header_text_set()
            
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scene = context.scene
        if context.object is None:
            self.report({'INFO'}, "There is no selected object!")
            return {'CANCELLED'}
        elif context.object.animation_data is None:
            self.report({'INFO'}, "The selected object has no animation data!")
            return {'CANCELLED'}
        else:
            if context.space_data.type == 'TIMELINE':
                timeline = context.space_data
                #timeline.show_only_selected = True

                def collect(fcurves):
                    for fcu in fcurves:
                        if fcu:
                            for kp in fcu.keyframe_points:
                                if scene.tl_frame_current:
                                    if kp.co.x == scene.frame_current:
                                        self._keys[kp] = (kp.co.x, kp.handle_left.x - kp.co.x, kp.handle_right.x - kp.co.x)
                                elif not scene.tl_frame_current:
                                    start_frame = scene.frame_preview_start if scene.use_preview_range else scene.frame_start
                                    end_frame = scene.frame_preview_end if scene.use_preview_range else scene.frame_end
                                    if kp.co.x >= start_frame and kp.co.x <= end_frame:
                                         self._keys[kp] = (kp.co.x, kp.handle_left.x - kp.co.x, kp.handle_right.x - kp.co.x)
                
                def collect_from_bones(fcurves):
                        '''If scene.tl_only_selected_bones is enabled, only collect keys from fcurves associated with the selected bones'''
                        self._bones = [bone for bone in context.selected_pose_bones]
                        for bone in self._bones:    
                            for fcu in fcurves:
                                if fcu:
                                    if fcu.data_path.split('"')[1] == bone.name:
                                        for kp in fcu.keyframe_points:
                                            if scene.tl_frame_current:
                                                if kp.co.x == scene.frame_current:
                                                    self._keys[kp] = (kp.co.x, kp.handle_left.x - kp.co.x, kp.handle_right.x - kp.co.x)
                                            elif not scene.tl_frame_current:
                                                start_frame = scene.frame_preview_start if scene.use_preview_range else scene.frame_start
                                                end_frame = scene.frame_preview_end if scene.use_preview_range else scene.frame_end
                                                if kp.co.x >= start_frame and kp.co.x <= end_frame:
                                                     self._keys[kp] = (kp.co.x, kp.handle_left.x - kp.co.x, kp.handle_right.x - kp.co.x)
     
                #Store keyframes and their handles' x offset from the key itself
                self._keys = {}
                for ob in context.selected_objects:
                    fcurves = ob.animation_data.action.fcurves
                    if ob.type == 'ARMATURE' and scene.tl_only_selected_bones:
                        collect_from_bones(fcurves)
                    else:
                        collect(fcurves)

                    if ob.data:
                        if ob.data.animation_data is not None and ob.data.animation_data.action is not None:
                            data_fcurves = ob.data.animation_data.action.fcurves
                            if not scene.tl_only_selected_bones:
                                collect(data_fcurves)
                                 
                if self._keys == {}:
                    self.report({'INFO'}, "There are no keyframes on the current frame")
                    return {'CANCELLED'}
                else:
                    self._initial_mouse = event.mouse_x
                    self._initial_frame = scene.frame_current
        
                    context.window_manager.modal_handler_add(self)
                    return {'RUNNING_MODAL'}
            else:
                self.report({'WARNING'}, "Active space must be a timeline")
                return {'CANCELLED'}
            
#-------------------------------------------
class TIMELINE_OT_KeyCopier(bpy.types.Operator):
    '''Copy keyframes on the selected object / bones from the current frame and move them in the timeline'''
    bl_idname = "timeline.key_copier"
    bl_label = "Key Copier"
    
    offset = IntProperty(name="Offset")

    def execute(self, context):
        scene = context.scene
        timeline = context.space_data
        
        keys = self._keys
        for kp in keys:
            #Move key
            kp.co.x = self._second_frame + self.offset
            #Move handle left
            kp.handle_left.x = self._second_frame + self.offset + keys[kp][0]
            #Move handle right
            kp.handle_right.x = self._second_frame + self.offset + keys[kp][1]
            if scene.tl_frame_follow:
                scene.frame_current = self._second_frame + self.offset
                
    def modal(self, context, event):
        timeline = context.space_data
        scene = context.scene
        fcurves = context.object.animation_data.action.fcurves
        
        if event.type == 'MOUSEMOVE':
            self.offset = (self._initial_mouse - event.mouse_x) * -(scene.tl_mouse_sens)
            self.execute(context)
            context.area.header_text_set("Move copied keys by offset %.1f" % self.offset)

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set()
            for fcu in fcurves:
                fcu.update()
            return {'FINISHED'}

        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            ###
            ### Need to delete the inserted keys!! 
            ###
            if context.object.type == 'ARMATURE':
                for bone in self._bones:
                    for fcu in fcurves:
                        if fcu.data_path.split('"')[1] == bone.name:
                            bone.keyframe_delete(data_path = fcu.data_path.split('.')[-1], frame = self._second_frame + self.offset)
            else:
                for fcu in fcurves:
                    context.object.keyframe_delete(data_path = fcu.data_path.split('.')[-1], frame = self._second_frame + self.offset)
            
            context.area.header_text_set()
            scene.frame_current = self._initial_frame
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scene = context.scene
        if context.object is None:
            self.report({'INFO'}, "There is no selected object!")
            return {'CANCELLED'}
        elif context.object.animation_data is None:
            self.report({'INFO'}, "The selected object has no animation data!")
            return {'CANCELLED'}
        else:
            fcurves = context.object.animation_data.action.fcurves
            if context.space_data.type == 'TIMELINE':
                timeline = context.space_data
                #timeline.show_only_selected = True
            
                #Store keyframes and their handles' x offset from the key itself
                self._keys = {}
                
                #Insert the duplicate frames
                scene = context.scene
                fcurves = context.object.animation_data.action.fcurves
                if context.object.type == 'ARMATURE':
                    self._bones = [bone for bone in context.selected_pose_bones]
                    for bone in self._bones:    
                        for fcu in fcurves:
                            if fcu.data_path.split('"')[1] == bone.name:
                                #how to duplicate a keyframe?
                                #have to set the index for the kp? and add 1 to all subsequent kp indices on that fcurve?
                                bone.keyframe_insert(data_path = fcu.data_path.split('.')[-1], frame = scene.frame_current + 1)
                                
                                #Then set scene.frame_current to += 1, and start moving 
                             
                else:
                    object = context.object
                    for fcu in fcurves:
                        object.keyframe_insert(data_path = fcu.data_path.split('.')[-1], frame = scene.frame_current + 1)
                        
                for fcu in fcurves:
                    if fcu:
                        for kp in fcu.keyframe_points:
                            if kp.co.x == scene.frame_current + 1:
                                self._keys[kp] = (kp.handle_left.x - kp.co.x,
                                                  kp.handle_right.x - kp.co.x)
                
                if self._keys == {}:
                    self.report({'INFO'}, "There are no keyframes on the current frame")
                    return {'CANCELLED'}
                else:
                    self._initial_mouse = event.mouse_x
                    self._initial_frame = scene.frame_current
                    self._second_frame = scene.frame_current + 1
        
                    context.window_manager.modal_handler_add(self)
                    return {'RUNNING_MODAL'}
            else:
                self.report({'WARNING'}, "Active space must be a timeline")
                return {'CANCELLED'}

#-------------------------------------------
class TIMELINE_HT_KeymoverMenu(bpy.types.Menu):
    bl_label = "Key Mover Menu"
    bl_idname = "key_mover_menu"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "tl_mouse_sens")
        layout.prop(scene, "tl_frame_current")
        layout.prop(scene, "tl_only_selected_bones")
        layout.prop(scene, "tl_frame_follow", text = "Cursor Follows Movement")

def draw_menu(self, context):
    layout = self.layout
    layout.menu(TIMELINE_HT_KeymoverMenu.bl_idname)
            
#-------------------------------------------            
class TIMELINE_HT_KeyMover(bpy.types.Header):
    bl_space_type = 'TIMELINE'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        self.layout.separator()
        layout.operator("timeline.key_mover", text = "Key Mover", icon = "SPACE2")
        layout.operator("timeline.key_copier", text = "Key Copier", icon = "COPYDOWN")
        

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.tl_mouse_sens = bpy.props.FloatProperty(name = "Sensitivity", description = "Sensitivity of cursor position to mouse movement", default = 0.1, min = 0.0, max = 1.0) 
    bpy.types.Scene.tl_frame_follow = bpy.props.BoolProperty(name = "Follow Movement", description = "Current frame follows movement of selected keyframe", default = True) 
    bpy.types.Scene.tl_frame_current = bpy.props.BoolProperty(name = "Only Current Frame", 
                                        description = "Move only keys on the current frame. If disabled, all the keys in the playback range will be moved",
                                        default = True)
    bpy.types.Scene.tl_only_selected_bones = bpy.props.BoolProperty(name = "Only Selected Bones", description = "Only move keys on selected bones", default = False)
    
    bpy.types.TIMELINE_HT_KeyMover.append(draw_menu)
    
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
