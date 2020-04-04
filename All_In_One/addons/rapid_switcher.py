import bpy
import re
from bpy.props import IntProperty, BoolProperty, StringProperty, CollectionProperty, EnumProperty
from bpy.types import Panel, UIList
import rna_keymap_ui


############################
#CODE STRUCTURE
############################
#Core Keys and Dictionaries
#---------------------------
#Core Functions
#---------------------------
#Setting Ops
#---------------------------
#Hotkey Ops
#---------------------------
#GUI
#---------------------------
#Pie Menu
#---------------------------
#Keymap Props
#---------------------------
#Addon Preferences
#---------------------------
#Property Groups
#---------------------------
#Register and Unregister
############################


bl_info = {
    "name": "Rapid Switcher",
    "description": "Switching windows by shortcut keys",
    "author": "Kozo Oeda",
    "version": (1, 9),
    "blender": (2, 78, 0),
    "location": "",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


##############################
# Core Keys and Dictionaries #
##############################


def setup_keys():
    return [ 
    ['3D View', 'VIEW_3D', 0, False],
    ['Timeline', 'TIMELINE', 1, False],
    ['Graph Editor', 'GRAPH_EDITOR', 2, False],
    ['Dope Sheet', 'DOPESHEET_EDITOR', 3, False],
    ['NLA Editor', 'NLA_EDITOR', 4, False],
    ['UV/Image Editor', 'IMAGE_EDITOR', 5, False],
    ['Video Sequence Editor', 'SEQUENCE_EDITOR', 6, False],
    ['Movie Clip Editor', 'CLIP_EDITOR', 7, False],
    ['Text Editor', 'TEXT_EDITOR', 8, False],
    ['Node Editor', 'NODE_EDITOR', 9, False],
    ['Logic Editor', 'LOGIC_EDITOR', 10, False],
    #['Properties', 'PROPERTIES', -1, False], #
    ['Outliner', 'OUTLINER', 11, False],
    #['User Preferences', 'USER_PREFERENCES', -1, False], #
    ['Info', 'INFO', 12, False],
    #['File Browser', 'FILE_BROWSER', -1, False], #
    ['Python Console','CONSOLE', 13, False]
    ],[
    ['3D View'], #destinations area
    ['Timeline'], 
    ['Graph Editor'], 
    ['Dope Sheet'], 
    ['NLA Editor'], 
    ['UV/Image Editor'], 
    ['Video Sequence Editor'],
    ['Movie Clip Editor'], 
    ['Text Editor'], 
    ['Node Editor'], 
    ['Logic Editor'], 
    #['Properties'], #
    ['Outliner'], 
    #['User Preferences'], # 
    ['Info'], 
    #['File Browser'],  #
    ['Python Console'] 
    ] 


indexes = len(setup_keys()[0])


consistency_dic = {
                '3D View': 'VIEW_3D',	
                'Timeline': 'TIMELINE',
                'Graph Editor': 'GRAPH_EDITOR',
                'Dope Sheet': 'DOPESHEET_EDITOR',
                'NLA Editor': 'NLA_EDITOR',
                'UV/Image Editor': 'IMAGE_EDITOR',
                'Video Sequence Editor': 'SEQUENCE_EDITOR',
                'Movie Clip Editor': 'CLIP_EDITOR',
                'Text Editor': 'TEXT_EDITOR',
                'Node Editor': 'NODE_EDITOR',
                'Logic Editor': 'LOGIC_EDITOR',
                #'Properties' : 'PROPERTIES', #
                'Outliner': 'OUTLINER',
                #'User Preferences' : 'USER_PREFERENCES', #
                'Info': 'INFO',
                #'File Browser' : 'FILE_BROWSER', #
                'Python Console': 'CONSOLE'
                }


icon_dic = {
	'VIEW_3D': 'MATCUBE',
	'TIMELINE': 'TIME',
	'GRAPH_EDITOR': 'IPO',
	'DOPESHEET_EDITOR': 'ACTION',
	'NLA_EDITOR': 'NLA',
	'IMAGE_EDITOR': 'IMAGE_COL',
	'SEQUENCE_EDITOR': 'SEQUENCE',
	'CLIP_EDITOR': 'RENDER_ANIMATION',
	'TEXT_EDITOR': 'TEXT',
	'NODE_EDITOR': 'NODETREE',
	'LOGIC_EDITOR': 'LOGIC',
	'PROPERTIES': 'UI',
	'OUTLINER': 'OOPS',
	'USER_PREFERENCES': 'PREFERENCES',
	'INFO': 'INFO',
	'FILE_BROWSER': 'FILESEL',
	'CONSOLE': 'CONSOLE',
	}


name_dic = {
	'VIEW_3D': '3D View',
	'TIMELINE': 'Timeline',
	'GRAPH_EDITOR': 'Graph Editor',
	'DOPESHEET_EDITOR': 'Dope Sheet',
	'NLA_EDITOR': 'NLA Editor',
	'IMAGE_EDITOR': 'UV/Image Editor',
	'SEQUENCE_EDITOR': 'Video Sequence Editor',
	'CLIP_EDITOR': 'Movie Clip Editor',
	'TEXT_EDITOR': 'Text Editor',
	'NODE_EDITOR': 'Node Editor',
	'LOGIC_EDITOR': 'Logic Editor',
	'PROPERTIES': 'Properties',
	'OUTLINER': 'Outliner',
	'USER_PREFERENCES': 'User Preferences',
	'INFO': 'Info',
	'FILE_BROWSER': 'File Browser',
	'CONSOLE': 'Python Console',
	}


##################
# Core Functions #
##################


def init(scene, item, indexes):
    if len(item) == indexes:
        return {'FINISHED'}
    else:
        ini, dst = setup_keys()
        ini, dst = sort_all(ini, dst)
        for i in range(indexes):
            item = scene.rpd_swt_window_properties.add()
            item.name = ini[i][0]
            item.id = ini[i][1]
            item.order = ini[i][2]
            item.rpd_swt_checker = ini[i][3]
            item.dst_name = dst[i][0]
            item.dst_id = consistency_dic[dst[i][0]]
        bpy.context.scene.rpd_swt_tmp_id = 'INVALID'


def init_screen(scene, item, indexes):
    indexes = len(bpy.data.screens)
    if len(item) == indexes:
        return {'FINISHED'}
    else:
        for i in range(indexes):
            item = scene.rpd_swt_screen_properties.add()
            item.name = bpy.data.screens[i].name


def sort_all(ini, dst):
    for i in range(indexes):
        dst[i].append(ini[i][2])
    new_ini = sorted(ini, key = lambda components: components[2])
    new_dst = sorted(dst, key = lambda components: components[1])
    return new_ini, new_dst


def swap_item(origin, target):
    origin.name, target.name = target.name, origin.name
    origin.id, target.id = target.id, origin.id
    origin.rpd_swt_checker, target.rpd_swt_checker = target.rpd_swt_checker, origin.rpd_swt_checker
    origin.dst_name, target.dst_name = target.dst_name, origin.dst_name
    origin.dst_id, target.dst_id = target.dst_id, origin.dst_id
	

def swap_up():
    rpd_swt_selected_index = bpy.context.scene.rpd_swt_selected_index
    if rpd_swt_selected_index > 0:
        swap_item(bpy.context.scene.rpd_swt_window_properties[rpd_swt_selected_index], bpy.context.scene.rpd_swt_window_properties[rpd_swt_selected_index - 1])
        bpy.context.scene.rpd_swt_selected_index -= 1 
		

def swap_down(indexes):
    rpd_swt_selected_index = bpy.context.scene.rpd_swt_selected_index
    if rpd_swt_selected_index < indexes - 1:
        swap_item(bpy.context.scene.rpd_swt_window_properties[rpd_swt_selected_index], bpy.context.scene.rpd_swt_window_properties[rpd_swt_selected_index + 1])
        bpy.context.scene.rpd_swt_selected_index += 1


def change_all(windows, indexes):
    rpd_swt_bool_pool = bpy.context.scene.rpd_swt_bool_pool
    for i in range(indexes):
        if windows[i].rpd_swt_checker == rpd_swt_bool_pool:
            windows[i].rpd_swt_checker = not rpd_swt_bool_pool
    bpy.context.scene.rpd_swt_bool_pool = not rpd_swt_bool_pool
		

def get_current_order(windows):
    for i in range(indexes):
        if bpy.context.area.type == windows[i].id:
            return windows[i].order


def get_rpd_swt_checker(windows, order):
    return windows[order].rpd_swt_checker


def switch_up_window(windows, indexes):
    current = (get_current_order(windows) - 1) % indexes
    for i in range(indexes):
        if get_rpd_swt_checker(windows, current) != True:
            current = (current - 1) % indexes
        else:
            bpy.context.area.type = windows[current].id


def switch_down_window(windows, indexes):
    current = (get_current_order(windows) + 1) % indexes
    for i in range(indexes):
        if get_rpd_swt_checker(windows, current) != True:	
            current = (current + 1) % indexes
        else:
            bpy.context.area.type = windows[current].id


tmp_dst = []


def shortcut_course(windows):
    current = get_current_order(windows)		
    if windows[current].dst_id != bpy.context.area.type:
        tmp_dst.append(bpy.context.area.type)
    
    if windows[current].dst_id != 'INVALID':
        bpy.context.area.type = windows[current].dst_id


def shortcut_course_back():
    if tmp_dst and tmp_dst[-1] != 'INVALID':
        bpy.context.area.type = tmp_dst[-1]
        tmp_dst.pop()


def get_current_screen():
    return bpy.context.screen.name


def get_current_screen_nu():
    for i in range(len(bpy.data.screens)):
        name = get_current_screen()
        if name == bpy.data.screens[i].name:
            return i


def screen_up():
    current = get_current_screen_nu()
    for i in range(len(bpy.data.screens)):
        current -= 1
        current = current % len(bpy.data.screens)
        if bpy.data.screens[current].rpd_swt_checker == True:
            bpy.context.window.screen = bpy.data.screens[current]
            return


def screen_down():
    current = get_current_screen_nu()
    for i in range(len(bpy.data.screens)):
        current += 1
        current = current % len(bpy.data.screens)
        if bpy.data.screens[current].rpd_swt_checker == True:
            bpy.context.window.screen = bpy.data.screens[current]
            return


def make_pattern():
    original_name = bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_name
    sign = '(?i)'
    return sign + original_name

			
def check_consistency():
    pattern = make_pattern()
    if len(bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_name) == 0:
        bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_name = "Invalid"
        bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_id = 'INVALID'
        return 	
    for key in consistency_dic:
        if re.match(pattern, key):
            bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_name = key
            bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_id = consistency_dic[key]
        elif bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_name not in consistency_dic:
            bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_name = "Invalid"
            bpy.context.scene.rpd_swt_window_properties[bpy.context.scene.rpd_swt_selected_index].dst_id = 'INVALID'


###############
# Setting Ops #
###############


class WindowOps(bpy.types.Operator):
    bl_idname = "rpd_swt_window_properties.operations"
    bl_label = "Window Ops"
    bl_options = {'INTERNAL'}

    operation = bpy.props.EnumProperty(
        items = (
                ('INIT', "Init", ""),	
                ('SWAPUP', "Swap Up", ""), 
                ('SWAPDOWN', "Swap Down", ""),
                ('ALL', "All", ""),
                ('SWITCHUP', "Switch Window up", ""),
                ('SWITCHDOWN', "Switch Window down", ""),
                ('SHORTRUN', "Shortcut Course", ""),
                ('SHORTRUNBACK', "Back Shortcut Course", ""),
                ('SCREENUP', "Change a Screen in an Upper Directin", ""),
                ('SCREENDOWN', "Change a Screen in an Downer Direction", "")
        )	
    )
    def execute(self, context):

        scene = context.scene

        index = scene.rpd_swt_selected_index
        item = scene.rpd_swt_window_properties

        index_screen = scene.rpd_swt_screen_selected_index
        item_screen = scene.rpd_swt_screen_properties

        try:
            if self.operation == 'INIT':
                indexes_screen = len(bpy.data.screens)
                init(scene, item, indexes)
                init_screen(scene, item_screen, indexes_screen)

            elif self.operation == 'SWAPUP':
                swap_up()

            elif self.operation == 'SWAPDOWN':
                swap_down(indexes)

            elif self.operation == 'ALL':
                change_all(item, indexes)

            elif self.operation == 'SWITCHUP':
                switch_up_window(item, indexes)

            elif self.operation == 'SWITCHDOWN':
                switch_down_window(item, indexes)

            elif self.operation == 'SHORTRUN':
                shortcut_course(item)

            elif self.operation == 'SHORTRUNBACK':
                shortcut_course_back()

            elif self.operation == 'SCREENUP':
                screen_up()

            elif self.operation == 'SCREENDOWN':
                screen_down()

        except IndexError:
            pass
                
        return {'FINISHED'}


##############
# Hotkey Ops # 
##############


class KeySwitchUp(bpy.types.Operator):
    bl_idname = "rpd_swt_window_properties.k_switch_up"
    bl_label = "Short Cut for Switch Up"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.rpd_swt_window_properties.operations(operation = 'SWITCHUP')
        return {'FINISHED'}


class KeySwitchDown(bpy.types.Operator):
    bl_idname = "rpd_swt_window_properties.k_switch_down"
    bl_label = "Short Cut for Switch Down"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.rpd_swt_window_properties.operations(operation = 'SWITCHDOWN')
        return {'FINISHED'}


class KeyShortRunner(bpy.types.Operator):
    bl_idname = "rpd_swt_window_properties.k_short_runner"
    bl_label = "Short Cut for Short Runner"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.rpd_swt_window_properties.operations(operation = 'SHORTRUN')
        return {'FINISHED'}


class KeyShortRunnerBack(bpy.types.Operator):
    bl_idname = "rpd_swt_window_properties.k_short_runner_back"
    bl_label = "Short Cut for Shor Runner Back Version"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.rpd_swt_window_properties.operations(operation = 'SHORTRUNBACK')
        return {'FINISHED'}


class KeyScreenUp(bpy.types.Operator):
    bl_idname = "rpd_swt_window_properties.k_screen_up"
    bl_label = "Screen Up"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.rpd_swt_window_properties.operations(operation = 'SCREENUP')
        return {'FINISHED'}


class KeyScreenDown(bpy.types.Operator):
    bl_idname = "rpd_swt_window_properties.k_screen_down"
    bl_label = "Screen Down"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.rpd_swt_window_properties.operations(operation = 'SCREENDOWN')
        return {'FINISHED'}


#######
# GUI #
#######


def clicker(window_property):
    if window_property.rpd_swt_checker == True:
        return 'RADIOBUT_ON'
    else:
        return 'RADIOBUT_OFF'


def show_icon(area_id): 
    if area_id in icon_dic:
        return icon_dic[area_id] 


class ListComponents(bpy.types.UIList):
	
    def draw_item(self, context, layout, data, item, icon, index):
        split = layout.split(0)
        split.prop(item, "name", text = "", emboss = False, translate = False, icon = show_icon(item.id)) 
        split.prop(item, "rpd_swt_checker", text = "", emboss = False, translate = False, icon = clicker(item))


class ShortRunComponents(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, index):
        split = layout.split(0)
        split.prop(item, "name", text = "", emboss = False, translate = False, icon = show_icon(item.id))
        split.prop(item, "dummy", text = "", emboss = False, translate = False, icon = 'RIGHTARROW_THIN')
        split.prop(item, "dst_name", text = "", emboss = False, translate = False, icon = 'NONE')


class ScreenSwitcherComponents(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, index):
        split = layout.split(0)
        split.prop(item, "name", text = "", emboss = False, translate = False, icon = 'NONE')
        split.prop(item, "rpd_swt_checker", text = "", emboss = False, translate = False, icon = clicker(item))


class QuickSwitcher(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'VIEW_3D_PT_quick_switcher'
    bl_label = "Quick Switcher"
    bl_category = "Rapid Switcher"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        row = layout.row()
        row.template_list("ListComponents", "", scene, "rpd_swt_window_properties", scene, "rpd_swt_selected_index", rows = indexes)

        col = row.column(align = True)
        col.operator("rpd_swt_window_properties.operations", icon = 'TRIA_UP', text = "").operation = 'SWAPUP'
        col.operator("rpd_swt_window_properties.operations", icon = 'TRIA_DOWN', text = "").operation = 'SWAPDOWN'
        col.operator("rpd_swt_window_properties.operations", icon = 'FILE_REFRESH', text = "").operation = 'ALL'
        col.separator()
        col.operator("rpd_swt_window_properties.operations", icon = 'QUIT', text = "").operation = 'INIT'


class ShortRunner(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'VIEW_3D_PT_short_cut'
    bl_label = "Short Runner"
    bl_category = "Rapid Switcher"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        row = layout.row()
        row.template_list("ShortRunComponents", "", scene, "rpd_swt_window_properties", scene, "rpd_swt_selected_index", rows = indexes)
        try:
            check_consistency()
        except IndexError:
            pass


class ScreenSwitcher(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'VIEW_3D_PT_screen_switcher'
    bl_label = 'Screen Switcher'
    bl_category = "Rapid Switcher"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        data = bpy.data

        row = layout.row()
        row.template_list("ScreenSwitcherComponents", "", data, "screens", scene, "rpd_swt_screen_selected_index", rows = len(bpy.data.screens))
        

############
# Pie Menu #
############


def get_area_name(area_id): 
    if area_id in name_dic:
        return name_dic[area_id] 


class SwitchAreaOps(bpy.types.Operator):
    bl_idname = "ops.switch_area_ops"
    bl_label = "Switch Area Via Pie Menu"

    area = bpy.props.StringProperty()

    def execute(self, context):
        if self.area != 'NONE':
            bpy.context.area.type = self.area
        return {'FINISHED'}
        

class SwitchAreaPie(bpy.types.Menu):
    bl_idname = "SwitchAreaPie"
    bl_label = "Switch Area Pie"

    def draw(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        north = addon_prefs.pie_north
        north_east = addon_prefs.pie_north_east
        east = addon_prefs.pie_east
        south_east = addon_prefs.pie_south_east
        south = addon_prefs.pie_south
        south_west = addon_prefs.pie_south_west
        west = addon_prefs.pie_west
        north_west = addon_prefs.pie_north_west

        north_sub = addon_prefs.pie_north_sub
        north_east_sub = addon_prefs.pie_north_east_sub
        east_sub = addon_prefs.pie_east_sub
        south_east_sub = addon_prefs.pie_south_east_sub
        south_sub = addon_prefs.pie_south_sub
        south_west_sub = addon_prefs.pie_south_west_sub
        west_sub = addon_prefs.pie_west_sub
        north_west_sub = addon_prefs.pie_north_west_sub

        layout = self.layout
        pie = layout.menu_pie()

        #West
        if west_sub != 'NONE':
            col = pie.column()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(west), icon = show_icon(west))
            props.area = west 
            col.separator()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(west_sub), icon = show_icon(west_sub))
            props.area = west_sub
        else:
            props = pie.operator(SwitchAreaOps.bl_idname, text = get_area_name(west), icon = show_icon(west))
            props.area = west 

        #East
        if east_sub != 'NONE':
            col = pie.column()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(east), icon = show_icon(east))
            props.area = east
            col.separator()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(east_sub), icon = show_icon(east_sub))
            props.area = east_sub
        else:
            props = pie.operator(SwitchAreaOps.bl_idname, text = get_area_name(east), icon = show_icon(east))
            props.area = east 

        #South
        if south_sub != 'NONE':
            row = pie.row()
            props = row.operator(SwitchAreaOps.bl_idname, text = get_area_name(south), icon = show_icon(south))
            props.area = south 
            props = row.operator(SwitchAreaOps.bl_idname, text = get_area_name(south_sub), icon = show_icon(south_sub))
            props.area = south_sub 
        else:
            props = pie.operator(SwitchAreaOps.bl_idname, text = get_area_name(south), icon = show_icon(south))
            props.area = south 

        #North
        if north_sub != 'NONE':
            row = pie.row()
            props = row.operator(SwitchAreaOps.bl_idname, text = get_area_name(north), icon = show_icon(north))
            props.area = north 
            props = row.operator(SwitchAreaOps.bl_idname, text = get_area_name(north_sub), icon = show_icon(north_sub))
            props.area = north_sub 
        else:
            props = pie.operator(SwitchAreaOps.bl_idname, text = get_area_name(north), icon = show_icon(north))
            props.area = north 

        #North West
        if north_west_sub != 'NONE':
            col = pie.column()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(north_west), icon = show_icon(north_west))
            props.area = north_west 
            col.separator()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(north_west_sub), icon = show_icon(north_west_sub))
            props.area = north_west_sub 
        else:
            props = pie.operator(SwitchAreaOps.bl_idname, text = get_area_name(north_west), icon = show_icon(north_west))
            props.area = north_west 

        #North East
        if north_east_sub != 'NONE':
            col = pie.column()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(north_east), icon = show_icon(north_east))
            props.area = north_east 
            col.separator()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(north_east_sub), icon = show_icon(north_east_sub))
            props.area = north_east_sub 
        else:
            props = pie.operator(SwitchAreaOps.bl_idname, text = get_area_name(north_east), icon = show_icon(north_east))
            props.area = north_east

        #South West
        if south_west_sub != 'NONE':
            col = pie.column()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(south_west), icon = show_icon(south_west))
            props.area = south_west 
            col.separator()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(south_west_sub), icon = show_icon(south_west_sub))
            props.area = south_west_sub 
        else:
            props = pie.operator(SwitchAreaOps.bl_idname, text = get_area_name(south_west), icon = show_icon(south_west))
            props.area = south_west 

        #South East
        if south_east_sub != 'NONE':
            col = pie.column()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(south_east), icon = show_icon(south_east))
            props.area = south_east 
            col.separator()
            props = col.operator(SwitchAreaOps.bl_idname, text = get_area_name(south_east_sub), icon = show_icon(south_east_sub))
            props.area = south_east_sub 
        else:
            props = pie.operator(SwitchAreaOps.bl_idname, text = get_area_name(south_east), icon = show_icon(south_east))
            props.area = south_east 


