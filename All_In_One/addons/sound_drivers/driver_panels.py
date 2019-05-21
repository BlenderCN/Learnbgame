bl_info = {
    "name": "Driver Panels",
    "author": "batFINGER",
    "location": "3D View Tools",
    "description": "Driver Panel Settings",
    "warning": "Still in Testing",
    "wiki_url": "http://wiki.blender.org/index.php/\
                User:BatFINGER/Addons/Sound_Drivers",
    "version": (1, 0),
    "blender": (2, 7, 7),
    "tracker_url": "",
    "icon": 'DRIVER',
    "support": 'TESTING',
    "category": "Animation",
    }

import bpy
from bpy.utils import register_class, unregister_class
from bpy.props import BoolProperty, IntProperty, StringProperty
# TODO move all icon "stuff" to icons.py
from sound_drivers.utils import get_icon, bpy_collections, icon_from_bpy_datapath
from bpy.types import AddonPreferences

# dummy AddonPrefs (used for top level)

class DriverPanelsAddonPreferences(AddonPreferences):
    ''' Driver Manager Prefs '''
    bl_idname = __name__

    # toggle to view drivers
    view_drivers = BoolProperty(default=False)
    toolbar_category = StringProperty(default="Drivers")

    def draw(self, context):
        def icon(test):
            if test:
                icon = 'FILE_TICK'
            else:
                icon = 'ERROR'
            return icon

        layout = self.layout
        row = layout.row()
        # TODO make this change the category of all panels
        row.prop(self, "toolbar_category")


class DRIVER_UL_driven_objects(bpy.types.UIList):    
    use_filter_empty = BoolProperty(name="Filter Empty", default=False, options=set(),
                                              description="Whether to filter empty vertex groups")
    use_filter_empty_reverse = BoolProperty(name="Reverse Empty", default=False, options=set(),
                                                      description="Reverse empty filtering")
    use_filter_name_reverse = BoolProperty(name="Reverse Name", default=False, options=set(),
                                                     description="Reverse name filtering")
                                                     
    use_filter_name = BoolProperty(name="Object Name", default=True, options=set(),
                                                     description="Reverse name filtering")
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, filter_flg):
        ob = data
        self.use_filter_sort_alpha = True

        coll = active_propname.strip("active_index")

        collection = getattr(bpy.data, coll)
        obj = collection.get(item.name) 
               
        icon = get_icon(obj.type) if hasattr(obj, "type") else icon_from_bpy_datapath(repr(obj))
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
           layout.label("  %s" % (item.name), icon=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=icon)

        return
        col.label(item.name)
        return



    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        layout.label("filetereer")
        layout.prop(self, "filter_name")
        layout.prop(self, "use_filter_name")
           
    def filter_items(self, context, data, propname):

        col = getattr(data, propname)
        filter_name = self.filter_name.lower()

        flt_flags = [self.bitflag_filter_item if any(
                filter_name in filter_set for filter_set in (
                    str(i), item.name.lower()
                )
            )
            else 0 for i, item in enumerate(col, 1)
        ]

        if self.use_filter_sort_alpha:
            flt_neworder = [x[1] for x in sorted(
                    zip(
                        [x[0] for x in sorted(enumerate(col), key=lambda x:( x[1].name))],
                        range(len(col))
                    )
                )
            ]
        else:
            flt_neworder = []

        #print(flt_flags, flt_neworder)    
        return flt_flags, flt_neworder


