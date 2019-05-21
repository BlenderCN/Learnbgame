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

'''
bl_info = {
    "name": "Import Reconstruct file (.ser)",
    "author": "Bartol, Tom",
    "version": (0, 2, 0),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Import .ser files,
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}
'''



class ImportSer(bpy.types.Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_scene.reconstruct_file"
    bl_label = "Import Reconstruct file and read trace names"
    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".ser"

    filter_glob = StringProperty(
            default="*.ser",
            options={'HIDDEN'},
            )

    files = CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):

        # get the folder
        folder = (os.path.dirname(self.filepath))

        # iterate through the selected files
        #for j, i in enumerate(self.files):

                # generate full path to file
      #          path_to_file = (os.path.join(folder, i.name))
      #          bpy.ops.import_scene.ser(filepath = path_to_file,

        if (len(sys.argv)<2):
            sys.stderr.write('\nUsage: %s reconstruct_series_prefix \n' % (sys.argv[0]))
            sys.stderr.write('           Get names of all objects in a Reconstruct Series \n')
            sys.stderr.write('           Output is written to stdout\n\n')
            exit(1)

        ser_prefix = sys.argv[1]

        ser_file = open(ser_prefix + '.ser')

        ser_data = ser_file.read()

        min_section = int(ser_data.split('first3Dsection="')[1].split('"')[0])
        max_section = int(ser_data.split('last3Dsection="')[1].split('"')[0])

        ser_file.close()

        all_names = []
        for i in range(min_section, max_section+1):
            ser_trace_file = open(ser_prefix + '.' + str(i))
            ser_trace_data = ser_trace_file.read()

            all_names.extend( [ s.split('"')[0] for s in ser_trace_data.split('Contour name="')[1:] ] )

            ser_trace_file.close()

        contour_names = list(set(all_names))
        contour_names.sort()
        print(contour_names)


        return {'FINISHED'}        





# Begin here:


# Now you would put the item in this python list into a Blender collection property

# Done




