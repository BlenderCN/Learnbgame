from . import operator


def menu(self, context):
    self.layout.operator(operator.Exporter.bl_idname, text="Export to .sls", icon='POSE_HLT')
