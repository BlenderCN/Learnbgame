# 游


#        编程语言

#

# [Game Engine]()

# 基础架构

###  游戏引擎的分层架构

##### 工具层

##### 为什么要分层

*  减少耦合，降低复杂度
*  上层无需知道下层的具体实现
*  应对不同的需求变化

##### 功能层

*  GameTick控制各系统周期性更新
*  为游戏引擎提供核心功能模块
*  多核多线程架构趋势

##### 资源层

*  GUID
*  运行时资产管理

        虚拟文件系统

        Handle
   
*  资产生命周期

        不同资源有不同的生命周期

        尽可能减少资源的内存申请与释放

        垃圾回收
   
##### 平台层

*    硬件架构
*    图形API概念

##### 核心层

*    数学计算库
*    数据结构与容器
*    内存管理


###  如何构建游戏世界

##### 游戏世界组成

*    万物皆Game Object
*    动态物
*    静态物
*    环境
*    其他

##### GameObject组成

*    组件
*    继承

##### 复杂情况处理

*    组件间的依赖关系
*    Game Object间的依赖关系
*    事件的处理时机

##### 游戏场景管理

*    空间数据结构
*    Game Object检索

##### 如何让游戏世界动起来

*    基于对象的更新Object-based tick
*    基于组件的更新Commponent-base tick
*    事件机制（基本概念）


# 渲染

### GPU渲染管线

*    顶点着色器
*    几何着色器
*    光栅化
*    像素着色器
*    合并阶段

### GPU架构

*    Immediate Mode Rendering
*    Tile Base Rendering
*    Tile Based Deferred Rendering
### 可见性裁剪

*    视锥裁剪
*    Potential Visibililty Set
*    遮挡剔除
*    入口裁剪

### 场景空间管理

*    层次包围盒（BVH）
*    二元空间分割树（BSP Trees）
*    四叉树（Quad Tree）
*    八叉树（Octree）
*    场景图（Scene Graphs）
*    KD树（K-Dimensional Tree）

### 贴图压缩

##### Adaptive Scalable Texture Compression

##### Ericsson Texture Compression

##### Block Compression

##### 为什么不使用png和jpg等常见压缩格式

尽管像jpg、png的压缩率很高，但并不适合纹理，主要问题是不支持像素的随机访问，这对GPU相当不友好，GPU渲染时只使用需要的纹理部分。

##### 为什么我们需要纹理压缩格式

*    内存
*    带宽
##### 压缩纹理算法特点
*    解压速度
*    随机访问
*    压缩率和图像质量
*    编码速度

### Frame Graph

##### 目标
*    单一实现，与图形API无关
*    简化渲染管线配置
*    简化异步渲染和资源屏障
*    支持多GPU渲染，可指定调度策略

##### 流程
*    Setup
            在这个阶段并不产生任何GPU命令，所有的资源都是虚拟的
*    Compile
*    1.    剔除所有没有被引用的Resources和Passes
     2.    计算资源的生命周期
     3.    根据资源的用途创建实际的GPU资源
*    Execute
            简单地顺序遍历所有真正需要绘制的Pass
 


### 渲染系统

##### 光照
*    全局光照
*    1.    光照探灯
     2.    反射探灯
     3.    预计算光照数据
*    IBL
*    1.    Specular

               Pre-filtered Environment Map

               Brdf Lut
       
     3.    Diffuse

               Irradiance Map
*    BRDF模型
*    1.    Lambert模型
     2.    Phong模型
     3.    Blinn-Phong模型
     4.    Cook-Torrance模型

##### 后处理

*    颜色校正

*    抗锯齿

*    1.    超级采样抗锯齿

            优点：往往能得到最佳的效果
            缺点：它会带来巨大的性能消耗

     2.    多重采样抗锯齿

            图像保真度和性能之间找到最佳的平衡点

     3.    快速近似抗锯齿

            优点：是低端PC最佳的抗锯齿方案，它对GPU的要求不是很高，因为它直接平滑屏幕图像而不需要考虑到游戏中的3D模型

            缺点：边缘和纹理会变得有点模糊

     4.    时间性抗锯齿

            综合历史帧的数据来实现抗锯齿，这样会将每个像素点的多次采样均摊到多个帧中，相对的开销要小得多

##### 基于物理渲染

*    能量守恒

           出射光线的能量，永远不能大于入射光线的能量
*    基于物理相机
*    1.    快门速度

            产生运动模糊效果
*    2.    光圈

            产生景深效果
*    3.    感光度

            产生Grain效果

*    基于物理材质

*    1.    SG工作流

           Albedo Color

           Specular Color

           Glossiness

           Normal

           优点：可以自己控制非金属F0值

           缺点：F0可能用错从而导致破坏PBR原则，因为工作流程有些名词和传统的工作流太相似，但实际对应的数据可能是不一样的。RGB贴图多，占用内存多。

*    2.    基于物理相机

           快门速度：产生运动模糊效果

           光圈：产生景深效果

           感光度：产生Grain效果

*    3.    F0

           当光线笔直或垂直（以0度角）撞击表面时，该光线的一部分会被反射为镜面反射。使用表面的折射率（IOR），可以推导出反射量。这被称为F0。
