from bpy import types, props, utils, ops, path
from bpy.types import Object, Scene
from . import destruction_data as dd
from . import voronoi
import bpy
import os
import random
from bpy_extras import mesh_utils
from operator import indexOf
import mathutils
from mathutils import Vector, Quaternion, Euler, Matrix, geometry
import math
import bisect
import sys
import bmesh

#import bgl
#import blf

#since a modification of fracture_ops is necessary, redistribute it
from . import fracture_ops as fo
imported = True
try: 
    from bpy.app.handlers import persistent
except ImportError:
    imported = False
    
from object_destruction.fracture_cell import fracture_cell_setup

#def getGrounds(obj):
##   # grounds = bpy.context.scene.objects[obj.name].destruction.grounds
#    grounds = obj.destruction.grounds.keys()
#    print("GET GROUNDS: ", grounds)
#    ret = []
#    for ground in grounds:
#        g = dd.Ground()
#        g.name = ground
#        
#        bGround = bpy.context.scene.objects[ground].bound_box.data.to_mesh(bpy.context.scene, False, 'PREVIEW')
#        for e in bGround.edges:
#            vStart = bGround.vertices[e.vertices[0]].co
#            vEnd = bGround.vertices[e.vertices[1]].co
#            g.edges.append((vStart, vEnd))
#        ret.append(g)
#    #print("RET", ret)
#    return ret

#def getTargets(obj):
#    targets = obj.destruction.destructorTargets
#    for t in targets:
#        props = dd.BGEProps()
#        props.hierarchy_depth = t.hierarchy_depth
#        props.dead_delay = t.dead_delay
#        props.radius = t.radius
#        props.min_radius = t.min_radius
#        props.modifier = t.modifier
#        props.acceleration_factor = t.acceleration_factor

def bgePropsScene(scene):
    props = dd.BGEProps()
    props.custom_ball = scene.custom_ball
    props.hideLayer = scene.hideLayer
    props.collapse_delay = scene.collapse_delay
    props.use_gravity_collapse = scene.useGravityCollapse
    
    return props
        
def bgeProps(ob):
    props = dd.BGEProps()
    
    props.cluster_dist = ob.destruction.cluster_dist[:] 
    props.cluster = ob.destruction.cluster
    props.is_backup_for = ob.destruction.is_backup_for
  
    props.use_collision_compound = ob.game.use_collision_compound
   
    props.was_compound = ob.destruction.wasCompound
    props.grid_bbox = ob.destruction.gridBBox[:]
    props.grid_dim = ob.destruction.gridDim[:]
    props.individual_override = ob.destruction.individual_override
    props.radius = ob.destruction.radius
    props.min_radius = ob.destruction.min_radius
    props.modifier = ob.destruction.modifier
    props.hierarchy_depth = ob.destruction.hierarchy_depth
    props.glue_threshold = ob.destruction.glue_threshold
   
    props.backup = ob.destruction.backup
    props.children = ob.destruction.children.keys()
    props.ascendants = ob.destruction.ascendants.keys()
    props.origLoc = ob.destruction.origLoc[:]
    
    if ob.data: 
        props.mesh_name = ob.data.name
    else:
        props.mesh_name = ""
        
    props.acceleration_factor = ob.destruction.acceleration_factor
    props.ground_connectivity = ob.destruction.groundConnectivity
    props.destroyable = ob.destruction.destroyable
    props.destructor = ob.destruction.destructor
    props.is_ground = ob.destruction.isGround
    props.flatten_hierarchy = ob.destruction.flatten_hierarchy
    props.dead_delay = ob.destruction.dead_delay
    props.destructor_targets = ob.destruction.destructorTargets.keys() #getTargets(ob)
    props.grounds = ob.destruction.grounds.keys() #getGrounds(ob)
   

    props.edges = []
    if (props.is_ground): #only then !! mostly is lowpoly or 1 face only
        for e in ob.data.edges:
            v1 = ob.data.vertices[e.vertices[0]].co.to_tuple()
            v2 = ob.data.vertices[e.vertices[1]].co.to_tuple()
            props.edges.append([v1, v2])
    
    if ob.data:
        props.bbox = ob.bound_box.data.dimensions[:]
    else:
        props.bbox = (0, 0, 0)
    
    return props
    
    
#do the actual non-bge processing here
class Processor():
          
    def processDestruction(self, context, impactLoc):
        
        dd.DataStore.impactLocation = impactLoc   
        parts = context.active_object.destruction.partCount
        #make an object backup if necessary (if undo doesnt handle this)
#        granularity = context.active_object.destruction.pieceGranularity
#        thickness = context.active_object.destruction.wallThickness
#        destroyable = context.active_object.destruction.destroyable
#        roughness = context.active_object.destruction.roughness
#        crack_type = context.active_object.destruction.crack_type
#        groundConnectivity = context.active_object.destruction.groundConnectivity
        cubify = context.active_object.destruction.cubify
#        jitter = context.active_object.destruction.jitter
#        cut_type = context.active_object.destruction.cut_type
#        volume = context.active_object.destruction.voro_volume
        
        objects = []
        #determine HERE, which objects will be decomposed
        transMode = context.active_object.destruction.transmitMode
        if transMode == context.active_object.destruction.transModes[0][0]: #self
            if context.selected_objects != None:
                sel = [o for o in context.selected_objects]
                for o in sel:
                    if o != context.active_object:
                        o.select = False  
            
           # print("CTX:", context.object)          
            objects = [context.active_object]
            
        else:
            self.copySettings(context, objects)
        
        if (parts > 1) or ((parts == 1) and cubify):
            print("OBJECTS: ", objects)
            
            #restore = False
            #ifcontext.active_object.destruction.destructionMode == 'DESTROY_C' or \
            #context.active_object.destruction.destructionMode == 'DESTROY_F':
            #restore = o.parent == None
            
            #for some reason zeroizing the location is necessary for cell fracture in my addon
            
            area = None
            for a in context.screen.areas:
                if a.type == 'PROPERTIES':
                    area = a
                
            space = None
            for s in area.spaces:
                if s.type == 'PROPERTIES':
                    s.context = 'PHYSICS'
                    s.pin_id = context.object
                    s.use_pin_id = True
                    space = s
            
            if context.scene.hideLayer != 1:
                context.scene.layers = self.layer(context.scene.hideLayer, True)
                
            self.destroy(context, objects, 0)   
           
            if context.scene.hideLayer != 1:
                context.scene.layers = self.layer(1)
           
            space.use_pin_id = False
            space.pin_id = None
            
        return None
    
    def destroy(self, context, objects, level):
        from bpy import data
        
        modes = {DestructionContext.destModes[0][0]: 
                    "self.applyFracture(context, obj)",
                 DestructionContext.destModes[1][0]: 
                     "self.applyExplo(context, obj)",
                 DestructionContext.destModes[2][0]: 
                     "self.applyVoronoi(context, obj, True)",  
                 DestructionContext.destModes[3][0]: 
                     "self.applyVoronoi(context, obj, False)",
                 DestructionContext.destModes[4][0]: 
                     "self.applyCellFracture(context, obj, level)",  
                 DestructionContext.destModes[5][0]:
                     "self.applyLooseParts(context, obj)" } 
        #according to mode call correct method
        
        if context.active_object.destruction.destructionMode != 'DESTROY_L':
            for o in data.objects:
                if o in objects:
                                   
                    o.select = True
                    ops.object.origin_set(type = 'ORIGIN_GEOMETRY', center = 'BOUNDS')
                    o.select = False
                    
                    if o.parent != None:
                        o.parent.destruction.restore = True
                            
                    o.destruction.restoreLoc = o.location.copy()
                    o.location = mathutils.Vector((0,0,0))
                    #move also the volume object RELATIVE to the base object
                    if o.destruction.voro_volume != "" and o.destruction.voro_volume in data.objects:
                        vol = data.objects[o.destruction.voro_volume]
                        if vol.destruction.move_name == "":
                            vol.destruction.move_name = str(o.name)
                            vol.location -= mathutils.Vector(o.destruction.restoreLoc)
                    
                    print("Memorizing...", o.destruction.restoreLoc, o.location)
                            
        context.scene.update()
        
        
        #hack for boolean fracture
        if context.active_object == None:
            for o in objects:
               if o.name in context.scene.objects:
                   context.scene.objects.active = context.scene.objects[o.name]
                   break
               
        ob = context.active_object
        if ob == None:
            #error case, if active_object does not intersect with original geometry
            return objects  
                   
        mode = ob.destruction.destructionMode
        ctx = ob.destruction.cell_fracture
            
        recursion = ctx.recursion
        recursion_chance = ctx.recursion_chance
        recursion_chance_select = ctx.recursion_chance_select
        use_remove_original = ctx.use_remove_original
        recursion_clamp = ctx.recursion_clamp
        
        obj = objects
        objects_recursive = eval(modes[mode])
                     
        if level < recursion:
            objects_recurse_input = [(i, o) for i, o in enumerate(objects_recursive)]
         
            if recursion_chance != 1.0:
                from mathutils import Vector
                if recursion_chance_select == 'RANDOM':
                    random.shuffle(objects_recurse_input)
                elif recursion_chance_select == {'SIZE_MIN', 'SIZE_MAX'}:
                    objects_recurse_input.sort(key=lambda ob_pair:
                        (Vector(ob_pair[1].bound_box[0]) -
                         Vector(ob_pair[1].bound_box[6])).length_squared)
                    if recursion_chance_select == 'SIZE_MAX':
                        objects_recurse_input.reverse()
                elif recursion_chance_select == {'CURSOR_MIN', 'CURSOR_MAX'}:
                    print(recursion_chance_select)
                    c = scene.cursor_location.copy()
                    objects_recurse_input.sort(key=lambda ob_pair:
                        (ob_pair[1].location - c).length_squared)
                    if recursion_chance_select == 'CURSOR_MAX':
                        objects_recurse_input.reverse()
                    
                    
                objects_recurse_input[int(recursion_chance * len(objects_recurse_input)):] = []
                objects_recurse_input.sort()
               # print("LEN", len(objects_recurse_input), recursion_chance)
            
                # reverse index values so we can remove from original list.
                objects_recurse_input.reverse()
            
            #objects_recursive = []
            objects_input = []
            for i, o in objects_recurse_input:
                  
                objects_input.append(o)
                if context.active_object == None:
                    context.scene.objects.active = o
                
            if recursion_clamp and len(objects_recursive) >= recursion_clamp:
                return objects_recursive
 
            objects_recursive += self.destroy(context, objects_input, level + 1)
            
        
        
            #if context.active_object != None:
            #    mode = context.active_object.destruction.destructionMode
            #    if mode == 'DESTROY_C':
            #        ctx = context.active_object.destruction.cell_fracture
            #        if ctx.use_interior_vgroup or ctx.use_sharp_edges:
            #           fracture_cell_setup.cell_fracture_interior_handle(objects,
            #                    use_interior_vgroup=ctx.use_interior_vgroup,
            #                    use_sharp_edges=ctx.use_sharp_edges,
            #                    use_sharp_edges_apply=ctx.use_sharp_edges_apply)
        
        if mode != 'DESTROY_L':      
            for o in data.objects:
                if o.name.startswith("P_"):
                    if (not o.destruction.restore):
                        backup = data.objects[o.destruction.backup]
                        o.location = mathutils.Vector(backup.destruction.restoreLoc)
                        #restore also the volume object RELATIVE to the base object
                        if backup.destruction.voro_volume != "" and backup.destruction.voro_volume in data.objects:
                            vol = data.objects[backup.destruction.voro_volume]
                            if vol.destruction.move_name == backup.destruction.orig_name:
                                vol.destruction.move_name = ""
                                vol.location += mathutils.Vector(backup.destruction.restoreLoc)
                        
                        backup.destruction.restoreLoc = mathutils.Vector((0,0,0)) 
                        print("Restoring...", o.location)
                        o.destruction.restore = True
                
        context.scene.update()
                   
        return objects_recursive

        
        
#    def applyToChildren(self, ob, objects, transMode):
#        for c in ob.children:
#           if transMode == ob.destruction.transModes[3][0]:
#               self.applyToChildren(c, objects, transMode) #apply recursively...
#           objects.append(c)
           
    def copySettings(self, context, objects):
        
        sel = [o for o in context.selected_objects]
        for o in sel:
            o.select = False
        
        for o in sel:
            if o.type == "MESH":         
                o.select = True
                context.scene.objects.active = o
                transMode = context.active_object.destruction.transmitMode
                if transMode == context.active_object.destruction.transModes[1][0] and \
                o.destruction.is_backup_for == "": #selected and no backup
                    if objects != None:
                        objects.append(o)
                     #apply values of current object to all selected objects
                    o.destruction.cubify = context.active_object.destruction.cubify 
                    o.destruction.remesh_depth = context.active_object.destruction.remesh_depth
                    o.destruction.voro_path = context.active_object.destruction.voro_path
                    o.destruction.voro_exact_shape = context.active_object.destruction.voro_exact_shape
                    o.destruction.voro_particles = context.active_object.destruction.voro_particles
                    o.destruction.deform = context.active_object.destruction.deform
                    o.destruction.cluster_dist = context.active_object.destruction.cluster_dist
                    o.destruction.cluster = context.active_object.destruction.cluster
                    o.destruction.dynamic_mode = context.active_object.destruction.dynamic_mode
                    o.destruction.destructionMode = context.active_object.destruction.destructionMode
                           
