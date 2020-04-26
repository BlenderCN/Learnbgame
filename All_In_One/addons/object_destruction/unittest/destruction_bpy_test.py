import bpy
import unittest


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.seq = list(range(10))

    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, list(range(10)))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
             self.assertTrue(element in self.seq)

#load in via test suite ? group here only as test case ??
#or put it in SimpleFractureTestCase ??


#suite1: without subs
#suite2: with subs (test layers, backup relationship)
#suite3: hierarchical fracture / or new case 
#class BackupCreationCase(unittest.TestCase):
#        
#    def test_backup_reference(self):
#        #without subs -> backup with which name
#        self.assertEqual(parent.destruction.backup, backup)
#    
#    #   parent.backup == backup # 
#    def test_backup_backreference(self):
#        self.assertEqual(self.backup.destruction.is_backup_for, self.parent)
#        
        #   is_backup_for == parent #
#    def test_backup_relationship(self):
#        self.assertEqual(self.backup, self.parent.child[0])
#        
#    def test_backup_user(self):
#        self.assertTrue(backup.use_fake_user)
#    
#   backup name is S_Cube.000 #
#    def test_backup_name_end(self):    
#        self.assertTrue(parent.destruction.backup.endswith(".000"))
#        
#    def test_backup_name_start(self):
#        self.assertTrue(parent.destruction.backup.startswith("S_Cube"))
#
#class SimpleFractureCase(unittest.TestCase):
#     
#       tests from initial state
#        # precalculated
#        #   fracturing one object - with all methods -> setup variations->CASES or suites
#        #   parenting one object - with all methods

#    def setUp(self):
#        #select default cube "Cube", if not there create it
#        if "Cube" not in bpy.data.objects:
#            bpy.ops.mesh.primitive_cube_add()
#        else:
#            bpy.data.objects["Cube"].select = True
#            bpy.context.scene.objects.active = True
#        
#        #default = Boolean
#        bpy.ops.object.destroy()
#     
#    def test_child_count(self):
#        
#        self.assertTrue(self.children.count >= 1)
#        #self.assertEqual(self.children.count, parts)
#    
  #parent = EMPTY, P_O_S_Cube.000 #
