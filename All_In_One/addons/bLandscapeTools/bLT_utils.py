import bpy,bgl,blf,bmesh
import subprocess,os,time, struct,sys, datetime
from shutil import copy,rmtree
from math import floor, isnan, ceil, sqrt
from numpy import genfromtxt,vstack,hstack,array,savetxt,delete,ones,zeros,flipud,empty,fromfile,float16,float32,reshape,uint8
from mathutils import Vector, Matrix


def bLTLogger(messageType,body):
    if bpy.data.texts.get("bLTlog") == None:
        bpy.data.texts.new('bLTlog')
    else:
        log = bpy.data.texts["bLTlog"]
        log.current_line_index = len(log.lines) if len(log.lines) != log.current_line_index else log.current_line_index
        if len(log.current_line.body) != 0:
            if log.current_line.body[0] != '~':
                log.current_line.body = ''
        if messageType == 'Err':
            log.write('~{} - {} @ERROR\n'.format(datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"),body))
        elif messageType == 'Scs':
            log.write('~{} - {} #SUCCESS\n'.format(datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"),body))
        elif messageType == 'Inf':
            log.write('~{} - {}\n'.format(datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"),body))
        elif messageType == 'Wrn':
            log.write('~{} - {} "WARNING"\n'.format(datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"),body))
        elif messageType == 'PgsUp':
            log.current_line.body = '~{} - {} "PROGRESS"'.format(datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"),body)
        elif messageType == 'PgsDn':
            log.current_line.body = ''
            log.write('~{} - {} #SUCCESS\n'.format(datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"),body))
    try:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    except:
        pass

def install_opencv():
    libFolder = '{}\lib'.format(getPaths()[1])
    sys.path.append(libFolder)
    import pip
    pip.main(['install', 'opencv-python', '--no-deps'])
    try:
        import cv2
        bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.OpenCVInstalled = True
        print('\nbLT_Info: OpenCV installed successfully')
    except:
        bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.OpenCVInstalled = False
        print('\nbLT_Info: OpenCV installation problem!!!')
    

    


def getTerrainTexTiles(texturePath):
    folderPath = os.path.dirname(os.path.abspath(texturePath))
    base = os.path.basename(texturePath)
    fileAndExt = os.path.splitext(base)
    fileNoNumber = fileAndExt[0].strip('_0')
    
    textureTiles = []
    textureTiles.append(texturePath)
    
    i = 0
    while True:
        i += 1
        if os.path.exists('{}\\{}_{}{}'.format(folderPath,fileNoNumber,i,fileAndExt[1])):
            textureTiles.append('{}\\{}_{}{}'.format(folderPath,fileNoNumber,i,fileAndExt[1]))
        else:
            break
    return textureTiles
    
def update_importterraintexturepath(self, context):
    terrainTexturePath = context.scene.ImportTerrainTexturePath
    
    if terrainTexturePath != '':
        
        if terrainTexturePath.split('.')[-1] in ['png','tif','tiff','jpg','jpeg','PNG','TIF','TIFF','JPG','JPEG']:
            
            context.scene.TerrainTextureFormatValid = True
            from cv2 import imread, imwrite, resize , IMREAD_COLOR
            
            GDALPath = context.user_preferences.addons["bLandscapeTools-master"].preferences.GDALPath
            ProjFolderPath = context.scene.ProjFolderPath
            ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
            
            if os.path.exists('{}ProjectData\\Textures\\previewSatTex.png'.format(ProjFolderPath)):
                os.remove('{}ProjectData\\Textures\\previewSatTex.png'.format(ProjFolderPath))   
                
            imagerySize = getImagerySize(GDALPath,terrainTexturePath)
            print('\nbLT_Info: Terrain texture preview creation started {}'.format(time.ctime()))
            
            if '_0.' in terrainTexturePath:
                bLTLogger('Wrn','Tiled terrain texture detected, creation of preview from tiles may take a while!')
                tilesList = getTerrainTexTiles(terrainTexturePath)
                tilesInRow = int(sqrt(len(tilesList)))
                tilePreviewRes = int(imagerySize / ((imagerySize * tilesInRow) / 5000))
                previewImage = zeros((tilePreviewRes * tilesInRow,tilePreviewRes * tilesInRow,3), uint8)
                
                topLeftX = topLeftY = 0
                bottomRightX = bottomRightY = tilePreviewRes
                i = 0
                for tile in tilesList:
                    input_image_cv = imread(tile, IMREAD_COLOR)
                    resizedImage = resize(input_image_cv, (tilePreviewRes, tilePreviewRes))
                    previewImage[topLeftY:bottomRightY,topLeftX:bottomRightX] = resizedImage
                    i += 1
                    if i < tilesInRow:
                        topLeftX += tilePreviewRes
                        bottomRightX += tilePreviewRes
                    else:
                        i = 0
                        topLeftX = 0
                        bottomRightX = tilePreviewRes
                        topLeftY += tilePreviewRes
                        bottomRightY += tilePreviewRes
                imwrite(r'{}ProjectData\Textures\previewSatTex.png'.format(ProjFolderPath), previewImage)
            else:
                if imagerySize < 5000:
                    bLTLogger('Inf','Terrain texture size <= 5000x5000 px, no resizing necessary.')
                    print(' Input imagery size <= 5000x5000 px, no resizing necessary.')
                    copy(context.scene.ImportTerrainTexturePath,'{}ProjectData\\Textures\\'.format(ProjFolderPath))
                    oldName = context.scene.ImportTerrainTexturePath.split('\\')[-1]
                    os.rename('{}ProjectData\\Textures\\{}'.format(ProjFolderPath,oldName),'{}ProjectData\\Textures\\previewSatTex.png'.format(ProjFolderPath))
                else:
                    bLTLogger('Wrn','Terrain texture size > 5000x5000 px, needs to be downscaled!')
                    print(' Input imagery size > 5000x5000 px, needs to be downscaled.')
                    input_image_cv = imread(terrainTexturePath, IMREAD_COLOR)
                    resizedImage = resize(input_image_cv, (5000, 5000))
                    imwrite(r'{}ProjectData\Textures\previewSatTex.png'.format(ProjFolderPath), resizedImage)
            
                
            if bpy.data.images.get('previewSatTex.png') is None:
                bpy.data.images.load('{}ProjectData\\Textures\\previewSatTex.png'.format(ProjFolderPath))
                bpy.data.images['previewSatTex.png'].use_fake_user = True
            else:
                bpy.data.images['previewSatTex.png'].reload()
                
            defaultLocationScene = bpy.data.scenes['Default_Location']    
            defaultLocationScene["ImageryResolution"] = imagerySize
            
            bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
            
            print(' Terrain texture preview image created successfully.')
            print('bLT_Info: Terrain texture preview creation finished {}'.format(time.ctime()))    
            bpy.ops.wm.save_mainfile()
            bLTLogger('Scs','Terrain texture preview image(used in 2D view) created successfully.')
        else:
            context.scene.TerrainTextureFormatValid = False
            print('\nbLT_Info: {} is not supported imagery file format! Use PNG, TIF, TIFF, JPG, JPEG instead.'.format(terrainTexturePath.split('.')[-1]))
            bLTLogger('Err','{} is not supported terrain texture file format! Use PNG, TIF, TIFF, JPG, JPEG instead.'.format(terrainTexturePath.split('.')[-1]))
    else:
        context.scene.TerrainTextureFormatValid = False
        
def update_importterrainsurfacemaskpath(self, context):
    terrainSurfaceMaskPath = context.scene.ImportTerrainSurfaceMaskPath
    ProjFolderPath = context.scene.ProjFolderPath
    ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
    
    if terrainSurfaceMaskPath != '':
        if terrainSurfaceMaskPath.split('.')[-1] in ['png','tif','tiff','PNG','TIF','TIFF']:
            context.scene.SurfaceMaskFormatValid = True
            bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
            bLTLogger('Scs','Surface mask loaded successfully.')
        else:
            context.scene.SurfaceMaskFormatValid = False
            print('\nbLT_Info: {} is unsupported surface mask file format! Use PNG, TIF, TIFF instead.'.format(terrainSurfaceMaskPath.split('.')[-1]))
            bLTLogger('Err','{} is unsupported surface mask file format! Use PNG, TIF, TIFF instead.'.format(terrainSurfaceMaskPath.split('.')[-1]))
    else:
        context.scene.SurfaceMaskFormatValid = False
    
def update_importterrainheightmappath(self, context):
    
    terrainHeightmapPath = context.scene.ImportTerrainHeightmapPath
    
    if terrainHeightmapPath !='':
        if terrainHeightmapPath.split('.')[-1] in ['asc','ascii']:
            context.scene.HeightmapFormatValid = True
            GDALPath = bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.GDALPath
            ProjFolderPath = bpy.data.scenes["Default_Location"].ProjFolderPath
            ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
            elevationInfo = getElevFileHeader(terrainHeightmapPath)
            print('\nbLT_Info: ASC elevation to bLTe format conversion started {}'.format(time.ctime()))
            ascElevation = genfromtxt(terrainHeightmapPath, delimiter=' ', skip_header=6)
            binElevFilePath = '{}ProjectData\\Textures\\elevation.bLTe'.format(ProjFolderPath)
            ascElevation.astype('float32').tofile(binElevFilePath)
            bLTLogger('Scs','ASC elevation converted to bLTe format successfully.')
            print('bLT_Info: ASC elevation to bLTe format conversion finished {}'.format(time.ctime()))
            
            print('\nbLT_Info: Shaded terrain preview creation started {}'.format(time.ctime()))
            updateterrainpreview(terrainHeightmapPath)
            bLTLogger('Scs','Shaded terrain preview image(used in 2D view) created successfully.')
            print('bLT_Info: Shaded terrain preview creation finished {}'.format(time.ctime()))
            
            defaultLocationScene = bpy.data.scenes['Default_Location']
            defaultLocationScene["TerrainResolution"] = elevationInfo[0]
            defaultLocationScene["xllcorner"] = elevationInfo[1]
            defaultLocationScene["yllcorner"] = elevationInfo[2]
            defaultLocationScene["CellSize"] = elevationInfo[3]
            bpy.data.scenes['Default_Location'].bLTElevationPath = binElevFilePath

            bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        else:
            context.scene.HeightmapFormatValid = False
            bLTLogger('Err','{} is unsupported elevation file format! Use ASC or ASCII instead.'.format(terrainHeightmapPath.split('.')[-1]))
            print('bLT_Info: {} is unsupported elevation file format! Use ASC or ASCII instead.'.format(terrainHeightmapPath.split('.')[-1]))
    else:
        context.scene.HeightmapFormatValid = False

def parseLayersCfg(path):
    bLTLogger('Inf','Parsing layers.cfg file.')
    try:
        surfaceDefinitionFile = open(path,encoding="utf8")
        surfaces = []
        materials = {}
        validRGBValues = []
        colors = {}
        
        for line in surfaceDefinitionFile.readlines():
            line = (line.lstrip()).rstrip('\n')
            if line.split(' ')[0] == 'class' and line.split(' ')[1] not in ['Layers','Legend','Colors']:
                surfaceName = line.split(' ')[1].strip()
                if '\t' in line.split(' ')[1].strip():
                    surfaceName = line.split(' ')[1].strip().split('\t')[0]
                surfaces.append(surfaceName)
            if line.split('=')[0].rstrip() == 'material':
                materials[surfaces[-1]] = line.split('=')[1].split(';')[0].strip()[1:-1]
            if line.split('[]')[0] in surfaces:
                RGBvalues = list(map(int, line.split('{{')[1].split('}}')[0].split(',')))
                validRGBValues.append(RGBvalues)
                colors[line.split('[]')[0]] = RGBvalues
        surfaceDefinitionFile.close()
        bLTLogger('Scs','layers.cfg parsed successfully.')
        return materials, colors, validRGBValues
    except:
        bLTLogger('Err','Problem while parsing layers.cfg.')
    
def update_importsurfacesdefinitionpath(self, context):
    surfacesDefinitionPath = context.scene.ImportSurfacesDefinitionPath
    ProjFolderPath = bpy.data.scenes["Default_Location"].ProjFolderPath
    ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
    
    if surfacesDefinitionPath != '':
        if surfacesDefinitionPath.split('.')[-1] == 'cfg':
            if len(context.scene.TexturePaintBrushNames) != 0:
                for textureBrushName in context.scene.TexturePaintBrushNames:
                    bpy.data.brushes.remove(bpy.data.brushes[textureBrushName.name])
                for TexturePaintBrushName in context.scene.TexturePaintBrushNames:
                    context.scene.TexturePaintBrushNames.remove(0)
                    
            
            DevDriveLetter = context.scene.DevDriveLetter
            ProjFolderPath = bpy.data.scenes["Default_Location"].ProjFolderPath
            
            materials, colors = parseLayersCfg(surfacesDefinitionPath)[0:2]
            
            from cv2 import imread, imwrite, resize, IMREAD_COLOR
            
            print('\nbLT_Info: Surface brushes and previews creation started {}'.format(time.ctime()))
            for surfaceName, materialPath in materials.items():
                f = open('{}{}'.format(DevDriveLetter,materialPath))
                texturePath = None
                for line in f.readlines():
                    line = (line.lstrip()).rstrip('\n')
                    if line.split('=')[0].rstrip(' ') == 'texture':
                        if line.split('_')[-1].split('.')[0] == 'co':
                            if line.split(';')[0].split('.')[1][0:-1] == 'png':
                                texturePath = (line.split('"')[1])
                f.close()
                
                if texturePath != None:
                    input_image_cv = imread('{}{}'.format(DevDriveLetter,texturePath), IMREAD_COLOR)
                    resizedImage = resize(input_image_cv, (128, 128))
                    rgb = ones((28,128,3), uint8)
                    rgb[:,:,2], rgb[:,:,1], rgb[:,:,0] = colors[surfaceName][0], colors[surfaceName][1], colors[surfaceName][2]
                    resizedImage[0:28,:] = rgb
                    imwrite(r'{}ProjectData\Textures\previewIcon_{}.png'.format(ProjFolderPath,surfaceName), resizedImage)
                    bLTLogger('Scs','Surface \'{}\' preview icon created successfully.'.format(surfaceName))
                else:
                    rgb = ones((128,128,3), uint8)
                    rgb[:,:,2], rgb[:,:,1], rgb[:,:,0] = colors[surfaceName][0], colors[surfaceName][1], colors[surfaceName][2]
                    imwrite(r'{}ProjectData\Textures\previewIcon_{}.png'.format(ProjFolderPath,surfaceName), rgb)
                    bLTLogger('Wrn','Surface \'{}\' has no valid texture(must be png), a color assigned to this surface will be used for the preview icon instead!'.format(surfaceName))
                    print('\tbLT_Info: Surface \'{}\' has no valid texture(must be png), a color assigned to this surface will be used for the preview icon instead!'.format(surfaceName))

                currentBrush = bpy.data.brushes.new(surfaceName)
                currentBrush.use_custom_icon = True
                currentBrush.icon_filepath = '{}ProjectData\Textures\previewIcon_{}.png'.format(ProjFolderPath,surfaceName)
                currentBrush.strength = 1.0
                bpy.context.scene.tool_settings.image_paint.use_normal_falloff = False
                bpy.context.scene.tool_settings.image_paint.seam_bleed = 0
                currentBrush.color = (0 if colors[surfaceName][0] == 0 else colors[surfaceName][0] / 255,
                                      0 if colors[surfaceName][1] == 0 else colors[surfaceName][1] / 255,
                                      0 if colors[surfaceName][2] == 0 else colors[surfaceName][2] / 255)
                currentBrush.secondary_color = (0 if colors[surfaceName][0] == 0 else colors[surfaceName][0] / 255,
                                                0 if colors[surfaceName][1] == 0 else colors[surfaceName][1] / 255,
                                                0 if colors[surfaceName][2] == 0 else colors[surfaceName][2] / 255)
                currentBrush.curve.curves[0].points.remove(currentBrush.curve.curves[0].points[1])
                currentBrush.curve.curves[0].points.remove(currentBrush.curve.curves[0].points[1])
                currentBrush.curve.curves[0].points[1].location[1] = 1.0
                currentBrush.curve.update()
                currentBrush = context.scene.TexturePaintBrushNames.add()
                currentBrush.name = surfaceName
                bLTLogger('Scs','Surface brush \'{}\' created successfully.'.format(surfaceName))
                
            bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
            print('bLT_Info: Surface brushes and previews creation finished {}'.format(time.ctime()))
                
        else:
            bLTLogger('Err','{} is unsupported config file format! Use CFG instead.'.format(surfacesDefinitionPath.split('.')[-1]))
            print('\nbLT_Info: {} is unsupported config file format! Use CFG instead.'.format(surfacesDefinitionPath.split('.')[-1]))
            
def update_devdriveletter(self, context):
    if not os.path.exists(context.scene.DevDriveLetter):
        context.scene.DevDriveValid = False
        bLTLogger('Err','System drive {} does not exist!'.format(context.scene.DevDriveLetter))
        print('\nbLT_Info: System drive {} doesn\'t exist!'.format(context.scene.DevDriveLetter))
    else:
        context.scene.DevDriveValid = True
        ProjFolderPath = bpy.data.scenes["Default_Location"].ProjFolderPath
        ProjectName = 'Project_{}'.format(ProjFolderPath.split('\\')[-2])
        bpy.ops.wm.save_as_mainfile(filepath='{}{}.blend'.format(ProjFolderPath,ProjectName))
        print('\nbLT_Info: System drive {} does exist.'.format(context.scene.DevDriveLetter))
          
def update_switchsculptmode(self, context):
    if context.scene.SculptModeSwitch:
        bpy.ops.object.select_all(action='DESELECT')
        terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
        terrainObject.select=True
        context.scene.objects.active = terrainObject
        bpy.ops.object.mode_set(mode='SCULPT')
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
def update_switchpaintmode(self, context):
    if context.scene.PaintModeSwitch:
        bpy.ops.object.select_all(action='DESELECT')
        terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
        terrainObject.select=True
        context.scene.objects.active = terrainObject
        bpy.ops.object.appearance_textured_nowire()
        terrainObject.material_slots[0].material.use_textures[1] = True
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
    else:
        contextCopy = context.area
        context.area.type = 'IMAGE_EDITOR'
        bpy.ops.image.save()
        bLTLogger('Scs','Surface mask changes saved successfully.')
        contextCopy.type = 'VIEW_3D'
        context.active_object.material_slots[0].material.use_textures[1] = False
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
def update_flatterwidth(self, context):
    splineTerrainModifier = context.active_object
    flatterObject = splineTerrainModifier.children[0]
    flatterObject.scale.y = self.FlatterWidth
    
def updateterrainpreview(terrainHeightmapPath):
    GDALPath = bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.GDALPath
    ProjFolderPath = bpy.data.scenes["Default_Location"].ProjFolderPath
    
    cmd = '"{}gdaldem.exe" hillshade -az 45 -z 1.3 "{}" "{}ProjectData\Textures\previewTerTex.tif"'.format(GDALPath,terrainHeightmapPath,ProjFolderPath)
    subprocess.call(cmd)
    
    if bpy.data.images.get('previewTerTex.tif') is None:
        bpy.data.images.load('{}ProjectData\\Textures\\previewTerTex.tif'.format(ProjFolderPath))
        bpy.data.images['previewTerTex.tif'].use_fake_user = True
    else:
        bpy.data.images['previewTerTex.tif'].reload()      
        
def getPaths():
    import addon_utils
    addons = [mod for mod in addon_utils.modules(refresh=False)]
    for mod in addons:
        if mod.__name__ == "bLandscapeTools-master":
            scriptPath = mod.__file__
            pass
           
    scriptFolder = scriptPath[:-12]
    dataFolder = '{}\\data'.format(scriptFolder)
    
    return scriptPath,scriptFolder,dataFolder
     
def getImagerySize(GDALPath,terrainTexturePath):
    ext = terrainTexturePath.split('.')[-1]
    if ext in  ['png','PNG']:
        worldFile = 'pgw'
    if ext in ['tif', 'tiff', 'TIF', 'TIFF']:
        worldFile = 'tfw'
    if ext in ['jpg', 'jpeg', 'JPG', 'JPEG']:
        worldFile = 'jgw'
        
    cmd = '{}gdalinfo.exe "{}"'.format(GDALPath,terrainTexturePath)
    satInfo = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    
    for i in range(0,10):
        line = str(satInfo.stdout.readline()).rstrip('\\r\\n\'')
        if line.split(' ')[0][2:] == 'Size':
            info = int(line.split(' ')[3])

    return info
    
def getElevFileHeader(path):
    info = []
    f = open(path,"r")
    line = f.readline().split(" ")
    for i in range(5):
        info.append( line[-1])
        line = f.readline().split(" ")
    f.close()
    ncols = int(info[0])
    cellSize = float(info[4])
    x = float(info[2])
    y = float(info[3])
    return ncols,x,y,cellSize

    
    

def setupLocationAppearance(locationName, hasMaterial):
    bpy.ops.object.lamp_add(type='HEMI')
    hemi = bpy.context.object
    hemi.hide = True
    hemi.name = "Hemi_" + locationName

    Areas = bpy.context.screen.areas
    for Area in Areas:
        if Area.type == 'VIEW_3D':
            if hasMaterial:
                Area.spaces.active.viewport_shade = 'MATERIAL'
            else:
                Area.spaces.active.viewport_shade = 'SOLID'
                bpy.ops.scene.appearance_matcap_nowire()
            Area.spaces.active.cursor_location = [0,0,0]
            Area.spaces.active.clip_start = 0.1
            Area.spaces.active.clip_end = 20000
            Area.spaces.active.show_world = True
            Area.spaces.active.show_floor = False
            Area.spaces.active.show_axis_x = False
            Area.spaces.active.show_axis_y = False
            Area.spaces.active.fx_settings.use_ssao = True
            Area.spaces.active.fx_settings.ssao.factor = 4.1
            Area.spaces.active.fx_settings.ssao.distance_max = 4.0
            Area.spaces.active.fx_settings.ssao.samples = 70
            Area.spaces.active.fx_settings.use_ssao = False
    
            
def createProject():
    dataFolder = getPaths()[2]
    print('\nbLT_Info: Project created.')
    ProjFolderPath = bpy.context.scene.ProjFolderPath

        
  
    
    
    bpy.ops.wm.read_homefile(use_splash=False, app_template="bLandscapeTools")
    bpy.context.scene.isProject = True
    bpy.context.scene.ProjFolderPath = ProjFolderPath
    bpy.context.scene['isLocation'] = False

    if not os.path.exists(bpy.context.scene.ProjFolderPath + 'ProjectData'):
	    os.makedirs(bpy.context.scene.ProjFolderPath + 'ProjectData\\Textures')
    else:
        rmtree(bpy.context.scene.ProjFolderPath + 'ProjectData')
        os.makedirs(bpy.context.scene.ProjFolderPath + 'ProjectData\\Textures')
    if not os.path.exists(bpy.context.scene.ProjFolderPath + 'Output'):
	    os.makedirs(bpy.context.scene.ProjFolderPath + 'Output\\bLTilities')
    else:
        rmtree(bpy.context.scene.ProjFolderPath + 'Output')
        os.makedirs(bpy.context.scene.ProjFolderPath + 'Output\\bLTilities')
        
def setup2dMapPreview():
    bpy.context.area.type = 'IMAGE_EDITOR'
    for space in bpy.context.area.spaces:
        if space.type == 'IMAGE_EDITOR':
            space.image = bpy.data.images['previewTerTex.tif']
            if bpy.data.images.get('previewSatTex.png') is not None:
                space.image = bpy.data.images['previewSatTex.png']        

    bpy.ops.image.view_all()
    bLTLogger('Inf', 'Hint: Cycle through available 2D maps with Backspace key.')
    screen = bpy.context.window.screen
    for area in screen.areas:
        if area.type == 'IMAGE_EDITOR':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'window': bpy.context.window, 'screen': screen, 'area': area, 'region': region}
    bpy.ops.view2d.pick_location(override,'INVOKE_DEFAULT')

def drawSplashScreen(self,context):
    region = context.region

    width,height = region.width,region.height
    center = [width / 2, height / 2]
    
    font_id = 0
    blf.size(font_id, 13, 80)
    blf.enable(0, blf.SHADOW)
    blf.shadow_offset(0, 1, -1)
    blf.shadow(0, 3, 0.0, 0.0, 0.0, 1)

    bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.img.bindcode[0])
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
    bgl.glEnable(bgl.GL_TEXTURE_2D)
    bgl.glTexEnvf(bgl.GL_TEXTURE_ENV,bgl.GL_TEXTURE_ENV_MODE, bgl.GL_REPLACE)
    bgl.glBegin(bgl.GL_QUADS)
    
    bgl.glTexCoord2f(0, 0)
    bgl.glVertex2f(center[0] - 384, center[1] - 245)

    bgl.glTexCoord2f(0, 1)
    bgl.glVertex2f(center[0] - 384, center[1] + 245)

    bgl.glTexCoord2f(1, 1)
    bgl.glVertex2f(center[0] + 384, center[1] + 245)

    bgl.glTexCoord2f(1, 0)
    bgl.glVertex2f(center[0] + 384, center[1] - 245)

    bgl.glEnd()
    bgl.glDisable(bgl.GL_TEXTURE_2D)
    
    bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
    blf.position(font_id, center[0] - 380, center[1] - 237, 0)
    blf.draw(font_id, 'Version: Bushlurker(Test build: 0.2)')
    
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    blf.disable(0, blf.SHADOW)
    
def drawLocationSelectionRectangle(self, context):
    region = context.region

    width,height = region.width,region.height

    font_id = 0
    blf.size(font_id, 12, 72)
    blf.enable(0, blf.SHADOW)
    blf.shadow_offset(0, 2, -2)
    blf.shadow(0, 3, 0.0, 0.0, 0.0, 1)
    
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineStipple(2, 0xAAAA)
    bgl.glColor4f(.7, .7, .7, 1.0)
    bgl.glEnable(bgl.GL_LINE_STIPPLE)
    
    if not self.switch:
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2i(0, self.mouseY)
        bgl.glVertex2i(width, self.mouseY)
        bgl.glVertex2i(self.mouseX, 0)
        bgl.glVertex2i(self.mouseX, height)
        bgl.glEnd()
        
    else:
        selOrigUV = self.selectionRectangleOriginUV
        selOrigWindow = list(bpy.context.region.view2d.view_to_region(selOrigUV[0],selOrigUV[1],clip=False))
        
        bgl.glBegin(bgl.GL_LINE_LOOP)
        bgl.glVertex2i(self.mouseX, self.mouseY)
        bgl.glVertex2i(selOrigWindow[0], self.mouseY)
        bgl.glVertex2i(selOrigWindow[0], selOrigWindow[1])
        bgl.glVertex2i(self.mouseX, selOrigWindow[1])
        bgl.glEnd()

        bgl.glColor4f(0.0, 1.0, 0.0, 0.3)
        bgl.glBegin(bgl.GL_POLYGON)
        bgl.glVertex2i(self.mouseX, self.mouseY)
        bgl.glVertex2i(selOrigWindow[0], self.mouseY)
        bgl.glVertex2i(selOrigWindow[0], selOrigWindow[1])
        bgl.glVertex2i(self.mouseX, selOrigWindow[1])
        bgl.glEnd()
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        blf.position(font_id, self.mouseX - 210, self.mouseY - 15, 0)
        blf.draw(font_id, self.vertexCount)
        blf.position(font_id, self.mouseX - 210, self.mouseY - 30, 0)
        blf.draw(font_id, self.trianglesCount)
        blf.position(font_id, self.mouseX - 210, self.mouseY - 45, 0)
        blf.draw(font_id, self.mapSize)      

    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    bgl.glDisable(bgl.GL_LINE_STIPPLE)
    blf.disable(0, blf.SHADOW)
          
def selectionCorrection(locCursor,locOrigin):
    cursorX, cursorY, originX, originY = locCursor[0], locCursor[1], locOrigin[0], locOrigin[1]

    if originX < 0:
        originX = 0.0
    elif originX > 1:
        originX = 1.0
        
    if originY < 0:
        originY = 0.0
    elif originY > 1:
        originY = 1.0

    if cursorX < 0:
        cursorX = 0.0
    elif cursorX > 1:
        cursorX = 1.0
    
    if cursorY < 0:
        cursorY = 0.0
    elif cursorY > 1:
        cursorY = 1.0

    if originX < cursorX:
        leftSelectionEdge = originX
        rightSelectionEdge = cursorX
    else:
        leftSelectionEdge = cursorX
        rightSelectionEdge = originX

    if originY > cursorY:
        topSelectionEdge = originY
        bottomSelectionEdge = cursorY
    else:
        topSelectionEdge = cursorY
        bottomSelectionEdge = originY
  
    return topSelectionEdge,leftSelectionEdge,bottomSelectionEdge,rightSelectionEdge
    
def terrainImportInfo(cellSize,terrainResolution,topSelectionEdge,leftSelectionEdge,bottomSelectionEdge,rightSelectionEdge):
    copyTopEdge = False
    copyRightEdge = False
    
    if isnan(topSelectionEdge):
        topSelectionEdge = 0.0
    if isnan(leftSelectionEdge):
        leftSelectionEdge = 0.0

    if topSelectionEdge == 1.0:
        topLeftRow = 0
        copyTopEdge = True
    else:
        topLeftRow = floor((1 - topSelectionEdge) * terrainResolution)
        
    topLeftColumn = ceil(leftSelectionEdge * terrainResolution)
    
    if bottomSelectionEdge == 0.0:
        bottomRightRow = terrainResolution - 1
    else:
        bottomRightRow = floor((1 - bottomSelectionEdge) * terrainResolution) - 1
        
    if rightSelectionEdge == 1.0:
         bottomRightColumn = terrainResolution - 1
         copyRightEdge = True
    else:
        bottomRightColumn = ceil(rightSelectionEdge * terrainResolution) - 1
        
    gridResX = bottomRightColumn - topLeftColumn + 2 if copyRightEdge else bottomRightColumn - topLeftColumn + 1
    gridResY = bottomRightRow - topLeftRow + 2 if copyTopEdge else bottomRightRow - topLeftRow + 1
        
    return topLeftRow, topLeftColumn, bottomRightRow, bottomRightColumn, copyTopEdge, copyRightEdge, gridResX, gridResY
    
def prepareHeightfield(dataPath,terrainResolution,topLeftRow,topLeftColumn,bottomRightRow,bottomRightColumn,copyTopEdge,copyRightEdge):
    print(' Heightfield preparation started {}'.format(time.ctime()))
    heightField = fromfile(dataPath, dtype=float32)
    heightField2D = reshape(heightField,(terrainResolution,terrainResolution))
    heightField = heightField2D[topLeftRow:bottomRightRow + 1,topLeftColumn:bottomRightColumn + 1]
    
    if copyTopEdge and copyRightEdge:
        copiedTopEdge = heightField[0]
        heightField = vstack((copiedTopEdge,heightField))
        copiedRightEdge = heightField[:,[-1]]
        heightField = hstack((heightField,copiedRightEdge))
    else:
        if copyTopEdge:
            copiedTopEdge = heightField[0]
            heightField = vstack((copiedTopEdge,heightField))
        if copyRightEdge:
            copiedRightEdge = heightField[:,[-1]]
            heightField = hstack((heightField,copiedRightEdge))
    print(' Heightfield preparation finished {}'.format(time.ctime()))
    return heightField

def getUVmapInfo(textureUVcellsizeMap,terrainUVcellsizeMap,topLeftColumn,topLeftRowChanged,topLeftPixelX,topLeftPixelY,locTextureResolutionX,locTextureResolutionY):
    uvShiftXMap = terrainUVcellsizeMap * topLeftColumn - textureUVcellsizeMap * topLeftPixelX
    uvShiftYMap = terrainUVcellsizeMap * topLeftRowChanged - textureUVcellsizeMap * topLeftPixelY
    print(' Pixel edge to vertex distance: ', uvShiftXMap,uvShiftYMap)
    vertexFromEdgeShiftX = 1 / textureUVcellsizeMap * uvShiftXMap
    vertexFromEdgeShiftY = 1 / textureUVcellsizeMap * uvShiftYMap
    print(' Vertex from pixel shift: ', vertexFromEdgeShiftX,vertexFromEdgeShiftY)
    
    uvStartX = 1 / locTextureResolutionX * vertexFromEdgeShiftX
    uvStartY = 1 - (1 / locTextureResolutionY * vertexFromEdgeShiftY)
    print(' uvStart at: ', uvStartX, uvStartY)
    
    terrainUVcellsizeLocX = (terrainUVcellsizeMap / textureUVcellsizeMap) * (1 / locTextureResolutionX)
    terrainUVcellsizeLocY = (terrainUVcellsizeMap / textureUVcellsizeMap) * (1 / locTextureResolutionY)
    print(' terrainUVcellsizeLoc: ', terrainUVcellsizeLocX, terrainUVcellsizeLocY)
    return uvStartX, uvStartY, terrainUVcellsizeLocX, terrainUVcellsizeLocY

def mergeTerrain(originalHeightField, heightField2D, mergePosition):
    originalHeightField[mergePosition[0]:mergePosition[0] + heightField2D.shape[0], mergePosition[1]:mergePosition[1] + heightField2D.shape[1]] = heightField2D
    return originalHeightField
    
def exportTerrain(overwriteSource):
    print('\nbLT_Info: Heightmap export started ', time.ctime())
    defaultProperties = bpy.data.scenes['Default_Location']
    binaryElevationPath = defaultProperties.bLTElevationPath
    ProjFolderPath = defaultProperties.ProjFolderPath
    terrainResolution,xllcorner,yllcorner,cellSize = defaultProperties["TerrainResolution"],defaultProperties["xllcorner"],defaultProperties["yllcorner"],defaultProperties["CellSize"]
    originalHeightField1D = fromfile(binaryElevationPath,dtype=float32)
    originalHeightField2D = originalHeightField1D.reshape((terrainResolution,terrainResolution))
    
    locationName = bpy.context.scene.name
    terrainObject = bpy.data.objects.get('Terrain_{}'.format(locationName))
    wMatrix = terrainObject.matrix_world
    
    heightField1D = []
    for v in terrainObject.data.vertices:
        worldCoord = wMatrix * v.co
        heightField1D.append(round(worldCoord[2],2))
    
    heightField2D = array(heightField1D).reshape(terrainObject["GridResY"],terrainObject["GridResX"])
    
    if terrainObject['TopEdgeAdded']:
        heightField2D = delete(heightField2D,0,0)
    if terrainObject['RightEdgeAdded']:
        heightField2D = delete(heightField2D,-1,1)
    
    mergedElevation = mergeTerrain(originalHeightField2D, heightField2D, [terrainObject["MergeRow"],terrainObject["MergeCol"]])
    mergedElevation.astype('float32').tofile(binaryElevationPath)
    if overwriteSource:
        outputPath = defaultProperties.ImportTerrainHeightmapPath
    else:
        outputPath = '{}\\Output\\elevation.asc'.format(ProjFolderPath)
    header = 'ncols         {}\nnrows         {}\nxllcorner     {}\nyllcorner     {}\ncellsize      {}\nNODATA_value  -9999'.format(terrainResolution,terrainResolution,xllcorner,yllcorner,cellSize)
    savetxt(outputPath,mergedElevation,fmt='%.2f',delimiter=' ',comments='',header=header)
    print(' bLT_Info: Shaded terrain preview regeneration started ', time.ctime())
    updateterrainpreview(outputPath)
    print(' bLT_Info: Shaded terrain preview regeneration finished ', time.ctime())
    print('bLT_Info: Heightmap export finished ', time.ctime())
    
def exportSurfaceMask(overwriteSource):
    terrainSurfaceMaskPath = bpy.data.scenes["Default_Location"].ImportTerrainSurfaceMaskPath
    if bpy.context.scene.SurfaceMaskFormatValid:
        print('\nbLT_Info: Surface map export started ', time.ctime())
        from cv2 import imread, imwrite, IMREAD_COLOR
        ProjFolderPath = bpy.data.scenes["Default_Location"].ProjFolderPath
        locationName = bpy.context.scene.name
        sourceSurfaceMask = imread(bpy.data.scenes["Default_Location"].ImportTerrainSurfaceMaskPath, IMREAD_COLOR)
        locationSurfaceMask = imread(r'{}ProjectData\Textures\TerrainMask_{}.png'.format(ProjFolderPath,locationName), IMREAD_COLOR)
        terrainObject = bpy.data.objects.get('Terrain_{}'.format(locationName))
        sourceSurfaceMask[terrainObject['MergeTopLeftY']:terrainObject["MergeBottomRightY"],terrainObject["MergeTopLeftX"]:terrainObject["MergeBottomRightX"]] = locationSurfaceMask
        if overwriteSource:
            outputPath = terrainSurfaceMaskPath
        else:
            outputPath = '{}Output\\surfaceMask.png'.format(ProjFolderPath)
        imwrite(outputPath, sourceSurfaceMask)
        print('bLT_Info: Surface map export finished ', time.ctime())
        bLTLogger('Scs','{} saved successfully.'.format(outputPath))
    else:
        print('\nbLT_Info:No surface map data exported!!! Source surface mask path not defined in Data Sources panel.')
        bLTLogger('Err','No surface map data exported!!! Source surface mask path not defined in Data Sources panel.')
    
    
def createOccupiedLocation(locationName,topLeftRow,topLeftColumn,bottomRightRow,bottomRightColumn,copyTopEdge,copyRightEdge):
    worldInfo = bpy.data.scenes['Default_Location']
    terrainResolution = worldInfo["TerrainResolution"]
    cellSize = worldInfo["CellSize"]
    
    occupiedLocationLayer = bpy.data.grease_pencil["OccupiedLocations"].layers.new(locationName)
    newFrame = occupiedLocationLayer.frames.new(0)
    newStroke = newFrame.strokes.new('newStroke')
    newStroke.colorname = 'Color'
    newStroke.draw_mode = '2DSPACE'
    
    mapSize = terrainResolution * cellSize
    
    topLeftX = (topLeftColumn * cellSize) / mapSize
    topLeftY = 1 if copyTopEdge else 1 - ((topLeftRow + 1) * cellSize / mapSize)
    bottomRightX = 1 if copyRightEdge else (bottomRightColumn * cellSize) / mapSize
    bottomRightY = 1 - ((bottomRightRow + 1) * cellSize / mapSize)
    
    
    newStroke.points.add()
    newStroke.points[0].co = Vector((topLeftX,topLeftY,0))
    newStroke.points.add()
    newStroke.points[1].co = Vector((topLeftX,bottomRightY,0))
    newStroke.points.add()
    newStroke.points[2].co = Vector((bottomRightX,bottomRightY,0))
    newStroke.points.add()
    newStroke.points[3].co = Vector((bottomRightX,topLeftY,0))
    
def createSeaSurface(locationName,terrainObject):
    bpy.ops.mesh.primitive_plane_add(radius=1.0, location=(terrainObject.location[0], terrainObject.location[1], 0.0))
    seaSurface = bpy.context.active_object
    seaSurface.dimensions = terrainObject.dimensions
    seaSurface.name = 'WaterSurface_' + locationName
    #-------------------------- Create new sea material ----------------------------------------------
    seaMaterial = bpy.data.materials.new('SeaMaterial_{}'.format(locationName))
    seaMaterial.diffuse_color = .009, .08, .036
    seaMaterial.specular_intensity = 0
    seaMaterial.use_transparency = True
    if bpy.context.scene.hasSea:
        seaMaterial.alpha = .5
        bLTLogger('Wrn','   Below sea level elevation detected, water surface mesh added!')
    else: 
        seaMaterial.alpha = .0
    bpy.ops.object.material_slot_add()
    seaSurface.material_slots[0].material = seaMaterial
    seaSurface.show_transparent = True
    seaSurface.select = False
    seaSurface.hide_select = True
    
    
def createNewLocation(locationName,gridResX,gridResY,topLeftRow,topLeftColumn,bottomRightRow,bottomRightColumn,copyTopEdge,copyRightEdge):
    worldInfo = bpy.data.scenes['Default_Location']
    terrainResolution = worldInfo["TerrainResolution"]
    cellSize = worldInfo["CellSize"]
    elevationPath = bpy.data.scenes['Default_Location'].bLTElevationPath
    terrainTexturePath = bpy.data.scenes["Default_Location"].ImportTerrainTexturePath
    terrainSurfaceMaskPath = bpy.data.scenes["Default_Location"].ImportTerrainSurfaceMaskPath
    ProjFolderPath = bpy.data.scenes["Default_Location"].ProjFolderPath

    bpy.context.window.screen.scene = bpy.data.scenes["Default_Location"]
    bpy.ops.scene.new(type='FULL_COPY')
    bpy.context.scene.name = locationName
    bpy.context.scene['isLocation'] = True
    
    
    if bpy.data.meshes.get('TerrainMesh_{}'.format(locationName)) is not None:
        bpy.data.meshes.get('TerrainMesh_{}'.format(locationName)).user_clear()
        bpy.data.meshes.remove(bpy.data.meshes.get('TerrainMesh_{}'.format(locationName)))

    terrainMesh = bpy.data.meshes.new('TerrainMesh_{}'.format(locationName))
    terrainObject = bpy.data.objects.new('Terrain_{}'.format(locationName),terrainMesh)
    bpy.context.scene.objects.link(terrainObject)
    terrainObject.select=True
    bpy.context.scene.objects.active = terrainObject
    
    contextCopy = bpy.context.area
    print('\nbLT_Info: Location creation started ', time.ctime())
    bLTLogger('Inf','Location \'{}\' import in progress...'.format(locationName))
    if bpy.context.scene.TerrainTextureFormatValid:
        imageryResolution = worldInfo["ImageryResolution"]
        
        textureUVcellsizeMap = 1 / imageryResolution
        terrainUVcellsizeMap = 1 / terrainResolution
        print(' UVCellTexture: ', textureUVcellsizeMap)
        print(' UVCellTerrain: ', terrainUVcellsizeMap)
        
        topLeftRowChanged = topLeftRow
        bottomRightColumnChanged = bottomRightColumn
        bottomRightRowChanged = bottomRightRow
        
        if not copyTopEdge:
            topLeftRowChanged += 1
            
        bottomRightRowChanged += 1     
            
        
        topLeftPixelX = floor(topLeftColumn * terrainUVcellsizeMap / textureUVcellsizeMap)
        topLeftPixelY = floor(round(topLeftRowChanged * terrainUVcellsizeMap / textureUVcellsizeMap,6))

        if copyRightEdge:
            bottomRightColumnChanged += 1
        
        bottomRightPixelX = ceil(bottomRightColumnChanged * terrainUVcellsizeMap / textureUVcellsizeMap)
        bottomRightPixelY = ceil(round(bottomRightRowChanged * terrainUVcellsizeMap / textureUVcellsizeMap,6))
        
        locTextureResolutionX = bottomRightPixelX - topLeftPixelX
        locTextureResolutionY = bottomRightPixelY - topLeftPixelY
         
        print(' Texture starts at: ', topLeftPixelX, topLeftPixelY)
        print(' Texture ends at: ', bottomRightPixelX, bottomRightPixelY)
        print(' Terrain texture resolution: ', locTextureResolutionX,locTextureResolutionY)
        
        from cv2 import imread, imwrite, IMREAD_COLOR
        print(' Location\'s terrain texture extraction started ', time.ctime())
        input_image_cv = imread(terrainTexturePath, IMREAD_COLOR)
        locationTexture = input_image_cv[topLeftPixelY:bottomRightPixelY,topLeftPixelX:bottomRightPixelX]
        imwrite(r'{}ProjectData\Textures\TerrainImage_{}.png'.format(ProjFolderPath,locationName), locationTexture)
        print(' Location\'s terrain texture extraction finished ', time.ctime())
        bLTLogger('Scs','   Terrain texture extracted to {}ProjectData\Textures\TerrainImage_{}.png'.format(ProjFolderPath,locationName))
        terrainTexture= bpy.data.textures.new('TerrainTexture_{}'.format(locationName), type = 'IMAGE')
        terrainTexture.image = bpy.data.images.load('{}ProjectData\\Textures\\TerrainImage_{}.png'.format(ProjFolderPath,locationName))
        
        if bpy.context.scene.SurfaceMaskFormatValid:
            print(' Location\'s surface mask extraction started ', time.ctime())
            input_image_cv = imread(terrainSurfaceMaskPath, IMREAD_COLOR)
            locationSurfaceMask = input_image_cv[topLeftPixelY:bottomRightPixelY,topLeftPixelX:bottomRightPixelX]
            imwrite(r'{}ProjectData\Textures\TerrainMask_{}.png'.format(ProjFolderPath,locationName), locationSurfaceMask)
            print(' Location\'s surface mask extraction finished ', time.ctime())
            bLTLogger('Scs','   Surface mask extracted to {}ProjectData\Textures\TerrainMask_{}.png'.format(ProjFolderPath,locationName))
            
            terrainMask= bpy.data.textures.new('TerrainMask_{}'.format(locationName), type = 'IMAGE')
            terrainMask.image = bpy.data.images.load('{}ProjectData\\Textures\\TerrainMask_{}.png'.format(ProjFolderPath,locationName))
        
    
        #-------------------------- Create new terrain material ----------------------------------------------
        terrainMaterial = bpy.data.materials.new('TerrainMaterial_{}'.format(locationName))
        terrainMaterial.specular_intensity = 0
        terrainMaterial.texture_slots.add()
        
        textureSlot = terrainMaterial.texture_slots[0]
        textureSlot.texture = terrainTexture
        textureSlot.texture_coords = 'UV'
        
        if bpy.context.scene.SurfaceMaskFormatValid:
            terrainMaterial.texture_slots.add()
            textureSlot = terrainMaterial.texture_slots[1]
            textureSlot.texture = terrainMask
            textureSlot.texture_coords = 'UV'
            textureSlot.diffuse_color_factor = .5
            terrainMaterial.use_textures[1] = False
            terrainMaterial.paint_active_slot = 1
        
        bpy.ops.object.material_slot_add()
        bpy.data.objects['Terrain_{}'.format(locationName)].material_slots[0].material = terrainMaterial  
    
    bm = bmesh.new() 
    bm.from_mesh(terrainMesh)
    
    if bpy.context.scene.TerrainTextureFormatValid:
        tex_layer = bm.faces.layers.tex.verify()
        uv_layer = bm.loops.layers.uv.verify()
        
    terrainZvalues = prepareHeightfield(elevationPath,terrainResolution,topLeftRow,topLeftColumn,bottomRightRow,bottomRightColumn,copyTopEdge,copyRightEdge)
    terrainTopLeftStartX = topLeftColumn * cellSize
    if copyTopEdge:
        terrainDimensionY = terrainResolution * cellSize
    else:
        terrainDimensionY = (terrainResolution - 1)  * cellSize
    
    print(' Terrain mesh/UVs generation started ', time.ctime())
    terrainTopLeftStartY = terrainDimensionY - (topLeftRow * cellSize)
    
    for row in range(gridResY):
        heightArray = terrainZvalues[row]
        for col in range(gridResX):
            if heightArray[col] < 0: bpy.context.scene.hasSea = True
            bm.verts.new((terrainTopLeftStartX,terrainTopLeftStartY,heightArray[col]))
            terrainTopLeftStartX += cellSize
        terrainTopLeftStartX = topLeftColumn * cellSize
        terrainTopLeftStartY -= cellSize
    bm.verts.ensure_lookup_table()
    
    if bpy.context.scene.TerrainTextureFormatValid:
        uvStartX, uvStartY, terrainUVcellsizeLocX, terrainUVcellsizeLocY = getUVmapInfo(textureUVcellsizeMap,terrainUVcellsizeMap,topLeftColumn,topLeftRowChanged,topLeftPixelX,topLeftPixelY,locTextureResolutionX,locTextureResolutionY)
    uvShiftY = 0
    for rowOfset in range(0,gridResX * (gridResY - 1), gridResX):
        for cellID in range (0, gridResX - 1):
            vertID = rowOfset + cellID
            face = [bm.verts[vertID],bm.verts[vertID + gridResX],bm.verts[vertID + gridResX + 1],bm.verts[vertID + 1]]
            currentFace = bm.faces.new(face)
            
            if bpy.context.scene.TerrainTextureFormatValid:
                currentFace[tex_layer].image = bpy.data.images['TerrainImage_{}.png'.format(locationName)]
                currentFace.loops[0][uv_layer].uv = [uvStartX + cellID * terrainUVcellsizeLocX, uvStartY - uvShiftY * terrainUVcellsizeLocY]
                currentFace.loops[1][uv_layer].uv = [uvStartX + cellID * terrainUVcellsizeLocX, uvStartY - uvShiftY * terrainUVcellsizeLocY - terrainUVcellsizeLocY]
                currentFace.loops[2][uv_layer].uv = [uvStartX + cellID * terrainUVcellsizeLocX + terrainUVcellsizeLocX, uvStartY - uvShiftY * terrainUVcellsizeLocY - terrainUVcellsizeLocY]
                currentFace.loops[3][uv_layer].uv = [uvStartX + cellID * terrainUVcellsizeLocX + terrainUVcellsizeLocX, uvStartY - uvShiftY * terrainUVcellsizeLocY]
        uvShiftY += 1
        
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=2)
    bm.to_mesh(terrainMesh)
    bm.free()
    print(' Terrain mesh/UVs generation finished ', time.ctime())
    
    
    terrainObject["MergeRow"] = topLeftRow
    terrainObject["MergeCol"] = topLeftColumn
    terrainObject["GridResX"] = gridResX
    terrainObject["GridResY"] = gridResY
    terrainObject["TopEdgeAdded"] = copyTopEdge
    terrainObject["RightEdgeAdded"] = copyRightEdge
    if bpy.context.scene.SurfaceMaskFormatValid:
        terrainObject["MergeTopLeftY"] = topLeftPixelY
        terrainObject["MergeTopLeftX"] = topLeftPixelX
        terrainObject["MergeBottomRightY"] = bottomRightPixelY
        terrainObject["MergeBottomRightX"] = bottomRightPixelX
    terrainObject.lock_location = True,True,True
    terrainObject.lock_rotation = True,True,True
    terrainObject.lock_scale = True,True,True
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    
    print('bLT_Info: Location creation finished {}\n'.format(time.ctime()))
    contextCopy.type = 'VIEW_3D'
    screen = bpy.context.window.screen
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'window': bpy.context.window, 'screen': screen, 'area': area, 'region': region, 'scene': bpy.context.scene, 'edit_object': bpy.context.edit_object}
    
    bpy.ops.view3d.view_selected(override)
    bLTLogger('Scs','   Terrain mesh/UV coordinates created.')
    
    setupLocationAppearance(locationName, hasMaterial = True if bpy.context.scene.TerrainTextureFormatValid else False)
    
    terrainObject.select = False
    terrainObject.hide_select = True
    
    createSeaSurface(locationName,terrainObject)
    
def assignMeshTerrainModifier(context):
    activeObject = context.active_object
    modifierSize = activeObject.dupli_group['Dimension']
    bpy.ops.mesh.primitive_plane_add(radius=modifierSize / 2 + (modifierSize * .1), location=activeObject.location, rotation=(0.0,0.0,activeObject.rotation_euler[2]))
    
    modifierObject = context.active_object
    modifierObject.show_x_ray = True
    modifierObject.draw_type = 'WIRE'
    modifierObject.name = 'Flatter_{}'.format(activeObject.name)
    
    activeObject.select = True
    bpy.context.scene.objects.active = activeObject
    bpy.ops.object.parent_set(type='OBJECT')
    
    terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
    flatterModifier = terrainObject.modifiers.new(modifierObject.name, 'SHRINKWRAP')
    flatterModifier.target = modifierObject
    flatterModifier.wrap_method = 'PROJECT'
    flatterModifier.use_project_z = True
    flatterModifier.use_negative_direction = True
    
    activeObject.select = False
    bpy.context.scene.objects.active = modifierObject
    
def addMeshTerrainModifier(context):
    bpy.ops.object.select_all(action='DESELECT')
    Areas = bpy.context.screen.areas
    for Area in Areas:
        if Area.type == 'VIEW_3D':
            cursorLocation = Area.spaces.active.cursor_location
    bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1.0, location=cursorLocation)
    emptyObject = context.active_object
    emptyObject.lock_scale = True,True,True
    emptyObject.show_x_ray = True
    emptyObject.empty_draw_size = 50
    emptyObject.name = "M_T_M"
    
    bpy.ops.mesh.primitive_plane_add(radius=context.scene['CellSize'] * 1.5, location=cursorLocation)
    modifierObject = context.active_object
    modifierObject.show_x_ray = True
    modifierObject.draw_type = 'WIRE'
    modifierObject.name = 'Flatter_{}'.format(emptyObject.name)
    
    emptyObject.select = True
    bpy.context.scene.objects.active = emptyObject
    bpy.ops.object.parent_set(type='OBJECT')
    
    terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
    flatterModifier = terrainObject.modifiers.new(modifierObject.name, 'SHRINKWRAP')
    flatterModifier.target = modifierObject
    flatterModifier.wrap_method = 'PROJECT'
    flatterModifier.use_project_z = True
    flatterModifier.use_negative_direction = True
    
    emptyObject.select = False
    bpy.context.scene.objects.active = modifierObject
  
def applyMeshTerrainModifier(context):
    selectedObjects = bpy.context.selected_objects
    
    terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
    bpy.context.scene.objects.active = terrainObject
    
    for selectedObject in selectedObjects:
        bpy.ops.object.modifier_apply(modifier=selectedObject.children[0].name)
        context.scene.objects.unlink(selectedObject.children[0])
        selectedObject.children[0].user_clear()
        bpy.data.objects.remove(selectedObject.children[0])
        if selectedObject.dupli_group is None:
            context.scene.objects.unlink(selectedObject)
            selectedObject.user_clear()
            bpy.data.objects.remove(selectedObject)        
            
def addSplineTerrainModifier(context):
    bpy.ops.object.select_all(action='DESELECT')
    Areas = bpy.context.screen.areas
    for Area in Areas:
        if Area.type == 'VIEW_3D':
            cursorLocation = Area.spaces.active.cursor_location
    
    splineData = bpy.data.curves.new('TerrainModifierSpline',"CURVE")
    splineData.splines.new("BEZIER")
    splineData.dimensions = '3D'
    splineTerrainModifier = bpy.data.objects.new("S_T_M", splineData)
    splineTerrainModifier.lock_scale = True,True,True
    splineTerrainModifier.show_x_ray = True
    splineData.splines[0].bezier_points[0].co.x = 0
    splineData.splines[0].bezier_points[0].co.y = 0
    splineData.splines[0].bezier_points[0].handle_right_type = 'ALIGNED'
    splineData.splines[0].bezier_points[0].handle_left_type = 'ALIGNED'
    splineData.splines[0].bezier_points[0].handle_left = 0,-20,0    
    splineData.splines[0].bezier_points[0].handle_right = 0,20,0
    splineData.splines[0].bezier_points.add(1)
    splineData.splines[0].bezier_points[1].co.x = 0
    splineData.splines[0].bezier_points[1].co.y = 80
    splineData.splines[0].bezier_points[1].handle_right_type = 'ALIGNED'
    splineData.splines[0].bezier_points[1].handle_left_type = 'ALIGNED'
    splineData.splines[0].bezier_points[1].handle_left = 0,60,0
    splineData.splines[0].bezier_points[1].handle_right = 0,100,0
    splineData.splines[0].resolution_u = 20
    splineData.twist_mode = 'Z_UP'
    bpy.context.scene.objects.link(splineTerrainModifier)
    splineTerrainModifier['FlatterWidth'] = context.scene['CellSize'] * 3
    
    bpy.ops.mesh.primitive_plane_add(radius= .5, location=(.5,0,0))
    modifierObject = context.active_object
        
    modifierObject.scale.y = splineTerrainModifier['FlatterWidth']
    modifierObject.name = 'Flatter_{}'.format(splineTerrainModifier.name)
    modifierObject.draw_type = 'WIRE'
    modifierObject.hide_select = True
    
    arrayModifier = modifierObject.modifiers.new('Array', 'ARRAY')
    arrayModifier.fit_type = 'FIT_CURVE'
    arrayModifier.curve = splineTerrainModifier
    
    curveModifier = modifierObject.modifiers.new('Curve', 'CURVE')
    curveModifier.object = splineTerrainModifier
    
    splineTerrainModifier.select = True
    bpy.context.scene.objects.active = splineTerrainModifier
    bpy.ops.object.parent_set(type='OBJECT')
    splineTerrainModifier.location = cursorLocation
    
    modifierObject.select = False
    
    terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
    flatterModifier = terrainObject.modifiers.new(modifierObject.name, 'SHRINKWRAP')
    flatterModifier.target = modifierObject
    flatterModifier.wrap_method = 'PROJECT'
    flatterModifier.use_project_z = True
    flatterModifier.use_negative_direction = True

def applySplineTerrainModifier(context):
    selectedObjects = bpy.context.selected_objects
    
    terrainObject = bpy.data.objects['Terrain_' + context.scene.name]
    bpy.context.scene.objects.active = terrainObject
   
    for obj in selectedObjects:
        bpy.ops.object.modifier_apply(modifier=obj.children[0].name)
        context.scene.objects.unlink(obj.children[0])
        context.scene.objects.unlink(obj)
        obj.children[0].user_clear()
        obj.user_clear()
        bpy.data.objects.remove(obj.children[0])
        bpy.data.objects.remove(obj)

def createFlatTerrain(cellSize,gridResolution,defaultElevation):
    OutputPath = bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.OutputPath
    if OutputPath != '':
        result = ones((gridResolution,gridResolution)) * defaultElevation
        header = 'ncols         {}\nnrows         {}\nxllcorner     0\nyllcorner     0\ncellsize      {}\nNODATA_value  -9999'.format(gridResolution,gridResolution,cellSize) 
        savetxt('{}\\elevation.asc'.format(OutputPath),result,fmt='%.2f',delimiter=' ',newline='\r\n',comments='',header=header)
        print('Elevation file saved to {}\\elevation.asc'.format(OutputPath))
        bLTLogger('Scs','{} saved successfully.'.format('{}\elevation.asc'.format(OutputPath)))
    
def createSurfaceMask(imageResolution,defaultColor):
    OutputPath = bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.OutputPath
    if OutputPath != '':
        from cv2 import imwrite
        blank_image = zeros((imageResolution,imageResolution,3), uint8)
        blank_image[:,:,0] = ones([imageResolution,imageResolution]) * defaultColor[2] * 255
        blank_image[:,:,1] = ones([imageResolution,imageResolution]) * defaultColor[1] * 255
        blank_image[:,:,2] = ones([imageResolution,imageResolution]) * defaultColor[0] * 255
        imwrite('{}\\surface_mask.png'.format(OutputPath), blank_image)
        print('Surface mask file saved to {}\\surface_mask.png'.format(OutputPath))
        bLTLogger('Scs','{} saved successfully.'.format('{}\surface_mask.png'.format(OutputPath)))
        
def update_checksurfacemaskpath(self, context):
    SurfaceMaskPath = context.scene.CheckSurfaceMaskPath
    
    if SurfaceMaskPath != '':
        if SurfaceMaskPath.split('.')[-1] in ['png','tif','tiff','PNG','TIF','TIFF']:
            context.scene.CheckSurfaceMaskFormatValid = True
        else:
            context.scene.CheckSurfaceMaskFormatValid = False
            print('\nbLT_Info: {} is unsupported surface mask file format! Use PNG, TIF, TIFF instead.'.format(SurfaceMaskPath.split('.')[-1]))
    else:
        context.scene.CheckSurfaceMaskFormatValid = False
        
def update_checksurfacesdefinitionpath(self, context):
    surfacesDefinitionPath = context.scene.CheckSurfacesDefinitionPath
    
    if surfacesDefinitionPath != '':
        if surfacesDefinitionPath.split('.')[-1] == 'cfg':
            context.scene.CheckSurfacesDefinitionFormatValid = True
        else:
            context.scene.CheckSurfacesDefinitionFormatValid = False
    else:
        context.scene.CheckSurfacesDefinitionFormatValid = False

def checkSurfaceMask(context,cellSize,gridResolution,tileSize):




    def calculateOverlap(m23,m24,m25,m26):
        def m1( x ):
            return floor(x + 0.5)

        def m2( x, i ):
            return (abs( x - i ) < 0.000001)

        m3 = m23 * m24  
        m4 = 1
        m5 = 1000000
        m6 = -1
        for i in range(0,8):
            m7 = m4 * m23
            m8 = abs(40.0 - m7)
            if m8 < m5:
                m5 = m8
                m6 = m4
            m4 *= 2

        m9 = m6
        #land grid cell size or _landGrid
        m10 = m9 * m23
        #land grid size or _landRange
        m11 = floor( m3 / m10 )
        #terrain grid size or _terrainRange
        m12 = m9 * m11
        #final terrain size
        m13 = m14 = m12 * m23
        m15 = 16
        m16 = m25 - m15
        m17 = m26 * m16
        m18 = floor( m17 / m10 )
        m18 -= m18 % 4
        m19 = m18 * m10
        m20 = m19 / m26
        m21 = m25 - m20
        m22 = ceil( m13 / m19 )
        return m21, m22
    
    def genColoredGrid(maskWidth,actualTileSize):
        rgb = zeros((maskWidth,maskWidth,3), uint8)
        white = ones((actualTileSize,actualTileSize,1), uint8) * 255
        switch = False
        for i in range(0,maskWidth,actualTileSize):
            for j in range(0,maskWidth,actualTileSize):
                if switch:
                    if rgb[i:i + actualTileSize,j:j + actualTileSize,0].shape == white[:,:,0].shape:
                        rgb[i:i + actualTileSize,j:j + actualTileSize,0]  = white[:,:,0]
                    else:
                        shape = rgb[i:i + actualTileSize,j:j + actualTileSize,0].shape
                        rgb[i:i + actualTileSize,j:j + actualTileSize,0]  = white[0:shape[0],0:shape[1],0]
                else:
                    if rgb[i:i + actualTileSize,j:j + actualTileSize,1].shape == white[:,:,0].shape:
                        rgb[i:i + actualTileSize,j:j + actualTileSize,1]  = white[:,:,0]
                    else:
                        shape = rgb[i:i + actualTileSize,j:j + actualTileSize,1].shape
                        rgb[i:i + actualTileSize,j:j + actualTileSize,1]  = white[0:shape[0],0:shape[1],0]
                switch = not switch
            switch = not switch if (maskWidth / actualTileSize) % 2 == 0 else switch
        return rgb
        
    from cv2 import imread, imwrite, merge, rectangle, putText, line, FONT_HERSHEY_DUPLEX
    
    surfaceMask = imread(context.scene.CheckSurfaceMaskPath,1)
    validRGBValues = parseLayersCfg(context.scene.CheckSurfacesDefinitionPath)[-1]
    maskResolution = (cellSize * gridResolution) / surfaceMask.shape[0]
    
    tileOverlap, tilesInRow = calculateOverlap(cellSize,gridResolution,tileSize,maskResolution)
    maskWidth = int((cellSize * gridResolution) / maskResolution)
    
    actualTileSize = int(tileSize - tileOverlap)
    lastTileMatches = False if maskWidth != actualTileSize * tilesInRow else True
    
    
    alpha = zeros((maskWidth,maskWidth,1), uint8)
    colorGrid = genColoredGrid(maskWidth,actualTileSize)
    invalidRGBMask = zeros((maskWidth,maskWidth,1), uint8)
    invalidRGBsGlobal = 0
    print(actualTileSize,tilesInRow,lastTileMatches)
    tileCounter = 0
    for tileX in range(0,tilesInRow):
        for tileY in range(0,tilesInRow):
            print(tileX,tileY)
            if tileX == tilesInRow - 1:
                tileTexRangeX = actualTileSize if lastTileMatches else actualTileSize - (actualTileSize * tilesInRow - maskWidth)
            else:
                tileTexRangeX = actualTileSize
            if tileY == tilesInRow - 1:
                tileTexRangeY = actualTileSize if lastTileMatches else actualTileSize - (actualTileSize * tilesInRow - maskWidth)
            else:
                tileTexRangeY = actualTileSize
            tile = surfaceMask[tileY * actualTileSize: (tileY * actualTileSize) + tileTexRangeY,tileX * actualTileSize: (tileX * actualTileSize) + tileTexRangeX]
            tileColorList = {}
            invalidRGBs = 0
            for k in range(0,tileTexRangeY):
                for l in range(0,tileTexRangeX):
                    b = tile.item(k,l,0)
                    g = tile.item(k,l,1)
                    r = tile.item(k,l,2)

                    if [r,g,b] in validRGBValues:
                        if (r,g,b) not in tileColorList:
                            tileColorList[(r,g,b)] = 1
                        else:
                            tileColorList[(r,g,b)] += 1
                    else:
                        invalidRGBs += 1
                        invalidRGBsGlobal += invalidRGBs
                        invalidRGBMask[tileY * actualTileSize + k,tileX * actualTileSize + l] = 255
            multiplier = 1
            for key, value in tileColorList.items():
                rectangle(colorGrid,((tileX * actualTileSize) + 20, (tileY * actualTileSize) + (20 * multiplier + 100)),((tileX * actualTileSize) + 50, (tileY * actualTileSize) + (20 * multiplier) + 120),(key[::-1]),-1)
                rectangle(alpha,((tileX * actualTileSize) + 20, (tileY * actualTileSize) + (20 * multiplier + 100)),((tileX * actualTileSize) + 50, (tileY * actualTileSize) + (20 * multiplier) + 120),(255),-1)
                putText(colorGrid, ' - {}'.format(value), ((tileX * actualTileSize) + 50, (tileY * actualTileSize) + (118 + (multiplier * 20))), FONT_HERSHEY_DUPLEX, .7, (255,255,255), 2)
                putText(alpha, ' - {}'.format(value), ((tileX * actualTileSize) + 50, (tileY * actualTileSize) + (118 + (multiplier * 20))), FONT_HERSHEY_DUPLEX, .7, (255), 2)
                multiplier += 1
            
            validRGBTextColor = (0,255,0) if len(tileColorList) < 7 else (0,0,255)
            putText(colorGrid, str(len(tileColorList)), (int((tileX * actualTileSize) + 2), int((tileY * actualTileSize) + 80)), FONT_HERSHEY_DUPLEX, 3, validRGBTextColor, 5)
            putText(alpha, str(len(tileColorList)), (int((tileX * actualTileSize) + 2), int((tileY * actualTileSize) + 80)), FONT_HERSHEY_DUPLEX, 3, (255), 5)
            
            invalidRGBTextColor = (0,255,0) if invalidRGBs == 0 else (0,0,255)
            putText(colorGrid, str(invalidRGBs), (int((tileX * actualTileSize) + 150), int((tileY * actualTileSize) + 80)), FONT_HERSHEY_DUPLEX, 3, invalidRGBTextColor, 5)
            putText(alpha, str(invalidRGBs), (int((tileX * actualTileSize) + 150), int((tileY * actualTileSize) + 80)), FONT_HERSHEY_DUPLEX, 3, (255), 5)
            
            tileCounter += 1
            bLTLogger('PgsUp','Tile {} of {} checked...'.format(tileCounter,tilesInRow * tilesInRow))          
    bLTLogger('PgsDn','All {} tiles checked. Saving results now.'.format(tilesInRow * tilesInRow))
    for i in range(0,tilesInRow):
        line(alpha,(i * actualTileSize,0),(i * actualTileSize,surfaceMask.shape[0]),(255),1)
        line(alpha,(i * actualTileSize + actualTileSize - 1,0),(i * actualTileSize + actualTileSize - 1,surfaceMask.shape[0]),(255),1)
        line(alpha,(0,i * actualTileSize),(surfaceMask.shape[0],i * actualTileSize),(255),1)
        line(alpha,(0,i * actualTileSize + actualTileSize - 1),(surfaceMask.shape[0],i * actualTileSize + actualTileSize - 1),(255),1)

    rgba = merge((colorGrid[:,:,0],colorGrid[:,:,1],colorGrid[:,:,2],alpha))
    OutputPath = bpy.context.user_preferences.addons["bLandscapeTools-master"].preferences.OutputPath
    imwrite('{}\surfacemask_check.png'.format(OutputPath),rgba)
    bLTLogger('Scs','{} saved successfully.'.format('{}surfacemask_check.png'.format(OutputPath)))
    if invalidRGBsGlobal != 0:
        imwrite('{}\invalidRGBMask.png'.format(OutputPath),invalidRGBMask)
        bLTLogger('Scs','{} saved successfully.'.format('{}invalidRGBMask.png'.format(OutputPath)))