#                elif transMode == context.object.destruction.transModes[2][0] or \ #not supported atm
#                transMode == context.object.destruction.transModes[3][0]:
#                    objects.append(o)
#                    self.applyToChildren(o, objects, transMode)
                o.select = False
                   
    def createBackup(self, context, obj):
        
        sel = []
        if context.selected_objects != None:
            for o in context.selected_objects:
                if o != obj:
                    sel.append(o)
                    o.select = False
                
        obj.select = True  
        context.scene.objects.active = obj
          
        ops.object.duplicate()
        backup = context.active_object
        backup.name = obj.name
        
        if len(backup.name.split(".")) == 1:
            backup.name += ".000"
        
        if obj.destruction.flatten_hierarchy or context.scene.hideLayer == 1:
            context.scene.objects.unlink(backup)
        print("Backup created: ", backup)
        
        for o in sel:
            o.select = True
        
        return backup
        
    def previewExplo(self, context, parts, thickness):
       
        print("previewExplo", parts, thickness)
        
        context.active_object.modifiers.new("Particle", 'PARTICLE_SYSTEM')
        context.active_object.modifiers.new("Explode", 'EXPLODE')
        
        if thickness > 0:
            
            context.active_object.modifiers.new("Solidify", 'SOLIDIFY')
            explode = context.active_object.modifiers[len(context.active_object.modifiers)-2]
            solidify = context.active_object.modifiers[len(context.active_object.modifiers)-1]
        
        else:
            explode = context.active_object.modifiers[len(context.active_object.modifiers)-1]
        
        #get modifier stackindex later, for now use a given order.
        settings = context.active_object.particle_systems[0].settings        
        settings.count = parts
        settings.frame_start = 2.0
        settings.frame_end = 2.0
        settings.distribution = 'RAND'
       
        explode.use_edge_cut = True
       
        if thickness > 0:
            solidify.thickness = thickness    
    
    def explo(self, context, obj, partCount, granularity, thickness):
                   
        context.scene.objects.active = obj # context.object
        currentParts = [context.active_object.name]
        
        if granularity > 0:
            ops.object.mode_set(mode = 'EDIT')
            ops.mesh.subdivide(number_cuts = granularity)
            ops.object.mode_set()

            #explosion modifier specific    
        self.previewExplo(context, partCount, thickness)
        parts = self.separateExplo(context, thickness)
        
        for o in context.scene.objects:
            o.select = True
        ops.object.origin_set(type = 'ORIGIN_GEOMETRY')
        for o in context.scene.objects:
            o.select = False
             
        return parts
            
    
    def looseParts(self, context, parent, depth):
        
        if len(parent.children) == 0:
            print("Returning")
            return
        
        if parent.type == 'EMPTY':
            if not parent.name.startswith("P_"):
                parent.name = "P_" + str(depth) + "_S_" + parent.name + ".000"
                parent.destruction.destroyable = True
                parent.destruction.flatten_hierarchy = context.active_object.destruction.flatten_hierarchy
              #  print("FLatten", parent.destruction.flatten_hierarchy)
              
        ops.object.select_all(action = 'DESELECT')
        
        childs = [o for o in parent.children]
        for obj in childs:               
            if obj.type == 'MESH':
                if not obj.name.startswith("S_"):
                    obj.name = "S_" + obj.name
                
                if obj.destruction.deform:
                    obj.game.physics_type = 'SOFT_BODY'
                else:
                    obj.game.physics_type = 'RIGID_BODY'
                obj.game.collision_bounds_type = 'CONVEX_HULL'
                obj.game.collision_margin = 0.0 
                obj.game.radius = 0.01
                obj.game.use_collision_bounds = True
                
                obj.select = True
                    
        ops.object.duplicate()      
        ops.object.join() # should join the dupes only !
        name = context.active_object.name
        obName = name.split(".")[0]
        context.active_object.name = obName + ".000" # this name is expected to be set
        print("Backup", context.active_object.name)
        
        for c in parent.children:
            if "." not in c.name:
                c.name += ".000" #rely on blender unique naming here!
            if context.scene.hideLayer != 1 and not c.name.endswith(".000"):
                c.layers = self.layer(context.scene.hideLayer)
        self.setCompound(parent, context.scene.hideLayer == 1 and not parent.destruction.flatten_hierarchy)
        context.active_object.destruction.is_backup_for = parent.name
        parent.destruction.backup = context.active_object.name
        
        if context.scene.hideLayer == 1:
            context.active_object.use_fake_user = True
            context.scene.objects.unlink(context.active_object)
        #else:
        #    if depth > 0:
        #        context.active_object.layers = self.layer(context.scene.hideLayer)
        
        for obj in childs: 
            print("Descending")
            self.looseParts(context, obj, depth + 1)
                   
    def applyLooseParts(self, context, objects):
        
        for obj in objects:
            if obj.parent != None and obj.parent.type == "EMPTY":
                self.looseParts(context, obj.parent, 0)
    
    def setLargest(self, largest, backup):
        bEnd = int(backup.name.split(".")[1])
        lEnd = int(largest)
        if bEnd > lEnd:
            if bEnd < 10:
                largest = "00" + str(bEnd)
            if bEnd < 100:
                largest = "0" + str(bEnd)
            else:
                largest = str(bEnd)
        return largest
    
    def applyCellFracture(self, context, objects, level):
        
        parts = []
        for obj in objects:
            orig_name = str(obj.name)
            parentName, nameStart, largest, bbox = self.prepareParenting(context, obj)
            backup = obj
            
            backup.destruction.orig_name = orig_name
            
            if len(backup.name.split(".")) == 1:
                backup.name += ".000"
            
            largest = self.setLargest(largest, backup)
            
            materialname = backup.destruction.inner_material
            mat_index = self.getMatIndex(materialname, backup)
            
            if obj.destruction.cubify:
                parts.extend(self.cubify(context, obj, bbox, 1, mat_index, materialname, level))
            else:
                parts.extend(self.fracture_cells(context, obj, mat_index, level))
            
            if obj.destruction.flatten_hierarchy or context.scene.hideLayer == 1:
                if not obj.destruction.cubify:
                    context.scene.objects.unlink(backup)
            else:
                oldSel = backup.select
                context.scene.objects.active = backup
                backup.select = True
                ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                backup.select = oldSel
            
            self.doParenting(context, parentName, nameStart, bbox, backup, largest, obj)
        return parts
                   
    def applyVoronoi(self, context, objects, wall):
        
        partCount = context.active_object.destruction.partCount
        volume = context.active_object.destruction.voro_volume
        
        parts = []
        for obj in objects:
            print("applyVoronoi", obj,  partCount, volume, wall)
            obj.destruction.wall = wall
            
            #prepare parenting
            orig_name = str(obj.name)
            parentName, nameStart, largest, bbox = self.prepareParenting(context, obj)
            if parentName == None:
                continue
            
            backup = obj
            
            backup.destruction.orig_name = orig_name
            
            print("BACKUP", backup.name)
            
           # print("LEN: ", len(backup.name.split(".")))
            if len(backup.name.split(".")) == 1:
                backup.name += ".000"
            
            if backup.name.endswith(".000"):
                print("ORIGINAL", obj.name)    
                obj.destruction.boolean_original = obj.name
            
            largest = self.setLargest(largest, backup)
            
            oldSel = backup.select
            context.scene.objects.active = backup
            backup.select = True
            ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            backup.select = oldSel
            
            materialname = backup.destruction.inner_material
            
            if not wall:
                mat_index = self.getMatIndex(materialname, backup)
            else:
                #regular voronoi, handle mat assignment afterwards (because no bool involved)
                mat_index = 0
            
            if obj.destruction.cubify:
                parts.extend(self.cubify(context, obj, bbox, partCount, mat_index, materialname))
            else:    
                parts.extend(voronoi.voronoiCube(context, obj, partCount, volume, wall, mat_index))
            
            origLoc = mathutils.Vector(obj.destruction.origLoc)
            
            if obj.destruction.flatten_hierarchy or context.scene.hideLayer == 1:
                backup.use_fake_user = True
                #if not obj.destruction.cubify:
                context.scene.objects.unlink(backup)
                
            elif context.scene.hideLayer != 1:
                def deselect(o):
                    o.select = False
                
                def select(o):
                    o.select = True
                
                if backup.name.endswith(".000"): #first backup only    
                    [deselect(o) for o in data.objects if o.name.startswith("S_")]
                    backup.select = True
                    ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
                    backup.select = False
                    
            #do the parenting
            self.doParenting(context, parentName, nameStart, bbox, backup, largest, obj) 
            
            if context.scene.hideLayer != 1 and not obj.destruction.flatten_hierarchy:
                #select from data because other selections seem to be ignored because of layers 
                [select(o) for o in data.objects if o.name.startswith("S_") and o != backup]           
                ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')          
                [deselect(o) for o in data.objects if o.name.startswith("S_")] 
        
        return parts
        
    def applyExplo(self, context, objects):
        #create objects from explo by applying it(or by loose parts)
        #check modifier sequence before applying it 
        #(if all are there; for now no other modifiers allowed in between)
        
        partCount = context.active_object.destruction.partCount
        granularity = context.active_object.destruction.pieceGranularity 
        thickness = context.active_object.destruction.wallThickness
        
        parts = []
        for obj in objects:
            print("applyExplo", obj,  partCount, granularity, thickness)
            
            #prepare parenting
            parentName, nameStart, largest, bbox = self.prepareParenting(context, obj)
            backup = self.createBackup(context, obj)
            
            backup.destruction.orig_name = str(obj.name)
            
            largest = self.setLargest(largest, backup)
           
            if obj.destruction.cubify:
              parts.extend(self.cubify(context, obj, bbox, partCount, 0))
            else:
              parts.extend(self.explo(context, obj, partCount, granularity, thickness))
              
            if obj.destruction.use_debug_redraw:
                context.scene.update()
                obj.destruction._redraw_yasiamevil()
                    
            #do the parenting, could use the found parts instead, TODO
            self.doParenting(context, parentName, nameStart, bbox, backup, largest, obj) 
        return parts
    
    def separateExplo(self, context, thickness): 
        
        explode = context.active_object.modifiers[len(context.active_object.modifiers)-1]
        if thickness > 0:
            explode = context.active_object.modifiers[len(context.active_object.modifiers)-2]
            solidify = context.active_object.modifiers[len(context.active_object.modifiers)-1]
        
        #if object shall stay together
        settings = context.active_object.particle_systems[0].settings  
        settings.physics_type = 'NO'
        settings.normal_factor = 0.0
        
        context.scene.frame_current = 2
       
        ctx = context.copy()
        ctx["object"] = context.active_object
        ops.object.modifier_apply(ctx, apply_as='DATA',  modifier = explode.name)
        
        if thickness > 0:
            ctx = context.copy()
            ctx["object"] = context.active_object
            ops.object.modifier_apply(ctx, apply_as='DATA', modifier = solidify.name)
        
        #must select particle system before somehow
        ctx = context.copy()
        ctx["object"] = context.active_object
        ops.object.particle_system_remove(ctx) 
        ops.object.mode_set(mode = 'EDIT')
        ops.mesh.select_all(action = 'DESELECT')
        #omit loose vertices, otherwise they form an own object!
        ops.mesh.select_loose_verts()
        ops.mesh.delete(type = 'VERT')
        ops.mesh.select_all(action = 'SELECT')
        ops.mesh.separate(type = 'LOOSE')
        ops.object.mode_set()
        print("separated") 
        
        #find new parts and return them, needed for recursion
        if context.active_object != None:
            oldPar = context.active_object.parent
            nameStart = context.active_object.name.split(".")[0] 
            parts = [c for c in context.scene.objects if self.isRelated(c, context, nameStart, oldPar)]
            return parts
        return [] # error case 
        
    def layer(self, n, keepFirst = False):
        ret = []
        for i in range(0, 20):
            if keepFirst and i == 0:
               ret.append(True)
            elif i == n-1:
                ret.append(True)
            else:
                ret.append(False)
        return ret       
    
    def doParenting(self, context, parentName, nameStart, bbox, backup, largest, obj):
        from bpy import data
        
        print("Largest: ", largest)    
        
        parent = None
        if context.active_object == None:
            parent = backup.parent
        else:
            parent = context.active_object.parent
        
        ops.object.add(type = 'EMPTY') 
        context.active_object.game.physics_type = 'STATIC'            
        context.active_object.game.radius = 0.01  
        context.active_object.game.use_ghost = True
              
        context.active_object.name = parentName   
        
        print("PARENT: ", parent)
        
        context.active_object.parent = parent
        context.active_object.destruction.gridBBox = bbox
        backup.destruction.is_backup_for = context.active_object.name
        
        #get the first backup, need that position
        pos = mathutils.Vector((0.0, 0.0, 0.0))
        if parent == None:
            for o in data.objects:
               if o.destruction != None:
                   if o.destruction.is_backup_for == "P_0_" + nameStart + "." + largest:# + ".000":
                       pos = o.location
                       #if o.destruction.flatten_hierarchy or context.scene.hideLayer == 1:
                       pos += mathutils.Vector(o.destruction.origLoc) #needed for voronoi
                       o.destruction.origLoc = mathutils.Vector((0, 0, 0))
            print("EMPTY Pos: ", pos)
            context.active_object.location = pos
        #else:
        #    pos = Vector((0.0, 0.0, 0.0))
                 
        oldPar = parent
        
        parent = context.active_object
        parent.destruction.pos = obj.destruction.pos
        parent.destruction.destroyable = True
        parent.destruction.partCount = obj.destruction.partCount
        parent.destruction.wallThickness = obj.destruction.wallThickness
        parent.destruction.pieceGranularity = obj.destruction.pieceGranularity
        parent.destruction.destructionMode = obj.destruction.destructionMode
        parent.destruction.roughness = obj.destruction.roughness
        parent.destruction.crack_type = obj.destruction.crack_type
        
        parent.destruction.gridDim = obj.destruction.gridDim
        parent.destruction.isGround = obj.destruction.isGround
        parent.destruction.destructor = obj.destruction.destructor
        parent.destruction.cubify = obj.destruction.cubify
        parent.destruction.flatten_hierarchy = obj.destruction.flatten_hierarchy
        parent.destruction.backup = backup.name
        parent.destruction.deform = obj.destruction.deform
        parent.destruction.cluster_dist = obj.destruction.cluster_dist
        parent.destruction.cluster = obj.destruction.cluster
        parent.destruction.dynamic_mode = obj.destruction.dynamic_mode
      #  parent.destruction.cell_fracture = obj.destruction.cell_fracture
        
        
        #distribute the object mass to the single pieces, equally for now
        #mass = backup.game.mass / backup.destruction.partCount
        
        oldBackupParent = backup.parent
        backupParent = context.active_object
        context.scene.objects.active = obj
        
        #polyList = [p for p in backup.data.polygons]
         
        if not obj.destruction.flatten_hierarchy:
            parent.layers = self.layer(context.scene.hideLayer)
    
        [self.applyDataSet(context, c, largest, parentName, pos, backup) for c in context.scene.objects if 
         self.isRelated(c, context, nameStart, oldPar)] 
         
        if (not obj.destruction.flatten_hierarchy) and context.scene.hideLayer != 1:
           # backup.name += "backup"
            backup.parent = backupParent
            
            
            temp = obj.name.split(".")[0]
            start = temp.split("_")[1]
            
            if oldBackupParent != None: 
                temp = oldBackupParent.name.split(".")[0]
                bstart = temp.split("_")[3]
            else:
                bstart = start
           
            
            print(start, bstart)
            if backupParent.name.startswith("P_0_") and start == bstart: 
                #only non generated parents may move their backup back
                print("Moving back...")
                backup.layers = self.layer(1)
        else:
            backup.use_fake_user = True
          
        #deactivate old compound settings always (not only if flatten hierarchy)
        if parent.parent != None and context.scene.hideLayer == 1: #and \
        #parent.destruction.flatten_hierarchy:
            self.delCompound(parent.parent)
        
        
        if backup.name not in context.scene.backups:
            prop = context.scene.backups.add()
            prop.name = backup.name
        
        #re-assign compound if parent is fractured
        if backup.game.use_collision_compound and context.scene.hideLayer == 1:
            self.setCompound(parent.parent)
             
        comp = self.setCompound(parent)
        
        if not obj.destruction.flatten_hierarchy and context.scene.hideLayer != 1:
            #backup.game.use_collision_compound = False
            if not comp:
                self.setBackupCompound(parent)
            #if backup.name.endswith(".000"):
            #    backup.select = True
            #    ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
            #    backup.select = False
        
        return parent
    
    def delCompound(self, parent):
        for c in parent.children:
            if c.game.use_collision_compound:
                print("WasCompound", c.name)
                c.destruction.wasCompound = True
                c.game.use_collision_compound = False
            self.delCompound(c)
    
    def setCompound(self, parent, delOld=False):
        loc = mathutils.Vector((0, 0, 0)) 
        
        #set compound at topmost position when groundconnectivity is enabled
        if parent.destruction.groundConnectivity and bpy.context.scene.useGravityCollapse:
            backup = bpy.context.scene.objects[parent.destruction.backup]
            dim = backup.bound_box.data.dimensions
            loc = mathutils.Vector(0, 0, dim[2]/2)
            print("LOC: ", loc) 
        
        mindist = sys.maxsize
        closest = None
        
        #???? deleting "wrong" backup compounds
        #for n in bpy.context.scene.backups:
        #    if n.name in bpy.context.scene.objects:
        #        o = bpy.context.scene.objects[n.name]
        #        if o.game.use_collision_compound:
        #            return True
        
        #childs = []
        #if parent.parent != None:
        childs = parent.destruction.ascendants # old children are potential backups     
        
        for c in parent.children:
            
            bName = c.name
            if c.name.startswith("P_"): # since we still have P_ members, use the backup name
                bName = c.destruction.backup
            
            parEnd = parent.name.split(".")[1]
            obEnd = bName.split(".")[1] 
            
           # print(parent.name, bName, bName in childs)
            if c.type == 'MESH' and not bName in childs and parEnd != obEnd: # c.name.endswith(".000"):
                if delOld and c.game.use_collision_compound:
                    c.game.use_collision_compound = False
                    c.destruction.wasCompound = True
                                    
                dist = (loc - c.location).length
                # print(mindist, dist, c)
                if dist < mindist:
                    mindist = dist
                    closest = c                
        if closest != None:
            print("Closest", closest.name)
            if closest.destruction.deform:
                closest.destruction.wasCompound = True
            else:
                closest.game.use_collision_compound = True
        return closest != None
            
    
    def setBackupCompound(self, parent):
        loc = mathutils.Vector((0, 0, 0))
        
        #set compound at topmost position when groundconnectivity is enabled
        if parent.destruction.groundConnectivity and bpy.context.scene.useGravityCollapse:
            backup = bpy.context.scene.objects[parent.destruction.backup]
            dim = backup.bound_box.data.dimensions
            loc = mathutils.Vector(0, 0, dim[2]/2)
            print("LOC: ", loc) 
        
        mindist = sys.maxsize
        closestBackup = None
         
        for c in parent.children:
            if c.type == 'EMPTY' and c.name.startswith("P_"):
                backup = c.destruction.backup
                dist = (loc - backup.location).length
                # print(mindist, dist, c)
                if dist < mindist:
                    mindist = dist
                    closestBackup = backup        
                
        if closestBackup != None:
            print("ClosestBackup", closestBackup.name)
            if closestBackup.destruction.deform:
                closestBackup.destruction.wasCompound = True
            else:
                closestBackup.game.use_collision_compound = True   
        
    def prepareParenting(self, context, obj):
        
        layers = list(context.scene.layers)
        
        context.scene.layers = [True, True, True, True, True,
                            True, True, True, True, True,
                            True, True, True, True, True,
                            True, True, True, True, True] 
        context.scene.objects.active = obj 
        
        if not context.active_object:
            return None, None, None, None# object might have been removed
                              
        context.active_object.destruction.pos = obj.location.to_tuple()
        bbox = obj.bound_box.data.dimensions.to_tuple()
        
        #context.scene.objects.active = obj
        
        split = obj.name.split(".")
        parentName = ""
        nameStart = ""
        nameEnd = ""
        
        if len(split) > 1:
            s = ""
            for i in split[:-1]:
                s = s + "." + i
            s = s.lstrip(".")
            nameStart =  s
            nameEnd = split[-1]
            if not nameStart.startswith("S_"):
                nameStart = "S_" + nameStart
            obj.name = nameStart + "." + nameEnd
        else:
            if not obj.name.startswith("S_"):
                nameStart = "S_" + obj.name
            else:
                nameStart = obj.name
            obj.name = nameStart + ".000"
            nameEnd = "000"
             
        parentName = "P_0_" + obj.name #nameStart + "." + nameEnd
   
        #and parent them all to an empty created before -> this is the key
        #P_name = Parent of
        
        children = context.scene.objects
        largest = nameEnd
        level = 0
      
        if obj.parent != None:
            pLevel = obj.parent.name.split("_")[1]
            level = int(pLevel)
            level += 1
            #get child with lowest number, must search for it if its not child[0]
            parentName = "P_" + str(level) + "_" + obj.name #+ "." + nameEnd
            print("Subparenting...", children)
            length = len(obj.parent.children)
            
            #get the largest child index number, hopefully it is the last one and hopefully
            #this scheme will not change in future releases !
            largest = obj.parent.children[length - 1].name.split(".")[1]
         
        context.scene.layers = layers
         
        return parentName, nameStart, largest, bbox    
        
    
