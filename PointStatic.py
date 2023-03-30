# 静态点云渲染示例脚本

import bpy
import re

############# params #############
# point size
point_max_size = 0.03
# point sparse rate
point_sparse_rate = 8
# point file name standerd
pc_file_pattern = r'sf_(.*)_pc'
    

############ func script ##########
def get_frame_num() :
    # get point cloud numbers
    obj_list = bpy.data.objects
    max_id = 0
    for obj in obj_list.items():
        pc_id = re.match(pc_file_pattern, obj[0])
        if(pc_id != None):
            pc_id = pc_id.group(1)
            max_id = max(max_id, int(pc_id))
    return max_id

def set_static_properties(frame_number):
    for i in range(0, frame_number):
        # clear and init animation
        pc_str = 'sf_' + str(i).rjust(4,'0') + '_pc'
        pc = bpy.data.objects[pc_str]
        pc.animation_data_clear()
        pc.modifiers["GeometryNodes"]["Input_2"] = point_max_size
        # sparse the point cloud
        pc.hide_render = (i % point_sparse_rate != 0)


############## main func ############
if __name__ == '__main__':
    
    # get frame number and set info object
    frame_number = get_frame_num() + 1
    
    # call funcs
    set_static_properties(frame_number)