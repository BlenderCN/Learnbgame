import bpy
import os
import os.path as op
import glob
import re
from collections import defaultdict
import subprocess
import mmvt_utils as mu


try:
    import pdfkit
    PDFKIT_EXIST = True
except:
    PDFKIT_EXIST = False


def _addon():
    return ReportsPanel.addon


def wkhtmltopdf_exist():
    wkhtmltopdf_bin_path = op.join(mu.get_parent_fol(mu.get_user_fol()), 'reports')
    wkhtmltopdf_bin_name = 'wkhtmltopdf.exe' if mu.is_windows() else 'wkhtmltopdf'
    if not op.isfile(op.join(wkhtmltopdf_bin_path, wkhtmltopdf_bin_name)):
        print("Reports panel: Can't find wkhtmltopdf!" + \
            'Please download wkhtmltopdf ({}) and put it in {}'.format(
            'https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf', wkhtmltopdf_bin_path))
        return False
    os.environ["PATH"] += os.pathsep + wkhtmltopdf_bin_path
    if mu.is_windows():
        wkhtmltopdf = subprocess.Popen(
            ['where', 'wkhtmltopdf'], stdout=subprocess.PIPE).communicate()[0].strip()
    else:
        wkhtmltopdf = subprocess.Popen(
            ['which', 'wkhtmltopdf'], stdout=subprocess.PIPE).communicate()[0].strip()
    try:
        with open(wkhtmltopdf) as f:
            return True
    except IOError:
        print('Reports panel: No wkhtmltopdf executable found! ' + \
            '(https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf)')
        return False


def create_report():
    report_text = read_report_html()
    fields = parse_report_fields_from_text(report_text)
    for field in fields:
        report_text = report_text.replace(
            '~{}~'.format(field), ReportsPanel.fields_values[bpy.context.scene.reports_files][field])
    new_html_fname = op.join(_addon().get_output_path(), '{}.html'.format(
        bpy.context.scene.reports_files.replace(' ', '_')))
    with open(new_html_fname, 'w') as html_file:
        html_file.write(report_text)
    output_fname = mu.change_fname_extension(new_html_fname, 'pdf')
    pdfkit.from_file(new_html_fname, output_fname)
    try:
        import webbrowser
        webbrowser.open_new(output_fname)
    except:
        print('The new report can be found here: {}'.format(output_fname))
        pass


def read_report_html():
    fol = op.join(mu.get_parent_fol(mu.get_user_fol()), 'reports')
    report_fname = op.join(fol, '{}.html'.format(bpy.context.scene.reports_files.replace(' ', '_')))
    with open(report_fname, 'r') as f:
        report_text = f.read()
    return report_text


def parse_report_fields_from_text(report_text, return_indices=False):
    fields_finder = re.finditer('~[0-9A-Za-z _]+~', report_text)
    fields_indices = []
    fields_names = set()
    for m in fields_finder:
        fields_names.add(report_text[m.start() + 1: m.end() - 1])
        fields_indices.append((m.start(), m.end()))
    if return_indices:
        return fields_indices
    else:
        return fields_names


def parse_report_files_from_text(report_text):
    substr = 'src=~Images prefix~'
    files_finder = re.finditer(substr, report_text)
    files_names = set()
    for m in files_finder:
        start = m.start() + len(substr)
        end = report_text[start:].find(' ') + start
        files_names.add(report_text[start:end])
    ReportsPanel.files[bpy.context.scene.reports_files] = files_names


def reports_files_update(self, context):
    report_text = read_report_html()
    fields = sorted(parse_report_fields_from_text(report_text))[::-1]
    for field_name in fields:
        if field_name not in ReportsPanel.fields_values[bpy.context.scene.reports_files]:
            ReportsPanel.fields_values[bpy.context.scene.reports_files][field_name] = ''
    reports_items = [(c, c, '', ind) for ind, c in enumerate(fields)]
    bpy.types.Scene.reports_fields = bpy.props.EnumProperty(
        items=reports_items, update=reports_fields_update)
    parse_report_files_from_text(report_text)
    bpy.context.scene.report_use_script = bpy.context.scene.reports_files in _addon().get_scripts_names()
    # bpy.context.scene.reports_files = reports_items[0]