#   # def isInCluster(self, child, parentName):
#        parent = data.objects[parentName]
#        if not parent.destruction.cluster:
#           return False
#        
#        bboxX = child.bound_box.data.dimensions[0]
#        bboxY = child.bound_box.data.dimensions[1]
#        bboxZ = child.bound_box.data.dimensions[2]
#        distVec = child.location - parent.location
#        if distVec[0] <= parent.destruction.cluster_dist[0] / 100 * bboxX and \
#           distVec[1] <= parent.destruction.cluster_dist[1] / 100 * bboxY and \
#           distVec[2] <= parent.destruction.cluster_dist[2] / 100 * bboxZ:   
#            return True
#        return False    
    
    def valid(self,context, child):
        return child.name.startswith(context.active_object.name)
    
    def applyDataSet(self, context, c, nameEnd, parentName, pos, backup):
        #print("NAME: ", c.name)
        
        end = 0
        if not c.name.endswith("backup"):
            split = c.name.split(".")
            end = split[1]
        
        if (int(end) > int(nameEnd)) or self.isBeingSplit(c, parentName, backup) or c.parent == None:
            self.assign(c, parentName, pos, backup, context)
    
    def getMatIndex(self, materialname, c):
       # print("Mat", materialname)
        if materialname != None and materialname != "" and \
        materialname in bpy.data.materials:
            slots = len(c.material_slots)
            found = False
            i = 0
            for slot in c.material_slots:
                if slot.material.name == materialname:
                    found = True
                    slots = i
                    break
                i += 1
                
                
            if not found:
                ctx = bpy.context.copy()
                ctx["object"] = c
                ops.object.material_slot_add(ctx)
                material = bpy.data.materials[materialname]
                c.material_slots[slots].material = material  
            return slots
        
        return 0
    
    def calcMass(self, obj, backup):
    
        if backup.destruction.cell_fracture.mass_mode == 'UNIFORM':
            obj.game.mass = obj.destruction.cell_fracture.mass
        elif backup.destruction.cell_fracture.mass_mode == 'VOLUME':
            from mathutils import Vector
            def _get_volume(obj_cell):
                def _getObjectBBMinMax():
                    min_co = Vector((1000000.0, 1000000.0, 1000000.0))
                    max_co = -min_co
                    matrix = obj_cell.matrix_world
                    for i in range(0, 8):
                        bb_vec = obj_cell.matrix_world * Vector(obj_cell.bound_box[i])
                        min_co[0] = min(bb_vec[0], min_co[0])
                        min_co[1] = min(bb_vec[1], min_co[1])
                        min_co[2] = min(bb_vec[2], min_co[2])
                        max_co[0] = max(bb_vec[0], max_co[0])
                        max_co[1] = max(bb_vec[1], max_co[1])
                        max_co[2] = max(bb_vec[2], max_co[2])
                    return (min_co, max_co)

                def _getObjectVolume():
                    min_co, max_co = _getObjectBBMinMax()
                    x = max_co[0] - min_co[0]
                    y = max_co[1] - min_co[1]
                    z = max_co[2] - min_co[2]
                    volume = x * y * z
                    return volume

                return _getObjectVolume()
        
   
            obj_volume_tot = _get_volume(backup)
            obj_volume = _get_volume(obj)
            mass_fac = obj.destruction.cell_fracture.mass / obj_volume_tot
            obj.game.mass = obj_volume * mass_fac
            
    def assign(self, c, parentName, pos, backup, context):
        
        c.destruction.cell_fracture.mass_mode = backup.destruction.cell_fracture.mass_mode
        c.destruction.cell_fracture.mass = backup.destruction.cell_fracture.mass
        c.destruction.dissolve_angle = backup.destruction.dissolve_angle
        c.destruction.cell_fracture.recursion_chance = backup.destruction.cell_fracture.recursion_chance
        c.destruction.cell_fracture.recursion_chance_select = backup.destruction.cell_fracture.recursion_chance_select
        c.destruction.cell_fracture.recursion = backup.destruction.cell_fracture.recursion
        c.destruction.voro_exact_shape = backup.destruction.voro_exact_shape
        c.destruction.voro_volume = backup.destruction.voro_volume
        c.destruction.voro_particles = backup.destruction.voro_particles
        c.destruction.destructionMode = backup.destruction.destructionMode
        c.destruction.dynamic_mode = backup.destruction.dynamic_mode
        
        #calculate mass
        self.calcMass(c, backup)
        
        slots = 0
        context.scene.objects.active = c 
        if backup.destruction.destructionMode != 'DESTROY_VB' and \
        backup.destruction.destructionMode != 'DESTROY_C' and \
        backup.destruction.destructionMode != 'DESTROY_F':
            #assign materials
            materialname = backup.destruction.inner_material
            slots = self.getMatIndex(materialname, backup)    
                
            if slots != 0 or backup.destruction.re_unwrap:
                ops.object.mode_set(mode = 'EDIT')
                ops.mesh.select_all(action = 'SELECT')
               # print("Seam", ops.mesh.mark_seam())
                ops.mesh.select_all(action = 'DESELECT')
                
                bm = bmesh.from_edit_mesh(c.data)
                facelist = [f for f in bm.faces if not self.testNormal(backup, c, f)]
                for f in facelist:
                    if slots != 0:
                      # print("Assigning index", slots)
                        f.material_index = slots
                    f.select = True
                    
                if backup.destruction.re_unwrap:
                    #unwrap inner faces again, so the textures dont look distorted (hopefully)  
                    ops.uv.smart_project(angle_limit = backup.destruction.smart_angle)
                ops.object.mode_set(mode = 'OBJECT')
        
        #correct a parenting "error": the parts are moved pos too far
        #print(backup.parent)
        b = None
        temp = c.name.split(".")[0]
        start = temp.split("_")[1]
        bStart = None
        if backup.parent != None:
            b = backup.parent.destruction.backup #old backup
         #   print("OLDBACKUP", b)
            temp = b.split(".")[0]
            bStart = temp.split("_")[1]   
            if bStart != start:
                pos = backup.parent.location
                print("Correcting pos", pos)   
            
        if backup.destruction.destructionMode != 'DESTROY_V' and backup.destruction.destructionMode != 'DESTROY_VB' and \
        backup.destruction.destructionMode != 'DESTROY_C':
            if c != backup and c.name != b and b != None: 
                c.location += pos
        elif backup.destruction.destructionMode == 'DESTROY_VB':
            if c != backup and (c.name != b or b == None) and (c.parent == None):
                if context.scene.hideLayer != 1:
                    c.location -= mathutils.Vector(backup.destruction.pos) #correction ?
            
          
        if c != backup and (c.name != b or b == None):
            #print("Setting parent", pos)
            c.location -= pos
                  
            #if groups are wanted DO NOT parent here
            myparent = bpy.data.objects[parentName]
            
            #if backup.destruction.destructionMode == 'DESTROY_V' or backup.destruction.destructionMode == 'DESTROY_VB':
            #    myparent.location = Vector(backup.destruction.origLoc)
            
            if backup.destruction.destructionMode == 'DESTROY_C':
                if not backup.destruction.cell_fracture.group_name:
                    c.parent = myparent
                else:
                    #delete unnecessary empty
                    if myparent.name in context.scene.objects:
                        context.scene.objects.unlink(myparent)
                        del myparent
            else:
                c.parent = myparent
                    
            c.destruction.flatten_hierarchy = backup.destruction.flatten_hierarchy
            c.layers = self.layer(context.scene.hideLayer)
            c.destruction.deform = backup.destruction.deform
            c.destruction.partCount = backup.destruction.partCount
            c.destruction.wallThickness = backup.destruction.wallThickness
            c.destruction.pieceGranularity = backup.destruction.pieceGranularity
            c.destruction.destructionMode = backup.destruction.destructionMode
            c.destruction.boolean_original = backup.destruction.boolean_original
            c.destruction.dynamic_mode = backup.destruction.dynamic_mode
            c.destruction.cubify = backup.destruction.cubify
            c.destruction.backup = backup.name
            c.destruction.re_unwrap = backup.destruction.re_unwrap
            c.destruction.smart_angle = backup.destruction.smart_angle
            c.destruction.use_debug_redraw = backup.destruction.use_debug_redraw
            c.destruction.glue_threshold = backup.destruction.glue_threshold
        
        if c == backup and b == None:
            #print("Setting backup parent", pos)
            c.location -= pos
        
        if c.destruction.deform:
            c.game.physics_type = 'SOFT_BODY'
            c.game.soft_body.dynamic_friction = 1
            c.game.soft_body.shape_threshold = 0.25
            c.game.soft_body.use_cluster_rigid_to_softbody = True
            c.game.soft_body.use_cluster_soft_to_softbody = True
            c.game.soft_body.linear_stiffness = 1
            c.game.soft_body.use_bending_constraints = False
            context.scene.objects.active = c
            c.select = True
           # ops.object.transform_apply(location = True)
            c.select = False
            ops.object.mode_set(mode = 'EDIT')
            ops.mesh.subdivide()
            #ops.mesh.subdivide()
            ops.object.mode_set(mode = 'OBJECT')
            
        else:
            c.game.physics_type = 'RIGID_BODY'
            c.game.collision_bounds_type = 'CONVEX_HULL'
            c.game.use_collision_bounds = True
            c.game.collision_margin = 0.0 
        
        
        
        #update stale data
       # context.scene.objects.active = c
       # ops.object.mode_set(mode = 'EDIT')
    #    ops.object.mode_set(mode = 'OBJECT')
        c.game.radius = 0.01
        c.select = True
        #c.game.mass = mass 
        c.destruction.transmitMode = 'T_SELECTED'
        c.destruction.destroyable = False
        
        #memorize children and this way "potential" backups too.
        par = bpy.data.objects[parentName]
        
        #needed for correct dissolve in destruction_bge.py
        #need to consider P_ children too ! (if any) 
        bPar = c.destruction.is_backup_for
        n = c.name
        if bPar != "":
            n = bPar
           
        if n not in par.destruction.children:
            prop = par.destruction.children.add()
            prop.name = n
  
        #accumulate ascendants as forbidden compounds.
        p = par.parent    
        while p != None:
            for ch in p.destruction.children:
                name = ch.name
                if ch.name.startswith("P_"):
                    name = bpy.data.objects[ch.name].destruction.backup
                    
                if name not in par.destruction.ascendants:
                    prp = par.destruction.ascendants.add()
                    prp.name = name
                   # print("Asc:", par.name, p.name, ch.name)
                    
            p = p.parent
                
        c.select = False        
           
            
        
