# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Animated Render Border",
    "description": "Track objects or groups with the border render",
    "author": "Ray Mairlot",
    "version": (2, 1),
    "blender": (2, 76, 0),
    "location": "Properties> Render> Animated Render Border",
    "category": "Learnbgame"
}

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from bpy.app.handlers import persistent
from itertools import chain

trackableObjectTypes = ["MESH", "FONT", "CURVE", "SURFACE", "META", "LATTICE", "ARMATURE"] #EMPTY, LAMP, CAMERA and SPEAKER objects cannot currently be tracked.
noVertexObjectTypes = ["FONT", "META"]

#######Update functions########################################################


def updateFrame(self,context):
    
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)       
     
   
   
def refreshTracking(self,context):
       
    border = context.scene.animated_render_border
    
    #Removes bounding box when object or group is no longer being tracked.       
    for object in border.old_trackable_objects:

        #If object is renamed or deleted it wont exist in object list
        if object.name in bpy.data.objects:
                
            bpy.data.objects[object.name].show_bounds = False
        
    if validObject():
       
        if bpy.data.objects[border.object].type in noVertexObjectTypes: #Objects that don't have vertices
           
            border.use_bounding_box = True  
            
        elif bpy.data.objects[border.object].type == "ARMATURE" and border.bone != "":
            
            border.use_bounding_box = False
            
        elif bpy.app.version < (2, 76, 0) and bpy.data.objects[border.object].type in ["ARMATURE","LATTICE"]:
            
            border.use_bounding_box = False
    
    #Create a a list of currently tracked objects so bounding boxes can be cleared
    #when switching to a new object            
    if border.type == "Object" and border.object !="":
        
        border.old_trackable_objects.clear()
        objectAdd = border.old_trackable_objects.add()
        objectAdd.name = border.object
        
    elif border.type == "Group" and border.group !="":
        
        border.old_trackable_objects.clear()
        for object in bpy.data.groups[border.group].objects:
            if object.type in trackableObjectTypes:
                objectAdd = border.old_trackable_objects.add()
                objectAdd.name = object.name
    
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)    
    
    updateBoundingBox(self,context)       
                   

    
def updateBoundingBox(self,context):
        
    border = context.scene.animated_render_border
                            
    if border.type == "Object":  
        
        toggleObjectBoundingBox(True)
        toggleGroupBoundingBox(False)
        
    elif border.type == "Group":
        
        toggleObjectBoundingBox(False)
        toggleGroupBoundingBox(True)
        
    elif border.type == "Keyframe":
                    
        toggleObjectBoundingBox(False)                       
        toggleGroupBoundingBox(False)    

  
  
def toggleObjectBoundingBox(toggle):
    
    border = bpy.context.scene.animated_render_border
    
    #If addon is disabled
    if not border.enable:
        
        toggle = False
        
    elif border.type == "Object":
        
        toggle = border.draw_bounding_box    
        
    if border.object != "" and border.object in bpy.data.objects:
        
        bpy.data.objects[border.object].show_bounds = toggle


    
def toggleGroupBoundingBox(toggle):
    
    border = bpy.context.scene.animated_render_border
    
    if not border.enable:
        
        toggle = False
        
    elif border.type == "Group":
        
        toggle = border.draw_bounding_box   
    
    #if group isn't blank AND it exits in group lists (in case of renames)
    if border.group != "" and border.group in bpy.data.groups:
    
        for object in bpy.data.groups[border.group].objects:
            
            #When in group mode all objects should be toggled, otherwise all objects apart from the one being tracked in object mode should be.
            if border.type == "Group":
                
                if object.type in trackableObjectTypes:
                    
                    object.show_bounds = toggle
            
            else:
                
                if object.name != border.object: #object may be in a group AND be the selected tracking object
                
                    if object.type in trackableObjectTypes:
                            
                        object.show_bounds = toggle
            


def toggleTracking(self,context):
    
    border = context.scene.animated_render_border
    
    if border.enable and not context.scene.render.use_border:
        context.scene.render.use_border = True

    updateBoundingBox(self,context)
                    
    if border.enable:
        
        updateObjectList(self)
        
    updateFrame(self,context)



