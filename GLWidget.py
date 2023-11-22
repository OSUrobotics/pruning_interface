import sys
sys.path.append('../')


from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QSlider, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMainWindow, QFrame, QGridLayout, QPushButton, QOpenGLWidget
from PySide2.QtCore import Qt, Signal, SIGNAL, QPoint
from PySide2.QtOpenGL import QGLWidget
from PySide2.QtGui import QOpenGLVertexArrayObject, QOpenGLBuffer, QOpenGLShaderProgram, QOpenGLShader, QOpenGLContext, QVector4D, QCloseEvent
from shiboken2 import VoidPtr
# from PySide2.shiboken2 import VoidPtr

# from PyQt6 import QtCore      # core Qt functionality
# from PyQt6 import QtGui       # extends QtCore with GUI functionality
# from PyQt6 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU        # OpenGL Utility Library, extends OpenGL functionality
# from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo
import pywavefront
import numpy as np
import ctypes                 # to communicate with c code under the hood



class Shader:
    def __init__(self, shaderType: str, shaderName: str, shaderPath: str):
        self.shader = None
        self.shaderType = shaderType
        self.shaderName = shaderName
        self.shaderPath = shaderPath

        # shaderSource = self.shaders[shaderType]  # gets the source code from above
        if shaderType == "vertex":
            self.shader = QOpenGLShader(QOpenGLShader.Vertex)
        else:
            self.shader = QOpenGLShader(QOpenGLShader.Fragment)

        isCompiled = self.shader.compileSourceFile(shaderPath)

        if isCompiled is False:
            print(self.shader.log())
            raise ValueError(
                "{0} shader {2} known as {1} is not compiled".format(shaderType, shaderName, shaderPath)
            )
        
    def getShader(self):
        return self.shader



class Mesh:
    def __init__(self, fname=None):
        self.fname = fname
        self.vertices = [] 
        self.vertex_count = 0 

        # loading the shaders
        self.vshader = None
        self.fshader = None
        
        # loading and getting all the vertices information
        self.mesh = self.load_mesh(fname)
        self.faces = self.mesh.mesh_list[0].faces # Gives us the triangles that are drawn by the system

        # get the vertices in the correct order based on faces
        # self.get_vertices() 
        self.vertices = self.get_vertex_list()
        self.vertex_count = len(self.vertices) / 3
        
        self.tree_color = QVector4D(0.5, 0.25, 0.0, 0.0) # brown color
           
       
        
        # opengl data
        self.context = QOpenGLContext()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = QOpenGLShaderProgram()
        # self.vao.create()
        # vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)         
        
    def load_mesh(self, fname):
        mesh = pywavefront.Wavefront(fname, collect_faces = True)
        return mesh


    # Uses the faces information to extract the correct ordering for drawing triangles based on the vertex location
    def get_vertex_list(self):
        vertices = []
        for face in self.faces:
            for vertex in face:
                vertices.extend(self.mesh.vertices[vertex]) # gets the exact vertex point and adds it to the list of values
                # print("Vertex {0} gets point {1}".format(v2, self.mesh.vertices[v2]))
        # print(vertices[:10])
        return np.array(vertices, dtype=ctypes.c_float)
            
            

    def initializeShaders(self):
        shaderName = "tree"
        self.vshader = Shader(shaderType="vertex", shaderName=shaderName, shaderPath='shaders/shader.vert').getShader()
        self.fshader = Shader(shaderType="fragment", shaderName=shaderName, shaderPath='shaders/shader.frag').getShader()

        # creating shader program
        self.program = QOpenGLShaderProgram(self.context)
        self.program.addShader(self.vshader)  # adding vertex shader
        self.program.addShader(self.fshader)  # adding fragment shader

        # bind attribute to a location
        self.program.bindAttributeLocation("vertexPos", 0) # notice the correspondance of the
        # name vertexPos in the vertex shader source


        # link the shader program
        isLinked = self.program.link()
        print("Shader program is linked: ", isLinked)

        # bind the program --> activates it!
        self.program.bind()

        # specify uniform value
        colorLoc = self.program.uniformLocation("color") 
        # notice the correspondance of the
        # name color in fragment shader
        # we also obtain the uniform location in order to 
        # set value to it
        self.program.setUniformValue(colorLoc,
                                     self.tree_color)
        # notice the correspondance of the color type vec4 
        # and the type of triangleColor



    def initializeMeshArrays(self):
        # create vao and vbo
        # vao
        isVao = self.vao.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)

        # vbo
        isVbo = self.vbo.create()
        isBound = self.vbo.bind()

        float_size = ctypes.sizeof(ctypes.c_float)

        # allocate buffer space
        self.vbo.allocate(self.vertices.tobytes(), 
                          float_size * self.vertices.size)

        
        # check if vao and vbo are created
        print('vao created: ', isVao)
        print('vbo created: ', isVbo)
        print('vbo bound: ', isBound)

        self.setupMeshAttribArrays()

        self.program.release()
        vaoBinder = None

    
    def setupMeshAttribArrays(self):
        self.vbo.bind()
        funcs = self.context.functions()  # self.context.currentContext().functions()  
        funcs.glEnableVertexAttribArray(0)

        float_size = ctypes.sizeof(ctypes.c_float)
        null = VoidPtr(0)
        funcs.glVertexAttribPointer(0,                 # where the array starts
                                3,                     # how long the vertex point is i.e., (x, y, z)
                                gl.GL_FLOAT,           # is a float
                                gl.GL_FALSE,
                                3 * float_size,        # size in bytes to the next vertex (x, y, z)
                                null)                  # where the data is stored (starting position) in memory
        
        self.vbo.release()

    def drawMesh(self):
        # drawing code
        funcs = self.context.functions()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()

        funcs.glDrawArrays(gl.GL_TRIANGLES,                     # telling it to draw triangles between vertices
                           0,                                   # where the vertices starts
                           self.vertex_count)                   # how many vertices to draw

        self.program.release()
        self.vao.release()
        vaoBinder = None

        # gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertex_count)
    
    
    def cleanUpMeshGL(self):
        self.context.makeCurrent(self)      # make context to release the current one
        self.vbo.destroy()                  # destroy the buffer
        del self.program                    # delete the shader program
        self.program = None                 # change pointed reference
        self.doneCurrent()                  # no current context for current thread

    def destroy(self):
        gl.glDeleteVertexArrays(1, (self.vao,))
        gl.glDeleteBuffers(1, (self.vbo,))


