import sys
sys.path.append('../')


from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QSlider, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMainWindow, QFrame, QGridLayout, QPushButton
from PySide2.QtCore import Qt
from PySide2.QtOpenGL import QGLWidget

# from PyQt6 import QtCore      # core Qt functionality
# from PyQt6 import QtGui       # extends QtCore with GUI functionality
# from PyQt6 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU        # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo
import pywavefront
import numpy as np



class Mesh:
    def __init__(self, fname=None):
        self.fname = fname
        self.mesh = self.load_object(fname)
        
        self.vertices = self.get_vertices(self.mesh)
        self.get_vbo(self.mesh)
        

    def load_object(self, fname):
        mesh = pywavefront.Wavefront(fname, collect_faces = True)
        return mesh
    
    def get_vertices(self, mobject):
        vertices = np.array(mobject.vertices, dtype=np.float32)
        return vertices
    
    def get_vbo(self, mobject):
        vertices = self.get_vertices(mobject)
        self.vbo = vbo.VBO(np.reshape(vertices, (1, -1)).astype(np.float32))
        self.vbo.bind()
    
    
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


class GLWidget(QGLWidget): 
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.mesh = Mesh('tree_files/exemplarTree.obj')
        self.background_color = QtGui.QColor(0, 59, 111) 


    def initializeGL(self):
        gl.glClearColor(self.background_color.redF(), self.background_color.greenF(), self.background_color.blueF(), self.background_color.alphaF())
        gl.glEnable(gl.GL_DEPTH_TEST) # enables depth testing so things are rendered correctly

        # initialize objects in here!



    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION) # used to define the vieweing volume contianing the projection transformation
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0) # defines the viewing frustrum
        gl.glMatrixMode(gl.GL_MODELVIEW)


    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        gl.glPushMatrix()
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.mesh.vbo)

        self.mesh.draw_mesh()

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

        gl.glPopMatrix()
        gl.glLoadIdentity()

        



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