class DriversManagerPanel(bpy.types.Panel):
    """Driver Tool Panel"""
    bl_label = "Driver Manager"
    bl_idname = "VIEW3D_PT_DriversManager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = 'Drivers'

    @classmethod
    def poll(self, context):
        dm = bpy.app.driver_namespace.get("DriverManager")
        if not dm:
            return True
        return bool(len(dm.all_drivers_list))

    @classmethod
    def idchange(cls, s):
        cls.bl_idname = s

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        dm = bpy.app.driver_namespace.get("DriverManager")

        if dm is not None:
            dm.draw_menus(self, context)
            pass

    def draw(self, context):

        scene = context.scene
        layout = self.layout
        dns = bpy.app.driver_namespace

        box = layout
        dm = dns.get("DriverManager")
        UserPrefs = context.user_preferences

        if not UserPrefs.system.use_scripts_auto_execute:
            row = layout.row()
            row.prop(UserPrefs.system, "use_scripts_auto_execute")
            row = layout.row()
            row.label("Warning Will not work unless Auto Scripts Enabled",
                      icon='ERROR')
            return
        if dm is None:
            #dm = DriverManager()
            box.label("No Driver Mangager", icon='INFO')
            row = box.row()
            row.operator("drivermanager.update")
            row = box.row()
            row.label("Once enabled will poll on drivers")

            return

        # dm.check_updates(context)
        row = box.row(align=True)
        if not len(dm._all_drivers_list):
            box.label("NO DRIVERS FOUND", icon='INFO')
            return
        ###dm.draw_menus(row, context)
        dm.draw_filters(self, context)

        return None
        # FIXME this can all go.
        ed = False
        settings = scene.driver_gui
        drivers_dict = dm.filter_dic
        seq_header, node_header = False, False
        for collname, collection in drivers_dict.items():
            bpy_collection = getattr(bpy.data, collname)
            # need to reorder for sequencer and nodes.
            # check for filter FIXME
            if settings.use_filters:
                if hasattr(settings.filters, collname):
                    if getattr(settings.filters, collname):
                        continue
            row = box.row()
            icon = get_icon(collname)

            if not len(collection):
                continue
            for name, object_drivers in collection.items():
                iobj = obj = bpy_collection.get(name)
                if hasattr(obj, "data") and obj.data is not None:
                    iobj = obj.data

                if not obj:
                    # a missing ob should invoke a dm refresh
                    continue
                # XXX code for context ...............................
                _filter_context_object = True
                if (collname == 'objects'
                        and _filter_context_object
                        and (obj != context.object
                             and obj not in context.selected_objects)):
                    continue

                _filter_context_scene = True
                if (collname == 'scenes'
                        and _filter_context_scene
                        and (obj != context.scene)):
                    continue

                # context world not in all spaces
                _filter_context_world = True
                if (collname == 'worlds'
                        and _filter_context_world
                        and hasattr(context, "world")
                        and (obj != context.world)):
                    continue

                row = box.row(align=True)
                row.label(text="", icon='DISCLOSURE_TRI_RIGHT')
                icon = get_icon(obj.rna_type.name)
                if hasattr(obj, "type"):
                    icon = get_icon(obj.type)

                '''
                if  context.scene.objects.active == obj:
                    row.template_ID(context.scene.objects, 'active')
                else:
                    row.label(text="", icon=icon)
                    row.prop(obj, "name", text="")


                '''
                #  TO BE REFACTORED
                row.label(text=obj.name, icon=icon)

                drivers = [dm.find(sdi)
                           for dp, ds in object_drivers.items()
                           for i, sdi in ds.items()]

                #REFACTO DLO
                #dm.draw_layout(layout, context, drivers)

        row = box.row()
        row.label("UPDATES %d" % dm.updates)
        '''
        if dm.edit_driver and not ed:
            #take out the edit driver
            dm.edit_driver = None

            row.label("OOPS")

        '''



class DriverPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Drivers"
    bl_label = " "
     
                
    def dic(self):
        return(context.driver_manager.get_collection_dic(self.collection))    
        
class EditDriverPanel(DriverPanel):

    @classmethod
    def poll(cls, context):
        return False
        #print("EDP", context.driver_manager.edit_driver is not None)
        return context.driver_manager is not None and context.driver_manager.edit_driver is not None
    
    def draw_header(self, context):
        layout = self.layout
        dm = context.driver_manager
        ed = dm.edit_driver
        op = layout.operator("driver.edit", text="EDIT DRIVER", icon='CANCEL')
        op.dindex=ed.index
        op.toggle=True
        layout.prop(ed.gui, "gui_types")

              
    def draw(self, context):
        layout = self.layout
        dm = context.driver_manager

        if ed is not None:
            dm.draw_layout(layout, context, dm.get_object_dic("xxx", "yyy"))
            dm.driver_edit_draw(layout, context)
            return None    
    
