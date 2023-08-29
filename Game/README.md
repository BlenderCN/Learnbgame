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
    1.  虚拟文件系统
    2.  Handle
*  资产生命周期
    1.    不同资源有不同的生命周期
    2.    尽可能减少资源的内存申请与释放
    3.    垃圾回收
   
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
*    1.    Billboard类型数据
     2.    Mesh类型数据
     3.    光束类型数据
     4.    条带类型数据
*    组件
*    1.    系统
     2.    发射器
     3.    模块
     4.    参数
*    粒子常见属性
*    1.    Acceleration
     2.    Attraction
     3.    Cammera
     4.    Collision
     5.    Color
     6.    Lifetime
     7.    Light
     8.    Location
     9.    Orbit
     10.   Orientation
     11.   Rotation
     12.   Size
     13.   Spawn
     14.   Velocity

##### 环境光遮蔽

*    屏幕空间环境光遮蔽
*    光线追踪环境光遮蔽
*    水平基准环境光遮蔽
*    体素基准环境光遮蔽
*    
##### 大气
*    大气散射
*    1.    地球大气的渲染主要包含两种散射，瑞利散射以及米氏散射，瑞利散射主要构成了天空的颜色变化，而米氏散射则造成了太阳周围的光环效果
     2.    相位函数
     3.    瑞利散射
     4.    米氏散射
     5.    几何散射
     6.    单次散射
     7.    多重散射

*    介质传播特性

        参与介质中的粒子本身会吸收光能，转换成其他形式的能量，这样在传播路径上的光就会衰减出散射，即光遇到粒子时，粒子会分散的传播方向，因此也会减弱传播路径上的光入散射，从其他传播路径上散射到当前传播路径上的现象，这回加强当前路径上的光能量。粒子本身是发光的，这会加强传播路径上的光

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
            Volumetric Scattering被水滴或者其他粒子比如灰尘等多吸收，这个过程称为Extinction（消散）或者吸收（absorption）穿出云层抵达人眼，这个称之为内散射in-scattering穿出云层但是并未进入人眼，称为外散射out-scattering

       
     5.    云层光照计算

     
*    面片云

*    基于公告板云

##### 渲染管线
*    群组渲染
*    1.    优点：相比于Tile的划分，进一步剔除了更多无关光源
     2.    缺点：Light Culling流程比较复杂，需要多个pass完成

*    延迟渲染
*    1.    优点：渲染性能不再与场景复杂度耦合，避免了over draw
     2.    缺点：Gubffer占用了较大的空间，Gbuffer的读写需要大量显存带框，对半透明物体支持不友好，对硬件MSAA支持不友好，需要硬件支持MRT，对大量自定义shader支持不友好。

*    分块渲染
*    1.    优点：减少了部分无关光源的计算
     2.    缺点：需要维护光源列表信息，并维护，带来了一定的性能开销，基于屏幕的Tile划分还是比较粗糙，没有考虑深度值

*    正向渲染
*    1.    优点：实现简单，支持MSAA和半透明渲染，带宽消耗小
     2.    缺点：场景复杂度和光源数量相关，会有大量的over draw

##### 地形
*    地形材质混合

        Texture Splatting技术，，地表纹理使用多种不同的纹理混合，使用一张叫做Splate map的权重图来记录这些纹理的权重

*    虚拟纹理
*    1.    Virtual texture
     2.    Physical texture
     3.    Page table
     4.    优势：渲染带宽降低：可以把多层地形材质实时混合好，可以Instancing/GpuDriven

*    地形几何
*    1.    网格
     2.    高度图

##### 阴影
*    Distance Field Shadow
*    Shadow Mapping算法流程：
*    1.    步骤一：从光源处出发，向光照的方向看去，来构造出光照空间。然后在光照空间，我们渲染需要产生阴影的物体，此时将深度写入到ZBuffer中，得到保存最近处物体的深度值的Shadow Map
     2.    步骤二：然后我们再次正常渲染物体，在渲染时，我们根据渲染物体的世界坐标，变换到上一阶段的光照空间坐标，再计算出该点在Shadow Map中的深度值并进行比较，如果相对光源的距离比Shadow Map中的深度要大，就说明该点处在阴影中，否则就说明不在阴影中。
     3.    Shadow Bias
     4.    Cascade Shadow Map
     5.    Variance Shadow Map
     6.    PCF
     7.    PCSS



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
*    1.    Visibility Pass：对场景进行光栅化，将Primitive ID和Material ID保存到visibility buffer中
     2.    Worklisk Pass：构建并Worklist，将屏幕划分成很多tile，根据使用到某个Material ID的tile加到该Materail ID的Worklist里，作为下一步的索引
     3.    Shading Passes：拿到几何和材质信息，对表面着色

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

           正常流程：为每个材质执行一次全屏渲染，跳过那些未被当前材质覆盖的像素，需要对每个材质都执行一遍渲染，对每个像素都执行一遍是否被材质覆盖的检测，效率较低。
       
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

           生成：Two Pass， Card Capture，Fix texel budget per frame(512x512),Sort by distance to camera and GPU feedback,Copy card capture to surface cache and compress,Card capture分辨率，根据card bounds最大extent投影到屏幕像素的长度决定，从8到1024，不一定是正方形，根据card的bounds长宽比确定

           管理：Surface Cache Altas size；4096x4096,Pysical Page size:128x128,virtutal page机制分配空间，通过page table进行物理地址映射

