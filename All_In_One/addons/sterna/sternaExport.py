import bpy, sys, importlib, math, re
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import Operator
try:
    import sternaMain
except ImportError:
    pass


def init():
    global sternaMain
    try:
        sternaMain
    except:
        sternaMain = sys.modules[modulesNames['sternaMain']]

def register():
    bpy.utils.register_class(SternaExport)
    bpy.types.INFO_MT_file_export.append(menu_sterna_export)
    init()


def unregister():
    bpy.utils.unregister_class(SternaExport)
    bpy.types.INFO_MT_file_export.remove(menu_sterna_export)


class SternaExport(Operator, ExportHelper):
    """ Exports a sterna to a SNAC file.
    """
    bl_label = "Export Snac"
    bl_idname = "sterna.export"


    filename_ext = ".snac"

    filter_glob = StringProperty(
            default="*.snac",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    meta_data = BoolProperty(
            name="Add comments",
            description="Annotate the SNAC file with comments describing the fields.",
            default=True,
            )

    generate_ug = BoolProperty(
            name="Generate UG pairs",
            description="Generates a partial primary structure with every n:th basepair replaced with a UG-pair.",
            default=True,
            )

    add_promoters = BoolProperty(
            name="Add promoter sequence to the strand.",
            description="Adds promoter sequences to the beginning and the end of the RNA strand.",
            default=True,
            )

    ug_proportion = FloatProperty(
            name="UG proportion",
            description="The proportion of UG pairs per a domain.",
            default= 1/6,
            )

    ug_min = IntProperty(
            name="Minimum number of UG pairs",
            description="The minimum number of UG pairs to generate per a domain.",
            default= 0,
            )


    padding = EnumProperty(
            name="Replace padding with",
            description="Replace unpaired bases between domains with ",
            items=(('NONE', "Nothing.", "Replace padding with nothing."),
                   ('A', "A's", "Replace padding with A's."),
                   ('C', "C's", "Replace padding with C's."),
                   ('G', "G's", "Replace padding with G's."),
                   ('U', "U's", "Replace padding with U's."),
                   ('W', "W's", "Replace padding with W's."),
                   ('S', "S's", "Replace padding with S's."),
                   ('M', "M's", "Replace padding with M's."),
                   ('K', "K's", "Replace padding with K's."),
                   ('R', "R's", "Replace padding with R's."),
                   ('Y', "Y's", "Replace padding with Y's."),
                   ('B', "B's", "Replace padding with B's."),
                   ('D', "D's", "Replace padding with D's."),
                   ('H', "H's", "Replace padding with H's."),
                   ('V', "V's", "Replace padding with V's."),
                   ('N', "N's", "Replace padding with N's.")),
            default='A',
            )

    def execute(self, context):
        return export(context, self.filepath, self.meta_data, self.add_promoters, self.ug_proportion * self.generate_ug, self.ug_min, self.padding)


def menu_sterna_export(self, context):
    """ Add an entry to export menu.
    """
    self.layout.operator(SternaExport.bl_idname, text="Snac (.snac)")


def export(context, filepath, meta_data, add_promoters, ug_proportion, ug_min, padding):
    """ Exports a sterna to a SNAC file according to input parameters.

    Args:
        context
        filepath
        meta_data -- bool, add meta data
        add_promoters -- bool, add promoters at the start and the end of the strand
        ug_proportion -- float, proportion of basepairs to replace with U's and G's
        ug_min -- minimum number of UG pairs per domain
        padding -- char, replace padding between helices with this
    """
    #import importlib
    #importlib.reload(sternaMain)
    positions, dotbracket, p_numbering = sternaMain.export_sterna_helix(context.object)

    partial_primary = get_partial_primary(dotbracket, ug_proportion, ug_min, padding)
    partial_primary = re.sub("\(|\)|\[|\]|\.", "N", partial_primary)
    partial_primary = re.sub("U|G", "K", partial_primary)


    if add_promoters:
        positions = 20 * "0 0 0, " + positions + 15 * ", 0 0 0"
        dotbracket = "...................." + dotbracket + "..............."
        partial_primary = "GACUAAUACGACUCACUAUAGGG" + partial_primary[3:] + "NNNNNNNNNNNNNNN"
        #insert CCC
        j = 0
        for i, c in enumerate(dotbracket):
            if c == "(": j += 1
            elif c == ")": j -= 1
            else: continue
            if j == 0:
                partial_primary = partial_primary[:i-2] + "CCC" + partial_primary[i+1:]
                break


    assert len(dotbracket) == len(partial_primary) == len(positions.split(","))
    print("partial primary:", partial_primary)

    with open(filepath, "w") as f:


        #primary structure
        if partial_primary != None:
            if meta_data:
                f.write("# Nucleic acid notation  '|':\n")
                f.write("# "+ get_primary_meta(partial_primary, dotbracket) + "\n")
            f.write("primary_structure: ")
            f.write(partial_primary + "\n")

        #secondary structure
        if meta_data:
            f.write("# domains separated by |:\n")
            f.write("# "+ get_secondary_meta(dotbracket) + "\n")
        f.write("secondary_structure: ")
        f.write(dotbracket + "\n")

        #tertiary structure
        if meta_data:
            f.write("# the following numbers are assigned to pseudoknot complexes in the same order as they appear in the secondary structure. For instance, 1 2 1 2 would mean that the first complex connects to the third one, and the second one connects to the fourth. \n")
        f.write("pseudoknot_numbering: ")
        f.write(p_numbering + "\n")
        
        #positions
        if meta_data:
            f.write("# The coordinates are represented as comma-separated three-tuples, x y z, in nanometers. The coordinates correspond to the primary and secondary structure in the same order.\n")
        f.write("positions: [")
        f.write(positions)
        f.write("]\n")


    return {'FINISHED'}

def get_primary_meta(primary_structure, secondary_structure):
    """ returns a human readable version of the primary structure.

    Returns:
        str
    """
    domains = split_to_domains(secondary_structure)
    result = []
    i = 0
    for d in domains:
        result.append("".join(primary_structure[i : i + len(d)]))
        i += len(d)
    return " | ".join(result)

def get_secondary_meta(secondary_structure):
    """ Returns a human readable version of the secondary structure

    Returns:
        str
    """
    domains = split_to_domains(secondary_structure)
    result = " | ".join(["".join(x) for x in domains])
    print("Domains:", result)
    return result


def get_partial_primary(secondary_structure, ug_proportion, ug_min, padding):
    """ Returns the secondary structure with certain entries replaced with known primary structure bases.

    Args:
        secondary_structure
        ug_proportion -- float, proportion of base pairs to replace with U's and G's
        ug_min -- minimum number of UG pairs per domain
        padding -- char, replace padding between helices with this

    Returns:
        str
    """
    r_open = "U"
    r_close = "G"
    r_padding = padding
    if ug_proportion == 0 and ug_min == 0 and padding == 'NONE':
        return None
    domains = split_to_domains(secondary_structure)
    primary_structure = []
    for d in domains:
        s = []
        print("".join(d))
        if ("(" in d or ")" in d) and not ("[" in d or "]" in d):
            n = max(int(len(d) * ug_proportion), ug_min)
            if n < 1:
                s.extend(d)
            else:
                p = int(len(d) / n)
                print("prop: {}, len: {}, n: {}, p: {}".format(ug_proportion, len(d), n, p))
                for i, sym in enumerate(d):
                    i += int(p/2)
                    if i % p == 0:
                        if sym == "(":
                            s.append(r_open)
                        else:
                            s.insert(0, r_close)
                    else:
                        if "(" in d:
                            s.append(sym)
                        else:
                            s.insert(0, sym)
        elif "[" in d or "]" in d or padding == 'NONE':
            s.extend(d)
        else:
            s = len(d) * [r_padding]
        primary_structure.append("".join(s))
    return "".join(primary_structure)


    return domains


def split_to_domains(secondary_structure):
    """ Splits the secondary structure to domains.

    Returns:
        array
    """
    pairs = {}
    stack = []
    p1 = "..[[[[[[."
    p2 = "..]]]]]]."
    ss = secondary_structure.replace(p1, "P1").replace(p2, "P2")
    #print(ss)

    for i, sym in enumerate(ss):
        if sym == "(":
            stack.append(i)
        elif sym == ")":
            pairs[i] = stack.pop()
            pairs[pairs[i]] = i

    domains = []
    for i, sym in enumerate(ss):
        if sym == "(":
            if pairs.get(i - 1) == None:
                domains.append([sym])
            elif pairs[i] == pairs[i - 1] - 1:
                domains[-1].append(sym)
        elif sym == ")":
            if pairs.get(i - 1) == None or pairs[i] != pairs[i - 1] - 1:
                domains.append([sym])
            else:
                domains[-1].append(sym)
        else:
            if len(domains) < 1 or domains[-1][0] in "()":
                domains.append([sym])
            else:
                domains[-1].append(sym)
    for i, d in enumerate(domains):
        if "".join(d) == "P1":
            domains[i] = p1
        elif "".join(d) == "P2":
            domains[i] = p2
    #print(domains)
    return domains



if __name__ == "__main__":
    register()

    bpy.ops.sterna.export('INVOKE_DEFAULT')
