import sys
sys.path.append('../')

from PyQt6 import QtCore      # core Qt functionality
from PyQt6 import QtGui       # extends QtCore with GUI functionality
from PyQt6 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU        # OpenGL Utility Library, extends OpenGL functionality

# Class for loading the .ply file as a new Widget using OpenGL as a wrapper
# from this tutorial: https://nrotella.github.io/journal/first-steps-python-qt-opengl.html
class GLWidget(QtOpenGL.QGLWidget): # 
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGlWidget.__init__(self, parent)

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0, 0, 255))
        gl.glEnable(gl.GL_DEPTH_TEST) # enables depth testing so things are rendered correctly

    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION) # used to define the vieweing volume contianing the projection transformation
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0) # defines the viewing frustrum
        gl.glMatrixMode(gl.GL_MODELVIEW)
    
    # where the rendering happens
    # currently telling OpenGL which buffers to clear
    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


