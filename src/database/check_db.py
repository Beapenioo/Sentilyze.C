import sqlite3
import os

def check_database():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "test.db")
    
    if not os.path.exists(db_path):
        print("Veritabanı dosyası bulunamadı!")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Tabloları listele
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTablolar:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Her tablonun içeriğini göster
            cursor.execute(f"SELECT * FROM {table[0]};")
            rows = cursor.fetchall()
            if rows:
                print(f"  İçerik ({len(rows)} kayıt):")
                for row in rows:
                    print(f"  {row}")
            else:
                print("  Boş")

if __name__ == "__main__":
    check_database() 