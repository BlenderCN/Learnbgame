from importlib import import_module, reload as import_reload
import bpy
from bpy.types import Operator, AddonPreferences, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty
reload_flag = True

def draw(self, context):
    layout = self.layout
    for subaddon in addons.values():
        module = subaddon.module
        info = subaddon.info
        mod = getattr(self, subaddon.name, None)
        box = layout.box()
        subaddon.draw(box, context)

class SubAddon:
    @property
    def _store(self):
        addon = bpy.context.user_preferences.addons.get(__package__)
        prefs = getattr(addon, "preferences", None)
        return getattr(prefs, self.name, None)

    def register_submodule(self):
        module = self.module
        def register(store, context):
            if module is None:
                return None
            if store.enabled:
                self.register()
            else:
                self.unregister()
            return None
        return register

    def _get_classes(self, blenderclassname):
        import inspect
        classtype = getattr(bpy.types, blenderclassname, None)

        classes = [(name, cls) for name, cls in vars(self.module).items()
                if inspect.isclass(cls) and issubclass(cls, classtype) and cls != classtype]
        return classes

    def _get_pref_class(self):
        import inspect
        for obj in vars(self.module).values():
            if inspect.isclass(obj) and issubclass(obj, AddonPreferences):
                if hasattr(obj, 'bl_idname'):# and obj.bl_idname == mod.__name__:
                    return obj
        return None

    _enabled = False
    @property
    def enabled(self):
        store = self._store
        #print("BLRNA", getattr(self.module, "bl_rna", False))
        #print("MOD", self.module)
        if store:
            self._enabled = getattr(store, "enabled")

        return self._enabled

    @enabled.setter
    def enabled(self, value):
        store = self._store
        if self._store:
            setattr(self._store, "enabled", value)
        self._enabled = value

    @property
    def preferences(self):
        if self.prefsclass:
            return getattr(self._store, "preferences", None)
        return None

    def register(self):
        print("%s.register()" % self.name, end="")
        if not hasattr(self.module, "register"):
            print("....Ok")
            return
        try:
            self.module.register()
            print("....Ok")
        except ValueError as val:
            print(".... ValueError!!!")
            print(val)
        except RuntimeError as rte:
            print(".... RuntimeError!!!")
            print(rte)

    def unregister(self):
        print("%s.unregister()" % self.name, end="")
        if not hasattr(self.module, "unregister"):
            print("....Ok")
            return
        try:
            self.module.unregister()
            print("....Ok")
        except ValueError as val:
            print(".... ValueError!!!")
            print(val)
        except RuntimeError as rte:
            print(".... RuntimeError!!!")
            print(rte)

    # TODO wire this in maybe
    def draw_keymaps(self, layout, context, module, key="addon_keymaps"):
        import rna_keymap_ui
        addon_keymaps = getattr(module, key, [])
        col = layout
        kc = context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            #kmi.name = kmi.name.encode('utf-8').strip()
            # TODO ERROR UTF decode error on kmi.name
            try: 
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            except:
                pass

    def draw_menus(self, layout, context):
        if not self.menus:
            return
        layout.label("Menus")
        for name, panel in self.panels:
            row = layout.row()

            row.label("   %s" % name, icon='BLANK1')
            #row.label("Registered: %s" % hasattr(panel, "bl_rna"))
            #row.label("Registered: %s" % hasattr(bpy.types, name))
            if hasattr(panel, "bl_category"):
                row.label("bl_category: %s" % getattr(panel, "bl_category"))

    def draw_operators(self, layout, context):
        if not self.operators:
            return
        layout.label("Operators")
        for name, operator in self.operators:
            row = layout.row()

            row.label("   %s" % name, icon='BLANK1')
            #row.label("Registered: %s" % hasattr(operator, "bl_rna"))
            row.label("Registered: %s" % getattr(operator, "is_registered", False))
            #row.label("Registered: %s" % hasattr(bpy.types, operator.bl_rna.name))
            row.label(operator.bl_idname)
            if hasattr(operator, "bl_category"):
                row.label("bl_category: %s" % getattr(operator, "bl_category"))

    def draw_panels(self, layout, context):
        if not self.panels:
            return
        layout.label("Panels")
        for name, panel in self.panels:
            row = layout.row()

            row.label("   %s" % name, icon='BLANK1')
            row.label("Registered: %s" % getattr(panel, "is_registered", False))
            #row.label("Registered: %s" % hasattr(bpy.types, panel.bl_rna.name))
            if hasattr(panel, "bl_category"):
                row.label("bl_category: %s" % getattr(panel, "bl_category"))

    def draw_info(self, layout, context):
        if not self.info:
            return
        store = self._store
        '''
        # sanitize info dic STUPID IDEA, blanked out everything maybe __name__ for bl_idname at least
        
        for info_name in ["description", "location", "author", "version", "warning", "wiki_url"]:
            self.info.setdefault(info_name, "")
        '''
        row = layout.row()
        row.prop(store, "info_expand", icon='TRIA_DOWN' if store.info_expand else 'TRIA_RIGHT', icon_only=True, emboss=False)
        row.label("Information", icon='INFO')
        if store.info_expand:
            box = layout.box() # TODO FIX
            colsub = box.column()
            info = self.info
            try: # TODO take out sanitize should take care of it.
                if info.get("description"):
                    split = colsub.row().split(percentage=0.15)
                    split.label(text="Description:")
                    split.label(text=info["description"])
                if info.get("location"):
                    split = colsub.row().split(percentage=0.15)
                    split.label(text="Location:")
                    split.label(text=info["location"])
                if self.module:
                    split = colsub.row().split(percentage=0.15)
                    split.label(text="File:")
                    split.label(text=self.module.__file__, translate=False)
                if info.get("author"):
                    split = colsub.row().split(percentage=0.15)
                    split.label(text="Author:")
                    split.label(text=info["author"], translate=False)
                if info.get("version"):
                    split = colsub.row().split(percentage=0.15)
                    split.label(text="Version:")
                    split.label(text='.'.join(str(x) for x in info["version"]), translate=False)
                if info.get("warning"):
                    split = colsub.row().split(percentage=0.15)
                    split.label(text="Warning:")
                    split.label(text='  ' + info["warning"], icon='ERROR')
                    tot_row = bool(info.get("wiki_url")) # + bool(user_addon)

                    if tot_row:
                        split = colsub.row().split(percentage=0.15)
                        split.label(text="Internet:")
                        if info.get("wiki_url"):
                            split.operator("wm.url_open", text="Documentation", icon='HELP').url = info["wiki_url"]
                        split.operator("wm.url_open", text="Report a Bug", icon='URL').url = info.get(
                                "tracker_url",
                                "https://developer.blender.org/maniphest/task/edit/form/2")

            except KeyError:
                # shouldn't happen
                # TODO take out?
                print(KeyError)

    def draw(self, layout, context):
        row = layout.row(align=True)

        store = self._store
        row.prop(store, "expand", icon='TRIA_DOWN' if store.expand else 'TRIA_RIGHT', icon_only=True, emboss=False)
        sub = row.row()
        sub.prop(store, "enabled", icon='CHECKBOX_HLT' if self.enabled else 'CHECKBOX_DEHLT', icon_only=True, emboss=False)
        sub.enabled = not store.is_required # can't turn off if required
        sub = row.row()
        sub.enabled = store.enabled
        sub.label(self.info.get("description", self.name))
        if store.expand:
            self.draw_info(layout.column(), context)
            #layout.label("%s %s" % (store.enable, store.has_prefs))
            if store.enabled and store.has_prefs:
                layout.label("Preferences:")
                modbox = layout.box()
                
                pref = getattr(store, "preferences")
                pref.layout = modbox
                pref.draw(context)
            self.draw_panels(layout.column(), context)
            self.draw_operators(layout.column(), context)


    @property
    def panels(self):
        return self._get_classes("Panel")

    @property
    def addon_preferences(self):
        return self._get_classes("AddonPreferences")

    @property
    def operators(self):
        return self._get_classes("Operator")

    def __init__(self, name):
        self.name = name
        #module = __import__("%s.%s" % (__package__, name), {}, {}, name)
        print("INIT", __package__, name)
        module = import_module(".%s" % name, package=__package__)
        if reload_flag:
            import_reload(module)
        self.module = module
        self.info = getattr(self.module, "bl_info", {})
        self.prefsclass = self._get_pref_class()
        '''
        print("VARS", vars(module))
        print("GLOBALS", module.__spec__)
        '''

