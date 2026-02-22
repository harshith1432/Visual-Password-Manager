import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Connecting to database...")
    # SQL to add the column if it doesn't exist
    sql = text("ALTER TABLE passwords ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'other';")
    conn.execute(sql)
    conn.commit()
    print("Column 'category' added successfully!")
