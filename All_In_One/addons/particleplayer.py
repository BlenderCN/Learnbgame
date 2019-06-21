'''
EXPORTED .JSON FILE FORMAT

{
    version: '1.0',
    precision: 1000,
    rotation: true,
    age: true,
    sprite_rotation: [0, 0, 0],
    frames: [<frames>]
}

Each frame is an array of particles. Each particle is an array of integers:
(to get the actual float value, divide by data.precision (1000 by default))

    [ position.x, position.y, position.z, rotation.x, rotation.y, rotation.z, age ]

If data is 0, the particle is not alive in that frame (it should be invisible)

age goes from 0 to data.precision

'''


import bpy
import json
import os
from math import floor
from bpy.app.handlers import persistent


VERSION = '1.1' # json format version

bl_info = {
    "name": "A-Frame particleplayer exporter",
    "description": "Exports current selected object particle systems to a JSON file ready to be consumed by A-Frame's particle player component.",
    "author": "Diego F. Goberna",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://github.com/supermedium/aframe-particleplayer-component",
    "tracker_url": "http://github.com/supermedium/aframe-particleplayer-component/issues",
    "category": "Learnbgame",
}

precision = 1000

def AA(n):
    return floor(n * precision)

def export_main(context, path, settings, operator):
    global precision
    obj = context.active_object
    precision = int(settings['precision'])
    data = {'version': VERSION, 'precision': precision, 'rotation': settings['userotation'], 'age': settings['useage'], 'frames': [], 'sprite_rotation': False }
    
    # update dep graph
    obj = bpy.context.depsgraph.objects.get(obj.name, None)

    if not obj or not obj.particle_systems:
        operator.report({'ERROR'}, "No particle systems in selected object")
        return {'CANCELLED'}

    f = open(path, 'w')
    if not f:
        operator.report({'ERROR'}, "Could not open " + path)
        return {'CANCELLED'}

    if settings['userotation']:
        dupli = obj.particle_systems[0].settings.instance_object
        if dupli:
            data['sprite_rotation'] = [0, 0, 0]
            data['sprite_rotation'][0] = AA( dupli.rotation_euler.x )
            data['sprite_rotation'][1] = AA( dupli.rotation_euler.z )
            data['sprite_rotation'][2] = AA( -dupli.rotation_euler.y )

    for frame in range(settings['firstframe'], settings['lastframe'] + 1, settings['framestep']):
        context.scene.frame_set(frame)
        fdata = []
        for ps in obj.particle_systems:
            for i in range(len(ps.particles)):
                part = []
                p = ps.particles[i]
                if p.is_exist and p.alive_state == 'ALIVE':
                    part.append(AA( p.location.x ))
                    part.append(AA( p.location.z ))
                    part.append(AA( -p.location.y ))
                    if settings['userotation']:
                        part.append(AA( p.rotation.to_euler().x ))
                        part.append(AA( p.rotation.to_euler().z ))
                        part.append(AA( -p.rotation.to_euler().y ))
                    if settings['useage']:
                        part.append(AA( (frame - p.birth_time) / p.lifetime ))
                else:
                    part = 0

                fdata.append(part)
        data['frames'].append(fdata)

    # write to file, finish
    f.write(json.dumps(data, separators = (',',':')))
    f.close()
    operator.report({'INFO'}, 'Saved ' + os.path.realpath(f.name))
    return {'FINISHED'}



from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from bpy.types import Operator


class ParticlePlayerExporter(Operator, ExportHelper):
    bl_idname = "aframe_export.particleplayer"
    bl_label = "Export A-Frame Particle Player"

    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    firstframe : IntProperty(name="First frame", min=0, subtype='UNSIGNED', default=0)
    lastframe : IntProperty(name="Last frame", min=0, subtype='UNSIGNED', default=20)
    framestep : IntProperty(name="Frame step", min=1, subtype='UNSIGNED', default=1)

    userotation : BoolProperty(name="Export rotation", default=False)
    useage : BoolProperty(name="Export age", default=False)
    precision : EnumProperty(name="Precision", description="Precision", default='1000',
            items=(
                ('1', '1', ''),
                ('10', '10', ''),
                ('100', '100', ''),
                ('1000', '1000', ''),
                ('10000', '10000', ''),
                ('100000', '100000', ''),
                ('1000000', '1000000', ''))
            )

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        if not obj:
            row = layout.row()
            row.label(text="No object selected!")
            return

        self.firstframe = context.scene.frame_start
        self.lastframe = context.scene.frame_end
        row = layout.row()
        row.prop(self, "firstframe")
        row = layout.row()
        row.prop(self, "lastframe")
        row = layout.row()
        row.prop(self, "framestep")
        row = layout.row()
        row.prop(self, "userotation")
        row = layout.row()
        row.prop(self, "useage")
        row = layout.row()
        row.prop(self, "precision", text="Precision ")

    def execute(self, context):
        settings = {
            'firstframe': self.firstframe,
            'lastframe': self.lastframe,
            'framestep': self.framestep,
            'userotation': self.userotation,
            'useage': self.useage,
            'precision': self.precision
        }
        return export_main(context, self.filepath, settings, self)


def menu_func_export(self, context):
    self.layout.operator(ParticlePlayerExporter.bl_idname, text="A-Frame Particle Player")


def register():
    bpy.utils.register_class(ParticlePlayerExporter)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ParticlePlayerExporter)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
