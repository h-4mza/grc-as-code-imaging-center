import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# The URL from docker-compose is postgresql://grc_user:grc_password@postgres/grc_db
# For local access via CLI outside docker, we might use localhost.
# In the container, it's postgres.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://grc_user:grc_password@localhost/grc_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
