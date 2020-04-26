from bge import logic, events
from time import clock
from mathutils import Vector, Matrix
import math
import Rasterizer
import destruction_bge as db

class P:
    target = None
   
def aim():
    
    mouse = logic.mouse
    scene = logic.getCurrentScene()
    player = scene.objects["Player"]
    eye = scene.objects["Eye"]
    player.applyRotation((0,0, -(round(mouse.position[0],2) - 0.5)))
    eye.applyRotation((round(mouse.position[1],2)- 0.5, 0, 0), True)
    mouse.position = ((0.5, 0.5))
    
    for c in player.controllers:
        if "PythonAim" == c.name:
            control = c
            
    lock = None
    for s in control.sensors:
        if "LockOn" in s.name:
            lock = s
    
    if P.target != lock.hitObject:
        P.target = lock.hitObject
        print("Locked On: ", P.target)
        
        #highlight the target somehow...
        
    #P.targetPos = lock.hitPosition
        if P.target != None:
            P.targetPos = P.target.worldPosition 
            

def addBall(act, value, isBomb, target):
    
    scene = logic.getCurrentScene()
    
    
    balls = []
    for a in act:
        
        #if a.object.name in scene.objects:
        #    o = scene.objects[a.object.namep]
        #    o.endObject()
            
        #control.activate(a)
        a.instantAddObject()
        #lastObj = scene.addObject(a.object, a.object)

        #here the ball is in the scene, change Parenting....TODO
        lastobj = a.objectLastCreated
        if isBomb:
            lastobj.worldPosition = target
        
       # last.suspendDynamics()
        #lastobj["inactive"] = False
        balls.append(lastobj)
    
    parent = None    
    for b in balls:
        if "myParent" in b.getPropertyNames():
            parent = scene.objects[b["myParent"]]
            b.setParent(parent)
            if parent.name not in db.children.keys():
                db.children[parent.name] = list()
            db.children[parent.name].append(b.name)
    
    if parent != None:
        childs = [c for c in parent.children]
        last = parent.children[-1]
        last.removeParent()    
        for c in childs:
            if c != last:
                c.removeParent()
                c.setParent(last, True, False)
        
        if isBomb:
            last["strength"] = value
        else:        
            last.linearVelocity = value    
    else:
        if isBomb:
            balls[0]["strength"] = value
        else:
            balls[0].linearVelocity = value
         
       
def shoot():

    mouse = logic.mouse
    scene = logic.getCurrentScene()
    launcher = scene.objects["Launcher"]
    for c in launcher.controllers:
        if "PythonShoot" == c.name:
            control = c
    act = []
    for a in control.actuators:
        if "Shoot" in a.name:
            act.append(a)
    
    speed = 0
    axis = launcher.worldOrientation * Vector((0, 0, -5))
    if mouse.events[events.LEFTMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
        P.startclock = clock()
    
    if mouse.events[events.LEFTMOUSE] == logic.KX_INPUT_JUST_RELEASED:
        speed = clock() - P.startclock
        print("Projectile Speed:", speed)
    
        linVelocity = axis * speed * 20 
        print(linVelocity)
        
        addBall(act, linVelocity, False, None)
        
                      
def screenshot():
    Rasterizer.makeScreenshot("shot#")

def detonate():
    
    mouse = logic.mouse
    scene = logic.getCurrentScene()
    launcher = scene.objects["Launcher"]
    for c in launcher.controllers:
        if "PythonDetonate" in c.name:
            control = c
    act = []
    for a in control.actuators:
        if "Detonate" in a.name:
            act.append(a)
            
    if mouse.events[events.RIGHTMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
        P.startclock = clock()
    
    if mouse.events[events.RIGHTMOUSE] == logic.KX_INPUT_JUST_RELEASED:
        strength = clock() - P.startclock
        print("Explosion Strength:", strength)
    
        if P.target != None:
            addBall(act, strength * 20, True, P.targetPos)
          