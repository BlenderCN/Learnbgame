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
from contextlib import contextmanager
from .explosions import NonfatalExportError
from .. import korlib
from . import logger
from pathlib import Path
from PyHSPlasma import *
import weakref
from xml.sax.saxutils import escape as xml_escape

_SP_LANGUAGES = {"English", "French", "German", "Italian", "Spanish"}

class LocalizationConverter:
    def __init__(self, exporter=None, **kwargs):
        if exporter is not None:
            self._exporter = weakref.ref(exporter)
            self._age_name = exporter.age_name
            self._report = exporter.report
            self._version = exporter.mgr.getVer()
        else:
            self._exporter = None
            self._age_name = kwargs.get("age_name")
            self._path = kwargs.get("path")
            self._version = kwargs.get("version")
        self._journals = {}
        self._strings = {}

    def add_journal(self, name, language, text_id, indent=0):
        if text_id.is_modified:
            self._report.warn("Journal '{}' translation for '{}' is modified on the disk but not reloaded in Blender.",
                              name, language, indent=indent)
        journal = self._journals.setdefault(name, {})
        journal[language] = text_id.as_string()

    def add_string(self, set_name, element_name, language, value):
        trans_set = self._strings.setdefault(set_name, {})
        trans_element = trans_set.setdefault(element_name, {})
        trans_element[language] = value

    @contextmanager
    def _generate_file(self, filename, **kwargs):
        if self._exporter is not None:
            with self._exporter().output.generate_dat_file(filename, **kwargs) as handle:
                yield handle
        else:
            dirname = kwargs.get("dirname", "dat")
            filepath = str(Path(self._path) / dirname / filename)
            handle = open(filepath, "wb")
            try:
                yield handle
            except:
                raise
            finally:
                handle.close()

    def _generate_journal_texts(self):
        age_name = self._age_name

        def write_journal_file(language, file_name, contents):
            try:
                with self._generate_file(dirname="ageresources", filename=file_name) as stream:
                    stream.write(contents.encode("windows-1252"))
            except UnicodeEncodeError:
                self._report.warn("Translation '{}': Contents contains characters that cannot be used in this version of Plasma. They will appear as a '?' in game.",
                                   language, indent=2)

                # Yes, there are illegal characters... As a stopgap, we will export the file with
                # replacement characters ("?") just so it'll work dammit.
                stream.write(contents.encode("windows-1252", "replace"))
            return True

        for journal_name, translations in self._journals.items():
            self._report.msg("Copying Journal '{}'", journal_name, indent=1)
            for language_name, value in translations.items():
                if language_name not in _SP_LANGUAGES:
                    self._report.warn("Translation '{}' will not be used because it is not supported in this version of Plasma.",
                                      language_name, indent=2)
                    continue
                suffix = "_{}".format(language_name.lower()) if language_name != "English" else ""
                file_name = "{}--{}{}.txt".format(age_name, journal_name, suffix)
                write_journal_file(language_name, file_name, value)

            # Ensure that default (read: "English") journal is available
            if "English" not in translations:
                language_name, value = next(((language_name, value) for language_name, value in translations.items()
                                            if language_name in _SP_LANGUAGES), (None, None))
                if language_name is not None:
                    file_name = "{}--{}.txt".format(age_name, journal_name)
                    # If you manage to screw up this badly... Well, I am very sorry.
                    if write_journal_file(language_name, file_name, value):
                        self._report.warn("No 'English' translation available, so '{}' will be used as the default",
                                          language_name, indent=2)
                else:
                    self._report.port("No 'English' nor any other suitable default translation available", indent=2)

    def _generate_loc_file(self):
        # Only generate this junk if needed
        if not self._strings and not self._journals:
            return

        def write_line(value, *args, **kwargs):
            # tabs suck, then you die...
            whitespace = "    " * kwargs.pop("indent", 0)
            if args or kwargs:
                value = value.format(*args, **kwargs)
            line = "".join((whitespace, value, "\n"))
            stream.write(line.encode("utf-16_le"))

        age_name = self._age_name
        enc = plEncryptedStream.kEncAes if self._version == pvEoa else None
        file_name = "{}.loc".format(age_name)
        with self._generate_file(file_name, enc=enc) as stream:
            # UTF-16 little endian byte order mark
            stream.write(b"\xFF\xFE")

            write_line("<?xml version=\"1.0\" encoding=\"utf-16\"?>")
            write_line("<localizations>")
            write_line("<age name=\"{}\">", age_name, indent=1)

            # Arbitrary strings defined by something like a GUI or a node tree
            for set_name, elements in self._strings.items():
                write_line("<set name=\"{}\">", set_name, indent=2)
                for element_name, translations in elements.items():
                    write_line("<element name=\"{}\">", element_name, indent=3)
                    for language_name, value in translations.items():
                        write_line("<translation language=\"{language}\">{translation}</translation>",
                                   language=language_name, translation=xml_escape(value), indent=4)
                    write_line("</element>", indent=3)
                write_line("</set>", indent=2)

            # Journals
            if self._journals:
                write_line("<set name=\"Journals\">", indent=2)
                for journal_name, translations in self._journals.items():
                    write_line("<element name=\"{}\">", journal_name, indent=3)
                    for language_name, value in translations.items():
                        write_line("<translation language=\"{language}\">{translation}</translation>",
                                   language=language_name, translation=xml_escape(value), indent=4)
                    write_line("</element>", indent=3)
                write_line("</set>", indent=2)

            # Verbose XML junk...
            # <Deledrius> You call it verbose.  I call it unambiguously complete.
            write_line("</age>", indent=1)
            write_line("</localizations>")

    def run(self):
        age_props = bpy.context.scene.world.plasma_age
        loc_path = str(Path(self._path) / "dat" / "{}.loc".format(self._age_name))
        log = logger.ExportVerboseLogger if age_props.verbose else logger.ExportProgressLogger
        with korlib.ConsoleToggler(age_props.show_console), log(loc_path) as self._report:
            self._report.progress_add_step("Harvesting Journals")
            self._report.progress_add_step("Generating Localization")
            self._report.progress_start("Exporting Localization Data")

            self._run_harvest_journals()
            self._run_generate()

            # DONE
            self._report.progress_end()
            self._report.raise_errors()

    def _run_harvest_journals(self):
        objects = bpy.context.scene.objects
        self._report.progress_advance()
        self._report.progress_range = len(objects)
        inc_progress = self._report.progress_increment

        for i in objects:
            journal = i.plasma_modifiers.journalbookmod
            if journal.enabled:
                translations = [j for j in journal.journal_translations if j.text_id is not None]
                if not translations:
                    self._report.error("Journal '{}': No content translations available. The journal will not be exported.",
                                       i.name, indent=2)
                for j in translations:
                    self.add_journal(journal.key_name, j.language, j.text_id, indent=1)
            inc_progress()

    def _run_generate(self):
        self._report.progress_advance()
        self.save()

    def save(self):
        if self._version > pvPots:
            self._generate_loc_file()
        else:
            self._generate_journal_texts()
