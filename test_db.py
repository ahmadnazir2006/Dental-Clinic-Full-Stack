from database import engine
with engine.connect() as connection:
    print("Database connection successful!")