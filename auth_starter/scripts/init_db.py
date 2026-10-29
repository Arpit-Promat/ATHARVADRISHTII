import os
from sqlalchemy import create_engine
from models import Base
url = os.getenv("DATABASE_URL")
if not url: raise SystemExit("DATABASE_URL environment variable is required.")
Base.metadata.create_all(create_engine(url, pool_pre_ping=True))
print("Database tables initialized.")
