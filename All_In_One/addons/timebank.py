#
# Copyright 2018 rn9dfj3
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import bpy
from pathlib import Path
from datetime import datetime, timedelta
bl_info = {
    "name": "Timebank",
    "author": "rn9dfj3",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Info > File",
    "description": "Save blender file named each process.",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/rn9dfj3/timebank/wiki",
    "tracker_url": "https://github.com/rn9dfj3/timebank/issues",
    "category": "Learnbgame",
}
OPTION_SAVED = {'REGISTER'}
PROCESSES = ("modeling", "skinning", "texturing",
             "morphing", "animating", "rendering", "compositing", "scripting")
MODELING = 0
SKINNING = 1
TEXTURING = 2
MORPHING = 3
ANIMATING = 4
RENDERING = 5
COMPOSITING = 6
SCRIPTING = 7
ALL = 8
MODELING_ICON = 'EDIT'
SKINNING_ICON = 'WPAINT_HLT'
TEXTURING_ICON = 'TEXTURE'
MORPHING_ICON = 'SHAPEKEY_DATA'
ANIMATING_ICON = 'ACTION'
RENDERING_ICON = 'RENDER_STILL'
COMPOSITING_ICON = 'NODETREE'
SCRIPTING_ICON = 'TEXT'
PROCESS = 0
RATIO = 1

def save(self, context, type):
        pref = context.user_preferences.addons[__name__].preferences
        filepath = context.blend_data.filepath
        if filepath == "":
            bpy.ops.wm.save_as_mainfile('INVOKE_AREA')
            #start save auto
            if pref.saveauto and not pref.saveauto_run:
                bpy.ops.wm.timebank_save_auto('INVOKE_DEFAULT')            
            return
        path = Path(filepath)
        suffix = path.suffix
        stem = path.stem
        # num
        first = stem.rfind("_")
        base = stem
        if first == -1:  # only base
            pass
        else:
            num = stem[first+1:]
            if num.isdigit():  # hit bank
                base = stem[:first]
                # process
                first = base.rfind("_")
                if first == -1:  # not bank
                    pass
                else:
                    process = base[first+1:]
                    if process in PROCESSES:
                        base = base[:first]
        parent = path.resolve()
        files = parent.parent.glob(base+'*'+suffix)
        m = 0
        for file in files:
            file_stem = file.stem
            second = file_stem.rfind("_")
            num = file_stem[second+1:]
            if num.isdigit():
                m = max(int(num), m)
            else:
                m = max(0, m)
        num = str(m+1)
        path = path.with_name(base+"_"+PROCESSES[type]+"_"+num)
        path = path.with_suffix(suffix)
        filepath = str(path)
        self.report({'INFO'}, "Saved "+str(path))
        bpy.ops.wm.save_as_mainfile(filepath=filepath, check_existing=True)
        #start save auto
        if pref.saveauto and not pref.saveauto_run:
            bpy.ops.wm.timebank_save_auto('INVOKE_DEFAULT')

class SaveModeling(bpy.types.Operator):
    bl_idname = "wm.timebank_modeling"
    bl_label = "Save Modeling"
    bl_description = "Save the current file as modeling process."
    bl_options = OPTION_SAVED

    def execute(self, context):
        save(self, context, MODELING)
        return {'FINISHED'}


class SaveSkinning(bpy.types.Operator):
    bl_idname = "wm.timebank_skinning"
    bl_label = "Save Skinning"
    bl_description = "Save the current file as skinning process."
    bl_options = OPTION_SAVED

    def execute(self, context):
        save(self, context, SKINNING)
        return {'FINISHED'}


class SaveTexturing(bpy.types.Operator):
    bl_idname = "wm.timebank_texturing"
    bl_label = "Save Texturing"
    bl_description = "Save the current file as texturing process."
    bl_options = OPTION_SAVED

    def execute(self, context):
        save(self, context, TEXTURING)
        return {'FINISHED'}


class SaveMorphing(bpy.types.Operator):
    bl_idname = "wm.timebank_morphing"
    bl_label = "Save Morphing"
    bl_description = "Save the current file as morphing process."
    bl_options = OPTION_SAVED

    def execute(self, context):
        save(self, context, MORPHING)
        return {'FINISHED'}


class SaveAnimating(bpy.types.Operator):
    bl_idname = "wm.timebank_animating"
    bl_label = "Save Animating"
    bl_description = "Save the current file as animating process."
    bl_options = OPTION_SAVED

    def execute(self, context):
        save(self, context, ANIMATING)
        return {'FINISHED'}


