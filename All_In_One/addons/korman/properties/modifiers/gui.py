#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import math
import bmesh
import mathutils
from bpy.props import *
from PyHSPlasma import *

from ...addon_prefs import game_versions
from .base import PlasmaModifierProperties, PlasmaModifierLogicWiz, PlasmaModifierUpgradable
from ... import idprops


journal_pfms = {
    pvPots : {
        # Supplied by the OfflineKI script:
        # https://gitlab.com/diafero/offline-ki/blob/master/offlineki/xSimpleJournal.py
        "filename": "xSimpleJournal.py",
        "attribs": (
            { 'id':  1, 'type': "ptAttribActivator", "name": "bookClickable" },
            { 'id':  2, 'type': "ptAttribString",    "name": "journalFileName" },
            { 'id':  3, 'type': "ptAttribBoolean",   "name": "isNotebook" },
            { 'id':  4, 'type': "ptAttribFloat",     "name": "BookWidth" },
            { 'id':  5, 'type': "ptAttribFloat",     "name": "BookHeight" },
        )
    },
    pvMoul : {
        "filename": "xJournalBookGUIPopup.py",
        "attribs": (
            { 'id':  1, 'type': "ptAttribActivator", 'name': "actClickableBook" },
            { 'id': 10, 'type': "ptAttribBoolean",   'name': "StartOpen" },
            { 'id': 11, 'type': "ptAttribFloat",     'name': "BookWidth" },
            { 'id': 12, 'type': "ptAttribFloat",     'name': "BookHeight" },
            { 'id': 13, 'type': "ptAttribString",    'name': "LocPath" },
            { 'id': 14, 'type': "ptAttribString",    'name': "GUIType" },
        )
    },
}

# Do not change the numeric IDs. They allow the list to be rearranged.
_languages = [("Dutch", "Nederlands", "Dutch", 0),
              ("English", "English", "", 1),
              ("Finnish", "Suomi", "Finnish", 2),
              ("French", "Français", "French", 3),
              ("German", "Deutsch", "German", 4),
              ("Hungarian", "Magyar", "Hungarian", 5),
              ("Italian", "Italiano ", "Italian", 6),
              # Blender 2.79b can't render 日本語 by default
              ("Japanese", "Nihongo", "Japanese", 7),
              ("Norwegian", "Norsk", "Norwegian", 8),
              ("Polish", "Polski", "Polish", 9),
              ("Romanian", "Română", "Romanian", 10),
              ("Russian", "Pyccĸий", "Russian", 11),
              ("Spanish", "Español", "Spanish", 12),
              ("Swedish", "Svenska", "Swedish", 13)]
languages = sorted(_languages, key=lambda x: x[1])
_DEFAULT_LANGUAGE_NAME = "English"
_DEFAULT_LANGUAGE_ID = 1


class ImageLibraryItem(bpy.types.PropertyGroup):
    image = bpy.props.PointerProperty(name="Image Item",
                                      description="Image stored for export.",
                                      type=bpy.types.Image,
                                      options=set())
    enabled = bpy.props.BoolProperty(name="Enabled",
                                     description="Specifies whether this image will be stored during export.",
                                     default=True,
                                     options=set())


class PlasmaImageLibraryModifier(PlasmaModifierProperties):
    pl_id = "imagelibmod"

    bl_category = "GUI"
    bl_label = "Image Library"
    bl_description = "A collection of images to be stored for later use"
    bl_icon = "RENDERLAYERS"

    images = CollectionProperty(name="Images", type=ImageLibraryItem, options=set())
    active_image_index = IntProperty(options={"HIDDEN"})

    def export(self, exporter, bo, so):
        if self.images:
            ilmod = exporter.mgr.find_create_object(plImageLibMod, so=so, name=self.key_name)

            for item in self.images:
                if item.image and item.enabled:
                    exporter.mesh.material.export_prepared_image(owner=ilmod, image=item.image, allowed_formats={"JPG", "PNG"}, extension="hsm")


class PlasmaJournalTranslation(bpy.types.PropertyGroup):
    def _poll_nonpytext(self, value):
        return not value.name.endswith(".py")

    language = EnumProperty(name="Language",
                            description="Language of this translation",
                            items=languages,
                            default=_DEFAULT_LANGUAGE_NAME,
                            options=set())
    text_id = PointerProperty(name="Journal Contents",
                              description="Text data block containing the journal's contents for this language",
                              type=bpy.types.Text,
                              poll=_poll_nonpytext,
                              options=set())


