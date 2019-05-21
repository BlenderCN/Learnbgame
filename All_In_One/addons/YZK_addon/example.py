#
# Example SDK usage from the Blender Python console. Control the Motion Service
# using the socket based Lua console. The SDK wraps the Lua commands in the
# Node class for convenient Python use.
#

import Shadow.MotionSDK as SDK

# Script node. Use just like the Lua "node" module. Connect to Lua console.
node = SDK.LuaConsole.Node(SDK.Client("127.0.0.1", 32075))

# Set up the configuration. Clear everything out, re-scan, and start streaming.
node.close()
node.erase()
node.scan()
node.start()

# Create rest pose.
node.set_pose_marker()

# Zero position. Start recording.
node.set_pose()
node.start_take()

# ...

# Stop recording. Export to BVH.
node.stop_take()
node.export("take.bvh")
