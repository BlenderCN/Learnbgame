'''Property Definitions (bpy.props)
   This module defines properties to extend Blender's internal data. The result of these functions is used to assign properties to classes registered with Blender and can't be used directly.
   
   Note: All parameters to these functions must be passed as keywords.
'''


def BoolProperty(name="", description="", default=False, options={'ANIMATABLE'}, subtype='NONE', update=None, get=None, set=None):
   '''Returns a new boolean property definition.
      
      Arguments:
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].
      @subtype (string): Enumerator in ['PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME', 'DISTANCE', 'NONE'].
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      
      @get (function): Function to be called when this value is 'read',This function must take 1 value (self) and return the value of the property.
      
      @set (function): Function to be called when this value is 'written',This function must take 2 values (self, value) and return None.
      

   '''

   pass

def BoolVectorProperty(name="", description="", default=(False, False, False), options={'ANIMATABLE'}, subtype='NONE', size=3, update=None, get=None, set=None):
   '''Returns a new vector boolean property definition.
      
      Arguments:
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @default (sequence): sequence of booleans the length of *size*.
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].
      @subtype (string): Enumerator in ['COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION', 'MATRIX', 'EULER', 'QUATERNION', 'AXISANGLE', 'XYZ', 'COLOR_GAMMA', 'LAYER', 'NONE'].
      @size (int): Vector dimensions in [1, 32].
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      
      @get (function): Function to be called when this value is 'read',This function must take 1 value (self) and return the value of the property.
      
      @set (function): Function to be called when this value is 'written',This function must take 2 values (self, value) and return None.
      

   '''

   pass

def CollectionProperty(type=None, name="", description="", options={'ANIMATABLE'}):
   '''Returns a new collection property definition.
      
      Arguments:
      @type (class): A subclass of bpy.types.PropertyGroup or bpy.types.ID.
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].

   '''

   pass

def EnumProperty(items, name="", description="", default=None, options={'ANIMATABLE'}, update=None, get=None, set=None):
   '''Returns a new enumerator property definition.
      
      Arguments:
      @items (sequence of string tuples or a function): sequence of enum items formatted:[(identifier, name, description, icon, number), ...].
      The first three elements of the tuples are mandatory.
      :identifier: The identifier is used for Python access.
      :name: Name for the interace.
      :description: Used for documentation and tooltips.
      :icon: An icon string identifier or integer icon value
      (e.g. returned by bpy.types.UILayout.icon)
      :number: Unique value used as the identifier for this item (stored in file data).
      Use when the identifier may need to change. If the *ENUM_FLAG* option is used,
      the values are bitmasks and should be powers of two.
      When an item only contains 4 items they define (identifier, name, description, number).
      For dynamic values a callback can be passed which returns a list in
      the same format as the static list.
      This function must take 2 arguments (self, context), **context may be None**.
      .. warning::
      There is a known bug with using a callback,
      Python must keep a reference to the strings returned or Blender will misbehave
      or even crash.
      
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @default (string or set): The default value for this enum, a string from the identifiers used in *items*.If the *ENUM_FLAG* option is used this must be a set of such string identifiers instead.
      WARNING: It shall not be specified (or specified to its default *None* value) for dynamic enums
      (i.e. if a callback function is given as *items* parameter).
      
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'ENUM_FLAG', 'LIBRARY_EDITABLE'].
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      
      @get (function): Function to be called when this value is 'read',This function must take 1 value (self) and return the value of the property.
      
      @set (function): Function to be called when this value is 'written',This function must take 2 values (self, value) and return None.
      

   '''

   pass

def FloatProperty(name="", description="", default=0.0, min=sys.float_info.min, max=sys.float_info.max, soft_min=sys.float_info.min, soft_max=sys.float_info.max, step=3, precision=2, options={'ANIMATABLE'}, subtype='NONE', unit='NONE', update=None, get=None, set=None):
   '''Returns a new float property definition.
      
      Arguments:
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @min (float): Hard minimum, trying to assign a value below will silently assign this minimum instead.
      @max (float): Hard maximum, trying to assign a value above will silently assign this maximum instead.
      @soft_min (float): Soft minimum (>= *min*), user won't be able to drag the widget below this value in the UI.
      @soft_max (float): Soft maximum (<= *max*), user won't be able to drag the widget above this value in the UI.
      @step (int): Step of increment/decrement in UI, in [1, 100], defaults to 3 (WARNING: actual value is /100).
      @precision (int): Maximum number of decimal digits to display, in [0, 6].
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].
      @subtype (string): Enumerator in ['PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME', 'DISTANCE', 'NONE'].
      @unit (string): Enumerator in ['NONE', 'LENGTH', 'AREA', 'VOLUME', 'ROTATION', 'TIME', 'VELOCITY', 'ACCELERATION'].
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      
      @get (function): Function to be called when this value is 'read',This function must take 1 value (self) and return the value of the property.
      
      @set (function): Function to be called when this value is 'written',This function must take 2 values (self, value) and return None.
      

   '''

   pass

