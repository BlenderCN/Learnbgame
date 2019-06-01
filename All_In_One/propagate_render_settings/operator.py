# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import BoolProperty, StringProperty

#
# Definition of “operator settings” in scene ID.
# TODO: If anyone knows how UI elements (i.e. panels etc.) can set an operator’s
#       settings in another way…
#


bpy.types.Scene.propagate_scale = BoolProperty(name="Render Scale",
                                               description="Propagate render’s scale setting.",
                                               default=True)
bpy.types.Scene.propagate_res = BoolProperty(name="Render Resolution",
                                             description="Propagate render’s resolution settings "
                                                        +"(high, width, and ratios).",
                                             default=False)
bpy.types.Scene.propagate_osa = BoolProperty(name="Render OSA",
                                             description="Propagate render’s OSA settings (OSA "
                                                        +"enabled, and OSA level).",
                                             default=True)
bpy.types.Scene.propagate_threads = BoolProperty(name="Render Threads",
                                                 description="Propagate render’s number of threads "
                                                            +"settings.",
                                                 default=False)
bpy.types.Scene.propagate_fields = BoolProperty(name="Render Fields",
                                                description="Propagate render’s fields settings.",
                                                default=True)
bpy.types.Scene.propagate_stamp = BoolProperty(name="Render Stamp",
                                               description="Propagate render’s stamp setting (i.e. only "
                                                          +"enable/disable stamp, not inner settings).",
                                               default=False)

bpy.types.Scene.propagate_filter_scene = StringProperty(name="Filter Scene",
                                                        description="Regex to only affect scenes "
                                                                   +"which name matches it.",
                                                        default="")

def main(context, do_scale, do_res, do_osa, do_threads, do_fields, do_stamp,
         filter_scene):
    # Get render settings from current scene.
    p = {"scale": ["resolution_percentage", None],
         "res_x": ["resolution_x", None],
         "res_y": ["resolution_y", None],
         "aspect_x": ["pixel_aspect_x", None],
         "aspect_y": ["pixel_aspect_y", None],
         "osa": ["use_antialiasing", None],
         "osa_level": ["antialiasing_samples", None],
         "threads_mode": ["threads_mode", None],
         "threads_nbr": ["threads", None],
         "fields": ["use_fields", None],
         "fields_order": ["field_order", None],
         "fields_still": ["use_fields_still", None],
         "stamp": ["use_stamp", None],
    }
    # put it in all other (valid) scenes’ render settings!
    for scene in bpy.data.scenes:
        # If regex, only proceed on matching scenes.
        if filter_scene:
            if not filter_scene.match(scene.name): continue
        if do_scale:
            if p["scale"][1] is None:
                p["scale"][1] = getattr(context.scene.render, p["scale"][0])
            setattr(scene.render, p["scale"][0], p["scale"][1])
        if do_res:
            if p["res_x"][1] is None:
                p["res_x"][1] = getattr(context.scene.render, p["res_x"][0])
            setattr(scene.render, p["res_x"][0], p["res_x"][1])
            if p["res_y"][1] is None:
                p["res_y"][1] = getattr(context.scene.render, p["res_y"][0])
            setattr(scene.render, p["res_y"][0], p["res_y"][1])
            if p["aspect_x"][1] is None:
                p["aspect_x"][1] = getattr(context.scene.render, p["aspect_x"][0])
            setattr(scene.render, p["aspect_x"][0], p["aspect_x"][1])
            if p["aspect_y"][1] is None:
                p["aspect_y"][1] = getattr(context.scene.render, p["aspect_y"][0])
            setattr(scene.render, p["aspect_y"][0], p["aspect_y"][1])
        if do_osa:
            if p["osa"][1] is None:
                p["osa"][1] = getattr(context.scene.render, p["osa"][0])
            setattr(scene.render, p["osa"][0], p["osa"][1])
            if p["osa_level"][1] is None:
                p["osa_level"][1] = getattr(context.scene.render, p["osa_level"][0])
            setattr(scene.render, p["osa_level"][0], p["osa_level"][1])
        if do_threads:
            if p["threads_mode"][1] is None:
                p["threads_mode"][1] = getattr(context.scene.render, p["threads_mode"][0])
            setattr(scene.render, p["threads_mode"][0], p["threads_mode"][1])
            if p["threads_nbr"][1] is None:
                p["threads_nbr"][1] = getattr(context.scene.render, p["threads_nbr"][0])
            setattr(scene.render, p["threads_nbr"][0], p["threads_nbr"][1])
        if do_fields:
            if p["fields"][1] is None:
                p["fields"][1] = getattr(context.scene.render, p["fields"][0])
            setattr(scene.render, p["fields"][0], p["fields"][1])
            if p["fields_order"][1] is None:
                p["fields_order"][1] = getattr(context.scene.render, p["fields_order"][0])
            setattr(scene.render, p["fields_order"][0], p["fields_order"][1])
            if p["fields_still"][1] is None:
                p["fields_still"][1] = getattr(context.scene.render, p["fields_still"][0])
            setattr(scene.render, p["fields_still"][0], p["fields_still"][1])
        if do_stamp:
            if p["stamp"][1] is None:
                p["stamp"][1] = getattr(context.scene.render, p["stamp"][0])
            setattr(scene.render, p["stamp"][0], p["stamp"][1])

