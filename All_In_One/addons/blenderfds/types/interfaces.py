"""BlenderFDS, interface types"""

import bpy
from blenderfds.types.results import BFResult, BFException
from blenderfds.types.collections import BFList, BFAutoItem
from blenderfds.types.flags import *
from blenderfds.lib import fds_format
from blenderfds.lib.utilities import isiterable

DEBUG = False

### BFCommon

class BFCommon(BFAutoItem):
    """Common attributes and methods for all BF classes.
    
    idname -- Instance unique identificator. Type: string, never None. Eg: "bf_fyi"
    label -- UI label. Type: string, if None idname is used. Eg: "FYI"
    description -- UI help text. Type: string, None. Eg: "For your information"
    enum_id -- Instance unique numeric id for EnumProperty item. Type: int, never None. Eg: "1023"    
    flags -- define specific behaviours, see types.flags. Eg: NOUI | NOEXPORT
    fds_label -- FDS label. Type: string, if None this is a free property. Eg: "ID"
    bf_props -- List of related BFProp idnames. Type: tuple of strings, None.
    bf_prop_export -- idname of related export BFProp. Type: string, None. Eg: "bf_fyi_export"
    bf_prop_free -- idname of related free BFProp. Type: string, None. Eg: "bf_fyi_free"
    bf_other -- Other optional BlenderFDS parameters. Type: dict, None. Eg: "{'prop1': value1, 'prop2': value2}"
    bpy_type -- Blender type of self. Eg: bpy.types.Scene, bpy.types.Object, bpy.types.Material
    bpy_idname -- idname of related Blender property. Type: string, None. Eg: "bf_fyi" or "name".
    bpy_prop -- Blender property type. Type: bpy.props.*Property, if None refer to existing Blender property.
    **kwargs -- Other optional Blender property parameters. Eg: default = "NONE".
    """
    bf_list = BFList() # contains all instances of this class

    def __init__(self, idname, label=None, description=None, enum_id=0, flags=0, \
        fds_label=None, bf_props=None, bf_prop_export=None, bf_prop_free=None, bf_other=None, \
        bpy_type=None, bpy_idname=None, bpy_prop=None, **kwargs):
        # Check enum_id unicity
        if enum_id and enum_id in (item.enum_id for item in self.bf_list):
            raise ValueError("BFDS: Duplicated enum_id '{}' in '{}' and '{}'".format(enum_id, item.idname, idname))
        # Parent class
        BFAutoItem.__init__(self, idname=idname)
        # Identification
        self.label = label or idname
        self.description = description
        self.enum_id = enum_id
        self.flags = flags
        # Others
        self.fds_label = fds_label
        self.bpy_type = bpy_type
        # Set related bf_props instances: transform BFList of idname in BFList of BFProp
        if bf_props: self.bf_props = BFProp.bf_list[bf_props]
        else: self.bf_props = None
        # Set export BFProp: transform idname in BFProp or create new BFProp
        if bf_prop_export:
            try: self.bf_prop_export = BFProp.bf_list[bf_prop_export] # Does it esist?
            except KeyError: # No, create a default one
                self.bf_prop_export = BFProp(
                    idname = bf_prop_export,
                    label = "Export",
                    description = "Export to FDS",
                    bpy_idname = bf_prop_export,
                    bpy_prop = bpy.props.BoolProperty,
                    default = False,
                    )
        else: self.bf_prop_export = None
        # Set free BFProp: transform idname in BFProp, do not create default it shall exist
        if bf_prop_free: self.bf_prop_free = BFProp.bf_list[bf_prop_free]
        else: self.bf_prop_free = None
        # Set bf_other
        self.bf_other = bf_other
        # Set related Blender property
        self.bpy_idname = bpy_idname
        self.bpy_prop = bpy_prop
        self.bpy_other = kwargs

    # Register/Unregister (me, each from self.bf_props, self.bf_prop_export, self.bf_prop_free)

    def register(self, bpy_type=None):
        """Register all related Blender properties."""
        # Get bpy_type: mine or that sent as parameter from caller object
        if not bpy_type: bpy_type = self.bpy_type
        # Register children, export and free BFProp
        for child in self.children: child.register(bpy_type)
        if self.bf_prop_export: self.bf_prop_export.register(bpy_type)
        if self.bf_prop_free: self.bf_prop_free.register(bpy_type)
        # Register my own Blender property
        if self.bpy_prop and self.bpy_idname:
            if DEBUG: print("BFDS: BFCommon.register:", bpy_type, self.bpy_idname) 
            setattr(bpy_type, self.bpy_idname, \
                self.bpy_prop(name=self.label, description=self.description, **self.bpy_other))

    def unregister(self, bpy_type=None):
        """Unregister all related Blender properties."""
        # Get bpy_type: mine or that sent as parameter from caller object
        if not bpy_type: bpy_type = self.bpy_type
        # Unregister children, export and free BFProp
        for child in self.children: child.unregister(bpy_type)
        if self.bf_prop_export: self.bf_prop_export.unregister(bpy_type)
        if self.bf_prop_free: self.bf_prop_free.unregister(bpy_type)
        # and unregister my own Blender property
        if self.bpy_idname:
            if DEBUG: print("BFDS: BFCommon.unregister:", bpy_type, self.bpy_idname) 
            try: delattr(bpy_type, self.bpy_idname)
            except: pass

    # UI
    
    def has_ui(self, context, element) -> "bool":
        """Return True if self has an user interface."""
        if self.flags & NOUI: return False
        return True

    def has_active_ui(self, context, element) -> "bool":
        """Return True if self has an active user interface."""
        if self.flags & ACTIVEUI: return True
        return self.get_exported(context, element) or False

    def _draw_extra(self, layout, context, element):
        """Draw extra customized widgets."""
        pass

    def draw_messages(self, layout, context, element):
        """Draw messages and exceptions."""
        try: res = self.get_my_res(context, element, ui=True)
        except BFException as err: err.draw(layout)
        else: res and res.draw(layout) # Check res existence before...    

    # Export

    def get_exported(self, context, element) -> "bool":
        """Return True if self is exported to FDS."""
        if self.flags & NOEXPORT: return False
        try: return self.bf_prop_export.get_value(context, element)
        except: return True

    def _get_children(self) -> "BFList of BFProps, never None":
        """Get my children, bf_prop_export is not a children."""
        children = BFList()
        if self.bf_props: children.extend(self.bf_props) # self.bf_props could be None
        if self.bf_prop_free: children.append(self.bf_prop_free) # self.bf_prop_free could be None
        return children
    
    children = property(_get_children)

    def _get_children_res(self, context, element, ui=False) -> "BFList of BFResult, never None":
        """Return a BFlist of children BFResult. On error raise joined BFException."""
        if DEBUG: print("BFDS: BFCommon._get_children_res:", self.idname, element.idname) 
        # Init
        children, children_res, err_msgs = self.children, BFList(), list()
        # Get children res, manage exceptions
        for index, child in enumerate(children):
            try: child_res = child.get_res(context, element, ui=False)
            except BFException as child_err:
                # The child sends exceptions, take note. Labels attach sender name to msgs.
                err_msgs.extend(child_err.labels)
            else:
                # The child did not send a result, continue
                if child_res is None: continue
                # The child result is appended to the BFList
                children_res.append(child_res) 
        # Return
        if err_msgs: raise BFException(sender=self, msgs=err_msgs) # Raise all piled exceptions to parent
        return children_res

    def _format(self, context, element, my_res, children_res) -> "str or None":
        """Format to FDS notation. On error raise BFException."""
        # Expected output:
        #   ! Me: Message               < my_res.labels
        #   ! Me: Children1: Message    < body < children_res values
        #   Children1 body
        #   ! Me: Children2: Message
        #   Children2 body
        #   My value                    < my_res.value
        return "".join((
            fds_format.to_comment(my_res.labels),
            "".join(child_res.value or str() for child_res in children_res or tuple()), # child_res.value could be None
            my_res.value or str(), # my_res.value could be None
        ))

    def get_my_res(self, context, element, ui=False) -> "BFResult or None":
        """Get my BFResult. On error raise BFException."""
        # Check me exported 
        if not self.get_exported(context, element): return None
        # Here you can set a value, append msgs, append relevant operators.
        # When something is not good you should raise a BFException.
        # When ui is calling, do not perform heavy or useless calculations.
        return BFResult(
            sender = self,
            value = DEBUG and "! Debug value from BFCommon.get_my_res of '{}'\n".format(self.idname) or None, 
            msg = DEBUG and "Debug message from BFCommon.get_my_res of '{}'".format(self.idname) or None, 
        )

    def get_res(self, context, element, ui=False) -> "BFResult or None":
        """Get full BFResult (children and mine). On error raise BFException."""
        # Init
        my_res = self.get_my_res(context, element, ui)
        if not my_res: return None
        children_res = self._get_children_res(context, element, ui)
        # Format value and return
        my_res.value = self._format(context, element, my_res, children_res)
        return my_res
   
    # Import

    def set_exported(self, context, element, value=True) -> "bool":
        """Set if self is exported to FDS."""
        if element and hasattr(self, "bf_prop_export") and self.bf_prop_export: self.bf_prop_export.set_value(context, element, value)

    # Other

    def _get_descendants(self) -> "Same as self.children":
        """Get my children and the children of my children..."""
        children = descendants = self.children # self.children is never None
        for child in children or list(): descendants.extend(child.descendants)
        return descendants
    
    descendants = property(_get_descendants)

    # Precision for float types
    
    def _get_precision(self) -> "int":
        """Get my precision for element or default to 2."""
        return self.bpy_other.get("precision", 2)

    precision = property(_get_precision)

    # Menu item for EnumProperty

    def _get_enumproperty_item(self) -> "tuple":
        """Get item for EnumProperty items."""
        if self.flags & NOUI: return None
        description = self.description and "{} ({})".format(self.label, self.description) or self.label
        return (self.idname, description, description, self.enum_id)

    enumproperty_item = property(_get_enumproperty_item)

