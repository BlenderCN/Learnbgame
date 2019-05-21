import bpy
import bgl
import blf
import os
from . common_utils import redraw

class Draw:
    """
    Composes and displays information
    """
    def __init__(self):
        self.PostPixelHandle = None     # Stores the draw handler
        self.font_id = 0

    def handle_add(self, context, draw_func, text=None):
        """
        Sets the draw handler which displays information in the 3DView
        :param context:
        :param draw_func: The function which will compose and display the information
        """
        if self.PostPixelHandle is None:
            self.PostPixelHandle = bpy.types.SpaceView3D.draw_handler_add(draw_func, (context, text), 'WINDOW', 'POST_PIXEL')
            redraw()

    def handle_remove(self, context):
        """
        Removes the draw handler
        :param context:
        """
        if self.PostPixelHandle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.PostPixelHandle, 'WINDOW')
            redraw()
        self.PostPixelHandle = None

    def draw_box(self, x, y, w, h, color=(0.0, 0.0, 0.0, 1.0)):
        bgl.glEnable(bgl.GL_BLEND)

        # bgl.glDepthRange (0.1, 1.0)
        bgl.glColor4f(*color)
        bgl.glBegin(bgl.GL_QUADS)

        bgl.glVertex2f(x + w, y + h)
        bgl.glVertex2f(x, y + h)
        bgl.glVertex2f(x, y)
        bgl.glVertex2f(x + w, y)
        bgl.glEnd()
        bgl.glDisable(bgl.GL_BLEND)
        return

    def draw_line(self, v1, v2):
        """
        Draws a line between the 2D position v1 and the 2D position v2
        :param v1: First 2D point of the line
        :param v2: Second 2D point of the line
        """
        if v1 and v2:
            bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex2f(*v1)
            bgl.glVertex2f(*v2)
            bgl.glEnd()
        return

    def left_justify(self, words, width):
        """Given an iterable of words, return a string consisting of the words
        left-justified in a line of the given width.

        >>> left_justify(["hello", "world"], 16)
        'hello world     '

        https://codereview.stackexchange.com/questions/95505/text-justification/95570#95570
        """
        return ' '.join(words).ljust(width)

    def justify_text(self, text, width):
        """Divide words (an iterable of strings) into lines of the given
        width, and generate them. The lines are fully justified, except
        for the last line, and lines with a single word, which are
        left-justified.

        >>> words = "This is an example of text justification.".split()
        >>> list(justify(words, 16))
        ['This    is    an', 'example  of text', 'justification.  ']

        https://codereview.stackexchange.com/questions/95505/text-justification/95570#95570
        """
        words = text.split(" ")

        line = []  # List of words in current line.
        col = 0  # Starting column of next word added to line.
        for word in words:
            if line and col + len(word) > width:
                if len(line) == 1:
                    yield self.left_justify(line, width)
                else:
                    # After n + 1 spaces are placed between each pair of
                    # words, there are r spaces left over; these result in
                    # wider spaces at the left.
                    n, r = divmod(width - col + 1, len(line) - 1)
                    narrow = ' ' * (n + 1)
                    if r == 0:
                        yield narrow.join(line)
                    else:
                        wide = ' ' * (n + 2)
                        yield wide.join(line[:r] + [narrow.join(line[r:])])
                line, col = [], 0
            line.append(word)
            col += len(word) + 1
        if line:
            yield self.left_justify(line, width)

    def draw_line_text(self, text, position, color):
        bgl.glColor3f(*color)
        blf.position(0, position[0], position[1], 0)
        blf.draw(self.font_id, text)

    def get_lines(self, text):
        lines_list = []

        w = 0
        h = 0
        file_lines = text.split("\n")
        for l in file_lines:
            sublines = self.justify_text(l.replace('\r', '').replace('\n', ''), 100)
            for sl in sublines:
                text_width, text_height = blf.dimensions(self.font_id, sl)
                if text_width>w:
                    w = text_width
                lines_list.append(sl)
                h = h + 15

            h = h+15
            lines_list.append("")

        return lines_list, (w,h)

    def draw_text(self, context, text):
        lines = self.get_lines(text)
        text_size = lines[1]
        padding = 25

        #w_start = context.region.width - (text_size[0]+perc[0]) - 25
        #h_start = text_size[1] + 25

        w_start = 75
        h_start = context.region.height - 75

        top_left = (w_start-padding, h_start+padding)
        top_right = (top_left[0] + text_size[0]+(padding*2), top_left[1])
        bottom_left = (top_left[0], top_left[1]-(text_size[1]+padding))
        bottom_right = (top_right[0], bottom_left[1])

        self.draw_box(top_left[0], top_left[1], text_size[0]+(padding*2), -(text_size[1]+padding), color=(1.0, 1.0, 1.0, 0.50))

        self.draw_line(top_left, top_right)
        self.draw_line(top_left, bottom_left)
        self.draw_line(bottom_left, bottom_right)
        self.draw_line(bottom_right, top_right)

        h=h_start
        for line in lines[0]:
            self.draw_line_text(line, (w_start, h), (0.0, 0.0, 0.0))
            h = h - 15

    def display_info(self, context, text):
        """
        Displays information in the 3D View
        :param context:
        """
        if self.PostPixelHandle is None:
            self.hide_info(context)
        self.handle_add(context, self.draw_text, text)

    def hide_info(self, context):
        """
        Hides information
        :param context:
        """
        if self.PostPixelHandle is not None:
            self.handle_remove(context)

