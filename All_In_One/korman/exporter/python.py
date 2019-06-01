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
from pathlib import Path
from PyHSPlasma import *

from .explosions import ExportError
from . import logger
from .. import korlib
from ..plasma_magic import plasma_python_glue, very_very_special_python

class PythonPackageExporter:
    def __init__(self, filepath, version):
        self._filepath = filepath
        self._modules = {}
        self._pfms = {}
        self._version = version

    def _compyle(self, report):
        report.progress_advance()
        report.progress_range = len(self._modules) + len(self._pfms)
        inc_progress = report.progress_increment

        age = bpy.context.scene.world.plasma_age
        Text = bpy.types.Text
        if self._version <= pvPots:
            py_version = (2, 2)
        else:
            py_version = (2, 3)
        py_code = []

        for filename, source in self._pfms.items():
            if isinstance(source, Text):
                if not source.plasma_text.package and age.python_method != "all":
                    inc_progress()
                    continue
                code = source.as_string()
            else:
                code = source

            code = "{}\n\n{}\n".format(code, plasma_python_glue)
            success, result = korlib.compyle(filename, code, py_version, report, indent=1)
            if not success:
                raise ExportError("Failed to compyle '{}':\n{}".format(filename, result))
            py_code.append((filename, result))
            inc_progress()

        for filename, source in self._modules.items():
            if isinstance(source, Text):
                if not source.plasma_text.package and age.python_method != "all":
                    inc_progress()
                    continue
                code = source.as_string()
            else:
                code = source

            # no glue needed here, ma!
            success, result = korlib.compyle(filename, code, py_version, report, indent=1)
            if not success:
                raise ExportError("Failed to compyle '{}':\n{}".format(filename, result))
            py_code.append((filename, result))
            inc_progress()

        # man that was ugly...
        return py_code

    def _ensure_age_sdl_hook(self, report):
        age_props = bpy.context.scene.world.plasma_age
        if age_props.age_sdl:
            fixed_agename = korlib.replace_python2_identifier(age_props.age_name)
            py_filename = "{}.py".format(fixed_agename)
            age_py = self._modules.get(py_filename)
            if age_py is not None:
                del self._modules[py_filename]
                if age_py.plasma_text.package or age.python_method == "all":
                    self._pfms[py_filename] = age_py
                else:
                    report.warn("AgeSDL Python Script provided, but not requested for packing... Using default Python.", indent=1)
                    self._pfms[py_filename] = very_very_special_python.format(age_name=fixed_agename)
            else:
                report.msg("Packing default AgeSDL Python", indent=1)
                very_very_special_python.format(age_name=age_props.age_name)
                self._pfms[py_filename] = very_very_special_python.format(age_name=fixed_agename)

    def _harvest_pfms(self, report):
        objects = bpy.context.scene.objects
        report.progress_advance()
        report.progress_range = len(objects)
        inc_progress = report.progress_increment

        for i in objects:
            logic = i.plasma_modifiers.advanced_logic
            if i.plasma_object.enabled and logic.enabled:
                for j in logic.logic_groups:
                    tree_versions = (globals()[version] for version in j.version)
                    if self._version in tree_versions:
                        self._harvest_tree(j.node_tree)
            inc_progress()

    def _harvest_modules(self, report):
        texts = bpy.data.texts
        report.progress_advance()
        report.progress_range = len(texts)
        inc_progress = report.progress_increment

        for i in texts:
            if i.name.endswith(".py") and i.name not in self._pfms:
                self._modules.setdefault(i.name, i)
            inc_progress()

    def _harvest_tree(self, tree):
        # Search the node tree for any python file nodes. Any that we find are PFMs
        for i in tree.nodes:
            if i.bl_idname == "PlasmaPythonFileNode":
                if i.filename and i.text_id:
                    self._pfms.setdefault(i.filename, i.text_id)

    def run(self):
        """Runs a stripped-down version of the Exporter that only handles Python files"""
        age_props = bpy.context.scene.world.plasma_age
        log = logger.ExportVerboseLogger if age_props.verbose else logger.ExportProgressLogger
        with korlib.ConsoleToggler(age_props.show_console), log(self._filepath) as report:
            report.progress_add_step("Harvesting Plasma PythonFileMods")
            report.progress_add_step("Harvesting Helper Python Modules")
            report.progress_add_step("Compyling Python Code")
            report.progress_add_step("Packing Compyled Code")
            report.progress_start("PACKING PYTHON")

            # Harvest the Python code
            self._harvest_pfms(report)
            self._harvest_modules(report)
            self._ensure_age_sdl_hook(report)

            # Compyle and package the Python
            self._package_python(report)

            # DONE
            report.progress_end()
            report.raise_errors()

    def _package_python(self, report):
        py_code = self._compyle(report)
        if not py_code:
            report.error("No Python files were packaged.")
        self._write_python_pak(py_code, report)

    def _write_python_pak(self, py_code, report):
        report.progress_advance()

        if self._version == pvEoa:
            enc = plEncryptedStream.kEncAes
        elif self._version == pvMoul:
            enc = None
        else:
            enc = plEncryptedStream.kEncXtea

        if enc is None:
            stream = hsFileStream(self._version).open(self._filepath, fmCreate)
        else:
            stream = plEncryptedStream(self._version).open(self._filepath, fmCreate, enc)
        try:
            korlib.package_python(stream, py_code)
        finally:
            stream.close()