### Blender property <-> BFProp <-> FDS parameter

class BFProp(BFCommon):
    """BlenderFDS property, interface between a Blender property and an FDS parameter. See BFCommon."""
    bf_list = BFList() # contains all instances of this class

    def __init__(self, idname, label=None, description=None, flags=0, \
        fds_label=None, bf_props=None, bf_prop_export=None, bf_other=None, \
        bpy_idname=None, bpy_prop=None, **kwargs):
        # Parent class, partially use its features
        BFCommon.__init__(self, idname=idname, label=label, description=description, flags=flags,\
            fds_label=fds_label, bf_props=bf_props, bf_prop_export=bf_prop_export, bf_other=bf_other, \
            bpy_idname=bpy_idname, bpy_prop=bpy_prop, **kwargs)

    # UI: draw panel (self.bf_prop_export, me)
    # Override methods for custom panel

    def _get_layout(self, layout, context, element) -> "layout":
        """If self has a bf_prop_export, prepare double-column Blender panel layout."""
        layout = layout.row()
        if self.bf_prop_export:
            # Set two distinct colums: layout_export and layout_ui
            layout_export, layout = layout.column(), layout.column()
            layout_export.prop(element, self.bf_prop_export.bpy_idname, text="")
        else:
            # Set one only column
            layout = layout.column()
        layout.active = bool(self.has_active_ui(context, element)) # bool( protects from None
        return layout

    def _draw_body(self, layout, context, element):
        """Draw my part of panel body."""
        if not self.bpy_idname: return
        row = layout.row()
        row.prop(element, self.bpy_idname, text=self.label)

    def draw(self, layout, context, element):
        """Draw my part of Blender panel."""
        if self.has_ui(context, element):
            layout = self._get_layout(layout, context, element)
            self._draw_body(layout, context, element)
            self._draw_extra(layout, context, element)
            self.draw_messages(layout, context, element)

    # Export (only me, not self.bf_props)
    # get_my_res and _get_children_res are not used
    
    # Override the get_exported() method for special exporting logic.
    # Override the get_value() method for specific calculations on my value or raise special BFExceptions
    # Override the _format_value() method for specific formatting
    # Override the get_res() method to send informative msgs or raise special BFExceptions
    # The get_res() method is also used to draw the same messages and exceptions on the UI panel

    def get_value(self, context, element) -> "any or None":
        """Get my Blender property value for element. On error raise BFException."""
        return getattr(element, self.bpy_idname or str(), None) # None is not accepted as attribute name, replaced with str()
        
    def _format_value(self, context, element, value) -> "str or None":
        """Format value in FDS notation for me. On error raise BFException."""
        # Expected output:
        #   ID='example' or PI=3.14 or COLOR=3,4,5
        # Free parameters (no self.fds_label) needs special treatment in fds.props or fds.props_geometry
        if value is None: return None
        # If value is not an iterable, then put it in a tuple
        if not isiterable(value): values = tuple((value,)) 
        else: values = value
        # Check first element of the iterable and choose formatting
        if   isinstance(values[0], bool):  value = ",".join(value and ".TRUE." or ".FALSE." for value in values)
        elif isinstance(values[0], int):   value = ",".join(str(value) for value in values)
        elif isinstance(values[0], float): value = ",".join("{:.{}f}".format(value, self.precision) for value in values)
        else: value = ",".join("'{}'".format(value) for value in values)
        return "=".join((self.fds_label, value))

    def get_my_res(self, context, element, ui=False) -> "BFResult or None":
        """Get my BFResult. On error raise BFException."""
        if not self.get_exported(context, element): return None
        res = BFResult(
            sender = self,
            msg = DEBUG and "Debug message from BFProp.get_my_res of '{}'".format(self.idname) or None, 
        )
        value = self.get_value(context, element)
        if not ui: res.value = self._format_value(context, element, value)
        return res

    def get_res(self, context, element, ui=False) -> "BFResult or None":
        """Get full BFResult (children and mine). On error raise BFException."""
        return self.get_my_res(context, element, ui)    

    # Import

    def set_value(self, context, element, value):
        """Set my Blender property value for element. On error raise BFException.
        Value is any type of data compatible with bpy_prop
        Eg: "String", (0.2,3.4,1.2), ...
        """
        try: setattr(element, self.bpy_idname, value)
        except: raise BFException(
            sender = self,
            msg = "Error setting '{}' to '{}.{}'".format(value, element.name, str(self.bpy_idname)),
        )

    def from_fds(self, context, element, value):
        """Set my value from value in FDS notation for element. On error raise BFException.
        Value is any type of data compatible with bpy_prop
        Eg: "String", (0.2,3.4,1.2), ...
        """
        self.set_exported(context, element, True)
        self.set_value(context, element, value)

