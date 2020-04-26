;MyAlt(v2.0) for Blender - Copyright 2019 - by Increality/FormAffinity

#IfWinActive, Blender
SetTitleMatchMode, 2 ; Fast|Slow|RegEx|1|2|3


Alt::
{
IfNotEqual, AltDown
gosub, AllUp
else
{
gosub, AllUp
SendInput {AltDown}{Click down}
AltDown := "1"
}
Return
}

Shift::
{
IfNotEqual, ShiftDown
gosub, AllUp
else
{
gosub, AllUp
SendInput {AltDown}{MButton down}
ShiftDown := "1"
}
Return
}

~WheelUp::
~WheelDown::

; ****************
; Functions / Modules
; ****************

; Functions here
AllUp:
{
SendInput {MButton up}{Click up}{AltUp}
ShiftDown := AltDown := ""
return
}

; ****************