def updateBorderWithMinX(self,context):

    border = bpy.context.scene.animated_render_border     
    context.scene.render.border_min_x = border.border_min_x
    
    if round(border.border_min_x,2) >= round(border.border_max_x,2):
        
        border.border_max_x = round(border.border_min_x,2) + 0.01
            
     
     
def updateBorderWithMaxX(self,context):

    border = bpy.context.scene.animated_render_border     
    context.scene.render.border_max_x = border.border_max_x
    
    if round(border.border_min_x,2) >= round(border.border_max_x,2):
        
        border.border_min_x = round(border.border_max_x,2) - 0.01
                        
    
    
def updateBorderWithMinY(self,context):

    border = bpy.context.scene.animated_render_border     
    context.scene.render.border_min_y = border.border_min_y
    
    if round(border.border_min_y,2) >= round(border.border_max_y,2):
        
        border.border_max_y = round(border.border_min_y,2) + 0.01
    
    
    
def updateBorderWithMaxY(self,context):

    border = bpy.context.scene.animated_render_border     
    context.scene.render.border_max_y = border.border_max_y  
    
    if round(border.border_min_y,2) >= round(border.border_max_y,2):
        
        border.border_min_y = round(border.border_max_y,2) - 0.01          

          
#########Properties###########################################################


class animatedRenderBorderProperties(bpy.types.PropertyGroup):
    
    old_trackable_objects = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    trackable_objects = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    object = bpy.props.StringProperty(description = "The object to track", update=refreshTracking)
    
    bone = bpy.props.StringProperty(description = "The bone to track", update=refreshTracking)

    group = bpy.props.StringProperty(description = "The group to track", update=refreshTracking)

    type = bpy.props.EnumProperty(description = "The type of tracking to do, Object or Group or Keyframe", items=[
                                                                                                        ("Object","Object","Object"),
                                                                                                        ("Group","Group","Group"),
                                                                                                        ("Keyframe","Keyframe","Keyframe")], update=refreshTracking)

    use_bounding_box = bpy.props.BoolProperty(default=True, description="Use object's bounding box (less reliable, quicker) or object's 'inner points' for boundary checks", update=updateFrame)

    margin = bpy.props.IntProperty(default=3, description="Add a margin around the object's bounds", update=updateFrame)

    draw_bounding_box = bpy.props.BoolProperty(default=False, description="Draw the bounding boxes of the objects being tracked", update=updateBoundingBox)

    enable = bpy.props.BoolProperty(default=False, description="Enable Animated Render Border", update=toggleTracking)
    
    border_min_x = bpy.props.FloatProperty(description="Minimum X value for the render border", default=0, min=0, max=0.99, update=updateBorderWithMinX)
    
    border_max_x = bpy.props.FloatProperty(description="Maximum X value for the render border", default=1, min=0.01, max=1, update=updateBorderWithMaxX)

    border_min_y = bpy.props.FloatProperty(description="Minimum Y value for the render border", default=0, min=0, max=0.99, update=updateBorderWithMinY)

    border_max_y = bpy.props.FloatProperty(description="Maximum Y value for the render border", default=1, min=0.01, max=1, update=updateBorderWithMaxY)    



#########Frame Handler########################################################

#Only needed when manually running from text editor
#bpy.app.handlers.frame_change_post.clear()
#bpy.app.handlers.scene_update_post.clear()


