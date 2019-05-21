'''
Simple Export
-- A simple export add-on for blender
Copyright (C) 2011  Joar Wandborg

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import random

from bpy_extras.io_utils import ExportHelper

"""
Add-on info, used by the blender add-on manager

 - bl_info documentation:
   http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Guidelines/Addons
"""

bl_info = {
    "name": "Simple exporter",
    "description": "A very basic export plugin for blender",
    "author": "Joar Wandborg",
    "version": (1, 0),
    "blender": (2, 5, 8),
    "api": 31236,
    "location": "File > Export",
    "warning": '',
    "wiki_url": "https://github.com/jwandborg/blender-simpleexport",
    "tracker_url": "https://github.com/jwandborg/blender-simpleexport/issues",
    "category": "Learnbgame"
}


class SimpleExport(bpy.types.Operator, ExportHelper):
    bl_idname = 'simpleexport.txt'
    bl_label = 'Simple Export (.txt)'

    filename_ext = '.txt'

    def execute(self, context):
        """
        blender callback hook
        """
        self.filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
        print(self.filepath)

        exported = self.main(context)
        if exported:
            print('Finished export')

        return {'FINISHED'}

    def invoke(self, context, event):
        """
        blender add-on callback hook

        This logic might look weird, but according to limited research it might
        be vital for the IO functions of an add-on

         - wm.fileselect_add(self)
           Probably triggers the fileselect window in blender, will run
           ``self.execute``
         - wm.invoke_search_popup(self)
           "search the enum"
         - wm.invoke_props_popup(self, event)
           "Redo popup"
         - self.execute(self)
        """
        wm = context.window_manager

        if True:
            wm.fileselect_add(self)
            return {'RUNNING_MODAL'}
        elif True:
            wm.invoke_search_popup(self)
            return {'RUNNING_MODAL'}
        elif False:
            return wm.invoke_props_popup(self, event)
        elif False:
            return self.execute(context)

    def main(self, context):
        """
        This is the worker function where we get all the data and output it
        """
        print(context)
        print(self.filepath)

        fd = open(self.filepath, 'w')

        greetings = [
            'Hi,',
            'Yo!',
            'Wazzup,',
            'Hey!',
            'Greetings!']

        self_descriptions = [
            'I\'m {0}',
            'my name is {0}',
            'I go by the name of {0}',
            '{0} here']

        """
        Fetch data from blender, just like you do in
        the blender "Python Console", and output it to a file
        """
        for name, i in bpy.data.objects.items():
            object_output = '{greeting} {self_description}!\n'.format(
                greeting=random.choice(greetings),
                self_description=random.choice(self_descriptions).format(
                    name))
            fd.write(
                object_output)

        return


def menu_func(self, context):
    """
    Invoked by ``register()`` and adds the export menu menu item
    """
    self.layout.operator(SimpleExport.bl_idname, text='Simple export (.txt)')


"""
blender add-on hook implementations
"""


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)


if __name__ == '__main__':
    register()