#    def test_child_type(self):
#        
#   all shards are children, MESH #
#        for child in self.children:
#            self.assertEqual(child.type, 'MESH')
#    
#    def test_child_parent_type(self):
#        
#        self.assertEqual(self.parent.type, 'EMPTY')
#    
#    
#    def test_child_parent_name(self):
#        
#        self.assertTrue(self.child.parent != None)
#        for child in self.children:
#            self.assertEqual(child.parent.name, "P_O_S_Cube.000")
#        children name start with S_Cube 
#                 
#        
#        #   parent.children == parent.destruction.children
#     def test_parent_children(self):
#         self.assertEqual(len(parent.children), len(parent.destruction.children))
#         for i in range(0, len(parent.children)):
#             self.assertEqual(parent.children[i].name, parent.destruction.children[i])
#     
##        #   parent.destruction.ascendants = parent.parent.destruction.children + parent.destr.children
#     def test_ascendants(self):
#         self.assertEqual(len(parent.ascendants), len(parent.parent.ascendants) + len(parent.children))
#         lst = parent.children + parent.parent.ascendants
#         for i in range(0, len(lst)):
#            self.assertEqual(lst[i], parent.ascendants[i])
#            
#     #   child count is >= 1, or even count == parts    
#     def test_child_count(self):
#         self.assertTrue(len(children) > 1)
#         
#                     
##        #   voronoi -> file created ?
#     def test_voronoi_file(self):
#         self.assertTrue(getFile(file), None)
#         self.assertEqual(getFileName(file), "test.out")
#         
#     
##        #   volume points inside, particle/exact shape points = verts
#     def test_voronoi_volume(self):
#         self.assertTrue( min <= x <= max)
#         self.assertTrue( min <= y <= max)
#         self.assertTrue( min <= z <= max)
#         
#     def test_voronoi_exactShape(self):
#         self.assertEqual(len(vertices), len(points))
#         for i in range(0, len(vertices)):
#            self.assertEqual(vertices[i].location, points[i].location) 
#                  
##        #  loose parts test empty, object, common
#     def test_loose_parts(self):
#         self.assertEqual(empty.name, P_O_S + orig.name)
#         self.assertTrue(empty.children > 1)
#         self.assertEqual(orig.children, empty.children)
#         
#         
##        #   compound: only one, closest ?
#
#     def test_compound(self):
#         #one per level
#         self.assertEqual(compoundCount, 1)
#         #multiple wasCompounds
#         self.assertTrue(wasCompoundCount > 1)
#         #closest must have the flag set 
#         self.assertTrue(closest.game.use_collision_compound)        
#
#
#class SelectedFractureCase(unittest.TestCase)
#
#     def setUp(self):
#         #create 2 or 3 cubes, name 000 001 / name differently
#         #select them all
#         #start fracture (voronoi + boolean, voronoi, boolean explosion loose)
#     # different setups
#     def test_boolean_fracture_selected()
#     def test_voronoi_fracture_selected()
#     def test_vorobool_fracture_selected()
#     def test_explosion_fracture_selected()
#     def test_loose_parts_selected()
##        # fracturing of selected objects - with all methods
##        # several independent P_0s, 
##        # child name compared to P_0_S_Name
##        # children at according P_0s 
#        self.assertTrue(P0Count > 1)
#        self.assertEqual(P0.parent, None)
#        self.assertEqual(childOriginalName, parentOriginalName)
##        
##        #variations, where common tests need to be called too -> all common funcs + variable func ->suites or inheritance
##        # fracture with substitution
#        self.assertEqual (backup, child[0])
#        self.assertTrue(not backup.use_fake_user)
#        self.assertEqual(backup.layer == scene.hideLayer)
#        self.assertEqual(children.layer == scene.hideLayer)
#        self.assertTrue(backup in bpy.context.scene.objects)
##        
##        # fracture without substitution (layer positioning)
#        self.assertTrue(backup != child[0])
#        self.assertTrue(backup.use_fake_user)
#        self.assertTrue(not backup in bpy.context.scene.objects)
#        self.assertEqual(children.layer == 1)
##        
##        # with inner material -> test normal closer than epsilon -> material_index 1 or 2
#        self.assertTrue(normalSameDirection and material_index == 1)
#        self.assertTrue(normalOppDirection and material_index == 2)
##        
##        # with cubify -> test expected count and sizes
#        self.assertEqual(count, x*y*z)
#        self.assertEqual(sizeX, dimx/X)
#        self.assertEqual(sizeY, dimx/Y)
#        self.assertEqual(sizeZ, dimx/Z) # or at least very close
##        
##        
##        #tests after first / maybe second fracture
##        # all from initial plus  suite = map(Case, funcs)
##        #                        suite.add(varfunc) so no inheritance, but setup/tear down ?
##        # hierarchy test
##        #   P_1 present with children, P_1 child of P_0, name comparison 
##        #parenting/hierarchy test
##        #positioning of children(coords, hierarchy)
##        # must be around old backup center, check visually
##        # check: for each object one corresponding P_0 root empty, after splitting it
##        #   check for at least one P_1 empty and children
##        #check hierarchy layer setting, new objects on expected layer
#        self.assertTrue(len(newchild.children) > 0)
#        self.assertEqual(newchild.type, 'EMPTY') 
#        self.assertTrue(newchild.name.startswith("P_1_S_Cube")) #replace with other name too !
#        self.assertTrue(newchild.name.endswith(parentSuffix)) #001, 002 etc.
#        self.assertEqual(P0.pos, orig.pos)
##           
##        # fracture a compound
##        # old compound is wasCompound now and gone, one new compound: real or backup
##        #one compound per level:
##        #if no real compound is there check backup is compound
##        #delete fractured compound,  
#        self.assertEqual(compoundCount, 1)
#        self.assertTrue(closest.use_collision_compound and dist < all others)
#        self.assertTrue(oldCompound.name = name and oldCompound.wasCompound)
#        self.assertTrue(not oldCompound.game.use_collision_compound) 
#        self.assertTrue(backup.use_collision_compound and all are P_ children in this level)
##        
##        
##        # dynamic (via bpy) 
##        # dummy object allocation: present, expected count, (bpy)
#        self.assertEqual(dummyCount, expectedCount)
#        self.assertEqual(dummy[0].name, "Dummy.000") 
##        
##        
##        #tests after setup player
##        # check for all objects, logic bricks, scripts (presence ?)
##        # really test the blender operators ??? no 
##        # necessary before to game parenting
#        self.assertTrue(data.objects["Player"] != None)
#        
##        
##        #tests after conversion
##        # check dissolve of parenting, relationships
#        self.assertEqual(child.parent, None)
#        self.assertEqual(child.props["myParent"].value, parent.name)
#        
##        #tests with ground connectivity enabled
##        #add ground/remove ground, add /remove selection
##        # add count -> count +1
##        #remove count -> count -1, if 0 -> 0
##        # ground name in list ?, doublettes ?
#        self.assertEqual(count, 0)
#        ops.ground.add()
#        self.assertEqual(grounds[0], ground)
#        self.assertEqual(count, 1)
#        ops.ground.remove()
#        self.assertEqual(count, 0)
#        
#        self.assertEqual(count, 0)
#        ops.ground.remove()
#        self.assertEqual(count, 0)
#        
#        self.assertEqual(count, 1)
#        ops.ground.add(same)
#        self.assertEqual(count, 1)
#        self.assertEqual(grounds[0], ground)
#        
##        
##        #grid calculation - cell position, size, count
##        # grid present, gridcount = 1, cellcountX/Y/Z = expectedX/Y/Z
#        self.assertTrue(grid != None)
#        self.assertEqual(gridCells, x*y*z)
##        # ground cell positions, availability near ground(s) 
##        # groundCell.pos - ground < groundcellsize
#        self.assertTrue(groundCell.pos - ground < groundcellsize)
##        #one grid per object, even across hierarchy 
#        self.assertEqual(parent.grids, 1)
##        # at substitution, use data objects, traverse through children
##        # but multiple grounds possible
##        # if groundcellcount = 0 in destlist -> destroy
##        #multiple grounds, or-ing them if no connection to any ground, collapse
##        #destroyables as grounds -> grid calculation
##        #destroyable ground -> unmark groundcells in adjacent destroyables -> isGroundFor similar to is backup for
##        #dynamic ground connectivity, need to recalculate grid in bge for shards and treat
##        # "rest" of object as shard(s) too
##        # grid calculation check for found ground cells, check for complete destruction if not connected
##        #check grid size, coordinates, especially when rotation is involved
##         
##           
##        #tests with multiple (another) destructor
##        #add/remove destroyable see ground
##        #add selected, add whole level / remove accordingly
##        #add complete level (enter a number and select root) ? or add /remove selection
##        #destroyable destructors or destroyable as destructor -> test with custom ball 
##        
##        #voronoi file is created
##        #voronoi number of shards matches ? -> not guaranteed with boolean ops involved
##        #but at least one empty and one shard must be present
##        #vornoi + boolean / boolean fracture -> no manifolds
##        #explosion modifier ????
##          
##        #use clusters check what ? approx. size ???, multiple childs -> in bge ! after setup
##      
##        #ball is created on layer 2, check custom ball (in game engine)
##        #check to game parenting conversion
##        
##        #undestroy : same object, name, state of this object as before (backup is used), check positioning
##        #and re-fracturing it (problem)
##       
##       
##       
##       
##       
##        #use cases, workflows:
##        
##        #smashing on ground, multiple destructors, level correctness, destroyable correctness, expected parts, parents, objects in bge
##        # voronoi particle system, exact shape check object positions at least (shape is checked visually)
##        
##         
##        #demo video: smashing complex objects, dynamic fracture ( with pre-allocation) otherwise wrong physics mesh and crashes because
##        #of sharing this mesh across instances of same object
##        
##        #smashing compound objects (wall with interior wood (splinters), bricks and below (done via intersect e.g 2 - 3 shards each brick)
##        #random points / random volume object
##        #davor ein Putz-Objekt, Fenster Türen Decken Dach(ziegel)-> 
##        #brick destruction mode, "Verschränkung" von Steinen, displacement of each 2nd row by half of "face-local" y axis (if possible)
##        #schon mit Bordmitteln lösbar, evtl noch boolean zum Cutten
##        
##        #test speed/radius/object death delay (trivial tests, test a timer ??? possible ???)
##        #blender has a global object death delay for now, keep mine local, add speed / dist threshold to omit death or re-enable (first is better)
##
     
        

def run():
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)