@persistent
def animated_render_border(scene):
        
    scene = bpy.context.scene
    camera = scene.camera
    border = scene.animated_render_border
    
    cameraExists = False
    
    if camera:
        if camera.type == "CAMERA":
            cameraExists = True
    
    if border.enable and cameraExists:
        #If object is chosen but consequently renamed, it can't be tracked.
        if validObject() or validGroup(): 
        
            objs = [] 
            if border.type == "Object":  
                objs = [bpy.data.objects[border.object]]
            elif border.type == "Group":
                objs = (object for object in bpy.data.groups[border.group].objects if object.type in trackableObjectTypes) #Type of objects that can be tracked
            
            coords_2d = []
            for obj in objs:
                
                verts = []
                if border.use_bounding_box or obj.type in noVertexObjectTypes: #Objects that have no vertices
                    
                    #Lattices and Armatures can't use bounding box in pre 2.76 version of blender.
                    if bpy.app.version < (2, 76, 0) and obj.type in ["ARMATURE","LATTICE"]:
                    
                        if obj.type == "LATTICE":
                            
                            verts = (vert.co_deform for vert in obj.data.points)
                            
                        elif obj.type == "ARMATURE":
                            
                            if border.bone == "":
                        
                                verts = (chain.from_iterable((bone.head, bone.tail) for bone in obj.pose.bones))
                        
                            else:
                                
                                bone = bpy.data.objects[border.object].pose.bones[border.bone]
                                verts = [bone.head, bone.tail]                                                   
                        
                    else:
                        
                        verts = (Vector(corner) for corner in obj.bound_box)
                
                elif obj.type == "MESH":

                    verts = (vert.co for vert in obj.data.vertices)
                
                elif obj.type == "CURVE":
                    
                    verts = (vert.co for spline in obj.data.splines for vert in spline.bezier_points)
                
                elif obj.type == "SURFACE":
                    
                    verts = (vert.co for spline in obj.data.splines for vert in spline.points)
                    
                elif obj.type == "LATTICE":
                           
                    verts = (vert.co_deform for vert in obj.data.points)
                        
                elif obj.type == "ARMATURE":

                    if border.bone == "":
                        
                        verts = (chain.from_iterable((bone.head, bone.tail) for bone in obj.pose.bones))
                        
                    else:
                        
                        bone = bpy.data.objects[border.object].pose.bones[border.bone]
                        verts = [bone.head, bone.tail]
                        
                wm = obj.matrix_world     #Vertices will be in local space unless multiplied by the world matrix
                for coord in verts:
                    coords_2d.append(world_to_camera_view(scene, camera, wm*coord))
            
            #If a group is empty there will be no coordinates
            if len(coords_2d) > 0:
                
                minX = 1
                maxX = 0
                minY = 1
                maxY = 0
                
                for x, y, distance_to_lens in coords_2d:
                                    
                    #Points behind camera will have negative coordinates, this makes them positive                
                    if distance_to_lens<0:
                        y = y *-1
                        x = x *-1               
                    
                    if x<minX:
                        minX = x
                    if x>maxX:
                        maxX = x
                    if y<minY:
                        minY = y
                    if y>maxY:
                        maxY = y
                                            
                margin = border.margin/100
                
                #Haven't worked out why I'm multiplying 'shift_x' and 'shift_y' by 2
                if scene.render.resolution_x > scene.render.resolution_y:
                        
                    aspectRatio = 2 * (scene.render.resolution_x / scene.render.resolution_y) * (scene.render.pixel_aspect_x / scene.render.pixel_aspect_y) 
                    
                    cameraShiftX = scene.camera.data.shift_x * 2
                    cameraShiftY = scene.camera.data.shift_y * aspectRatio
                    
                else:
                    
                    aspectRatio = 2 * (scene.render.resolution_y / scene.render.resolution_x) * (scene.render.pixel_aspect_y / scene.render.pixel_aspect_x) 
                    
                    cameraShiftX = scene.camera.data.shift_x*aspectRatio
                    cameraShiftY = scene.camera.data.shift_y*2
                    
                
                scene.render.border_min_x = (minX - margin) - cameraShiftX
                scene.render.border_max_x = (maxX + margin) - cameraShiftX
                scene.render.border_min_y = (minY - margin) - cameraShiftY
                scene.render.border_max_y = (maxY + margin) - cameraShiftY
            
        elif border.type == "Keyframe":
            
            scene.render.border_min_x = border.border_min_x
            scene.render.border_max_x = border.border_max_x
            scene.render.border_min_y = border.border_min_y
            scene.render.border_max_y = border.border_max_y
          