*     4.    金属和非金属

           金属有良好的导热和导电性。
           导电金属中的电场为零，
           当由组成光波的电磁场碰到金属表面时，
           一部分光波被反射，
           而折射的部分全部被吸收
           非金属（绝缘体）的导电性能很差。
           对于绝缘体，折射光会被散射和吸收（有的会重新透出物体表面），
           所以反射光线的量远小于金属，
           而且有漫反射颜色。 

*     5.    MR工作流
 
           Base Color
  
           Roughness

           Metallic

           Normal

           优点：纹理占用内存少，因为金属和粗糙度贴图都是灰度图（单通道）
  
           缺点：F0不容易自己指定

##### 视效

*    粒子数据类型

         Billboard类型数据

         Mesh类型数据

         光束类型数据

         条带类型数据

*    组件

         系统

         发射器

         模块

         参数
     
*    粒子常见属性

         Acceleration

         Attraction

         Cammera

         Collision

         Color

         Lifetime

         Light

         Location

         Orbit

         Orientation

         Rotation

         Size

         Spawn

         Velocity

##### 环境光遮蔽

*    屏幕空间环境光遮蔽
*    光线追踪环境光遮蔽
*    水平基准环境光遮蔽
*    体素基准环境光遮蔽
*    
##### 大气

*    大气散射

         地球大气的渲染主要包含两种散射，瑞利散射以及米氏散射，瑞利散射主要构成了天空的颜色变化，而米氏散射则造成了太阳周围的光环效果

         相位函数

         瑞利散射

         米氏散射

         几何散射

         单次散射

         多重散射

*    介质传播特性

        参与介质中的粒子本身会吸收光能，转换成其他形式的能量，这样在传播路径上的光就会衰减出散射，即光遇到粒子时，
        粒子会分散的传播方向，因此也会减弱传播路径上的光入散射，从其他传播路径上散射到当前传播路径上的现象，这回加强当前路径上的光能量。
        粒子本身是发光的，这会加强传播路径上的光

##### 雾效

*    体积雾

        在摄像机视锥的每个点上都计算参与媒介的密度和光照

*    高度雾

        指数高度雾在地图上较低位置处密度较大，而在较高位置处密度较小。其过渡十分平滑，随着海拔升高，也不会出现明显切换
   
##### 云

*    体积云
*    1.    云层建模

            Fractal Brownian Motion
            Density-Height Functions
            Weather Texture
            云层覆盖率
            云层降雨概率
            云层种类

        
     2.    云层渲染

            In-Scattering Probability Function模拟当观察方向与太阳光方向一致时的in-scattering效果
            Henyey-Greenstein Phase Function用于模拟光线与星际尘云交互后各个方向上散射强度与入射光方向夹角的依赖规律
            Beer's Law用于描述光线穿过一个材质后的衰减作用
            Volumetric Scattering被水滴或者其他粒子比如灰尘等多吸收，这个过程称为Extinction（消散）或者吸收（absorption）穿出云层抵达人眼，
            这个称之为内散射in-scattering穿出云层但是并未进入人眼，称为外散射out-scattering

       
     5.    云层光照计算

     
*    面片云

*    基于公告板云

##### 渲染管线

*    群组渲染

         优点：相比于Tile的划分，进一步剔除了更多无关光源
         缺点：Light Culling流程比较复杂，需要多个pass完成

*    延迟渲染

         优点：渲染性能不再与场景复杂度耦合，避免了over draw
     
         缺点：Gubffer占用了较大的空间，Gbuffer的读写需要大量显存带框，对半透明物体支持不友好，
             对硬件MSAA支持不友好，需要硬件支持MRT，对大量自定义shader支持不友好。

*    分块渲染

         优点：减少了部分无关光源的计算
     
         缺点：需要维护光源列表信息，并维护，带来了一定的性能开销，基于屏幕的Tile划分还是比较粗糙，没有考虑深度值

*    正向渲染

         优点：实现简单，支持MSAA和半透明渲染，带宽消耗小
         缺点：场景复杂度和光源数量相关，会有大量的over draw

##### 地形

*    地形材质混合

        Texture Splatting技术，，地表纹理使用多种不同的纹理混合，使用一张叫做Splate map的权重图来记录这些纹理的权重

*    虚拟纹理

         Virtual texture
         Physical texture
         Page table
         优势：渲染带宽降低：可以把多层地形材质实时混合好，可以Instancing/GpuDriven

*    地形几何

         网格
         高度图

##### 阴影

*    Distance Field Shadow
*    Shadow Mapping算法流程：

          步骤一：从光源处出发，向光照的方向看去，来构造出光照空间。然后在光照空间，我们渲染需要产生阴影的物体，
          此时将深度写入到ZBuffer中，得到保存最近处物体的深度值的Shadow Map

          步骤二：然后我们再次正常渲染物体，在渲染时，我们根据渲染物体的世界坐标，变换到上一阶段的光照空间坐标，
          再计算出该点在Shadow Map中的深度值并进行比较，如果相对光源的距离比Shadow Map中的深度要大，
          就说明该点处在阴影中，否则就说明不在阴影中。

          Shadow Bias

          Cascade Shadow Map

          Variance Shadow Map

          PCF

          PCSS