class DriverCollectionPanel(DriverPanel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = " "

    def context(self, context, obj):
        '''
        REFACTOR TO RETURN ob, keys
        '''
        if self.collection not in ["objects", "scenes"]:
            return True
        elif self.collection in ["scenes"]:
            return obj == context.scene
        elif self.collection in ["objects"]:
            return context.object
        elif self.collection in ["materials"]:
            return context.object.active_material

    '''
    @classmethod
    def unregister(cls):
        print("URC", cls.bl_idname)
        bpy.utils.unregister_class(cls)
    

    '''
    @classmethod
    def poll(cls, context):
        scene = context.scene
        dm = context.driver_manager
        do = getattr(scene, "driver_objects", None)
        if do is None or dm is None:
            return False
        #return True
        return(do.use_filters == getattr(do.filters, cls.collection) 
               and len(dm.get_collection_dic(cls.collection)))


    def draw_header(self, context):
        #self.layout.prop(context.scene, "use_gravity", text="")
        collection = getattr(self, "collection", "objects")
        self.layout.label(icon=get_icon(collection), text=collection.title())
    
    
    def draw(self, context):
        layout = self.layout

        collection = self.collection
        scene = context.scene
        wm = context.window_manager
        dm = context.driver_manager
        search = getattr(scene.driver_objects, "search_%s" % self.collection, False)
        index = getattr(scene.driver_objects, "active_%s_index" % self.collection, -1)
        coll = getattr(scene.driver_objects, collection)
        layout.prop(scene.driver_objects, "search_%s" % self.collection)
        if getattr(scene.driver_objects, "search_%s" % self.collection):
            ui = layout.template_list("SD_%s_ui_list" % self.collection,
                                      "", scene.driver_objects,
                                      self.collection, scene.driver_objects,
                                      "active_%s_index" % self.collection, self.collection)

        # get_driven_scene_objects(scene)
        if self.collection.startswith("ob"):
            #dic = dm.get_driven_scene_objects(scene)
            ob = coll[index] if search else context.object
            
            keys = [ob.name] if ob is not None else []
        elif self.collection.startswith("sce"):
            ob = context.scene
            keys = [ob.name]
        elif self.collection.startswith("mat"):
            ob = context.object.active_material
            keys = [ob.name] if ob is not None else []
        elif self.collection.startswith("shape_keys"):
            ob = getattr(context.object.data, "shape_keys", None)
            keys = [ob.name] if ob is not None else []
        else:
            #dic = dm.get_collection_dic(type(self).collection)
            ob = coll[index]
            keys = [ob.name]
            #keys = sorted(dic.keys())
        
        if ob is None:
            layout.label("NO CONTEXT OBJECT")
            return None
        dm.check_deleted_drivers()
        dic = dm.get_object_dic(collection, ob.name)
        

        obj = getattr(bpy.data, collection).get(ob.name)

     #  TO BE REFACTORED
        col = layout.column(align=True)
        icon = get_icon(obj.type) if hasattr(obj, "type") else icon_from_bpy_datapath(repr(obj))
        row = col.row()
        row.alignment = 'LEFT'
        row.label(icon='DISCLOSURE_TRI_RIGHT', text="")
        if not search and collection.startswith("obj"):
            row.template_ID(context.scene.objects, "active")
        else:
            row.label(icon=icon, text=ob.name)
        #obj = dm.find(dic[m][0][0]).driven_object.id_data            '''
        dm.draw_layout(col, context, dic)
        #dm.check_added_drivers(ob)
        return None

def register():
    register_class(DriversManagerPanel)
    
    register_class(EditDriverPanel)
    propdic = { 
                "bl_space_type" :  'VIEW_3D',
                "bl_region_type" :  'TOOLS',
                "bl_category" :  "Drivers",
                
                }
    for collection in bpy_collections:
        propdic["collection"] = collection
        bl_idname = "SD_%s_Panel" % collection
        propdic["bl_idname"] = bl_idname

        col_ui_list = type("SD_%s_ui_list" % collection, (DRIVER_UL_driven_objects,), {})
        x = type(bl_idname, (DriverCollectionPanel,), propdic)
        register_class(x)
        register_class(col_ui_list)
    
      
    def get_dm(self):
        dns = bpy.app.driver_namespace
        return dns.get("DriverManager")
    
    bpy.types.Context.driver_manager = property(get_dm)


def unregister():
    # should have done this earlier
    unregister_class(DriversManagerPanel)
    for c in bpy_collections:
        unregister_class(getattr(bpy.types, "SD_%s_Panel" % c))
        unregister_class(getattr(bpy.types, "SD_%s_ui_list" % c))
    #bpy.utils.unregister_class(DriverCollectionPanel)
    unregister_class(EditDriverPanel)
    # Need to remove all of these
    del bpy.types.Context.driver_manager

