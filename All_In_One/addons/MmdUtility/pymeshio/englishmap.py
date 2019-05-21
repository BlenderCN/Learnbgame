#!/usr/bin/env python
# coding: utf8
"""
日本語名との変換マップ
"""
import sys

"""
ボーン名変換
"""
boneMap=[
("center", "センター", 1),
("upper body", "上半身"),
("neck", "首"),
("head", "頭"),
("eye_L", "左目", 5),
("eye_R", "右目", 5),
("necktie1", "ﾈｸﾀｲ１"),
("necktie2", "ﾈｸﾀｲ２"),
("necktie3", "ﾈｸﾀｲ３"),
("lower body", "下半身"),
("waist accessory", "腰飾り"),
("hair1_L", "左髪１"),
("hair2_L", "左髪２"),
("hair3_L", "左髪３"),
("hair4_L", "左髪４"),
("hair5_L", "左髪５"),
("hair6_L", "左髪６"),
("shoulder_L", "左肩"),
("arm_L", "左腕"),
("arm twist_L", "左腕捩", 8),
("elbow_L", "左ひじ"),
("wrist twist_L", "左手捩", 8),
("wrist_L", "左手首"),
("sleeve_L", "左袖", 1),
("thumb1_L", "左親指１"),
("thumb2_L", "左親指２"),
("fore1_L", "左人指１"),
("fore2_L", "左人指２"),
("fore3_L", "左人指３"),
("middle1_L", "左中指１"),
("middle2_L", "左中指２"),
("middle3_L", "左中指３"),
("third1_L", "左薬指１"),
("third2_L", "左薬指２"),
("third3_L", "左薬指３"),
("little1_L", "左小指１"),
("little2_L", "左小指２"),
("little3_L", "左小指３"),
("front skirt_L", "左ｽｶｰﾄ前"),
("back skirt_L", "左ｽｶｰﾄ後"),
("leg_L", "左足"),
("knee_L", "左ひざ"),
("ankle_L", "左足首"),
("hair1_R", "右髪１"),
("hair2_R", "右髪２"),
("hair3_R", "右髪３"),
("hair4_R", "右髪４"),
("hair5_R", "右髪５"),
("hair6_R", "右髪６"),
("shoulder_R", "右肩"),
("arm_R", "右腕"),
("arm twist_R", "右腕捩", 8),
("elbow_R", "右ひじ"),
("wrist twist_R", "右手捩", 8),
("wrist_R", "右手首"),
("sleeve_R", "右袖", 1),
("thumb1_R", "右親指１"),
("thumb2_R", "右親指２"),
("fore1_R", "右人指１"),
("fore2_R", "右人指２"),
("fore3_R", "右人指３"),
("middle1_R", "右中指１"),
("middle2_R", "右中指２"),
("middle3_R", "右中指３"),
("third1_R", "右薬指１"),
("third2_R", "右薬指２"),
("third3_R", "右薬指３"),
("little1_R", "右小指１"),
("little2_R", "右小指２"),
("little3_R", "右小指３"),
("front skirt_R", "右ｽｶｰﾄ前"),
("back skirt_R", "右ｽｶｰﾄ後"),
("leg_R", "右足"),
("knee_R", "右ひざ"),
("ankle_R", "右足首"),
("eyes", "両目"),
("front hair1", "前髪１"),
("front hair2", "前髪２"),
("front hair3", "前髪３"),
("eyelight_L", "左目光"),
("eyelight_R", "右目光"),
("necktie4", "ﾈｸﾀｲ４"),
("hair7_L", "左髪７"),
("hair7_R", "右髪７"),
("toe_L", "左つま先"),
("toe_R", "右つま先"),
("necktie IK", "ﾈｸﾀｲＩＫ"),
("hair IK_L", "左髪ＩＫ"),
("hair IK_R", "右髪ＩＫ"),
("leg IK_L", "左足ＩＫ"),
("leg IK_R", "右足ＩＫ"),
("toe IK_L", "左つま先ＩＫ"),
("toe IK_R", "右つま先ＩＫ"),

("lower body_t", "下半身先"),
("head_t", "頭先"),
("eye_L_t", "左目先"),
("eye_R_t", "右目先"),
("waist accessory_t", "腰飾り先"),

("sleeve_L_t", "左袖先"),
("wrist_L_t", "左手先"),
("thumb2_L_t", "左親指先"),
("fore3_L_t", "左人差指先"),
("middle3_L_t", "左中指先"),
("third3_L_t", "左薬指先"),
("little3_L_t", "左小指先"),
("front skirt_L_t", "左スカート前先"),
("back skirt_L_t", "左スカート後先"),

("sleeve_R_t", "右袖先"),
("wrist_R_t", "右手先"),
("thumb2_R_t", "右親指先"),
("fore3_R_t", "右人差指先"),
("middle3_R_t", "右中指先"),
("third3_R_t", "右薬指先"),
("little3_R_t", "右小指先"),
("front skirt_R_t", "右スカート前先"),
("back skirt_R_t", "右スカート後先"),

("center_t", "センター先"),
("eyes_t", "両目先"),
("necktie IK_t", "ﾈｸﾀｲＩＫ先"),
("hair IK_L_t", "左髪ＩＫ先"),
("hair IK_R_t", "右髪ＩＫ先"),
("leg IK_L_t", "左足ＩＫ先"),
("leg IK_R_t", "右足ＩＫ先"),
("toe IK_L_t", "左つま先ＩＫ先"),
("toe IK_R_t", "右つま先ＩＫ先"),
("front hair1_t", "前髪１先"),
("front hair2_t", "前髪２先"),
("front hair3_t", "前髪３先"),
("eyelight_L_t", "左目光先"),
("eyelight_R_t", "右目光先"),
("arm twist_L_t", "左腕捩先"),
("wrist twist_L_t", "左手捩先"),
("arm twist_R_t", "右腕捩先"),
("wrist twist_R_t", "右手捩先"),
("arm twist1_L", "左腕捩1", 9),
("arm twist2_L", "左腕捩2", 9),
("arm twist3_L", "左腕捩3", 9),
("arm twist1_R", "右腕捩1", 9),
("arm twist2_R", "右腕捩2", 9),
("arm twist3_R", "右腕捩3", 9),
#
("arm twist1_L_t", "左腕捩1先"),
("arm twist2_L_t", "左腕捩2先"),
("arm twist3_L_t", "左腕捩3先"),
("arm twist1_R_t", "右腕捩1先"),
("arm twist2_R_t", "右腕捩2先"),
("arm twist3_R_t", "右腕捩3先"),

# 追加ボーン
("root", "全ての親"),
("root_t", "全ての親先"),
("group", "グループ"),
("group_t", "グループ先"),
("front_shirt_L", "左シャツ前"),
("front_shirt_R", "右シャツ前"),
("back_shirt_L", "左シャツ後"),
("back_shirt_R", "右シャツ後"),
]
def getEnglishBoneName(name):
    for v in boneMap:
        if v[1]==name:
            return v[0]