# Expose collection

bf_props = BFProp.bf_list

### Blender group of variables or panel <-> BFNamelist <-> FDS namelist

class BFNamelist(BFCommon):
    """BlenderFDS namelist, interface between a Blender object and an FDS namelist. See BFCommon."""
    bf_list = BFList() # contains all instances of this class

    def __init__(self, idname, label=None, description=None, enum_id=0, flags=0, \
        fds_label=None, bf_props=None, bf_prop_export=None, bf_prop_free=None, bf_other=None, \
        bpy_type=None):
        # Parent class, partially use its features
        BFCommon.__init__(self, idname=idname, label=label, description=description, enum_id=enum_id, flags=flags, \
            fds_label=fds_label, bf_props=bf_props, bf_prop_export=bf_prop_export, bf_prop_free=bf_prop_free, bf_other=bf_other, \
            bpy_type=bpy_type)

    # UI: draw panel (me, self.bf_prop_export, self.bf_props, self.bf_prop_free)
    # Override methods for custom panel
    
    def draw_header(self, layout, context, element):
        """Draw Blender panel header."""
        if self.bf_prop_export: layout.prop(element, self.bf_prop_export.bpy_idname, text="")
        if self.description: return "BlenderFDS {} ({})".format(self.label, self.description)
        return "BlenderFDS {}".format(self.label)
    
    def _get_layout(self, layout, context, element) -> "layout":
        """If self has a bf_prop_export, prepare Blender panel layout."""
        layout.active = bool(self.has_active_ui(context, element)) # bool( protects from None
        return layout

    def _draw_body(self, layout, context, element):
        """Draw panel body."""
        for bf_prop in self.bf_props or tuple(): bf_prop.draw(layout, context, element)
        if self.bf_prop_free: self.bf_prop_free.draw(layout, context, element)

    def draw(self, layout, context, element):
        """Draw Blender panel."""
        if self.has_ui(context, element):
            layout = self._get_layout(layout, context, element)
            self.draw_messages(layout, context, element)
            self._draw_body(layout, context, element)
            self._draw_extra(layout, context, element)

    # Export (me and children)
    # Override the get_exported() method for special exporting logic.
    # Override the _format() method for specific formatting
    # Override the get_my_res() method to send informative msgs, special values or raise special BFExceptions
    # The get_my_res() method is also used to draw the same messages and exceptions on the UI panel
    # Override the get_res() method to send informative msgs or raise special BFExceptions

    # Single ID is sent from bf_id BFProp,
    # multiple ID is embedded in multivalues coming from geometric BFProp

    def _format(self, context, element, my_res, children_res) -> "str or None":
        """Format to FDS notation. On error raise BFException."""
        # Expected output:
        #   ! OBST: Message                 < my_res.labels
        #   ! OBST: ID: Message               + children labels (from self.bf_props)
        #   ! OBST: XB: Message
        #   &OBST ID='example' XB=... /\n   < body < c_multivalue[0] + c_value
        #   &OBST ID='example' XB=... /\n            c_multivalue[1] + c_value
        #   &XXXX P1=... /\n                < my_res.value
        # Append children messages to my messages (children are self.bf_props)
        my_res.msgs.extend(label for child_res in children_res for label in child_res.labels)
        # Search and extract the first (and should be only) multivalue from children values     
        child_multivalues = None
        for child_res in children_res:
            if isiterable(child_res.value):
                # Set the multivalue and remove multivalue child_res from single value children_res
                child_multivalues = child_res.value
                children_res.remove(child_res)
                # Each multivalue contains its multi ID, then remove ordinary single ID sent by "bf_id"
                children_res.remove(children_res["bf_id"])
                break
        # Set fds_label: use self.fds_label or last children_res value, that should be bf_free
        # When using last children value, remove child from BFList 
        if self.fds_label: fds_label = self.fds_label
        else: fds_label = children_res.pop().value
        # Join children values
        children_value = " ".join(child_res.value for child_res in children_res if child_res.value)
        # Build body: When multivalue exists, ID is embedded into each child_multivalue;
        # else ID is embedded into children_value
        if child_multivalues: body = "".join("&{} {} {} /\n".format(
            fds_label, child_multivalue, children_value,
            ) for child_multivalue in child_multivalues
        )
        else: body = "&{} {} /\n".format(fds_label, children_value)
        # Return
        return "".join((
            fds_format.to_comment(my_res.labels),
            body,
            my_res.value or str(), # my_res.value could be None
        ))

    # Import

    def from_fds(self, context, element, tokens) -> "None":
        """Translate and set FDS tokens to myself for element.
        On error raise BFException (trapped by parent from_fds method).
        tokens -- ((fds_original, fds_label, fds_value), ...)
            Eg: (("ID='example'", "ID", "example"), ("XB=...", "XB", (1., 2., 3., 4., 5., 6.,)), ...)
        """
        # Init
        if DEBUG: print("BFDS: BFNamelist.from_fds: <{}>, <{}>\n".format(self.idname, element.name), tokens)
        if not tokens: return
        # Order tokens: SURF_ID needs a working mesh, so treat last
        tokens.sort(key=lambda k:k[1]==("SURF_ID")) # Order is: False then True
        # Set my exporting and appearance (see props.py for definition)
        self.set_exported(context, element, True)
        if self.bf_other:
            if "show_transparent" in self.bf_other: element.show_transparent = self.bf_other["show_transparent"]
            if "draw_type" in self.bf_other: element.draw_type = self.bf_other["draw_type"]
            if "hide" in self.bf_other: element.hide = self.bf_other["hide"]
            if "hide_select" in self.bf_other: element.hide_select = self.bf_other["hide_select"]
        # For each token set corresponding descendant or free_texts
        err_msgs, free_texts = list(), list()
        for token in tokens:
            fds_original, fds_label, fds_value = token
            is_token_imported = False
            # Search the corresponding descendant by fds_label and try to set its fds_value
            for descendant in self.descendants:
                if descendant.fds_label == fds_label:            
                    # fds_label corresponding
                    try: descendant.from_fds(context, element, fds_value)
                    except BFException as descendant_err:
                        err_msgs.extend(descendant_err.labels) # The descendant sends exceptions, take note.
                    else: is_token_imported = True # succesful import
                    break # end the search for descendants
            # Check if import was succesful
            if not is_token_imported:
                # The token could not be imported because of
                # a raised exception or corresponding descendant not found,
                # so pile the original token into free_texts.
                if DEBUG: print("BFDS: BFNamelist.from_fds: to free param:\n ", fds_original) 
                free_texts.append(fds_original)
        # Set final bf_prop_free. If no self.bf_prop_free, then the saved fds_origins are lost
        if free_texts and self.bf_prop_free:
            self.bf_prop_free.set_value(context, element, " ".join(free_texts)) # Set new value
        # Raise all piled exceptions to parent
        if err_msgs: raise BFException(sender=self, msgs=err_msgs)

# Expose collection

bf_namelists = BFNamelist.bf_list