class SwitchAreaPieTrigger(bpy.types.Operator):
    bl_idname = 'wm.switch_area_pie_trigger'
    bl_label = "Pie Trigger"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name = 'SwitchAreaPie')
        return {'FINISHED'}


################
# Keymap Props #
##########S#######


addon_keymaps = []


region_types = ['WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI', 'TOOLS', 'TOOL_PROPS', 'PREVIEW']


keymap_prop = [
		['Window', 'EMPTY'],
		#['User Interface', 'EMPTY'],
		#['Header', 'EMPTY'],
		#['Screen', 'EMPTY'],
		]


keymap_names = [prop[0] for prop in keymap_prop]


key_lists = [
    [KeySwitchUp.bl_idname, 'UP_ARROW'],
    [KeySwitchDown.bl_idname, 'DOWN_ARROW'],
    [KeyShortRunner.bl_idname, 'RIGHT_ARROW'],
    [KeyShortRunnerBack.bl_idname, 'LEFT_ARROW']
]


key_lists2 = [
    [KeyScreenUp.bl_idname, 'UP_ARROW'],
    [KeyScreenDown.bl_idname, 'DOWN_ARROW']
]


#####################
# Addon Preferences #
#####################


def get_keymap_item(km, kmi_idname):
    for keymap_item in km.keymap_items:
        if keymap_item.idname == kmi_idname:
            return keymap_item
    return None


