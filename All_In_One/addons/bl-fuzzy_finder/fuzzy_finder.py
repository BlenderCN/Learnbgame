import string
import difflib
import bpy


# Translate blender event.types to symbols they represent.
TRANSLATE = {
    'ZERO': '0',
    'ONE': '1',
    'TWO': '2',
    'THREE': '3',
    'FOUR': '4',
    'FIVE': '5',
    'SIX': '6',
    'SEVEN': '7',
    'EIGHT': '8',
    'NINE': '9',
    'SEMI_COLON': ';',
    'PERIOD': '.',
    'COMMA': ',',
    'QUOTE': '”',
    'ACCENT_GRAVE': '`',
    'MINUS': '-',
    'SLASH': '/',
    'BACK_SLASH': '\\',
    'EQUAL': '=',
    'LEFT_BRACKET': '[',
    'RIGHT_BRACKET': ']',
    'SPACE': ' ',
}


ALLOWED_INPUT = [letter for letter in string.ascii_uppercase] + \
                list(TRANSLATE.keys())


class FuzzyFinderSelect(bpy.types.Operator):
    bl_description = "Context sensitive search and select."
    bl_idname = "fuzzy_finder.select"
    bl_label = "Fuzzy Finder"
    bl_options = {"REGISTER", "UNDO"}

    # Names of the objects you can select. Based on current context area.
    names = []
    user_input = ""

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        if context.area.type == 'IMAGE_EDITOR':
            self.names = [i.name for i in bpy.data.images]
        elif context.area.type == 'TEXT_EDITOR':
            self.names = [t.name for t in bpy.data.texts]
        elif context.area.type == 'NODE_EDITOR':
            if context.area.spaces.active.tree_type == 'ShaderNodeTree':
                self.names = [m.name for m in bpy.data.materials]
            if context.area.spaces.active.tree_type == 'TextureNodeTree':
                self.names = [t.name for t in bpy.data.textures]
        else:
            # Default to VIEW_3D
            self.names = [o.name for o in bpy.data.objects]
        self.user_input = ""
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def select(self, context, event, name):
        """
        Process current input and select based on context.
        """
        context_type = context.area.type
        active_space = context.area.spaces.active
        try:
            if context_type == 'IMAGE_EDITOR':
                active_space.image = bpy.data.images[name]
            elif context_type == 'TEXT_EDITOR':
                context.area.spaces.active.text = bpy.data.texts[name]
            elif context_type == 'NODE_EDITOR':
                if active_space.tree_type == 'ShaderNodeTree':
                    active_space.node_tree = bpy.data.materials[name].node_tree
                if active_space.tree_type == 'TextureNodeTree':
                    active_space.node_tree = bpy.data.textures[name].node_tree
            else:
                # Default to VIEW_3D
                bpy.data.objects[name].select = True
                context.scene.objects.active = bpy.data.objects[name]
        except IndexError:
            pass  # No object with that name.

    def modal(self, context, event):
        self.user_input = process_input(self.user_input, event)

        fuzznames = fuzzy_find(self.user_input, self.names)

        # Header text
        context.area.header_text_set(format_output(fuzznames, self.user_input))

        # Exit on esc
        if event.type == 'ESC':
            context.area.header_text_set()
            return {'CANCELLED'}

        # End typing on enter
        if event.type == 'RET' and event.value == 'PRESS':
            context.area.header_text_set()
            if len(fuzznames) > 0:
                self.select(context, event, fuzznames[0])
            return {'FINISHED'}
        return {'RUNNING_MODAL'}


def process_input(current_input, event):
    """
    Check current event and return string of pressed key based on input.
    """
    if event.type == 'BACK_SPACE' and event.value == 'PRESS':
        current_input = current_input[:-1]
        return current_input

    if event.type in ALLOWED_INPUT and event.value == 'PRESS':
        inp = event.type
        if inp in TRANSLATE:
            inp = TRANSLATE[inp]
        if not event.shift:
            inp = inp.lower()
        return current_input + inp
    else:
        return current_input


def fuzzy_find(user_input, items):
    """Search for user_input in items and return closest find."""
    return difflib.get_close_matches(user_input,
                                     items,
                                     n=10,
                                     cutoff=0.01)


def format_output(names, user_input):
    """
    Create string that can be used on header using list of names and user input.
    """
    if len(names) > 0:
        output = "{}  :  {}  :  {}".format(names[0],
                                           names[1:],
                                           user_input)
    else:
        output = "    :  {}  :  {}".format(names[1:],
                                           user_input)
    return output


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
