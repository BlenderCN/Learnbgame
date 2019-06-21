# Functions to get note Names and Indices & Frets from input
# MIDI Note List
noteList = [
    'c0','cs0','d0','ds0','e0','f0','fs0','g0','gs0','a0','as0','b0',
    'c1','cs1','d1','ds1','e1','f1','fs1','g1','gs1','a1','as1','b1',
    'c2','cs2','d2','ds2','e2','f2','fs2','g2','gs2','a2','as2','b2',
    'c3','cs3','d3','ds3','e3','f3','fs3','g3','gs3','a3','as3','b3',
    'c4','cs4','d4','ds4','e4','f4','fs4','g4','gs4','a4','as4','b4',
    'c5','cs5','d5','ds5','e5','f5','fs5','g5','gs5','a5','as5','b5',
    'c6','cs6','d6','ds6','e6','f6','fs6','g6','gs6','a6','as6','b6',
    'c7','cs7','d7','ds7','e7','f7','fs7','g7','gs7','a7','as7','b7',
    'c8','cs8','d8','ds8','e8','f8','fs8','g8','gs8','a8','as8','b8',
    'c9','cs9','d9','ds9','e9','f9','fs9','g9']

# 6 String Fret List
fretListS = [
    'NUT','F1','F2','F3','F4',
    'NUT','F1','F2','F3','F4',
    'NUT','F1','F2','F3','F4',
    'NUT','F1','F2','F3',
    'NUT','F1','F2','F3','F4',
    'NUT','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
    'F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24']
# Bass Fret List
fretListB = [
    'NUT','F1','F2','F3','F4',
    'NUT','F1','F2','F3','F4',
    'NUT','F1','F2','F3','F4',
    'NUT','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
    'F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24']

def getNote(noteIdx, offSet):
    if (noteIdx + offSet) < len(noteList):
        return noteList[noteIdx + offSet]
    else:
        return 'Not in Range'

def getIndex(noteName):
    idx = next((i for i, x in enumerate(noteList) if x == noteName), -1)
    return idx

def getFretS(noteIdx, offSet):
    if (noteIdx + offSet) < len(fretListS):
        return fretListS[noteIdx + offSet]
    else:
        return 'null'

def getFretB(noteIdx, offSet):
    if (noteIdx + offSet) < len(fretListB):
        return fretListB[noteIdx + offSet]
    else:
        return 'null'
