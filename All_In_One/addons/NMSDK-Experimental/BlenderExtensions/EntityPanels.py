# All the custom panels and properties for all the different object types

import bpy
from bpy.props import (StringProperty, BoolProperty, EnumProperty, IntProperty,
                       FloatProperty, PointerProperty, CollectionProperty)
from functools import reduce


""" Various properties for each of the different panel types """


class NMSEntityProperties(bpy.types.PropertyGroup):
    name_or_path = StringProperty(
        name="Name or path",
        description=("Name or path of the entity file to be produced.\n"
                     "This name can be shared by other objects in the scene\n"
                     "Any name here with forward or backslashes will be assume"
                     " to be a path"))
    is_anim_controller = BoolProperty(
        name="Is animation controller?",
        description=("When ticked, this entity contains all the required "
                     "animation information. Only tick this for one entity "
                     "per scene."),
        default=False)
    has_action_triggers = BoolProperty(
        name="Has ActionTriggers?",
        description=("Whether or not this entity file will be give the data "
                     "for the action triggers."),
        default=False)
    custom_physics = BoolProperty(
        name="Has custom physics?",
        description=("If true an extra panel is added to specify some specific"
                     " custom physics properties"),
        default=True)


class EntityItem(bpy.types.PropertyGroup):
    # very simple property group to contain the names
    name = bpy.props.StringProperty(name="Struct Name")


def ListProperty(type_):
    # this will return a CollectionProperty with type type_
    return bpy.props.CollectionProperty(type=type_)


""" Custom physics panel properties """


class NMSPhysicsProperties(bpy.types.PropertyGroup):
    VolumeTriggerType = EnumProperty(
        name="Volume trigger type",
        description="What type of cover the volume warrants",
        items=[('Open', 'Open', 'Open'),
               ('GenericInterior', 'GenericInterior', 'GenericInterior'),
               ('GenericGlassInterior', 'GenericGlassInterior',
                'GenericGlassInterior'),
               ('Corridor', 'Corridor', 'Corridor'),
               ('SmallRoom', 'SmallRoom', 'SmallRoom'),
               ('LargeRoom', 'LargeRoom', 'LargeRoom'),
               ('OpenCovered', 'OpenCovered', 'OpenCovered'),
               ('HazardProtection', 'HazardProtection', 'HazardProtection'),
               ('FieldBoundary', 'FieldBoundary', 'FieldBoundary'),
               ('Custom_Biodome', 'Custom_Biodome', 'Custom_Biodome'),
               ('Portal', 'Portal', 'Portal'),
               ('VehicleBoost', 'VehicleBoost', 'VehicleBoost')])


""" Struct specific properties """


# GcObjectPlacementComponentData related properties
class NMS_GcObjectPlacementComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcObjectPlacementComponentData """
    GroupNodeName = StringProperty(name="Group Node Name",
                                   default="_Clump")
    ActivationType = EnumProperty(
        name="Activation Type",
        items=[("Locator", "Locator", "Objects are placed at the locators"),
               ("GroupNode", "GroupNode", "I don't know...")])
    FractionOfNodesActive = FloatProperty(
        name="Fraction Of Nodes Active",
        description="Percentage of nodes that should be active",
        min=0,
        max=1)
    MaxNodesActivated = IntProperty(name="Max Nodes Activated",
                                    default=0)
    MaxGroupsActivated = IntProperty(name="Max Groups Activated",
                                     default=0)
    UseRaycast = BoolProperty(name="Use Raycast",
                              default=False)


# GcScannableComponentData related properties
class NMS_GcScannerIconTypes_Properties(bpy.types.PropertyGroup):
    """ Properties for GcScannerIconTypes """
    ScanIconType = EnumProperty(name="Scan Icon Type",
                                items=[('None', 'None', 'None'),
                                       ('Health', 'Health', 'Health'),
                                       ('Shield', 'Shield', 'Shield'),
                                       ('Hazard', 'Hazard', 'Hazard'),
                                       ('Tech', 'Tech', 'Tech'),
                                       ('Heridium', 'Heridium', 'Heridium'),
                                       ('Platinum', 'Platinum', 'Platinum'),
                                       ('Chrysonite', 'Chrysonite',
                                        'Chrysonite'),
                                       ('Signal', 'Signal', 'Signal'),
                                       ('Fuel', 'Fuel', 'Fuel'),
                                       ('Carbon', 'Carbon', 'Carbon'),
                                       ('Plutonium', 'Plutonium', 'Plutonium'),
                                       ('Thamium', 'Thamium', 'Thamium'),
                                       ('Mineral', 'Mineral', 'Mineral'),
                                       ('Iron', 'Iron', 'Iron'),
                                       ('Zinc', 'Zinc', 'Zinc'),
                                       ('Titanium', 'Titanium', 'Titanium'),
                                       ('Multi', 'Multi', 'Multi'),
                                       ('Artifact', 'Artifact', 'Artifact'),
                                       ('TechRecipe', 'TechRecipe',
                                        'TechRecipe'),
                                       ('RareProp', 'RareProp', 'RareProp'),
                                       ('Trade', 'Trade', 'Trade'),
                                       ('Exotic', 'Exotic', 'Exotic')])


class NMS_GcScannableComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcScannableComponentData """
    ScanRange = FloatProperty(
        name="Scan Range",
        description="Distance away the object can be picked up by a scanner")
    ScanName = StringProperty(name="Scan Name")
    ScanTime = FloatProperty(name="Scan Time")
    IconType = PointerProperty(type=NMS_GcScannerIconTypes_Properties)
    PermanentIcon = BoolProperty(name="Permanent Icon")
    PermanentIconRadius = FloatProperty(name="Permanent Icon Radius")


# GcShootableComponentData related properties
class NMS_GcProjectileImpactType_Properties(bpy.types.PropertyGroup):
    """ Properties for GcProjectileImpactType """
    Impact = EnumProperty(name="Impact",
                          items=[("Default", "Default", "Default"),
                                 ("Terrain", "Terrain", "Terrain"),
                                 ("Substance", "Substance", "Substance"),
                                 ("Rock", "Rock", "Rock"),
                                 ("Asteroid", "Asteroid", "Asteroid"),
                                 ("Shield", "Shield", "Shield"),
                                 ("Creature", "Creature", "Creature"),
                                 ("Robot", "Robot", "Robot"),
                                 ("Freighter", "Freighter", "Freighter"),
                                 ("Cargo", "Cargo", "Cargo"),
                                 ("Ship", "Ship", "Ship"),
                                 ("Plant", "Plant", "Plant")])


