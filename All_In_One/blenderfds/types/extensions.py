"""BlenderFDS, extended Blender types"""

import bpy
from blenderfds.types.results import BFResult, BFException
from blenderfds.types.collections import BFList, BFAutoItem
from blenderfds.types.interfaces import BFCommon, BFNamelist
from blenderfds.lib import fds_surf, fds_to_py, version
from blenderfds import geometry

DEBUG = False

### Blender Object <-> BFObject <-> FDS geometric entity (eg. OBST, VENT, HOLE...)

class BFObject(BFCommon):
    """Extend Blender object type"""

    def _get_idname(self) -> "str": return self.name

    idname = property(_get_idname)

    # UI
    # Panel generation is handled in ui/panels.py
    # draw_messages() is inherited

    # Export (me and children)

    def _get_bf_namelist(self):
        """Get my bf_namelist"""
        return BFNamelist.bf_list[self.bf_namelist_idname]

    def _set_bf_namelist(self, bf_namelist):
        """Set my bf_namelist"""
        self.bf_namelist_idname = bf_namelist.idname
        
    # This is an element that has one BFNamelist: Object, Material
    bf_namelist = property(_get_bf_namelist, _set_bf_namelist)

    def _get_children(self) -> "BFList of BFNamelist and Blender objects, never None":
        """Get children: bf_namelist related to self, children objects."""
        # Init
        children = list()
        context = bpy.context
        # Get my bf_namelist, if self is a MESH
        if self.type == "MESH": children.append(self.bf_namelist) 
        # Get children objects
        obs = list(ob for ob in context.scene.objects \
            if ob.type in ("MESH", "EMPTY",) and ob.parent == self and ob.bf_export)
        # Alphabetic order by element name
        obs.sort(key=lambda k:k.name)
        children.extend(obs)
        return BFList(children)

    children = property(_get_children)

    def get_exported(self, context, element=None) -> "bool": # 'element' kept for polymorphism
        """Return True if self is exported to FDS."""
        return True

    def get_my_res(self, context, element, ui=False) -> "BFResult or None": # 'element' kept for polymorphism
        """Get my BFResult. On error raise BFException."""
        if not self.get_exported(context, element): return None
        if self.type == "EMPTY" and not ui: msg = self.bf_fyi or " " # FIXME hackish
        else: msg = None
        return BFResult(sender=self, msg=msg)

    def get_res(self, context, element=None, ui=False) -> "BFResult or None": # 'element' kept for polymorphism
        """Get full BFResult (children and mine). On error raise BFException."""
        if DEBUG: print("BFDS: BFObject.get_res:", self.idname)
        return BFCommon.get_res(self, context, self, ui) # 'self' replaces 'element' as reference
    
    def to_fds(self, context=None) -> "str or None":
        """Export me in FDS notation, on error raise BFException."""
        if not context: context = bpy.context
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        res = self.get_res(context, self)
        if res: return res.value
        w.cursor_modal_restore()

def update_ob_bf_namelist_idname(self, context):
    """Update function for object.bf_namelist_idname bpy_prop"""
    # Del all tmp_objects, if self has one
    if self.bf_has_tmp: geometry.tmp.del_all_tmp_objects(context)
    # Set all geometries to NONE, as different namelists have different geometric possibilities
    self.bf_xb, self.bf_xyz, self.bf_pb = "NONE", "NONE", "NONE"

# System properties

bpy.types.Object.bf_export = bpy.props.BoolProperty(
    name="Export", description="Set if object is exported to FDS", default=True)
    
bpy.types.Object.bf_namelist_idname = bpy.props.EnumProperty( # link to related BFNamelist
    name="Namelist", description="Type of FDS namelist",
    items=(("bf_obst","OBST","OBST",1000),), default="bf_obst", update=update_ob_bf_namelist_idname) # items are updated later

bpy.types.Object.bf_is_tmp = bpy.props.BoolProperty(
    name="Is Tmp", description="Set if this element is tmp", default=False)

bpy.types.Object.bf_has_tmp = bpy.props.BoolProperty(
    name="Has Tmp", description="Set if this element has a visible tmp element companion", default=False)

bpy.types.Object.bf_fyi = bpy.props.StringProperty(
    name="FYI", description="Object description", maxlen=128)

bpy.types.Object.bf_free = bpy.props.StringProperty(
    name="Free",
    description="Free parameters, use matched single quotes as string delimiters, eg ABC='example'",
    maxlen=1024)

