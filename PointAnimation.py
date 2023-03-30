# 动态点云渲染示例脚本

import bpy
import re

############# params #############
# point size
point_max_size = 0.03
# point sparse rate
point_sparse_rate = 1
# point file name standerd
pc_file_pattern = r'sf_(.*)_pc'
# point single render mode
is_single_render_mode = True
    

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


def set_info_object(frame_number) :
    # if don't exist, create it
    if bpy.data.objects.find('FrameInfo') == -1 :
        bpy.ops.object.empty_add()
        bpy.context.object.name = 'FrameInfo'
        bpy.context.object.hide_render = True
    # set anim control - const var
    frame_info = bpy.data.objects['FrameInfo']
    frame_info['SingleFrameNum'] = frame_number
    return frame_info


def set_pc_animation(frame_number, frame_info):
    for i in range(0, frame_number):
        # clear and init animation
        pc_str = 'sf_' + str(i).rjust(4,'0') + '_pc'
        pc = bpy.data.objects[pc_str]
        pc.animation_data_clear()
        pc.animation_data_create()
        # create driver
        control_radius_path = 'modifiers["GeometryNodes"]["Input_2"]'
        pc.animation_data.drivers.new(control_radius_path)
        pc.animation_data.drivers[0].driver.type = 'SCRIPTED'
        # driver setting
        pc.animation_data.drivers[0].driver.variables.new()
            # bpy.context.object.animation_data.drivers[0].driver.variables[0].type = 'SINGLE_PROP' #(default)
        pc.animation_data.drivers[0].driver.variables[0].name = 't'
        pc.animation_data.drivers[0].driver.variables[0].targets[0].id = bpy.data.objects['TrackBall']
        pc.animation_data.drivers[0].driver.variables[0].targets[0].data_path = 'constraints["Follow Path"].offset_factor'
        pc.animation_data.drivers[0].driver.variables.new()
            # bpy.context.object.animation_data.drivers[0].driver.variables[0].type = 'SINGLE_PROP' #(default)
        pc.animation_data.drivers[0].driver.variables[1].name = 'fn'
        pc.animation_data.drivers[0].driver.variables[1].targets[0].id = frame_info
        pc.animation_data.drivers[0].driver.variables[1].targets[0].data_path = '["SingleFrameNum"]'
        # set expression
        expression_str = '-(min(t,1.0/fn*' + str(i+1) + ')-1.0/fn*' + str(i+2) + ') * (min(t,1.0/fn*' + str(i+1) + ')-1.0/fn*' + str(i) + ')*' + str(point_max_size) + '*fn*fn'
        pc.animation_data.drivers[0].driver.expression = expression_str
        # set sparse rate
        pc.hide_render = (i % point_sparse_rate != 0)
        
        
def set_pc_single_render(frame_number, frame_info):
    # render driver
    for i in range(0, frame_number):
        
        # clear and init animation
        pc_str = 'sf_' + str(i).rjust(4,'0') + '_pc'
        pc = bpy.data.objects[pc_str]
        
        # create driver
        control_render_path = 'hide_render'
        pc.animation_data.drivers.new(control_render_path)
        pc.animation_data.drivers[1].driver.type = 'SCRIPTED'
        
        # driver setting
        pc.animation_data.drivers[1].driver.variables.new()
        # bpy.context.object.animation_data.drivers[0].driver.variables[0].type = 'SINGLE_PROP' #(default)
        pc.animation_data.drivers[1].driver.variables[0].name = 't'
        pc.animation_data.drivers[1].driver.variables[0].targets[0].id = bpy.data.objects['TrackBall']
        pc.animation_data.drivers[1].driver.variables[0].targets[0].data_path = 'constraints["Follow Path"].offset_factor'
        
        pc.animation_data.drivers[1].driver.variables.new()
        # bpy.context.object.animation_data.drivers[0].driver.variables[0].type = 'SINGLE_PROP' #(default)
        pc.animation_data.drivers[1].driver.variables[1].name = 'fn'
        pc.animation_data.drivers[1].driver.variables[1].targets[0].id = frame_info
        pc.animation_data.drivers[1].driver.variables[1].targets[0].data_path = '["SingleFrameNum"]'
    
        # single expr
        expression_str = '(-(t-1.0/fn*' + str(i+2) + ') * (t-1.0/fn*' + str(i) + ')*fn*fn) - 0.75 < 0.0'
        pc.animation_data.drivers[1].driver.expression = expression_str


############## main func ############
if __name__ == '__main__':
    
    # get frame number and set info object
    frame_number = get_frame_num() + 1
    
    # call funcs
    frame_info = set_info_object(frame_number)
    set_pc_animation(frame_number, frame_info)
    # option for single render
    if is_single_render_mode :
        set_pc_single_render(frame_number, frame_info)