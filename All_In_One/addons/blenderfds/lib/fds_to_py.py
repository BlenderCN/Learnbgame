"""BlenderFDS, tokenize FDS file in a readable notation"""

import re

DEBUG = False

def _extract(value, pattern):
    """Extract compiled regex pattern from value sequentially"""
    start = 0
    results = list()
    while True:
        m = pattern.match(value, start)
        if not m: break
        results.append(list(m.groups()))
        start = m.end(0)
    if DEBUG:
        print("BFDS: fds_to_py._extract:")
        for result in results: print(", ".join("<{}>".format(item) for item in result))
    return results

choose_fds_to_py = {".TRUE.": "True", ".FALSE.": "False"}

def tokenize(fds_file):
    """Parse and tokenize fds file.
    Input:  "&OBST ID='Hello' XB=1,2,3,4,5,6 /"
    Output: [[fds_original, fds_label, [[fds_original, fds_label, fds_value], ...]], ...]
    Output: [["&OBST ID='Hello' XB=1,2,3,4,5,6 /", "OBST", [["ID='Hello'", "ID", "Hello"], ...]], ...]
    """
    # Extract namelists
    regex = r"""
        .*?    # zero or more chars of any type (not greedy) (re.DOTALL) 
        (?P<namelist>   # namelist, group "namelist"
            ^&                              # ampersand after newline (re.MULTILINE)
            (?P<label>[A-Z0-9_]{4})         # namelist label, 4 chars, group "fds_label"
            [,\s]+                          # followed by one or more separators of any kind
            (?P<params>                     # namelist parameters, group "fds_params"
                (?: '[^']*?' | "[^"]*?" | [^'"] )*?     # namelist params; protect chars in strings, "no params" allowed by *
            )
        [,\s]*          # followed by zero or more separators of any kind
        /               # closing slash, anything outside &.../ is a comment and is ignored
        )    
    """, re.VERBOSE | re.MULTILINE | re.DOTALL
    pattern = re.compile(regex[0], regex[1])
    namelists = _extract(fds_file, pattern)
    # Extract parameters
    regex = r"""
        [,\s]*          # zero or more separators
        (?P<fds_original>   # the original namelist group
            (?P<fds_label>      # the parameter label group. Could be: ID or MATL_ID(1:2,1)
                [A-Z0-9_]+          # First part, as in MATL_ID
                (?:\([0-9:,]+\))?   # Second optional part, as in (1:2,1)
            )
            [\s]*           # followed by zero or more spaces
            =               # an equal sign
            [\s]*           # followed by zero or more spaces
            (?P<fds_value>  # the value group
                (?: '[^']*?' | "[^"]*?" | [^'"] )+? # protect chars in strings, anonymous group, "no value" not allowed by +
            )
            (?=             # stop the previous value match when it is followed by
                [,\s]+          # one or more separators
                [A-Z0-9_]+      # another parameter label (same definition as before)
                (?:\([0-9:,]+\))?
                [\s]*           # zero or more spaces
                =               # an equal sign
                |               # or
                $               # the end of the string
            )
        )
    """, re.VERBOSE | re.MULTILINE | re.DOTALL
    pattern = re.compile(regex[0], regex[1])
    for namelist in namelists:
        # Extract parameter
        params = list()
        for param in _extract(namelist[2], pattern):
            # Unpack and clean original
            fds_original, fds_label, fds_value = param       
            fds_original = "=".join((fds_label, fds_value))
            # Translate value from FDS to Py
            try: fds_value = eval(choose_fds_to_py.get(fds_value, fds_value))
            except:
                print("BFDS: fds_to_py.tokenize: '{}' parameter evaluation error:\n<{}>".format(fds_label, fds_original))
            # Append
            params.append((fds_original, fds_label, fds_value))
        # Update extracted
        namelist[2] = params
    # Return
    return namelists

# Test
if __name__ == "__main__":
    # Get fds_file
    import sys
    if not sys.argv: exit()
    print("BFDS tokenizing:", sys.argv[1])
    with open(sys.argv[1], 'r') as f:
        fds_file = f.read()
    # Tokenize it
    results = tokenize(fds_file)
    print("BFDS: fds_to_py.__main__:")
    for result in results: print(", ".join("<{}>".format(item) for item in result))
