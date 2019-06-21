#Cloth Weaver
#Author: Alexander Kane
#Version: 4.15
#Updated: 2018-5-1
#Copyright © 2018 XANDERAK, LLC

bl_info = {
        "name" : "Cloth Weaver",
        "category": "Learnbgame",
        "author": "XANDERAK, LLC",
        "blender": (2, 80, 0),
        "version":"4.1",
        "description":"Quickly sew clothing & apply fabrics to your models."
        }

from bpy.types import Scene,PropertyGroup
from bpy.props import StringProperty, EnumProperty 
import bpy
import atexit
import os
import webbrowser
from urllib import request
from bpy.types import Panel, Operator, EnumProperty, WindowManager, PropertyGroup

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
                    
import bpy.utils.previews



tmp = bpy.context.preferences.filepaths.temporary_directory + "CW-tmp/"
softwaretype = "IndividualSubscription"
productcode = "aIuh"
fipVvieq = 0
ioTeifj = 4.15
copyright = "Copyright © 2018 XANDERAK, LLC"
running = 0
epnVSLKa = ""
localdrive = 0
corefunctions = 0
editmodefunctions = 0
aFrTemnL = ""
previousdir = ""

versionstatus = "(You have the latest version!)"
fePnEzl = "no"
uPenlAepqn = "0"
BIlPds = "Mini-Market Offline"
epnkleE = 0
pNleNS = ""
stars = "0"
pub = ""
update = "never"
count = "0"
info = "N/A"
commercial = "No"
GjwQpts = "0"
puNLfnB = "0"
qEwupVB = ""
pNLvbUY = "empty"
EiUpWQ = "empty"
characterobj = "empty"
file = bpy.utils.script_path_user()
new = str(file)
new = new.replace("]","")
new = new.replace("[","")
new = new.replace("'","")
tsuOPEn = "/addons/learnbgame_ClothWeaver/cloth.blend"
enfjkwjpe = "/addons/learnbgame_ClothWeaver/"
blendfile = new + tsuOPEn
BunsLiGDF = new + enfjkwjpe
rig = "rig"
OmoshiNVB = ""
rhyJpSQ = ""
marketicon = ""
yPhKDEwq = 1
images = "/addons/learnbgame_ClothWeaver/preseticons/"
gallery = new + images
eoNsA = "/"
iPuTlN = "/"
tcategory = ""
placehold = ""
backups = []
eqPBSLGHDK = {}
customeqPBSLGHDK = {}
marketeqPBSLGHDK = {}
useMBL = 0
localcategory = ""

# Create a new preview collection (only upon register)
pcoll = bpy.utils.previews.new()

pcoll.images_location = gallery

# Enable access to our preview collection outside of this function
eqPBSLGHDK["thumbnail_previews"] = pcoll


###("Current Mini-Market Directory: '" + iPuTlN + "'")
marketgallery = bpy.utils.previews.new()
marketgallery.images_location = iPuTlN
marketeqPBSLGHDK["marketthumbnail_previews"] = marketgallery

customgallery = bpy.utils.previews.new()
customgallery.images_location = eoNsA
customeqPBSLGHDK["customthumbnail_previews"] = customgallery

def vkLpdDs(ctype):

    print("\n**Importing Clothing**")
    print("Clothing Selected = " + ctype)
    
    print("path=" + blendfile)
    
    section   = "\\Object\\"
    object    = ctype

    filepath  = blendfile + section + object
    directory = blendfile + section
    filename  = object

    bpy.ops.wm.append(filepath=filepath, filename=filename, directory=directory)
    #select newly imported object
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    if bpy.context.scene.cloth.MBL is True:
        bpy.context.object.scale[0] = 0.277
        bpy.context.object.scale[1] = 0.277
        bpy.context.object.scale[2] = 0.277

    print("append " + OmoshiNVB)
    return {"FINISHED"}

def bevtdvawq(ctype):

    print("\n**Importing custom items**")
    print("Clothing Selected = " + ctype)
    
    blenderfile = aFrTemnL.split("/")[1]
    
    print("path=" + eoNsA + aFrTemnL + "/" + blenderfile + ".blend")
    
    section   = "\\Object\\"
    object    = ctype
    userPreset = eoNsA + aFrTemnL + "/" + blenderfile + ".blend"

    filepath  = userPreset + section + object
    directory = userPreset + section
    filename  = object

    bpy.ops.wm.append(filepath=filepath, filename=filename, directory=directory)
    #select newly imported object
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    print("append " + ctype)
    return {"FINISHED"}

class CLOTH_PROPERTY(PropertyGroup):
    def eszJNlew():
        # We are accessing all of the information that we generated in the register function below
        pcoll = eqPBSLGHDK["thumbnail_previews"]
        image_location = pcoll.images_location
        VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg')
        
        enum_items = []
        
        # Generate the thumbnails
        for i, image in enumerate(os.listdir(image_location)):
            imagename = image.split(".")[0]
            if image.endswith(VALID_EXTENSIONS):
                filepath = os.path.join(image_location, image)
                thumb = pcoll.load(filepath, filepath, 'IMAGE')
                enum_items.append((image, image, imagename, thumb.icon_id, i))
        return enum_items


    def fPtpoJN():
        marketgallery = marketeqPBSLGHDK["marketthumbnail_previews"]
        image_location = marketgallery.images_location
        VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg')
        
        enum_items = []
        
        # Generate the thumbnails
        for i, image in enumerate(os.listdir(image_location)):
            imagename = image.split(".")[0]
            if image.endswith(VALID_EXTENSIONS):
                filepath = os.path.join(image_location, image)
                thumb = marketgallery.load(filepath, filepath, 'IMAGE')
                enum_items.append((image, image, imagename, thumb.icon_id, i))
                
        return enum_items

    def witNlp():
        customgallery = customeqPBSLGHDK["customthumbnail_previews"]
        image_location = customgallery.images_location
        VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg')
        
        enum_items = []
        
        # Generate the thumbnails
        try:  
            for i, image in enumerate(os.listdir(image_location)):
                imagename = image.split(".")[0]
                if image.endswith(VALID_EXTENSIONS):
                    filepath = os.path.join(image_location, image)
                    thumb = customgallery.load(filepath, filepath, 'IMAGE')
                    enum_items.append((image, image, imagename, thumb.icon_id, i))
        except:
            print("Can't generate custom previews. Does directory exist?")
                
        return enum_items

    # This is an EnumProperty to hold all of the images
    my_thumbnails : EnumProperty(
        items=eszJNlew(),
        )

    marketthumbnails : EnumProperty(
        items=fPtpoJN(),
        )
    customthumbnails : EnumProperty(
        items=witNlp(),
        )
    sewForces : FloatProperty(
        name = "Sewing Force",
        description = "Force when putting on clothing (Higher = stronger)",
        default = 2.00,
        min=0.01
        )
    massClothCustom : FloatProperty(
        name = "Mass",
        description = "Mass of Cloth",
        default = 0.3,
        min=0.01
        )
    stiffClothCustom : FloatProperty(
        name = "Stiffness",
        description = "Stiffness of Cloth",
        default = 5,
        min=0.01
        )
    bendClothCustom : FloatProperty(
        name = "Bending",
        description = "Bending/wrinkles (lower = many small wrinkles | higher = few bigger wrinkles, )",
        default = 0.1,
        min=0.01
        )
    LK : StringProperty(
        name = "Key",
        description = "Paste License Key"
        )
    EmailAddress : StringProperty(
        name = "Email",
        description = "Enter email address used for purchase"
        )
    customfile : StringProperty(
        name = "custom file",
        description = "Choose root a directory for housing Mini-Market items",
        default = eoNsA,
        subtype="DIR_PATH"
        )
    MBL : BoolProperty(
        name="use Avastar | Manuel Bastioni Lab",
        description="Checkmark if using Avastar or Manuel Bastioni LAB characters",
        default = False
        )
    IMVU : BoolProperty(
        name="use IMVU",
        description="Checkmark if using IMVU characters",
        default = False
        )



#---------------------------LINKS-----------------------------------
class CLOTH_OT_UPDATE(Operator):
    
    bl_idname = "updates.id"
    bl_label = "updates"
    bl_description = "Log in to your Gumroad Library to update Cloth Weaver"
    
    def execute(self, context):
        
        url = "https://gumroad.com/library"
        webbrowser.open_new_tab(url)
        
        return {"FINISHED"}
    
class CLOTH_OT_EDITHELP(Operator):
    
    bl_idname = "edithelp.id"
    bl_label = "edithelp"
    bl_description = "View tutorials for this section"
    
    def execute(self, context):
        
        url = "https://www.youtube.com/watch?v=N8kDPYJ71pI&list=PLY7tnlwiJ4ajoKx-x6FOid6520lSBaYBQ&index=4"
        webbrowser.open_new_tab(url)
        
        return {"FINISHED"}
    
class CLOTH_OT_CWHOME(Operator):
    
    bl_idname = "cwhome.id"
    bl_label = "cwhome"
    bl_description = "Visit ClothWeaver.com"
    
    def execute(self, context):
        
        url = "https://clothweaver.com"
        webbrowser.open_new_tab(url)
        
        return {"FINISHED"}
    
