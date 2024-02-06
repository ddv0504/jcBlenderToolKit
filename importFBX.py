import bpy
# prject directory
output_project = r'X:/2305_D59'

# output sequence
output_directory = 'SR004/bg.####.png'

# set output 
scene = bpy.context.scene
scene.render.filepath = '%s/%s' % (output_project,output_directory)



fbx_path = r'E:\temp\fbx\camera.fbx'
startframe = 101
# endframe = 205
fps = 30
width = 1280
height = 1024



bpy.context.scene.frame_start = startframe
# bpy.context.scene.frame_end = endframe


fbx = bpy.ops.import_scene.fbx(filepath = fbx_path,anim_offset=0)
# print(type(fbx))
# print(dir(fbx))
sels = bpy.context.selected_objects
# print(sels)
if sels:
    for sel in sels:
        # print(sel.data)
        if type(sel.data) == bpy.types.Camera:
            scene.camera = sel
            bpy.context.view_layer.objects.active = sel
            sel.data.sensor_fit = 'VERTICAL'
            animation_data = sel.animation_data
            # keyframes = animation_data.action.fcurves
            # bpy.context.scene.frame_end = keyframes[-1]
            last_frame = int(animation_data.action.frame_range[-1])
            bpy.context.scene.frame_end = last_frame
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 1024

# bpy.context.view_layer.objects.active = 