class NMS_GcShootableComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcShootableComponentData """
    Health = IntProperty(name="Health", default=200, min=0)
    AutoAimTarget = BoolProperty(name="Auto Aim Target", default=False)
    PlayerOnly = BoolProperty(name="Player Only", default=False)
    ImpactShake = BoolProperty(name="Impact Shake", default=True)
    ImpactShakeEffect = StringProperty(name="Impact Shake Effect", maxlen=0x10)
    ForceImpactType = PointerProperty(
        type=NMS_GcProjectileImpactType_Properties)
    IncreaseWanted = IntProperty(name="Increase Wanted", default=0, min=0,
                                 max=5)
    IncreaseWantedThresholdTime = FloatProperty(
        name="Increase Wanted Threshold Time", default=0.5)
    IncreaseFiendWanted = BoolProperty(name="Increase Fiend Wanted",
                                       default=False)
    RepairTime = FloatProperty(name="Repair Time", default=0.5)
    MinDamage = IntProperty(name="Min Damage", default=0)
    StaticUntilShot = BoolProperty(name="Static Until Shot", default=False)
    HitEffectEnabled = BoolProperty(name="Hit Effect Enabled", default=False)
    HitEffectEntireModel = BoolProperty(name="Hit Effect Entire Model",
                                        default=False)
    NameOverride = StringProperty(name="Name Override", maxlen=0x20)
    RequiredTech = StringProperty(name="Required Tech", maxlen=0x10)
    DamageMultiplier = StringProperty(name="Damage Multiplier", maxlen=0x10)


# GcDestructableComponentData related properties
class NMS_TkTextureResource_Properties(bpy.types.PropertyGroup):
    """ Properties for TkTextureResource """
    Filename = StringProperty(name="Filename", maxlen=0x80)


class NMS_GcStatTrackType_Properties(bpy.types.PropertyGroup):
    """ Properties for GcStatTrackType """
    StatTrackType = EnumProperty(name="StatTrackType",
                                 items=[("Set", "Set", "Set"),
                                        ("Add", "Add", "Add"),
                                        ("Max", "Max", "Max"),
                                        ("Min", "Min", "Min")])


class NMS_GcRarity_Properties(bpy.types.PropertyGroup):
    """ Properties for GcRarity """
    Rarity = EnumProperty(name="Rarity",
                          items=[("Common", "Common", "Common"),
                                 ("Uncommon", "Uncommon", "Uncommon"),
                                 ("Rare", "Rare", "Rare"),
                                 ("Extraordinary", "Extraordinary",
                                  "Extraordinary"),
                                 ("None", "None", "None")])


class NMS_GcRealitySubstanceCategory_Properties(bpy.types.PropertyGroup):
    """ Properties for GcRealitySubstanceCategory """
    SubstanceCategory = EnumProperty(
        name="SubstanceCategory",
        items=[("Commodity", "Commodity", "Commodity"),
               ("Technology", "Technology", "Technology"),
               ("Fuel", "Fuel", "Fuel"),
               ("Tradeable", "Tradeable", "Tradeable"),
               ("Special", "Special", "Special"),
               ("BuildingPart", "BuildingPart", "BuildingPart")])


class NMS_GcSubstanceAmount_Properties(bpy.types.PropertyGroup):
    """ Properties for GcSubstanceAmount """
    AmountMin = IntProperty(name="AmountMin", default=0)
    AmountMax = IntProperty(name="AmountMax", default=0)
    Specific = StringProperty(name="Specific", maxlen=0x10)
    SpecificSecondary = StringProperty(name="SpecificSecondary", maxlen=0x10)
    SubstanceCategory = PointerProperty(
        type=NMS_GcRealitySubstanceCategory_Properties)
    Rarity = PointerProperty(type=NMS_GcRarity_Properties)


class NMS_GcStatsEnum_Properties(bpy.types.PropertyGroup):
    """ Properties for GcStatsEnum """
    Stat = EnumProperty(name="Stat",
                        items=[("None", "None", "None"),
                               ("DEPOTS_BROKEN", "DEPOTS_BROKEN",
                                "DEPOTS_BROKEN"),
                               ("FPODS_BROKEN", "FPODS_BROKEN",
                                "FPODS_BROKEN"),
                               ("PLANTS_PLANTED", "PLANTS_PLANTED",
                                "PLANTS_PLANTED"),
                               ("SALVAGE_LOOTED", "SALVAGE_LOOTED",
                                "SALVAGE_LOOTED"),
                               ("TREASURE_FOUND", "TREASURE_FOUND",
                                "TREASURE_FOUND"),
                               ("QUADS_KILLED", "QUADS_KILLED",
                                "QUADS_KILLED"),
                               ("WALKERS_KILLED", "WALKERS_KILLED",
                                "WALKERS_KILLED")])


class NMS_GcDestructableComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcDestructableComponentData """
    Explosion = StringProperty(name="Explosion", maxlen=0x10)
    ExplosionScale = FloatProperty(name="ExplosionScale")
    ExplosionScaleToBounds = BoolProperty(name="ExplosionScaleToBounds",
                                          default=False)
    VehicleDestroyEffect = StringProperty(name="VehicleDestroyEffect",
                                          maxlen=0x10)
    TriggerAction = StringProperty(name="TriggerAction", maxlen=0x10)
    IncreaseWanted = IntProperty(name="IncreaseWanted", default=0, min=0,
                                 max=5)
    LootReward = StringProperty(name="LootReward", maxlen=0x10)
    LootRewardAmountMin = IntProperty(name="LootRewardAmountMin", default=0)
    LootRewardAmountMax = IntProperty(name="LootRewardAmountMax", default=0)
    GivesSubstances = CollectionProperty(type=NMS_GcSubstanceAmount_Properties)
    StatsToTrack = PointerProperty(type=NMS_GcStatsEnum_Properties)
    GivesReward = StringProperty(name="GivesReward", maxlen=0x10)
    HardModeSubstanceMultiplier = FloatProperty(
        name="HardModeSubstanceMultiplier")
    RemoveModel = BoolProperty(name="RemoveModel", default=True)
    DestroyedModel = PointerProperty(type=NMS_TkTextureResource_Properties)
    DestroyedModelUsesScale = BoolProperty(name="DestroyedModelUsesScale",
                                           default=False)
    DestroyForce = FloatProperty(name="DestroyForce")
    DestroyForceRadius = FloatProperty(name="DestroyForceRadius")
    DestroyEffect = StringProperty(name="DestroyEffect", maxlen=0x10)
    DestroyEffectPoint = StringProperty(name="DestroyEffectPoint", maxlen=0x10)
    DestroyEffectTime = FloatProperty(name="DestroyEffectTime")
    ShowInteract = BoolProperty(name="ShowInteract", default=False)
    ShowInteractRange = FloatProperty(name="ShowInteractRange")
    GrenadeSingleHit = BoolProperty(name="GrenadeSingleHit", default=True)


# GcSimpleInteractionComponentData related properties
class NMS_GcSizeIndicator_Properties(bpy.types.PropertyGroup):
    """ Properties for GcSizeIndicator """
    SizeIndicator = EnumProperty(name="SizeIndicator",
                                 items=[("Small", "Small", "Small"),
                                        ("Medium", "Medium", "Medium"),
                                        ("Large", "Large", "Large")])


class NMS_NMSString0x10_Properties(bpy.types.PropertyGroup):
    """ Properties for NMSString0x10 """
    Value = StringProperty(name="Value", maxlen=0x10)


class NMS_GcInteractionActivationCost_Properties(bpy.types.PropertyGroup):
    """ Properties for GcInteractionActivationCost """
    SubstanceId = StringProperty(name="SubstanceId")
    AltIds = CollectionProperty(type=NMS_NMSString0x10_Properties)
    Cost = IntProperty(name="Cost")
    Repeat = BoolProperty(name="Repeat")
    RequiredTech = StringProperty(name="RequiredTech")


class NMS_GcDiscoveryTypes_Properties(bpy.types.PropertyGroup):
    """ Properties for GcDiscoveryTypes """
    DiscoveryType = EnumProperty(name="DiscoveryType",
                                 items=[("Unknown", "Unknown", "Unknown"),
                                        ("SolarSystem", "SolarSystem",
                                         "SolarSystem"),
                                        ("Planet", "Planet", "Planet"),
                                        ("Animal", "Animal", "Animal"),
                                        ("Flora", "Flora", "Flora"),
                                        ("Mineral", "Mineral", "Mineral"),
                                        ("Sector", "Sector", "Sector"),
                                        ("Building", "Building", "Building"),
                                        ("Interactable", "Interactable",
                                         "Interactable"),
                                        ("Sentinel", "Sentinel", "Sentinel")])


class NMS_GcBaseBuildingTriggerAction_Properties(bpy.types.PropertyGroup):
    """ Properties for GcBaseBuildingTriggerAction """
    ID = StringProperty(name="ID")
    TimeDelay = IntProperty(name="TimeDelay")


