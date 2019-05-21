from enum import Enum
from io import open
import os
import sys


def printSkeletonSerializerUsage():
    print("usage: blender --python OgreSkeletonSerializer.py -- file.skeleton");

try:
    import bpy;
    import mathutils;
except ImportError:
    print("You need to execute this script using blender");
    printSkeletonSerializerUsage();
    sys.exit();

try:
    from OgreSkeletonFileFormat import OgreSkeletonChunkID
    from OgreSerializer import OgreSerializer
    from OgreBone import OgreBone

except ImportError as e:
    directory = os.path.dirname(os.path.realpath(__file__));    
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreSkeletonFileFormat.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))
    srcfile="OgreSerializer.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))
    srcfile="OgreBone.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))

class OgreSkeletonVersion(IntEnum):
    #/// OGRE version v1.0+
    SKELETON_VERSION_1_0 = 100;
    #/// OGRE version v1.8+
    SKELETON_VERSION_1_8 = 180;
    #Latest version available
    SKELETON_VERSION_LATEST = 180;

class OgreSkeletonSerializer(OgreSerializer):
    """
    Class for serialising skeleton data to/from an OGRE .skeleton file.
    @remarks
        This class allows exporters to write OGRE .skeleton files easily, and allows the
        OGRE engine to import .skeleton files into instantiated OGRE Skeleton objects.
        Note that a .skeleton file includes not only the Skeleton, but also definitions of
        any Animations it uses.
    @par
        To export a Skeleton:<OL>
        <LI>Create a Skeleton object and populate it using it's methods.</LI>
        <LI>Call the exportSkeleton method</LI>
        </OL>
    """

    SSTREAM_OVERHEAD_SIZE = 2 + 4;
    HEADER_STREAM_ID_EXT = 0x1000;

    def __init__(self):
        OgreSerializer.__init__(self);
        self._version = "[Unknown]";
        self.invertYZ = True;
        self.scale_fail_import = 0;

    def _calcBoneSizeWithoutScale(self, skeleton, bone):
        size = OgreSkeletonSerializer.SSTREAM_OVERHEAD_SIZE;
        size += 2; #handle
        size += 4*3; #position
        size += 4*4; #orientation
        return size;

    def _calcBoneSize(self, skeleton, bone):
        size = self._calcBoneSizeWithoutScale(skeleton,bone);
        #TODO Don't assume the scale it's never unit scale
        size += 3*3; #scale
        return size;

    def _calcKeyFrameSizeWithoutScale(self, skeleton, keyframe):
        size = OgreSkeletonSerializer.SSTREAM_OVERHEAD_SIZE;
        size += 4; #time
        size += 4*4; #quaternion rotate
        size += 4*3; #translation
        return size;

    def _readBone(self,stream, skeleton, bone_map):
        name = OgreSerializer.readString(stream);
        handle = self._readUShorts(stream,1)[0];

        bpy_bone = skeleton.edit_bones.new(name);

        bone = OgreBone(name, handle, skeleton, bpy_bone, bone_map);
        bone_map[handle] = bone;

        bone.local_position = mathutils.Vector(self._readVector3(stream));
        bone.local_rotation = mathutils.Quaternion(self._readBlenderQuaternion(stream));

        self._chunkSizeStack[-1] += OgreSerializer.calcStringSize(name);

        #hum some ugly code <3
        if (self._currentstreamLen > self._calcBoneSizeWithoutScale(skeleton,bone)):
            bone.local_scale = mathutils.Vector(self._readVector3(stream));
            self.scale_fail_import += 1;
            print("Warning scale " + str(bone.local_scale) + " will not be used");

        bone.computeBlenderBone();

        print("Add Bone (handle: " + str(handle) + "): " + str(name));
        #print("pos: "+str(bone.position)+" rot: "+str(bone.rotation)+" scale:"+str(bone.scale));


    def _readBoneParent(self, stream, skeleton, bone_map):
        childHandle = self._readUShorts(stream,1)[0];
        parentHandle = self._readUShorts(stream,1)[0];

        try:
            parent = bone_map[parentHandle];
            child = bone_map[childHandle];
            parent.addChild(child);
            #print("Create bone link [parent: " + parent.name + " (handle: "+str(parentHandle)+ "), child: " + child.name +" (handle:"+str(childHandle)+")]" );
        except IndexError as e:
            print(str(e) + " Attempt to create link for bone that doesn't exists");


    def _readKeyFrame(self, stream, tracks,skeleton, keyframe_index):
        time = self._readFloats(stream, 1)[0];
        for i in range(7):
            tracks[i].keyframe_points.add(1);
            tracks[i].keyframe_points[keyframe_index].interpolation = 'LINEAR';


        rot = self._readBlenderQuaternion(stream);
        trans = self._readVector3(stream);

        time *= 60.0; #sec to frame at 60 fps

        #position
        tracks[0].keyframe_points[keyframe_index].co = (time, trans[0]);
        tracks[1].keyframe_points[keyframe_index].co = (time, trans[1]);
        tracks[2].keyframe_points[keyframe_index].co = (time, trans[2]);

        #rotation
        tracks[3].keyframe_points[keyframe_index].co = (time , rot[0]);
        tracks[4].keyframe_points[keyframe_index].co = (time , rot[1]);
        tracks[5].keyframe_points[keyframe_index].co = (time , rot[2]);
        tracks[6].keyframe_points[keyframe_index].co = (time , rot[3]);


        #hum ugly again <3
        if (self._currentstreamLen > self._calcKeyFrameSizeWithoutScale(skeleton,tracks)):
            scale = self._readVector3(stream);
            #scale
        #    trans[7].keyframe_points[keyframe_index].co = (time, scale[0]);
        #    trans[8].keyframe_points[keyframe_index].co = (time, scale[1]);
        #    trans[9].keyframe_points[keyframe_index].co = (time, scale[2]);
        #else:
    #        trans[7].keyframe_points[keyframe_index].co = (time, 1.0);
