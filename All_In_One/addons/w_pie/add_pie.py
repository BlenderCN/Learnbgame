import bpy
from bpy.types import Menu
#
# bl_info = {
#     "name": "Add Object Pie Menu",
#     "author": "TARDIS Maker",
#     "version": (0, 0, 0),
#     "blender": (2, 72, 2),
#     "description": "A pie menu for adding objects",
#     "location": "SHIFT + A",
#     "category": "Learnbgame"
}









class add_node(bpy.types.Menu):
    bl_idname = "pie.add_node"
    bl_label = "add node"


    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
#4 - LEFT
        pie.operator("node.add_node", text="Diffuse", icon= 'SOLID').type='ShaderNodeBsdfDiffuse'
#6 - RIGHT
        pie.operator("node.add_node", icon= 'META_EMPTY').type='ShaderNodeBsdfTransparent'
#2 - BOTTOM
        pie.operator("node.add_node", text="Glossy", icon= 'MATERIAL').type='ShaderNodeBsdfGlossy'
#8 - TOP
        pie.operator("node.add_node", text="Emission", icon= 'LAMP_SUN').type='ShaderNodeEmission'
#7 - TOP - LEFT
        pie.operator("node.add_node", text="LayerWeight", icon= 'MOD_MIRROR').type='ShaderNodeLayerWeight'
#1 - BOTTOM - LEFT
        pie.operator("node.add_node", text="RGBCurve", icon= 'IPO_CIRC').type='ShaderNodeRGBCurve'
#3 - BOTTOM - RIGHT
        pie.operator("node.add_node", text="Glass", icon= 'MOD_MIRROR').type='ShaderNodeBsdfGlass'




        #ファイル、プロパティ関連
        box = pie.split().column()
        row = box.row(align=True)
        box.operator("node.add_node", text="NormalMap", icon= 'MOD_UVPROJECT').type='ShaderNodeNormalMap'
        box.operator("node.add_node", text="BumpMap", icon= 'MESH_CUBE').type='ShaderNodeBump'
        box.operator("node.add_node", text="Color Lamp", icon= 'IMAGE_COL').type='ShaderNodeValToRGB'
        box.operator("node.add_node", text="Bright Contrast", icon= 'IMAGE_COL').type='ShaderNodeBrightContrast'
        box.operator("node.add_node", text="Gamma", icon= 'IMAGE_COL').type='ShaderNodeGamma'
        box.operator("node.add_node", text="Noise", icon= 'SNAP_INCREMENT').type='ShaderNodeTexNoise'
        box.operator("node.add_node", text="Hue", icon= 'COLOR').type='ShaderNodeHueSaturation'

        box.operator("node.add_node", text="BW", icon= 'INLINK').type='ShaderNodeRGBToBW'





        return{'FINISHED'}
























class add_nurbs_curves(bpy.types.Operator):
    bl_idname = "object.add_nurbs_curves"
    bl_label = "add_nurbs_curves"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        layout = self.layout

        bpy.ops.curve.primitive_nurbs_path_add()
        #bpy.ops.curve.spline_type_set(type='NURBS')
        bpy.context.object.data.resolution_u = 3
        bpy.context.object.data.bevel_resolution = 2
        bpy.context.object.data.fill_mode = 'FULL'
        bpy.context.object.data.bevel_depth = 0.25
        bpy.ops.object.shade_flat()
        bpy.ops.shading.flat()

        return {'FINISHED'}




class VIEW3D_PIE_Add_Mesh(Menu):
    bl_idname = "add.mesh"
    bl_label = "Add Mesh"

    def draw(self, context):
        layout = self.layout


        pie = layout.menu_pie()
        pie.operator("mesh.primitive_cube_add", text="Add Cube", icon='MESH_CUBE')
        pie.operator("mesh.primitive_plane_add", text="Add Plane", icon='MESH_PLANE')
        pie.operator("mesh.primitive_circle_add", text="Add Circle", icon='MESH_CIRCLE')
        pie.operator("mesh.primitive_uv_sphere_add", text="Add UV Sphere", icon='MESH_UVSPHERE')
        pie.operator("mesh.primitive_ico_sphere_add", text="Add Ico Sphere", icon='MESH_ICOSPHERE')
        pie.operator("mesh.primitive_cylinder_add", text="Add Cylinder", icon='MESH_CYLINDER')
        pie.operator("mesh.primitive_cone_add", text="Add Cone", icon='MESH_CONE')
        pie.operator("mesh.primitive_torus_add", text="Add Torus", icon='MESH_TORUS')

