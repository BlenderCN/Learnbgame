import re
import ast

# We want to grab all of the ptAttributes initialized at the start of every
# script.  We could use the Abstract Syntax Tree parser... except that if we
# try to use that on a script written for a substantially different version of
# Python (e.g., parsing Path of the Shell scripts in the Py 3.4 interpreter),
# we'll get a nice *boom*.  I don't want to write a full parser, so we'll
# compromise.
#
# Here's what we're going to do:
# Using a regex we'll collect all of the assignments that occur using the
# ptAttrib initializers, and then process them.  Some arguments can contain
# lists and tuples. We can't use literal_eval since the function call can also
# contain keyword arguments, which from its point of view is an expression.
# Writing a full parser in Python's regex is not going to happen, so we'll lump
# them all together and throw them at an AST visitor to do the heavy lifting
# and give us back a nice data structure.


# This is the regex we'll be using to find all of the ptAttrib assignments.
# It captures commented-out assignments too, but the AST parser will wisely
# recognize them as comments and won't trouble us with them.
ptAttribFunction = "(#*\w+?\s*?=\s*?ptAttrib[^()]+?\s*?\(.+\).*\s*?)"
funcregex = re.compile(ptAttribFunction)


class PlasmaAttributeVisitor(ast.NodeVisitor):
    def __init__(self):
        self._attributes = dict()

    def visit_Module(self, node):
        # Filter out anything that isn't an assignment, and make a nice list.
        assigns = [x for x in node.body if isinstance(x, ast.Assign)]
        for assign in assigns:
            # We only want:
            #  - assignments with targets
            #  - that are taking a function call (the ptAttrib Constructor)
            #  - whose name starts with ptAttrib
            if (len(assign.targets) == 1
                and isinstance(assign.value, ast.Call)
                and hasattr(assign.value.func, "id")
                and assign.value.func.id.startswith("ptAttrib")):
                # Start pulling apart that delicious information
                ptVar = assign.targets[0].id
                ptType = assign.value.func.id
                ptArgs = []
                for arg in assign.value.args:
                    value = self.visit(arg)
                    ptArgs.append(value)

                # Some scripts use dynamic ptAttribs (see: dsntKILightMachine)
                # which only have an index.  We don't want those.
                if len(ptArgs) > 1:
                    # Add the common arguments as named items.
                    self._attributes[ptArgs[0]] = {"name": ptVar, "type": ptType, "desc": ptArgs[1]}
                    # Add the class-specific arguments under the 'args' item.
                    if ptArgs[2:]:
                        self._attributes[ptArgs[0]]["args"] = ptArgs[2:]

                # Add the keyword arguments, if any.
                if assign.value.keywords:
                    for keyword in assign.value.keywords:
                        self._attributes[ptArgs[0]][keyword.arg] = self.visit(keyword.value)
        return self.generic_visit(node)

    def visit_Name(self, node):
        # Workaround for old Cyan scripts: replace variables named "true" or "false"
        # with the respective constant values True or False.
        if node.id.lower() in  {"true", "false"}:
            return ast.literal_eval(node.id.capitalize())
        return node.id

    def visit_Num(self, node):
        return node.n

    def visit_Str(self, node):
        return node.s

    def visit_List(self, node):
        elts = []
        for x in node.elts:
            elts.append(self.visit(x))
        return elts

    def visit_Tuple(self, node):
        elts = []
        for x in node.elts:
            elts.append(self.visit(x))
        return tuple(elts)

    def visit_NameConstant(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        if type(node.op) == ast.USub:
            return -self.visit(node.operand)
        elif type(node.op) == ast.UAdd:
            return self.visit(node.operand)

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)


def get_attributes_from_file(filepath):
    """Scan the file for assignments matching our regex, let our visitor parse them, and return the
       file's ptAttribs, if any."""
    with open(str(filepath)) as script:
        return get_attributes_from_str(script.read())

def get_attributes_from_str(code):
    results = funcregex.findall(code)
    if results:
        # We'll fake the ptAttribs being all alone in a module...
        assigns = ast.parse("\n".join(results))
        v = PlasmaAttributeVisitor()
        v.visit(assigns)
        if v._attributes:
            return v._attributes
    return {}

if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys

    if len(sys.argv) != 2:
        print("Specify a path containing Plasma Python!")
    else:
        readpath = sys.argv[1]
        files = Path(readpath).glob("*.py")
        ptAttribs = {}
        for scriptFile in files:
            attribs = get_attributes_from_file(scriptFile)
            if attribs:
                ptAttribs[scriptFile.stem] = attribs

        jsonout = open("attribs.json", "w")
        jsonout.write(json.dumps(ptAttribs, sort_keys=True, indent=2))
