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


bl_info = {
    'name': "UV/Image Tools",
    'author': "MKB",
    'version': (1, 0, 1),
    'blender': (2, 69, 0),
    'location': "IMAGE_EDITOR > TOOLS",
    'description': "UV Toolbar",
    "wiki_url": "http://blenderartists.org/forum/showthread.php?339842-Addon-UV-Image-Tools",
    'category': 'UV'}

    # changes by russcript:tested 2.7 RC windows and linux
    # added tabs organization (line 46)
    # toolbar now shows only in uv edit modes and not uv sculpt(line 51)
    # changed a few tooltips and labels, for clarity
    # made the Islands tools button show only in uv edit mode(line 622)
    # hope this helps, thanks for the addon




import bpy
from bpy.props import BoolProperty, IntProperty, FloatProperty


class uvtools(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'
    bl_label = "UV Tools"



    @classmethod
    def poll(cls, context):
        sima = context.space_data
        return sima.show_uvedit and not context.tool_settings.use_uv_sculpt



    def draw(self, context):
        layout = self.layout




#--Transform-------------------------------------------------------------------





        col = layout.column(align=True)
        col.label(text="Transform:")

        row = col.row(align=True)

        row.operator("transform.translate",text="(G)", icon="MAN_TRANS")
        row.operator("transform.rotate", text="(R)", icon="MAN_ROT")
        row.operator("transform.resize", text="(S)", icon="MAN_SCALE")

        row = col.row(align=True)
        row.operator("transform.mirror", text="Mirror X").constraint_axis=(True, False, False)
        row.operator("transform.mirror", text="Mirror Y").constraint_axis=(False, True, False)

        row = col.row(align=True)
        row.operator("uv.island_tools", text="Islands Tools")
        row.operator("uv.rotatednine", text="Rot90°")






#--Align------------------------------------------------------------------------------------





        col = layout.column(align=True)
        col.label(text="Align:")

        row = col.row(align=True)


        row.operator("uv.align",text="Align X").axis='ALIGN_X'
        row.operator("uv.align",text="Align Y").axis='ALIGN_Y'
        row.operator("uv.align",text="Auto").axis='ALIGN_AUTO'

        row = col.row(align=True)
        row.operator("uv.align",text="Straighten").axis='ALIGN_S'
        row.operator("uv.align",text="Straighten X").axis='ALIGN_T'
        row.operator("uv.align",text="StraightenY").axis='ALIGN_U'






#--Selections------------------------------------------------------------------------------



        col = layout.column(align=True)
        col.label(text="Select with / Select:")

        row = col.row(align=True)
        row.operator("uv.select_border", text="Box", icon="BORDER_RECT").pinned=False
        row.operator("uv.select_border", text="Box Pinned").pinned=True




        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("uv.select_all", text="All").action='TOGGLE'
        row.operator("uv.select_all", text="Invert").action='INVERT'

        row = col.row(align=True)
        row.operator("uv.select_linked", text="Linked")
        row.operator("uv.select_split", text="Split")
        row.operator("uv.select_pinned", text="Pinned")







#--Editing--------------------------------------------------------------------------------




        col = layout.column(align=True)
        col.label(text="Editing:")

        row = col.row(align=True)
        row.operator("uv.weld", text="Weld", icon="AUTOMERGE_ON")
        row.operator("uv.stitch", text="Stitch")


        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("uv.pin", text="Pin").clear=False
        row.operator("uv.pin", text="UnPin").clear=True

        row = col.row(align=True)
        row.operator("uv.minimize_stretch", text="Minimize Stretch")
        row.operator("uv.average_islands_scale", text="Average Scale")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("uv.remove_doubles", text="Remove Doubles", icon="PANEL_CLOSE")




#--Seams---------------------------------------------------------------------------------




        col = layout.column(align=True)
        col.label(text="Seams:")

        row = col.row(align=True)
        row.operator("uv.mark_seam", text="Mark Seams")
        row.operator("uv.seams_from_islands", text="from Islands")









#--Island----------------------------------------------------------------------------------




        col = layout.column(align=True)
        col.label(text="Island:")

        row = col.row(align=True)
        row.operator("uv.pack_islands", text="Pack", icon="GRID")
        row.operator("mesh.faces_mirror_uv", text="Copy Mirror UV")

        row = col.row(align=True)
        row.operator("uv.unwrap", text="Unwrap")
        row.operator("uv.reset", text="Reset")



#--Hide------------------------------------------------------------------------------



        col = layout.column(align=True)
        col.label(text="Hidden:")

        row = col.row(align=True)
        row.operator("uv.hide", text="Select").unselected=False
        row.operator("uv.hide", text="UnSelect").unselected=True
        row.operator("uv.reveal", text="Show All")


        col = layout.column(align=True)
        col.label(text="History:")

        row = col.row(align=True)
        row.operator("ed.undo_history", text="History")
        row.operator("ed.undo", text="Undo")
        row.operator("ed.redo", text="Redo")






#--Save---------------------------------------------------------------------------------




        col = layout.column(align=True)
        col.label(text="Save:")


        row = col.row(align=True)

        row.operator("uv.export_layout", text="Export UV Layout")
        row.operator("wm.save_mainfile",text="",icon="FILE_TICK")
        row.operator("wm.save_as_mainfile",text="",icon="SAVE_AS")











#--Edit Image external---------------------------------------------------------------------------------



        #col = layout.column(align=True)
        #col.label(text="External Editor!!!:")


        #row = col.row(align=True)
        #row.operator("image.external_edit",text="Edit Image External")






#--Snap-------------------------------------------------------------------------------------




        #col = layout.column(align=True)
        #col.label(text="Snap:")



        #row = col.row(align=True)
        #row.operator("uv.snap_selected", text="Selected > Cursor").target="CURSOR"
        #row.operator("uv.snap_selected", text="-> Cursor Offset").target="CURSOR_OFFSET"

        #row = col.row(align=True)

        #row.operator("uv.snap_selected", text="Selected > Pixel").target="PIXELS"
        #row.operator("uv.snap_selected", text="-> Adjacent").target="ADJACENT_UNSELECTED"

        #row = col.row(align=True)
        #row.operator("uv.snap_cursor", text="Cursor > Selected").target="SELECTED"
        #row.operator("uv.snap_cursor", text="Cursor > Pixel").target="PIXELS"






        #   ‘PIXELS’, ‘CURSOR’, ‘CURSOR_OFFSET’, ‘ADJACENT_UNSELECTED’








#-------------------------------------------------------------------------------------


class imagetools(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Image Tools"




    def draw(self, context):
        layout = self.layout



#--Image---------------------------------------------------------------------------------



        col = layout.column(align=True)
        col.label(text="Image:")

        row = col.row(align=True)
        row.operator("image.open", text="Open", icon="FILESEL")
        row.operator("image.new", text="New")

        row = col.row(align=True)
        row.operator("image.reload", text="Reload")
        row.operator("image.replace", text="Replace")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("image.external_edit",text="Edit Image External")


#--Image Pack---------------------------------------------------------------------------


        col = layout.column(align=True)
        col.label(text="Pack into File:")

        row = col.row(align=True)
        row.operator("image.pack", text="Pack", icon="PACKAGE")
        row.operator("image.pack", text="Pack as PNG").as_png=True


#--Save-------------------------------------------------------------------------------

        col = layout.column(align=True)
        col.label(text="Save:")

        row = col.row(align=True)
        row.operator("image.save", text="Save", icon="FILE_TICK")
        row.operator("image.save_as", text="Save as" , icon="SAVE_AS")
        row.operator("image.save_as", text="Save Copy").copy=True






#--Edit Image external---------------------------------------------------------------------------------



        #col = layout.column(align=True)
        #col.label(text="External Editor!!!:")


        #row = col.row(align=True)
        #row.operator("image.external_edit",text="Edit Image External")






#--Snap-------------------------------------------------------------------------------------




        #col = layout.column(align=True)
        #col.label(text="Snap:")



        #row = col.row(align=True)
        #row.operator("uv.snap_selected", text="Selected > Cursor").target="CURSOR"
        #row.operator("uv.snap_selected", text="-> Cursor Offset").target="CURSOR_OFFSET"

        #row = col.row(align=True)

        #row.operator("uv.snap_selected", text="Selected > Pixel").target="PIXELS"
        #row.operator("uv.snap_selected", text="-> Adjacent").target="ADJACENT_UNSELECTED"

        #row = col.row(align=True)
        #row.operator("uv.snap_cursor", text="Cursor > Selected").target="SELECTED"
        #row.operator("uv.snap_cursor", text="Cursor > Pixel").target="PIXELS"






        #   ‘PIXELS’, ‘CURSOR’, ‘CURSOR_OFFSET’, ‘ADJACENT_UNSELECTED’








class uvrotated(bpy.types.Operator):
    """uv rotate 90°"""
    bl_label = "UV Rotate 90°"
    bl_idname = "uv.rotatednine"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        bpy.ops.transform.rotate(value=1.5708, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1.61051)

        return {"FINISHED"}





#--------------------------------------------------------------------------------------------------


#bl_info = {
#    "name": "Island Tools",
#    "author": "Jordi Vall-llovera Medina",
#    "version": (1, 3, 5),
#    "blender": (2, 6, 4),
#    "location": "UV / Image Editor",
#    "description": "Tools for transform islands from individual origins",
#    "warning": "",
#    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/UV/Island_Tools",
#    "tracker_url": "",
#    "category": "Learnbgame"
}

#"""
#Additional links:
#    Author Site: http://jordiart3d.blogspot.com.es/
#"""



def main(context, only_selection, view_all_selected, x_size, y_size,\
    size_link, rotation, x_mirror, y_mirror):

    obj = context.active_object
    mesh = obj.data

    is_editmode = (obj.mode == 'EDIT')
    bpy.context.space_data.pivot_point = 'MEDIAN'
    tool = bpy.context.tool_settings
    tool.mesh_select_mode = (False, False, True)
    tool.uv_select_mode = 'ISLAND'
    x = 0.0
    y = 0.0

    for repeat in range (11):
        if size_link:
            y_size = x_size
            x_size = y_size
        if only_selection:
            bpy.ops.uv.hide(unselected = True)

        search(x, y, x_size, y_size, rotation, x_mirror, y_mirror)
        x = 0.0
        y += 0.1

    bpy.ops.uv.reveal()
    if view_all_selected:
        bpy.ops.uv.select_all(action='SELECT')
    else:
        bpy.ops.uv.select_all(action='DESELECT')

    tool.use_uv_select_sync = False
    bpy.ops.uv.cursor_set(location = (0.0, 0.0))

    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

def search(x, y, x_size, y_size, rotation, x_mirror, y_mirror):
    center = bpy.context.space_data.uv_editor
    for repeat in range (11):
        bpy.ops.uv.cursor_set(location = (x, y))
        bpy.ops.uv.select(extend = False, location =( x, y))

        #Scale islands
        bpy.ops.transform.resize(value=(x_size, y_size, 1),\
         constraint_axis=(False, False, False),\
          constraint_orientation='GLOBAL', mirror=False,\
           proportional='DISABLED', proportional_edit_falloff='SMOOTH',\
            proportional_size=1, snap=False, snap_target='CLOSEST',\
             snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0),\
              texture_space=False, release_confirm=False)

        #Rotate islands
        bpy.ops.transform.rotate(value=rotation, axis=(-0, -0, -1),\
         constraint_axis=(False, False, False),\
          constraint_orientation='GLOBAL', mirror=False,\
           proportional='DISABLED', proportional_edit_falloff='SMOOTH',\
            proportional_size=1, snap=False, snap_target='CLOSEST',\
             snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0),\
              release_confirm=False)

        #Mirror islands
        if x_mirror or y_mirror:
            bpy.ops.transform.mirror(\
            constraint_axis=(x_mirror, y_mirror, False),\
             constraint_orientation='GLOBAL', proportional='DISABLED',\
              proportional_edit_falloff='SMOOTH', proportional_size=1,\
               release_confirm=False)

        bpy.ops.uv.hide(unselected=False)
        x += 0.1

