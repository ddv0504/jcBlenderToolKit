bl_info = {
"name": "JTools",
"author": "JCO",
"version": (0, 0, 1),
"blender": (4, 00, 1),
"description": "Toolset for animation production",
"category": "Development"
    }

import bpy
from . import MyFirstTool
from . import MyGui
from importlib import reload
from . import MyGui

vfx_tools = [
    
    MyFirstTool.MyFirstToolOp,
    MyGui.MyFirstGuiOp
]

def register():
    reload(MyFirstTool)
    reload(MyGui)
    for cls in vfx_tools:
        bpy.utils.register_class(cls)

def unregister():
    for cls in vfx_tools:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()