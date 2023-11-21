import sys
sys.path.append('../')


from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QSlider, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMainWindow, QFrame, QGridLayout, QPushButton, QOpenGLWidget
from PySide2.QtCore import Qt
from PySide2.QtOpenGL import QGLWidget
from PySide2.QtGui import QOpenGLVertexArrayObject, QOpenGLBuffer, QOpenGLShaderProgram, QOpenGLShader, QOpenGLContext, QVector4D
# from PySide2.shiboken2 import VoidPtr

# from PyQt6 import QtCore      # core Qt functionality
# from PyQt6 import QtGui       # extends QtCore with GUI functionality
# from PyQt6 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU        # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo
import pywavefront
import numpy as np
import ctypes                 # to communicate with c code under the hood



class Mesh:
    def __init__(self, fname=None):
        self.fname = fname
        self.mesh = self.load_mesh(fname)
        self.vertices = [] 
        self.vertex_count = 0  

        self.get_vertices()  
           

          
        # self.faces = self.mesh.mesh_list[0].faces # Gives us the triangles that are drawn by the system
        
        self.vao = QOpenGLVertexArrayObject()
        self.context = QOpenGLContext()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = QOpenGLShaderProgram()
        # self.vao.create()
        # vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)   


        # Vertices --> telling the system to load the points to the graphics card
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_STATIC_DRAW)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 12, ctypes.c_void_p(0))  # should stride 12 bytes per vertex since [x, y, z]

        # self.vbo = QOpenGLBuffer()
        # vboBinder = QOpenGLBuffer.bind(self.vbo)

        # self.shader = QOpenGLShaderProgram() # TO ADD

        # f = QOpenGLContext.currentContext().function()
        # f.glEnableVertexAttribArray(0)
        # f.glEnableVertexAttribArray(1)
       
        
        

    def load_mesh(self, fname):
        mesh = pywavefront.Wavefront(fname, collect_faces = True)
        return mesh
    
    def get_vertices(self):
        for vertex in self.mesh.vertices:
            for v in vertex:
                self.vertices.append(v)
            self.vertex_count += 1
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
    

    def draw(self):
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertex_count)
    
    def draw_mesh(self):
        for mesh in self.mesh.mesh_list:
            for mat in mesh.materials:
                vertex_size = mat.vertex_size
                vertices = np.array(mat.vertices)
                vertices = np.reshape(vertices, (int(len(mat.vertices)/vertex_size), vertex_size))
                if len(vertices[0]) > 6:
                    gl.glEnable(gl.GL_TEXTURE_2D)
                #print(mat.vertex_format)
                #print(vertices[0])
                gl.glBegin(gl.GL_TRIANGLES)
            #visualization.draw_materials(mesh.materials)
                for v in vertices:
                    gl.glVertex3f(v[-3], v[-2], v[-1])
                    gl.glNormal3f(v[-6], v[-5], v[-4])
                    if len(v) > 6:
                        gl.glTexCoord2f(v[-8], v[-7])
                gl.glEnd()
                if len(vertices[0]) > 6:
                    gl.glDisable(gl.GL_TEXTURE_2D)


    def destroy(self):
        gl.glDeleteVertexArrays(1, (self.vao,))
        gl.glDeleteBuffers(1, (self.vbo,))


##############################################################################################################
#
#  Initial Code base taken from 
#  https://github.com/D-K-E/pyside-opengl-tutorials/blob/master/tutorials/01-triangle/TriangleTutorial.ipynb
#
##############################################################################################################