def reports_field_value_update(self, context):
    ReportsPanel.fields_values[bpy.context.scene.reports_files][bpy.context.scene.reports_fields] = \
        bpy.context.scene.reports_field_value


def reports_fields_update(self, context):
    bpy.context.scene.reports_field_value = \
        ReportsPanel.fields_values[bpy.context.scene.reports_files][bpy.context.scene.reports_fields]


def set_report_name(report_name):
    bpy.context.scene.reports_files = report_name


def get_report_name():
    return bpy.context.scene.reports_files


def get_report_files():
    return ReportsPanel.files[bpy.context.scene.reports_files]


def get_report_fields():
    fields = ReportsPanel.fields_values[bpy.context.scene.reports_files].copy()
    fields = {k.lower().replace(' ', '_'): v for k, v in fields.items()}
    return mu.Bag(fields)


def reports_draw(self, context):
    layout = self.layout
    missing_files = []
    layout.prop(context.scene, "reports_files", text="")
    row = layout.row(align=0)
    row.prop(context.scene, "reports_fields", text="")
    row.prop(context.scene, "reports_field_value", text="")
    if len(ReportsPanel.files[bpy.context.scene.reports_files]) > 0:
        missing_files = [file_name for file_name in ReportsPanel.files[bpy.context.scene.reports_files] if \
                         not op.isfile(op.join(_addon().get_output_path(), file_name))]
        if len(missing_files) > 0:
            layout.label('Missing files:')
            col = layout.box().column()
            for file_name in ReportsPanel.files[bpy.context.scene.reports_files]:
                if not op.isfile(op.join(_addon().get_output_path(), file_name)):
                    mu.add_box_line(col, file_name, '', 1)
    if context.scene.report_use_script:
        layout.prop(context.scene, 'report_use_script', text='Use script')
    if len(missing_files) == 0 or context.scene.report_use_script:
        layout.operator(CreateReport.bl_idname, text="Create report", icon='STYLUS_PRESSURE')


class CreateReport(bpy.types.Operator):
    bl_idname = "mmvt.create_report"
    bl_label = "Create report"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        if bpy.context.scene.report_use_script:
            _addon().run_script(bpy.context.scene.reports_files)
        else:
            create_report()
        return {'PASS_THROUGH'}


bpy.types.Scene.reports_files = bpy.props.EnumProperty(items=[])
bpy.types.Scene.reports_fields = bpy.props.EnumProperty(items=[], update=reports_fields_update)
bpy.types.Scene.reports_field_value = bpy.props.StringProperty(update=reports_field_value_update)
bpy.types.Scene.report_use_script = bpy.props.BoolProperty(False)


class ReportsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Reports"
    addon = None
    init = False
    fields_values = defaultdict(dict)
    files = defaultdict(list)

    def draw(self, context):
        if ReportsPanel.init:
            reports_draw(self, context)


def init(addon):
    ReportsPanel.addon = addon
    if not PDFKIT_EXIST:
        print('reports_panel: no pdfkit')
        return None
    if not wkhtmltopdf_exist():
        print('reports_panel: no wkhtmltopdf')
        return None
    user_fol = mu.get_user_fol()
    reports_files = glob.glob(op.join(mu.get_parent_fol(user_fol), 'reports', '*.html'))
    if len(reports_files) == 0:
        print('reports_panel: no reports')
        return None
    files_names = [mu.namebase(fname).replace('_', ' ') for fname in reports_files]
    reports_items = [(c, c, '', ind) for ind, c in enumerate(files_names)]
    bpy.types.Scene.reports_files = bpy.props.EnumProperty(
        items=reports_items, description="reports files", update=reports_files_update)
    bpy.context.scene.reports_files = files_names[0]
    bpy.context.scene.report_use_script = files_names[0] in _addon().get_scripts_names()
    register()
    ReportsPanel.init = True


def register():
    try:
        unregister()
        bpy.utils.register_class(ReportsPanel)
        bpy.utils.register_class(CreateReport)
    except:
        print("Can't register Reports Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(ReportsPanel)
        bpy.utils.unregister_class(CreateReport)
    except:
        pass
