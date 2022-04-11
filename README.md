# [虚幻Unreal项目](Unreal)

[B站成果/进展/视频展示](https://space.bilibili.com/599592220)

#  :book: Learnbgame ----learnbgame is learn by game

Learnbgame的目标是一个创建一个关于科学知识学习的:video_game:[3D游戏]():video_game:,将科学研究得到的科学知识进行三维可视化,力求创建一种所见即所得的学习方式,你可以理解为现实世界的虚拟仿真映射.

关于[Learnbgame](https://www.bilibili.com/video/BV1kf4y1q7Mp)

## Learnbgame开发路线图式

![](mDrivEngine/develep.jpg)

Learnbgame目标的实现还有很长的路要走,因此现阶段Learnbgame为依托主流开源虚幻引擎Unreal以及houdini Engine for unreal的3D游戏项目，力求

*   模型尽量使用节点式非破坏性程序化模型----现阶段采用Houdini的hda进行创建

*   逻辑采用节点式逻辑----现阶段采用Unreal的蓝图和houdini hda进行实现

## [LearnruT](https://github.com/BlenderCN/Learnbgame/tree/master/LearnruT)为Learnbgame项目实时进行时

##  百科知识元宇宙
数学:memo:    
     |————    物理:memo:   
                |————     化学:memo:   
                            |————   生物:memo:   
                                      |————   地理:memo:   
                                                |————   天文:memo:   

## 节点时代 :memo: All_In_One流程

    原画
     |————————模型(节点式非破坏性程序化模型)
                |————材质(程序化材质纹理)
                      |—————————————————动画(动作捕捉库)     
                                          |————————————特效(实时解算)
                                                        |————————————————渲染（实时渲染）
                                                                          |
                                                                         后期合成
                                                                          |
                                                                         视频剪辑




* 节点式非破坏性程序化模型----现阶段使用houdini的hda

* 程序化材质纹理----现阶段使用substance design，houdini，blender实现

* 后期----现阶段采用Nuke，houdini，blender实现

* 节点式逻辑----现阶段使用unreal蓝图

* [blender]() + [houdini]() + [unreal蓝图]() + [Nuke]() + 


###  :memo: poqbdb---- poqbdb is power or quest by database

这是关于Learnbgame世界的数据集合引擎
*   模型的生成主要采用节点式非破坏性程序化模型

###  :memo: [ImmunemaG](ImmunemaG.md)

这是关于免疫学知识的卡牌游戏 :video_game: [部分内容展示](http://www.learnbgame.com/)




##  :book: 模型集成插件UI架构--基于现实世界和科学研究理论进行分类
![](mDrivEngine/struct.jpg)

###  :memo: 物质世界


    夸克————质子
            |—————原子核
           中子      |——————原子————分子————细胞————组织————器官————功能系统————个体————物种————种群————群落————生态系统——————地球————太阳系————银河系————本星系群————总星系————宇宙——————世界
                   电子


从原子出发，有元素周期表,往前，有原子核和电子组成的电子云，往后，则是原子构成分子的三维结构，以[pdb]()和[smiles]()格式在blender中，这是个微观世界，

往后，以gltf格式,是物种，种群组成的生态系统。

再往后，是地球以外广阔的宇宙。


###  :memo: 生物

![](mDrivEngine/poqbdb.png)
atoms---molecules---species---planets---

原子---分子---物种----星球---

:six_pointed_star: 原子--元素周期表--核外电子排布--

</br>


:six_pointed_star:  分子--无机物--有机大分子--

:six_pointed_star:   无机物--[smiles]()

✡   有机大分子--[pdb]()--[mol]()

</br>


:ghost: 物种--界--门--纲--目--科--属--种
</a>
</br>

:earth_asia: 星球--

</br>


[其他](https://github.com/BlenderCN/Blender3DWorld/blob/master/blender%E6%A8%A1%E5%9E%8B%E5%BA%93.md)



###  :memo: 能量驱动



声--光--热--电--动--势--场

 :musical_score: [声]()--  

</br>




:boom: [光]()--材质库(blender有内置材质库)--<a href="http://codeofart.com/easy-hdri-0-9-0/">环境光easyhdri</a>

</br>


:fire: [热]()--烟--火

</br>


:zap: [电]()--

</br>

:nut_and_bolt: [动]()--骨骼--

</br>

 :anchor: [势]()--状态--液体状态--<a href="https://github.com/rlguy/Blender-FLIP-Fluids">FLIP Fluids</a>
</a>
</br>

:cyclone: [场]()--Force Field(blender内置)
</a>
</br>

#  :book: requirement 

blender 3+
openbabel

#  :book: LearnruT----他山之石,可以工玉

* houdini特效借鉴

# [Learnbgame 在虚幻引擎](Unreal)

* [虚幻商城资源VaultCache](Unreal/VaultCache)

* [Learnbgame in Github with Unreal](https://github.com/all-in-one-unreal/readme)

#  :warning: 注意事项:

* 目前由于插件中的化学分子三维结构生成部分需要调用openbabel化学python库,所以还需另外安装,日后会进行改进,敬请期待

* atom模块中电子的排布引用Fibonacci lattice算法,运动引用AXIS ANGLE旋转算法.

* learnbgame目前主要在kali linux系统中开发,所以可能会有系统兼容性问题,欢迎提[bug](https://github.com/BlenderCN/Learnbgame/issues)


# :book:Learnbgame游戏引擎LearnbgamEngine

*   [三维模型--专注于节点式非破坏性程序化模型，格式多借鉴于hda(houdini data asset)格式]()

*   [脚本语言/逻辑节点: python :black_large_square: C++  :black_large_square: blueprint ]()

*   [注释系统:memo:]()

*   [特效系统:dizzy:](Unreal/特效系统.md)

*   [库存系统](Unreal/库存系统.md)

*   [物理引擎:]()

*   [交易商城系统，拍卖系统]()

*   [声音引擎:sound:](Unreal/声音系统.md)

*   [人工智能AI :computer:]()



# :book:other

<a href="Fofight.md">
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
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
LearmWWW
</a>
</br>
<a href="LearnbdnelB.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
LearnbdnelB
</a>
</br>
<a href="Learnbgame.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
Learnbgame
</a>
</br>
<a href="LearnbgameWWW.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
LearnbgameWWW
</a>
</br>
<a href="LearnBikiW.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
LearnBikiW
</a>
</br>
<a href="LearnioC.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
LearnioC
</a>
</br>
<a href="LearnruT.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
LearnruT.md
</a>
</br>
<a href="LearnW5H.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
LearnW5H
</a>
</br>
<a href="PByHack.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
PByHack
</a>
</br>
<a href="poqbdb.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoleft.png" align="left">
poqbdb
</a>
</br>
<a href="Lmy.md">
  <img src="https://github.com/BlenderCN/blenderTutorial/blob/master/mDrivEngine/blenderpng/logoright.png" align="left">
Lmy
</a>
