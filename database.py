from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/sentilyze"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_engine():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()"))
            current_db = result.scalar()
            
            if not current_db:
                conn.execute(text("CREATE DATABASE IF NOT EXISTS sentilyze"))
                conn.execute(text("USE sentilyze"))
            
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