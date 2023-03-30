# 创建曲线的示例脚本

import os, sys
import json
# import numpy
import bpy

def read_json_file(input_json_file_path):
    with open(input_json_file_path, 'r') as f:
        curves = json.load(f)
    return curves

def convert_points_to_curve(points, curve_name):
    # Create a curve object and set the points as nodes of the curve
    curve = bpy.data.curves.new("Curve", "CURVE")
    curve.dimensions = '3D'
    spline = curve.splines.new("BEZIER")
    #spline = curve.splines.new("POLY")
    spline.bezier_points.add(len(points) - 1)
    #spline.points.add(len(points) - 1)
    for i, coord in enumerate(points):
        spline.bezier_points[i].co = coord

    #spline.type = 'POLY'

    # Create an object to hold the curve and add it to the scene
    curve_obj = bpy.data.objects.new(curve_name, curve)
    bpy.context.collection.objects.link(curve_obj)
    
    curve_obj.select_set(True)

    bpy.context.view_layer.objects.active = curve_obj
    bpy.ops.object.editmode_toggle()
    bpy.ops.curve.select_all(action='SELECT')
    bpy.ops.curve.spline_type_set(type='POLY')
    bpy.ops.object.editmode_toggle()
    
    #This script assumes that the text file curve_points.txt is located in the same directory as the Blender file and contains one point per line, with the x, y, and z values separated by spaces. You can modify this script to fit the format of your text file.

    #bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))


def import_single_curve(file_path):
    # Get the path to the text file
    # file_path = "D:/studio/Blender/txt"
    # Read the text file and store the point data in a list
    points = []

    with open(os.path.join(file_path, "curve_points.txt")) as f:
        for line in f:
    #        x, y, z, a = map(float, line.strip().split())
    #        points.append((x, y, z, a))
            x, y, z = map(float, line.strip().split())
            points.append((x, y, z))
    
    convert_points_to_curve(points, "curve_1")


def import_and_join_multi_curve(input_curves_path):
    curves = read_json_file(input_curves_path)
    curves_num = len(curves)
    for i in range(curves_num):
        convert_points_to_curve(curves[i], "curve_"+str(i))
        
#    bpy.ops.object.editmode_toggle()
#    bpy.ops.curve.spline_type_set(type='POLY')
#    bpy.ops.object.editmode_toggle()
    bpy.ops.object.join()


if __name__=="__main__":
    input_file_path = "./data/factory-3_refine_filter.json"
    import_and_join_multi_curve(input_file_path)