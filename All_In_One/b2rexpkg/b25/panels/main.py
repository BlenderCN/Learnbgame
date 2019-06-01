"""
 Main panel managing the connection.
"""

import bpy
import uuid

import b2rexpkg
from b2rexpkg.b25.ops import getLogLabel
from b2rexpkg.tools import runexternal
#from ..properties import B2RexProps


class ConnectionPanel(bpy.types.Panel):
    bl_label = "b2rex" #baseapp.title
    #bl_space_type = "VIEW_3D"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    #bl_region_type = "UI"
    bl_context = "scene"
    bl_idname = "b2rex"
    cb_pixel = None
    cb_view = None
    def __init__(self, context=None):
        self._prev_tundra_path = ""
        bpy.types.Panel.__init__(self)
        # not the best place to set the loglevel :P
        bpy.ops.b2rex.loglevel(level=str(bpy.context.scene.b2rex_props.loglevel))
    def __del__(self):
        if bpy.b2rex_session.rt_on:
            bpy.b2rex_session.onToggleRt()
        print("byez!")

    def draw_callback_view(self, context):
        pass # we dont really want this callback, but keeps the object
        # from dying all the time so we keep it for now

    def draw_connections(self, layout, session, props):
        box = layout.box()
        row = box.row()
        if len(props.connection.list):
            row.prop_search(props.connection, 'search', props.connection,
                            'list', icon='SCRIPTWIN',text='connection')
            if props.connection.search in ['add', 'edit']:
                pass
            else:
                row.operator("b2rex.addconnection", text="", icon='SETTINGS',
                             emboss=False).action = "edit"
                row.operator("b2rex.addconnection", text="", icon='ZOOMOUT',
                             emboss=False).action = "delete"
                row.operator("b2rex.addconnection", text="", icon='ZOOMIN',
                             emboss=False).action = "create"
                if props.connection.search and props.connection.search in props.connection.list:
                    col = row.column()
                    col.alignment = 'RIGHT'
                    if session.simrt:
                        if session.simrt.connected:
                            col.operator("b2rex.toggle_rt", text="RT",
                                         icon='PMARKER_ACT')
                        else:
                            col.operator("b2rex.toggle_rt", text="RT",
                                         icon='PMARKER_SEL')
                    else:
                        col.operator("b2rex.toggle_rt", text="RT", icon='PMARKER')

        if not len(props.connection.list) or props.connection.search in ['add', 'edit']:
            if not len(props.connection.list):
                row.label("New connection")
            box_c = box.box()
            form = props.connection.form
            box_c.prop(form, "name")
            box_c.prop(form, "url")
            box_c.prop(form, "username")
            box_c.prop(form, "password")
            if form.url and form.username and form.password:
                if form.name in props.connection.list:
                    text = "Save"
                else:
                    text = "Add"
                box_c.operator("b2rex.addconnection", text=text, icon='FILE_TICK').action = "add"
            if len(props.connection.list):
                box_c.operator("b2rex.addconnection", text="Cancel",
                               icon='CANCEL').action = "cancel"
        if session.status_level == 0:
            box.label(text=session.status, icon='ERROR')
        else:
            box.label(text="Status: "+session.status)

            #row.prop_enum(props.connection, 'list')
            #           row.template_list(props.connection, 'list', props.connection,
            #                 'selected', type='COMPACT')


    def draw_regions(self, layout, session, props):
        if not len(props.regions):
            return
        row = layout.column()
        if props.regions_expand:
            row.prop(props, 'regions_expand', icon="TRIA_DOWN", text="Regions")
        else:
            row.prop(props, 'regions_expand', icon="TRIA_RIGHT", text="Regions")
            return
        row = layout.row() 
        row.template_list(props, 'regions', props, 'selected_region')
        # XXX only real time operations for the moment.
        return
        if props.selected_region > -1:
            col = layout.column_flow(0)
            col.operator("b2rex.exportupload", text="Export/Upload")
            col.operator("b2rex.export", text="Upload")
            col.operator("b2rex.export", text="Clear")
            col.operator("b2rex.check", text="Check")
            col.operator("b2rex.sync", text="Sync")
            col.operator("b2rex.import", text="Import")

        row = layout.column()
        for k in session.region_report:
            row.label(text=k)


    def draw(self, context):
        if self.cb_view == None:
            # callback is important so object doesnt die ?
            self.cb_view = context.region.callback_add(self.draw_callback_view, 
                                        (context, ),
                                        'POST_VIEW') # XXX POST_PIXEL ;)
        
        layout = self.layout
        props = context.scene.b2rex_props
        session = bpy.b2rex_session

        self.draw_connections(layout, session, props)

        session.drawModules(layout, props)
        self.draw_regions(layout, session, props)

        self.draw_settings(layout, session, props)

    def draw_settings(self, layout, session, props):
        row = layout.row()
        if props.expand:
            row.prop(props,"expand", icon="TRIA_DOWN", text="Settings",
                     emboss=True)
        else:
            row.prop(props,"expand", icon="TRIA_RIGHT", text="Settings",
                     emboss=True)
            return
        for prop in ['agent_libs_path', 'tools_path']: # "loc", "path", "pack", "server_url", "username", "password",
            row = layout.row()
            row.prop(props, prop)

        row = layout.row()
        row.prop(props, 'tundra_path')
        if not props.tundra_path == self._prev_tundra_path:
            self._prev_tundra_path = props.tundra_path
            bpy.ops.b2rex.reload_components()
        if runexternal.find_application('server', [props.tundra_path], True):
            row.label(text='', icon='FILE_TICK')

        check_icon = ['CHECKBOX_DEHLT', 'CHECKBOX_HLT']
        col = layout.column_flow()
        col.operator('b2rex.toggleimportterrain', text="Import Terrain", icon=check_icon[props.importTerrain], emboss=False) 
        col.operator('b2rex.toggleimporttextures', text="Import Textures", icon=check_icon[props.importTextures], emboss=False) 
        col.operator('b2rex.toggle_safe_mode', text="Safe Mode",
                     icon=check_icon[b2rexpkg.safe_mode], emboss=False) 

        #col.prop(props,"regenMaterials")
        #col.prop(props,"regenObjects")

        #col.prop(props,"regenTextures")
        #col.prop(props,"regenMeshes")

        box = layout.row()
        box.operator_menu_enum("b2rex.loglevel", 'level', icon='INFO',
                               text=getLogLabel(props.loglevel))
        box = layout.row()
        box.prop(props, "kbytesPerSecond")
        box = layout.row()
        box.prop(props, "rt_budget")
        box = layout.row()
        box.prop(props, "rt_sec_budget")
        box = layout.row()
        box.prop(props, "pool_workers")
        box = layout.row()
        box.prop(props, "terrainLOD")
