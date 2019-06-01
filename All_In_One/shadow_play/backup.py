# class AnimationBrushes:
#     gp = [None]
#     brush_dict = {}


# def AnimationHandlerUpdateBrushes(self, context):
#     if brushes.AnimationBrushes.gp[0] == None:
#         brushes.AnimationBrushes.gp[0] = bpy.data.grease_pencil.new('AnimationPencil')
#
#     gp = brushes.AnimationBrushes.gp[0]
#     context.scene.grease_pencil = gp
#
#     if 'FOLLOWPATH' not in brushes.AnimationBrushes.brush_dict:
#         layer = gp.layers.new('FOLLOWPATH')
#         layer.tint_color = (1.0, 0.0, 0.0)
#         layer.tint_factor = 1.0
#         brushes.AnimationBrushes.brush_dict['FOLLOWPATH'] = layer
#     if 'HPOINT' not in brushes.AnimationBrushes.brush_dict:
#         layer = gp.layers.new('HPOINT')
#         layer.tint_color = (0.5, 0.5, 0.5)
#         layer.tint_factor = 1.0
#         brushes.AnimationBrushes.brush_dict['HPOINT'] = layer
#     if 'ARAP' not in brushes.AnimationBrushes.brush_dict:
#         layer = gp.layers.new('ARAP')
#         layer.tint_color = (0.5, 1.0, 0.0)
#         layer.tint_factor = 1.0
#         brushes.AnimationBrushes.brush_dict['ARAP'] = layer
#
#     if context.scene.enum_brushes!=None:
#         gp.layers.active = brushes.AnimationBrushes.brush_dict[context.scene.enum_brushes]
#
#     return None


# import bpy
#
# # TODO, the patterns look similar, refactoring it later
#
# # https://blender.stackexchange.com/questions/23086/add-a-simple-vertex-via-python
# def create_triangle(name, verts):
#     # create a new mesh
#     mesh = bpy.data.meshes.new(name+'_mesh')
#     obj = bpy.data.objects.new(name, mesh)
#
#     # link
#     bpy.context.scene.objects.link(obj)
#     mesh.from_pydata(verts, [], [[0, 1, 2]])
#     mesh.update()
#     return obj
#
# # https://blender.stackexchange.com/questions/6750/poly-bezier-curve-from-a-list-of-coordinates
# def create_curve(name, verts):
#     curve = bpy.data.curves.new(name+'_curve', type='CURVE')
#     curve.dimensions = '3D'
#     curve.resolution_u = 2
#
#     polyline = curve.splines.new('NURBS')
#     polyline.points.add(len(verts))
#     for i, coord in enumerate(verts):
#         x, y, z = coord
#         polyline.points[i].co = (x, y, z, 1)
#
#     # link
#     obj = bpy.data.objects.new(name, curve)
#     bpy.context.scene.objects.link(obj)
#     return [obj, curve]

# def get_boundingbox_of_verts(verts):
#     import sys
#     bbx_min = sys.maxsize
#     bbx_max = -sys.maxsize
#     bbz_min = sys.maxsize
#     bbz_max = -sys.maxsize
#     for i in range(len(verts)):
#         if verts[i].x < bbx_min:
#             bbx_min = verts[i].x
#         if verts[i].x > bbx_max:
#             bbx_max = verts[i].x
#         if verts[i].z < bbz_min:
#             bbz_min = verts[i].z
#         if verts[i].z > bbz_max:
#             bbz_max = verts[i].z
#
#     return (bbx_min, bbx_max, bbz_min, bbz_max)

# class AnimationOperatorAddBone(bpy.types.Operator):
#     bl_idname = 'animation.add_bone'
#     bl_label = 'Add Bone'
#     bl_options = {'REGISTER', 'UNDO'}
#
#     def invoke(self, context, event):
#         bpy.ops.object.armature_add()
#         ob = bpy.context.scene.objects.active
#         ob.data.draw_type = 'STICK'
#         ob.show_x_ray = True
#         bpy.ops.object.mode_set(mode='EDIT')
#
#         return {'FINISHED'}

