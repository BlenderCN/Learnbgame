#=========================================================================#
#       "A_ Face MoTrack 0.1" -> Copyright (C) 2018 Alexandre Mulek       #
#                                                                         #
#            Official Website -> https://www.alexandremulek.com           #
#                                                                         #
#              Official Email -> info@alexandremulek.com                  #
#                                                                         #
#               Private Email -> alexandremulek@hotmail.com               #
#=========================================================================#
#                                                                         #
#  This program is free software: you can redistribute it and/or modify   #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation, either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful,        #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#  GNU General Public License for more details.                           #
#                                                                         #
#  You should have received a copy of the GNU General Public License      #
#  along with this program.  If not, see <https://www.gnu.org/licenses/>  #
#                                                                         #
#  IMPORTANT: PLEASE READ THE "A_ SoftwareLicense Agreement.txt" AND      #
#  "Python License.txt" AS WELL.                                          #
#                                                                         #
#=========================================================================#


bl_info = {
    "name": "A_ Face MoTrack",
	"description": "Capturing facial movements to animate characters.",
    "author": "Alexandre Mulek",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Movie Clip Editor > Tools > A_ Face MoTrack",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
    }


import bpy
import requests     #--AFACEMOTRACK, AMULEKNEWS,
import webbrowser   #--AFACEMOTRACK, AMULEKNEWS,
import math
import os


MarkersScale = 1.0
ClipStart = 1
AllMarkersNames = ['A_ Nose','A_ Nose R','A_ Nose L']
AllMarkersNames = AllMarkersNames + ['A_ Lid B R','A_ Lid T R','A_ Lid R','A_ Lid B L','A_ Lid T L','A_ Lid L']
AllMarkersNames = AllMarkersNames + ['A_ Brow','A_ Brow R','A_ Brow L','A_ Forehead']

NoteLabel = '# '
MenuItems = ''

DataActionMeter = 0

DatabaseStart = 1
DatabaseEnd = 900
DatabaseMsg = ''
DatabaseProcessed = ''

DatabaseClipName = ''
ObjectSelected = ''

ActionStart = 1
ActionEnd = 900
ActionMsg = ''




#--AMULEKNEWS--#
NewsHost = "https://www.alexandremulek.com"
NewsUrlRequest = NewsHost + "/apps/apps/a__mulek_news/a__mulek_news_0p1.php"
NewsUrlHome = NewsHost + "/apps/index.php"
NewsUrlPayments = NewsHost + "/apps/pagina_pagamentos.php"
NewsAppsNumber = 0
NewsAppsRequest = []
NewsPaymentsAmount = '0.00'
NewsPaymentsNumber = 0
NewsPaymentsRequest = []



#================#

#--create panel _TRACKING_ -> movie clip editor (tools)
class AFAC_MO_TRACK_PT_TRACKING(bpy.types.Panel):
    bl_label = "Tracking Markers"
    #bl_idname = "afacemotrack0p1.paneltracking"
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "A_ Face MoTrack"

    def draw(self, context):
        global NoteLabel
        
        layout = self.layout
        
        row = layout.row(align=True)
        sub = row.row(align=True)
        sub.operator("afacemotrack0p1.resizeup", icon="ZOOMIN")
        sub.operator("afacemotrack0p1.createreset")
        sub.operator("afacemotrack0p1.resizedown", icon="ZOOMOUT")
        
        #based in panel TRACK
        row = layout.row(align=True)
        row.label(text="Track:")
        row.operator("afacemotrack0p1.trackprev", icon='FRAME_PREV')
        row.operator("afacemotrack0p1.trackreverse", icon='PLAY_REVERSE')
        row.operator("afacemotrack0p1.trackplay", icon='PLAY')
        row.operator("afacemotrack0p1.tracknext", icon='FRAME_NEXT')
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Clear:")
        row.scale_x = 2.0
        props = row.operator("clip.clear_track_path", text="", icon='BACK')
        props.action = 'UPTO'
        props = row.operator("clip.clear_track_path", text="", icon='FORWARD')
        props.action = 'REMAINED'


#--button _CREATE/RESET TRACKS_
class AFaceMoTrack0p1_CreateReset(bpy.types.Operator):
    bl_label = "Create/Reset Markers"
    bl_idname = "afacemotrack0p1.createreset"
    
    def execute(self, context):
        global MarkersScale
        
        MarkersScale = 1.0
        AFaceMoTrack0p1_def_CreateReset()
        return {'FINISHED'}


