import bpy

from .bLT_utils import *

from bpy.props import StringProperty,FloatProperty,IntProperty,BoolProperty,EnumProperty,CollectionProperty,FloatVectorProperty
from bpy.types import Panel,Scene,AddonPreferences,UIList,PropertyGroup,WindowManager,Object
from bl_ui.properties_paint_common import UnifiedPaintPanel, brush_texture_settings, brush_texpaint_common

class OP_AP_InstallOpenCV(bpy.types.Operator):
    bl_idname = "a.install_opencv"
    bl_label = "Install OpenCV"
    bl_description = 'Installs OpenCV'

    def execute(self, context):
        install_opencv()
        return {'FINISHED'}

class LocationItems(PropertyGroup):
    isVisibleLocItem = BoolProperty(name="",default=False)
    
class TexturePaintBrush(PropertyGroup):
    name = StringProperty(name="Brush Name")
            
class UL_Locations_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False)
        
        icon = 'RESTRICT_VIEW_OFF' if item.isVisibleLocItem else 'RESTRICT_VIEW_ON'
        op = layout.operator("scene.switch_locations", text="", emboss=False, icon=icon)
        op.group_idx = index

class OP_UI_RemoveLocation(bpy.types.Operator):
    bl_idname = "scene.remove_location"
    bl_label = "Remove Location"
    bl_options = {'REGISTER'}
    bl_description = 'Removes current location(eye icon) without commiting any changes!!!'

    @classmethod
    def poll(cls, context):
        return context.scene.SculptModeSwitch == False and context.scene.PaintModeSwitch == False
    
    def execute(self, context):
        scene = bpy.data.scenes['Default_Location']
        locationgroups = scene.locationgroups
        
        locationName = context.scene.name
        
        for index, location in enumerate(locationgroups):
            if location.name == locationName:
                group_idx = index
        
        scene.locationgroups.remove(group_idx)
        bpy.ops.scene.delete()
        
        
        bpy.data.objects.remove(bpy.data.objects['Terrain_{}'.format(locationName)])
        bpy.data.meshes.remove(bpy.data.meshes['TerrainMesh_{}'.format(locationName)])
        if bpy.data.materials.get('TerrainMaterial_{}'.format(locationName)) is not None:
            bpy.data.materials.remove(bpy.data.materials['TerrainMaterial_{}'.format(locationName)])
        if bpy.data.textures.get('TerrainTexture_{}'.format(locationName)) is not None:
            bpy.data.textures.remove(bpy.data.textures['TerrainTexture_{}'.format(locationName)])
        if bpy.data.textures.get('TerrainMask_{}'.format(locationName)) is not None:
            bpy.data.textures.remove(bpy.data.textures['TerrainMask_{}'.format(locationName)])
        if bpy.data.images.get('TerrainImage_{}.png'.format(locationName)) is not None:
            imageFilePath = bpy.data.images['TerrainImage_{}.png'.format(locationName)].filepath
            bpy.data.images.remove(bpy.data.images['TerrainImage_{}.png'.format(locationName)])    
            if os.path.isfile(imageFilePath):
                os.remove(imageFilePath)
            
        if bpy.data.images.get('TerrainMask_{}.png'.format(locationName)) is not None:
            imageFilePath = bpy.data.images['TerrainMask_{}.png'.format(locationName)].filepath
            bpy.data.images.remove(bpy.data.images['TerrainMask_{}.png'.format(locationName)])
            if os.path.isfile(imageFilePath):
                os.remove(imageFilePath)
 
        bpy.data.grease_pencil["OccupiedLocations"].layers.remove(bpy.data.grease_pencil["OccupiedLocations"].layers[locationName])
        
        if len(locationgroups) != 0:
            locationgroups[0].isVisibleLocItem = True
            context.window.screen.scene = bpy.data.scenes[locationgroups[0].name]
            
            terrainObject = bpy.data.objects['Terrain_{}'.format(locationgroups[0].name)]
            terrainObject.hide_select = False
            terrainObject.select = True
            context.scene.objects.active = terrainObject
            bpy.ops.view3d.view_selected()
            terrainObject.select = False
            terrainObject.hide_select = True
        else:
            context.window.screen.scene = bpy.data.scenes['Default_Location']
            context.scene.ViewportSettingsSwitch = False
            context.scene.DataSourceSwitch = True
            
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        bLTLogger('Scs','Location \'{}\' removed successfully.'.format(locationName))
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)
        
class OP_UI_SwitchLocations(bpy.types.Operator):
    bl_idname = "scene.switch_locations"
    bl_label = "Switch Locations"
    bl_description = 'Click on a closed eye to switch to selected location'
    
    group_idx = IntProperty()
    
    def execute(self, context):
        scene = bpy.data.scenes['Default_Location']
        locationgroups = scene.locationgroups
        group_idx = self.group_idx
        
        for location in locationgroups:
            location.isVisibleLocItem = False
        locationgroups[group_idx].isVisibleLocItem = True
        
        bpy.context.window.screen.scene = bpy.data.scenes[locationgroups[group_idx].name]
        context.scene.layers[0] = True
        
        terrainObject = bpy.data.objects['Terrain_{}'.format(locationgroups[group_idx].name)]
        terrainObject.hide_select = False
        terrainObject.select = True
        bpy.context.scene.objects.active = terrainObject
        bpy.ops.view3d.view_selected()
        terrainObject.select = False
        terrainObject.hide_select = True
        
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}
        
class OP_CreateProject(bpy.types.Operator):
    bl_idname = "scene.create_project"
    bl_label = "Create Project"
    
    def execute(self, context):
        createProject()
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'window': window, 'screen': screen, 'area': area, 'region': region}
        bpy.ops.view3d.draw_splash(override,'INVOKE_DEFAULT')
        
        context.scene.ProjectSettingsSwitch = False
        context.scene.DataSourceSwitch = True
        context.scene.LocationsManagerSwitch = True
        
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        bLTLogger('Scs', 'Project {}{}.blend succesfully created.'.format(ProjFolderPath,ProjectName))
        bLTLogger('Inf', 'Find information about Data Source tab at https://github.com/paxetgloria/bLandscapeTools/wiki/Data-Source')
        bLTLogger('Inf', 'Find information about Locations manager tab at https://github.com/paxetgloria/bLandscapeTools/wiki/Locations-manager')
        
        return {'FINISHED'}
        