def getIndexByEnglish(name):
    for i, v in enumerate(boneMap):
        if v[0]==name:
            return i

def getUnicodeBoneName(name):
    for v in boneMap:
        if v[0]==name:
            return v

"""
モーフ名変換
"""
skinMap=[
("base", "base", 0),
("serious", "真面目", 1),
("sadness", "困る", 1),
("cheerful", "にこり", 1),
("anger", "怒り", 1),
("go up", "上", 1),
("go down", "下", 1),
("blink", "まばたき", 2),
("smile", "笑い", 2),
("wink", "ウィンク", 2),
("wink2", "ウィンク２", 2),
("wink_R", "ウィンク右", 2),
("wink2_R", "ｳｨﾝｸ２右", 2),
("close><", "はぅ", 2),
("calm", "なごみ", 2),
("surprise", "びっくり", 2),
("doubt", "じと目", 2),
("confuse", "なぬ！", 2),
("pupil", "瞳小", 4),
("a", "あ", 3),
("i", "い", 3),
("u", "う", 3),
("o", "お", 3),
("triangle", "▲", 3),
("regret", "∧", 3),
("omega", "ω", 3),
("omegabox", "ω□", 3),
("fool", "はんっ！", 3),
("tongue", "ぺろっ", 4),
("e-", "えー", 3),
("grin", "にやり", 3),
]
def getEnglishSkinName(name):
    for v in skinMap:
        if v[1]==name:
            return v[0]

def getUnicodeSkinName(name):
    for v in skinMap:
        if v[0]==name:
            return v

"""
ボーングループ名変換
"""
boneGroupMap=[
        ("Root", "Root"),
        ("Exp", "表情"),
        ("IK", "ＩＫ"),
        ("Body[u]", "体(上)"),
        ("Hair", "髪"),
        ("Arms", "腕"),
        ("Fingers", "指"),
        ("Body[l]", "体(下)"),
        ("Legs", "足"),
        ]
def getEnglishBoneGroupName(name):
    for v in boneGroupMap:
        if v[1]==name:
            return v[0]

def getUnicodeBoneGroupName(name):
    for v in boneGroupMap:
        if v[0]==name:
            return v[1]


###############################################################################
# blender2.4 str to unicode
###############################################################################
if sys.version_info[0]<3:
    print('convert boneMap and skinMap to unicode...')
    # python2.x
    # unicodeに変換
    for i, l in enumerate(boneMap):
        replace=[]
        for j, m in enumerate(l):
            if j==1:
                replace.append(m.decode('utf-8'))
            else:
                replace.append(m)
        boneMap[i]=replace

    for i, l in enumerate(skinMap):
        replace=[]
        for j, m in enumerate(l):
            if j==1:
                replace.append(m.decode('utf-8'))
            else:
                replace.append(m)
        skinMap[i]=replace
    print('done')        

