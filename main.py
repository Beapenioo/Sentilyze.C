import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from sqlalchemy import create_engine, Column, Integer, String, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

def init_db():
    try:
        DATABASE_URL = "mysql+pymysql://root:@localhost:3306/sentilyze"
        engine = create_engine(DATABASE_URL, echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"Database initialization error: {e}")
        return None

class SignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: #2A2A2A;")
        
        self.session = init_db()
        if not self.session:
            QMessageBox.critical(self, "Error", "Failed to initialize database")
            return
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        logo = QLabel()
        logo_pixmap = QPixmap("icons\logo.png")
        logo.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo, alignment=Qt.AlignCenter)

        title = QLabel("Sign Up")
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title, alignment=Qt.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
        self.name_input.setAlignment(Qt.AlignCenter)
        self.name_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 24px; border-radius: 4px; padding: 12px;")
        self.name_input.setFixedWidth(400)
        main_layout.addWidget(self.name_input, alignment=Qt.AlignCenter)

        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Surname")
        self.surname_input.setAlignment(Qt.AlignCenter)
        self.surname_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 24px; border-radius: 4px; padding: 12px;")
        self.surname_input.setFixedWidth(400)
        main_layout.addWidget(self.surname_input, alignment=Qt.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setAlignment(Qt.AlignCenter)
        self.email_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 24px; border-radius: 4px; padding: 12px;")
        self.email_input.setFixedWidth(400)
        main_layout.addWidget(self.email_input, alignment=Qt.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setAlignment(Qt.AlignCenter)
        self.password_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 24px; border-radius: 4px; padding: 12px;")
        self.password_input.setFixedWidth(400)
        main_layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        signup_button = QPushButton("SIGN UP")
        signup_button.setFixedSize(300, 60)
        signup_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 24px; border-radius: 4px;")
        signup_button.clicked.connect(self.handle_signup)
        main_layout.addWidget(signup_button, alignment=Qt.AlignCenter)

        back_button = QPushButton("BACK")
        back_button.setFixedSize(300, 60)
        back_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 24px; border-radius: 4px;")
        back_button.clicked.connect(self.go_back)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def handle_signup(self):
        if not self.session:
            QMessageBox.critical(self, "Error", "No database connection")
            return

        name = self.name_input.text()
        surname = self.surname_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if not all([name, surname, email, password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        try:
            self.session.begin()
            
            existing_user = self.session.query(User).filter_by(email=email).first()
            if existing_user:
                QMessageBox.warning(self, "Error", "Email already exists")
                return

            new_user = User(
                name=name,
                surname=surname,
                email=email,
                password=password
            )
            self.session.add(new_user)
            self.session.commit()

            user = self.session.query(User).filter_by(email=email).first()
            if user:
                print(f"User created successfully: {user.name} {user.surname}")
                QMessageBox.information(self, "Success", "Account created successfully!")
                self.go_back()
            else:
                print("Failed to create user")
                QMessageBox.warning(self, "Error", "Failed to create account")
                
        except Exception as e:
            print(f"Error during signup: {e}")
            self.session.rollback()
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def go_back(self):
        self.parent().setCentralWidget(FirstPage())

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: #2A2A2A;")
        
        self.session = init_db()
        if not self.session:
            QMessageBox.critical(self, "Error", "Failed to initialize database")
            return
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        logo = QLabel()
        logo_pixmap = QPixmap("icons\logo.png")
        logo.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo, alignment=Qt.AlignCenter)

        title = QLabel("Login")
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title, alignment=Qt.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setAlignment(Qt.AlignCenter)
        self.email_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 24px; border-radius: 4px; padding: 12px;")
        self.email_input.setFixedWidth(400)
        main_layout.addWidget(self.email_input, alignment=Qt.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setAlignment(Qt.AlignCenter)
        self.password_input.setStyleSheet("background-color: #fff; color: #232323; font-size: 24px; border-radius: 4px; padding: 12px;")
        self.password_input.setFixedWidth(400)
        main_layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        login_button = QPushButton("LOGIN")
        login_button.setFixedSize(300, 60)
        login_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 24px; border-radius: 4px;")
        login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(login_button, alignment=Qt.AlignCenter)

        back_button = QPushButton("BACK")
        back_button.setFixedSize(300, 60)
        back_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 24px; border-radius: 4px;")
        back_button.clicked.connect(self.go_back)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def handle_login(self):
        if not self.session:
            QMessageBox.critical(self, "Error", "No database connection")
            return

        email = self.email_input.text()
        password = self.password_input.text()

        if not all([email, password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        try:
            user = self.session.query(User).filter_by(email=email, password=password).first()
            if user:
                print(f"User logged in successfully: {user.name} {user.surname}")
                QMessageBox.information(self, "Success", "Login successful!")
                self.parent().setCentralWidget(HomePage())
            else:
                print(f"Login failed for email: {email}")
                QMessageBox.warning(self, "Error", "Invalid email or password")
        except Exception as e:
            print(f"Error during login: {e}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def go_back(self):
        self.parent().setCentralWidget(FirstPage())

class FirstPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: #2A2A2A;")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        logo_pixmap = QPixmap("icons\logo.png")
        logo.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo, alignment=Qt.AlignCenter)

        main_layout.addSpacing(10)

        title = QLabel("Sentilyze")
        title.setFont(QFont("Century Gothic", 40))
        title.setStyleSheet("color: #fff;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title, alignment=Qt.AlignCenter)

        main_layout.addSpacing(40)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(30)
        button_layout.setAlignment(Qt.AlignCenter)

        signup_button = QPushButton("SIGN UP")
        signup_button.setFixedSize(300, 60)
        signup_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 24px; border-radius: 4px;")
        signup_button.clicked.connect(self.open_signup)
        button_layout.addWidget(signup_button, alignment=Qt.AlignCenter)

        login_button = QPushButton("LOGIN")
        login_button.setFixedSize(300, 60)
        login_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 24px; border-radius: 4px;")
        login_button.clicked.connect(self.open_login)
        button_layout.addWidget(login_button, alignment=Qt.AlignCenter)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def open_signup(self):
        self.parent().setCentralWidget(SignUp())

    def open_login(self):
        self.parent().setCentralWidget(Login())

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze - Home")
        self.setStyleSheet("background-color: #2A2A2A;")

        # Ana yatay layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # --- SOL PANEL ---
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignTop)
        left_panel.setSpacing(20)

        logo = QLabel()
        logo_pixmap = QPixmap("icons/logo.png")
        logo.setPixmap(logo_pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignLeft)
        left_panel.addWidget(logo, alignment=Qt.AlignLeft)

        sentilyze_label = QLabel("Sentilyze")
        sentilyze_label.setFont(QFont("Century Gothic", 24))
        sentilyze_label.setStyleSheet("color: #fff;")
        sentilyze_label.setAlignment(Qt.AlignLeft)
        left_panel.addWidget(sentilyze_label, alignment=Qt.AlignLeft)

        left_panel.addSpacing(30)

        history_title = QLabel("History  <span style='font-size:16px;'>&#9432;</span>")
        history_title.setFont(QFont("Century Gothic", 16))
        history_title.setStyleSheet("color: #fff;")
        history_title.setAlignment(Qt.AlignLeft)
        left_panel.addWidget(history_title, alignment=Qt.AlignLeft)

        # Placeholder for history list
        self.history_list = QVBoxLayout()
        history_item = QPushButton("Lorem ipsum ...")
        history_item.setStyleSheet("background-color: #444; color: #fff; border:none; text-align:left; padding:8px; font-size:16px;")
        history_item.setFixedWidth(180)
        self.history_list.addWidget(history_item)
        left_panel.addLayout(self.history_list)
        left_panel.addStretch(1)

        # --- ORTA PANEL ---
        center_panel = QVBoxLayout()
        center_panel.setAlignment(Qt.AlignBottom)
        center_panel.setSpacing(20)

        # Sohbet kutusu (üstte)
        self.chat_box = QVBoxLayout()
        self.chat_box.setAlignment(Qt.AlignTop)
        # Placeholder mesaj
        user_msg = QLabel("<b>U</b> Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.")
        user_msg.setWordWrap(True)
        user_msg.setStyleSheet("color: #fff; font-size: 20px; background: transparent;")
        self.chat_box.addWidget(user_msg)
        center_panel.addLayout(self.chat_box)
        center_panel.addSpacing(30)

        # Analiz kutusu (placeholder)
        analyze_logo = QLabel()
        analyze_logo.setPixmap(logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        analyze_logo.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(analyze_logo, alignment=Qt.AlignCenter)

        analyzing_label = QLabel("Text is analyzing...")
        analyzing_label.setStyleSheet("color: #fff; font-size: 20px;")
        analyzing_label.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(analyzing_label, alignment=Qt.AlignCenter)

        # Emoji ve analiz sonucu (placeholder)
        emoji_row = QHBoxLayout()
        for color in ["#E74C3C", "#F1C40F", "#27AE60"]:
            emoji = QLabel()
            emoji.setFixedSize(40, 40)
            emoji.setStyleSheet(f"background: {color}; border-radius: 20px;")
            emoji_row.addWidget(emoji)
        center_panel.addLayout(emoji_row)

        result_label = QLabel("The text has an overall neutral sentiment with a slight positive leaning.")
        result_label.setStyleSheet("color: #fff; font-size: 18px;")
        result_label.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(result_label, alignment=Qt.AlignCenter)
        center_panel.addStretch(1)

        # En altta metin kutusu ve Analyze butonu
        input_row = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter the text to be analyzed.")
        self.text_input.setStyleSheet("background-color: #444; color: #fff; font-size: 18px; border-radius: 4px; padding: 12px;")
        input_row.addWidget(self.text_input)
        analyze_btn = QPushButton("Analyze")
        analyze_btn.setFixedSize(120, 48)
        analyze_btn.setStyleSheet("background-color: #757575; color: #fff; font-size: 18px; border-radius: 4px;")
        analyze_btn.clicked.connect(self.send_message)
        input_row.addWidget(analyze_btn)
        center_panel.addLayout(input_row)

        # --- SAĞ PANEL ---
        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignTop)
        right_panel.setSpacing(20)

        # Profil butonu
        self.profile_btn = QPushButton("U")
        self.profile_btn.setFixedSize(48, 48)
        self.profile_btn.setStyleSheet("background-color: #444; color: #fff; font-size: 24px; border-radius: 24px;")
        self.profile_btn.clicked.connect(self.show_profile_menu)
        right_panel.addWidget(self.profile_btn, alignment=Qt.AlignRight)

        # Profil menüsü (gizli başta)
        self.profile_menu = QWidget()
        self.profile_menu.setStyleSheet("background-color: #333; border-radius: 8px;")
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)
        for text in ["Profile", "Settings", "Log Out"]:
            btn = QPushButton(text)
            btn.setStyleSheet("background: none; color: #fff; font-size: 16px; padding: 8px 16px; text-align:left;")
            btn.setCursor(Qt.PointingHandCursor)
            menu_layout.addWidget(btn)
        self.profile_menu.setLayout(menu_layout)
        self.profile_menu.hide()
        right_panel.addWidget(self.profile_menu, alignment=Qt.AlignRight)

        right_panel.addStretch(1)

        # AI Bot logosu (tıklanabilir)
        self.ai_bot_btn = QPushButton()
        ai_pixmap = QPixmap("icons/logo.png")
        self.ai_bot_btn.setIcon(QIcon(ai_pixmap))
        self.ai_bot_btn.setIconSize(ai_pixmap.size())
        self.ai_bot_btn.setFixedSize(64, 64)
        self.ai_bot_btn.setStyleSheet("background: none; border: none;")
        self.ai_bot_btn.setCursor(Qt.PointingHandCursor)
        right_panel.addWidget(self.ai_bot_btn, alignment=Qt.AlignRight)

        # Layoutları ana layouta ekle
        main_layout.addLayout(left_panel, 2)
        main_layout.addSpacing(20)
        main_layout.addLayout(center_panel, 6)
        main_layout.addSpacing(20)
        main_layout.addLayout(right_panel, 2)

        self.setLayout(main_layout)

    def send_message(self):
        text = self.text_input.text().strip()
        if text:
            msg = QLabel(f"<b>U</b> {text}")
            msg.setWordWrap(True)
            msg.setStyleSheet("color: #fff; font-size: 20px; background: transparent;")
            self.chat_box.addWidget(msg)
            self.text_input.clear()

    def show_profile_menu(self):
        if self.profile_menu.isVisible():
            self.profile_menu.hide()
        else:
            self.profile_menu.show()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(1600,900)
        self.setWindowIcon(QIcon("icons/logo.png"))
        self.setStyleSheet("background-color: #2A2A2A;")
        self.setCentralWidget(FirstPage())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()