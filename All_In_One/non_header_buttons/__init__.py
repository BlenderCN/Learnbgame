#----------------------------------------------------------
# File __init__.py
#----------------------------------------------------------

# section 1
# bl_info must be initialized in this file, as it gets parsed
bl_info = \
    {
        "name": "Non Header Buttons",
        "author" : "Walid Shouman <eng.walidshouman@gmail.com>",
        "version" : (1, 0, 0),
        "blender" : (2, 7, 9),
        "location" : "Every editor(space) and area which can have a button registered to.",
        "description" :
            "Add a button to each editor except for headers.",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category": "Learnbgame",
    }
# end of section 1

import os
current_directory = os.path.dirname(os.path.abspath(__file__))

# section 2
# support addon reloading
reloadfile = os.path.join(current_directory, '__reload__.py')
exec(open(reloadfile).read())
# end of section 2

import bpy

# section 3
# support addon registration
registrationfile = os.path.join(current_directory, '__register__.py')
exec(open(registrationfile).read())

if __name__ == "__main__":
    register()
# end of section 3
