from db_operations import DatabaseOperations
from data_insertion import DataInsertion
import os
import sqlite3

def test_database_operations():
    # Veritabanı yolunu belirle
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "test.db")
    
    # Eğer veritabanı dosyası varsa sil
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Eski veritabanı silindi.")
    
    # Veritabanı işlemleri sınıfını başlat
    db_ops = DatabaseOperations(db_path)
    db_insert = DataInsertion(db_path)
    
    # Test kullanıcısı oluştur
    print("\nTest kullanıcısı oluşturuluyor...")
    db_ops.register_user("Test", "User", "test@example.com", "password123")
    
    # Test kullanıcısının ID'sini al
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", ("test@example.com",))
        user_id = cursor.fetchone()[0]
    
    print(f"Test kullanıcısı ID: {user_id}")
    
    # Test verilerini ekle
    print("\n1. Metin girişi ekleme testi:")
    text_entry_id = db_insert.insert_text_entry(
        user_id=user_id,
        text="Bu bir test metnidir",
        language="tr"
    )
    print(f"Text entry ID: {text_entry_id}")
    
    print("\n2. Ayar ekleme testi:")
    setting_result = db_insert.insert_setting(
        user_id=user_id,
        key="theme",
        value="dark"
    )
    print(f"Setting result: {setting_result}")
    
    print("\n3. Oturum logu ekleme testi:")
    session_result = db_insert.insert_session_log(
        user_id=user_id,
        action="login",
        details="Test login"
    )
    print(f"Session log result: {session_result}")
    
    print("\n4. Analiz sonucu ekleme testi:")
    if text_entry_id:
        analysis_result = db_insert.insert_analysis_result(
            text_entry_id=text_entry_id,
            sentiment_label="positive",
            sentiment_score=0.85
        )
        print(f"Analysis result: {analysis_result}")
    else:
        print("Text entry ID bulunamadı, analiz sonucu eklenemedi")

if __name__ == "__main__":
    test_database_operations() 