#            trans[8].keyframe_points[keyframe_index].co = (time, 1.0);
#            trans[9].keyframe_points[keyframe_index].co = (time, 1.0);

    def _readAnimationTrack(self,stream,skeleton,bone_map,anim):
        boneHandle = self._readShorts(stream,1)[0];
        targetBone = bone_map[boneHandle];
        tracks = []
        #Creates curves for the animations of a boneHandle
        # 0: position.x
        # 1: position.y
        # 2: position.z
        # 3: rotation.w
        # 4: rotation.x
        # 5: rotation.y
        # 6: rotation.z
        # 7: scale.x
        # 8: scale.y
        # 9: scale.z

        basename = 'pose.bones["' + targetBone.name + '"]';
        tracks.append(anim.fcurves.new(data_path=basename+".location",index=0,action_group=targetBone.name));
        tracks.append(anim.fcurves.new(data_path=basename+".location",index=1,action_group=targetBone.name));
        tracks.append(anim.fcurves.new(data_path=basename+".location",index=2,action_group=targetBone.name));
        tracks.append(anim.fcurves.new(data_path=basename+".rotation_quaternion",index=0,action_group=targetBone.name));
        tracks.append(anim.fcurves.new(data_path=basename+".rotation_quaternion",index=1,action_group=targetBone.name));
        tracks.append(anim.fcurves.new(data_path=basename+".rotation_quaternion",index=2,action_group=targetBone.name));
        tracks.append(anim.fcurves.new(data_path=basename+".rotation_quaternion",index=3,action_group=targetBone.name));
        #tracks.append(anim.fcurves.new(data_path=basename+".scale",index=0,action_group=targetBone.name));
        #tracks.append(anim.fcurves.new(data_path=basename+".scale",index=1,action_group=targetBone.name));
        #tracks.append(anim.fcurves.new(data_path=basename+".scale",index=2,action_group=targetBone.name));

        self._pushInnerChunk(stream);
        streamID = self._readChunk(stream);
        keyframe_index = 0;
        while (streamID == OgreSkeletonChunkID.SKELETON_ANIMATION_TRACK_KEYFRAME):
            self._readKeyFrame(stream, tracks, skeleton,keyframe_index);
            keyframe_index += 1;
            streamID = self._readChunk(stream);
        if (streamID is not None):
            self._backpedalChunkHeader(stream);
        self._popInnerChunk(stream);




    def _readAnimation(self, stream, skeleton, bone_map, skeleton_object):
        #name of the animation
        name = OgreSerializer.readString(stream);
        #length of the animation in seconds
        length = self._readFloats(stream, 1)[0];

        print("Creating action: " + name + " (length: " + str(length) + "s)");

        pAnim = bpy.data.actions.new(name);
        skeleton_object.animation_data.action = pAnim;
        eof = False;

        self._pushInnerChunk(stream);
        streamID = self._readChunk(stream);

        if (streamID == OgreSkeletonChunkID.SKELETON_ANIMATION_BASEINFO):
            baseAnimName = OgreSkeletonSerializer.readString(stream);
            baseKeyTime = self._readFloats(stream,1)[0];
            print("This animation is based on: "+baseAnimName+" (with the key time: +"+str(baseKeyTime)+")");
            print("Warning this is not implemented");
            #TODO code the base key frame implementation
            streamID = self._readChunk(stream);

        while (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION_TRACK):
            self._readAnimationTrack(stream, skeleton, bone_map, pAnim);
            streamID = self._readChunk(stream);

        if (stream is not None):
            self._backpedalChunkHeader(stream);
        self._popInnerChunk(stream);






    def setWorkingVersion(self, ver):
        if (ver == OgreSkeletonVersion.SKELETON_VERSION_1_0):
            self._version = "[Serializer_v1.10]";
        elif (ver == OgreSkeletonVersion.SKELETON_VERSION_1_8):
            self._version = "[Serializer_v1.80]";
        else:
            raise ValueError("Invalid Skeleton serializer version " + str(ver));

    def importSkeleton(self, stream, filename=None):
        if (filename is None):
            if (hasattr(stream,'name')):
                filename = stream.name;
            elif (hasattr(stream, 'filename')):
                filename = stream.filename;
            else:
                raise ValueError("Cannot determine the filename of the stream please add filename parameter")

        self.scale_fail_import = 0;
        self._determineEndianness(stream);
        self._readFileHeader(stream);
        self._pushInnerChunk(stream);

        filename = os.path.basename(filename);
        skeleton_name = os.path.splitext(filename)[0];

        skeleton = None;
        skeleton_object = None;


        if skeleton_name in bpy.data.armatures.keys():
            raise ValueError("Armature with name " + skeleton_name + " already exists in blender");

        print("Create armature from skeleton: " + skeleton_name);
        skeleton = bpy.data.armatures.new(skeleton_name);
        #to be able to edit the armature we need to got in edit mode.
        skeleton_object = bpy.data.objects.new(skeleton_name, skeleton);
        #skeleton_object.show_x_ray = True;
        skeleton_object.animation_data_create();
        scene = bpy.context.scene;
        scene.objects.link(skeleton_object);
        scene.objects.active=skeleton_object;
        scene.update();
        #bugged ? bpy.ops.object.object.mode_set(mode='EDIT');
        bpy.ops.object.editmode_toggle();

        skeleton.show_names = True;
        bone_map = {};

        streamID = self._readChunk(stream);
        while (streamID is not None):
            if (streamID==OgreSkeletonChunkID.SKELETON_BLENDMODE):
                blendMode = self._readUShorts(stream,1)[0];
                print("Find blendMode: " + str(blendMode) + " (not used)");
            elif (streamID==OgreSkeletonChunkID.SKELETON_BONE):
                self._readBone(stream, skeleton, bone_map);
            elif (streamID==OgreSkeletonChunkID.SKELETON_BONE_PARENT):
                self._readBoneParent(stream, skeleton, bone_map);
            elif (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION):
                if (self.scale_fail_import>0):
                    print("Warning: scale import is not supported yet " + str(self.scale_fail_import) + " bones may have incorrectly loaded");
                print("Warning: animations are not supported at the moment see the head_tail_experiment branch for partial support (https://github.com/lamogui/ogre_blender_importer/tree/head_tail_experiment)");
                return;
                self._readAnimation(stream,skeleton, bone_map, skeleton_object);
            elif (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION_LINK):
                self._readSkeletonAnimationLink(stream,skeleton);

            streamID=self._readChunk(stream);
        #TODO skeleton set binding possible
        self._popInnerChunk(stream);
        if (self.scale_fail_import>0):
            print("Warning: scale import is not supported yet " + str(self.scale_fail_import) + " bones may have incorrectly loaded");



if __name__ == "__main__":
    argv = sys.argv;
    try:
        argv = argv[argv.index("--")+1:];  # get all args after "--"
    except:
        printSkeletonSerializerUsage();
        sys.exit();

    if (len(argv) > 0):
        filename = argv[0];
        skeletonfile = open(filename,mode='rb');
        skeletonserializer = OgreSkeletonSerializer();
        skeletonserializer.disableValidation();
        skeletonserializer.setWorkingVersion(OgreSkeletonVersion.SKELETON_VERSION_LATEST);
        skeletonserializer.importSkeleton(skeletonfile);
    else:
        printSkeletonSerializerUsage();
