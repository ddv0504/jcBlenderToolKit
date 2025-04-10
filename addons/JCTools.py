#-*- coding: utf-8 -*-
import bpy
import os
import sys
from pprint import pprint
import json
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


# global variables
possible_object_types = {
    'MESH',
    'META',
    'CURVE',
    'CURVES',
    'SURFACE',
    'FONT'
}


# def main(context):
#     # Get the current scene
#     for ob in context.scene.objects:
#         print(ob.name)
    # scene = context.scene

bl_info = {
    "name": "JCTools",
    "description": "B1 Blender Pipeline Tools",
    "author": "JCO",
    "version": (0, 0, 1),
    "blender": (4, 3, 0),
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Development" }


# From Matalogue
class JC_WM_Settings(bpy.types.PropertyGroup):
    mat_selected_only: bpy.props.BoolProperty(
        name="Selected Objects Only", default=False, description="Only show materials used by objects that are selected"
    )
    mat_visible_only: bpy.props.BoolProperty(
        name="Visible Collections Only",
        default=False,
        description="Only show materials used by objects that are visible in the current scene.",
    )

    light_visible_only: bpy.props.BoolProperty(
        name="Visible Collections Only",
        default=False,
        description="Only show lights that are visible in the current scene.",
    )

    geo_selected_only: bpy.props.BoolProperty(
        name="Selected Objects Only",
        default=False,
        description="Only show geometry node trees used by objects that are selected",
    )
    geo_visible_only: bpy.props.BoolProperty(
        name="Visible Only",
        default=False,
        description="Only show geometry node trees used by objects that are visible in the current scene",
    )

# ====================== Operators ======================

# Add current ui-active properties to keyframes
class MouseCursorPropertyOperator(bpy.types.Operator):
    bl_idname = "screen.active_int_property_add"
    bl_label = "Adjust active mouse cursor integer property"
    bl_options = {'REGISTER', 'UNDO'}
    
    my_int = bpy.props.IntProperty(default=100)
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.ui.copy_data_path_button.poll()

    def execute(self, context):      
        
        # get the data path
        bpy.ops.ui.copy_data_path_button()
        path = context.window_manager.clipboard
        
        # get full data path
        bpy.ops.ui.copy_data_path_button(full_path=True)
        full_path = context.window_manager.clipboard
        
        # split path in class and property
        rna, prop = context.window_manager.clipboard.rsplit('.', 1)
            
        # set attribute if type is integer
        if type(eval(full_path)) is int:
            rna_eval = (eval(rna))
            value = getattr(rna_eval, prop)
            setattr(rna_eval, prop, value + self.my_int)
            self.report({"INFO"}, "{} set to {}".format(prop, value + self.my_int))
        else:
            print (type(eval(full_path)))
            self.report({"INFO"}, "{} is not an integer property".format(prop))
            
        return {'FINISHED'}
    
# JC Common Tools Operators
class JCLinkLastModifier(bpy.types.Operator):
    bl_idname = "object.jc_link_last_modifier"
    bl_label = "Link Last Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        link_latest_modifier_to_selected()
        # # Get the selected objects
        # selected = context.selected_objects
        # # Get the active object
        # active = context.active_object
        # # Get the last modifier
        # last_modifier = active.modifiers[-1]
        # # Link the last modifier to the selected objects
        # for obj in selected:
        #     obj.modifiers.new(name=last_modifier.name, type=last_modifier.type)
        #     obj.modifiers[-1].copy(last_modifier)
        return {'FINISHED'}

class JCClearAllModifiers(bpy.types.Operator):
    bl_idname = "object.jc_clear_all_modifiers"
    bl_label = "Clear All Modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        clear_all_modifiers_from_selected()
        return {'FINISHED'}

# Set key frame selected objects
class JCSetKeyFrame(bpy.types.Operator):
    bl_idname = "object.jc_set_key_frame"
    bl_label = "Set Key Frame"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Get the selected objects
        selected = context.selected_objects
        # Set the key frame
        for obj in selected:
            obj.keyframe_insert(data_path='location')
            obj.keyframe_insert(data_path='rotation_euler')
            obj.keyframe_insert(data_path='scale')
        return {'FINISHED'}

# Set key frame to translate
class JCSetKeyFrameTranslate(bpy.types.Operator):
    bl_idname = "object.jc_set_key_frame_translate"
    bl_label = "Set Key Frame Translate"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Get the selected objects
        selected = context.selected_objects
        # Set the key frame
        for obj in selected:
            obj.keyframe_insert(data_path='location')
        return {'FINISHED'}
# Set key frame to rotate
class JCSetKeyFrameRotate(bpy.types.Operator):
    bl_idname = "object.jc_set_key_frame_rotate"
    bl_label = "Set Key Frame Rotate"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Get the selected objects
        selected = context.selected_objects
        # Set the key frame
        for obj in selected:
            obj.keyframe_insert(data_path='rotation_euler')
        return {'FINISHED'}
# Set key frame to scale
class JCSetKeyFrameScale(bpy.types.Operator):
    bl_idname = "object.jc_set_key_frame_scale"
    bl_label = "Set Key Frame Scale"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Get the selected objects
        selected = context.selected_objects
        # Set the key frame
        for obj in selected:
            obj.keyframe_insert(data_path='scale')
        return {'FINISHED'}

# Visibility Operators
# Hide View Port
class JCHideViewPort(bpy.types.Operator):
    bl_idname = "object.hide_viewport_set"
    bl_label = "Hide"
    bl_options = {'REGISTER', 'UNDO'}
    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None
    def execute(self, context):
        # Get the selected objects
        selected = context.selected_objects
        # Hide the selected objects
        for obj in selected:
            obj.hide_viewport = True
        return {'FINISHED'}

# Unhide View Port
class JCUnhideViewPort(bpy.types.Operator):
    bl_idname = "object.hide_viewport_clear"
    bl_label = "Unhide"
    bl_options = {'REGISTER', 'UNDO'}
    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None
    def execute(self, context):
        # Get marked objects in outliner
        objs = context.view_layer.objects

        objs = context.view_layer.objects
        for obj in objs:
            obj.hide_viewport = False
        return {'FINISHED'}

# Render Visibility
class JCHideRender(bpy.types.Operator):
    bl_idname = "object.jc_hide_render"
    bl_label = "Hide"
    bl_options = {'REGISTER', 'UNDO'}
    Hidden: BoolProperty(default=True)
    def execute(self, context):
        # Get the selected objects
        selected = context.selected_objects
        # Hide the selected objects
        for obj in selected:
            obj.hide_render = self.Hidden
        return {'FINISHED'}

# Shader Operators
# Red
class JCSolidShaderRed(bpy.types.Operator):
    bl_idname = "shader.jc_shader_red"
    bl_label = "Simple Shader Operator"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        # Get the active object
        obj = context.active_object
        # Create a new material
        mat = bpy.data.materials.new(name="Red")
        # Assign it to the object
        if obj.data.materials:
            # assign to 1st material slot
            obj.data.materials[0] = mat
        else:
            # no slots
            obj.data.materials.append(mat)
        # Use nodes
        mat.use_nodes = True
        # Remove default node
        node = mat.node_tree.nodes.get('Principled BSDF')
        mat.node_tree.nodes.remove(node)
        # Add RGB node
        node = mat.node_tree.nodes.new('ShaderNodeRGB')
        node.location = (-300, 300)
        # Link RGB to Material Output
        output = mat.node_tree.nodes.get('Material Output')
        mat.node_tree.links.new(node.outputs[0], output.inputs[0])
        # Set the diffuse color
        node.outputs[0].default_value = (1, 0, 0, 1)

        return {'FINISHED'}
# Green
class JCSolidShaderGreen(bpy.types.Operator):
    bl_idname = "shader.jc_shader_green"
    bl_label = "Simple Shader Operator"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        # Get the active object
        obj = context.active_object
        # Create a new material
        mat = bpy.data.materials.new(name="Green")
        # Assign it to the object
        if obj.data.materials:
            # assign to 1st material slot
            obj.data.materials[0] = mat
        else:
            # no slots
            obj.data.materials.append(mat)
        # Use nodes
        mat.use_nodes = True
        # Remove default node
        node = mat.node_tree.nodes.get('Principled BSDF')
        mat.node_tree.nodes.remove(node)
        # Add RGB node
        node = mat.node_tree.nodes.new('ShaderNodeRGB')
        node.location = (-300, 300)
        # Link RGB to Material Output
        output = mat.node_tree.nodes.get('Material Output')
        mat.node_tree.links.new(node.outputs[0], output.inputs[0])
        # Set the diffuse color
        node.outputs[0].default_value = (0, 1, 0, 1)


        return {'FINISHED'}

# Blue
class JCSolidShaderBlue(bpy.types.Operator):
    bl_idname = "shader.jc_shader_blue"
    bl_label = "Simple Shader Operator"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        # Get the active object
        obj = context.active_object
        # Create a new material
        mat = bpy.data.materials.new(name="Blue")
        # Assign it to the object
        if obj.data.materials:
            # assign to 1st material slot
            obj.data.materials[0] = mat
        else:
            # no slots
            obj.data.materials.append(mat)
        
        # Use nodes
        mat.use_nodes = True
        # Remove default node
        node = mat.node_tree.nodes.get('Principled BSDF')
        mat.node_tree.nodes.remove(node)
        # Add RGB node
        node = mat.node_tree.nodes.new('ShaderNodeRGB')
        node.location = (-300, 300)
        # Link RGB to Material Output
        output = mat.node_tree.nodes.get('Material Output')
        mat.node_tree.links.new(node.outputs[0], output.inputs[0])
        # Set the diffuse color
        node.outputs[0].default_value = (0, 0, 1, 1)


        return {'FINISHED'}

# Remove Materials
class JCRemoveMaterials(bpy.types.Operator):
    bl_idname = "shader.jc_remove_all_materials"
    bl_label = "Remove All Materials"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        remove_all_materials_from_selected()
        return {'FINISHED'}

# Toon Base Shaders
class JCToonBaseShaders(bpy.types.Operator):
    bl_idname = "shader.jc_toon_base_shader_group"
    bl_label = "Toon Shader"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        # Get the active object
        obj = context.active_object
        obj_name = obj.name
        # Create a new base color material for the object
        mat = bpy.data.materials.new(name=obj_name + "_base_color")
        mat.use_nodes = True
        # delete the default principled bsdf node
        node = mat.node_tree.nodes.get('Principled BSDF')
        mat.node_tree.nodes.remove(node)
        # Assign it to the object
        if obj.data.materials:
            # assign to 1st material slot
            obj.data.materials[0] = mat
        else:
            # no slots
            obj.data.materials.append(mat)
        
        mat = bpy.data.materials.new(name=obj_name + "_shadow_color")
        mat.use_nodes = True
        # delete the default principled bsdf node
        node = mat.node_tree.nodes.get('Principled BSDF')
        mat.node_tree.nodes.remove(node)
        try:
            # Assign it to the object
            if obj.data.materials:
                # assign to 1st material slot
                obj.data.materials[1] = mat
        except:
            # no slots
            obj.data.materials.append(mat)
        
        mat = bpy.data.materials.new(name=obj_name + "_shadow_matt")
        mat.use_nodes = True
        # delete the default principled bsdf node
        node = mat.node_tree.nodes.get('Principled BSDF')
        mat.node_tree.nodes.remove(node)
        try:
            # Assign it to the object
            if obj.data.materials:
                # assign to 1st material slot
                obj.data.materials[2] = mat
        except:
            # no slots
            obj.data.materials.append(mat)
        
        mat = bpy.data.materials.new(name=obj_name + "_line_matt")
        mat.use_nodes = True
        # delete the default principled bsdf node
        node = mat.node_tree.nodes.get('Principled BSDF')
        mat.node_tree.nodes.remove(node)

        try:
            # Assign it to the object
            if obj.data.materials:
                # assign to 1st material slot
                obj.data.materials[3] = mat
        except:
            # no slots
            obj.data.materials.append(mat)
                    
        
        return {'FINISHED'}


# Playblast
class JCPlayblast(bpy.types.Operator):
    bl_idname = "render.playblast"
    bl_label = "Playblast"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        render = bpy.ops.render
        current_scene =  bpy.context.scene


        original_output = bpy.data.scenes[current_scene.name].render.filepath
        original_format = bpy.data.scenes[current_scene.name].render.image_settings.file_format


        filePath = bpy.data.filepath
        baseName  = filePath.split('.blend')[0]

        n = 1
        moviePath = ''

        baseName = '%s_p%s' % (baseName,str(n).zfill(3))

        moviePath = '%s.mov' % baseName



        if os.path.isfile(moviePath):

            original_base = baseName.split('_p')[0]
            n = int(baseName.split('_p')[-1])
            
            moviePath = '%s_p%s.mov' % (original_base,str(n).zfill(3))
            
            while os.path.isfile(moviePath):
                n+=1
                moviePath = '%s_p%s.mov' % (original_base,str(n).zfill(3))

        bpy.data.scenes[current_scene.name].render.filepath = moviePath

        bpy.data.scenes[current_scene.name].render.image_settings.file_format = 'FFMPEG'
        bpy.data.scenes[current_scene.name].render.ffmpeg.format = 'QUICKTIME'
        bpy.data.scenes[current_scene.name].render.ffmpeg.codec

        render.opengl(animation=True)


        # turn to original setting
        bpy.data.scenes[current_scene.name].render.image_settings.file_format = original_format

        bpy.data.scenes[current_scene.name].render.filepath = original_output
        
        return {'FINISHED'}

# Submit to Deadline
class submit_to_deadline(bpy.types.Operator):
    bl_idname = "render.submit_to_deadline"
    bl_label = "Submit to Deadline"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def execute(self, context):
        scriptPath = r'\\192.168.0.226\DeadlineRepository10\submission\Blender\Main'
        if not scriptPath in sys.path:
            sys.path.append(scriptPath)
        try:
            import SubmitBlenderToDeadline
            SubmitBlenderToDeadline.main()
        except ImportError:
            print('Error importing SubmitBlenderToDeadline')

        return {'FINISHED'}

# Alembric Importer
class JC_Alembic_Importer(bpy.types.Operator, ImportHelper):
    bl_idname = "import.jc_alembic"
    bl_label = "Import Alembic Camera"
    bl_options = {'REGISTER', 'UNDO'}
    # json_file: StringProperty(name="JSON File")
    filter_glob: StringProperty(default='*.abc',options={'HIDDEN'})
    def execute(self, context):
        # Get the current scene
        scene = context.scene
        # Get the selected object
        # selected = context.selected_objects
        # Get the file path
        file_path = self.filepath
        # Import the alembic
        bpy.ops.wm.alembic_import(filepath=file_path)
        print(file_path)

        # jsonfile 
        json_file = os.path.splitext(file_path)[0] + '.json'
        print(json_file)
        # Load the json file
        with open(json_file) as f:
            data = json.load(f)
        if not data:
            print('No data found')
        pprint    (data)
        # else:
        #     for obj, keyData in data.items():
        #         if not keyData:
        #             continue
        #         selected = bpy.data.objects[obj]
        #         # selected = bpy.data.objects[obj]
        #         for time, value in keyData.items():
        #             # set keyframe either time and value
        #             # object = bpy.data.objects[obj]
        #             # set the frame
        #             scene.frame_set(int(time))
        #             # set the value to render visibility
        #             # print(not(int(value)))
        #             selected.hide_render = not(int(value))
        #             # set the value to viewport visibility
        #             # selected.hide_viewport = not(int(value))
        #             # set the keyframe
        #             selected.keyframe_insert(data_path='hide_render')

        return {'FINISHED'}

# FBX Camera Importer
class JC_FBX_Camera_Importer(bpy.types.Operator, ImportHelper):
    bl_idname = "import.jc_fbx_camera"
    bl_label = "Import FBX Camera"
    bl_options = {'REGISTER', 'UNDO'}
    filter_glob: StringProperty(default='*.fbx',options={'HIDDEN'})
    Camera_name_as_filename: BoolProperty(name="Camera name as file name", default=True)
    
    def execute(self, context):
        # Get the current scene
        scene = context.scene
        # Get the selected object
        selected = context.selected_objects
        # Get the file path
        file_path = self.filepath
        # Import the camera
        bpy.ops.import_scene.fbx(filepath=file_path,use_anim=True,use_custom_props=True,use_custom_props_enum_as_string=True,anim_offset=0)
        # Get the camera
        camera = bpy.context.selected_objects[0]
        # Set the camera as the active camera
        scene.camera = camera
        # Set the camera name as the file name
        if self.Camera_name_as_filename:
            camera.name = os.path.splitext(os.path.basename(file_path))[0]
            # Set the camera name as the file name
            camera.data.name = os.path.splitext(os.path.basename(file_path))[0]
            # Set the camere sensor fit to vertical
            camera.data.sensor_fit = 'VERTICAL'
            # Render resolution
            scene.render.resolution_x = 1920
            scene.render.resolution_y = 1536
            
            # Set camera sensor size
            camera.data.sensor_height = 36
            
        try:
            # Scene frame start
            scene.frame_start = int(camera.animation_data.action.frame_range[0])
            # Scene frame end
            scene.frame_end = int(camera.animation_data.action.frame_range[-1])
            
        except:
            print('No animation data found')
        # Set the camera to the current view
        bpy.ops.view3d.camera_to_view()
        
        return {'FINISHED'}
    
# JC Match to Armature Name
class JCMatchToArmatureName(bpy.types.Operator):
    bl_idname = "object.jc_match_to_armature_name"
    bl_label = "Match to Armature Name"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Get bone chain from selected armature
        selected = context.selected_objects
        # Get the selected object
        for obj in selected:
            if obj.type == 'ARMATURE':
                armature = obj
                break
        else:
            return {'FINISHED'}
        # Get the bone chain
        bone_chain = []
        for bone in armature.data.bones:
            bone_chain.append(bone.name)
            bone.name = obj.name + '_' + bone.name
            # armature.name
        
        return {'FINISHED'}
        
# JC Copy Bone Damped Track
class JCCopyBoneDampedTrack(bpy.types.Operator):
    bl_idname = "object.jc_copy_bone_damped_track"
    bl_label = "Copy Bone Damped Track"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Get Selected pose bones
        selected = context.selected_pose_bones
        # Get the actived bone's damped track
        for bone in selected:
            if bone.constraints.get('Damped Track'):
                damped_track = bone.constraints['Damped Track']
                break
        else:
            return {'FINISHED'}
        
# JC Common Tools Panel
class JC_PT_Common_Tools(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Common_Tools_Panel"
    bl_label = "Common"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'

    def draw(self, context):
        layout = self.layout
        # Common
        row = layout.row()
        row.operator("object.jc_clear_all_modifiers", text="Clear All Modifiers")
        row = layout.row()
        row.operator("object.jc_link_last_modifier", text="Link Last Modifier")

# JC_Collection_Tools
class JC_PT_Collection_Tools(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Collection_Tools_Panel"
    bl_label = "Collection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'

    def draw(self, context):
        layout = self.layout
        # Collection
        row = layout.row()
        row.label(text="Collection:")

# JC_Rig_Tools
class JC_PT_Rig_Tools(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Rig_Tools_Panel"
    bl_label = "Rigging"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'
    
    def draw(self, context):
        layout = self.layout
        # Rigging
        row = layout.row()
        row.label(text="Rename Bones:")
        row.operator("object.jc_match_to_armature_name", text="Match to Armature Name")
        row = layout.row()
        row.label(text="Copy Bone Damped Track:")
        row.operator("object.jc_copy_bone_damped_track", text="Copy Bone Damped Track")
# JC_Animation_Tools
class JC_Animation_Tools(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_File_Builder_Panel"
    bl_label = "Animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'

    def draw(self, context):
        layout = self.layout
        # File Builder
        row = layout.row()
        row.label(text="Animation:")
        row = layout.row()
        row.operator("object.jc_set_key_frame", text="Set Key Frame")
        row = layout.row()
        row.operator("object.jc_set_key_frame_translate", text="Set Key Frame Translate")
        row = layout.row()
        row.operator("object.jc_set_key_frame_rotate", text="Set Key Frame Rotate")
        row = layout.row()
        row.operator("object.jc_set_key_frame_scale", text="Set Key Frame Scale")
        # row.operator("object.jc_file_builder", text="Build File")

# Visibility Tools
class JC_Visibility_Tools(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Visibility_Tools"
    bl_label = "Visibility"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'

    def draw(self, context):
        # layout = self.layout
        # Visibility
        
        layout = self.layout
        scene = context.scene
        row = layout.row()
        # layout.template_list("JC_UL_DISPLAY_UIList", "", scene, "jc_display_object_list", scene, "jc_display_object_index")        
        
        # Viewport Display
        row = layout.row()
        row.label(text="Viewport Display:")
        row.operator("object.hide_viewport_set", text="Hide", icon = 'RESTRICT_VIEW_OFF')
        row.operator("object.hide_viewport_clear", text="Unhide", icon = 'RESTRICT_VIEW_ON')
        
        # Render Display
        row = layout.row()
        row.label(text="Render Display:")
        row.operator("object.jc_hide_render", text="Hide", icon='RESTRICT_RENDER_OFF')
        
        row = layout.row()
        row.label(text="List Type:")
        row.operator("object.refresh_hidden_object_list", text="",icon = 'HIDE_OFF')
        row.operator("object.refresh_display_object_list", text="",icon = 'RESTRICT_VIEW_OFF')
        row.operator("object.refresh_renderable_object_list", text="", icon='RESTRICT_RENDER_OFF')
        layout.template_list("JC_UL_HIDDEN_UIList", "", scene, "jc_hidden_object_list", scene, "jc_hidden_object_index")
        layout.operator("object.select_object_from_jc_hidden_list", text="Select Object")
        # layout.operator("object.refresh_hidden_object_list", text="Refresh List")

        # row = layout.row()
        # row.label(text="ViewPort Display Object List:")
        # layout.template_list("JC_UL_DISPLAY_UIList", "", scene, "jc_display_object_list", scene, "jc_display_object_index")
        # layout.operator("object.select_object_from_jc_display_list", text="Select Object")
        # layout.operator("object.refresh_display_object_list", text="Refresh List")
        # # row.operator("object.refresh_object_list", text="Refresh List")

        # row = layout.row()
        # row.label(text="Unrenderable Object List:")
        # layout.template_list("JC_UL_RENDERABLE_UIList", "", scene, "jc_renderable_object_list", scene, "jc_renderable_object_index")
        # layout.operator("object.select_object_from_jc_renderable_list", text="Select Object")
        # layout.operator("object.refresh_renderable_object_list", text="Refresh List")

# Import Tools
class JC_PT_Import_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Import_Panel"
    bl_label = "Import"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'

    def draw(self, context):
        layout = self.layout
        # FBX Camera Importer
        row = layout.row()
        row.label(text="Import FBX Camera:")
        row.operator("import.jc_fbx_camera", text="Import FBX Camera")
        # Alembic Importer
        row = layout.row()
        row.label(text="Import Alembic Camera:")
        row.operator("import.jc_alembic", text="Import Alembic Camera")

# UI List
# Define a custom property group to store each object
class JC_NO_MAT_OBJECT_ITEM(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Object Name")

class JC_HIDDEN_OBJECT_ITEM(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Object Name")

# Define the UIList class
class JC_UL_No_Mat_UIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Custom layout for each item in the list
        # custom_icon = 'OBJECT_HIDDEN' if data.objects[item.name].hide_viewport else 'OBJECT'
        # layout.prop(item, "set_name", text="", emboss=False, icon=custom_icon)
        # op = layout.operator("object.select", icon="RESTRICT_SELECT_OFF")
        # op.index = index
        icon = 'OBJECT_DATA'
        obj = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=obj.name, icon=icon)  # , translate=False)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=obj.name)


class JC_UL_HIDDEN_UIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Custom layout for each item in the list
        # custom_icon = 'OBJECT_HIDDEN' if data.objects[item.name].hide_viewport else 'OBJECT'
        # layout.prop(item, "set_name", text="", emboss=False, icon=custom_icon)
        # op = layout.operator("object.select", icon="RESTRICT_SELECT_OFF")
        # op.index = index
        icon = 'OBJECT_DATA'
        obj = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=obj.name, icon=icon, )  # , translate=False)
            # layout.operator('object.select_object_from_jc_no_mat_list', text=obj.name, emboss=False, icon=icon,depress=False)
            # layout.icon(icon_value=layout.icon(obj))
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=obj.name)
        
    # contextmenu
    def draw_item_context_menu(self, context, layout):
        layout.operator("object.select_object_from_hidden_list", text="Select Object")
        layout.operator("object.refresh_hidden_object_list", text="Refresh List")
        layout.operator("object.hide_viewport_set", text="Hide Viewport")
        layout.operator("object.hide_viewport_clear", text="Unhide Viewport")
        layout.operator("object.jc_hide_render", text="Hide Render")
        layout.operator("object.jc_remove_all_materials", text="Remove All Materials")
        layout.operator("shader.jc_toon_base_shader_group", text="Toon Shader")
    
class JC_HIDDEN_OBJECT_ITEM(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Object Name")
    
    
# Shader Tools
class JC_PT_Shader_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Shader_Tools"
    bl_label = "Shaders"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'

    def draw(self, context):
        layout = self.layout
        # scene = context.scene
        # Shader List
        scene = context.scene
        row = layout.row()
        row.label(text="Shader List:")
        row.operator("shader.jc_shader_red", text="Red", icon='SEQUENCE_COLOR_01')
        row.operator("shader.jc_shader_green", text="Green", icon='SEQUENCE_COLOR_04')
        row.operator("shader.jc_shader_blue", text="Blue", icon='SEQUENCE_COLOR_05')
        
        row = layout.row()
        row.label(text="Remove Materials:")
        row.operator("shader.jc_remove_all_materials", text="Remove All Materials", icon='MATERIAL')
        
        
        row = layout.row()
        row.label(text="Toon Shader:")
        row.operator("shader.jc_toon_base_shader_group", text="Toon Shader", icon='MATERIAL')
        # row.operator("object.refresh_object_list", text="Refresh List")
        
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.label(text="No Material Object List:")
        layout.template_list("JC_UL_No_Mat_UIList", "", scene, "jc_no_material_object_list", scene, "jc_no_mat_object_index")
        layout.operator("object.select_object_from_jc_no_mat_list", text="Select Object")
        layout.operator("object.refresh_no_mat_object_list", text="Refresh List")

        # row.template_list("JC_Shader_UIList", "", scene, "selected_object_list", scene, "selected_object_list_index")
        # layout.template_list("JC_Shader_UIList", "compact", obj, "material_slots",obj, "active_material_index", type='COMPACT')
    

class JC_Select_Object_From_Hidden_List(bpy.types.Operator):
    bl_idname = "object.select_object_from_hidden_list"
    bl_label = "Select Object from List"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        JC_No_Mat_UL_OBJECT_OT_refresh_object_list.execute(self, context)
        scene = context.scene
        index = scene.jc_hidden_object_index
        try:
            name = scene.jc_hidden_object_list[index].name
        except IndexError:
            return {'FINISHED'}
        obj = bpy.data.objects.get(name)
        if obj:
            # print(obj)
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return {'FINISHED'}
    
class JC_Select_Object_From_No_Mat_List(bpy.types.Operator):
    bl_idname = "object.select_object_from_jc_no_mat_list"
    bl_label = "Select Object from List"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        JC_No_Mat_UL_OBJECT_OT_refresh_object_list.execute(self, context)
        scene = context.scene
        index = scene.jc_no_mat_object_index
        try:
            name = scene.jc_no_material_object_list[index].name
        except IndexError:
            return {'FINISHED'}
        obj = bpy.data.objects.get(name)
        if obj:
            # print(obj)
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return {'FINISHED'}


class JC_Select_Object_From_Hidden_List(bpy.types.Operator):
    bl_idname = "object.select_object_from_jc_hidden_list"
    bl_label = "Select Object from List"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # print('hello')
        scene = context.scene
        index = scene.jc_hidden_object_index
        try:
            name = scene.jc_hidden_object_list[index].name
        except IndexError:
            return {'FINISHED'}
        obj = bpy.data.objects.get(name)
        if obj:
            # print(obj)
            # obj.select_set(True)
            context.view_layer.objects.active = obj
        else:
            print('Object not found')

        return {'FINISHED'}

class JC_Hidden_UL_OBJECT_OT_refresh_object_list(bpy.types.Operator):
    bl_label = "Refresh Object List"
    bl_idname = "object.refresh_hidden_object_list"

    def execute(self, context):
        scene = context.scene
        scene.jc_hidden_object_list.clear()

        objects = bpy.data.objects
        # Get All Hidden Objects
        hidden_objects = [
            obj for obj in bpy.context.scene.objects
            if obj.hide_get()
        ]

        if not hidden_objects:
            return {'FINISHED'}
        
        for obj in hidden_objects:
            
            item = scene.jc_hidden_object_list.add()
            item.name = obj.name
        return {'FINISHED'}

class JC_Display_UL_OBJECT_OT_refresh_object_list(bpy.types.Operator):
    bl_label = "Refresh Object List"
    bl_idname = "object.refresh_display_object_list"

    def execute(self, context):
        scene = context.scene
        scene.jc_hidden_object_list.clear()

        objects = bpy.data.objects
        # Get All Hidden Objects
        hide_viewport_objs = [
            obj for obj in bpy.context.scene.objects
            if obj.hide_viewport
        ]

        if not hide_viewport_objs:
            return {'FINISHED'}
        
        for obj in hide_viewport_objs:
            
            item = scene.jc_hidden_object_list.add()
            item.name = obj.name
        return {'FINISHED'}

class JC_Renderable_UL_OBJECT_OT_refresh_object_list(bpy.types.Operator):
    bl_label = "Refresh Object List"
    bl_idname = "object.refresh_renderable_object_list"

    def execute(self, context):
        scene = context.scene
        scene.jc_hidden_object_list.clear()

        objects = bpy.data.objects

        # Get all unrederable objects
        renderable_objects = [
            obj for obj in bpy.context.scene.objects
            if obj.hide_render
        ]
        
        if not renderable_objects:
            return {'FINISHED'}
        # Print the names of these objects
        for obj in renderable_objects:
            
            item = scene.jc_hidden_object_list.add()
            item.name = obj.name
        return {'FINISHED'}

class JC_Select_Object_From_Display_List(bpy.types.Operator):
    bl_idname = "object.select_object_from_jc_display_list"
    bl_label = "Select Object from List"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # JC_Display_UL_OBJECT_OT_refresh_object_list.execute(self, context)
        scene = context.scene
        index = scene.jc_display_object_index
        try:
            name = scene.jc_display_object_list[index].name
        except IndexError:
            return {'FINISHED'}
        obj = bpy.data.objects.get(name)
        if obj:
            # print(obj)
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return {'FINISHED'}

class JC_Select_Object_From_Renderable_List(bpy.types.Operator):
    bl_idname = "object.select_object_from_jc_renderable_list"
    bl_label = "Select Object from List"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # JC_Display_UL_OBJECT_OT_refresh_object_list.execute(self, context)
        scene = context.scene
        index = scene.jc_renderable_object_index
        try:
            name = scene.jc_renderable_object_list[index].name
        except IndexError:
            return {'FINISHED'}
        obj = bpy.data.objects.get(name)
        if obj:
            # print(obj)
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return {'FINISHED'}
    
# Operator to refresh the list
# Add object if no material in the slot
class JC_No_Mat_UL_OBJECT_OT_refresh_object_list(bpy.types.Operator):
    bl_label = "Refresh Object List"
    bl_idname = "object.refresh_no_mat_object_list"

    def execute(self, context):
        scene = context.scene
        scene.jc_no_material_object_list.clear()

        objects = bpy.data.objects
        # No material in the slot
        # Get all objects that either have no materials or have empty material slots
        objects_with_empty_material_slots = [
            obj for obj in bpy.context.scene.objects 
            if obj.type == 'MESH' and (not obj.data.materials or any(mat is None for mat in obj.data.materials))
        ]


        if not objects_with_empty_material_slots:
            return {'FINISHED'}
        # Print the names of these objects
        for obj in objects_with_empty_material_slots:
            
            item = scene.jc_no_material_object_list.add()
            item.name = obj.name
                    
        # # Populate the list with selected objects
        # for obj in context.selected_objects:
        #     item = scene.jc_no_material_object_list.add()
        #     item.name = obj.name

        return {'FINISHED'}

# Export Shader Operator
class JC_Export_Shader(bpy.types.Operator):
    bl_idname = "shader.jc_export_shader"
    bl_label = "Export Shader"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        data = {}
        materials = bpy.data.materials
        for mat in materials:
            # print(mat)
            data[mat.name] = {}
            if not mat.node_tree:
                continue
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    for index,inp in enumerate(node.inputs):
                        # data[mat.name][inp.name] = node.inputs[inp.name].default_value
                        # print(inp.name,node.inputs[index].default_value,type(node.inputs[index].default_value))
                        if type(node.inputs[index].default_value) == bpy.types.bpy_prop_array:
                            data[mat.name][inp.name] = list(node.inputs[index].default_value)
                        else:
                            data[mat.name][inp.name] = node.inputs[index].default_value
        pprint(data)
                        
                    # data[mat.name]['Base Color'] = node.inputs['Base Color'].default_value
                    # data[mat.name]['Subsurface'] = node.inputs['Subsurface'].default_value
                    # data[mat.name]['Subsurface Radius'] = node.inputs['Subsurface Radius'].default_value
                    # data[mat.name]['Subsurface Color'] = node.inputs['Subsurface Color'].default_value
                    # data[mat.name]['Metallic'] = node.inputs['Metallic'].default_value
                    # data[mat.name]['Specular'] = node.inputs['Specular'].default_value
                    # data[mat.name]['Specular Tint'] = node.inputs['Specular Tint'].default_value
                    # data[mat.name]['Roughness'] = node.inputs['Roughness'].default_value
                    # data[mat.name]['Anisotropic'] = node.inputs['Anisotropic'].default_value
                    # data[mat.name]['Anisotropic Rotation'] = node.inputs['Anisotropic Rotation'].default_value
                    # data[mat.name]['Sheen'] = node.inputs['Sheen'].default_value
                    # data[mat.name]['Sheen Tint'] = node.inputs['Sheen Tint'].default_value
                    # data[mat.name]['Clearcoat'] = node.inputs['Clearcoat'].default_value
                    # data[mat.name]['Clearcoat Roughness'] = node.inputs['Clearcoat Roughness'].default_value
                    # data[mat.name]['IOR'] = node.inputs['IOR'].default_value
                    # data[mat.name]['Transmission'] = node.inputs['Transmission'].default_value
                    # data[mat.name]['Transmission Roughness'] = node.inputs['Transmission Roughness'].default_value
                    # data[mat.name]['Emission'] = node.inputs['Emission'].default_value
                    # data[mat.name]['Alpha'] = node.inputs['Alpha'].default_value
        
        return {'FINISHED'}
        
        
        
class JC_Compositor_Output(bpy.types.Operator):
    bl_idname = "node.jc_compositor_output"
    bl_label = "Create Output Node"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        outputPath = scene.render.filepath
        
        sel = context.selected_nodes
        
        renderLayer = sel[0]
        pos = renderLayer.location
        
        n = 0
        cryptoMattList = []
        for output in renderLayer.outputs:
            if 'Crypto' in output.name:
                cryptoMattList.append(output.name)
                continue
            # Create a new output node
            bpy.ops.node.add_node(use_transform=False, type="CompositorNodeOutputFile")
            # Set the output path
            node = context.active_node
            node.label = output.name
            node.name = output.name
            node.base_path = outputPath
            node.file_slots[0].path = output.name
            node.base_path = outputPath + "\\" + output.name
            node.format.file_format = 'PNG'
            node.format.color_mode = 'RGBA'
            node.location = (pos[0] + 600, pos[1] - n)
            # link the output node to the render layer
            try:
                scene.node_tree.links.new(node.inputs[0], renderLayer.outputs[output.name])
            except KeyError:
                bpy.ops.node.delete()
                break
                print('KeyError')
            n += 150
        bpy.ops.node.add_node(use_transform=False, type="CompositorNodeOutputFile")
        node = bpy.context.active_node
        node.format.file_format = 'OPEN_EXR_MULTILAYER'
        node.base_path = outputPath + "\\" + "CryptoMatt" + "\\" + "CryptoMatt_####" 
        node.label = 'CryptoMatt'
        node.name = 'CryptoMatt'
        index = 0
        for crypto in cryptoMattList:
            bpy.ops.node.output_file_add_socket()
            # rename the socket
            node.layer_slots[index].name = crypto
            # '__doc__', '__module__', '__slots__', '
            # active_input_index', 'base_path', 'bl_description', 
            # 'bl_height_default', 'bl_height_max', 'bl_height_min',
            # 'bl_icon', 'bl_idname', 'bl_label', 'bl_rna',
            # 'bl_static_type', 'bl_width_default', 'bl_width_max', 
            # 'bl_width_min', 'color', 'dimensions', 
            # 'draw_buttons', 'draw_buttons_ext', 'file_slots', 
            # 'format', 'height', 'hide', 'input_template', 
            # 'inputs', 'internal_links', 'is_registered_node_type',
            # 'label', 'layer_slots', 'location', 'mute', 'name',
            # 'output_template', 'outputs', 'parent', 'poll', 
            # 'poll_instance', 'rna_type', 'select', 'show_options',
            # 'show_preview', 'show_texture', 'socket_value_update',
            # 'tag_need_exec', 'type', 'update', 'use_custom_color',
            # 'width']
            # link the output node to the render layer
            bpy.context.scene.node_tree.links.new(node.inputs[index], renderLayer.outputs[crypto])
            
            index += 1
        return {'FINISHED'}

# Render Tools
class JC_PT_Render_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Tools"
    bl_label = "Render"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'

    def draw(self, context):
        layout = self.layout

        # Dropdown for Resolution Presets
        row = layout.row()
        row.label(text="Render Engine:")
        row.prop(context.scene.render, "engine", text="")
        # Device Dropdown
        row = layout.row()
        row.label(text="Device:")
        row.prop(context.scene.cycles, "device", text="")

        row = layout.row()

        row = layout.row()
        row.label(text="Custom Resolution:")
        col = row.column(align=True)
        col.prop(context.scene.render, "resolution_x", text="Width")
        col.prop(context.scene.render, "resolution_y", text="Height")

        # Start Frame
        row = layout.row()
        row.label(text="Start Frame:")
        row.prop(context.scene, "frame_start", text="")
        # End Frame
        row = layout.row()
        row.label(text="End Frame:")
        row.prop(context.scene, "frame_end", text="")


        # FPS slider
        row = layout.row()
        row.label(text="FPS:")
        row.prop(context.scene.render, "fps", text="")
        row = layout.row()
        row.label(text="=====================")
        
        # Output Path
        row = layout.row()
        row.label(text="Output Path:")
        col = row.column(align=True)
        col.prop(context.scene.render, "filepath", text="")
        
        # Output Properties
        row = layout.row()
        row.label(text="Output Properties:")
        col = row.column(align=True)
        col.prop(context.scene.render.image_settings, "file_format", text="Format")
        # Color
        col.prop(context.scene.render.image_settings, "color_mode", text="Color")
        # Color depth
        col.prop(context.scene.render.image_settings, "color_depth", expand=True,text="Depth")
        # Compression
        col.prop(context.scene.render.image_settings, "compression", text="Compression")

        # Render buttons
        row = layout.row()
        row.operator("render.render", text="Render Image")
        row.operator("render.render", text="Render Animation").animation = True
        row.operator("render.opengl", text="Viewport Render Image")
        row.operator("render.opengl", text="Viewport Render Animation").animation = True
        # Play blast button
        row = layout.row()
        row.operator("render.playblast", text="Playblast")
        # Submit to Deadline
        row = layout.row()
        row.operator("render.submit_to_deadline", text="Submit to Deadline")

######################### Panel for the Shader Editor ############################
# Shader Editor Panel
class JC_PT_Shader_Editor_Panel(bpy.types.Panel):
    bl_idname = "SHADER_PT_JC_Shader_Editor_Panel"
    bl_label = "Materials"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'JC_Tools'
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type in possible_object_types 
                and context.scene.render.engine in {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'HYDRA_STORM'} and context.space_data.tree_type == 'ShaderNodeTree')

    def draw_header(self, context):
        settings = context.window_manager.jc_wm_settings
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(settings, "mat_selected_only", text="", icon="RESTRICT_SELECT_OFF")
        row.prop(settings, "mat_visible_only", text="", icon="RESTRICT_VIEW_OFF")
        row.separator()

    def draw(self, context):
        settings = context.window_manager.jc_wm_settings
        draw_shadernodes_panel(self, context, settings.mat_selected_only, settings.mat_visible_only)
        row = self.layout.row()
        row.operator("shader.jc_export_shader", text="Export Shader")
# Compositor panel
class JC_PT_Compositing_Panel(bpy.types.Panel):
    bl_label = "Compositing"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "JC_Compositor_Tools"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type in possible_object_types 
                and context.scene.render.engine in {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'HYDRA_STORM'} and context.space_data.tree_type == 'CompositorNodeTree')

    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="NODE_COMPOSITING")

    def draw(self, context):
        pass

class JC_PT_Compositing_output(bpy.types.Panel):
    bl_label = "Output"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "JC_Compositor_Tools"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type in possible_object_types 
                and context.scene.render.engine in {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'HYDRA_STORM'} and context.space_data.tree_type == 'CompositorNodeTree')

    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="NODE_COMPOSITING")

    def draw(self, context):
        layout = self.layout
        # scene = context.scene
        # layout.prop(scene, "jc_compositor_output_path", text="Output Path")
        # text field for output path
        # row = layout.row()
        # row.label(text="Output Path:")
        # row.prop(context.scene, "jc_compositor_output_path", text="ttt")
        row = layout.row()
        # create a new output node
        row.operator("node.jc_compositor_output", text="Create Output Node")


# ============================Functions=================================================

def get_output_path():
    # Get the current scene
    scene = bpy.context.scene
    # Get the output path
    output_path = scene.render.filepath
    # Return the output path
    return output_path

def frame_change_handler(scene):
    # logger.info('Frame Changed')
    pass

# Function to link the latest modifier to selected objects
def link_latest_modifier_to_selected():
    # Get the active object (source object)
    source_obj = bpy.context.view_layer.objects.active
    
    # Get the selected objects excluding the active object
    selected_objects = [obj for obj in bpy.context.selected_objects if obj != source_obj]
    
    if not source_obj:
        print("No active object found.")
        return

    if not selected_objects:
        print("No selected objects found.")
        return

    if not source_obj.modifiers:
        print(f"Active object '{source_obj.name}' has no modifiers to link.")
        return

    # Get the last modifier of the active object
    latest_modifier = source_obj.modifiers[-1]

    for target_obj in selected_objects:
        # Add a similar modifier to each target object
        new_modifier = target_obj.modifiers.new(name=latest_modifier.name, type=latest_modifier.type)

        # Copy the properties of the source modifier to the target modifier
        for attr in dir(latest_modifier):
            if not attr.startswith("_") and hasattr(new_modifier, attr):
                try:
                    setattr(new_modifier, attr, getattr(latest_modifier, attr))
                except AttributeError:
                    # Skip attributes that can't be set
                    pass

        print(f"Linked modifier '{latest_modifier.name}' from '{source_obj.name}' to '{target_obj.name}'.")

# Remove all materials from selected objects
def remove_all_materials_from_selected():
    # Get the selected objects
    selected_objects = bpy.context.selected_objects

    for obj in selected_objects:
        # Remove all materials from the object
        obj.data.materials.clear()

    print("All materials removed from selected objects.")

# Clear all modifiers from selected objects
def clear_all_modifiers_from_selected():
    # Get the selected objects
    selected_objects = bpy.context.selected_objects

    for obj in selected_objects:
        # Clear all modifiers from the object
        obj.modifiers.clear()

    print("All modifiers removed from selected objects.")


# outliner context menu
# Define the custom operator
class JC_OT_Exclude_Selected_Collection_From_All_ViewLayers(bpy.types.Operator):
    bl_idname = "outliner.exclude_collection"
    bl_label = "Exclude from All View Layers"
    bl_description = "Exclude the selected collection from all view layers"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.collection is not None

    def execute(self, context):
        collection = context.collection
        scene = context.scene

        if not collection:
            self.report({'WARNING'}, "No collection selected.")
            return {'CANCELLED'}
        
        # Loop through all view layers and exclude the collection
        for view_layer in scene.view_layers:
            layer_collection = view_layer.layer_collection
            self._exclude_collection(layer_collection, collection)

        self.report({'INFO'}, f"Collection '{collection.name}' excluded from all view layers.")
        return {'FINISHED'}

    def _exclude_collection(self, layer_collection, target_collection):
        """Recursively search and exclude the target collection in the view layer"""
        if layer_collection.collection == target_collection:
            layer_collection.exclude = True
            return

        for child in layer_collection.children:
            self._exclude_collection(child, target_collection)

# Function to add the operator to the Outliner context menu
def JC_OutLiner_Context_Menu(self, context):
    layout = self.layout
    if context.collection:
        layout.separator()
        layout.operator(JC_OT_Exclude_Selected_Collection_From_All_ViewLayers.bl_idname, text="Exclude from All View Layers")

# From MataLogue
def draw_shadernodes_panel(self, context, selected_only=False, visible_only=False):
    def draw_item(context, col, mat, indent):
        row = col.row(align=True)
        for i in range(indent):
            row.label(text="", icon="BLANK1")

        try:
            icon_val = layout.icon(mat)
        except RuntimeError:
            icon_val = 1
            print("WARNING [Mat Panel]: Could not get icon value for %s" % mat.name)

        active = mat == context.space_data.id and context.space_data.path[-1].node_tree.name == mat.node_tree.name
        op = row.operator(
            "matalogue.goto_mat",
            text=mat.name,
            emboss=active,
            icon_value=icon_val,
        )
        op.mat = mat.name
        if mat.library:
            row.label(text="", icon="LINKED")
        elif mat.use_fake_user:
            row.label(text="", icon="FAKE_USER_ON")
        elif not mat.users:
            row.alert = True
            row.label(text="", icon="ORPHAN_DATA")

        # Node trees in this tree:
        if active:
            already_drawn = []
            for node in mat.node_tree.nodes:
                if node.type == "GROUP" and node.node_tree.name not in already_drawn:
                    row = col.row(align=True)
                    row.label(text="", icon="BLANK1")
                    op = row.operator("matalogue.goto_group", text=node.node_tree.name, emboss=False, icon="NODETREE")
                    op.tree_type = "ShaderNodeTree"
                    op.tree = node.node_tree.name
                    already_drawn.append(node.node_tree.name)

    def used_by_selected(mat):
        for obj in context.selected_objects:
            for slot in obj.material_slots:
                if slot.material == mat:
                    return True
        return False

    def used_by_visible(mat):
        for obj in context.view_layer.objects:
            if obj.visible_get():
                for slot in obj.material_slots:
                    if slot.material == mat:
                        return True
        return False

    layout = self.layout

    col = layout.column(align=True)

    materials = []
    for mat in bpy.data.materials:
        if mat.use_nodes:
            if selected_only and not used_by_selected(mat):
                continue
            if visible_only and not used_by_visible(mat):
                continue
            materials.append(mat)

    num_drawn = 0
    for mat in materials:
        draw_item(context, col, mat, 0)
        num_drawn += 1

    if num_drawn == 0:
        row = col.row()
        row.alignment = "CENTER"
        row.enabled = False
        if selected_only:
            row.label(text="No selected materials")
        elif visible_only:
            row.label(text="No visible materials")
        else:
            row.label(text="None")

classes =  [
            JC_WM_Settings,
            JC_PT_Common_Tools,
            JC_PT_Rig_Tools,
            JC_Animation_Tools,
            JC_Visibility_Tools,
            JC_PT_Import_Panel,
            JC_PT_Shader_Panel,
            JC_PT_Render_Panel,
            JCLinkLastModifier,
            JCSolidShaderRed,
            JCSolidShaderGreen,
            JCSolidShaderBlue,
            JCToonBaseShaders,
            JC_PT_Shader_Editor_Panel,
            JCClearAllModifiers,
            JCRemoveMaterials,
            JCPlayblast,
            JC_NO_MAT_OBJECT_ITEM,
            JC_HIDDEN_OBJECT_ITEM,
            JC_Hidden_UL_OBJECT_OT_refresh_object_list,
            JC_Select_Object_From_Hidden_List,
            JC_Export_Shader,
            # JC_UL_RENDERABLE_UIList,
            JC_Select_Object_From_Renderable_List,
            JC_Renderable_UL_OBJECT_OT_refresh_object_list,
            JC_Display_UL_OBJECT_OT_refresh_object_list,
            JC_Select_Object_From_Display_List,
            JC_UL_No_Mat_UIList,
            JC_UL_HIDDEN_UIList,
            JC_No_Mat_UL_OBJECT_OT_refresh_object_list,
            JC_Select_Object_From_No_Mat_List,
            JCSetKeyFrame,
            JCSetKeyFrameTranslate,
            JCSetKeyFrameRotate,
            JCSetKeyFrameScale,
            JC_FBX_Camera_Importer,
            JC_Alembic_Importer,
            submit_to_deadline,
            JCHideViewPort,
            JCUnhideViewPort,
            JCHideRender,
            JCMatchToArmatureName,
            JCCopyBoneDampedTrack,
            JC_PT_Compositing_Panel,
            JC_PT_Compositing_output,
            JC_Compositor_Output,
            JC_OT_Exclude_Selected_Collection_From_All_ViewLayers
            # JCCompositorOutput
            # JCFileBuilder,
            # BasicMenu
            ]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.jc_wm_settings = bpy.props.PointerProperty(type=JC_WM_Settings)
    bpy.types.Scene.jc_hidden_object_list = bpy.props.CollectionProperty(type=JC_HIDDEN_OBJECT_ITEM)
    bpy.types.Scene.jc_hidden_object_index = bpy.props.IntProperty(name="Index", default=0)
    bpy.types.Scene.jc_no_material_object_list = bpy.props.CollectionProperty(type=JC_NO_MAT_OBJECT_ITEM)
    bpy.types.Scene.jc_no_mat_object_index = bpy.props.IntProperty(name="Index", default=0)
    bpy.types.OUTLINER_MT_context_menu.append(JC_OutLiner_Context_Menu)
def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.jc_hidden_object_list
    del bpy.types.Scene.jc_hidden_object_index
    del bpy.types.Scene.jc_no_material_object_list
    del bpy.types.Scene.jc_no_mat_object_index
    bpy.types.OUTLINER_MT_context_menu.remove(JC_OutLiner_Context_Menu)
if __name__ == "__main__":
    register()