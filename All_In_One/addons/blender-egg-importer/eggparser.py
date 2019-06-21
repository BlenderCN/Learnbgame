""" This file contains the function parse_egg, which parses the .egg structure
and calls begin_child and end_child on the visitor methods as it discovers
.egg children. """

__all__ = ["parse_egg"]

def skip_whitespace(fp, char):
    """ Returns the next non-whitespace non-comment character. """

    read = fp.read
    while char.isspace() or char == '/': #FIXME
        char = read(1)
        if char != '/':
            continue

        char = read(1)
        if not char:
            return char
        elif char == '/':
            # Single-line comment.
            fp.readline()
            char = '\n'
        elif char == '*':
            # Scan for closing comment.
            while True:
                char = read(1)
                if not char:
                    return ''
                elif char == '*':
                    char = read(1)
                    if char == '/':
                        read(1)
                        break
    return char


def parse_number(str):
    str = str.lower()

    if str.startswith('nan'):
        return float('nan')
    elif str == '1.#inf':
        return float('inf')
    elif str == '-1.#inf':
        return float('-inf')
    elif str.startswith('0x'):
        return int(str[2:], 16)
    elif str.startswith('0b'):
        return int(str[2:], 2)
    else:
        return float(str)


class EggSyntaxError(Exception):
    pass


def parse_egg(fp, visitor, context=None):
    read = fp.read
    char = read(1)
    char = skip_whitespace(fp, char)

    while char == '<':
        _parse_egg_element(fp, visitor, context)

        # Skip spaces.
        char = read(1)
        char = skip_whitespace(fp, char)

    if char:
        raise EggSyntaxError("expected EOF or <, not %s" % (char))


def _parse_egg_element(fp, visitor, context):
    " Called after a < element is found that starts a new element. "
    read = fp.read

    # A sub-element.  Read what kind it is.
    type = ''
    char = read(1)
    while char != '>': #TODO prevent infinite loop
        type += char
        char = read(1)

    # Skip spaces.
    char = read(1)
    char = skip_whitespace(fp, char)

    # Now check for a name.
    name = ''
    if char == '{':
        # No name, just start processing the body.
        pass
    elif char == '"':
        # A quoted string.
        char = read(1)
        while char != '"':
            name += char
            char = read(1)
        char = read(1)
    else:
        # An unquoted string.
        while char not in ' \t\n\r{}"':
            name += char
            char = read(1)

    char = skip_whitespace(fp, char)
    if char != '{':
        raise EggSyntaxError("parsing <%s> %s: expected {, not %s" % (type, name, char))

    char = read(1)
    char = skip_whitespace(fp, char)

    # Check if there is a string or other value directly underneath.
    values = []
    while char != '}' and char != '<':
        value = ''
        if char == '"':
            # A quoted string.
            char = read(1)
            while char != '"':
                value += char
                char = read(1)
            char = read(1)
        else:
            # An unquoted string, or a number.  We can't know.
            while char not in ' \t\n\r{}"':
                value += char
                char = read(1)

        values.append(value)
        char = skip_whitespace(fp, char)

    if hasattr(visitor, 'begin_child'):
        child = visitor.begin_child(context, type, name, values)
    else:
        child = None

    # Read child elements.
    while char == '<':
        _parse_egg_element(fp, child, context)

        # Skip spaces.
        char = read(1)
        char = skip_whitespace(fp, char)

    if hasattr(visitor, 'end_child'):
        visitor.end_child(context, type, name, child)

    if not char:
        raise EggSyntaxError("parsing <%s> %s: reached end-of-file while parsing body" % (type, name))
    elif char != '}':
        raise EggSyntaxError("parsing <%s> %s: expected < or }, not %s" % (char))