# def update_mode_func(self, context):
#     mode = context.scene.edit_mode
#     if mode=='Object':
#         bpy.ops.object.mode_set(mode='OBJECT')
#     elif mode=='Edit':
#         bpy.ops.object.mode_set(mode='EDIT')
#     elif mode=='Pose':
#         bpy.ops.object.mode_set(mode='POSE')

    # bpy.types.Scene.edit_mode = bpy.props.EnumProperty(name='Edit Mode',
    #                                                 description='Different Modes',
    #                                                 items=[('','',''),
    #                                                        ('Object','Object',''),
    #                                                        ('Edit','Edit',''),
    #                                                        ('Pose','Pose','')],
    #                                                 default='', update=update_mode_func)

            # column.prop(context.scene, 'construction_mode', text='Mode')
# # Operator
# class CameraOperatorSetting(bpy.types.Operator):
#     bl_idname = 'camera.setting'
#     bl_label = 'Camera Setting'
#     bl_options = {'REGISTER','UNDO'}
#
#     def invoke(self, context, event):
#         context.scene.cursor_location.x = context.scene.objects['Camera'].location.x
#         context.scene.cursor_location.y = context.scene.objects['Camera'].location.y+2.5
#         return {'FINISHED'}

# class DirectionPieMenu(Menu):
#     bl_idname = 'OBJECT_MT_direction_pie_menu'
#     bl_label = "Select Direction"
#
#     def draw(self, context):
#         layout = self.layout
#
#         pie = layout.menu_pie()
#         pie.operator_enum("mesh.select_mode", "type")
#
# class CameraUIPanel(Panel):
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'TOOLS'
#
#     bl_idname = 'OBJECT_PT_camera_path'
#     bl_label = 'Camera Path'
#     bl_context = 'objectmode'
#     bl_category = 'Easy Animation'
#
#     def draw(self, context):
#         layout = self.layout
#         camera = context.scene.objects['Camera']
#
#         box = layout.box()
#         box.prop(camera, 'location', text='')
#
#
#         box = layout.box()
#         box.label('Active Object')
#         obj = context.active_object
#         if obj==None:
#             return {'FINISHED'}
#
#         box.prop(obj, 'location', text='Location')
#
#

            # row = box.row()
            # row.prop(view, 'show_world', text='Show World')



                        # view = context.space_data

                                        # row = column.row()
                                        # row.operator('animation.add_bone', text='Add Bone', icon='BONE_DATA')
                                        # row.operator('armature.extrude', text='Extrude Bone')
                                        # row = column.row()
                                        # row.operator('object.parent_set', text='Bind', icon='CONSTRAINT')
                                        # row.operator('object.parent_set', text='Bone Deform', icon='OUTLINER_DATA_MESH')

                                                        # row.operator('gpencil.draw', text='Add Bone', icon='BONE_DATA').mode='DRAW'

                # row.operator('gpencil.draw', text='Add CP', icon='EDIT').mode='DRAW'

