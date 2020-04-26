import random
from logging import getLogger

import cv2
import bpy
import gpu
import bgl
import numpy as np
from gpu_extras.batch import batch_for_shader

from ocvl.core.globals import CALLBACK_DICT


logger = getLogger(__name__)


def tag_redraw_all_nodeviews():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'NODE_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


def extract_bind_code(node):
    try:
        return node.texture[node.node_id]['name'][0]
    except (KeyError, IndexError) as e:
        logger.error("Node {} hasn't bide texture.".format(node))
        raise


def simple_screen(node, x, y, width, height):
    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, extract_bind_code(node))

    shader = gpu.shader.from_builtin('2D_IMAGE')
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {
            "pos": ((x, y), (x+width, y), (x+width, y+height), (x, y+height)),
            "texCoord": ((0, 1), (1, 1), (1, 0), (0, 0)),
        },
    )

    shader.bind()
    shader.uniform_int("image", 0)
    batch.draw(shader)


def callback_enable(node=None, x=None, y=None, width=None, height=None):
    if node.n_id in CALLBACK_DICT:
        return
    args = node, x, y, width, height
    handle_pixel = bpy.types.SpaceNodeEditor.draw_handler_add(simple_screen, args, 'WINDOW', 'POST_VIEW')
    CALLBACK_DICT[node.n_id] = handle_pixel
    tag_redraw_all_nodeviews()


def callback_disable(n_id):
    handle_pixel = CALLBACK_DICT.get(n_id, None)
    if not handle_pixel:
        return
    bpy.types.SpaceNodeEditor.draw_handler_remove(handle_pixel, 'WINDOW')
    del CALLBACK_DICT[n_id]
    tag_redraw_all_nodeviews()


def convert_to_gl_image(image_cv):
    image_cv = cv2.flip(image_cv, 0)
    if len(image_cv.shape) == 3:
        image_gl = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGBA) / 255
    if len(image_cv.shape) == 2:
        r = g = b = image_cv / 255
        a = np.ones(image_cv.shape, dtype=r.dtype)
        image_gl = cv2.merge((r, g, b, a))
    image_gl.astype(np.uint8)
    return image_gl


def init_texture(width, height, texname, texture, internalFormat, format):
    bgl.glEnable(bgl.GL_TEXTURE_2D)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, texname)
    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_EDGE)  # bgl.GL_CLAMP
    bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_EDGE)  # bgl.GL_CLAMP
    bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
    bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
    bgl.glTexImage2D(
        bgl.GL_TEXTURE_2D,
        0, internalFormat, width, height,
        0, format, bgl.GL_UNSIGNED_BYTE, texture
    )


def convert_to_cv_image(image_gl):
    image_cv = np.array(image_gl.pixels, dtype=np.float32)
    image_cv = image_cv.reshape((image_gl.size[1], image_gl.size[0], image_gl.channels))
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGBA2BGR) * 255
    image_cv = cv2.flip(image_cv, 0)
    image_cv.astype(np.uint8)
    return image_cv


def gen_image_random_lines(width=200, height=200, layers=3, bg_color=(76, 76, 53), lines_number=20):
    image = np.zeros((width, height, layers), np.uint8)
    image[:, :, ] = bg_color
    for i in range(lines_number):
        pt1 = (random.randint(1, width), random.randint(1, height))
        pt2 = (random.randint(1, width), random.randint(1, height))
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        image = cv2.line(image, pt1, pt2, color, random.randint(1, 10))


def gen_image_lines_horizontal(width=200, height=200, layers=4, grid_height=10):
    image = np.zeros((width, height, layers), np.uint8)
    image[:, :, ] = [0] * layers
    a_color = [100] * layers
    color = b_color = [200] * layers
    for i in range(int(height / grid_height) + 1):
        pt1 = (0, i * grid_height)
        pt2 = (width, i * grid_height)
        if color == a_color:
            color = b_color
        else:
            color = a_color
        image = cv2.line(image, pt1, pt2, color, grid_height)
    return image


def gen_image_lines_verticals(width=200, height=200, layers=4, grid_width=10):
    image = np.zeros((width, height, layers), np.uint8)
    image[:, :, ] = [0] * layers
    a_color = [100] * layers
    color = b_color = [200] * layers
    for i in range(int(height / grid_width) + 1):
        pt1 = (i * grid_width, 0)
        pt2 = (i * grid_width, height)
        if color == a_color:
            color = b_color
        else:
            color = a_color
        image = cv2.line(image, pt1, pt2, color, grid_width)
    return image


def gen_image_grid(width=200, height=200, layers=3, grid_width=10, grid_height=10):
    img_1 = gen_image_lines_horizontal(width=width, height=height, layers=layers, grid_height=grid_height)
    img_2 = gen_image_lines_verticals(width=width, height=height, layers=layers, grid_width=grid_width)
    return cv2.bitwise_xor(img_1, img_2)


def add_background_to_image(image):
    height = image.shape[0]
    width = image.shape[1]
    bg_image = gen_image_grid(width=width, height=height)

    for y in range(height):
        for x in range(width):
            alpha = image[y, x, 3]
            if alpha > 0:
                alpha = alpha / 255.
                image[y, x, 0] = int((alpha * image[y,x,0]) + ((1-alpha) * bg_image[y,x,0]))
                image[y, x, 1] = int((alpha * image[y,x,1]) + ((1-alpha) * bg_image[y,x,1]))
                image[y, x, 2] = int((alpha * image[y,x,2]) + ((1-alpha) * bg_image[y,x,2]))
            else:
                image[y, x, 0] = bg_image[y, x, 0]
                image[y, x, 1] = bg_image[y, x, 1]
                image[y, x, 2] = bg_image[y, x, 2]
    return image