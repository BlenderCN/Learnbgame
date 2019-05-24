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

# <pep8 compliant>
#

bl_info = {
    "name": "Path Editor",
    "author": "Alfonso Annarumma",
    "version": (0, 5),
    "blender": (2, 70, 0),
    "location": "Proprieties > Scene > Path Editor",
    "description": "Display and Edit Path",
    "wiki_url": "http://blenderaddonlist.blogspot.com.au/2014/06/addon-path-editor.html",
    "category": "Learnbgame",
}

import bpy
import os
from bpy.props import StringProperty, BoolProperty, CollectionProperty, IntProperty

#EDIT = {"EDIT_MESH", "EDIT_CURVE", "EDIT_SURFACE", "EDIT_METABALL", "EDIT_TEXT", "EDIT_ARMATURE"}

#funbzione per elencare le path e metterle nella proprietà directory path
def list_file_path (files, type):
    scene = bpy.context.scene
    #creo una lista vuota dove mettere le directory di tutte le immagini
    directory_files_list= []

    # in questo ciclo, estraggo per ogni immagine la path della sua directory
    for file in files:

        if type == 'SEQUENCE' and file.type != 'MOVIE':
            continue
        file_path = file.filepath
        directory_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        abs = bpy.path.abspath(file_path)
        if type =='FILE_IMAGE' and os.path.exists(abs):
            file.update()



        #if os.path.exists(abs):

            #file.update()


        # per evitare doppioni metto nella lista (directory_images_list) solo le directory_path che non ci sono già
        if not directory_path in directory_files_list:

            directory_files_list.append(directory_path)
         # ottengo così una lista dei percorsi delle cartelle dove sono le immagini

    for old_directory in directory_files_list:

        scene.directory_old_path.add()
        scene.directory_new_path.add()
        scene.directory_old_path[-1].name = old_directory
        scene.directory_new_path[-1].directory_path = old_directory
        #print(type)
        scene.directory_old_path[-1].type = type
        scene.directory_new_path[-1].type = type

    return {'FINISHED'}


# classe per definire i la proprietà che si occuperà di gestire le path delle directory
class DirectoryPath(bpy.types.PropertyGroup):


    directory_path = StringProperty(name = "",default = "",description = "Define path of directory", subtype = 'DIR_PATH')

    show_images_links = BoolProperty(name="Show images link", default=False)

    extension = StringProperty(default="none")

    type = StringProperty()



class RemoveFile(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "scene.removefile"
    bl_label = "Remove File"


    name = StringProperty()
    type = StringProperty()



    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene

        # prima di tutto stabilisce il tipo di file
        if self.type == 'FILE_IMAGE':

            files = bpy.data.images

        if self.type == 'SEQUENCE':
            # per i video del sequence non si agisce sui data ma direttamente sulle strip
            files = scene.sequence_editor.sequences
            file = files[self.name]

            files.remove(file)
            return {'FINISHED'}

        if self.type == 'CLIP':

            files = bpy.data.movieclips

        if self.type == 'SOUND':

            return {'FINISHED'}

        if self.type == 'TEXT':

            files = bpy.data.texts

        #se invce di tratta di data, si cancella anche l'user

        file = files[self.name]
        file.user_clear()
        files.remove(file)


        # in fine si fa un refreshpath
        if not files:
            bpy.ops.scene.refreshpath()

        return {'FINISHED'}

class RenamePath(bpy.types.Operator):
    '''Change the directory'''
    bl_idname = "scene.renamepath"
    bl_label = "Rename Path"

    old_path = StringProperty()
    new_path = StringProperty()
    extension = StringProperty()
    type = StringProperty()
    dir_index = IntProperty()


    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):


        scene = bpy.context.scene
        files = ""

        if self.type == 'FILE_IMAGE':

            files = bpy.data.images

        if self.type == 'SEQUENCE':

            files = scene.sequence_editor.sequences

        if self.type == 'CLIP':

            files = bpy.data.movieclips

        if self.type == 'SOUND':

            files = bpy.data.sounds

        if self.type == 'TEXT':

            files = bpy.data.texts


        if not self.new_path:
            self.new_path = self.old_path

        # avvio il rename solo se il campo path è pieno oppure se è pieno quello dell'estensione
        if (self.old_path != self.new_path) or (self.extension != ""):

            # listo i file nella nuova directory
            #f = []
                #for (dirpath, dirnames, filenames) in os.walk(self.new_path):
                #f.extend(filenames)
                #break

            for file in files:

                if self.type == 'SEQUENCE' and file.type != 'MOVIE':
                    continue
                file_path = file.filepath

                old_file = file_path

                directory_path = os.path.dirname(file_path)


                file_name = os.path.basename(file_path)

                #controllo che l'immagine sia nella cartella
                if directory_path == self.old_path:

                    n= len(file_name)

                    slash = "/"
                    #controllo se la nuova path abbia lo "/" finale altrimento lo aggiuingo
                    if self.new_path[-1] != slash:
                        self.new_path = self.new_path + slash
                        #print (self.new_path[-1])

                    file_path = self.new_path + file_name
                    # se la path esiste (cioè l'immagine nella nuova cartella c'è) applico la modifica

                    #print(file_name [n-3:])
                    #print(file_name [n-4:])

                    #controllo che ci sia da cambiare l'estensione
                    if (self.extension != "none") and ((self.extension != file_name [n-3:]) or (self.extension != file_name [n-4:])):

                        file_path = bpy.path.ensure_ext(file_path, "."+self.extension, case_sensitive=False)
                        #print (image_path)

                    #prima di applicare la modifica della path, controllo che il file esista
                    abs = bpy.path.abspath(file_path)

                    #if os.path.exists(abs):

                    file.filepath = file_path

                    #if not image.update():
                        #print("error")
                        #image.filepath = old_image
                    #if not image.has_data:
                       # image.filepath = old_image
                        #image.update()
                   # else:

            bpy.ops.scene.refreshpath()
            scene.directory_old_path[self.dir_index].show_images_links = True
            #print(self.dir_index)
        return {'FINISHED'}


