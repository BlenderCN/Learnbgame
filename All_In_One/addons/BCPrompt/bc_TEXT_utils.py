import bpy


def detect_comments(lines):
    for line in lines:
        if len(line.strip()) == 0:
            # just spaces..
            continue
        elif line.strip().startswith("#"):
            # line starts with #
            continue
        else:
            return False
    return True


class TEXT_OT_do_comment(bpy.types.Operator):

    bl_idname = "text.do_comment"
    bl_label = "set or unset comment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        print(self, context)

        edit_text = bpy.context.edit_text
        strs = edit_text.as_string()

        wm = bpy.context.window_manager

        bpy.ops.text.copy()
        copied_text = wm.clipboard
        copied_lines = copied_text.split('\n')

        # are all lines essentially comments?
        comment_mode = detect_comments(copied_lines)

        if comment_mode:
            ''' lines are all comments '''
            pass

        else:
            ''' lines need to be commented '''
            # find least indent
            num_spaces = []
            for idx, l in enumerate(copied_lines):
                if '\t' in l:
                    print('mixing tabs..')
                    return {'FINISHED'}
                else:
                    g = l.lstrip()
                    indent_size = len(l) - len(g)
                    num_spaces.append(indent_size)

            min_space = min(num_spaces)
            print('minspace:', min_space)

            indent = ' ' * min_space
            for idx, l in enumerate(copied_lines):
                copied_lines[idx] = indent + "# " + l[min_space:]

            lines_to_paste = '\n'.join(copied_lines)
            wm.clipboard = lines_to_paste
            bpy.ops.text.paste()

        return {'FINISHED'}


class TEXT_Cycle_TextBlocks(bpy.types.Operator):

    bl_idname = "text.cycle_textblocks"
    bl_label = "switch text content of current viewer"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        edit_text = bpy.context.edit_text

        texts = bpy.data.texts
        num_texts = len(texts)

        def get_index_of_text(text_name):
            for idx, text in enumerate(texts):
                if text.name == text_name:
                    return idx

        current_idx = get_index_of_text(edit_text.name)
        new_idx = (current_idx + self.direction) % num_texts
        context.space_data.text = texts[new_idx]

        return {'FINISHED'}


class TEXT_Duplicate_Textblock(bpy.types.Operator):

    bl_idname = "text.duplicate_textblock"
    bl_label = "Duplicate Textblock"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        edit_text = bpy.context.edit_text
        texts = bpy.data.texts
        t = texts.new(name=edit_text.name + "_dupe")
        t.from_string(edit_text.as_string())
        context.space_data.text = t
        return {'FINISHED'}


classes = [TEXT_Duplicate_Textblock, TEXT_Cycle_TextBlocks, TEXT_OT_do_comment]
register, unregister = bpy.utils.register_classes_factory(classes)