'''
Copyright (c) 2018 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os
import subprocess

def get_output_path(context, index):
    return bpy.path.abspath(context.scene.rct_graphics_helper_general_properties.output_directory+str(index)+".png")

def get_offset_output_path(context, index):
    return bpy.path.abspath(context.scene.rct_graphics_helper_general_properties.output_directory+str(index)+".txt")

def mask_layer(layer_index, context):
    for render_layer in context.scene.render.layers:
        if render_layer.use:
            for i in range(9): # Maximum of 8 rider pairs, 1 for the vehicle itself
                render_layer.layers[i] = i == layer_index
                render_layer.layers_zmask[i] = i <= layer_index
            render_layer.use_zmask = True
            break

def render(context, index):
    bpy.data.scenes['Scene'].render.filepath = get_output_path(context, index)
    bpy.ops.render.render( write_still = True ) 
    return

def rotate_for_vertical_joint(x, y, modifier = 1):
    vertical_joint = bpy.data.objects['VerticalJoint']
    if vertical_joint is None:
        return False
    angle = -vertical_joint.rotation_euler[2] * modifier
    return [round(x * math.cos(angle) - y * math.sin(angle)), round(x * math.sin(angle) + y * math.cos(angle))]


def position_cookie_cutter(context, x, y, left, right, enable):
    cookie_cutter = bpy.data.objects['CookieCutter']
    if cookie_cutter is None:
        return False
    cookie_cutter_floor = bpy.data.objects['CookieCutterFloor']
    if cookie_cutter_floor is None:
        return False
    vertical_joint = bpy.data.objects['VerticalJoint']
    if vertical_joint is None:
        return False
    cookie_cutter_floor.hide_render = not enable
    angle = vertical_joint.rotation_euler[2]
    cookie_cutter.location[1] = -(x * math.cos(angle) - y * math.sin(angle)) * 4
    cookie_cutter.location[0] = -(x * math.sin(angle) + y * math.cos(angle)) * 4
    cookie_cutter.location[2] = 0
    
    cookie_cutter_l = bpy.data.objects['CookieCutterLeft']
    if cookie_cutter_l is None:
        return False
    cookie_cutter_l.hide_render = not left
    cookie_cutter_r = bpy.data.objects['CookieCutterRight']
    if cookie_cutter_r is None:
        return False
    cookie_cutter_r.hide_render = not right
    return True

def rotate_rig(context, angle, verAngle=0, bankedAngle=0, midAngle=0):
        object = bpy.data.objects['Rig']
        if object is None:
            return False
        object.rotation_euler = (math.radians(bankedAngle),math.radians(verAngle),math.radians(midAngle))
        vJoint = object.children[0] 
        vJoint.rotation_euler = (0,0,math.radians(angle))
        return True

def post_render(context, index, crop = True):
    magick_path = "magick"
    output_path = get_output_path(context, index)

    palette_path = context.scene.rct_graphics_helper_general_properties.palette_path

    result = ""
    if crop:
        result = str(subprocess.check_output(magick_path + " \"" + output_path + "\" -fuzz 0 -fill none -opaque rgb(57,59,57)  -quantize RGB -dither FloydSteinberg -define dither:diffusion-amount=30% -remap \"" + palette_path + "\" -colorspace sRGB -bordercolor none -border 1 -trim -format  \"%[fx:page.x - page.width/2] %[fx:page.y - page.height/2]\" -write info: \"" + output_path + "\"", shell=True))
        
        offset_file = open(get_offset_output_path(context, index), "w")
        offset_file.write(result[2:][:-1])
        offset_file.close()
    
    else:
        result = str(subprocess.check_output(magick_path + " \"" + output_path + "\" -fuzz 0 -fill none -opaque rgb(57,59,57)  -quantize RGB -dither FloydSteinberg -define dither:diffusion-amount=30% -remap \"" + palette_path + "\" -colorspace sRGB \"" + output_path + "\"", shell=True))
        return

def mask(context, base, mask, output, operation = "In"):
    magick_path = "magick"
    output_path = get_output_path(context, output)
    base_path = get_output_path(context, base)
    mask_path = get_output_path(context, mask)

    result = str(subprocess.check_output(magick_path + " \"" + mask_path + "\" +repage -gravity center \"" + base_path + "\" -compose " + operation + " -composite \"" + output_path + "\"", shell=True))
    return


class AngleSectionTask(object):
    section = None
    frame = None
    frame_index = 0
    anim_start = 0
    anim_count = 1
    anim_index = 0
    sub_index = 0
    out_index = None
    status = "CREATED"
    inverted = False
    context = None
    render_layer = 0
    width = 1
    height = 1

    def __init__(self, section_in, out_index_start, context):
        self.render_layer = section_in.render_layer
        self.inverted = section_in.inverted
        self.section = section_in.angle_section
        self.out_index = out_index_start
        self.anim_start = section_in.anim_frame_index
        self.anim_count = section_in.anim_frame_count
        self.frame = None
        self.frame_index = 0
        self.sub_index = 0
        self.anim_index = 0
        self.status = "CREATED"
        self.context = context
        self.width = section_in.width
        self.height = section_in.height
        self.wx = 0
        self.wy = 0
        self.sub_tiles = False

    def step(self):
        if self.frame_index == len(self.section):
            self.status = "FINISHED"
        self.frame = self.section[self.frame_index]

        if self.frame_index == 0:
            mask_layer(self.render_layer, self.context)

        frame = self.frame
        angle = 0
        if frame[0]:
            angle = 45
        if frame[1] == 2:
            angle += 90 * self.sub_index
        else:
            angle += 360 / frame[1] * self.sub_index

        extra_roll = 0
        if self.inverted:
            extra_roll = 180

        has_sub_tiles = self.width > 1 or self.height > 1

        self.context.scene.frame_set(self.anim_start + self.anim_index)
        rotate_rig(self.context, angle, frame[2], frame[3] + extra_roll, frame[4])

        if self.sub_tiles:
            wh = rotate_for_vertical_joint(-1, -1)
            if wh[0] < 0:
                wh[0] = 0
            if wh[1] < 0:
                wh[1] = 0
            xy = rotate_for_vertical_joint(self.wx, self.wy)
            position_cookie_cutter(self.context, self.wx, self.wy, abs(xy[0]) == wh[1] * (self.height - 1), abs(xy[1]) == wh[0] * (self.width - 1), True)
        else:
            position_cookie_cutter(self.context, 0, 0, False, False, False)

        output = self.out_index
        if has_sub_tiles:
            output = "full" + "_" + str(self.out_index)
        if has_sub_tiles and self.sub_tiles:
            output = (self.wy * self.width + self.wx) * frame[1] + self.out_index
        render(self.context, output)
        post_render(self.context, output, not has_sub_tiles)

        if self.sub_tiles:
            if self.wx == self.width - 1:
                self.wx = 0
                if self.wy == self.height - 1:
                    self.wy = 0
                    self.sub_tiles = False
                    self.anim_index += 1

                    for i in range(self.width):
                        for j in range(self.height):
                            index = (j * self.width + i) * frame[1] + self.out_index
                            mask(self.context, index, index, "c_" + str(index), "Dst")

                    for i in range(self.width):
                        for j in range(self.height):
                            posx =  rotate_for_vertical_joint(1, 0)
                            posy =  rotate_for_vertical_joint(0, 1)
                            index = (j * self.width + i) * frame[1] + self.out_index
                            indexx2 = ((j + posx[1]) * self.width + (i + posx[0])) * frame[1] + self.out_index
                            indexy2 = ((j + posy[1]) * self.width + (i + posy[0])) * frame[1] + self.out_index
                            if i + posx[0] < self.width and j + posx[1] < self.height and i + posx[0] >= 0 and j + posx[1] >= 0:
                                mask(self.context, "c_" + str(index), str(indexx2), "c_" + str(index), "Out")
                            if i + posy[0] < self.width and j + posy[1] < self.height and i + posy[0] >= 0 and j + posy[1] >= 0:
                                mask(self.context, "c_" + str(index), str(indexy2), "c_" + str(index), "Out")

                    for i in range(self.width):
                        for j in range(self.height):
                            index = (j * self.width + i) * frame[1] + self.out_index
                            mask(self.context, "c_" + str(index), "full" + "_" + str(self.out_index), index, "Dst_In")
                            os.remove(get_output_path(self.context, "c_" + str(index)))
                            post_render(self.context, index)
                            
                    self.out_index += 1
                else:
                    self.wy += 1
            else:
                self.wx += 1
        else:
            if has_sub_tiles:
                if not self.sub_tiles:
                    self.sub_tiles = True
            else:
                self.anim_index += 1
                self.out_index += 1

        if self.anim_index == self.anim_count:
            self.anim_index = 0
            self.sub_index += 1
        if self.sub_index == self.frame[1]:
            self.sub_index = 0
            self.frame_index += 1
        if self.frame_index == len(self.section):
            self.status = "FINISHED"
            return "FINISHED"
        self.status = "RUNNING"
        return "RUNNING"

class RenderTaskSection(object):
    angle_section = None
    inverted = False
    render_layer = 0
    anim_frame_index = 0
    anim_frame_count = 1
    width = 1
    height = 1
    def __init__(self, angle_section, render_layer = 0, inverted = False, frame_index = 0, frame_count = 1, width = 1, height = 1):
        self.angle_section = angle_section
        self.inverted = inverted
        self.render_layer = render_layer
        self.anim_frame_index = frame_index
        self.anim_frame_count = frame_count
        self.width = width
        self.height = height


class RenderTask(object):
    out_index = 0
    sections = []
    section_index = 0
    status = "CREATED"
    section_task = None
    out_index = 0
    context = None
    use_antialiasing = False
    def __init__(self, out_index_start, context):
        self.out_index = out_index_start
        self.sections = []
        self.section_index = 0
        self.status = "CREATED"
        self.section_task = None
        self.context = context
        self.use_antialiasing = context.scene.render.use_antialiasing

    def add(self, angle_section, render_layer = 0, inverted = False, frame_index = 0, frame_count = 1, width = 1, height = 1):
        self.sections.append(RenderTaskSection(angle_section, render_layer, inverted, frame_index, frame_count, width, height))

    def step(self):
        if self.section_task is None:
            section = self.sections[self.section_index]
            self.section_task = AngleSectionTask(section, self.out_index, self.context)

        result = self.section_task.step()
        self.out_index = self.section_task.out_index

        if result == "FINISHED":
            self.section_task = None
            self.section_index += 1

            if self.section_index == len(self.sections):
                position_cookie_cutter(self.context, 0, 0, False, False, False)
                self.status = "FINISHED"
                return "FINISHED"