#        c.destruction.partCount = 1
#        c.destruction.wallThickness = 0.01
#        c.destruction.pieceGranularity = 0
#        c.destruction.destructionMode = 'DESTROY_F'
        
        
    
    def isBeingSplit(self, c, parentName, backup):
        if c.name.endswith("backup"):
            return False
        
        temp = backup.name.split(".")[0]
        bstart = temp.split("_")[1]
        
        temp = c.name.split(".")[0]
        start = temp.split("_")[1]
        
        temp = parentName.split(".")[0]
        pstart = temp.split("_")[3]
        
   #     print(start, bstart, pstart)
        
        if parentName.split(".")[1] == c.name.split(".")[1] or (start == bstart and pstart != start and c != backup):
            return True
        return False
   
        
    def applyFracture(self, context, objects):
        
        partCount = context.active_object.destruction.partCount
        roughness = context.active_object.destruction.roughness
        crack_type = context.active_object.destruction.crack_type
        
        parts = []
        for obj in objects:
            parentName, nameStart, largest, bbox = self.prepareParenting(context, obj)
            if parentName == None:
                continue
            
            backup = self.createBackup(context, obj) 
            
            backup.destruction.orig_name = str(obj.name)
            
            #fracture the sub objects if cubify is selected
            largest = self.setLargest(largest, backup)
            materialname = backup.destruction.inner_material
            
            #assign inner material to another slot of object, so it is used together with cutter material
            self.getMatIndex(materialname, obj)
            
            if obj.destruction.cubify:
                parts.extend(self.cubify(context, obj, bbox, partCount, 0, materialname))
            else:
                parts.extend(self.boolFrac(context, [obj], partCount, crack_type, roughness, materialname))
            
            parent = self.doParenting(context, parentName, nameStart, bbox, backup, largest, obj)
            
            for c in parent.children:
                c.destruction.groundConnectivity = False
                #c.destruction.cubify = False
                #c.destruction.gridDim = (1,1,1)
                                
        return parts
    
    def boolFrac(self, context, obj, partCount, crack_type, roughness, materialname):
        
        fo.fracture_basic(context, obj, partCount, crack_type, roughness, materialname)
        #find new parts and return them, needed for recursion
        if context.active_object != None:
            print("parts......")
            oldPar = context.active_object.parent
            nameStart = context.active_object.name.split(".")[0] 
            parts = [c for c in context.scene.objects if self.isRelated(c, context, nameStart, oldPar)]
            return parts
        return [] # error case 
    
    def edgeCount(self, vertex, mesh):
        occurrence = 0
        for key in mesh.edge_keys:
            if vertex == mesh.vertices[key[0]] or vertex == mesh.vertices[key[1]]:
                occurrence += 1
        print("Vertex has ", occurrence, " edges ")        
        return occurrence
        
    def getSize(self, obj):
        areas = [f.area for f in obj.data.faces]
        return sum(areas)
    
    def dictItem(self, dict, key, value):
        dict[key] = value
        
    def applyKnife(self, context, objects, parts, jitter, granularity, cut_type):
        
        for obj in objects:
            parentName, nameStart, largest, bbox = self.prepareParenting(context, obj)
            backup = self.createBackup(context, obj) 
            
            if obj.destruction.cubify:
                self.cubify(context, obj, bbox, parts)
            else:
                self.knife(context, obj, parts, jitter, granularity, cut_type)
              
            parent = self.doParenting(context, parentName, nameStart, bbox, backup, largest, obj)
            
            for c in parent.children:
                c.destruction.groundConnectivity = False
            #    c.destruction.cubify = False
            #    c.destruction.gridDim = (1,1,1)
            
    def testNormal(self, backup, c, face):
        
        for p in backup.data.polygons:
            n = p.normal
            dot = round(n.dot(face.normal), 3)
            prod = round(n.length * face.normal.length, 3)
            if dot == prod or n == face.normal:
                
                #distance between faces
                #d = geometry.distance_point_to_plane(face.verts[0].co, mesh.vertices[p.vertices[0]].co, 
                #                                     mesh.vertices[p.vertices[1]].co)
                p1 = mathutils.Vector(face.verts[0].co)
                p2 = mathutils.Vector(backup.data.vertices[p.vertices[0]].co)
                
                p1 = p1 + c.location
                
                if backup.destruction.destructionMode != 'DESTROY_VB':
                    p2 = p2 + backup.location
                 
                #handle scale and rotation too
                p1 = p1 * c.rotation_euler.to_matrix()
                p2 = p2 * backup.rotation_euler.to_matrix()
                
                p1[0] = p1[0] * c.scale[0]
                p1[1] = p1[1] * c.scale[1]
                p1[2] = p1[2] * c.scale[2]
                
                p2[0] = p2[0] * backup.scale[0]
                p2[1] = p2[1] * backup.scale[1]
                p2[2] = p2[2] * backup.scale[2]
                                    
                d = round((p1 - p2).dot(n), 3)
                
                if backup.destruction.destructionMode != 'DESTROY_VB':
                    bx = abs(round(backup.location[0], 3))
                    by = abs(round(backup.location[1], 3))
                    bz = abs(round(backup.location[2], 3))
                else:
                    bx = abs(round(backup.destruction.origLoc[0], 3))
                    by = abs(round(backup.destruction.origLoc[1], 3))
                    bz = abs(round(backup.destruction.origLoc[2], 3))
                
                #print("Distance", d, bx, by, bz)
                if abs(d) in (bx, by, bz):
                    return True                                              
        return False
        
           
    def knife(self, context, ob, parts, jitter, granularity, cut_type):
        
        currentParts = [ob.name]
        
        #print("ob in SCENE: ", ob, ob.name in context.scene)
        context.scene.objects.active = ob
        ops.object.mode_set(mode = 'EDIT')
        #subdivide the object once, say 10 cuts (let the user choose this)
        ops.mesh.subdivide(number_cuts = granularity)
        ops.object.mode_set(mode = 'OBJECT')
        
        zero = Vector((0, 0, 0))
        align = [1, 0, 0, 0]
        matrix = Matrix.Identity(4)
        
        area = None
        region = None
        for a in context.screen.areas:
            if a.type == 'VIEW_3D':
                area = a
                reg = [r for r in area.regions if r.type == 'WINDOW']          
                region = reg[0]
        
        #move parts to center of SCREEN to cut them correctly
        for s in area.spaces:
            if s.type == 'VIEW_3D':
                zero = s.region_3d.view_location
                align = s.region_3d.view_rotation
                matrix = s.region_3d.view_matrix
        
        #for 1 ... parts
        tries = 0
        isHorizontal = False
        names = [ob.name]
        sizes = [self.getSize(ob)]
        
        while (len(currentParts) < parts):
                    
            #give up when always invalid objects result from operation
            if tries > 100:
                break
            
            for o in context.scene.objects:
                o.select = False
                 
            oldnames = [o.name for o in context.scene.objects]
            
            #split by loose parts -> find new names, update oldnames, names and sizes, then proceed as usual
            #pick largest object first
           
            name = names[len(names) - 1] 
            
           # print("Oldnames/names : ", len(oldnames), len(names))
            
            tocut = context.scene.objects[name]
            context.scene.objects.active = tocut
            
            ops.object.mode_set(mode = 'EDIT')
            ops.mesh.select_all(action = 'SELECT')
            ops.mesh.separate(type = 'LOOSE')
            ops.mesh.select_all(action = 'DESELECT')
            ops.object.mode_set(mode = 'OBJECT')
            
            newObj = self.findNew(context, oldnames)
            for obj in newObj:
                oldnames.append(obj.name)
                sizeNew = self.getSize(obj)
                indexNew = bisect.bisect(sizes, sizeNew)
                sizes.insert(indexNew, sizeNew)
                names.insert(indexNew, obj.name)
                
              
            #re-pick the new largest object to subdivide next
            name = names[len(names) - 1] 
            tocut = context.scene.objects[name]
            
           
            tocut.select = True
            ops.object.duplicate()
            tocut.select = False
            backupName = self.findNew(context, oldnames)[0].name
            print("Created Backup: ", backupName)

            backup = context.scene.objects[backupName]
            backup.name = "KnifeBackup"
            context.scene.objects.unlink(backup)
            
            context.scene.objects.active = tocut
            
            rotStart = context.active_object.destruction.rot_start
            rotEnd = context.active_object.destruction.rot_end
             
            parent = context.active_object.parent
            anglex = random.randint(rotStart, rotEnd)
            anglex = math.radians(anglex)
            
            angley = random.randint(rotStart, rotEnd)
            angley = math.radians(angley)
            
            anglez = random.randint(rotStart, rotEnd)
            anglez = math.radians(anglez)
            
           
            
            
            #pick longest side of bbox
            dims = tocut.bound_box.data.dimensions.to_tuple()
            mx = max(dims)
            index = dims.index(mx)
         #   print(mx, index, dims)    
            
            
            #store old rotation in quaternions and align to view
            tocut.rotation_mode = 'QUATERNION'
            oldquat = Quaternion(tocut.rotation_quaternion)
            tocut.rotation_quaternion = align
            context.scene.update()
          
            tocut.rotation_mode = 'XYZ'
            
            # a bit variation (use lower values...)
            if (index < 2):
                
                euler = align.to_euler()
                euler.rotate_axis('X', anglex)
                euler.rotate_axis('Y', anglex)
                euler.rotate_axis('Z', anglex)
                
                context.active_object.rotation_euler = (euler.x, euler.y, euler.z)
                context.scene.update()
            
            loc = Vector(context.active_object.location)
            context.active_object.location = zero
            context.scene.update()
            
            print("POS", context.active_object.location)
            
            #maybe rotate by 90 degrees to align ?
            
          
           # indexRot = [0,0,0]
            
            if index == 0:
                # x is longest, cut vertical
                isHorizontal = True 
            elif index == 1:
                # y is longest, cut horizontal
                isHorizontal = False    
                
            elif index == 2:
                #z is longest, so rotate by 90 degrees around x, then cut horizontal
                #indexRot = tocut.rotation_euler
                ortho = align.to_euler()
                ortho.rotate_axis('X', math.radians(90))
            #    axis = ortho.to_quaternion().axis
            #    ops.transform.rotate(value = [math.radians(90)], axis = axis)
            
                 #vary a bit
                ortho.rotate_axis('X', anglex)
                ortho.rotate_axis('Y', angley)
                ortho.rotate_axis('Z', anglez)
                
                context.active_object.rotation_euler = (ortho.x, ortho.y, ortho.z)
                context.scene.update()
                isHorizontal = False
            
            #context.scene.objects.active = tocut
            #make a random OperatorMousePath Collection to define cut path, the higher the jitter
            #the more deviation from path
            #opmousepath is in screen coordinates, assume 0.0 -> 1.0 since 0.5 centers it ?
            #[{"name":"", "loc":(x,y), "time":0},{...}, ...]
            
            width = region.width
            height = region.height
            
            lineStart = context.active_object.destruction.line_start
            lineEnd = context.active_object.destruction.line_end
            
            path = []
            if cut_type == 'LINEAR':
               # isHorizontal = not isHorizontal
                path = self.linearPath(context, tocut, jitter, width, height, isHorizontal, lineStart, lineEnd)
            elif cut_type == 'ROUND':
                path = self.spheroidPath(jitter, width, height, lineStart, lineEnd)
            
          #  print("PATH: ", path, tocut.location, tocut.rotation_euler)    
            #apply the cut, exact cut
            ops.object.mode_set(mode = 'EDIT')
            ops.mesh.select_all(action = 'SELECT')
            
            ctx = context.copy()
            ctx["area"] = area
            ctx["region"] = region
            ops.mesh.knife_cut(ctx, type = 'EXACT', path = path, region_width = region.width, region_height = region.height,
                               perspective_matrix = matrix)
            
            part = self.handleKnife(context, tocut, backup, names, oldquat, loc, oldnames, tries)
            
            #use fallback method if no patch available
            # create cutters
            
            
            if part == None:
                tries += 1
                continue
            
            obj = context.active_object
            
            if len(obj.data.vertices) == 0 or len(tocut.data.vertices) == 0:
                print("Undo (no vertices)...")
                context.scene.objects.unlink(tocut)
                context.scene.objects.unlink(obj)
                backup.name = tocut.name
                context.scene.objects.link(backup)
                
                tries += 1
                continue
            
            manifold1 = min(mesh_utils.edge_face_count(obj.data))
            manifold2 = min(mesh_utils.edge_face_count(tocut.data))
            
           # print(manifold1, manifold2)
            manifold = min(manifold1, manifold2)
            
            #manifold = 2
            if manifold < 2:
                print("Undo (non-manifold)...", tocut.name, obj.name)
                
                
                context.scene.objects.unlink(tocut)
                context.scene.objects.unlink(obj)
          
                #backup.name = tocut.name
                context.scene.objects.link(backup)
                backup.name = tocut.name #doesnt really work... Blender renames it automatically
            
                #so update the names array
                print("Re-linked: ", backup.name, tocut.name)
                del names[len(names) - 1]
                names.append(backup.name)
                #if tocut.name in oldnames:
                #    oldnames.remove(tocut.name)
                #if backup.name in oldnames:
                #    oldnames.remove(backup.name)
                    
                #undoOccurred = True
                tries += 1
                #undoOccurred = True
                continue
                      
            currentParts.append(part)
            
            #context.object seems to disappear so store parent in active object
            context.active_object.parent = parent
            tries = 0
            print("Split :", tocut.name, part)
            
            # update size/name arrays
            # remove the last one because this was chosen to be split(its the biggest one)
            del sizes[len(sizes) - 1]
            del names[len(names) - 1]
            
            sizeTocut = self.getSize(tocut)
            sizePart = self.getSize(context.scene.objects[part])
            
            indexTocut = bisect.bisect(sizes, sizeTocut)
            sizes.insert(indexTocut, sizeTocut)
            names.insert(indexTocut, tocut.name)
            
            indexPart = bisect.bisect(sizes, sizePart)
            sizes.insert(indexPart, sizePart)
            names.insert(indexPart, part)
                           
           
    def handleKnife(self, context, tocut, backup, names, oldquat, loc, oldnames, tries):
            ops.object.mode_set(mode = 'OBJECT')
            
            #restore rotations 
        #    if index == 2:
        #       context.active_object.rotation_euler = indexRot
        #        context.scene.update()
          
            context.active_object.rotation_mode = 'QUATERNION'
            context.active_object.rotation_quaternion = oldquat
            
         #   context.active_object.rotation_euler = (0, 0, 0)
            context.scene.update()
            context.active_object.rotation_mode = 'XYZ'
     
            context.active_object.location = loc
            context.scene.update()
          
            
            ops.object.mode_set(mode = 'EDIT')
            ops.mesh.loop_to_region()
            
            #separate object by selection
          #  print("BEFORE", len(context.scene.objects))
            ops.mesh.separate(type = 'SELECTED')
          #  print("AFTER", len(context.scene.objects))
            
            newObject = self.findNew(context, oldnames)
            if len(newObject) > 0:
                part = newObject[0].name
            else:
                part = None
             
            ops.mesh.select_all(action = 'SELECT')
            ops.mesh.region_to_loop()
            ops.mesh.fill()
                
            ops.object.mode_set(mode = 'OBJECT')
            tocut.select = True
            ops.object.origin_set(type = 'ORIGIN_GEOMETRY')
            tocut.select = False
            
            ops.object.mode_set(mode = 'EDIT')
           # ops.mesh.select_all(action = 'DESELECT')
        #    ops.mesh.select_all(action = 'SELECT')
            ops.mesh.normals_make_consistent(inside = False)
            