class RefreshPath(bpy.types.Operator):
    '''Update the images list'''
    bl_idname = "scene.refreshpath"
    bl_label = "Refresh Path"

    filepath = StringProperty()

    @classmethod
    def poll(cls, context):
        return context.scene is not None


    def execute(self, context):
        scene = context.scene
        scene.directory_old_path.clear()
        scene.directory_new_path.clear()

        if scene.MovieclipsFilter:
            movies = bpy.data.movieclips
            list_file_path(movies,'CLIP')

        if scene.ImagesFilter:

            #preleva una lista di tutte le immagini in scena
            images = bpy.data.images
            list_file_path(images,'FILE_IMAGE')

        if scene.SoundsFilter:
            sounds = bpy.data.sounds
            list_file_path(sounds, 'SOUND')

        if scene.TextsFilter:
            texts = bpy.data.texts
            list_file_path(texts, 'TEXT')

        if scene.SequencesVideosFilter:
            if scene.sequence_editor:

                sequences = scene.sequence_editor.sequences
                list_file_path(sequences, 'SEQUENCE')

        #funzione per creare lista path cartelle immagini

        return {'FINISHED'}

class PathEditorPanel(bpy.types.Panel):
    """Rename directory path of multiply file"""
    bl_label = "Path Editor"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    bpy.types.Scene.MovieclipsFilter= BoolProperty(name="Show Movieclips", default=False)
    bpy.types.Scene.ImagesFilter= BoolProperty(name="Show Images", default=True)
    bpy.types.Scene.TextsFilter= BoolProperty(name="Show Texts", default=False)
    bpy.types.Scene.SequencesVideosFilter= BoolProperty(name="Show SequencesVideos", default=False)
    bpy.types.Scene.SoundsFilter= BoolProperty(name="Show Sounds", default=False)

    def draw(self, context):

        scene = context.scene

        layout = self.layout

        # Create FIVE columns, by using a split layout.


        column = layout.column()

        # riga per filtri


        row01 = column.row(align=True)

        row01.prop(scene, "MovieclipsFilter", text="", icon='FILE_MOVIE')
        row01.prop(scene, "ImagesFilter", text="", icon='FILE_IMAGE')
        row01.prop(scene, "SoundsFilter", text="", icon='FILE_SOUND')
        row01.prop(scene, "TextsFilter", text="", icon='FILE_TEXT')
        row01.prop(scene, "SequencesVideosFilter", text="", icon='SEQUENCE')

        row1= column.row()

        # prima riga, pulsante per il refresh

        col = row1.column()
        col.operator("scene.refreshpath", text="refresh")


        #col0 = row1.column()
        #col0.prop(scene, "ImageThree")

        #seconda riga, titoli
        row2= column.row()


        # First column
        col1 = row2.column(align=True)
        col1.scale_x = 0.5
        col1.label(text="Directory")

        # Second column, aligned
        col2 = row2.column(align=True)
        col2.scale_x = 2.0
        col2.label(text="Path:")



        # third column, aligned
        col3 = row2.column(align=True)
        col3.scale_x = 0.3
        col3.label(text="extension:")


        # Forth column, aligned
        col4 = row2.column(align=True)
        col4.scale_x = 0.2
        col4.label(text="Apply:")

    ########################################

        i=0
        images = bpy.data.images
        dirs = sorted(scene.directory_old_path, key=lambda DirectoryPath: DirectoryPath.type)
        newdirs = sorted(scene.directory_new_path, key=lambda DirectoryPath: DirectoryPath.type)
        typef = "NONE"
      # per ogni cartella che si trova nella lista elenco le opzioni per il rename
        for old_dir in dirs:

            #variabili
            new_dir = newdirs[i]
            directory_files = []

            #stampa il tipo di file sulle righe
            if old_dir.type != typef:
                typef = old_dir.type
                #print("typef"+typef)
                row42 = column.row()
                col42 = row42.column()

                col42.label(text=typef, icon=typef)

            #print("+"+old_dir.type)

            box4 = column.box()
            row3 = box4.row()
            #terza riga, elenco cartelle


            # Old_path
            col5 = row3.column(align=True)
            col5.scale_x = 0.5
            dir = os.path.basename(old_dir.name)

            col5.label(text=dir)

            # show images link

            if old_dir.show_images_links:
                icon_show = 'DISCLOSURE_TRI_DOWN'
            else:
                icon_show = 'DISCLOSURE_TRI_RIGHT'

            col61 = row3.column(align=True)
            col61.scale_x = 2.0
            col61.prop(old_dir, "show_images_links", text="", icon=icon_show, emboss=False)

            # New_path
            col6 = row3.column(align=True)
            col6.scale_x = 2.0
            col6.prop(new_dir, "directory_path")
            #col.prop(scene.directory_path[-1],"name")


            # Extension
            col7 = row3.column(align=True)
            col7.scale_x = 0.3
            col7.prop(new_dir, "extension", text="")


            # Apply
            col8 = row3.column(align=True)
            col8.scale_x = 0.2
            ren = col8.operator("scene.renamepath", text="apply")
            ren.old_path = old_dir.name
            ren.new_path = new_dir.directory_path
            ren.extension = new_dir.extension
            ren.dir_index = i
            ren.type = typef

            #typef = old_dir.type


            #riga aggiuntiva per immagini

            if old_dir.show_images_links:

                if typef == 'FILE_IMAGE':

                    files = bpy.data.images

                if typef == 'SEQUENCE':

                    files = scene.sequence_editor.sequences

                if typef == 'CLIP':

                    files = bpy.data.movieclips

                if typef == 'SOUND':

                    files = bpy.data.sounds

                if typef == 'TEXT':

                    files = bpy.data.texts


                for file in files:

                    if typef == 'SEQUENCE' and file.type != 'MOVIE':
                        continue


                    file_path = file.filepath
                    directory_path = os.path.dirname(file_path)


                    if directory_path == old_dir.name:


                        directory_files.append(file)


                box = column.box()


                for file in directory_files:

                    #if typef == 'SOUND' and file.users == 0:
                        #continue

                    row4 = box.row()
                    # colonna di stacco
                    col9 = row4.column(align=True)
                    col9.scale_x = 0.5
                    col9.prop(file, "name", text ="")


                    col10 = row4.column(align=True)
                    col10.scale_x = 1.6
                    col10.prop(file, "filepath", text ="")

                    if typef == 'FILE_IMAGE':

                        if not file.has_data:
                            dirty = 'ERROR'
                            format = "Error"
                        else:
                            dirty = typef
                            format = file.file_format
                    else:
                        format = ''
                        dirty = 'NONE'


                    if typef == 'SOUND':
                        col12 = row4.column(align=True)
                        col12.scale_x = 1
                        col12.label(text="", icon=typef)
                        continue

                    col11 = row4.column(align=True)
                    col11.scale_x = 0.3
                    col11.label(text=format)

                    col12 = row4.column(align=True)
                    col12.scale_x = 1
                    col12.label(text="", icon=typef)

                    col13 = row4.column(align=True)

                    col13.scale_x = 1
                    remove = col13.operator("scene.removefile", text="", icon='X')
                    remove.name = file.name
                    remove.type =typef


            i = 1+i


def register():

    bpy.utils.register_module(__name__)

    bpy.types.Scene.directory_old_path = CollectionProperty(type=DirectoryPath)
    bpy.types.Scene.directory_new_path = CollectionProperty(type=DirectoryPath)
    #bpy.types.Scene.dir_path = StringProperty()

def unregister():


    bpy.utils.register_module(__name__)
    del bpy.types.Scene.directory_old_path
    del bpy.types.Scene.directory_new_path


if __name__ == "__main__":
    register()
