import bpy
import math
import bpy_extras
import bpy_extras.view3d_utils
import rna_keymap_ui


######################
#CODE STRUCTURE
######################
#Base Funtions Section
#---------------------
#Pie Menu Section
#---------------------
#Execution Section
#---------------------
#Keymap Management Section
#---------------------
#Register and Unregister
######################


bl_info = {
        "name" : "View Snapper",
        "description" : "Snap a current view to the nearest dimension automatically",
        "author" : "Kozo Oeda",
        "version" : (2, 4),
        "location" : "",
        "warning" : "",
        "support" : "COMMUNITY",
        "wiki_url" : "",
        "tracker_url" : "",
        "category": "Learnbgame",
        }


###############################
#    Base Functions Section   #
############################### 


def get_region_window_size_context():
    for region in bpy.context.area.regions:
        if region.type == 'WINDOW':
            return region.width, region.height


def get_viewport_loc_context():
    region = bpy.context.region
    rv3d = bpy.context.region_data
    width, height = get_region_window_size_context()
    coord = (width/2, height/2)
    return bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)


def is_higher(x, y,  z, limit_degree):
    if math.degrees(math.atan(z / pow(x * x + y * y, 0.5))) > limit_degree:
        return True
    else:
        return False


def is_lower(x, y,  z, limit_degree):
    if math.degrees(math.atan(z / pow(x * x + y * y, 0.5))) < limit_degree:
        return True
    else:
        return False


def sin(degrees):
    return math.sin(math.radians(degrees))


def cos(degrees):
    return math.cos(math.radians(degrees))


def pivotz(v, degrees):
    return (cos(degrees) * v[0] - sin(degrees) * v[1], sin(degrees) * v[0] + cos(degrees) * v[1], v[2])
    

def is_in_the_first_quadrant(x, y): #corresponds to BACK by -45 rotation:
    if 0 < x and 0 <= y:
        return True
    else:
        return False


def is_in_the_second_quadrant(x, y): #corresponds to LEFT by -45 rotation:
    if x <= 0 and 0 < y:
        return True
    else:
        return False


def is_in_the_third_quadrant(x, y): #corresponds to FRONT by -45 rotation:
    if x < 0 and y <= 0:
        return True
    else:
        return False


def is_in_the_forth_quadrant(x, y): #corresponds to RIGHT by -45 rotation:
    if 0 <= x and y < 0:
        return True
    else:
        return False


def set_front(): 
    bpy.ops.view3d.viewnumpad(type = 'FRONT')


def set_right():
    bpy.ops.view3d.viewnumpad(type = 'RIGHT')


def set_back():
    bpy.ops.view3d.viewnumpad(type = 'BACK')


def set_left():
    bpy.ops.view3d.viewnumpad(type = 'LEFT')


def set_top():
    bpy.ops.view3d.viewnumpad(type = 'TOP')


def set_bottom():
    bpy.ops.view3d.viewnumpad(type = 'BOTTOM')


####################
# Pie Menu Section #
####################


class MoveToActiveCamera(bpy.types.Operator):
    bl_idname = "ops.move_to_active_camera"
    bl_label = "Move to Active Camera"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.view3d.viewnumpad(type = 'CAMERA')
        return {'FINISHED'}


class ViewOpsPie(bpy.types.Menu):
    bl_idname = "ViewOpsPie"
    bl_label = "View Ops"
    bl_options = {'INTERNAL'}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.camera_to_view", text = "View to Camera", icon = 'CAMERA_DATA')
        pie.operator(MoveToActiveCamera.bl_idname, text = "Active Camera", icon = 'OUTLINER_OB_CAMERA') 


class ViewOpsPieTrigger(bpy.types.Operator):
    bl_idname = 'wm.view_ops_pie_trigger'
    bl_label = 'View Pie Ops Trigger'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name = 'ViewOpsPie')
        return {'FINISHED'}


