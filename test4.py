#Lily Oliphant Interface


import sys
sys.path.append('../')

# testing for QtWidgets
# from openalea.vpltk.qt import QtWidgets
import random
# from openalea.oalab.project.projectwidget import ProjectManagerWidget
# from openalea.core.project.manager import ProjectManager
# from openalea.oalab.session.session import Session
# from openalea.core.path import tempdir
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PIL import Image
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFrame, QGridLayout
from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, QRect
# from openalea.lpy import *
# from openalea.plantgl.all import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.instance = QtWidgets.QApplication.instance()
        # if self.instance is None:
        #     self.app = QtWidgets.QApplication([])
        # else:
        #     self.app = self.instance

        self.setWindowTitle("Apple Pruning Tutorial")
        self.setGeometry(100, 100, 800, 600)

        # Create a main widget and set it as the central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a QGridLayout for the central widget
        self.layout = QGridLayout(self.central_widget)

        # Create a QLabel to display the tutorial images
        self.image_label = QLabel(self.central_widget)
        self.layout.addWidget(self.image_label, 0, 0, 2, 1)  # Row 0, Column 0, Span 2 rows and 1 column

        # Create a small view QLabel for the image
        self.small_view_label = QLabel(self.central_widget)
        self.small_view_label.setFixedSize(200, 150)
        self.layout.addWidget(self.small_view_label, 0, 1, 1, 1)  # Row 0, Column 1, Span 1 row and 1 column

        # Create a QFrame for the directory and buttons column
        self.frame = QFrame(self.central_widget)
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
        self.previous_button.clicked.connect(self.show_previous_image)
        self.directory_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_image)
        self.directory_layout.addWidget(self.next_button)

        # Create a Help button
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.show_help)
        self.directory_layout.addWidget(self.help_button)

        # Define a list of tutorial images and corresponding task descriptions
        self.images = ["image1.jpg", "image2.jpg", "image3.jpg", "image4.jpg", "image5.jpg"]  # Replace with actual image paths
        self.images = [r"C:\Users\lilyo\.vscode\robotics\img_1.jpg", r"C:\Users\lilyo\.vscode\robotics\img_2.jpg", r"C:\Users\lilyo\.vscode\robotics\img_3.jpg"]
        self.lpy_files = [r"examples/Envy_tie_prune_label.lpy", r"examples/UFO_tie_prune_label.lpy"]
        self.tasks = [
            "Remove vigorous wood.",
            "Prune crossing branches.",
            "Thin out overcrowded areas.",
            "Remove dead or diseased wood.",
            "Prune to encourage desired shape."
        ]

        #This does limit the images to five with each statement but this can be edited, just keep in mind when adding LPy

        # Initialize the current image index
        self.current_image_index = 0

        # Show the first image, task, and small view image
        #self.show_current_lpy_file()
        self.show_current_image()

    def show_current_image(self):
        # Get the path of the current image
        image_path = self.images[self.current_image_index]

        # Load and display the image
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        # Set the current task description
        self.task_label.setText(self.tasks[self.current_image_index])

        # Load and display the image in the small view
        small_pixmap = pixmap.scaled(self.small_view_label.width(), self.small_view_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.small_view_label.setPixmap(small_pixmap)
        self.small_view_label.setScaledContents(True) # camera angle modifications might be done here

    
    # def show_current_lpy_file(self):
    #     # Get the path of the current image
    #     lpy_file = self.lpy_files[self.current_image_index]

    #     lsystem = Lsystem(lpy_file) # gets the lstring from the lpy file 
    #     for lstring in lsystem:
    #         t = PglTurtle()
    #         lsystem.turtle_interpretation(lstring, t)
    #         scene = t.getScene()
    #         #lsystem.plot(lstring)
            
    #     # Load and display the image
    #     pixmap = QPixmap(image_path)
    #     self.image_label.setPixmap(pixmap)
    #     self.image_label.setScaledContents(True)

    #     # Set the current task description
    #     self.task_label.setText(self.tasks[self.current_image_index])

    #     # Load and display the image in the small view
    #     small_pixmap = pixmap.scaled(self.small_view_label.width(), self.small_view_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
    #     self.small_view_label.setPixmap(small_pixmap)
    #     self.small_view_label.setScaledContents(True)

    
    
    def show_previous_image(self):
        # Decrease the current image index
        self.current_image_index -= 1

        # Wrap around to the last image if necessary
        if self.current_image_index < 0:
            self.current_image_index = len(self.images) - 1

        # Show the updated image, task, and small view image
        self.show_current_image()

    def show_next_image(self):
        # Increase the current image index
        self.current_image_index += 1

        # Wrap around to the first image if necessary
        if self.current_image_index >= len(self.images):
            self.current_image_index = 0

        # Show the updated image, task, and small view image
        self.show_current_image()

    def show_help(self):
        # Implement the functionality for the Help button
        # Display a help dialog or perform any other actions as needed
        pass

    def get_app(self):
        return self.app

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app = QtWidgets.QApplication(sys.argv)

    # instance = QtWidgets.QApplication.instance()
    # if instance is None:
    #     app = QtWidgets.QApplication([])
    # else:
    #     app = instance

    window = MainWindow()
    window.show()
    #app = window.get_app()
    sys.exit(app.exec())