addons = {}
def create_addon_prefs(bl_idname, sub_modules_names, subaddonprefs={ "bl_idname": "",                 
                                         "draw": draw,
                                         "addons": {}
                                        }, addons={}):

    subaddonprefs["bl_idname"] = bl_idname
    for name, default_enabled, is_required in sub_modules_names:
        subaddon = SubAddon(name)
        mod = subaddon.module
        prefsclass = subaddon.prefsclass
        props = {}

        props["enabled"] = BoolProperty(update=subaddon.register_submodule(), default=default_enabled, description="Enable %s" % name)
        props["expand"] = BoolProperty(default=False)
        props["is_required"] = is_required
        if subaddon.info:
            props["info_expand"] = BoolProperty(default=False)

        props["has_prefs"] = prefsclass is not None
        if prefsclass:
            # build a property group from the addonspref class            
            addonprefs = type("%sAddonPreferences" % name, (PropertyGroup,), {k:v for k,v in vars(prefsclass).items() if not k.startswith("__")})
            #addonprefs.layout = None
            bpy.utils.register_class(addonprefs)
            props["preferences"] = PointerProperty(type=addonprefs)

        preferences = type("%sPreferences" % name, (PropertyGroup,), props)
        #classes.append(preferences)
        bpy.utils.register_class(preferences)
        #classes.append(preferences)
        subaddonprefs[name] = PointerProperty(type=preferences)
        subaddonprefs["addons"][name] = subaddon
        addons[name] = subaddon

    # make an addonspref 
    return type("AddonPrefs", (AddonPreferences,), subaddonprefs)


# Registration
def handle_registration(dummy, addons):
    if dummy:
        print("HANDLE REGO")
        for name, subaddon in addons.items():
            if subaddon.enabled:
                subaddon.register()
        
    else:
        print("HANDLE UNREGO")
        for name, subaddon in addons.items():
            if subaddon.enabled:
                subaddon.unregister()

    return None


