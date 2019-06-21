###################################
#enables standalone support
if __name__ == "__main__":
    import os
    import sys
    from os.path import dirname, join, abspath, basename
    #Error handling if started from within blender's IDE
    try:
        main_package = dirname(abspath(__file__))
        print("main_package set!")
    except NameError:
        print("__file__ didn't work. trying bpy.")
        try:
            import bpy
            main_package = dirname(bpy.data.filepath)
            print("main_package set!")
        except:
            raise NameError("Can't hook blend file.")
    #
    #Iterates until it finds nimbus_vis or has run 10 times #10 subdirs max
    iter = 0
    #
    while basename(main_package) != "nimbus_vis" and iter in range(10):
        main_package = dirname(main_package)
        iter = iter + 1
    #
    if not main_package in sys.path:
        sys.path.append(main_package)
        print(main_package + " appended to sys path")
    #
    library = join(main_package, "libs")
    #
    if not library in sys.path:
        sys.path.append(library)
        print(library + " appended to sys path")
    #
    os.chdir(main_package) ###THIS IS VERY IMPORTANT AND FIXES EVERYTHING
    ####################
    anim_nodes_lib = join(main_package, "anim_node_port", "animation_nodes")
    #
    if not anim_nodes_lib in sys.path:
        sys.path.append(anim_nodes_lib)
        print(anim_nodes_lib + " appended to path")
#################################

import bpy
from animation_nodes.base_types import AnimationNode as AnNode


class TestNode(bpy.types.Node, AnNode):
    bl_idname = "al_TestNode"
    bl_label = "Test"
    
    def create(self):
        self.newInput("Object", "Thing", "thing")
        
    def execute(self, thing):
        if thing is None:
            return