class OP_ImportLocation(bpy.types.Operator):
    bl_idname = "scene.import_location"
    bl_label = "Import Location"
    bl_description = 'Imports a new location'
     
    @classmethod
    def poll(cls, context):
        return (context.scene.SculptModeSwitch == False 
        and context.scene.PaintModeSwitch == False 
        and context.scene.HeightmapFormatValid 
        and (context.scene.ImportTerrainTexturePath == '' or context.scene.TerrainTextureFormatValid)
        and (context.scene.ImportTerrainSurfaceMaskPath == '' or context.scene.SurfaceMaskFormatValid))

    def execute(self, context):
        setup2dMapPreview()
        return {'FINISHED'}

class OP_CreateLocation(bpy.types.Operator):
    bl_idname = "scene.create_location"
    bl_label = "Create Location"
    
    locationName = StringProperty(name="Location name:")
    
    def execute(self, context):
        for location in bpy.data.scenes:
            if location.name == self.locationName:
                self.report({'WARNING'}, "Location with this name already exists! Try a different name.")
                bpy.ops.scene.import_location()
                return {'CANCELLED'}
        
        if self.locationName == '':
            self.report({'WARNING'}, "Location must have a name!")
            bpy.ops.scene.import_location()
            return {'CANCELLED'}
                
        global topLeftRow,topLeftColumn,bottomRightRow,bottomRightColumn,copyTopEdge,copyRightEdge,gridResX,gridResY
        createNewLocation(self.locationName,gridResX,gridResY,topLeftRow,topLeftColumn,bottomRightRow,bottomRightColumn,copyTopEdge,copyRightEdge)
        
        scene = bpy.data.scenes['Default_Location']
        locationgroups = scene.locationgroups
        location_idx = len(locationgroups)
        
        location_group = locationgroups.add()
        location_group.name = self.locationName
        for location in locationgroups:
            location.isVisibleLocItem = False
        location_group.isVisibleLocItem = True
        scene.locationgroups_index = location_idx

        context.scene.ViewportSettingsSwitch = True
        context.scene.DataSourceSwitch = False
        context.scene.TerrainEditingSwitch = True
        if context.scene.TerrainTextureFormatValid and context.scene.SurfaceMaskFormatValid:
            context.scene.SurfacePaintingSwitch = True
            
        createOccupiedLocation(self.locationName,topLeftRow,topLeftColumn,bottomRightRow,bottomRightColumn,copyTopEdge,copyRightEdge)
        
        bpy.ops.wm.save_mainfile()
        bLTLogger('Scs','Location \'{}\' imported successfully.'.format(self.locationName))
        bLTLogger('Inf', 'Hint: press F key to initiate Fly-mode, press LMB to confirm current location, scroll MMB to speed up/slow down camera, hold SHIFT for instant speed shift.')
        return {'FINISHED'}
        
    def invoke(self, context, event):
        self.locationName = ''
        return context.window_manager.invoke_props_dialog(self)
        
    def cancel(self, context):
        context.area.type = 'VIEW_3D'
        return {'CANCELLED'}
        
class OP_CommitLocation(bpy.types.Operator):
    bl_idname = "scene.commit_location"
    bl_label = "Commit Location"
    bl_description = 'Commits terrain/surface mask changes from the current location'
    
    overwriteSource = BoolProperty(description="Checked: Data will be written to paths defined in Data Source panel\nUnchecked: Data will be written to the Output folder within the Project folder", name="Overwrite source data",default=False)
    commintElevation = BoolProperty(description="Commit elevation", name="Elevation",default=True)
    commintSurfaceMask = BoolProperty(description="Commit surface mask", name="Surface mask",default=True)
    
    @classmethod
    def poll(cls, context):
        return context.scene.SculptModeSwitch == False and context.scene.PaintModeSwitch == False
    
    def execute(self, context):
        if self.commintElevation:
            exportTerrain(self.overwriteSource)
        if self.commintSurfaceMask:
            exportSurfaceMask(self.overwriteSource)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
     
