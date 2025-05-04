import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from sqlalchemy import create_engine, Column, Integer, String, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import requests

TRANSLATIONS = {
    'en': {
        'SETTINGS': 'SETTINGS',
        'Theme Selection': 'Theme Selection',
        'Dark': 'Dark',
        'Light': 'Light',
        'Language': 'Language',
        'Turkish': 'Turkish',
        'English': 'English',
        'Delete History': 'Delete History',
        'Delete Feedback': 'Delete Feedback',
        'Back': 'Back',
        'PROFILE': 'PROFILE',
        'Name': 'Name',
        'Surname': 'Surname',
        'Email': 'Email',
        'Delete Account': 'Delete Account',
        'Log out': 'Log out',
        'Home': 'Home',
        'Sentilyze': 'Sentilyze',
        'SIGN UP': 'SIGN UP',
        'LOGIN': 'LOGIN',
        'Enter the text to be analyzed.': 'Enter the text to be analyzed.',
        'Profile': 'Profile',
        'Settings': 'Settings',
        'Analyze': 'Analyze',
        'History': 'History',
    },
    'tr': {
        'SETTINGS': 'AYARLAR',
        'Theme Selection': 'Tema Seçimi',
        'Dark': 'Koyu',
        'Light': 'Açık',
        'Language': 'Dil',
        'Turkish': 'Türkçe',
        'English': 'İngilizce',
        'Delete History': 'Geçmişi Sil',
        'Delete Feedback': 'Geri Bildirimi Sil',
        'Back': 'Geri',
        'PROFILE': 'PROFİL',
        'Name': 'Ad',
        'Surname': 'Soyad',
        'Email': 'E-posta',
        'Delete Account': 'Hesabı Sil',
        'Log out': 'Çıkış Yap',
        'Home': 'Ana Sayfa',
        'Sentilyze': 'Sentilyze',
        'SIGN UP': 'KAYIT OL',
        'LOGIN': 'GİRİŞ',
        'Enter the text to be analyzed.': 'Analiz edilecek metni girin.',
        'Profile': 'Profil',
        'Settings': 'Ayarlar',
        'Analyze': 'Analiz Et',
        'History': 'Geçmiş',
    }
}
def tr(text, lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(text, text)

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
        self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))

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
                self.parent().setCentralWidget(HomePage(user.name, user.surname, user.email, self.session, self.window()))
            else:
                print(f"Login failed for email: {email}")
                QMessageBox.warning(self, "Error", "Invalid email or password")
        except Exception as e:
            print(f"Error during login: {e}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def go_back(self):
        self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))

class FirstPage(QWidget):
    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
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
        self.title = QLabel("Sentilyze")
        self.title.setFont(QFont("Century Gothic", 40))
        self.title.setStyleSheet("color: #fff;")
        self.title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title, alignment=Qt.AlignCenter)
        main_layout.addSpacing(40)
        button_layout = QVBoxLayout()
        button_layout.setSpacing(30)
        button_layout.setAlignment(Qt.AlignCenter)
        self.signup_button = QPushButton("SIGN UP")
        self.signup_button.setFixedSize(300, 60)
        self.signup_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 24px; border-radius: 4px;")
        self.signup_button.clicked.connect(self.open_signup)
        button_layout.addWidget(self.signup_button, alignment=Qt.AlignCenter)
        self.login_button = QPushButton("LOGIN")
        self.login_button.setFixedSize(300, 60)
        self.login_button.setStyleSheet("background-color: #757575; color: #fff; font-size: 24px; border-radius: 4px;")
        self.login_button.clicked.connect(self.open_login)
        button_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    def open_signup(self):
        self.parent().setCentralWidget(SignUp())
    def open_login(self):
        self.parent().setCentralWidget(Login())
    def update_language(self, lang):
        self.title.setText(tr('Sentilyze', lang) if 'Sentilyze' in TRANSLATIONS['en'] else "Sentilyze")
        self.signup_button.setText(tr('SIGN UP', lang) if 'SIGN UP' in TRANSLATIONS['en'] else "SIGN UP")
        self.login_button.setText(tr('LOGIN', lang) if 'LOGIN' in TRANSLATIONS['en'] else "LOGIN")

