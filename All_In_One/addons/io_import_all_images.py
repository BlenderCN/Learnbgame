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

bl_info = {
    'name': 'Import: All Images',
    'description': 'Import All Images from Selected Directory including Image Sequences.',
    'author': 'Bartek Skorupa',
    'version': (0, 1),
    'blender': (2, 6, 9),
    'location': 'File > Import > All Images',
    'warning': "",
    'wiki_url': "",
    'tracker_url': "",
    'category': 'Import-Export',
    }
#directory = '/Volumes/PROJECTS/130901_Kinder_Niespodzianka_KINO_bilboard/AE_composite/(Footage)/video/050913_2/JASNE'
import bpy, os, sys, time
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
extensions = (
    '.jpg',
    '.JPG',
    '.jpeg',
    '.JPEG',
    '.png',
    '.PNG',
    '.tga',
    '.TGA',
    '.tif',
    '.TIF',
    '.tiff',
    '.TIFF',
    '.exr',
    '.EXR',
    )
def main(directory, context, add_to_compositor):
    if directory:
        print('\n\n\n\nImporting Images From Directory:')
        print(directory)
        scn = context.scene
        tree = scn.node_tree
        if tree:
            nodes = tree.nodes
            links = tree.links
        items = os.listdir(directory)
        files = [f for f in items if os.path.isfile(os.path.join(directory,f))]
        files.sort()
        print('Found ' + str(len(files)) + ' files in directory')
        print('\nSearching for sequences...')
        start = time.time()
        sequences = []
        sequence = []
        basename = ''
        frame = 0
        for file in files:
            full_filename = os.path.splitext(file)
            filename = full_filename[0]
            extension = full_filename[1]
            if extension in extensions:
                for i, char in enumerate(filename):
                    cur_basename = ''
                    cur_frame = 0
                    if filename[i:].isdigit():
                        cur_basename = filename[0:i-1]
                        cur_frame = int(filename[i:])
                        break
                if (cur_basename == basename and cur_frame == frame + 1):
                    frame += 1
                else:
                    if sequence:
                        sequences.append(sequence)
                    sequence = []
                    frame = cur_frame
                    basename = cur_basename
                sequence.append([file, cur_basename])
                if file == files[-1]:
                    sequences.append(sequence)
        if add_to_compositor and tree:
            locy = 0.0
            for n in nodes:
                n.select = False
        for seq in sequences:
            file = seq[0][0]
            label = seq[0][1]
            bpy.ops.image.open(filepath=os.path.join(directory, file))
            img = bpy.data.images[file]
            if len(seq) > 1:
                img.source = 'SEQUENCE'
            if add_to_compositor and tree:
                node = nodes.new('CompositorNodeImage')
                node.image = bpy.data.images[file]
                node.label = label
                node.location.y = locy
                locy -= 50.0
                node.hide = True
                node.width_hidden = 100.0
                node.show_preview = False
                nodes.active = node
                node.select = True
                if node.image.source == 'SEQUENCE':
                    node.frame_duration = 10000
                    node.use_auto_refresh = True
        end = time.time()
        print('\nFound ' + str(len(sequences)) + ' images or sequences.')
        print('Time elapsed: ' + str(end - start) + ' seconds.')
    
    return {'FINISHED'}


class ImportAllImages(bpy.types.Operator, ImportHelper):
    """Import all images from selected directory including image sequences."""
    bl_idname = "import.all_images"
    bl_label = "Import All Images"
    bl_options = {'REGISTER', 'UNDO'}
    directory = StringProperty(subtype="DIR_PATH")
    add_to_compositor = BoolProperty(
            name="Add Nodes",
            description="Add Image Input Nodes to Compositor",
            default=True,
            )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label('Set Up Compositing:')
        box.prop(self, 'add_to_compositor')

    def execute(self, context):
        return main(self.directory, context, self.add_to_compositor)

def menu_func(self, context):
    self.layout.operator(ImportAllImages.bl_idname, text="All Images")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()    