class PropagateRenderSettings(bpy.types.Operator):
    '''
    Propagate render settings from current scene to others.
    '''
    bl_idname = "scene.propagate_render_settings"
    bl_label = "Propagate Render Settings"
    # Enable undo…
    bl_option = {'REGISTER', 'UNDO'}

#    do_scale = BoolProperty(name="Render Scale",
#                            description="Propagate render’s scale setting.",
#                            default=True)
#    do_res = BoolProperty(name="Render Resolution",
#                          description="Propagate render’s resolution settings "
#                                     +"(high, width, and ratios).",
#                          default=False)
#    do_osa = BoolProperty(name="Render OSA",
#                          description="Propagate render’s OSA settings (OSA "
#                                     +"enabled, and OSA level).",
#                          default=True)
#    do_threads = BoolProperty(name="Render Threads",
#                              description="Propagate render’s number of threads "
#                                         +"settings.",
#                              default=False)
#    do_fields = BoolProperty(name="Render Fields",
#                             description="Propagate render’s fields settings.",
#                             default=True)
#    do_stamp = BoolProperty(name="Render Stamp",
#                            description="Propagate render’s stamp setting (i.e. only "
#                                       +"enable/disable stamp, not inner settings).",
#                            default=False)

#    filter_scene = StringProperty(name="Filter Scene",
#                                  description="Regex to only affect scenes which name "
#                                             +"matches it.",
#                                  default="")

    @classmethod
    def poll(cls, context):
        return context.scene != None

    def execute(self, context):
        regex = None
#        if self.filter_scene:
        if context.scene.propagate_filter_scene:
            try:
                import re
                try:
                    regex = re.compile(context.scene.propagate_filter_scene)
#                    regex = re.compile(self.filter_scene)
                except Exception as e:
                    self.report('ERROR_INVALID_INPUT', "The filter-scene regex "
                               +"did not compile (%s)." % str(e))
                    return {'CANCELLED'}
            except:
                regex = None
                self.report('WARNING', "Impossible to import the re module. Regex "
                           +"scene filtering will be disabled!")
        self.report('DEBUG', "Propagating following render settings:\n    scale: {}\n    resolution: {}"
                            +"\n    osa: {}\n    threads: {}\n    fields: {}\n    stamp: {}\n"
                            +"  for scenes matching “{}”."
                            +"".format(context.scene.propagate_scale, context.scene.propagate_res,
                                       context.scene.propagate_osa, context.scene.propagate_threads,
                                       context.scene.propagate_fields, context.scene.propagate_stamp,
                                       context.scene.propagate_filter_scene))
        main(context, do_scale=context.scene.propagate_scale, do_res=context.scene.propagate_res,
             do_osa=context.scene.propagate_osa, do_threads=context.scene.propagate_threads,
             do_fields=context.scene.propagate_fields, do_stamp=context.scene.propagate_stamp,
             filter_scene=regex)
#        main(context, do_scale=self.do_scale, do_res=self.do_res, do_osa=self.do_osa, do_threads=self.do_threads,
#             do_fields=self.do_fields, do_stamp=self.do_stamp, filter_scene=regex)
        return {'FINISHED'}


if __name__ == "__main__":
    bpy.ops.scene.propagate_render_settings()

