import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper

import json

from . import utils
from .utils import MultiCamContext
from .multicam_fade import MultiCamFaderProperties

class MultiCamExport(bpy.types.Operator, ExportHelper, MultiCamContext):
    bl_idname = 'sequencer.export_multicam'
    bl_label = 'Export Multicam'
    filename_ext = '.json'
    def get_cuts(self, scene, mc_strip):
        d = {}
        data_path = '.'.join([mc_strip.path_from_id(), 'multicam_source'])
        fcurve = utils.get_fcurve(scene, data_path)
        if fcurve is not None:
            for kf in fcurve.keyframe_points:
                key = str(kf.co[0])
                d[key] = kf.co[1]
        return d
    def execute(self, context):
        mc_strip = self.get_strip(context)
        data = {}
        props = MultiCamFaderProperties.get_for_strip(mc_strip)
        if props is not None:
            data['fades'] = props.serialize()
        data['cuts'] = self.get_cuts(context.scene, mc_strip)
        with open(self.filepath, 'w') as f:
            f.write(json.dumps(data, indent=2))
        return {'FINISHED'}
    
class MultiCamImport(bpy.types.Operator, ImportHelper, MultiCamContext):
    bl_idname = 'sequencer.import_multicam'
    bl_label = 'Import Multicam'
    filename_ext = '.json'
    def execute(self, context):
        with open(self.filepath, 'r') as f:
            data = json.loads(f.read())
        mc_strip = self.get_strip(context)
        props, created = MultiCamFaderProperties.get_or_create(mc_strip=mc_strip)
        for key, fade_data in data.get('fades', {}).items():
            for attr in ['start_frame', 'end_frame']:
                fade = props.get_fade_in_range(fade_data['start_frame'])
                if fade is not None:
                    props.remove_fade(fade)
            props.add_fade(**fade_data)
        data_path = '.'.join([mc_strip.path_from_id(), 'multicam_source'])
        fcurve = utils.get_or_create_fcurve(context.scene, data_path)
        for key, source in data.get('cuts', {}).items():
            frame = float(key)
            fade = props.get_fade_in_range(frame)
            if fade is not None:
                continue
            if fcurve is None:
                mc_strip.keyframe_insert('multicam_source', frame=frame)
                fcurve = utils.get_fcurve(context.scene, data_path)
                kf = utils.get_keyframe(fcurve, frame)
                kf.co[1] = source
                kf.interpolation = 'CONSTANT'
            else:
                utils.set_keyframe(fcurve, frame, source)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MultiCamExport)
    bpy.utils.register_class(MultiCamImport)
    
def unregister():
    bpy.utils.unregister_class(MultiCamExport)
    bpy.utils.unregister_class(MultiCamImport)
    