class VIEW3D_PIE_Add_Curve(Menu):
    bl_idname = "add.curve"
    bl_label = "Add Curve"

    def draw(self, context):
        layout = self.layout


        pie = layout.menu_pie()
        pie.operator("curve.primitive_bezier_curve_add", text="Add Bezier Curve", icon='CURVE_BEZCURVE')
        pie.operator("object.add_nurbs_curves", text="Tube", icon='CURVE_PATH')
        pie.operator("curve.primitive_nurbs_path_add", text="Add Nurbs Path", icon='CURVE_PATH')
        pie.operator("curve.primitive_bezier_circle_add", text="Add Bezier Circle", icon='CURVE_BEZCIRCLE')
        pie.operator("curve.primitive_nurbs_curve_add", text="Add Nurbs Curve", icon='CURVE_NCURVE')
        pie.operator("curve.primitive_nurbs_circle_add", text="Add Nurbs Circle", icon='CURVE_NCIRCLE')




class VIEW3D_PIE_Add_Lamp(Menu):
    bl_idname = "add.lamp"
    bl_label = "Add Lamp"

    def draw(self, context):
        layout = self.layout


        pie = layout.menu_pie()
        pie.operator("object.lamp_add", text="Point Lamp", icon='LAMP_POINT').type='POINT'
        pie.operator("object.lamp_add", text="Sun Lamp", icon='LAMP_SUN').type='SUN'
        pie.operator("object.lamp_add", text="Spot Lamp", icon='LAMP_SPOT').type='SPOT'
        pie.operator("object.lamp_add", text="Hemi Lamp", icon='LAMP_HEMI').type='HEMI'
        pie.operator("object.lamp_add", text="Area Lamp", icon='LAMP_AREA').type='AREA'



class VIEW3D_PIE_Add_Surface(Menu):
    bl_idname = "add.surface"
    bl_label = "Add Lamp"

    def draw(self, context):
        layout = self.layout


        pie = layout.menu_pie()
        pie.operator("surface.primitive_nurbs_surface_curve_add", text="Nurbs Curve", icon='SURFACE_NCURVE')
        pie.operator("surface.primitive_nurbs_surface_circle_add", text="Nurbs Circle", icon='SURFACE_NCIRCLE')
        pie.operator("surface.primitive_nurbs_surface_surface_add", text="Nurbs Surface", icon='SURFACE_NSURFACE')
        pie.operator("surface.primitive_nurbs_surface_cylinder_add", text="Nurbs Cylinder", icon='SURFACE_NCYLINDER')
        pie.operator("surface.primitive_nurbs_surface_sphere_add", text="Nurbs Sphere", icon='SURFACE_NSPHERE')
        pie.operator("surface.primitive_nurbs_surface_torus_add", text="Nurbs Torus", icon='SURFACE_NTORUS')



class VIEW3D_PIE_Add_MetaBall(Menu):
    bl_idname = "add.metaball"
    bl_label = "Add MetaBall"

    def draw(self, context):
        layout = self.layout


        pie = layout.menu_pie()
        pie.operator("object.metaball_add", text="Ball", icon='META_BALL').type='BALL'
        pie.operator("object.metaball_add", text="Capsule", icon='META_CAPSULE').type='CAPSULE'
        pie.operator("object.metaball_add", text="Plane", icon='META_PLANE').type='PLANE'
        pie.operator("object.metaball_add", text="Ellipsoid", icon='META_ELLIPSOID').type='ELLIPSOID'
        pie.operator("object.metaball_add", text="Cube", icon='META_CUBE').type='CUBE'



class VIEW3D_PIE_Add_ForceField(Menu):
    bl_idname = "add.force-field"
    bl_label = "Add Force Field"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.effector_add", text="Force", icon='FORCE_FORCE').type='FORCE'
        layout.operator("object.effector_add", text="Wind", icon='FORCE_WIND').type='WIND'
        layout.operator("object.effector_add", text="Vortex", icon='FORCE_VORTEX').type='VORTEX'
        layout.operator("object.effector_add", text="Magnetic", icon='FORCE_MAGNETIC').type='MAGNET'
        layout.operator("object.effector_add", text="Harmonic", icon='FORCE_HARMONIC').type='HARMONIC'
        layout.operator("object.effector_add", text="Charge", icon='FORCE_CHARGE').type='CHARGE'
        layout.operator("object.effector_add", text="Lennard-Jones", icon='FORCE_LENNARDJONES').type='LENNARDJ'
        layout.operator("object.effector_add", text="Curve Guide", icon='FORCE_CURVE').type='GUIDE'
        layout.operator("object.effector_add", text="Boid", icon='FORCE_BOID').type='BOID'
        layout.operator("object.effector_add", text="Turbulence", icon='FORCE_TURBULENCE').type='TURBULENCE'
        layout.operator("object.effector_add", text="Drag", icon='FORCE_DRAG').type='DRAG'
        layout.operator("object.effector_add", text="Smoke Flow", icon='FORCE_SMOKEFLOW').type='SMOKE'







