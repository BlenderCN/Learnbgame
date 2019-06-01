import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty
from .. import M3utils as m3
from .. utils.operators import unlink_render_result


class PanelUnwrap(bpy.types.Operator):
    bl_idname = "machin3.decal_panel_unwrap"
    bl_label = "MACHIN3: Panel Unwrap"
    bl_options = {'REGISTER', 'UNDO'}

    rotateUVs = BoolProperty(name="Rotate UVs", default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "rotateUVs")

    def execute(self, context):
        panel_unwrap(knife=self.rotateUVs)

        return {'FINISHED'}


def panel_unwrap(object=None, knife=False):
    mode = m3.get_mode()
    if object is None:
        object = bpy.context.active_object
        mesh = object.data
        if mode != "OBJECT":
            if mode == "EDGE":
                bpy.ops.mesh.mark_seam(clear=False)
                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.mesh.mark_seam(clear=True)
            else:
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.mark_seam(clear=True)
            m3.set_mode("OBJECT")
    else:
        mesh = object.data
    mesh.polygons.active = 0

    m3.set_mode("EDIT")
    m3.set_mode("FACE")
    m3.unhide_all("MESH")
    m3.select_all("MESH")

    # if this is not set to True by DM and the user has it at False, nothing will be rotated
    bpy.context.scene.tool_settings.use_uv_select_sync = True

    # clear out all existing uv 'channels'
    uvs = mesh.uv_textures
    while uvs:
        uvs.remove(uvs[0])

    # add a new channel
    uvs.new('UVMap')

    # resetting will unwrap each quad perfectly fitting the uv space
    bpy.ops.uv.reset()

    # change context to UV editor
    oldcontext = m3.change_context('IMAGE_EDITOR')

    # Check if it is a result image linked, if there is, then no geometry will show in the image editor and nothing can be scaled or rotated
    # so we need to unlink the render result
    unlink_render_result()

    if not knife:
        # rotate 90° clockwise
        bpy.ops.transform.rotate(value=1.5708, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    # with each quad being separate, there will be smoothing issues(like hard edges) at panel bends
    # follow_active_quads solves that
    # bpy.ops.uv.follow_active_quads(mode='EVEN')
    bpy.ops.uv.follow_active_quads(mode='LENGTH')

    # the uv strip now extends the bounds, unfortunatly its centered only with an uneven amount of polygons
    # theres's the uv vertex x and y positions at the top right, which can be used to perfectly center the strip simply by making x = y(as y is already centered)
    # you could then scale it down along u a lot, turn on bouncdary limit and scale it up again and it will fit perfectily
    # these coordinates are the average positions of all selected verts

    # contrain uvs to uv/image bounds
    # bpy.context.space_data.uv_editor.lock_bounds = True

    # # scaling up a lot to hit those bounds and so fill out the entire uv space
    # bpy.ops.transform.resize(value=(1000, 1000, 1000), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    # # turning bounds off again
    # bpy.context.space_data.uv_editor.lock_bounds = False

    #TODO: set the cursor to the center using bpy.ops.uv.cursor_set(location=(0.5, 0.5))
    #TODO: set the pivot point to cursor: bpy.context.space_data.pivot_point = 'CURSOR'

    #TODO: you can fit the entire panel strip into 0-1 uv space using pack islands
    #TODO: you can scale it by setting the cursor to the bottom left corner and scaling up from there
    #TODO: the last two, should probably only be done for exporting, as its easier to work with the panel strips(when vert sliding for transitioning) when they are not tightly packed

    # change the context back to what it was
    m3.change_context(oldcontext)

    # go to object mode, except when panel_unwrap was called from edit mode
    if mode == "OBJECT":
        m3.set_mode("OBJECT")