def FloatVectorProperty(name="", description="", default=(0.0, 0.0, 0.0), min=sys.float_info.min, max=sys.float_info.max, soft_min=sys.float_info.min, soft_max=sys.float_info.max, step=3, precision=2, options={'ANIMATABLE'}, subtype='NONE', unit='NONE', size=3, update=None, get=None, set=None):
   '''Returns a new vector float property definition.
      
      Arguments:
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @default (sequence): sequence of floats the length of *size*.
      @min (float): Hard minimum, trying to assign a value below will silently assign this minimum instead.
      @max (float): Hard maximum, trying to assign a value above will silently assign this maximum instead.
      @soft_min (float): Soft minimum (>= *min*), user won't be able to drag the widget below this value in the UI.
      @soft_max (float): Soft maximum (<= *max*), user won't be able to drag the widget above this value in the UI.
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].
      @step (int): Step of increment/decrement in UI, in [1, 100], defaults to 3 (WARNING: actual value is /100).
      @precision (int): Maximum number of decimal digits to display, in [0, 6].
      @subtype (string): Enumerator in ['COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION', 'MATRIX', 'EULER', 'QUATERNION', 'AXISANGLE', 'XYZ', 'COLOR_GAMMA', 'LAYER', 'NONE'].
      @unit (string): Enumerator in ['NONE', 'LENGTH', 'AREA', 'VOLUME', 'ROTATION', 'TIME', 'VELOCITY', 'ACCELERATION'].
      @size (int): Vector dimensions in [1, 32].
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      
      @get (function): Function to be called when this value is 'read',This function must take 1 value (self) and return the value of the property.
      
      @set (function): Function to be called when this value is 'written',This function must take 2 values (self, value) and return None.
      

   '''

   pass

def IntProperty(name="", description="", default=0, min=-2**31, max=2**31-1, soft_min=-2**31, soft_max=2**31-1, step=1, options={'ANIMATABLE'}, subtype='NONE', update=None, get=None, set=None):
   '''Returns a new int property definition.
      
      Arguments:
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @min (int): Hard minimum, trying to assign a value below will silently assign this minimum instead.
      @max (int): Hard maximum, trying to assign a value above will silently assign this maximum instead.
      @soft_max (int): Soft maximum (<= *max*), user won't be able to drag the widget above this value in the UI.
      @soft_min: Soft minimum (>= *min*), user won't be able to drag the widget below this value in the UI.
      @step (int): Step of increment/decrement in UI, in [1, 100], defaults to 1 (WARNING: unused currently!).
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].
      @subtype (string): Enumerator in ['PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR', 'ANGLE', 'TIME', 'DISTANCE', 'NONE'].
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      
      @get (function): Function to be called when this value is 'read',This function must take 1 value (self) and return the value of the property.
      
      @set (function): Function to be called when this value is 'written',This function must take 2 values (self, value) and return None.
      

   '''

   pass

def IntVectorProperty(name="", description="", default=(0, 0, 0), min=-2**31, max=2**31-1, soft_min=-2**31, soft_max=2**31-1, step=1, options={'ANIMATABLE'}, subtype='NONE', size=3, update=None, get=None, set=None):
   '''Returns a new vector int property definition.
      
      Arguments:
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @default (sequence): sequence of ints the length of *size*.
      @min (int): Hard minimum, trying to assign a value below will silently assign this minimum instead.
      @max (int): Hard maximum, trying to assign a value above will silently assign this maximum instead.
      @soft_min (int): Soft minimum (>= *min*), user won't be able to drag the widget below this value in the UI.
      @soft_max (int): Soft maximum (<= *max*), user won't be able to drag the widget above this value in the UI.
      @step (int): Step of increment/decrement in UI, in [1, 100], defaults to 1 (WARNING: unused currently!).
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].
      @subtype (string): Enumerator in ['COLOR', 'TRANSLATION', 'DIRECTION', 'VELOCITY', 'ACCELERATION', 'MATRIX', 'EULER', 'QUATERNION', 'AXISANGLE', 'XYZ', 'COLOR_GAMMA', 'LAYER', 'NONE'].
      @size (int): Vector dimensions in [1, 32].
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      
      @get (function): Function to be called when this value is 'read',This function must take 1 value (self) and return the value of the property.
      
      @set (function): Function to be called when this value is 'written',This function must take 2 values (self, value) and return None.
      

   '''

   pass

def PointerProperty(type=None, name="", description="", options={'ANIMATABLE'}, poll=None, update=None):
   '''Returns a new pointer property definition.
      
      Arguments:
      @type (class): A subclass of bpy.types.PropertyGroup or bpy.types.ID.
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].
      @poll (function): function to be called to determine whether an item is valid for this property.The function must take 2 values (self, object) and return Bool.
      
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      

   '''

   pass

def RemoveProperty(cls, attr):
   '''Removes a dynamically defined property.
      
      Arguments:
      @cls (type): The class containing the property (must be a positional argument).
      @attr (string): Property name (must be passed as a keyword).

      Note: Typically this function doesn't need to be accessed directly.Instead use del cls.attr
      
   '''

   pass

def StringProperty(name="", description="", default="", maxlen=0, options={'ANIMATABLE'}, subtype='NONE', update=None, get=None, set=None):
   '''Returns a new string property definition.
      
      Arguments:
      @name (string): Name used in the user interface.
      @description (string): Text used for the tooltip and api documentation.
      @default (string): initializer string.
      @maxlen (int): maximum length of the string.
      @options (set): Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', 'PROPORTIONAL','TEXTEDIT_UPDATE'].
      @subtype (string): Enumerator in ['FILE_PATH', 'DIR_PATH', 'FILE_NAME', 'BYTE_STRING', 'PASSWORD', 'NONE'].
      @update (function): Function to be called when this value is modified,This function must take 2 values (self, context) and return None.
      *Warning* there are no safety checks to avoid infinite recursion.
      
      @get (function): Function to be called when this value is 'read',This function must take 1 value (self) and return the value of the property.
      
      @set (function): Function to be called when this value is 'written',This function must take 2 values (self, value) and return None.
      

   '''

   pass