class VIEW3D_PIE_Add_Other(Menu):
    bl_idname = "add.other"
    bl_label = "Add Other"

    def draw(self, context):
        layout = self.layout


        pie = layout.menu_pie()
        pie.operator("wm.call_menu_pie", text="Surface", icon='OUTLINER_OB_SURFACE').name = "add.surface"
        pie.operator("object.empty_add", icon='OUTLINER_OB_EMPTY').type = 'PLAIN_AXES'
#        pie.operator("wm.call_menu_pie", text="Metaball", icon='OUTLINER_OB_META').name = "add.metaball"
#        pie.menu("add.force-field", text="Force Field", icon='OUTLINER_OB_EMPTY')
        pie.operator("object.add_coordinated_lattice", text="Lattice", icon='OUTLINER_OB_LATTICE')
        pie.operator("object.speaker_add", text="Speaker", icon='SPEAKER')



# カメラ
        pie.operator("object.camera_add", text="Camera", icon='OUTLINER_DATA_CAMERA')

#アーマチュア
        pie.operator("object.armature_add", text="Single Bone", icon='BONE_DATA')
#エンプティ
        pie.operator("object.empty_add", text="Empty", icon='OUTLINER_DATA_EMPTY')
# テキスト
        pie.operator("object.text_add", text="Text", icon='FONT_DATA')




class VIEW3D_PIE_Add_Menu(Menu):
    bl_idname = "add.menu"
    bl_label = "Add"


    def draw(self, context):
        layout = self.layout


        pie = layout.menu_pie()


        pie.operator("mesh.primitive_cube_add", text="Add Cube", icon='MESH_CUBE')
        pie.operator("mesh.primitive_plane_add", text="Add Plane", icon='MESH_PLANE')
#        pie.operator("mesh.primitive_circle_add", text="Add Circle", icon='MESH_CIRCLE')
        pie.operator("mesh.primitive_uv_sphere_add", text="Add UV Sphere", icon='MESH_UVSPHERE')
#        pie.operator("mesh.primitive_ico_sphere_add", text="Add Ico Sphere", icon='MESH_ICOSPHERE')
        pie.operator("mesh.primitive_cylinder_add", text="Add Cylinder", icon='MESH_CYLINDER')
#        pie.operator("mesh.primitive_cone_add", text="Add Cone", icon='MESH_CONE')
#        pie.operator("mesh.primitive_torus_add", text="Add Torus", icon='MESH_TORUS')


# メッシュのリスト。なんかエラーが出る
# 		pie.operator("wm.call_menu_pie", text="Mesh", icon='OUTLINER_OB_MESH').name = "add.mesh"

        pie.operator("wm.call_menu_pie", text="Curve", icon='OUTLINER_OB_CURVE').name = "add.curve"
        pie.operator("wm.call_menu_pie", text="Lamp", icon='OUTLINER_OB_LAMP').name = "add.lamp"
        pie.operator("wm.call_menu_pie", text="Other", icon='PLUS').name = "add.other"
        pie.operator("mesh.primitive_monkey_add", text="Add Monkey", icon='MESH_MONKEY')








addon_keymaps = []

