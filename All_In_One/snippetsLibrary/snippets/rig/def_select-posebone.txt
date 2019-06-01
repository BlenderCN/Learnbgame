def select_posebone(pb, select=1):
    '''Select / Deselect given poseBone'''
    pb.bone.select=select
    pb.bone.select_tail=select
    pb.bone.select_head=select