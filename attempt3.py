#Lily Oliphant 
#test interface #3

import sys
from PIL import Image
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QRect

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apple Pruning Tutorial")
        self.setGeometry(100, 100, 800, 600)
        
        # Create a main widget and set it as the central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a horizontal layout for the main widget
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create a QVBoxLayout for the image column
        self.image_layout = QVBoxLayout()
        self.layout.addLayout(self.image_layout)

        # Create a QLabel to display the tutorial images
        self.image_label = QLabel()
        self.image_layout.addWidget(self.image_label)

        # Create a QVBoxLayout for the directory and buttons column
        self.directory_layout = QVBoxLayout()
        self.layout.addLayout(self.directory_layout)

        # Create a small view QLabel for the image
        self.small_view_label = QLabel()
        self.small_view_label.setFixedSize(200, 150)
        self.directory_layout.addWidget(self.small_view_label)

        # Create a QLabel to display the directory
        self.directory_label = QLabel("Current Directory:")
        self.directory_layout.addWidget(self.directory_label)

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

        # Define a list of tutorial images
        try: 
            img_1  = Image.open("branch10.jpg") 
        except IOError:
            pass
         # Define a list of tutorial images
        try: 
            img_2  = Image.open("branch10.jpg") 
        except IOError:
            pass
         # Define a list of tutorial images
        try: 
            img_3  = Image.open("branch10.jpg") 
        except IOError:
            pass

        self.images = [r"C:\Users\lilyo\.vscode\robotics\img_1.jpg"]  # Replace with actual image paths
        
        # Initialize the current image index
        self.current_image_index = 0
        
        # Show the first image

        self.show_current_image()

    def show_current_image(self):
        # Get the path of the current image
        image_path = self.images[self.current_image_index]
        
        # Load and display the image in the main view
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        # Load and display the image in the small view
        small_pixmap = pixmap.scaled(self.small_view_label.width(), self.small_view_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.small_view_label.setPixmap(small_pixmap)
        self.small_view_label.setScaledContents(True)

    def show_previous_image(self):
        # Decrease the current image index
        self.current_image_index -= 1
        
        # Wrap around to the last image if necessary
        if self.current_image_index < 0:
            self.current_image_index = len(self.images) - 1
        
        # Show the updated image
        self.show_current_image()

    def show_next_image(self):
        # Increase the current image index
        self.current_image_index += 1
        
        # Wrap around to the first image if necessary
        if self.current_image_index >= len(self.images):
            self.current_image_index = 0
        
        # Show the updated image
        self.show_current_image()

    def show_help(self):
        # Implement the functionality for the Help button
        # Display a help dialog or perform any other actions as needed
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())