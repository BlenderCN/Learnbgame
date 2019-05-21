# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

'''
Contains all animation names used by Neverwinter Nights.

@author: Erik Ylipää
'''

names = {}


def construct_names():
    if names:
        return
    for group in [items, door,  effect, tile, gui]:
        for animation, dict in group.items():
            for class_name in dict["classes"]:
                class_name = class_name.lower()
                if class_name not in names:
                    names[class_name] = []
                names[class_name].append(animation)
    names["character"] = {}
    for group in [character_player_full, character_simple_large]:
        for animation, dict in group.items():
            for class_name in dict["classes"]:
                class_name = class_name.lower()
                if class_name not in names["character"]:
                    names["character"][class_name] = []
                names["character"][class_name].append(animation)


def get_names():
    if not names:
        construct_names()
    return names


def get_names_by_classification(classification):
    if not names:
        construct_names()
    return names[classification]


items = {
    'default': {'classes': ['Item']},
    'off': {'classes': ['Item']},
    'off2on': {'classes': ['Item']},
    'on': {'classes': ['Item']},
    'on2off': {'classes': ['Item']},
    'close': {'classes': ['Item']},
    'close2open': {'classes': ['Item']},
    'open': {'classes': ['Item']},
    'open2close': {'classes': ['Item']},
    'damage': {'classes': ['Item']},
    'die': {'classes': ['Item']},
    'dead': {'classes': ['Item']},
}


door = {
    'default': {'classes': ['Door']},
    'opening1': {'classes': ['Door']},
    'opening2': {'classes': ['Door']},
    'opened2': {'classes': ['Door']},
    'opened1': {'classes': ['Door']},
    'closed': {'classes': ['Door']},
    'closing1': {'classes': ['Door']},
    'closing2': {'classes': ['Door']},
    'trans': {'classes': ['Door']},
    'die': {'classes': ['Door']},
    'dead': {'classes': ['Door']},
    'damage': {'classes': ['Door']},
}


