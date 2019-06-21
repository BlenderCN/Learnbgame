"""
RealXtend character exporter
"""

import os
import b2rexpkg
from b2rexpkg.tools.siminfo import GridInfo
from b2rexpkg.tools.simconnection import SimConnection
from b2rexpkg.b24.ogre_exporter import OgreExporter
from b2rexpkg.tools.uuidexport import reset_uuids

from ogrepkg.base import indent
from ogrepkg.armatureexport import GetArmatureObject
from ogremeshesexporter import ArmatureAnimationProxyManager, ArmatureAnimationProxy 

import Blender

class CharacterExporter(object):
    action_uuids = {'Walk': '6ed24bd8-91aa-4b12-ccc7-c97c857ab4e0',
                    'CrouchWalk': "47f5f6fb-22e5-ae44-f871-73aaaf4a6022",
                    'Fly': "aec4610c-757f-bc4e-c092-c6e9caf18daf",
                    "HoverDown": "20f063ea-8306-2562-0b07-5c853b37b31e",
                    "HoverUp": "62c5de58-cb33-5743-3d07-9e4cd4352864",
                    "Hover": "4ae8016b-31b9-03bb-c401-b1ea941db41d",
                    "Run": "05ddbff8-aaa9-92a1-2b74-8fe77a29b445",
                    "Sit": "1a5fe8ac-a804-8a5d-7cbd-56bd83184568",
                    "SitGround": "1c7600d6-661f-b87b-efe2-d7421eb93c86",
                    "Stand": "2408fe9e-df1d-1d7d-f4ff-1384fa7b350f"}
    def __init__(self):
        # rest
        self.gridinfo = GridInfo()
        self.sim = SimConnection()
        self.ogre = OgreExporter()
        self.settings = {}
        self.actions_map = {}
        for name in self.action_uuids:
            self.actions_map[name.lower()] =  name

    def connect(self, base_url):
        """
        Connect to an opensim instance
        """
        self.gridinfo.connect(base_url)
        print self.sim.connect(base_url)

    def test(self):
        """
        Api tests
        """
        print self.gridinfo.getGridInfo()["gridnick"]
        regions = self.gridinfo.getRegions()
        for id in regions:
            region = regions[id]
            print " *", region["name"], region["x"], region["y"], id

        # xmlrpc
        print self.sim.login("caedes", "caedes", "pass")
        print self.sim.sceneClear("d9d1b302-5049-452d-b176-3a9561189ca4",
                                         "cube")
        print self.sim.sceneUpload("d9d1b302-5049-452d-b176-3a9561189ca4",
                              "cube",
                              "/home/caedes/groupmembers.zip")

    def writeAnimation(self, f, id, name, internal_name):
        """
        Write an animation to the avatar file
        """
        f.write(indent(1)+'<animation name="'+name+'" ')
        f.write('id="'+id+'" internal_name="'+internal_name+'" ')
        f.write('looped="1" speedfactor="1.0" ')
        if 'walk' in name.lower() or 'run' in name.lower():
            f.write('usevelocity="1" ')
        f.write('fadein="0.25" ')
        f.write('fadeout="0.25" />\n')

    def writeAnimations(self, f):
        """
        Write all animations to the avatar file
        """
        actions = Blender.Armature.NLA.GetActions()
        for name, action in actions.items():
            if action.name.lower() in self.actions_map:
                action_name = self.actions_map[action.name.lower()]
                action_uuid = self.action_uuids[action_name]
            else:
                action_name = action.name
                action_uuid = 'not-needed' # has to exist according to manual
            self.writeAnimation(f,
                                action_uuid,
                                action_name,
                                action.name)

    def writeProperty(self, f, name, value):
        """
        Write an avatar property
        """
        f.write(indent(1) + '<property name="'+name+'" value="'+value+'" />')

    def writeProperties(self, f):
        """
        Write all properties
        """
        if self.settings['MovementSpeed']:
            self.writeProperty(f, 'MovementSpeed', self.settings['MovementSpeed']) # needed??

        # automatic ground offset:
        # bone which should be adjusted to align with the ground
        if self.settings['basebone']:
            self.writeProperty(f, 'basebone', self.settings['basebone'])
        # avatar skeleton's  hierarchy root
        if self.settings['rootbone']:
            self.writeProperty(f, 'rootbone', self.settings['rootbone'])
        # finetuning
        if self.settings['baseoffset']:
            self.writeProperty(f, 'baseoffset', self.settings['baseoffset'])
        return
        # parametrized head turning:
        if self.settings['headbone']:
            self.writeProperty(f, 'headbone', '')
        if self.settings['neckbone']:
            self.writeProperty(f, 'neckbone', '')
        if self.settings['torsobone']:
            self.writeProperty(f, 'torsobone', '')
        if self.settings['headboneaxis']:
            self.writeProperty(f, 'headboneaxis', '') # optional
        if self.settings['neckboneaxis']:
            self.writeProperty(f, 'neckboneaxis', '') # optional
        if self.settings['torsoboneaxis']:
            self.writeProperty(f, 'torsoboneaxis', '') # optional

    def writeAvatarFile(self, f):
        """
        Write an avatar file for the selected mesh.
        """
        f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
        f.write('<avatar>\n')
        f.write(indent(1)+'<version>0.2</version>\n')
        f.write(indent(1)+'<base name="default_female" mesh="'+self.settings['mesh_file']+'" />\n')
        f.write(indent(1)+'<skeleton name="'+self.settings['skeleton_file']+'" />\n')
        #f.write(indent(1)+'<material name="male/Body" />\n')
        #f.write(indent(1)+'<material name="male/Face" />\n')
        first_face_image = self.getMesh().getData(0, True).faces[0].image
        if first_face_image:
            texture_name = os.path.basename(first_face_image.getFilename())
        else:
            texture_name = ''
        f.write(indent(1)+'<texture_body name="'+texture_name+'" />\n')
        #f.write(indent(1)+'<texture_face name="" />\n')
        f.write(indent(1)+'<appearance height="1.800000" weight="1" />\n')
        f.write(indent(1)+'<transformation position="%s" rotation="%s" \
                scale="%s" />\n' % (self.settings['translation'],
                                    self.settings['rotation'],
                                    self.settings['scale']))
        self.writeProperties(f)
        self.writeAnimations(f)
        f.write('</avatar>')

    def createAvatarFile(self, path):
        """
        Create the avatar file at the specified location.
        """
        character_name = self.settings['character_name']
        f = open(os.path.join(path, character_name + '.xml'), 'w')
        self.writeAvatarFile(f)
        f.close()

    def getMesh(self):
        """
        Get the selected mesh
        """
        selected = Blender.Object.GetSelected()
        for sel in selected:
            if sel.getType() == 'Mesh':
                return sel

    def getArmature(self):
        """
        Get the selected object's armature
        """
        bObject = self.getMesh()
        return GetArmatureObject(bObject)

    def parseSettings(self, exportSettings):
        """
        Decide settings for export
        """
        mesh = self.getMesh()
        name = mesh.getData(0, True).name
        armature_name = self.getArmature().name
        self.settings['character_name'] = mesh.name
        self.settings['mesh_file'] = name + '.mesh'
        self.settings['skeleton_file'] = armature_name + '.skeleton'
        self.settings.update(exportSettings.getDict())

    def setupAnimations(self):
        """
        Setup animations on the ogre exporter.
        """
        ogreSelection = self.ogre.meshapp.selectedObjectManager
        ogreSelection.updateSelection()
        armatureManager = ogreSelection.getArmatureAnimationProxyManager(self.getMesh().getData(True))

        armatureManager.removeProxies() # cleanup
        armatureManager.animationProxyKeyList = [] # shouldnt be needed
        armatureManager.update()

        actionList = armatureManager.getActions()
        for action in actionList:
            bAction = action.bAction
            anim = ArmatureAnimationProxy(armatureManager, action,
                                          action.getName(),
                                          action.getFirstFrame(),
                                          action.getLastFrame())
            armatureManager.addProxy(anim)
        armatureManager.savePackageSettings()

    def export(self, path, pack_name, offset, exportSettings):
        """
        Export the character and its avatar file.
        """
        b2rexpkg.start()
        self.setupAnimations()
        self.ogre.export(path, pack_name, offset)
        self.parseSettings(exportSettings)
        self.createAvatarFile(path)
        #f = open(os.path.join(path, pack_name + ".uuids"), 'w')
        #b2rexpkg.write(f)
        #f.close()