# class Stroke2Mesh(bpy.types.Operator):
#     bl_idname = 'gpencil.stroke2mesh'
#     bl_label = 'Convert Stroke to Mesh'
#
#     @classmethod
#     def poll(cls, context):
#         gp = context.scene.grease_pencil
#         return (gp!=None) and (gp.layers.active.active_frame.strokes!=None)
#
#     def invoke(self, context, event):
#         scene = context.scene
#         gp = context.scene.grease_pencil
#
#         strokes = gp.layers.active.active_frame.strokes
#         for i in range(len(strokes)):
#             stroke = strokes[i]
#             if stroke.select == True:
#                 # create a path
#                 verts = []
#                 points = stroke.points
#                 for j in range(len(stroke.points)):
#                     verts.append(points[j].co)
#
#                 curve = mesh.create_curve('test', verts)
#                 curve.fill_mode = 'FULL'
#                 curve.bevel_depth = 0.005
#                 material = bpy.data.materials.new(name="Material")
#                 material.diffuse_color[0] = 0.0
#                 material.diffuse_color[1] = 0.0
#                 material.diffuse_color[2] = 0.0
#                 curve.materials.append(material)
#
#
#                 # create all triangles
#                 # create a new material for triangles
#                 material = bpy.data.materials.new(name="Material")
#                 triangles = stroke.triangles
#                 for j in range(len(triangles)):
#                     v1 = triangles[j].v1
#                     v2 = triangles[j].v2
#                     v3 = triangles[j].v3
#                     co1 = stroke.points[v1].co
#                     co2 = stroke.points[v2].co
#                     co3 = stroke.points[v3].co
#                     obj = mesh.create_triangle('test', [co1, co2, co3])
#                     obj.data.materials.append(material)
#                     obj.show_transparent = True
#                     obj.active_material.diffuse_color[0] = stroke.color.fill_color[0]
#                     obj.active_material.diffuse_color[1] = stroke.color.fill_color[1]
#                     obj.active_material.diffuse_color[2] = stroke.color.fill_color[2]
#                     obj.active_material.alpha = stroke.color.fill_alpha
#         return {"FINISHED"}

#####################################################################
## Panels
#####################################################################
#
# class My_GPENCIL_UL_palettecolor(UIList):
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#         # assert(isinstance(item, bpy.types.PaletteColor)
#         palcolor = item
#
#         if self.layout_type in {'DEFAULT', 'COMPACT'}:
#             if palcolor.lock:
#                 layout.active = False
#
#             split = layout.split(percentage=0.25)
#             row = split.row(align=True)
#             row.enabled = not palcolor.lock
#             row.prop(palcolor, "color", text="", emboss=palcolor.is_stroke_visible)
#             row.prop(palcolor, "fill_color", text="", emboss=palcolor.is_fill_visible)
#             split.prop(palcolor, "name", text="", emboss=False)
#
#             row = layout.row(align=True)
#             row.prop(palcolor, "lock", text="", emboss=False)
#             row.prop(palcolor, "hide", text="", emboss=False)
#
#         elif self.layout_type == 'GRID':
#             layout.alignment = 'CENTER'
#             layout.label(text="", icon_value=icon)
#
# class My_GPENCIL_UL_layer(UIList):
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#         # assert(isinstance(item, bpy.types.GPencilLayer)
#         gpl = item
#
#         if self.layout_type in {'DEFAULT', 'COMPACT'}:
#             if gpl.lock:
#                 layout.active = False
#
#             row = layout.row(align=True)
#             if gpl.is_parented:
#                 icon = 'BONE_DATA'
#             else:
#                 icon = 'BLANK1'
#
#             row.label(text="", icon=icon)
#             row.prop(gpl, "info", text="", emboss=False)
#
#             row = layout.row(align=True)
#             row.prop(gpl, "lock", text="", emboss=False)
#             row.prop(gpl, "hide", text="", emboss=False)
#             row.prop(gpl, "unlock_color", text="", emboss=False)
#         elif self.layout_type == 'GRID':
#             layout.alignment = 'CENTER'
#             layout.label(text="", icon_value=icon)
#
#