##############################################################################################################
#
#  Code inspiration taken from:
#  https://github.com/D-K-E/pyside-opengl-tutorials/blob/master/tutorials/01-triangle/TriangleTutorial.ipynb
#  https://github.com/PyQt5/Examples/blob/master/PySide2/opengl/hellogl2.py#L167 
#
##############################################################################################################

class GLWidget(QOpenGLWidget): 
    # for the rotation of the widget window
    xRotationChanged = Signal(int)
    yRotationChanged = Signal(int)
    zRotationChanged = Signal(int)

    def __init__(self):
        super().__init__()
        # self.parent = parent
        self.mesh = Mesh('tree_files/side2_branch_1.obj')
        # self.mesh = Mesh('tree_files/exemplarTree.obj')
        self.background_color = QtGui.QColor(0, 59, 111) 

        # Rotation values
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.lastPos = 0

        # opengl data
        self.context = QOpenGLContext()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = QOpenGLShaderProgram()


    def xRotation(self):
        return self.xRot
    
    def yRotation(self):
        return self.yRot
    
    def zRotation(self):
        return self.zRot
    

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle


    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.emit(SIGNAL("xRotationChanged(int)"), angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.emit(SIGNAL("yRotationChanged(int)"), angle) # telling the system what exactly has changed
            self.update()
    
    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.emit(SIGNAL("zRotationChanged(int)"), angle)
            self.update()
    
    
    def mousePressEvent(self, event) -> None:
        self.lastPos = QPoint(event.pos())
        # return super().mousePressEvent(event)
    
    
    def getGlInfo(self):
        "Get opengl info"
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
            """.format(
                gl.glGetString(gl.GL_VENDOR),
                gl.glGetString(gl.GL_RENDERER),
                gl.glGetString(gl.GL_VERSION),
                gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
            )
        return info

    # # Overrides the closeEvent function in QOpenGLWidget
    # def closeEvent(self, event: QCloseEvent) -> None:
    #     self.cleanUpGl() 
    #     return super().closeEvent(event)
    
    # Basic Function needed by OpenGL
    def initializeGL(self):
        print('gl initial')
        print(self.getGlInfo())

        # create context 
        self.context.create()
        # if the close signal is given we clean up the ressources as per defined above
        self.context.aboutToBeDestroyed.connect(self.cleanUpGl)  


       # initialize functions
        funcs = self.context.functions()  # we obtain functions for the current context
        funcs.initializeOpenGLFunctions() # we initialize functions
        funcs.glClearColor(self.background_color.redF(), self.background_color.greenF(), self.background_color.blueF(), self.background_color.alphaF()) # the color that will fill the frame when we call the function
        # for cleaning the frame in paintGL

        funcs.glEnable(gl.GL_DEPTH_TEST) # enables depth testing so things are rendered correctly
    
        self.mesh.initializeShaders()
        self.mesh.initializeMeshArrays()

    
    def setupVertexAttribs(self):
        self.vbo.bind()
        funcs = self.context.functions()  # self.context.currentContext().functions()  
        funcs.glEnableVertexAttribArray(0)

        float_size = ctypes.sizeof(ctypes.c_float)
        null = VoidPtr(0)
        funcs.glVertexAttribPointer(0,                 # where the array starts
                                3,                     # how long the vertex point is i.e., (x, y, z)
                                gl.GL_FLOAT,           # is a float
                                gl.GL_FALSE,
                                3 * float_size,        # size in bytes to the next vertex
                                null)                  # where the data is stored (starting position) in memory
        
        self.vbo.release()

    

    # Basic function required by OpenGL
    def resizeGL(self, width: int, height: int):
        funcs = self.context.functions()
        funcs.glViewport(0, 0, width, height)
        # gl.glViewport(0, 0, width, height)

        # # funcs.glMatrixMode(gl.GL_PROJECTION) # used to define the vieweing volume contianing the projection transformation
        gl.glMatrixMode(gl.GL_PROJECTION) 
        
        # # funcs.glLoadIdentity()
        gl.glLoadIdentity()
        aspect = width / float(height)        
        GLU.gluPerspective(45.0, aspect, 1.0, 100.0) # defines the viewing frustrum
        # # funcs.glMatrixMode(gl.GL_MODELVIEW)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    # Cleans up the buffers upon exiting the app
    def cleanUpGl(self):
        self.context.makeCurrent(self)      # make context to release the current one
        self.vbo.destroy()                  # destroy the buffer
        del self.program                    # delete the shader program
        self.program = None                 # change pointed reference
        self.doneCurrent()                  # no current context for current thread

    # Basic function needed for OpenGL
    def paintGL(self):
        funcs = self.context.functions()
        # clean up what was drawn in the previous frame
        funcs.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT) 
        self.mesh.drawMesh()
        

# Creating sliders on the screen
class Slider:
    def __init__(self, min: int, max: int, step_size):
        self.layout = QHBoxLayout()
        self.min = min
        self.max = max
        self.step_size = step_size
        self.slider = self.createSlider()

    def createSlider(self):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(self.min, self.max)
        slider.setSingleStep(self.step_size)
        slider.setPageStep(15 * self.step_size)
        slider.setTickInterval(15 * self.step_size)
        slider.setTickPosition(QSlider.TicksBelow)

        return slider
    
    def getSlider(self):
        return self.slider()
    # different functions for changing values
    



class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.main_window = main_window
        self.setWindowTitle("Pruning Interface Test")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget() # GLWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout(self.central_widget)

        self.tree_section_widget = GLWidget() #GLWidget(self.central_widget)
        self.layout.addWidget(self.tree_section_widget, 0, 0, 2, 1)  # Row 0, Column 0, Span 2 rows and 1 column

        self.whole_tree_view = GLWidget() #GLWidget(self.central_widget)
        self.whole_tree_view.setFixedSize(200, 150)
        self.layout.addWidget(self.whole_tree_view, 0, 1, 1, 1)  # Row 0, Column 1, Span 1 row and 1 column

        # Create a QFrame for the directory and buttons column
        self.frame = QFrame(self.central_widget) # self.central_widget
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(self.frame, 1, 1, 1, 1)  # Row 1, Column 1, Span 1 row and 1 column

        # Create a QVBoxLayout for the directory and buttons column
        self.directory_layout = QVBoxLayout(self.frame)

        # Create a QLabel to display the directory
        self.directory_label = QLabel("Your Task:")
        self.directory_layout.addWidget(self.directory_label)

        # Create a QLabel to display the task description
        self.task_label = QLabel("Task description goes here")
        self.directory_layout.addWidget(self.task_label)




        # # creating a slider
        # self.slider = QSlider(Qt.Horizontal)
        # self.slider.setRange(0, 360 * 16)
        # self.slider.setSingleStep(16)
        # self.slider.setPageStep(15 * 16)
        # self.slider.setTickInterval(15 * 16)
        # self.slider.setTickPosition(QSlider.TicksBelow)

        # self.directory_layout.addWidget(self.slider)

        # Create buttons for navigation
        self.previous_button = QPushButton("Previous")
        # self.previous_button.clicked.connect(self.show_previous_image)
        self.directory_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Next")
        # self.next_button.clicked.connect(self.show_next_image)
        self.directory_layout.addWidget(self.next_button)

        # Create a Help button
        self.help_button = QPushButton("Help")
        # self.help_button.clicked.connect(self.show_help)
        self.directory_layout.addWidget(self.help_button)
       
        
    
    def create_slider(self):
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        
        self.slider.setTickInterval(10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
            
        return self.slider


    def change_value(self):
        self.scale = self.slider.value()
        self.label.setText(str(self.scale))
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.showMaximized()
    sys.exit(app.exec_())