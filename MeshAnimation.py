# 动态网格渲染示例脚本

import bpy
import re

############# params #############
# point sparse rate
mesh_sparse_rate = 1
# point file name standerd
mesh_file_pattern = r'mf_(.*)_mesh' # start from 1
#mesh_file_pattern = r'sf_(.*)_mesh'
is_only_final_mode = False
    

############ func script ##########
def get_frame_num() :
    # get point cloud numbers
    obj_list = bpy.data.objects
    max_id = 0
    for obj in obj_list.items():
        mesh_id = re.match(mesh_file_pattern, obj[0])
        if(mesh_id != None):
            mesh_id = mesh_id.group(1)
            max_id = max(max_id, int(mesh_id))
    return max_id


def set_info_object(frame_number) :
    # if don't exist, create it
    if bpy.data.objects.find('FrameInfo') == -1 :
        bpy.ops.object.empty_add()
        bpy.context.object.name = 'FrameInfo'
        bpy.context.object.hide_render = True
    # set anim control - const var
    frame_info = bpy.data.objects['FrameInfo']
    frame_info['MultiFrameNum'] = frame_number
    return frame_info


def set_mesh_animation(frame_number, frame_info):
    for i in range(0, frame_number):
        
        # clear and init animation
        mesh_str = 'mf_' + str(i + 1).rjust(4,'0') + '_mesh'
        mesh = bpy.data.objects[mesh_str]
        mesh.animation_data_clear()
        mesh.animation_data_create()
        
        if i % mesh_sparse_rate != 0 :
            mesh.hide_render = True
            continue
        
        # create animation driver
        control_radius_path = 'hide_render'
        mesh.animation_data.drivers.new(control_radius_path)
        mesh.animation_data.drivers[0].driver.type = 'SCRIPTED'
        # driver setting
        mesh.animation_data.drivers[0].driver.variables.new()
            # bpy.context.object.animation_data.drivers[0].driver.variables[0].type = 'SINGLE_PROP' #(default)
        mesh.animation_data.drivers[0].driver.variables[0].name = 't'
        mesh.animation_data.drivers[0].driver.variables[0].targets[0].id = bpy.data.objects['TrackBall']
        mesh.animation_data.drivers[0].driver.variables[0].targets[0].data_path = 'constraints["Follow Path"].offset_factor'
        mesh.animation_data.drivers[0].driver.variables.new()
            # bpy.context.object.animation_data.drivers[0].driver.variables[0].type = 'SINGLE_PROP' #(default)
        mesh.animation_data.drivers[0].driver.variables[1].name = 'fn'
        mesh.animation_data.drivers[0].driver.variables[1].targets[0].id = frame_info
        mesh.animation_data.drivers[0].driver.variables[1].targets[0].data_path = '["MultiFrameNum"]'
        
        # keep frame
        # expression_str = '(-(min(t,1.0/fn*' + str(i+1) + ')-1.0/fn*' + str(i+2) + ') * (min(t,1.0/fn*' + str(i+1) + ')-1.0/fn*' + str(i) + ')*1.01*fn*fn) < 1.0'
        # throw frame
        # (- (t-1.0/fn*(i+2)) * (t-1.0/fn*i) * 1.01 * fn^2) + 0.5 < 1.0
        expression_str = '(-(t-1.0/fn*' + str(i+2) + ') * (t-1.0/fn*' + str(i) + ')*fn*fn) - 0.75 < 0.0'
        mesh.animation_data.drivers[0].driver.expression = expression_str

def set_mesh_only_final(frame_number):
     for i in range(0, frame_number):
        
        # clear and init animation
        mesh_str = 'mf_' + str(i + 1).rjust(4,'0') + '_mesh'
        mesh = bpy.data.objects[mesh_str]
        mesh.animation_data_clear()
        mesh.animation_data_create()
        
        mesh.hide_render = i + 1 != frame_number
            

############## main func ############
if __name__ == '__main__':
    
    # get frame number and set info object
    frame_number = get_frame_num()
    
    # call funcs
    # optional mode only final
    if is_only_final_mode :
        set_mesh_only_final(frame_number)
    else :
        frame_info = set_info_object(frame_number)
        set_mesh_animation(frame_number, frame_info)