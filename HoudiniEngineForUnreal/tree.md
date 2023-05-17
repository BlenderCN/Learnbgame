  Learnbgame
     │  Learnbgame.uproject
     │  terrain.hda
     │
     ├─Config
     │  │  DefaultEditor.ini
     │  │  DefaultEditorPerProjectUserSettings.ini
     │  │  DefaultEngine.ini
     │  │  DefaultGame.ini
     │  │  DefaultInput.ini
     │  │
     │  └─Localization
     │          Game_Compile.ini
     │          Game_Gather.ini
     │          Game_GenerateReports.ini
     │
     └─Content
         │  Lmy.uasset
         │
         ├─Collections
         ├─CompleteRPG
         │  ├─Blueprints
         │  │  ├─Alchemy
         │  │  │      BP_QuestAlchemyst.uasset
         │  │  │      BP_SellerCharacter.uasset
         │  │  │      E_SellerType.uasset
         │  │  │
         │  │  ├─AngleSpeed
         │  │  │      AC_AngleSpeed.uasset
         │  │  │      FC_AcgleWalking.uasset
         │  │  │
         │  │  ├─Areas
         │  │  │      BP_Area.uasset
         │  │  │      BP_NavPoint.uasset
         │  │  │      BP_TravelPoint.uasset
         │  │  │
         │  │  ├─ClimbSystem
         │  │  │      AC_ClimbComponent.uasset
         │  │  │      BP_ClimbHelper.uasset
         │  │  │      BP_I_ClimbInterface.uasset
         │  │  │
         │  │  ├─Combat
         │  │  │  │  AC_CombatEvents.uasset
         │  │  │  │  AC_RegisterCollision.uasset
         │  │  │  │
         │  │  │  └─AI
         │  │  │      │  BT_StunedAI.uasset
         │  │  │      │
         │  │  │      ├─Characters
         │  │  │      │      BP_Axe_AI.uasset
         │  │  │      │      BP_Sword_AI.uasset
         │  │  │      │      BP_Warrior_AI.uasset
         │  │  │      │
         │  │  │      ├─Controll
         │  │  │      │      BB_MainBlackboard.uasset
         │  │  │      │      BP_CombatAI.uasset
         │  │  │      │      BP_MainAIController.uasset
         │  │  │      │
         │  │  │      ├─Decorators
         │  │  │      │      BTD_CanInteractTarget.uasset
         │  │  │      │      BTD_CanReach.uasset
         │  │  │      │      BTD_HasEnergy.uasset
         │  │  │      │      BTD_RandomInteger.uasset
         │  │  │      │
         │  │  │      ├─EQS
         │  │  │      │  │  EQS_Target.uasset
         │  │  │      │  │
         │  │  │      │  └─LeftAndRight
         │  │  │      │          EQS_LeftWalk.uasset
         │  │  │      │          EQS_LeftWalkPoint.uasset
         │  │  │      │          EQS_ReightWalt.uasset
         │  │  │      │          EQS_RightWalkPoint.uasset
         │  │  │      │
         │  │  │      ├─Services
         │  │  │      │  │  BTS_Distance.uasset
         │  │  │      │  │  BTS_Strafe.uasset
         │  │  │      │  │
         │  │  │      │  └─Toggles
         │  │  │      │          BTS_ToggleAttacking.uasset
         │  │  │      │          BTS_ToggleRotation.uasset
         │  │  │      │
         │  │  │      └─Tasks
         │  │  │          │  BTT_MoveToPatrolPoint.uasset
         │  │  │          │  BTT_PlayMontageByAction.uasset
         │  │  │          │  BTT_RandomAttackPlay.uasset
         │  │  │          │  BTT_StopMontage.uasset
         │  │  │          │  BTT_StopMovement.uasset
         │  │  │          │
         │  │  │          └─SetKEys
         │  │  │              │  BTT_TaskBase.uasset
         │  │  │              │
         │  │  │              ├─Combat
         │  │  │              │      BTT_RandomAttack.uasset
         │  │  │              │      BTT_RandomBeh.uasset
         │  │  │              │      BTT_SetAttack.uasset
         │  │  │              │      BTT_SetCombat.uasset
         │  │  │              │      BTT_SetRangeToTarget.uasset
         │  │  │              │
         │  │  │              └─Patrol
         │  │  │                      BTT_ChangePatrol.uasset
         │  │  │                      BTT_SetMovementState.uasset
         │  │  │
         │  │  ├─DemoCharacter
         │  │  │      BP_ArmorHelper.uasset
         │  │  │      BP_MainController.uasset
         │  │  │
         │  │  ├─Dialogue
         │  │  │  │  AC_DialogueSystem.uasset
         │  │  │  │  BP_AdvancedCamActor.uasset
         │  │  │  │  BP_CameraHelper.uasset
         │  │  │  │  BP_CasualCharacter.uasset
         │  │  │  │  BP_DialogueCharacter.uasset
         │  │  │  │  BP_PatrolPoint.uasset
         │  │  │  │
         │  │  │  ├─MainQuest
         │  │  │  │      BP_LittleBrother.uasset
         │  │  │  │      BP_OldHouseMan.uasset
         │  │  │  │      BP_QuestDialChar.uasset
         │  │  │  │
         │  │  │  └─SideQuests
         │  │  │          BP_NeckleCharacter.uasset
         │  │  │          BP_ThievesTask.uasset
         │  │  │
         │  │  ├─Eagle
         │  │  │      AC_Eagle.uasset
         │  │  │      BP_FlyingPawn.uasset
         │  │  │
         │  │  ├─FallDamage
         │  │  │      AC_FallDamage.uasset
         │  │  │      BP_NoFallDamage.uasset
         │  │  │      DT_FallSound.uasset
         │  │  │      E_FallType.uasset
         │  │  │      FC_FallDamage.uasset
         │  │  │      S_FallSound.uasset
         │  │  │
         │  │  ├─Footsteps
         │  │  │      AC_Footsteps.uasset
         │  │  │      BP_FootstepEmitter.uasset
         │  │  │      BP_FootstepHelper.uasset
         │  │  │
         │  │  ├─GameSettings
         │  │  │      DT_GameSettings.uasset
         │  │  │      E_UnlockType.uasset
         │  │  │      S_GameSettings.uasset
         │  │  │
         │  │  ├─IK
         │  │  │  │  AC_FootIK.uasset
         │  │  │  │  BP_I_FootIK.uasset
         │  │  │  │  E_WhatChange.uasset
         │  │  │  │
         │  │  │  └─HeadRotation
         │  │  │          AC_HeadRotator.uasset
         │  │  │          BP_I_HeadRotation.uasset
         │  │  │
         │  │  ├─Information
         │  │  │  │  E_Region.uasset
         │  │  │  │  E_SallerState.uasset
         │  │  │  │  E_WorldActorType.uasset
         │  │  │  │
         │  │  │  ├─AIStates
         │  │  │  │      E_Health_AI.uasset
         │  │  │  │      E_MovementState_AI.uasset
         │  │  │  │      E_Patrol_AI.uasset
         │  │  │  │      E_State_AI.uasset
         │  │  │  │
         │  │  │  ├─Alchemy
         │  │  │  │  │  DT_Alchemy.uasset
         │  │  │  │  │  E_AlchemyType.uasset
         │  │  │  │  │  E_AlchemyWidgetType.uasset
         │  │  │  │  │  S_Alchemy.uasset
         │  │  │  │  │
         │  │  │  │  └─WidgetSetup
         │  │  │  │          S_CreaftAlchemyItemTypes.uasset
         │  │  │  │          S_WidgetCraftSetup.uasset
         │  │  │  │
         │  │  │  ├─Area
         │  │  │  │      DT_Areas.uasset
         │  │  │  │      E_AreaOwners.uasset
         │  │  │  │      S_AreaInfoStat.uasset
         │  │  │  │      S_AreaStateStat.uasset
         │  │  │  │
         │  │  │  ├─BooksInfo
         │  │  │  │      DT_BpoksInfo.uasset
         │  │  │  │      S_BookDynamic.uasset
         │  │  │  │      S_BookInfo.uasset
         │  │  │  │
         │  │  │  ├─CharactersInfo
         │  │  │  │      AC_CharactersInformation.uasset
         │  │  │  │      BP_Save_Characters.uasset
         │  │  │  │      DT_CharacterInformation.uasset
         │  │  │  │      E_JobTypes.uasset
         │  │  │  │      S_CharacterDynam.uasset
         │  │  │  │      S_CharacterInfoStat.uasset
         │  │  │  │
         │  │  │  ├─Combat
         │  │  │  │      E_AttackType.uasset
         │  │  │  │      E_Combat_AI.uasset
         │  │  │  │      E_HitDirection.uasset
         │  │  │  │      E_WeaponType.uasset
         │  │  │  │
         │  │  │  ├─CombatInformation
         │  │  │  │  │  S_Axis.uasset
         │  │  │  │  │
         │  │  │  │  ├─DataTable
         │  │  │  │  │      DT_AI_Animations.uasset
         │  │  │  │  │      DT_FightAnimations.uasset
         │  │  │  │  │
         │  │  │  │  ├─RotationMovementCombat
         │  │  │  │  │      E_MontageAction.uasset
         │  │  │  │  │      E_Range.uasset
         │  │  │  │  │      E_RotationMode.uasset
         │  │  │  │  │      E_State.uasset
         │  │  │  │  │
         │  │  │  │  └─Struct
         │  │  │  │          S_CombatMontage.uasset
         │  │  │  │
         │  │  │  ├─CreaturesInfo
         │  │  │  │      DT_CreatureInfo.uasset
         │  │  │  │      S_CreatureDynamic.uasset
         │  │  │  │      S_CreatureInfo.uasset
         │  │  │  │      S_CreatureWeakness.uasset
         │  │  │  │
         │  │  │  ├─DialogueInfo
         │  │  │  │  ├─Enums
         │  │  │  │  │      e_DialogueSelectionTypes.uasset
         │  │  │  │  │      E_OptionType.uasset
         │  │  │  │  │
         │  │  │  │  └─Structures
         │  │  │  │          DT_CharacterTitleText.uasset
         │  │  │  │          DT_DialogueInfo.uasset
         │  │  │  │          S_CharacterTextDynamic.uasset
         │  │  │  │          S_CharacterTitleText.uasset
         │  │  │  │          S_DialogueInfo.uasset
         │  │  │  │          S_DialogueInfoDynamic.uasset
         │  │  │  │          S_DialogueOption.uasset
         │  │  │  │          S_OptionInfo.uasset
         │  │  │  │
         │  │  │  ├─Effects
         │  │  │  │      DT_EffectsInformation.uasset
         │  │  │  │      S_EffectsInformation.uasset
         │  │  │  │
         │  │  │  ├─FootSteps
         │  │  │  │      DT_Footsteps.uasset
         │  │  │  │      DT_HorseSteps.uasset
         │  │  │  │      S_FootstepType.uasset
         │  │  │  │
         │  │  │  ├─Inventory
         │  │  │  │      DT_SubslotIcon.uasset
         │  │  │  │      DT_SubslotsArray.uasset
         │  │  │  │      E_InventoryOwnerType.uasset
         │  │  │  │      E_InventorySort.uasset
         │  │  │  │      E_MoveType.uasset
         │  │  │  │      S_SubslotIcon.uasset
         │  │  │  │      S_SubslotsArray.uasset
         │  │  │  │
         │  │  │  ├─Items
         │  │  │  │  │  DT_Items.uasset
         │  │  │  │  │  E_ItemSubtype.uasset
         │  │  │  │  │  E_ItemType.uasset
         │  │  │  │  │  S_ItemsInventory.uasset
         │  │  │  │  │  S_ItemStatic.uasset
         │  │  │  │  │  S_RewardStat.uasset
         │  │  │  │  │
         │  │  │  │  ├─Armor
         │  │  │  │  │      DT_ArmorInformation.uasset
         │  │  │  │  │      E_ArmorType.uasset
         │  │  │  │  │      S_ArmorInformation.uasset
         │  │  │  │  │
         │  │  │  │  ├─BombsInfo
         │  │  │  │  │      DT_BombInfo.uasset
         │  │  │  │  │      S_Bomb.uasset
         │  │  │  │  │
         │  │  │  │  ├─FoodInfo
         │  │  │  │  │      DT_FoodInformation.uasset
         │  │  │  │  │      E_FoodEffect.uasset
         │  │  │  │  │      S_EffectValues.uasset
         │  │  │  │  │      S_Food.uasset
         │  │  │  │  │
         │  │  │  │  ├─Modifications
         │  │  │  │  │      DT_Modification.uasset
         │  │  │  │  │      S_Modification.uasset
         │  │  │  │  │      S_ModificationHandler.uasset
         │  │  │  │  │
         │  │  │  │  ├─Rarity
         │  │  │  │  │      DT_RarityColor.uasset
         │  │  │  │  │      E_ItemRarity.uasset
         │  │  │  │  │      S_RarityColor.uasset
         │  │  │  │  │
         │  │  │  │  └─Weapon
         │  │  │  │          DT_WeapInfo.uasset
         │  │  │  │          E_WeaponTypeLong.uasset
         │  │  │  │          S_DamageRange.uasset
         │  │  │  │          S_WeaponInformation.uasset
         │  │  │  │
         │  │  │  ├─PlayerInfo
         │  │  │  │  │  DT_HorseSpeed.uasset
         │  │  │  │  │  DT_Speed.uasset
         │  │  │  │  │  DT_StaminaConsumption.uasset
         │  │  │  │  │  E_WalkState.uasset
         │  │  │  │  │  S_StaminaConsumption.uasset
         │  │  │  │  │  S_WalkState.uasset
         │  │  │  │  │
         │  │  │  │  ├─Chances
         │  │  │  │  │      E_EffectType.uasset
         │  │  │  │  │      S_EffectChance.uasset
         │  │  │  │  │
         │  │  │  │  └─Particles
         │  │  │  │          DT_ParticleEffect.uasset
         │  │  │  │          S_ParticleEffect.uasset
         │  │  │  │
         │  │  │  ├─Quests
         │  │  │  │      DT_Quests.uasset
         │  │  │  │      E_QuestCompleteType.uasset
         │  │  │  │      S_QuestDynam.uasset
         │  │  │  │      S_QuestsMain.uasset
         │  │  │  │      S_SubtaskComplete.uasset
         │  │  │  │
         │  │  │  ├─Saves
         │  │  │  │  │  BP_SaveSaveBlueprints.uasset
         │  │  │  │  │  BP_Save_items.uasset
         │  │  │  │  │  S_AreaSave.uasset
         │  │  │  │  │  S_OtherMoneyAndInventory.uasset
         │  │  │  │  │  S_SaveQuestAct.uasset
         │  │  │  │  │  S_SaveSaveBlueprint.uasset
         │  │  │  │  │  S_SaveWorldItem.uasset
         │  │  │  │  │  S_SaveWorldParts.uasset
         │  │  │  │  │
         │  │  │  │  └─Widgets
         │  │  │  │          S_PlayerViewSave.uasset
         │  │  │  │
         │  │  │  ├─Skills
         │  │  │  │  ├─DataTable
         │  │  │  │  │      DT_Color_Icon_Skill.uasset
         │  │  │  │  │      DT_Skills.uasset
         │  │  │  │  │      DT_SubAndSkill.uasset
         │  │  │  │  │      DT_SubskillIcon.uasset
         │  │  │  │  │      DT_SubslotSkills.uasset
         │  │  │  │  │
         │  │  │  │  ├─Enums
         │  │  │  │  │      E_SkillSubtype.uasset
         │  │  │  │  │      E_SkillType.uasset
         │  │  │  │  │
         │  │  │  │  └─Structs
         │  │  │  │          S_ColorSkillIcon.uasset
         │  │  │  │          S_EffectChances.uasset
         │  │  │  │          S_SaveSkillUpgrade.uasset
         │  │  │  │          S_Skill.uasset
         │  │  │  │          S_SkillAndSubskill.uasset
         │  │  │  │          S_SkillDynamic.uasset
         │  │  │  │          S_SubskillIcon.uasset
         │  │  │  │          S_SubslotSkills.uasset
         │  │  │  │
         │  │  │  ├─Tasks
         │  │  │  │      DT_TaskInformation.uasset
         │  │  │  │      E_TaskType.uasset
         │  │  │  │      S_PlaceTask.uasset
         │  │  │  │      S_pTaskList.uasset
         │  │  │  │
         │  │  │  ├─tutorial
         │  │  │  │      DT_Tutorial.uasset
         │  │  │  │      S_Tutorial.uasset
         │  │  │  │      S_TutorialDynamic.uasset
         │  │  │  │
         │  │  │  ├─Widgets
         │  │  │  │      DT_DefaultMapping.uasset
         │  │  │  │      E_InteractTypes.uasset
         │  │  │  │      E_MainPromptType.uasset
         │  │  │  │      S_DefaultMapping.uasset
         │  │  │  │
         │  │  │  ├─WorldActor
         │  │  │  │      DT_WorldActors.uasset
         │  │  │  │      E_WorldActor.uasset
         │  │  │  │      S_ExpRange.uasset
         │  │  │  │      S_MoneyRange.uasset
         │  │  │  │      S_WorldActor.uasset
         │  │  │  │
         │  │  │  ├─WorldMap
         │  │  │  │      DT_DrawObjectsMapSize.uasset
         │  │  │  │      E_ObjectType.uasset
         │  │  │  │      E_TargetPointType.uasset
         │  │  │  │      S_DrawObjectsPerc.uasset
         │  │  │  │      S_MarkerInformation.uasset
         │  │  │  │
         │  │  │  └─WorldParts
         │  │  │      │  DT_WorldParts.uasset
         │  │  │      │  E_CollisionTypeWP.uasset
         │  │  │      │  S_WorldPart.uasset
         │  │  │      │  S_WorldPartDynamic.uasset
         │  │  │      │
         │  │  │      └─AreaEmblem
         │  │  │              DT_AreaEmblem.uasset
         │  │  │              S_AreaEmblem.uasset
         │  │  │
         │  │  ├─InteractActors
         │  │  │  │  BP_BagWithNeckle.uasset
         │  │  │  │  BP_BigBagMoney.uasset
         │  │  │  │  BP_HardChest.uasset
         │  │  │  │  BP_InteractActor.uasset
         │  │  │  │  BP_MultBag.uasset
         │  │  │  │  BP_SimpleChest.uasset
         │  │  │  │
         │  │  │  └─InteractItems
         │  │  │          BP_GemWorld.uasset
         │  │  │          BP_InvItem.uasset
         │  │  │          BP_StoneWorld.uasset
         │  │  │
         │  │  ├─Inventory
         │  │  │      BP_InventoryHelper.uasset
         │  │  │      FC_WeightSpeed.uasset
         │  │  │
         │  │  ├─Lock
         │  │  │      AC_LockedActor.uasset
         │  │  │      BP_LockedActorRender.uasset
         │  │  │
         │  │  ├─MapComponents
         │  │  │  │  AC_QuestsHandler.uasset
         │  │  │  │
         │  │  │  ├─ComponentsSaves
         │  │  │  │  │  BP_Save_Areas.uasset
         │  │  │  │  │  BP_Save_Exp.uasset
         │  │  │  │  │  BP_Save_Inventory.uasset
         │  │  │  │  │  BP_Save_Money.uasset
         │  │  │  │  │  BP_Save_Time.uasset
         │  │  │  │  │
         │  │  │  │  └─Quests
         │  │  │  │          BP_Save_Quests.uasset
         │  │  │  │          S_qLocation.uasset
         │  │  │  │          S_SaveQuestCharacter.uasset
         │  │  │  │
         │  │  │  ├─Interaction
         │  │  │  │      AC_Interaction.uasset
         │  │  │  │      BP_InteractionSpheresHelper.uasset
         │  │  │  │
         │  │  │  ├─Minimap
         │  │  │  │      AC_Minimap.uasset
         │  │  │  │      BP_MinimapHandler.uasset
         │  │  │  │
         │  │  │  ├─PlayerState
         │  │  │  │      AC_ExpSystem.uasset
         │  │  │  │      AC_Inventory.uasset
         │  │  │  │      AC_MoneySystem.uasset
         │  │  │  │
         │  │  │  └─WorldMap
         │  │  │          AC_WorldMap.uasset
         │  │  │          BP_MapTargetPoint.uasset
         │  │  │          BP_Marker.uasset
         │  │  │
         │  │  ├─MultipleItems
         │  │  │      AC_MultipleItems.uasset
         │  │  │
         │  │  ├─Other
         │  │  │  │  BPL_DataTableSlotInfo.uasset
         │  │  │  │  BPL_WidgetsMacro.uasset
         │  │  │  │  BP_ThirdPersonGameMode.uasset
         │  │  │  │  SM_MasterClass.uasset
         │  │  │  │
         │  │  │  └─Interfaces
         │  │  │          BP_I_CanBeAttacked.uasset
         │  │  │          BP_I_CanBeFocused.uasset
         │  │  │          BP_I_Interact.uasset
         │  │  │          BP_I_Widgets.uasset
         │  │  │
         │  │  ├─Player
         │  │  │      AC_FocusTarget.uasset
         │  │  │      AC_PlayerCharaacteristics.uasset
         │  │  │      AC_PlayerCurrentState.uasset
         │  │  │      AC_SavePlayerLocation.uasset
         │  │  │      AC_SpeedChange.uasset
         │  │  │
         │  │  ├─PlayerRender
         │  │  │      BP_RenderMesh.uasset
         │  │  │      M_MeshRender.uasset
         │  │  │      RT_MeshRender.uasset
         │  │  │
         │  │  ├─Portal
         │  │  │      BP_Portal.uasset
         │  │  │
         │  │  ├─Quests
         │  │  │      AC_QuestActor.uasset
         │  │  │      BP_QuestActor.uasset
         │  │  │      BP_QuestCharacter.uasset
         │  │  │      BP_QuestPlaceHelper.uasset
         │  │  │
         │  │  ├─Saves
         │  │  │      BP_FirstEnterSave.uasset
         │  │  │      BP_Save.uasset
         │  │  │      BP_SaveLocation.uasset
         │  │  │      BP_SavePLayerCharact.uasset
         │  │  │      BP_SkillsSave.uasset
         │  │  │
         │  │  ├─Shakes
         │  │  │      BP_ShakeExample.uasset
         │  │  │
         │  │  ├─Skills
         │  │  │      AC_Skills.uasset
         │  │  │
         │  │  ├─Skysphere
         │  │  │  │  BP_SkySphere.uasset
         │  │  │  │
         │  │  │  └─Curves
         │  │  │          FC_CloudNoise1.uasset
         │  │  │          FC_CloudNoise2.uasset
         │  │  │
         │  │  ├─Spells
         │  │  │  │  BP_Fireball.uasset
         │  │  │  │  BP_FrostSpell.uasset
         │  │  │  │  BP_ImpactSpell.uasset
         │  │  │  │  BP_ProjectilePrediction.uasset
         │  │  │  │  BP_SpellBase.uasset
         │  │  │  │  DT_SpellsInfo.uasset
         │  │  │  │  E_ActiveType.uasset
         │  │  │  │  S_Range.uasset
         │  │  │  │  S_SpellInformation.uasset
         │  │  │  │
         │  │  │  ├─Bombs
         │  │  │  │      BP_Arrow.uasset
         │  │  │  │      BP_BombBase.uasset
         │  │  │  │      BP_FireBomb.uasset
         │  │  │  │      BP_FrostBomb.uasset
         │  │  │  │
         │  │  │  └─StartAttachers
         │  │  │          BP_AttacherBase.uasset
         │  │  │          BP_Crossbow.uasset
         │  │  │          BP_FireballAttacher.uasset
         │  │  │          BP_FireBombAttacher.uasset
         │  │  │          BP_FrostBombAttacher.uasset
         │  │  │
         │  │  ├─Targeting
         │  │  │      BP_ArrowHelper.uasset
         │  │  │
         │  │  ├─TimeManagment
         │  │  │  │  AC_TimeManager.uasset
         │  │  │  │  BP_TimeCamera.uasset
         │  │  │  │
         │  │  │  └─DayNight
         │  │  │          FC_DayNightIntensity.uasset
         │  │  │          S_FTime.uasset
         │  │  │
         │  │  ├─Torch
         │  │  │      BP_Torch.uasset
         │  │  │
         │  │  ├─Tutorial
         │  │  │      AC_Tutorial.uasset
         │  │  │      BP_SaveTutorial.uasset
         │  │  │
         │  │  ├─Water
         │  │  │      AC_Swimming.uasset
         │  │  │      BP_Water.uasset
         │  │  │
         │  │  ├─Weather
         │  │  │  │  AC_WeatherScreenEffect.uasset
         │  │  │  │  BP_WeatherManager.uasset
         │  │  │  │  DT_WeatherTypes.uasset
         │  │  │  │  E_WeatherState.uasset
         │  │  │  │  E_YearType.uasset
         │  │  │  │  FC_AlphaCurve.uasset
         │  │  │  │  FC_CloudsSun.uasset
         │  │  │  │  S_WeatherSettings.uasset
         │  │  │  │
         │  │  │  ├─Effects
         │  │  │  │  ├─Blueprints
         │  │  │  │  │      BP_WeatherEffects.uasset
         │  │  │  │  │
         │  │  │  │  ├─Materials
         │  │  │  │  │  │  M_BoltLightning.uasset
         │  │  │  │  │  │  M_PPScreenEffect.uasset
         │  │  │  │  │  │  M_Rain.uasset
         │  │  │  │  │  │  M_RainImpact.uasset
         │  │  │  │  │  │  M_SheetLightning.uasset
         │  │  │  │  │  │
         │  │  │  │  │  └─Functions
         │  │  │  │  │          MPC_StormMaterial.uasset
         │  │  │  │  │          M_LightningLight.uasset
         │  │  │  │  │
         │  │  │  │  ├─Particles
         │  │  │  │  │      NS_Rain.uasset
         │  │  │  │  │      NS_Splash.uasset
         │  │  │  │  │
         │  │  │  │  ├─Sound
         │  │  │  │  │  ├─Cues
         │  │  │  │  │  │      SC_RainLoop.uasset
         │  │  │  │  │  │      SC_ThunderRumble.uasset
         │  │  │  │  │  │
         │  │  │  │  │  └─Wavs
         │  │  │  │  │          S_LightningStrike.uasset
         │  │  │  │  │          S_RainLoop.uasset
         │  │  │  │  │          S_ThunderRumble_1.uasset
         │  │  │  │  │          S_ThunderRumble_2.uasset
         │  │  │  │  │          S_ThunderRumble_3.uasset
         │  │  │  │  │
         │  │  │  │  └─Textures
         │  │  │  │          T_Fog.uasset
         │  │  │  │          T_LightningTexture.uasset
         │  │  │  │          T_Raindrop_3.uasset
         │  │  │  │
         │  │  │  ├─Materials
         │  │  │  │      MPC_Weather.uasset
         │  │  │  │      M_Burst.uasset
         │  │  │  │      M_explosion_subUV.uasset
         │  │  │  │      M_flare_01.uasset
         │  │  │  │      M_radial_ramp.uasset
         │  │  │  │      M_smoke_subUV.uasset
         │  │  │  │
         │  │  │  └─Particles
         │  │  │      │  NS_Explosion.uasset
         │  │  │      │  NS_LightningBolts.uasset
         │  │  │      │  NS_SheetLightning.uasset
         │  │  │      │  NS_Snow.uasset
         │  │  │      │
         │  │  │      └─Materials
         │  │  │              M_Snow.uasset
         │  │  │
         │  │  ├─WidgetHandler
         │  │  │      AC_MainWidgetHandler.uasset
         │  │  │
         │  │  └─WorldParts
         │  │          BP_WorldPart.uasset
         │  │
         │  ├─Font
         │  │  │  100_Fm.uasset
         │  │  │  101_Md.uasset
         │  │  │  102_No.uasset
         │  │  │  103_Lr.uasset
         │  │  │  104_Rf.uasset
         │  │  │  105_Db.uasset
         │  │  │  106_Sg.uasset
         │  │  │  107_Bh.uasset
         │  │  │  108_Hs.uasset
         │  │  │  109_Mt.uasset
         │  │  │  10_Ne.uasset
         │  │  │  110_Ds.uasset
         │  │  │  111_Rg.uasset
         │  │  │  112_Cn.uasset
         │  │  │  113_Uut.uasset
         │  │  │  114_Fl.uasset
         │  │  │  115_Uup.uasset
         │  │  │  116_Lv.uasset
         │  │  │  117_Uus.uasset
         │  │  │  118_Uuo.uasset
         │  │  │  11_Na.uasset
         │  │  │  12_Mg.uasset
         │  │  │  13_Al.uasset
         │  │  │  14_Si.uasset
         │  │  │  15_P.uasset
         │  │  │  16_S.uasset
         │  │  │  17_Cl.uasset
         │  │  │  18_Ar.uasset
         │  │  │  19_K.uasset
         │  │  │  1_H.uasset
         │  │  │  20_Ca.uasset
         │  │  │  21_Sc.uasset
         │  │  │  22_Ti.uasset
         │  │  │  23_V.uasset
         │  │  │  24_Cr.uasset
         │  │  │  25_Mn.uasset
         │  │  │  26_Fe.uasset
         │  │  │  27_Co.uasset
         │  │  │  28_Ni.uasset
         │  │  │  29_Cu.uasset
         │  │  │  2_He.uasset
         │  │  │  30_Zn.uasset
         │  │  │  31_Ga.uasset
         │  │  │  32_Ge.uasset
         │  │  │  33_As.uasset
         │  │  │  34_Se.uasset
         │  │  │  35_Br.uasset
         │  │  │  36_Kr.uasset
         │  │  │  37_Rb.uasset
         │  │  │  38_Sr.uasset
         │  │  │  39_Y.uasset
         │  │  │  3_Li.uasset
         │  │  │  40_Zr.uasset
         │  │  │  41_Nb.uasset
         │  │  │  42_Mo.uasset
         │  │  │  43_Tc.uasset
         │  │  │  44_Ru.uasset
         │  │  │  45_Rh.uasset
         │  │  │  46_Pd.uasset
         │  │  │  47_Ag.uasset
         │  │  │  48_Cd.uasset
         │  │  │  49_In.uasset
         │  │  │  4_Be.uasset
         │  │  │  50_Sn.uasset
         │  │  │  51_Sb.uasset
         │  │  │  52_Te.uasset
         │  │  │  53_I.uasset
         │  │  │  54_Xe.uasset
         │  │  │  55_Cs.uasset
         │  │  │  56_Ba.uasset
         │  │  │  57_La.uasset
         │  │  │  58_Ce.uasset
         │  │  │  59_Pr.uasset
         │  │  │  5_B.uasset
         │  │  │  60_Nd.uasset
         │  │  │  61_Pm.uasset
         │  │  │  62_Sm.uasset
         │  │  │  63_Eu.uasset
         │  │  │  64_Gd.uasset
         │  │  │  65_Tb.uasset
         │  │  │  66_Dy.uasset
         │  │  │  67_Ho.uasset
         │  │  │  68_Er.uasset
         │  │  │  69_Tm.uasset
         │  │  │  6_C.uasset
         │  │  │  70_Yb.uasset
         │  │  │  71_Lu.uasset
         │  │  │  72_Hf.uasset
         │  │  │  73_Ta.uasset
         │  │  │  74_W.uasset
         │  │  │  75_Re.uasset
         │  │  │  76_Os.uasset
         │  │  │  77_Ir.uasset
         │  │  │  78_Pt.uasset
         │  │  │  79_Au.uasset
         │  │  │  7_N.uasset
         │  │  │  80_Hg.uasset
         │  │  │  81_Tl.uasset
         │  │  │  82_Pb.uasset
         │  │  │  83_Bi.uasset
         │  │  │  84_Po.uasset
         │  │  │  85_At.uasset
         │  │  │  86_Rn.uasset
         │  │  │  87_Fr.uasset
         │  │  │  88_Ra.uasset
         │  │  │  89_Ac.uasset
         │  │  │  8_O.uasset
         │  │  │  90_Th.uasset
         │  │  │  91_Pa.uasset
         │  │  │  92_U.uasset
         │  │  │  93_Np.uasset
         │  │  │  94_Pu.uasset
         │  │  │  95_Am.uasset
         │  │  │  96_Cm.uasset
         │  │  │  97_Bk.uasset
         │  │  │  98_Cf.uasset
         │  │  │  99_Es.uasset
         │  │  │  9_F.uasset
         │  │  │
         │  │  └─AminoAcid
         │  │          Alanine.uasset
         │  │          Arginine.uasset
         │  │          Asparagine.uasset
         │  │          Aspartic.uasset
         │  │          cysteine.uasset
         │  │          Glutamate.uasset
         │  │          Glutamine.uasset
         │  │          Glycine.uasset
         │  │          histidine.uasset
         │  │          Isoleucine.uasset
         │  │          Leucine.uasset
         │  │          Lysine.uasset
         │  │          Methionine.uasset
         │  │          Phenylalanine.uasset
         │  │          proline.uasset
         │  │          Serine.uasset
         │  │          Threonine.uasset
         │  │          Tryptophan.uasset
         │  │          Tyrosine.uasset
         │  │          Valine.uasset
         │  │
         │  ├─Horse
         │  │  ├─Animations
         │  │  │  │  ABP_Horse.uasset
         │  │  │  │  A_Horse_Idle.uasset
         │  │  │  │  A_Horse_Run.uasset
         │  │  │  │  A_Horse_Walk.uasset
         │  │  │  │  BP_Horse.uasset
         │  │  │  │  BP_PlayerHorse.uasset
         │  │  │  │  BS_HorseLocomotion.uasset
         │  │  │  │
         │  │  │  └─Jump
         │  │  │          A_Horse_JumpStart.uasset
         │  │  │          A_Horse_Jump_Loop.uasset
         │  │  │          A_Horse_JusmpEnd.uasset
         │  │  │
         │  │  └─Mesh
         │  │          SK_Horse.uasset
         │  │          SK_HorsePhysics.uasset
         │  │          SK_Horse_Skeleton.uasset
         │  │
         │  ├─Mannequin
         │  │  ├─Animations
         │  │  │  ├─AnimationNotifies
         │  │  │  │      ANS_HitBox.uasset
         │  │  │  │      ANS_IgnoreRootMotion-Player.uasset
         │  │  │  │      ANS_PlayerInput.uasset
         │  │  │  │      ANS_RotateTowardsTarget-AI.uasset
         │  │  │  │      AN_IgnoreRootMotion-Player.uasset
         │  │  │  │      AN_ResetCombat-Player.uasset
         │  │  │  │
         │  │  │  ├─Climbing
         │  │  │  │  │  AM_ClimbDown.uasset
         │  │  │  │  │  AM_ClimbUp.uasset
         │  │  │  │  │  AM_JumpDown.uasset
         │  │  │  │  │  AM_JumpLeft.uasset
         │  │  │  │  │  AM_JumpRight.uasset
         │  │  │  │  │  AM_JumpUp.uasset
         │  │  │  │  │  A_Climb.uasset
         │  │  │  │  │  A_Climb_Back.uasset
         │  │  │  │  │  A_CrouchIdle.uasset
         │  │  │  │  │  A_CrouchWalkForward.uasset
         │  │  │  │  │  A_IdleHang.uasset
         │  │  │  │  │  A_JumpDown.uasset
         │  │  │  │  │  A_JumpLeft.uasset
         │  │  │  │  │  A_JumpRight.uasset
         │  │  │  │  │  A_JumpUp.uasset
         │  │  │  │  │  A_MoveLeft.uasset
         │  │  │  │  │  A_MoveRight.uasset
         │  │  │  │  │  A_StandFomCrouch.uasset
         │  │  │  │  │
         │  │  │  │  └─Turn
         │  │  │  │          AM_CornerLeft.uasset
         │  │  │  │          AM_CornerRight.uasset
         │  │  │  │          A_BackLooped.uasset
         │  │  │  │          A_LeftCorner.uasset
         │  │  │  │          A_RightCorner.uasset
         │  │  │  │          A_TurnedBack.uasset
         │  │  │  │
         │  │  │  ├─Combat
         │  │  │  │  │  A_Dash.uasset
         │  │  │  │  │  A_HeavyAttack_06.uasset
         │  │  │  │  │
         │  │  │  │  ├─Block
         │  │  │  │  │      AO_Block.uasset
         │  │  │  │  │      A_Block_AO.uasset
         │  │  │  │  │      A_Idle_AO.uasset
         │  │  │  │  │
         │  │  │  │  ├─Dash
         │  │  │  │  │      AM_Dash.uasset
         │  │  │  │  │
         │  │  │  │  ├─Equip
         │  │  │  │  │      AM_EquipWeapon.uasset
         │  │  │  │  │      AM_UnequipWeapon.uasset
         │  │  │  │  │      A_EquipWeapon.uasset
         │  │  │  │  │      A_UnequipWeapon_.uasset
         │  │  │  │  │
         │  │  │  │  ├─GetHitKick
         │  │  │  │  │      AM_ParryGetHit.uasset
         │  │  │  │  │      AM_Stun.uasset
         │  │  │  │  │      A_ParryGetHit.uasset
         │  │  │  │  │      A_Stun.uasset
         │  │  │  │  │
         │  │  │  │  ├─HeavyAttacks
         │  │  │  │  │      AM_HeavyAttack_01.uasset
         │  │  │  │  │      AM_HeavyAttack_03.uasset
         │  │  │  │  │      A_SwordHeavy_01.uasset
         │  │  │  │  │
         │  │  │  │  ├─LightAttacks
         │  │  │  │  │      AM_LightAttack_01.uasset
         │  │  │  │  │      AM_LightAttack_02.uasset
         │  │  │  │  │      AM_LightAttack_03.uasset
         │  │  │  │  │      A_LightAttack_02.uasset
         │  │  │  │  │      A_LightAttack_03.uasset
         │  │  │  │  │      A_LightAttack_04.uasset
         │  │  │  │  │      A_Thrust.uasset
         │  │  │  │  │
         │  │  │  │  ├─Locomotion
         │  │  │  │  │      A_Idle.uasset
         │  │  │  │  │      A_RunBackward.uasset
         │  │  │  │  │      A_RunBackwardLeft.uasset
         │  │  │  │  │      A_RunBackwardRight.uasset
         │  │  │  │  │      A_RunForward.uasset
         │  │  │  │  │      A_RunForwardLeft.uasset
         │  │  │  │  │      A_RunForwardRight.uasset
         │  │  │  │  │      A_RunLeft.uasset
         │  │  │  │  │      A_RunRight.uasset
         │  │  │  │  │      A_WalkBack.uasset
         │  │  │  │  │      A_WalkBackLeft.uasset
         │  │  │  │  │      A_WalkBackRight.uasset
         │  │  │  │  │      A_WalkBackwardRight.uasset
         │  │  │  │  │      A_WalkForward.uasset
         │  │  │  │  │      A_WalkForwardLeft.uasset
         │  │  │  │  │      A_WalkForwardRight.uasset
         │  │  │  │  │      A_WalkRight.uasset
         │  │  │  │  │
         │  │  │  │  ├─SpecialAttack
         │  │  │  │  │      AM_SpecialAttack.uasset
         │  │  │  │  │      A_SpecialAttack.uasset
         │  │  │  │  │
         │  │  │  │  └─Thrust
         │  │  │  │          AM_ThrustAttack.uasset
         │  │  │  │
         │  │  │  ├─Horse
         │  │  │  │      AM_CharHorse_Off.uasset
         │  │  │  │      AM_CharHorse_On.uasset
         │  │  │  │      A_CharHorse_Idle.uasset
         │  │  │  │      A_CharHorse_Off.uasset
         │  │  │  │      A_CharHorse_On.uasset
         │  │  │  │      A_CharHorse_Run.uasset
         │  │  │  │      A_CharHorse_Walk.uasset
         │  │  │  │      BS_CharHorse.uasset
         │  │  │  │
         │  │  │  ├─Magic
         │  │  │  │      AM_SpellEnd.uasset
         │  │  │  │      AM_SpellStart.uasset
         │  │  │  │      A_PrepareSpell.uasset
         │  │  │  │      A_SpellEnd.uasset
         │  │  │  │      A_SpellLoop.uasset
         │  │  │  │      A_SpellStart.uasset
         │  │  │  │
         │  │  │  ├─Other
         │  │  │  │  │  ABP_mainRPG.uasset
         │  │  │  │  │  AM_HandsBack.uasset
         │  │  │  │  │  A_Crossbow.uasset
         │  │  │  │  │  A_JumpEnd.uasset
         │  │  │  │  │  A_JumpLoop.uasset
         │  │  │  │  │  A_JumpStart.uasset
         │  │  │  │  │  A_Torch.uasset
         │  │  │  │  │  A_TP_Idle_1.uasset
         │  │  │  │  │  BS_NoWeapon.uasset
         │  │  │  │  │  BS_Weapon.uasset
         │  │  │  │  │
         │  │  │  │  ├─NoWeapon
         │  │  │  │  │      A_NoWeapon_HandsBack.uasset
         │  │  │  │  │      A_NoWeapon_Idle.uasset
         │  │  │  │  │      A_NoWeapon_RunBack.uasset
         │  │  │  │  │      A_NoWeapon_RunBackLeft.uasset
         │  │  │  │  │      A_NoWeapon_RunBackRight.uasset
         │  │  │  │  │      A_NoWeapon_RunBackward.uasset
         │  │  │  │  │      A_NoWeapon_RunForward.uasset
         │  │  │  │  │      A_NoWeapon_RunLeft.uasset
         │  │  │  │  │      A_NoWeapon_RunRight.uasset
         │  │  │  │  │      A_NoWeapon_WalkBackLeft.uasset
         │  │  │  │  │      A_NoWeapon_WalkBackRight.uasset
         │  │  │  │  │      A_NoWeapon_WalkForward.uasset
         │  │  │  │  │      A_NoWeapon_WalkLeft.uasset
         │  │  │  │  │      A_NoWeapon_WalkRight.uasset
         │  │  │  │  │
         │  │  │  │  └─Parry
         │  │  │  │          AM_ParryAttack.uasset
         │  │  │  │          A_ParryAttack.uasset
         │  │  │  │
         │  │  │  └─Swimming
         │  │  │          A_Swim_Forward.uasset
         │  │  │          A_Swim_Idle.uasset
         │  │  │          BS_Swim.uasset
         │  │  │
         │  │  └─Character
         │  │      ├─Materials
         │  │      │  │  M_UE4Man_Body.uasset
         │  │      │  │  M_UE4Man_ChestLogo.uasset
         │  │      │  │
         │  │      │  ├─Alchemyst
         │  │      │  │      MI_LogoAlchemyst.uasset
         │  │      │  │      M_Alchem.uasset
         │  │      │  │
         │  │      │  ├─MaterialLayers
         │  │      │  │      ML_GlossyBlack_Latex_UE4.uasset
         │  │      │  │      ML_Plastic_Shiny_Beige.uasset
         │  │      │  │      ML_Plastic_Shiny_Beige_LOGO.uasset
         │  │      │  │      ML_SoftMetal_UE4.uasset
         │  │      │  │      T_ML_Aluminum01.uasset
         │  │      │  │      T_ML_Aluminum01_N.uasset
         │  │      │  │      T_ML_Rubber_Blue_01_D.uasset
         │  │      │  │      T_ML_Rubber_Blue_01_N.uasset
         │  │      │  │
         │  │      │  ├─OldHouse
         │  │      │  │      MI_LogoAlchemyst.uasset
         │  │      │  │      M_Alchem.uasset
         │  │      │  │
         │  │      │  └─Thieves
         │  │      │          M_UE4_Thieves_Body.uasset
         │  │      │          M_UE4_Thieves_Chest.uasset
         │  │      │
         │  │      ├─Mesh
         │  │      │      SK_Mannequin.uasset
         │  │      │      SK_Mannequin_PhysicsAsset.uasset
         │  │      │      UE4_Mannequin_Skeleton.uasset
         │  │      │
         │  │      └─Textures
         │  │              T_UE4Man_Logo_N.uasset
         │  │              T_UE4_LOGO_CARD.uasset
         │  │              T_UE4_Mannequin_MAT_MASKA.uasset
         │  │              T_UE4_Mannequin__normals.uasset
         │  │
         │  ├─Maps
         │  │  │  L_MainLevel.umap
         │  │  │
         │  │  └─L_MainLevel_0_sharedassets
         │  │          Dirt_LayerInfo.uasset
         │  │          GrassDry_LayerInfo.uasset
         │  │          GrassLush_LayerInfo.uasset
         │  │          Rock_LayerInfo.uasset
         │  │
         │  ├─Materials
         │  │  │  M_Bag_00.uasset
         │  │  │  M_Bark.uasset
         │  │  │  M_black.uasset
         │  │  │  M_Body.uasset
         │  │  │  M_CasualArmorMetal.uasset
         │  │  │  M_CubeMaterial.uasset
         │  │  │  M_Cursor_Decal.uasset
         │  │  │  M_DarkMetal.uasset
         │  │  │  M_Eye.uasset
         │  │  │  M_GrayColor.uasset
         │  │  │  M_GreenLeaves.uasset
         │  │  │  M_HorseTexture.uasset
         │  │  │  M_lambert1.uasset
         │  │  │  M_Lock.uasset
         │  │  │  M_Log.uasset
         │  │  │  M_Minimap.uasset
         │  │  │  M_ProjectilePrediction.uasset
         │  │  │  M_RenderLock.uasset
         │  │  │  M_SliteWood.uasset
         │  │  │  M_smoke_subUV_2.uasset
         │  │  │  M_Tools.uasset
         │  │  │  M_treasure_chest1.uasset
         │  │  │  M_WoodColor.uasset
         │  │  │
         │  │  ├─Arrow
         │  │  │      M_PointColor.uasset
         │  │  │      M_Wings.uasset
         │  │  │      M_WoodLit.uasset
         │  │  │
         │  │  ├─Bombs
         │  │  │      M_FireBomb.uasset
         │  │  │      M_FrostBomb.uasset
         │  │  │      M_GoldBag.uasset
         │  │  │
         │  │  ├─Circle
         │  │  │      MI_CircleEffect.uasset
         │  │  │      MI_ProgressCircle.uasset
         │  │  │      M_ProgressCircle.uasset
         │  │  │
         │  │  ├─Dissolve
         │  │  │      M_DissolveEffect.uasset
         │  │  │      T_Noise_2.uasset
         │  │  │
         │  │  ├─Footsteps
         │  │  │      M_Horsesteps.uasset
         │  │  │
         │  │  ├─Juvelery
         │  │  │      MI_AmuletArmor.uasset
         │  │  │      MI_AmuletEnergy.uasset
         │  │  │      MI_AmuletHealth.uasset
         │  │  │      MI_EmeraldRing.uasset
         │  │  │      MI_GoldenRing.uasset
         │  │  │      M_AmuletMaterial.uasset
         │  │  │      M_RingMaterial.uasset
         │  │  │
         │  │  ├─Physics
         │  │  │      PM_Grass.uasset
         │  │  │      PM_Stone.uasset
         │  │  │      PM_Water.uasset
         │  │  │      PM_Wood.uasset
         │  │  │
         │  │  ├─Sky
         │  │  │      MC_SkysphereMain.uasset
         │  │  │      MF_DissolveSS.uasset
         │  │  │      MF_WaveAnimation.uasset
         │  │  │      MF_ZColor.uasset
         │  │  │      M_CasualStar.uasset
         │  │  │      M_CloudsSphere.uasset
         │  │  │      M_Sky_Panning_Clouds2.uasset
         │  │  │
         │  │  ├─Stones
         │  │  │      MI_Stone_11.uasset
         │  │  │      MI_Stone_4.uasset
         │  │  │      M_Stones.uasset
         │  │  │
         │  │  └─Water
         │  │          M_Water.uasset
         │  │          M_WaterPP.uasset
         │  │
         │  ├─Meshes
         │  │  │  SM_Sphere.uasset
         │  │  │
         │  │  ├─Armor
         │  │  │  ├─ArmorBody_0
         │  │  │  │      SM_ArmorBody.uasset
         │  │  │  │
         │  │  │  ├─ArmoredHandes_0
         │  │  │  │      SM_Hand.uasset
         │  │  │  │
         │  │  │  ├─Armored_Legs
         │  │  │  │      SM_ArmoredLeg_1.uasset
         │  │  │  │
         │  │  │  ├─Armored_Legs_2
         │  │  │  │      SM_ArmoredLeg.uasset
         │  │  │  │
         │  │  │  ├─Arm_Body_3
         │  │  │  │      SM_ArmorBody_1.uasset
         │  │  │  │
         │  │  │  ├─Axe
         │  │  │  ├─Crossbow
         │  │  │  │  │  SM_Crossbow.uasset
         │  │  │  │  │
         │  │  │  │  └─Arrow
         │  │  │  │          SM_Arrow.uasset
         │  │  │  │
         │  │  │  ├─Halmet
         │  │  │  │      SM_Halmet.uasset
         │  │  │  │
         │  │  │  └─Sword
         │  │  ├─Bags
         │  │  │  ├─Bag1
         │  │  │  │      SM_Bag_02.uasset
         │  │  │  │
         │  │  │  └─Bag2
         │  │  │          SM_Treasure.uasset
         │  │  │
         │  │  ├─Clouds
         │  │  │      SM_CloudsSphere.uasset
         │  │  │
         │  │  ├─Eagle
         │  │  │      SM_Crow.uasset
         │  │  │
         │  │  ├─Fire
         │  │  │      SM_Log.uasset
         │  │  │
         │  │  ├─Geometry
         │  │  │      SM_Cube.uasset
         │  │  │
         │  │  ├─Juvelery
         │  │  │  ├─Amulets
         │  │  │  │      SM_Amulet_Armor.uasset
         │  │  │  │      SM_Amulet_Energy.uasset
         │  │  │  │      SM_Amulet_Health.uasset
         │  │  │  │
         │  │  │  └─Rings
         │  │  │          SM_EmeraldRing.uasset
         │  │  │          SM_GoldenRing.uasset
         │  │  │
         │  │  ├─Lock
         │  │  │      SM_Door_Lock.uasset
         │  │  │      SM_Lockpick.uasset
         │  │  │      SM_RotTool.uasset
         │  │  │
         │  │  ├─StoneGem
         │  │  │  ├─Stones_1
         │  │  │  │      SM_Stone_2.uasset
         │  │  │  │
         │  │  │  └─Stones_4
         │  │  ├─Torch
         │  │  │      SM_Torch.uasset
         │  │  │
         │  │  ├─Tree
         │  │  │      SM_Fir_Tree.uasset
         │  │  │
         │  │  └─Weapon
         │  │          SK_Axe.uasset
         │  │          SK_Axe_Skeletal.uasset
         │  │          SK_Axy_Physics.uasset
         │  │          SK_Sword.uasset
         │  │          SK_Sword_Physics.uasset
         │  │          SK_Sword_Skeletal.uasset
         │  │
         │  ├─Particles
         │  │  ├─Materials
         │  │  │  │  MF_ky_UVcontrol_4x4.uasset
         │  │  │  │  M_attentuation_sphere_01.uasset
         │  │  │  │  M_blob.uasset
         │  │  │  │  M_BloodDecal.uasset
         │  │  │  │  M_cloudRadial.uasset
         │  │  │  │  M_Diamond.uasset
         │  │  │  │  M_Fire.uasset
         │  │  │  │  M_FireBall.uasset
         │  │  │  │  M_Fire_SubUV.uasset
         │  │  │  │  M_FootstepParticle.uasset
         │  │  │  │  M_Heat_Distortion.uasset
         │  │  │  │  M_impact_splash_subUV.uasset
         │  │  │  │  M_ky_dust01_4x4.uasset
         │  │  │  │  M_ky_dustLine02.uasset
         │  │  │  │  M_ky_magicCircle03_4x4.uasset
         │  │  │  │  M_ky_magicCircle03_symbol.uasset
         │  │  │  │  M_Portal.uasset
         │  │  │  │  M_Radial_Gradient.uasset
         │  │  │  │  M_radial_ramp.uasset
         │  │  │  │  M_Single_Master.uasset
         │  │  │  │  M_Smoke.uasset
         │  │  │  │
         │  │  │  └─Meteor
         │  │  │          M_LittleRock.uasset
         │  │  │          M_Smoke.uasset
         │  │  │
         │  │  ├─Meshes
         │  │  │      SM_Atcapsule.uasset
         │  │  │
         │  │  ├─ParticleSystems
         │  │  │  │  NS_Attenuation.uasset
         │  │  │  │  NS_ExplosionM.uasset
         │  │  │  │  NS_FallingStar.uasset
         │  │  │  │  NS_Fire.uasset
         │  │  │  │  NS_Fireball.uasset
         │  │  │  │  NS_Imp_Metal.uasset
         │  │  │  │  NS_ky_circle1.uasset
         │  │  │  │  NS_PortalParticle.uasset
         │  │  │  │  NS_Sparks_Impact.uasset
         │  │  │  │
         │  │  │  ├─BodyEffects
         │  │  │  │      NS_BodyFire.uasset
         │  │  │  │      NS_BodyPotion.uasset
         │  │  │  │      NS_body_bullet_impact.uasset
         │  │  │  │
         │  │  │  └─Footsteps
         │  │  │          NS_FootstepDirt.uasset
         │  │  │          NS_FootstepStone.uasset
         │  │  │
         │  │  └─Textures
         │  │      │  T_Blast.uasset
         │  │      │  T_Caustics_2.uasset
         │  │      │  T_CloudPerlin.uasset
         │  │      │  T_ky_dust01_4x4.uasset
         │  │      │  T_ky_magicCircle03_4x4.uasset
         │  │      │  T_ky_magicCircle03_deco.uasset
         │  │      │  T_ky_maskRGB3.uasset
         │  │      │  T_ky_noise14.uasset
         │  │      │  T_ky_noise6.uasset
         │  │      │  T_Smoke2_Tile.uasset
         │  │      │  T_Smoke_Tile_01.uasset
         │  │      │  T_Soft_Smoke2_Dup.uasset
         │  │      │  T_SparkSingle.uasset
         │  │      │
         │  │      ├─Blood
         │  │      │      T_blood_various.uasset
         │  │      │      T_blood_various_N.uasset
         │  │      │      T_Splatters.uasset
         │  │      │      T_water_nrm.uasset
         │  │      │
         │  │      └─Meteor
         │  │              T_FireSheet.uasset
         │  │              T_Stone.uasset
         │  │              T_Stone_Normal.uasset
         │  │
         │  ├─Sounds
         │  │  │  SC_Fire01_Cue.uasset
         │  │  │  S_Blow.uasset
         │  │  │  S_Boiling.uasset
         │  │  │  S_Fire01.uasset
         │  │  │  S_fire2.uasset
         │  │  │  S_Horsewhish.uasset
         │  │  │  S_SpellWind.uasset
         │  │  │  S_Thunder___Sound_effect.uasset
         │  │  │
         │  │  ├─Crossbow
         │  │  │      SC_Shoot.uasset
         │  │  │      S_shoot_1.uasset
         │  │  │      S_shoot_2.uasset
         │  │  │      S_shoot_3.uasset
         │  │  │
         │  │  ├─Dialogues
         │  │  │  │  SA_CasualSmalltalk.uasset
         │  │  │  │  SA_Combat.uasset
         │  │  │  │
         │  │  │  ├─Alchemy
         │  │  │  │      S_CameBack.uasset
         │  │  │  │      S_GladToSeeYou.uasset
         │  │  │  │      S_GoodBye.uasset
         │  │  │  │      S_Hi___.uasset
         │  │  │  │
         │  │  │  ├─AngryCit
         │  │  │  │      SC_Back.uasset
         │  │  │  │      SC_Back_2.uasset
         │  │  │  │      SC_Hey.uasset
         │  │  │  │      S_BackOff_1.uasset
         │  │  │  │      S_BackOff_2.uasset
         │  │  │  │      S_Hey.uasset
         │  │  │  │
         │  │  │  ├─FindBrother
         │  │  │  │  │  S_BringHimBack.uasset
         │  │  │  │  │  S_CantFindBrother.uasset
         │  │  │  │  │  S_CantHelp.uasset
         │  │  │  │  │  S_FindMeInOldHOuse.uasset
         │  │  │  │  │  S_Fine.uasset
         │  │  │  │  │  S_HeCouldGetProblems.uasset
         │  │  │  │  │  S_IWillFindBrother.uasset
         │  │  │  │  │  S_OKListening.uasset
         │  │  │  │  │  S_PleaseINeedYourHelp.uasset
         │  │  │  │  │  S_ThankYou.uasset
         │  │  │  │  │  S_Too_busy.uasset
         │  │  │  │  │
         │  │  │  │  ├─Borther_2
         │  │  │  │  │      SC_IThought.uasset
         │  │  │  │  │      SC_ThankYou.uasset
         │  │  │  │  │      S_BrothcerWasCought.uasset
         │  │  │  │  │      S_HeWasCought.uasset
         │  │  │  │  │      S_IThought.uasset
         │  │  │  │  │      S_MyFriend.uasset
         │  │  │  │  │      S_ThankYou.uasset
         │  │  │  │  │      S_TheyDidACamp.uasset
         │  │  │  │  │      S_YoucanFindHim.uasset
         │  │  │  │  │
         │  │  │  │  └─FindAlchemyst
         │  │  │  │          S_THeGuyFromOldHouse.uasset
         │  │  │  │          S_WhereShouldISearch.uasset
         │  │  │  │
         │  │  │  ├─Hello
         │  │  │  │      SC_Hello.uasset
         │  │  │  │      S_Hello_0.uasset
         │  │  │  │
         │  │  │  ├─Neckle
         │  │  │  │      S_Alright_Voice.uasset
         │  │  │  │      S_CanYouBring.uasset
         │  │  │  │      S_DidntFind.uasset
         │  │  │  │      S_DidYouFind.uasset
         │  │  │  │      S_HereYougo.uasset
         │  │  │  │      S_ICant.uasset
         │  │  │  │      S_ISee.uasset
         │  │  │  │      S_IThinkIHaveLeft.uasset
         │  │  │  │      S_IWillWait.uasset
         │  │  │  │      S_LostNeckle.uasset
         │  │  │  │      S_OfCourse.uasset
         │  │  │  │      S_Reward_2.uasset
         │  │  │  │      S_ThankYou.uasset
         │  │  │  │
         │  │  │  ├─Nice
         │  │  │  │  └─NiceCit
         │  │  │  │          SC_Hi.uasset
         │  │  │  │          SC_What_0.uasset
         │  │  │  │          SC_What_1.uasset
         │  │  │  │          SC_What_2.uasset
         │  │  │  │          S_hi__.uasset
         │  │  │  │          S_Waht_.uasset
         │  │  │  │          S_Waht__.uasset
         │  │  │  │          S_What.uasset
         │  │  │  │
         │  │  │  └─Thieves
         │  │  │          S_CantHelp.uasset
         │  │  │          S_ISaw.uasset
         │  │  │          S_IWillKillThem.uasset
         │  │  │          S_Reward.uasset
         │  │  │          S_WeHaveALot.uasset
         │  │  │          S_WillUHelp.uasset
         │  │  │
         │  │  ├─Drop
         │  │  │      SC_CasualDropStep.uasset
         │  │  │      SC_LeavesDrop.uasset
         │  │  │      S_Drop_0.uasset
         │  │  │      S_Drop_1.uasset
         │  │  │      S_LeavesDrop_0.uasset
         │  │  │      S_LeavesDrop_1.uasset
         │  │  │
         │  │  ├─Eagle
         │  │  │      SC_Flap.uasset
         │  │  │      S_EagleFlap1_Wav.uasset
         │  │  │      S_EagleFlap2_Wav.uasset
         │  │  │
         │  │  ├─Eat
         │  │  │      S_drink.uasset
         │  │  │      S_eat.uasset
         │  │  │
         │  │  ├─GUI
         │  │  │      S_Click_Wav.uasset
         │  │  │      S_Hovered_Wav.uasset
         │  │  │
         │  │  ├─InteractActor
         │  │  │      SC_Check.uasset
         │  │  │      SC_Chest.uasset
         │  │  │      SC_Take.uasset
         │  │  │      S_Check2_Wav.uasset
         │  │  │      S_Chest_Wav.uasset
         │  │  │      S_Take_Wav.uasset
         │  │  │
         │  │  ├─Inventory
         │  │  │      SC_BookInventory.uasset
         │  │  │      SC_Bottle.uasset
         │  │  │      SC_MetalInventory.uasset
         │  │  │      SC_PutInventory.uasset
         │  │  │      SC_TakeStone.uasset
         │  │  │      SC_WeaponInventory.uasset
         │  │  │      S_Book.uasset
         │  │  │      S_Bottle.uasset
         │  │  │      S_Clothes.uasset
         │  │  │      S_Metal.uasset
         │  │  │      S_Money.uasset
         │  │  │      S_OpenInventory.uasset
         │  │  │      S_PutSound.uasset
         │  │  │      S_Ring.uasset
         │  │  │      S_TakeStone.uasset
         │  │  │
         │  │  ├─Metal
         │  │  │      SC_Metal.uasset
         │  │  │      S_Metal_0.uasset
         │  │  │      S_Metal_2.uasset
         │  │  │      S_Metal_3.uasset
         │  │  │      S_Metal_4.uasset
         │  │  │      S_Metal_5.uasset
         │  │  │      S_Metal_6.uasset
         │  │  │      S_Metal_7.uasset
         │  │  │
         │  │  ├─Other
         │  │  │      SC_Nature.uasset
         │  │  │      S_Birds_Wav.uasset
         │  │  │      S_Wind1_Wav.uasset
         │  │  │      S_Wind2_Wav.uasset
         │  │  │
         │  │  ├─Portal
         │  │  │      SC_Portal.uasset
         │  │  │      S_Portal.uasset
         │  │  │
         │  │  ├─Steps
         │  │  │  ├─Beton
         │  │  │  │      SC_Gravel.uasset
         │  │  │  │      S_Gravel_0.uasset
         │  │  │  │      S_Gravel_1.uasset
         │  │  │  │      S_Gravel_2.uasset
         │  │  │  │      S_Gravel_3.uasset
         │  │  │  │
         │  │  │  ├─Horse
         │  │  │  │      SC_HorseSteps.uasset
         │  │  │  │      S_HorseStep_0.uasset
         │  │  │  │      S_HorseStep_1.uasset
         │  │  │  │      S_HorseStep_10.uasset
         │  │  │  │      S_HorseStep_2.uasset
         │  │  │  │      S_HorseStep_3.uasset
         │  │  │  │      S_HorseStep_4.uasset
         │  │  │  │      S_HorseStep_5.uasset
         │  │  │  │      S_HorseStep_6.uasset
         │  │  │  │      S_HorseStep_7.uasset
         │  │  │  │      S_HorseStep_8.uasset
         │  │  │  │      S_HorseStep_9.uasset
         │  │  │  │
         │  │  │  ├─Plate
         │  │  │  │      SC_Casual_Step.uasset
         │  │  │  │      S_Casual_Step_0.uasset
         │  │  │  │      S_Casual_Step_1.uasset
         │  │  │  │      S_Casual_Step_2.uasset
         │  │  │  │      S_Casual_Step_3.uasset
         │  │  │  │      S_Casual_Step_4.uasset
         │  │  │  │
         │  │  │  ├─Puddle
         │  │  │  │      SC_Water.uasset
         │  │  │  │      S_Water1_Wav.uasset
         │  │  │  │      S_Water2_Wav.uasset
         │  │  │  │
         │  │  │  └─Wood
         │  │  │          SC_WoodCue.uasset
         │  │  │          S_WoodStep_0.uasset
         │  │  │          S_WoodStep_1.uasset
         │  │  │          S_WoodStep_2.uasset
         │  │  │          S_WoodStep_3.uasset
         │  │  │          S_WoodStep_4.uasset
         │  │  │
         │  │  ├─Sword
         │  │  │  │  SC_BodyHit.uasset
         │  │  │  │  SC_SwordHit.uasset
         │  │  │  │  SC_SwordSwing.uasset
         │  │  │  │  S_BackWeapon.uasset
         │  │  │  │  S_Sw_Body_01.uasset
         │  │  │  │  S_Sw_Body_02.uasset
         │  │  │  │  S_Sw_Body_03.uasset
         │  │  │  │  S_Sw_Sw_01.uasset
         │  │  │  │  S_Sw_Sw_02.uasset
         │  │  │  │  S_Sw_Sw_03.uasset
         │  │  │  │  S_Sw_Sw_04.uasset
         │  │  │  │  S_TakeWeapon.uasset
         │  │  │  │
         │  │  │  └─Whoosh
         │  │  │          S_Whoosh_1.uasset
         │  │  │          S_Whoosh_2.uasset
         │  │  │          S_Whoosh_3.uasset
         │  │  │          S_Whoosh_4.uasset
         │  │  │          S_Whoosh_5.uasset
         │  │  │
         │  │  ├─Water
         │  │  │      MSC_Water.uasset
         │  │  │      SC_Underwater_Cue.uasset
         │  │  │      S_Underwater.uasset
         │  │  │
         │  │  └─Whoosh
         │  │          SC_WhooshObs_.uasset
         │  │          SC_WhooshTime.uasset
         │  │          S_Whoosh1_Wav.uasset
         │  │          S_WhooshObs_Wav.uasset
         │  │          S_WhooshTime_Wav.uasset
         │  │
         │  ├─StarterContent
         │  │  ├─Materials
         │  │  │      M_Rock.uasset
         │  │  │
         │  │  ├─Props
         │  │  │      SM_Rock.uasset
         │  │  │
         │  │  └─Textures
         │  │          T_Detail_Rocky_N.uasset
         │  │          T_Fire_SubUV.uasset
         │  │          T_Ground_Gravel_D.uasset
         │  │          T_Ground_Gravel_N.uasset
         │  │          T_RockMesh_M.uasset
         │  │          T_RockMesh_N.uasset
         │  │          T_Rock_Basalt_D.uasset
         │  │          T_Rock_Basalt_N.uasset
         │  │          T_Smoke_SubUV.uasset
         │  │
         │  ├─Textures
         │  │  │  T_Burst_M.uasset
         │  │  │  T_Dissolve.uasset
         │  │  │  T_Explosion_SubUV.uasset
         │  │  │  T_Fire_SubUV.uasset
         │  │  │  T_Fire_Tiled_D.uasset
         │  │  │  T_HeatrRed.uasset
         │  │  │  T_Horse.uasset
         │  │  │  T_Log.uasset
         │  │  │  T_Log_Normal.uasset
         │  │  │  T_Perlin_Noise_BC.uasset
         │  │  │  T_seamless-ice-snow-normal-mapping_640v640.uasset
         │  │  │  T_Smoke_SubUV.uasset
         │  │  │  T_Smoke_Tiled_D.uasset
         │  │  │  T_TorchDown.uasset
         │  │  │  T_TorchIcon.uasset
         │  │  │  T_treasure_chest.uasset
         │  │  │  T_Water.uasset
         │  │  │  T_Water_N.uasset
         │  │  │
         │  │  ├─Footsteps
         │  │  │      T_HorsestepNormal.uasset
         │  │  │      T_HorsestepsHighmap.uasset
         │  │  │
         │  │  ├─Sky
         │  │  │      T_CloudsMain_0.uasset
         │  │  │      T_CloudsMain_1.uasset
         │  │  │      T_FallStar.uasset
         │  │  │      T_SkyCloudNormal.uasset
         │  │  │      T_SkyCloudNorm_1.uasset
         │  │  │      T_Sky_Clouds.uasset
         │  │  │      T_Sky_Clouds_M.uasset
         │  │  │      T_Sky_Stars.uasset
         │  │  │
         │  │  └─StoneGems
         │  │          T_BaseColor_Stone_1.uasset
         │  │          T_BaseColor_Stone_4.uasset
         │  │          T_Normal_Stone_1.uasset
         │  │          T_Normal_Stone_4.uasset
         │  │          T_Specular_Stone_1.uasset
         │  │          T_Spec_Stone_4.uasset
         │  │
         │  └─UI
         │      ├─Textures
         │      │  │  T_Aim.uasset
         │      │  │  T_AlchemyBackground.uasset
         │      │  │  T_AppleIcon.uasset
         │      │  │  T_ArrowUP.uasset
         │      │  │  T_Book.uasset
         │      │  │  T_Corned_0.uasset
         │      │  │  T_CornersAlpha.uasset
         │      │  │  T_Croner_1.uasset
         │      │  │  T_DarkEffect.uasset
         │      │  │  T_DownUpFade.uasset
         │      │  │  T_ExclamationSign.uasset
         │      │  │  T_GammaSettings.uasset
         │      │  │  T_GammaTexture.uasset
         │      │  │  T_GemBackground.uasset
         │      │  │  T_Grass_Alpha.uasset
         │      │  │  T_Grass_noAlpha.uasset
         │      │  │  T_HotbarsBack.uasset
         │      │  │  T_Hummer.uasset
         │      │  │  T_Knight.uasset
         │      │  │  T_loadingBackground.uasset
         │      │  │  T_MenuBackground.uasset
         │      │  │  T_NoiseMap.uasset
         │      │  │  T_QuestionMark.uasset
         │      │  │  T_RightLeftFade.uasset
         │      │  │  T_RubbishHand.uasset
         │      │  │  T_Scull_2.uasset
         │      │  │  T_Smoke.uasset
         │      │  │  T_StarKeyboard.uasset
         │      │  │  T_VillageArea.uasset
         │      │  │
         │      │  ├─Arrows
         │      │  │      T_Arrow_Big.uasset
         │      │  │      T_Arrow_Small.uasset
         │      │  │      T_CircleMask.uasset
         │      │  │
         │      │  ├─Compass
         │      │  │      T_ArrowC.uasset
         │      │  │      T_CombasBackground.uasset
         │      │  │      T_Compass_Objective.uasset
         │      │  │      T_Compass_Points.uasset
         │      │  │      T_PlaceCheck.uasset
         │      │  │      T_Player.uasset
         │      │  │      T_Triangle.uasset
         │      │  │
         │      │  ├─DayNight
         │      │  │      T_CircleTime.uasset
         │      │  │      T_DayNight.uasset
         │      │  │      T_Moon.uasset
         │      │  │      T_NightDay.uasset
         │      │  │      T_Sun.uasset
         │      │  │
         │      │  ├─Eagle
         │      │  │      T_circle.uasset
         │      │  │
         │      │  ├─Emblems
         │      │  │      T_Area_00.uasset
         │      │  │      T_Area_01.uasset
         │      │  │      T_Area_02.uasset
         │      │  │
         │      │  ├─Gems
         │      │  │      T_ModificationGem__10_.uasset
         │      │  │      T_ModificationGem__11_.uasset
         │      │  │      T_ModificationGem__12_.uasset
         │      │  │      T_ModificationGem__13_.uasset
         │      │  │      T_ModificationGem__14_.uasset
         │      │  │      T_ModificationGem__15_.uasset
         │      │  │      T_ModificationGem__16_.uasset
         │      │  │      T_ModificationGem__17_.uasset
         │      │  │      T_ModificationGem__18_.uasset
         │      │  │      T_ModificationGem__19_.uasset
         │      │  │      T_ModificationGem__1_.uasset
         │      │  │      T_ModificationGem__20_.uasset
         │      │  │      T_ModificationGem__21_.uasset
         │      │  │      T_ModificationGem__2_.uasset
         │      │  │      T_ModificationGem__3_.uasset
         │      │  │      T_ModificationGem__4_.uasset
         │      │  │      T_ModificationGem__5_.uasset
         │      │  │      T_ModificationGem__6_.uasset
         │      │  │      T_ModificationGem__7_.uasset
         │      │  │      T_ModificationGem__8_.uasset
         │      │  │      T_ModificationGem__9_.uasset
         │      │  │
         │      │  ├─Glossary
         │      │  │  ├─Books
         │      │  │  │      T_Book_0.uasset
         │      │  │  │      T_Book_1.uasset
         │      │  │  │      T_Book_2.uasset
         │      │  │  │      T_Book_3.uasset
         │      │  │  │
         │      │  │  ├─Characters
         │      │  │  │  └─ColoredMesh
         │      │  │  │      │  T_Character_1_Full.uasset
         │      │  │  │      │  T_Character_2_Full.uasset
         │      │  │  │      │  T_Character_3_Full.uasset
         │      │  │  │      │  T_Character_4_Full.uasset
         │      │  │  │      │  T_Character_5_Full.uasset
         │      │  │  │      │  T_Character_6_Full.uasset
         │      │  │  │      │  T_Character_7_Full.uasset
         │      │  │  │      │  T_Character_8_Full.uasset
         │      │  │  │      │
         │      │  │  │      └─Parts
         │      │  │  │              T_Character_1_Part.uasset
         │      │  │  │              T_Character_2_Part.uasset
         │      │  │  │              T_Character_3_Part.uasset
         │      │  │  │              T_Character_4_Part.uasset
         │      │  │  │              T_Character_5_Part.uasset
         │      │  │  │              T_Character_6_Part.uasset
         │      │  │  │              T_Character_7_Part.uasset
         │      │  │  │              T_Character_8_Part.uasset
         │      │  │  │
         │      │  │  └─Creatures
         │      │  │          T_InfoIconCreature.uasset
         │      │  │
         │      │  ├─InventorySlots
         │      │  │      T_AlchemyType.uasset
         │      │  │      T_OtherType.uasset
         │      │  │      T_ShieldBackground.uasset
         │      │  │      T_TasksType.uasset
         │      │  │
         │      │  ├─Item
         │      │  │  │  T_armor-vest.uasset
         │      │  │  │  T_Circle.uasset
         │      │  │  │  T_Neckle.uasset
         │      │  │  │  T_sword-hilt.uasset
         │      │  │  │
         │      │  │  ├─Armor
         │      │  │  │      T_Body.uasset
         │      │  │  │      T_Body_Background.uasset
         │      │  │  │      T_Body_Light.uasset
         │      │  │  │      T_Graves_0.uasset
         │      │  │  │      T_Greaves.uasset
         │      │  │  │      T_Halmet_Background.uasset
         │      │  │  │      T_hand_1.uasset
         │      │  │  │      T_Helmet.uasset
         │      │  │  │
         │      │  │  ├─Bombs
         │      │  │  │      T_Bomb_1.uasset
         │      │  │  │      T_Bomb_2.uasset
         │      │  │  │      T_Bomb_3.uasset
         │      │  │  │
         │      │  │  ├─Bottles
         │      │  │  │      T_DirtyWater.uasset
         │      │  │  │      T_EmptyBottle.uasset
         │      │  │  │      T_EnergyBottle.uasset
         │      │  │  │      T_HealthBottle.uasset
         │      │  │  │      T_Meat.uasset
         │      │  │  │      T_MetalBar.uasset
         │      │  │  │      T_MetalOre.uasset
         │      │  │  │      T_RawMeat.uasset
         │      │  │  │      T_Rose.uasset
         │      │  │  │      T_Sand.uasset
         │      │  │  │      T_Stick.uasset
         │      │  │  │      T_tulip.uasset
         │      │  │  │      T_Water.uasset
         │      │  │  │
         │      │  │  ├─Juwelery
         │      │  │  │      T_Bag.uasset
         │      │  │  │      T_Bag_Background.uasset
         │      │  │  │      T_neckleBackground.uasset
         │      │  │  │      T_Neckle_1.uasset
         │      │  │  │      T_neckle_2.uasset
         │      │  │  │      T_neckle_3.uasset
         │      │  │  │      T_RingBackground.uasset
         │      │  │  │      T_RingEmerald.uasset
         │      │  │  │      T_RingNull.uasset
         │      │  │  │
         │      │  │  └─Weapon
         │      │  │          T_ArrowBackground.uasset
         │      │  │          T_Arrows.uasset
         │      │  │          T_Axe.uasset
         │      │  │          T_Crossbow.uasset
         │      │  │          T_Crossbow_Background.uasset
         │      │  │          T_Greaves_Background.uasset
         │      │  │          T_Sword.uasset
         │      │  │          T_Sword_Background.uasset
         │      │  │
         │      │  ├─Items
         │      │  │      T_Gemstone.uasset
         │      │  │      T_Stone.uasset
         │      │  │      T_Wood.uasset
         │      │  │
         │      │  ├─Lockpick
         │      │  │      T_EscHelp.uasset
         │      │  │      T_MouseMoveIcon.uasset
         │      │  │      T_RenderLock.uasset
         │      │  │
         │      │  ├─MainGameplayGUI
         │      │  │  │  T_Background_Top.uasset
         │      │  │  │  T_LevelUp_2.uasset
         │      │  │  │  T_MainBackground.uasset
         │      │  │  │  T_MenuSlots.uasset
         │      │  │  │  T_Weight.uasset
         │      │  │  │
         │      │  │  └─Stats
         │      │  │          T_Armor.uasset
         │      │  │          T_Energy.uasset
         │      │  │          T_Plus.uasset
         │      │  │          T_Toxicity.uasset
         │      │  │
         │      │  ├─Map
         │      │  │  │  T_cash.uasset
         │      │  │  │  T_cave-entrance.uasset
         │      │  │  │  T_eagle-emblem__2_.uasset
         │      │  │  │  T_eagle-emblem__3_.uasset
         │      │  │  │  T_forest-camp__3_.uasset
         │      │  │  │  T_Marker.uasset
         │      │  │  │  T_QuestionMark_2.uasset
         │      │  │  │  T_river.uasset
         │      │  │  │  T_shield.uasset
         │      │  │  │  T_upgrade.uasset
         │      │  │  │
         │      │  │  ├─MapImages
         │      │  │  │      T_map2.uasset
         │      │  │  │      T_MapPArtDown.uasset
         │      │  │  │      T_MapPartUp.uasset
         │      │  │  │
         │      │  │  └─Minimap
         │      │  │          T_RenderMinimap.uasset
         │      │  │          T_RenderMinimap_1.uasset
         │      │  │          T_RenderMinimap_2.uasset
         │      │  │          T_RenderMinimap_3.uasset
         │      │  │
         │      │  ├─Menu
         │      │  │      T_Color.uasset
         │      │  │
         │      │  ├─Mouse
         │      │  │      T_LMB.uasset
         │      │  │      T_MMB.uasset
         │      │  │      T_RMB.uasset
         │      │  │
         │      │  ├─Quests
         │      │  │      T_ActiveQuest.uasset
         │      │  │      T_Done.uasset
         │      │  │      T_InProgress.uasset
         │      │  │      T_QuestNotActive.uasset
         │      │  │
         │      │  ├─Skills
         │      │  │  │  T_Area.uasset
         │      │  │  │  T_BackgroundSpell.uasset
         │      │  │  │  T_Cost.uasset
         │      │  │  │  T_DNA_first.uasset
         │      │  │  │  T_Energy.uasset
         │      │  │  │  T_FadeCircle.uasset
         │      │  │  │  T_FireSpell.uasset
         │      │  │  │  T_FrostSpell.uasset
         │      │  │  │  T_Health.uasset
         │      │  │  │  T_Impact_Spell.uasset
         │      │  │  │  T_Jog.uasset
         │      │  │  │  T_Overlay_Cue.uasset
         │      │  │  │  T_Person.uasset
         │      │  │  │  T_Power.uasset
         │      │  │  │  T_Run.uasset
         │      │  │  │  T_Signs.uasset
         │      │  │  │  T_Speed.uasset
         │      │  │  │  T_Start.uasset
         │      │  │  │  T_Sword_Selection.uasset
         │      │  │  │  T_Time.uasset
         │      │  │  │  T_Walk.uasset
         │      │  │  │
         │      │  │  └─DNA
         │      │  │          T_DNA_0.uasset
         │      │  │          T_DNA_01.uasset
         │      │  │          T_DNA_1.uasset
         │      │  │          T_DNA_2.uasset
         │      │  │          T_DNA_4.uasset
         │      │  │          T_DNA_5.uasset
         │      │  │          T_DNA_6.uasset
         │      │  │          T_DNA_7.uasset
         │      │  │
         │      │  ├─Tasks
         │      │  │  ├─MapTasks
         │      │  │  │      T_chest__3_.uasset
         │      │  │  │      T_swap-bag.uasset
         │      │  │  │
         │      │  │  └─Quests
         │      │  │          T_hasQuest.uasset
         │      │  │          T_QuestLocked.uasset
         │      │  │          T_QuestPlace.uasset
         │      │  │
         │      │  ├─Tutorial
         │      │  │      T_Craft_Tutorial.uasset
         │      │  │      T_Tutorial_Chest.uasset
         │      │  │      T_Tutorial_Dialogue.uasset
         │      │  │      T_Tutorial_Map.uasset
         │      │  │      T_Tutorial_Quest_1.uasset
         │      │  │      T_Tutorial_Skills.uasset
         │      │  │      T_Tutorial_Spell.uasset
         │      │  │      T_Tutorial_Storage.uasset
         │      │  │
         │      │  ├─UpgradeSlot
         │      │  │      T_ModificationSelected.uasset
         │      │  │      T_Modification_Overlay.uasset
         │      │  │
         │      │  └─WorldActors
         │      │          T_chest__4_.uasset
         │      │          T_locked-chest.uasset
         │      │
         │      └─Widgets
         │          ├─Alchemy
         │          │  │  WB_AlchemyInfo.uasset
         │          │  │  WB_AlchemyInfoWidget.uasset
         │          │  │  WB_AlchemyInvSlot.uasset
         │          │  │  WB_AlchemyNeedSlot.uasset
         │          │  │  WB_AlchemySlot.uasset
         │          │  │  WB_AlchemySlotType.uasset
         │          │  │  WB_AlchemyToolTip.uasset
         │          │  │
         │          │  ├─Alchemyst
         │          │  │      WB_AlchemystInventory.uasset
         │          │  │      WB_AlchemystSell.uasset
         │          │  │
         │          │  └─Crafter
         │          │      │  E_CrafterTypes.uasset
         │          │      │  WB_CrafterWidget.uasset
         │          │      │
         │          │      ├─Fix
         │          │      │      WB_Fix.uasset
         │          │      │
         │          │      ├─Parts
         │          │      │      WB_BreakIntoParts.uasset
         │          │      │      WB_PartSlot.uasset
         │          │      │
         │          │      └─RemoveModification
         │          │              WB_RemoveModification.uasset
         │          │              WB_RemoveModificationSlot.uasset
         │          │
         │          ├─AnnounceScreen
         │          │      WB_NewArea.uasset
         │          │      WB_RewardAnnouncment.uasset
         │          │      WB_RewardsAlert.uasset
         │          │      WB_RewardSlot.uasset
         │          │
         │          ├─Compas
         │          │      E_PlaceCompassLocation.uasset
         │          │      E_ZoneType.uasset
         │          │      WB_Compass.uasset
         │          │      WB_CompassNavSlot.uasset
         │          │
         │          ├─Dialogue
         │          │      WB_CharacterTalkTitleText.uasset
         │          │      WB_CharacterTitleWidget.uasset
         │          │      WB_DialogueOptionSLot.uasset
         │          │      WB_DialogueSlot.uasset
         │          │      WB_MainDialogue.uasset
         │          │      WB_TimerDialogue.uasset
         │          │
         │          ├─Eagle
         │          │      WB_EagleNoAim.uasset
         │          │      WB_EagleVision.uasset
         │          │
         │          ├─Effects
         │          │      WB_EffectSlot.uasset
         │          │      WB_EffectWidget.uasset
         │          │
         │          ├─Glossary
         │          │  ├─Books
         │          │  │      WB_BookInfoWidget.uasset
         │          │  │      WB_BooksInfo.uasset
         │          │  │      WB_BooksSlot.uasset
         │          │  │
         │          │  ├─Characters
         │          │  │      WB_CharacterInfo.uasset
         │          │  │      WB_CharacterInfoSlot.uasset
         │          │  │      WB_CharacterInfoWidget.uasset
         │          │  │
         │          │  ├─Creatures
         │          │  │      WB_CreatureInfo.uasset
         │          │  │      WB_CreatureInfoSlot.uasset
         │          │  │      WB_CreatureInfoWidget.uasset
         │          │  │      WB_CreatureWeaknessSlot.uasset
         │          │  │
         │          │  └─Tutorial
         │          │      │  E_TutorialType.uasset
         │          │      │  WB_TutorialInfo.uasset
         │          │      │  WB_TutorialInfoWidget.uasset
         │          │      │  WB_TutorialSlot.uasset
         │          │      │  WB_TutorialSlotType.uasset
         │          │      │
         │          │      └─Override
         │          │              WB_TutorialChest.uasset
         │          │              WB_TutorialMap.uasset
         │          │              WB_Tutorial_Attack.uasset
         │          │              WB_Tutorial_Craft.uasset
         │          │              WB_Tutorial_Dialogue.uasset
         │          │              WB_Tutorial_Eagle.uasset
         │          │              WB_Tutorial_Horse.uasset
         │          │              WB_Tutorial_Inventory.uasset
         │          │              WB_Tutorial_QUests.uasset
         │          │              WB_Tutorial_Skills.uasset
         │          │              WB_Tutorial_Spells.uasset
         │          │              WB_Tutorial_Storage.uasset
         │          │
         │          ├─InteractItems
         │          │      WB_CheckTheActor.uasset
         │          │      WB_Interact.uasset
         │          │      WB_ItemWorld.uasset
         │          │      WB_ShowObserveObject.uasset
         │          │
         │          ├─Inventory
         │          │  │  WB_Inventory.uasset
         │          │  │  WB_InventorySlot.uasset
         │          │  │  WB_InventoryToolTip.uasset
         │          │  │  WB_InvSlotDragged.uasset
         │          │  │  WB_MoveItem.uasset
         │          │  │  WB_PlayerInventory.uasset
         │          │  │
         │          │  ├─Modification
         │          │  │      WB_ModificationSlot.uasset
         │          │  │
         │          │  ├─MultiplaeItems
         │          │  │      WB_MultipleItems.uasset
         │          │  │      WB_MultipleItemsSlot.uasset
         │          │  │
         │          │  ├─Sort
         │          │  │      WB_InventorySort.uasset
         │          │  │      WB_SortSlot.uasset
         │          │  │
         │          │  ├─Storage
         │          │  │      BP_InventoryStorage.uasset
         │          │  │      WB_InventoryStorage.uasset
         │          │  │
         │          │  └─UpgradeSlot
         │          │          WB_Upgrade.uasset
         │          │
         │          ├─Lockpick
         │          │      WB_Lockpicking.uasset
         │          │
         │          ├─MainGameplayGUI
         │          │      E_TopMenuType.uasset
         │          │      WB_MainTopGUI.uasset
         │          │      WB_TopGUISlot.uasset
         │          │
         │          ├─Menu
         │          │      BP_Save_Settings.uasset
         │          │      WB_Damage.uasset
         │          │      WB_LoadingScreen.uasset
         │          │      WB_MainGameplayMenu.uasset
         │          │      WB_MainGUI.uasset
         │          │      WB_Pause.uasset
         │          │      WB_PeriodicTable.uasset
         │          │      WB_Save.uasset
         │          │
         │          ├─Other
         │          │      WB_BossFight.uasset
         │          │      WB_Crossbow.uasset
         │          │      WB_FadeOut.uasset
         │          │      WB_InBattle.uasset
         │          │      WB_MainPrompt.uasset
         │          │      WB_PlayerAim.uasset
         │          │      WB_Rubbish.uasset
         │          │      WB_SpeedupTime.uasset
         │          │      WB_Welcome.uasset
         │          │
         │          ├─Player
         │          │      WB_AIStats.uasset
         │          │      WB_Death.uasset
         │          │      WB_LevelUp.uasset
         │          │      WB_LockIcon.uasset
         │          │      WB_Player3D.uasset
         │          │      WB_PlayerCharacteristics.uasset
         │          │      WB_PlayerStatsScreen.uasset
         │          │      WB_PlayerView.uasset
         │          │      WB_Tutorial.uasset
         │          │      WB_Water.uasset
         │          │
         │          ├─Quests
         │          │  │  E_QuestAnnounce.uasset
         │          │  │  WB_QuestAnnounce.uasset
         │          │  │  WB_Quests.uasset
         │          │  │  WB_TaskWidget.uasset
         │          │  │
         │          │  └─New
         │          │          DT_QuestColor.uasset
         │          │          E_QuestSubslotState.uasset
         │          │          E_QuestType.uasset
         │          │          S_QuestTypeColor.uasset
         │          │          S_SubtaskActors.uasset
         │          │          S_SubtaskDescription.uasset
         │          │          WB_QuestsInfo.uasset
         │          │          WB_QuestsInfoWidget.uasset
         │          │          WB_QuestSlot.uasset
         │          │          WB_QuestSlotType.uasset
         │          │          WB_QuestSubSlot.uasset
         │          │
         │          ├─RewardAnnounce
         │          │      WB_GotCraft.uasset
         │          │
         │          ├─ScreenFastBinds
         │          │      T_BlackCircle.uasset
         │          │      WB_FastBindSlot.uasset
         │          │      WB_FastBindsWidget.uasset
         │          │
         │          ├─Settings
         │          │  │  WB_Gamma.uasset
         │          │  │  WB_InputKey.uasset
         │          │  │  WB_Settings.uasset
         │          │  │
         │          │  └─Settings
         │          │          BP_SaveProperties.uasset
         │          │          WB_InputWarning.uasset
         │          │
         │          ├─Skills
         │          │  │  WB_SkillDraggable.uasset
         │          │  │  WB_SkillsInfo.uasset
         │          │  │  WB_SkillsTop.uasset
         │          │  │  WB_SkillSubslotSlot.uasset
         │          │  │  WB_SkillTooltip.uasset
         │          │  │  WB_SkillupgradeDrag.uasset
         │          │  │
         │          │  ├─SetSpellsRow
         │          │  │      WB_SpellsRow.uasset
         │          │  │
         │          │  ├─SkillsSetup
         │          │  │      S_TypeUpgrade.uasset
         │          │  │      WB_ReqSkillSlot.uasset
         │          │  │      WB_SkillSetupChunk.uasset
         │          │  │      WB_SkillSetupSlot.uasset
         │          │  │      WB_SkillSetupUpgrade.uasset
         │          │  │      WB_SkillSetupWidget.uasset
         │          │  │
         │          │  └─SkillsSubslot
         │          │          WB_SkillSubslot.uasset
         │          │          WB_TopSkillDraggable.uasset
         │          │          WB_TopSkillSubslot.uasset
         │          │
         │          ├─Spells
         │          │      T_Rad2_circle.uasset
         │          │      T_SpellCircle.uasset
         │          │      WB_SpellsSlot.uasset
         │          │      WB_SpellsWidget.uasset
         │          │
         │          └─WorldMap
         │              │  WB_Legend.uasset
         │              │  WB_Marker.uasset
         │              │  WB_TeleportationPoint.uasset
         │              │  WB_UndescoveredArea.uasset
         │              │  WB_WorldActorWidget.uasset
         │              │  WB_WorldMap.uasset
         │              │
         │              ├─Minimap
         │              │      WB_Minimap.uasset
         │              │
         │              ├─Quest
         │              │      WB_QuestPoint.uasset
         │              │
         │              └─WorldPlace
         │                      WB_FastTravelToolTip.uasset
         │                      WB_MapArea.uasset
         │                      WB_RewardSlot.uasset
         │                      WB_TaskSlot.uasset
         │                      WB_ToolTip.uasset
         │                      WB_ToolTipTask.uasset
         │
         ├─Developers
         │  ├─Administrator
         │  │  └─Collections
         │  └─kali
         │      └─Collections
         ├─GodOfWarPak
         │  ├─Anims
         │  │      axethrower.uasset
         │  │      axe_aim.uasset
         │  │      Axe_Catch_End.uasset
         │  │      Axe_Catch_Idle.uasset
         │  │      Axe_Catch_Start.uasset
         │  │      Hold_Axe_Idle.uasset
         │  │
         │  ├─Axe
         │  │  ├─Anims
         │  │  │      Axe_Floor.uasset
         │  │  │      Axe_Idle.uasset
         │  │  │      Axe_Return_Floor.uasset
         │  │  │      Axe_Return_Wall.uasset
         │  │  │      Axe_Spin.uasset
         │  │  │      Axe_Spin_Return_Slow.uasset
         │  │  │      Axe_Wall.uasset
         │  │  │      Axe_Wiggle_Floor.uasset
         │  │  │      Axe_Wiggle_Wall.uasset
         │  │  │      BS_Return.uasset
         │  │  │      Hammer_InAir.uasset
         │  │  │
         │  │  ├─Curves
         │  │  │      Curve_AxeReturn.uasset
         │  │  │      Curve_AxeReturnRight.uasset
         │  │  │      Curve_AxeRotation.uasset
         │  │  │      Curve_AxeStraighten.uasset
         │  │  │
         │  │  ├─Material
         │  │  │      God-of-war-kratos-leviathan-axe.uasset
         │  │  │      MAT_Axe.uasset
         │  │  │      MAT_AxeTrail.uasset
         │  │  │
         │  │  └─Mesh
         │  │          Axe.uasset
         │  │          Axe_PhysicsAsset.uasset
         │  │          Axe_Skeleton.uasset
         │  │
         │  └─Sounds
         │          bullet_flyby_01.uasset
         │          bullet_flyby_03.uasset
         │          bullet_flyby_09.uasset
         │          bullet_flyby_fast_05.uasset
         │          bullet_flyby_fast_08.uasset
         │          bullet_flyby_fast_09.uasset
         │          bullet_impact_body_flesh_02.uasset
         │          bullet_impact_body_flesh_07.uasset
         │          bullet_impact_metal_heavy_02.uasset
         │          bullet_impact_metal_heavy_02_Cue.uasset
         │          bullet_impact_metal_heavy_03.uasset
         │          bullet_impact_metal_heavy_05.uasset
         │          bullet_impact_metal_heavy_07.uasset
         │          bullet_impact_metal_heavy_08.uasset
         │          cinematic_buildup_reverse_whoosh_01.uasset
         │          cinematic_buildup_reverse_whoosh_01_Cue.uasset
         │          cinematic_buildup_reverse_whoosh_02.uasset
         │          cinematic_deep_low_whoosh_impact_02.uasset
         │          cinematic_deep_low_whoosh_impact_04.uasset
         │          cinematic_deep_low_whoosh_impact_05.uasset
         │          Cue_VaseBreak.uasset
         │          foley_soldier_gear_equipment_metal_cloth_heavy_movement_strong_01.uasset
         │          foley_soldier_gear_equipment_metal_cloth_heavy_movement_strong_02.uasset
         │          foley_soldier_gear_equipment_metal_cloth_heavy_movement_strong_03.uasset
         │          foley_soldier_gear_equipment_metal_cloth_heavy_movement_strong_04.uasset
         │          punch_general_body_impact_01.uasset
         │          punch_general_body_impact_01_Cue.uasset
         │          punch_general_body_impact_02.uasset
         │          punch_general_body_impact_03.uasset
         │          punch_general_body_impact_07.uasset
         │          punch_general_body_impact_08.uasset
         │          punch_grit_wet_impact_06.uasset
         │          punch_grit_wet_impact_07.uasset
         │          punch_grit_wet_impact_08.uasset
         │          Throw.uasset
         │          WAV_Vase_Break.uasset
         │          WAV_Vase_Break_02.uasset
         │          WAV_Vase_Break_Cue.uasset
         │          whoosh_swish_high_fast_01.uasset
         │          whoosh_swish_high_fast_02.uasset
         │          whoosh_swish_high_fast_03.uasset
         │          whoosh_swish_high_fast_04.uasset
         │          wind2.uasset
         │          Wind_Cue.uasset
         │          Woosh.uasset
         │
         ├─HDA
         │      terrain_intro.uasset
         │
         ├─HoudiniEngine
         │  └─Temp
         │      └─terrain_intro
         │          └─617616BE
         │                  Landscape_Temp_layer_bedrock.uasset
         │                  Landscape_Temp_layer_debris.uasset
         │                  Landscape_Temp_layer_flow.uasset
         │                  Landscape_Temp_layer_flowdir_x.uasset
         │                  Landscape_Temp_layer_flowdir_y.uasset
         │                  Landscape_Temp_layer_flowdir_z.uasset
         │                  Landscape_Temp_layer_grass.uasset
         │                  Landscape_Temp_layer_mask.uasset
         │                  Landscape_Temp_layer_rock.uasset
         │                  Landscape_Temp_layer_sediment.uasset
         │                  Landscape_Temp_layer_slump_flow.uasset
         │                  Landscape_Temp_layer_soil.uasset
         │                  Landscape_Temp_layer_trees.uasset
         │                  Landscape_Temp_layer_water.uasset
         │
         ├─Input
         │  │  IMC_Default.uasset
         │  │
         │  └─Actions
         │          IA_Attack.uasset
         │          IA_ChooseSpell.uasset
         │          IA_Crouch.uasset
         │          IA_Eagle.uasset
         │          IA_EquipWeapon.uasset
         │          IA_Horse.uasset
         │          IA_HotKey.uasset
         │          IA_Interact.uasset
         │          IA_Inventory.uasset
         │          IA_Jump.uasset
         │          IA_Look.uasset
         │          IA_Map.uasset
         │          IA_Move.uasset
         │          IA_Protect.uasset
         │          IA_Quests.uasset
         │          IA_Spell.uasset
         │          IA_Sprint.uasset
         │          IA_Torch.uasset
         │          IA_Tutorial.uasset
         │          IA_Walk.uasset
         │
         ├─KiteDemo
         │  ├─Environments
         │  │  ├─Foliage
         │  │  │  ├─BogMyrtleBush_01
         │  │  │  │      BogMyrtleBush_01.uasset
         │  │  │  │
         │  │  │  ├─BogMyrtleBush_02
         │  │  │  │      BogMyrtleBush_02.uasset
         │  │  │  │
         │  │  │  ├─BogMyrtle_01
         │  │  │  │      BogMyrtle_01_Atlas_Normal_Tex.uasset
         │  │  │  │      BogMyrtle_01_Atlas_Tex.uasset
         │  │  │  │      BogMyrtle_01_Fronds_Mat.uasset
         │  │  │  │      T_BogMyrtleBtm_01_D.uasset
         │  │  │  │      T_BogMyrtleBtm_01_N.uasset
         │  │  │  │
         │  │  │  └─Ferns
         │  │  │          M_Fern_01.uasset
         │  │  │          M_Fern_01_Inst.uasset
         │  │  │          SM_Fern_01.uasset
         │  │  │          SM_Fern_02.uasset
         │  │  │          T_Fern_01_D.uasset
         │  │  │          T_Fern_01_N.uasset
         │  │  │          T_Ice_Noise_N.uasset
         │  │  │          T_TilingNoise06_N.uasset
         │  │  │
         │  │  ├─GroundTiles
         │  │  │  └─Grass
         │  │  │          T_GDC_Grass01_D_NoisyAlpha.uasset
         │  │  │          T_Ground_Grass_N.uasset
         │  │  │
         │  │  └─Textures
         │  │          T_Water_N.uasset
         │  │          T_Water_Screen_Noise_Soft.uasset
         │  │          T_Water_Screen_Noise_Soft2.uasset
         │  │
         │  └─Material
         │          WorldCoords-XY.uasset
         │
         ├─MaterialInstance
         │      MI_starDust.uasset
         │      MI_Trail_50.uasset
         │
         ├─Materials
         │      M_starDust.uasset
         │      M_Terrain_Intro.uasset
         │      M_Terrain_Intro_Inst.uasset
         │      M_Trail.uasset
         │
         ├─Niagara
         │      NS_Sin_50_System.uasset
         │
         ├─Niagara_Script
         │      FloatHashToVector4.uasset
         │      Sin_UpdatePosition_50.uasset
         │
         └─Textures
                 logo.uasset
                 logo_aim.uasset
                 logo_back.uasset
                 logo_x.uasset
                 T_dust_longStar.uasset
                 T_Silky_Smoke_Trail.uasset
                 T_Silky_Smoke_Trail_Blur.uasset
                 T_Soft_Energy_Trail.uasset
