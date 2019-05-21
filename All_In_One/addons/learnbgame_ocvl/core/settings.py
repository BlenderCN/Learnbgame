# Color node without necessary data to process
NODE_COLOR_REQUIRE_DATE = (1, 0.3, 0)
# In draw_buttons_ext width text
WRAP_TEXT_SIZE_FOR_ERROR_DISPLAY = 75
# In NodeBase if True make copy for "image_in/img_in" sockets data
IS_WORK_ON_COPY_INPUT = True

DEBUG_MODE = False
DEBUG = DEBUG_MODE

class Category:
    uncategorized = "uncategorized"
    filters = "filters"


class SocketColors:
    StringsSocket = 0.1, 1.0, 0.2, 1
    ImageSocket = 0.1, 1.0, 0.8, 1
    SvColorSocket = 0.1, 0.7, 1.0, 1


CATEGORY_TREE = Category()
SOCKET_COLORS = SocketColors()