class NMS_GcSimpleInteractionComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcSimpleInteractionComponentData """
    SimpleInteractionType = EnumProperty(
        name="SimpleInteractionType",
        items=[("Interact", "Interact", "Interact"),
               ("Treasure", "Treasure", "Treasure"),
               ("Beacon", "Beacon", "Beacon"),
               ("Scan", "Scan", "Scan"),
               ("Save", "Save", "Save"),
               ("CallShip", "CallShip", "CallShip"),
               ("CallVehicle", "CallVehicle", "CallVehicle"),
               ("Word", "Word", "Word"),
               ("Tech", "Tech", "Tech"),
               ("GenericReward", "GenericReward", "GenericReward"),
               ("Feed", "Feed", "Feed"),
               ("Teleport", "Teleport", "Teleport"),
               ("ClaimBase", "ClaimBase", "ClaimBase"),
               ("TeleportStartPoint", "TeleportStartPoint",
                "TeleportStartPoint"),
               ("TeleportEndPoint", "TeleportEndPoint", "TeleportEndPoint"),
               ("Portal", "Portal", "Portal"),
               ("Chest", "Chest", "Chest"),
               ("ResourceHarvester", "ResourceHarvester", "ResourceHarvester"),
               ("BaseCapsule", "BaseCapsule", "BaseCapsule"),
               ("Hologram", "Hologram", "Hologram"),
               ("NPCTerminalMessage", "NPCTerminalMessage",
                "NPCTerminalMessage"),
               ("VehicleBoot", "VehicleBoot", "VehicleBoot"),
               ("BiomeHarvester", "BiomeHarvester", "BiomeHarvester"),
               ("FreighterGalacticMap", "FreighterGalacticMap",
                "FreighterGalacticMap")])
    InteractDistance = FloatProperty(name="InteractDistance")
    Id = StringProperty(name="Id")
    Rarity = PointerProperty(type=NMS_GcRarity_Properties)
    SizeIndicator = PointerProperty(type=NMS_GcSizeIndicator_Properties)
    TriggerAction = StringProperty(name="TriggerAction")
    BroadcastTriggerAction = BoolProperty(name="BroadcastTriggerAction")
    Delay = FloatProperty(name="Delay")
    InteractIsCrime = BoolProperty(name="InteractIsCrime")
    InteractCrimeLevel = IntProperty(name="InteractCrimeLevel")
    ActivationCost = PointerProperty(
        type=NMS_GcInteractionActivationCost_Properties)
    StatToTrack = PointerProperty(type=NMS_GcStatsEnum_Properties)
    Name = StringProperty(name="Name")
    TerminalMessage = StringProperty(name="TerminalMessage")
    ScanType = StringProperty(name="ScanType")
    ScanData = StringProperty(name="ScanData")
    ScanIcon = PointerProperty(type=NMS_GcDiscoveryTypes_Properties)
    BaseBuildingTriggerActions = CollectionProperty(
        type=NMS_GcBaseBuildingTriggerAction_Properties)


# GcCustomInventoryComponentData related properties
class NMS_GcInventoryTechProbability_Properties(bpy.types.PropertyGroup):
    """ Properties for GcInventoryTechProbability """
    Tech = StringProperty(name="Tech")
    DesiredTechProbability = EnumProperty(
        name="DesiredTechProbability",
        items=[("Never", "Never", "Never"),
               ("Rare", "Rare", "Rare"),
               ("Common", "Common", "Common"),
               ("Always", "Always", "Always")])


class NMS_GcCustomInventoryComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcCustomInventoryComponentData """
    Size = StringProperty(name="Size")
    DesiredTechs = CollectionProperty(
        type=NMS_GcInventoryTechProbability_Properties)
    Cool = BoolProperty(name="Cool")


# GcAISpaceshipComponentData related properties
class NMS_GcAISpaceshipTypes_Properties(bpy.types.PropertyGroup):
    """ Properties for GcAISpaceshipTypes """
    ShipType = EnumProperty(name="ShipType",
                            items=[("None", "None", "None"),
                                   ("Pirate", "Pirate", "Pirate"),
                                   ("Police", "Police", "Police"),
                                   ("Trader", "Trader", "Trader"),
                                   ("Freighter", "Freighter", "Freighter")])


class NMS_GcSpaceshipClasses_Properties(bpy.types.PropertyGroup):
    """ Properties for GcSpaceshipClasses """
    ShipClass = EnumProperty(name="ShipClass",
                             items=[("Freighter", "Freighter", "Freighter"),
                                    ("Dropship", "Dropship", "Dropship"),
                                    ("Fighter", "Fighter", "Fighter"),
                                    ("Scientific", "Scientific", "Scientific"),
                                    ("Shuttle", "Shuttle", "Shuttle"),
                                    ("PlayerFreighter", "PlayerFreighter",
                                     "PlayerFreighter"),
                                    ("Royal", "Royal", "Royal")])


class NMS_GcPrimaryAxis_Properties(bpy.types.PropertyGroup):
    """ Properties for GcPrimaryAxis """
    PrimaryAxis = EnumProperty(name="PrimaryAxis",
                               items=[("Z", "Z", "Z"),
                                      ("ZNeg", "ZNeg", "ZNeg")])


class NMS_GcAISpaceshipComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcAISpaceshipComponentData """
    Type = PointerProperty(type=NMS_GcAISpaceshipTypes_Properties)
    Class = PointerProperty(type=NMS_GcSpaceshipClasses_Properties)
    Axis = PointerProperty(type=NMS_GcPrimaryAxis_Properties)
    Hangar = PointerProperty(type=NMS_TkTextureResource_Properties)
    IsSpaceAnomaly = BoolProperty(name="IsSpaceAnomaly")


# TkAudioComponentData related properties
class NMS_TkAudioAnimTrigger_Properties(bpy.types.PropertyGroup):
    """ Properties for TkAudioAnimTrigger """
    Sound = StringProperty(name="Sound")
    Anim = StringProperty(name="Anim")
    FrameStart = IntProperty(name="FrameStart")


class NMS_TkAudioComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for TkAudioComponentData """
    Ambient = StringProperty(name="Ambient")
    MaxDistance = IntProperty(name="MaxDistance")
    AnimTriggers = CollectionProperty(type=NMS_TkAudioAnimTrigger_Properties)


# GcEncyclopediaComponentData related properties
class NMS_GcEncyclopediaComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcEncyclopediaComponentData """
    Type = PointerProperty(type=NMS_GcDiscoveryTypes_Properties)


# GcEncounterComponentData related properties
class NMS_GcEncounterComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcEncounterComponentData """
    EncounterType = EnumProperty(name="EncounterType",
                                 items=[("FactoryGuards", "FactoryGuards",
                                         "FactoryGuards"),
                                        ("HarvesterGuards", "HarvesterGuards",
                                         "HarvesterGuards")])


