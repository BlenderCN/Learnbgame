import math

def vec3(v = None, x = None, y = None, z = None):
  if v != None:
    return (round(v[0], 6), round(v[1], 6), round(v[2], 6))
  else:
    return (round(x, 6), round(y, 6), round(z, 6))
    
def vec2(v = None, x = None, y = None):
  if v != None:
    return (round(v[0], 6), round(v[1], 6))
  else:
    return (round(x, 6), round(y, 6))
    
