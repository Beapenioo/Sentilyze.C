from sqlalchemy import create_engine
from models import Base
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Create database path
db_path = os.path.join(current_dir, "users.db")

# Create SQLite engine
engine = create_engine(f'sqlite:///{db_path}')

# Create all tables
Base.metadata.create_all(engine) 