### Nanite

#####    GPU Driven Render Pipeline

*    Culling

*    1.    三角形剔除

            Backface Culling
       
            Small Triangle Culling
       
            Occlusion Culling
*    2.    Cluster 剔除（Coarse）

*    3.    提交

           Material Batch

           Indirect Draw

           Texture Batch

           Virtual Texture

           Bindless Texture

*    目标：GPU承担更多的提交和剔除工作
       
#####    Visibility Buffer

*    解决了延迟渲染的问题：带宽高，渲染性能与场景复杂度绑定，容易造成over draw，对MSAA支持不友好

*    流程

         Visibility Pass：对场景进行光栅化，将Primitive ID和Material ID保存到visibility buffer中
     
         Worklisk Pass：构建并Worklist，将屏幕划分成很多tile，
             根据使用到某个Material ID的tile加到该Materail ID的Worklist里，作为下一步的索引
     
         Shading Passes：拿到几何和材质信息，对表面着色

#####    Virtualized Geometry Nanite

*    Nanite Mesh Build Process

         Group
     
         merge
     
         Simplify

         Split

*    Deferred Materail

*    1.    思想：将材质分类，找出每个材质对应的像素进行Shading

*    2.    Material ID：表示当前像素属于哪个材质

*    3.    Material Shading

           正常流程：为每个材质执行一次全屏渲染，跳过那些未被当前材质覆盖的像素，需要对每个材质都执行一遍渲染，
               对每个像素都执行一遍是否被材质覆盖的检测，效率较低。
       
           Material Culling：将Material ID存成深度值，将屏幕分成Tile，不需要进行一个全屏的材质的绘制进行基于tile尺寸的绘制


### Lumen

##### Lumen流程

*    Shading Full Pixels with Screen Space Probes
*    Surface Caching
*    1.    Mesh Card

            功能：可以看成是放在6个轴对称方向上的相机，通过正交投影的方式来光栅化Mesh，从而获取Mesh的各种属性（Albedo，Normal,Depth等等）对应surface cache

            离线生成：Mesh-Surfel-Surfel Clusters-Cards最多2级LOD
       
*    2.    Surface Cache

           内容：5张Altas-Albedo，Normal，Depth，Emissive，Opacity

           生成：Two Pass， Card Capture，Fix texel budget per frame(512x512),Sort by distance to camera and GPU feedback,
           Copy card capture to surface cache and compress,Card capture分辨率，根据card bounds最大extent投影到屏幕像素的长度决定，
           从8到1024，不一定是正方形，根据card的bounds长宽比确定

           管理：Surface Cache Altas size；4096x4096,Pysical Page size:128x128,virtutal page机制分配空间，通过page table进行物理地址映射

*    Fast Ray Trace in Any Hardware
*    1.    有向距离场（SDF）

            原理 ：有向距离场在每个点将距离最近表面的距离保存到体积纹理中。网格体外的每个点保存的距离为正值，网格体内的每个点保存的距离为负值
           
*    2.    实用属性

            在追踪光线时安全地跳过空白空间，因为到最近表面的距离已经明确（有时称这种方法为球体追踪）。只需区区几步就可以判定出交叉点。
            对距离场进行光线追踪将生成可见性效果，也就是说如果光线和网格体交叉，光线就会投射出阴影。

            在追踪光线时，通过追踪经过遮挡物的距离最近的光线就可以计算出近似的锥体交叉点，而不产生额外成本。这种近似法可以利用距离场来实现非常柔和的区域阴影和天空遮罩。
            这个属性是距离场环境光遮蔽的关键，因为少量的锥体即可接收器点的整个半球计算出柔和的可见性。

*    3.    局限性

            通过全局位置位置偏移或置换使网格体变形的材质可能会导致自阴影失真，因为距离场表达是离线生成的，并不知道有这些变形仅投射刚性网格体的阴影

*    4.    全局距离场

            全局距离场是分辨率较低的距离场，跟随摄像机的同时，在关卡中使用有向距离场遮蔽。这会创建每个Object网格体距离场的缓存，然后将它们合成到围绕摄像机的若干体积纹理中，称为裁剪图。由于只有新的可见区域或受到场景修改影响的可见区域才需要更新，合成过程中不会有太多消耗。

*    Radiance Injection

*    1.    直接光照

            Cull lights to 8x8 tiles Select first 8 lights per tile 1 bit shadow mask First smmple Shadow Map,then trace Offsecreen Shadows
       
*    2.    更新策略

            Fixed update budget Select pages to update based based on priority,Priority = LastUsed-LastUpdated,
            Priority queue using radix sort 1024x1024 texels for direct lighting,512x512texels for indirect lightning

*    3.    间接光照

            N+2 bounces through feedback,Probe 4x4 hemispherical probe per 4x4 tile Jitter probe placement and ray directioins.
            Trace in last frame's Voxel Lighting. Lighting Gather ,Bilinear interpolation of 4 probes plane weighting.Visibility weighting using probe hitT.
            Convert to SH.Shading pixels on surface cache
       