class OP_PickLocation(bpy.types.Operator):
    bl_idname = "view2d.pick_location"
    bl_label = "Pick Location"

    def modal(self, context, event):
        global topLeftRow,topLeftColumn,bottomRightRow,bottomRightColumn,copyTopEdge,copyRightEdge,gridResX,gridResY
        context.area.tag_redraw()
        
        worldInfo = bpy.data.scenes['Default_Location']
        terrainResolution = worldInfo["TerrainResolution"]
        cellSize = worldInfo["CellSize"]
        
        selectionRectangleCursorUV = context.region.view2d.region_to_view(self.mouseX,self.mouseY)
        
        topSelectionEdge,leftSelectionEdge,bottomSelectionEdge,rightSelectionEdge = selectionCorrection(list(selectionRectangleCursorUV),list(self.selectionRectangleOriginUV))
        
        topLeftRow, topLeftColumn, bottomRightRow, bottomRightColumn, copyTopEdge, copyRightEdge, gridResX, gridResY = terrainImportInfo(cellSize,terrainResolution,topSelectionEdge,leftSelectionEdge,bottomSelectionEdge,rightSelectionEdge)
        
        self.vertexCount = 'TerrainVerts: {:,}({:,}x{:,})'.format(gridResX * gridResY,gridResX,gridResY)
        trianglesCount = 0  if ((gridResX - 1) * (gridResY - 1)) * 2 <= 0 else ((gridResX - 1) * (gridResY - 1)) * 2
        self.trianglesCount = 'TerrainTris: {:,}'.format(trianglesCount)
        mapSizeX = 0 if (gridResX - 1) * cellSize <= 0 else (gridResX - 1) * cellSize
        self.mapSize = 'MapSize: {:.2f}x{:.2f} m'.format(mapSizeX, (gridResY - 1) * cellSize)
        
        if event.type == 'MOUSEMOVE':
            self.mouseX, self.mouseY = event.mouse_region_x,event.mouse_region_y
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.switch = True
            self.clickCount += 1
            if self.clickCount == 2:
                if ((gridResX - 1) * (gridResY - 1)) * 2 <= 0:
                    self.report({'WARNING'}, "No vertices to create a triangle")
                    self.clickCount = 0
                    self.switch = False
                else:
                    bpy.ops.scene.create_location('INVOKE_DEFAULT')
                    bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, 'WINDOW')
                    return {'FINISHED'}
                
            self.selectionRectangleOriginUV = context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
            
        elif event.type == 'BACK_SPACE':
            if bpy.data.images.get('previewSatTex.png') is not None and bpy.data.images.get('previewTerTex.tif') is not None:
                for space in bpy.context.area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        curPreview = space.image.name

                if curPreview == 'previewSatTex.png':
                    for space in bpy.context.area.spaces:
                        if space.type == 'IMAGE_EDITOR':
                            space.image = bpy.data.images['previewTerTex.tif']
                else:
                    for space in bpy.context.area.spaces:
                        if space.type == 'IMAGE_EDITOR':
                            space.image = bpy.data.images['previewSatTex.png']
                            
            return {'PASS_THROUGH'}
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.type = 'VIEW_3D'
            bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
            
        elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE','MIDDLEMOUSE','LEFT_SHIFT'}:
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}
  
    def invoke(self, context, event):
        self.mouseX,self.mouseY = 0,0
        self.clickCount = 0
        self.selectionRectangleOriginUV = [0,0]
        self.switch = False
        
        if context.area.type == 'IMAGE_EDITOR':
            args = (self, context)
            self._handle = bpy.types.SpaceImageEditor.draw_handler_add(drawLocationSelectionRectangle, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Image Editor not found, cannot run operator")
            return {'CANCELLED'}
 
class OP_DrawSplashScreen(bpy.types.Operator):
    bl_idname = "view3d.draw_splash"
    bl_label = "Draw splash screen"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'LEFTMOUSE', 'ESC'}:
            self.img.gl_free()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(drawSplashScreen, args, 'WINDOW', 'POST_PIXEL')
            dataFolder = getPaths()[2]
            if bpy.data.images.get('splash.png') is None:
                bpy.data.images.load('{}\\splash.png'.format(dataFolder))
                bpy.data.images['splash.png'].use_fake_user = True
            else:
                bpy.data.images['splash.png'].reload()
            self.img = bpy.data.images['splash.png']
            self.img.gl_load()
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class OP_AssignMeshTerrainModifier(bpy.types.Operator):
    bl_idname = "object.assign_mesh_terrain_modifier"
    bl_label = "Assign Mesh Terrain Modifier"
    bl_description = 'Assigns a mesh terrain modifier to selected object(only MESH type)'
    
    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
        and context.active_object.dupli_group is not None
        and context.active_object.name.split('_')[0] != 'Flatter'
        and len(context.active_object.children) == 0
        and len(context.selected_objects) == 1
        and context.active_object.mode not in {'SCULPT','EDIT','TEXTURE_PAINT'}
        and context.active_object.type == 'EMPTY')

    def execute(self, context):
        assignMeshTerrainModifier(context)
        
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}
        
class OP_AddMeshTerrainModifier(bpy.types.Operator):
    bl_idname = "object.add_mesh_terrain_modifier"
    bl_label = "Add Mesh Terrain Modifier"
    bl_description = 'Adds a mesh terrain modifier at 3D cursor position'
    
    @classmethod
    def poll(cls, context):
        validForPlacement = True
        if context.active_object is not None:
            if context.active_object.mode in {'SCULPT','EDIT','TEXTURE_PAINT'}:
                validForPlacement = False  
        return validForPlacement

    def execute(self, context):
        addMeshTerrainModifier(context)
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}
        
class OP_ApplyMeshTerrainModifier(bpy.types.Operator):
    bl_idname = "object.apply_mesh_terrain_modifier"
    bl_label = "Apply Mesh Terrain Modifier(s)"
    bl_description = 'Applies terrain changes from all selected objects and removes terran modifier from the scene'
    
    @classmethod
    def poll(cls, context):
        isEmpty = True
        flatterNotInSelection = True

        for ob in context.selected_objects:
            if len(ob.children) == 0:
                flatterNotInSelection = False
            if ob.type != 'EMPTY':
                isEmpty = False
        return (len(context.selected_objects) != 0 and isEmpty and flatterNotInSelection)

    def execute(self, context):
        applyMeshTerrainModifier(context)
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}
        
class OP_AddSplineTerrainModifier(bpy.types.Operator):
    bl_idname = "object.add_spline_terrain_modifier"
    bl_label = "Add Spline Terrain Modifier"
    bl_description = 'Adds a spline terrain modifier at 3D cursor location'
    
    @classmethod
    def poll(cls, context):
        validForPlacement = False
        if context.active_object is None:
            validForPlacement = True
        else:
            if context.active_object.mode not in {'SCULPT','EDIT','TEXTURE_PAINT'}:
                validForPlacement = True
        return validForPlacement
        
    def execute(self, context):
        addSplineTerrainModifier(context)
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}
        
class OP_ApplySplineTerrainModifier(bpy.types.Operator):
    bl_idname = "object.apply_spline_terrain_modifier"
    bl_label = "Apply Spline Terrain Modifier(s)"
    bl_description = 'Applies terrain changes and removes terran modifier from the scene'
    
    @classmethod
    def poll(cls, context):
        isSpline = True
        
        for ob in context.selected_objects:
            if ob.type != 'CURVE':
                isSpline = False
        return (len(context.selected_objects) != 0 and isSpline and context.active_object.mode not in 'EDIT')

    def execute(self, context):
        applySplineTerrainModifier(context)
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}
            
class OP_AppearanceTexturedWire(bpy.types.Operator):
    bl_idname = "object.appearance_textured_wire"
    bl_label = "Textured + Wire overlay"

    def execute(self, context):
        Areas = context.screen.areas
        for Area in Areas:
            if Area.type == 'VIEW_3D':
                Area.spaces.active.viewport_shade = 'TEXTURED'
        
        terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
        terrainObject.show_wire = True
        terrainObject.show_all_edges = True
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}