class PlasmaJournalBookModifier(PlasmaModifierProperties, PlasmaModifierLogicWiz):
    pl_id = "journalbookmod"

    bl_category = "GUI"
    bl_label = "Journal"
    bl_description = "Journal Book"
    bl_icon = "WORDWRAP_ON"

    versions = EnumProperty(name="Export Targets",
                            description="Plasma versions for which this journal exports",
                            items=game_versions,
                            options={"ENUM_FLAG"},
                            default={"pvMoul"})
    start_state = EnumProperty(name="Start",
                               description="State of journal when activated",
                               items=[("OPEN", "Open", "Journal will start opened to first page"),
                                      ("CLOSED", "Closed", "Journal will start closed showing cover")],
                               default="CLOSED")
    book_type = EnumProperty(name="Book Type",
                             description="GUI type to be used for the journal",
                             items=[("bkBook", "Book", "A journal written on worn, yellowed paper"),
                                    ("bkNotebook", "Notebook", "A journal written on white, lined paper")],
                             default="bkBook")
    book_scale_w = IntProperty(name="Book Width Scale",
                               description="Width scale",
                               default=100, min=0, max=100,
                               subtype="PERCENTAGE")
    book_scale_h = IntProperty(name="Book Height Scale",
                               description="Height scale",
                               default=100, min=0, max=100,
                               subtype="PERCENTAGE")
    clickable_region = PointerProperty(name="Region",
                                       description="Region inside which the avatar must stand to be able to open the journal (optional)",
                                       type=bpy.types.Object,
                                       poll=idprops.poll_mesh_objects)

    def _get_translation(self):
        # Ensure there is always a default (read: English) translation available.
        default_idx, default = next(((idx, translation) for idx, translation in enumerate(self.journal_translations)
                                    if translation.language == _DEFAULT_LANGUAGE_NAME), (None, None))
        if default is None:
            default_idx = len(self.journal_translations)
            default = self.journal_translations.add()
            default.language = _DEFAULT_LANGUAGE_NAME
        if self.active_translation_index < len(self.journal_translations):
            language = self.journal_translations[self.active_translation_index].language
        else:
            self.active_translation_index = default_idx
            language = default.language

        # Due to the fact that we are using IDs to keep the data from becoming insane on new
        # additions, we must return the integer id...
        return next((idx for key, _, _, idx in languages if key == language))

    def _set_translation(self, value):
        # We were given an int here, must change to a string
        language_name = next((key for key, _, _, i in languages if i == value))
        idx = next((idx for idx, translation in enumerate(self.journal_translations)
                   if translation.language == language_name), None)
        if idx is None:
            self.active_translation_index = len(self.journal_translations)
            translation = self.journal_translations.add()
            translation.language = language_name
        else:
            self.active_translation_index = idx

    journal_translations = CollectionProperty(name="Journal Translations",
                                              type=PlasmaJournalTranslation,
                                              options=set())
    active_translation_index = IntProperty(options={"HIDDEN"})
    active_translation = EnumProperty(name="Language",
                                      description="Language of this translation",
                                      items=languages,
                                      get=_get_translation, set=_set_translation,
                                      options=set())

    def export(self, exporter, bo, so):
        our_versions = (globals()[j] for j in self.versions)
        version = exporter.mgr.getVer()
        if version not in our_versions:
            # We aren't needed here
            exporter.report.port("Object '{}' has a JournalMod not enabled for export to the selected engine.  Skipping.",
                                 bo.name, version, indent=2)
            return

        # Export the Journal translation contents
        translations = [i for i in self.journal_translations if i.text_id is not None]
        if not translations:
            exporter.report.error("Journal '{}': No content translations available. The journal will not be exported.",
                                  bo.name, indent=2)
            return
        for i in translations:
            exporter.locman.add_journal(self.key_name, i.language, i.text_id, indent=2)

        if self.clickable_region is None:
            # Create a region for the clickable's condition
            rgn_mesh = bpy.data.meshes.new("{}_Journal_ClkRgn".format(self.key_name))
            self.temp_rgn = bpy.data.objects.new("{}_Journal_ClkRgn".format(self.key_name), rgn_mesh)
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=(6.0))
            bmesh.ops.transform(bm, matrix=mathutils.Matrix.Translation(bo.location - self.temp_rgn.location), space=self.temp_rgn.matrix_world, verts=bm.verts)
            bm.to_mesh(rgn_mesh)
            bm.free()

            # No need to enable the object as a Plasma object; we're exported automatically as part of the node tree.
            # It does need a page, however, so we'll put it in the same place as the journal object itself.
            self.temp_rgn.plasma_object.page = bo.plasma_object.page
            bpy.context.scene.objects.link(self.temp_rgn)
        else:
            # Use the region provided
            self.temp_rgn = self.clickable_region

        # Generate the logic nodes
        with self.generate_logic(bo, age_name=exporter.age_name, version=version) as tree:
            tree.export(exporter, bo, so)

        # Get rid of our temporary clickable region
        if self.clickable_region is None:
            bpy.context.scene.objects.unlink(self.temp_rgn)

    def logicwiz(self, bo, tree, age_name, version):
        nodes = tree.nodes

        # Assign journal script based on target version
        journal_pfm = journal_pfms[version]
        journalnode = nodes.new("PlasmaPythonFileNode")
        with journalnode.NoUpdate():
            journalnode.filename = journal_pfm["filename"]

            # Manually add required attributes to the PFM
            journal_attribs = journal_pfm["attribs"]
            for attr in journal_attribs:
                new_attr = journalnode.attributes.add()
                new_attr.attribute_id = attr["id"]
                new_attr.attribute_type = attr["type"]
                new_attr.attribute_name = attr["name"]
        journalnode.update()

        if version <= pvPots:
            self._create_pots_nodes(bo, nodes, journalnode, age_name)
        else:
            self._create_moul_nodes(bo, nodes, journalnode, age_name)

    def _create_pots_nodes(self, clickable_object, nodes, journalnode, age_name):
        clickable_region = nodes.new("PlasmaClickableRegionNode")
        clickable_region.region_object = self.temp_rgn

        facing_object = nodes.new("PlasmaFacingTargetNode")
        facing_object.directional = False
        facing_object.tolerance = math.degrees(-1)

        clickable = nodes.new("PlasmaClickableNode")
        clickable.link_input(clickable_region, "satisfies", "region")
        clickable.link_input(facing_object, "satisfies", "facing")
        clickable.link_output(journalnode, "satisfies", "bookClickable")
        clickable.clickable_object = clickable_object

        srcfile = nodes.new("PlasmaAttribStringNode")
        srcfile.link_output(journalnode, "pfm", "journalFileName")
        srcfile.value = self.key_name

        guitype = nodes.new("PlasmaAttribBoolNode")
        guitype.link_output(journalnode, "pfm", "isNotebook")
        guitype.value = self.book_type == "bkNotebook"

        width = nodes.new("PlasmaAttribIntNode")
        width.link_output(journalnode, "pfm", "BookWidth")
        width.value_float = self.book_scale_w / 100.0

        height = nodes.new("PlasmaAttribIntNode")
        height.link_output(journalnode, "pfm", "BookHeight")
        height.value_float = self.book_scale_h / 100.0

    def _create_moul_nodes(self, clickable_object, nodes, journalnode, age_name):
        clickable_region = nodes.new("PlasmaClickableRegionNode")
        clickable_region.region_object = self.temp_rgn

        facing_object = nodes.new("PlasmaFacingTargetNode")
        facing_object.directional = False
        facing_object.tolerance = math.degrees(-1)

        clickable = nodes.new("PlasmaClickableNode")
        clickable.link_input(clickable_region, "satisfies", "region")
        clickable.link_input(facing_object, "satisfies", "facing")
        clickable.link_output(journalnode, "satisfies", "actClickableBook")
        clickable.clickable_object = clickable_object

        start_open = nodes.new("PlasmaAttribBoolNode")
        start_open.link_output(journalnode, "pfm", "StartOpen")
        start_open.value = self.start_state == "OPEN"

        width = nodes.new("PlasmaAttribIntNode")
        width.link_output(journalnode, "pfm", "BookWidth")
        width.value_float = self.book_scale_w / 100.0

        height = nodes.new("PlasmaAttribIntNode")
        height.link_output(journalnode, "pfm", "BookHeight")
        height.value_float = self.book_scale_h / 100.0

        locpath = nodes.new("PlasmaAttribStringNode")
        locpath.link_output(journalnode, "pfm", "LocPath")
        locpath.value = "{}.Journals.{}".format(age_name, self.key_name)

        guitype = nodes.new("PlasmaAttribStringNode")
        guitype.link_output(journalnode, "pfm", "GUIType")
        guitype.value = self.book_type

    @property
    def requires_actor(self):
        # We are too late in the export to be harvested automatically, so let's be explicit
        return True