*    4.    Voxel Lighting

           动机：Global SDF can't sample surface cache.Merge all cards into lobal clipmaps centered around the camera
       
           Structure:4 clipmaps of 64x64x64 voxels.Radiance per 6 directions per vovel.Sample and interppolate 3 directions using normal
       
           Visibility Buffer:Track object updates and set modified bricks on GPU.
           Voxelize modified bricks by tracing rays.6 rays per voxel.
           Cull objects to 4^3 bricks.One thread per mesh SDF per trace.Cache hits in a visibility buffer HitT I Mesh Index.
           InterlockedMin write hit to visibility buffer

           Updating:Shade the entire visibility buffer every frame.Sample lighting from surface cache(Final Lighting)

# 动画系统

### 动画技术基础

##### 蒙皮动画实现

*    坐标空间转换
*    生物的骨骼结构
*    游戏中的人形骨骼
*    GamePlay相关的关节
*    根骨骼
*    骨骼绑定
*    绑定姿势
*    T-pose
*    A-pose
*    谷歌姿势

##### 游戏中的2D动画技术

*    精灵动画
*    Live2D
*    2D Skinned Animation

##### 游戏中的3D动画技术

*    DoF（Degrees of Freedom）
*    Rigid Hierarchical Animation
*    Per-vertex Animation
*    Morph Target Animation
*    3D Skinned Animation
*    基于物理的动画Physics-based Animation

            布娃娃系统Ragdol  
            布料与流体模拟
            IK（Inverse Kinematics）
*    动画内容创作
*    DCC

        动画捕捉
        Motion Capture

##### 2D旋转中的数学

##### 3D旋转中的数学

*    欧拉角
*    欧拉角中的顺序依赖
*    万向节死锁
*    欧拉角的缺点

        顺序依赖
        万向节死锁
        难以插值、组合等
*    四元数

        2D旋转与复数
        四元数的定义
        欧拉角到四元数的转换
        使用四元数进行转换
        四元数到旋转矩阵的转换
        给定旋转轴的四元数旋转
     
##### 关节姿势（Joint Pose）

*    旋转Orientation
*    位置Position
*    缩放Scale
*    仿射矩阵
*    局部空间到物体空间
*    插值
*    单关节蒙皮
*    蒙皮矩阵
*    在内存中存储骨骼
*    蒙皮矩阵调色板
*    多骨骼的权重蒙皮
*    权重蒙皮的混合
*    动画片段（clip）
*    姿势的插值
*    NLERP的最短路径插值
*    SLERP
*    简单动画的运行时管线

##### 动画DCC流程

*    网格制作
*    网格调整
*    骨骼绑定
*    添加GamePlay关节
*    添加根骨骼
*    蒙皮
*    动画制作
*    动画导出

##### 动画压缩

*   动画片段存储
*   动画数据尺寸
*   动画轨道（track）数据之间的差别
*   关节动画数据之间的差别
*   DoF缩减
*   关键帧

        关键帧提取
*    浮点数压缩
*    四元数压缩
*    误差累积
*    精读衡量
*    误差补偿

##### 动画重定向

*    重定向流程
*    Morph Animation的重定向

##### 面部动画
*    面部编码系统（FACS）
*    Action Unit
*    Key Pose Blending
*    Morph Target Animation
*    UV Texture Facial Animation
*    Muscle Model Animation

### 动画技术进阶

##### 动画混合

*    LERP
*    混合权重的计算
*    混合时间轴对齐
  

##### 混合空间Blend Space

*    1D混合空间
*    2D混合空间
*    分部混合Skeleton Masked Blending
*    叠加混合Additive Blending
 

##### 动画状态机

*    ASM的定义
*    Cross Fades
*    分层ASM

##### 动画混合树

*    Blend Tree
*    LERP blend node
*    additive blend node
*    动画混合树的节点
*    动画树的控制信号

##### 反向动力学Inverse Kinematics

*    基础概念

      终端效应器End-Effectors
      IK
      FK

*    Two Bone IK
*    多关节IK
*    关节约束
*    启发式算法
*    循环坐标下降算法CCD
*    FABRIK

        FABRIK的约束

*     多终端效应器难题
*     雅可比矩阵法
*     IK前沿方向
     

# 物理系统

### 物理系统基础概念

##### 刚体Physics Actor

*    静态刚体static
*    动态刚体dynamic
*    触发器（trigger）
*    受控刚体kinematic

##### 形状

*    分类

     球
     胶囊
     方盒
     凸包
     三角网格
     高度场
*    碰撞体制作标准
*    属性
   
     质量与密度
     质心（COM）
     摩擦系数
     回弹系数

##### 运动

*    第一牛顿定律
*    第二牛顿定律
*    
     不变外力下的运动
     变化外力下的运动
     
*    运动状态

*    游戏中对运动离散模拟

     时间积分
     欧拉法
     前向欧拉法、显式欧拉法
     后向欧拉法、隐式欧拉法
     半隐式欧拉法
    
##### 刚体动力学

*  质点动力学
*  刚体动力学
*  朝向
*  角速度
*  角加速度
*  转动惯量
*  角动量
*  扭矩
*  应用：台球动力学

