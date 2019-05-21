from mathutils import Vector
from .draw_stippled_line import draw_stippled_line
from .draw_arrows import draw_arrows

def draw_px_point(self, context):
    """
    Draws the handle seen when rotating or scaling
    """
    # Stopped working after API change --> theme = context.user_preferences.themes['Default']
    #active_color = theme.view_3d.object_active

    #color = (active_color[0], active_color[1], active_color[2], 1.0)

    color = (1.0, 0.5, 0, 1.0)

    v1 = [self.center_area.x, self.center_area.y]
    v2 = [self.mouse_pos.x, self.mouse_pos.y]

    if self.mouse_pos != Vector([-1, -1]):
        draw_stippled_line(v1, v2, 2, 10, color)
        if hasattr(self, 'rot_prev'):
            draw_arrows(v1, v2, 2, 20, color, angle_offset=90)
        else:
            draw_arrows(v1, v2, 2, 20, color)
