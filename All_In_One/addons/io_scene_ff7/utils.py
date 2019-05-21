_debug = False

def setDebug(debug_value):
    global _debug
    _debug = debug_value
    
def debug(message):
    if _debug:
        print(message)