import bpy
import bge
import unittest
import random


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
    
    #        #bge tests
#        # build up child structure (maybe unnecessary, use bpy properties instead)-> common tests and later refactoring
#          childs[p] = parent.children
#          childs[p] = parent.destruction.children
#          childCount = ExpectedCount
#        #children dict: children[p] vs. destruction.children, last is better, no extra dictionary necessary
#        # parent , firstparent, compound buildup
#        # call collide function manually, test dissolve, swapBackup, activate calls when expected
#        # only objects in proximity get activated / dissolved
#        # check for correct hierarchy level (and not further)
#        # check for only registered objects being swapped
#        # with flatten hierarchy -> test for one level, all children must be present (in bge!)
#        #flatten hierarchy -> number of levels must be 1, all parts child of P_0xxxx
#        # check for hierarchy > 2 -> in bge structure children[p] is different from bpy.destruction.children maybe need both indeed ? 
#        # without subs: Expected failure in bge (if no real compound present
#        # dynamic (via bge)
#        #usage in bge #gone after quitting bge -> test operator, after some time quit bge automatically ? 
#        #bge
         #
         
         #test swap dynamic, meshes need to be there, children, backups
#        #check registration of destructables (destructor destroys distinct destroyable up to given level
#        #problematic: correct destruction in game engine (hierarchy with/without substitution
#        #omit lower levels of destruction by omitting lower hierarchies, add levels by adding hierarchies 
#        
         #bge getFaceDistance/projection
         #setupClusters
         #determine leafparents = expectedleafs
         #all inside "range" must be children (of higher level(s)) 
         
         #setup flatten hierarchy, substitution (initial, later)

def run():
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
