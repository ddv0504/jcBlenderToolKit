import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from bpy.types import Operator

from . import MyFirstGuiUI
from importlib import reload
reload(MyFirstGuiUI)

class MyFirstGuiOp(Operator):
    bl_idname = "jtools.my_first_gui_op"
    bl_label = "JTools - My First GUI"
    # bl_description = "This is my first tool"
    # bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        self.widget = MyFirstGuiUI.Widget()
        self.widget.show()
        
        return {'RUNNING_MODAL'}