#            if self.testNormalInside(tocut):
#                ops.mesh.normals_make_consistent(inside = False)
#                tocutFlipped = True
            
            ops.object.mode_set(mode = 'OBJECT')
            
             #missed the object, retry with different values until success   
            if part == None:
                print("Undo (naming error)...")
               
                context.scene.objects.unlink(tocut)
                context.scene.objects.link(backup)
                backup.name = tocut.name #doesnt really work... Blender renames it automatically
            
                #so update the names array
                print("Re-linked: ", backup.name, tocut.name, oldnames)
                del names[len(names) - 1]
                names.append(backup.name)
                if tocut.name in oldnames:
                    oldnames.remove(tocut.name)
                if backup.name in oldnames:
                    oldnames.remove(backup.name)
                
                tries += 1
                return None
            
      
            context.scene.objects.active = context.scene.objects[part]
            ops.object.mode_set(mode = 'EDIT')
            ops.mesh.select_all(action = 'SELECT')
            ops.mesh.region_to_loop()
            ops.mesh.fill()
                    
            ops.object.mode_set(mode = 'OBJECT')
            context.active_object.select = True
            ops.object.origin_set(type = 'ORIGIN_GEOMETRY')
            context.active_object.select = False
            
            ops.object.mode_set(mode = 'EDIT')
            #ops.mesh.select_all(action = 'DESELECT')
            #ops.mesh.select_all(action = 'SELECT')
            ops.mesh.normals_make_consistent(inside = False)
            
            #if self.testNormalInside(context.active_object):
            #   ops.mesh.normals_make_consistent(inside = False)
            #   partFlipped = True
            ops.object.mode_set(mode = 'OBJECT')
            
            return part
     
    def handleKnifeBoolean(self, context, tocut, backup, names, oldquat, loc, oldnames):
        pass
        
        
            
    def linearPath(self, context, tocut, jitter, width, height, isHorizontal, lineStart, lineEnd):
        startx = 0;
        starty = 0
        endx = width
        endy = height
        
        
        steps = 100
        if jitter > 0.01:
           steps = random.randint(100, 200)
        
        if isHorizontal:
            startPercentage = round((lineStart / 100 * width), 0)
            endPercentage = round((lineEnd / 100 * width), 0)
            startx = random.randint(startPercentage, endPercentage)
            starty = 0
            endx = width - startx
            endy = height
            
        
        else:
            startPercentage = round((lineStart / 100 * height), 0)
            endPercentage = round((lineEnd / 100 * height), 0)
            startx = 0
            starty = random.randint(startPercentage, endPercentage)
            endx = width
            endy = height - starty
        
            
        deltaX = (endx - startx) / steps
        deltaY = (endy - starty) / steps
        
        delta = math.sqrt(deltaX * deltaX + deltaY * deltaY)
        sine = deltaX / delta
        cosine = deltaY / delta
        if isHorizontal:
             sine = deltaY / delta
             cosine = deltaX / delta
        
        path = [] 
        path.append(self.entry(startx, starty))
        
        for i in range(1, steps + 1):
            x = startx + i * deltaX
            y = starty + i * deltaY
            
            if jitter > 0.01:
                jit = random.uniform(-jitter, jitter) 
                if isHorizontal:
                    x += (cosine * jit * width / 100)
                    y -= (sine * jit * height / 100)
                else:
                    x -= (sine * jit * width / 100)
                    y += (cosine * jit * height / 100)
                    
            path.append(self.entry(x,y))
  
        return path        
    
    def spheroidPath(self, jitter, width, height, lineStart, lineEnd):
        midx = random.randint(0, width)
        midy = random.randint(0, height)

        startPercentage = round((lineStart / 100 * width), 0)
        endPercentage = round((lineEnd / 100 * width), 0)
        
        radius = random.uniform(startPercentage, endPercentage)
        steps = random.randint(100, 200)
        
        deltaAngle = 360 / steps
        
        angle = 0
        path = []
        for i in range(0, steps):
            x = midx + math.cos(math.radians(angle)) * radius
            y = midy + math.sin(math.radians(angle)) * radius
            
            #if jitter > 0:
            #   x += random.uniform(-jitter, jitter)
            #   y += random.uniform(-jitter, jitter)
            
            path.append(self.entry(x,y))  
            angle += deltaAngle  
        
        return path  
           
    def entry(self, x, y):
        return {"name":"", "loc":(x, y), "time":0}
    
    def findNew(self, context, oldnames):
        ret = []
        for o in context.scene.objects:
            if o.name not in oldnames:
                ret.append(o)
        print("found: ", ret)
        return ret
            
    
    def isRelated(self, c, context, nameStart, parent):
        
        split = c.name.split(".")
        nameEnd = split[-1]
        objname = ""
        for s in split[:-1]:
            objname = objname + "." + s
        objname = objname.lstrip(".")
      #  print("OBJ", objname, nameStart)
    #    print("Related: ", c.name, c.parent, parent)
        return (objname == nameStart) and c.parent == parent and (not c.destruction.converted)
              
    def endStr(self, nr):
        if nr < 10:
            return "00" + str(nr)
        if nr < 100:
            return "0" + str(nr)
        return str(nr)
        
    def cubify(self, context, object, bbox, parts, mat_index, mat_name = "", level = 0):
        #create a cube with dim of cell size, (rotate/position it accordingly)
        #intersect with pos of cells[0], go through all cells, set cube to pos, intersect again
        #repeat always with original object
        
        loc = mathutils.Vector(object.destruction.pos)
        obj = object
        while obj.parent != None:
            loc += obj.parent.location
            obj = obj.parent
        
       # print("loc", loc) 
        grid = dd.Grid(object.destruction.cubifyDim, 
                       loc.to_tuple(),
                       bbox, 
                       [], 
                       object.destruction.grounds)
        
        #o = context.object
      #  obj = context.active_object    
        ops.mesh.primitive_cube_add()
