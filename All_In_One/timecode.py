bl_info = {
    "name": "Timecode",
    "author": "Ray Mairlot",
    "version": (1, 1, 5),
    "blender": (2, 78, 0),
    "location": "Timeline Header or Space> Set timecode",
    "description": "Allows viewing and setting the current frame via a timecode (HH:MM:SS:FF)",
    "category": "Learnbgame",
    }
    


import bpy
import blf
import bgl
from bpy.app.handlers import persistent


handle = None


def containsLetters(itemList):

    letters = [item for item in itemList if item.isdigit() == False]
    
    return len(letters) > 0



def calculateTimecode():

    fps = bpy.context.scene.render.fps
    timecode = bpy.context.scene.timecode
    totalFrames = bpy.context.scene.frame_current

    #Stops all 4 time property's update functions from updating. Only 1 needs to.
    timecode.updating = True
            
    hours = int((totalFrames / fps) / 3600)
    
    if hours >= 1:
        
        timecode.hours = str(hours).zfill(2)   
        totalFrames = totalFrames - ((hours * fps) * 3600)
        
    else:
        
        timecode.hours = "00"  
        
    minutes = int((totalFrames / fps) / 60)
    
    if minutes >= 1:
        
        timecode.minutes = str(minutes).zfill(2)
        totalFrames = totalFrames - ((minutes * fps) * 60)        
        
    else:
        
        timecode.minutes = "00"  
            
    seconds = int(totalFrames / fps)
    
    if seconds >= 1:
        
        timecode.seconds = str(seconds).zfill(2)
        totalFrames = totalFrames - (seconds * fps)        
        
    else:
        
        timecode.seconds = "00"   

    #Now that the other property's update functions have been skipped, re-enable them and let 'frames' trigger the update once.
    timecode.updating = False

    frames = totalFrames
    
    if frames >= 1:          
        timecode.frames = str(frames).zfill(2)
        
    else:
        
        timecode.frames = "00"



def formatTimecode():

    timecode = bpy.context.scene.timecode
    
    timecode.hours = timecode.hours.zfill(2)
    timecode.minutes = timecode.minutes.zfill(2)
    timecode.seconds = timecode.seconds.zfill(2)
    timecode.frames = timecode.frames.zfill(2)
    
    fps = bpy.context.scene.render.fps
    
    maximumEndFrame = bpy.types.Scene.bl_rna.properties['frame_end'].hard_max
    
    maximumHours = int((maximumEndFrame / fps) / 3600)
    
    if int(timecode.hours) > maximumHours:
        
        timecode.hours = str(maximumHours)
        
    if int(timecode.minutes) > 59:
        
        timecode.minutes = str(59)
        
    if int(timecode.seconds) > 59:
        
        timecode.seconds = str(59)
        
    if int(timecode.frames) > (fps - 1):
        
        timecode.frames = str(fps - 1)



def toggle3DViewLabel(self, context):
    
    global handle    
    preferences = bpy.context.user_preferences.addons['timecode'].preferences

    if preferences.display_in_3d_view:

        handle = bpy.types.SpaceView3D.draw_handler_add(drawTimecode, (), 'WINDOW', 'POST_PIXEL')
        
    elif preferences.display_in_3d_view == False:
    
        bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')



def toggleTimelineHeaderUI(self, context):
    
    preferences = bpy.context.user_preferences.addons['timecode'].preferences
    
    if preferences.display_in_header:
    
        bpy.types.TIME_HT_header.append(TimecodeMenu)
        
    elif preferences.display_in_header == False:
        
        bpy.types.TIME_HT_header.remove(TimecodeMenu)
        
        
        
def setFrame(self, context):

    timecode = context.scene.timecode
                
    #Don't trigger this function again when values are being updated by this function or if letters have been entered
    if not timecode.updating:

        stringInputs = [timecode.hours, timecode.minutes, timecode.seconds, timecode.frames]

        if not containsLetters(stringInputs):

            #Prevents infite loop by not re-triggering this function when performing 'zfill' on properties
            timecode.updating = True
            formatTimecode()
            timecode.updating = False

            fps = context.scene.render.fps
            hours = int(timecode.hours)
            minutes = int(timecode.minutes)
            seconds = int(timecode.seconds)
            frames = int(timecode.frames)
                
            currentFrame = (hours * fps * 3600) + (minutes * fps * 60) + (seconds * fps) + frames
            
            #Prevent infite loop by not triggering frame_change_post when setting the new frame
            timecode.updating = True
            formatTimecode()            
            bpy.context.scene.frame_set(currentFrame)
            timecode.updating = False
            
        else:
            
            #If letters have been entered just ignore it by recalculating what the timecode should be
            timecode.updating = True
            calculateTimecode()
            timecode.updating = False
        


class TimecodeProperties(bpy.types.PropertyGroup):
    
    hours = bpy.props.StringProperty(name="Hours", description="Hours", default="00", update=setFrame)

    minutes = bpy.props.StringProperty(name="Minutes", description="Minutes", default="00", update=setFrame)
    
    seconds = bpy.props.StringProperty(name="Seconds", description="Seconds", default="00", update=setFrame)    

    frames = bpy.props.StringProperty(name="Frames", description="Frames", default="00", update=setFrame)
    
    updating = bpy.props.BoolProperty(name="Updating", default=False)

    rendering = bpy.props.BoolProperty(name="Rendering", description="Keeps track of when the files is being rendered to prevent frame_change_post handler from running", default=False)