class SaveRendering(bpy.types.Operator):
    bl_idname = "wm.timebank_rendering"
    bl_label = "Save Rendering"
    bl_description = "Save the current file as rendering process."
    bl_options = OPTION_SAVED

    def execute(self, context):
        save(self, context, RENDERING)
        return {'FINISHED'}


class SaveCompositing(bpy.types.Operator):
    bl_idname = "wm.timebank_compositing"
    bl_label = "Save Compositing"
    bl_description = "Save the current file as compositing process."
    bl_options = OPTION_SAVED

    def execute(self, context):
        save(self, context, COMPOSITING)
        return {'FINISHED'}


class SaveScripting(bpy.types.Operator):
    bl_idname = "wm.timebank_scripting"
    bl_label = "Save Scripting"
    bl_description = "Save the current file as scripting process."
    bl_options = OPTION_SAVED

    def execute(self, context):
        save(self, context, SCRIPTING)
        return {'FINISHED'}


class Laod(bpy.types.Operator):
    bl_idname = "wm.timebank_load"
    bl_label = "Load file"
    bl_description = "Load the blender file."
    bl_options = OPTION_SAVED
    #bl_options = "INTERNAL"
    filepath = bpy.props.StringProperty(name="Filepath", description="Filepath to open mainfile.")#, options="HIDDEN")
    
    def execute(self, context):
        bpy.ops.wm.open_mainfile(filepath=self.filepath)
        self.report({'INFO'}, "Loaded " + self.filepath)        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        #return wm.invoke_props_dialog(self)
        return wm.invoke_confirm(self, event)        
    #def draw(self, context):
    #    layout = self.layout
    #    #layout.label("Load?")
    
class LoadLatest(bpy.types.Operator):
    bl_idname = "wm.timebank_load_latest"
    bl_label = "Load Latest file"
    bl_description = "Load the latest file."
    bl_options = OPTION_SAVED

    def execute(self, context):
        #save(self, context, SCRIPTING)
        filepath = context.blend_data.filepath
        if filepath == "":
            #bpy.ops.wm.save_as_mainfile('INVOKE_AREA')
            #return
            return {'CANCELLED'}
        path = Path(filepath)
        suffix = path.suffix
        stem = path.stem
        first = stem.rfind("_")
        base = stem
        if first == -1:
            return {'CANCELLED'}
        base = base[:first]
        first = base.rfind("_")
        if first == -1:
            return {'CANCELLED'}                
        base = base[:first]
        #self.report({'INFO'}, base)
        parent = path.resolve()
        files = parent.parent.glob(base+'*'+suffix)
        max_num = 0
        max_file = None
        for file in files:
            file_stem = file.stem
            if not file_stem.startswith(base):
                continue
            #self.report({'INFO'}, file_stem)
            first = file_stem.rfind("_")
            num = file_stem[first+1:]
            if num.isdigit():
                #self.report({'INFO'}, num)                        
                num = int(num)                        
                if num > max_num:
                    max_num = num
                    max_file = file
#        bpy.ops.wm.open_mainfile(filepath=str(max_file))
#        self.report({'INFO'}, "Loaded "+str(max_file))        
        bpy.ops.wm.timebank_load("INVOKE_DEFAULT", filepath = str(max_file))
        return {'FINISHED'}
    
#    def invoke(self, context, event):
#            wm = context.window_manager
#            return wm.invoke_props_dialog(self)
    #def draw(self, context):
    #    layout = self.layout
    #    layout.label("Load?")
#class Load(bpy.types.Operator):
#    bl_idname = "wm.timebank_load"
#    bl_label = "Load"
#    bl_description = "Load the file."
#    bl_options = OPTION_SAVED

#    def execute(self, context):
#        #save(self, context, SCRIPTING)
#        filepath = context.blend_data.filepath
#        if filepath == "":
#            #bpy.ops.wm.save_as_mainfile('INVOKE_AREA')
#            #return
#            return {'CANCELLED'}
#        path = Path(filepath)
#        suffix = path.suffix
#        stem = path.stem
#        first = stem.rfind("_")
#        base = stem
#        if first == -1:
#            return {'CANCELLED'}
#        else:
#            base = base[:first]
#            first = base.rfind("_")
#            if first == -1:
#                return {'CANCELLED'}                
#            else:
#                base = base[:first]
#                #self.report({'INFO'}, base)
#                parent = path.resolve()
#                files = parent.parent.glob(base+'*'+suffix)
#                max_num = 0
#                max_file = None
#                #for file in files:
#                #    file_stem = file.stem
#                #    self.report({'INFO'}, file_stem)
#                #    first = file_stem.rfind("_")
#                #    num = file_stem[first+1:]
#                #    if num.isdigit():
#                #        self.report({'INFO'}, num)                        
#                #        num = int(num)                        
#                #        if num > max_num:
#                #            max_num = num
#                #            max_file = file
#                self.report({'INFO'}, "Loaded "+str(max_file))
#                bpy.ops.wm.open_mainfile(filepath=str(max_file))
#        return {'FINISHED'}