# These properties are left from old BlenderFDS to allow some transition
# and recognition of old files

bpy.types.Object.bf_nl = bpy.props.StringProperty(
        name="OLD Namelist",
        description="OLD Namelist group name")

# Add methods to original Blender type

bpy.types.Object.idname = BFObject.idname
bpy.types.Object.draw_messages = BFObject.draw_messages
bpy.types.Object.get_exported = BFObject.get_exported
bpy.types.Object.bf_namelist = BFObject.bf_namelist
bpy.types.Object.children = BFObject.children
bpy.types.Object.descendants = BFObject.descendants
bpy.types.Object._format = BFObject._format
bpy.types.Object._get_children_res = BFObject._get_children_res
bpy.types.Object.get_my_res = BFObject.get_my_res
bpy.types.Object.get_res = BFObject.get_res
bpy.types.Object.to_fds = BFObject.to_fds

### Blender Material <-> BFMaterial <-> FDS SURF

class BFMaterial(BFObject):
    """Extend Blender material type"""

    # UI
    # Panel generation is handled in ui/panels.py
    # draw_messages() is inherited

    # Export

    def _get_children(self) -> "BFList of Blender elements, never None":
        """Get children: bf_namelist related to self."""
        return BFList((self.bf_namelist,))

    children = property(_get_children)

# System properties

bpy.types.Material.bf_export = bpy.props.BoolProperty(
    name="Export", description="Set if material is exported to FDS", default=True)

bpy.types.Material.bf_namelist_idname = bpy.props.EnumProperty( # link to related BFNamelist
    name="Namelist", description="Type of FDS namelist",
    items=(("bf_surf","SURF","SURF",2000),), default="bf_surf") # items are updated later

bpy.types.Material.bf_fyi = bpy.props.StringProperty(
    name="FYI", description="Material description", maxlen=128)

bpy.types.Material.bf_free = bpy.props.StringProperty(
    name="Free",
    description="Free parameters, use matched single quotes as string delimiters, eg ABC='example'",
    maxlen=1024)

# Add methods to original Blender type

bpy.types.Material.idname = BFMaterial.idname
bpy.types.Material.draw_messages = BFMaterial.draw_messages
bpy.types.Material.get_exported = BFMaterial.get_exported
bpy.types.Material.bf_namelist = BFMaterial.bf_namelist
bpy.types.Material.children = BFMaterial.children
bpy.types.Material.descendants = BFMaterial.descendants
bpy.types.Material._format = BFMaterial._format
bpy.types.Material._get_children_res = BFMaterial._get_children_res
bpy.types.Material.get_my_res = BFMaterial.get_my_res
bpy.types.Material.get_res = BFMaterial.get_res
bpy.types.Material.to_fds = BFMaterial.to_fds

### Blender Scene <-> BFScene <-> FDS Case

