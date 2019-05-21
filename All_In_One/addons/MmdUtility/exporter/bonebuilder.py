# coding: utf-8
from .. import bl
from ..pymeshio import englishmap


class IKChain(object):
    __slots__=['index', 'limitAngle', 'limitMin', 'limitMax']
    def __init__(self, index, limitAngle, limitMin, limitMax):
        self.index=index
        self.limitAngle=limitAngle
        self.limitMin=limitMin
        self.limitMax=limitMax


class IKSolver(object):
    __slots__=['target_index', 'effector_index', 'iterations', 'weight', 'chain']
    def __init__(self, target_index, effector_index, iterations, weight):
        self.target_index=target_index
        self.effector_index=effector_index
        self.iterations=iterations
        self.weight=weight
        self.chain=[]

    def __str__(self):
        return "<IKSolver %d->%d, %d times(%f)>" % (
                self.target_index, self.effector_index,
                self.iterations, self.weight)


CONSTRAINT_NONE=0
CONSTRAINT_IK=1
CONSTRAINT_COPY_ROTATION=2
CONSTRAINT_LIMIT_ROTATION=3
CONSTRAINT_LIMIT_TRANSLATION=4
class Bone(object):
    __slots__=['index', 'name', 'english_name', 'ik_index',
            'ikSolver',
            'ikEffector',
            'pos', 'tail', 'parent_index', 'tail_index',
            'isVisible', 'hasTail', 
            'fixed_axis',
            'canTranslate',
            'connected',
            'constraint',
            'constraintTarget',
            'constraintInfluence',

            'children',
            ]
    def __init__(self, index, name, english_name, pos, isVisible):
        self.index=index
        self.name=name
        self.english_name=english_name
        self.pos=pos
        self.tail=None
        self.parent_index=None
        self.tail_index=None
        self.isVisible=isVisible
        self.hasTail=False
        self.canTranslate=False
        self.ikSolver=None
        self.ikEffector=None
        self.connected=None
        self.children=[]
        #
        self.constraint=CONSTRAINT_NONE
        self.constraintTarget=0
        self.constraintInfluence=0

    def __eq__(self, rhs):
        return self.index==rhs.index

    def __str__(self):
        return "<Bone %s>" % (self.name)

    def isFixedAxis(self):
        return self.constraint==CONSTRAINT_LIMIT_ROTATION

    def canManipulate(self):
        return True

    def hasValidTailIndex(self):
        return self.tail_index and self.tail_index!=-1 and self.tail_index!=0