# GcSpaceshipComponentData related properties
class NMS_GcSpaceshipComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcSpaceshipComponentData """
    ShipClass = PointerProperty(type=NMS_GcSpaceshipClasses_Properties)
    Cockpit = StringProperty(name="Cockpit")
    MaxHeadTurn = FloatProperty(name="MaxHeadTurn")
    MaxHeadPitchUp = FloatProperty(name="MaxHeadPitchUp")
    MaxHeadPitchDown = FloatProperty(name="MaxHeadPitchDown")
    BaseHealth = IntProperty(name="BaseHealth")
    FoVFixedDistance = FloatProperty(name="FoVFixedDistance")
    WheelModel = StringProperty(name="WheelModel")


# GcInteractionComponentData realted properties
class NMS_GcInteractionType_Properties(bpy.types.PropertyGroup):
    """ Properties for GcInteractionType """
    InteractionType = EnumProperty(
        name="InteractionType",
        items=[("None", "None", "None"),
               ("Shop", "Shop", "Shop"),
               ("NPC", "NPC", "NPC"),
               ("NPC_Secondary", "NPC_Secondary", "NPC_Secondary"),
               ("NPC_Anomaly", "NPC_Anomaly", "NPC_Anomaly"),
               ("NPC_Anomaly_Secondary", "NPC_Anomaly_Secondary",
                "NPC_Anomaly_Secondary"),
               ("Ship", "Ship", "Ship"),
               ("Outpost", "Outpost", "Outpost"),
               ("SpaceStation", "SpaceStation", "SpaceStation"),
               ("RadioTower", "RadioTower", "RadioTower"),
               ("Monolith", "Monolith", "Monolith"),
               ("Factory", "Factory", "Factory"),
               ("AbandonedShip", "AbandonedShip", "AbandonedShip"),
               ("Harvester", "Harvester", "Harvester"),
               ("Observatory", "Observatory", "Observatory"),
               ("TradingPost", "TradingPost", "TradingPost"),
               ("DistressBeacon", "DistressBeacon", "DistressBeacon"),
               ("Portal", "Portal", "Portal"),
               ("Plaque", "Plaque", "Plaque"),
               ("AtlasStation", "AtlasStation", "AtlasStation"),
               ("AbandonedBuildings", "AbandonedBuildings",
                "AbandonedBuildings"),
               ("WeaponTerminal", "WeaponTerminal", "WeaponTerminal"),
               ("SuitTerminal", "SuitTerminal", "SuitTerminal"),
               ("SignalScanner", "SignalScanner", "SignalScanner"),
               ("Teleporter_Base", "Teleporter_Base", "Teleporter_Base"),
               ("Teleporter_Station", "Teleporter_Station",
                "Teleporter_Station"),
               ("ClaimBase", "ClaimBase", "ClaimBase"),
               ("NPC_Freighter_Captain", "NPC_Freighter_Captain",
                "NPC_Freighter_Captain"),
               ("NPC_HIRE_Weapons", "NPC_HIRE_Weapons", "NPC_HIRE_Weapons"),
               ("NPC_HIRE_Weapons_Wait", "NPC_HIRE_Weapons_Wait",
                "NPC_HIRE_Weapons_Wait"),
               ("NPC_HIRE_Farmer", "NPC_HIRE_Farmer", "NPC_HIRE_Farmer"),
               ("NPC_HIRE_Farmer_Wait", "NPC_HIRE_Farmer_Wait",
                "NPC_HIRE_Farmer_Wait"),
               ("NPC_HIRE_Builder", "NPC_HIRE_Builder", "NPC_HIRE_Builder"),
               ("NPC_HIRE_Builder_Wait", "NPC_HIRE_Builder_Wait",
                "NPC_HIRE_Builder_Wait"),
               ("NPC_HIRE_Vehicles", "NPC_HIRE_Vehicles", "NPC_HIRE_Vehicles"),
               ("NPC_HIRE_Vehicles_Wait", "NPC_HIRE_Vehicles_Wait",
                "NPC_HIRE_Vehicles_Wait"),
               ("MessageBeacon", "MessageBeacon", "MessageBeacon"),
               ("NPC_HIRE_Scientist", "NPC_HIRE_Scientist",
                "NPC_HIRE_Scientist"),
               ("NPC_HIRE_Scientist_Wait", "NPC_HIRE_Scientist_Wait",
                "NPC_HIRE_Scientist_Wait"),
               ("NPC_Recruit", "NPC_Recruit", "NPC_Recruit"),
               ("NPC_Freighter_Captain_Secondary",
                "NPC_Freighter_Captain_Secondary",
                "NPC_Freighter_Captain_Secondary"),
               ("NPC_Recruit_Secondary", "NPC_Recruit_Secondary",
                "NPC_Recruit_Secondary"),
               ("Vehicle", "Vehicle", "Vehicle"),
               ("MessageModule", "MessageModule", "MessageModule"),
               ("TechShop", "TechShop", "TechShop"),
               ("VehicleRaseStart", "VehicleRaseStart", "VehicleRaseStart"),
               ("BuildingShop", "BuildingShop", "BuildingShop"),
               ("MissionGiver", "MissionGiver", "MissionGiver"),
               ("HoloHub", "HoloHub", "HoloHub"),
               ("HoloExplorer", "HoloExplorer", "HoloExplorer"),
               ("HoloSceptic", "HoloSceptic", "HoloSceptic"),
               ("HoloNoone", "HoloNoone", "HoloNoone"),
               ("PortalRunEntry", "PortalRunEntry", "PortalRunEntry"),
               ("PortalActivate", "PortalActivate", "PortalActivate"),
               ("CrashedFreighter", "CrashedFreighter", "CrashedFreighter"),
               ("GraveInCave", "GraveInCave", "GraveInCave"),
               ("GlitchyStroyBox", "GlitchyStroyBox", "GlitchyStroyBox"),
               ("NetworkPlayer", "NetworkPlayer", "NetworkPlayer"),
               ("NetworkMonument", "NetworkMonument", "NetworkMonument"),
               ("AnomalyComputer", "AnomalyComputer", "AnomalyComputer"),
               ("AtlasPlinth", "AtlasPlinth", "AtlasPlinth"),
               ("Epilogue", "Epilogue", "Epilogue")])


class NMS_Vector4f_Properties(bpy.types.PropertyGroup):
    """ Properties for Vector4f """
    x = FloatProperty(name="x")
    y = FloatProperty(name="y")
    z = FloatProperty(name="z")
    t = FloatProperty(name="t")


class NMS_TkCameraWanderData_Properties(bpy.types.PropertyGroup):
    """ Properties for TkCameraWanderData """
    CamWander = BoolProperty(name="CamWander")
    CamWanderPhase = FloatProperty(name="CamWanderPhase")
    CamWanderAmplitude = FloatProperty(name="CamWanderAmplitude")


class NMS_TkModelRendererCameraData_Properties(bpy.types.PropertyGroup):
    """ Properties for TkModelRendererCameraData """
    Distance = FloatProperty(name="Distance")
    Offset = PointerProperty(type=NMS_Vector4f_Properties)
    Pitch = FloatProperty(name="Pitch")
    Rotate = FloatProperty(name="Rotate")
    LightPitch = FloatProperty(name="LightPitch")
    LightRotate = FloatProperty(name="LightRotate")
    Wander = PointerProperty(type=NMS_TkCameraWanderData_Properties)


class NMS_TkModelRendererData_Properties(bpy.types.PropertyGroup):
    """ Properties for TkModelRendererData """
    Camera = PointerProperty(type=NMS_TkModelRendererCameraData_Properties)
    Fov = FloatProperty(name="Fov")
    AspectRatio = FloatProperty(name="AspectRatio")
    ThumbnailMode = EnumProperty(name="ThumbnailMode",
                                 items=[("None", "None", "None"),
                                        ("HUD", "HUD", "HUD"),
                                        ("GUI", "GUI", "GUI")])
    FocusType = EnumProperty(
        name="FocusType",
        items=[("ResourceBounds", "ResourceBounds", "ResourceBounds"),
               ("ResourceBoundingHeight", "ResourceBoundingHeight",
                "ResourceBoundingHeight"),
               ("NodeBoundingBox", "NodeBoundingBox", "NodeBoundingBox")])
    Anim = StringProperty(name="Anim", maxlen=0x10)
    HeightOffset = FloatProperty(name="HeightOffset")


class NMS_GcAlienRace_Properties(bpy.types.PropertyGroup):
    """ Properties for GcAlienRace """
    AlienRace = EnumProperty(name="AlienRace",
                             items=[("Traders", "Traders", "Traders"),
                                    ("Warriors", "Warriors", "Warriors"),
                                    ("Explorers", "Explorers", "Explorers"),
                                    ("Robots", "Robots", "Robots"),
                                    ("Atlas", "Atlas", "Atlas"),
                                    ("Diplomats", "Diplomats", "Diplomats"),
                                    ("None", "None", "None")])


class NMS_GcInteractionDof_Properties(bpy.types.PropertyGroup):
    """ Properties for GcInteractionDof """
    IsEnabled = BoolProperty(name="IsEnabled")
    UseGlobals = BoolProperty(name="UseGlobals")
    NearPlaneMin = FloatProperty(name="NearPlaneMin")
    NearPlaneAdjust = FloatProperty(name="NearPlaneAdjust")
    FarPlane = FloatProperty(name="FarPlane")
    FarFadeDistance = FloatProperty(name="FarFadeDistance")


class NMS_GcAlienPuzzleMissionOverride_Properties(bpy.types.PropertyGroup):
    """ Properties for GcAlienPuzzleMissionOverride """
    Mission = StringProperty(name="Mission")
    Puzzle = StringProperty(name="Puzzle")


class NMS_GcInteractionComponentData_Properties(bpy.types.PropertyGroup):
    """ Properties for GcInteractionComponentData """
    InteractionAction = EnumProperty(
        name="InteractionAction",
        items=[("PressButton", "PressButton", "PressButton"),
               ("HoldButton", "HoldButton", "HoldButton"),
               ("Shoot", "Shoot", "Shoot")])
    InteractionType = PointerProperty(type=NMS_GcInteractionType_Properties)
    Renderer = PointerProperty(type=NMS_TkModelRendererData_Properties)
    Race = PointerProperty(type=NMS_GcAlienRace_Properties)
    AttractDistanceSq = FloatProperty(name="AttractDistanceSq")
    RepeatInteraction = BoolProperty(name="RepeatInteraction")
    UseInteractCamera = BoolProperty(name="UseInteractCamera")
    BlendToCameraTime = FloatProperty(name="BlendToCameraTime")
    BlendFromCameraTime = FloatProperty(name="BlendFromCameraTime")
    ActivationCost = PointerProperty(
        type=NMS_GcInteractionActivationCost_Properties)
    TriggerAction = StringProperty(name="TriggerAction", maxlen=0x10)
    BroadcastTriggerAction = BoolProperty(name="BroadcastTriggerAction")
    InteractAngle = FloatProperty(name="InteractAngle")
    InteractDistance = FloatProperty(name="InteractDistance")
    InteractInvertFace = BoolProperty(name="InteractInvertFace")
    SecondaryInteractionType = PointerProperty(
        type=NMS_GcInteractionType_Properties)
    SecondaryActivationCost = PointerProperty(
        type=NMS_GcInteractionActivationCost_Properties)
    EventRenderers = CollectionProperty(
        type=NMS_TkModelRendererData_Properties)
    SecondaryCameraTransitionTime = FloatProperty(
        name="SecondaryCameraTransitionTime")
    DoInteractionsInOrder = BoolProperty(name="DoInteractionsInOrder")
    DepthOfField = PointerProperty(type=NMS_GcInteractionDof_Properties)
    PuzzleMissionOverrideTable = CollectionProperty(
        type=NMS_GcAlienPuzzleMissionOverride_Properties)


# miscellaneous functions


def rgetattr(obj, attr):
    def _getattr(obj, name):
        return getattr(obj, name)
    return reduce(_getattr, [obj]+attr.split('.'))

# Panel and box wrappers to give them extra functionality


# this function is essentially a wrapper for the boxes so they have a top
# section with name and a button to remove the box
# I wanted this to be able to be implemented as a decorator but I am bad at
# python :'(
def EntityPanelTop(layout, name):
    row = layout.row()
    row.label(text=name)
    s = row.split()
    s.alignment = 'RIGHT'
    s.operator('wm.move_entity_struct_up', text='', icon='TRIA_UP',
               emboss=False).struct_name = name
    s.operator('wm.move_entity_struct_down', text='', icon='TRIA_DOWN',
               emboss=False).struct_name = name
    s.operator('wm.remove_entity_struct', text='', icon='PANEL_CLOSE',
               emboss=False).remove_name = name
    newbox = layout.box()
    return newbox


def ListEntityTop(layout, list_struct, prop_name, name, index):
    box = layout.box()
    row = box.row()
    if '_' in name:
        name = name.split('_')[0]
    row.label(text=name)
    s = row.split()
    s.alignment = 'RIGHT'
    op = s.operator('wm.remove_list_struct', text='', icon='PANEL_CLOSE',
                    emboss=False)
    op.remove_index = index
    op.prop_name = prop_name
    op.list_struct = list_struct
    return box


# a function to return a ui box with the name and a plus button to add extra
# entries
def ListEntryAdder(box, list_struct, prop_name):
    row = box.row()
    row.label(text=prop_name)
    s = row.split()
    s.alignment = 'RIGHT'
    # create a new operator to add the sub structs
    op = s.operator('wm.add_list_struct', text='', icon='PLUS', emboss=False)
    op.prop_name = prop_name
    op.list_struct = list_struct
    return box


class RowGen():
    """ simple wrapper class to make the individual functions in
    DATA_PT_entities half the size... """
    def __init__(self, ctx, layout):
        """
        ctx is the object property that will be read from
        layout is the blender layout to write the rows to
        """
        self.ctx = ctx
        self.layout = layout

    def row(self, prop):
        """ Create a new row and add a new property with the specified name """
        r = self.layout.row()
        r.prop(self.ctx, prop)

    def mrow(self, props=[]):
        # not sure if I'll use this... but might be nice
        for prop in props:
            self.row(prop)

    def box(self, prop):
        new_ctx = getattr(self.ctx, prop)
        new_layout = self.layout.box()
        new_layout.label(text=prop)
        return RowGen(new_ctx, new_layout)

    def listbox(self, cls, obj, list_struct, prop_name, name):
        # a container function to be called to create a list box
        # class is required so that the panel layout can pass itself into this
        # so the correct attributes can be found
        listbox = ListEntryAdder(self.layout.box(), list_struct, prop_name)
        j = 0
        for _ in getattr(self.ctx, prop_name):
            box = ListEntityTop(listbox, list_struct, prop_name, name, j)
            # add the object and give it the appropriate index
            getattr(cls, name)(box, obj, index=j)
            j += 1


class NMSPhysicsPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Physics Properties"
    bl_idname = "OBJECT_PT_physics_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # this should only show for an object that is called NMS_SCENE
        if context.object.NMSEntity_props.custom_physics is True:
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSPhysics_props, "VolumeTriggerType")


# this is the main class that contains all the information... It's going to be
# BIG with all the structs in it...
class DATA_PT_entities(bpy.types.Panel):
    bl_idname = "OBJECT_MT_entity_menu"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "NMS Entity Constructor"

    @classmethod
    def poll(cls, context):
        if (context.object.NMSMesh_props.has_entity or
                context.object.NMSLocator_props.has_entity):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object

        row = layout.row()
        row.prop(obj.NMSEntity_props, "name_or_path")
        row = layout.row()
        row.prop(obj.NMSEntity_props, "is_anim_controller")
        row = layout.row()
        row.prop(obj.NMSEntity_props, "has_action_triggers")
        row = layout.row()
        row.prop(obj.NMSEntity_props, "custom_physics")

        layout.operator_menu_enum("wm.add_entity_struct", "structs",
                                  text="Select an entity struct to add")

        for struct in obj.EntityStructs:
            lb = layout.box()
            box = EntityPanelTop(lb, struct.name)
            # now call the actual layout on this modified box
            getattr(self, struct.name)(box, obj)

    def GcObjectPlacementComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcObjectPlacementComponentData_props, layout)
        r.row("GroupNodeName")
        r.row("ActivationType")
        r.row("FractionOfNodesActive")
        r.row("MaxNodesActivated")
        r.row("MaxGroupsActivated")
        r.row("UseRaycast")

    def GcScannableComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcScannableComponentData_props, layout)
        r.row("ScanRange")
        r.row("ScanName")
        r.row("ScanTime")
        b = r.box("IconType")
        b.row("ScanIconType")
        r.row("PermanentIcon")
        r.row("PermanentIconRadius")

    def GcShootableComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcShootableComponentData_props, layout)
        r.row("Health")
        r.row("AutoAimTarget")
        r.row("PlayerOnly")
        r.row("ImpactShake")
        r.row("ImpactShakeEffect")
        b = r.box("ForceImpactType")
        b.row("Impact")
        r.row("IncreaseWanted")
        r.row("IncreaseWantedThresholdTime")
        r.row("IncreaseFiendWanted")
        r.row("RepairTime")
        r.row("MinDamage")
        r.row("StaticUntilShot")
        r.row("HitEffectEnabled")
        r.row("HitEffectEntireModel")
        r.row("NameOverride")
        r.row("RequiredTech")
        r.row("DamageMultiplier")

    # GcDestructableComponentData related layouts
    def GcDestructableComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcDestructableComponentData_props, layout)
        r.row("Explosion")
        r.row("ExplosionScale")
        r.row("ExplosionScaleToBounds")
        r.row("VehicleDestroyEffect")
        r.row("TriggerAction")
        r.row("IncreaseWanted")
        r.row("LootReward")
        r.row("LootRewardAmountMin")
        r.row("LootRewardAmountMax")
        r.listbox(self, obj, "NMS_GcDestructableComponentData_props",
                  "GivesSubstances", "GcSubstanceAmount")
        b = r.box("StatsToTrack")
        b.row("Stat")
        r.row("GivesReward")
        r.row("HardModeSubstanceMultiplier")
        r.row("RemoveModel")
        b = r.box("DestroyedModel")
        b.row("Filename")
        r.row("DestroyedModelUsesScale")
        r.row("DestroyForce")
        r.row("DestroyForceRadius")
        r.row("DestroyEffect")
        r.row("DestroyEffectPoint")
        r.row("DestroyEffectTime")
        r.row("ShowInteract")
        r.row("ShowInteractRange")
        r.row("GrenadeSingleHit")

    def GcSubstanceAmount(self, layout, obj, index=0):
        r = RowGen(
            obj.NMS_GcDestructableComponentData_props.GivesSubstances[index],
            layout)
        r.row("AmountMin")
        r.row("AmountMax")
        r.row("Specific")
        r.row("SpecificSecondary")
        b = r.box("SubstanceCategory")
        b.row("SubstanceCategory")
        b = r.box("Rarity")
        b.row("Rarity")

    # GcSimpleInteractionComponentData related layouts
    def GcSimpleInteractionComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcSimpleInteractionComponentData_props, layout)
        r.row("SimpleInteractionType")
        r.row("InteractDistance")
        r.row("Id")
        b1 = r.box("Rarity")
        b1.row("Rarity")
        b1 = r.box("SizeIndicator")
        b1.row("SizeIndicator")
        r.row("TriggerAction")
        r.row("BroadcastTriggerAction")
        r.row("Delay")
        r.row("InteractIsCrime")
        r.row("InteractCrimeLevel")
        b1 = r.box("ActivationCost")
        b1.row("SubstanceId")
        b1.listbox(self, obj,
                   "NMS_GcSimpleInteractionComponentData_props.ActivationCost",
                   "AltIds", "NMSString0x10_GcSimpleInteractionComponentData")
        b1.row("Cost")
        b1.row("Repeat")
        b1.row("RequiredTech")
        b1 = r.box("StatToTrack")
        b1.row("Stat")
        r.row("Name")
        r.row("TerminalMessage")
        r.row("ScanType")
        r.row("ScanData")
        b1 = r.box("ScanIcon")
        b1.row("DiscoveryType")
        r.listbox(self, obj, "NMS_GcSimpleInteractionComponentData_props",
                  "BaseBuildingTriggerActions", "GcBaseBuildingTriggerAction")

    def GcBaseBuildingTriggerAction(self, layout, obj, index=0):
        r = RowGen(
            obj.NMS_GcSimpleInteractionComponentData_props.BaseBuildingTriggerActions[index],  # noqa
            layout)
        r.row("ID")
        r.row("TimeDelay")

    def NMSString0x10_GcSimpleInteractionComponentData(self, layout, obj,
                                                       index=0):
        r = RowGen(
            obj.NMS_GcSimpleInteractionComponentData_props.ActivationCost.AltIds[index],  # noqa
            layout)
        r.row("Value")

    # GcCustomInventoryComponentData related layouts
    def GcCustomInventoryComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcCustomInventoryComponentData_props, layout)
        r.row("Size")
        r.listbox(self, obj, "NMS_GcCustomInventoryComponentData_props",
                  "DesiredTechs", "GcInventoryTechProbability")
        r.row("Cool")

    def GcInventoryTechProbability(self, layout, obj, index=0):
        r = RowGen(
            obj.NMS_GcCustomInventoryComponentData_props.DesiredTechs[index],
            layout)
        r.row("Tech")
        r.row("DesiredTechProbability")

    # GcAISpaceshipComponentData related layouts
    def GcAISpaceshipComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcAISpaceshipComponentData_props, layout)
        b1 = r.box("Type")
        b1.row("ShipType")
        b1 = r.box("Class")
        b1.row("ShipClass")
        b1 = r.box("Axis")
        b1.row("PrimaryAxis")
        b1 = r.box("Hangar")
        b1.row("Filename")
        r.row("IsSpaceAnomaly")

    # TkAudioComponentData related layouts
    def TkAudioComponentData(self, layout, obj):
        r = RowGen(obj.NMS_TkAudioComponentData_props, layout)
        r.row("Ambient")
        r.row("MaxDistance")
        r.listbox(self, obj, "NMS_TkAudioComponentData_props", "AnimTriggers",
                  "TkAudioAnimTrigger")

    def TkAudioAnimTrigger(self, layout, obj, index=0):
        r = RowGen(obj.NMS_TkAudioComponentData_props.AnimTriggers[index],
                   layout)
        r.row("Sound")
        r.row("Anim")
        r.row("FrameStart")

    # GcEncyclopediaComponentData related layouts
    def GcEncyclopediaComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcEncyclopediaComponentData_props, layout)
        b1 = r.box("Type")
        b1.row("DiscoveryType")

    # GcEncounterComponentData related layouts
    def GcEncounterComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcEncounterComponentData_props, layout)
        r.row("EncounterType")

    # GcSpaceshipComponentData related layouts
    def GcSpaceshipComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcSpaceshipComponentData_props, layout)
        b1 = r.box("ShipClass")
        b1.row("ShipClass")
        r.row("Cockpit")
        r.row("MaxHeadTurn")
        r.row("MaxHeadPitchUp")
        r.row("MaxHeadPitchDown")
        r.row("BaseHealth")
        r.row("FoVFixedDistance")
        r.row("WheelModel")

    # GcInteractionComponentData related layouts
    def GcInteractionComponentData(self, layout, obj):
        r = RowGen(obj.NMS_GcInteractionComponentData_props, layout)
        r.row("InteractionAction")
        b1 = r.box("InteractionType")
        b1.row("InteractionType")
        b1 = r.box("Renderer")
        b2 = b1.box("Camera")
        b2.row("Distance")
        b3 = b2.box("Offset")
        b3.row("x")
        b3.row("y")
        b3.row("z")
        b3.row("t")
        b2.row("Pitch")
        b2.row("Rotate")
        b2.row("LightPitch")
        b2.row("LightRotate")
        b3 = b2.box("Wander")
        b3.row("CamWander")
        b3.row("CamWanderPhase")
        b3.row("CamWanderAmplitude")
        b1.row("Fov")
        b1.row("AspectRatio")
        b1.row("ThumbnailMode")
        b1.row("FocusType")
        b1.row("Anim")
        b1.row("HeightOffset")
        b1 = r.box("Race")
        b1.row("AlienRace")
        r.row("AttractDistanceSq")
        r.row("RepeatInteraction")
        r.row("UseInteractCamera")
        r.row("BlendToCameraTime")
        r.row("BlendFromCameraTime")
        b1 = r.box("ActivationCost")
        b1.row("SubstanceId")
        b1.listbox(self, obj,
                   "NMS_GcInteractionComponentData_props.ActivationCost",
                   "AltIds",
                   "NMSString0x10_GcInteractionComponentData_ActivationCost")
        b1.row("Cost")
        b1.row("Repeat")
        b1.row("RequiredTech")
        r.row("TriggerAction")
        r.row("BroadcastTriggerAction")
        r.row("InteractAngle")
        r.row("InteractDistance")
        r.row("InteractInvertFace")
        b1 = r.box("SecondaryInteractionType")
        b1.row("InteractionType")
        b1 = r.box("SecondaryActivationCost")
        b1.row("SubstanceId")
        b1.listbox(
            self, obj,
            "NMS_GcInteractionComponentData_props.SecondaryActivationCost_props",  # noqa
            "AltIds",
            "NMSString0x10_GcInteractionComponentData_SecondaryActivationCost")
        b1.row("Cost")
        b1.row("Repeat")
        b1.row("RequiredTech")
        r.listbox(self, obj, "NMS_GcInteractionComponentData_props",
                  "EventRenderers", "TkModelRendererData")
        r.row("SecondaryCameraTransitionTime")
        r.row("DoInteractionsInOrder")
        b1 = r.box("DepthOfField")
        b1.row("IsEnabled")
        b1.row("UseGlobals")
        b1.row("NearPlaneMin")
        b1.row("NearPlaneAdjust")
        b1.row("FarPlane")
        b1.row("FarFadeDistance")
        r.listbox(self, obj, "NMS_GcInteractionComponentData_props",
                  "PuzzleMissionOverrideTable", "GcAlienPuzzleMissionOverride")

    def TkModelRendererData(self, layout, obj, index=0):
        r = RowGen(
            obj.NMS_GcInteractionComponentData_props.EventRenderers[index],
            layout)
        b1 = r.box("Camera")
        b1.row("Distance")
        b2 = b1.box("Offset")
        b2.row("x")
        b2.row("y")
        b2.row("z")
        b2.row("t")
        b1.row("Pitch")
        b1.row("Rotate")
        b1.row("LightPitch")
        b1.row("LightRotate")
        b2 = b1.box("Wander")
        b2.row("CamWander")
        b2.row("CamWanderPhase")
        b2.row("CamWanderAmplitude")
        r.row("Fov")
        r.row("AspectRatio")
        r.row("ThumbnailMode")
        r.row("FocusType")
        r.row("Anim")
        r.row("HeightOffset")

    def GcAlienPuzzleMissionOverride(self, layout, obj, index=0):
        r = RowGen(
            obj.NMS_GcInteractionComponentData_props.PuzzleMissionOverrideTable[index],  # noqa
            layout)
        r.row("Mission")
        r.row("Puzzle")

    def NMSString0x10_GcInteractionComponentData_ActivationCost(self, layout,
                                                                obj, index=0):
        r = RowGen(
            obj.NMS_GcInteractionComponentData_props.ActivationCost_props.AltIds[index],  # noqa
            layout)
        r.row("Value")

    def NMSString0x10_GcInteractionComponentData_SecondaryActivationCost(
            self, layout, obj, index=0):
        r = RowGen(
            obj.NMS_GcInteractionComponentData_props.SecondaryActivationCost_props.AltIds[index],  # noqa
            layout)
        r.row("Value")


""" Operators required for button functionality in the UI elements """


class AddListStruct(bpy.types.Operator):
    bl_idname = "wm.add_list_struct"
    bl_label = "Add List Struct"

    # name of the struct that is to be added
    list_struct = StringProperty()
    # name of the property containing the CollectionProperty
    prop_name = StringProperty()
    # not needed??
    curr_index = IntProperty()

    def execute(self, context):
        obj = context.object
        # TODO: see if this is needed? Maybe .add() returns None??
        list_obj = rgetattr(obj, "{0}.{1}".format(self.list_struct,
                                                  self.prop_name)).add()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class RemoveListStruct(bpy.types.Operator):
    bl_idname = "wm.remove_list_struct"
    bl_label = "Remove Entity Struct"

    remove_index = IntProperty()
    list_struct = StringProperty()
    prop_name = StringProperty()

    def execute(self, context):
        obj = context.object
        list_obj = rgetattr(
            obj, "{0}.{1}".format(self.list_struct,
                                  self.prop_name)).remove(self.remove_index)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


# this will add the selected struct to the selectable list
class AddEntityStruct(bpy.types.Operator):
    bl_idname = "wm.add_entity_struct"
    bl_label = "Add Entity Struct"

    structs = EnumProperty(
        items=[("GcObjectPlacementComponentData",
                "GcObjectPlacementComponentData",
                "Relates to placements of objects in the "
                "SelectableObjectsTable in Metadata"),
               ("GcScannableComponentData", "GcScannableComponentData",
                "This allows the entity to be scannable"),
               ("GcShootableComponentData", "GcShootableComponentData",
                "Describes how the entity reacts to being shot"),
               ("GcDestructableComponentData", "GcDestructableComponentData",
                "Decribes what happens when the object is destroyed"),
               ("GcSimpleInteractionComponentData",
                "GcSimpleInteractionComponentData",
                "The simpler interaction type"),
               ("GcInteractionComponentData", "GcInteractionComponentData",
                "Full interaction type"),
               ("GcAISpaceshipComponentData", "GcAISpaceshipComponentData",
                "Causes the object to be an AI spaceship"),
               ("GcCustomInventoryComponentData",
                "GcCustomInventoryComponentData",
                "Used to correlate with the inventory table"),
               ("TkAudioComponentData", "TkAudioComponentData",
                "Sets up an ambient soundscape around the object"),
               ("GcEncyclopediaComponentData", "GcEncyclopediaComponentData",
                "Lets the object appear in the encyclopedia"),
               ("GcEncounterComponentData", "GcEncounterComponentData",
                "Places sentry sentinals around the object (like a factory)"),
               ("GcSpaceshipComponentData", "GcSpaceshipComponentData",
                "Required to make a ship fly-able")])

    def execute(self, context):
        # add the struct name to the objects' list of structs so that it can be
        # drawn in the UI
        obj = context.object
        # only add the struct if it isn't already in the list
        if not self.entity_exists(obj, self.structs):
            new_name = obj.EntityStructs.add()
            new_name.name = self.structs
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

    @staticmethod
    def entity_exists(obj, name):
        # returns True if the named struct is already in the obj's
        # EntityStructs
        for i in obj.EntityStructs:
            if i.name == name:
                return True
        return False


# this will allow the cross to remove the box from the entity panel
class RemoveEntityStruct(bpy.types.Operator):
    bl_idname = "wm.remove_entity_struct"
    bl_label = "Remove Entity Struct"

    remove_name = StringProperty(name='remove_name')

    def execute(self, context):
        obj = context.object
        # gotta remove it in a really annoying way since the collection
        # property only allows you to remove by index, not anything else...
        i = 0
        for struct_name in obj.EntityStructs:
            if struct_name.name == self.remove_name:
                obj.EntityStructs.remove(i)
            else:
                i += 1
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class MoveEntityUp(bpy.types.Operator):
    bl_idname = 'wm.move_entity_struct_up'
    bl_label = "Move Entity Struct Up"

    struct_name = StringProperty(name='struct_name')

    def execute(self, context):
        obj = context.object
        i = self.get_index(obj)

        # make sure that the object isn't at the top of the list and move
        if i != 0:
            obj.EntityStructs.move(i, i-1)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

    def get_index(self, obj):
        for i, struct in enumerate(obj.EntityStructs):
            if struct.name == self.struct_name:
                return i


class MoveEntityDown(bpy.types.Operator):
    bl_idname = 'wm.move_entity_struct_down'
    bl_label = "Move Entity Struct Down"

    struct_name = StringProperty(name='struct_name')

    def execute(self, context):
        obj = context.object
        i = self.get_index(obj)

        # make sure that the object isn't at the top of the list and move
        if i != len(obj.EntityStructs):
            obj.EntityStructs.move(i, i+1)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

    def get_index(self, obj):
        for i, struct in enumerate(obj.EntityStructs):
            if struct.name == self.struct_name:
                return i


class NMSEntities():
    """ Class to contain all the registration information to be called from the
        nmsdk.py file """
    @staticmethod
    def register():
        # do entity items first...
        bpy.utils.register_class(EntityItem)
        bpy.types.Object.EntityStructs = CollectionProperty(type=EntityItem)

        # register the properties
        bpy.utils.register_class(NMS_TkTextureResource_Properties)
        bpy.utils.register_class(NMS_GcObjectPlacementComponentData_Properties)
        bpy.utils.register_class(NMS_GcScannerIconTypes_Properties)
        bpy.utils.register_class(NMS_GcScannableComponentData_Properties)
        bpy.utils.register_class(NMS_GcProjectileImpactType_Properties)
        bpy.utils.register_class(NMS_GcShootableComponentData_Properties)
        bpy.utils.register_class(NMS_GcStatTrackType_Properties)
        bpy.utils.register_class(NMS_GcRarity_Properties)
        bpy.utils.register_class(NMS_GcRealitySubstanceCategory_Properties)
        bpy.utils.register_class(NMS_GcSubstanceAmount_Properties)
        bpy.utils.register_class(NMS_GcStatsEnum_Properties)
        bpy.utils.register_class(NMS_GcDestructableComponentData_Properties)
        bpy.utils.register_class(NMS_NMSString0x10_Properties)
        bpy.utils.register_class(NMS_GcSizeIndicator_Properties)
        bpy.utils.register_class(NMS_GcBaseBuildingTriggerAction_Properties)
        bpy.utils.register_class(NMS_GcInteractionActivationCost_Properties)
        bpy.utils.register_class(NMS_GcDiscoveryTypes_Properties)
        bpy.utils.register_class(NMS_GcSimpleInteractionComponentData_Properties)  # noqa
        bpy.utils.register_class(NMS_GcInventoryTechProbability_Properties)
        bpy.utils.register_class(NMS_GcCustomInventoryComponentData_Properties)
        bpy.utils.register_class(NMS_GcAISpaceshipTypes_Properties)
        bpy.utils.register_class(NMS_GcSpaceshipClasses_Properties)
        bpy.utils.register_class(NMS_GcPrimaryAxis_Properties)
        bpy.utils.register_class(NMS_GcAISpaceshipComponentData_Properties)
        bpy.utils.register_class(NMS_TkAudioAnimTrigger_Properties)
        bpy.utils.register_class(NMS_TkAudioComponentData_Properties)
        bpy.utils.register_class(NMS_GcEncyclopediaComponentData_Properties)
        bpy.utils.register_class(NMS_GcEncounterComponentData_Properties)
        bpy.utils.register_class(NMS_GcSpaceshipComponentData_Properties)
        bpy.utils.register_class(NMS_TkCameraWanderData_Properties)
        bpy.utils.register_class(NMS_Vector4f_Properties)
        bpy.utils.register_class(NMS_TkModelRendererCameraData_Properties)
        bpy.utils.register_class(NMS_GcAlienPuzzleMissionOverride_Properties)
        bpy.utils.register_class(NMS_TkModelRendererData_Properties)
        bpy.utils.register_class(NMS_GcAlienRace_Properties)
        bpy.utils.register_class(NMS_GcInteractionType_Properties)
        bpy.utils.register_class(NMS_GcInteractionDof_Properties)
        bpy.utils.register_class(NMS_GcInteractionComponentData_Properties)
        bpy.utils.register_class(AddListStruct)
        bpy.utils.register_class(RemoveListStruct)
        bpy.utils.register_class(AddEntityStruct)
        bpy.utils.register_class(RemoveEntityStruct)
        bpy.utils.register_class(MoveEntityDown)
        bpy.utils.register_class(MoveEntityUp)
        bpy.utils.register_class(NMSEntityProperties)
        bpy.utils.register_class(NMSPhysicsProperties)

        # link the properties with the objects' internal variables

        bpy.types.Object.NMS_GcObjectPlacementComponentData_props = PointerProperty(type=NMS_GcObjectPlacementComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcScannableComponentData_props = PointerProperty(type=NMS_GcScannableComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcShootableComponentData_props = PointerProperty(type=NMS_GcShootableComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcDestructableComponentData_props = PointerProperty(type=NMS_GcDestructableComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcSimpleInteractionComponentData_props = PointerProperty(type=NMS_GcSimpleInteractionComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcCustomInventoryComponentData_props = PointerProperty(type=NMS_GcCustomInventoryComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcAISpaceshipComponentData_props = PointerProperty(type=NMS_GcAISpaceshipComponentData_Properties)  # noqa
        bpy.types.Object.NMS_TkAudioComponentData_props = PointerProperty(type=NMS_TkAudioComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcEncyclopediaComponentData_props = PointerProperty(type=NMS_GcEncyclopediaComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcEncounterComponentData_props = PointerProperty(type=NMS_GcEncounterComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcSpaceshipComponentData_props = PointerProperty(type=NMS_GcSpaceshipComponentData_Properties)  # noqa
        bpy.types.Object.NMS_GcInteractionComponentData_props = PointerProperty(type=NMS_GcInteractionComponentData_Properties)  # noqa
        bpy.types.Object.NMSEntity_props = PointerProperty(type=NMSEntityProperties)  # noqa
        bpy.types.Object.NMSPhysics_props = PointerProperty(type=NMSPhysicsProperties)  # noqa

        # register the panels
        bpy.utils.register_class(NMSPhysicsPropertyPanel)
        bpy.utils.register_class(DATA_PT_entities)

    @staticmethod
    def unregister():
        # del bpy.types.Object.EntityStructs

        # unregister the property classes
        bpy.utils.unregister_class(NMS_TkTextureResource_Properties)
        bpy.utils.unregister_class(EntityItem)
        bpy.utils.unregister_class(NMS_GcObjectPlacementComponentData_Properties)  # noqa
        bpy.utils.unregister_class(NMS_GcScannerIconTypes_Properties)
        bpy.utils.unregister_class(NMS_GcScannableComponentData_Properties)
        bpy.utils.unregister_class(NMS_GcProjectileImpactType_Properties)
        bpy.utils.unregister_class(NMS_GcShootableComponentData_Properties)
        bpy.utils.unregister_class(NMS_GcStatTrackType_Properties)
        bpy.utils.unregister_class(NMS_GcRarity_Properties)
        bpy.utils.unregister_class(NMS_GcRealitySubstanceCategory_Properties)
        bpy.utils.unregister_class(NMS_GcSubstanceAmount_Properties)
        bpy.utils.unregister_class(NMS_GcDestructableComponentData_Properties)
        bpy.utils.unregister_class(NMS_NMSString0x10_Properties)
        bpy.utils.unregister_class(NMS_GcStatsEnum_Properties)
        bpy.utils.unregister_class(NMS_GcSizeIndicator_Properties)
        bpy.utils.unregister_class(NMS_GcBaseBuildingTriggerAction_Properties)
        bpy.utils.unregister_class(NMS_GcInteractionActivationCost_Properties)
        bpy.utils.unregister_class(NMS_GcDiscoveryTypes_Properties)
        bpy.utils.unregister_class(NMS_GcSimpleInteractionComponentData_Properties)  # noqa
        bpy.utils.unregister_class(NMS_GcInventoryTechProbability_Properties)
        bpy.utils.unregister_class(NMS_GcCustomInventoryComponentData_Properties)  # noqa
        bpy.utils.unregister_class(NMS_GcAISpaceshipTypes_Properties)
        bpy.utils.unregister_class(NMS_GcSpaceshipClasses_Properties)
        bpy.utils.unregister_class(NMS_GcPrimaryAxis_Properties)
        bpy.utils.unregister_class(NMS_GcAISpaceshipComponentData_Properties)
        bpy.utils.unregister_class(NMS_TkAudioAnimTrigger_Properties)
        bpy.utils.unregister_class(NMS_TkAudioComponentData_Properties)
        bpy.utils.unregister_class(NMS_GcEncyclopediaComponentData_Properties)
        bpy.utils.unregister_class(NMS_GcEncounterComponentData_Properties)
        bpy.utils.unregister_class(NMS_GcSpaceshipComponentData_Properties)
        bpy.utils.unregister_class(NMS_TkCameraWanderData_Properties)
        bpy.utils.unregister_class(NMS_Vector4f_Properties)
        bpy.utils.unregister_class(NMS_TkModelRendererCameraData_Properties)
        bpy.utils.unregister_class(NMS_GcAlienPuzzleMissionOverride_Properties)
        bpy.utils.unregister_class(NMS_TkModelRendererData_Properties)
        bpy.utils.unregister_class(NMS_GcAlienRace_Properties)
        bpy.utils.unregister_class(NMS_GcInteractionType_Properties)
        bpy.utils.unregister_class(NMS_GcInteractionDof_Properties)
        bpy.utils.unregister_class(NMS_GcInteractionComponentData_Properties)
        bpy.utils.unregister_class(AddListStruct)
        bpy.utils.unregister_class(RemoveListStruct)
        bpy.utils.unregister_class(AddEntityStruct)
        bpy.utils.unregister_class(RemoveEntityStruct)
        bpy.utils.unregister_class(MoveEntityDown)
        bpy.utils.unregister_class(MoveEntityUp)
        bpy.utils.unregister_class(NMSEntityProperties)
        bpy.utils.unregister_class(NMSPhysicsProperties)

        # delete the properties from the objects
        del bpy.types.Object.EntityStructs
        del bpy.types.Object.NMS_GcObjectPlacementComponentData_props
        del bpy.types.Object.NMS_GcShootableComponentData_props
        del bpy.types.Object.NMS_GcDestructableComponentData_props
        del bpy.types.Object.NMS_GcSimpleInteractionComponentData_props
        del bpy.types.Object.NMS_GcCustomInventoryComponentData_props
        del bpy.types.Object.NMS_GcAISpaceshipComponentData_props
        del bpy.types.Object.NMS_TkAudioComponentData_props
        del bpy.types.Object.NMS_GcEncyclopediaComponentData_props
        del bpy.types.Object.NMS_GcEncounterComponentData_props
        del bpy.types.Object.NMS_GcSpaceshipComponentData_props
        del bpy.types.Object.NMS_GcInteractionComponentData_props
        del bpy.types.Object.NMSEntity_props
        del bpy.types.Object.NMSPhysics_props

        # unregister the panels
        bpy.utils.unregister_class(NMSPhysicsPropertyPanel)
        bpy.utils.unregister_class(DATA_PT_entities)
