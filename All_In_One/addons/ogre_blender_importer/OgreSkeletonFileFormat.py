from enum import IntEnum

class OgreSkeletonChunkID(IntEnum):
    """
    Definition of the OGRE .skeleton file format

    .skeleton files are binary files (for read efficiency at runtime) and are arranged into chunks
    of data; very like 3D Studio's format.
    A chunk always consists of:
        unsigned short CHUNK_ID        : one of the following chunk ids identifying the chunk
        unsigned long  LENGTH          : length of the chunk in bytes; including this header
        void*          DATA            : the data; which may contain other sub-chunks (various data types)

    A .skeleton file contains both the definition of the Skeleton object and the animations it contains. It
    contains only a single skeleton but can contain multiple animations.
    """
    SKELETON_HEADER = 0x1000;
    #char* version           : Version number check
    SKELETON_BLENDMODE = 0x1010;
    #unsigned short blendmode     : SkeletonAnimationBlendMode
    SKELETON_BONE = 0x2000;
    # Repeating section defining each bone in the system.
    # Bones are assigned indexes automatically based on their order of declaration
    # starting with 0.
    # char* name                       : name of the bone
    # unsigned short handle            : handle of the bone; should be contiguous & start at 0
    # Vector3 position                 : position of this bone relative to parent
    # Quaternion orientation           : orientation of this bone relative to parent
    # Vector3 scale                    : scale of this bone relative to parent
    SKELETON_BONE_PARENT = 0x3000;
    #    // Record of the parent of a single bone; used to build the node tree
    #    // Repeating section; listed in Bone Index order; one per Bone
    #        // unsigned short handle             : child bone
    #        // unsigned short parentHandle   : parent bone
    SKELETON_ANIMATION = 0x4000;
    #    // A single animation for this skeleton
    #        // char* name                       : Name of the animation
    #        // float length                      : Length of the animation in seconds
    SKELETON_ANIMATION_BASEINFO = 0x4010;
    #        // [Optional] base keyframe information
    #        // char* baseAnimationName (blank for self)
    #        // float baseKeyFrameTime
    SKELETON_ANIMATION_TRACK = 0x4100;
    #        // A single animation track (relates to a single bone)
    #        // Repeating section (within SKELETON_ANIMATION)
    #            // unsigned short boneIndex     : Index of bone to apply to
    SKELETON_ANIMATION_TRACK_KEYFRAME = 0x4110;
    #            // A single keyframe within the track
    #            // Repeating section
    #                // float time                    : The time position (seconds)
    #                // Quaternion rotate            : Rotation to apply at this keyframe
    #                // Vector3 translate            : Translation to apply at this keyframe
    #                // Vector3 scale                : Scale to apply at this keyframe
    SKELETON_ANIMATION_LINK = 0x5000;
    #    // Link to another skeleton; to re-use its animations
    #        // char* skeletonName                   : name of skeleton to get animations from
    #        // float scale                          : scale to apply to trans/scale keysSKELETON_HEADER            = 0x1000;
    #        // char* version           : Version number check
    #        SKELETON_BLENDMODE         = 0x1010; // optional
    #            // unsigned short blendmode     : SkeletonAnimationBlendMode
