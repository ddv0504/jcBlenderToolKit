from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import bpy
import qdarkstyle

class Widget(QWidget):
    def __init__(self, parent=None,*args, **kwargs):
        super(Widget, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("My First GUI")
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.show()
    def create_widgets(self):
        self.label = QLabel("This is my first GUI")
        self.button1 = QPushButton("Button 1")
        self.button = QPushButton("Close")
        
    def create_layouts(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button1)
        self.setLayout(self.layout)
        
    def create_connections(self):
        self.button.clicked.connect(self.close)
        self.button1.clicked.connect(self.print_hello)
    
    def print_hello(self):
        
        print(bpy.context.view_layer.objects.active)