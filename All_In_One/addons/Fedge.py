bl_info = {
    "name": "Fedge",
    "author": "nikitron.cc.ua",
    "version": (0, 6, 2),
    "blender": (2, 7, 5),
    "location": "View3D > Tool Shelf > 1D > select loose",
    "description": "selects objects and edges that lost",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
from bpy.props import BoolProperty

WRONG_AREA = 0.02

class D1_fedge(bpy.types.Operator):
    ''' \
    Select loose parts. edges first, vertices second, non-quad polygons third. \
    Выделяет потеряные рёбра, потом вершины и грани, каждый раз вызываясь. \
    '''
    bl_idname = "object.fedge"
    bl_label = "Fedge"

    selected_show = False
    selected_hide = False

    def make_edges(self, edges):
        for e in edges:
            if e.is_loose:
                return True
        return False
    
    # makes indexes set for compare with vertices 
    # in object and find difference
    def make_indeces(self, list, vertices):
        for e in list:
            for i in e.vertices:
                vertices.add(i)

    def make_areas(self, pols):
        zerop = bpy.context.scene.zerop
        three = bpy.context.scene.three
        for p in pols:
            if p.area <= WRONG_AREA and zerop:
                return True
            if len(p.vertices) == 3 and three:
                return True
        return False
    
    def verts(self, obj,selected_hide,selected_show):
        # stage two verts
        if not bpy.context.scene.verts:
            return selected_show, selected_hide
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()
        vertices = set()
        self.make_indeces(obj.data.edges, vertices)
        self.make_indeces(obj.data.polygons, vertices)
        for i, ver in enumerate(obj.data.vertices):
            if i not in vertices and not ver.hide:
                ver.select = True
                selected_show = True
            elif i not in vertices and ver.hide:
                selected_hide = True
        bpy.ops.object.editmode_toggle()
        return selected_show, selected_hide
    
    def edges(self, obj,selected_hide,selected_show):
        # stage one edges
        if not bpy.context.scene.edges:
            return selected_show, selected_hide
        if not selected_show:
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()
            for edg in obj.data.edges:
                if edg.is_loose and not edg.hide:
                    edg.select = True
                    selected_show = True
                elif edg.is_loose and edg.hide:
                    selected_hide = True
            bpy.ops.object.editmode_toggle()
        return selected_show, selected_hide

    def zero(self, obj,selected_hide,selected_show):
        #stage area 0
        if not bpy.context.scene.zerop:
            return selected_show, selected_hide
        if not selected_show:
            bpy.ops.mesh.select_mode(type='FACE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()
            for pol in obj.data.polygons:
                if pol.area <= WRONG_AREA and not pol.hide:
                    pol.select = True
                    selected_show = True
                elif pol.area <= WRONG_AREA and pol.hide:
                    selected_hide = True
            bpy.ops.object.editmode_toggle()
        return selected_show, selected_hide

    def three(self, obj,selected_hide,selected_show):
        #stage three polygons
        if not bpy.context.scene.three:
            return selected_show, selected_hide
        if not selected_show:
            bpy.ops.mesh.select_mode(type='FACE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()
            for pol in obj.data.polygons:
                if len(pol.vertices) != 4 and not pol.hide:
                    pol.select = True
                    selected_show = True
                elif len(pol.vertices) != 4 and pol.hide:
                    selected_hide = True
            bpy.ops.object.editmode_toggle()
        return selected_show, selected_hide

    def select_loose_objt(self):
        objects = bpy.context.selected_objects
        if not objects:
            self.report({'ERROR'},\
                'ALARMA!!!\n'+
                'Fedge founds no objects selected.\n'+
                'Select objects or enter edit mode.')
            return
        bpy.ops.object.select_all(action='DESELECT')

        def dosel(obj, renam):
            obj.select = True
            if obj.name[:9] != '__empty__' and renam:
                obj.name = '__empty__' + obj.name

        for obj in objects:
            if obj.type != 'MESH':
                continue
            data = obj.data
            # zero-verts objs
            if bpy.context.scene.empty:
                if not len(data.vertices):
                    dosel(obj,True)
            # loose verts objs
            if bpy.context.scene.verts:
                vertices = set()
                self.make_indeces(data.edges, vertices)
                self.make_indeces(data.polygons, vertices)
                v = set([i for i in range(len(data.vertices))])
                if v.difference(vertices):
                    dosel(obj,False)
            # zero area pols condition in def
            if bpy.context.scene.zerop:
                if self.make_areas(obj.data.polygons):
                    dosel(obj,False)
            # loose edges
            if bpy.context.scene.edges:
                if self.make_edges(data.edges):
                    dosel(obj,False)
            # triangles
            if bpy.context.scene.three:
                for p in data.polygons:
                    if len(p.vertices) == 3:
                        dosel(obj,False)
            print(obj.name, obj.select)
                
    def select_loose_edit(self):
        obj = bpy.context.active_object
        selected_show = False
        selected_hide = False


        # stage two verts
        selected_show, selected_hide = self.verts(obj,selected_hide,selected_show)
        # stage one edges
        selected_show, selected_hide = self.edges(obj,selected_hide,selected_show)
        #stage area 0
        selected_show, selected_hide = self.zero(obj,selected_hide,selected_show)
        #stage three polygons
        selected_show, selected_hide = self.three(obj,selected_hide,selected_show)
        # object mode if mesh clean
        if selected_show:
            self.report({'INFO'}, \
                'FEDGE: Found something')
        elif selected_hide:
            self.report({'INFO'}, \
                'FEDGE: Nothing found (but hidden)')
        else:
            bpy.ops.object.editmode_toggle()
            self.report({'INFO'}, \
                'FEDGE: Your object is clean')

    def execute(self, context):
        if bpy.context.mode == 'OBJECT':
            self.select_loose_objt()
        elif bpy.context.mode == 'EDIT_MESH':
            self.select_loose_edit()
        return {'FINISHED'}

class D1_fedge_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Fedge"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = '1D'
    

    def draw(self, context):
        ''' \
        If not finds loose - returns object mode \
        Если нет потеряшек - возвращается в объектный режим \
        '''
        layout = self.layout
        row = layout.row(align=True)
        row.operator('object.fedge', text='fedge')
        if bpy.context.mode == 'OBJECT':
            row = layout.row(align=True)
            row.prop(bpy.context.scene, 'empty')
        row = layout.row(align=True)
        row.prop(bpy.context.scene, 'verts')
        row.prop(bpy.context.scene, 'edges')
        row = layout.row(align=True)
        row.prop(bpy.context.scene, 'zerop')
        row.prop(bpy.context.scene, 'three')

def register():
    bpy.types.Scene.verts = BoolProperty(name='verts', default=True,
            options={'ANIMATABLE'})
    bpy.types.Scene.edges = BoolProperty(name='edges', default=True,
            options={'ANIMATABLE'})
    bpy.types.Scene.zerop = BoolProperty(name='zerop', default=True,
            options={'ANIMATABLE'})
    bpy.types.Scene.empty = BoolProperty(name='empty', default=True,
            options={'ANIMATABLE'})
    bpy.types.Scene.three = BoolProperty(name='three', default=True,
            options={'ANIMATABLE'})

    bpy.utils.register_class(D1_fedge)
    bpy.utils.register_class(D1_fedge_panel)
    
    # short
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Fedge', space_type='EMPTY')
    kmi = km.keymap_items.new('object.fedge', 'L', 'PRESS', shift=True, ctrl=True, alt=True)
    addons_keymap = []
    addons_keymap.append((km, kmi))
    #km = wm.keyconfigs.addon.keymaps.new(name='Fedge', space_type='VIEW_3D')
    #kmi = km.keymap_items.new('mesh.fedge', 'L', 'PRESS', shift=True, ctrl=True, alt=True)
    #addons_keymap.append((km, kmi))
    #new_shortcut.properties.name = 'd1_select_loose_edges'

def unregister():
    bpy.utils.unregister_class(D1_fedge_panel)
    bpy.utils.unregister_class(D1_fedge)
    
    del bpy.types.Scene.verts, bpy.types.Scene.edges, \
        bpy.types.Scene.zerop, bpy.types.Scene.three
    
    for a, b in addons_keymap:
        a.keymap_items.remove(b)
        del a, b
    del addons_keymap

    
    del bpy.types.Scene.verts
    del bpy.types.Scene.edges
    del bpy.types.Scene.zerop
    del bpy.types.Scene.empty
    del bpy.types.Scene.three

if __name__ == "__main__":
    register()