# class NotInterestingPanel1(Panel):
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'TOOLS'
#
#     bl_idname = 'OBJECT_PT_notinerestingpanel1'
#     bl_label = 'Not Interesting Panel 1'
#     bl_context = 'objectmode'
#     bl_category = 'StayTuned'
#
#     def draw(self, context):
#         layout = self.layout
#         gp = context.scene.grease_pencil
#         view = context.space_data
#         world = context.scene.world
#         box = layout.box()
#         box.label('World Settings')
#         row = box.row()
#         split = row.split(percentage=0.55)
#         split.prop(view, "show_floor", text="Show Floor")
#         split.prop(view, "show_axis_x", text="X", toggle=True)
#         split.prop(view, "show_axis_y", text="Y", toggle=True)
#         split.prop(view, "show_axis_z", text="Z", toggle=True)
#
#         box.column().prop(view, 'show_world', text='Show World')
#         # box.column().prop(world, 'use_sky_paper', text='Use Skey Color')
#         # box.column().prop(world, 'use_sky_blend', text='Use Ground Color')
#         row = box.row()
#         row.column().prop(world, "horizon_color", text="Ground Color")
#         # row.column().prop(world, "zenith_color", text='Sky Color')
#
# class NotInterestingPanel2(Panel):
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'TOOLS'
#
#     bl_idname = 'OBJECT_PT_notinerestingpanel2'
#     bl_label = 'Not Interesting Panel 2'
#     bl_context = 'objectmode'
#     bl_category = 'StayTuned'
#
#     def draw(self, context):
#         layout = self.layout
#         gp = context.scene.grease_pencil
#
#         box = layout.box()
#         box.label('Color Palette')
#         palette = context.active_gpencil_palette
#         if palette != None:
#             # Palette colors
#             row = box.row()
#             col = row.column()
#             if len(palette.colors) >= 2:
#                 color_rows = 2
#             else:
#                 color_rows = 2
#             col.template_list("My_GPENCIL_UL_palettecolor", "", palette, "colors", palette.colors, "active_index",
#                               rows=color_rows)
#
#             col = row.column()
#             sub = col.column(align=True)
#             sub.operator("gpencil.palettecolor_add", icon='ZOOMIN', text="")
#             sub.operator("gpencil.palettecolor_remove", icon='ZOOMOUT', text="")
#
#             pcolor = palette.colors.active
#             if pcolor:
#                 self.draw_palettecolors(box, pcolor)
#
#         box = layout.box()
#         box.label('Painting Layers')
#         if gp!=None:
#             if len(gp.layers) >= 2:
#                 layer_rows = 2
#             else:
#                 layer_rows = 2
#             box.template_list("My_GPENCIL_UL_layer", "", gp, "layers", gp.layers, "active_index", rows=layer_rows)
#
#     # Draw palette colors
#     def draw_palettecolors(self, layout, pcolor):
#         # color settings
#         split = layout.split(percentage=0.5)
#         split.active = not pcolor.lock
#
#         # Column 1 - Stroke
#         col = split.column(align=True)
#         col.enabled = not pcolor.lock
#         col.prop(pcolor, "color", text="Stroke Color")
#         col.prop(pcolor, "alpha", slider=True)
#
#         # Column 2 - Fill
#         col = split.column(align=True)
#         col.enabled = not pcolor.lock
#         col.prop(pcolor, "fill_color", text="Filling Color")
#         col.prop(pcolor, "fill_alpha", text="Opacity", slider=True)
#
#         # Options
#         split = layout.split(percentage=0.5)
#         split.active = not pcolor.lock
#