def register():
    # print("starting to register")
    # bpy.utils.unregister_class(add_node)
    # bpy.utils.register_class(add_nurbs_curves)
    # bpy.utils.register_class(VIEW3D_PIE_Add_Menu)
    # bpy.utils.register_class(VIEW3D_PIE_Add_Mesh)
    # bpy.utils.register_class(VIEW3D_PIE_Add_Curve)
    # bpy.utils.register_class(VIEW3D_PIE_Add_Lamp)
    # bpy.utils.register_class(VIEW3D_PIE_Add_Other)
    # bpy.utils.register_class(VIEW3D_PIE_Add_Surface)
    # bpy.utils.register_class(VIEW3D_PIE_Add_MetaBall)
    # bpy.utils.register_class(VIEW3D_PIE_Add_ForceField)


    #Keymaps

    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new("wm.call_menu_pie", "RIGHTMOUSE", "PRESS", shift=True)
    kmi.properties.name="add.menu"
    addon_keymaps.append(km)
    print(kmi.properties.name)

    #mesh edit mode
    km = wm.keyconfigs.addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("wm.call_menu_pie", "RIGHTMOUSE", "PRESS", shift=True)
    kmi.properties.name="add.mesh"
    addon_keymaps.append(km)
    print(kmi.properties.name)

    #curve edit mode
    km = wm.keyconfigs.addon.keymaps.new(name="Curve")
    kmi = km.keymap_items.new("wm.call_menu_pie", "RIGHTMOUSE", "PRESS", shift=True)
    kmi.properties.name="add.curve"
    addon_keymaps.append(km)
    print(kmi.properties.name)

    #mataball edit mode
    km = wm.keyconfigs.addon.keymaps.new(name="Metaball")
    kmi = km.keymap_items.new("wm.call_menu_pie", "RIGHTMOUSE", "PRESS", shift=True)
    kmi.properties.name="add.metaball"
    addon_keymaps.append(km)

    #mataball edit mode
    # km = wm.keyconfigs.addon.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
    km = wm.keyconfigs.addon.keymaps.new(name = "Node Editor", space_type = "NODE_EDITOR")
    kmi = km.keymap_items.new("wm.call_menu_pie", "RIGHTMOUSE", "PRESS", shift=True)
    kmi.properties.name="add.add_node"
    addon_keymaps.append(km)
    #
    # global addon_keymaps
    # wm = bpy.context.window_manager
    # km = wm.keyconfigs.addon.keymaps.new(name = "Node Editor", space_type = "NODE_EDITOR")
    # kmi = km.keymap_items.new("wm.call_menu_pie", type = "E",alt=True, value = "PRESS")
    # kmi.properties.name = "view3d.switcher"
    # addon_keymaps.append(km)

    print(kmi.properties.name)






















    # addon_keymaps = []
    # # kmi_defs entry: (identifier, key, action, CTRL, SHIFT, ALT, props, nice name)
    # # props entry: (property name, property value)
    # kmi_defs = (
    #     # MERGE NODES
    #     # NWMergeNodes with Ctrl (AUTO).
    #     (NWMergeNodes.bl_idname, 'NUMPAD_0', 'PRESS', True, False, False,
    #         (('mode', 'MIX'), ('merge_type', 'AUTO'),), "Merge Nodes (Automatic)"),
    # )
    #
    #
    # def register():
    #
    #     bpy.utils.register_module(__name__)
    #
    #     # keymaps
    #     addon_keymaps.clear()
    #     kc = bpy.context.window_manager.keyconfigs.addon
    #     if kc:
    #         km = kc.keymaps.new(name='Node Editor', space_type="NODE_EDITOR")
    #         for (identifier, key, action, CTRL, SHIFT, ALT, props, nicename) in kmi_defs:
    #             kmi = km.keymap_items.new(identifier, key, action, ctrl=CTRL, shift=SHIFT, alt=ALT)
    #             if props:
    #                 for prop, value in props:
    #                     setattr(kmi.properties, prop, value)
    #             addon_keymaps.append((km, kmi))

























# Register / Unregister Classes
def unregister():
    bpy.utils.unregister_class(w_pie_Prefs)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()


# def unregister():
#     bpy.utils.unregister_class(add_nurbs_curves)
#     bpy.utils.unregister_class(add_node)
#     bpy.utils.unregister_class(VIEW3D_PIE_Add_Menu)
#     bpy.utils.unregister_class(VIEW3D_PIE_Add_Mesh)
#     bpy.utils.unregister_class(VIEW3D_PIE_Add_Curve)
#     bpy.utils.unregister_class(VIEW3D_PIE_Add_Lamp)
#     bpy.utils.unregister_class(VIEW3D_PIE_Add_Other)
#     bpy.utils.unregister_class(VIEW3D_PIE_Add_Surface)
#     bpy.utils.unregister_class(VIEW3D_PIE_Add_MetaBall)
#     bpy.utils.unregister_class(VIEW3D_PIE_Add_ForceField)
#
#     wm = bpy.context.window_manager
#
#     print("about to clear keymap")
#     for km in addon_keymaps:
#         print(km)
#         for kmi in km.keymap_items:
#             print(kmi.properties.name)
#             km.keymap_items.remove(kmi)
#
#         wm.keyconfigs.addon.keymaps.remove(km)
#
#     # clear the list
#     del addon_keymaps[:]
#
# if __name__ == "__main__":
#     register()
