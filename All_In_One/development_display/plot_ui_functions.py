import numpy as np
from math import *
import bpy

def valid_expression(expr=''):
    
    if not expr:
        return False
        
    x=1
    try:
        result = eval(expr)
    except:
        return False

    return True


def eval_expression(expr=''):
    
    settings = bpy.context.window_manager.display_settings
    interval = settings.plot_ui_interval
    if interval[0] >= interval[1]:
        return [0], [0]
    X = np.arange(*interval)
    Y = []
    for x in X:
        Y.append(eval(expr))
    return X, Y