##### 力与冲量

##### 碰撞检测

*  粗阶段

   动态BVH树
   排序与扫描Sort and Sweep
   
*  精细阶段

*  1.  概念

     闵可夫斯基和/差
     凸多边形闵可夫斯基和性质
     相交对应闵可夫斯基差中的原点
*  2.  基于闵可夫斯基差的方法

      分离轴定理
         凸性
         相交的必要条件
         分离判据
         二维情形
         三维情形
      GJK算法
         分离情形
         相交情形
*  3.  基础形状求交检测

      球-球求交
      球-胶囊求交
      胶囊-胶囊求交

##### 碰撞解决

*  惩罚力法
*  求解速度约束

      拉格朗日力学
      碰撞约束
      迭代求解
*  求解位置约束

##### 场景查询

*  射线检测raycast
*  形状扫描sweep
*  求交overlap
*  碰撞组过滤

##### 性能、精度与确定性

*  模拟岛
*  休眠
*  连续碰撞检测:冲击时间-保守步进法
*  确定性模拟

### 物理系统应用

##### 角色控制器

*  与刚体动力学的差异
*  基本组成
*  与环境的碰撞
*  自动阶跃（auto stepping）
*  坡度限制与强制滑坡
*  更新大小
*  推动物体
*  移动平台

##### 布娃娃模拟

*  用途
*  骨骼与刚体的映射
*  人体关节约束
*  约束参数
*  动画与布娃娃的混合过渡
*  富力布娃娃

##### 布料模拟（方法）

*  基于网格的布料模拟
*  基于动画的布料表现

   物理网格vs渲染网格
   刷布料约束
   布料物理材料
   求解
     弹簧-质点系统
     Verlet积分
     PBD(Positioin Based Dynamics)
     自碰撞
   
*  基于刚体的布料模拟

##### 载具模拟

*  真实感-风格化谱系
*  建模
*  力

     牵引力
     弹簧力
     轮胎力
*  质心

     转向过度与转向不足
*  重量转移
*  转向角

     Ackermann转向
   
*  轮胎接触

##### 破坏模拟

*  概念

     分块层级
     连接图
     连接强度
     计算损伤
   
*  模型破碎模拟
     维诺图
     二维
     三维
     不同的破碎图案
*  破坏系统
*  增加真实感
*  破坏系统引入的问题
*  常见的破坏SDK

##### PBD/XPBD

*  拉格朗日力学约束建模
*  拉伸约束
*  约束投影
*  工作流
*  XPBD

# 音效

### 音频

##### 声障

##### 声笼

##### 空间化音频

*  平移

     听者几何体
     扬声器几何体
     中央声道
     音频平移
       线性平移
       等功率平移
   
*  音效衰减

     衰减函数
       线性
       对数
       反函数
       对数反函数
       自然音效
     自定义
     衰减形状
       球体
       胶囊体
       盒体
       锥体

*  双耳音频空间化

### 声音基础

##### 声音三要素

*  响度
*  音高
*  音色

##### 脉冲编码调制

*  采样
*  量化
*  编码

# GamePlay

### 复杂的游戏性及其基本要素

##### 事件机制

*    发布-订阅模式
*    事件定义

         硬编码
         反射与自动代码生成
     
*    事件回调函数注册

         对象生命周期及回调安全保证
         对象的强引用
         对象的弱引用
     
*    事件分发机制

         立即分发
         延迟分发
             消息队列


##### 如何编码游戏逻辑

*    脚本语言的优点及工作原理
*    对象生命周期管理
         在原生引擎代码中管理对象生命周期
         在脚本中管理对象生命周期
*    脚本系统运行框架

         由原生引擎代码支配游戏世界
             脚本扩展原生引擎功能
         由脚本支配游戏世界
             脚本实现绝大部分游戏逻辑
*    脚本热更新
*    脚本语言的选择
         多种脚本语言的对比
     
##### 可视化脚本

*    可视化脚本是一种编程语言

         编程语言的要素及相应可视化示例
     
*    提供用户友好型的交互方式

         启发式的节点创建
         便捷的调试工具
     
*    可视化脚本的问题

         不便于合并
         需要良好的布局规范
*    3C

         控制（Control）
             控制手感优化
             辅助瞄准
             基于游戏环境做控制调整
         角色（Character）
             角色的移动
             多种移动方式
             与其他系统协作
             移动状态机
         相机（Camera）
             相机的绑定
             弹簧臂
             多种相机效果
             相机抖动
             滤镜
             基于玩家主观感觉做优化

     

### 基础AI系统

##### 转向

*    从路点到运动
*    转向行为

         寻找/逃跑
         速度匹配
         对其
     
##### 群体模拟

*    微观模型

        基于规则Boids
     
*    宏观模型

        流场
*    介观模型
*    碰撞规避

         基于力的模型
         基于速度的模型
             VO
             RVO
             ORCA
     
##### 感知

*    内部信息
*    外部信息

         静态空间信息
         动态空间信息
             影响力图
             其他游戏对象
         角色信息

*    感知模拟
     
     
##### 经典决策算法

*    有限状态机

         层级有限状态机

