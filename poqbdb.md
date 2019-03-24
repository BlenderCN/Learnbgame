poqbdb is process or query by database

blender物质模型库

blender 模型管理插件poqbdb(process or query by database的缩写)

插件托管在 https://github.com/BlenderCN/poqbdb

随着blender学习的深入和工作的需要,我们可能会接触或创建出大量模型,而随着模型的逐渐增多,管理这些模型就会成为比较麻烦的事,所以我就想着写一个插件,来管理模型.插件主要有两部分,poqbdb文件夹,逻辑脚本__init__.py和poqbdb.py

	poqbdb
		|
		|---poqbdb
		|
		|---__init__.py
		|
		|---poqbdb.py

只要你将你的模型以gltf格式放入poqbdb文件夹,就能自动在软件界面形成相应的按钮,到时候就能很方便通过一键生成你自己的模型

关于gltf格式的问题:目前只采用gltf的格式进行导入,关于gltf格式可以参考 https://github.com/KhronosGroup/glTF
可能有些人喜欢.obj或.fbx或其他格式的导入方式,只需要在脚本
将bpy.ops.import_scene.gltf()改为bpy.ops.import_scene.obj()或	其他对应命令即可.

poqbdb文件夹示例目录树:

	poqbdb
	├── learnioc.glb
	├── planets
	│   ├── earth.glb
	│   ├── jupiter.glb
	│   └── moon.glb
	└── species
	    ├── animal
	    │   ├── armadillo.glb
	    │   ├── bear.glb
	    │   ├── bison.glb
	    │   ├── cow.glb
	    │   ├── crab.glb
	    │   ├── crocodile.glb
	    │   ├── crow.glb
	    │   ├── deer.glb
	    │   ├── dog.glb
	    │   ├── dolphin.glb
	    │   ├── duck.glb
	    │   ├── elephant.glb
	    │   ├── elk.glb
	    │   ├── fish.glb
	    │   ├── frog.glb
	    │   ├── giraffe.glb
	    │   ├── goat.glb
	    │   ├── goldfish.glb
	    │   ├── hawk.glb
	    │   ├── horse.glb
	    │   ├── kangaroo.glb
	    │   ├── monkey.glb
	    │   ├── muskrat.glb
	    │   ├── ostrich.glb
	    │   ├── parrot.glb
	    │   ├── penguin.glb
	    │   ├── pheasant.glb
	    │   ├── pig.glb
	    │   ├── rabbit.glb
	    │   ├── racoon.glb
	    │   ├── seahorse.glb
	    │   ├── sealion.glb
	    │   ├── shrimp.glb
	    │   ├── snake.glb
	    │   ├── spider.glb
	    │   ├── swan.glb
	    │   ├── turtle.glb
	    │   └── walrus.glb
	    ├── learnioc.glb
	    ├── micrabe
	    │   ├── coli.glb
	    │   └── phage.glb
	    └── plant
	        ├── sunflower.glb
	        └── tulip.glb

插件UI


