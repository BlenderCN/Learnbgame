from mathutils import Matrix, Vector
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy.types import Menu
import bpy
import bmesh

bl_info = {
    "name": "Pie Normal",
    "description": "",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}


class TILA_MT_pie_normal(Menu):
    bl_idname = "TILA_MT_pie_normal"
    bl_label = "Normal"

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object
        pie = layout.menu_pie()
        # Left
        split = pie.split()
        split.scale_y = 3
        split.scale_x = 1.5
        if context.mode == "OBJECT":
            text = 'Smooth'
        else:
            text = 'Merge'

        split.operator("view3d.tila_normalsmartmerge", icon='NODE_MATERIAL', text=text)

        # Right
        split = pie.split()
        split.scale_y = 3
        split.scale_x = 1.5
        split.operator("view3d.tila_normalsmartsplit", icon='MESH_CUBE', text="Split")

        # Bottom
        split = pie.split()
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1
        col.operator("mesh.tila_normalaverage", icon='META_CUBE', text="Average Normal")
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1
        col.operator("mesh.tila_normaluseface", icon='MOD_SOLIDIFY', text="Use Face Normal")
        col.operator("mesh.tila_normalsmoothen", icon='INVERSESQUARECURVE', text="Smoothen Normal")

        # Top
        split = pie.split()
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1
        if context.mode == "EDIT_MESH":
            col.operator('mesh.tila_normalflatten', icon='NORMALS_FACE', text='Flatten Normal')

        # Top Left

        split = pie.split()

        # Top Right
        split = pie.split()

        # Bottom Left

        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1

        # Bottom Right
        split = pie.split()
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1
        col.prop(view.overlay, "show_split_normals", text="Show Vertex Normal", icon='NORMALS_VERTEX_FACE')
        col = split.column()
        col.prop(view.overlay, "normals_length", text="Size")

        # bpy.context.space_data.overlay.show_split_normals = True


def element_is_selected(object):
    bm = bmesh.from_edit_mesh(object.data)
    if bpy.context.scene.tool_settings.mesh_select_mode[0]:
        for v in bm.verts:
            if v.select:
                return True
        else:
            return False
    if bpy.context.scene.tool_settings.mesh_select_mode[1]:
        for e in bm.edges:
            if e.select:
                return True
        else:
            return False
    if bpy.context.scene.tool_settings.mesh_select_mode[2]:
        for f in bm.faces:
            if f.select:
                return True
        else:
            return False


def run_on_selection(context, functions):
    def run_cmd(object, functions, mode):
        def run():
            if functions[mode]:
                for f in functions[mode]:
                    kwargs = f[1]
                    if kwargs:
                        f[0](**kwargs)
                    else:
                        f[0]()

        if mode == 'OBJECT':
            run()
        else:
            if element_is_selected(object):
                run()

    active = bpy.context.active_object

    if active:
        selection = bpy.context.selected_objects
        if active not in selection:
            selection.append(active)

        for o in selection:
            context.view_layer.objects.active = o
            if context.mode == "EDIT_MESH":
                if bpy.context.scene.tool_settings.mesh_select_mode[0]:
                    run_cmd(o, functions, 'VERT')
                if bpy.context.scene.tool_settings.mesh_select_mode[1]:
                    run_cmd(o, functions, 'EDGE')
                if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                    run_cmd(o, functions, 'FACE')
            elif context.mode == "OBJECT":
                run_cmd(o, functions, 'OBJECT')


def flatten_normals(context):
    pass


class TILA_OT_selectBorderEdges(bpy.types.Operator):
    bl_idname = "mesh.tila_selectborderedges"
    bl_label = "Tilapiatsu select border edge of current face selection"
    bl_options = {'REGISTER', 'UNDO'}

    mode = bpy.props.EnumProperty(name='mode', items=(('ACTIVE', 'Active', 'Active'), ('SELECTED', 'Selected', 'Selected')), default='SELECTED')

    def select_border(self, context, object):
        if context.mode == "EDIT_MESH":
            if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                try:
                    if element_is_selected(object):
                        bpy.ops.mesh.region_to_loop()
                        if not element_is_selected(object):
                            bpy.ops.mesh.select_all(action='INVERT')
                except Exception as e:
                    print(e)

    def execute(self, context):
        active = bpy.context.active_object
        if active:
            if self.mode == 'SELECTED':
                selection = bpy.context.selected_objects
                if active not in selection:
                    selection.append(active)

                for o in selection:
                    context.view_layer.objects.active = o
                    self.select_border(context, o)
            elif self.mode == 'ACTIVE' and active is not None:
                self.select_border(context, active)
        return {'FINISHED'}


