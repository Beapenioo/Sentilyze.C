from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from database.db_operations import DatabaseOperations
import sqlite3

class SignupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 600)
        self.db = DatabaseOperations()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: #F5F5F5;
                min-height: 30px;
                max-width: 300px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                border: none;
                border-radius: 5px;
                min-height: 30px;
                max-width: 300px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)

        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("assets/logo.png")
            if not logo_pixmap.isNull():
                logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio))
        except:
            pass  # If logo loading fails, we'll just skip it
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        title_label = QLabel("Create Account")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input, 0, Qt.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input, 0, Qt.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input, 0, Qt.AlignCenter)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_input, 0, Qt.AlignCenter)

        signup_button = QPushButton("Sign Up")
        signup_button.clicked.connect(self.handle_signup)
        layout.addWidget(signup_button, 0, Qt.AlignCenter)

        back_button = QPushButton("Back to Login")
        back_button.setStyleSheet("background-color: #6c757d;")
        back_button.clicked.connect(self.go_to_login)
        layout.addWidget(back_button, 0, Qt.AlignCenter)

        self.setLayout(layout)

    def handle_signup(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not all([username, email, password, confirm_password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM users 
                    WHERE username = ? OR email = ?
                ''', (username, email))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Error", "Username or email already exists")
                    return

                cursor.execute('''
                    INSERT INTO users (username, email, password)
                    VALUES (?, ?, ?)
                ''', (username, email, password))
                conn.commit()

            QMessageBox.information(self, "Success", "Account created successfully!")
            self.go_to_login()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Database error: {str(e)}")

    def go_to_login(self):
        from .login_page import LoginPage
        self.login_page = LoginPage()
        self.parent().setCentralWidget(self.login_page) 