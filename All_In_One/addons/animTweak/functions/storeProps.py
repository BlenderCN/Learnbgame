import bpy

def store_props(ob):
    for bone in ob.pose.bones :
        BoneCustomProp={}
        for key,value in bone.items() :
            if key!= '_RNA_UI' and value != 0 and type(value) in (int,float):
                BoneCustomProp[key]=round(value,3)
        if len(BoneCustomProp) !=0 :
            ob.data.DefaultValues[bone.name]=BoneCustomProp