class TILA_OT_normalflatten(bpy.types.Operator):
    bl_idname = "mesh.tila_normalflatten"
    bl_label = "Tilapiatsu Flatten Normals"
    bl_options = {'REGISTER', 'UNDO'}

    def update_customnormals(self, mesh, normalslist):
        if len(normalslist) > 0:
            if mesh.use_auto_smooth:
                newnormslist = ()
                
                for f in mesh.polygons:
                    for i in range(len(f.vertices)):
                        if f.select:
                            newnormslist = newnormslist + ((normalslist[0][0].x, normalslist[0][0].y, normalslist[0][0].z),)
                        else:
                            newnormslist = newnormslist + ((f.normal.x, f.normal.y, f.normal.z),)

                # for f in normalslist:
                #     newnormslist = tuple([(n.x, n.y, n.z) for n in f])

                print('newnormslist', newnormslist)
                mesh.calc_normals_split()

                for e in mesh.edges:
                    e.use_edge_sharp = False

                mesh.validate(clean_customdata=False)
                mesh.normals_split_custom_set(newnormslist)
                mesh.free_normals_split()
                mesh.update()
                return True

            else:
                meshverts = []
                if bpy.context.mode == 'EDIT_MESH':
                    bm = bmesh.from_edit_mesh(mesh)
                    meshverts = [v for v in bm.verts]

                    for v_index, v in enumerate(meshverts):
                        v.normal = normalslist[v_index].copy()

                    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
                    mesh.update()
                else:
                    bm = bmesh.new()
                    bm.from_mesh(mesh)
                    meshverts = [v for v in bm.verts]

                    for v_index, v in enumerate(meshverts):
                        v.normal = normalslist[v_index].copy()

                    bm.to_mesh(mesh)

                del meshverts[:]
                return True

        return False

    def flatten_new(self, context, object):
        # https://github.com/isathar/Blender-Normal-Editing-Tools/blob/master/custom_normals_editor/normeditor_functions.py
        mesh = object.data
        bm = bmesh.from_edit_mesh(mesh)

        normalsdata = []
        normalsdata_proc = []

        # Get selected faces
        selected_face = [f for f in bm.faces if f.select]

        # sum all selected normals
        sum = Vector((1, 1, 1))
        for f in selected_face:
            sum = sum + f.normal.copy()
        length = len(selected_face)
        sum = Vector((sum.x / length, sum.y / length, sum.z / length)).normalized()

        for f_index, f in enumerate(bm.faces):
            normalsdata_proc.append([])

            for i_index, i in enumerate(f.verts):
                if f.select:
                    normalsdata_proc[f_index].append(sum)
                else:
                    normalsdata_proc[f_index].append((i.normal.copy().normalized()))
        
        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)

        if (self.update_customnormals(mesh, normalsdata_proc)):
            context.area.tag_redraw()
            context.scene.update()

        # clean up
        del normalsdata_proc[:]

    def flatten(self, context, object):
        mesh = object.data
        bm = bmesh.from_edit_mesh(mesh)

        if bpy.context.scene.tool_settings.mesh_select_mode[0]:
            bpy.ops.mesh.select_mode(type="FACE")
        if bpy.context.scene.tool_settings.mesh_select_mode[1]:
            bpy.ops.mesh.select_mode(type="FACE")
        if bpy.context.scene.tool_settings.mesh_select_mode[2]:
            selected = []

            # Get selected faces
            for f in bm.faces:
                if f.select:
                    selected.append(f)

            # sum all selected normals
            sum = Vector((1, 1, 1))
            for f in selected:
                sum = sum + f.normal
            length = len(selected)
            sum = (sum.x / length, sum.y / length, sum.z / length)

            sum = Vector(sum)
            sum.normalize()

            print(sum)

            for f in selected:
                for v in f.verts:
                    v.normal = sum

                # f.normal_update()
            # bm.select_flush(True)
            bmesh.update_edit_mesh(mesh)
            mesh.update()
            # bpy.ops.mesh.normals_make_consistent()

    def execute(self, context):
        active = bpy.context.active_object

        if active:
            selection = bpy.context.selected_objects

            if active not in selection:
                selection.append(active)

            for o in selection:
                context.view_layer.objects.active = o

                self.flatten(context, o)

        return {'FINISHED'}