#        print(context.object, context.active_object)
        
        cutter = context.active_object
        cutter.name = "Cutter"
        
        #assign inner mat to cutter
        if mat_name != "" and mat_name != None and \
        mat_name in bpy.data.materials:
            ctx = bpy.context.copy()
            ctx["object"] = bpy.context.active_object
            bpy.ops.object.material_slot_add(ctx)
            material = bpy.data.materials[mat_name]
            bpy.context.active_object.material_slots[0].material = material
        
        cutter.select = False
     
        cubes = []
        for cell in grid.cells.values():
            ob = self.cubifyCell(cell,cutter, context, object)
            if ob.destruction.use_debug_redraw:
                context.scene.update()
                ob.destruction._redraw_yasiamevil()
            cubes.append(ob)
            
           
       
        context.scene.objects.unlink(cutter)
        
        
        shards = []
        if object.destruction.destructionMode == "DESTROY_C":
            for cube in cubes:
                shards.extend(self.fracture_cells(context, cube, mat_index, level))
                context.scene.objects.unlink(cube)
                
        if parts > 1: 
            if object.destruction.destructionMode == 'DESTROY_F':
                crack_type = object.destruction.crack_type
                roughness = object.destruction.roughness
                context.scene.objects.unlink(object) 
                for cube in cubes:
                    shards.extend(self.boolFrac(context, cubes, parts, crack_type, roughness, mat_name))
                
#            elif object.destruction.destructionMode == 'DESTROY_K':
#                jitter = object.destruction.jitter
#                granularity = object.destruction.pieceGranularity
#                cut_type = object.destruction.cut_type 
#                context.scene.objects.unlink(object) 
#                 
#                for cube in cubes:
#                shards.extend(self.knife(context, cube, parts, jitter, granularity, cut_type)
            
            elif object.destruction.destructionMode == 'DESTROY_V' or \
                 object.destruction.destructionMode == 'DESTROY_VB':
                 volume = context.active_object.destruction.voro_volume
                 wall = context.active_object.destruction.wall
                   
                 for cube in cubes:
                     shards.extend(voronoi.voronoiCube(context, cube, parts, volume, wall, mat_index))
                     context.scene.objects.unlink(cube)
            
            else:
                granularity = object.destruction.pieceGranularity
                thickness = object.destruction.wallThickness
                
                mode = object.destruction.destructionMode
                modes = object.destruction.destModes
                
                massive = False
                pairwise = False
                
                if mode == modes[2][0]:
                    massive = True
                    pairwise = True
                    
                if mode == modes[3][0]:
                    massive = True
                
                context.scene.objects.unlink(object)
                for cube in cubes:
                    shards.extend(self.explo(context, cube, parts, granularity, thickness))
                
        else:
             if object.destruction.destructionMode not in ('DESTROY_V', 'DESTROY_VB'):
                context.scene.objects.unlink(object)
             shards = cubes
             
        #if parts == 1 or (parts > 1  and object.destruction.destructionMode not in ('DESTROY_V', 'DESTROY_VB')):
        #    #apply position correction, seems to be off always at -2.75 in Z direction
        #    for c in cubes: 
        #        c.location[2] += 2.75
                  
        return shards 
              
    def cubifyCell(self, cell, cutter, context, obj):
      #  context.active_object.select = True #maybe link it before...
        context.scene.objects.active = obj #= context.object
        obj.select = True
      #  print(context.object)
        
        ops.object.duplicate()
        #context.object.select = False
        obj.select = False
        ob = context.active_object
       # print(ob, context.object, context.scene.objects, context.selected_objects)
        
        #print("LOC", ob.location, cell.center)
        cutter.location = mathutils.Vector(cell.center)
        cutter.dimensions = mathutils.Vector(cell.dim) * 1.01
        context.scene.update()
        
        bool = ob.modifiers.new("Boolean", 'BOOLEAN')
        bool.object = cutter
        bool.operation = 'INTERSECT'
        
        ctx = context.copy()
        ctx["object"] = ob
        ctx["modifier"] = bool
        ops.object.modifier_apply(ctx, apply_as='DATA', modifier = bool.name)
        #mesh = ob.to_mesh(context.scene, 
        #                  apply_modifiers=True, 
        #                  settings='PREVIEW')
        #print(mesh)                  
        #old_mesh = ob.data
        #ob.data = None
        #old_mesh.user_clear()
        
        #if (old_mesh.users == 0):
        #    bpy.data.meshes.remove(old_mesh)  
            
        #ob.data = mesh 
        ob.select = False
        #ob.modifiers.remove(bool)
        
        ops.object.mode_set(mode = 'EDIT')  
        ops.mesh.select_all(action = 'SELECT')
        ops.mesh.remove_doubles(threshold = 0.0001)
        ops.object.mode_set(mode = 'OBJECT') 
        
        ob.select = True
        ops.object.origin_set(type = 'ORIGIN_GEOMETRY', center = 'BOUNDS') 
        ob.select = False
        
        context.scene.objects.active = obj#context.object 
        
        return ob
        
       #from ideasman42    
    def fracture_cell(self, scene, obj, ctx, mat_index, level):
        
        # pull out some args
        use_recenter = ctx.use_recenter
        group_name = ctx.group_name
        #use_island_split = ctx.use_island_split
        
        use_interior_hide=(ctx.use_interior_vgroup or ctx.use_sharp_edges)
        objects = fracture_cell_setup.cell_fracture_objects(scene, obj, mat_index)
        objects = fracture_cell_setup.cell_fracture_boolean(scene, obj, objects, use_interior_hide, level)
    
        # todo, split islands.
    
        # must apply after boolean.
        if use_recenter:
            bpy.ops.object.origin_set({"selected_editable_objects": objects},
                                      type='ORIGIN_GEOMETRY', center='BOUNDS') 
        
        #--------------
        # Scene Options
    
        # group
        if group_name:
            group = bpy.data.groups.get(group_name)
            if group is None:
                group = bpy.data.groups.new(group_name)
            group_objects = group.objects[:]    
            for obj_cell in objects:
                if obj_cell not in group_objects:
                    group.objects.link(obj_cell)             
    
        # testing only!
        #obj.hide = True
        return objects
    
    
    def fracture_cells(self,context, obj, mat_index, level):
        import time
        t = time.time()
        scene = context.scene
        #obj = context.active_object
        ctx = obj.destruction.cell_fracture
        objects = self.fracture_cell(scene, obj, ctx, mat_index, level)
    
        bpy.ops.object.select_all(action='DESELECT')
        for obj_cell in objects:
            obj_cell.select = True
        
        print("Done! %d objects in %.4f sec" % (len(objects), time.time() - t))
        return objects
    
#end from ideasman42
                        
                    
#def updateGrid(self, context):
#    return None

#def updateDestructionMode(self, context):
#    return None

#def updatePartCount(self, context):
#    return None

#def updateWallThickness(self, context):
#    return None

#def updatePieceGranularity(self, context):
#    return None

#def updateIsGround(context):
#    for c in context.object.children:
#        c.destruction.isGround = context.object.destruction.isGround      
#    return None


#def updateGroundConnectivity(self, context):
#    return None

def updateDestructor(context):
    
    layers = context.scene.layers
    context.scene.layers = [True, True, True, True, True,
                            True, True, True, True, True,
                            True, True, True, True, True,
                            True, True, True, True, True] 
                            
    for c in context.active_object.children:
        c.destruction.destructor = context.active_object.destruction.destructor
        if c.destruction.destructor:
            for p in context.active_object.destruction.destructorTargets:
                prop = c.destruction.destructorTargets.add()
                prop.name = p.name
           
        else:
            for p in context.active_object.destruction.destructorTargets:
                index = 0
                found = False
                for prop in c.destruction.destructorTargets:
                    if p.name == prop.name:
                        found = True    
                        break
                    index += 1
                    
                if found:
                    c.destruction.destructorTargets.remove(index) 
                      
    context.scene.layers = layers 
                    
    return None


def updateTransmitMode(self, context):
    return None 

def updateDestroyable(self, context):
    return None 

def updateCam(self, context):
    p = None
    if "Player" in bpy.data.objects:
        p = bpy.data.objects["Player"]
    if p:
        if context.scene.use_player_cam:
            p.game.controllers[0].link(p.game.sensors[0], p.game.actuators[0])
        else:
            p.game.controllers[0].unlink(p.game.sensors[0], p.game.actuators[0])
    return None

def updateFlattenHierarchy(self, context):
    if context.object.destruction.flatten_hierarchy:
        context.scene.hideLayer = 1

def updateDynamicMode(self, context):
    if context.object == None:
        return None
   
    context.scene.to_precalculated = False
    
    if context.object.destruction.dynamic_mode == 'D_DYNAMIC' and not \
    context.object.name.startswith("P_"):
        context.object.game.physics_type = 'RIGID_BODY'
        context.object.game.collision_bounds_type = 'CONVEX_HULL'
        context.object.game.collision_margin = context.object.destruction.collision_margin 
        context.object.game.radius = 0.01
        context.object.game.use_collision_bounds = True
    return None

#BEFORE ToGameParenting
def childsRec(par):
    ret = []
    for c in par.children:
        ret.extend(childsRec(c))
        ret.append(c)
        
    return ret
        
def updateCollisionMargin(self, context):
    if context.object.destruction.enable_all_children:
        #go recursively(?) thru all children ?
        childs = childsRec(context.object)
        for c in childs:
            if not context.object.destruction.enable_all_children or \
            context.object.game.use_collision_compound:
                c.game.collision_margin = context.object.destruction.collision_margin 
    return None
    

def updateDestructionDelay(self, context):
    #first all children
    if context.object.destruction.enable_all_children:
        #go recursively(?) thru all children ?
        childs = childsRec(context.object)
        for c in childs:
            sensornames = [s.name for s in c.game.sensors]
            if "Collision" in sensornames:
                c.game.sensors["Collision"].frequency = context.object.destruction.destruction_delay
    
    
    #then object itself
    sensornames = [s.name for s in context.object.game.sensors]
    if "Collision" in sensornames:
        context.object.game.sensors["Collision"].frequency = context.object.destruction.destruction_delay
         
    return None


