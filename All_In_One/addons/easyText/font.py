import bpy


def search(font):
    print("Searching for " + font)  # search for text
    z = 0  # zaehlvariable
    ft = 0  # textoutput
    for a in bpy.data.fonts:
        z = z + 1
        print("Searching: " + a.name)  # Output all safed Fonts
        if a.name == font:
            ft = z - 1
            print(font + " found as number in text-array:")  # if found output
            print(ft)
    return (ft)