class ProfilePage(QWidget):
    def __init__(self, user_name, user_surname, user_email, session, language='en'):
        super().__init__()
        self.user_name = user_name
        self.user_surname = user_surname
        self.user_email = user_email
        self.session = session
        self.language = language
        self.setStyleSheet("background-color: #2A2A2A;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        title = QLabel(tr('PROFILE', self.language))
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        first_letter = self.user_name[0].upper() if self.user_name else "U"
        avatar = QLabel(first_letter)
        avatar.setFixedSize(90, 90)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("background-color: #888; color: #222; font-size: 40px; border-radius: 45px;")
        layout.addWidget(avatar, alignment=Qt.AlignHCenter)
        layout.addSpacing(20)
        info = QLabel(f"{tr('Name', self.language)} : {self.user_name}\n{tr('Surname', self.language)}: {self.user_surname}\n{tr('Email', self.language)}: {self.user_email}")
        info.setFont(QFont("Century Gothic", 28))
        info.setStyleSheet("color: #fff;")
        info.setAlignment(Qt.AlignHCenter)
        layout.addWidget(info, alignment=Qt.AlignHCenter)
        layout.addSpacing(30)
        del_btn = QPushButton(tr('Delete Account', self.language))
        del_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 28px; border: none; padding: 8px;")
        del_btn.setFixedWidth(350)
        del_btn.clicked.connect(self.delete_account)
        layout.addWidget(del_btn, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)
        back_btn = QPushButton(tr('Back', self.language))
        back_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 24px; border: none; padding: 8px;")
        back_btn.setFixedWidth(350)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)
        logout_btn = QPushButton(tr('Log out', self.language))
        logout_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 28px; border: none; padding: 8px;")
        logout_btn.setFixedWidth(350)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn, alignment=Qt.AlignHCenter)
        self.setLayout(layout)
        self.update_language(self.language)

    def delete_account(self):
        reply = QMessageBox.question(self, 'Delete Account', 'Are you sure?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                from main import User
                self.session.begin()
                user = self.session.query(User).filter_by(email=self.user_email).first()
                if user:
                    self.session.delete(user)
                    self.session.commit()
                self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))
            except Exception as e:
                self.session.rollback()
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def logout(self):
        self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))

    def go_back(self):
        self.parent().setCentralWidget(HomePage(self.user_name, self.user_surname, self.user_email, self.session, self.window()))

    def update_language(self, lang):
        self.layout().itemAt(0).widget().setText(tr('PROFILE', lang))
        info_label = self.layout().itemAt(4).widget()
        info_label.setText(f"{tr('Name', lang)} : {self.user_name}\n{tr('Surname', lang)}: {self.user_surname}\n{tr('Email', lang)}: {self.user_email}")
        self.layout().itemAt(6).widget().setText(tr('Delete Account', lang))
        self.layout().itemAt(8).widget().setText(tr('Back', lang))
        self.layout().itemAt(10).widget().setText(tr('Log out', lang))