def get_mesh_select_mode():
    return (bpy.context.scene.tool_settings.mesh_select_mode[0], bpy.context.scene.tool_settings.mesh_select_mode[1], bpy.context.scene.tool_settings.mesh_select_mode[2])
    
def set_mesh_select_mode(mode):
    print(mode)
    i=0
    for i in range(len(mode)):
        bpy.context.scene.tool_settings.mesh_select_mode[i] = mode[i]
        i += 1

class TILA_OT_normalaverage(bpy.types.Operator):
    bl_idname = "mesh.tila_normalaverage"
    bl_label = "Tilapiatsu Average Normals"
    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.average_normals, {'average_type': 'FACE_AREA'}),),
            'EDGE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.average_normals, {'average_type': 'FACE_AREA'}),),
            'FACE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.average_normals, {'average_type': 'FACE_AREA'}))}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_normaluseface(bpy.types.Operator):
    bl_idname = "mesh.tila_normaluseface"
    bl_label = "Tilapiatsu Use Face Normals"
    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.set_normals_from_faces, None)),
            'EDGE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.set_normals_from_faces, None)),
            'FACE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.set_normals_from_faces, None))}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_normalsmoothen(bpy.types.Operator):
    bl_idname = "mesh.tila_normalsmoothen"
    bl_label = "Tilapiatsu Smoothen Normals"
    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.smoothen_normals, {'factor': 1}),),
            'EDGE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.smoothen_normals, {'factor': 1}),),
            'FACE': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.smoothen_normals, {'factor': 1}))}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_smartsplit(bpy.types.Operator):
    bl_idname = "view3d.tila_normalsmartsplit"
    bl_label = "Tilapiatsu Smartly Split vertex normal"
    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.normals_tools, {'mode': 'RESET'}), (bpy.ops.view3d.tila_splitnormal, None)),
            'EDGE': ((bpy.ops.view3d.tila_splitnormal, None),),
            'FACE': ((bpy.ops.mesh.tila_selectborderedges, {'mode': 'ACTIVE'}), (bpy.ops.view3d.tila_splitnormal, None)),
            'OBJECT': ((bpy.ops.object.shade_flat, None),)}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_normalsmartmerge(bpy.types.Operator):
    bl_idname = "view3d.tila_normalsmartmerge"
    bl_label = "Tilapiatsu Smartly merge vertex normal"

    bl_options = {'REGISTER', 'UNDO'}

    func = {'VERT': ((bpy.ops.view3d.tila_autosmooth, None), (bpy.ops.mesh.smoothen_normals, {'factor': 1}), (bpy.ops.view3d.tila_smoothnormal, None)),
            'EDGE': ((bpy.ops.view3d.tila_smoothnormal, None),),
            'FACE': ((bpy.ops.mesh.tila_selectborderedges, {'mode': 'ACTIVE'}), (bpy.ops.view3d.tila_smoothnormal, None)),
            'OBJECT': ((bpy.ops.object.shade_smooth, None),)}

    def execute(self, context):

        run_on_selection(context, self.func)

        return {'FINISHED'}


class TILA_OT_autoSmooth(bpy.types.Operator):
    bl_idname = "view3d.tila_autosmooth"

    bl_label = "Tilapiatsu Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    value = bpy.props.BoolProperty(name='value', default=True)

    def execute(self, context):
        active = bpy.context.active_object

        if active:
            sel = bpy.context.selected_objects
            if active not in sel:
                sel.append(active)

            for obj in sel:
                obj.data.use_auto_smooth = self.value

        return {'FINISHED'}


class TILA_OT_splitNormal(bpy.types.Operator):
    bl_idname = "view3d.tila_splitnormal"
    bl_label = "Tilapiatsu Split Normal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.view3d.tila_autosmooth(value=True)
        bpy.ops.mesh.split_normals()
        return {'FINISHED'}


class TILA_OT_smoothNormal(bpy.types.Operator):
    bl_idname = "view3d.tila_smoothnormal"
    bl_label = "Tilapiatsu Smooth Normal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.view3d.tila_autosmooth(value=True)
        bpy.ops.mesh.merge_normals()
        return {'FINISHED'}


classes = (
    TILA_MT_pie_normal,
    TILA_OT_autoSmooth


)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
