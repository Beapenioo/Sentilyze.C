import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import sqlite3

class SignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(400, 600)
        self.setStyleSheet("background-color: #232323;")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        logo = QLabel()
        logo_pixmap = QPixmap("logo.png")
        logo.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Sign Up")
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
        self.name_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 16px; border-radius: 4px; padding: 8px;")
        layout.addWidget(self.name_input)

        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Surname")
        self.surname_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 16px; border-radius: 4px; padding: 8px;")
        layout.addWidget(self.surname_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 16px; border-radius: 4px; padding: 8px;")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 16px; border-radius: 4px; padding: 8px;")
        layout.addWidget(self.password_input)

        signup_button = QPushButton("SIGN UP")
        signup_button.setFixedHeight(45)
        signup_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 20px; border-radius: 4px;")
        signup_button.clicked.connect(self.handle_signup)
        layout.addWidget(signup_button)

        back_button = QPushButton("BACK")
        back_button.setFixedHeight(45)
        back_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 20px; border-radius: 4px;")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def handle_signup(self):
        name = self.name_input.text()
        surname = self.surname_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if not all([name, surname, email, password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            # Drop existing table if it exists
            cursor.execute('DROP TABLE IF EXISTS users')
            
            # Create new table with all fields
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            
            # Check if email already exists
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "Email already exists")
                return

            cursor.execute('INSERT INTO users (name, surname, email, password) VALUES (?, ?, ?, ?)',
                         (name, surname, email, password))
            conn.commit()
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.go_back()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Database error: {str(e)}")
        finally:
            conn.close()

    def go_back(self):
        self.parent().setCentralWidget(FirstPage())

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(400, 600)
        self.setStyleSheet("background-color: #232323;")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        logo = QLabel()
        logo_pixmap = QPixmap("logo.png")
        logo.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Login")
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 16px; border-radius: 4px; padding: 8px;")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 16px; border-radius: 4px; padding: 8px;")
        layout.addWidget(self.password_input)

        login_button = QPushButton("LOGIN")
        login_button.setFixedHeight(45)
        login_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 20px; border-radius: 4px;")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        back_button = QPushButton("BACK")
        back_button.setFixedHeight(45)
        back_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 20px; border-radius: 4px;")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not all([email, password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                         (email, password))
            if cursor.fetchone():
                QMessageBox.information(self, "Success", "Login successful!")
                # TODO: Open main application window
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Database error: {str(e)}")
        finally:
            conn.close()

    def go_back(self):
        self.parent().setCentralWidget(FirstPage())

class FirstPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(400, 600)
        self.setStyleSheet("background-color: #232323;")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        logo = QLabel()
        logo_pixmap = QPixmap("logo.png")
        logo.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Sentilyze")
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff;")
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
        login_button.clicked.connect(self.open_login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def open_signup(self):
        self.parent().setCentralWidget(SignUp())

    def open_login(self):
        self.parent().setCentralWidget(Login())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(400, 600)
        self.setCentralWidget(FirstPage())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 