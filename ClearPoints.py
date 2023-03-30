# 删除文件的示例脚本
import bpy
import re

# point file name standerd
pc_file_pattern = r'sf_(.*)_pc'


############ func script ##########
def remove_all_pc():
    obj_list = bpy.data.objects
    remove_list = []
    # record remove
    for obj in obj_list.items():
        pc_id = re.match(pc_file_pattern, obj[0])
        if(pc_id != None):
            remove_list.append(obj[1])
    # start remove
    for obj in remove_list:
        obj_list.remove(obj)
        
    
######### main script ############
if __name__ == '__main__' :
    
    remove_all_pc()