class SettingsPage(QWidget):
    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
        self.theme = mainwindow.theme if mainwindow else 'dark'
        self.language = mainwindow.language if mainwindow else 'en'
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(30, 30, 30, 30)
        self.title = QLabel(tr('SETTINGS', self.language))
        self.title.setFont(QFont("Century Gothic", 36))
        self.title.setStyleSheet("color: #fff;" if self.theme=='dark' else "color: #222;")
        self.title.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        main_layout.addSpacing(30)
        theme_row = QHBoxLayout()
        self.theme_label = QLabel(tr('Theme Selection', self.language))
        self.theme_label.setFont(QFont("Century Gothic", 28))
        self.theme_label.setStyleSheet("background-color: #ddd; color: #222; padding: 4px 16px;")
        self.theme_label.setFixedWidth(320)
        theme_row.addWidget(self.theme_label)
        self.dark_radio = QRadioButton(tr('Dark', self.language), self)
        self.dark_radio.setFont(QFont("Century Gothic", 24))
        self.dark_radio.setStyleSheet("color: #fff;" if self.theme=='dark' else "color: #222;")
        self.light_radio = QRadioButton(tr('Light', self.language), self)
        self.light_radio.setFont(QFont("Century Gothic", 24))
        self.light_radio.setStyleSheet("color: #fff;" if self.theme=='dark' else "color: #222;")
        self.theme_group = QButtonGroup(self)
        self.theme_group.addButton(self.dark_radio)
        self.theme_group.addButton(self.light_radio)
        if self.theme == 'dark':
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)
        self.dark_radio.toggled.connect(self.set_dark_theme)
        self.light_radio.toggled.connect(self.set_light_theme)
        theme_row.addWidget(self.dark_radio)
        theme_row.addWidget(self.light_radio)
        theme_row.addStretch(1)
        main_layout.addLayout(theme_row)
        main_layout.addSpacing(30)
        lang_row = QHBoxLayout()
        self.lang_label = QLabel(tr('Language', self.language))
        self.lang_label.setFont(QFont("Century Gothic", 28))
        self.lang_label.setStyleSheet("background-color: #ddd; color: #222; padding: 4px 16px;")
        self.lang_label.setFixedWidth(320)
        lang_row.addWidget(self.lang_label)
        self.tr_radio = QRadioButton(tr('Turkish', self.language), self)
        self.tr_radio.setFont(QFont("Century Gothic", 24))
        self.tr_radio.setStyleSheet("color: #fff;" if self.theme=='dark' else "color: #222;")
        self.en_radio = QRadioButton(tr('English', self.language), self)
        self.en_radio.setFont(QFont("Century Gothic", 24))
        self.en_radio.setStyleSheet("color: #fff;" if self.theme=='dark' else "color: #222;")
        self.lang_group = QButtonGroup(self)
        self.lang_group.addButton(self.tr_radio)
        self.lang_group.addButton(self.en_radio)
        if self.language == 'tr':
            self.tr_radio.setChecked(True)
        else:
            self.en_radio.setChecked(True)
        self.tr_radio.toggled.connect(lambda: self.set_language('tr'))
        self.en_radio.toggled.connect(lambda: self.set_language('en'))
        lang_row.addWidget(self.tr_radio)
        lang_row.addWidget(self.en_radio)
        lang_row.addStretch(1)
        main_layout.addLayout(lang_row)
        self.del_history_btn = QPushButton(tr('Delete History', self.language))
        self.del_history_btn.setFont(QFont("Century Gothic", 28))
        self.del_history_btn.setStyleSheet("background-color: #ddd; color: #222; border: none; padding: 8px;")
        self.del_history_btn.setFixedWidth(350)
        self.del_feedback_btn = QPushButton(tr('Delete Feedback', self.language))
        self.del_feedback_btn.setFont(QFont("Century Gothic", 28))
        self.del_feedback_btn.setStyleSheet("background-color: #ddd; color: #222; border: none; padding: 8px;")
        self.del_feedback_btn.setFixedWidth(350)
        del_row = QHBoxLayout()
        del_row.addWidget(self.del_history_btn)
        del_row.addWidget(self.del_feedback_btn)
        main_layout.addLayout(del_row)
        main_layout.addSpacing(30)
        self.back_btn = QPushButton(tr('Back', self.language))
        self.back_btn.setFont(QFont("Century Gothic", 24))
        self.back_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 24px; border: none; padding: 8px;")
        self.back_btn.setFixedWidth(350)
        self.back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        self.set_theme(self.theme)
        self.update_language(self.language)

    def set_theme(self, theme):
        self.theme = theme
        self.setStyleSheet("background-color: #2A2A2A;" if theme == 'dark' else "background-color: #676767;")
        self.update_radio_colors("#fff" if theme=='dark' else "#222")
        if self.mainwindow:
            self.mainwindow.set_theme(theme)
        self.update_theme(theme)

    def set_dark_theme(self):
        if self.dark_radio.isChecked():
            self.set_theme('dark')

    def set_light_theme(self):
        if self.light_radio.isChecked():
            self.set_theme('light')

    def update_radio_colors(self, color):
        self.dark_radio.setStyleSheet(f"color: {color};")
        self.light_radio.setStyleSheet(f"color: {color};")
        self.tr_radio.setStyleSheet(f"color: {color};")
        self.en_radio.setStyleSheet(f"color: {color};")

    def set_language(self, lang):
        self.language = lang
        if self.mainwindow:
            self.mainwindow.set_language(lang)
        self.update_language(lang)

    def update_theme(self, theme):
        self.theme = theme
        self.setStyleSheet("background-color: #2A2A2A;" if theme == 'dark' else "background-color: #F4F4F4;")
        self.title.setStyleSheet("color: #fff;" if theme=='dark' else "color: #222;")
        self.theme_label.setStyleSheet("background-color: #ddd; color: #222; padding: 4px 16px;")
        self.lang_label.setStyleSheet("background-color: #ddd; color: #222; padding: 4px 16px;")
        self.del_history_btn.setStyleSheet("background-color: #ddd; color: #222; border: none; padding: 8px;")
        self.del_feedback_btn.setStyleSheet("background-color: #ddd; color: #222; border: none; padding: 8px;")
        self.back_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 24px; border: none; padding: 8px;")
        self.dark_radio.setStyleSheet("color: #fff;" if theme=='dark' else "color: #222;")
        self.light_radio.setStyleSheet("color: #fff;" if theme=='dark' else "color: #222;")
        self.tr_radio.setStyleSheet("color: #fff;" if theme=='dark' else "color: #222;")
        self.en_radio.setStyleSheet("color: #fff;" if theme=='dark' else "color: #222;")

    def update_language(self, lang):
        self.title.setText(tr('SETTINGS', lang))
        self.theme_label.setText(tr('Theme Selection', lang))
        self.dark_radio.setText(tr('Dark', lang))
        self.light_radio.setText(tr('Light', lang))
        self.lang_label.setText(tr('Language', lang))
        self.del_history_btn.setText(tr('Delete History', lang))
        self.del_feedback_btn.setText(tr('Delete Feedback', lang))
        self.back_btn.setText(tr('Back', lang))

    def go_back(self):
        if self.mainwindow:
            self.mainwindow.setCentralWidget(HomePage(self.mainwindow.user_name, self.mainwindow.user_surname, self.mainwindow.user_email, self.mainwindow.session, self.mainwindow))
        else:
            self.parent().setCentralWidget(SettingsPage())