# class CGenerating(bpy.types.Operator):
#     bl_idname = "gpencil.cgenerating"
#     bl_label = "Generate Selected GPencil Strokes"
#     bl_options = {"UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         scene = context.scene
#         gp = context.scene.grease_pencil
#         return (gp != None) and (len(gp.layers['GP_Layer'].active_frame.strokes)!=0)
#
#     def invoke(self, context, event):
#         scene = context.scene
#         gp = context.scene.grease_pencil
#
#         sketch_strokes = gp.layers['GP_Layer'].active_frame.strokes
#         construct_strokes = gp.layers['gpl_constructing'].active_frame.strokes
#
#         position = []
#         for i in range(len(construct_strokes)):
#             construct_stroke = construct_strokes[i]
#             for i, point in enumerate(construct_stroke.points):
#                 position.append(point.co)
#
#         for k in range(len(position)):
#             for i in range(len(sketch_strokes)):
#                 sketch_stroke = sketch_strokes[i]
#                 if sketch_stroke.select==True:
#                     new_stroke = sketch_strokes.new(sketch_stroke.colorname)
#                     new_stroke.draw_mode = '3DSPACE'
#                     new_stroke.points.add(count=len(sketch_stroke.points))
#
#                     points = sketch_stroke.points
#                     for i, point in enumerate(points):
#                         new_stroke.points[i].co = points[i].co + position[k]
#
#
#         # nlayer = len(gp.layers)
#         # print('num of layers: ' + str(nlayer))
#         # nframe = {}
#         # for i in nlayer:
#         #     nframe[i] = len(gp.layers[i].frames)
#         #     print('num of frames: ' + str(nframe[i]))
#
#         # https://blender.stackexchange.com/questions/48992/how-to-add-points-to-a-grease-pencil-stroke-or-make-new-one-with-python-script
#         # https://blender.stackexchange.com/questions/24694/query-grease-pencil-strokes-from-python
#         # omit all setups
#         # counter = 0
#         # active_strokes = gp.layers.active.active_frame.strokes
#         # for i in range(len(active_strokes)): # MUST use this pattern!
#         #     old_stroke = active_strokes[i]
#         #     if old_stroke.select==True:
#         #         counter += 1
#         #         # API: https://docs.blender.org/api/current/bpy.types.GPencilStrokes.html#bpy.types.GPencilStrokes.new
#         #         new_stroke = active_strokes.new(old_stroke.colorname)
#         #
#         #         new_stroke.draw_mode = '3DSPACE'
#         #         #new_stroke.color = old_stroke.color
#         #         new_stroke.points.add(count=len(old_stroke.points))
#         #
#         #         points = old_stroke.points
#         #         for i, point in enumerate(points):
#         #             points[i].co = old_stroke.points[i].co + mathutils.Vector((1, 1, 1))
#         return {"FINISHED"}


# for constructing scenes
# class CStartRepetition(bpy.types.Operator):
#     bl_idname = "gpencil.cstartrepetition"
#     bl_label = "Start Repetition for Constructing"
#     bl_options = {"UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         gp = context.scene.grease_pencil
#         return (gp != None) and (gp.layers != None)
#
#     def invoke(self, context, event):
#         scene = context.scene
#         gp = context.scene.grease_pencil
#
#         gpl_constructing = gp.layers.new('gpl_constructing', set_active = True )
#         # if gpl_constructing.frames:
#         #     fr = gpl_constructing.active_frame
#         # else:
#         #     fr = gpl_constructing.frames.new(1)
#         #
#         # str = fr.strokes.new()
#         # str.draw_mode = '3DSPACE'
#
#         return {"FINISHED"}






# class ReArrangeLayout(bpy.types.Operator):
#     bl_idname = 'layout.relayout'
#     bl_label = 'Update the stroke to relayout the instances'
#     bl_options = {'UNDO', 'REGISTER'}
#
#     @classmethod
#     def poll(cls, context):
#         return context.scene.grease_pencil.layers.active.active_frame != None
#
#     def invoke(self, context, event):
#         gp = context.scene.grease_pencil
#         scene = context.scene
#
#         strokes = gp.layers.active.active_frame.strokes
#
#         if gp==None:
#             return {'FINISHED'}
#         if len(strokes)==0:
#             return {'FINISHED'}
#
#         bpy.ops.object.mode_set(mode='GPENCIL_EDIT')
#         scene.tool_settings.proportional_edit = 'CONNECTED'
#
#         # for i in range(len)
#
#
#         scene.tool_settings.proportional_size = 1
#
#         bpy.ops.transform.translate()
#
#
#         return {'FINISHED'}





# this is a good example to illustrate the usage of execute, invoke, and modal
# class Instancing(bpy.types.Operator):
#     bl_idname = "gpencil.instancing"
#     bl_label = "Instancing based on strokes"
#     bl_options = {"UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         return (context.area.type == "VIEW_3D")
#
#     def __init__(self):
#         print("Start Invoke")
#         # bpy.ops.gpencil.draw(mode='DRAW')
#
#     def __del__(self):
#         print("End Invoke")
#
#     # def execute(self, context):
#     #     print('I am execute')
#     #     return {'FINISHED'}
#     #
#     def modal(self, context, event):
#         if event.type == 'MOUSEMOVE':
#             # bpy.ops.gpencil.draw('INVOKE_DEFAULT',mode='DRAW')
#             # self.execute(context)
#             return {'RUNNING_MODAL'}
#         if event.type == 'LEFTMOUSE':
#             if event.value == 'RELEASE':
#         #     print('rightmouse')
#                 return {'FINISHED'}
#             elif event.type == 'PRESS':
#                 # bpy.ops.gpencil.draw('INVOKE_DEFAULT',mode='DRAW')
#                 return {'RUNNING_MODAL'}
#         return {'PASS_THROUGH'}
#
#     def invoke(self, context, event):
#         bpy.ops.gpencil.draw('INVOKE_DEFAULT',mode='DRAW')
#         print('I am invoke')
#         # self.execute(context)
#         context.window_manager.modal_handler_add(self)
#         return {'RUNNING_MODAL'}
#