character_player_full = {
    'conjure1': {'description': 'Conjuration', 'classes': ['Player', 'Full']},
    'conjure2': {'description': 'Conjuration', 'classes': ['Player', 'Full']},
    'castout': {'description': 'Cast out, beginning', 'classes': ['Player', 'Full']},
    'castoutlp': {'description': 'Cast out, looping', 'classes': ['Player', 'Full']},
    'castself': {'description': 'Cast on self, beginning', 'classes': ['Player', 'Full']},
    'castselflp': {'description': 'Cast on self, looping', 'classes': ['Player', 'Full']},
    'castup': {'description': 'Cast up, beginning', 'classes': ['Player', 'Full']},
    'castuplp': {'description': 'Cast up, looping', 'classes': ['Player', 'Full']},
    'castarea': {'description': 'Cast area effect, beginning', 'classes': ['Player', 'Full']},
    'castarealp': {'description': 'Cast area effect, looping', 'classes': ['Player', 'Full']},
    'victoryfr': {'description': 'Victory', 'classes': ['Player', 'Full']},
    'victorymg': {'description': 'Victory', 'classes': ['Player', 'Full']},
    'victoryth': {'description': 'Victory', 'classes': ['Player', 'Full']},
    'castpoint': {'description': 'Cast by pointing, beginning', 'classes': ['Player', 'Full']},
    'castpointlp': {'description': 'Cast by pointing, looping', 'classes': ['Player', 'Full']},
    'appear': {'description': 'Drop from above', 'classes': ['Player', 'Full']},
    'disappear': {'description': 'Leap upward, beginning', 'classes': ['Player', 'Full']},
    'disappearlp': {'description': 'Leap upward, looping', 'classes': ['Player', 'Full']},
    '1hreadyr': {'description': '1-handed ready, right', 'classes': ['Player', 'Full']},
    '1hreadyl': {'description': '1-handed ready, left', 'classes': ['Player', 'Full']},
    '2wreadyr': {'description': '2-weapon ready, right', 'classes': ['Player', 'Full']},
    '2wreadyl': {'description': '2-weapon ready, left', 'classes': ['Player', 'Full']},
    'nwreadyl': {'description': 'No weapon ready, left', 'classes': ['Player', 'Full']},
    'nwreadyr': {'description': 'No weapon ready, right', 'classes': ['Player', 'Full']},
    '1hslashl': {'description': '1-handed slash, left', 'classes': ['Player', 'Full']},
    '1hslashr': {'description': '1-handed slash, right', 'classes': ['Player', 'Full']},
    '1hstab': {'description': '1-handed stab', 'classes': ['Player', 'Full']},
    '1hcloseh': {'description': '1-handed close, high', 'classes': ['Player', 'Full']},
    '1hclosel': {'description': '1-handed close, low', 'classes': ['Player', 'Full']},
    '1hreach': {'description': '1-handed reach for target', 'classes': ['Player', 'Full']},
    '1hparryr': {'description': '1-handed parry, right', 'classes': ['Player', 'Full']},
    '1hparryl': {'description': '1-handed parry, left', 'classes': ['Player', 'Full']},
    'dodgelr': {'description': 'Dodge, lower or duck', 'classes': ['Player', 'Full']},
    'dodges': {'description': 'Dodge, sidestep', 'classes': ['Player', 'Full']},
    'damages': {'description': 'Hit, from stab', 'classes': ['Player', 'Full']},
    'cwalkf': {'description': 'Combat walk, forward', 'classes': ['Player', 'Full']},
    'cwalkb': {'description': 'Combat walk, backward', 'classes': ['Player', 'Full']},
    'cwalkl': {'description': 'Combat walk, left', 'classes': ['Player', 'Full']},
    'cwalkr': {'description': 'Combat walk, right', 'classes': ['Player', 'Full']},
    '2wslashl': {'description': '2-weapon slash, left', 'classes': ['Player', 'Full']},
    '2wslashr': {'description': '2-weapon slash, right', 'classes': ['Player', 'Full']},
    '2wstab': {'description': '2-weapon stab', 'classes': ['Player', 'Full']},
    '2wcloseh': {'description': '2-weapon close, high', 'classes': ['Player', 'Full']},
    '2wclosel': {'description': '2-weapon close, low', 'classes': ['Player', 'Full']},
    '2wreach': {'description': '2-weapon reach for target', 'classes': ['Player', 'Full']},
    'nwslashl': {'description': 'No weapon slash, left', 'classes': ['Player', 'Full']},
    'nwstab': {'description': 'No Weapon stab', 'classes': ['Player', 'Full']},
    'throwr': {'description': 'Throw, right hand', 'classes': ['Player', 'Full']},
    '2wparryl': {'description': '2-weapon parry, left', 'classes': ['Player', 'Full']},
    '2wparryr': {'description': '2-weapon parry, right', 'classes': ['Player', 'Full']},
    'shieldl': {'description': 'Shield block, low', 'classes': ['Player', 'Full']},
    'kdbck': {'description': 'Knockdown back, beginning', 'classes': ['Player', 'Full']},
    'kdbckps': {'description': 'Knockdown back, looping', 'classes': ['Player', 'Full']},
    'kdbckdmg': {'description': 'Knockdown back, hit', 'classes': ['Player', 'Full']},
    'kdbckdie': {'description': 'Knockdown back, die', 'classes': ['Player', 'Full']},
    'gutokdb': {'description': 'Get up, to knockdown back', 'classes': ['Player', 'Full']},
    'gustandb': {'description': 'Get up, from gutokdb', 'classes': ['Player', 'Full']},
    'kdfnt': {'description': 'Knockdown forward, beginning', 'classes': ['Player', 'Full']},
    'kdfntps': {'description': 'Knockdown forward, looping', 'classes': ['Player', 'Full']},
    'kdfntdmg': {'description': 'Knockdown forward, hit', 'classes': ['Player', 'Full']},
    'kdfntdie': {'description': 'Knockdown forward, die', 'classes': ['Player', 'Full']},
    'gutokdf': {'description': 'Get up, to knockdown forward', 'classes': ['Player', 'Full']},
    'gustandf': {'description': 'Get up, from gutokdf', 'classes': ['Player', 'Full']},
    'damagel': {'description': 'Hit, from left', 'classes': ['Player', 'Full']},
    'damager': {'description': 'Hit, from right', 'classes': ['Player', 'Full']},
    'nwcloseh': {'description': 'No weapon close, high', 'classes': ['Player', 'Full']},
    'nwclosel': {'description': 'No weapon close, low (kick)', 'classes': ['Player', 'Full']},
    'spasm': {'description': 'Spasm', 'classes': ['Player', 'Full']},
    'deadfnt': {'description': 'Dead, forward, looping', 'classes': ['Player', 'Full']},
    'deadbck': {'description': 'Dead, back, looping', 'classes': ['Player', 'Full']},
    'nwreach': {'description': 'No weapon, reach', 'classes': ['Player', 'Full']},
    'nwkickl': {'description': 'No weapon, kick left', 'classes': ['Player', 'Full']},
    'nwkickr': {'description': 'No weapon, kick right', 'classes': ['Player', 'Full']},
    'nwslashr': {'description': 'No weapon, slash right', 'classes': ['Player', 'Full']},
    'nwkicks': {'description': 'No weapon, kick stab', 'classes': ['Player', 'Full']},
    'bowrdy': {'description': 'Hold bow at ready', 'classes': ['Player', 'Full']},
    'xbowrdy': {'description': 'Hold crossbow at ready', 'classes': ['Player', 'Full']},
    'bowshot': {'description': 'Shoot bow', 'classes': ['Player', 'Full']},
    'xbowshot': {'description': 'Shoot crossbow', 'classes': ['Player', 'Full']},
    '2wslasho': {'description': '2-weapon slash, only upper body', 'classes': ['Player', 'Full']},
    'nwslasho': {'description': 'No weapon slash, only upper body', 'classes': ['Player', 'Full']},
    '1hslasho': {'description': '1-weapon slash, only upper body', 'classes': ['Player', 'Full']},
    '2hslasho': {'description': '2-handed slash, only upper body', 'classes': ['Player', 'Full']},
    'cturnr': {'description': 'Combat turn, right', 'classes': ['Player', 'Full']},
    'damageb': {'description': 'Hit, back', 'classes': ['Player', 'Full']},
    'walk': {'description': 'Walk', 'classes': ['Player', 'Full']},
    'pause1': {'description': 'Pause, looping', 'classes': ['Player', 'Full']},
    'hturnl': {'description': 'Head turn, left', 'classes': ['Player', 'Full']},
    'hturnr': {'description': 'Head turn, right', 'classes': ['Player', 'Full']},
    'pausesh': {'description': 'Pause, scratch head', 'classes': ['Player', 'Full']},
    'pausebrd': {'description': 'Pause, bored', 'classes': ['Player', 'Full']},
    'pausetrd': {'description': 'Pause, tired', 'classes': ['Player', 'Full']},
    'pausepsn': {'description': 'Pause, poisoned or drunk', 'classes': ['Player', 'Full']},
    'listen': {'description': 'Listen, looping', 'classes': ['Player', 'Full']},
    'salute': {'description': 'Salute', 'classes': ['Player', 'Full']},
    'bow': {'description': 'Bow', 'classes': ['Player', 'Full']},
    'drink': {'description': 'Drink', 'classes': ['Player', 'Full']},
    'read': {'description': 'Read', 'classes': ['Player', 'Full']},
    'tlknorm': {'description': 'Talk, normal', 'classes': ['Player', 'Full']},
    'tlkplead': {'description': 'Talk, Pleading', 'classes': ['Player', 'Full']},
    'tlkforce': {'description': 'Talk, forceful', 'classes': ['Player', 'Full']},
    'tlklaugh': {'description': 'Talk, laughing', 'classes': ['Player', 'Full']},
    'greeting': {'description': 'Greeting', 'classes': ['Player', 'Full']},
    'run': {'description': 'Run', 'classes': ['Player', 'Full']},
    'getlow': {'description': 'Get low, beginning', 'classes': ['Player', 'Full']},
    'getmid': {'description': 'Get middle, beginning', 'classes': ['Player', 'Full']},
    'torchl': {'description': 'Lift torch', 'classes': ['Player', 'Full']},
    'sitdown': {'description': 'Sit down, beginning', 'classes': ['Player', 'Full']},
    'walkdead': {'description': 'Walk as if dead', 'classes': ['Player', 'Full']},
    'kneel': {'description': 'Kneel', 'classes': ['Player', 'Full']},
    'meditate': {'description': 'Meditate, looping', 'classes': ['Player', 'Full']},
    'worship': {'description': 'Worship, looping', 'classes': ['Player', 'Full']},
    'walkinj': {'description': 'Walk with injured leg', 'classes': ['Player', 'Full']},
    'pause2': {'description': 'Pause, looping', 'classes': ['Player', 'Full']},
    'getmidlp': {'description': 'Get middle, looping', 'classes': ['Player', 'Full']},
    'getlowlp': {'description': 'Get low, looping', 'classes': ['Player', 'Full']},
    'lookfar': {'description': 'Look far away', 'classes': ['Player', 'Full']},
    'sit': {'description': 'Sit in chair, looping', 'classes': ['Player', 'Full']},
    'sitcross': {'description': 'Sit crosslegged, beginning', 'classes': ['Player', 'Full']},
    'sitcrossps': {'description': 'Sit crosslegged, looping', 'classes': ['Player', 'Full']},
    'drwright': {'description': 'Draw weapon, right hand', 'classes': ['Player', 'Full']},
    'drwleft': {'description': 'Draw weapon, left hand', 'classes': ['Player', 'Full']},
    'taunt': {'description': 'Taunt', 'classes': ['Player', 'Full']},
    'steal': {'description': 'Steal', 'classes': ['Player', 'Full']},
    'pauseturn': {'description': 'Pause and turn in place', 'classes': ['Player', 'Full']},
    'pausewalkl': {'description': 'Pause and walk left', 'classes': ['Player', 'Full']},
    'pausewalkr': {'description': 'Pause and walk right', 'classes': ['Player', 'Full']},
    'xbowr': {'description': 'Hold crossbow at rest', 'classes': ['Player', 'Full']},
    'pausewalkfl': {'description': 'Pause and walk forward', 'classes': ['Player', 'Full']},
    'pausewalkfr': {'description': 'Pause and walk forward right', 'classes': ['Player', 'Full']},
    'runfl': {'description': 'Pause and run forward left', 'classes': ['Player', 'Full']},
    'runfr': {'description': 'Pause and run forward right', 'classes': ['Player', 'Full']},
    'plpause1': {'description': 'Hold polearm at rest', 'classes': ['Player', 'Full']},
    '2hreadyr': {'description': '2-handed ready, right', 'classes': ['Player', 'Full']},
    '2hreadyl': {'description': '2-handed ready, left', 'classes': ['Player', 'Full']},
    'plreadyr': {'description': 'Polearm ready, right', 'classes': ['Player', 'Full']},
    'plreadyl': {'description': 'Polearm ready, left', 'classes': ['Player', 'Full']},
    '2hslashl': {'description': '2-handed slash, left', 'classes': ['Player', 'Full']},
    '2hslashr': {'description': '2-handed slash, right', 'classes': ['Player', 'Full']},
    '2hstab': {'description': '2-handed stab', 'classes': ['Player', 'Full']},
    '2hcloseh': {'description': '2-handed close, high', 'classes': ['Player', 'Full']},
    '2hclosel': {'description': '2-handed close, low', 'classes': ['Player', 'Full']},
    '2hreach': {'description': '2-handed reach for target', 'classes': ['Player', 'Full']},
    '2hparryl': {'description': '2-handed parry, left', 'classes': ['Player', 'Full']},
    '2hparryr': {'description': '2-handed parry, right', 'classes': ['Player', 'Full']},
    'plslashl': {'description': 'Polearm slash, left', 'classes': ['Player', 'Full']},
    'plslashr': {'description': 'Polearm slash, right', 'classes': ['Player', 'Full']},
    'plstab': {'description': 'Polearm stab', 'classes': ['Player', 'Full']},
    'plcloseh': {'description': 'Polearm close, high', 'classes': ['Player', 'Full']},
    'plclosel': {'description': 'Polearm close, low', 'classes': ['Player', 'Full']},
    'plreach': {'description': 'Polearm reach for target', 'classes': ['Player', 'Full']},
    'plparryl': {'description': 'Polearm parry, left', 'classes': ['Player', 'Full']},
    'plparryr': {'description': 'Polearm parry, right', 'classes': ['Player', 'Full']},
    'plslasho': {'description': 'Polearm slash, only upper body', 'classes': ['Player']},
}


