######################################################################################################
# An operator to save your file with an incremental suffix                                          #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me.                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################

############# Add-on description (used by Blender)

bl_info = {
    "name": "Save Incremental",
    "description": 'Save your file with an incremental suffix',
    "author": "Lapineige",
    "version": (1, 7),
    "blender": (2, 72, 0),
    "location": "File > Save Incremental",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=18&t=736",
    "category": "Learnbgame"
}

##############
import bpy, os

def detect_number(name):
    last_nb_index = -1

    for i in range(1,len(name)):
        if name[-i].isnumeric():
            if last_nb_index == -1:
                last_nb_index = len(name)-i+1 # +1 because last index in [:] need to be 1 more
        elif last_nb_index != -1:
            first_nb_index = len(name)-i+1 #+1 to restore previous index
            return (first_nb_index,last_nb_index,name[first_nb_index:last_nb_index]) #first: index of the number / last: last number index +1
    return False

class FileIncrementalSave(bpy.types.Operator):
    bl_idname = "file.save_incremental"
    bl_label = "Save Incremental"
   
    def execute(self, context):
        if bpy.data.filepath:
            sep = os.path.sep
            d_sep = sep + sep
            f_path = bpy.data.filepath
            #bpy.ops.wm.save_mainfile(filepath=f_path)

            increment_files=[file for file in os.listdir(os.path.dirname(f_path)) if os.path.basename(f_path).split('.blend')[0] in file.split('.blend')[0] and file.split('.blend')[0] !=  os.path.basename(f_path).split('.blend')[0]]
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
                d_nb =False
                d_nb_filepath = detect_number(os.path.basename(f_path).split('.blend')[0])
                #if numbers: ## USELESS ??
                #    str_nb.zfill(3)
                if d_nb_filepath:
                    str_nb = str(int(d_nb_filepath[2]) + 1).zfill(len(d_nb_filepath[2]))

            if d_nb:
                if len(increment_files[-1].split('.blend')[0]) < d_nb[1]: # in case last_nb_index is just after filename's max index
                    output = bpy.path.abspath(d_sep) + increment_files[-1].split('.blend')[0][:d_nb[0]] + str_nb + '.blend'
                else:
                    output = bpy.path.abspath(d_sep) + increment_files[-1].split('.blend')[0][:d_nb[0]] + str_nb + increment_files[-1].split('.blend')[0][d_nb[1]:] + '.blend'
            else:
                if d_nb_filepath:
                    if len(os.path.basename(f_path).split('.blend')[0]) < d_nb_filepath[1]: # in case last_nb_index is just after filename's max index
                        output = bpy.path.abspath(d_sep) + os.path.basename(f_path).split('.blend')[0][:d_nb_filepath[0]] + str_nb + '.blend'
                    else:
                        output = bpy.path.abspath(d_sep) + os.path.basename(f_path).split('.blend')[0][:d_nb_filepath[0]] + str_nb + os.path.basename(f_path).split('.blend')[0][d_nb_filepath[1]:] + '.blend'
                else:
                    output = f_path.split(".blend")[0] + '_' + '001' + '.blend'

            if os.path.isfile(output):
                self.report({'WARNING'}, "Internal Error: trying to save over an existing file. Cancelled")
                print('Tested Output: ', output)
                return {'CANCELLED'}
            bpy.ops.wm.save_mainfile()
            bpy.ops.wm.save_as_mainfile(filepath=output, copy=True)
            
            self.report({'INFO'}, "File: {0} - Created at: {1}".format(output[len(bpy.path.abspath(d_sep)):], output[:len(bpy.path.abspath(d_sep))]))
        else:
            self.report({'WARNING'}, "Please save a main file")
        return {'FINISHED'}
        ###### PENSER A TESTER AUTRES FICHIERS DU DOSSIER, VOIR SI TROU DANS NUMEROTATION==> WARNING

def draw_into_file_menu(self,context):
    self.layout.operator('file.save_incremental', icon='SAVE_COPY')


def register():
    bpy.utils.register_class(FileIncrementalSave)
    bpy.types.INFO_MT_file.prepend(draw_into_file_menu)


def unregister():
    bpy.utils.unregister_class(FileIncrementalSave)
    bpy.types.INFO_MT_file.remove(draw_into_file_menu)


if __name__ == "__main__":
    register()
