import bpy
from bpy.types import Operator

class MyFirstToolOp(Operator):
    bl_idname = "jtools.my_first_tool_op"
    bl_label = "JTools - My First Tool"
    # bl_description = "This is my first tool"
    # bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        return {'RUNNING_MODAL'}