#--button _RESIZE UP_
class AFaceMoTrack0p1_ResizeUp(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.resizeup"
    bl_icon = "ZOOMIN"
    
    def execute(self, context):
        global MarkersScale
        
        MarkersScale = MarkersScale * 1.1
        AFaceMoTrack0p1_def_CreateReset()
        return {'FINISHED'}


#--button _RESIZE DOWN_
class AFaceMoTrack0p1_ResizeDown(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.resizedown"
    bl_icon = "ZOOMOUT"
    
    def execute(self, context):
        global MarkersScale
        
        MarkersScale = MarkersScale / 1.1
        AFaceMoTrack0p1_def_CreateReset()
        return {'FINISHED'}


def AFaceMoTrack0p1_def_CreateReset():
    #--capture current video name
    nameCurrentClip = bpy.context.space_data.clip.name
    
    #--delete all tracks
    bpy.ops.clip.select_all(action='SELECT')
    bpy.ops.clip.delete_track()
    
    #--add news tracks with correct positions and names
    x = (0.47 - 0.5) * MarkersScale + 0.5
    y = (0.415 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Nose R"
    
    x = (0.53 - 0.5) * MarkersScale + 0.5
    y = (0.415 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Nose L"
    
        
    x = (0.46 - 0.5) * MarkersScale + 0.5
    y = (0.495 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Lid B R"
    
    x = (0.46 - 0.5) * MarkersScale + 0.5
    y = (0.54 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Lid T R"
    
    x = (0.42 - 0.5) * MarkersScale + 0.5
    y = (0.505 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Lid R"
    
    x = (0.54 - 0.5) * MarkersScale + 0.5
    y = (0.495 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Lid B L"
    
    x = (0.54 - 0.5) * MarkersScale + 0.5
    y = (0.54 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Lid T L"
    
    x = (0.58 - 0.5) * MarkersScale + 0.5
    y = (0.505 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Lid L"
    
    
    x = 0.5
    y = (0.585 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Brow"
    
    x = (0.44 - 0.5) * MarkersScale + 0.5
    y = (0.585 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Brow R"
    
    x = (0.56 - 0.5) * MarkersScale + 0.5
    y = (0.585 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Brow L"
    
    
    x = 0.5
    y = (0.7 - 0.5) * MarkersScale + 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Forehead"
    
    
    x = 0.5
    y = 0.5
    bpy.ops.clip.add_marker(location=(x,y))
    bpy.data.movieclips[nameCurrentClip].tracking.tracks.active.name = "A_ Nose"
    
    #--select all tracks
    bpy.ops.clip.select_all(action='SELECT')
    
    #--resize scale of all tracks
    bpy.ops.transform.resize(value=(MarkersScale,MarkersScale,MarkersScale))


#--button _TRACK PREV_
class AFaceMoTrack0p1_TrackPrev(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.trackprev"
    
    def execute(self, context):
        AFaceMoTrack0p1_def_Tracking(True)
        return {'FINISHED'}


#--button _TRACK REVERSE_
class AFaceMoTrack0p1_TrackReverse(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.trackreverse"
    
    _timer = None
    stop : bpy.props.BoolProperty(default=False)

    def modal(self, context, event):
        if event.type == 'ESC' or self.stop == True:
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}
        
        if event.type == 'TIMER':
            self.stop = AFaceMoTrack0p1_def_Tracking(True)
        
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(time_step=0.12, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


#--button _TRACK PLAY_
class AFaceMoTrack0p1_TrackPlay(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.trackplay"
    
    _timer = None
    stop : bpy.props.BoolProperty(default=False)

    def modal(self, context, event):
        if event.type == 'ESC' or self.stop == True:
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}
        
        if event.type == 'TIMER':
            self.stop = AFaceMoTrack0p1_def_Tracking(False)
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(time_step=0.12, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


#--button _TRACK NEXT_
class AFaceMoTrack0p1_TrackNext(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.tracknext"
    
    def execute(self, context):
        AFaceMoTrack0p1_def_Tracking(False)
        return {'FINISHED'}
        

def AFaceMoTrack0p1_def_Tracking(backWards):
    global AllMarkers
    
    nameCurrentClip = bpy.context.space_data.clip.name
    currentClip = bpy.data.movieclips[nameCurrentClip]
    
    bpy.ops.clip.select_all(action='SELECT')
    bpy.ops.clip.track_markers(backwards=backWards, sequence=False)
    
    #--check if each marker has coordinates
    currentFrame = bpy.context.scene.frame_current
    print(currentFrame)
    stop = False
    x = 0
    while (x < len(AllMarkersNames)):
        if (not currentClip.tracking.tracks[AllMarkersNames[x]].markers.find_frame(currentFrame)):
            currentClip.tracking.tracks[AllMarkersNames[x]].select = False
            print(AllMarkersNames[x])
            stop = True
        x += 1
    
    #--stop tracking if any marker has no coordinate
    if (stop == True):
        bpy.ops.clip.delete_marker()
        bpy.ops.clip.select_all(action='INVERT')
        if (backWards == False):
            bpy.context.scene.frame_current = currentFrame - 1
        else:
            bpy.context.scene.frame_current = currentFrame + 1
    
    return stop




#----#
#--create panel _DATABASE_ -> movie clip editor (tools)
class AFACE_MO_TRACK_PT_DATA_ACTION(bpy.types.Panel):
    bl_label = "Database / Action"
    #bl_idname = "afacemotrack0p1.paneldataaction"
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "A_ Face MoTrack"
    
    bpy.types.Scene.MenuItems = bpy.props.EnumProperty(items = (('0','Database',''),('1','Action','')))
    bpy.types.Scene.DatabaseStart = bpy.props.IntProperty(default = 1)
    bpy.types.Scene.DatabaseEnd = bpy.props.IntProperty(default = 900)
    bpy.types.Scene.ActionStart = bpy.props.IntProperty(default = 1)
    bpy.types.Scene.ActionEnd = bpy.props.IntProperty(default = 900)
    
    def draw(self, context):
        global NoteLabel
        global ClipStart
        global MenuItems
        global DatabaseStart
        global DatabaseEnd
        global DatabaseMsg
        global DatabaseClipName
        global ObjectSelected
        global ActionStart
        global ActionEnd
        global ActionMsg
        global DataActionMeter
        
        if (bpy.context.active_object != None):
	        ObjectSelected = bpy.context.active_object.name
        else:
            ObjectSelected = ''
        
        MenuItems = bpy.context.scene.MenuItems
        DatabaseStart = bpy.context.scene.DatabaseStart
        DatabaseEnd = bpy.context.scene.DatabaseEnd
        ActionStart = bpy.context.scene.ActionStart
        ActionEnd = bpy.context.scene.ActionEnd
        
        layout = self.layout
        
        nameCurrentClip = bpy.context.space_data.clip.name
        ClipStart = bpy.data.movieclips[nameCurrentClip].frame_start
        
        #--check that all tracks are present in the clip to enable the buttons
        stop = False
        x = 0
        while (x < len(AllMarkersNames)):
            if bpy.data.movieclips[nameCurrentClip].tracking.tracks.get(AllMarkersNames[x]) is None:
                print(AllMarkersNames[x])
                stop = True
            x += 1
        
        
        if stop == True:
            layout.label(text="Please, create all markers!")
        else:
            layout.prop(context.scene, 'MenuItems', expand=True)
            
            
            #Clear DatabaseMsg and ActionMsg
            if (DataActionMeter > 9):
                DatabaseMsg = ''
                ActionMsg = ''
                DataActionMeter = 0
            elif ((DatabaseMsg != '') or (ActionMsg != '')):
                DataActionMeter += 1
            
            
            if MenuItems == '0': #--database
                row = layout.row(align=True)
                sub = row.row(align=True)
                sub.label(text= "Video Footage Settings:")
                sub.operator("afacemotrack0p1.move", icon="FILE_REFRESH")
                sub.operator("afacemotrack0p1.recover", icon="RECOVER_AUTO")
                sub.operator("afacemotrack0p1.save", icon="FILE_TICK")
                
                row = layout.row()
                row.prop(context.space_data.clip, "frame_start", text="Video Start in Frame")
                row = layout.row()
                row.label(text= "Database Settings:")
                row = layout.row(align=True)
                row.prop(context.scene, "DatabaseStart", text="DaStart")
                row.prop(context.scene, "DatabaseEnd", text="DaEnd")
                
                layout.operator("afacemotrack0p1.generate", text="Generate Database")
                layout.label(text= NoteLabel + DatabaseMsg)
            
            else: #--action
                row = layout.row(align=True)
                sub = row.row(True)
                sub.label(text= "Video Footage Settings:")
                sub.operator("afacemotrack0p1.move", icon="FILE_REFRESH")
                sub.operator("afacemotrack0p1.recover", icon="RECOVER_AUTO")
                sub.operator("afacemotrack0p1.save", icon="FILE_TICK")
                
                row = layout.row()
                row.prop(context.space_data.clip, "frame_start", text="Video Start in Frame")
                row = layout.row()
                row.label(text= "Action Settings:")
                row = layout.row(align=True)
                row.prop(context.scene, "ActionStart", text="AcStart")
                row.prop(context.scene, "ActionEnd", text="AcEnd")
                
                layout.label(text= "Database: " + DatabaseClipName)
                layout.label(text= "Object: " + ObjectSelected)
                
                layout.operator("afacemotrack0p1.generate", text="Generate Action")
                layout.label(text= NoteLabel + ActionMsg)


#--button _DATAACTION (UPDATE) FRAMES_
class AFaceMoTrack0p1_Move(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.move"
    bl_description = "Move Panel Settings"
    
    def execute(self, context):
        global ClipStart
        
        nameCurrentClip = bpy.context.space_data.clip.name
        currentFrame = bpy.context.scene.frame_current
        clipStartChange = currentFrame - ClipStart
        
        bpy.data.movieclips[nameCurrentClip].frame_start = currentFrame
        bpy.context.scene.DatabaseStart = bpy.context.scene.DatabaseStart + clipStartChange
        bpy.context.scene.DatabaseEnd = bpy.context.scene.DatabaseEnd + clipStartChange
        bpy.context.scene.ActionStart = bpy.context.scene.ActionStart + clipStartChange
        bpy.context.scene.ActionEnd = bpy.context.scene.ActionEnd + clipStartChange
        
        print(clipStartChange)
        return {'FINISHED'}


#--button _DATAACTION RECOVER_
class AFaceMoTrack0p1_Recover(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.recover"
    bl_description = "Recover Panel Settings"
    
    def execute(self, context):
        nameCurrentClip = bpy.context.space_data.clip.name
        
        if ' A_->' in nameCurrentClip:
            dataCurrentClip = nameCurrentClip.split(' A_->')[1]
            dataCurrentClipSplit = dataCurrentClip.split(',')
            
            if (dataCurrentClipSplit[0].isdigit()) and (dataCurrentClipSplit[1].isdigit()) and (dataCurrentClipSplit[2].isdigit()) and (dataCurrentClipSplit[3].isdigit()) and (dataCurrentClipSplit[4].isdigit()):
                bpy.data.movieclips[nameCurrentClip].frame_start = int(dataCurrentClipSplit[0])
                bpy.context.scene.DatabaseStart = int(dataCurrentClipSplit[1])
                bpy.context.scene.DatabaseEnd = int(dataCurrentClipSplit[2])
                bpy.context.scene.ActionStart = int(dataCurrentClipSplit[3])
                bpy.context.scene.ActionEnd = int(dataCurrentClipSplit[4])
        return {'FINISHED'}


#--button _DATAACTION SAVE_
class AFaceMoTrack0p1_Save(bpy.types.Operator):
    bl_label = ""
    bl_idname = "afacemotrack0p1.save"
    bl_description = "Save Panel Settings"
    
    def execute(self, context):
        global ClipStart
        
        nameCurrentClip = bpy.context.space_data.clip.name
        onlyNameCurrentClip = nameCurrentClip.split(' A_->')[0]
        onlyNameLength = len(onlyNameCurrentClip)
        
        dataSave = " A_->" + str(ClipStart) + "," + str(bpy.context.scene.DatabaseStart) + "," + str(bpy.context.scene.DatabaseEnd) + "," + str(bpy.context.scene.ActionStart) + "," + str(bpy.context.scene.ActionEnd)
        maxLength = 60 - len(dataSave)
        
        if (len(onlyNameCurrentClip) > maxLength):
            renameCurrentClip = onlyNameCurrentClip[0:int((maxLength / 2) - 1)] + '..' + onlyNameCurrentClip[int(onlyNameLength) - int((maxLength / 2) + 1):int(onlyNameLength)] + dataSave
        else:
            renameCurrentClip = onlyNameCurrentClip + dataSave
        
        bpy.data.movieclips[nameCurrentClip].name = renameCurrentClip
        return {'FINISHED'}


#--button _DATAACTION GENERATE_
class AFaceMoTrack0p1_Generate(bpy.types.Operator):
    bl_label = "Generate"
    bl_idname = "afacemotrack0p1.generate"
    
    def execute(self, context):
        global ClipStart
        global MenuItems
        
        global DatabaseStart
        global DatabaseEnd
        global DatabaseMsg
        global DatabaseProcessed
        
        global DatabaseClipName
        global ObjectSelected
        
        global ActionStart
        global ActionEnd
        global ActionMsg
        
        #--assembly, format and procces data
        if (MenuItems == '0') or (MenuItems == '1' and DatabaseClipName != '' and ObjectSelected !=''):
            nameCurrentClip = bpy.context.space_data.clip.name
            currentClip = bpy.data.movieclips[nameCurrentClip]
            
            if (MenuItems == '0'): #--_DATABASE_
                DatabaseClipName = nameCurrentClip.split(' A_->')[0]
                DatabaseProcessed = ''
                
                currentFrame = DatabaseStart - ClipStart
                endFrame = DatabaseEnd - ClipStart
                
            else: #--_ACTION_
                currentFrame = ActionStart - ClipStart
                endFrame = ActionEnd - ClipStart
                
                AFaceMoTrack0p1_def_AddKeyFrames()
            
            framesProcessed = 0
            dataAssembly = ''
            
            print('----')
            
            while True:
                currentFrame += 1
                
                if (not currentClip.tracking.tracks['A_ Nose'].markers.find_frame(currentFrame)) or (currentFrame > endFrame + 1):
                    break
                
                positionX = currentClip.tracking.tracks['A_ Nose'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Nose'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('nose ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Lid R'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Lid R'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('lidR ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Lid L'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Lid L'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('lidL ' + str(positionX) + ' ' + str(positionY) + ',')
                
                
                positionX = currentClip.tracking.tracks['A_ Nose R'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Nose R'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('noseR ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Nose L'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Nose L'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('noseL ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Lid B R'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Lid B R'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('lidBR ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Lid T R'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Lid T R'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('lidTR ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Lid B L'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Lid B L'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('lidBL ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Lid T L'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Lid T L'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('lidTL ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Brow'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Brow'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('brow ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Brow R'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Brow R'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('browR ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Brow L'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Brow L'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('browL ' + str(positionX) + ' ' + str(positionY) + ',')
                
                positionX = currentClip.tracking.tracks['A_ Forehead'].markers.find_frame(currentFrame).co.xy[0]
                positionY = currentClip.tracking.tracks['A_ Forehead'].markers.find_frame(currentFrame).co.xy[1]
                positionX = int(positionX * currentClip.size[0])
                positionY = int(positionY * currentClip.size[1])
                dataAssembly = dataAssembly + ('forehead ' + str(positionX) + ' ' + str(positionY))
                
                
                formatted = AFaceMoTrack0p1_def_Format(currentFrame, dataAssembly)
                
                if MenuItems == '0': #-- _DATABASE_
                    DatabaseProcessed = DatabaseProcessed + formatted
                else: #--_ACTION_
                    AFaceMoTrack0p1_def_Action(framesProcessed, currentFrame, formatted)
                
                
                framesProcessed += 1
                dataAssembly = ''
            
            if MenuItems == '0': #-- _DATABASE_
                print(DatabaseProcessed)
                
                if (framesProcessed == 0) or (framesProcessed == 1):
                    DatabaseMsg = str(framesProcessed) + ' frame updated!'
                else:
                    DatabaseMsg = str(framesProcessed) + ' frames updated!'
            else: #--_ACTION_
                if (framesProcessed == 0) or (framesProcessed == 1):
                    ActionMsg = str(framesProcessed) + ' frame updated!'
                else:
                    ActionMsg = str(framesProcessed) + ' frames updated!'
        
        elif (DatabaseClipName == ''):
                ActionMsg = 'Create the DATABASE first!'
        
        elif (ObjectSelected == ''):
                ActionMsg = 'Select an OBJECT to animate!'
        
        return {'FINISHED'}




def AFaceMoTrack0p1_def_AddKeyFrames():
    global ActionStart
    
    #add keyframes in frame: (ActionStart - 1)
    bpy.context.scene.frame_current = int(ActionStart - 1)
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator R"].keyframe_insert(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator C"].keyframe_insert(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator L"].keyframe_insert(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Procerus R"].keyframe_insert(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Procerus L"].keyframe_insert(data_path="value")
    
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Palpebral R"].keyframe_insert(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Palpebral L"].keyframe_insert(data_path="value")
    
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Nasalis Nasal R"].keyframe_insert(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Nasalis Nasal L"].keyframe_insert(data_path="value")




def AFaceMoTrack0p1_def_Format(currentFrame, dataAssembly):
    formatted = ''
    
    splitMarkers = dataAssembly.split(',')
    lenMarkers = len(splitMarkers)
    
    #Search markers 'nose', 'lidL' e 'lidR' and capture their respective X and Y
    x = 0
    while (x < lenMarkers):
        splitNameXY = splitMarkers[x].split(' ')
        
        if (splitNameXY[0] == 'nose'):
            nose_X = float(splitNameXY[1])
            nose_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'lidR'):
            lidR_X = float(splitNameXY[1])
            lidR_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'lidL'):
            lidL_X = float(splitNameXY[1])
            lidL_Y = float(splitNameXY[2])
        
        x += 1
    
    #Calculate one hundred percent and head tilt (convert Tangent -> Radian, Radian -> Degrees)
    cathetusOpposite = lidR_Y - lidL_Y
    cathetusAdjacent = lidL_X - lidR_X
    
    hypotenuse = math.sqrt((cathetusOpposite ** 2) + (cathetusAdjacent ** 2))
    cemPorCento = round(hypotenuse, 1)
    
    tangent = cathetusOpposite / cathetusAdjacent
    inclination = (180 / math.pi) * (math.atan(tangent)) #rad2deg
    
    formatted = formatted + '|FRAME:' + str(currentFrame)
    
    #Repositioning the markers by removing head tilt and calculating positions based on percentage
    zero_X = 0
    zero_Y = 0
    
    x = 0
    while (x < lenMarkers):
        splitNameXY = splitMarkers[x].split(' ')
        
        marker_X = float(splitNameXY[1])
        marker_Y = float(splitNameXY[2])
        
        a = marker_Y
        b = marker_X
        c = math.sqrt((a ** 2) + (b ** 2))
        
        tanA = a / b
        angA = (180 / math.pi) * (math.atan(tanA)) #rad2deg
        
        angA = angA + inclination
        cosA = math.cos((math.pi / 180) * angA) #deg2rad
        
        b = cosA * c
        a = math.sqrt((c ** 2) - (b ** 2))
        
        if ((splitNameXY[0] == 'nose') and (zero_X == 0)):
            zero_X = b
            zero_Y = a
            x = -1
        elif (zero_X != 0):
            marker_X = round((b - zero_X) * 100 / cemPorCento, 1)
            marker_Y = round((a - zero_Y) * 100 / cemPorCento, 1)
            
            formatted = formatted + ',' + str(splitNameXY[0]) + ' ' + str(marker_X) + ' ' + str(marker_Y)
        
        x += 1
    return (formatted)




def AFaceMoTrack0p1_def_Action(framesProcessed, currentFrame, formatted):
    global DatabaseProcessed
    global ActionStart
    global ActionEnd
    
    global frontalCorrugatorR_value, frontalCorrugatorR_lastKey_value, frontalCorrugatorR_lastKey_frame
    global frontalCorrugatorC_value, frontalCorrugatorC_lastKey_value, frontalCorrugatorC_lastKey_frame
    global frontalCorrugatorL_value, frontalCorrugatorL_lastKey_value, frontalCorrugatorL_lastKey_frame
    global frontalProcerusR_value, frontalProcerusR_lastKey_value, frontalProcerusR_lastKey_frame
    global frontalProcerusL_value, frontalProcerusL_lastKey_value, frontalProcerusL_lastKey_frame
    global oculiPalpebralR_value, oculiPalpebralR_lastKey_value, oculiPalpebralR_lastKey_frame
    global oculiPalpebralL_value, oculiPalpebralL_lastKey_value, oculiPalpebralL_lastKey_frame
    global oculiOrbitalR_value, oculiOrbitalR_lastKey_value, oculiOrbitalR_lastKey_frame
    global oculiOrbitalL_value, oculiOrbitalL_lastKey_value, oculiOrbitalL_lastKey_frame
    global nasalisNasalR_value, nasalisNasalR_lastKey_value, nasalisNasalR_lastKey_frame
    global nasalisNasalL_value, nasalisNasalL_lastKey_value, nasalisNasalL_lastKey_frame
    
    if (framesProcessed == 0):
        frontalCorrugatorR_value = 0.5
        frontalCorrugatorR_lastKey_value = 0.5
        frontalCorrugatorR_lastKey_frame = 0
        
        frontalCorrugatorC_value = 0.5
        frontalCorrugatorC_lastKey_value = 0.5
        frontalCorrugatorC_lastKey_frame = 0
        
        frontalCorrugatorL_value = 0.5
        frontalCorrugatorL_lastKey_value = 0.5
        frontalCorrugatorL_lastKey_frame = 0
        
        frontalProcerusR_value = 0.5
        frontalProcerusR_lastKey_value = 0.5
        frontalProcerusR_lastKey_frame = 0
        
        frontalProcerusL_value = 0.5
        frontalProcerusL_lastKey_value = 0.5
        frontalProcerusL_lastKey_frame = 0
        
        oculiPalpebralR_value = 0.5
        oculiPalpebralR_lastKey_value = 0.5
        oculiPalpebralR_lastKey_frame = 0
        
        oculiPalpebralL_value = 0.5
        oculiPalpebralL_lastKey_value = 0.5
        oculiPalpebralL_lastKey_frame = 0
        
        oculiOrbitalR_value = 0.5
        oculiOrbitalR_lastKey_value = 0.5
        oculiOrbitalR_lastKey_frame = 0
        
        oculiOrbitalL_value = 0.5
        oculiOrbitalL_lastKey_value = 0.5
        oculiOrbitalL_lastKey_frame = 0
        
        nasalisNasalR_value = 0.5
        nasalisNasalR_lastKey_value = 0.5
        nasalisNasalR_lastKey_frame = 0
        
        nasalisNasalL_value = 0.5
        nasalisNasalL_lastKey_value = 0.5
        nasalisNasalL_lastKey_frame = 0
    
    splitMarkers = formatted.split(',')
    lenMarkers = len(splitMarkers)
    
    #Capture respective X and Y of all markers
    x = 0
    while (x < lenMarkers):
        splitNameXY = splitMarkers[x].split(' ')
        
        if (splitNameXY[0] == 'nose'):
            nose_X = float(splitNameXY[1])
            nose_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'lidR'):
            lidR_X = float(splitNameXY[1])
            lidR_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'lidL'):
            lidL_X = float(splitNameXY[1])
            lidL_Y = float(splitNameXY[2])
        
        elif (splitNameXY[0] == 'noseR'):
            noseR_X = float(splitNameXY[1])
            noseR_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'noseL'):
            noseL_X = float(splitNameXY[1])
            noseL_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'lidBR'):
            lidBR_X = float(splitNameXY[1])
            lidBR_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'lidTR'):
            lidTR_X = float(splitNameXY[1])
            lidTR_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'lidBL'):
            lidBL_X = float(splitNameXY[1])
            lidBL_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'lidTL'):
            lidTL_X = float(splitNameXY[1])
            lidTL_Y = float(splitNameXY[2])
        
        elif (splitNameXY[0] == 'brow'):
            brow_X = float(splitNameXY[1])
            brow_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'browR'):
            browR_X = float(splitNameXY[1])
            browR_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'browL'):
            browL_X = float(splitNameXY[1])
            browL_Y = float(splitNameXY[2])
        elif (splitNameXY[0] == 'forehead'):
            forehead_X = float(splitNameXY[1])
            forehead_Y = float(splitNameXY[2])
        
        x += 1
    
    #Explode database to find more similar frame reference
    splitDatabaseProcessedFrames = DatabaseProcessed.split('|FRAME:')
    lenDatabaseProcessedFrames = len(splitDatabaseProcessedFrames)
    
    difference_XY = 100
    difference_X = 100
    difference_Y = 100
    dataCaptureMarkers_X = 'n'
    dataCaptureMarkers_Y = 'n'
    
    x = 1
    while (x < lenDatabaseProcessedFrames):
        splitDatabaseProcessedMarkers = splitDatabaseProcessedFrames[x].split(',')
        lenDatabaseProcessedMarkers = len(splitDatabaseProcessedMarkers)
        
        #Search markers 'nose', 'lidL' e 'lidR' and capture their respective X and Y
        y = 1
        while (y < lenDatabaseProcessedMarkers):
            splitDatabaseProcessedMarkersNameXY = splitDatabaseProcessedMarkers[y].split(' ')
            
            if (splitDatabaseProcessedMarkersNameXY[0] == 'nose'):
                difNose_X = float(splitDatabaseProcessedMarkersNameXY[1])
                difNose_Y = float(splitDatabaseProcessedMarkersNameXY[2])
            elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidR'):
                difLidR_X = float(splitDatabaseProcessedMarkersNameXY[1])
                difLidR_Y = float(splitDatabaseProcessedMarkersNameXY[2])
            elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidL'):
                difLidL_X = float(splitDatabaseProcessedMarkersNameXY[1])
                difLidL_Y = float(splitDatabaseProcessedMarkersNameXY[2])
            
            y += 1
        
        #Calculate the difference between Action and the current database frame (round and make a positive number)
        dif_X = abs(round(((lidR_X - difLidR_X) + (lidL_X - difLidL_X)) / 2, 1))
        dif_Y = abs(round(((lidR_Y - difLidR_Y) + (lidL_Y - difLidL_Y)) / 2, 1))
        
        #Analyze X and Y together if tolerance less than 1%
        if ((dif_X < 1) and (dif_Y < 1)):
            dif_XY = (dif_X + dif_Y) / 2
            
            if (dif_XY < difference_XY):
                difference_XY = dif_XY
                dataCaptureMarkers_X = 's'
                dataCaptureMarkers_Y = 's'
        
        #If greater than 1%, analyze X and Y separately
        elif (difference_XY > 1):
            if (dif_X < difference_X):
                difference_X = dif_X
                dataCaptureMarkers_X = 's'
                
            if (dif_Y < difference_Y):
                difference_Y = dif_Y
                dataCaptureMarkers_Y = 's'
        
        #Capture markers when frame is compatible on X axis
        if (dataCaptureMarkers_X == 's'):
            z = 1
            while (z < lenDatabaseProcessedMarkers):
                splitDatabaseProcessedMarkersNameXY = splitDatabaseProcessedMarkers[z].split(' ')
                
                if (splitDatabaseProcessedMarkersNameXY[0] == 'nose'):
                    dataNose_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidR'):
                    dataLidR_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidL'):
                    dataLidL_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'noseR'):
                    dataNoseR_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'noseL'):
                    dataNoseL_X = float(splitDatabaseProcessedMarkersNameXY[1])
                
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidTR'):
                    dataLidTR_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidBR'):
                    dataLidBR_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidTL'):
                    dataLidTL_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidBL'):
                    dataLidBL_X = float(splitDatabaseProcessedMarkersNameXY[1])
                
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'brow'):
                    dataBrow_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'browR'):
                    dataBrowR_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'browL'):
                    dataBrowL_X = float(splitDatabaseProcessedMarkersNameXY[1])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'forehead'):
                    dataForehead_X = float(splitDatabaseProcessedMarkersNameXY[1])
                
                dataCaptureMarkers_X = 'n'
                z += 1
        
        #Capture markers when frame is compatible on Y axis
        if (dataCaptureMarkers_Y == 's'):
            z = 1
            while (z < lenDatabaseProcessedMarkers):
                splitDatabaseProcessedMarkersNameXY = splitDatabaseProcessedMarkers[z].split(' ')
                
                if (splitDatabaseProcessedMarkersNameXY[0] == 'nose'):
                    dataNose_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidR'):
                    dataLidR_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidL'):
                    dataLidL_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'noseR'):
                    dataNoseR_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'noseL'):
                    dataNoseL_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidTR'):
                    dataLidTR_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidBR'):
                    dataLidBR_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidTL'):
                    dataLidTL_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'lidBL'):
                    dataLidBL_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'brow'):
                    dataBrow_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'browR'):
                    dataBrowR_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'browL'):
                    dataBrowL_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                elif (splitDatabaseProcessedMarkersNameXY[0] == 'forehead'):
                    dataForehead_Y = float(splitDatabaseProcessedMarkersNameXY[2])
                
                dataCaptureMarkers_Y = 'n'
                z += 1
        
        x += 1
    
    #Move current frame and delete all key frames
    bpy.context.scene.frame_current = int(currentFrame) + ActionStart
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator R"].keyframe_delete(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator C"].keyframe_delete(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator L"].keyframe_delete(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Procerus R"].keyframe_delete(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Procerus L"].keyframe_delete(data_path="value")
    
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Palpebral R"].keyframe_delete(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Palpebral L"].keyframe_delete(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Orbital R"].keyframe_delete(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Orbital L"].keyframe_delete(data_path="value")
    
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Nasalis Nasal R"].keyframe_delete(data_path="value")
    bpy.context.active_object.data.shape_keys.key_blocks["A_ Nasalis Nasal L"].keyframe_delete(data_path="value")
    
    #--frontalCorrugatorR
    extraBrowR = ((browR_Y - brow_Y) - (dataBrowR_Y - dataBrow_Y)) / 80
    frontalCorrugatorR_value = round(((abs(browR_Y) - abs(dataBrowR_Y)) / 8) + extraBrowR, 2)
    
    if (frontalCorrugatorR_value > 1.0):
        frontalCorrugatorR_value = 1.0
    elif (frontalCorrugatorR_value < 0.0):
        frontalCorrugatorR_value = 0.0
    
    frontalCorrugatorR_variation = abs(frontalCorrugatorR_lastKey_value - frontalCorrugatorR_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (frontalCorrugatorR_variation > 0.03) and (currentFrame - frontalCorrugatorR_lastKey_frame > 30): 
        addKeyFrame = True
    if (frontalCorrugatorR_variation > 0.09) and (currentFrame - frontalCorrugatorR_lastKey_frame > 20): 
        addKeyFrame = True
    if (frontalCorrugatorR_variation > 0.18) and (currentFrame - frontalCorrugatorR_lastKey_frame > 10): 
        addKeyFrame = True
    if (frontalCorrugatorR_variation > 0.24) and (currentFrame - frontalCorrugatorR_lastKey_frame > 5):
        addKeyFrame = True
    if (frontalCorrugatorR_variation > 0.48):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        frontalCorrugatorR_lastKey_frame = currentFrame
        frontalCorrugatorR_lastKey_value = round(frontalCorrugatorR_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator R"].value = frontalCorrugatorR_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator R"].keyframe_insert(data_path="value")
    
    
    #--frontalCorrugatorC
    extraBrowCR = ((brow_Y - browR_Y) - (dataBrow_Y - dataBrowR_Y)) / 160
    extraBrowCL = ((brow_Y - browL_Y) - (dataBrow_Y - dataBrowL_Y)) / 160
    frontalCorrugatorC_value = round(((abs(brow_Y) - abs(dataBrow_Y)) / 8) + extraBrowCR + extraBrowCL, 2)
    
    if (frontalCorrugatorC_value > 1.0):
        frontalCorrugatorC_value = 1.0
    elif (frontalCorrugatorC_value < -1.0):
        frontalCorrugatorC_value = -1.0
    
    frontalCorrugatorC_variation = abs(frontalCorrugatorC_lastKey_value - frontalCorrugatorC_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (frontalCorrugatorC_variation > 0.03) and (currentFrame - frontalCorrugatorC_lastKey_frame > 30): 
        addKeyFrame = True
    if (frontalCorrugatorC_variation > 0.09) and (currentFrame - frontalCorrugatorC_lastKey_frame > 20): 
        addKeyFrame = True
    if (frontalCorrugatorC_variation > 0.18) and (currentFrame - frontalCorrugatorC_lastKey_frame > 10): 
        addKeyFrame = True
    if (frontalCorrugatorC_variation > 0.24) and (currentFrame - frontalCorrugatorC_lastKey_frame > 5):
        addKeyFrame = True
    if (frontalCorrugatorC_variation > 0.48):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        frontalCorrugatorC_lastKey_frame = currentFrame
        frontalCorrugatorC_lastKey_value = round(frontalCorrugatorC_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator C"].value = frontalCorrugatorC_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator C"].keyframe_insert(data_path="value")
    
    
    #--frontalCorrugatorL
    extraBrowL = ((browL_Y - brow_Y) - (dataBrowL_Y - dataBrow_Y)) / 80
    frontalCorrugatorL_value = round(((abs(browL_Y) - abs(dataBrowL_Y)) / 8) + extraBrowL, 2)
    
    if (frontalCorrugatorL_value > 1.0):
        frontalCorrugatorL_value = 1.0
    elif (frontalCorrugatorL_value < 0.0):
        frontalCorrugatorL_value = 0.0
    
    frontalCorrugatorL_variation = abs(frontalCorrugatorL_lastKey_value - frontalCorrugatorL_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (frontalCorrugatorL_variation > 0.03) and (currentFrame - frontalCorrugatorL_lastKey_frame > 30): 
        addKeyFrame = True
    if (frontalCorrugatorL_variation > 0.09) and (currentFrame - frontalCorrugatorL_lastKey_frame > 20): 
        addKeyFrame = True
    if (frontalCorrugatorL_variation > 0.18) and (currentFrame - frontalCorrugatorL_lastKey_frame > 10): 
        addKeyFrame = True
    if (frontalCorrugatorL_variation > 0.24) and (currentFrame - frontalCorrugatorL_lastKey_frame > 5):
        addKeyFrame = True
    if (frontalCorrugatorL_variation > 0.48):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        frontalCorrugatorL_lastKey_frame = currentFrame
        frontalCorrugatorL_lastKey_value = round(frontalCorrugatorL_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator L"].value = frontalCorrugatorL_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Corrugator L"].keyframe_insert(data_path="value")
    
    
    #--frontalProcerusR
    frontalProcerusR_value = round(((abs(dataBrowR_X) - abs(browR_X)) / 4), 2)
    
    if (frontalProcerusR_value > 1.0):
        frontalProcerusR_value = 1.0
    elif (frontalProcerusR_value < 0.0):
        frontalProcerusR_value = 0.0
    
    frontalProcerusR_variation = abs(frontalProcerusR_lastKey_value - frontalProcerusR_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (frontalProcerusR_variation > 0.12) and (currentFrame - frontalProcerusR_lastKey_frame > 36): 
        addKeyFrame = True
    if (frontalProcerusR_variation > 0.24) and (currentFrame - frontalProcerusR_lastKey_frame > 24): 
        addKeyFrame = True
    if (frontalProcerusR_variation > 0.36) and (currentFrame - frontalProcerusR_lastKey_frame > 12): 
        addKeyFrame = True
    if (frontalProcerusR_variation > 0.48) and (currentFrame - frontalProcerusR_lastKey_frame > 6):
        addKeyFrame = True
    if (frontalProcerusR_variation > 0.60):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        frontalProcerusR_lastKey_frame = currentFrame
        frontalProcerusR_lastKey_value = round(frontalProcerusR_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Procerus R"].value = frontalProcerusR_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Procerus R"].keyframe_insert(data_path="value")
    
    
    #--frontalProcerusL
    frontalProcerusL_value = round(((abs(dataBrowL_X) - abs(browL_X)) / 4), 2)
    
    if (frontalProcerusL_value > 1.0):
        frontalProcerusL_value = 1.0
    elif (frontalProcerusL_value < 0.0):
        frontalProcerusL_value = 0.0
    
    frontalProcerusL_variation = abs(frontalProcerusL_lastKey_value - frontalProcerusL_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (frontalProcerusL_variation > 0.12) and (currentFrame - frontalProcerusL_lastKey_frame > 36): 
        addKeyFrame = True
    if (frontalProcerusL_variation > 0.24) and (currentFrame - frontalProcerusL_lastKey_frame > 24): 
        addKeyFrame = True
    if (frontalProcerusL_variation > 0.36) and (currentFrame - frontalProcerusL_lastKey_frame > 12): 
        addKeyFrame = True
    if (frontalProcerusL_variation > 0.48) and (currentFrame - frontalProcerusL_lastKey_frame > 6):
        addKeyFrame = True
    if (frontalProcerusL_variation > 0.60):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        frontalProcerusL_lastKey_frame = currentFrame
        frontalProcerusL_lastKey_value = round(frontalProcerusL_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Procerus L"].value = frontalProcerusL_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Frontal Procerus L"].keyframe_insert(data_path="value")
    
    
    #--oculiPalpebralR
    oculiPalpebralR_value = round(((abs(dataLidBR_Y - dataLidTR_Y) - abs(lidBR_Y - lidTR_Y)) / 9), 2)
    
    if (oculiPalpebralR_value > 0.75):
        oculiPalpebralR_value = 1.0
    elif (oculiPalpebralR_value > 0.5):
        oculiPalpebralR_value = 0.5
    elif (oculiPalpebralR_value > 0.25):
        oculiPalpebralR_value = 0.25
    elif (oculiPalpebralR_value > 0.0):
        oculiPalpebralR_value = 0.0
    elif (oculiPalpebralR_value < 0.0):
        oculiPalpebralR_value = -0.25
    
    oculiPalpebralR_variation = abs(oculiPalpebralR_lastKey_value - oculiPalpebralR_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (oculiPalpebralR_variation > 0.24) and (currentFrame - oculiPalpebralR_lastKey_frame > 6): 
        addKeyFrame = True
    if (oculiPalpebralR_variation > 0.48):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        oculiPalpebralR_lastKey_frame = currentFrame
        oculiPalpebralR_lastKey_value = round(oculiPalpebralR_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Palpebral R"].value = oculiPalpebralR_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Palpebral R"].keyframe_insert(data_path="value")
    
    
    #--oculiPalpebralL
    oculiPalpebralL_value = round(((abs(dataLidBL_Y - dataLidTL_Y) - abs(lidBL_Y - lidTL_Y)) / 9), 2)
    
    if (oculiPalpebralL_value > 0.75):
        oculiPalpebralL_value = 1.0
    elif (oculiPalpebralL_value > 0.5):
        oculiPalpebralL_value = 0.5
    elif (oculiPalpebralL_value > 0.25):
        oculiPalpebralL_value = 0.25
    elif (oculiPalpebralL_value > 0.0):
        oculiPalpebralL_value = 0.0
    elif (oculiPalpebralL_value < 0.0):
        oculiPalpebralL_value = -0.25
    
    oculiPalpebralL_variation = abs(oculiPalpebralL_lastKey_value - oculiPalpebralL_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (oculiPalpebralL_variation > 0.24) and (currentFrame - oculiPalpebralL_lastKey_frame > 6): 
        addKeyFrame = True
    if (oculiPalpebralL_variation > 0.48):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        oculiPalpebralL_lastKey_frame = currentFrame
        oculiPalpebralL_lastKey_value = round(oculiPalpebralL_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Palpebral L"].value = oculiPalpebralL_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Palpebral L"].keyframe_insert(data_path="value")
    
    
    #--oculiOrbitalR
    extraBrowR = ((brow_Y - browR_Y) - (dataBrow_Y - dataBrowR_Y)) / 80
    oculiOrbitalR_value = round(((abs(dataBrowR_Y) - abs(browR_Y)) / 8) + extraBrowR, 2)
    
    if (oculiOrbitalR_value > 1.0):
        oculiOrbitalR_value = 1.0
    elif (oculiOrbitalR_value < 0.0):
        oculiOrbitalR_value = 0.0
    
    oculiOrbitalR_variation = abs(oculiOrbitalR_lastKey_value - oculiOrbitalR_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (oculiOrbitalR_variation > 0.03) and (currentFrame - oculiOrbitalR_lastKey_frame > 30): 
        addKeyFrame = True
    if (oculiOrbitalR_variation > 0.09) and (currentFrame - oculiOrbitalR_lastKey_frame > 20): 
        addKeyFrame = True
    if (oculiOrbitalR_variation > 0.18) and (currentFrame - oculiOrbitalR_lastKey_frame > 10): 
        addKeyFrame = True
    if (oculiOrbitalR_variation > 0.24) and (currentFrame - oculiOrbitalR_lastKey_frame > 5):
        addKeyFrame = True
    if (oculiOrbitalR_variation > 0.48):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        oculiOrbitalR_lastKey_frame = currentFrame
        oculiOrbitalR_lastKey_value = round(oculiOrbitalR_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Orbital R"].value = oculiOrbitalR_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Orbital R"].keyframe_insert(data_path="value")
    
    
    #--oculiOrbitalL
    extraBrowL = ((brow_Y - browL_Y) - (dataBrow_Y - dataBrowL_Y)) / 80
    oculiOrbitalL_value = round(((abs(dataBrowL_Y) - abs(browL_Y)) / 8) + extraBrowL, 2)
    
    if (oculiOrbitalL_value > 1.0):
        oculiOrbitalL_value = 1.0
    elif (oculiOrbitalL_value < 0.0):
        oculiOrbitalL_value = 0.0
    
    oculiOrbitalL_variation = abs(oculiOrbitalL_lastKey_value - oculiOrbitalL_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (oculiOrbitalL_variation > 0.03) and (currentFrame - oculiOrbitalL_lastKey_frame > 30): 
        addKeyFrame = True
    if (oculiOrbitalL_variation > 0.09) and (currentFrame - oculiOrbitalL_lastKey_frame > 20): 
        addKeyFrame = True
    if (oculiOrbitalL_variation > 0.18) and (currentFrame - oculiOrbitalL_lastKey_frame > 10): 
        addKeyFrame = True
    if (oculiOrbitalL_variation > 0.24) and (currentFrame - oculiOrbitalL_lastKey_frame > 5):
        addKeyFrame = True
    if (oculiOrbitalL_variation > 0.48):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        oculiOrbitalL_lastKey_frame = currentFrame
        oculiOrbitalL_lastKey_value = round(oculiOrbitalL_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Orbital L"].value = oculiOrbitalL_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Oculi Orbital L"].keyframe_insert(data_path="value")
    
    
    #--nasalisNasalR
    nasalisNasalR_value = round(((abs(dataNoseR_Y) - abs(noseR_Y)) / 10), 2)
    
    if (nasalisNasalR_value > 1.0):
        nasalisNasalR_value = 1.0
    elif (nasalisNasalR_value < 0.0):
        nasalisNasalR_value = 0.0
    
    nasalisNasalR_variation = abs(nasalisNasalR_lastKey_value - nasalisNasalR_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (nasalisNasalR_variation > 0.12) and (currentFrame - nasalisNasalR_lastKey_frame > 36): 
        addKeyFrame = True
    if (nasalisNasalR_variation > 0.24) and (currentFrame - nasalisNasalR_lastKey_frame > 24): 
        addKeyFrame = True
    if (nasalisNasalR_variation > 0.36) and (currentFrame - nasalisNasalR_lastKey_frame > 12): 
        addKeyFrame = True
    if (nasalisNasalR_variation > 0.48) and (currentFrame - nasalisNasalR_lastKey_frame > 6):
        addKeyFrame = True
    if (nasalisNasalR_variation > 0.60):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        nasalisNasalR_lastKey_frame = currentFrame
        nasalisNasalR_lastKey_value = round(nasalisNasalR_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Nasalis Nasal R"].value = nasalisNasalR_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Nasalis Nasal R"].keyframe_insert(data_path="value")
    
    
    #--nasalisNasalL
    nasalisNasalL_value = round(((abs(dataNoseL_Y) - abs(noseL_Y)) / 10), 2)
    
    if (nasalisNasalL_value > 1.0):
        nasalisNasalL_value = 1.0
    elif (nasalisNasalL_value < 0.0):
        nasalisNasalL_value = 0.0
    
    nasalisNasalL_variation = abs(nasalisNasalL_lastKey_value - nasalisNasalL_value)
    
    addKeyFrame = False
    if (currentFrame == ActionEnd):
        addKeyFrame = True
    if (nasalisNasalL_variation > 0.12) and (currentFrame - nasalisNasalL_lastKey_frame > 36): 
        addKeyFrame = True
    if (nasalisNasalL_variation > 0.24) and (currentFrame - nasalisNasalL_lastKey_frame > 24): 
        addKeyFrame = True
    if (nasalisNasalL_variation > 0.36) and (currentFrame - nasalisNasalL_lastKey_frame > 12): 
        addKeyFrame = True
    if (nasalisNasalL_variation > 0.48) and (currentFrame - nasalisNasalL_lastKey_frame > 6):
        addKeyFrame = True
    if (nasalisNasalL_variation > 0.60):
        addKeyFrame = True
    
    if (addKeyFrame == True):
        nasalisNasalL_lastKey_frame = currentFrame
        nasalisNasalL_lastKey_value = round(nasalisNasalL_value, 2)
        #insert keyframe
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Nasalis Nasal L"].value = nasalisNasalL_lastKey_value
        bpy.context.active_object.data.shape_keys.key_blocks["A_ Nasalis Nasal L"].keyframe_insert(data_path="value")




#================# #--AMULEKNEWS--#

#--create panel _AMULEKNEWS PANEL_
class AMulekNews0p1_Panel(bpy.types.Panel):
    bl_label = "A_ Mulek News 0.1"
    #bl_idname = "amuleknews0p1.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "A_ Mulek News"

    
    def draw(self, context):
        global NewsAppsNumber
        global NewsAppsRequest
        global NewsPaymentsAmount
        global NewsPaymentsNumber
        global NewsPaymentsRequest
        
        layout = self.layout
        row = layout.row(align=True)
        
        row.label(text='APPS')
        row = layout.row(align=True)
        
        row.label(text='- Latest versions:')
        row = layout.row(align=True)
        
        row.operator("amuleknews0p1.home", text='alexandremulek.com', icon='WORLD')
        row.operator("amuleknews0p1.update", icon='FILE_REFRESH')
        row = layout.row(align=True)
        
        row = layout.row(align=True)
        
        if (NewsAppsNumber > 0):
            i = 0
            while (i < NewsAppsNumber):
                row.label(text=NewsAppsRequest[i], icon='LAMP')
                row = layout.row(align=True)
                i += 1
        else:
            row.label(text='Warning: Offline')
        
		
        row = layout.separator()
        row = layout.row(align=True)
        row = layout.separator()
        row = layout.row(align=True)
		
        
        row.label(text='PAYMENTS')
        row = layout.row(align=True)
        
        row.label(text='- Total amount received this month:')
        row = layout.row(align=True)
        
        row.operator("amuleknews0p1.pay", text=NewsPaymentsAmount, icon='INFO')
        row.operator("amuleknews0p1.update", icon='FILE_REFRESH')
        row = layout.row(align=True)
        
        row = layout.row(align=True)
        
        if (NewsPaymentsNumber > 0):
            i = 0
            while (i < NewsPaymentsNumber):
                row.label(text=NewsPaymentsRequest[i + 1], icon='SOLO_ON')
                row = layout.row(align=True)
                i += 1
        else:
            row.label(text='Warning: Offline')
            row = layout.row(align=True)


#--button _AMULEKNEWS UPDATE_
class AMulekNews0p1_Update(bpy.types.Operator):
    bl_label = ""
    bl_idname = "amuleknews0p1.update"
    bl_description = 'Update Payment Data'
    
    def execute(self, context):
        AMulekNews0p1_def_Update()
        return {'FINISHED'}


def AMulekNews0p1_def_Update():
    global NewsUrlRequest
    global NewsAppsNumber
    global NewsAppsRequest
    global NewsPaymentsAmount
    global NewsPaymentsNumber
    global NewsPaymentsRequest
    """
    print('----')
    dataSend = {'resultado':'1'}
    r = requests.post(NewsUrlRequest, data = dataSend)
    print(r.text)
    
    splitText = r.text.split('|')
    if (splitText[0] == 'OK'):
        NewsAppsRequest = splitText[1].split('< >')
        NewsAppsNumber = len(NewsAppsRequest)
        
        NewsPaymentsRequest = splitText[2].split('< >')
        NewsPaymentsAmount = NewsPaymentsRequest[0]
        NewsPaymentsNumber = len(NewsPaymentsRequest) - 1
        """

#--button _AMULEKNEWS HOME_
class AMulekNews0p1_Home(bpy.types.Operator):
    bl_label = ""
    bl_idname = "amuleknews0p1.home"
    bl_description = 'Go To Website'
    
    def execute(self, context):
        global NewsUrlHome
        
        webbrowser.open(NewsUrlHome, 0, True)
        return {'FINISHED'}


#--button _AMULEKNEWS PAY_
class AMulekNews0p1_Pay(bpy.types.Operator):
    bl_label = ""
    bl_idname = "amuleknews0p1.pay"
    bl_description = 'View All Payments'
    
    def execute(self, context):
        global NewsUrlPayments
        
        webbrowser.open(NewsUrlPayments, 0, True)
        return {'FINISHED'}




#================#

def register():    
    bpy.utils.register_class(AFAC_MO_TRACK_PT_TRACKING)
    bpy.utils.register_class(AFaceMoTrack0p1_CreateReset)
    bpy.utils.register_class(AFaceMoTrack0p1_ResizeUp)
    bpy.utils.register_class(AFaceMoTrack0p1_ResizeDown)
    bpy.utils.register_class(AFaceMoTrack0p1_TrackPrev)
    bpy.utils.register_class(AFaceMoTrack0p1_TrackReverse)
    bpy.utils.register_class(AFaceMoTrack0p1_TrackPlay)
    bpy.utils.register_class(AFaceMoTrack0p1_TrackNext)
    
    bpy.utils.register_class(AFACE_MO_TRACK_PT_DATA_ACTION)
    bpy.utils.register_class(AFaceMoTrack0p1_Move)
    bpy.utils.register_class(AFaceMoTrack0p1_Recover)
    bpy.utils.register_class(AFaceMoTrack0p1_Save)
    bpy.utils.register_class(AFaceMoTrack0p1_Generate)
    
    #--AMULEKNEWS--#
    try:
        bpy.utils.register_class(AMulekNews0p1_Panel)
        bpy.utils.register_class(AMulekNews0p1_Update)
        bpy.utils.register_class(AMulekNews0p1_Home)
        bpy.utils.register_class(AMulekNews0p1_Pay)
    except:
        pass


def unregister():
    bpy.utils.unregister_class(AFAC_MO_TRACK_PT_TRACKING)
    bpy.utils.unregister_class(AFaceMoTrack0p1_CreateReset)
    bpy.utils.unregister_class(AFaceMoTrack0p1_ResizeUp)
    bpy.utils.unregister_class(AFaceMoTrack0p1_ResizeDown)
    bpy.utils.unregister_class(AFaceMoTrack0p1_TrackPrev)
    bpy.utils.unregister_class(AFaceMoTrack0p1_TrackReverse)
    bpy.utils.unregister_class(AFaceMoTrack0p1_TrackPlay)
    bpy.utils.unregister_class(AFaceMoTrack0p1_TrackNext)
    
    bpy.utils.unregister_class(AFACE_MO_TRACK_PT_DATA_ACTION)
    bpy.utils.unregister_class(AFaceMoTrack0p1_Move)
    bpy.utils.unregister_class(AFaceMoTrack0p1_Recover)
    bpy.utils.unregister_class(AFaceMoTrack0p1_Save)
    bpy.utils.unregister_class(AFaceMoTrack0p1_Generate)


if __name__ == "__main__":
    register()


#--AMULEKNEWS--#
AMulekNews0p1_def_Update()