*    Fast Ray Trace in Any Hardware
*    1.    有向距离场（SDF）

            原理 ：有向距离场在每个点将距离最近表面的距离保存到体积纹理中。网格体外的每个点保存的距离为正值，网格体内的每个点保存的距离为负值
           
*    2.    实用属性

            在追踪光线时安全地跳过空白空间，因为到最近表面的距离已经明确（有时称这种方法为球体追踪）。只需区区几步就可以判定出交叉点。对距离场进行光线追踪将生成可见性效果，也就是说如果光线和网格体交叉，光线就会投射出阴影。

            在追踪光线时，通过追踪经过遮挡物的距离最近的光线就可以计算出近似的锥体交叉点，而不产生额外成本。这种近似法可以利用距离场来实现非常柔和的区域阴影和天空遮罩。这个属性是距离场环境光遮蔽的关键，因为少量的锥体即可接收器点的整个半球计算出柔和的可见性。

*    3.    局限性

            通过全局位置位置偏移或置换使网格体变形的材质可能会导致自阴影失真，因为距离场表达是离线生成的，并不知道有这些变形仅投射刚性网格体的阴影

*    4.    全局距离场

            全局距离场是分辨率较低的距离场，跟随摄像机的同时，在关卡中使用有向距离场遮蔽。这会创建每个Object网格体距离场的缓存，然后将它们合成到围绕摄像机的若干体积纹理中，称为裁剪图。由于只有新的可见区域或受到场景修改影响的可见区域才需要更新，合成过程中不会有太多消耗。

*    Radiance Injection

*    1.    直接光照

            Cull lights to 8x8 tiles Select first 8 lights per tile 1 bit shadow mask First smmple Shadow Map,then trace Offsecreen Shadows
       
*    2.    更新策略

            Fixed update budget Select pages to update based based on priority,Priority = LastUsed-LastUpdated,Priority queue using radix sort 1024x1024 texels for direct lighting,512x512texels for indirect lightning

*    3.    间接光照

            N+2 bounces through feedback,Probe 4x4 hemispherical probe per 4x4 tile Jitter probe placement and ray directioins.Trace in last frame's Voxel Lighting. Lighting Gather ,Bilinear interpolation of 4 probes plane weighting.Visibility weighting using probe hitT.Convert to SH.Shading pixels on surface cache
       
*    4.    Voxel Lighting

           动机：Global SDF can't sample surface cache.Merge all cards into lobal clipmaps centered around the camera
       
           Structure:4 clipmaps of 64x64x64 voxels.Radiance per 6 directions per vovel.Sample and interppolate 3 directions using normal
       
           Visibility Buffer:Track object updates and set modified bricks on GPU.Voxelize modified bricks by tracing rays.6 rays per voxel.Cull objects to 4^3 bricks.One thread per mesh SDF per trace.Cache hits in a visibility buffer HitT I Mesh Index.InterlockedMin write hit to visibility buffer

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
*    
##### 混合空间Blend Space

*    1D混合空间
*    2D混合空间
*    分部混合Skeleton Masked Blending
*    叠加混合Additive Blending
*    
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
*    
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
         
*    可视化脚本的问题
*    3C

### 基础AI系统
### 构建高级的AI系统

# 工具链

### 界面（GUI)
### 资产管理
### 数据结构设计
### C++代码反射
### 鲁棒性设计
### 软件架构
### 常见编辑器
### 插件
### 协同编辑



# 网络

### 网络基础
### 网络同步
### 服务器架构
### 游戏优化

# 面向数据编程与任务系统

### 游戏并行框架
### 实体-组件-系统ECS
### 面向数据编程
### 并行编程基础知识
