######################################################################################################
# An operator to automatically save your file with an incremental suffix                             #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me.                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################

############# Add-on description (used by Blender)

bl_info = {
    "name": "Auto Save Incremental",
    "description": 'Automatically save your file with an incremental suffix (after a defined period of time)',
    "author": "Lapineige",
    "version": (1, 6),
    "blender": (2, 74, 0),
    "location": "File > Auto Save Incremental",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

##############

import bpy, os
from time import time as tm
from bpy.props import IntProperty, FloatProperty, StringProperty, BoolProperty

#####

def rp_d(path): # realpath for directories
    path = os.path.realpath(path)
    if not path[-1] == os.path.sep:
        path += os.path.sep
    return path

def rp_f(path): # realpath for files
    path = os.path.realpath(path)
    return path
  
##############

class AutoSaveIncrementalPreferencesPanel(bpy.types.AddonPreferences):
    """ """
    bl_idname = __name__
    
    sep = os.path.sep

    time_btw_save_second = IntProperty(default=0, min=0, max=59)
    time_btw_save_min = IntProperty(default=5, min=0, max=86400) # max 1 day
    dir_path_user_defined = StringProperty(subtype='DIR_PATH', default= '//'+'Auto Save'+sep, description="Output directory for the render") # user defined, will be changed by the code    # Voir chemin os + bouton setup adapté à l'os
    dir_path = StringProperty(subtype='DIR_PATH', default='', description="Output directory for the render used by the Auto Save tool")
    stop = BoolProperty(default=False, description="Property used to stop auto save - to avoid multiple simultaneous instances")
    active = BoolProperty(default=False, description="Property used to avoid starting it after a save - if not enabeled")
    active_main_save = BoolProperty(default=False, description="Property used to avoid starting it after auto save - preven from handler effect")
    report_save = BoolProperty(default=True, description="Show an info message on saving on the info header")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "time_btw_save_min", text="Timer (mins)")
        row.prop(self, "time_btw_save_second", text="Timer (seconds)")
        #row.prop(self, "report_save", text="Show Save Alert")

        layout.prop(self, "dir_path_user_defined", text="Auto-Save Directory")
        return {'FINISHED'}

class AutoIncrementalSave(bpy.types.Operator):
    bl_idname = "file.auto_save_incremental"
    bl_label = "Auto Save Incremental"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        sep = os.path.sep
        
        if bpy.data.filepath:
            dir_name = rp_d(context.user_preferences.addons[__name__].preferences.dir_path)
            f_path = os.path.dirname(bpy.data.filepath) + dir_name + bpy.path.basename(bpy.data.filepath)
            #bpy.ops.wm.save_mainfile(filepath=f_path)

            # detecting number
            increment_files = [file for file in os.listdir(os.path.dirname(f_path)) if os.path.basename(f_path).split('.blend')[0] in file.split('.blend')[0] and file.split('.blend')[0] !=  os.path.basename(f_path).split('.blend')[0]]
            for file in increment_files:
                if not detect_number(file):
                    increment_files.remove(file)
            numbers_index = [ ( index, detect_number(file.split('.blend')[0]) ) for index, file in enumerate(increment_files)]
            numbers = [index_nb[1] for index_nb in numbers_index] #[detect_number(file.split('.blend')[0]) for file in increment_files]
            if numbers: # prevent from error with max()
                str_nb = str( max([int(n[2]) for n in numbers])+1 ) # zfill to always have something like 001, 010, 100

            if increment_files:
                d_nb = detect_number(increment_files[-1].split('.blend')[0])
                str_nb = str_nb.zfill(len(d_nb[2]))
                #print(d_nb, len(d_nb[2]))
            else:
                d_nb = False
                d_nb_filepath = detect_number(os.path.basename(f_path).split('.blend')[0])
                #if numbers: ## USELESS ??
                #    str_nb.zfill(3)
                if d_nb_filepath:
                    str_nb = str(int(d_nb_filepath[2]) + 1).zfill(len(d_nb_filepath[2]))
            # generating output file name
            if d_nb:
                if len(increment_files[-1].split('.blend')[0]) < d_nb[1]: # in case last_nb_index is just after filename's max index
                    output = bpy.path.abspath("//") + dir_name + increment_files[-1].split('.blend')[0][:d_nb[0]] + str_nb + '.blend'
                else:
                    output = bpy.path.abspath("//") + dir_name + increment_files[-1].split('.blend')[0][:d_nb[0]] + str_nb + increment_files[-1].split('.blend')[0][d_nb[1]:] + '.blend'
            else:
                if d_nb_filepath:
                    if len(os.path.basename(f_path).split('.blend')[0]) < d_nb_filepath[1]: # in case last_nb_index is just after filename's max index
                        output = bpy.path.abspath("//") + dir_name + os.path.basename(f_path).split('.blend')[0][:d_nb_filepath[0]] + str_nb + '.blend'
                    else:
                        output = bpy.path.abspath("//") + dir_name + os.path.basename(f_path).split('.blend')[0][:d_nb_filepath[0]] + str_nb + os.path.basename(f_path).split('.blend')[0][d_nb_filepath[1]:] + '.blend'
                else:
                    output = rp_f(f_path.split(".blend")[0] + '_' + '001' + '.blend')
            if os.path.isfile(output):
                self.report({'WARNING'}, "Internal Error: trying to save over an existing file. Cancelled")
                print('Tested Output: ', output)
                return {'CANCELLED'}

            bpy.context.user_preferences.addons[__name__].preferences.active_main_save = True # active_main_save avoid restrarting at this state
            bpy.ops.wm.save_as_mainfile(filepath=output, copy=True)
            bpy.context.user_preferences.addons[__name__].preferences.active_main_save = False

            self.report({'INFO'}, "File: {0} - Created at: {1}".format( rp_f(os.path.basename(output)), rp_d(os.path.basename(output)) ))
            
        else:
            self.report({'WARNING'}, "Please save a main file")
            
        return {'FINISHED'}
        ###### PENSER A TESTER AUTRES FICHIERS DU DOSSIER, VOIR SI TROU DANS NUMEROTATION==> WARNING

