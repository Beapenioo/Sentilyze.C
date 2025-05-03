import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class FirstPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setStyleSheet("background-color: #232323;")
        self.setFixedSize(600, 500)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        logo_pixmap = QPixmap("logo.png")
        logo.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Sentilyze")
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff; margin-bottom: 40px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        signup_button = QPushButton("SIGN UP")
        signup_button.setFixedHeight(45)
        signup_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 20px; border-radius: 4px;")
        layout.addWidget(signup_button)

        login_button = QPushButton("LOGIN")
        login_button.setFixedHeight(45)
        login_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 20px; border-radius: 4px;")
        layout.addWidget(login_button)

        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    window = FirstPage()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 