# class SelectObject(bpy.types.Operator):
#     bl_idname = "instance.selectobject"
#     bl_label = "Select Object"
#     bl_options = {"UNDO"}
#
#     @classmethod
#     def poll(cls, context):
#         return (context.area.type == "VIEW_3D")
#
#     # def __init__(self):
#     #     # print("Start Invoke")
#     #     # bpy.ops.gpencil.draw(mode='DRAW')
#     #
#     # def __del__(self):
#         # print("End Invoke")
#
#     # def execute(self, context):
#     #     print('I am execute')
#     #     return {'FINISHED'}
#     #
#     def modal(self, context, event):
#         if event.type == 'LEFTMOUSE':
#             if event.value == 'RELEASE':
#                 DataBase.current_object = context.active_object
#                 print(DataBase.current_object)
#                 return {'FINISHED'}
#         return {'PASS_THROUGH'}
#
#     def invoke(self, context, event):
#         bpy.ops.object.mode_set(mode='OBJECT')
#         context.window_manager.modal_handler_add(self)
#         return {'RUNNING_MODAL'}






################################################################################
# hairy stuff below for instance-based layout
################################################################################


        # works
        # if DataBase.current_object!=None:
        #     DataBase.current_object.location[0] = DataBase.current_object.location[0]+0.01
        #     DataBase.current_object.location[0] = DataBase.current_object.location[0]-0.01
        # else:
        #     context.active_object.location[0] = context.active_object.location[0]+0.01
        #     context.active_object.location[0] = context.active_object.location[0]-0.01


                # bpy.data.objects.remove(DataBase.current_control, do_unlink = True)
                # for i in range(len(bpy.data.curves)):
                #     bpy.data.curves.remove(bpy.data.curves[i], do_unlink=True)




                    # instance_nbr = IntProperty(name="Instancing Number", default=10)
                    # instance_direction = EnumProperty(name='Instancing Direction',
                    #                                   description='Instancing Direction',
                    #                                   items=[('Left', "Left", ""),
                    #                                          ('Right', 'Right', ''),
                    #                                          ('Forward', 'Forward', ''),
                    #                                          ('Backward', 'Backward', '')])



    # from bpy.utils import register_class
    # for cls in classes:
    #     register_class(cls)
    # bpy.utils.register_class(DirectionPieMenu)
    # wm = bpy.context.window_manager
    # km = wm.keyconfigs.addon.keymaps.new(name="Object Mode" )
    # kmi = km.keymap_items.new('wm.call_menu_pie', 'SPACE', 'PRESS').properties.name='OBJECT_MT_direction_pie_menu'


    # from bpy.utils import unregister_class
    # for cls in classes:
    #     unregister_class(cls)
    # bpy.utils.unregister_class(DirectionPieMenu)


    # b_use_projection = BoolProperty(name="Use Projection", description="", default=False)

    # class DataBase:
    #     current_object = None
    #     current_control = None
    #     current_object_array = []
    #     brushes = {}



                # row = column.row()
                # row.operator('instance.selectobject', text='Select', icon='GREASEPENCIL')
                # row.operator('object.delete', text='Delete', icon='GREASEPENCIL')
                # column.separator()
                # column.operator('gpencil.draw', text='Drawing', icon='GREASEPENCIL').mode = 'DRAW'
                # column.prop(my_settings, 'b_use_projection', text='Projection')


                            # column.separator()
                            # column.prop(my_settings, 'instance_nbr', text='PlaneInstancing Number')
                            # column.prop(my_settings, 'instance_direction', text='Direction')
                            # column.operator('layout.instancing', text='Updating', icon='GREASEPENCIL')




            # column.operator('layout.relayout', text='Relayout', icon='GREASEPENCIL')
            # column.separator()




                        # TODO, this is a rather bad design, replace it later
                        # row.operator('gpencil.editmode_toggle', text='Start Constructing Mode', icon='POSE_DATA')
                        # row.operator('gpencil.select_border', text='Border Select', icon='BORDER_RECT')
                        # row.operator('gpencil.select_all', text='Deselect All', icon='CANCEL')
                        #
                        # column = box.column()
                        # column.operator('gpencil.stroke2mesh', text='Object', icon='COPYDOWN')
                        #
                        # column = box.column()
                        # column.operator('gpencil.cstartrepetition', text='Start', icon='COPYDOWN')
                        # column.operator('gpencil.draw', text='Draw', icon='GREASEPENCIL').mode = 'DRAW'
                        # column.operator('gpencil.cgenerating', text='Generate', icon='COPYDOWN')


            # if my_settings.enum_brushes=='ANCHOR':
            #     context.scene.grease_pencil = AnimationData.
            # column.operator('animation.createanchor', text='Add Anchor', icon='GREASEPENCIL')


            # bpy.ops.transform.translate(value=(t0, 0, t1), proportional='PROJECTED', proportional_size=2.0)



        # basic settings
        # bpy.data.window_managers['WinMan'].key_points = True

        # R_local2world = np.array([[1,0,0], [0,0,-1], [0,1,0]])
        # R_world2local = LA.inv(R_local2world)


                # if obj.mode is not 'EDIT':
                #     bpy.ops.object.mode_set(mode='EDIT')


                            # me = obj.data
                            # bm = bmesh.from_edit_mesh(me)


                            # for vert in bm.verts:
                            #     co_local = np.array(vert.co.xyz)
                            #     co_world = np.dot(R_local2world, co_local) + location
                            #     dist = LA.norm([co_world[0]-new_phandler[0], co_world[2]-new_phandler[1]], 2)
                            #     weight = np.exp(-5*dist)
                            #     delta_world = np.array([t0, 0, t1])
                            #     delta_local = np.dot(R_world2local,delta_world) # - np.dot(R_world2local,location)
                            #     vert.co.x += weight*(delta_local[0])
                            #     vert.co.y += weight*(delta_local[1])

                            # bmesh.update_edit_mesh(me)
                            # context.scene.frame_current = i
                            # bpy.ops.anim.insert_keyframe_animall()

                        # context.scene.frame_end = nframe
                        # bpy.ops.screen.animation_play()

                        # if obj.mode is not 'OBJECT':
                        #     bpy.ops.object.mode_set(mode='OBJECT')




