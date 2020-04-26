"""BlenderFDS, export geometry to ge1 cad file format."""

import bpy
from blenderfds.geometry.utilities import *

# GE1 file format:

# [APPEARANCE]  < immutable title
# 2             < number of appearances (from Blender materials)
# INERT                     < appearance name
# 0 200 200 50 0.0 0.0 0.5  < index, red, green, blue, twidth, theight, alpha, tx0, ty0, tz0 (t is texture)
#                           < texture file, blank if None
# Burner
# 1 255 0 0 0.0 0.0 0.5
#
# [FACES]       < immutable title
# 2             < number of quad faces (from OBST and SURF objects tessfaces)
# 6.0 3.9 0.5 6.0 1.9 0.5 6.0 1.9 1.9 6.0 3.9 1.9 0 < x0, y0, z0, x1, y1, z1, ..., ref to appearance index
# 6.0 3.9 0.5 6.0 1.9 0.5 6.0 1.9 1.9 6.0 3.9 1.9 0
# EOF

# FIXME color for holes?

def scene_to_ge1(context, scene):
    """Export scene geometry in FDS GE1 notation, on error raise BFException."""
    # Cursor
    w = context.window_manager.windows[0]
    w.cursor_modal_set("WAIT")
    # Get GE1 appearances from materials
    appearances = list()
    ma_to_appearance = dict()
    for index, ma in enumerate(bpy.data.materials):
        ma_to_appearance[ma.name] = index
        appearances.append(
            "{desc}\n{i} {r} {g} {b} 0. 0. {alpha:.6f}\n\n".format(
                desc=ma.name, i=index,
                r=int(ma.diffuse_color[0]*255), g=int(ma.diffuse_color[1]*255), b=int(ma.diffuse_color[2]*255), 
                alpha=ma.alpha,
            )
        )
    # Get GE1 gefaces from objects
    obs = (ob for ob in context.scene.objects if ob.type == "MESH"
        and not ob.hide_render  # hide some objects if requested
        and not ob.bf_is_tmp    # do not show temporary objects
        and ob.bf_export        # show only exported objects
        and ob.bf_namelist_idname in ("bf_obst", "bf_vent", "bf_hole") # show only some namelists
        and getattr(ob.active_material, "name", None) != "OPEN" # do not show open VENTs
    )
    gefaces = list()
    for ob in obs:
        me = get_global_mesh(context, ob)
        tessfaces = get_tessfaces(context, me)
        # Transform ob tessfaces in GE1 gefaces
        if ob.active_material: active_material_name = ob.active_material.name
        else: active_material_name = "INERT"
        appearance_index = str(ma_to_appearance.get(active_material_name, 0)) + "\n"
        for tessface in tessfaces:
            # Get tessface vertices: (x0, y0, z0), (x1, y1, z1), (x2, y2, z2), ... tri or quad
            verts = list(me.vertices[vertex] for vertex in tessface.vertices)
            # Transform tri in quad
            if len(verts) == 3: verts.append(verts[-1])
            # Unzip and format verts, append ref to appearance
            items = ["{:.6f}".format(co) for vert in verts for co in vert.co]
            items.append(appearance_index)
            # Append GE1 face
            gefaces.append(" ".join(items))
    # Prepare GE1 file and return
    ge1_file_a = "[APPEARANCE]\n{}\n{}".format(len(appearances), "".join(appearances))
    ge1_file_f = "[FACES]\n{}\n{}".format(len(gefaces), "".join(gefaces))
    w.cursor_modal_restore()
    return "".join((ge1_file_a, ge1_file_f))