class SaveAuto(bpy.types.Operator):
    bl_idname = "wm.timebank_save_auto"
    bl_label = "Save Auto"
    bl_description = "Save the file automatically"
    bl_options = {'REGISTER'}
    #start = None
    processes = None
    _timer = None
    current = 0
    
    def execute(self, context):
        #self.report({"INFO"}, "1")
        self._timer = None
        context.user_preferences.addons[__name__].preferences.saveauto_run = False
        return {'FINISHED'}
    
    def modal(self, context, event):
        #context.area.tag_redraw()
        if not context.user_preferences.addons[__name__].preferences.saveauto:
            self._timer = None
            context.user_preferences.addons[__name__].preferences.saveauto_run = False
            return {'FINISHED'}
        if not event.type == 'TIMER':
            return {'PASS_THROUGH'}
        screen = bpy.context.screen
        window = bpy.context.window
        window_area = window.width * window.height
        #x = event.mouse_x
        #y = event.mouse_y
        #current = datetime.now()
        #end = self.start + timedelta(seconds=1)
#        if current > end:
        #self.report({"INFO"}, ".")
        #self.report({"INFO"}, bpy.context.mode)
        process_area = {MODELING:0.0, SKINNING:0.0, TEXTURING:0.0, MORPHING:0.0, ANIMATING:0.0, RENDERING:0.0, COMPOSITING:0.0, SCRIPTING:0.0}
        for area in screen.areas:
            area_area = area.width * area.height
            ratio = area_area / window_area
            if area.type in ["TIMELINE", "GRAPH_EDITOR", "DOPESHEET_EDITOR", "NLA_EDITOR"]:
                process_area[ANIMATING] += ratio
            if area.type in ["IMAGE_EDITOR"]:
                process_area[TEXTURING] += ratio
            if area.type in ["TEXT_EDITOR", "CONSOLE"]:
                process_area[SCRIPTING] += ratio
            if area.type in ["IMAGE_EDITOR", "NODE_EDITOR"]:
                process_area[COMPOSITING] += ratio
            if area.type in ["SEQUENCE_EDITOR", "CLIP_EDITOR"]:
                process_area[RENDERING] += ratio
            if area.type in ["VIEW_3D"]:
                #self.report({"INFO"}, "c"+context.mode)                        
                #self.report({"INFO"}, "b"+bpy.context.mode)                        
                if context.mode in ["OBJECT","EDIT_MESH", "EDIT_CURVE", "EDIT_SURFACE", "EDIT_TEXT", "EDIT_METABALL", "EDIT_LATTICE", "SCULPT","PARTICLE"]:
                    process_area[MODELING] += ratio
                if context.mode in ["EDIT_ARMATURE", "PAINT_WEIGHT"]:
                    process_area[SKINNING] += ratio
                if context.mode in ["POSE"]:
                    process_area[SKINNING] += ratio
                    process_area[ANIMATING] += ratio                    
                if context.mode in ["PAINT_TEXTURE"]:
                    process_area[TEXTURING] += ratio
        self.current +=1
        self.processes[MODELING] += process_area[MODELING]
        self.processes[SKINNING] += process_area[SKINNING]
        self.processes[TEXTURING] += process_area[TEXTURING]
        self.processes[MORPHING] += process_area[MORPHING]
        self.processes[ANIMATING] += process_area[ANIMATING]
        self.processes[RENDERING] += process_area[RENDERING]
        self.processes[COMPOSITING] += process_area[COMPOSITING]
        self.processes[SCRIPTING] += process_area[SCRIPTING]
            #h = area.x <= x and x < area.x + area.width
            #v = area.y <= y and y < area.y + area.height
            #if h and v:
            #    self.report({"INFO"}, ".")
            #    #print(area.type)
            #    if area.type in ["TIMELINE", "GRAPH_EDITOR", "DOPESHEET_EDITOR", "NLA_EDITOR"]:
            #        self.processes.append(ANIMATING)
            #    if area.type in ["IMAGE_EDITOR"]:
            #        self.processes.append(TEXTURING)
            #    if area.type in ["TEXT_EDITOR", "CONSOLE"]:
            #        self.processes.append(SCRIPTING)
            #    if area.type in ["NODE_EDITOR"]:
            #        self.processes.append(COMPOSITING)
            #    if area.type in ["SEQUENCE_EDITOR", "CLIP_EDITOR"]:
            #        self.processes.append(RENDERING)
            #    if area.type in ["VIEW_3D"]:
            #        self.processes.append(MODELING)                        
        #self.start = current
        num = context.user_preferences.addons[__name__].preferences.saveauto_interval
        if self.current >= num:
            ps = [[n, 0.0] for n in range(ALL)]
            ps[MODELING][RATIO] = self.processes[MODELING]
            ps[SKINNING][RATIO] = self.processes[SKINNING]            
            ps[TEXTURING][RATIO] = self.processes[TEXTURING]
            ps[MORPHING][RATIO] = self.processes[MORPHING]
            ps[ANIMATING][RATIO] = self.processes[ANIMATING]
            ps[RENDERING][RATIO] = self.processes[RENDERING]
            ps[COMPOSITING][RATIO] = self.processes[COMPOSITING]
            ps[SCRIPTING][RATIO] = self.processes[SCRIPTING]            
            ranks = sorted(ps,  key=lambda p: p[1], reverse=True)
            first = ranks[0][PROCESS]
            second = ranks[1][PROCESS]
            ave_second = ranks[1][RATIO] / num
            if ave_second > 0.33:
                p1 = min(first, second)
                p2 = max(first, second)
                if p1 == MODELING:
                    self.save(context, second)
                else:
                    self.save(context, first)
            else:
                self.save(context, first)
            self.processes = {MODELING:0.0, SKINNING:0.0, TEXTURING:0.0, MORPHING:0.0, ANIMATING:0.0, RENDERING:0.0, COMPOSITING:0.0, SCRIPTING:0.0}
            self.current = 0
        #return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        #self.report({"INFO"}, "1")
        context.user_preferences.addons[__name__].preferences.saveauto_run = True
        #self.start = datetime.now()
        #self.processes = []
        self.current = 0
        self.processes = {MODELING:0.0, SKINNING:0.0, TEXTURING:0.0, MORPHING:0.0, ANIMATING:0.0, RENDERING:0.0, COMPOSITING:0.0, SCRIPTING:0.0}
        self._timer = context.window_manager.event_timer_add(1.0, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def save(self, context, index):
        filepath = context.blend_data.filepath
        if filepath == "":
            self.report({"WARNING"}, "Auto save was failed. Please save the file manually once.")
            return
        if index == MODELING:
            #SaveModeling.execute(context)
            bpy.ops.wm.timebank_modeling()
        if index == SKINNING:
            #SaveSkinning.execute(context)
            bpy.ops.wm.timebank_skinning()
        if index == TEXTURING:
            #SaveTexturing.execute(context)
            bpy.ops.wm.timebank_texturing()
        if index == MORPHING:
            #SaveMorphing.execute(context)
            bpy.ops.wm.timebank_morphing()
        if index == ANIMATING:
            #SaveAnimating.execute(context)
            bpy.ops.wm.timebank_animating()
        if index == RENDERING:
            #SaveRendering.execute(context)
            bpy.ops.wm.timebank_rendering()
        if index == COMPOSITING:
            #SaveCompositing.execute(context)
            bpy.ops.wm.timebank_compositing()
        if index == SCRIPTING:
            #SaveScripting.execute(context)
            bpy.ops.wm.timebank_scripting()
        self.report({"INFO"}, "Saved the file automatically.")
        
class TimebankLoadMenu(bpy.types.Menu):
    bl_label = "Load Timebank"
    bl_idname = "INFO_MT_timebank_load_menu"

    def draw(self, context):
        layout = self.layout
        #layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(LoadLatest.bl_idname)
        layout.menu(TimebankAllMenu.bl_idname, icon="RECOVER_LAST")
        
        
class TimebankAllMenu(bpy.types.Menu):
    bl_label = "All files"
    bl_idname = "INFO_MT_timebank_all_menu"

    def draw(self, context):
        layout = self.layout
        #layout.operator_context = 'EXEC_DEFAULT'
        layout.operator_context = "INVOKE_DEFAULT"
        filepath = context.blend_data.filepath
        if filepath == "":
            return
        path = Path(filepath)
        suffix = path.suffix
        stem = path.stem
        first = stem.rfind("_")
        base = stem
        if first == -1:
            return
        base = base[:first]
        first = base.rfind("_")
        if first == -1:
            return
        base = base[:first]
        #self.report({'INFO'}, base)
        parent = path.resolve()
        files = parent.parent.glob(base+'*'+suffix)
        files = sorted(files, key = num_fn, reverse=True)
        #max_num = 0
        #max_file = None
        for file in files:
            file_stem = file.stem
            #layout.label(text=file_stem)
            first = file_stem.rfind("_")
            if first == -1:
                continue
            pro = file_stem[:first]
            first = pro.rfind("_")
            if first == -1:
                continue
            pro = pro[first+1:]
            icon = "NONE"
            if pro == PROCESSES[MODELING]:
                icon = MODELING_ICON
            if pro == PROCESSES[SKINNING]:
                icon = SKINNING_ICON
            if pro == PROCESSES[TEXTURING]:
                icon = TEXTURING_ICON
            if pro == PROCESSES[MORPHING]:
                icon = MORPHING_ICON
            if pro == PROCESSES[ANIMATING]:
                icon = ANIMATING_ICON
            if pro == PROCESSES[RENDERING]:
                icon = RENDERING_ICON
            if pro == PROCESSES[COMPOSITING]:
                icon = COMPOSITING_ICON
            if pro == PROCESSES[SCRIPTING]:
                icon = SCRIPTING_ICON
            if icon == "NONE":
                continue
            #op = layout.operator("wm.open_mainfile", text = file.name, icon=icon)
            op = layout.operator("wm.timebank_load", text = file.name, icon=icon)
            #bpy.ops.wm.timebank_load("INVOKE_DEFAULT", filepath = str(max_file))
            op.filepath = str(file)
            #op.bl_options = OPTION_SAVED
            #op.label = file.name
        #    self.report({'INFO'}, file_stem)
        #    first = file_stem.rfind("_")
        #    num = file_stem[first+1:]
        #    if num.isdigit():
        #        self.report({'INFO'}, num)                        
        #        num = int(num)                        
        #        if num > max_num:
        #            max_num = num
        #            max_file = file
        #self.report({'INFO'}, "Loaded "+str(max_file))
        #bpy.ops.wm.open_mainfile(filepath=str(max_file))

def num_fn(file):
    stem = file.stem
    first = stem.rfind("_")
    num = stem[first+1:]
    if not num.isdigit():
        num = -1
    return int(num)

def menu_fn(self, context):
    self.layout.separator()
    self.layout.menu(TimebankLoadMenu.bl_idname, icon="RECOVER_LAST")
    self.layout.operator(SaveModeling.bl_idname, icon=MODELING_ICON)
    self.layout.operator(SaveSkinning.bl_idname, icon=SKINNING_ICON)
    self.layout.operator(SaveTexturing.bl_idname, icon=TEXTURING_ICON)
    self.layout.operator(SaveMorphing.bl_idname, icon=MORPHING_ICON)
    self.layout.operator(SaveAnimating.bl_idname, icon=ANIMATING_ICON)
    self.layout.operator(SaveRendering.bl_idname, icon=RENDERING_ICON)
    self.layout.operator(SaveCompositing.bl_idname, icon=COMPOSITING_ICON)
    self.layout.operator(SaveScripting.bl_idname, icon=SCRIPTING_ICON)
    #self.layout.operator(SaveAuto.bl_idname, icon=SCRIPTING_ICON)
    
class TIMEBANK_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    saveauto = bpy.props.BoolProperty(name="Save Auto", description="Save the file automatically")
    saveauto_run = bpy.props.BoolProperty(name="Save Auto Run", description="Whether autosave run or not", default=False, options={"HIDDEN", "SKIP_SAVE"})
    saveauto_interval = bpy.props.IntProperty(name="Interval", description="Interval for saving automatically in seconds", min=1, default=180)
    
    def draw(self, context):
        layout = self.layout
        #layout.label("Test")
        #row = layout.row()
        row = layout.row()        
        row.prop(self, "saveauto")
        row.label("The starting need saving manually once.", icon="ERROR")
        column = layout.column()
        column.prop(self, "saveauto_interval")
        column.enabled = not context.user_preferences.addons[__name__].preferences.saveauto_run
                
        #if self.saveauto and not self.saveauto_run:
        #    #SaveAuto.execute(self, context)
        #    bpy.ops.wm.timebank_save_auto('INVOKE_DEFAULT')            
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file.append(menu_fn)


def unregister():
    bpy.types.INFO_MT_file.remove(menu_fn)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
