import bpy
from console_python import add_scrollback, get_console

history_append = bpy.ops.console.history_append

def do_nodeview_theme():
    current_theme = bpy.context.user_preferences.themes.items()[0][0]
    node_editor = bpy.context.user_preferences.themes[current_theme].node_editor

    types = """\
        color_node
        converter_node
        distor_node
        filter_node
        frame_node
        gp_vertex
        gp_vertex_select
        gp_vertex_size
        group_node
        group_socket_node
        input_node
        layout_node
        matte_node
        node_active
        node_backdrop
        node_selected
        noodle_curving
        output_node
        pattern_node
        script_node
        selected_text
        shader_node
        texture_node
        vector_node
        wire
        wire_inner
        wire_select
    """

    current_theme = bpy.context.user_preferences.themes.items()[0][0]
    node_editor = bpy.context.user_preferences.themes[current_theme].node_editor

    settings = """\
color_node         0.894117,1.0,0.7882353
converter_node     0.9098039865493774,1.0,0.960784375667572
distor_node        0.4549019932746887,0.5921568870544434,0.5921568870544434
filter_node        0.6784313917160034,0.6039215922355652,0.7529412508010864
frame_node         1.0,1.0,1.0,0.501960813999176
gp_vertex          0.0,0.0,0.0
gp_vertex_select   1.0,0.5215686559677124,0.0
group_node         0.5411764979362488,0.6117647290229797,0.572549045085907
group_socket_node  0.874509871006012,0.7921569347381592,0.20784315466880798
input_node         1.0,1.0,1.0
layout_node        0.6784313917160034,0.6039215922355652,0.7529412508010864
matte_node         0.5921568870544434,0.4549019932746887,0.4549019932746887
node_active        1.0,0.6666666865348816,0.250980406999588
node_selected      0.9450981020927429,0.3450980484485626,0.0
output_node        1.0,1.0,1.0
pattern_node       0.6784313917160034,0.6039215922355652,0.7529412508010864
script_node        0.6784313917160034,0.6039215922355652,0.7529412508010864
selected_text      0.7019608020782471,0.6117647290229797,0.6117647290229797
shader_node        0.6392157077789307,0.9098039865493774,1.0
texture_node       0.2392157018184662,0.9764706492424011,1.0
vector_node        0.6784313917160034,0.6039215922355652,0.7529412508010864
wire               1.0,1.0,1.0
wire_inner         1.0,1.0,1.0
wire_select        1.0,0.46274513006210327,0.0
    """

    for configurable in settings.split('\n'):
        if not configurable.strip():
            continue
        print(configurable)
        attr_name, attr_value = configurable.split()
        attr_floats = [float(i) for i in attr_value.split(',')]
        setattr(node_editor, attr_name, attr_floats)

### These can be imported ---- below this line --------------------------

def set_nodewhite(context, m):
    current_theme = bpy.context.user_preferences.themes.items()[0][0]
    editor = bpy.context.user_preferences.themes[current_theme].node_editor
    editor.space.back = (1, 1, 1)


def set_3de(context, m):
    current_theme = bpy.context.user_preferences.themes.items()[0][0]
    editor = bpy.context.user_preferences.themes[current_theme].view_3d
    editor.grid = [0.533277, 0.533277, 0.533277]
    editor.space.gradients.show_grad = False
    editor.space.gradients.high_gradient = [0.701102, 0.701102, 0.701102]


def set_theme(context, m):
    history_append(text=m, remove_duplicates=True)
    add_scrollback('From the following list pick an index and type "theme_<idx>"', 'INFO')

    import os
    fullpath = bpy.app.binary_path
    directory = os.path.dirname(fullpath)
    num = str(bpy.app.version[0]) + '.' + str(bpy.app.version[1])
    fullext_path = (num + "/scripts/presets/interface_theme").split("/")
    seekable_path = os.path.join(directory, *fullext_path)

    def path_iterator(path_name, kind):
        for fp in os.listdir(path_name):
            if fp.endswith("." + kind):
                yield fp

    themes = list(path_iterator(seekable_path, 'xml'))
    if m.split('_')[1] == 'list':
        print(themes)
        for idx, line in enumerate(themes):
            add_scrollback('[{0}] - '.format(idx) + line[:-4], 'OUTPUT')
    elif m.split('_')[1].strip().isnumeric():
        idx = int(m.split('_')[1].strip())
        fullest_path = os.path.join(seekable_path, themes[idx])
        bpy.ops.script.execute_preset('INVOKE_DEFAULT', filepath=fullest_path, menu_idname="USERPREF_MT_interface_theme_presets")
    elif m.strip() == 'theme_flatty_light':
        fullest_path = os.path.join(seekable_path, "flatty_light.xml")
        bpy.ops.script.execute_preset('INVOKE_DEFAULT', filepath=fullest_path, menu_idname="USERPREF_MT_interface_theme_presets")        


