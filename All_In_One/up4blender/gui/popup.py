import bpy


def show_message_box(message='', title='Message Box', icon='INFO'):
    """
    Pops out a message box with message, title and icon given

    :param message: *(str)* message to display
    :param title:   *(str)* title at the top of the box
    :param icon:    *(str)* standardized icons. Takes INFO, ERROR
    :return:
    """
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