@persistent          
def updateObjectList(scene):
            
    border = bpy.context.scene.animated_render_border     
    
    if border.enable:        
        border.trackable_objects.clear()
        
        for object in bpy.context.scene.objects:
            if object.type in trackableObjectTypes: #Types of object that can be tracked
                objectAdd = border.trackable_objects.add()
                objectAdd.name = object.name    
                           


###########Functions############################################################

def render(self, context):
    
    #If blender is being run in the background (command line) do not use the modal renderer
    if bpy.app.background:
    
        print("Rendering frame "+str(context.scene.frame_current))
    
        oldStart = context.scene.frame_start
        oldEnd = context.scene.frame_end
        oldCurrent = context.scene.frame_current
                
        for i in range(oldStart, oldEnd+1):
                            
            context.scene.frame_set(i)
            animated_render_border(context.scene)
            
            context.scene.frame_start = i
            context.scene.frame_end = i
             
            bpy.ops.render.render(animation=True)
                
        context.scene.frame_current = oldCurrent    
        context.scene.frame_start = oldStart
        context.scene.frame_end = oldEnd

    else:
    
        if self.counter > self.oldEnd:
            
            self.finished = True
            
        else:
            
            print("Rendering frame "+str(self.counter))
                    
            context.scene.frame_set(self.counter)
            animated_render_border(context.scene)
            
            context.scene.frame_start = self.counter
            context.scene.frame_end = self.counter
             
            bpy.ops.render.render(animation=True)
            
            context.window_manager.progress_update(self.counter)
            
            self.counter += context.scene.frame_step
        
        
def endRender(self, context):
    
    context.scene.frame_current = self.oldCurrent    
    context.scene.frame_start = self.oldStart
    context.scene.frame_end = self.oldEnd
    
    context.window_manager.event_timer_remove(self.timer)
    self.timer = None
    context.window_manager.progress_end()
       
    
def mainFix(context):
                
    context.scene.render.use_border = True
    
    bpy.context.scene.frame_set(bpy.context.scene.frame_current) 
    
    
def insertKeyframe(context):
    
    border = context.scene.animated_render_border
    
    if round(bpy.context.scene.render.border_min_x,2) == round(bpy.context.scene.render.border_max_x,2):
        
        bpy.context.scene.render.border_max_x += 0.01 
        
    if round(bpy.context.scene.render.border_min_y,2) == round(bpy.context.scene.render.border_max_y,2):
        
        bpy.context.scene.render.border_max_y += 0.01         

    refreshUIValues(context)       
        
    context.scene.keyframe_insert(data_path="animated_render_border.border_min_x")  
    context.scene.keyframe_insert(data_path="animated_render_border.border_max_x")  
    context.scene.keyframe_insert(data_path="animated_render_border.border_min_y")  
    context.scene.keyframe_insert(data_path="animated_render_border.border_max_y")    
    
    
def deleteKeyframe(context):

    if context.scene.animation_data.action:
        
        context.scene.keyframe_delete(data_path="animated_render_border.border_min_x")  
        context.scene.keyframe_delete(data_path="animated_render_border.border_max_x")  
        context.scene.keyframe_delete(data_path="animated_render_border.border_min_y")  
        context.scene.keyframe_delete(data_path="animated_render_border.border_max_y")   
    

def validObject():
    
    border = bpy.context.scene.animated_render_border
    
    if border.type == "Object" and border.object != "" and border.object in bpy.data.objects: #If object is chosen as object but renamed, it can't be tracked.
        
        return True    
  
    
def validGroup():
    
    border = bpy.context.scene.animated_render_border
    
    if border.type == "Group" and border.group != "" and border.group in bpy.data.groups:
        
        return True   
    
    