def updateMass(self, context):
    
    if context.object == None:
        return None
                            
    childs = childsRec(context.object)
    [self.calcMass(c, c.backup) for c in childs]    
  
    return None

def updateEnableAllChildren(self, context):
    childs = childsRec(context.object)
    
    for c in childs:
        c.destruction.destructor = context.object.destruction.enable_all_children
            
    return None            
    

#disable decorator when persistence is not available
def unchanged(func):
    return func

pers = unchanged
if imported:
    pers = persistent

@pers
def updateValidTargets(object):
    #print("Current Object is: ", object)
    
    #for index in range(0, len(bpy.context.scene.validTargets)):
        #print("Removing :", index)
    #    bpy.context.scene.validTargets.remove(index)
    if object.destruction.destroyable:
        if object.name not in bpy.context.scene.validTargets:
            prop = bpy.context.scene.validTargets.add()
            prop.name = object.name
    else:
        #print("Not:", object.name)
        if object.name in bpy.context.scene.validTargets:
            index = bpy.context.scene.validTargets.index(object.name)
            bpy.context.scene.validTargets.remove(index) 
         #   print("Removing valid:", object.name)
            
        for o in bpy.context.scene.objects:
            if o.destruction.destructor and object.name in o.destruction.destructorTargets:
                index = 0
                for ob in o.destruction.destructorTargets:
                    if ob.name == object.name:
                        break
                    index += 1
          #      print("Removing:", object.name)
                o.destruction.destructorTargets.remove(index)
           
    return None 

@pers
def updateValidGrounds(object):
    #print("Current Object is: ", object)
    
    if object.destruction.isGround:
        if object.name not in bpy.context.scene.validGrounds:
            prop = bpy.context.scene.validTargets.add()
            prop.name = object.name
    else:
       # print("Not:", object.name)
        if object.name in bpy.context.scene.validGrounds:
            index = bpy.context.scene.validGrounds.index(object.name)
            bpy.context.scene.validTargets.remove(index) 
        #    print("Removing valid:", object.name)
            
        for o in bpy.context.scene.objects:
            if object.name in o.destruction.grounds:
                #index = o.destruction.grounds.index(object.name)
                index = 0
                for ob in o.destruction.grounds:
                    if ob.name == object.name:
                        break
                    index += 1
             
         #       print("Removing:", object.name, index)
                o.destruction.grounds.remove(index)
           
    return None

class CellFractureContext(types.PropertyGroup):
    
    #From ideasman42, cell fracture script
    
    # -------------------------------------------------------------------------
    # Source Options
    
    items_own = (('VERT_OWN', "Own Verts", "Use own vertices"),
                   ('EDGE_OWN', "Own Edges", "Use own edges"),
                   ('FACE_OWN', "Own Faces", "Use own faces"),
                   ('PARTICLE_OWN', "Own Particles", "All particle systems of the "
                                                      "source object"), )
                                                      
    items_child = (('VERT_CHILD', "Child Verts", "Use child object vertices"),
                   ('EDGE_CHILD', "Child Edges", "Use child edges"),
                   ('FACE_CHILD', "Child Faces", "Use child faces"),
                   ('PARTICLE_CHILD', "Child Particles", "All particle systems of the "
                                                          "child objects"), )
                                                          
    items_pencil = (('PENCIL', "Grease Pencil", "This object's grease pencil"),)
    
#    items = tuple(items_own + items_child + items_pencil)
    
#    source = props.EnumProperty(
#            name="Source",
#            items=(('VERT_OWN', "Own Verts", "Use own vertices"),
#                   ('EDGE_OWN', "Own Edges", "Use own edges"),
#                   ('FACE_OWN', "Own Faces", "Use own faces"),
#                   ('VERT_CHILD', "Child Verts", "Use child object vertices"),
#                   ('EDGE_CHILD', "Child Edges", "Use child edges"),
#                   ('FACE_CHILD', "Child Faces", "Use child faces"),
#                   ('PARTICLE_OWN', "Own Particles", ("All particle systems of the "
#                                                      "source object")),
#                   ('PARTICLE_CHILD', "Child Particles", ("All particle systems of the "
#                                                          "child objects")),
#                   ('PENCIL', "Grease Pencil", "This object's grease pencil"),
#                   ),
#            items = items, 
#            options={'ENUM_FLAG'},
#           default={'PARTICLE_OWN', 'VERT_OWN'}  # 'VERT_OWN', 'EDGE_OWN', 'FACE_OWN'
#            )
    
    source = set(items_own + items_child + items_pencil)
   # source = set(('VERT_OWN', 'EDGE_OWN', 'FACE_OWN', 'PARTICLE_OWN', 
#               'VERT_CHILD', 'EDGE_CHILD', 'FACE_CHILD', 'PARTICLE_CHILD',
#               'PENCIL'))
               
#    source = {
#        'VERT_OWN', 'EDGE_OWN', 'FACE_OWN',
#        'VERT_CHILD', 'EDGE_CHILD', 'FACE_CHILD',
#        'PARTICLE_OWN', 'PARTICLE_CHILD',
#        'PENCIL',
#        }
    
    source_own = props.EnumProperty(
        name = "SourceOwn", 
        items = items_own, 
        options = {'ENUM_FLAG'}, 
        default={'PARTICLE_OWN', 'VERT_OWN'})  # 'VERT_OWN', 'EDGE_OWN', 'FACE_OWN'

    source_child = props.EnumProperty(
        name = "SourceChild", 
        items = items_child, 
        options = {'ENUM_FLAG'})
        
    source_pencil = props.EnumProperty(
        name = "Pencil", 
        items = items_pencil, 
        options = {'ENUM_FLAG'}) 
        
    source_limit = props.IntProperty(
            name="Source Limit",
            description="Limit the number of input points, 0 for unlimited",
            min=0, max=5000,
            default=1000,
            )

    source_noise = props.FloatProperty(
            name="Noise",
            description="Randomize point distribution",
            min=0.0, max=1.0,
            default=0.0,
            )
    
    cell_scale = props.FloatVectorProperty(
            name="Scale",
            description="Scale Cell Shape",
            size=3,
            min=0.0, max=1.0,
            default=(1.0, 1.0, 1.0),
            )

    # -------------------------------------------------------------------------
    # Mesh Data Options

    use_smooth_faces = props.BoolProperty(
            name="Smooth Faces",
            default=False,
            )

    use_sharp_edges = props.BoolProperty(
            name="Sharp Edges",
            description="Set sharp edges when disabled",
            default=True,
            )

    use_sharp_edges_apply = props.BoolProperty(
            name="Apply Split Edge",
            description="Split sharp hard edges",
            default=True,
            )

    use_data_match = props.BoolProperty(
            name="Match Data",
            description="Match original mesh materials and data layers",
            default=True,
            )

    use_island_split = props.BoolProperty(
            name="Split Islands",
            description="Split disconnected meshes",
            default=True,
            )

    margin = props.FloatProperty(
            name="Margin",
            description="Gaps for the fracture (gives more stable physics)",
            min=0.0, max=1.0,
            default=0.001,
            )
    
    use_interior_vgroup = props.BoolProperty(
            name="Interior VGroup",
            description="Create a vertex group for interior verts",
            default=False,
            )
    
    # -------------------------------------------------------------------------
    # Physics Options
    
    mass_mode = props.EnumProperty(
            name="Mass Mode",
            items=(('VOLUME', "Volume", "Objects get part of specified mass based on their volume"),
                   ('UNIFORM', "Uniform", "All objects get the same volume"),
                   ),
            default='VOLUME',
            update = updateMass
            )
    
    mass = props.FloatProperty(
            name="Mass",
            description="Mass to give created objects",
            min=0.001, max=1000.0,
            default=1.0,
            update = updateMass
            )
   

    # -------------------------------------------------------------------------
    # Object Options

    use_recenter = props.BoolProperty(
            name="Recenter",
            description="Recalculate the center points after splitting",
            default=True,
            )

    use_remove_original = props.BoolProperty(
            name="Remove Original",
            description="Removes the parents used to create the shatter",
            default=True,
            )
            
        # -------------------------------------------------------------------------
    # Scene Options
    #

    group_name = props.StringProperty(
            name="Group",
            description="Create objects into a group "
                        "(use existing or create new)",
            )

    # -------------------------------------------------------------------------
    # Debug
    use_debug_points = props.BoolProperty(
            name="Debug Points",
            description="Create mesh data showing the points used for fracture",
            default=False,
            )
    
    use_debug_bool = props.BoolProperty(
            name="Debug Boolean",
            description="Skip applying the boolean modifier",
            default=False,
            )
    # -------------------------------------------------------------------------
    # Recursion

    recursion = props.IntProperty(
            name="Recursion",
            description="Break shards recursively",
            min=0, max=5000,
            default=0,
            )

    recursion_chance = props.FloatProperty(
            name="Random Factor",
            description="Likelihood of recursion",
            min=0.0, max=1.0,
            default=1.0,
            )

    recursion_chance_select = props.EnumProperty(
            name="Recurse Over",
            items=(('RANDOM', "Random", ""),
                   ('SIZE_MIN', "Small", "Recursively subdivide smaller objects"),
                   ('SIZE_MAX', "Big", "Recursively subdivide bigger objects"),
                   ('CURSOR_MIN', "Cursor Close", "Recursively subdivide objects closer to the cursor"),
                   ('CURSOR_MAX', "Cursor Far", "Recursively subdivide objects farther from the cursor"),
                   ),
            default='SIZE_MIN',
            )
            
    #recursion_source_limit = props.IntProperty(
    #        name="Source Limit",
    #        description="Limit the number of input points, 0 for unlimited (applies to recursion only)",
    #        min=0, max=5000,
    #        default=8,
    #        )

    recursion_clamp = props.IntProperty(
            name="Clamp Recursion",
            description="Finish recursion when this number of objects is reached (prevents recursing for extended periods of time), zero disables",
            min=0, max=10000,
            default=250,
            )
       
class DestructorTargetContext(types.PropertyGroup):
    
    hierarchy_depth = props.IntProperty(name = "hierarchy_depth", default = 1, min = 1, 
                                        description = "Up to which hierarchy depth given targets can be destroyed by this object")
                                        
    dead_delay = props.FloatProperty(name = "dead_delay", default = 0, min = 0, max = 10, 
                                    description = "After which time period activated objects get inactive again, set 0 for never")
                                    
    radius = props.FloatProperty(name = "radius", default = 1, min = 0, 
    description = "Speed independent destruction radius, is added to Speed Modifier")
    modifier = props.FloatProperty(name = "modifier",default = 0.25, min = 0, 
    description = "Modifier(factor) for destructors speed relative to object speed, is added to Radius")
                                        
    acceleration_factor = props.FloatProperty(name = "acceleration_factor", default = 1.0, min = 1.0, max = 20.0, 
        description = "Accelerate shards by this factor on impact")
  #  destruction_delay = props.IntProperty(name = "destruction_delay", default = 25, min = 0, max = 500, 
#        description = "Delay in logic ticks after which destruction should occur (repeatedly)", update = updateDestructionDelay)
    min_radius = props.FloatProperty(name = "min_radius", default = 1.0, min = 0.0, description = "Lower boundary of activation area")