*    行为树

         执行节点/叶子节点
             行为节点
             条件节点
         控制节点
             序列节点Sequence
             选择器Selector
             并行节点Parallel
         运行
         实现优化
             装饰节点
             前置条件
             黑板变量
         
             
##### 寻路

*    路径平滑

         漏斗算法

*    工作流

*    地图表示

         可通行区域
         形式
             路点网络
             格子
             寻路网格
             凸多边形
             稀疏体素八叉树Sparse Voxel Octree
*    路径发现

         数学抽象
             图搜索算法
         深度优先搜索
         广度优先搜索
         最优优先算法
             Dijkstra算法
             A*算法
             计算开销
             启发函数
             格子情形
             寻路网格情形
*    进阶内容：寻路网格生成

         体素化
         区域分割
             分水岭算法
         网格生成
         高级特性
             多边形标记
             分块
             网格外链接Off-mesh link

### 构建高级的AI系统

##### Machine Learning（机器学习；ML）

*    监督学习
*    无监督学习
*    半监督学习
*    强化学习
         马尔科夫决策过程
             状态
             动作
             奖励
                 累计奖励最大
         如何利用强化学习构建AI
             状态抽象
                 长度固定的统计变量
                 长度不固定的序列数据
                 图像数据
             动作抽象
             奖励设置
                 AlphaStar
                 OpenAIFive
             网格设计
                 MLP
                 CNN
                 LSTM
                 Transformer
             训练策略
                 监督学习
                 强化学习
                     自博弈
                     群体演化
##### AI Planning

*    Hierarchical Tasks Network（分层任务网络；HTN）

         原子任务
             前提条件
             动作影响对World State的改变描述
         复合任务
             前提条件
             拆分方法
*    Goal-Orientated Action Planner（目标导向的动作规划器；GOAP）

         目标集
             对World State中的部分属性做是否满足的判断
         动作集
             前提条件
             动作损耗
             动作影响
                 对World State的改变描述
         逆向规划
     
*    Monte Carlo Tree Search（蒙特卡洛树搜索；MCTS）

         思考
             选择
                 Tree Policy
                     UCB公式
                         平衡开发与探索问题
             拓展
             仿真+评估
                 Rollout Policy
                 评估函数
             反向传播
         决策
             Default Policy
                 最保守的选择
                 最佳的选择
                 最鲁棒的选择
                 最激进的选择


# 工具链

### 界面（GUI)

##### UI模式

*    即时模式（IMGUI）
*    保留模式（RMGUI）

##### 架构模式

*    MVC
*    MVP
*    MVVM

### 资产管理

##### 资产格式

*    文本（Text）
*    二进制（Binary）

##### 资产加载

*    序列化与反序列化
*    版本兼容

##### 资产结构设计

*    资产引用
*    资产实例

         数据拷贝
         数据继承



### 数据结构设计

##### 数据定义（Schema）

*    基础元素
*    继承
*    引用
*    两种设计方式

         独立的Schema定义文件
         代码内部定义
     
*    不同场景下的引擎数据

         Runtime
         Storage
         Tools
     
### C++代码反射

##### 代码分析

*    抽象语法树（AST）
*    Clang

##### 反射信息收集

*    Tags

##### 代码生成

*    代码渲染

        Mustache
##### 运行时反射信息注册

### 鲁棒性设计

##### Command模式

*    定义
*    UID
*    序列化与反序列化
*    基础command类型

         Add
         Delete
         Update
     
### 软件架构

##### Stand-alone架构

##### In Game架构

*    Play in Editor

### 常见编辑器

##### World Editor

*    架构
*    数据抽象

         布局信息（Layout）
         地形（Terrain）
         环境（Environment）
             多系统间的数据交互（eg.Rule System）
##### Sequencer

*    数据绑定
*    关键帧
*    插值
*    
### 插件

##### 架构

*    Plugin Manager
*    Interfaces
*    SDK

##### 版本控制

### 协同编辑

##### 资产拆分

*    按逻辑分层
*    按位置分块
*    One File Per Actor

##### 在一个场景内协同编辑

*    同步操作

*    分布式操作的一致性问题

         锁
             实例锁
             资产锁
         操作转换（OT）
         无冲突复制数据类型（CRDT）
     
*    工作流

# 网络

### 网络基础

##### 网络协议

*    基于UDP的可靠实时通信实现

         自动重传（ARQ）
         前向纠错（FEC）
     
*    Socket套接字

         TCP协议
             面向连接
             可靠、有序
             流控
             阻塞控制
         UDP协议
             无连接
             不可靠
             无流控
             无拥塞控制
     
*    网络分层

         OSI七层模型
             物理层
             数据链路层
             网络层
             传输层
             会话层
             表示层
             应用层
     
##### 时钟同步

*    网络时间协议（NTP）

         四个对应时间戳以及误差调整
             1.客户端发送时间戳
             2.服务端接收时间戳
             3.服务端发送返回时间戳
             4.客户端接收时间戳
         NTP在计算传输时延的时候默认上行延迟和下行延迟相等
     
*    基于流的消除高阶的时间同步协议

         游戏开始的时候直接进行类似NTP的对时操作
         利用多次对时消除误差过大项来达到时间差校准
     
