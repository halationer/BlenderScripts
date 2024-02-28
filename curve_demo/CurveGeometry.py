import bpy
import re
import numpy as np
import os
 
### need folder with objects ###
# root_path
# |__instance1
#    |__xxx_outer_wall.obj
#    |__xxx_roof.obj
#    |__xxx_room.obj
#    |__......obj
# |__instance2...

############# params #############
root_path = 'C:/Users/11247/Desktop/To_YD/Root/'

cprefix = 'c_'
pattern_list = [
    r'c_(.*)_outer_wall',
    r'c_(.*)_roof',
    r'c_(.*)_room(.*)',
    r'c_(.*)_wall_points',
    r'c_(.*)_roof_points',
    r'c_(.*)_room(.*)_points',
]
seed_list = [
    'wall_seed',
    'roof_seed',
    'room_seed',
    'wall_points_seed',
    'roof_points_seed',
    'room_points_seed',
]

plane_seed_prefix = 'plane_seed_'
plane_seed_nums = 4
plane_object_subfix = '_bottom_plane'

############ load funcs ###########
# 获取文件夹中的所有文件，返回文件路径列表
def readDir(dir_path):
    file_names = os.listdir(dir_path)
    file_paths = [os.path.join(dir_path, file_name) for file_name in file_names]
    return file_paths

# 渲染图片到指定路径（修改blender默认存储结果图的位置）
def renderImage(outputPath):
    bpy.data.scenes['Scene'].render.filepath = outputPath
    bpy.ops.render.render(write_still = True)

# 读取一个obj文件到场景中
# 参考：https://github.com/HTDerekLiu/BlenderToolbox/blob/master/demos/demo_amber.py
def readOBJ(filePath, location, rotation_euler, scale):
	x = rotation_euler[0] * 1.0 / 180.0 * np.pi 
	y = rotation_euler[1] * 1.0 / 180.0 * np.pi 
	z = rotation_euler[2] * 1.0 / 180.0 * np.pi 
	angle = (x,y,z)

	prev = []
	for ii in range(len(list(bpy.data.objects))):
		prev.append(bpy.data.objects[ii].name)
	bpy.ops.wm.obj_import(filepath=filePath, use_split_groups=False)
	after = []
	for ii in range(len(list(bpy.data.objects))):
		after.append(bpy.data.objects[ii].name)
	name = list(set(after) - set(prev))[0]
	mesh = bpy.data.objects[name]

	mesh.location = location
	mesh.rotation_euler = angle
	mesh.scale = scale
	bpy.context.view_layer.update()

	return mesh 

# 加载obj文件，并设置加载后的资源名称
def readAndAddPrefix(filePath, frame_id, location=(0,0,0), rotation_euler=(0,0,0), scale=(1,1,1)):
    mesh = readOBJ(filePath, location, rotation_euler, scale)
    mesh.name = cprefix + str(frame_id).rjust(4, '0') + '_' + mesh.name
    return mesh

############ node funcs ##########
# 激活场景树中第一层级指定名称的场景集合（文件夹）
def active_collection(name):
    collection_list = bpy.context.view_layer.layer_collection.children
    for collection in collection_list:
        if(name == collection.name):
            bpy.context.view_layer.active_layer_collection = collection
            return collection