class SetTimecodeOperator(bpy.types.Operator):
    bl_idname = "scene.set_timecode"
    bl_label = "Set timecode"


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        return {'FINISHED'}


    def draw(self, context):
        
        layout = self.layout
        row = layout.row(align=False)
        row.label("Timecode:")
        
        row = layout.row(align=True)
        row.prop(context.scene.timecode, "hours", text="")
        row.label("   :")
        row.prop(context.scene.timecode, "minutes", text="")
        row.label("   :")
        row.prop(context.scene.timecode, "seconds", text="")
        row.label("   :")
        row.prop(context.scene.timecode, "frames", text="")



@persistent
def timecodeUpdate(scene):

    #Prevent infinite loop by not re-triggering when the current frame is being set by 'setFrame'
    #Is also prevented from running when rendering. See: https://github.com/RayMairlot/Timecode/issues/2
    if not scene.timecode.updating and not scene.timecode.rendering:
                    
        calculateTimecode()



@persistent
def startedRendering(scene):

    bpy.context.scene.timecode.rendering = True



@persistent
def finishedRendering(scene):

    bpy.context.scene.timecode.rendering = False

                    

#Only needed when manually running from text editor
#bpy.app.handlers.frame_change_post.clear()
#bpy.app.handlers.frame_change_post.append(timecodeUpdate)



def drawTimecode():
    
    timecode = bpy.context.scene.timecode
    
    pixelSize = bpy.context.user_preferences.system.pixel_size
    dpi = bpy.context.user_preferences.system.dpi
    dpiFac = pixelSize * dpi
        
    xPosition = 69 + ((dpiFac - 70) / 4)
    
    #Default dpi will make y = 25
    yPosition = dpiFac / 2.88
    
    blf.position(0, xPosition, yPosition, 0)
    blf.size(0, 11, int(dpiFac))
    bgl.glColor3f(1.0, 1.0, 1.0)
    blf.draw(0, timecode.hours + ':' + timecode.minutes + ':' + timecode.seconds + ':' + timecode.frames)



def TimecodeMenu(self, context):
                
    layout = self.layout
    row = layout.row(align=False)
    row.label("Timecode:")
    row.scale_x = 0.8
    
    labelScale = 0.6
    propertyScale = 0.3
    
    row = layout.row(align=True)
    
    column = row.column(align=True)    
    column.prop(context.scene.timecode, "hours", text="")
    column.scale_x = propertyScale
    
    column = row.column(align=True)
    column.label(":")
    column.scale_x = labelScale
    
    column = row.column(align=True)    
    column.prop(context.scene.timecode, "minutes", text="")
    column.scale_x = propertyScale
    
    column = row.column(align=True)
    column.label(":")
    column.scale_x = labelScale
    
    column = row.column(align=True)    
    column.prop(context.scene.timecode, "seconds", text="")
    column.scale_x = propertyScale
    
    column = row.column(align=True)
    column.label(":")
    column.scale_x = labelScale
    
    column = row.column(align=True)    
    column.prop(context.scene.timecode, "frames", text="")
    column.scale_x = propertyScale
    


class TimecodePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__  
    
    display_in_header = bpy.props.BoolProperty(name="Timeline header", default=True, description="Display the timecode UI in the Timeline header", update=toggleTimelineHeaderUI)
    display_in_3d_view = bpy.props.BoolProperty(name="3D View", default=True, description="Display the timecode in the 3D View, above the selected object's name", update=toggle3DViewLabel)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "display_in_3d_view")
        row.prop(self, "display_in_header")



def register():
    global handle

    bpy.utils.register_class(SetTimecodeOperator)
    bpy.utils.register_class(TimecodeProperties)
    bpy.utils.register_class(TimecodePreferences)
    bpy.types.Scene.timecode = bpy.props.PointerProperty(type=TimecodeProperties)
    bpy.app.handlers.frame_change_post.append(timecodeUpdate)
    bpy.app.handlers.render_pre.append(startedRendering)
    bpy.app.handlers.render_post.append(finishedRendering)

    handle = bpy.types.SpaceView3D.draw_handler_add(drawTimecode, (), 'WINDOW', 'POST_PIXEL')
    bpy.types.TIME_HT_header.append(TimecodeMenu) 



def unregister():
    
    preferences = bpy.context.user_preferences.addons['timecode'].preferences
    
    if preferences.display_in_3d_view:
    
        bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
        
    if preferences.display_in_header:
    
        bpy.types.TIME_HT_header.remove(TimecodeMenu) 
        
    bpy.utils.unregister_class(SetTimecodeOperator)
    bpy.utils.unregister_class(TimecodeProperties)
    bpy.utils.unregister_class(TimecodePreferences)    
    bpy.app.handlers.frame_change_post.remove(timecodeUpdate)
    bpy.app.handlers.render_pre.remove(startedRendering)
    bpy.app.handlers.render_post.remove(finishedRendering)



if __name__ == "__main__":
    register()
