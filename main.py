import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class SignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setStyleSheet("background-color: #232323;")
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

        form_layout = QVBoxLayout()
        for label_text in ["Name", "Surname", "Email", "Password"]:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFont(QFont("Century Gothic", 14))
            label.setStyleSheet("color: #fff;")
            label.setFixedWidth(80)
            input_field = QLineEdit()
            input_field.setFixedHeight(32)
            input_field.setStyleSheet("background-color: #e0e0e0; color: #232323; font-size: 16px; border-radius: 2px;")
            if label_text == "Password":
                input_field.setEchoMode(QLineEdit.Password)
            row.addWidget(label)
            row.addWidget(input_field)
            form_layout.addLayout(row)
        layout.addLayout(form_layout)

        signup_button = QPushButton("Sign Up")
        signup_button.setFixedHeight(40)
        signup_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 18px; border-radius: 20px; width: 180px;")
        layout.addSpacing(20)
        layout.addWidget(signup_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setStyleSheet("background-color: #232323;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        logo_pixmap = QPixmap("logo.png")
        logo.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Welcome to Sentilyze")
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff; margin-bottom: 40px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.setLayout(layout)

class FirstPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setStyleSheet("background-color: #232323;")
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
        signup_button.clicked.connect(self.open_signup)
        layout.addWidget(signup_button)

        login_button = QPushButton("LOGIN")
        login_button.setFixedHeight(45)
        login_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 20px; border-radius: 4px;")
        login_button.clicked.connect(self.open_homepage)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def open_signup(self):
        self.signup_window = SignUp()
        self.signup_window.showFullScreen()
        self.close()

    def open_homepage(self):
        self.homepage_window = HomePage()
        self.homepage_window.showFullScreen()
        self.close()

def main():
    app = QApplication(sys.argv)
    window = FirstPage()
    window.showFullScreen()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 