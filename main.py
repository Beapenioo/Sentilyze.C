import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QRadioButton, QButtonGroup, QScrollArea, QDialog, QTextEdit
from PyQt5.QtCore import Qt, QTimer, QSize, QMetaObject, Q_ARG
from PyQt5.QtGui import QFont, QPixmap, QIcon
from sqlalchemy import create_engine, Column, Integer, String, event, ForeignKey, DateTime, Float, Text, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import requests
from datetime import datetime

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

class SessionLog(Base):
    __tablename__ = 'session_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    login_time = Column(DateTime, default=datetime.now)
    logout_time = Column(DateTime, nullable=True)

class TextEntry(Base):
    __tablename__ = 'text_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    text_id = Column(Integer, ForeignKey('text_entries.id'), nullable=False)
    sentiment = Column(String(50), nullable=False)
    sentiment_score = Column(Float, nullable=False)
    analysis_date = Column(DateTime, default=datetime.now)

class Feedback(Base):
    __tablename__ = 'feedbacks'
    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text_id = Column(Integer, ForeignKey('text_entries.id'), nullable=False)
    feedback_text = Column(String(500), nullable=True)
    rating = Column(Integer, nullable=False)
    feedback_date = Column(DateTime, default=datetime.now)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Global database session and engine
db_engine = None
db_session = None

def get_db_engine():
    global db_engine
    if db_engine is None:
        try:
            DATABASE_URL = "mysql+pymysql://root:@localhost:3306/sentilyze"
            db_engine = create_engine(DATABASE_URL, echo=True)
            
            # Veritabanı bağlantısını test et
            with db_engine.connect() as conn:
                # Veritabanının var olup olmadığını kontrol et
                result = conn.execute(text("SELECT DATABASE()"))
                current_db = result.scalar()
                
                if not current_db:
                    # Veritabanı yoksa oluştur
                    conn.execute(text("CREATE DATABASE IF NOT EXISTS sentilyze"))
                    conn.execute(text("USE sentilyze"))
                
                # Tabloları oluştur
                Base.metadata.create_all(db_engine)
                conn.commit()
                
        except Exception as e:
            print(f"Database engine initialization error: {e}")
            return None
    return db_engine

def get_db_session():
    global db_session
    if db_session is None:
        engine = get_db_engine()
        if engine:
            Session = sessionmaker(bind=engine)
            db_session = Session()
    return db_session

def close_db_session():
    global db_session
    if db_session:
        db_session.close()
        db_session = None

def perform_analysis(session, text_entry_id, sentiment, sentiment_score):
    try:
        analysis_result = AnalysisResult(
            text_id=text_entry_id,
            sentiment=sentiment,
            sentiment_score=sentiment_score
        )
        session.add(analysis_result)
        session.commit()
        return analysis_result.result_id
    except Exception as e:
        print(f"Error performing analysis: {e}")
        session.rollback()
        return None

def retrieve_analysis(session, text_entry_id):
    try:
        analysis = session.query(AnalysisResult).filter_by(text_id=text_entry_id).first()
        return analysis
    except Exception as e:
        print(f"Error retrieving analysis: {e}")
        return None

class SignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: #2A2A2A;")
        
        try:
            self.session = get_db_session()
            if not self.session:
                QMessageBox.critical(self, "Error", "Failed to initialize database. Please try again.")
                self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))
                return
        except Exception as e:
            print(f"Database initialization error in SignUp: {e}")
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
            self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))
            return
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        logo = QLabel()
        logo_path = get_resource_path("icons/logo.png")
        logo_pixmap = QPixmap(logo_path)
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
            # Önce mevcut kullanıcıyı kontrol et
            existing_user = self.session.query(User).filter_by(email=email).first()
            if existing_user:
                QMessageBox.warning(self, "Error", "Email already exists")
                return

            # Yeni kullanıcı oluştur
            new_user = User(
                name=name,
                surname=surname,
                email=email,
                password=password
            )
            self.session.add(new_user)
            self.session.commit()

            # Kullanıcının oluşturulduğunu doğrula
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
        try:
            if self.session:
                self.session.close()
            self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))
        except Exception as e:
            print(f"Error during go_back: {e}")
            self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: #2A2A2A;")
        
        self.session = get_db_session()
        if not self.session:
            QMessageBox.critical(self, "Error", "Failed to initialize database")
            return
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        logo = QLabel()
        logo_path = get_resource_path("icons/logo.png")
        logo_pixmap = QPixmap(logo_path)
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
                # Create session log
                session_log = SessionLog(user_id=user.id)
                self.session.add(session_log)
                self.session.commit()
                # Store session_log_id in mainwindow
                mainwindow = self.parent()
                if hasattr(mainwindow, 'session_log_id'):
                    mainwindow.session_log_id = session_log.id
                print(f"User logged in successfully: {user.name} {user.surname}")
                QMessageBox.information(self, "Success", "Login successful!")
                self.parent().setCentralWidget(HomePage(user.name, user.surname, user.email, self.session, mainwindow=mainwindow, session_log_id=session_log.id))
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
        logo_path = get_resource_path("icons/logo.png")
        logo_pixmap = QPixmap(logo_path)
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
    def __init__(self, user_name, user_surname, user_email, session, language='en', session_log_id=None, mainwindow=None):
        super().__init__()
        self.user_name = user_name
        self.user_surname = user_surname
        self.user_email = user_email
        self.session = session
        self.language = language
        self.session_log_id = session_log_id
        self.mainwindow = mainwindow
        self.setStyleSheet("background: none;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        title = QLabel(tr('PROFILE', self.language))
        title.setFont(QFont("Century Gothic", 32))
        title.setStyleSheet("color: #fff; background: none;" if self.language=='en' else "color: #fff; background: none;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        first_letter = self.user_name[0].upper() if self.user_name else "U"
        avatar = QLabel(first_letter)
        avatar.setFixedSize(90, 90)
        avatar.setAlignment(Qt.AlignCenter)
        # Use mainwindow.theme if available, else fallback to dark
        theme = self.mainwindow.theme if self.mainwindow and hasattr(self.mainwindow, 'theme') else 'dark'
        avatar.setStyleSheet(f"background: none; color: {'#fff' if theme == 'dark' else '#222'}; font-size: 40px; border-radius: 45px; border: 2px solid #888;")
        layout.addWidget(avatar, alignment=Qt.AlignHCenter)
        layout.addSpacing(20)
        info = QLabel(f"{tr('Name', self.language)} : {self.user_name}\n{tr('Surname', self.language)}: {self.user_surname}\n{tr('Email', self.language)}: {self.user_email}")
        info.setFont(QFont("Century Gothic", 28))
        info.setStyleSheet("color: #fff; background: none;" if self.language=='en' else "color: #fff; background: none;")
        info.setAlignment(Qt.AlignHCenter)
        layout.addWidget(info, alignment=Qt.AlignHCenter)
        layout.addSpacing(30)
        del_btn = QPushButton(tr('Delete Account', self.language))
        del_btn.setStyleSheet("background-color: #b00020; color: #fff; font-size: 28px; border: none; border-radius: 8px; padding: 8px 0;")
        del_btn.setFixedWidth(350)
        del_btn.setFixedHeight(48)
        del_btn.clicked.connect(self.delete_account)
        layout.addWidget(del_btn, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)
        back_btn = QPushButton(tr('Back', self.language))
        back_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 24px; border: none; border-radius: 8px; padding: 8px 0;")
        back_btn.setFixedWidth(350)
        back_btn.setFixedHeight(48)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)
        logout_btn = QPushButton(tr('Log out', self.language))
        logout_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 28px; border: none; border-radius: 8px; padding: 8px 0;")
        logout_btn.setFixedWidth(350)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn, alignment=Qt.AlignHCenter)
        self.setLayout(layout)
        self.update_language(self.language)

    def delete_account(self):
        reply = QMessageBox.question(self, 'Delete Account', 'Are you sure?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                user = self.session.query(User).filter_by(email=self.user_email).first()
                if user:
                    # Kullanıcının tüm text_entry id'lerini al
                    text_ids = [t.id for t in self.session.query(TextEntry).filter_by(user_id=user.id).all()]
                    if text_ids:
                        # Önce feedbackleri sil
                        self.session.query(Feedback).filter(Feedback.text_id.in_(text_ids)).delete(synchronize_session=False)
                        # Sonra analysis_results sil
                        self.session.query(AnalysisResult).filter(AnalysisResult.text_id.in_(text_ids)).delete(synchronize_session=False)
                    # Text_entries sil
                    self.session.query(TextEntry).filter_by(user_id=user.id).delete(synchronize_session=False)
                    # SessionLogs sil
                    self.session.query(SessionLog).filter_by(user_id=user.id).delete(synchronize_session=False)
                    # En son kullanıcıyı sil
                    self.session.delete(user)
                    self.session.commit()
                self.parent().setCentralWidget(FirstPage(mainwindow=self.window()))
            except Exception as e:
                self.session.rollback()
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def logout(self):
        session_log_id = self.session_log_id or (self.mainwindow.session_log_id if self.mainwindow and hasattr(self.mainwindow, 'session_log_id') else None)
        session = self.session or (self.mainwindow.session if self.mainwindow and hasattr(self.mainwindow, 'session') else None)
        if session_log_id and session:
            try:
                session_log = session.query(SessionLog).get(session_log_id)
                if session_log:
                    session_log.logout_time = datetime.now()
                    session.commit()
            except Exception as e:
                print(f"Error updating session log: {e}")
        self.parent().setCentralWidget(FirstPage(mainwindow=self.mainwindow))

    def go_back(self):
        self.parent().setCentralWidget(HomePage(self.user_name, self.user_surname, self.user_email, self.session, mainwindow=self.mainwindow))

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
        self.user_name = mainwindow.user_name if mainwindow else "User"
        self.user_surname = mainwindow.user_surname if mainwindow else ""
        self.user_email = mainwindow.user_email if mainwindow else ""
        self.session = mainwindow.session if mainwindow else None
        self.session_log_id = mainwindow.session_log_id if mainwindow and hasattr(mainwindow, 'session_log_id') else None
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Notification icon
        notif_row = QHBoxLayout()
        notif_row.addStretch(1)
        self.notif_btn = QPushButton()
        notif_icon_path = get_resource_path('icons/notification.png')
        if os.path.exists(notif_icon_path):
            notif_icon = QIcon(notif_icon_path)
            self.notif_btn.setIcon(notif_icon)
            self.notif_btn.setIconSize(QSize(32, 32))
        self.notif_btn.setFixedSize(48, 48)
        self.notif_btn.setStyleSheet("background: none; border: none;")
        self.notif_btn.clicked.connect(self.show_notifications)
        notif_row.addWidget(self.notif_btn)
        main_layout.addLayout(notif_row)

        self.title = QLabel(tr('SETTINGS', self.language))
        self.title.setFont(QFont("Century Gothic", 36))
        self.title.setStyleSheet("color: #fff; background: none;" if self.theme=='dark' else "color: #232323; background: none;")
        self.title.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        main_layout.addSpacing(30)
        theme_row = QHBoxLayout()
        self.theme_label = QLabel(tr('Theme Selection', self.language))
        self.theme_label.setFont(QFont("Century Gothic", 28))
        self.theme_label.setStyleSheet(f"color: #fff; background: none;" if self.theme=='dark' else "color: #232323; background: none;")
        self.theme_label.setMinimumWidth(420)
        theme_row.addWidget(self.theme_label)
        self.dark_radio = QRadioButton(tr('Dark', self.language), self)
        self.dark_radio.setFont(QFont("Century Gothic", 24))
        self.dark_radio.setStyleSheet(f"color: #fff; background: none;" if self.theme=='dark' else "color: #232323; background: none;")
        self.light_radio = QRadioButton(tr('Light', self.language), self)
        self.light_radio.setFont(QFont("Century Gothic", 24))
        self.light_radio.setStyleSheet(f"color: #fff; background: none; margin-left: 32px;" if self.theme=='dark' else "color: #232323; background: none; margin-left: 32px;")
        self.theme_group = QButtonGroup(self)
        self.theme_group.addButton(self.dark_radio)
        self.theme_group.addButton(self.light_radio)
        if self.theme == 'dark':
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)
        self.dark_radio.toggled.connect(self.set_dark_theme)
        self.light_radio.toggled.connect(self.set_light_theme)
        theme_row.addSpacing(60)
        theme_row.addWidget(self.dark_radio)
        theme_row.addWidget(self.light_radio)
        theme_row.addStretch(1)
        main_layout.addLayout(theme_row)
        main_layout.addSpacing(30)
        lang_row = QHBoxLayout()
        self.lang_label = QLabel(tr('Language', self.language))
        self.lang_label.setFont(QFont("Century Gothic", 28))
        self.lang_label.setStyleSheet(f"color: #fff; background: none;" if self.theme=='dark' else "color: #232323; background: none;")
        self.lang_label.setFixedWidth(320)
        lang_row.addWidget(self.lang_label)
        lang_row.addSpacing(60)
        self.tr_radio = QRadioButton(tr('Turkish', self.language), self)
        self.tr_radio.setFont(QFont("Century Gothic", 24))
        self.tr_radio.setStyleSheet(f"color: #fff; background: none;" if self.theme=='dark' else "color: #232323; background: none;")
        self.en_radio = QRadioButton(tr('English', self.language), self)
        self.en_radio.setFont(QFont("Century Gothic", 24))
        self.en_radio.setStyleSheet(f"color: #fff; background: none; margin-left: 32px;" if self.theme=='dark' else "color: #232323; background: none; margin-left: 32px;")
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
        self.del_history_btn.setFont(QFont("Century Gothic", 22))
        self.del_history_btn.setStyleSheet("background-color: #b00020; color: #fff; border: none; padding: 12px 18px; border-radius: 8px; min-width: 220px; font-weight: 600;")
        self.del_history_btn.setMinimumWidth(220)
        self.del_history_btn.clicked.connect(self.delete_history)
        self.del_feedback_btn = QPushButton(tr('Delete Feedback', self.language))
        self.del_feedback_btn.setFont(QFont("Century Gothic", 22))
        self.del_feedback_btn.setStyleSheet("background-color: #b00020; color: #fff; border: none; padding: 12px 18px; border-radius: 8px; min-width: 220px; font-weight: 600;")
        self.del_feedback_btn.setMinimumWidth(220)
        self.del_feedback_btn.clicked.connect(self.delete_feedback)
        del_row = QHBoxLayout()
        del_row.addWidget(self.del_history_btn)
        del_row.addWidget(self.del_feedback_btn)
        main_layout.addLayout(del_row)
        main_layout.addSpacing(30)
        self.back_btn = QPushButton(tr('Back', self.language))
        self.back_btn.setFont(QFont("Century Gothic", 24))
        self.back_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 24px; border: none; padding: 8px; border-radius: 8px;")
        self.back_btn.setFixedWidth(350)
        self.back_btn.setFixedHeight(48)
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
        # Always apply margin-left for alignment
        self.dark_radio.setStyleSheet(f"color: {color}; background: none; margin-left: 0px;")
        self.light_radio.setStyleSheet(f"color: {color}; background: none; margin-left: 32px;")
        self.tr_radio.setStyleSheet(f"color: {color}; background: none; margin-left: 0px;")
        self.en_radio.setStyleSheet(f"color: {color}; background: none; margin-left: 32px;")

    def set_language(self, lang):
        self.language = lang
        if self.mainwindow:
            self.mainwindow.set_language(lang)
        self.update_language(lang)

    def update_theme(self, theme):
        self.theme = theme
        bg_color = "#2A2A2A" if theme == 'dark' else "#F4F4F4"
        text_color = "#fff" if theme == 'dark' else "#232323"
        btn_bg = "#444" if theme == 'dark' else "#F4F4F4"
        btn_text = "#fff" if theme == 'dark' else "#232323"
        accent_bg = "#757575" if theme == 'dark' else "#B0B0B0"
        self.setStyleSheet(f"background-color: {bg_color};")
        self.title.setStyleSheet(f"color: {text_color}; background: none;")
        self.theme_label.setStyleSheet(f"color: {text_color}; background: none;")
        self.lang_label.setStyleSheet(f"color: {text_color}; background: none;")
        self.del_history_btn.setStyleSheet("background-color: #b00020; color: #fff; border: none; padding: 12px 18px; border-radius: 8px; min-width: 220px; font-weight: 600;")
        self.del_feedback_btn.setStyleSheet("background-color: #b00020; color: #fff; border: none; padding: 12px 18px; border-radius: 8px; min-width: 220px; font-weight: 600;")
        self.back_btn.setStyleSheet("background-color: #ddd; color: #222; font-size: 24px; border: none; padding: 8px; border-radius: 8px;")
        self.update_radio_colors(text_color)

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
            self.mainwindow.setCentralWidget(HomePage(
                user_name=self.mainwindow.user_name,
                user_surname=self.mainwindow.user_surname,
                user_email=self.mainwindow.user_email,
                session=self.mainwindow.session,
                mainwindow=self.mainwindow,
                session_log_id=self.mainwindow.session_log_id if self.mainwindow and hasattr(self.mainwindow, 'session_log_id') else None
            ))
        else:
            self.parent().setCentralWidget(SettingsPage())

    def delete_history(self):
        reply = QMessageBox.question(self, tr('Delete History', self.language), tr('Are you sure?', self.language), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                user = self.session.query(User).filter_by(email=self.user_email).first()
                if user:
                    # Kullanıcının tüm text_entry id'lerini al
                    text_ids = [t.id for t in self.session.query(TextEntry).filter_by(user_id=user.id).all()]
                    if text_ids:
                        # Önce feedbackleri sil
                        self.session.query(Feedback).filter(Feedback.text_id.in_(text_ids)).delete(synchronize_session=False)
                        # Sonra analysis_results sil
                        self.session.query(AnalysisResult).filter(AnalysisResult.text_id.in_(text_ids)).delete(synchronize_session=False)
                    # En son text_entries sil
                    self.session.query(TextEntry).filter_by(user_id=user.id).delete(synchronize_session=False)
                    self.session.commit()
                    QMessageBox.information(self, tr('Delete History', self.language), tr('History deleted successfully!', self.language))
                    if self.mainwindow:
                        self.mainwindow.setCentralWidget(SettingsPage(self.mainwindow))
                else:
                    QMessageBox.warning(self, tr('Delete History', self.language), tr('User not found!', self.language))
            except Exception as e:
                self.session.rollback()
                QMessageBox.warning(self, tr('Delete History', self.language), f"Error: {str(e)}")

    def delete_feedback(self):
        reply = QMessageBox.question(self, tr('Delete Feedback', self.language), tr('Are you sure?', self.language), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                user = self.session.query(User).filter_by(email=self.user_email).first()
                if user:
                    self.session.query(Feedback).filter_by(user_id=user.id).delete(synchronize_session=False)
                    self.session.commit()
                    QMessageBox.information(self, tr('Delete Feedback', self.language), tr('Feedback deleted successfully!', self.language))
                else:
                    QMessageBox.warning(self, tr('Delete Feedback', self.language), tr('User not found!', self.language))
            except Exception as e:
                self.session.rollback()
                QMessageBox.warning(self, tr('Delete Feedback', self.language), f"Error: {str(e)}")

    def show_notifications(self):
        # Show login/logout history for the user
        if not self.session:
            QMessageBox.information(self, "Notifications", "No database connection.")
            return
        user = self.session.query(User).filter_by(email=self.user_email).first()
        if not user:
            QMessageBox.information(self, "Notifications", "User not found.")
            return
        logs = self.session.query(SessionLog).filter_by(user_id=user.id).order_by(SessionLog.login_time.desc()).all()
        if not logs:
            QMessageBox.information(self, "Notifications", "No login/logout history found.")
            return
        msg = ""
        for log in logs:
            login_str = log.login_time.strftime('%Y-%m-%d %H:%M:%S') if log.login_time else '-'
            logout_str = log.logout_time.strftime('%Y-%m-%d %H:%M:%S') if log.logout_time else '-'
            msg += f"Login: {login_str}\nLogout: {logout_str}\n---\n"
        # Show in a scrollable dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Login/Logout History")
        dlg.setFixedSize(400, 350)
        layout = QVBoxLayout()
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(msg)
        layout.addWidget(text)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.setLayout(layout)
        dlg.exec_()

class HomePage(QWidget):
    def __init__(self, user_name="User", user_surname="", user_email="", session=None, mainwindow=None, session_log_id=None):
        super().__init__()
        self.user_name = user_name
        self.user_surname = user_surname
        self.user_email = user_email
        self.session = session
        self.mainwindow = mainwindow
        self.session_log_id = session_log_id or (mainwindow.session_log_id if mainwindow and hasattr(mainwindow, 'session_log_id') else None)
        self.language = mainwindow.language if mainwindow else 'en'
        self.theme = mainwindow.theme if mainwindow else 'dark'
        self.ai_chat_dialog = None  # Initialize ai_chat_dialog as None
        
        # Kullanıcı bilgilerini mainwindow'a aktar
        if mainwindow:
            mainwindow.user_name = user_name
            mainwindow.user_surname = user_surname
            mainwindow.user_email = user_email
            mainwindow.session_log_id = self.session_log_id
        self.setWindowTitle("Sentilyze - Home")
        self.setStyleSheet("background-color: #2A2A2A;" if self.theme == 'dark' else "background-color: #F4F4F4;")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignTop)
        left_panel.setSpacing(20)

        self.logo = QLabel()
        logo_path = get_resource_path("icons/logo.png")
        logo_pixmap = QPixmap(logo_path)
        self.logo.setPixmap(logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignLeft)
        self.logo.setStyleSheet("background: none;")
        left_panel.addWidget(self.logo, alignment=Qt.AlignLeft)

        self.sentilyze_label = QLabel("Sentilyze")
        self.sentilyze_label.setFont(QFont("Century Gothic", 18))
        self.sentilyze_label.setStyleSheet("color: #fff; background: none;" if self.theme == 'dark' else "color: #232323; background: none;")
        self.sentilyze_label.setAlignment(Qt.AlignLeft)
        left_panel.addWidget(self.sentilyze_label, alignment=Qt.AlignLeft)

        left_panel.addSpacing(30)

        self.history_title = QLabel(tr('History', self.language) + "  <span style='font-size:16px;'>&#9432;</span>")
        self.history_title.setFont(QFont("Century Gothic", 16))
        self.history_title.setStyleSheet("color: #fff; background: none;" if self.theme == 'dark' else "color: #232323; background: none;")
        left_panel.addWidget(self.history_title, alignment=Qt.AlignLeft)

        self.history_widget = QWidget()
        self.history_list = QVBoxLayout()
        self.history_list.setAlignment(Qt.AlignTop)
        self.history_widget.setLayout(self.history_list)
        self.history_widget.setMinimumWidth(200)
        self.history_widget.setMaximumWidth(200)
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setWidget(self.history_widget)
        self.history_scroll.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        left_panel.addWidget(self.history_scroll)

        # Geçmiş kayıtlarını yükle
        self.load_history()

        left_panel.addStretch(1)

        center_panel = QVBoxLayout()
        center_panel.setAlignment(Qt.AlignBottom)
        center_panel.setSpacing(20)

        self.chat_box_widget = QWidget()
        self.chat_box = QVBoxLayout()
        self.chat_box.setAlignment(Qt.AlignTop)
        self.chat_box_widget.setLayout(self.chat_box)
        self.chat_box_widget.setMinimumWidth(700)
        self.chat_box_widget.setMaximumWidth(700)
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setWidget(self.chat_box_widget)
        self.chat_scroll.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        center_panel.addWidget(self.chat_scroll, stretch=1)

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

        # Profile button (top right)
        first_letter = self.user_name[0].upper() if self.user_name else "U"
        self.profile_btn = QPushButton(first_letter)
        self.profile_btn.setFixedSize(48, 48)
        self.profile_btn.setStyleSheet("background-color: #444; color: #fff; font-size: 24px; border-radius: 24px;")
        self.profile_btn.clicked.connect(self.show_profile_menu)
        right_panel.addWidget(self.profile_btn, alignment=Qt.AlignRight)

        right_panel.addStretch(1)

        # AI Button (center right)
        self.ai_btn = QPushButton()
        ai_icon_path = get_resource_path('icons/ai.png')
        if os.path.exists(ai_icon_path):
            ai_icon = QIcon(ai_icon_path)
            self.ai_btn.setIcon(ai_icon)
            self.ai_btn.setIconSize(QSize(40, 40))
        self.ai_btn.setFixedSize(60, 60)
        self.ai_btn.setStyleSheet("background: none; border: none; border-radius: 8px;")
        self.ai_btn.clicked.connect(self.show_ai_chat)
        right_panel.addWidget(self.ai_btn, alignment=Qt.AlignVCenter | Qt.AlignRight)

        right_panel.addStretch(1)

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
        logout_btn.clicked.connect(self.logout)
        menu_layout.addWidget(logout_btn)
        self.profile_menu.setLayout(menu_layout)
        self.profile_menu.hide()
        right_panel.addWidget(self.profile_menu, alignment=Qt.AlignRight)

        right_panel.addStretch(1)

        main_layout.addLayout(left_panel, 2)
        main_layout.addSpacing(20)
        main_layout.addLayout(center_panel, 6)
        main_layout.addSpacing(20)
        main_layout.addLayout(right_panel, 2)

        self.setLayout(main_layout)
        self.update_language(self.language)

    def load_history(self):
        try:
            # Önceki geçmiş kayıtlarını temizle
            while self.history_list.count():
                item = self.history_list.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Kullanıcının geçmiş kayıtlarını veritabanından al
            user = self.session.query(User).filter_by(email=self.user_email).first()
            if user:
                text_entries = self.session.query(TextEntry).filter_by(user_id=user.id).order_by(TextEntry.created_at.desc()).all()
                
                for entry in text_entries:
                    history_btn = QPushButton(entry.text[:30] + ("..." if len(entry.text) > 30 else ""))
                    if self.theme == 'dark':
                        history_btn.setStyleSheet("background-color: #444; color: #fff; border:none; text-align:left; padding:8px; font-size:16px;")
                    else:
                        history_btn.setStyleSheet("background-color: #E0E0E0; color: #232323; border:none; text-align:left; padding:8px; font-size:16px;")
                    history_btn.setFixedWidth(180)
                    history_btn.clicked.connect(lambda checked, text=entry.text: self.show_history_item(text))
                    self.history_list.addWidget(history_btn)

        except Exception as e:
            print(f"Error loading history: {e}")

    def show_history_item(self, text):
        # Geçmiş öğesini tıklandığında metin kutusuna yerleştir
        self.text_input.setText(text)

    def send_message(self):
        text = self.text_input.text().strip()
        if text:
            try:
                # Get user from database
                user = self.session.query(User).filter_by(email=self.user_email).first()
                if not user:
                    print(f"User not found in database: {self.user_email}")
                    QMessageBox.warning(self, "Error", "User session expired. Please login again.")
                    self.logout()
                    return

                # Create text entry
                text_entry = TextEntry(
                    user_id=user.id,
                    text=text,
                    language=self.detect_lang(text)
                )
                self.session.add(text_entry)
                self.session.commit()

                # Create message container
                message_container = QWidget()
                message_layout = QVBoxLayout()
                message_layout.setContentsMargins(0, 0, 0, 20)
                message_layout.setSpacing(10)

                # User message
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
                message_layout.addWidget(msg_widget)

                # Analyzing widget
                analyzing_widget = QWidget()
                analyzing_layout = QVBoxLayout()
                analyzing_layout.setContentsMargins(50, 0, 0, 0)
                analyzing_layout.setSpacing(5)
                bar_logo = QLabel()
                bar_pixmap = QPixmap("icons/bar.png")
                bar_logo.setPixmap(bar_pixmap.scaled(120, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                bar_logo.setAlignment(Qt.AlignCenter)
                analyzing_layout.addWidget(bar_logo, alignment=Qt.AlignCenter)
                analyzing_label = QLabel("Text is analyzing...")
                analyzing_label.setStyleSheet("color: #fff; font-size: 18px; font-weight: bold;" if self.theme == 'dark' else "color: #232323; font-size: 18px; font-weight: bold;")
                analyzing_label.setAlignment(Qt.AlignCenter)
                analyzing_layout.addWidget(analyzing_label, alignment=Qt.AlignCenter)
                analyzing_widget.setLayout(analyzing_layout)
                message_layout.addWidget(analyzing_widget)
                message_container.setLayout(message_layout)
                self.chat_box.addWidget(message_container)
                self.text_input.clear()
                QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum()))

                def show_result():
                    try:
                        # Remove analyzing widget
                        analyzing_widget.setParent(None)
                        lang = self.detect_lang(text)
                        label, score, explanation = self.analyze_sentiment_api(text, lang)
                        
                        # Save analysis result
                        analysis_result = AnalysisResult(
                            text_id=text_entry.id,
                            sentiment=label,
                            sentiment_score=score,
                            analysis_date=datetime.now()
                        )
                        self.session.add(analysis_result)
                        self.session.commit()

                        result_widget = QWidget()
                        result_layout = QVBoxLayout()
                        result_layout.setContentsMargins(50, 0, 0, 0)
                        result_layout.setSpacing(5)
                        
                        # Logo
                        logo_label = QLabel()
                        logo_pixmap = QPixmap("icons/logo.png")
                        logo_label.setPixmap(logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        logo_label.setAlignment(Qt.AlignLeft)
                        result_layout.addWidget(logo_label, alignment=Qt.AlignLeft)
                        
                        # Sentiment label with score
                        if label == "error":
                            sentiment_row = QHBoxLayout()
                            # Emoji selection
                            emoji_path = None
                            if label.lower() == 'positive':
                                emoji_path = get_resource_path('icons/positive.jpg')
                            elif label.lower() == 'negative':
                                emoji_path = get_resource_path('icons/negative.png')
                            elif label.lower() == 'neutral':
                                emoji_path = get_resource_path('icons/neutral.png')
                            if emoji_path and os.path.exists(emoji_path):
                                emoji_label = QLabel()
                                emoji_pixmap = QPixmap(emoji_path)
                                emoji_label.setPixmap(emoji_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                                emoji_label.setAlignment(Qt.AlignVCenter)
                                sentiment_row.addWidget(emoji_label)
                            sentiment_label = QLabel("Sunucuya ulaşılamıyor veya analiz yapılamadı.")
                            sentiment_label.setStyleSheet("color: #ff5555; font-size: 18px; font-weight: bold;" if self.theme == 'dark' else "color: #b00020; font-size: 18px; font-weight: bold;")
                            print(f"API error: label=error, score={score}, explanation={explanation}")
                        else:
                            sentiment_row = QHBoxLayout()
                            # Emoji selection
                            emoji_path = None
                            if label.lower() == 'positive':
                                emoji_path = get_resource_path('icons/positive.jpg')
                            elif label.lower() == 'negative':
                                emoji_path = get_resource_path('icons/negative.png')
                            elif label.lower() == 'neutral':
                                emoji_path = get_resource_path('icons/neutral.png')
                            if emoji_path and os.path.exists(emoji_path):
                                emoji_label = QLabel()
                                emoji_pixmap = QPixmap(emoji_path)
                                emoji_label.setPixmap(emoji_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                                emoji_label.setAlignment(Qt.AlignVCenter)
                                sentiment_row.addWidget(emoji_label)
                            sentiment_label = QLabel(f"{label.upper()} ({score:.2f})")
                            sentiment_label.setStyleSheet("color: #fff; font-size: 18px; font-weight: bold;" if self.theme == 'dark' else "color: #232323; font-size: 18px; font-weight: bold;")
                            sentiment_label.setAlignment(Qt.AlignVCenter)
                            sentiment_row.addWidget(sentiment_label)
                            sentiment_row.addStretch(1)
                            result_layout.addLayout(sentiment_row)
                        
                        # Explanation
                        if explanation:
                            explanation_label = QLabel(explanation)
                            explanation_label.setWordWrap(True)
                            explanation_label.setStyleSheet("color: #fff; font-size: 16px;" if self.theme == 'dark' else "color: #232323; font-size: 16px;")
                            result_layout.addWidget(explanation_label)

                        # Feedback section
                        feedback_widget = QWidget()
                        feedback_layout = QVBoxLayout()
                        feedback_layout.setContentsMargins(0, 10, 0, 0)
                        
                        # Add comment input field
                        comment_input = QLineEdit()
                        comment_input.setPlaceholderText("Add your comment (optional)")
                        comment_input.setStyleSheet("background-color: #444; color: #fff; font-size: 16px; border-radius: 4px; padding: 8px;" if self.theme == 'dark' else "background-color: #E0E0E0; color: #232323; font-size: 16px; border-radius: 4px; padding: 8px;")
                        feedback_layout.addWidget(comment_input)
                        
                        rating_widget = QWidget()
                        rating_layout = QHBoxLayout()
                        rating_layout.setContentsMargins(0, 5, 0, 0)
                        
                        feedback_label = QLabel("Feedback:")
                        feedback_label.setStyleSheet("color: #fff; font-size: 16px;" if self.theme == 'dark' else "color: #232323; font-size: 16px;")
                        rating_layout.addWidget(feedback_label)
                        
                        for i in range(1, 6):
                            star_btn = QPushButton("★")
                            star_btn.setStyleSheet("background: none; color: #888; font-size: 24px;")
                            star_btn.setCursor(Qt.PointingHandCursor)
                            star_btn.clicked.connect(lambda checked, rating=i, comment_input=comment_input: self.submit_feedback(text_entry.id, rating, comment_input.text(), comment_input))
                            rating_layout.addWidget(star_btn)
                        
                        rating_widget.setLayout(rating_layout)
                        feedback_layout.addWidget(rating_widget)
                        feedback_widget.setLayout(feedback_layout)
                        result_layout.addWidget(feedback_widget)
                        
                        result_widget.setLayout(result_layout)
                        message_layout.addWidget(result_widget)
                        message_container.setLayout(message_layout)
                        
                        # Update history
                        self.load_history()
                        
                    except Exception as e:
                        print(f"Error during analysis: {e}")
                        QMessageBox.warning(self, "Error", f"Analysis error: {str(e)}")

                # Simulate analysis delay (1 second)
                QTimer.singleShot(1000, show_result)

            except Exception as e:
                print(f"Error during send_message: {e}")
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
                if "User session expired" in str(e):
                    self.logout()

    def submit_feedback(self, text_id, rating, comment="", comment_input=None):
        try:
            user = self.session.query(User).filter_by(email=self.user_email).first()
            if user:
                feedback = Feedback(
                    user_id=user.id,
                    text_id=text_id,
                    rating=rating,
                    feedback_text=comment,
                    feedback_date=datetime.now()
                )
                self.session.add(feedback)
                self.session.commit()
                QMessageBox.information(self, "Success", "Feedback submitted successfully!")
                # Clear the comment input field
                if comment_input:
                    comment_input.clear()
        except Exception as e:
            print(f"Error submitting feedback: {e}")
            QMessageBox.warning(self, "Error", f"Failed to submit feedback: {str(e)}")

    def show_profile_menu(self):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        menu.setStyleSheet(
            "QMenu { background-color: #333; color: #fff; border-radius: 8px; font-size: 16px; }"
            "QMenu::item:selected { background-color: #444; }"
        )
        profile_action = menu.addAction("Profile")
        settings_action = menu.addAction("Settings")
        logout_action = menu.addAction("Log out")
        profile_action.triggered.connect(self.goto_profile)
        settings_action.triggered.connect(self.goto_settings)
        logout_action.triggered.connect(self.logout)
        # Tam butonun altına aç
        btn_rect = self.profile_btn.rect()
        btn_global = self.profile_btn.mapToGlobal(btn_rect.bottomLeft())
        menu.move(btn_global.x(), btn_global.y())
        menu.exec_()

    def goto_profile(self):
        self.parent().setCentralWidget(ProfilePage(self.user_name, self.user_surname, self.user_email, self.session, self.language, self.session_log_id, self.mainwindow))

    def goto_settings(self):
        if self.mainwindow and isinstance(self.mainwindow, QMainWindow):
            # Kullanıcı bilgilerini mainwindow'a aktar
            self.mainwindow.user_name = self.user_name
            self.mainwindow.user_surname = self.user_surname
            self.mainwindow.user_email = self.user_email
            self.mainwindow.setCentralWidget(SettingsPage(self.mainwindow))
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
        bg_color = "#2A2A2A" if theme == 'dark' else "#F4F4F4"
        text_color = "#fff" if theme == 'dark' else "#232323"
        btn_bg = "#444" if theme == 'dark' else "#F4F4F4"
        btn_text = "#fff" if theme == 'dark' else "#232323"
        accent_bg = "#757575" if theme == 'dark' else "#B0B0B0"
        self.setStyleSheet(f"background-color: {bg_color};")
        self.logo.setStyleSheet("background: none;")
        self.sentilyze_label.setStyleSheet(f"color: {text_color}; background: none; font-size: 22px; font-weight: 600;")
        self.history_title.setStyleSheet(f"color: {text_color}; background: none; font-size: 18px; font-weight: 500;")
        self.history_widget.setStyleSheet("background: none;")
        self.chat_box_widget.setStyleSheet(f"background: none;")
        self.text_input.setStyleSheet(
            f"background-color: {btn_bg}; color: {btn_text}; font-size: 18px; border-radius: 8px; padding: 12px; border: none;"
        )
        self.analyze_btn.setStyleSheet(
            f"background-color: {accent_bg}; color: {btn_text}; font-size: 18px; border-radius: 8px; padding: 0 24px; min-width: 120px; border: none;"
        )
        for i in range(self.history_list.count()):
            btn = self.history_list.itemAt(i).widget()
            if btn:
                btn.setStyleSheet(f"background-color: {btn_bg}; color: {btn_text}; border:none; text-align:left; padding:8px 12px; font-size:16px; border-radius: 8px;")
                btn.setMinimumHeight(36)
                btn.setMaximumWidth(180)

    def logout(self):
        session_log_id = self.session_log_id or (self.mainwindow.session_log_id if self.mainwindow and hasattr(self.mainwindow, 'session_log_id') else None)
        session = self.session or (self.mainwindow.session if self.mainwindow and hasattr(self.mainwindow, 'session') else None)
        if session_log_id and session:
            try:
                session_log = session.query(SessionLog).get(session_log_id)
                if session_log:
                    session_log.logout_time = datetime.now()
                    session.commit()
            except Exception as e:
                print(f"Error updating session log: {e}")
        self.parent().setCentralWidget(FirstPage(mainwindow=self.mainwindow))

    def detect_lang(self, text):
        turkish_chars = "çğıöşü"
        for ch in turkish_chars:
            if ch in text.lower():
                return "tr"
        return "en"

    def analyze_sentiment_api(self, text, lang="en"):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                json={"text": text, "lang": lang}
            )
            if response.ok:
                data = response.json()
                return data['label'], data['score'], data.get('explanation', '')
            else:
                return "error", 0, ""
        except Exception as e:
            print(f"API error: {e}")
            return "error", 0, ""

    def show_ai_chat(self):
        if self.ai_chat_dialog is not None:
            self.ai_chat_dialog.show()
            self.ai_chat_dialog.raise_()
            return

        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QSizePolicy
        dlg = QDialog(self)
        dlg.setWindowTitle("AI Chat")
        dlg.setFixedSize(500, 600)
        layout = QVBoxLayout()
        
        # Chat history
        self.ai_chat_history = QTextEdit()
        self.ai_chat_history.setReadOnly(True)
        self.ai_chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #2A2A2A;
                color: #fff;
                font-size: 15px;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.ai_chat_history)
        
        # Input area
        input_row = QHBoxLayout()
        self.ai_chat_input = QLineEdit()
        self.ai_chat_input.setPlaceholderText("Ask something to AI...")
        self.ai_chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #444;
                color: #fff;
                font-size: 15px;
                border-radius: 8px;
                padding: 10px;
                border: none;
            }
        """)
        self.ai_chat_input.returnPressed.connect(self.send_ai_message)  # Enter tuşu ile gönderme
        input_row.addWidget(self.ai_chat_input)
        
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: #fff;
                font-size: 15px;
                border-radius: 8px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #888;
            }
        """)
        send_btn.clicked.connect(self.send_ai_message)
        input_row.addWidget(send_btn)
        layout.addLayout(input_row)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: #fff;
                font-size: 15px;
                border-radius: 8px;
                padding: 10px;
                border: none;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        
        dlg.setLayout(layout)
        self.ai_chat_dialog = dlg
        dlg.show()

    def send_ai_message(self):
        user_msg = self.ai_chat_input.text().strip()
        if not user_msg:
            return
        self.ai_chat_history.append(f'<div style="margin: 10px 0;"><b style="color: #4CAF50;">You:</b> {user_msg}</div>')
        self.ai_chat_input.clear()

        import threading
        import requests
        import json
        from PyQt5.QtCore import QMetaObject, Qt, Q_ARG

        def get_ai_response():
            try:
                api_key = "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"
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [
                        {"role": "user", "content": user_msg}
                    ]
                }
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data["choices"][0]["message"]["content"]
                    QMetaObject.invokeMethod(
                        self.ai_chat_history,
                        "append",
                        Qt.QueuedConnection,
                        Q_ARG(str, f'<div style="margin: 10px 0;"><b style="color: #2196F3;">AI:</b> {ai_response}</div>')
                    )
                else:
                    error_msg = f"API Error: {response.status_code} - {response.text}"
                    QMetaObject.invokeMethod(
                        self.ai_chat_history,
                        "append",
                        Qt.QueuedConnection,
                        Q_ARG(str, f'<div style="margin: 10px 0; color: #f44336;">{error_msg}</div>')
                    )
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                QMetaObject.invokeMethod(
                    self.ai_chat_history,
                    "append",
                    Qt.QueuedConnection,
                    Q_ARG(str, f'<div style="margin: 10px 0; color: #f44336;">{error_msg}</div>')
                )

        threading.Thread(target=get_ai_response, daemon=True).start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentilyze")
        self.setFixedSize(1600,900)
        self.theme = 'dark'
        self.language = 'en'
        self.session_log_id = None  # Always keep this in mainwindow
        # Veritabanı bağlantısını başlat
        try:
            self.session = get_db_session()
            if not self.session:
                QMessageBox.critical(self, "Error", "Failed to initialize database. Please restart the application.")
                sys.exit(1)
        except Exception as e:
            print(f"Database initialization error in MainWindow: {e}")
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
            sys.exit(1)
            
        self.user_name = "User"
        self.user_surname = ""
        self.user_email = ""
        self.setWindowIcon(QIcon(get_resource_path("icons/logo.png")))
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

    def closeEvent(self, event):
        """Uygulama kapatılırken veritabanı bağlantısını kapat"""
        close_db_session()
        event.accept()

    def setCentralWidget(self, widget):
        """Merkez widget değiştiğinde veritabanı bağlantısını ve kullanıcı bilgilerini koru"""
        if hasattr(self, 'session'):
            widget.session = self.session
        if hasattr(self, 'user_name'):
            widget.user_name = self.user_name
        if hasattr(self, 'user_surname'):
            widget.user_surname = self.user_surname
        if hasattr(self, 'user_email'):
            widget.user_email = self.user_email
        if hasattr(self, 'theme'):
            widget.theme = self.theme
        if hasattr(self, 'language'):
            widget.language = self.language
        if hasattr(self, 'session_log_id'):
            widget.session_log_id = self.session_log_id
        super().setCentralWidget(widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

    # // Yapılacaklar
    # // AI eklenecek
    # // Sonucun doğruluğu test edilecek