# 上下文切换示例脚本

import bpy

# console mode has the 'tab' tips

# get objects:
obj_list = bpy.data.objects
print("object_list: ", obj_list)
names = []
obj_datas = []
for obj in obj_list.items():
    names.append(obj[0])
    obj_datas.append(obj[1])

# get a specific object (reference, not copy)
pc_0 = bpy.data.objects['sf_0000_pc']
print("pc0: ", pc_0)

# get now working context (pointer read-only, but object referece)
pc_now = bpy.context.object
print("context: ", pc_now)

# change the context
bpy.context.view_layer.objects.active = pc_0
pc_0.select_set(True)
print("context: ", bpy.context.object)