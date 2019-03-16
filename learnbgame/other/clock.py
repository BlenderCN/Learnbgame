import bpy
import datetime

now = datetime.datetime.now()                        #Get the current date/time

hour = now.hour                                      #Get hours,
min = now.minute                                     #minutes
sec = now.second                                     #and seconds  


bpy.ops.object.select_all(action='TOGGLE')            #Deselects any objects which may be selected
bpy.ops.object.select_all(action='TOGGLE')            #Selects all objects
bpy.ops.object.delete()                               #Deletes all objects to allow for new clockface (will delete old one)


#Clock hand creation


bpy.ops.mesh.primitive_cube_add(location=(0,0,1))                                        
bpy.context.active_object.name = "hour hand"
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.transform.resize(value=(0.2,0.2,2.5))

bpy.context.active_object.rotation_euler = (-0.523599*hour)+(-min*0.008727),0,0          # 30 degrees*hour to get the correct placement on clock. But at
                                                                                           # half past the hour the hour hand should be placed somewhere between
                                                                                           # two hour numbers, hence the min*0.5 (*0.5 converts 60 minutes to 30 degrees)

bpy.ops.mesh.primitive_cube_add(location=(0,0,1))
bpy.context.active_object.name = "min hand"
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.transform.resize(value=(0.2,0.2,3)) 

bpy.context.active_object.rotation_euler = (-0.104720*min)+(-sec*0.001745),0,0             # Same as the hour hand except using the seconds to offset the minutes



bpy.ops.mesh.primitive_cube_add(location=(0,0,1))
bpy.context.active_object.name = "sec hand"
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.transform.resize(value=(0.1,0.1,3.5)) 

bpy.context.active_object.rotation_euler = -0.104720*sec,0,0

#Clock rim creation

for i in range(0,60):
	
	
	bpy.ops.mesh.primitive_cube_add(location=(0,0,8))              #add cube

	bpy.ops.transform.resize(value=(0.1,0.1,0.5))                  #resize it

	bpy.context.scene.cursor_location = 0,0,0                      #Set cursor to origin of scene
	bpy.ops.object.origin_set(type='ORIGIN_CURSOR')                #Set objects origin to cursor

	bpy.context.active_object.rotation_euler = 0.104720*i,0,0      #rotate object with radians (6 degrees)
 

#Clock numbers creation

for i in range(1,13):

    bpy.ops.object.text_add(rotation=(1.570796,0,1.5707960))            #Create text object
    bpy.ops.object.editmode_toggle()                                    #Go to edit mode to allow text editing
    bpy.ops.font.delete(type='PREVIOUS_WORD')                                     #Delete text
    bpy.ops.font.text_insert(text=str(i), accent=False)                 #Make the text a number (i)
    bpy.ops.object.editmode_toggle()                                    #Back to object mode to allow object manipulation

    bpy.context.active_object.name = "Text" +str(i)                     #Give a name to text of 'Texti' so they can be accessed later

    bpy.context.active_object.location = 0,0,6.5                        #Move text up to clock face edge

    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')                     #Set pivot point to origin of scene
    
    bpy.ops.object.convert(target='MESH', keep_original=False)          #Convert text to mesh so rotation can be applied
    
    bpy.ops.object.transform_apply(rotation=True)                                     #Apply rotation
    
    bpy.context.active_object.rotation_euler =-0.523599*i,0,0           #Rotate numbers around clock face
    
    bpy.ops.object.transform_apply(rotation=True)                                       #Apply rotation
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')                   #Set origins back to center or geometry (needed for correction, below)
    
    
#Corrects rotation for numbers on bottom half of clockface
    
for i in range(4,9):                                                    #Loop through numbers 4-9
    
    currentText = bpy.data.objects['Text'+str(i)]                       #Get the object
    
    bpy.context.view_layer.objects.active = currentText                      #Set the object to selected
 
    bpy.context.active_object.rotation_euler = 3.141593,0,0             #Rotate number to right way up (180 degrees)
  

bpy.context.scene.frame_current = 1    

#Insert keyframe 1

currentObject = bpy.data.objects['hour hand']
bpy.context.view_layer.objects.active= currentObject
bpy.context.view_layer.objects.active.select_set(True)
bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)    #Inserts first keyframe for rotation

currentObject = bpy.data.objects['min hand']
bpy.context.view_layer.objects.active= currentObject
bpy.context.view_layer.objects.active.select_set(True)
bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)

currentObject = bpy.data.objects['sec hand']
bpy.context.view_layer.objects.active= currentObject
bpy.context.view_layer.objects.active.select_set(True)
bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)
 
bpy.context.scene.frame_current = bpy.context.scene.frame_end           #Go to the last frame in playback range 


#Insert Keyframe 2

currentObject = bpy.data.objects['hour hand']
bpy.context.view_layer.objects.active= currentObject
bpy.context.view_layer.objects.active.select_set(True)
bpy.context.active_object.rotation_euler.x = bpy.context.active_object.rotation_euler.x+(0.000006*-bpy.context.scene.frame_end) #adds new rotation of 0.00033333*number of frames to get correct position
bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)

currentObject = bpy.data.objects['min hand']
bpy.context.view_layer.objects.active= currentObject
bpy.context.view_layer.objects.active.select_set(True)
bpy.context.active_object.rotation_euler.x = bpy.context.active_object.rotation_euler.x+(0.000070*-bpy.context.scene.frame_end) #Same as above except 0.004 degrees
bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)

currentObject = bpy.data.objects['sec hand']
bpy.context.view_layer.objects.active= currentObject
bpy.context.view_layer.objects.active.select_set(True)
bpy.context.active_object.rotation_euler.x = bpy.context.active_object.rotation_euler.x+(0.004189*-bpy.context.scene.frame_end) #Same as above except 0.24 degrees
bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)

bpy.context.area.type = 'GRAPH_EDITOR'              #Change screen to graph editor to do the next operation

bpy.ops.graph.interpolation_type(type='LINEAR')     #Set keyframe type to linear to avoid acceleration of the hands animation

bpy.context.area.type = 'TEXT_EDITOR'               #Change back to text editor

bpy.ops.screen.animation_play()                     #Play animation