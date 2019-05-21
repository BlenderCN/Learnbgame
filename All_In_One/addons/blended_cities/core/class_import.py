##\file
# class_import.py
# provide functions to link existing
# builders classes to
# bpy.context.scene.city.builders, as for .buildings
# classes are appended from the builders folder
print('class_import.py')
import bpy
import sys
import os
from blended_cities.core.main import BlendedCities

builders_list  = []

# registers a new builder class
def register_builder(builderClass,uiClass):
    global builders_list
    global BC_builders
    bpy.utils.register_class(builderClass)
    bpy.utils.register_class(uiClass)
    builders_list.append(builderClass)
    collection = bpy.props.CollectionProperty(type=builderClass)
    exec('BC_builders.%s = collection'%(builderClass.bc_collection))
    update_builders_dropdown()

# unregisters a new builder class
def unregister_builder(builderClass,uiClass):
    global builders_list
    exec('del BlendedCities.builders.%s'%builderClass.bc_collection)
    bpy.utils.unregister_class(builderClass)
    bpy.utils.unregister_class(uiClass)
    builders_list.remove(builderClass)

    update_builders_dropdown()

# updates dropdown in the main tagging ui
def update_builders_dropdown():
    global builders_list
    class_selector = []
    #class_selector = [ ('nones','Empty outline','store only the outline geometry') ]
    for cl in builders_list :
        class_selector.append( (cl.bc_collection,cl.bc_label,cl.bc_description) )
    bpy.types.WindowManager.city_builders_dropdown = bpy.props.EnumProperty( items = class_selector, name = "Builders", description = "" )


def register_default_builders():
    '''seek the builders folders for existing builders classes (and their gui)'''
    # seek and register
    mod = sys.modules['blended_cities']
    path_builders = mod.__path__[0] + '/builders'
    global builders_list
    print('\n. builders :')
    for file in os.listdir(path_builders) :
        if file[0:4] == 'bld_' and file[-3:]=='.py':
            classname = 'BC_'+file[4:-3]
            exec('from blended_cities.builders.%s import *'%file[0:-3],globals())
            builderClass = eval(classname)
            panelClass = eval('%s_panel'%classname)
            register_builder(builderClass,panelClass)
            print('\timported %s'%file[4:-3])
    print()
    

def unregister_default_builders():
    '''seek the builders folders for existing builders classes (and their gui)'''
    # seek and register
    mod = sys.modules['blended_cities']
    builders_dir = mod.__path__[0] + '/builders'
    global builders_list
    print('. builders :')
    for file in os.listdir(builders_dir) :
        if file[0:3] == 'bld_' :
            classname = 'BC_'+file[3:-3]
            exec('from blended_cities.builders.%s import *'%file[0:-3],globals())
            builderClass = eval('BC_%'%classname)
            panelClass = eval('BC_%_panel'%classname)
            unregister_builder(builderClass,panelClass)
            print('    unregistered %s'%file[3:-3])
    print()