class GLWidget(QOpenGLWidget): 
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # self.mesh = Mesh('tree_files/exemplarTree.obj')
        self.background_color = QtGui.QColor(0, 59, 111) 

        # openGl data
        self.vao = QOpenGLVertexArrayObject()                   # making the vertex attribure object
        self.context = QOpenGLContext()                         # Making the context
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)    # making the vertext buffer object
        self.program = QOpenGLShaderProgram()                          # making the shaders

        self.vertices = np.array( # to replace with mesh vertices
            [-0.5, -0.5, 0.0, # x, y, z
             0.5, -0.5, 0.0,
             0.0, 0.5, 0.0
            ],
            dtype=ctypes.c_float
        )
        self.triangleColor = QVector4D(0.5, 0.5, 0.0, 0.0) # yellow


        self.shaders = {
            "vertex": """
            attribute highp vec3 aPos; 

            void main(void)
            {
                gl_Position = vec4(vertexPos, 1.0);
            }
            """,

            "fragment": """
            uniform mediump vec4 color;
            void main(void)
            {
                gl_FragColor = color;
            }
            """
            
        }

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


    def initializeGL(self):
        print('gl initial')
        print(self.getGlInfo())

        self.context.create()  # create an OpenGL context
        self.context.aboutToBeDestroyed.connect(self.cleanUpGl)


        # # initialize functions
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        funcs.glClearColor(1, 1, 1, 1)
        # funcs.glClearColor(self.background_color.redF(), self.background_color.greenF(), self.background_color.blueF(), self.background_color.alphaF())
        # gl.glClearColor(self.background_color.redF(), self.background_color.greenF(), self.background_color.blueF(), self.background_color.alphaF())
        funcs.glEnable(gl.GL_DEPTH_TEST)
        # gl.glEnable(gl.GL_DEPTH_TEST) # enables depth testing so things are rendered correctly
    
        # Initialize objects here!
        shaderName = "tree"
        vertex_shader = self.loadShader(shaderType="vertex", shaderName=shaderName, shaderPath='shaders/shader.vert')
        frag_shader = self.loadShader(shaderType="fragment", shaderName=shaderName, shaderPath='shaders/shader.frag')

        # create and load shaders
        self.program = QOpenGLShaderProgram(self.context)
        self.program.addShader(vertex_shader)
        self.program.addShader(frag_shader)
        
        self.program.bindAttributeLocation("vertexPos", 0) # vertexPos corresponds to shader.vertex for vertices


        # link the shader program
        isLinked = self.program.link()
        print("Shader program is linked: ", isLinked)

        # bind the program --> activates it!
        self.program.bind()

        # specifies the uniform value in the fragment shader
        colorLoc = self.program.uniformLocation("color")  # color defined as uniform vector in shader.frag
        self.program.setUniformValue(colorLoc, self.triangleColor)


        # create the vao and vbo
        isVao = self.vao.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)

        isVbo = self.vbo.create()
        isBound = self.vbo.bind()

        print("vao created: ", isVao)
        print("vbo created: ", isVbo)

        float_size = ctypes.sizeof(ctypes.c_float)

        # allocate buffer space
        self.vbo.allocate(self.vertices.tobytes(), 
                          float_size * self.vertices.size)
        funcs.glEnableVertexAttribArray(0)
        nullptr = ctypes.c_void_p(0) # VoidPtr(0)
        funcs.glVertexAttribPointer(0,                    # where the array starts
                                    3,                    # how long the vertex point is i.e., (x, y, z)
                                    int(gl.GL_FLOAT),     # is a float
                                    int(gl.GL_FALSE),
                                    3 * float_size,       # size in bytes
                                    nullptr)              # where the data is stored (starting position) in memory
        
        
        self.vbo.release()
        self.program.release()
        vaoBinder = None

    def loadShader(self, shaderType: str, shaderName: str, shaderPath: str):
       
        # shaderSource = self.shaders[shaderType]  # gets the source code from above

        if shaderType == "vertex":
            shader = QOpenGLShader(QOpenGLShader.Vertex)
        else:
            shader = QOpenGLShader(QOpenGLShader.Fragment)

        isCompiled = shader.compileSourceFile(shaderPath)

        if isCompiled is False:
            print(shader.log())
            raise ValueError(
                "{0} shader {2} known as {1} is not compiled".format(shaderType, shaderName, shaderPath)
            )

        return shader

    def resizeGL(self, width: int, height: int):
        funcs = self.context.functions()
        funcs.glViewport(0, 0, width, height)
        # gl.glViewport(0, 0, width, height)

        # # funcs.glMatrixMode(gl.GL_PROJECTION) # used to define the vieweing volume contianing the projection transformation
        # gl.glMatrixMode(gl.GL_PROJECTION) 
        
        # # funcs.glLoadIdentity()
        # gl.glLoadIdentity()
        # aspect = width / float(height)

        
        # GLU.gluPerspective(45.0, aspect, 1.0, 100.0) # defines the viewing frustrum
        
        # # funcs.glMatrixMode(gl.GL_MODELVIEW)
        # gl.glMatrixMode(gl.GL_MODELVIEW)

    
    def cleanUpGl(self):
        self.context.makeCurrent(self)     # make context to release the current one
        self.vbo.destroy()             # destroy the buffer
        del self.program                    # delete the shader program
        self.program = None                 # change pointed reference
        self.doneCurrent()                  # no current context for current thread

    def paintGL(self):
        funcs = self.context.functions()

        # clean up what was drawn in the previous frame
        funcs.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # drawing code
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()
        funcs.glDrawArrays(gl.GL_TRIANGLES,
                           0,
                           3)

        self.program.release()
        vaoBinder = None


    # def paintGL(self):
    #     # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,)
    #     gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT) # clears the GL window of Color and depth before painting
      
    #     gl.glBindVertexArray(self.mesh.vao)
    #     # vaoBinder = QOpenGLVertexArrayObject.Binder(self.mesh.vao)
    #     self.mesh.draw()

    #     # vaoBinder = None

    #     # # RENDERING CODE FOR OUR MESH GOES HERE
    #     # gl.glPushMatrix()
    #     # # self.mesh.set_translate(0.0, 0.0, -15.0)

    #     # #self.read_texture()

    #     # gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    #     # # gl.glEnableClientState(gl.GL_COLOR_ARRAY) 

    #     # gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.mesh.vbo)
        
    #     # # # draws the object with lines by each vertex point
    #     # self.mesh.draw_mesh()

    #     # gl.glBindVertexArray(self.mesh.vao)
    #     # # # want to draw the elements on the array as triangles
    #     # gl.glDrawElements(gl.GL_TRIANGLES, len(self.mesh.faces), gl.GL_UNSIGNED_INT, 0) # 0 used to be self.mesh.faces

    #     # gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
    #     # # gl.glDisableClientState(gl.GL_COLOR_ARRAY)

    #     # gl.glPopMatrix() # restore previous model view

    #     # gl.glLoadIdentity()
    #     # gl.glBindVertexArray(0)
    #     # # gl.glRotated(self.up_down, 1.0, 0.0, 0.0)
    #     # # gl.glRotated(self.turntable, 0.0, 1.0, 0.0)
    #     # # gl.glRotated(self.zRot, 0.0, 0.0, 1.0)

    



class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.main_window = main_window
        self.setWindowTitle("Pruning Interface Test")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget() # GLWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout(self.central_widget)

        self.tree_section_widget = GLWidget(self.central_widget)
        self.layout.addWidget(self.tree_section_widget, 0, 0, 2, 1)  # Row 0, Column 0, Span 2 rows and 1 column

        self.whole_tree_view = GLWidget(self.central_widget) # self.central_widget
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
        self.task_label = QLabel()
        self.directory_layout.addWidget(self.task_label)

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