

import contextlib, os

@contextlib.contextmanager
def chdir(to):
    original = os.getcwd()
    try: 
      os.chdir(to)
      yield
    finally:
      os.chdir(original)

def get_all_parents(objects):
  """
  Gets a set of all direct ancestors of all objects passed in.
  This will work as long as the objects have a single 'parent' attribute that
  either points to the tree parent, or is None.
  """
  objs = set()
  if not hasattr(objects, "__iter__"):
    objects = [objects]
  for item in objects:
    objs.add(item)
    if item.parent:
      objs.update(get_all_parents(item.parent))
  return objs

def get_root_object(obj):
  """Given an object, returns the root node.
  Follows 'parent' attribute references until none remain."""
  obj = obj
  while obj.parent:
    obj = obj.parent
  return obj


def matrix_string(mat, title="Matrix", prefix=""):
  pad  = len(title) * " "
  lines = [
    "{} ┌ {: 6.4f} {: 6.4f} {: 6.4f} {: 6.4f} ┐".format(title, *mat[0]),
    "{} │ {: 6.4f} {: 6.4f} {: 6.4f} {: 6.4f} │".format(pad, *mat[1]),
    "{} │ {: 6.4f} {: 6.4f} {: 6.4f} {: 6.4f} │".format(pad, *mat[2]),
    "{} └ {: 6.4f} {: 6.4f} {: 6.4f} {: 6.4f} ┘".format(pad, *mat[3])]

  return "\n".join(prefix + line for line in lines) \
    .replace("-0.0000", " 0.0000") \
    .replace(".0000", ".    ") \
    .replace(" 0. ", "  . ")

def vector_string(vec):
  parts = ["{: 6.4f}".format(x) for x in vec]
  s = ",".join(parts)#.replace("-0.0000", " 0.0000") \
  #   .replace(".0000", ".    ") \
  #   .replace(" 0. ", "  . ")

  return "[ " + s + " ]"


def print_edm_graph(root, inspector=None):
  """Prints a graph of the tree, optionally with an inspection function"""

  def _printNode(node, prefix=None, last=True):
    if prefix is None:
      firstPre = ""
      prefix = ""
    else:
      firstPre = prefix + (" ┗━" if last else " ┣━")
      prefix = prefix + ("   " if last else " ┃ ")
    print(firstPre + repr(node))
    if inspector is not None:
      inspectPrefix = (" ┃ " if node.children else "   ")
      inspector(node, prefix + inspectPrefix)
    for child in node.children:
      _printNode(child, prefix, child is node.children[-1])

  _printNode(root)