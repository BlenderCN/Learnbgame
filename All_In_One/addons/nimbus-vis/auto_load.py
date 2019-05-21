import os
import sys
import importlib


def init():
    register()
    
def register_module_from_package(package_name):
    importlib.import_module()
    

def register_all():
    print("Yeetis")
    
def register():
    register_all()
    print("All auto-load features loaded!")
    
def unregister():
    
    print("All auto-load features unloaded.")



    
    #enables standalone support    
if __name__ == "__main__":
    register()