# blender-ScreencastKeysMod

[Screencast Key Status Tool](http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/Screencast_Key_Status_Tool "Screencast Key Status Tool")

このアドオンをModalOperator中のイベントも取得出来るように改造したもの。

注意事項、既知の問題点:
* 公式の2.77(a)専用。
* レンダリング中は全てのイベントを取得出来ない。
* scene_callback_pre で wmWindow.modalhandlersを並び替えるので落ちる可能性がある。