class OP_AppearanceTexturedNoWire(bpy.types.Operator):
    bl_idname = "object.appearance_textured_nowire"
    bl_label = "Textured"

    def execute(self, context):
        Areas = context.screen.areas
        for Area in Areas:
            if Area.type == 'VIEW_3D':
                Area.spaces.active.viewport_shade = 'TEXTURED'
        terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
        terrainObject.show_wire = False
        terrainObject.show_all_edges = False
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}
        
class OP_AppearanceSmooth(bpy.types.Operator):
    bl_idname = "object.appearance_smooth"
    bl_label = "Smooth"

    
    @classmethod
    def poll(cls, context):
        return not context.scene.PaintModeSwitch
    
    def execute(self, context):
        if context.active_object is not None and context.active_object.mode == 'SCULPT':
            bpy.ops.object.mode_set(mode='OBJECT')
            context.active_object.hide_select = False
            context.active_object.select = True
            bpy.ops.object.shade_smooth()
            context.active_object.select = False
            context.active_object.hide_select = True
            bpy.ops.object.mode_set(mode='SCULPT')
        else:
            activeObject = context.active_object if context.active_object is not None else None
            bpy.ops.object.select_all(action='DESELECT')
            terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
            terrainObject.hide_select = False
            terrainObject.select = True
            bpy.ops.object.shade_smooth()
            terrainObject.select = False
            terrainObject.hide_select = True
            if activeObject is not None:
                activeObject.select = True
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}
        
class OP_AppearanceFlat(bpy.types.Operator):
    bl_idname = "object.appearance_flat"
    bl_label = "Flat"
    
    @classmethod
    def poll(cls, context):
        return not context.scene.PaintModeSwitch
    
    def execute(self, context):
        if context.active_object is not None and context.active_object.mode == 'SCULPT':
            bpy.ops.object.mode_set(mode='OBJECT')
            context.active_object.hide_select = False
            context.active_object.select = True
            bpy.ops.object.shade_flat()
            context.active_object.select = False
            context.active_object.hide_select = True
            bpy.ops.object.mode_set(mode='SCULPT')
        else:
            activeObject = context.active_object if context.active_object is not None else None
            bpy.ops.object.select_all(action='DESELECT')
            terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
            terrainObject.hide_select = False
            terrainObject.select = True
            bpy.ops.object.shade_flat()
            terrainObject.select = False
            terrainObject.hide_select = True
            if activeObject is not None:
                activeObject.select = True
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}

class OP_AppearanceMatCapNoWire(bpy.types.Operator):
    bl_idname = "scene.appearance_matcap_nowire"
    bl_label = "MatCap"

    @classmethod
    def poll(cls, context):
        return not context.scene.PaintModeSwitch
    
    def execute(self, context):
        Areas = context.screen.areas
        for Area in Areas:
            if Area.type == 'VIEW_3D':
                Area.spaces.active.viewport_shade = 'SOLID'
                Area.spaces.active.use_matcap = True
        terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
        terrainObject.show_wire = False
        terrainObject.show_all_edges = False
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}

class OP_AppearanceMatCapWire(bpy.types.Operator):
    bl_idname = "scene.appearance_matcap_wire"
    bl_label = "MatCap + Wire overlay"

    @classmethod
    def poll(cls, context):
        return not context.scene.PaintModeSwitch
    
    def execute(self, context):
        Areas = context.screen.areas
        for Area in Areas:
            if Area.type == 'VIEW_3D':
                Area.spaces.active.viewport_shade = 'SOLID'
                Area.spaces.active.use_matcap = True
        terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
        terrainObject.show_wire = True
        terrainObject.show_all_edges = True
        ProjFolderPath = context.scene.ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        return {'FINISHED'}

class OP_CreateFlatTerrain(bpy.types.Operator):
    bl_idname = "scene.create_flatterrain"
    bl_label = "Generate flat terrain"
    bl_description = 'Generates a flat terrain asc file and writes it to\nthe Output folder defined in addon\'s preferences'
    
    cellSize = FloatProperty(name="Cell size:",default=1.0,min=.0)
    gridResolution = IntProperty(name="Grid resolution:",default=512,min=0)
    defaultElevation = FloatProperty(name="Default elevation:",default=10.0)
    
    def execute(self, context):
        createFlatTerrain(self.cellSize,self.gridResolution,self.defaultElevation)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
class OP_CreateSurfaceMask(bpy.types.Operator):
    bl_idname = "scene.create_surfacemask"
    bl_label = "Generate empty surface mask"
    bl_description = 'Generates a raster filled with a default color in png format and writes it to\nthe Output folder defined in addon\'s preferences'
    
    imageResolution = IntProperty(name="Image resolution(px):",default=5000,min=0)
    defaultColor = FloatVectorProperty(name="Default color:",min=0.0,max=1.0,subtype='COLOR')
    
    def execute(self, context):
        createSurfaceMask(self.imageResolution,self.defaultColor)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
