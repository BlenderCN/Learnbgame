"""BlenderFDS, other utilities"""

def isiterable(var):
    """Check if var is iterable or not
    
    >>> isiterable("hello"), isiterable((1,2,3)), isiterable({1,2,3})
    (False, True, True)
    """
    # A str is iterable in Py... not what I want
    if isinstance(var, str): return False
    # Let's try and fail nicely
    try:
        for item in var: break
    except TypeError: return False
    return True
    
def factor(n):
    """Generator for prime factors of n.
Many thanks Dhananjay Nene (http://dhananjaynene.com/)
for publishing this code"""
    yield 1  
    i = 2  
    limit = n**0.5  
    while i <= limit:
        if n % i == 0:
            yield i
            n = n / i
            limit = n**0.5  
        else:
            i += 1  
    if n > 1:  
        yield int(n)
        
def is_writable(filepath):
    """Check if filepath is writable"""
    return write_to_file(filepath, "Test")

def write_to_file(filepath, text_file):
    """Write text_file to filepath"""
    if text_file is None: text_file = str()
    try:
        with open(filepath, "w") as out_file: out_file.write(text_file)
        return True
    except IOError:
        return False
