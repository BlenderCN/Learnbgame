import bpy


#context = bpy.context, items = object from where the collection must be found
def find_collection(context, item): 
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collection



#context must be bpy.context
#Collection_Name = Name for Collection
#List_ob = object list for in new collection
#active_ob = one object that stays in previous collection
def new_collection(context, Collection_Name, List_ob, active_ob, skip_act):   
    new_collect = bpy.data.collections.new(name= Collection_Name)
    bpy.context.scene.collection.children.link(new_collect)
    if List_ob != None:
        for ob in List_ob:
            if ob != active_ob and skip_act == False:
                old_collect = find_collection(bpy.context, ob)
                old_collect.objects.unlink(ob)
            new_collect.objects.link(ob)
    return new_collect

def parent(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()