##########################
#   Execution Section    #
##########################


def snap(self, context):
    loc = get_viewport_loc_context()

    if is_higher(loc[0], loc[1], loc[2], 45):
        set_top()
        return 
    elif is_lower(loc[0], loc[1], loc[2], -45):
        set_bottom()
        return 

    pivoted_loc = pivotz(loc, -45)

    if is_in_the_first_quadrant(pivoted_loc[0], pivoted_loc[1]):
        set_back()
    elif is_in_the_second_quadrant(pivoted_loc[0], pivoted_loc[1]):
        set_left()
    elif is_in_the_third_quadrant(pivoted_loc[0], pivoted_loc[1]):
        set_front()
    elif is_in_the_forth_quadrant(pivoted_loc[0], pivoted_loc[1]):
        set_right()
    
    return 
        
    
class SnapView(bpy.types.Operator):
    bl_idname = "view3d.snapview"
    bl_label = "Snap View" 
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        try:
            snap(self, context)

        except ZeroDivisionError:
            pass

        return {'FINISHED'}

class PerspOrtho(bpy.types.Operator):
    bl_idname = "view3d.p_o"
    bl_label = "Persp/Ortho"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        bpy.ops.view3d.view_persportho()
        return {'FINISHED'}
        

#############################
# Keymap Management Section #
#############################


def get_keymap_item(km, kmi_idname):
    for keymap_item in km.keymap_items:
        if keymap_item.idname == kmi_idname:
            return keymap_item
    return None


class ManageViewSnapperKeymap(bpy.types.AddonPreferences): #TODO
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.label("3D View is a section for Object/Edit Mode. However keyboard inputs affect to the other modes.")
        layout.label("And note that Mouse Click inputs are not affecting to the other modes.")
        layout.label("Basically it is recommended that keymaps are same in all modes.")
        wm = context.window_manager
        kc = wm.keyconfigs.user
        keymap_names = ['3D View', 'Sculpt', 'Vertex Paint', 'Weight Paint', 'Image Paint']
        box = layout.box()

        #keymap main gui
        idnames = [SnapView.bl_idname, PerspOrtho.bl_idname, ViewOpsPieTrigger.bl_idname]
        kms = kc.keymaps

        for n in range(len(keymap_names)):
            km_n = kms[keymap_names[n]]

            for m, idname in enumerate(idnames):
                split = box.split()
                col = split.column()
                if m is 0:
                    col.label(keymap_names[n])
                kmi_n = get_keymap_item(km_n, idname)

                #core draw
                if kmi_n:
                    col.context_pointer_set("keymap", km_n)
                    rna_keymap_ui.draw_kmi([], kc, km_n, kmi_n, col, 0)
                else:
                    register_keymap()

                            
###########################
# Register and Unregister #
###########################


addon_keymaps = []


def register_keymap(): #TODO
    name_spacetypes = [('3D View', 'VIEW_3D'), ('Sculpt', 'EMPTY'), ('Vertex Paint', 'EMPTY'), ('Weight Paint', 'EMPTY'), ('Image Paint', 'EMPTY')]
    wm = bpy.context.window_manager

    for name_spacetype in name_spacetypes:
        km = wm.keyconfigs.addon.keymaps.new(name = name_spacetype[0], space_type = name_spacetype[1])

        kmi = km.keymap_items.new(SnapView.bl_idname, 'LEFTMOUSE', 'PRESS', ctrl = True, head = True)
        kmi.active = True

        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(PerspOrtho.bl_idname, 'NONE', 'PRESS', head = True)
        kmi.active = True

        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(ViewOpsPieTrigger.bl_idname, 'RIGHTMOUSE', 'PRESS', ctrl = True, head = True)
        kmi.active = True

        addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    bpy.utils.register_module(__name__)
    register_keymap()


def unregister():
    bpy.utils.unregister_module(__name__)
    unregister_keymap()


if __name__ == "__main__":
    register()
