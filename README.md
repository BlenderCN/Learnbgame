<div align=center> <a href="https://www.learnbgame.com"><img src="https://avatars3.githubusercontent.com/u/20420400?s=40&v=4"/></a></div>


# [HoudiniForUnreal项目](HoudiniEngineForUnreal)

[B站成果/进展/视频展示](https://space.bilibili.com/599592220)

#  :book: Learnbgame ----learnbgame is learn by game

Learnbgame的目标是一个创建一个关于科学知识学习的:video_game:[3D游戏平台](https://www.learnbgame.com/):video_game:,将科学研究得到的科学知识进行三维可视化,构建一个科学知识元宇宙，力求创建一种所见即所得的学习方式,你可以理解为现实世界的虚拟仿真映射.这个项目旨在不断迭代构建可行性方案蓝图。

关于[Learnbgame](https://www.bilibili.com/video/BV1kf4y1q7Mp)

## Learnbgame开发路线图式


![](mDrivEngine/develep.jpg)

Learnbgame目标的实现还有很长的路要走,因此会随着不断的迭代会修正不同的施行方案和蓝图，现阶段Learnbgame为依托主流开源虚幻引擎Unreal以及houdini Engine for unreal的3D游戏项目，力求

*   模型尽量使用节点式非破坏性程序化模型----现阶段采用Houdini的hda进行创建

*   逻辑采用节点式逻辑----现阶段采用Unreal的蓝图和houdini hda进行实现

## [LearnruT](https://github.com/BlenderCN/Learnbgame/tree/master/LearnruT)为Learnbgame项目实时进行时

[Blender3DWorld](https://github.com/Fofight/Blender3DWorld)——————>[All_In_One](https://github.com/FofightFong/All_In_One)————>[Learnrut](https://github.com/FofightFong/Learnrut)————>

##  [百科知识元宇宙](https://github.com/BlenderCN/Learnbgame/blob/master/LearnBikiW.md)
     ✡ [数学]()
         |———— ✡  [物理]()
                    |———— ✡ [化学]()
                                |———— ✡  [生物]()
                                          |———— ✡ [地理]()
                                                    |———— ✡ [天文]()
![](mDrivEngine/frame.png)
## [节点时代 :memo: All_In_One流程](All_In_One)

参考Houdini PDG将All_In_One流程有机连接在一起

    ✡原画
     |————————✡模型(节点式非破坏性程序化模型)
                |——————————✡材质(程序化材质纹理)
                            |—————————————————✡动画(动作捕捉库)     
                                               |————————————✡特效(实时解算)
                                                             |————————————————✡渲染（实时渲染）
                                                                               |
                                                                             ✡后期合成
                                                                               |
                                                                             ✡视频剪辑




* [节点式非破坏性程序化模型](poqbdb.md)----现阶段使用houdini的hda

* 程序化材质纹理----现阶段使用substance design，houdini，blender实现

* 后期----现阶段采用Nuke，houdini，blender实现

* 节点式逻辑----现阶段使用unreal蓝图

* [blender]() + [houdini]() + [unreal蓝图]() + [Nuke]() + 


###  :memo: poqbdb---- poqbdb is power or quest by database

这是关于Learnbgame世界的数据集合引擎
*   模型的生成主要采用节点式非破坏性程序化模型

###  :memo: [ImmunemaG](ImmunemaG.md)

这是关于免疫学知识的卡牌游戏 :video_game: [部分构想展示](http://www.learnbgame.com/)




##  :book: 模型集成插件UI架构--基于现实世界和科学研究理论进行分类
![](mDrivEngine/struct.jpg)

###  :memo: [物质世界(主要以poqbdb节点式非破坏性程序化模型形式体现)](https://github.com/BlenderCN/Learnbgame/tree/master/poqbdb)


    ✡夸克————✡质子
            |—————✡原子核
           ✡中子      |——————✡原子————✡分子————✡细胞————✡组织————✡器官————✡功能系统————✡个体————✡物种————✡种群————✡群落————✡生态系统——————✡地球————✡太阳系————✡银河系————✡本星系群————✡总星系————✡宇宙——————✡世界
                   ✡电子


从原子出发，有元素周期表,往前，有原子核和电子组成的电子云，往后，则是原子构成分子的三维结构，以[smiles](https://github.com/BlenderCN/Learnbgame/blob/master/poqbdb/%E5%88%86%E5%AD%90.md)格式构建分子三维结构，这是个微观世界，

往后，以节点式非破坏性程序化模型形式式,是物种，种群组成的生态系统。

再往后，是地球以外广阔的宇宙。


###  :memo: 生物

![](mDrivEngine/poqbdb.png)
atoms---molecules---species---planets---

原子---分子---物种----星球---

:atom: 原子--[元素周期表](https://ptable.com/#Properties)--核外电子排布--

</br>


:electron:  分子--无机物--有机大分子--

:six_pointed_star:   无机物--[smiles](https://github.com/BlenderCN/Learnbgame/blob/master/poqbdb/%E5%88%86%E5%AD%90.md)

✡   有机大分子--[pdb]()--[mol]()

</br>


:ghost: 物种--界--门--纲--目--科--属--种
</a>
</br>

:earth_asia: 星球--

</br>


[其他](https://github.com/BlenderCN/Blender3DWorld/blob/master/blender%E6%A8%A1%E5%9E%8B%E5%BA%93.md)



###  :memo: [能量驱动——（主要以特效形式体现LByEFX）](https://github.com/BlenderCN/Learnbgame/tree/master/LByEFX))



声--光--热--电--动--势--场

 :musical_score: [声]()--  

</br>




:boom: [光]()--材质库(程序纹理材质库)--<a href="">环境光</a>

</br>


:fire: [热]()--烟--火

</br>


:zap: [电]()--

</br>

:nut_and_bolt: [动]()--骨骼--

</br>

 :anchor: [势]()--状态--液体状态--<a href=""></a>
</a>
</br>

:cyclone: [场]()--Force Field()
</a>
</br>

#  :book: requirement 

blender

python

#  :book: LearnruT----他山之石,可以工玉



# [Learnbgame 在虚幻引擎](Unreal)

* [虚幻商城资源VaultCache](HoudiniEngineForUnreal/VaultCache)

* [Learnbgame in Github with Unreal](https://github.com/all-in-one-unreal/readme)

#  :warning: 注意事项:



* atom模块中电子的排布引用Fibonacci lattice算法,运动引用AXIS ANGLE旋转算法.




# :book:Learnbgame游戏引擎LearnbgamEngine

*   [三维模型--专注于节点式非破坏性程序化模型，格式多借鉴于hda(houdini data asset)格式](poqbdb)

*   [脚本语言/逻辑节点: python :black_large_square: C++  :black_large_square: blueprint ](PByHack.md)

*   [注释系统:memo:]()

*   [特效系统:dizzy:](https://github.com/BlenderCN/Learnbgame/tree/master/LByEFX)

*   [库存系统](HoudiniEngineForUnreal/库存系统.md)

*   [物理引擎:](HoudiniEngineForUnreal/物理引擎.md)

*   [交易商城系统，拍卖系统](FreetimeJoW)

*   [声音引擎:sound:](HoudiniEngineForUnreal/声音系统.md)

*   [人工智能AI :computer:](HoudiniEngineForUnreal/人工智能.md)



# :book:other

<a href="Fofight.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
Fofight
</a>

</br>
<a href="poqbdb">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
poqbdb
</a>
</br>
<a href="PByHack">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
PByHack
</a>
</br>
<a href="FreetimeJoW.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
Fofight
</a>
</br>
<a href="ImmunemaG.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
ImmunemaG
</a>
</br>
<a href="LearmWWW.md">
<p style="text-align:center;">LearmWWW</p>
     <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">

</a>
</br>
<a href="LearnbdnelB.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">
LearnbdnelB
</a>
</br>
<a href="Learnbgame.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">
Learnbgame
</a>
</br>
<a href="LearnbgameWWW.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">
LearnbgameWWW
</a>
</br>
<a href="LearnBikiW.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">
LearnBikiW
</a>
</br>
<a href="LearnioC.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">
LearnioC
</a>
</br>
<a href="LearnruT">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">
LearnruT
</a>
</br>
<a href="LearnW5H.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">
LearnW5H
</a>
</br>

<a href="LByEFX">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">
LByEFX
</a>
</br>
<a href="Lmy">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="right">    
<p style="text-align:center;">Lmy</p>
</a>