# class My_GPENCIL_UL_layer(UIList):
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#         # assert(isinstance(item, bpy.types.GPencilLayer)
#         gpl = item
#
#         if self.layout_type in {'DEFAULT', 'COMPACT'}:
#             if gpl.lock:
#                 layout.active = False
#
#             row = layout.row(align=True)
#             if gpl.is_parented:
#                 icon = 'BONE_DATA'
#             else:
#                 icon = 'BLANK1'
#
#             row.label(text="", icon=icon)
#             row.prop(gpl, "info", text="", emboss=False)
#
#             row = layout.row(align=True)
#             row.prop(gpl, "lock", text="", emboss=False)
#             row.prop(gpl, "hide", text="", emboss=False)
#             row.prop(gpl, "unlock_color", text="", emboss=False)
#         elif self.layout_type == 'GRID':
#             layout.alignment = 'CENTER'
#             layout.label(text="", icon_value=icon)
#





        # box = layout.box()
        # box.label('Record')
        #
        # gp=context.scene.grease_pencil
        # if gp!=None:
        #     if len(gp.layers) >= 2:
        #         layer_rows = 2
        #     else:
        #         layer_rows = 2
        # row = box.row()
        # col = row.column()
        # col.template_list("My_GPENCIL_UL_layer", "", gp, "layers", gp.layers, "active_index", rows=layer_rows)
        #
        # col = row.column()
        # sub = col.column(align=True)
        # sub.operator("gpencil.layer_add", icon='ZOOMIN', text="")
        # sub.operator("gpencil.layer_remove", icon='ZOOMOUT', text="")