class ManageQuickSwitcherKeymap(bpy.types.AddonPreferences):
    bl_idname = __name__

    area_items = [
        ('VIEW_3D', "3D View", "", 1), 
        ('TIMELINE', "Timeline", "", 2), 
        ('GRAPH_EDITOR', "Graph Editor", "", 3), 
        ('DOPESHEET_EDITOR', "Dope Sheet", "", 4), 
        ('NLA_EDITOR', "NLA Editor", "", 5), 
        ('IMAGE_EDITOR', "UV/Image Editor", "", 6), 
        ('SEQUENCE_EDITOR', "Video Sequence Editor", "", 7), 
        ('CLIP_EDITOR', "Movie Clip Editor", "", 8), 
        ('TEXT_EDITOR', "Text Editor", "", 9), 
        ('NODE_EDITOR', "Node Editor", "", 10), 
        ('LOGIC_EDITOR', "Logic Editor", "", 11), 
        ('PROPERTIES', "Properties", "", 12), 
        ('OUTLINER', "Outliner", "", 13), 
        ('USER_PREFERENCES', "User Preferences", "", 14), 
        ('INFO', "Info", "", 15), 
        ('FILE_BROWSER', "File Browser", "", 16), 
        ('CONSOLE', "Python Console", "", 17) 
    ]

    area_sub_items = [
        ('NONE', "None", "", 1), 
        ('VIEW_3D', "3D View", "", 2), 
        ('TIMELINE', "Timeline", "", 3), 
        ('GRAPH_EDITOR', "Graph Editor", "", 4), 
        ('DOPESHEET_EDITOR', "Dope Sheet", "", 5), 
        ('NLA_EDITOR', "NLA Editor", "", 6), 
        ('IMAGE_EDITOR', "UV/Image Editor", "", 7), 
        ('SEQUENCE_EDITOR', "Video Sequence Editor", "", 8), 
        ('CLIP_EDITOR', "Movie Clip Editor", "", 9), 
        ('TEXT_EDITOR', "Text Editor", "", 10), 
        ('NODE_EDITOR', "Node Editor", "", 11), 
        ('LOGIC_EDITOR', "Logic Editor", "", 12), 
        ('PROPERTIES', "Properties", "", 13), 
        ('OUTLINER', "Outliner", "", 14), 
        ('USER_PREFERENCES', "User Preferences", "", 15), 
        ('INFO', "Info", "", 16), 
        ('FILE_BROWSER', "File Browser", "", 17), 
        ('CONSOLE', "Python Console", "", 18) 
    ]


    pie_north = EnumProperty(items = area_items)
    pie_north_east = EnumProperty(items = area_items)
    pie_east = EnumProperty(items = area_items)
    pie_south_east = EnumProperty(items = area_items)
    pie_south = EnumProperty(items = area_items)
    pie_south_west = EnumProperty(items = area_items)
    pie_west = EnumProperty(items = area_items)
    pie_north_west = EnumProperty(items = area_items)

    pie_north_sub = EnumProperty(items = area_sub_items)
    pie_north_east_sub = EnumProperty(items = area_sub_items)
    pie_east_sub = EnumProperty(items = area_sub_items)
    pie_south_east_sub = EnumProperty(items = area_sub_items)
    pie_south_sub = EnumProperty(items = area_sub_items)
    pie_south_west_sub = EnumProperty(items = area_sub_items)
    pie_west_sub = EnumProperty(items = area_sub_items)
    pie_north_west_sub = EnumProperty(items = area_sub_items)

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        kc = wm.keyconfigs.user
        box = layout.box()
        box.label("Pie Menu Setting")

        split = box.split()
        col = split.column(align = True)
        col.label(text = "Main")
        col.prop(self, "pie_north", text = "↑ ")
        col.prop(self, "pie_north_east", text = "↗ ")
        col.prop(self, "pie_east", text = "→ ")
        col.prop(self, "pie_south_east", text = "↘ ")
        col.prop(self, "pie_south", text = "↓ ")
        col.prop(self, "pie_south_west", text = "↙ ")
        col.prop(self, "pie_west", text = "← ")
        col.prop(self, "pie_north_west", text = "↖ ")

        col = split.column(align = True)
        col.label(text = "Sub")
        col.prop(self, "pie_north_sub", text = "")
        col.prop(self, "pie_north_east_sub", text = "")
        col.prop(self, "pie_east_sub", text = "")
        col.prop(self, "pie_south_east_sub", text = "")
        col.prop(self, "pie_south_sub", text = "")
        col.prop(self, "pie_south_west_sub", text = "")
        col.prop(self, "pie_west_sub", text = "")
        col.prop(self, "pie_north_west_sub", text = "")


        idnames = [SwitchAreaPieTrigger.bl_idname, KeySwitchUp.bl_idname, KeySwitchDown.bl_idname, KeyShortRunner.bl_idname, KeyShortRunnerBack.bl_idname, KeyScreenUp.bl_idname, KeyScreenDown.bl_idname]
        kms = kc.keymaps

        for n in range(len(keymap_names)):
            km_n = kms[keymap_names[n]]

            for m, idname in enumerate(idnames):
                split = box.split()
                col = split.column()
                if m is 0:
                    col.label(keymap_names[n])
                kmi_n = get_keymap_item(km_n, idname)

                if kmi_n:
                    col.context_pointer_set("keymap", km_n)
                    rna_keymap_ui.draw_kmi([], kc, km_n, kmi_n, col, 0)
                else:
                    register_keymap()


