#-*- coding: utf-8 -*-
import bpy
import os
import sys
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


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
    "blender": (4, 0, 0),
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Development" }


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

# Import Tools
class JC_Import_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Import_Panel"
    bl_label = "Import"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Render_Tools'

    def draw(self, context):
        layout = self.layout
        # FBX Camera Importer
        row = layout.row()
        row.label(text="Import FBX Camera:")
        row.operator("import.jc_fbx_camera", text="Import FBX Camera")

# Shader Tools
class JC_Shader_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Shader_Tools"
    bl_label = "Shaders"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Render_Tools'

    def draw(self, context):
        layout = self.layout
        # Shader List
        row = layout.row()
        row.label(text="Shader List:")
        row.operator("shader.jc_shader_red", text="Red", icon='SEQUENCE_COLOR_01')
        row.operator("shader.jc_shader_green", text="Green", icon='SEQUENCE_COLOR_04')
        row.operator("shader.jc_shader_blue", text="Blue", icon='SEQUENCE_COLOR_05')
        


    
# Render Tools
class JC_Render_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_JC_Render_Tools"
    bl_label = "Render"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'JC_Render_Tools'

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
        # Submit to Deadline
        row = layout.row()
        row.operator("render.submit_to_deadline", text="Submit to Deadline")




classes = [JC_Import_Panel,JC_Shader_Panel,JC_Render_Panel,JCSolidShaderRed,JCSolidShaderGreen,JCSolidShaderBlue,JC_FBX_Camera_Importer,submit_to_deadline]
# Frame Change Handler
def frame_change_handler(scene):
    # logger.info('Frame Changed')
    pass

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.utils.register_class(JC_Render_Tools)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    #bpy.utils.unregister_class(JC_Render_Tools)
    



if __name__ == "__main__":
    register()

    # JC_Render_Tools('jc.render_tools')