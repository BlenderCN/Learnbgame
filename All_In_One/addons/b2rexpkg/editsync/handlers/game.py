"""
 GameModule: Functionality related to starting up or running in game engine
 mode.
"""
from .base import SyncModule

import bpy
import os
import mathutils

class ControlFlags:
    # some controlflags from pyogp.lib.client.enums.AgentControlFlags
    AtPos   = 0x00000001
    AtNeg   = 0x00000002
    LeftPos = 0x00000004
    LeftNeg = 0x00000008
    UpPos   = 0x00000010
    UpNeg   = 0x00000020
    Fly     = 0x00002000

def processControls():
    """
    Process keyboard and mouse. Function to hook up
    inside a blender python module controller.
    """
    bpy.b2rex_session.Game.game_controls()

def processCommands():
    """
    Process incoming sim commands. Function to hook up
    inside a blender python module controller.
    """
    bpy.b2rex_session.Game.game_commands()

class GameModule(SyncModule):
    def has_game_uuid(self, obj):
        """
        Returns true if the object has the uuid game property.
        """
        for prop in obj.game.properties:
            if prop.name == 'uuid':
                return True

    def import_object(self, obname):
        """
        Import an object from a blender library (not used, example)
        """
        opath = "//cube.blend\\Object\\" + obname
        s = os.sep
        dpath = bpy.utils.script_paths()[0] + \
            '%saddons%sb2rexpkg%sdata%sblend%scube.blend\\Object\\' % (s, s, s, s, s)

        # DEBUG
        #print('import_object: ' + opath)

        bpy.ops.wm.link_append(
                filepath=opath,
                filename=obname,
                directory=dpath,
                filemode=1,
                link=False,
                autoselect=True,
                active_layer=True,
                instance_groups=True,
                relative_path=True)
                
       # for ob in bpy.context.selected_objects:
       #     ob.location = bpy.context.scene.cursor_location

    def game_controls(self):
        """
        Process keyboard and mouse controls for the game engine.
        """
        from bge import logic as G
        from bge import render as R
        from bge import events

        sensitivity = 1.0    # mouse sensitivity
        speed = 0.2    # walk speed
        owner = G.getCurrentController().owner
        camera = owner.children[0]

        simrt = bpy.b2rex_session.simrt
        session = bpy.b2rex_session

        if "oldX" not in owner:
            G.mouse.position = (0.5,0.5)
            owner["oldX"] = 0.0
            owner["oldY"] = 0.0
            owner["minX"] = 10.0
            owner["minY"] = 10.0
            owner["flying"] = False
            owner["flags"] = 0
        else:
            
            # clamp camera to above surface
            #if owner.position[2] < 0:
            #    owner.position[2] = 0
                
            x = 0.5 - G.mouse.position[0]
            y = 0.5 - G.mouse.position[1]
            
            if abs(x) > abs(owner["minX"]) and abs(y) > abs(owner["minY"]):
            
                x *= sensitivity
                y *= sensitivity
                
                # Smooth movement
                #owner['oldX'] = (owner['oldX']*0.5 + x*0.5)
                #owner['oldY'] = (owner['oldY']*0.5 + y*0.5)
                #x = owner['oldX']
                #y = owner['oldY']
                 
                # set the values
                owner.applyRotation([0, 0, x], False)
                #camera.applyRotation([y, 0, 0], True)
                
                _rotmat = owner.localOrientation
                #_roteul = _rotmat.to_euler()
                # XXX to_quaternion in 257?
                q = _rotmat.to_quat()
                #rot = session.unapply_rotation(_roteul)
            #    print(rot)
                simrt.BodyRotation([q.x, q.y, q.z, q.w])
            
            else:
                owner["minX"] = x
                owner["minY"] = y
                
            # Center mouse in game window
            G.mouse.position = (0.5,0.5)
            
            # keyboard control
            keyboard = G.keyboard.events

            # walk forwards / backwards
            if keyboard[events.WKEY]:
                owner['flags'] |= ControlFlags.AtPos
            else:
                owner['flags'] &= ~ControlFlags.AtPos
            if keyboard[events.SKEY]:
                owner['flags'] |= ControlFlags.AtNeg
            else:
                owner['flags'] &= ~ControlFlags.AtNeg

            # strafe
            if keyboard[events.AKEY]:
                owner['flags'] |= ControlFlags.LeftPos
            else:
                owner['flags'] &= ~ControlFlags.LeftPos
            if keyboard[events.DKEY]:
                owner['flags'] |= ControlFlags.LeftNeg
            else:
                owner['flags'] &= ~ControlFlags.LeftNeg

            # fly up
            if keyboard[events.EKEY]:
                owner['flags'] |= ControlFlags.UpPos
            else:
                owner['flags'] &= ~ControlFlags.UpPos

            # fly down
            if keyboard[events.CKEY]:
                owner['flags'] |= ControlFlags.UpNeg
            else:
                owner['flags'] &= ~ControlFlags.UpNeg

            # toggle fly
            if keyboard[events.FKEY]:
                if not owner['f_pressed']:
                    owner['flying'] = not owner['flying']
                    owner['f_pressed'] = True
            else:
                owner['f_pressed'] = False

            # set flying control flag
            if owner['flying']:
                owner['flags'] |= ControlFlags.Fly
            else:
                owner['flags'] &= ~ControlFlags.Fly
            # stop
            #if not action and not owner['flying']:
            if owner['flags']:
                simrt.SetFlags(owner['flags'])
            else:
                simrt.Stop()


    def game_commands(self):
        """
        Process incoming sim queue commands.
        """
        from bge import logic as G
        from bge import render as R
        from bge import events

        scene = G.getCurrentScene()

        simrt = bpy.b2rex_session.simrt
        session = bpy.b2rex_session

        commands = simrt.getQueue()

        for command in commands:
            if command[0] == "pos":
                self.processPosition(scene, *command[1:])


    def find_object(self, scene, obj_uuid):
        """
        Find the object in the given scene with given uuid.
        """
        for obj in scene.objects:
            if obj.get('uuid') == obj_uuid:
                return obj


    def processPosition(self, scene, objid, pos, rot=None):
        """
        Process a position command.
        """
        session = bpy.b2rex_session
        obj = self.find_object(scene, objid)
        if obj:
            obj.worldPosition = session._apply_position(pos)
            if rot:
               b_q = mathutils.Quaternion((rot[3], rot[0], rot[1], rot[2]))
               obj.worldOrientation = b_q


    def ensure_game_uuid(self, context, obj):
        """
        Ensure the uuid is set as a game object property.
        """
        if obj.opensim.uuid:
            if not self.has_game_uuid(obj):
                obj.select = True
                context.scene.objects.active = obj
                bpy.ops.object.game_property_new()
                # need to change type and then get the property otherwise
                # it will stay in the wrong class
                obj.game.properties[-1].type = 'STRING'
                prop = obj.game.properties[-1]
                prop.name = 'uuid'
                prop.value = obj.opensim.uuid
                obj.select = False


    def prepare_avatar(self, context, obj):
        """
        Prepare an avatar for the game engine. Creates the necessary
        logic bricks.
        """
        # add sensors
        if not len(obj.game.sensors):
            bpy.ops.logic.sensor_add( type='ALWAYS'  )
            sensor = obj.game.sensors[-1]
            sensor.use_pulse_true_level = True
        # add controllers
        if not len(obj.game.controllers):
            for name in ['processCommands', 'processControls']:
                bpy.ops.logic.controller_add( type='PYTHON'  )
                controller = obj.game.controllers[-1]
                controller.mode = 'MODULE'
                controller.module = 'b2rexpkg.editsync.handlers.game.' + name
                controller.link(sensor=obj.game.sensors[-1])


    def prepare_object(self, context, obj):
        """
        Prepare the given object for running inside the
        game engine.
        """
        self.ensure_game_uuid(context, obj)
        if obj.opensim.uuid and obj.opensim.uuid == self._parent.agent_id:
            self.prepare_avatar(context, obj)


    def start_game(self, context):
        """
        Start blender game engine, previously setting up game
        properties for opensim.
        """
        # save selected for later
        selected = list(context.selected_objects)

        # unselect all
        for obj in selected:
            obj.select = False

        # prepare each object
        for obj in bpy.data.objects:
            self.prepare_object(context, obj)

        # restore initial selection
        for obj in selected:
            obj.select = True

        # start the game
        bpy.ops.view3d.game_start()