def checkForErrors():
    
    border = bpy.context.scene.animated_render_border
    scene = bpy.context.scene
    
    errors = ""
         
    if not scene.render.use_border and border.enable:

        errors += "\n 'Border' is disabled in 'Dimensions' panel."

    if scene.camera:    
        if scene.camera.type != "CAMERA":

            errors += "\n Active camera must be a Camera object, not "+scene.camera.type.lower().capitalize()+"'."

    else:

        errors += "\n No camera is set in scene properties."
       
    if border.type == "Object" and border.object != "" and border.object not in bpy.data.objects:    

        errors += "\n The object selected to be tracked does not exist."
     
    elif border.type == "Group" and border.group != "" and border.group not in bpy.data.groups:

        errors += "\n The group selected to be tracked does not exist."
     
    #Checks for empty groups or groups with no trackable objects
    trackableObjects = 0
    if border.type == "Group" and border.group != "" and border.group in bpy.data.groups:

        for object in bpy.data.groups[border.group].objects:

            if object.type in trackableObjectTypes:

                trackableObjects+=1

        if trackableObjects < 1:

            errors += "\n The selected group has no trackable objects."
 
    if errors != "":
        errors = "\n The following error(s) have to be addressed before rendering:"+errors
        raise Exception(errors)         
    
  
def refreshUIValues(context):
    
    border = bpy.context.scene.animated_render_border
    
    #Values need to be stored before changing, otherwise the border update functions will kick in
    #E.g. Changing 'border_min_x' could cause 'border_max_x' to change before it has been stored. 
    min_x = context.scene.render.border_min_x
    max_x = context.scene.render.border_max_x
    min_y = context.scene.render.border_min_y
    max_y = context.scene.render.border_max_y
    
    border.border_min_x = min_x
    border.border_max_x = max_x
    border.border_min_y = min_y
    border.border_max_y = max_y
      
      
###########UI################################################################