# 删除场景集合中的所有物体资源
def delete_all_objects(collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    active_collection(collection_name)
    object_list = bpy.context.collection.all_objects
    for obj in object_list:
        obj.select_set(True)
    bpy.ops.object.delete()

# 从物体资源集合中，搜索第一个名称符合条件的物体
def get_first_object(pattern):
    obj_list = bpy.data.objects
    for obj in obj_list.items():
        name = re.match(pattern, obj[0])
        if(name != None):
            return obj[1]

def get_first_object_byid(id):
    return get_first_object(pattern_list[id])

def get_seed_object_byid(id):
    return get_first_object(seed_list[id])

# 从物体资源集合中，搜索名称符合条件的物体，并全选
def select_all_object(pattern):
    obj_list = bpy.data.objects
    for obj in obj_list.items():
        name = re.match(pattern, obj[0])
        if(name != None):
            obj[1].select_set(True)

def select_all_object_byid(id):
    select_all_object(pattern_list[id])

# 从物体资源集合中，搜索名称符合条件的物体，清除所有的修改器
def clear_none_seed_modifier(pattern):
    obj_list = bpy.data.objects
    for obj in obj_list.items():
        name = re.match(pattern, obj[0])
        if(name != None and name.group(1) != 'seed'):
            obj[1].modifiers.clear()

def clear_none_seed_modifier_byid(id):
    clear_none_seed_modifier(pattern_list[id])

############# render funcs ##########
def get_frame_num():
    obj_list = bpy.data.objects
    count = 0
    for obj in obj_list.items():
        curve_id = re.match(pattern_list[0], obj[0])
        if(curve_id != None):
            count = count + 1
    return count

# 对于不同组别的数据，设置driver动画，使其在不同帧渲染
def set_curve_animation(frame_number, pre_str, sub_str):
    for i in range(0, frame_number):
        # clear and init animation
        bpy.ops.object.select_all(action='DESELECT')
        mesh_pattern = pre_str + str(i).rjust(4,'0') + sub_str
        select_all_object(mesh_pattern)
        for mesh in bpy.context.selected_objects:
            mesh.animation_data_clear()
            mesh.animation_data_create()

            # create animation driver
            control_radius_path = 'hide_render'
            mesh.animation_data.drivers.new(control_radius_path)
            mesh.animation_data.drivers[0].driver.type = 'SCRIPTED'
            # driver setting
            mesh.animation_data.drivers[0].driver.variables.new()
            mesh.animation_data.drivers[0].driver.variables[0].name = 't'
            mesh.animation_data.drivers[0].driver.variables[0].targets[0].id = bpy.data.objects['TrackBall']
            mesh.animation_data.drivers[0].driver.variables[0].targets[0].data_path = 'constraints["Follow Path"].offset'
            # (t-i)^2 < 0.1
            expression_str = '(t - ' + str(i) + ') * (t - ' + str(i) + ') > 0.1'
            mesh.animation_data.drivers[0].driver.expression = expression_str

def process_instance(instance_path, instance_id):
    model_names = readDir(dir_path)
    for model_name in model_names:
        mesh = readAndAddPrefix(model_name, instance_id)

# 将seed物体中的修改器，拷贝到对应类型的物体中
def copy_common_geometry_nodes(id):
    bpy.ops.object.select_all(action='DESELECT')
    # select and active seed object
    seed_object = get_seed_object_byid(id)
    seed_object.select_set(True)
    bpy.context.view_layer.objects.active = seed_object
    # select all object
    select_all_object_byid(id)
    # copy to select
    clear_none_seed_modifier_byid(id)
    geometry_node_name = seed_object.modifiers.keys()[0]
    bpy.ops.object.modifier_copy_to_selected(modifier=geometry_node_name)

# 将seed物体的材质，拷贝到对应类型的物体中
def copy_plane_material():
    for room_id in range(10):
        bpy.ops.object.select_all(action='DESELECT')
        # remove current material
        plane_pattern = '(.*)' + str(room_id) + plane_object_subfix
        clear_none_seed_modifier(plane_pattern)
        select_all_object(plane_pattern)
        # select seed plane
        random_index = room_id % plane_seed_nums + 1
        seed_object = get_first_object(plane_seed_prefix + str(random_index))
        seed_object.select_set(True)
        bpy.context.view_layer.objects.active = seed_object
        # copy to selected
        bpy.ops.object.material_slot_copy()
        

############## main func ############
if __name__ == '__main__':

    # clear workspace
    delete_all_objects('Test')

    # read root
    dir_names = readDir(root_path)

    # read one instance
    instance_num = len(dir_names)
    for instance_id in range(len(dir_names)):
        dir_path = dir_names[instance_id]
        process_instance(dir_path, instance_id)

    # select and copy geometry nodes
    for id in range(len(seed_list)):
        copy_common_geometry_nodes(id)

    # random color to plane
    # copy_plane_material()

    # make animation
    set_curve_animation(instance_num, cprefix, '_(.*)')
        