class BoneBuilder(object):
    __slots__=['bones', 'boneMap', 'ik_list', 'bone_groups', 'no_parent_bones']
    def __init__(self):
        self.bones=[]
        self.boneMap={}
        self.ik_list=[]
        self.bone_groups=[]
        self.no_parent_bones=[]

    def getBoneGroup(self, bone):
        for i, g in enumerate(self.bone_groups):
            for b in g[1]:
                if b==bone.name:
                    return i+1

    def build(self, armatureObj):
        if not armatureObj:
            return

        #bl.message("build skeleton")
        armature=armatureObj.data

        ####################
        # bone group
        ####################
        for g in armatureObj.pose.bone_groups:
            self.bone_groups.append((g.name, []))

        ####################
        # create bones
        ####################
        def createBone(i, b):
            bone=Bone(i, 
                    b.name, b.get(bl.BONE_ENGLISH_NAME, 'bone%04d' % i),
                    b.head_local[0:3],
                    not b.hide
                    )
            if bl.BONE_CAN_TRANSLATE in b:
                pass
            else:
                bone.constraint=CONSTRAINT_LIMIT_TRANSLATION
            return bone
        self.bones=[createBone(i, b) for i, b in enumerate(armature.bones.values())]
        # name map
        for bone in self.bones:
            self.boneMap[bone.name]=bone

        # buid tree hierarchy
        def __getBone(bone, b):
            bone.hasTail=not (bl.BONE_USE_TAILOFFSET in b)

            if len(b.children)==0:
                return

            for i, c in enumerate(b.children):
                child=self.boneMap[c.name]
                if bone:
                    child.parent_index=bone.index
                if c.use_connect:
                    bone.connected=child
                __getBone(child, c)

        for bone, b in zip(self.bones, armature.bones.values()):
            if not b.parent:
                # root bone
                __getBone(bone, b)

        ####################
        # get pose bone info
        ####################
        pose = armatureObj.pose
        for b in pose.bones.values():
            bone=self.boneMap[b.name]
            ####################
            # assing bone group
            ####################
            self.__assignBoneGroup(b, b.bone_group)

            # translation lock
            if not b.lock_location[0]:
                bone.canTranslate=True

            for c in b.constraints:
                if c.type=='IK':
                    # IK effector
                    ####################
                    # IK 接続先
                    effector=self.boneByName(b.name)
                    effector.ikEffector=True

                    # IK solver
                    ####################
                    target=self.boneByName(c.subtarget)
                    target.ikSolver=IKSolver(target.index, effector.index, 
                                int(c.iterations * 0.1), 
                                armature.bones[target.name].get(bl.IK_UNITRADIAN, 1.0)
                                )
                    # ik chain
                    ####################
                    chain=b.parent
                    for i in range(c.chain_count):
                        limit_anlge=False
                        limit_min=[0, 0, 0]
                        limit_max=[0, 0, 0]
                        if chain.use_ik_limit_x:
                            limit_anlge=True
                            # right handed to left handed ?
                            limit_min[0]=-chain.ik_max_x
                            limit_max[0]=-chain.ik_min_x
                        if chain.use_ik_limit_y:
                            limit_anlge=True
                            limit_min[1]=chain.ik_min_y
                            limit_max[1]=chain.ik_max_y
                        if chain.use_ik_limit_z:
                            limit_anlge=True
                            limit_min[2]=chain.ik_min_z
                            limit_max[2]=chain.ik_max_z
                        # IK影響下
                        target.ikSolver.chain.append(IKChain(
                            self.boneByName(chain.name).index,
                            limit_anlge, limit_min, limit_max))
                        # next
                        chain=chain.parent

                if c.type=='COPY_ROTATION':
                    # copy rotation
                    bone.constraint=CONSTRAINT_COPY_ROTATION
                    bone.constraintTarget=c.subtarget
                    bone.constraintInfluence=c.influence

                if c.type=='LIMIT_ROTATION':
                    # fixed_axis
                    bone.constraint=CONSTRAINT_LIMIT_ROTATION

                if c.type=='LIMIT_LOCATION':
                    # rotation only
                    bone.constraint=CONSTRAINT_LIMIT_TRANSLATION

        ####################

        # boneのsort
        #self._sortBy()
        self._fix()
        self._build_hierarchy()
        # IKのsort
        for b in self.bones:
            if b.ikSolver:
                self.ik_list.append(b.ikSolver)
        def getIndex(ik):
            for i, v in enumerate(englishmap.boneMap):
                if v[0]==self.bones[ik.target_index].name:
                    return i
            return len(englishmap.boneMap)
        self.ik_list.sort(key=getIndex)

    def __assignBoneGroup(self, poseBone, boneGroup):
        if boneGroup:
            for g in self.bone_groups:
                if g[0]==boneGroup.name:
                    g[1].append(poseBone.name)

    def _sortBy(self):
        """
        boneMap順に並べ替える
        """
        boneMap=englishmap.boneMap
        original=self.bones[:]
        def getIndex(bone):
            for i, k_v in enumerate(boneMap):
                if (k_v[0]==bone.name or k_v[1]==bone.name):
                    return i
            return len(boneMap)

        self.bones.sort(key=getIndex)

        sortMap={}
        for i, b in enumerate(self.bones):
            src=original.index(b)
            sortMap[src]=i
        for b in self.bones:
            b.index=sortMap[b.index]
            if b.parent_index:
                b.parent_index=sortMap[b.parent_index]
            if b.tail_index:
                b.tail_index=sortMap[b.tail_index]
            if b.ikSolver:
                solver=b.ikSolver
                solver.target_index=sortMap[solver.target_index]
                solver.effector_index=sortMap[solver.effector_index]
                for c in solver.chain:
                    c.index=sortMap[c.index]

    def _fix(self):
        """
        調整
        """
        # set parent_index and tail_index
        for b in self.bones:
            if b.parent_index==None:
                b.parent_index=-1
            else:
                parent_b=self.bones[b.parent_index]
                if parent_b.connected:
                    parent_b.tail_index=parent_b.connected.index
                if b.constraint==CONSTRAINT_LIMIT_TRANSLATION:
                    # 移動不可ボーン
                    if b.isVisible and parent_b.isFixedAxis():
                        self.bones[parent_b.parent_index].tail_index=b.index
                        parent_b.tail=[l - r for l, r in zip(b.pos, parent_b.pos)]

        # set tail
        for b in self.bones:
            if not b.tail_index:
                b.tail_index=-1
                if not b.hasTail:
                    if not b.isFixedAxis():
                        b.tail=(0, 0, 0)
                    b.tail_index=-1

    def _build_hierarchy(self):
        """
        親子関係を再構築する
        """
        for b in self.bones:
            if b.parent_index==-1:
                self.no_parent_bones.append(b)
            else:
                self.bones[b.parent_index].children.append(b)

    def getIndex(self, bone):
        for i, b in enumerate(self.bones):
            if b==bone:
                return i
        assert(false)

    def indexByName(self, name):
        if name=='':
            return 0
        else:
            try:
                return self.getIndex(self.boneByName(name))
            except:
                return 0

    def boneByName(self, name):
        return self.boneMap[name]