class AutoIncrementalSaveModal(bpy.types.Operator):
    """  """
    bl_idname = "file.auto_save_incremental_modal"
    bl_label = "Auto Save Incremental"
    
    def modal(self, context, event):
        #print(tm()-self.time)

        if context.user_preferences.addons[__name__].preferences.stop == True:
            print('Auto Save Disabled')
            context.user_preferences.addons[__name__].preferences.active = False
            return {'FINISHED'}

        if tm()-self.time >= ( context.user_preferences.addons[__name__].preferences.time_btw_save_min*60 + context.user_preferences.addons[__name__].preferences.time_btw_save_second):
            print('Auto Saving...')
            bpy.ops.file.auto_save_incremental()
            if context.user_preferences.addons[__name__].preferences.report_save:
                self.report({'WARNING'}, "Auto Saving....")
            self.time = tm()

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if not bpy.data.filepath:
            self.report({'WARNING'}, "Auto Save Cancelled: Please save a main file")
            return {'CANCELLED'}
        sep = os.path.sep
        
        context.user_preferences.addons[__name__].preferences.dir_path = context.user_preferences.addons[__name__].preferences.dir_path_user_defined + os.path.basename(bpy.data.filepath.split('.blend')[0]) + sep # to create a directory with base file name # change to prefs => access from all the code
        dir_path = rp_d( os.path.dirname(bpy.data.filepath) + context.user_preferences.addons[__name__].preferences.dir_path ) # base path + new directory path
        
        print()
        print('Creating directory and base file (copy of current file)...')

        print('Trying to create directory: ', dir_path)
        if os.path.isdir(dir_path):
            print('Directory already exists')
        else:
            os.makedirs(dir_path, exist_ok=True) # os.makedirs(dir_path) => it's enough (without any existence info)
            print('Directory created')
        
        bpy.context.user_preferences.addons[__name__].preferences.active_main_save = True # active_main_save avoid restarting at this state
        basefile = rp_f( dir_path + bpy.path.basename(bpy.data.filepath).split('.blend')[0] + '_000' +  '.blend')
        bpy.ops.wm.save_as_mainfile(filepath=basefile, copy=True)
        bpy.context.user_preferences.addons[__name__].preferences.active_main_save = False
        print('Base file created: ', basefile)

        context.user_preferences.addons[__name__].preferences.stop = False
        context.user_preferences.addons[__name__].preferences.active = True    
        self.time = tm()
        context.window_manager.modal_handler_add(self)

        print('Auto Incremental Saving started')
        print()
        return {'RUNNING_MODAL'}
        #self.report({'WARNING'}, "No active object, could not finish")
        #return {'CANCELLED'}

##############

def detect_number(name):
    last_nb_index = -1

    for i in range(1,len(name)):
        if name[-i].isnumeric():
            if last_nb_index == -1:
                last_nb_index = len(name)-i+1 # +1 because last index in [:] need to be 1 more
        elif last_nb_index != -1:
            first_nb_index = len(name)-i+1 #+1 to restore previous index
            return (first_nb_index,last_nb_index,name[first_nb_index:last_nb_index]) # first: index of the number / last: last number index +1
    return False

# layout
def draw_into_file_menu(self,context):
    self.layout.operator('file.auto_save_incremental_modal', icon='SAVE_COPY')

def draw_into_info_header(self,context):
    if context.user_preferences.addons[__name__].preferences.active:
        self.layout.label('Auto Save Enabled',icon='REC')


# handlers
def stop_on_save(dummy):
    if not bpy.context.user_preferences.addons[__name__].preferences.active_main_save:
        print('Manual Save - Auto Save Restarting...')
        print()
        if bpy.context.user_preferences.addons[__name__].preferences.active:   
            bpy.context.user_preferences.addons[__name__].preferences.stop = True # kill any running instance

def start_after_save(dummy):
    if not bpy.context.user_preferences.addons[__name__].preferences.active_main_save:
        if bpy.context.user_preferences.addons[__name__].preferences.active:
            bpy.ops.file.auto_save_incremental_modal('INVOKE_DEFAULT')
        #else:
        #    bpy.context.user_preferences.addons[__name__].preferences.stop = False


##############

def register():
    bpy.utils.register_class(AutoIncrementalSave)
    bpy.types.INFO_MT_file.prepend(draw_into_file_menu)
    bpy.types.INFO_HT_header.append(draw_into_info_header)
    bpy.utils.register_class(AutoIncrementalSaveModal)
    bpy.utils.register_class(AutoSaveIncrementalPreferencesPanel)
    bpy.app.handlers.save_pre.append(stop_on_save)
    bpy.app.handlers.save_post.append(start_after_save)


def unregister():
    bpy.utils.unregister_class(AutoIncrementalSave)
    bpy.types.INFO_MT_file.remove(draw_into_file_menu)
    bpy.types.INFO_HT_header.remove(draw_into_info_header)
    bpy.utils.unregister_class(AutoIncrementalSaveModal)
    bpy.utils.unregister_class(AutoSaveIncrementalPreferencesPanel)
    bpy.app.handlers.save_pre.remove(stop_on_save)
    bpy.app.handlers.save_post.remove(start_after_save)


if __name__ == "__main__":
    register()