character_simple_large = {
    'creadyr': {'description': 'Ready, right', 'classes': ['Simple', 'Large']},
    'creadyl': {'description': 'Ready, left', 'classes': ['Simple', 'Large']},
    'cdamagel': {'description': 'Hit, from left', 'classes': ['Simple', 'Large']},
    'cdamager': {'description': 'Hit, from right', 'classes': ['Simple', 'Large']},
    'cdamages': {'description': 'Hit, stabbed', 'classes': ['Simple', 'Large']},
    'cpause1': {'description': 'Pause, looping', 'classes': ['Simple', 'Large']},
    'ca1slashl': {'description': 'Creature attack, slash left', 'classes': ['Simple', 'Large']},
    'cwalk': {'description': 'Walk', 'classes': ['Simple', 'Large']},
    'cclosel': {'description': 'Attack close, low', 'classes': ['Simple', 'Large']},
    'ca1slashr': {'description': 'Creature attack, slash right', 'classes': ['Simple', 'Large']},
    'ca1stab': {'description': 'Creature attack, stab', 'classes': ['Simple', 'Large']},
    'ccloseh': {'description': 'Attack close, high', 'classes': ['Simple', 'Large']},
    'creach': {'description': 'Attach reach for target', 'classes': ['Simple', 'Large']},
    'cparryr': {'description': 'Parry, right', 'classes': ['Simple', 'Large']},
    'cparryl': {'description': 'Parry, left', 'classes': ['Simple', 'Large']},
    'cdodgelr': {'description': 'Dodge, lower or duck', 'classes': ['Simple', 'Large']},
    'cdodges': {'description': 'Dodge, sidestep', 'classes': ['Simple', 'Large']},
    'ckdbck': {'description': 'Knockdown back,beginning', 'classes': ['Simple', 'Large']},
    'ckdbckps': {'description': 'Knockdown back, looping', 'classes': ['Simple', 'Large']},
    'ckdbckdmg': {'description': 'Knockdown back, hit', 'classes': ['Simple', 'Large']},
    'ckdbckdie': {'description': 'Knockdown back, die', 'classes': ['Simple', 'Large']},
    'cdead': {'description': 'Dead, looping', 'classes': ['Simple', 'Large']},
    'cguptokdb': {'description': 'Get up, to knockdown back', 'classes': ['Simple', 'Large']},
    'cgustandb': {'description': 'Get up, from gutokdb', 'classes': ['Simple', 'Large']},
    'ccwalkf': {'description': 'Combat walk, forward', 'classes': ['Simple', 'Large']},
    'ccwalkb': {'description': 'Combat walk, backward', 'classes': ['Simple', 'Large']},
    'ccwalkl': {'description': 'Combat walk, left', 'classes': ['Simple', 'Large']},
    'ccwalkr': {'description': 'Combat walk, right', 'classes': ['Simple', 'Large']},
    'cgetmid': {'description': 'Get middle, beginning', 'classes': ['Simple', 'Large']},
    'chturnl': {'description': 'Head turn, left', 'classes': ['Simple', 'Large']},
    'chturnr': {'description': 'Head turn, right', 'classes': ['Simple', 'Large']},
    'ctaunt': {'description': 'Taunt', 'classes': ['Simple', 'Large']},
    'cconjure1': {'description': 'Conjuration', 'classes': ['Simple', 'Large']},
    'ccastoutlp': {'description': 'Cast out, looping', 'classes': ['Simple', 'Large']},
    'cappear': {'description': 'Drop from above', 'classes': ['Simple', 'Large']},
    'cdisappear': {'description': 'Leap upward, beginning', 'classes': ['Simple', 'Large']},
    'ccastout': {'description': 'Cast out, beginning', 'classes': ['Simple', 'Large']},
    'cgetmidlp': {'description': 'Get middle, looping', 'classes': ['Simple', 'Large']},
    'cspasm': {'description': 'Spasm', 'classes': ['Simple', 'Large']},
    'crun': {'description': 'Run', 'classes': ['Simple', 'Large']},
    'ccturnr': {'description': 'Combat turn, right', 'classes': ['Simple', 'Large']},
    'cdisappearlp': {'description': 'Leap upward, looping', 'classes': ['Simple', 'Large']},
}