class cIslandTools(bpy.types.Operator):
    '''UV Transform operations on islands'''
    bl_idname = "uv.island_tools"
    bl_label = "Island Tools"
    bl_options = {'REGISTER', 'UNDO'}

    only_selection = BoolProperty(name = "Only selection",
        description = "Only transform selected islands",
        default = True)

    view_all_selected = BoolProperty(name = "View all selected",
        description = "View all selected while transform",
        default = False)

    x_size = FloatProperty(name = "X size",
        description = "Island scale on local X axis",
        default = 1,
        min = 0,
        max = 100,
        soft_min = 0,
        soft_max = 1,
        subtype = 'FACTOR')

    y_size = FloatProperty(name = "Y size",
        description = "Island scale on local Y axis",
        default = 1,
        min = 0,
        max = 100,
        soft_min = 0,
        soft_max = 1,
        subtype = 'FACTOR')

    size_link = BoolProperty(name = "Link size",
        description = "Link X and Y size for uniform transformations(use X)",
        default = True)

    rotation = FloatProperty(name = "Rotation",
        description = "Value to specify rotation angle of islands",
        default = 0,
        min = -360,
        max = 360,
        soft_min = -360,
        soft_max = 360,
        subtype = 'ANGLE')

    x_mirror = BoolProperty(name = "X mirror",
        description = "Mirror islands on local X axis",
        default = False)

    y_mirror = BoolProperty(name = "Y mirror",
        description = "Mirror islands on local Y axis",
        default = False)

    #@classmethod - Changed to activate the header button on show_uv in def menu_func

    #def poll(cls, context):
       # if bpy.context.area.type == "IMAGE_EDITOR":
            #obj = bpy.context.active_object
            #if obj.type == 'MESH':
                #if obj.mode == 'EDIT':
                    #if obj.data.uv_layers:
                        #return(obj.type == 'MESH')

    def draw(self, context):
        obj = context.object
        layout = self.layout
        col = layout.column()
        col.prop(self, "only_selection")
        row = col.row()
        row.prop(self, "view_all_selected")
        row.prop(self, "size_link")
        row = col.row()
        row.prop(self, "x_size")
        row.prop(self, "y_size")
        row = col.row()
        row.prop(self, "rotation")
        row = col.row()
        row.prop(self, "x_mirror")
        row.prop(self, "y_mirror")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)

    def execute(self, context):
        main(context, self.only_selection, self.view_all_selected, self.x_size,\
         self.y_size, self.size_link, self.rotation, self.x_mirror, self.y_mirror)
        return {'FINISHED'}

def menu_func(self, context):
    show_uvedit = context.space_data.show_uvedit
    if show_uvedit:
        self.layout.operator("uv.island_tools",
        text="Island Tools",
        icon='UV_ISLANDSEL')

def register():
    bpy.utils.register_class(uvtools)
    bpy.utils.register_class(imagetools)
    bpy.utils.register_class(cIslandTools)
    bpy.types.IMAGE_MT_uvs_transform.prepend(menu_func)
    bpy.types.IMAGE_HT_header.append(menu_func)
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_class(uvtools)
    bpy.utils.unregister_class (imagetools)
    bpy.utils.unregister_class(cIslandTools)
    bpy.types.IMAGE_MT_uvs_transform.remove(menu_func)
    bpy.types.IMAGE_HT_header.remove(menu_func)
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()
