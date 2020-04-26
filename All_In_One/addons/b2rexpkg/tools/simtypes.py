
ZERO_UUID_STR = '00000000-0000-0000-0000-000000000000'

class LayerTypes:
    LayerLand = 0x4C
    LayerWater = 0x57
    LayerWind = 0x37
    LayerCloud = 0x38

# pyogp.lib.enums.PCodeEnum
class PCodeEnum(object):
    """ classifying the PCode of objects """
    Primitive = 9          # 0x09
    Avatar = 47            # 0x2F
    Grass = 95             # 0x5F
    NewTree = 111          # 0x6F
    ParticleSystem = 143   # 0x8F
    Tree = 255   

class RexDrawType:
    Prim = 0
    Mesh = 1

# pyogp.lib.client.enums.AssetType
class AssetType:
    OgreMesh = 43
    OgreSkeleton = 44
    OgreMaterial = 45
    OgreParticles = 47
    FlashAnimation = 49
    GAvatar = 46

# pyogp.lib.client.enums.InventoryType
class InventoryType:
    OgreParticles = 41
    FlashAnimation = 42
    OgreMaterial = 41

class RegionFlags:
    AllowDamage = 1 << 0
    AllowLandmak = 1 << 1
    AllowSetHome = 1 << 2
    ResetHomeOnTeleport = 1 << 3
    SunFixed = 1 << 4
    TaxFree = 1 << 5
    BlockTerraform = 1 << 6
    BlockLandResell = 1 << 7
    Sandbox = 1 << 8
    NullLayer = 1 << 9
    SkipAgentAction = 1 << 10
    SkipUpdateInterestList = 1 << 11
    SkipCollisions = 1 << 12
    SkipScripts = 1 << 13
    SkipPhysics = 1 << 14
    ExternallyVisible = 1 << 15
    MainlandVisible = 1 << 16
    PublicAllowed = 1 << 17
    BlockDwell = 1 << 18
    NoFly = 1 << 19
    AllowDirectTeleport = 1 << 20
    EstateSkipScripts = 1 << 21
    RestrictPushObject = 1 << 22
    DenyAnonymous = 1 << 23
    DenyIdentified = 1 << 24
    DenyTransacted = 1 << 25
    AllowParcelChanges = 1 << 26
    AbuseEmailToEstateOwner = 1 << 27
    AllowVoice = 1 << 28
    BlockParcelSearch = 1 << 29
    DenyAgeUnverified = 1 << 30

class SimAccess:
    Min = 0
    Trial = 7
    PG = 13
    Mature = 21
    Adult = 42
    Down = 254
    NonExistent = 255