class BFScene(BFObject):
    """Extend bpy.types.scene"""

    # UI
    # Panel generation is handled in ui/panels.py
    # draw_messages() is inherited

    # Export

    def _get_children(self) -> "BFList of Blender elements, never None":
        """Get children: bf_namelists related to Scene, objects in Scene, materials in Scene."""
        children = list()
        context = bpy.context
        # Get my bf_namelists
        children.extend([bf_namelist for bf_namelist in BFNamelist.bf_list if bf_namelist.bpy_type == bpy.types.Scene])
        # Get materials (export all not only referenced materials as before)
        mas = list(ma for ma in bpy.data.materials \
            if ma.bf_export and \
            (ma.name not in fds_surf.predefined))
        mas.sort(key=lambda k:k.name) # Alphabetic order by element name
        children.extend(mas)
        # Get objects
        obs = list(ob for ob in context.scene.objects \
            if ob.type in ("MESH", "EMPTY",) and ob.parent == None and ob.bf_export)
        obs.sort(key=lambda k:k.name) # Alphabetic order by element name
        children.extend(obs)
        # Return
        return BFList(children)

    children = property(_get_children)
            
    def get_my_res(self, context, element, ui=False) -> "BFResult or None":
        """Get my BFResult. On error raise BFException."""
        if ui: return None # No msg
        return BFResult(sender=self, value="&TAIL /\n") # closing namelist

    def to_ge1(self, context=None):
        """Export my geometry in FDS GE1 notation, on error raise BFException."""
        if not context: context = bpy.context
        return geometry.to_ge1.scene_to_ge1(context, self)

    # Import

    def from_fds(self, context=None, value=None) -> "None":
        """Import a text in FDS notation into self. On error raise BFException.
        Value is any text in good FDS notation.
        """
        # Init
        if not context: context = bpy.context
        # Cursor
        w = context.window_manager.windows[0]
        w.cursor_modal_set("WAIT")
        # Tokenize value and manage exception
        try: tokens = fds_to_py.tokenize(value)
        except Exception as err:
            w.cursor_modal_restore()
            raise BFException(sender=self, msg="Unrecognized FDS syntax, cannot import.")
        # Init
        free_texts = list()
        is_error_reported = False
        bf_namelist_choice = {bf_namelist.fds_label: (bf_namelist, bf_namelist.bpy_type) for bf_namelist in BFNamelist.bf_list} 
        # Handle tokens: create corresponding elements
        for index, token in enumerate(tokens):
            # Unpack
            element = None
            fds_original, fds_label, fds_value = token
            fds_props_dict = dict((prop[1], prop[2]) for prop in fds_value) # {fds_label: fds_value, ...}
            fds_props_set = set(prop[1] for prop in fds_value) # {fds_label, ...}
            # Prepare name
            fds_id = fds_props_dict.get("ID", "new {}".format(fds_label))
            # Try to create relative element. First, search for bf_namelist
            bf_namelist, bpy_type = bf_namelist_choice.get(fds_label, (None, None))
            if bf_namelist:
                # Supported bf_namelist found, create related element
                if bpy_type == bpy.types.Scene:
                    element = self
                elif bpy_type == bpy.types.Object:
                    element = geometry.utilities.get_new_object(context, name=fds_id)
                    element.bf_namelist_idname = bf_namelist.idname # link to found namelist
                elif bpy_type == bpy.types.Material:
                    element = geometry.utilities.get_new_material(context, name=fds_id)
                    element.bf_namelist_idname = "bf_surf" # link to generic SURF namelist
                    element.use_fake_user = True # Blender saves it even if it has no users
                else: raise ValueError("BFDS: BFScene.from_fds: Unrecognized namelist type!")
            else:
                # Free namelist. Is it geometric?
                if set(("XB", "XYZ", "PBX", "PBY", "PBZ")) & fds_props_set:
                    bf_namelist = BFNamelist.bf_list["bf_free"]
                    element = geometry.utilities.get_new_object(context, name=fds_id)
                    element.bf_namelist_idname = bf_namelist.idname
                    # Insert fds_label as first fds_value 
                    fds_value.insert(0, (fds_label, fds_label, None))
            # Element created?
            if element:
                # Try to set element properties
                try: bf_namelist.from_fds(context, element, fds_value)
                except BFException as child_err:
                    free_texts.append("".join(("! ERROR: {}\n".format(msg) for msg in child_err.labels)))
                    is_error_reported = True
                continue # go to the next token
            else:
                # Append original namelist to free_texts
                if DEBUG: print("BFDS: BFScene.from_fds: to free text:\n", fds_original) 
                free_texts.append(fds_original + "\n")
        # Write free text
        if free_texts:
            self.bf_head_free_text = "HEAD free text ({})".format(self.name)
            bpy.data.texts.new(self.bf_head_free_text)
            bpy.data.texts[self.bf_head_free_text].from_string("".join(free_texts))
        # Report error
        w.cursor_modal_restore()
        if is_error_reported: raise BFException(sender=self, msg="Errors reported while importing, see free text file.")

# System properties:

bpy.types.Scene.bf_file_version = bpy.props.IntVectorProperty(
    name="BlenderFDS File Version", description="BlenderFDS file format version", size=3, default=version.blenderfds_version)

# Add methods to original Blender type

bpy.types.Scene.idname = BFScene.idname
bpy.types.Scene.draw_messages = BFScene.draw_messages
bpy.types.Scene.get_exported = BFScene.get_exported
bpy.types.Scene.children = BFScene.children
bpy.types.Scene.descendants = BFScene.descendants
bpy.types.Scene._format = BFScene._format
bpy.types.Scene._get_children_res = BFScene._get_children_res
bpy.types.Scene.get_my_res = BFScene.get_my_res
bpy.types.Scene.get_res = BFScene.get_res
bpy.types.Scene.to_fds = BFScene.to_fds
bpy.types.Scene.to_ge1 = BFScene.to_ge1
bpy.types.Scene.from_fds = BFScene.from_fds