class CLOTH_OT_DEACTIVATE(Operator):
    bl_idname = "deactivate.id"
    bl_label = "deactivate"
    bl_description = "De-activate this install of Cloth Weaver. This will 'free up' a license slot allowing you to migrate to another computer."
    
    def execute(self, context):
        global running
        print("\n**De-activate Current Install**")
        keyfile = BunsLiGDF + "LKstore.txt"
        if os.path.isfile(keyfile): 
            currentKey = open(keyfile,"r")
            cKey = str(currentKey.readline().strip())
            ###(cKey)
            urlcw = "https://clothweaver.com/LK-Store/dLicense.php/"
            full_url = urlcw + '?LK=' + cKey + '&ST=' + softwaretype
            ###(full_url)
            response = request.urlopen(full_url)
            request_body = response.read()
            ###(request_body)
            running = 0
            
        else:
            print("can't find license key file")
        
        try:
            bpy.utils.unregister_module(__name__)
            bpy.utils.register_class(license)
            bpy.utils.register_class(NepYud)
        except ValueError as err:
            print("Can't unregister classes\n")
            print(err)
        
        return {"FINISHED"}
    
class CLOTH_OT_DOWNLOAD(Operator):
    bl_idname = "download.id"
    bl_label = "download"
    bl_description = "Download Package"
    
    def execute(self, context):
        global epnkleE
        global epnVSLKa
        tmpcategory = ""
        catdirect = ""
        #CHECK IF PAID ITEM & LOOKUP URL IN SPECIAL TXT FILE
        epnVSLKa = "Downloading..."
        if bpy.context.scene.cloth.customfile == "" or bpy.context.scene.cloth.customfile == "/":
            print("Please specify a directory to save to.")
            epnVSLKa = "ERROR: Please choose a save directory"
            epnkleE = 1
        elif os.path.exists(bpy.context.scene.cloth.customfile):
            if 'A!' in bpy.context.scene.cloth.marketthumbnails:
                tmpcategory = 'accessories'
            elif 'C!' in bpy.context.scene.cloth.marketthumbnails:
                tmpcategory = 'clothing'
            elif 'D!' in bpy.context.scene.cloth.marketthumbnails:
                tmpcategory = 'decor'
            
            catdirect = bpy.context.scene.cloth.customfile + tmpcategory + "/"
            
            if os.path.exists(catdirect):
                print("subDir exists at: " + catdirect)
            else:
                os.makedirs(catdirect)
                catimg = "c!" + tmpcategory + ".png"
                localimg = bpy.context.scene.cloth.customfile + catimg
                catimg = "https://clothweaver.com/Mini-Market-Data/CW-Mini-Market/" + catimg
                with request.urlopen(catimg) as url:
                    saveit = open(localimg, 'wb')
                    saveit.write(url.read())
                    saveit.close
                    print("Saved Icon: " + catimg)
            
            item = "https://clothweaver.com/Mini-Market-Data/CW-Downloadables/" + pNleNS + ".zip"
            print("Downloading: " + item)
            downloadfile = catdirect + pNleNS + ".zip"
            with request.urlopen(item) as url:
                saveit = open(downloadfile, 'wb')
                saveit.write(url.read())
                saveit.close
                print("Saved to: " + downloadfile)
            try:
                import zipfile
                print("unzipping")
                zip_ref = zipfile.ZipFile(downloadfile, 'r')
                zip_ref.extractall(catdirect)
                zip_ref.close()
                epnVSLKa = "Downloaded!"
            except:
                print("Error unzipping files")
                epnVSLKa = "ERROR: Cannot unzip files..."
        else:
            print("Please specify a directory to save to.")
            epnVSLKa = "ERROR: Please choose a save directory"
            epnkleE = 1
        
        return {"FINISHED"}

class CLOTH_OT_REVIEW(Operator):
    bl_idname = "review.id"
    bl_label = "review"
    bl_description = "Review the item"
    
    def execute(self, context):
        url = "https://docs.google.com/forms/d/e/1FAIpQLSfXCT6edWBZf1Tsyilu_7i8m0Ck-Kc6MnWKf7GM9Tiww3D5Ow/viewform"
        webbrowser.open_new_tab(url)
        
        return {"FINISHED"}

# -----------------------------RIG---------------------------------------
class CLOTH_OT_RIG(Operator):
    
    bl_idname = "rig.id"
    bl_label = "rig"
    bl_description = "Attach cloth to a rig (first define clothing and armature) **IMPORTANT** Rig & Cloth must be visible when using this button. Blender crashes otherwise. I do not know why."
    
    def execute(self, context):
        print("**Attach to Rig**")
        
        bpy.ops.object.select_all(action='DESELECT')
        
        bpy.data.objects[pNLvbUY].select_set(True)
        print("selected " + pNLvbUY)
        bpy.context.view_layer.objects.active = bpy.data.objects[EiUpWQ]
        bpy.ops.object.posemode_toggle()
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.pose.select_all(action='TOGGLE')

        print("selected " + EiUpWQ)
        
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        
        bpy.context.view_layer.objects.active = bpy.data.objects[pNLvbUY]
        
        bpy.ops.object.modifier_move_up(modifier="Armature")
        bpy.ops.object.modifier_move_up(modifier="Armature")
        bpy.ops.object.modifier_move_up(modifier="Armature")
        bpy.ops.object.modifier_move_up(modifier="Armature")

        return {"FINISHED"}

class CLOTH_OT_DEFCLOTH(Operator):
    
    bl_idname = "defcloth.id"
    bl_label = "defcloth"
    bl_description = "Select cloth to be rigged then press this button"
    
    def execute(self, context):
        print("\n**define cloth**")
        
        global pNLvbUY
        
        pNLvbUY = bpy.context.object.name
        print("pNLvbUY = " + pNLvbUY)
    
        return {"FINISHED"}

class CLOTH_OT_DEFRIG(Operator):
    
    bl_idname = "defrig.id"
    bl_label = "defrig"
    bl_description = "Select armature (in object mode) then press this button"
    
    def execute(self, context):
        
        global EiUpWQ
        
        print("\n**Define armature**")
        
        EiUpWQ = bpy.context.object.name
        print("EiUpWQ = " + EiUpWQ)
    
        return {"FINISHED"}
#---------------------CREATE CLOTHES BUTTONS--------------------------
class CLOTH_OT_CREATECLOTH(Operator):
    bl_idname = "createcloth.id"
    bl_label = "createcloth"
    bl_description = "Imports selected clothing"
    
    def execute(self, context):
        print("\n**Create " + OmoshiNVB + "**")
      
        vkLpdDs(OmoshiNVB)
            
        return {"FINISHED"}
    
class CLOTH_OT_CREATECUSTOMCLOTH(Operator):
    bl_idname = "createcustomcloth.id"
    bl_label = "createcustomcloth"
    bl_description = "Imports custom clothing"
    
    def execute(self, context):
        customitem = bpy.context.scene.customthumbnails.split(".")[0]
        print("\n**Create " + customitem + "**")
      
        bevtdvawq(customitem)
            
        return {"FINISHED"}
#-----------------------FIX TOWEL FIBERS----------------------------
class CLOTH_OT_FIXTOWEL(Operator):
    
    bl_idname = "fixtowel.id"
    bl_label = "fixtowel"
    bl_description = "Fix display of towel fibers (use after sewing towel on model)"
    
    def execute(self, context):
        print("**Fix fibers**") 
        
        bpy.ops.object.modifier_move_down(modifier="ParticleSystem 1")
        bpy.ops.object.modifier_move_down(modifier="ParticleSystem 1")
        bpy.ops.object.modifier_move_down(modifier="ParticleSystem 1")
        
        return {"FINISHED"}

#-----------------------------MAIN FUNCTIONS-----------------------------------
class CLOTH_OT_GENT(Operator):
    bl_idname = "gent.id"
    bl_label = "GenClothing"
    
    def execute(self, context):
        print("**Base Clothing**")
        vkLpdDs("Base")
    
        return {"FINISHED"}

class CLOTH_OT_ATTACH(Operator):
    bl_idname = "attach.id"
    bl_label = "AttachClothing"
    bl_description = "Attach cloth to model"
    global backups
    def execute(self, context):
        print("\n**Put On Clothing**")
        bpy.context.scene.sync_mode = 'NONE'
        print("Get name of current selected model")
        currentname = bpy.context.object.name
        print("Remove current model from backup list")
        
        try:
            backups.remove(currentname)
            print("removed " + currentname)
        except:
            print(currentname + " not in list")
        
        print("Duplicate model")
        bpy.ops.object.duplicate()
        backups.append(bpy.context.object.name)
        print(backups)

        print("Hide Backup model")
        bpy.ops.object.hide_view_set(unselected=False)
        print("Select original model")
        bpy.context.view_layer.objects.active = bpy.data.objects[currentname]
        
        print("*Fold clothing*")
        bpy.ops.object.modifier_remove(modifier="Cloth")
        bpy.context.scene.frame_current = 1
        bpy.ops.object.modifier_add(type='CLOTH')
        bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
        bpy.context.object.modifiers["Cloth"].settings.use_sewing_springs = True
        bpy.context.object.modifiers["Cloth"].settings.sewing_force_max = bpy.context.scene.cloth.sewForces
        bpy.context.scene.use_gravity = False
        bpy.context.object.modifiers["Cloth"].settings.quality = 5
        bpy.context.object.modifiers["Cloth"].settings.mass = bpy.context.scene.cloth.massClothCustom
        #bpy.context.object.modifiers["Cloth"].settings.structural_stiffness = bpy.context.scene.cloth.stiffClothCustom
        bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = bpy.context.scene.cloth.stiffClothCustom
        bpy.context.object.modifiers["Cloth"].settings.bending_stiffness = bpy.context.scene.cloth.bendClothCustom
        #bpy.context.object.modifiers["Cloth"].settings.vel_damping = 1
        #bpy.context.object.modifiers["Cloth"].settings.vel_damping = 1
        print("play simulation")
        bpy.ops.screen.animation_play()

        return {'FINISHED'}

