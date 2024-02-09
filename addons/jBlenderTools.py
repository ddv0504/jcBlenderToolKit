#-*- coding: utf-8 -*-
import sys
import os
import pprint
currentPath = os.path.dirname(os.path.abspath(__file__))
package = os.path.join(currentPath, 'package')
if not package in sys.path:
    sys.path.append(package)


bl_info = {
    "name": "JCTools",
    "description": "B1 Blender Pipeline Tools",
    "author": "JCO",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Development" }
    
import bpy
from bpy.types import Panel, Operator
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
import qdarkstyle
import logging


# QThread
class RenderThread(QThread):
    def __init__(self, parent=None):
        super(RenderThread, self).__init__(parent)
    def run(self):
        pass

# logger
logger = logging.getLogger('JC_BlenderTool')
# Main Window
class JC_BlenderTool_UI(QMainWindow):
    renderLst = []
    def __init__(self, parent=None):
        super(JC_BlenderTool_UI, self).__init__(parent)
        self.setWindowTitle("JC_BlenderTool")
        # self.setFixedSize(400, 300)
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        self.setForm()
        # Show
        self.show()

    def setForm(self):
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.model_tab_widget = QWidget()
        self.model_tab_layout = QVBoxLayout()
        self.model_tab_widget.setLayout(self.model_tab_layout)
        self.tab_widget.addTab(self.model_tab_widget, "Model")

        self.shader_tab_widget = QWidget()
        self.shader_tab_layout = QVBoxLayout()
        self.shader_tab_widget.setLayout(self.shader_tab_layout)
        self.tab_widget.addTab(self.shader_tab_widget, "Shader")
        
        self.rig_tab = QWidget()
        self.rig_tab_layout = QVBoxLayout()
        self.rig_tab.setLayout(self.rig_tab_layout)
        self.tab_widget.addTab(self.rig_tab, "Rig")

        self.anim_tab = QWidget()
        self.anim_tab_layout = QVBoxLayout()
        self.anim_tab.setLayout(self.anim_tab_layout)
        self.tab_widget.addTab(self.anim_tab, "Animation")

        self.render_tab = QWidget()
        self.render_tab_layout = QVBoxLayout()
        self.render_tab.setLayout(self.render_tab_layout)
        self.tab_widget.addTab(self.render_tab, "Render")

        self.setTabModel()
        self.setTabShader()
        self.setTabRig()
        self.setTabAnim()
        self.setTabRender()

    def setTabModel(self):
        self.model_tab_layout.addWidget(QLabel("Model"))
        self.model_tab_layout.addWidget(QPushButton("Model"))

    def setTabShader(self):
        self.shader_sub_tab_widget = QTabWidget()
        self.shader_tab_layout.addWidget(self.shader_sub_tab_widget)

        self.toon_widget = QWidget()
        self.toon_layout = QVBoxLayout()
        self.toon_widget.setLayout(self.toon_layout)
        self.shader_sub_tab_widget.addTab(self.toon_widget, "Toon")

        self.setTabToon()
    
    def setTabToon(self):
        self.eevee_toon_widget = QWidget()
        self.eevee_toon_layout = QHBoxLayout()
        self.eevee_toon_widget.setLayout(self.eevee_toon_layout)
        self.toon_layout.addWidget(self.eevee_toon_widget)
        self.generateToonShader_label = QLabel("Generate EEVEE Toon Shader")
        self.eevee_toon_layout.addWidget(self.generateToonShader_label)

        self.generateToonShader_btn = QPushButton("Generate")
        self.eevee_toon_layout.addWidget(self.generateToonShader_btn)

    def setTabRig(self):
        self.rig_tab_layout.addWidget(QLabel("Rig"))
        self.rig_tab_layout.addWidget(QPushButton("Rig"))

    def setTabAnim(self):
        self.anim_tab_layout.addWidget(QLabel("Animation"))
        self.anim_tab_layout.addWidget(QPushButton("Animation"))

    def setTabRender(self):
        # Scroll Area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.render_tab_layout.addWidget(self.scrollArea)
        # headSplitter = QSplitter()
        self.scrollLayout = QVBoxLayout()
        self.scrollAreaWidgetContents.setLayout(self.scrollLayout)

        headLayout = QHBoxLayout()
        self.scrollLayout.addLayout(headLayout)
        self.allCB = QCheckBox("All")
        headLayout.addWidget(self.allCB)

        camsLabel = QLabel("Cameras:")

        headLayout.addWidget(camsLabel)
        plusBtn = QPushButton("+")
        headLayout.addWidget(plusBtn)
        # minusBtn = QPushButton("-")
        # headLayout.addWidget(minusBtn)

        midLayout = QVBoxLayout()
        self.scrollLayout.addLayout(midLayout)
        self.scrollLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        btnLayout = QHBoxLayout()
        self.render_tab_layout.addLayout(btnLayout)
        self.renderBtn = QPushButton("Render")
        btnLayout.addWidget(self.renderBtn)

        self.viewportRender = QPushButton("Viewport Render")
        btnLayout.addWidget(self.viewportRender)

        self.renderProgress = QProgressBar()
        self.render_tab_layout.addWidget(self.renderProgress)

        plusBtn.clicked.connect(self.setOutput)
        self.viewportRender.clicked.connect(lambda: self.render(viewport=True))

        self.renderBtn.clicked.connect(self.render)

    def setOutput(self):
        
        self.output = outputWidget(self)
        self.scrollLayout.insertWidget(self.render_tab_layout.count() - 2, self.output)
        self.renderLst.append(self.output)
        print(self.renderLst)
    def frameChangeHandler(self, scene,*args):
        maxFrame = bpy.context.scene.frame_end
        startFrame = bpy.context.scene.frame_start
        currentFrame = bpy.context.scene.frame_current
        self.renderProgress.setValue((currentFrame - startFrame) / (maxFrame - startFrame) * 100)
        
    def render(self,viewport=False):
        for outputWidget in self.renderLst:
            info = outputWidget.getInfo()
            cam = info['cam']
            renderPath = info['output']
            startFrame = int(info['startFrame'])
            endFrame = int(info['endFrame'])
            width = int(info['width'])
            height = int(info['height'])
            bpy.context.scene.camera = bpy.data.objects[cam]
            bpy.context.scene.render.filepath = renderPath
            bpy.context.scene.frame_start = startFrame
            bpy.context.scene.frame_end = endFrame
            bpy.context.scene.render.resolution_x = width
            bpy.context.scene.render.resolution_y = height
            bpy.app.handlers.frame_change_pre.append(self.frameChangeHandler)
            if viewport:
                return
                # bpy.ops.render.opengl(animation=True)
            else:
                # print(cam,renderPath,startFrame,endFrame,width,height)
                # bpy.app.handlers.frame_change_pre.append(self.frameChangeHandler)
                bpy.ops.render.render(animation=True,use_viewport=False)
        
        self.renderProgress.setValue(100)
        # Show Message
        QMessageBox.information(self, "Render", "Render Completed")
        # Remove Handler After Render
        bpy.app.handlers.frame_change_pre.remove(self.frameChangeHandler)    
        
    def generateToonShader(self):
        
        # Selected object
        obj = bpy.context.active_object
        name = obj.name
        # Set Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        data = obj.data
        
        
        # Clear material slots
        obj.data.materials.clear()

        # Get the material
        mat = obj.active_material
        shaderName = '%s_toon_shader' % name
            
        # Delete shader if object name shader is exists
        if bpy.data.materials.get(shaderName):
            materials = bpy.data.materials.get(shaderName)
            bpy.data.materials.remove(materials)
        
        # Clear materials
        materials = obj.data.materials
        
        mat = bpy.data.materials.new(name='%s_toon_shader' % name)
        obj.data.materials.append(mat)
        mat.use_nodes = True

        # Assign it to the active object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
            
        
        # Clear Nodes
        mat.node_tree.nodes.clear()
        
        # Build Node Tree
        
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Create the material output node
        mat_output = nodes.new(type='ShaderNodeOutputMaterial')
        # bpy.ops.node.add_node(use_transform=True, type="ShaderNodeRGB")

        # RGB
        baseColor_rgb =nodes.new(type="ShaderNodeRGB")
        baseColor_rgb.name = 'baseColor_rgb'
        baseColor_rgb.location = (-1000,0)
        
        
        # Link the nodes
        # links.new(toon.outputs['BSDF'], mat_output.inputs['Surface'])

    def closeEvent(self, event):
        # self.app.quit()
        self.event_loop.exit()
        event.accept()

class outputWidget(QGroupBox):
    info = {}
    def __init__(self, parent=None):
        super(outputWidget, self).__init__(parent)
        self.parent=parent
        mainSplitter = QSplitter()
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(mainSplitter)
        leftWidget = QWidget()
        leftLayout = QVBoxLayout()
        leftWidget.setLayout(leftLayout)
        mainSplitter.addWidget(leftWidget)
        rightWidget = QWidget()
        rightLayout = QVBoxLayout()
        rightWidget.setLayout(rightLayout)
        mainSplitter.addWidget(rightWidget)
        renderSizeLayout = QHBoxLayout()
        leftLayout.addLayout(renderSizeLayout)

        renderSizeLayout.addWidget(QLabel("Render Size:"))
        self.width = QLineEdit()
        renderSizeLayout.addWidget(self.width)
        xLabel = QLabel("x")
        renderSizeLayout.addWidget(xLabel)
        self.height = QLineEdit()
        renderSizeLayout.addWidget(self.height)
        renderSizeLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        self.camLabel = QLabel("Camera:")
        leftLayout.addWidget(self.camLabel)
        self.cam = QLineEdit()
        leftLayout.addWidget(self.cam)

        buttonLayout = QHBoxLayout()
        leftLayout.addLayout(buttonLayout)
        self.importBtn = QPushButton("Import")
        buttonLayout.addWidget(self.importBtn)
        self.pickBtn = QPushButton("Pick")
        buttonLayout.addWidget(self.pickBtn)
        self.outputLabel = QLabel("Output:")
        leftLayout.addWidget(self.outputLabel)
        self.output = QLineEdit()
        leftLayout.addWidget(self.output)
        self.browseBtn = QPushButton("Browse")
        leftLayout.addWidget(self.browseBtn)
        frameRangeLayout = QHBoxLayout()
        leftLayout.addLayout(frameRangeLayout)
        frameRangeLayout.addWidget(QLabel("Frame Range:"))
        self.startFrame = QLineEdit('101')
        frameRangeLayout.addWidget(self.startFrame)
        self.endFrame = QLineEdit()
        frameRangeLayout.addWidget(self.endFrame)
        frameRangeLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.removeBtn = QPushButton("Remove")
        rightLayout.addWidget(self.removeBtn)
        mainSplitter.setSizes([350, 50])

        self.importBtn.clicked.connect(self.importFile)
        self.pickBtn.clicked.connect(self.pick)
        self.browseBtn.clicked.connect(self.browse)
        self.removeBtn.clicked.connect(self.deleteLater)
    

    def deleteLater(self):
        self.parent.renderLst.remove(self)
        super().deleteLater()    
    def importFile(self):
        fd = QFileDialog()
        filename = fd.getOpenFileName()
        # Import File
        bpy.ops.import_scene.fbx(filepath=filename[0],anim_offset=0)
        # Get Active Object
        camera = bpy.context.view_layer.objects.selected[0]
        self.cam.setText(camera.name)
        if camera:
            
            if type(camera.data) == bpy.types.Camera:
                
                camera.data.sensor_fit = 'VERTICAL'
                animation_data = camera.animation_data
                first_frame = int(animation_data.action.frame_range[0])
                self.startFrame.setText(str(first_frame))
                last_frame = int(animation_data.action.frame_range[-1])
                self.endFrame.setText(str(last_frame))
                # Set Camera Clip Start
                camera.data.clip_start = 0.1
                # Set Camera Clip End
                camera.data.clip_end = 10000

    def pick(self):
        context = bpy.context
        # Get Selected Objects
        selected = context.view_layer.objects.active
        # If Selected Objects Is Not Camera
        if selected.type != 'CAMERA':
            # Show Error Message
            QMessageBox.critical(self, "Error", "Please select a camera")
            return
        # Set Camera Name
        self.cam.setText(selected.name)

        # self.cam.setText(bpy.context.scene.camera.name)
    def browse(self):
        fd = QFileDialog()
        self.output.setText(fd.getExistingDirectory())
    
    def getInfo(self):
        self.info['cam'] = self.cam.text()
        self.info['output'] = self.output.text()
        self.info['startFrame'] = self.startFrame.text()
        self.info['endFrame'] = self.endFrame.text()
        self.info['width'] = self.width.text()
        self.info['height'] = self.height.text()
        return self.info
    def closeEvent(self,*args, **kwargs):
        self.deleteLater()
        return super().closeEvent(**kwargs)

class JC_BlenderTool_Panel(Panel):
    bl_category = "JC_BlenderTool"
    bl_label = "JC_BlenderTool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.operator('pyside.jc_blender_tool_window',icon = 'TOPBAR')
        
class JC_BlenderTool_Operator(Operator):
    '''  '''
    bl_idname = 'pyside.jc_blender_tool_window'
    bl_label = "MainWindow"
    bl_options = {'REGISTER'}
    
    
    def execute(self, context):
        
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(['blender'])

        self.event_loop = QEventLoop()

        self.widget = JC_BlenderTool_UI()
        

        return {'FINISHED'}


# Frame Change Handler
def frame_change_handler(scene):
    # logger.info('Frame Changed')
    pass

def register():
    bpy.utils.register_class(JC_BlenderTool_Panel)
    bpy.utils.register_class(JC_BlenderTool_Operator)

def unregister():
    bpy.utils.unregister_class(JC_BlenderTool_Panel)
    bpy.utils.unregister_class(JC_BlenderTool_Operator)



if __name__ == "__main__":
    register()