class OP_CheckSurfaceMaskFull(bpy.types.Operator):
    bl_idname = "scene.check_surfacemaskfull"
    bl_label = "Check surface mask"
    bl_description = 'Generates a raster with information about the count of surfaces per surface tile'
    
    cellSize = FloatProperty(name="Cell size(m):",default=7.5,min=0.0)
    gridResolution = IntProperty(name="Terrain grid resolution(px):",default=2048,min=0)
    tileSizeList = [
    ("512", "512", "", 1),
    ("1024", "1024", "", 2),
    ("2048", "2048", "", 3),
    ("4096", "4096", "", 4)]
    tileSize = EnumProperty(items=tileSizeList,name="Tile size(px):",default='512')
    _timer = None

    @classmethod
    def poll(cls, context):
        return context.scene.CheckSurfaceMaskFormatValid and context.scene.CheckSurfacesDefinitionFormatValid
    
    def execute(self, context):
        checkSurfaceMask(context,self.cellSize,self.gridResolution,int(self.tileSize))
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
class VIEW3D_ProjectSettings(Panel):
    bl_category = "bLandscape Tools"
    bl_label = "Project Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    Scene.isProject = BoolProperty(name="",
        description="",
        default=False)
    
    Scene.ProjFolderPath = StringProperty(name="",
        attr="projFolderPath",
        description="Path to project folder",
        maxlen= 1024,
        subtype='DIR_PATH',
        default='')
        
    Scene.bLTElevationPath = StringProperty(name="",
        attr="terrainPath",
        description="Path to bLT internal elevation file",
        maxlen= 1024,
        subtype='FILE_PATH')
        
    enginesList = [
    ("RVEngine", "RVEngine", "", 1),
    ("Unreal Engine 4", "Unreal Engine 4", "", 2),
    ("CryEngine", "CryEngine", "", 3),
    ("Unity", "Unity", "", 4),
    ("Enfusion", "Enfusion", "", 5)
    ]

    Scene.GameEngine = EnumProperty(items=enginesList,name="Engine",default='RVEngine')
    
    Scene.ProjectSettingsSwitch = BoolProperty(default=True)
    
    @classmethod
    def poll(cls, context):
        return context.scene.ProjectSettingsSwitch

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        box = layout.box()
        row = box.column()
        row.label(text="Project Folder")
        row.prop(scene,'ProjFolderPath')
        row.separator()
        row.prop(scene, 'GameEngine')

        row3 = box.column()
        row3.separator()
        row3.operator("scene.create_project",text='Create Project')
        
        if scene.ProjFolderPath is '':
            row3.enabled = False
        else:
            row3.enabled = True
                
class VIEW3D_DataSource(Panel):
    bl_category = "bLandscape Tools"
    bl_label = "Data Source"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    Scene.DataSourceSwitch = BoolProperty(default=False)
    Scene.ImportTerrainTexturePath = StringProperty(name="Terrain Texture",
        description="Any imagery format supported by GDAL",
        maxlen= 1024,
        subtype='FILE_PATH',
        update=update_importterraintexturepath)

    Scene.ImportTerrainHeightmapPath = StringProperty(name="Terrain Heightmap",
        description="Supports ARC/INFO ASCII GRID only",
        maxlen= 1024,
        subtype='FILE_PATH',
        update=update_importterrainheightmappath)
        
    Scene.ImportTerrainSurfaceMaskPath = StringProperty(name="Terrain Surface Mask",
        description="",
        maxlen= 1024,
        subtype='FILE_PATH',
        update=update_importterrainsurfacemaskpath)
        
    Scene.ImportSurfacesDefinitionPath = StringProperty(name="Layers.cfg",
        description="",
        maxlen= 1024,
        subtype='FILE_PATH',
        update=update_importsurfacesdefinitionpath)
        
    Scene.HeightmapFormatValid = BoolProperty(default=False)
    Scene.TerrainTextureFormatValid = BoolProperty(default=False)
    Scene.SurfaceMaskFormatValid = BoolProperty(default=False)
    Scene.DevDriveValid = BoolProperty(default=False)
    
    
    lettersList = [("", "", "", 0),("A:\\", "A:\\", "", 1),("B:\\", "B:\\", "", 2),("C:\\", "C:\\", "", 3),("D:\\", "D:\\", "", 4),
    ("E:\\", "E:\\", "", 5),("F:\\", "F:\\", "", 6),("G:\\", "G:\\", "", 7),("I:\\", "I:\\", "", 8),("J:\\", "J:\\", "", 9),("K:\\", "K:\\", "", 10),("L:\\", "L:\\", "", 11),("M:\\", "M:\\", "", 12),("N:\\", "N:\\", "", 13),("O:\\", "O:\\", "", 14),
    ("P:\\", "P:\\", "", 15),("Q:\\", "Q:\\", "", 16),("R:\\", "R:\\", "", 17),("S:\\", "S:\\", "", 18),("T:\\", "T:\\", "", 19),("U:\\", "U:\\", "", 20),("V:\\", "V:\\", "", 21),("W:\\", "W:\\", "", 22),("X:\\", "X:\\", "", 23),("Y:\\", "Y:\\", "", 24),
    ("Z:\\", "Z:\\", "", 25)
    ]

    Scene.DevDriveLetter = bpy.props.EnumProperty(items=lettersList,name="Dev. Drive",description="Sets the letter of the developer's drive",default="",update=update_devdriveletter)

    
    @classmethod
    def poll(cls, context):
        return context.scene.DataSourceSwitch

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        box = layout.box()
        row1 = box.column()
        row1.prop(scene, 'ImportTerrainTexturePath')
        row1.prop(scene, 'ImportTerrainHeightmapPath')
        row2 = box.column()
        row2.prop(scene, 'ImportTerrainSurfaceMaskPath')
        row4 = box.column()
        row4.prop(scene, 'DevDriveLetter')
        row3 = box.column()
        row3.prop(scene, 'ImportSurfacesDefinitionPath')
        
        
        if not scene.TerrainTextureFormatValid:
            row2.enabled = False
        if not scene.SurfaceMaskFormatValid:
            row4.enabled = False
        if not scene.SurfaceMaskFormatValid or not scene.DevDriveValid:
            row3.enabled = False
        
class VIEW3D_LocationsManager(Panel):
    bl_category = "bLandscape Tools"
    bl_label = "Locations manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    Scene.isLocation = BoolProperty(name="",
    description="",
    default=False)
    
    Scene.LocationsManagerSwitch = BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return context.scene.LocationsManagerSwitch

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        col = layout.column()
        
        if context.scene['isLocation']:
            if len(bpy.data.objects['Terrain_' + context.scene.name].modifiers) != 0:
                col.label(text='Terrain has modifier(s) assigned, BE CAREFUL!',icon='ERROR')
            if scene.SculptModeSwitch:
                col.label(text='Terrain Sculpting mode is ON!',icon='ERROR')
                col.label(text='Turn it OFF before any action with the current location!',icon='OUTLINER_OB_LAMP')
            if scene.PaintModeSwitch:
                col.label(text='Surface Painting mode is ON!',icon='ERROR')
                col.label(text='Turn it OFF before any action with the current location!',icon='OUTLINER_OB_LAMP')
        row = layout.row()
        if scene.isProject:
            row.template_list("UL_Locations_list", "", bpy.data.scenes['Default_Location'], "locationgroups", bpy.data.scenes['Default_Location'], "locationgroups_index")
        col = row.column()
        row1 = col.row()
        row1.operator("scene.import_location",icon='ZOOMIN',text="")
        if bpy.context.object is not None:
            if bpy.context.object.mode == 'EDIT':
                row1.enabled = False
                    
        row2 = col.row()        
        row2.operator("scene.commit_location",icon='APPEND_BLEND',text="")
        if not scene.isLocation:
            row2.enabled = False
        elif bpy.context.object is not None:
            if bpy.context.object.mode == 'EDIT':
                row2.enabled = False    
        
        row3 = col.row()        
        row3.operator("scene.remove_location",icon='ZOOMOUT',text="")
        if not scene.isLocation:
            row3.enabled = False
        elif len(bpy.data.scenes["Default_Location"].locationgroups) == 0:
            row3.enabled = False  
        elif bpy.context.object is not None:
            if bpy.context.object.mode == 'EDIT':
                row3.enabled = False    
       
   
                
            