class CLOTH_OT_SEW(Operator):
    bl_idname = "sew.id"
    bl_label = "SewClothing"
    bl_description = "Sew cloth & smooth"
    
    def execute(self, context):
        count = 2
        number = 0
        print("\n**Sewing cloth**")
        bpy.context.scene.sync_mode = 'NONE'
        bpy.ops.object.shade_smooth()
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Mirror")
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Cloth")
        bpy.ops.object.modifier_add(type='CLOTH')
        bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
        #bpy.context.object.modifiers["Cloth"].settings.use_pin_cloth = True
        bpy.context.object.modifiers["Cloth"].settings.mass = bpy.context.scene.cloth.massClothCustom
        #bpy.context.object.modifiers["Cloth"].settings.structural_stiffness = bpy.context.scene.cloth.stiffClothCustom
        bpy.context.object.modifiers["Cloth"].settings.tension_stiffness = bpy.context.scene.cloth.stiffClothCustom
        bpy.context.object.modifiers["Cloth"].settings.bending_stiffness = bpy.context.scene.cloth.bendClothCustom
        bpy.context.object.modifiers["Cloth"].settings.vertex_group_mass = "pins"
        bpy.context.scene.use_gravity = True
        bpy.context.scene.frame_current = 1
        print("enter edit mode")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_mode(type="VERT")#NEW
    
        print("Prep selectors")
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.select_all(action='TOGGLE')
    
        print("Select index LOOP")
        #select odd group
        name = bpy.context.object.name
        bpy.data.objects[name].vertex_groups.active_index = 0
        
        while count > number:
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.merge(type='COLLAPSE')
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.object.vertex_group_remove(all=False)
            count = count - 1
            print("Loop Stitching")
    
        print("exit edit mode")
        bpy.ops.object.editmode_toggle()
        print("add thickness")
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.02

        print("smoothing")
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subdivision"].levels = 2

        print("play simulation")
        bpy.ops.screen.animation_play()
      
        return {'FINISHED'} 

class CLOTH_OT_FIXMIX(Operator):
    bl_idname = "fixmix.id"
    bl_label = "AdjustMe"
    bl_description = "Attempt to clean up the clothing model"
    
    def execute(self, context):
        print("\n**FixMix**")
        global characterobj
        if characterobj == "empty":
            print("please define a character")
        else:
            try:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Cloth")
            except:
                print("cloth modifier already applied")
            bpy.context.scene.frame_current = 1
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].use_keep_above_surface = True
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
            bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects[characterobj]
            bpy.context.object.modifiers["Shrinkwrap"].offset = 0.25
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.vertices_smooth(factor=0.25)
            bpy.ops.object.editmode_toggle()
            #bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")
            bpy.ops.object.modifier_add(type='CLOTH')
            bpy.context.object.modifiers["Cloth"].collision_settings.use_self_collision = True
            bpy.ops.object.modifier_move_up(modifier="Cloth")
            bpy.ops.object.modifier_move_up(modifier="Cloth")
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
            
            bpy.ops.screen.animation_play()
            
            #count = 1
            
            #while count <= 10:
                #bpy.data.scenes[bpy.context.scene.name].frame_set(count, subframe=count)
                #bpy.context.scene.frame_current = count
                #count = count + 1

        return {'FINISHED'}

class CLOTH_OT_DEFCHAR(Operator):
    
    bl_idname = "defchar.id"
    bl_label = "defchar"
    bl_description = "Select your character then press this button."
    
    def execute(self, context):
        print("\n**define character**")
        
        global characterobj
        
        characterobj = bpy.context.object.name
        print("characterobj = " + characterobj)
    
        return {"FINISHED"}

class CLOTH_OT_RESTORE(Operator):
    bl_idname = "restore.id"
    bl_label = "restoreprevious"
    bl_description = "Restore detached clothing **IMPORTANT** these items will appear in your render unless moved to another layer)"
    
    def execute(self, context):
        print("\n**Restore**")    
        for item in backups:
            try:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.data.objects[item]
                bpy.data.objects[item].hide = False
            except:
                print("can't restore backup")
        
        return {'FINISHED'}

class CLOTH_OT_DELETEBACKUPS(Operator):
    bl_idname = "deletebackups.id"
    bl_label = "deletebackups"
    bl_description = "Delete backup clothing models"
    def execute(self, context):
        global backups
        print("\n**Delete Backups**")
        bpy.ops.view3d.layers(nr=0, extend=False)
        print(backups)
        for item in backups:
            try:
                print("item = " + item)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.data.objects[item]
                bpy.data.objects[item].hide = False
                bpy.data.objects[item].select_set(True)
                bpy.ops.object.delete()
            except:
                print("can't delete backup")
        backups = []
        bpy.ops.view3d.layers(nr=0, extend=False)
        print(backups)
        
        return {'FINISHED'}

class CLOTH_OT_REFLECT(Operator):
    bl_idname = "reflect.id"
    bl_label = "reflect"
    bl_description = "Reflect along the Z-Axis (Reflect Left & Right)"
    
    def execute(self, context):
        print("\n**Reflect**")
        from new import reflect
        text = reflect("Reflect")
        print(text)
        return {'FINISHED'}

class CLOTH_OT_SIM(Operator):
    bl_idname = "sim.id"
    bl_label = "sim"
    bl_description = "Restart/Stop Simulation (A/V-sync will be disabled to speed up simulation)"
    
    def execute(self, context):
        print("\n**Restart/Stop Sim**")
        bpy.ops.screen.frame_jump(end=False)
        bpy.context.scene.sync_mode = 'NONE'
        bpy.ops.screen.animation_play()
        return {'FINISHED'}

class CLOTH_OT_ADDCOL(Operator):
    bl_idname = "addcol.id"
    bl_label = "addcol"
    bl_description = "Gives the character/object a collision, allowing the cloth to interact."
    
    def execute(self, context):
        print("\n**Add Collision**")
        bpy.ops.object.modifier_add(type='COLLISION')
        if bpy.context.scene.cloth.MBL is True:
            bpy.context.object.collision.thickness_outer = 0.005

        return {'FINISHED'}
    