###################
# Property Groups #
###################


class WindowProperty(bpy.types.PropertyGroup):
    name = StringProperty()
    id = StringProperty()
    order = IntProperty()
    rpd_swt_checker = BoolProperty()
    dst_name = StringProperty()
    dst_id = StringProperty()
    dummy = BoolProperty()


class ScreenProperty(bpy.types.PropertyGroup):
    name = StringProperty()

###########################
# Register and Unregister #
###########################


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.rpd_swt_window_properties = CollectionProperty(type = WindowProperty)
    bpy.types.Scene.rpd_swt_screen_properties = CollectionProperty(type = ScreenProperty)
    bpy.types.Scene.rpd_swt_selected_index = IntProperty()
    bpy.types.Scene.rpd_swt_screen_selected_index = IntProperty()
    bpy.types.Scene.rpd_swt_bool_pool = BoolProperty()
    bpy.types.Scene.rpd_swt_tmp_id = StringProperty()
    bpy.types.Screen.rpd_swt_checker = BoolProperty()
    register_keymap()


def register_keymap():
    for i in range(len(keymap_prop)):
        wm = bpy.context.window_manager
        for region_type in region_types:
            km = wm.keyconfigs.addon.keymaps.new(name = keymap_prop[i][0], space_type = keymap_prop[i][1], region_type = region_type)

            for (idname, key) in key_lists:
                kmi = km.keymap_items.new(idname, key, 'PRESS', ctrl = False, shift = False, alt = True, head = True)
                kmi.active = True
                addon_keymaps.append((km, kmi))

            for (idname, key) in key_lists2:
                kmi = km.keymap_items.new(idname, key, 'PRESS', ctrl = False, shift = True, alt = True, head = True)
                kmi.active = True
                addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(SwitchAreaPieTrigger.bl_idname, 'NONE', 'PRESS', ctrl = False, shift = False, alt = False, head = True)
            kmi.active = True
            addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_module(__name__)
            
    del bpy.types.Scene.rpd_swt_window_properties
    del bpy.types.Scene.rpd_swt_selected_index
    del bpy.types.Scene.rpd_swt_screen_selected_index
    del bpy.types.Scene.rpd_swt_bool_pool 
    del bpy.types.Scene.rpd_swt_tmp_id
    del bpy.types.Screen.rpd_swt_checker

    unregister_keymap()
    
def unregister_keymap():
    wm = bpy.context.window_manager

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
    

if __name__ == '__main__':
    register()
    bpy.ops.rpd_swt_window_properties.operations(operation = 'INIT')