##### 通信方式

*    NetMessage

         传统的消息机制通常是异步通信
*    RPC

         Socket编程所面临的诸多问题
             消息格式不统一
             封包和解包
             消息分发处理
             不是一种自然的编程模型
         RPC实现通信的基本原理
             1.客户端发起函数调用（Client functions）
             2.客户端通过Client Stub进行消息的封装（序列化）及传输
             3.Server端通过Server Stub（或者叫Skeleton）进行解码并找到对应的函数进行相关处理，以及返回处理结果
             4.Client Stub接收消息（反序列化),得到结果
         使用RPC的好处
             集中式代码
             易于编程
             通信透明
     
##### 网络拓扑

*    DS

         特点
             具有权威性
             负责模拟整个游戏世界
             负责分发数据给每个玩家
             具备高性能
         优点
             反作弊易实现
             能让更多的玩家一同游戏
             游戏响应不取决于每个玩家的网络状态
         缺点
             服务器花费较高
             服务端承担更多的逻辑处理
             服务器故障会影响到玩家
     
*    P2P

         特点
             客户端之间互相通信
             客户端承担游戏逻辑处理
         优点
             一个客户端挂掉，不影响其他玩家
             不依赖于服务器，游玩方便
         缺点
             易作弊
             需要良好的网络连接
             玩家人数受限

### 网络同步

##### 同步分类

*    快照同步
*    帧同步
*    状态同步

##### 同步的效果

*    多端一致

##### 快照同步

*    全量快照

*    增量快照

*    带宽对比

         全量快照大
         增量快照小
     
*    快照同步的缺点

         随着游戏复杂，快照越来越大
         带宽浪费
         服务器压力大
     
##### 帧同步

*    Bucket Synchronization

*    Deterministic Lockstep

*    帧同步需要面对的挑战与解决：多端不一致问题

         浮点数
         随机数
         容器与排序算法等
         数学工具
     
*    掉线与重连问题

         掉线重连的基本流程
             掉线
             重连
             接收游戏开始到现在所有请求
             追帧
         重连的问题：耗时
         重连的优化
             大重连（客户端崩溃，内存中无数据）
                 通过快照，加速重连
                     客户端定时快照，关键帧快照，序列化到磁盘
                     服务器做定时快照（更换终端登录，用这种优化）
             小重连（客户端未崩溃，内存中有数据）
                 客户端定时快照，关键帧快照
     
*    作弊问题

         多人PVP
         双人PVP
         帧同步本地有全部数据，透视外挂等
     
*    滞后和延迟问题

         缓冲池
     
*    帧同步的优缺点

         优点
             低带宽
             开发效率高
         缺点
             确定性实现困难
             作弊（全图挂）问题较难避免
             断线重连需要优化
     
*    不一致问题的定位方法

         定时上传游戏数据checksum
         如果不同玩家checksum不一致
             上传游戏玩家最近一段时间的游戏日志
             通过对比进行定位
     
*    逻辑和渲染分离

         不同帧率，独立运行
         服务器可以跑逻辑帧
             断线重连加速
             一定程度上防作弊
     
##### 状态同步

*    状态分类

         属性（血量，攻击力，地图坐标...)
         事件（开火，移动...)

*    流程的阶段拆分

         Authorized
             eg.开火
         Server
             收到开火请求，同步给玩家
         Replicated
             模拟Authorized开火
     
*    如何解决延迟

         哑客户端（客户端不做预测）
             发出移动请求
             等待服务器回复
             收到服务器回复，并作出移动
         解决
             客户端预测
                 客户端发送移动请求后，在收到服务器回复之前，就根据现有状态对未来的移动做出预测
                 收到服务器的包，预测是对的；
                 在收到服务器包后，什么也不用做，已经在正确的位置上了
         预测错误
             服务器和解
     
##### 游戏同步举例

*    角色位移同步

         必要性
             远程客户端发送来的同步数据存在传输延迟
             受机器性能影响，远程客户端的数据同步频率低于渲染帧率
             网络包到达时间会受网络抖动影响导致间隔不一致
         内插值&外插值
             内插值
                 实现方法
                 缓存玩家位置
                 利用缓存之间的位置进行插值
                 问题
                     物体移动速度较大时容易产生结果判断不一致
             外插值
                 外插值的实现方法（航位推算）
                     投影速度混合法
                         使用归一化参数平滑运动轨迹
                     外插值的碰撞处理
                         发生碰撞的时刻让客户端接管物理模拟
         内插值和外插值的使用场景
             内插值的使用场景
                 角色的移动不符合真实世界的物理模型 加速度非常大
                 对于角色位置的精度要求很高
                 典型例子：FPS类游戏
             外插值的使用场景
                 游戏对象的移动遵守物理规则，加速度不会突然变化
                 游戏对象的移动速度会比较快，延迟会导致位置出现巨大的偏差
                 典型例子：载具系统，赛车游戏
             混合使用
                 对载具系统采用外插值
                 对人物采用内插值