class CLOTH_OT_IMVUSCALEDOWN(Operator):
    bl_idname = "imvuscaledown.id"
    bl_label = "imvuscaledown"
    bl_description = "First: Select all components of your IMVU character [Everything, rig (in object mode), all body mesh object]. Second: use this button to shrink the IMVU character's scale for cloth editing purposes"
    
    def execute(self, context):
        print("\n**IMVU Scale Down**")
        
        if bpy.context.scene.cloth.IMVU is True:
            bpy.ops.transform.resize(value=(0.01, 0.01, 0.01), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.ops.view3d.snap_cursor_to_center()
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        return {'FINISHED'}
    
class CLOTH_OT_IMVUSCALEUP(Operator):
    bl_idname = "imvuscaleup.id"
    bl_label = "imvuscaleup"
    bl_description = "First: Select all components of your IMVU character [Everything, rig (in object mode), all body mesh object]. Second: use this button to restore the IMVU character's scale for exporting purposes"
    
    def execute(self, context):
        print("\n**IMVU Scale Up**")
        
        if bpy.context.scene.cloth.IMVU is True:
            bpy.ops.transform.resize(value=(100, 100, 100), constraint_axis=(False, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}

#---------------------------------MAIN UI PANELS---------------------------
class CLOTH_PT_WEAVER(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Cloth Weaver"
    #bl_context = "objectmode"
    bl_category = "Cloth Weaver"
    
    #Draw UI
    def draw(self, context):
        layout = self.layout
        #New row
        obj = context.object
        row = layout.row()
        row.label(text=copyright)
        row = layout.row()
        updating = row.box()
        updating.label(text="STATUS: " + versionstatus)
        if fePnEzl == "yes":
            updating.operator("updates.id", text = "Update Now", icon="SOLO_OFF")
        
        row = layout.row()
        row.label(text= "v" + str(ioTeifj) + " | " + softwaretype + " | Installs: " + str(yPhKDEwq))
        row = layout.row()
        row.label(text="Installed: " + str(fipVvieq) + " of " + str(yPhKDEwq))
        row = layout.row()
        row.operator("cwhome.id", text = "www.ClothWeaver.com", icon="INFO")
        row = layout.row()
        row.operator("deactivate.id", text = "De-activate this Install", icon="CANCEL")
        row = layout.row()
        row = layout.row()

class CORE_PT_FUC_PHY_RIG(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Core Functions | Physics | Rigging"
    #bl_context = "objectmode"
    bl_category = "Cloth Weaver"
    
    #Draw UI
    def draw(self, context):
        global corefunctions
        global useMBL
        layout = self.layout
        
        #get selected
        obj = context.object
        scn = context.scene
        #Generate Template
        row = layout.row()
        
        coref = row.box()
        physicsf = row.box()
        riggingf = row.box()
        if corefunctions == 1:
            coref.alert = False
            physicsf.alert = True
            riggingf.alert = False
        elif corefunctions == 2:
            coref.alert = False
            physicsf.alert = False
            riggingf.alert = True
        else:
            coref.alert = True
            physicsf.alert = False
            riggingf.alert = False
        coref.operator("corefunctions.id", text="Core", icon="SOLO_OFF")
        physicsf.operator("physicsfunctions.id", text="Physics", icon="PHYSICS")
        riggingf.operator("rigfunctions.id", text="Rigging", icon="POSE_HLT")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        if corefunctions == 1:
            coref.enabled = True
            physicsf.enabled = False
            riggingf.enabled = True
            row = layout.row()
            row.prop(scn.cloth, "MBL")
            row = layout.row()
            row.prop(scn.cloth, "IMVU")
            if bpy.context.scene.cloth.IMVU is True:
                row = layout.row()
                row.operator("imvuscaledown.id", text = "Scale character down", icon="MANIPUL")
                row = layout.row()
                row.operator("imvuscaleup.id", text = "Scale character up", icon="MANIPUL")
            row = layout.row()
            row.operator("addcol.id", text = "Add Collision to Character", icon="MOD_PHYSICS")
            layout.prop(scn.cloth, 'sewForces', toggle=True)
            layout.prop(scn.cloth, 'massClothCustom', toggle=True)
            layout.prop(scn.cloth, 'stiffClothCustom', toggle=True)
            layout.prop(scn.cloth, 'bendClothCustom', toggle=True)
        elif corefunctions == 2:
            coref.enabled = True
            physicsf.enabled = True
            riggingf.enabled = False
            row = layout.row()
            row.operator("defcloth.id", text = "Define Clothing", icon="MOD_CLOTH")
            row = layout.row()
            row.label(text="Cloth = " + pNLvbUY)
            row = layout.row()
            row.operator("defrig.id", text = "Define Armature", icon="OUTLINER_OB_ARMATURE")
            row = layout.row()
            row.label(text="Armature = " + EiUpWQ)
            row = layout.row()
            row.operator("Rig.id", text = "Attach Cloth to Armature", icon="POSE_HLT")
        else:
            coref.enabled = False
            physicsf.enabled = True
            riggingf.enabled = True
            
            row = layout.row()
            row.operator("gent.id", text = "Create Base Plane", icon="MESH_PLANE")
            row = layout.row()
            row.label(text="Fabric")
            row = layout.row()
            col = row.column()
            cols = col.row(align=True)
            cols.operator("attach.id", text = "1. Put on Clothing", icon="SOLO_OFF")
            cols.operator("sew.id", text = "2. Sew Clothing", icon="AUTOMERGE_ON")
            row = layout.row()
            row.label(text="Character = " + characterobj)
            row = layout.row()
            column = col.row(align=True)
            column.operator("defchar.id", text = "3. Define Character", icon="SOLO_OFF")
            column.operator("fixmix.id", text = "4. Clean Up", icon="MOD_CLOTH")
            #Restore Previous
            row = layout.row()
            row.label(text="Backups")
            row = layout.row()
            column = row.column()
            columns = column.row(align=True)
            columns.operator("restore.id", text = "Reveal", icon="RECOVER_LAST")
            columns.operator("deletebackups.id", text = "Delete", icon="CANCEL")
            row = layout.row()
            row.label(text="Other")
            row = layout.row()
            row.operator("reflect.id", text = "Reflect", icon="MOD_MIRROR")
            row = layout.row()
            row.operator("sim.id", text = "Restart/Stop Simulation", icon="PLAY")
        row = layout.row()
        row = layout.row()
            
class CORE_OT_FUNCTIONS(Operator):
    bl_idname = "corefunctions.id"
    bl_label = "corefunctions"
    bl_description = "Display Core Functions"
    def execute(self, context):
        global corefunctions
        corefunctions = 0
        return {'FINISHED'}
    
class PHYSICS_OT_FUNCTIONS(Operator):
    bl_idname = "physicsfunctions.id"
    bl_label = "physicsfunctions"
    bl_description = "Display Physics Functions"
    def execute(self, context):
        global corefunctions
        corefunctions = 1
        return {'FINISHED'}
class RIG_OT_FUNCTIONS(Operator):
    bl_idname = "rigfunctions.id"
    bl_label = "rigfunctions"
    bl_description = "Display Rigging Functions"
    def execute(self, context):
        global corefunctions
        corefunctions = 2
        return {'FINISHED'}
    



class CLOTH_PT_TEMPLATES(Panel):

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Clothing Templates"
    #bl_context = "objectmode"
    bl_category = "Cloth Weaver"
    
    #Draw UI
    def draw(self, context):
        global OmoshiNVB
        layout = self.layout
        wm = context.window_manager
        row = layout.row()
        #Presets
        row.template_icon_view(context.scene.cloth, "my_thumbnails")
        row = layout.row()
        
        # Just a way to access which one is selected
        OmoshiNVB = context.scene.cloth.my_thumbnails
        OmoshiNVB = OmoshiNVB.split(".")[0]
        row.operator("createcloth.id", text = "Create " + OmoshiNVB, icon="MOD_CLOTH")
        if bpy.context.scene.cloth.my_thumbnails == 'Towel.png':
            row = layout.row()
            row.operator("fixtowel.id", text = "Fix Towel Fibers", icon="PARTICLES")
        if bpy.context.scene.cloth.my_thumbnails == 'CollarShirt.png':
            row = layout.row()
            row.label(text="Tip: Re-adjust the collar")
        row = layout.row()
        row = layout.row()
            
class MINI_MARKET_PT_LOCAL_ASSETS(Panel):

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Mini Market | Local Assets"
    #bl_context = "objectmode"
    bl_category = "Cloth Weaver"
    
    #Draw UI
    def draw(self, context):
        global count
        global marketicon
        global BIlPds
        global tmp
        global iPuTlN
        global tcategory
        global pNleNS
        global stars
        global pub
        global update
        global info
        global commercial
        global epnkleE
        global epnVSLKa
        global localdrive
        global eoNsA
        global aFrTemnL
        global previousdir
        global placehold
        global subdir
        global subdira
        global subdirb
        global localcategory
        layout = self.layout
        scn = context.scene
        wm = context.window_manager
        row = layout.row()
        if epnVSLKa != "":
            alerts = row.box()
            alerts.label(text=epnVSLKa)
            row = layout.row()
        mmbox = row.box()
        labox = row.box()
        if epnkleE == 0:
            mmbox.alert=True
            labox.alert=False
        else:
            mmbox.alert=False
            labox.alert=True
        mmbox.operator("selectionmarket.id", text = "Mini Market", icon="WORLD")
        labox.operator("selectionlocal.id", text = "Local Assets", icon="DISK_DRIVE")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()

        #Mini-Marlet
        if epnkleE == 0:
            mmbox.enabled = False
            labox.enabled = True
            #box.label(text="Welcome to the Mini Market")
            #OFFLINE
            if BIlPds == "Mini-Market Offline":
                box = row.box()
                box.label(text=BIlPds)
                row = layout.row()
                row.operator("marketcontrib.id", text = "Contribute Your Designs!", icon="FILE_BACKUP")
		    #ONLINE
            else:
                row.template_icon_view(scn.cloth, "marketthumbnails")
                marketicon = bpy.context.scene.cloth.marketthumbnails
                marketicon = marketicon.split(".")[0]
                row = layout.row()
                location = placehold
                if 'CW-tmp' in placehold:
                    location = placehold.split("CW-tmp")[1]
                row.label(text="Location: " + location)
                #Mini-Market Welcome
                if bpy.context.scene.cloth.marketthumbnails == 'CW-icon.png':
                    row = layout.row()
                    row.operator("markethome.id", text = "Enter", icon="WORLD")
                    row = layout.row()
                    row.label(text="Items listed: " + GjwQpts, icon="COLOR")
                    row = layout.row()
                    row.label(text="Contributing artists: " + puNLfnB, icon="FILE_SOUND")
                    row = layout.row()
                    row.label(text=qEwupVB, icon="ERROR")
                    row = layout.row()
                    row.operator("marketcontrib.id", text = "Contribute Your Designs!", icon="FILE_BLEND")
	            #CATEGORY
                elif "c!" in bpy.context.scene.cloth.marketthumbnails:
                    iPuTlN = bpy.context.scene.cloth.marketthumbnails
                    iPuTlN = iPuTlN.split("!")[1]
                    iPuTlN = iPuTlN.split(".")[0]
                    iPuTlN = tmp + iPuTlN + "/"
                    placehold = tmp
                    tcategory = iPuTlN
                    row = layout.row()
                    row.operator("marketwelcome.id", text = "Welcome", icon="KEYTYPE_EXTREME_VEC")
                    row.operator("marketfolder.id", text = "Open Folder", icon="FILE_FOLDER")
                elif "s!" in bpy.context.scene.cloth.marketthumbnails:
                    subdir = bpy.context.scene.cloth.marketthumbnails
                    subdir = subdir.split("!")[1]
                    subdir = subdir.split(".")[0]
                    iPuTlN = tcategory + subdir
                    placehold = tcategory
                    previousdir = tmp
                    row = layout.row()
                    row.operator("markethome.id", text = "Back", icon="FILE_PARENT")
                    row.operator("marketfolder.id", text = "Open Folder", icon="FILE_FOLDER")   
                elif "t!" in bpy.context.scene.cloth.marketthumbnails:
                    subdira = bpy.context.scene.cloth.marketthumbnails
                    subdira = subdira.split("!")[1]
                    subdira = subdira.split(".")[0]
                    placehold = tcategory + subdir
                    iPuTlN = placehold + "/" + subdira
                    previousdir = tcategory
                    row = layout.row()
                    row.operator("markethome.id", text = "Back", icon="FILE_PARENT")
                    row.operator("marketfolder.id", text = "Open Folder", icon="FILE_FOLDER")
                elif "u!" in bpy.context.scene.cloth.marketthumbnails:
                    subdirb = bpy.context.scene.cloth.marketthumbnails
                    subdirb = subdirb.split("!")[1]
                    subdirb = subdirb.split(".")[0]
                    placehold = tcategory + subdir + "/" + subdira
                    iPuTlN = placehold + "/" + subdirb
                    previousdir = tcategory
                    row = layout.row()
                    row.operator("markethome.id", text = "Back", icon="FILE_PARENT")
                    row.operator("marketfolder.id", text = "Open Folder", icon="FILE_FOLDER")   
                else: #ITEM
                    previousdir = placehold
                    #GET DATA
                    #Set Artist & Package name for downloading...
                    tmpdownload = bpy.context.scene.cloth.marketthumbnails
                    tmpdownload = tmpdownload.split(".")[0]
                    tmpdownload = tmpdownload.split("!-")[1]
                    if pNleNS != tmpdownload:
                        ###("\nGet Product Data from Mini-Market")
                        pNleNS = tmpdownload
                        data = open(tmp + "product-info.txt","r")
                        for line in data:
                            line = line.strip()
                            newdata = str(line)
                            if pNleNS in newdata:
                                ###(newdata)
                                #Set star rating
                                stars = newdata.split("stars:")[1]
                                stars = stars.split(" ")[0]
                                #Set date published
                                pub = newdata.split("pub:")[1]
                                pub = pub.split(" ")[0]
                                #Set update
                                update = newdata.split("update:")[1]
                                update = update.split(" ")[0]
                                #Set info
                                info = newdata.split("info:")[1]
                                info = info.split("*")[0]
                                #Set commercial use
                                commercial = newdata.split("commercial:")[1]
                                commercial = commercial.split(" ")[0]
                        data.close()
                    
                    #DISPLAY DATA
                    row = layout.row()
                    row.operator("markethome.id", text = "Back", icon="FILE_PARENT")
                    row.operator("download.id", text = "Download", icon="URL")
                    
                    category = bpy.context.scene.cloth.marketthumbnails.split("!-")[0]
                    if "A" in category:
                        category = "Accessories"
                    elif "C" in category:
                        category = "Clothing"
                    elif "D" in category:
                        category = "Decor"
                    else:
                        category = "Misc."
                    row = layout.row()
                    row.label(text="Category: " + category, icon="COPY_ID")
                    #Check Item
                    newitem = bpy.context.scene.cloth.marketthumbnails.split("!-")[1]
                    item = newitem
                    item = item.split("-")[1]
                    item = item.split(".")[0]
                    row = layout.row()
                    row.label(text="Item: " + item, icon="COLOR")
                    #Check Artist
                    artist = newitem
                    artist = artist.split("-")[0]
                    row = layout.row()
                    row.label(text="Artist: " + artist, icon="FILE_SOUND")
                    #Publish Date
                    row = layout.row()
                    row.label(text="Publish Date: " + pub, icon="SORTTIME")
                    #Update
                    row = layout.row()
                    row.label(text="Updated: " + update, icon="SCRIPT")
                    #Info
                    row = layout.row()
                    row.label(text="Info: " + info, icon="INFO")
                    #Commercial
                    row = layout.row()
                    if commercial == "No":
                        row.label(text="Commercial use: No", icon="LIBRARY_DATA_BROKEN")
                    else:
                        row.label(text="Commercial use: Yes", icon="SAVE_COPY")
                    #Rating
                    row = layout.row()
                    row.label(text="Rating: ")
                    #DISPLAY RATINGS Stars
                    if stars == "5":
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                    elif stars == "1":
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                    elif stars == "2":
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                    elif stars == "3":           
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                    elif stars == "4":
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_ON")
                        row.label(icon="SOLO_OFF")
                    else:
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                        row.label(icon="SOLO_OFF")
                    #Review Item
                    row = layout.row()
                    row.operator("review.id", text = "Review Item", icon="SAVE_AS")
        #Local Disk        
        else:
            mmbox.enabled = True
            labox.enabled = False
            #box.label(text="Local Assets")
            if localdrive == 0:
                layout.prop(scn.cloth, "customfile", text="Directory")
                row = layout.row()
                row.operator("reload.id", text = "refresh", icon="FILE_REFRESH")
            if localdrive == 1:
                row = layout.row()
                row.operator("localroot.id", text = "Return to Directory", icon="DISK_DRIVE")
            row = layout.row()
            eoNsA = bpy.context.scene.cloth.customfile
            row.template_icon_view(scn.cloth, "customthumbnails")
            rhyJpSQ = bpy.context.scene.cloth.customthumbnails
            rhyJpSQ = rhyJpSQ.split(".")[0]
            
            if "c!" in bpy.context.scene.cloth.customthumbnails:
                row = layout.row()
                row.operator("localfolder.id", text = "Open Folder", icon="BOOKMARKS")
                aFrTemnL = bpy.context.scene.cloth.customthumbnails.split("c!")[1]
                aFrTemnL = aFrTemnL.split(".")[0]
                localcategory = aFrTemnL + "/"
            
            elif "!-" in bpy.context.scene.cloth.customthumbnails:
                aFrTemnL = bpy.context.scene.cloth.customthumbnails.split("!-")[1]
                aFrTemnL = aFrTemnL.split(".")[0]
                aFrTemnL = localcategory + aFrTemnL
                artist = aFrTemnL
                product = artist.split("-")[1]
                product = product.split(".")[0]
                artist = artist.split("-")[0]
                
                category = bpy.context.scene.cloth.customthumbnails.split("!-")[0]
                if "A" in category:
                    category = "Accessories"
                elif "C" in category:
                    category = "Clothing"
                elif "D" in category:
                    category = "Decor"
                else:
                    category = "Misc."
                row = layout.row()
                row.operator("localfolder.id", text = "Open Folder " + product, icon="BOOKMARKS")
                row = layout.row()
                row.label(text="Category: " + category, icon="COPY_ID")
                row = layout.row()
                row.label(text="Item: " + product, icon="COLOR")
                row = layout.row()
                row.label(text="Artist: " + artist, icon="FILE_SOUND")
            else:
                product = bpy.context.scene.cloth.customthumbnails.split(".")[0]
                row = layout.row()
                row.operator("createcustomcloth.id", text = "Create " + product, icon="COLOR")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()

class LOCAL_OT_FOLDER(Operator):
    
    bl_idname = "localfolder.id"
    bl_label = "localfolder"
    bl_description = "Open local folder"
    
    def execute(self, context): 
        global localdrive
        global epnVSLKa
        global eoNsA
        epnVSLKa = ""
        localdrive = 1
        eoNsA = eoNsA + aFrTemnL + "/"
        for customgallery in customeqPBSLGHDK.values():
            bpy.utils.previews.remove(customgallery)
        #refresh()
        customgallery = bpy.utils.previews.new()
        customgallery.images_location = eoNsA
        customeqPBSLGHDK["customthumbnail_previews"] = customgallery
        #bpy.context.scene.customthumbnails = bpy.context.scene.customthumbnails
        return {'FINISHED'}
             
class LOCAL_OT_ROOT(Operator):
    
    bl_idname = "localroot.id"
    bl_label = "localroot"
    bl_description = "Go to root local folder"
    
    def execute(self, context): 
        global localdrive
        global epnVSLKa
        epnVSLKa = ""
        localdrive = 0
        for customgallery in customeqPBSLGHDK.values():
            bpy.utils.previews.remove(customgallery)
        #refresh()
        customgallery = bpy.utils.previews.new()
        customgallery.images_location = eoNsA
        customeqPBSLGHDK["customthumbnail_previews"] = customgallery
        #bpy.context.scene.customthumbnails = bpy.context.scene.customthumbnails
        return {'FINISHED'}

class SELECTION_OT_MARKET(Operator):
    
    bl_idname = "selectionmarket.id"
    bl_label = "selectionMarket"
    bl_description = "Go to Mini-Market"
    
    def execute(self, context): 
        global epnkleE
        global epnVSLKa
        epnVSLKa = ""
        epnkleE = 0
        return {'FINISHED'}
        
class SELECTION_OT_LOCAL(Operator):
    
    bl_idname = "selectionlocal.id"
    bl_label = "selectionPLocal"
    bl_description = "Go to Local Drive"
    
    def execute(self, context): 
        global epnkleE
        epnkleE = 1
        return {'FINISHED'}
        
class MARKET_OT_FOLDER(Operator):
    
    bl_idname = "marketfolder.id"
    bl_label = "marketfolder"
    bl_description = "Open Selected Folder"
    
    def execute(self, context):
        global iPuTlN
        
        for marketgallery in marketeqPBSLGHDK.values():
            bpy.utils.previews.remove(marketgallery)
        minimarket()
        bpy.context.scene.cloth.marketthumbnails = bpy.context.scene.marketthumbnails
        return {'FINISHED'}

class MARKET_OT_HOME(Operator):
    bl_idname = "markethome.id"
    bl_label = "markethome"
    bl_description = "Return Home"
    
    def execute(self, context):
        global iPuTlN
        global previousdir
        if "CW" in bpy.context.scene.cloth.marketthumbnails:
            iPuTlN = tmp
            previousdir = tmp
        else:
            iPuTlN = previousdir
        for marketgallery in marketeqPBSLGHDK.values():
            bpy.utils.previews.remove(marketgallery)
        minimarket()
        #bpy.context.scene.marketthumbnails = bpy.context.scene.marketthumbnails
        return {'FINISHED'}
    
class MARKET_OT_WELCOME(Operator):
    bl_idname = "marketwelcome.id"
    bl_label = "marketwelcome"
    bl_description = "Return to Welcome Screen"
    
    def execute(self, context):
        global iPuTlN
        global previousdir
        iPuTlN = tmp + "CW-icon/"
        previousdir = iPuTlN
        for marketgallery in marketeqPBSLGHDK.values():
            bpy.utils.previews.remove(marketgallery)
        minimarket()
        bpy.context.scene.cloth.marketthumbnails = 'CW-icon.png'
        return {'FINISHED'}
    
class MARKET_OT_CONTRIB(Operator):
    bl_idname = "marketcontrib.id"
    bl_label = "marketcontrib"
    bl_description = "Contribute your designs and help grow the Mini-Market community!"
    
    def execute(self, context):
        url = "https://docs.google.com/forms/d/e/1FAIpQLSfp0wVXcKvgxEHFv_T1Kx7uU-IgV7kW1rUPhcuEfzP2kCnbtg/viewform"
        webbrowser.open_new_tab(url)
        return {'FINISHED'}     

class RE_OT_LOAD(Operator):
    bl_idname = "reload.id"
    bl_label = "reload"
    bl_description = "Refresh User Gallery"
    #bl_context = "scene"
    def execute(self, context):
        for customgallery in customeqPBSLGHDK.values():
            bpy.utils.previews.remove(customgallery)
        #refresh()
        customgallery = bpy.utils.previews.new()
        customgallery.images_location = eoNsA
        customeqPBSLGHDK["customthumbnail_previews"] = customgallery
        nLupnvajlp(eoNsA)
        return {'FINISHED'}

#------------------------------EDIT MODE OPTIONS------------------------

class JOIN_OT_EDGE(Operator):
    bl_idname = "joinedge.id"
    bl_label = "joinedge"
    bl_description = "Select edges to be sewn together, then press this button **IMPORTANT** Select only adjacent edges (Ex: Side of Dress separately from shoulder straps)"
    
    def execute(self, context):
        print("\n**Join Edges**")
        bpy.ops.mesh.bridge_edge_loops()
        bpy.ops.mesh.delete(type='ONLY_FACE')
        
        return {'FINISHED'}
#possible automate selection, loop assign edges & vertex groups for each, var for # of vertex groups
class ASSIGN_OT_EVENS(Operator):
    bl_idname = "assignevens.id"
    bl_label = "assignevens"
    bl_description = "IN VERTEXT SELECT MODE: Select each group of edges, then use this button to assign EVENS"
    
    def execute(self, context):
        print("\n**Select Evens**")
        bpy.ops.mesh.select_nth(nth=2, skip=1, offset=1)
        name = bpy.context.object.name
        bpy.data.objects[name].vertex_groups.active_index = 1
        bpy.ops.object.vertex_group_assign()
        
        return {'FINISHED'}
    
class ASSIGN_OT_ODDS(Operator):
    bl_idname = "assignodds.id"
    bl_label = "assignodds"
    bl_description = "IN VERTEXT SELECT MODE: Select each group of edges, then use this button to assign ODDS"
    
    def execute(self, context):
        print("\n**Select Odds**")
        bpy.ops.mesh.select_nth(nth=2, skip=1, offset=0)
        name = bpy.context.object.name
        bpy.data.objects[name].vertex_groups.active_index = 0
        bpy.ops.object.vertex_group_assign()
        
        return {'FINISHED'}
    
class BACK_OT_SIDE(Operator):
    bl_idname = "backside.id"
    bl_label = "backside"
    bl_description = "Creates backside of clothing"
    
    def execute(self, context):
        print("\n**Select Odds**")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 1, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.mesh.flip_normals()
        bpy.ops.mesh.select_all(action='DESELECT')
        
        return {'FINISHED'}

class U_OT_V(Operator):
    
    bl_idname = "uv.id"
    bl_label = "uv"
    bl_description = "Reset UVs"
    
    def execute(self, context):
        print("\n**Reset UVs**")
        from new import uvs
        text = uvs("Reset UVs")
        print(text)
        return {"FINISHED"}
    
class MARK_OT_SEAM(Operator):
    
    bl_idname = "markseam.id"
    bl_label = "markseam"
    bl_description = "Mark Seam"
    
    def execute(self, context):
        print("\n**Mark Seam**")
        from new import markseams
        text = markseams("Mark Seam")
        print(text)
        return {"FINISHED"}

#---------------------------------EDIT MODE PANEL--------------------------------------
class EDIT_PT_MODE(Panel):

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Cloth Weaver"
    #bl_context = "mesh_edit"
    bl_category = "Cloth Weaver"
    
    #Draw UI
    def draw(self, context):
        
        global editmodefunctions
        layout = self.layout
        
        #get selected
        obj = context.object
        scn = context.scene
        #Generate Template
        row = layout.row()
        row.label(text=copyright)
        row = layout.row()
        row = layout.row()
        row.operator("EditHelp.id", text="View Tutorial for Custom Clothing", icon="HELP")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        vertexf = row.box()
        uvf = row.box()
        if editmodefunctions == 1:
            vertexf.alert = False
            uvf.alert = True
        else:
            vertexf.alert = True
            uvf.alert = False
        vertexf.operator("vertexfunctions.id", text="Custom Cloth Edit", icon="SOLO_OFF")
        uvf.operator("uvfunctions.id", text="UV Panel", icon="SOLO_OFF")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row = layout.row()
        
        if editmodefunctions == 1:
            uvf.enabled = False
            vertexf.enabled = True
            row = layout.row()
            row.operator("uv.id", text = "Reset UVs", icon="UV_FACESEL")
            row = layout.row()
            row.operator("markseam.id", text = "Mark Seams", icon="UV_EDGESEL")
        else:
            vertexf.enabled = False
            uvf.enabled = True
      
            row = layout.row()
            row.operator("backside.id", text = "Create Backside & Flip Normals", icon="SOLO_OFF")
            row = layout.row()
            row = layout.row()
            
            #Attach Clothing
            row = layout.row()
            row.operator("assignevens.id", text = "Assign Evens", icon="SNAP_VERTEX")
            row = layout.row()
            row.operator("assignodds.id", text = "Assign Odds", icon="SNAP_VERTEX")
            row = layout.row()
            row.operator("joinedge.id", text = "Join Parallel Edges", icon="UV_SYNC_SELECT")
            
            #help
            row = layout.row()
            row.label(text="Instructions for sewing edges")
            row = layout.row()
            row.label(text="1. Assign  EVENS  for each edge group")
            row = layout.row()
            row.label(text="2. Assign  ODDS  for each edge group")
            row = layout.row()
            row.label(text="3. Join Edges for each edge group pair")
            row = layout.row()
            row = layout.row()
            row = layout.row()
            
            row = layout.row()
            row.label(text="Vertex Groups")
            ob = context.object
            group = ob.vertex_groups.active

            rows = 2
            if group:
                rows = 4

            row = layout.row()
            row.template_list("MESH_UL_vgroups", "", ob, "vertex_groups", ob.vertex_groups, "active_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.vertex_group_add", icon='ZOOM_IN', text="")
            col.operator("object.vertex_group_remove", icon='ZOOM_OUT', text="").all = False
            #col.menu("MESH_MT_vertex_group_specials", icon='DOWNARROW_HLT', text="")
            if group:
                col.separator()
                col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if ob.vertex_groups and (ob.mode == 'EDIT' or (ob.mode == 'WEIGHT_PAINT' and ob.type == 'MESH' and ob.data.use_paint_mask_vertex)):
                row = layout.row()

                sub = row.row(align=True)
                sub.operator("object.vertex_group_assign", text="Assign")
                sub.operator("object.vertex_group_remove_from", text="Remove")

                sub = row.row(align=True)
                sub.operator("object.vertex_group_select", text="Select")
                sub.operator("object.vertex_group_deselect", text="Deselect")

                #layout.prop(context.tool_settings, "vertex_group_weight", text="Weight")
                
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row.label(text="Note: Must have groups named even & odd")
            row = layout.row()
            row.label(text="Tip: If adding more edge loops, redo 1-3")
            row = layout.row()
                
class VERTEX_OT_FUNCTION(Operator):
    bl_idname = "vertexfunctions.id"
    bl_label = "vertexfunctions"
    bl_description = "Display Cloth Editing Functions"
    def execute(self, context):
        global editmodefunctions
        editmodefunctions = 0
        return {'FINISHED'}      
    
class UV_OT_FUNCTION(Operator):
    bl_idname = "uvfunctions.id"
    bl_label = "uvfunctions"
    bl_description = "Display UV Functions"
    def execute(self, context):
        global editmodefunctions
        editmodefunctions = 1
        return {'FINISHED'}         

#------------------------------Startup Functions---------------------------------------
def feqpVvnal():
    global eoNsA
    print("\n*Load main program*")
    #bpy.utils.register_module(__name__)
    print("registered modules")
    #refresh()
    customgallery = bpy.utils.previews.new()
    customgallery.images_location = eoNsA
    customeqPBSLGHDK["customthumbnail_previews"] = customgallery
    try:
        bpy.utils.unregister_class(license)
    except:
        print("")
    
    #CHECK CURRENT SOFTWARE VERSION
    global ioTeifj
    global versionstatus
    global fePnEzl
    global BIlPds
    """
    try:
        urlv = request.urlopen('http://alexanderkane.net/CWv.txt').read()
        BIlPds = "Mini-Market Open"
        CWV = str(urlv)
        CWV = CWV.split("'")[1]
        CWV = CWV.split("'")[0]
        if '\\' in CWV:
            CWV = CWV.split('\\')[0]
        print("Latest version: " + CWV)
        print("My version: " + str(ioTeifj))
        if ioTeifj < float(CWV):
            versionstatus = "(v" + CWV + " available!)"
            fePnEzl = "yes"
    except:
        print("\nnot online")
        versionstatus = "(Can't check for updates, not online)"
    """
    if BIlPds == "Mini-Market Offline":
        print("Mini-Market Offline")
        
    else:
        opuRbb()
    
    print("\n**************************************\n* Done Loading...Cloth Weaver Ready! *\n**************************************\n\n")

def opuRbb():
    #LOAD STORE GALLERY
    global tmp
    global running
    global iPuTlN
    global GjwQpts
    global puNLfnB
    global qEwupVB
    import shutil
    print("\n*Create Local Directories for Store*")
    
    running = 1
    
    if os.path.exists(tmp):
        information = tmp + "product-info.txt"
        if os.path.isfile(information):
            try:
                os.remove(information)
                print('purge tmp info')
            except:
                print('cannot purge tmp info')
        print("CW temp directory exists at '" + tmp + "'")
    else:
        try:
            os.makedirs(tmp)
            print("Created '" + tmp + "'")
        except:
            print("Error creating root directory, check write permissions?")   
    
    #STORE URL & INSTRUCTIONS 
    #CREATE TMP DIRECTORIES ON LOCAL. DOWNLOAD STORE PREVIEWS ONCE ON STARTUP
    RootURL = "https://www.clothweaver.com/Mini-Market-Data/CW-Mini-Market/"
    instructionsURL = request.urlopen("https://clothweaver.com/Mini-Market-Data/CW-Mini-Market/instructions.txt")
    directory = ""
    for line in instructionsURL:
        line = line.strip()
        instruc = str(line)
        instruc = instruc.replace("b'","")
        instruc = instruc.replace("'","")
        if instruc.startswith("#stats"):
            GjwQpts = instruc.split("items:")[1]
            GjwQpts = GjwQpts.split(" ")[0]
            puNLfnB = instruc.split("artists:")[1]
            puNLfnB = puNLfnB.split(" ")[0]
            qEwupVB = instruc.split("msg:")[1]
            qEwupVB = qEwupVB.split("*")[0]
            continue
        elif instruc.startswith("directory"):
            directory = instruc.split(" ")[1]
            newfolder = tmp + directory
            if os.path.exists(newfolder):
                print("Directory EXISTS: '" + newfolder + "'")
            else:  
                try:
                    os.makedirs(newfolder)
                    print("NEW directory '" + newfolder + "'")
                except:
                    print("ERROR creating directory, check write permissions?")
        elif instruc[:3] == "img":
            img = instruc.split(" ")[1]
            imgurl = RootURL + directory + img
            downloadfile = tmp + directory + img
            if os.path.isfile(downloadfile):
                print("FILE EXISTS: '" + downloadfile + "'")
            else:
                try:
                    with request.urlopen(imgurl) as url:
                        saveit = open(downloadfile, 'wb')
                        saveit.write(url.read())
                        saveit.close
                        print("DOWNLOADING: '" + imgurl + "'")
                except:
                    print("ERROR creating preview image, check write permissions?")
                    print("errorurl: " + imgurl)
    instructionsURL.close()
    iPuTlN = tmp + "CW-icon/"
    minimarket()

"""
def minimarket():
    ###("Current Mini-Market Directory: '" + iPuTlN + "'")
    marketgallery = bpy.utils.previews.new()
    marketgallery.images_location = iPuTlN
    marketeqPBSLGHDK["marketthumbnail_previews"] = marketgallery

def refresh():
    customgallery = bpy.utils.previews.new()
    customgallery.images_location = eoNsA
    customeqPBSLGHDK["customthumbnail_previews"] = customgallery
"""    

    
def nLupnvajlp(file):
    directory = BunsLiGDF + "customdir.txt"
    print("\n*Saving User Presets*\ndirectory: " + directory + "\ndata: " + file)
    saveFile = open(directory,"w")
    saveFile.write(file)
    saveFile.close
class CLOTH_PT_LICENSE(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Cloth Weaver -Register"
    #bl_context = "objectmode"
    bl_category = "Cloth Weaver"
    
    #Draw UI
    def draw(self, context):
        
        global uPenlAepqn
        
        layout = self.layout
        row = layout.row()
        box = row.box()
        box.label("STATUS: " + uPenlAepqn)
        row = layout.row()
        row.label(text=copyright)
        row = layout.row()
        row.label(text="Please enter your Email & license key")
        row = layout.row()
        scn = context.scene
        layout.prop(scn.cloth, 'EmailAddress', icon='COPY_ID')
        layout.prop(scn.cloth, 'LK', icon='LOCKED')
        #Generate Template
        row = layout.row()
        row.operator("sregister.id", text = "Register Key", icon="WORLD")

class NEP_OT_YUD(Operator):
    
    bl_idname = "sregister.id"
    bl_label = "sregister"
    bl_description = "Register Key"
    
    def execute(self, context):
        
        global uPenlAepqn
        import urllib
        global yPhKDEwq
        global fipVvieq
        
        print("\n*Register Key")
        
        url = 'https://api.gumroad.com/v2/licenses/verify'
        data = urllib.parse.urlencode({'increment_uses_count' : 'false', 'product_permalink' : productcode, 'license_key'  : bpy.context.scene.cloth.LK})
        data = data.encode('utf-8')
        req = urllib.request.Request(url, data)
        print("checking for license key...")
        try:
            print("connecting to server...")
            result = urllib.request.urlopen(req).read().decode("utf-8")
            email = result.split('email":"')[1]
            email = email.split('"')[0]
            
            uses = 0
            try:
                userURL = "https://clothweaver.com/LK-Store/" + softwaretype + "-" + bpy.context.scene.cloth.LK + ".txt"
                uses = request.urlopen(userURL).read()
                uses = int(uses)
            except:
                print("license has not been created yet")
            ###("uses: " + str(uses))
            try:
                quantity = result.split('quantity":')[1]
                quantity = quantity.split(',')[0]
                quantity = int(quantity)
            except:
                quantity = yPhKDEwq
            fipVvieq = uses
            yPhKDEwq = quantity
            try:
                yfpeJKl = result.split('subscription_cancelled_at":')[1]
                yfpeJKl = yfpeJKl.split(',')[0]
            except:
                yfpeJKl = "null"
            try:
                subfailed = result.split('subscription_failed_at":')[1]
                subfailed = subfailed.split('}')[0]
            except:
                subfailed = "null"
            ###("\nresult:\n" + result + "\nemail:\n" + email + "\nuses:\n" + str(uses) + "\nquantity\n" + str(quantity) + "\nyfpeJKl\n" + yfpeJKl + "\nsubfailed\n" + subfailed+ "\n")
            if bpy.context.scene.cloth.EmailAddress == email and "null" in yfpeJKl and "null" in subfailed and uses <= quantity:
                print("Subscription is Current")
                uPenlAepqn = "Subscription is Current"         
                try:
                    data = urllib.parse.urlencode({'increment_uses_count' : 'true', 'product_permalink' : productcode, 'license_key'  : bpy.context.scene.cloth.LK})
                    data = data.encode('utf-8')
                    req = urllib.request.Request(url, data)
                    result = urllib.request.urlopen(req).read().decode("utf-8")
                    
                    urlcw = "https://clothweaver.com/LK-Store/addLicense.php/"
                    full_url = urlcw + '?LK=' + bpy.context.scene.cloth.LK + '&ST=' + softwaretype + '&txt=' + str(quantity)
                    ###("addLicenseURL: " + full_url)
                    response = request.urlopen(full_url)
                    request_body = response.read()
                    ###(request_body)
                    
                    userURL = "https://clothweaver.com/LK-Store/" + softwaretype + "-" + bpy.context.scene.cloth.LK + ".txt"
                    uses = request.urlopen(userURL).read()
                    uses = int(uses)
                    ###("uses: " + str(uses))
                    fipVvieq = uses
                    print("Saving Key to file")
                    saveFile = open(BunsLiGDF + "LKstore.txt","w")
                    saveFile.write(bpy.context.scene.cloth.LK)
                    saveFile.close      
                    print("Saving Email to file")
                    saveFile = open(BunsLiGDF + "Email.txt","w")
                    saveFile.write(bpy.context.scene.cloth.EmailAddress)
                    saveFile.close
                except:
                    print("Can't save key or email to file")
                
                feqpVvnal()
            elif "null" not in yfpeJKl:
                print("Subscription was Cancelled")
                uPenlAepqn = "Subscription was Cancelled"
            elif "null" not in subfailed:
                print("Subscription failed to renew")
                uPenlAepqn = "Subscription failed to renew"
            elif uses >= quantity:
                print("Too many Installs active at one time.\nYou have " + str(quantity) + " Installs on your account.")
                uPenlAepqn = "Too many Installs active at one time.You have " + str(quantity) + " Installs on your account."
            elif email != bpy.context.scene.cloth.EmailAddress:
                print("Email is not correct")
                uPenlAepqn = "Email is not correct"
            else:
                print("error unknown 888")
                uPenlAepqn = "error unkown 888"
        except urllib.error.HTTPError as err:
            if err.code == 404:
                print("License Key not found")
                uPenlAepqn = "License Key not found"
            else:
                uPenlAepqn = "Not Online (connect to Internet & restart Blender)"
                print("Not Online (connect to Internet & restart Blender)")
                raise
        except:
            uPenlAepqn = "Not Online (connect to Internet & restart Blender)"
            print("Not Online (connect to Internet & restart Blender)")
            feqpVvnal()
        
        return {"FINISHED"}


def my_cleanup_code():
    print("\n**De-activate Current Install**")
    keyfile = BunsLiGDF + "LKstore.txt"
    if os.path.isfile(keyfile):
        if running != 0:
            print("FULS")
            currentKey = open(keyfile,"r")
            cKey = str(currentKey.readline().strip())
            ###(cKey)
            urlcw = "https://clothweaver.com/LK-Store/dLicense.php/"
            full_url = urlcw + '?LK=' + cKey + '&ST=' + softwaretype
            ###(full_url)
            #response = request.urlopen(full_url)
            #request_body = response.read()
            ###(request_body)      
    else:
        print("can't find license key file")

classes = (
    CLOTH_PROPERTY,
    CLOTH_PT_WEAVER,
    CORE_PT_FUC_PHY_RIG,
    CLOTH_PT_TEMPLATES,
    EDIT_PT_MODE,
    MINI_MARKET_PT_LOCAL_ASSETS,
    CLOTH_OT_EDITHELP,
    CLOTH_OT_CWHOME,
    CLOTH_OT_DEACTIVATE,
    CLOTH_OT_DOWNLOAD,
    CLOTH_OT_REVIEW,
    CLOTH_OT_RIG,
    CLOTH_OT_DEFCLOTH,
    CLOTH_OT_DEFRIG,
    CLOTH_OT_CREATECLOTH,
    CLOTH_OT_CREATECUSTOMCLOTH,
    CLOTH_OT_FIXTOWEL,
    CLOTH_OT_GENT,
    CLOTH_OT_ATTACH,
    CLOTH_OT_SEW,
    CLOTH_OT_FIXMIX,
    CLOTH_OT_DEFCHAR,
    CLOTH_OT_RESTORE,
    CLOTH_OT_DELETEBACKUPS,
    CLOTH_OT_REFLECT,
    CLOTH_OT_SIM,
    CLOTH_OT_ADDCOL,
    CLOTH_OT_IMVUSCALEDOWN,
    CLOTH_OT_IMVUSCALEUP,
    CORE_OT_FUNCTIONS,
    PHYSICS_OT_FUNCTIONS,
    RIG_OT_FUNCTIONS,
    LOCAL_OT_FOLDER,
    LOCAL_OT_ROOT,
    SELECTION_OT_MARKET,
    SELECTION_OT_LOCAL,
    MARKET_OT_FOLDER,
    MARKET_OT_HOME,
    MARKET_OT_WELCOME,
    MARKET_OT_CONTRIB,
    RE_OT_LOAD,
    JOIN_OT_EDGE,
    ASSIGN_OT_EVENS,
    ASSIGN_OT_ODDS,
    BACK_OT_SIDE,
    U_OT_V,
    MARK_OT_SEAM,
    VERTEX_OT_FUNCTION,
    UV_OT_FUNCTION,
    )

def register():
    for cla in classes:
        bpy.utils.register_class(cla)
    bpy.types.Scene.cloth = PointerProperty(type=CLOTH_PROPERTY)
       
    print("\n\n**********************\n* Start Cloth Weaver *\n**********************\n")
    
    customdir = BunsLiGDF + "customdir.txt"
    global eoNsA
    if os.path.isfile(customdir):
        eoNsA = open(customdir,"r")
        eoNsA = str(eoNsA.read())
        print("Custom file Exists: " + customdir)
    else:
        try:
            print("Trying to create customdir storage file")
            nLupnvajlp("/")
            print("Created " + customdir)
        except:
            print("Can't create customdir.txt -Write error?")
    
    
    try:
        bpy.context.scene.cloth.customfile = eoNsA
    except:
        print("set customdir thumbnail?")


    
    

    
    
    global uPenlAepqn
    global yPhKDEwq
    global fipVvieq
    import urllib
    keyfile = BunsLiGDF + "LKstore.txt"
    emailfile = BunsLiGDF + "Email.txt"
    if os.path.isfile(keyfile) and os.path.isfile(emailfile):
        currentKey = open(keyfile,"r")
        cKey = str(currentKey.readline().strip())
        print("Check Key from File: '" + cKey + "'")
        purchaseemail = open(emailfile,"r")
        pemail = str(purchaseemail.readline().strip())
        print("Check Email from File: '" + pemail + "'")
        
        
        url = 'https://api.gumroad.com/v2/licenses/verify'
        #data = urllib.parse.urlencode({'increment_uses_count' : 'false','product_permalink' : productcode, 'license_key' : cKey})
        #data = data.encode('utf-8')
        #req = urllib.request.Request(url, data)
        print("checking license key...")
        try:
            """print("connecting to server...")
            result = urllib.request.urlopen(req).read().decode("utf-8")
            email = result.split('email":"')[1]
            email = email.split('"')[0]"""
            uses = 0
            
            
            try:
                #quantity = result.split('quantity":')[1]
                quantity = quantity.split(',')[0]
                quantity = int(quantity)
            except:
                quantity = yPhKDEwq
                
            """
            try:
                ###("check uses file")
                userURL = "https://clothweaver.com/LK-Store/" + softwaretype + "-" + cKey + ".txt"
                ###(userURL)
                uses = request.urlopen(userURL).read()
                uses = int(uses)
                ###("number of uses: " + str(uses))
            except:
                print("keyDB does not exist")
                
            
            fipVvieq = uses"""
            fipVvieq = 1
            yPhKDEwq = quantity
            try:
                #yfpeJKl = result.split('subscription_cancelled_at":')[1]
                yfpeJKl = "null"#yfpeJKl.split(',')[0]
            except:
                yfpeJKl = "null"
            try:
                #subfailed = result.split('subscription_failed_at":')[1]
                subfailed = subfailed.split('}')[0]
            except:
                subfailed = "null"

            if "null" in yfpeJKl and "null" in subfailed: #and pemail == email  and uses < quantity:
                print("Subscription is Current")
                uPenlAepqn = "Subscription is Current"
                urlcw = "https://clothweaver.com/LK-Store/addLicense.php/"
                full_url = urlcw + '?LK=' + cKey + '&ST=' + softwaretype + '&txt=' + str(quantity)
                #response = request.urlopen(full_url)
                fipVvieq = fipVvieq + 1
                feqpVvnal()
                """elif uses >= quantity:
                print("Too many Installs active at one time.\nYou have " + str(quantity) + " Installs on your account.")
                uPenlAepqn = "Too many Installs active at one time.You have " + str(quantity) + " Installs on your account."
                feqpVvnal()"""
            elif "null" not in yfpeJKl:
                print("Subscription was Cancelled")
                uPenlAepqn = "Subscription was Cancelled"
                feqpVvnal()
            elif "null" not in subfailed:
                print("Subscription failed to renew")
                uPenlAepqn = "Subscription failed to renew"
                feqpVvnal()
            else:
                print("error unknown 555")
                uPenlAepqn = "error unkown 555"
                feqpVvnal()
        except urllib.error.HTTPError as err:
            if err.code == 404:
                print("License Key not found")
                uPenlAepqn = "License Key not found"
                feqpVvnal()
            else:
                uPenlAepqn = "Not Online (connect to Internet & restart Blender)"
                print("Not Online (connect to Internet & restart Blender)")
                feqpVvnal()
                raise
        except:
            uPenlAepqn = "Not Online (connect to Internet & restart Blender)"
            print("Not Online (connect to Internet & restart Blender)")
            feqpVvnal()
    else:
        try:
            print("Trying to create keystore file")
            saveFile = open(keyfile,"w")
            saveFile.write("")
            saveFile.close
            print("Created keystore at " + keyfile)
            
            print("Trying to create emailstore file")
            saveFile = open(emailfile,"w")
            saveFile.write("")
            saveFile.close
            print("Created emailfile at " + emailfile)
            feqpVvnal()
            
        except:
            print("Can't create keyfiles -Write error?")
            uPenlAepqn = "Can't create keyfiles -Write error?"
            feqpVvnal()

def unregister():
    for cla in classes:
        bpy.utils.unregister_class(cla)
    del bpy.types.Scene.cloth
    print("unregistered")
    my_cleanup_code()
    from bpy.types import WindowManager
    for pcoll in eqPBSLGHDK.values():
        bpy.utils.previews.remove(pcoll)
    eqPBSLGHDK.clear()
    

if __name__ == '__main__':
    register()