effect = {
    'default': {'classes': ['Effect']},
    'hit01': {'classes': ['Effect']},
    'cast01': {'classes': ['Effect']},
    'conjure01': {'classes': ['Effect']},
    'travel01': {'classes': ['Effect']},
    'impact': {'classes': ['Effect']},
    'duration': {'classes': ['Effect']},
    'cessation': {'classes': ['Effect']},
    'fade': {'classes': ['Effect']},
}


tile = {
    'default': {'classes': ['Tile']},
    'tiledefault': {'classes': ['Tile']},
    'animloop01': {'classes': ['Tile']},
    'animloop02': {'classes': ['Tile']},
    'animloop03': {'classes': ['Tile']},
    'Day': {'classes': ['Tile']},
    'Day2Night': {'classes': ['Tile']},
    'Night': {'classes': ['Tile']},
    'Night2Day': {'classes': ['Tile']},
}


gui = {
    'default': {'classes': ['GUI']},
    'up': {'classes': ['GUI']},
    'down': {'classes': ['GUI']},
    'press': {'classes': ['GUI']},
    'release': {'classes': ['GUI']},
    'checkedup': {'classes': ['GUI']},
    'checkeddown': {'classes': ['GUI']},
    'uncheckedup': {'classes': ['GUI']},
    'uncheckeddown': {'classes': ['GUI']},
    'ghosted': {'classes': ['GUI']},
    'percentage': {'classes': ['GUI']},
    'size': {'classes': ['GUI']},
    'thumbsize': {'classes': ['GUI']},
    'enabled': {'classes': ['GUI']},
    'disabled': {'classes': ['GUI']},
    'activehilite': {'classes': ['GUI']},
    'hilite': {'classes': ['GUI']},
    'fog': {'classes': ['GUI']},
    'checkedhilite': {'classes': ['GUI']},
    'encouraged': {'classes': ['GUI']},
}