*    命中判定

         如何做判定
             客户端判定
                 基本流程
                     客户端判定命中结果
                     服务器做命中的校验
                 优势
                     命中位置精准，像素级
                 问题
                     容易作弊
             延迟补偿（服务器判断）
                 延迟补偿的问题
                     拐角问题
                         进入拐角问题
                         Peeker and holder问题（探头打人）
                     解决（能够减缓，不能消除）
                         添加前摇
                         添加特效
                         客户端预测命中过程
                             不触发命中结果
                             命中结果等待服务器返回
                 延迟补偿
                     原因
                         因为有延迟，也就是开枪打中了敌人过去的位置，等到开枪事件到达服务器上，敌人已经不再开枪的位置了，
                         在服务器上，回溯到你开枪时候敌人的真实位置做判定，一切以服务器为准；
                         开枪的时间，回溯到开枪时候敌人的位置，做命中判定
                     难点
                         如何回溯，回溯多久
##### 状态同步和帧同步的对比

*    网络带宽

         帧同步
             小
         状态同步
             大
*    开发效率

         帧同步
             开发较快，debug较困难
         状态同步
             较慢
     
*    支持玩家的数量

         帧同步
             少量玩家
         状态同步
             大量玩家
     
*    游戏响应

         帧同步
             较慢
         状态同步
             较快
     
*    跨平台

         帧同步
             相对复杂
         状态同步
             相对简单
     
*    回放文件大小

         帧同步
             小
         状态同步
             大
*    作弊

         帧同步
             部分作弊较难避免，如透视
         状态同步
             可以对作弊做多种优化
     
### 服务器架构

##### 系统举例

*    大厅系统
*    用户管理系统
*    交易系统
*    社交系统
*    匹配系统
*    数据存储举例

         Mysql
         Mongo
         Redis
     
##### 分布式系统

*    分布式系统挑战

         互斥问题
         幂等性
         故障与部分失效
         不可靠的网络
         分布式问题传染
         一致性和共识算法
         分布式事务
     
*    负载均衡

         随机
         轮询
         一致性哈希
     
*    服务发现

         Etcd
         Zookeeper
##### 可扩展游戏世界（实现方案）

*    Zoninng

         在大世界中将大量玩家分布

*    Instancing

         独立运行大量的游戏区域
         减少拥挤、竞争
     
*    Replication

         允许大量玩家高度聚集游玩
     
### 游戏优化

##### 带宽优化

*    数据压缩
*    对象更新频率
*    对象相关性

         静态区域
         AOI
             暴力法
             九宫格
             十字链表
             PVS
     
##### 反作弊

*    作弊手段分类

         读取、篡改内存
         读取网络包
         AI Cheat
         修改本地文件，贴图等
     
##### 反作弊方法

*    混淆加密内存
*    加壳
*    本地文件校验
*    网络包加密

         非对称加密分发密钥
         对称加密传输数据
     
*    VAC & EAV
*    基于统计数据反作弊
*    检测已知的作弊程序

# 面向数据编程与任务系统

### 游戏引擎并行框架

##### Fixed-thread

##### Thread fork-join

##### Unreal并行框架

*    Named Thread 与Worker Thread TaskGraph

##### Job System
*    协程介绍

         携程与线程的对比
         协程实现方式
             有栈协程
             无栈协程
     
*    基于Fiber的Job System

         Job调度
             Job队列
                 全局队列
                 线程局部队列
                 两种访问方式
                     先进先出
                     后进后出
         基本构成
             Job为实际任务
             Fiber提供任务执行的上下文
             Work Thread是实际执行的单元
         Work Thread数量与CPU核数匹配
         Job系统的利弊分析
     
### 实体-组件-系统ECS

##### 回顾：基于组件的设计

##### 概念

*    实体Entity
*    组件Component
*    系统System

##### 实现举例

*    Unity DOTS

         Unity ECS
             原型Archetype
             数据排布
             系统实现
         Unity C#任务系统
             原生容器
             安全性系统
         Burst编译器

*    Unreal Mass框架

         实体Entity实现
         组件Component实现
             碎片Fragment
         系统System实现
             碎片请求
             执行

### 面向数据编程

##### 其他编程范式

*    面向过程编程
*    面向对象编程

         在游戏引擎中的问题
     
##### 缓存

*    局域性原则
*    LRU策略
*    缓存行Cache line
*    缓存缺失Cache miss

##### 硬件环境

*    处理器-内存性能差距

##### SIMD

##### 原则思想

*    万物皆数据
*    指令也是数据
*    让代码与数据在内存中保持精致

##### 性能敏感数据排布

*    减少内存依赖
*    AOS vs. SOA

##### 原则思想

*    万物皆数据
*    指令也是数据
*    让代码与数据在内存中保持紧致

##### 性能敏感编程

*    减少顺序依赖
*    false sharing
*    分支预测
*    基于存在性处理

### 并行编程基础知识

##### 操作系统的并行支持

*    进程与线程
*    线程的上下文切换

##### 多任务的类型

*    抢占式
*    非抢占式

##### 并行计算问题

*    易并行问题
*    不易并行问题

         解决数据竞争
             阻塞方法
                 锁原语
             非阻塞方法
                 原子操作
                 内存序问题
