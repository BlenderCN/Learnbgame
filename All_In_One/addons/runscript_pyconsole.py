
# original script copied from
# http://www.blenderartists.org/forum/showthread.php?312821-Run-Script-in-PyConsole-%28Menu%29

bl_info = {
    "name": "Run Script in PyConsole",
    "author": "CoDEmanX, SAmbler",
    "version": (2, 0),
    "blender": (2, 80, 0),
    "location": "Python Console > Console > Run Script",
    "description": "Execute the code of a textblock or file within the python console.",
    "warning": "",
    "wiki_url": "https://github.com/sambler/myblendercontrib/blob/master/runscript_pyconsole.py",
    "tracker_url": "https://github.com/sambler/myblendercontrib/issues",
    "category": "Learnbgame",
    }

import bpy
import os

script_menu_items = {}

def clear_menu_items(self, context):
    script_menu_items = {}

def update_script_menu():
    prefs = bpy.context.preferences.addons[__name__].preferences
    if prefs.scripts_folder.startswith('//') or not prefs.scripts_folder.startswith('/'):
        folder = bpy.path.abspath(prefs.scripts_folder)
    else:
        folder = prefs.scripts_folder
    for root, dirs, files in os.walk(folder):
        for f in files:
            script_menu_items[os.path.join(root,f)] = { 'parent': root,
                                                        'display': f,
                                                        }

def load_script(s_path):
    for t in bpy.data.texts:
        if t.filepath == s_path:
            return t
    return None

def get_texts(context):
    l = []
    for area in context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            text = area.spaces[0].text
            if text is not None and text not in l:
                l.append(text)
    return {'visible': [t.name for t in l],
            'invisible': [t.name for t in bpy.data.texts if t not in l]}

def reload_script(txt, context):
    for area in context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            override = context.copy()
            override['area'] = area
            vis_text = area.spaces[0].text
            area.spaces[0].text = txt
            bpy.ops.text.reload(override)
            area.spaces[0].text = vis_text
            break

def main(self, context):
    text = bpy.data.texts.get(self.text)
    if text is not None:
        if text.is_modified:
            reload_script(text, context)
        text = "exec(compile(" + repr(text) + ".as_string(), '" + text.name + "', 'exec'))"
        bpy.ops.console.clear_line()
        bpy.ops.console.insert(text=text)
        bpy.ops.console.execute()

class RunScriptPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    scripts_folder = bpy.props.StringProperty(name="Scripts Folder",
                        description="Folder containing scripts to add to the menu.",
                        default='//scripts', update=clear_menu_items)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self,"scripts_folder")

class CONSOLE_OT_run_script(bpy.types.Operator):
    """Run a text datablock in PyConsole"""
    bl_idname = "console.run_code"
    bl_label = "Run script"

    text = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}

class CONSOLE_MT_run_script(bpy.types.Menu):
    bl_label = "Run script"
    bl_idname = "CONSOLE_MT_run_script"

    def draw(self, context):
        layout = self.layout
        texts = get_texts(context)
        visible, invisible = texts['visible'], texts['invisible']

        if not (visible or invisible):
            layout.label(text="No text blocks!")
        else:
            if invisible:
                for t in invisible:
                    layout.operator(CONSOLE_OT_run_script.bl_idname, text=t).text = t
            if visible and invisible:
                layout.separator()
            if visible:
                for t in visible:
                    layout.operator(CONSOLE_OT_run_script.bl_idname, text=t, icon='VISIBLE_IPO_ON').text = t

class CONSOLE_OT_load_script(bpy.types.Operator):
    """load and run a text file in PyConsole"""
    bl_idname = "console.run_code_file"
    bl_label = "Run script from file"

    filepath = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.area.type == 'CONSOLE'

    def execute(self, context):
        tb = load_script(self.filepath)
        if tb is None:
            tb = bpy.data.texts.load(self.filepath)
        bpy.ops.console.run_code(text=tb.name)
        return {'FINISHED'}

class CONSOLE_MT_load_script(bpy.types.Menu):
    bl_label = "Load and run script file"
    bl_idname = "CONSOLE_MT_run_script_file"

    def draw(self, context):
        layout = self.layout

        if  len(script_menu_items) == 0:
            update_script_menu()

        if  len(script_menu_items) == 0:
            layout.label("No scripts available!")
        else:
            kl = sorted(script_menu_items.keys())
            for k in kl:
                layout.operator(CONSOLE_OT_load_script.bl_idname,
                            text=script_menu_items[k]['display']).filepath = k

def draw_item_block(self, context):
    layout = self.layout
    layout.menu(CONSOLE_MT_run_script.bl_idname)

def draw_item_file(self, context):
    layout = self.layout
    layout.menu(CONSOLE_MT_load_script.bl_idname)

classes = (
    RunScriptPreferences,
    CONSOLE_OT_run_script,
    CONSOLE_MT_run_script,
    CONSOLE_OT_load_script,
    CONSOLE_MT_load_script,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.CONSOLE_MT_console.prepend(draw_item_block)
    bpy.types.CONSOLE_MT_console.prepend(draw_item_file)

def unregister():
    bpy.types.CONSOLE_MT_console.remove(draw_item_block)
    bpy.types.CONSOLE_MT_console.remove(draw_item_file)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