# class FollowingPath(bpy.types.Operator):
#     bl_idname = 'animation.following_path'
#     bl_label = 'Rigid Body Transformation'
#     bl_options = {'UNDO'}
#
#     @classmethod
#     def poll(cls, context):
#         return (context.active_object!=None) and (context.scene.grease_pencil!=None)
#
#     def invoke(self, context, event):
#         strokes = context.scene.grease_pencil.layers.active.active_frame.strokes
#         if strokes==None:
#             return {'FINISHED'}
#
#         anim_all_option_check = bpy.data.window_managers['WinMan'].key_points
#         bpy.data.window_managers['WinMan'].key_points = True
#
#         stroke = strokes[-1]
#         sample_nb = len(stroke.points)
#         step = 1
#
#         context.scene.frame_start = 0
#         for i in range(sample_nb):
#             context.scene.frame_current = i
#             context.active_object.location[0] = stroke.points[i].co[0]
#             context.active_object.location[2] = stroke.points[i].co[2]
#             bpy.ops.anim.insert_keyframe_animall()
#
#         context.scene.frame_end = sample_nb
#         bpy.ops.screen.animation_play()
#
#         bpy.data.window_managers['WinMan'].key_points = anim_all_option_check
#         return {'FINISHED'}


            # row = box.row()
            # if not scene.use_preview_range:
            #     row.prop(scene, "frame_start", text="Start")
            #     row.prop(scene, "frame_end", text="End")
            # else:
            #     row.prop(scene, "frame_preview_start", text="Start")
            #     row.prop(scene, "frame_preview_end", text="End")
            # column = box.column()
            # if context.screen.is_animation_playing==True:
            #     column.operator("screen.animation_play", text="", icon='PAUSE')
            # else:
            #     column.operator('screen.animation_play', text='Play', icon='RIGHTARROW')
            # column.separator()
            # column.operator('animation.following_path', text='Following Path', icon='GREASEPENCIL')


# # Property
# class ConstructionProperty:
#     instance_nb = 6


# # Property
# class AnimationProperty():
#     current_frame = 1
#     frame_block_nb = 100
#     sampling_step = 2

                                                # update=AnimationHandlerUpdateBrushes)









        # self.testA_list = []
        # for i in range(ncp):
        #     A = {}
        #     for vert in self.mesh.vertices:
        #         first = np.array(vert.co[0:2])-self.p_star[vert.index]
        #         third = self.p[i]-self.p_star[vert.index]
        #         second = np.zeros((2,2))
        #         for k in range(ncp):
        #             a=np.reshape(self.p[k]-self.p_star[vert.index], (1,2))
        #             b=np.reshape(self.p[k]-self.p_star[vert.index], (2,1))
        #             second += self.weight_list[k][vert.index]*np.dot(b,a)
        #         tmp = np.dot(first, LA.inv(second))
        #         A[vert.index] = np.dot(tmp, third)
        #     self.testA_list.append(A)




                        # count = np.zeros(2)
                        # for i in range(ncp):
                        #     q_hat = q[i] - q_star[vert.index]
                        #     count += self.testA_list[i][vert.index]*q_hat
                        # vco_new = count + q_star[vert.index]
                        # print(vco_new)


        # if bpy.context.active_object.mode=='OBJECT':
        #     context.scene.edit_mode=='Object'
        # elif bpy.context.active_object.mode=='EIDT':
        #     context.scene.edit_mode=='Edit'
        # elif bpy.context.active_object.mode=='POSE':
        #     context.scene.edit_mode=='Pose'
