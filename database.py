from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# MySQL bağlantı bilgileri
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/sentilyze"

# Engine oluştur
engine = create_engine(DATABASE_URL, echo=True)

# Session factory oluştur
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class oluştur
Base = declarative_base()

def get_db_engine():
    try:
        # Veritabanı bağlantısını test et
        with engine.connect() as conn:
            # Veritabanının var olup olmadığını kontrol et
            result = conn.execute(text("SELECT DATABASE()"))
            current_db = result.scalar()
            
            if not current_db:
                # Veritabanı yoksa oluştur
                conn.execute(text("CREATE DATABASE IF NOT EXISTS sentilyze"))
                conn.execute(text("USE sentilyze"))
            
            # Tabloları oluştur
            Base.metadata.create_all(engine)
            conn.commit()
            
        return engine
    except Exception as e:
        print(f"Database engine initialization error: {e}")
        return None

def get_db_session():
    engine = get_db_engine()
    if engine:
        Session = sessionmaker(bind=engine)
        return Session()
    return None

def close_db_session(session):
    if session:
        session.close() 