class HomePage(QWidget):
    def __init__(self, user_name="User", user_surname="", user_email="", session=None, mainwindow=None):
        super().__init__()
        self.user_name = user_name
        self.user_surname = user_surname
        self.user_email = user_email
        self.session = session
        self.mainwindow = mainwindow
        self.language = mainwindow.language if mainwindow else 'en'
        self.theme = mainwindow.theme if mainwindow else 'dark'
        self.setWindowTitle("Sentilyze - Home")
        self.setStyleSheet("background-color: #2A2A2A;" if self.theme == 'dark' else "background-color: #F4F4F4;")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignTop)
        left_panel.setSpacing(20)

        self.logo = QLabel()
        logo_pixmap = QPixmap("icons/logo.png")
        self.logo.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignLeft)
        self.logo.setStyleSheet("background-color: #232323;" if self.theme == 'dark' else "background-color: #F4F4F4;")
        left_panel.addWidget(self.logo, alignment=Qt.AlignLeft)

        self.sentilyze_label = QLabel("Sentilyze")
        self.sentilyze_label.setFont(QFont("Century Gothic", 18))
        self.sentilyze_label.setStyleSheet("color: #fff; background-color: #232323;" if self.theme == 'dark' else "color: #232323; background-color: #F4F4F4;")
        self.sentilyze_label.setAlignment(Qt.AlignLeft)
        left_panel.addWidget(self.sentilyze_label, alignment=Qt.AlignLeft)

        left_panel.addSpacing(30)

        self.history_title = QLabel(tr('History', self.language) + "  <span style='font-size:16px;'>&#9432;</span>")
        self.history_title.setFont(QFont("Century Gothic", 16))
        self.history_title.setStyleSheet("color: #fff; background-color: #232323;" if self.theme == 'dark' else "color: #232323; background-color: #F4F4F4;")
        left_panel.addWidget(self.history_title, alignment=Qt.AlignLeft)

        self.history_list = QVBoxLayout()
        left_panel.addLayout(self.history_list)
        left_panel.addStretch(1)

        center_panel = QVBoxLayout()
        center_panel.setAlignment(Qt.AlignBottom)
        center_panel.setSpacing(20)

        self.chat_box = QVBoxLayout()
        self.chat_box.setAlignment(Qt.AlignTop)
        center_panel.addLayout(self.chat_box)
        center_panel.addSpacing(30)

        self.analyze_widget = QWidget()
        analyze_layout = QVBoxLayout()
        analyze_layout.setAlignment(Qt.AlignCenter)
        analyze_layout.setSpacing(10)

        analyze_logo = QLabel()
        analyze_logo.setPixmap(logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        analyze_logo.setAlignment(Qt.AlignCenter)
        analyze_layout.addWidget(analyze_logo, alignment=Qt.AlignCenter)

        analyzing_label = QLabel("Text is analyzing...")
        analyzing_label.setStyleSheet("color: #fff; font-size: 20px;")
        analyzing_label.setAlignment(Qt.AlignCenter)
        analyze_layout.addWidget(analyzing_label, alignment=Qt.AlignCenter)

        emoji_row = QHBoxLayout()
        for color in ["#E74C3C", "#F1C40F", "#27AE60"]:
            emoji = QLabel()
            emoji.setFixedSize(40, 40)
            emoji.setStyleSheet(f"background: {color}; border-radius: 20px;")
            emoji_row.addWidget(emoji)
        analyze_layout.addLayout(emoji_row)

        result_label = QLabel("The text has an overall neutral sentiment with a slight positive leaning.")
        result_label.setStyleSheet("color: #fff; font-size: 18px;")
        result_label.setAlignment(Qt.AlignCenter)
        analyze_layout.addWidget(result_label, alignment=Qt.AlignCenter)

        self.analyze_widget.setLayout(analyze_layout)
        self.analyze_widget.hide()
        center_panel.addWidget(self.analyze_widget)
        center_panel.addStretch(1)

        input_row = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(tr('Enter the text to be analyzed.', self.language))
        self.text_input.setStyleSheet("background-color: #444; color: #fff; font-size: 18px; border-radius: 4px; padding: 12px;" if self.theme == 'dark' else "background-color: #E0E0E0; color: #232323; font-size: 18px; border-radius: 4px; padding: 12px;")
        input_row.addWidget(self.text_input)
        self.analyze_btn = QPushButton(tr('Analyze', self.language))
        self.analyze_btn.setFixedSize(120, 48)
        self.analyze_btn.setStyleSheet("background-color: #757575; color: #fff; font-size: 18px; border-radius: 4px;" if self.theme == 'dark' else "background-color: #B0B0B0; color: #232323; font-size: 18px; border-radius: 4px;")
        self.analyze_btn.clicked.connect(self.send_message)
        input_row.addWidget(self.analyze_btn)
        center_panel.addLayout(input_row)

        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignTop)
        right_panel.setSpacing(20)

        first_letter = self.user_name[0].upper() if self.user_name else "U"
        self.profile_btn = QPushButton(first_letter)
        self.profile_btn.setFixedSize(48, 48)
        self.profile_btn.setStyleSheet("background-color: #444; color: #fff; font-size: 24px; border-radius: 24px;")
        self.profile_btn.clicked.connect(self.show_profile_menu)
        right_panel.addWidget(self.profile_btn, alignment=Qt.AlignRight)

        self.profile_menu = QWidget()
        self.profile_menu.setStyleSheet("background-color: #333; border-radius: 8px;")
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)

        profile_btn = QPushButton("Profile")
        profile_btn.setStyleSheet("background: none; color: #fff; font-size: 16px; padding: 8px 16px; text-align:left;")
        profile_btn.setCursor(Qt.PointingHandCursor)
        profile_btn.clicked.connect(self.goto_profile)
        menu_layout.addWidget(profile_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet("background: none; color: #fff; font-size: 16px; padding: 8px 16px; text-align:left;")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(self.goto_settings)
        menu_layout.addWidget(settings_btn)

        logout_btn = QPushButton("Log Out")
        logout_btn.setStyleSheet("background: none; color: #fff; font-size: 16px; padding: 8px 16px; text-align:left;")
        logout_btn.setCursor(Qt.PointingHandCursor)
        menu_layout.addWidget(logout_btn)
        self.profile_menu.setLayout(menu_layout)
        self.profile_menu.hide()
        right_panel.addWidget(self.profile_menu, alignment=Qt.AlignRight)

        right_panel.addStretch(1)

        self.ai_bot_btn = QPushButton()
        ai_pixmap = QPixmap("icons/ai.png")
        self.ai_bot_btn.setIcon(QIcon(ai_pixmap))
        self.ai_bot_btn.setIconSize(ai_pixmap.size())
        self.ai_bot_btn.setFixedSize(50, 50)
        self.ai_bot_btn.setStyleSheet("background: none; border: none;")
        self.ai_bot_btn.setCursor(Qt.PointingHandCursor)
        right_panel.addWidget(self.ai_bot_btn, alignment=Qt.AlignRight)

        main_layout.addLayout(left_panel, 2)
        main_layout.addSpacing(20)
        main_layout.addLayout(center_panel, 6)
        main_layout.addSpacing(20)
        main_layout.addLayout(right_panel, 2)

        self.setLayout(main_layout)
        self.update_language(self.language)

    def analyze_sentiment_api(self, text, lang="en"):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                json={"text": text, "lang": lang}
            )
            if response.ok:
                data = response.json()
                return data['label'], data['score']
            else:
                return "error", 0
        except Exception as e:
            print(f"API error: {e}")
            return "error", 0

    def send_message(self):
        text = self.text_input.text().strip()
        if text:
            msg_widget = QWidget()
            msg_layout = QHBoxLayout()
            msg_layout.setContentsMargins(0, 0, 0, 0)
            msg_layout.setSpacing(10)
            first_letter = self.user_name[0].upper() if self.user_name else "U"
            avatar = QLabel(first_letter)
            avatar.setFixedSize(40, 40)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setStyleSheet("background-color: #888; color: #222; font-size: 20px; border-radius: 20px;")
            msg_layout.addWidget(avatar)
            msg = QLabel(text)
            msg.setWordWrap(True)
            if self.theme == 'dark':
                msg.setStyleSheet("color: #fff; font-size: 20px; background: transparent;")
            else:
                msg.setStyleSheet("color: #232323; font-size: 20px; background: transparent;")
            msg_layout.addWidget(msg)
            msg_widget.setLayout(msg_layout)
            self.chat_box.addWidget(msg_widget)
            self.text_input.clear()
            lang = self.language if hasattr(self, 'language') else 'en'
            label, score = self.analyze_sentiment_api(text, lang)
            self.analyze_widget.show()
            if hasattr(self.analyze_widget, 'result_label'):
                self.analyze_widget.result_label.setText(f"{label} ({score:.2f})")
            else:
                for child in self.analyze_widget.findChildren(QLabel):
                    if 'sentiment' in child.text().lower() or 'Text is analyzing' in child.text():
                        child.setText(f"{label} ({score:.2f})")
                        break
            history_btn = QPushButton(text[:30] + ("..." if len(text) > 30 else ""))
            if self.theme == 'dark':
                history_btn.setStyleSheet("background-color: #444; color: #fff; border:none; text-align:left; padding:8px; font-size:16px;")
            else:
                history_btn.setStyleSheet("background-color: #E0E0E0; color: #232323; border:none; text-align:left; padding:8px; font-size:16px;")
            history_btn.setFixedWidth(180)
            self.history_list.addWidget(history_btn)

    def show_profile_menu(self):
        if self.profile_menu.isVisible():
            self.profile_menu.hide()
        else:
            self.profile_menu.show()

    def goto_profile(self):
        self.parent().setCentralWidget(ProfilePage(self.user_name, self.user_surname, self.user_email, self.session, self.language))

    def goto_settings(self):
        mainwindow = self.window()
        print('DEBUG: mainwindow =', mainwindow)
        print('DEBUG: is QMainWindow?', isinstance(mainwindow, QMainWindow))
        if isinstance(mainwindow, QMainWindow):
            mainwindow.setCentralWidget(SettingsPage(mainwindow))
        else:
            print('DEBUG: mainwindow is not QMainWindow, cannot open SettingsPage')

    def update_language(self, lang):
        self.text_input.setPlaceholderText(tr('Enter the text to be analyzed.', lang))
        self.analyze_btn.setText(tr('Analyze', lang))
        self.history_title.setText(tr('History', lang) + "  <span style='font-size:16px;'>&#9432;</span>")
        if hasattr(self, 'profile_menu'):
            layout = self.profile_menu.layout()
            if layout:
                for i in range(layout.count()):
                    btn = layout.itemAt(i).widget()
                    if btn:
                        if i == 0:
                            btn.setText(tr('Profile', lang))
                        elif i == 1:
                            btn.setText(tr('Settings', lang))
                        elif i == 2:
                            btn.setText(tr('Log out', lang))

    def update_theme(self, theme):
        self.theme = theme
        self.setStyleSheet("background-color: #2A2A2A;" if theme == 'dark' else "background-color: #F4F4F4;")
        self.logo.setStyleSheet("background-color: #232323;" if theme == 'dark' else "background-color: #F4F4F4;")
        self.sentilyze_label.setStyleSheet("color: #fff; background-color: #232323;" if theme == 'dark' else "color: #232323; background-color: #F4F4F4;")
        self.history_title.setStyleSheet("color: #fff; background-color: #232323;" if theme == 'dark' else "color: #232323; background-color: #F4F4F4;")
        self.text_input.setStyleSheet("background-color: #444; color: #fff; font-size: 18px; border-radius: 4px; padding: 12px;" if theme == 'dark' else "background-color: #E0E0E0; color: #232323; font-size: 18px; border-radius: 4px; padding: 12px;")
        self.analyze_btn.setStyleSheet("background-color: #757575; color: #fff; font-size: 18px; border-radius: 4px;" if theme == 'dark' else "background-color: #B0B0B0; color: #232323; font-size: 18px; border-radius: 4px;")
        for i in range(self.history_list.count()):
            btn = self.history_list.itemAt(i).widget()
            if btn:
                if theme == 'dark':
                    btn.setStyleSheet("background-color: #444; color: #fff; border:none; text-align:left; padding:8px; font-size:16px;")
                else:
                    btn.setStyleSheet("background-color: #E0E0E0; color: #232323; border:none; text-align:left; padding:8px; font-size:16px;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(1600,900)
        self.theme = 'dark'
        self.language = 'en'
        self.session = None
        self.user_name = "User"
        self.user_surname = ""
        self.user_email = ""
        self.setWindowIcon(QIcon("icons/logo.png"))
        self.setCentralWidget(FirstPage(mainwindow=self))
        self.apply_theme()

    def set_theme(self, theme):
        self.theme = theme
        self.apply_theme()
        cw = self.centralWidget()
        if hasattr(cw, 'update_theme'):
            cw.update_theme(theme)

    def set_language(self, lang):
        self.language = lang
        cw = self.centralWidget()
        if hasattr(cw, 'update_language'):
            cw.update_language(lang)

    def apply_theme(self):
        if self.theme == 'dark':
            self.setStyleSheet("background-color: #2A2A2A;")
        else:
            self.setStyleSheet("background-color: #676767;")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()