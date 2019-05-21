"""
script_watcher.py: Reload watched script upon changes.

Copyright (C) 2015 Isaac Weaver
Author: Isaac Weaver <wisaac407@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

bl_info = {
    "name": "Script Watcher",
    "author": "Isaac Weaver",
    "version": (0, 6),
    "blender": (2, 75, 0),
    "location": "Properties > Scene > Script Watcher",
    "description": "Reloads an external script on edits.",
    "warning": "Still in beta stage.",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Development/Script_Watcher",
    "tracker_url": "https://github.com/wisaac407/blender-script-watcher/issues/new",
    "category": "Development",
}

import os, sys
import io
import traceback
import types
import console_python # Blender module giving us access to the blender python console.
import bpy
from bpy.app.handlers import persistent

@persistent
def load_handler(dummy):
    running = bpy.context.scene.sw_settings.running
    
    # First of all, make sure script watcher is off on all the scenes.
    for scene in bpy.data.scenes:
        bpy.ops.wm.sw_watch_end({'scene': scene})
    
    # Startup script watcher on the current scene if needed.
    if running and bpy.context.scene.sw_settings.auto_watch_on_startup:
        bpy.ops.wm.sw_watch_start()
        
    # Reset the consoles list to remove all the consoles that don't exist anymore.
    for screen in bpy.data.screens:
        screen.sw_consoles.clear()
    
def add_scrollback(ctx, text, text_type):
    for line in text:
        bpy.ops.console.scrollback_append(ctx, text=line.replace('\t', '    '), 
                                          type=text_type)

def get_console_id(area):
    """Return the console id of the given region."""
    if area.type == 'CONSOLE': # Only continue if we have a console area.
        for region in area.regions:
            if region.type == 'WINDOW':
                return hash(region) # The id is the hash of the window region.
    return False

def isnum(s):
    return s[1:].isnumeric() and s[0] in '-+1234567890'

class SplitIO(io.StringIO):
    """Feed the input stream into another stream."""
    PREFIX = '[Script Watcher]: '
    
    _can_prefix = True

    def __init__(self, stream):
        io.StringIO.__init__(self)
        
        self.stream = stream
        
    def write(self, s):
        # Make sure we prefix our string before we do anything else with it.
        if self._can_prefix:
            s = self.PREFIX + s
        # only add the prefix if the last stream ended with a newline.
        self._can_prefix = s.endswith('\n')
        
        # Make sure to call the super classes write method.
        io.StringIO.write(self, s)
        
        # When we are written to, we also write to the secondary stream.
        self.stream.write(s)

# Define the script watching operator.
class WatchScriptOperator(bpy.types.Operator):
    """Watches the script for changes, reloads the script if any changes occur."""
    bl_idname = "wm.sw_watch_start"
    bl_label = "Watch Script"

    _timer = None
    _running = False
    _times = None
    filepath = None
    
    def get_paths(self):
        """Find all the python paths surrounding the given filepath."""
        
        dirname = os.path.dirname(self.filepath)
        
        paths = []
        filepaths = []
        
        for root, dirs, files in os.walk(dirname, topdown=True):
            if '__init__.py' in files:
                paths.append(root)
                for f in files:
                    filepaths.append(os.path.join(root, f))
            else:
                dirs[:] = [] # No __init__ so we stop walking this dir.
        
        # If we just have one (non __init__) file then return just that file.
        return paths, filepaths or [self.filepath]

    def get_mod_name(self):
        """Return the module name and the root path of the givin python file path."""
        dir, mod = os.path.split(self.filepath)
        
        # Module is a package.
        if mod == '__init__.py':
            mod = os.path.basename(dir)
            dir = os.path.dirname(dir)
        
        # Module is a single file.
        else:
            mod = os.path.splitext(mod)[0]
        
        return mod, dir
    
    def remove_cached_mods(self):
        """Remove all the script modules from the system cache."""
        paths, files = self.get_paths()
        for mod_name, mod in list(sys.modules.items()):
            if hasattr(mod, '__file__') and os.path.dirname(mod.__file__) in paths:
                del sys.modules[mod_name]

    def _reload_script_module(self):
        print('Reloading script:', self.filepath)
        self.remove_cached_mods()
        try:
            f = open(self.filepath)
            paths, files = self.get_paths()
            
            # Get the module name and the root module path.
            mod_name, mod_root = self.get_mod_name()
            
            # Create the module and setup the basic properties.
            mod = types.ModuleType('__main__')
            mod.__file__ = self.filepath
            mod.__path__ = paths
            mod.__package__ = mod_name
            
            # Add the module to the system module cache.
            sys.modules[mod_name] = mod
            
            # Fianally, execute the module.
            exec(compile(f.read(), self.filepath, 'exec'), mod.__dict__)
        except IOError:
            print('Could not open script file.')
        except:
            sys.stderr.write("There was an error when running the script:\n" + traceback.format_exc())
        else:
            f.close()
            
    def reload_script(self, context):
        """Reload this script while printing the output to blenders python console."""
        
        # Setup stdout and stderr.
        stdout = SplitIO(sys.stdout)
        stderr = SplitIO(sys.stderr)
        
        sys.stdout = stdout
        sys.stderr = stderr
        
        # Run the script.
        self._reload_script_module()
        
        # Go back to the begining so we can read the streams.
        stdout.seek(0)
        stderr.seek(0)
        
        # Don't use readlines because that leaves trailing new lines.
        output = stdout.read().split('\n')
        output_err = stderr.read().split('\n')
        
        for console in context.screen.sw_consoles:
            if console.active and isnum(console.name): # Make sure it's not some random string.

                console, _, _ = console_python.get_console(int(console.name))

                # Set the locals to the modules dict.
                console.locals = sys.modules[self.get_mod_name()[0]].__dict__
        
        if self.use_py_console:
            # Print the output to the consoles.
            for area in context.screen.areas:
                if area.type == "CONSOLE":
                    ctx = context.copy()
                    ctx.update({"area": area})
                    
                    # Actually print the output.
                    if output:
                        add_scrollback(ctx, output, 'OUTPUT')
                        
                    if output_err:
                        add_scrollback(ctx, output_err, 'ERROR')
        
        # Cleanup
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__        

    def modal(self, context, event):
        if not context.scene.sw_settings.running:
            self.cancel(context)
            return {'CANCELLED'}

        if context.scene.sw_settings.reload:
            context.scene.sw_settings.reload = False
            self.reload_script(context)
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            for path in self._times:
                cur_time = os.stat(path).st_mtime
                
                if cur_time != self._times[path]:
                    self._times[path] = cur_time
                    self.reload_script(context)

        return {'PASS_THROUGH'}

    def execute(self, context):
        if context.scene.sw_settings.running:
            return {'CANCELLED'}
        
        # Grab the settings and store them as local variables.
        self.filepath = bpy.path.abspath(context.scene.sw_settings.filepath)
        self.use_py_console = context.scene.sw_settings.use_py_console
        
        # If it's not a file, doesn't exist or permistion is denied we don't preceed.
        if not os.path.isfile(self.filepath):
            self.report({'ERROR'}, 'Unable to open script.')
            return {'CANCELLED'}
        
        # Setup the times dict to keep track of when all the files where last edited.
        dirs, files = self.get_paths()
        self._times = dict((path, os.stat(path).st_mtime) for path in files) # Where we store the times of all the paths.
        self._times[files[0]] = 0  # We set one of the times to 0 so the script will be loaded on startup.
        
        # Setup the event timer.
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        
        context.scene.sw_settings.running = True
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        self.remove_cached_mods()

        context.scene.sw_settings.running = False


class CancelScriptWatcher(bpy.types.Operator):
    """Stop watching the current script."""
    bl_idname = "wm.sw_watch_end"
    bl_label = "Stop Watching"

    def execute(self, context):
        # Setting the running flag to false will cause the modal to cancel itself.
        context.scene.sw_settings.running = False
        return {'FINISHED'}


class ReloadScriptWatcher(bpy.types.Operator):
    """Reload the current script."""
    bl_idname = "wm.sw_reload"
    bl_label = "Reload Script"

    def execute(self, context):
        # Setting the reload flag to true will cause the modal to cancel itself.
        context.scene.sw_settings.reload = True
        return {'FINISHED'}


# Create the UI for the operator. NEEDS FINISHING!!
class ScriptWatcherPanel(bpy.types.Panel):
    """UI for the script watcher."""
    bl_label = "Script Watcher"
    bl_idname = "SCENE_PT_script_watcher"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        running = context.scene.sw_settings.running

        col = layout.column()
        col.prop(context.scene.sw_settings, 'filepath')
        col.prop(context.scene.sw_settings, 'use_py_console')
        col.prop(context.scene.sw_settings, 'auto_watch_on_startup')
        col.operator('wm.sw_watch_start', icon='VISIBLE_IPO_ON')
        col.enabled = not running
        if running:
            row = layout.row(align=True)
            row.operator('wm.sw_watch_end', icon='CANCEL')
            row.operator('wm.sw_reload', icon='FILE_REFRESH')


class ScriptWatcherSettings(bpy.types.PropertyGroup):
    """All the script watcher settings."""
    running = bpy.props.BoolProperty(default=False)
    reload = bpy.props.BoolProperty(default=False)
    
    filepath = bpy.props.StringProperty(
        name        = 'Script',
        description = 'Script file to watch for changes.',
        subtype     = 'FILE_PATH'
    )
    
    use_py_console = bpy.props.BoolProperty(
        name        = 'Use py console',
        description = 'Use blenders built-in python console for program output (e.g. print statments and error messages)',
        default     = False
    )
    
    auto_watch_on_startup = bpy.props.BoolProperty(
        name        = 'Watch on startup',
        description = 'Watch script automatically on new .blend load',
        default     = False
    )


def update_debug(self, context):
    console_id = get_console_id(context.area)
    
    console, _, _ = console_python.get_console(console_id)
    
    if self.active:
        console.globals = console.locals
        
        if context.scene.sw_settings.running:
            dir, mod = os.path.split(bpy.path.abspath(context.scene.sw_settings.filepath))
        
            # XXX This is almost the same as get_mod_name so it should become a global function.
            if mod == '__init__.py':
                mod = os.path.basename(dir)
            else:
                mod = os.path.splitext(mod)[0]
        
            console.locals = sys.modules[mod].__dict__
        
    else:
        console.locals = console.globals
    
    #ctx = context.copy() # Operators only take dicts.
    #bpy.ops.console.update_console(ctx, debug_mode=self.active, script='test-script.py')


class SWConsoleSettings(bpy.types.PropertyGroup):
    active = bpy.props.BoolProperty(
        name        = "Debug Mode",
        update      = update_debug,
        description = "Enter Script Watcher debugging mode (when in debug mode you can access the script variables).",
        default     = False
    )


class SWConsoleHeader(bpy.types.Header):
    bl_space_type = 'CONSOLE'
    
    def draw(self, context):
        layout = self.layout
        
        cs = context.screen.sw_consoles
        
        console_id = str(get_console_id(context.area))
        
        # Make sure this console is in the consoles collection.
        if console_id not in cs:
            console = cs.add()
            console.name = console_id

        row = layout.row()
        row.scale_x = 1.8
        row.prop(cs[console_id], 'active', toggle=True)


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.sw_settings = \
        bpy.props.PointerProperty(type=ScriptWatcherSettings)
    
    bpy.app.handlers.load_post.append(load_handler)
    
    bpy.types.Screen.sw_consoles = bpy.props.CollectionProperty(
        type   = SWConsoleSettings
    )


def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.app.handlers.load_post.remove(load_handler)


    del bpy.types.Scene.sw_settings
    
    del bpy.types.Screen.sw_consoles


if __name__ == "__main__":
    register()