class DestructionContext(types.PropertyGroup):
        
    use_debug_redraw = props.BoolProperty(
            name="Show Progress Realtime",
            description="Redraw as fracture is done",
            default=False
            )
    
    def _redraw_yasiamevil(self):
        #if bpy.context.active_object and bpy.context.active_object.destruction.dynamic_mode == 'D_PRECALCULATED':
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
       
    
#    def fracture_progress(self, prog):
#        
#        #width = bpy.context.area.width
#        #height = bpy.context.area.height
#        #bpy.context.area.tag_redraw()
#        
#        width = 600
#        height = 600
#        
#        # OpenGL setup
#        bgl.glMatrixMode(bgl.GL_PROJECTION)
#        bgl.glLoadIdentity()
#        bgl.gluOrtho2D(0, width, 0, height)
#        bgl.glMatrixMode(bgl.GL_MODELVIEW)
#        bgl.glLoadIdentity()
#
#        # BLF drawing routine
#       # path = bpy.context.user_preferences.filepaths.font_directory
#        #font_id = blf.load(path + "droidsans.ttf")
#        font_id = 0 # use default font   
#        blf.position(font_id, (width * 0.2), (height * 0.3), 0)
#        blf.size(font_id, 50, 72)
#        blf.draw(font_id, prog)
       
    
    def getVolumes():
        ret = []
        for o in bpy.context.scene.objects:
            if o.type == 'MESH' and o != bpy.context.scene.objects.active:
                ret.append((o.name, o.name, o.name))
        return ret
    
    destModes = [('DESTROY_F', 'Boolean Fracture', 'Destroy this object using boolean fracturing', 0 ), 
             ('DESTROY_E_H', 'Explosion Modifier', 
              'Destroy this object using the explosion modifier, forming a hollow shape', 1),
            # ('DESTROY_K', 'Knife Tool', 'Destroy this object using the knife tool', 2),
             ('DESTROY_V', 'Voronoi Fracture', 'Destroy this object using voronoi decomposition', 2),
             ('DESTROY_VB', 'Voronoi + Boolean', 'Destroy this object using simple voronoi and a boolean  modifier', 3),
             ('DESTROY_C', 'Blender Cell Fracture', 'Destroy this object using blenders builtin voronoi fracture', 4), 
             ('DESTROY_L', 'Loose Parts', 'Destroy this object into its predefined loose parts', 5)] 
      
             
    
    transModes = [('T_SELF', 'This Object', 'Apply settings to this object only', 0), 
             ('T_SELECTED', 'Selected', 'Apply settings to all selected objects as well', 1)]
             
    dynamicMode = [('D_PRECALCULATED', 'Precalculated', 'Precalculate fracture by hitting destroy button', 0), 
             ('D_DYNAMIC', 'Dynamic', 'Fracture dynamically via game engine', 1)]
    
    destroyable = props.BoolProperty(name = "destroyable",
                         description = "This object can be destroyed, according to parent relations", 
                         update = updateDestroyable)
    
    partCount = props.IntProperty(name = "partCount", default = 10, min = 1, max = 10000,
                        description = "How many shards shall be made out of this object")
    destructionMode = props.EnumProperty(items = destModes)
    destructor = props.BoolProperty(name = "destructor", 
                        description = "This object can trigger destruction")
    isGround = props.BoolProperty(name = "isGround", 
     description = "This object serves as a hard point, objects not connected to it will be destroyed")
     
    groundConnectivity = props.BoolProperty(name = "groundConnectivity", 
    description = "Determines whether connectivity of parts of this object is calculated, \
so only unconnected parts collapse according to their parent relations")
    gridDim = props.IntVectorProperty(name = "grid", default = (1, 1, 1), min = 1, max = 100, 
                                          subtype ='XYZ',
                                          description = "How many connectivity cells are created per direction")
                                          
    cubifyDim = props.IntVectorProperty(name = "cubifyDim", default = (1, 1, 1), min = 1, max = 100, 
                                          subtype ='XYZ', description = "How many cubes per direction shall be created" )
    
    gridBBox = props.FloatVectorProperty(name = "gridbbox", default = (0, 0, 0))
    destructorTargets = props.CollectionProperty(type = DestructorTargetContext, name = "destructorTargets")
    grounds = props.CollectionProperty(type = types.PropertyGroup, name = "grounds")
    transmitMode = props.EnumProperty(items = transModes, name = "Transmit Mode", default = 'T_SELECTED')
    active_target = props.IntProperty(name = "active_target", default = 0)
    active_ground = props.IntProperty(name = "active_ground", default = 0)
 
    groundSelector = props.StringProperty(name = "groundSelector", description = "Select Ground Object to add here and click + button")
    targetSelector = props.StringProperty(name = "targetSelector", description = "Select Destructor Target to add here and click + button")

    wallThickness = props.FloatProperty(name = "wallThickness", default = 0.01, min = 0, max = 10,
                                      description = "Thickness of the explosion modifier shards")
    pieceGranularity = props.IntProperty(name = "pieceGranularity", default = 4, min = 0, max = 100,  
    description = "How often the mesh will be subdivided before applying the explosion modifier, set higher to get more possible shards")
    
    applyDone = props.BoolProperty(name = "applyDone", default = False)
    previewDone = props.BoolProperty(name = "previewDone", default = False)
    
   
    pos = props.FloatVectorProperty(name = "pos" , default = (0, 0, 0))
    rot_start = props.IntProperty(name = "rot_start", default = -30, min = -90, max = 90)
    rot_end = props.IntProperty(name = "rot_end", default = 30, min = -90, max = 90)
    
    line_start = props.IntProperty(name = "line_start", default = 0, min = 0, max = 100)
    line_end = props.IntProperty(name = "line_end", default = 100, min = 0, max = 100)
    
    hierarchy_depth = props.IntProperty(name = "hierarchy_depth", default = 1, min = 1, 
                                        description = "Up to which hierarchy depth given targets can be destroyed by this object")
    flatten_hierarchy = props.BoolProperty(name = "flatten_hierarchy", default = False, 
                                           description = "Make one level out of hierarchy",
                                           update = updateFlattenHierarchy)
    
    voro_volume = props.StringProperty(name="volumeSelector", description = "Create point cloud in this object instead of the target itself")
    is_backup_for = props.StringProperty(name = "is_backup_for")
    wall = props.BoolProperty(name = "wall", default = True)
    tempLoc = props.FloatVectorProperty(name = "tempLoc", default = (0, 0, 0))
    origLoc = props.FloatVectorProperty(name = "origLoc", default = (0, 0, 0))
    restoreLoc = props.FloatVectorProperty(name = "restoreLoc", default = (0, 0, 0))
    
    voro_exact_shape = props.BoolProperty(name = "voro_exact_shape", description = "Use the vertices of the given object as point cloud")
    voro_particles = props.StringProperty(name = "voro_particles", description = "Use the particles of the given particle system as point cloud")
    voro_path = props.StringProperty(name="voro_path", default = bpy.app.tempdir + "test.out",
    description = "Set path and filename to intermediate voronoi file here, leave default and it will be created in blender executable dir")
    inner_material = props.StringProperty(name = "inner_material", description = "Material the inner shards will get")
    remesh_depth = props.IntProperty(name="remesh_depth", default = 0, min = 0, max = 10, 
    description = "Optionally apply remesh modifier prior to fracture with the given octree depth, set to 0 to omit remeshing")
    wasCompound = props.BoolProperty(name="wasCompound", default = False)
    children = props.CollectionProperty(type = types.PropertyGroup, name = "children")
    backup = props.StringProperty(name = "backup")
    dead_delay = props.FloatProperty(name = "dead_delay", default = 0, min = 0, max = 10, 
                                   description = "After which time period activated objects get inactive again, set 0 for never")
    deform = props.BoolProperty(name = "deform", default = False)
    cluster_dist = props.IntVectorProperty(name = "cluster_dist", default = (200, 200, 200), min = 0, subtype = 'XYZ',
                                    description = "Distance or size of cluster in % of according bounding box dimension")
    cluster = props.BoolProperty(name = "cluster", default = False, description = "Use Clustering of child objects to build irregular shapes")
    boolean_original = props.StringProperty(name = "boolean_original")
    dynamic_mode = props.EnumProperty(name = "dynamic_mode", items = dynamicMode, description = "Fracture Objects dynamically or precalculated",
                                      update = updateDynamicMode)
    converted = props.BoolProperty(name = "converted", default = False)
    radius = props.FloatProperty(name = "radius", default = 1.5, min = 0, description = "Speed independent destruction radius, is added to Speed Modifier")
    modifier = props.FloatProperty(name = "modifier",default = 0.25, min = 0, 
    description = "Modifier(factor) for destructors speed relative to object speed, is added to Radius")
    
    ascendants = props.CollectionProperty(type = types.PropertyGroup, name = "ascendants")
    
    # From pildanovak, fracture script
    crack_type = props.EnumProperty(name='Crack type',
        items=(
            ('FLAT', 'Flat', 'a'),
            ('FLAT_ROUGH', 'Flat rough', 'a'),
            ('SPHERE', 'Spherical', 'a'),
            ('SPHERE_ROUGH', 'Spherical rough', 'a')),
        description='Look of the fracture surface',
        default='FLAT')

    roughness = props.FloatProperty(name="Roughness",
        description="Roughness of the fracture surface",
        min=0.0,
        max=3.0,
        default=0.5)
   # End from        

   # grid = None
    jitter = props.FloatProperty(name = "jitter", default = 0.0, min = 0.0, max = 100.0) 
    
    cubify = props.BoolProperty(name = "cubify", description = "Split the given object to cubes before fracturing it, \
EACH cube will be further fractured to the given part count")
    cut_type = props.EnumProperty(name = 'Cut type', 
                items = (
                        ('LINEAR', 'Linear', 'a'),
                        ('ROUND', 'Round', 'a')),
                default = 'LINEAR') 
   
    cell_fracture = props.PointerProperty(type=CellFractureContext, name = "CellFractureContext")
    
    restore = props.BoolProperty(name = "restore")
    basic_fracture = props.BoolProperty(name = "basic_fracture", description = "Basic Fracture Options")
    advanced_fracture = props.BoolProperty(name = "advanced_fracture", description = "Advanced Fracture Options")
    auto_recursion = props.BoolProperty(name = "auto_recursion", description = "Automatic Recursion Options")
    setup_gameengine = props.BoolProperty(name = "setup_gameengine", description = "Game Engine Setup Options")
    re_unwrap = props.BoolProperty(name = "re_unwrap", description = "Unwrap shards with Smart Projection to reduce uv distortion")
    smart_angle = props.FloatProperty(name = "smart_angle", default = 66.0, min = 1.0, max = 89.0, description = "Angle limit for Smart Projection")
    glue_threshold = props.FloatProperty(name = "glue_threshold", default = 0.0, min = 0.0, 
        description = "Determines how high the speed between destructor and shard must be to activate the shard on hit, 0 for immediate break")
    dissolve_angle = props.FloatProperty(name = "dissolve_angle", 
                                         default = math.radians(2.5), 
                                         min = math.radians(0.0), 
                                         max = math.radians(180.0), 
                                         subtype = 'ANGLE',
                                         description = "Angle limit for Limited Dissolve")
    move_name = props.StringProperty(name = "move_name")
    orig_name = props.StringProperty(name = "orig_name")
    
    enable_all_children = props.BoolProperty(name = "enable_all_children", default = True, description = "Make child objects destructors as well", 
        update = updateEnableAllChildren )
    
    collision_margin = props.FloatProperty(name = "collision_margin", default = 0.01, min = 0.0, max = 1.0, 
           description = "Margin for collision bounds", update = updateCollisionMargin)
        
    acceleration_factor = props.FloatProperty(name = "acceleration_factor", default = 1.0, min = 1.0, max = 20.0, 
        description = "Accelerate shards by this force factor on impact")
    destruction_delay = props.IntProperty(name = "destruction_delay", default = 25, min = 0, max = 500, 
        description = "Delay in logic ticks after which destruction should occur (repeatedly)")
        
    individual_override = props.BoolProperty(name = "individual_override", description = "Adjust destructor settings individually per target")
    
    min_radius = props.FloatProperty(name = "min_radius", default = 0.0, min = 0.0, description = "Lower boundary of activation area")
    
    destructor_settings = props.BoolProperty(name = "destructor_settings")


def initialize():
    Object.destruction = props.PointerProperty(type = DestructionContext, name = "DestructionContext")
    Scene.player = props.BoolProperty(name = "player")
    Scene.setup_basic_scene = props.BoolProperty(name = "setup_basic_scene", description = "Setup Basic Scene", default = True)
    Scene.converted = props.BoolProperty(name = "converted")
    Scene.hideLayer = props.IntProperty(name = "hideLayer", min = 1, max = 20, default = 1, 
                                        description = "Layer where to hide the object hierarchy, needed for object substitution in game engine")
    Scene.backups = props.CollectionProperty(name = "backups", type = types.PropertyGroup)
    Scene.useGravityCollapse = props.BoolProperty(name = "useGravityCollapse", 
                                        description = "Collapse object automatically based on layer integrity (the lower, the weaker) ")
    Scene.collapse_delay = props.FloatProperty(name = "collapse_delay", min = 0.0, default = 1.0, 
                                        description = "Delay in seconds after which the dropping building should collapse completely") 
    Scene.dummyPoolSize = props.IntProperty(name = "dummyPoolSize", min = 10, max = 1000, default = 100,
                                            description = "How many dummy objects to pre-allocate for dynamic destruction (cant add them dynamically in BGE)")
    Scene.runBGETests = props.BoolProperty(name = "runBGETests")
    
    Scene.use_player_cam = props.BoolProperty(name = "use_player_cam", default = True, update = updateCam, 
                                              description = "Use Player Camera in Game Engine")
                                              
    Scene.custom_ball = props.StringProperty(name="custom_ball" , 
       description = "Select custom ball object here before setup player, this will be shot from the player instead of the default ball")
    #Scene.fracture_progress = props.StringProperty(name = "fracture_progress", description = "Fracture Progress")
    Scene.to_precalculated = props.BoolProperty(name = "to_precalculated")

    
    dd.DataStore.proc = Processor()  
  
def uninitialize():
    del Object.destruction
    
    


    
    