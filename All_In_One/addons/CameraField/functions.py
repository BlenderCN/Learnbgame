import bpy
import bgl


# def remap(value, leftMin, leftMax, rightMin, rightMax):
#     # Figure out how 'wide' each range is
#     leftSpan = leftMax - leftMin
#     rightSpan = rightMax - rightMin
#
#     # Convert the left range into a 0-1 range (float)
#     valueScaled = (value - leftMin) / leftSpan
#
#     # Convert the 0-1 range into a value in the right range.
#     return rightMin + valueScaled * rightSpan


def draw_callback_3d(cameras):
    # bgl.glDisable(bgl.GL_DEPTH_TEST)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glPointSize(4)
    bgl.glLineWidth(3)

    bgl.glBegin(bgl.GL_POINTS)
    for cam in cameras:
        bgl.glColor4f(*cam["color"], 0.5)
        for co in cam["co"]:
            bgl.glVertex3f(*co)

    bgl.glEnd()

    # Restore opengl defaults
    bgl.glPointSize(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    # bgl.glEnable(bgl.GL_DEPTH_TEST)