class View3DPaintPanel(UnifiedPaintPanel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
                
class VIEW3D_TerrainEditing(Panel,View3DPaintPanel):
    bl_category = "bLandscape Tools"
    bl_label = "Terrain Editing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    
    Scene.TerrainEditingSwitch = BoolProperty(default=False)
    
    Scene.SculptModeSwitch = BoolProperty(default=False,update=update_switchsculptmode)
    
    Scene.SculptTextureSettingsSwitch = BoolProperty(default=False)
    Scene.SculptStrokeSwitch = BoolProperty(default=False)
    Scene.BrushShapeCurveSwitch = BoolProperty(default=False)
    Object.FlatterWidth = FloatProperty(default=1,update=update_flatterwidth)
    
    @classmethod
    def poll(cls, context):
        return (context.scene.TerrainEditingSwitch or cls.paint_settings(context) or context.sculpt_object)

    def draw(self, context):
        scene = context.scene
        object = context.active_object
        layout = self.layout
       
        col = layout.column()
        
        
        if scene.SculptModeSwitch:
            text = 'Disable Terrain Sculpting'     
        else:
            text = 'Enable Terrain Sculpting'
        col.prop(scene, "SculptModeSwitch", text=text, icon="SCULPTMODE_HLT")
        if scene.PaintModeSwitch or (context.active_object is not None and context.active_object.mode == 'EDIT'):
            col.enabled = False
        
        if len(bpy.data.objects['Terrain_' + context.scene.name].modifiers) != 0:
            col.label(text='Terrain has modifier(s) assigned, BE CAREFUL!',icon='ERROR')

        if scene.SculptModeSwitch:
            toolsettings = context.tool_settings
            settings = self.paint_settings(context)
            brush = settings.brush
            
            box = layout.box()            
            col = box.column()
            col.label(text='Brush settings')
            
            if not context.particle_edit_object:
                col.separator()
                col.separator()
                col.template_ID_preview(settings, "brush", new="brush.add", rows=3, cols=8)
            
            capabilities = brush.sculpt_capabilities
            col.separator()
            row = col.row(align=True)
            ups = toolsettings.unified_paint_settings
            if ((ups.use_unified_size and ups.use_locked_size) or
                    ((not ups.use_unified_size) and brush.use_locked_size)):
                self.prop_unified_size(row, context, brush, "use_locked_size", icon='LOCKED')
                self.prop_unified_size(row, context, brush, "unprojected_radius", slider=True, text="Radius")
            else:
                self.prop_unified_size(row, context, brush, "use_locked_size", icon='UNLOCKED')
                self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")
                
            self.prop_unified_size(row, context, brush, "use_pressure_size")

            col.separator()
            row = col.row(align=True)

            if capabilities.has_space_attenuation:
                row.prop(brush, "use_space_attenuation", toggle=True, icon_only=True)

            self.prop_unified_strength(row, context, brush, "strength", text="Strength")

            if capabilities.has_strength_pressure:
                self.prop_unified_strength(row, context, brush, "use_pressure_strength")

            if capabilities.has_auto_smooth:
                col.separator()

                row = col.row(align=True)
                row.prop(brush, "auto_smooth_factor", slider=True)
                row.prop(brush, "use_inverse_smooth_pressure", toggle=True, text="")

            if capabilities.has_sculpt_plane:
                col.separator()
                row = col.row(align=True)

                row.prop(brush, "use_original_normal", toggle=True, icon_only=True)

                row.prop(brush, "sculpt_plane", text="")

            if brush.sculpt_tool == 'MASK':
                col.prop(brush, "mask_tool", text="")
                
            if capabilities.has_plane_offset:
                row = col.row(align=True)
                row.prop(brush, "plane_offset", slider=True)
                row.prop(brush, "use_offset_pressure", text="")

                col.separator()

                row = col.row()
                row.prop(brush, "use_plane_trim", text="Trim")
                row = col.row()
                row.active = brush.use_plane_trim
                row.prop(brush, "plane_trim", slider=True, text="Distance")

            if capabilities.has_height:
                row = col.row()
                row.prop(brush, "height", slider=True, text="Height")
                
            col.separator()
            row = col.row()
            row.prop(brush, "use_frontface", text="Front Faces Only")

            col.separator()
            col.row().prop(brush, "direction", expand=True)

            if capabilities.has_accumulate:
                col.separator()

                col.prop(brush, "use_accumulate")

            if capabilities.has_persistence:
                col.separator()

                ob = context.sculpt_object
                do_persistent = True

                for md in ob.modifiers:
                    if md.type == 'MULTIRES':
                        do_persistent = False
                        break

                if do_persistent:
                    col.prop(brush, "use_persistent")
                    col.operator("sculpt.set_persistent_base")
            
            col = layout.column()
            col.separator()
            
            box = layout.box()            
            col = box.column()
            col.prop(scene, "SculptTextureSettingsSwitch", text='Sculpt Texture Settings', icon="TEXTURE")
            
            if scene.SculptTextureSettingsSwitch:
                col.template_ID_preview(brush, "texture", new="texture.new", rows=3, cols=8)
                brush_texture_settings(col, brush, context.sculpt_object)
                
            
            col = layout.column()
            col.separator()

            box = layout.box()            
            col = box.column()
            col.prop(scene, "SculptStrokeSwitch", text='Stroke Settings', icon="BRUSH_DATA")
            
            if scene.SculptStrokeSwitch:
                col.label(text="Stroke Method:")
                col.prop(brush, "stroke_method", text="")
                
                if brush.use_anchor:
                    col.separator()
                    col.prop(brush, "use_edge_to_edge", "Edge To Edge")

                if brush.use_airbrush:
                    col.separator()
                    col.prop(brush, "rate", text="Rate", slider=True)

                if brush.use_space:
                    col.separator()
                    row = col.row(align=True)
                    row.prop(brush, "spacing", text="Spacing")
                    row.prop(brush, "use_pressure_spacing", toggle=True, text="")

                if brush.use_line or brush.use_curve:
                    col.separator()
                    row = col.row(align=True)
                    row.prop(brush, "spacing", text="Spacing")

                if brush.use_curve:
                    col.separator()
                    col.template_ID(brush, "paint_curve", new="paintcurve.new")
                    col.operator("paintcurve.draw")

                if context.sculpt_object:
                    if brush.sculpt_capabilities.has_jitter:
                        col.separator()

                        row = col.row(align=True)
                        row.prop(brush, "use_relative_jitter", icon_only=True)
                        if brush.use_relative_jitter:
                            row.prop(brush, "jitter", slider=True)
                        else:
                            row.prop(brush, "jitter_absolute")
                        row.prop(brush, "use_pressure_jitter", toggle=True, text="")

                    if brush.sculpt_capabilities.has_smooth_stroke:
                        col.separator()

                        col.prop(brush, "use_smooth_stroke")

                        sub = col.column()
                        sub.active = brush.use_smooth_stroke
                        sub.prop(brush, "smooth_stroke_radius", text="Radius", slider=True)
                        sub.prop(brush, "smooth_stroke_factor", text="Factor", slider=True)
                else:
                    col.separator()

                    row = col.row(align=True)
                    row.prop(brush, "use_relative_jitter", icon_only=True)
                    if brush.use_relative_jitter:
                        row.prop(brush, "jitter", slider=True)
                    else:
                        row.prop(brush, "jitter_absolute")
                    row.prop(brush, "use_pressure_jitter", toggle=True, text="")

                    col.separator()

                    if brush.brush_capabilities.has_smooth_stroke:
                        col.prop(brush, "use_smooth_stroke")

                        sub = col.column()
                        sub.active = brush.use_smooth_stroke
                        sub.prop(brush, "smooth_stroke_radius", text="Radius", slider=True)
                        sub.prop(brush, "smooth_stroke_factor", text="Factor", slider=True)
                        
                col.prop(settings, "input_samples")
                
            col = layout.column()
            col.separator()
            
            box = layout.box()            
            col = box.column()
            col.prop(scene, "BrushShapeCurveSwitch", text='Brush Shape Curve', icon="SMOOTHCURVE")
            
            if scene.BrushShapeCurveSwitch:
                col.template_curve_mapping(brush, "curve", brush=True)
                col = box.column()
                row = col.row(align=True)
                row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
                row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
                row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
                row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
                row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
                row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'
                
        if not scene.SculptModeSwitch:
            col.separator()
            col.separator()
            box = layout.box()            
            col = box.column()
            col.label(text='Mesh Based Terrain Editing:')
            col.operator("object.assign_mesh_terrain_modifier", icon='OUTLINER_OB_LATTICE')
            col.operator("object.add_mesh_terrain_modifier", icon='OUTLINER_OB_LATTICE')
            col.operator("object.apply_mesh_terrain_modifier", icon='FILE_TICK')
            col.separator()
            col.label(text='Spline Based Terrain Editing:')
            col.operator("object.add_spline_terrain_modifier", icon='IPO_BEZIER')
            col.operator("object.apply_spline_terrain_modifier", icon='FILE_TICK')
            if context.active_object is not None and context.active_object.type == 'CURVE':
                col.prop(object,'FlatterWidth',text='Modifier Width')
                
            if context.active_object is not None and context.active_object.type == 'CURVE' and context.active_object.mode == 'EDIT':
                for point in bpy.context.active_object.data.splines.active.bezier_points:
                    if point.select_control_point == True:
                        col.prop(point,'radius',text='Custom Width')
                        col.prop(point,'tilt')
                        break
        
class VIEW3D_SurfacePainting(Panel,View3DPaintPanel):
    bl_category = "bLandscape Tools"
    bl_label = "Surface Painting"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    
    Scene.SurfacePaintingSwitch = BoolProperty(default=False)
    
    Scene.PaintModeSwitch = BoolProperty(default=False,update=update_switchpaintmode)
    Scene.PaintStrokeSwitch = BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return context.scene.SurfacePaintingSwitch

    def draw(self, context):
        scene = context.scene
        object = context.active_object
        layout = self.layout
        
        col = layout.column()
        
        if scene.PaintModeSwitch:
            text = 'Disable Surface Painting & Save Changes'
            
        else:
            text = 'Enable Surface Painting'
        col.prop(scene, "PaintModeSwitch", text=text, icon="TPAINT_HLT")
        if scene.SculptModeSwitch or (context.active_object is not None and context.active_object.mode == 'EDIT'):
            col.enabled = False
            
        if scene.PaintModeSwitch:
            toolsettings = context.tool_settings
            settings = self.paint_settings(context)
            brush = settings.brush
            
            box = layout.box()            
            col = box.column()
            col.label(text='Brush settings')
            
            if not context.particle_edit_object:
                col.separator()
                col.separator()
                col.template_ID_preview(settings, "brush", new="brush.add", rows=3, cols=8)
                
            capabilities = brush.sculpt_capabilities
            col.separator()
            col.separator()
            row = col.row(align=True)
            
            if context.image_paint_object and brush:
                self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")
            
            col = layout.column()
            col.separator()
            
            box = layout.box()            
            col = box.column()
            col.prop(scene, "PaintStrokeSwitch", text='Stroke Settings', icon="BRUSH_DATA")
            
            if scene.PaintStrokeSwitch:
                col.label(text="Stroke Method:")

                col.prop(brush, "stroke_method", text="")

                if brush.use_anchor:
                    col.separator()
                    col.prop(brush, "use_edge_to_edge", "Edge To Edge")

                if brush.use_airbrush:
                    col.separator()
                    col.prop(brush, "rate", text="Rate", slider=True)

                if brush.use_space:
                    col.separator()
                    row = col.row(align=True)
                    row.prop(brush, "spacing", text="Spacing")
                    row.prop(brush, "use_pressure_spacing", toggle=True, text="")

                if brush.use_line or brush.use_curve:
                    col.separator()
                    row = col.row(align=True)
                    row.prop(brush, "spacing", text="Spacing")

                if brush.use_curve:
                    col.separator()
                    col.template_ID(brush, "paint_curve", new="paintcurve.new")
                    col.operator("paintcurve.draw")

                col.separator()

                row = col.row(align=True)
                row.prop(brush, "use_relative_jitter", icon_only=True)
                if brush.use_relative_jitter:
                    row.prop(brush, "jitter", slider=True)
                else:
                    row.prop(brush, "jitter_absolute")
                row.prop(brush, "use_pressure_jitter", toggle=True, text="")

                col.separator()

                if brush.brush_capabilities.has_smooth_stroke:
                    col.prop(brush, "use_smooth_stroke")
                    sub = col.column()
                    sub.active = brush.use_smooth_stroke
                    sub.prop(brush, "smooth_stroke_radius", text="Radius", slider=True)
                    sub.prop(brush, "smooth_stroke_factor", text="Factor", slider=True)
                col.prop(settings, "input_samples")
                   
class VIEW3D_ViewportSettings(Panel):
    bl_category = "bLandscape Tools"
    bl_label = "Viewport Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    
    Scene.ViewportSettingsSwitch = BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return context.scene.ViewportSettingsSwitch

    def draw(self, context):
        scene = context.scene
        view = context.space_data
        layout = self.layout
        fx_settings = view.fx_settings
        userPreferences = context.user_preferences
        systemTab = userPreferences.system
        
        
        row = layout.row(align=True)
        row.operator("object.appearance_textured_nowire",icon='TEXTURE')
        row.operator("object.appearance_textured_wire",icon='ASSET_MANAGER')
        if not scene.TerrainTextureFormatValid:
            row.enabled = False
            
        row2 = layout.row(align=True)
        row2.operator("object.appearance_smooth", text="Smooth",icon='MOD_SMOOTH')
        row2.operator("object.appearance_flat", text="Flat",icon='MOD_DISPLACE')
        
        
        
        row1 = layout.row(align=True)
        row1.operator("scene.appearance_matcap_nowire",icon='MATCAP_13')
        row1.operator("scene.appearance_matcap_wire",icon='MOD_TRIANGULATE')
        
        Areas = context.screen.areas
        for Area in Areas:
            if Area.type == 'VIEW_3D':
                if  Area.spaces.active.use_matcap == True and Area.spaces.active.viewport_shade == 'SOLID':
                    row4 = layout.row(align=False)
                    row4.template_icon_view(view, "matcap_icon")
        
        col = layout.column()
        col.prop(fx_settings, "use_ssao", text="Ambient Occlusion")
        if fx_settings.use_ssao:
                ssao_settings = fx_settings.ssao
                subcol = col.column(align=True)
                subcol.prop(ssao_settings, "factor")
                subcol.prop(ssao_settings, "distance_max")
                subcol.prop(ssao_settings, "attenuation")
                subcol.prop(ssao_settings, "samples")
          
        col = layout.column()
        col.separator()
        
        if scene.SurfaceMaskFormatValid:
            surfaceMaskTexture = bpy.data.objects['Terrain_' + context.scene.name].material_slots[0].material.texture_slots[1]
            row3 = layout.row(align=True)
            row3.prop(surfaceMaskTexture,"diffuse_color_factor",text='Surface mask opacity')
            row3.prop(surfaceMaskTexture,"blend_type")
            if not scene.PaintModeSwitch:
                row3.enabled = False
        
        colMipMap = layout.column()
        colMipMap.prop(systemTab, "use_mipmaps",text='Textures mipmaps')
        if not scene.TerrainTextureFormatValid:
            colMipMap.enabled = False
        colMipMap.separator()
            
        rowSea = layout.row(align=True)
        seaMaterial = bpy.data.materials['SeaMaterial_{}'.format(context.scene.name)]
        rowSea.prop(seaMaterial,'alpha', text='Sea transparency')
        rowSea.prop(seaMaterial,'diffuse_color',text='')
        
            
        colNearFar = layout.column(align=True)
        colNearFar.separator()
        colNearFar.label(text="Clip Near/Far Plane(m):")
        colNearFar.prop(view, "clip_start", text="Start")
        colNearFar.prop(view, "clip_end", text="End")

    
    
    
                 
class VIEW3D_bLTilities(Panel):
    bl_category = "bLandscape Tools"
    bl_label = "bLTilities"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    
    Scene.CheckSurfaceMaskPath = StringProperty(name="Surface mask path",
        description="Path to surface mask",
        default='Surface Mask',
        maxlen= 1024,
        subtype='FILE_PATH',
        update=update_checksurfacemaskpath)
        
    Scene.CheckSurfaceMaskFormatValid = BoolProperty(default=False)
    
    Scene.CheckSurfacesDefinitionPath = StringProperty(name="Layers.cfg",
        description="",
        default='Layers cfg',
        maxlen= 1024,
        subtype='FILE_PATH',
        update=update_checksurfacesdefinitionpath)
        
    Scene.CheckSurfacesDefinitionFormatValid = BoolProperty(default=False)
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout

        col = layout.column(align=True)
        col.operator("scene.create_flatterrain",icon='MESH_GRID')
        col.operator("scene.create_surfacemask",icon='COLORSET_03_VEC')
        
        col1 = layout.column(align=True)
        col1.operator("scene.check_surfacemaskfull",icon='IMAGE_RGB')
        row = col1.row(align=False)
        row.prop(scene,'CheckSurfaceMaskPath',text="")
        row.prop(scene,'CheckSurfacesDefinitionPath',text="")