class RENDER_PT_animated_render_border(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Animated Render Border"
    bl_idname = "RENDER_PT_animated_render_border"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"


    def draw_header(self, context):

        self.layout.prop(context.scene.animated_render_border, "enable", text="")


    def draw(self, context):
                        
        layout = self.layout
        scene = context.scene
        border = context.scene.animated_render_border
        
        layout.active = scene.animated_render_border.enable
        
        error = 0
        
        if not context.scene.render.use_border and border.enable:
            row = layout.row()
            split = row.split(0.7)
            
            column = split.column()
            column.label(text="'Border' is disabled in", icon="ERROR")
            column.label(text="'Dimensions' panel.", icon="SCULPT_DYNTOPO")
            
            column = split.column()         
            column.operator("render.animated_render_border_fix", text="Fix")
            
            error+=1
        
        if scene.camera:    
            if scene.camera.type != "CAMERA":
                row = layout.row()
                row.label(text="Active camera must be a Camera", icon="ERROR")
                row = layout.row()
                row.label(text="object, not '"+scene.camera.type.lower().capitalize()+"'.", icon="SCULPT_DYNTOPO")
                
                error+=1
        
        else:
            row = layout.row()
            row.label(text="No camera is set in scene properties", icon="ERROR")
            
            error+=1
            
        if border.type == "Object" and border.object != "" and border.object not in bpy.data.objects:    
            row = layout.row()
            row.label(text="The object selected to be tracked", icon="ERROR")
            row = layout.row()
            row.label(text="does not exist.", icon="SCULPT_DYNTOPO")
             
            error+=1
         
        elif border.type == "Group" and border.group != "" and border.group not in bpy.data.groups:
            row = layout.row()
            row.label(text="The group selected to be tracked", icon="ERROR") 
            row = layout.row()
            row.label(text="does not exist.", icon="SCULPT_DYNTOPO")
             
            error+=1        
         
        #Checks for empty groups or groups with no trackable objects
        trackableObjects = 0
        if border.type == "Group" and border.group != "" and border.group in bpy.data.groups:
            
            for object in bpy.data.groups[border.group].objects:
                
                if object.type in trackableObjectTypes:
                    
                    trackableObjects+=1
                    
            if trackableObjects < 1:
                
                row = layout.row()
                row.label(text="The selected group has no trackable", icon="ERROR") 
                row = layout.row()
                row.label(text="objects.", icon="SCULPT_DYNTOPO")
                
                error+=1
                     
        column = layout.column()
         
        row = column.row()
        row.prop(scene.animated_render_border, "type",expand=True)
        row = column.row()
        
        if border.type == "Keyframe":
        
            column = layout.column()
            column.active = context.scene.render.use_border and border.enable
            
            col = column.column(align=True)
            col.operator("render.animated_render_border_insert_keyframe", text="Insert Keyframe", icon="KEY_HLT")
            col.operator("render.animated_render_border_delete_keyframe", text="Delete Keyframe", icon="KEY_DEHLT")    
            col.label(text="Border Vales:")
            
            if scene.render.border_min_x != border.border_min_x or \
               scene.render.border_max_x != border.border_max_x or \
               scene.render.border_min_y != border.border_min_y or \
               scene.render.border_min_y != border.border_min_y:
                row = column.row()
                row.operator("render.animated_render_border_refresh_values", text="Refresh to synchonise border values", icon="FILE_REFRESH")  
                      
            row = column.row()
            row.label(text="")
            row.prop(scene.animated_render_border, "border_max_y", text="Max Y")  
            row.label(text="")
            row = column.row(align=True)
            row.prop(scene.animated_render_border, "border_min_x", text="Min X")  
            row.label(text="")
            row.prop(scene.animated_render_border, "border_max_x", text="Max X")  
            row = column.row()
            row.label(text="")
            row.prop(scene.animated_render_border, "border_min_y", text="Min Y")        
            row.label(text="")
            
            row = column.row()
            row.label(text="")
            row = column.row()          
                     
            row.operator("render.animated_render_border_render", text="Render Animation", icon="RENDER_ANIMATION")                        
            
        else:
            
            if border.type == "Object":
                row.label(text="Object to track:")
                row = column.row()
                
                #Armatures and Lattices can only be tracked in blender 2.76 and later.
                if validObject() and bpy.app.version < (2, 76, 0) and bpy.data.objects[border.object].type in ["ARMATURE","LATTICE"]:
                    row = column.row()
                    row.label(text=bpy.data.objects[border.object].type.lower().capitalize()+" objects can only use bounding", icon="ERROR")
                    row = column.row()
                    row.label(text="box tracking in Blender 2.76 and later.", icon="SCULPT_DYNTOPO")
                    row = column.row()   
                
                objectIcon = "OBJECT_DATA"
                if validObject():
                    objectIcon = "OUTLINER_OB_"+bpy.data.objects[border.object].type
                    
                    #Removed as speaker objects cannot be tracked
                    #if bpy.data.objects[border.object].type == "SPEAKER":   
                    #    objectIcon = "SPEAKER" #Speaker doesn't have it's own icon like other objects
                     
                row.prop_search(scene.animated_render_border, "object", scene.animated_render_border, "trackable_objects", text="", icon=objectIcon) #Where my property is, name of property, where list I want is, name of list                    
                
            else:
                row.label(text="Group to track:")
                
                #Armatures and Lattices can only be tracked in blender 2.76 and later.
                warningNeeded = False
                if validGroup() and bpy.app.version < (2, 76, 0) and border.use_bounding_box:
                
                    for object in bpy.data.groups[border.group].objects:
                        
                        if bpy.data.objects[object.name].type in ["ARMATURE","LATTICE"]:
                            
                            warningNeeded = True
                            
                            #Only need to find 1 object for it to be an error, can cancel after that
                            break;
                
                if warningNeeded:            
                    row = column.row()
                    row.label(text="Armature or Lattice objects in this group", icon="ERROR")
                    row = column.row()
                    row.label(text="can only use bounding box tracking in", icon="SCULPT_DYNTOPO")
                    row = column.row()
                    row.label(text="Blender 2.76 and later.", icon="SCULPT_DYNTOPO")
                    row = column.row()  
                
                row = column.row()
                row.prop_search(scene.animated_render_border, "group", bpy.data, "groups", text="")
            
            
            if border.type == "Object" and border.object == "" or \
               border.type == "Group" and border.group == "":
                                
                enabled = False
            else:
                enabled = True
            
            #New column is to separate it from previous row, it needs to be able to be disabled.
            columnMargin = row.column()
            columnMargin.enabled = enabled    
            columnMargin.prop(scene.animated_render_border, "margin", text="Margin")    
            
            if validObject():
                if bpy.data.objects[border.object].type == "ARMATURE":
        
                   row = column.row()
                   row.label(text="Bone to track (optional):")
                   row = column.row()
                   row.prop_search(scene.animated_render_border, "bone", bpy.data.objects[border.object].data, "bones", text="", icon="BONE_DATA") #Where my property is, name of property, where list I want is, name of list
                   row.label(text="")    
                
            row = column.row()
            
            noVertices = False
            
            if validObject() and bpy.data.objects[border.object].type not in ["ARMATURE","LATTICE"]:

                if bpy.data.objects[border.object].type in noVertexObjectTypes or border.bone != "": #Objects without vertices or bones
                    
                    noVertices = True
                    
            elif border.type == "Group" and border.group == "":
                
                    noVertices = True
                    
            elif border.type == "Object":
                
                if border.object == "":
                        
                    noVertices = True
                    
                if bpy.app.version < (2, 76, 0):
                    
                    noVertices = True     
                                            
            if noVertices:    
                row.enabled = False
            else:
                row.enabled = True   
            row.prop(scene.animated_render_border, "use_bounding_box", text="Use Bounding Box")
            
            row = column.row()
            row.enabled = enabled                 
            row.prop(scene.animated_render_border, "draw_bounding_box", text="Draw Bounding Box")                
  
            row = column.row()     
            row.enabled = enabled and error == 0
            
            if error > 0:
                renderLabel = "Fix errors to render"
            else:
                renderLabel = "Render Animation"
                     
            row.operator("render.animated_render_border_render", text=renderLabel, icon="RENDER_ANIMATION")
            
        if bpy.context.user_preferences.addons['animatedRenderborder'].preferences.display_border_dimensions:
            
            resolutionX = (scene.render.resolution_x/100)*scene.render.resolution_percentage
            resolutionY = (scene.render.resolution_y/100)*scene.render.resolution_percentage
                
            xSize = round(resolutionX*(scene.render.border_max_x - scene.render.border_min_x))
            ySize = round(resolutionY*(scene.render.border_max_y - scene.render.border_min_y))

            row = column.row()
            row.label(text="Border dimensions: "+str(xSize)+" x "+str(ySize)+" pixels")
        


###########OPERATORS#########################################################
       

class RENDER_OT_animated_render_border_render(bpy.types.Operator):
    """Render the sequence using the animated render border"""
    bl_idname = "render.animated_render_border_render"
    bl_label = "Render Animation"
    
    finished = False
    counter = 0
    timer = None
    oldStart = 0
    oldEnd = 0
    oldCurrent = 0

    #Only use modal if blender is not being run in the background (command line)
    if not bpy.app.background:

        def modal(self, context, event):
                    
            if event.type == 'ESC':
                
                print("Render Cancelled")
                
                endRender(self, context)
                
                return {'CANCELLED'}
            
            elif event.type == 'TIMER' and not self.finished:
                
                render(self, context)

            elif self.finished:
                
                print("Finished rendering")
                
                self.report({'INFO'}, "Border rendering finished")
                
                endRender(self, context)
                
                return {'FINISHED'}
            
            return {'RUNNING_MODAL'}
     
    
    def execute(self, context):
        
        #Raises Exception if error(s) are found                         
        checkForErrors() 
                             
        if bpy.context.scene.camera:
            
            #If blender is running in the background (command line) don't use modal renderer
            if bpy.app.background:
                
                render(self, context)
                
                return {'FINISHED'}
                                    
            else:
                
                self.finished = False
                self.counter = bpy.context.scene.frame_start
                self.timer = context.window_manager.event_timer_add(0.1, context.window)
                self.oldStart = bpy.context.scene.frame_start
                self.oldEnd = bpy.context.scene.frame_end
                self.oldCurrent = bpy.context.scene.frame_current
                
                context.window_manager.progress_begin(0,context.scene.frame_end)
                
                context.window_manager.modal_handler_add(self)
                
                return {'RUNNING_MODAL'}
        
        else:
                        
            return {'CANCELLED'}
            
 
         
class RENDER_OT_animated_render_border_fix(bpy.types.Operator):
    """Fix the render border by turning on 'Border' rendering"""
    bl_idname = "render.animated_render_border_fix"
    bl_label = "Render Border Fix"

    def execute(self, context):
 
        mainFix(context)
            
        return {'FINISHED'}    
    
    
class RENDER_OT_animated_render_border_insert_keyframe(bpy.types.Operator):
    """Insert a keyframe for all the render border values"""
    bl_idname = "render.animated_render_border_insert_keyframe"
    bl_label = "Insert Animated Render Border Keyframe"

    def execute(self, context):
     
        insertKeyframe(context)
            
        return {'FINISHED'}  
    
    
class RENDER_OT_animated_render_border_delete_keyframe(bpy.types.Operator):
    """Delete a keyframe for all the render border values"""
    bl_idname = "render.animated_render_border_delete_keyframe"
    bl_label = "Delete Animated Render Border Keyframe"

    def execute(self, context):
     
        deleteKeyframe(context)
            
        return {'FINISHED'}  
    
    
class RENDER_OT_animated_render_border_refresh_values(bpy.types.Operator):
    """Refresh the UI values in case the border was manually redrawn in the viewport"""
    bl_idname = "render.animated_render_border_refresh_values"
    bl_label = "Delete Animated Render Border Keyframe"

    def execute(self, context):
     
        refreshUIValues(context)
            
        return {'FINISHED'}           
            
            
###########USER PREFERENCES##################################################            
            
                   
class AnimatedRenderBorderPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__  
    
    display_border_dimensions = bpy.props.BoolProperty(name="Display border dimensions",default=False,description="Shows the dimensions of the current border, under the 'Render Animation' button")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "display_border_dimensions")
               

