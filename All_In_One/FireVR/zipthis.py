import os

os.system('zip -r FireVR.zip FireVR -x \*.git\* -x FireVR/docs/\*')
os.system("rm -f -r ~/.config/blender/2.78/scripts/addons/FireVR")
os.system("cp -r ~/FireVR ~/.config/blender/2.78/scripts/addons/FireVR")
os.system("~/blender-2.78a-linux-glibc211-x86_64/blender")
