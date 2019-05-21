import bpy


class CleanoutDecalTextureDuplicates(bpy.types.Operator):
    bl_idname = "machin3.cleanout_decal_texture_duplicates"
    bl_label = "MACHIN3: Cleanout Decal Texture Difuplicates"

    def execute(self, context):
        print()

        # just running remove_images() doesn't work for height images coming in from
        # paralax decals, as the height images are deep in instanced node groups
        # we have to remove those 0 user duplicate node groups first before the
        # height textures in them have 0 users as well and can be removed properly

        self.remove_nodegroups("parallax.decal")
        self.remove_nodegroups("NodeGroup.decal")

        self.remove_images()

        print()

        return {'FINISHED'}

    def remove_nodegroups(self, groupstring):
        for group in bpy.data.node_groups:
            if groupstring in group.name:
                for dup in bpy.data.node_groups:
                    if group.name in dup.name and len(dup.name) > len(group.name):
                        if dup.users == 0:
                            print("Removing node group '%s',a likely duplicate of '%s'." % (dup.name, group.name))
                            bpy.data.node_groups.remove(dup)

    def remove_images(self):
        # finding potential duplicates by filename
        texturedups = []
        for img in bpy.data.images:
            for dup in bpy.data.images:
                if img.name.startswith(dup.name) and len(dup.name) > len(img.name):
                    print("Preparing to remove '%s', a likely duplicate of '%s'." % (dup.name, img.name))
                    texturedups.append((dup, img))

        # re-assigning textures in image texture nodes
        for dup, img in texturedups:
            for mat in bpy.data.materials:
                for node in mat.node_tree.nodes:
                    if "Image Texture" in node.name:
                        if node.image == dup:
                            node.image = img
                            print(" > Replaced '%s' in node '%s' of material '%s' with '%s'." % (dup.name, node.name, mat.name, img.name))

        # removing 0 user images
        for img in bpy.data.images:
            if img.users == 0:
                print("Removing '%s', which has 0 users." % (img.name))
                bpy.data.images.remove(img)