def register():
    
    bpy.utils.register_class(animatedRenderBorderProperties)
    
    bpy.types.Scene.animated_render_border = bpy.props.PointerProperty(type=animatedRenderBorderProperties)
    
    bpy.app.handlers.frame_change_post.append(animated_render_border)
    bpy.app.handlers.scene_update_post.append(updateObjectList)
    
    bpy.utils.register_class(RENDER_PT_animated_render_border)
    bpy.utils.register_class(RENDER_OT_animated_render_border_render)
    bpy.utils.register_class(RENDER_OT_animated_render_border_fix)
    bpy.utils.register_class(RENDER_OT_animated_render_border_insert_keyframe)   
    bpy.utils.register_class(RENDER_OT_animated_render_border_delete_keyframe)  
    bpy.utils.register_class(RENDER_OT_animated_render_border_refresh_values)  
    bpy.utils.register_class(AnimatedRenderBorderPreferences)        
    
    
def unregister():
    
    bpy.app.handlers.frame_change_post.remove(animated_render_border)        
    bpy.app.handlers.scene_update_post.remove(updateObjectList)
    
    bpy.utils.unregister_class(RENDER_PT_animated_render_border)
    bpy.utils.unregister_class(RENDER_OT_animated_render_border_render)
    bpy.utils.unregister_class(RENDER_OT_animated_render_border_fix)
    bpy.utils.unregister_class(RENDER_OT_animated_render_border_insert_keyframe)    
    bpy.utils.unregister_class(RENDER_OT_animated_render_border_delete_keyframe)  
    bpy.utils.unregister_class(RENDER_OT_animated_render_border_refresh_values)        
    bpy.utils.unregister_class(animatedRenderBorderProperties)
    bpy.utils.unregister_class(AnimatedRenderBorderPreferences)    
    
    del bpy.types.Scene.animated_render_border
    

if __name__ == "__main__":
    register()