# Copyright (c) 2013, Martin Herkt
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

bl_info = {
    "name": "Export: Adobe After Effects 6.0 Keyframe Data",
    "description": "Export motion tracking markers to Adobe After Effects 6.0 compatible files",
    "author": "Martin Herkt",
    "version": (0, 1, 2),
    "blender": (2, 62, 0),
    "location": "File > Export > Adobe After Effects 6.0 Keyframe Data",
    "warning": "",
    "category": "Import-Export",
    }

import bpy, mathutils, math, pyperclip

def write_files(prefix, context):
    scene = context.scene
    fps = scene.render.fps / scene.render.fps_base

    clipno = 0

    for clip in bpy.data.movieclips:
        trackno = 0

        for track in clip.tracking.tracks:
            with open("{0}_c{1:02d}_t{2:02d}.txt".format(prefix, clipno, trackno), "w") as f:

                frameno = clip.frame_start
                startarea = None
                startwidth = None
                startheight = None
                startrot = None

                data = []

                clipboard = ""
				
                f.write("Adobe After Effects 6.0 Keyframe Data\r\n\r\n")
                clipboard += "Adobe After Effects 6.0 Keyframe Data\r\n\r\n"
                f.write("\tUnits Per Second\t{0:.3f}\r\n".format(fps))
                clipboard += "\tUnits Per Second\t{0:.3f}\r\n".format(fps)
                f.write("\tSource Width\t{0}\r\n".format(clip.size[0]))
                clipboard += "\tSource Width\t{0}\r\n".format(clip.size[0])
                f.write("\tSource Height\t{0}\r\n".format(clip.size[1]))
                clipboard += "\tSource Height\t{0}\r\n".format(clip.size[1])
                f.write("\tSource Pixel Aspect Ratio\t1\r\n")
                clipboard += "\tSource Pixel Aspect Ratio\t1\r\n"
                f.write("\tComp Pixel Aspect Ratio\t1\r\n\r\n")
                clipboard += "\tComp Pixel Aspect Ratio\t1\r\n\r\n"

                while frameno <= clip.frame_duration:
                    marker = track.markers.find_frame(frameno)
                    frameno += 1

                    if not marker or marker.mute:
                        continue

                    coords = marker.co
                    corners = marker.pattern_corners

                    area = 0
                    width = math.sqrt((corners[1][0] - corners[0][0]) * (corners[1][0] - corners[0][0]) + (corners[1][1] - corners[0][1]) * (corners[1][1] - corners[0][1]))
                    height = math.sqrt((corners[3][0] - corners[0][0]) * (corners[3][0] - corners[0][0]) + (corners[3][1] - corners[0][1]) * (corners[3][1] - corners[0][1]))
                    for i in range(1,3):
                        x1 = corners[i][0] - corners[0][0]
                        y1 = corners[i][1] - corners[0][1]
                        x2 = corners[i+1][0] - corners[0][0]
                        y2 = corners[i+1][1] - corners[0][1]
                        area += x1 * y2 - x2 * y1

                    area = abs(area / 2)

                    if startarea == None:
                        startarea = area
                        
                    if startwidth == None:
                        startwidth = width
                    if startheight == None:
                        startheight = height

                    zoom = math.sqrt(area / startarea) * 100
                    
                    xscale = width / startwidth * 100
                    yscale = height / startheight * 100

                    p1 = mathutils.Vector(corners[0])
                    p2 = mathutils.Vector(corners[1])
                    mid = (p1 + p2) / 2
                    diff = mid - mathutils.Vector((0,0))

                    rotation = math.atan2(diff[0], diff[1]) * 180 / math.pi

                    if startrot == None:
                        startrot = rotation
                        rotation = 0
                    else:
                        rotation -= startrot - 360

                    x = coords[0] * clip.size[0]
                    y = (1 - coords[1]) * clip.size[1]

                    data.append([marker.frame, x, y, xscale, yscale, rotation])

                posline = "\t{0}\t{1:.3f}\t{2:.3f}\t0"
                scaleline = "\t{0}\t{1:.3f}\t{2:.3f}\t100"
                rotline = "\t{0}\t{1:.3f}"

                positions = "\r\n".join([posline.format(d[0], d[1], d[2]) for d in data]) + "\r\n\r\n"
                scales = "\r\n".join([scaleline.format(d[0], d[3], d[4]) for d in data]) + "\r\n\r\n"
                rotations = "\r\n".join([rotline.format(d[0], d[5]) for d in data]) + "\r\n\r\n"

                f.write("Anchor Point\r\n")
                clipboard += "Anchor Point\r\n"
                f.write("\tFrame\tX pixels\tY pixels\tZ pixels\r\n")
                clipboard += "\tFrame\tX pixels\tY pixels\tZ pixels\r\n"
                f.write(positions)
                clipboard += positions

                f.write("Position\r\n")
                clipboard += "Position\r\n"
                f.write("\tFrame\tX pixels\tY pixels\tZ pixels\r\n")
                clipboard += "\tFrame\tX pixels\tY pixels\tZ pixels\r\n"
                f.write(positions)
                clipboard += positions

                f.write("Scale\r\n")
                clipboard += "Scale\r\n"
                f.write("\tFrame\tX percent\tY percent\tZ percent\r\n")
                clipboard += "\tFrame\tX percent\tY percent\tZ percent\r\n"
                f.write(scales)
                clipboard += scales

                f.write("Rotation\r\n")
                clipboard += "Rotation\r\n"
                f.write("\tFrame Degrees\r\n")
                clipboard += "\tFrame Degrees\r\n"
                f.write(rotations)
                clipboard += rotations

                f.write("End of Keyframe Data\r\n")
                clipboard += "End of Keyframe Data\r\n"

                trackno += 1

            clipno += 1
    pyperclip.copy(clipboard)
    return {'FINISHED'}

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty

class ExportAFXKey(bpy.types.Operator, ExportHelper):
    """Export motion tracking markers to Adobe After Effects 6.0 compatible files"""
    bl_idname = "export.afxkey"
    bl_label = "Export to Adobe After Effects 6.0 Keyframe Data"
    filename_ext = ""
    filter_glob = StringProperty(default="*", options={'HIDDEN'})

    def execute(self, context):
        return write_files(self.filepath, context)


def menu_func(self, context):
    self.layout.operator(ExportAFXKey.bl_idname, text="Adobe After Effects 6.0 Keyframe Data")


def register():
    bpy.utils.register_class(ExportAFXKey)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ExportAFXKey)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()