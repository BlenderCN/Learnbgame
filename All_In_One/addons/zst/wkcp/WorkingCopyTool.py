# Setting for Working Copy Add-On Prooerties
# Setting for Add-On Prooerties

import bpy, os

# 1. load all py file at this directory
# -> py file define some classes inherit operator class or panel class and the other
#
# 2. registor and unregistor loaded classes
def register():
    print("*** Start Testing ***")

def unregister():
    print("*** End Testing ***")


print("*** Root Dir ***")
print("dirname: %s" % os.path.dirname(os.path.abspath(__file__)))
if __name__ == "__main__":
    print("__name__ Start")
    register()

print("*** After Root ***")
